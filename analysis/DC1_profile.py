"""DC1 stage 1: loader and profile statistics only (brief briefs/DC1/README.md §3).

No controller, predictor or scoring code lives here.

Data: NLR "Dataset of Generative AI Workload Power Profiles" (OpenEI submission 8651, CC BY 4.0).
Unit of analysis: one multi-node training job's total power (GPU + CPU, summed over the job's nodes), as aggregated by
the provider (01_aggregated_datasets/training, 0.2 s grid over the window common to all nodes). The aggregation is
cross-checked here against an independent sum of the raw per-node WattAMeter logs.

Usage: python3 -E analysis/DC1_profile.py <dataset root x/> results/DC1/profile.json
"""
import json
import os
import sys

import numpy as np
import pandas as pd

ACTIVE_FRAC = 0.6        # DC1-P1: active segment = first..last frame with P >= ACTIVE_FRAC * max
BAND = (0.05, 2.5)       # Hz, brief §3.2
PEAK_HALF_WIDTH = 0.10   # peak band = f_pk * (1 +/- 0.10)
WELCH_SEG_S = 256.0      # Welch segment length (s), 50 % overlap, Hann
PERIODIC_SHARE = 0.20    # brief §3.3
GATE_A, GATE_DUR_MIN, GATE_FS = 0.30, 10.0, 5.0   # brief §3.4
CROSSCHECK_IDX = (0, 21, 37)  # one 2-node Llama, one 2-node SD, one 16-node SD job


def load_training(root):
    """Return metadata DataFrame and a dict idx -> (t [s], P [W]) for every aggregated training job."""
    base = os.path.join(root, '01_aggregated_datasets', 'training')
    meta = pd.read_csv(os.path.join(base, 'metadata.csv'), index_col=0)
    jobs = {}
    for i, r in meta.iterrows():
        d = pd.read_parquet(os.path.join(base, 'results', os.path.basename(r.path_save)))
        jobs[i] = (d.index.values.astype(float), d['power[W]'].values.astype(float))
    return meta, jobs


def _read_raw(path, kind):
    with open(path) as f:
        header = f.readline().lstrip('#').split()
    d = pd.read_csv(path, sep=r'\s+', comment='#', header=None)
    ts = pd.to_datetime(d[0], format='%Y-%m-%d_%H:%M:%S.%f')
    if kind == 'nvml':
        d.columns = header
        p = sum(d[f'gpu-{g}[mW]'] for g in range(4)) * 1e-3
    else:  # rapl: the four [W] columns, as named by the provider; a NaN reading is skipped in the row sum, as the
        # provider's pandas sum does (the count is reported)
        p = d[[6, 7, 8, 9]].sum(axis=1, skipna=True)
        _read_raw.nan_cells += int(d[[6, 7, 8, 9]].isna().values.sum())
    return ts.values, p.values.astype(float)


_read_raw.nan_cells = 0


def raw_job_sum(root, model, nodes, slurmid):
    """Independent re-aggregation: linear interpolation of every node's GPU and CPU series onto a 0.2 s grid over the
    common window, then a plain sum."""
    sub = {'llama2_70b_lora': 'training_llama2_70b_lora', 'stable_diffusion': 'training_stable_diffusion'}[model]
    d = os.path.join(root, '00_raw_datasets', sub, f'{nodes}node')
    files = sorted(f for f in os.listdir(d) if f'slurmid_{slurmid}_' in f)
    series = [_read_raw(os.path.join(d, f), f.split('_')[0]) for f in files]
    t0 = max(s[0][0] for s in series)
    t1 = min(s[0][-1] for s in series)
    n = int((t1 - t0) / np.timedelta64(200, 'ms')) + 1
    grid = (np.arange(n) * 0.2)
    tot = np.zeros(n)
    for ts, p in series:
        x = (ts - t0) / np.timedelta64(1, 's')
        tot += np.interp(grid, x, p)
    return len(files), grid, tot


def welch(x, fs):
    nseg = int(WELCH_SEG_S * fs)
    if len(x) < nseg:
        nseg = len(x)
    step = nseg // 2
    w = np.hanning(nseg)
    acc = None
    k = 0
    for s in range(0, len(x) - nseg + 1, step):
        seg = x[s:s + nseg] - x[s:s + nseg].mean()
        spec = np.abs(np.fft.rfft(seg * w)) ** 2
        acc = spec if acc is None else acc + spec
        k += 1
    return np.fft.rfftfreq(nseg, 1 / fs), acc / k


def dwell(above, dt):
    """Median run length (s) of the True and the False states."""
    edges = np.flatnonzero(np.diff(above.astype(int))) + 1
    runs = np.split(above, edges)
    up = [len(r) * dt for r in runs if r[0]]
    dn = [len(r) * dt for r in runs if not r[0]]
    return (float(np.median(up)) if up else None, float(np.median(dn)) if dn else None, len(up), len(dn))


