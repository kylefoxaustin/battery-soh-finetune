"""DC1 stage 2: storage sizing under a ramp spec, reactive vs forecasting controllers.

Implements results/DC1/DC1_preregistration.md (§1-§7) with deviations D-1 (co-primary decisions per workload) and D-2
(K1-r, the 1 s ramp comparator, and the memory readout M). Every number produced here is DERIVED from SOURCED traces
(NLR GenAI power profiles, CC BY 4.0) under ASSUMED specs.

The plant loop and the causal forecasters run in C (analysis/DC1_sim.c, built to a temporary directory at start-up).
Pure-Python references of all of them are gated against C (§4.5) before any E* is computed; the run stops if the
gate fails.

Usage: python3 -E analysis/DC1_storage.py <dataset root x/> results/DC1 [--workers N]
"""
import ctypes
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ProcessPoolExecutor

import numpy as np

from DC1_profile import active_segment, load_training

HERE = os.path.dirname(os.path.abspath(__file__))

# §2-§4, fixed by the pre-registration
S_TGT = (0.3, 0.4, 0.5, 0.6, 0.7)
T_REC = (2.0, 5.0, 10.0, 30.0)
G_GRID = (0.0, 0.25, 0.5, 1.0, 1.5, 2.0)
G_INF = G_GRID + (3.0, 5.0)
WS = (1, 5, 30, 60)            # s; 1/5/30 the §4.2 grid, 60 added by DC1-P6 and joined to W* by D-2
W_PRIMARY = 30
RHO_MIN = 0.5
LMIN_S, HP_S, RAMP_S = 1.0, 5.0, 1.0
E_LO, E_HI, BIS_TOL = 1e-2, 600.0, 0.01
N_MONO = 12
NBOOT, BOOT_SEED = 1000, 0
SAVES_G, SAVES_LO, SH_MAX, REACTIVE_G = 1.25, 1.0, 1.10, 1.10   # §6
M_BAR, WSTAR_FRAC = 1.10, 0.95                                   # D-2
GATE_IDX = (0, 21, 37)
EXAMPLE_IDX = (0, 21)
BASE = {'R': 0.10, 'budget': 0.001, 'pms': 2.0, 'eta': 1.0, 'seg': 'active', 'dec': 1}
SCENARIOS = {                  # §7; each re-fit end to end
    'primary': {},
    'R0.05': {'R': 0.05}, 'R0.20': {'R': 0.20},
    'eta0.90': {'eta': 0.90},
    'Pmax_s_1x': {'pms': 1.0},
    'budget0.5%': {'budget': 0.005},
    'decimate_1Hz': {'dec': 5},
    'whole_trace': {'seg': 'whole'},
}

_LIB = None


def _js(o):
    if isinstance(o, np.generic):
        return o.item()
    raise TypeError(type(o))


def build_lib(dst):
    so = os.path.join(dst, 'dc1_sim.so')
    subprocess.check_call(['gcc', '-O2', '-shared', '-fPIC', '-o', so, os.path.join(HERE, 'DC1_sim.c'), '-lm'])
    return so


def lib(so=None):
    global _LIB
    if _LIB is None:
        L = ctypes.CDLL(so)
        dp = np.ctypeslib.ndpointer(np.float64, flags='C')
        ip = np.ctypeslib.ndpointer(np.int32, flags='C')
        d = ctypes.c_double
        L.dc1_sim.restype = ctypes.c_int
        L.dc1_sim.argtypes = [dp, dp, ctypes.c_int] + [d] * 10 + [ctypes.c_void_p, ctypes.c_void_p]
        L.dc1_fc_seasonal.restype = None
        L.dc1_fc_seasonal.argtypes = [dp, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, d,
                                      ctypes.c_void_p, dp, ip]
        L.dc1_fc_ramp.restype = None
        L.dc1_fc_ramp.argtypes = [dp, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_void_p, dp]
        _LIB = L
    return _LIB


def _init(so):
    lib(so)


# ---------------------------------------------------------------- C wrappers

def sim_c(P, dh, E, s, T, g, sc, pl, soe=None, pup=None):
    eta = math.sqrt(sc['eta'])
    return lib().dc1_sim(P, dh, len(P), E, s, T, g, sc['R'], pl['Pmax'], pl['Pmax_s'], pl['dt'], eta, eta,
                         None if soe is None else soe.ctypes.data, None if pup is None else pup.ctypes.data)


def fc_seasonal_c(P, nW, Lmin, Hp, perm):
    dh = np.zeros(len(P))
    Ls = np.zeros(len(P), dtype=np.int32)
    lib().dc1_fc_seasonal(P, len(P), nW, Lmin, Hp, RHO_MIN, None if perm is None else perm.ctypes.data, dh, Ls)
    return dh, Ls


def fc_ramp_c(P, n, Hp, perm):
    dh = np.zeros(len(P))
    lib().dc1_fc_ramp(P, len(P), n, Hp, None if perm is None else perm.ctypes.data, dh)
    return dh


# ---------------------------------------------------------------- Python references (§4.5 gate)

def sim_py(P, dh, E, s_tgt, T, g, sc, pl):
    R, Pmax, Pms, dt = sc['R'], pl['Pmax'], pl['Pmax_s'], pl['dt']
    eta = math.sqrt(sc['eta'])
    lim, tol = R * Pmax * dt, 1e-9 * Pmax
    soe, prev, viol = s_tgt * E, P[0], 0
    out = [soe]
    for t in range(1, len(P)):
        s = s_tgt
        if g != 0.0:
            d = dh[t]
            s = min(max(s_tgt + g / (2 * R * Pmax * E) * np.sign(d) * d * d, 0.05), 0.95)
        r = P[t] + (s * E - soe) / T
        pst = min(max(r, prev - lim), prev + lim)
        lo = max(-Pms, -(E - soe) / (eta * dt))
        hi = min(Pms, soe * eta / dt)
        ps = min(max(P[t] - pst, lo), hi)
        pup = P[t] - ps
        soe = soe - ps * dt / eta if ps > 0 else soe - ps * dt * eta
        viol += abs(pup - prev) > lim + tol
        prev = pup
        out.append(soe)
    return viol, np.array(out)


def _pearson(a, b):
    a = a - a.mean()
    b = b - b.mean()
    saa, sbb = (a * a).sum(), (b * b).sum()
    return float('nan') if saa <= 0 or sbb <= 0 else float((a * b).sum() / math.sqrt(saa * sbb))