def acf_peak(x, fs, lo_s=2.0, hi_s=60.0):
    """Descriptive only: the highest autocorrelation in lags lo_s..hi_s and its lag."""
    x = x - x.mean()
    n = len(x)
    f = np.fft.rfft(x, 2 * n)
    ac = np.fft.irfft(f * np.conj(f))[:n]
    ac = ac / ac[0]
    a, b = int(lo_s * fs), min(int(hi_s * fs), n - 1)
    k = a + int(np.argmax(ac[a:b]))
    return float(ac[k]), k / fs


def stats(t, p):
    dt = float(np.median(np.diff(t)))
    fs = 1.0 / dt
    mx = float(p.max())
    p5, p50, p95 = (float(np.percentile(p, q)) for q in (5, 50, 95))
    mid = (p5 + p95) / 2
    above = p > mid
    up_s, dn_s, n_up, n_dn = dwell(above, dt)
    f, s = welch(p, fs)
    tot = s[1:].sum()
    band = (f >= BAND[0]) & (f <= BAND[1])
    fpk = float(f[band][np.argmax(s[band])])
    pk = (f >= fpk * (1 - PEAK_HALF_WIDTH)) & (f <= fpk * (1 + PEAK_HALF_WIDTH))
    share = float(s[pk].sum() / tot)
    harm = np.zeros_like(f, dtype=bool)
    for h in range(1, 8):
        harm |= (f >= h * fpk * (1 - PEAK_HALF_WIDTH)) & (f <= h * fpk * (1 + PEAK_HALF_WIDTH))
    ac, lag = acf_peak(p, fs)
    return {
        'n': int(len(p)), 'dt_s': dt, 'fs_hz': fs, 'duration_min': float((t[-1] - t[0]) / 60),
        'p5_W': p5, 'p50_W': p50, 'p95_W': p95, 'max_W': mx,
        'A': (p95 - p5) / mx,
        'frac_above_mid': float(above.mean()), 'dwell_above_s_median': up_s, 'dwell_below_s_median': dn_s,
        'n_above_runs': n_up, 'n_below_runs': n_dn,
        'f_peak_hz': fpk, 'period_s': 1 / fpk, 'peak_share': share,
        'peak_share_with_harmonics_descriptive': float(s[harm].sum() / tot),
        'acf_peak_descriptive': ac, 'acf_lag_s_descriptive': lag,
        'step_p95_frac_of_max': float(np.percentile(np.abs(np.diff(p)), 95) / mx),
        'step_max_frac_of_max': float(np.abs(np.diff(p)).max() / mx),
    }


def active_segment(t, p):
    on = np.flatnonzero(p >= ACTIVE_FRAC * p.max())
    a, b = on[0], on[-1] + 1
    return t[a:b], p[a:b], float(t[a]), float(t[b - 1])


def folds(rows):
    """Brief §3.5 (CHOSEN): within each workload, sort by the active-segment A and assign A,B,B,A,A,B,B,A,..."""
    pat = ['A', 'B', 'B', 'A']
    out = {}
    for model in sorted({r['model'] for r in rows}):
        rs = sorted((r for r in rows if r['model'] == model), key=lambda r: (r['active']['A'], r['idx']))
        for k, r in enumerate(rs):
            out[r['idx']] = pat[k % 4]
    return out


def plot(jobs, rows, path):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    pick = [10, 21, 32, 37]
    fig, ax = plt.subplots(5, 2, figsize=(14, 16))
    for k, i in enumerate(pick):
        t, p = jobs[i]
        r = rows[i]
        a0, a1 = r['active_window_s']
        x = ax[k, 0]
        x.plot(t / 60, p / 1e3, lw=.3)
        x.axvspan(a0 / 60, a1 / 60, color='C1', alpha=.12, label='active segment (DC1-P1)')
        x.set_title(f"job {i}: {r['model']}, {r['nodes']} nodes; A full {r['full']['A']:.2f}, active {r['active']['A']:.2f}")
        x.set_xlabel('min'); x.set_ylabel('kW'); x.legend(loc='lower center', fontsize=8)
        z = ax[k, 1]
        c = (a0 + a1) / 2
        s = (t >= c) & (t < c + 60)
        z.plot(t[s] - c, p[s] / 1e3, '.-', lw=.5, ms=2)
        z.set_title(f"job {i}: 60 s from mid-active; period {r['active']['period_s']:.1f} s, share {r['active']['peak_share']:.2f}")
        z.set_xlabel('s'); z.set_ylabel('kW')
    for m, c in (('llama2_70b_lora', 'C0'), ('stable_diffusion', 'C3')):
        rr = [r for r in rows if r['model'] == m]
        ax[4, 0].scatter([r['active']['A'] for r in rr], [r['active']['peak_share'] for r in rr], c=c, label=m, s=18)
        ax[4, 1].scatter([r['active']['A'] for r in rr], [r['active']['period_s'] for r in rr], c=c, label=m, s=18)
    ax[4, 0].axvline(GATE_A, color='k', ls='--', lw=.8); ax[4, 0].axhline(PERIODIC_SHARE, color='k', ls=':', lw=.8)
    ax[4, 0].set_xlabel('A, active segment'); ax[4, 0].set_ylabel('spectral peak share'); ax[4, 0].legend(fontsize=8)
    ax[4, 1].axvline(GATE_A, color='k', ls='--', lw=.8)
    ax[4, 1].set_xlabel('A, active segment'); ax[4, 1].set_ylabel('dominant period (s)')
    fig.suptitle('DC1 profile: NLR GenAI power profiles (CC BY 4.0), job total power, 5 Hz. SOURCED traces.')
    plt.tight_layout()
    plt.savefig(path, dpi=70)


def main(root, out):
    meta, jobs = load_training(root)
    rows = []
    for i, r in meta.iterrows():
        t, p = jobs[i]
        ta, pa, a0, a1 = active_segment(t, p)
        rows.append({'idx': int(i), 'model': r.model, 'nodes': int(r.nodes), 'repeat': int(r['repeat']),
                     'slurmid': int(r.slurmid), 'file': os.path.basename(r.path_save),
                     'full': stats(t, p), 'active': stats(ta, pa), 'active_window_s': [a0, a1]})
    fd = folds(rows)
    for r in rows:
        r['fold'] = fd[r['idx']]
        for k in ('full', 'active'):
            s = r[k]
            s['gate'] = bool(s['A'] >= GATE_A and s['duration_min'] >= GATE_DUR_MIN and s['fs_hz'] >= GATE_FS - 1e-6)
            s['periodic'] = bool(s['peak_share'] >= PERIODIC_SHARE)

    xc = []
    for i in CROSSCHECK_IDX:
        r = meta.loc[i]
        nan0 = _read_raw.nan_cells
        nfiles, g, tot = raw_job_sum(root, r.model, int(r.nodes), int(r.slurmid))
        t, p = jobs[i]
        m = min(len(g), len(t))
        rel = np.abs(tot[:m] - p[:m]) / p[:m].max()
        xc.append({'idx': int(i), 'files': nfiles, 'expected_files': 2 * int(r.nodes), 'n_raw_grid': int(len(g)),
                   'n_agg': int(len(t)), 'max_abs_diff_frac_of_max': float(rel.max()),
                   'p99_abs_diff_frac_of_max': float(np.percentile(rel, 99)),
                   'rapl_nan_cells_skipped': _read_raw.nan_cells - nan0})

    inf = {}
    for name in ('inference_offline_llama3_70b', 'inference_online_finite_llama3_70b', 'inference_online_rate_llama3_70b'):
        m = pd.read_csv(os.path.join(root, '01_aggregated_datasets', name, 'metadata.csv'))
        col = 'elapsed' if 'elapsed' in m else ('execution_time_seconds' if 'execution_time_seconds' in m else 'duration')
        inf[name] = {'runs': int(len(m)), 'duration_col': col, 'duration_s_min': float(m[col].min()),
                     'duration_s_max': float(m[col].max()), 'nodes': 1}

    summ = {}
    for k in ('full', 'active'):
        A = np.array([r[k]['A'] for r in rows])
        per = np.array([r[k]['period_s'] for r in rows])
        g = [r for r in rows if r[k]['gate']]
        summ[k] = {'A_quartiles': [float(np.percentile(A, q)) for q in (0, 25, 50, 75, 100)],
                   'period_s_quartiles': [float(np.percentile(per, q)) for q in (0, 25, 50, 75, 100)],
                   'n_gate': len(g), 'n_gate_periodic': sum(r[k]['periodic'] for r in g),
                   'n_periodic_all': sum(r[k]['periodic'] for r in rows),
                   'n_gate_by_model': {m: sum(r['model'] == m for r in g) for m in sorted({r['model'] for r in rows})},
                   'n_gate_by_fold': {f: sum(r['fold'] == f for r in g) for f in 'AB'}}
    res = {'constants': {'ACTIVE_FRAC': ACTIVE_FRAC, 'BAND_hz': BAND, 'PEAK_HALF_WIDTH': PEAK_HALF_WIDTH,
                         'WELCH_SEG_S': WELCH_SEG_S, 'PERIODIC_SHARE': PERIODIC_SHARE,
                         'GATE': [GATE_A, GATE_DUR_MIN, GATE_FS]},
           'jobs': rows, 'crosscheck': xc, 'inference': inf, 'summary': summ}
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w') as f:
        json.dump(res, f, indent=1)
    plot(jobs, rows, os.path.join(os.path.dirname(out), 'profile.png'))
    for k in ('full', 'active'):
        print(k, json.dumps(summ[k]))
    print('crosscheck', json.dumps(xc))
    print('inference', json.dumps(inf))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