def fc_seasonal_py(P, nW, Lmin, Hp, perm, frames):
    dh, Ls = {}, {}
    for t in frames:
        dh[t], Ls[t] = 0.0, 0
        if t < nW - 1 or nW // 2 < Lmin:
            continue
        w = P[t - nW + 1:t + 1]
        if perm is not None:
            w = w[perm[t - nW + 1]]
        best, L = -2.0, 0
        for l in range(Lmin, nW // 2 + 1):
            r = _pearson(w[l:], w[:-l])
            if not math.isnan(r) and r > best:
                best, L = r, l
        if L == 0 or best < RHO_MIN:
            continue
        Ls[t] = L
        dm = 0.0
        for h in range(1, Hp + 1):
            d = w[nW - 1 + h - math.ceil(h / L) * L] - P[t]
            if abs(d) > abs(dm):
                dm = d
        dh[t] = dm
    return dh, Ls


def fc_ramp_py(P, n, Hp, perm, frames):
    out = {}
    x = np.arange(n, dtype=float)
    for t in frames:
        out[t] = 0.0
        if t < n - 1:
            continue
        v = P[t - n + 1:t + 1]
        if perm is not None:
            v = v[perm[t - n + 1]]
        b = ((x - x.mean()) * (v - v.mean())).sum() / ((x - x.mean()) ** 2).sum()
        dm = 0.0
        for h in range(1, Hp + 1):
            if abs(b * h) > abs(dm):
                dm = b * h
        out[t] = dm
    return out


# ---------------------------------------------------------------- segment, forecasts, E*

def segment(t, p, sc):
    if sc['seg'] == 'active':
        _, p, _, _ = active_segment(t, p)
    dt = float(np.median(np.diff(t)))
    k = sc['dec']
    if k > 1:
        n = len(p) // k
        p = p[:n * k].reshape(n, k).mean(axis=1)
        dt *= k
    dt = round(dt, 6)
    P = np.ascontiguousarray(p, dtype=np.float64)
    swing = float(np.percentile(P, 95) - np.percentile(P, 5))
    return P, {'dt': dt, 'Pmax': float(P.max()), 'swing': swing, 'Pmax_s': sc['pms'] * swing, 'N': len(P)}


def perms(seed, n, count):
    rng = np.random.default_rng(seed)
    out = np.empty((max(count, 0), n), dtype=np.int32)
    for i in range(count):
        out[i] = rng.permutation(n)
    return out


def sizes(dt):
    return {W: int(round(W / dt)) for W in WS}, max(1, int(round(LMIN_S / dt))), int(round(HP_S / dt)), \
        max(2, int(round(RAMP_S / dt)))


def forecasts(idx, P, dt):
    nWs, Lmin, Hp, nr = sizes(dt)
    N = len(P)
    f = {}
    for W, nW in nWs.items():
        f[f'K1_{W}'] = fc_seasonal_c(P, nW, Lmin, Hp, None)[0]
        f[f'K1sh_{W}'] = fc_seasonal_c(P, nW, Lmin, Hp, perms(1000 * idx + W, nW, N - nW + 1))[0]
    f['K1r'] = fc_ramp_c(P, nr, Hp, None)
    f['K1rsh'] = fc_ramp_c(P, nr, Hp, perms(1000 * idx + 1001, nr, N - nr + 1))
    fut = np.zeros(N)
    for h in range(1, Hp + 1):
        d = np.zeros(N)
        d[:N - h] = P[h:] - P[:N - h]
        fut = np.where(np.abs(d) > np.abs(fut), d, fut)
    f['Kinf'] = fut
    f['K0'] = np.zeros(N)
    return f


def budget_n(sc, pl):
    return int(math.floor(sc['budget'] * pl['N']))


def estar(P, dh, s, T, g, sc, pl):
    """§3: smallest E (units Pmax x 1 s) with violations <= budget; (E*, flag) with flag 'cens'/'floor'/''."""
    nb = budget_n(sc, pl)

    def ok(e):
        return sim_c(P, dh, e * pl['Pmax'], s, T, g, sc, pl) <= nb
    if not ok(E_HI):
        return E_HI, 'cens'
    if ok(E_LO):
        return E_LO, 'floor'
    lo, hi = math.log10(E_LO), math.log10(E_HI)
    while 10 ** (hi - lo) - 1 >= BIS_TOL:
        mid = (lo + hi) / 2
        if ok(10 ** mid):
            hi = mid
        else:
            lo = mid
    return 10 ** hi, ''


# ---------------------------------------------------------------- per-job workers

def ctrl_grid():
    """(controller key, forecast key, g grid) for every non-K0 controller."""
    out = []
    for W in WS:
        out.append((f'K1_{W}', f'K1_{W}', G_GRID))
        out.append((f'K1sh_{W}', f'K1sh_{W}', G_GRID))
    out += [('K1r', 'K1r', G_GRID), ('K1rsh', 'K1rsh', G_GRID), ('Kinf', 'Kinf', G_INF)]
    return out


def job_k0(args):
    idx, t, p, sc = args
    P, pl = segment(t, p, sc)
    z = np.zeros(len(P))
    return idx, pl, {(s, T): estar(P, z, s, T, 0.0, sc, pl) for s in S_TGT for T in T_REC}


def job_ctrl(args):
    idx, t, p, sc, pairs, cache = args
    P, pl = segment(t, p, sc)
    key = os.path.join(cache, f"fc_{idx}_{sc['seg']}_{sc['dec']}.npz") if cache else None
    if key and os.path.exists(key):
        f = dict(np.load(key))
    else:
        f = forecasts(idx, P, pl['dt'])
        if key:
            np.savez(key, **f)
    out = {}
    for (s, T) in pairs:
        for c, fk, gg in ctrl_grid():
            for g in gg:
                out[(s, T, c, g)] = estar(P, f[fk], s, T, g, sc, pl)
    return idx, out


def job_eval(args):
    """Monotonicity (§3), dynamic range, and (primary only) example traces at the job's out-of-fold configs."""
    idx, t, p, sc, cfgs, cache, want_traces = args
    P, pl = segment(t, p, sc)
    f = dict(np.load(os.path.join(cache, f"fc_{idx}_{sc['seg']}_{sc['dec']}.npz")))
    nb = budget_n(sc, pl)
    Es = np.logspace(math.log10(E_LO), math.log10(E_HI), N_MONO)
    res = {}
    for name, (fk, s, T, g, e) in cfgs.items():
        v = [sim_c(P, f[fk], E * pl['Pmax'], s, T, g, sc, pl) for E in Es]
        incr = any(v[k + 1] > v[k] for k in range(len(v) - 1))
        ok = [x <= nb for x in v]
        pf = any(ok[k] and not ok[k + 1] for k in range(len(ok) - 1))
        pup = np.zeros(len(P))
        soe = np.zeros(len(P))
        sim_c(P, f[fk], e * pl['Pmax'], s, T, g, sc, pl, soe, pup)
        res[name] = {'mono_count_increase': incr, 'mono_passfail_flip': pf,
                     'dyn_range_at_Estar': float((np.percentile(pup, 95) - np.percentile(pup, 5)) / pl['Pmax'])}
    tr = None
    if want_traces:
        e0 = cfgs['K0'][4]
        tr = {'P': P, 'dt': pl['dt'], 'Pmax': pl['Pmax'], 'E': e0}
        for name in ('K0', f'K1_{W_PRIMARY}', 'Kinf'):
            fk, s, T, g, _ = cfgs[name]
            pup = np.zeros(len(P))
            soe = np.zeros(len(P))
            v = sim_c(P, f[fk], e0 * pl['Pmax'], s, T, g, sc, pl, soe, pup)
            tr[name] = {'pup': pup, 'soe': soe / (e0 * pl['Pmax']), 'viol': v}
    return idx, res, tr


# ---------------------------------------------------------------- gate (§4.5)

def gate(jobs, sc):
    rep = []
    ok = True
    for idx in GATE_IDX:
        t, p = jobs[idx]
        P, pl = segment(t, p, sc)
        nWs, Lmin, Hp, nr = sizes(pl['dt'])
        frames = list(range(0, 400)) + list(range(len(P) // 2, len(P) // 2 + 400)) + list(range(len(P) - 200, len(P)))
        fc = {}
        for W in (5, 30, 60):
            nW = nWs[W]
            pm = perms(1000 * idx + W, nW, len(P) - nW + 1)
            for name, pr in ((f'K1_{W}', None), (f'K1sh_{W}', pm)):
                dc, Lc = fc_seasonal_c(P, nW, Lmin, Hp, pr)
                dp, Lp = fc_seasonal_py(P, nW, Lmin, Hp, pr, frames)
                dd = max(abs(dc[k] - dp[k]) for k in frames) / pl['Pmax']
                lm = sum(int(Lc[k] != Lp[k]) for k in frames)
                rep.append({'idx': idx, 'what': name, 'frames': len(frames), 'max_abs_dhat_diff_frac_Pmax': dd,
                            'Lstar_mismatch': lm})
                ok &= dd <= 1e-9 and lm == 0
                fc[name] = dc
        pm = perms(1000 * idx + 1001, nr, len(P) - nr + 1)
        for name, pr in (('K1r', None), ('K1rsh', pm)):
            dc = fc_ramp_c(P, nr, Hp, pr)
            dp = fc_ramp_py(P, nr, Hp, pr, frames)
            dd = max(abs(dc[k] - dp[k]) for k in frames) / pl['Pmax']
            rep.append({'idx': idx, 'what': name, 'frames': len(frames), 'max_abs_dhat_diff_frac_Pmax': dd})
            ok &= dd <= 1e-9
            fc[name] = dc
        for e in (0.3, 3.0, 30.0):
            for name, g in (('K0', 0.0), (f'K1_{W_PRIMARY}', 1.0), ('K1r', 1.0)):
                dh = fc.get(name, np.zeros(len(P)))
                E = e * pl['Pmax']
                vc_soe = np.zeros(len(P))
                vc = sim_c(P, dh, E, 0.5, 5.0, g, sc, pl, vc_soe, None)
                vp, vp_soe = sim_py(P, dh, E, 0.5, 5.0, g, sc, pl)
                sd = float(np.abs(vc_soe - vp_soe).max() / E)
                rep.append({'idx': idx, 'what': f'sim {name} g={g}', 'E_over_Pmax_s': e, 'viol_c': vc, 'viol_py': vp,
                            'max_abs_soe_diff_frac_E': sd})
                ok &= vc == vp and sd <= 1e-9
    return ok, rep


# ---------------------------------------------------------------- readouts

def boot(pop, fold, stats):
    """Headline = mean over folds of the median over that fold's jobs; CI from NBOOT resamples within fold.
    stats: name -> callable(dict of per-fold resampled index arrays) -> value."""
    by = {F: np.array([j for j in pop if fold[j] == F]) for F in 'AB'}
    point = {k: fn(by) for k, fn in stats.items()}
    rng = np.random.default_rng(BOOT_SEED)
    bs = {k: [] for k in stats}
    for _ in range(NBOOT):
        rs = {F: rng.choice(v, size=len(v), replace=True) for F, v in by.items()}
        for k, fn in stats.items():
            bs[k].append(fn(rs))
    return {k: {'point': point[k], 'ci95': [float(np.percentile(bs[k], 2.5)), float(np.percentile(bs[k], 97.5))]}
            for k in stats}


def hl(vals):
    return lambda by: float(np.mean([np.median([vals[j] for j in by[F]]) for F in 'AB']))


def readout(pop, fold, G):
    W30 = W_PRIMARY
    st = {'G': hl(G[f'K1_{W30}']), 'G_sh': hl(G[f'K1sh_{W30}']), 'G_sh_ownfit': hl(G[f'K1sh_{W30}_own']),
          'G_inf': hl(G['Kinf']), 'G_r': hl(G['K1r']), 'G_r_sh': hl(G['K1rsh']), 'G_r_sh_ownfit': hl(G['K1rsh_own'])}
    for W in WS:
        st[f'G_W{W}'] = hl(G[f'K1_{W}'])
        st[f'G_sh_W{W}'] = hl(G[f'K1sh_{W}'])
    st['M'] = lambda by: hl(G[f'K1_{W30}'])(by) / hl(G['K1r'])(by)
    b = boot(pop, fold, st)
    g, lo, sh = b['G']['point'], b['G']['ci95'][0], b['G_sh']['point']
    if g >= SAVES_G and lo > SAVES_LO and sh < SH_MAX:
        v = 'FORECASTING SAVES STORAGE'
    elif g < REACTIVE_G:
        v = 'REACTIVE SUFFICES'
    else:
        v = 'UNCLEAR'
    m, mlo = b['M']['point'], b['M']['ci95'][0]
    if m >= M_BAR and mlo > 1.0:
        mv = 'NEEDS HISTORY'
    elif m < M_BAR:
        mv = 'NO HISTORY NEEDED' + (' (K1-r beat K1)' if m < 1 / M_BAR else '')
    else:
        mv = 'UNCLEAR on memory'
    curve = {1: b['G_r']['point'], 5: b['G_W5']['point'], 30: b['G_W30']['point'], 60: b['G_W60']['point']}
    mx = max(curve.values())
    wstar = min(W for W, x in curve.items() if x >= WSTAR_FRAC * mx)
    return {'n': len(pop), 'n_by_fold': {F: sum(fold[j] == F for j in pop) for F in 'AB'}, 'stats': b,
            'verdict': v, 'memory': mv, 'W_star_s': wstar, 'W_curve': curve}


# ---------------------------------------------------------------- one scenario

def fit_k0(k0, fold, F):
    js = [j for j in k0 if fold[j] == F]
    best = None
    for s in S_TGT:
        for T in T_REC:
            m = float(np.median([k0[j][(s, T)][0] for j in js]))
            if best is None or m < best[0]:
                best = (m, s, T)
    return best[1], best[2], best[0]


def fit_g(tab, fold, F, s, T, c, gg):
    js = [j for j in tab if fold[j] == F]
    best = None
    for g in gg:
        m = float(np.median([tab[j][(s, T, c, g)][0] for j in js]))
        if best is None or m < best[0]:
            best = (m, g)
    return best[1], best[0]


def run_scenario(name, jobs, rows, ex, cache, primary):
    sc = dict(BASE, **SCENARIOS[name])
    fold = {r['idx']: r['fold'] for r in rows}
    ids = sorted(jobs)
    k0, pl = {}, {}
    for idx, p, d in ex.map(job_k0, [(i, *jobs[i], sc) for i in ids]):
        k0[idx], pl[idx] = d, p
    fit = {F: {'K0': fit_k0(k0, fold, F)} for F in 'AB'}
    pairs = sorted({fit[F]['K0'][:2] for F in 'AB'})
    tab = {}
    for idx, d in ex.map(job_ctrl, [(i, *jobs[i], sc, pairs, cache) for i in ids]):
        tab[idx] = d
    for F in 'AB':
        s, T, _ = fit[F]['K0']
        for c, _, gg in ctrl_grid():
            fit[F][c] = fit_g(tab, fold, F, s, T, c, gg)
    other = {'A': 'B', 'B': 'A'}
    ev = {}
    for j in ids:
        F = other[fold[j]]           # parameters come from the fold j is not in
        s, T, _ = fit[F]['K0']
        e = {'K0': k0[j][(s, T)]}
        cfg = {'K0': ('K0', s, T, 0.0)}
        for c, fk, _ in ctrl_grid():
            if c.startswith('K1sh_') or c == 'K1rsh':
                base_c = 'K1_' + c.split('_')[1] if c.startswith('K1sh_') else 'K1r'
                g = fit[F][base_c][0]                   # deciding: K1's (K1-r's) fitted g, unchanged
                e[c] = tab[j][(s, T, c, g)]
                cfg[c] = (fk, s, T, g)
                go = fit[F][c][0]
                e[c + '_own'] = tab[j][(s, T, c, go)]
                cfg[c + '_own'] = (fk, s, T, go)
            else:
                g = fit[F][c][0]
                e[c] = tab[j][(s, T, c, g)]
                cfg[c] = (fk, s, T, g)
        ev[j] = {'Estar': {k: v[0] for k, v in e.items()}, 'flag': {k: v[1] for k, v in e.items()}, 'cfg': cfg}
    keys = list(ev[ids[0]]['Estar'])
    G = {k: {j: ev[j]['Estar']['K0'] / ev[j]['Estar'][k] for j in ids} for k in keys if k != 'K0'}
    # evaluation pass: monotonicity, dynamic range, example traces
    tasks = []
    for j in ids:
        cfgs = {k: (*ev[j]['cfg'][k], ev[j]['Estar'][k]) for k in keys}
        tasks.append((j, *jobs[j], sc, cfgs, cache, primary and j in EXAMPLE_IDX))
    traces = {}
    for idx, res, tr in ex.map(job_eval, tasks):
        ev[idx]['eval'] = res
        if tr is not None:
            traces[idx] = tr
    model = {r['idx']: r['model'] for r in rows}
    seg = 'full' if sc['seg'] == 'whole' else 'active'
    pops = {
        'llama2_70b_lora': [j for j in ids if model[j] == 'llama2_70b_lora'],
        'stable_diffusion': [j for j in ids if model[j] == 'stable_diffusion'],
        'pooled_41': ids,
        'gated_20': [r['idx'] for r in rows if r['active']['gate']],
        'periodic': [r['idx'] for r in rows if r[seg]['periodic']],
    }
    out = {'spec': sc, 'fit': {F: {k: list(v) for k, v in fit[F].items()} for F in 'AB'},
           'populations': {k: readout(v, fold, G) for k, v in pops.items()},
           'censored': {k: sum(ev[j]['flag'][k] == 'cens' for j in ids) for k in keys},
           'floored': {k: sum(ev[j]['flag'][k] == 'floor' for j in ids) for k in keys},
           'mono_count_increase': {k: sum(ev[j]['eval'][k]['mono_count_increase'] for j in ids) for k in keys},
           'mono_passfail_flip': {k: sum(ev[j]['eval'][k]['mono_passfail_flip'] for j in ids) for k in keys},
           'dyn_range_median': {k: float(np.median([ev[j]['eval'][k]['dyn_range_at_Estar'] for j in ids]))
                                for k in keys},
           'jobs': {str(j): {'model': model[j], 'fold': fold[j], 'plant': pl[j], 'Estar': ev[j]['Estar'],
                             'flag': ev[j]['flag'], 'cfg': {k: list(v) for k, v in ev[j]['cfg'].items()},
                             'eval': ev[j]['eval']} for j in ids}}
    return out, traces


# ---------------------------------------------------------------- report + plots

def line(name, r):
    s = r['stats']
    f = lambda k: f"{s[k]['point']:.3f} [{s[k]['ci95'][0]:.3f}, {s[k]['ci95'][1]:.3f}]"
    return (f"  {name:18s} n={r['n']:2d}  G={f('G')}  G_sh={s['G_sh']['point']:.3f}  G_inf={s['G_inf']['point']:.3f}"
            f"  G_r={s['G_r']['point']:.3f}  M={f('M')}  W*={r['W_star_s']}s  -> {r['verdict']} / {r['memory']}")


def plots(res, traces, rows, outdir):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    pr = res['scenarios']['primary']
    jobs = pr['jobs']
    order = sorted(jobs, key=lambda j: (jobs[j]['model'], jobs[j]['Estar']['K0']))
    fig, ax = plt.subplots(figsize=(14, 5))
    x = np.arange(len(order))
    for k, m in (('K0', 'o'), (f'K1_{W_PRIMARY}', 's'), (f'K1sh_{W_PRIMARY}', 'x'), ('K1r', '^'), ('Kinf', 'v')):
        ax.scatter(x, [jobs[j]['Estar'][k] for j in order], marker=m, s=22, label=k, alpha=.8)
    nl = sum(jobs[j]['model'] == 'llama2_70b_lora' for j in order)
    ax.axvline(nl - .5, color='k', lw=.8)
    ax.text(nl / 2, ax.get_ylim()[1], 'Llama-2-70B LoRA', ha='center', va='bottom')
    ax.text(nl + (len(order) - nl) / 2, ax.get_ylim()[1], 'Stable Diffusion', ha='center', va='bottom')
    ax.set_yscale('log'); ax.set_xticks(x); ax.set_xticklabels(order, fontsize=7)
    ax.set_xlabel('job idx'); ax.set_ylabel('E* (P_max x 1 s)')
    ax.legend(fontsize=8, ncol=5)
    ax.set_title('DC1 E* per job, out of fold, primary spec. DERIVED from SOURCED traces under ASSUMED specs.', pad=18)
    plt.tight_layout(); plt.savefig(os.path.join(outdir, 'dc1_estar.png'), dpi=80); plt.close(fig)

    fig, ax = plt.subplots(1, 2, figsize=(12, 4.5), sharey=True)
    for a, m in zip(ax, ('llama2_70b_lora', 'stable_diffusion')):
        r = pr['populations'][m]
        s = r['stats']
        Wk = [5, 30, 60]
        a.plot([1] + Wk, [s['G_r']['point']] + [s[f'G_W{W}']['point'] for W in Wk], 'o-', label='K1 (1 s: K1-r)')
        a.plot([1] + Wk, [s['G_r_sh']['point']] + [s[f'G_sh_W{W}']['point'] for W in Wk], 'x--',
               label='shuffled (1 s: K1-r-sh)')
        a.plot(1, s['G_W1']['point'], 'k.', label='K1 at 1 s (= 1 by construction)')
        a.axhline(s['G_inf']['point'], color='C2', ls=':', label=f"G_inf (H_p 5 s) = {s['G_inf']['point']:.2f}")
        a.axhline(SAVES_G, color='k', lw=.6, ls='--'); a.axhline(REACTIVE_G, color='k', lw=.6, ls='-.')
        lo, hi = s['G']['ci95']
        a.vlines(30, lo, hi, color='C0', lw=3, alpha=.4)
        a.set_xscale('log'); a.set_xticks([1, 5, 30, 60]); a.set_xticklabels(['1', '5', '30', '60'])
        a.set_xlabel('history window W (s)'); a.set_title(f"{m}: {r['verdict']}", fontsize=9)
        a.legend(fontsize=7)
    ax[0].set_ylabel('median G = E*(K0)/E*(K1), mean of fold medians')
    fig.suptitle('DC1 memory readout. DERIVED from SOURCED traces (NLR, CC BY 4.0) under ASSUMED specs.', fontsize=10)
    plt.tight_layout(); plt.savefig(os.path.join(outdir, 'dc1_G_vs_W.png'), dpi=80); plt.close(fig)

    fig, ax = plt.subplots(2, 2, figsize=(14, 8))
    for k, idx in enumerate(sorted(traces)):
        tr = traces[idx]
        P, dt = tr['P'], tr['dt']
        n = int(120 / dt)
        a0 = len(P) // 2
        tt = np.arange(n) * dt
        a = ax[k, 0]
        a.plot(tt, P[a0:a0 + n] / tr['Pmax'], 'k', lw=.8, label='P_load')
        for name, c in (('K0', 'C0'), (f'K1_{W_PRIMARY}', 'C1'), ('Kinf', 'C2')):
            a.plot(tt, tr[name]['pup'][a0:a0 + n] / tr['Pmax'], c, lw=.9,
                   label=f"P_up {name} ({tr[name]['viol']} viol. in job)")
        a.set_ylabel('P / P_max'); a.legend(fontsize=7)
        a.set_title(f"job {idx} ({jobs[str(idx)]['model']}), E = E*(K0) = {tr['E']:.2f} P_max s, 120 s mid-segment",
                    fontsize=9)
        b = ax[k, 1]
        for name, c in (('K0', 'C0'), (f'K1_{W_PRIMARY}', 'C1'), ('Kinf', 'C2')):
            b.plot(tt, tr[name]['soe'][a0:a0 + n], c, lw=.9, label=name)
        b.set_ylabel('SoE / E'); b.set_ylim(-.02, 1.02); b.legend(fontsize=7)
    ax[1, 0].set_xlabel('s'); ax[1, 1].set_xlabel('s')
    fig.suptitle('DC1 example traces. DERIVED from SOURCED traces under ASSUMED specs (R = 0.10/s, lossless).',
                 fontsize=10)
    plt.tight_layout(); plt.savefig(os.path.join(outdir, 'dc1_traces.png'), dpi=80); plt.close(fig)


def main(root, outdir, workers):
    meta, jobs = load_training(root)
    prof = json.load(open(os.path.join(outdir, 'profile.json')))
    rows = prof['jobs']
    tmp = tempfile.mkdtemp(prefix='dc1_')
    try:
        so = build_lib(tmp)
        lib(so)
        ok, grep = gate(jobs, dict(BASE))
        print('gate', 'PASS' if ok else 'FAIL')
        for g in grep:
            print('  ', json.dumps(g, default=_js))
        if not ok:
            json.dump({'gate_pass': False, 'gate': grep}, open(os.path.join(outdir, 'dc1.json'), 'w'), indent=1, default=_js)
            sys.exit('C/Python gate failed; no E* reported')
        res = {'gate_pass': True, 'gate': grep,
               'constants': {'S_TGT': S_TGT, 'T_REC': T_REC, 'G_GRID': G_GRID, 'G_INF': G_INF, 'WS': WS,
                             'W_PRIMARY': W_PRIMARY, 'RHO_MIN': RHO_MIN, 'LMIN_S': LMIN_S, 'HP_S': HP_S,
                             'RAMP_S': RAMP_S, 'E_bounds': [E_LO, E_HI], 'BIS_TOL': BIS_TOL, 'NBOOT': NBOOT,
                             'BOOT_SEED': BOOT_SEED, 'thresholds': {'SAVES_G': SAVES_G, 'SAVES_LO': SAVES_LO,
                                                                    'SH_MAX': SH_MAX, 'REACTIVE_G': REACTIVE_G,
                                                                    'M_BAR': M_BAR, 'WSTAR_FRAC': WSTAR_FRAC},
                             'BASE': BASE, 'SCENARIOS': SCENARIOS},
               'tags': 'Every number DERIVED from SOURCED traces (NLR GenAI power profiles, CC BY 4.0) under ASSUMED '
                       'specs.',
               'scenarios': {}}
        cache = os.path.join(tmp, 'fc')
        os.makedirs(cache)
        traces = {}
        with ProcessPoolExecutor(workers, initializer=_init, initargs=(so,)) as ex:
            for name in SCENARIOS:
                r, tr = run_scenario(name, jobs, rows, ex, cache, name == 'primary')
                res['scenarios'][name] = r
                traces.update(tr)
                print(name, json.dumps(r['fit'], default=_js))
                for pn, pr in r['populations'].items():
                    print(line(pn, pr))
                print('   censored', r['censored'])
                print('   mono(count incr)', r['mono_count_increase'], 'mono(pass/fail flip)', r['mono_passfail_flip'])
                sys.stdout.flush()
        with open(os.path.join(outdir, 'dc1.json'), 'w') as f:
            json.dump(res, f, indent=1, default=_js)
        plots(res, traces, rows, outdir)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == '__main__':
    a = sys.argv[1:]
    w = 16
    if '--workers' in a:
        k = a.index('--workers')
        w = int(a[k + 1])
        del a[k:k + 2]
    main(a[0], a[1], w)
