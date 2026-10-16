"""Experiment H2-a (pre-registered in results/H2/H2_preregistration.md, commit bf6ca52, before this script existed).
H-a counterfactual replay re-run on the Weihai 9 x 396-cell LFP BESS (Zenodo 20094787, CC BY 4.0).
Stage 1 (extract): per Charge operation and rack, 10 s zero-order-hold grid of 396 cell V + 216 probe T + dAh.
Stage 2 (replay): per-cell vs min/max vs pack-mean limiters, as in analysis/H_replay.py with the LFP voltage taper.
Every number DERIVED; every limit ASSUMED.
Usage: python analysis/H2_replay.py extract [--jobs 8]
       python analysis/H2_replay.py replay --out results/H2 [--jobs 10]
"""
import argparse
import glob
import json
import os
import sys
from multiprocessing import Pool

import h5py
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mcos_dt  # noqa: E402

RAW = "data/raw/weihai"
FR = "data/weihai/frames"
NC, NP, NR = 396, 216, 9
GRID_S, GAP_I, MIN_FRAMES = 10.0, 60.0, 30
CT_T = np.array([-20, 0, 10, 25, 40, 50, 60], float)
CT_C = np.array([0.05, 0.2, 0.6, 1.5, 1.5, 0.8, 0.0])
KNEE_V, END_V, CUT_V, TAPER_END = 3.40, 3.60, 3.65, 0.05
M_MV = [0, 5, 10, 20, 30, 50, 75, 100]
M_T = [0, 2, 5, 10]
N_PERM = 100
UNSAFE_TOL = 1.001
BANDS = [(-99, 10), (10, 20), (20, 25), (25, 40), (40, 99)]


# ---------------------------------------------------------------- stage 1: extraction
def _series(f, refs, cells, g):
    return mcos_dt.dt_ms(f, refs, cells, g["t"][()]) / 1e3, g["value"][()].ravel()


def _zoh(t, v, grid):
    i = np.searchsorted(t, grid, side="right") - 1
    return v[np.clip(i, 0, None)]


def _cum_ah(t, i_a):
    """cumulative charged Ah from rack current samples (charge negative); gaps > GAP_I contribute 0"""
    q = np.clip(-i_a, 0, None)
    dt = np.diff(t)
    inc = np.where(dt <= GAP_I, 0.5 * (q[1:] + q[:-1]) * dt / 3600.0, 0.0)
    return np.concatenate([[0.0], np.cumsum(inc)])


def extract_file(fn):
    f = h5py.File(fn, "r")
    refs, cells, *_ = mcos_dt.obj_cells(f)
    top = [k for k in f.keys() if not k.startswith("#")][0]
    G = f[top]
    n_out = 0
    for op in G.keys():
        g = G[op]
        if "".join(map(chr, g["Type"][()].ravel())) != "Charge":
            continue
        st = mcos_dt.dt_ms(f, refs, cells, g["StartTime"][()])[0] / 1e3
        en = mcos_dt.dt_ms(f, refs, cells, g["EndTime"][()])[0] / 1e3
        tag = f"{top[-10:-4]}_{op}"
        for r in range(1, NR + 1):
            out = f"{FR}/{tag}_rack{r}.npz"
            if os.path.exists(out):
                n_out += 1
                continue
            R = g[f"Rack{r}"]
            Vs = [_series(f, refs, cells, R[f"Voltage{k}"]) for k in range(1, NC + 1)]
            Ts = [_series(f, refs, cells, R[f"Temperature{p}"]) for p in range(1, NP + 1)]
            t0 = max([s[0][0] for s in Vs] + [s[0][0] for s in Ts])
            grid = np.arange(max(st, t0), en, GRID_S)
            ti, ii = _series(f, refs, cells, {"t": g[f"Rack{r}CurrentTime"], "value": g[f"Rack{r}CurrentValue"]})
            if len(grid) < MIN_FRAMES or len(ti) < 2:
                np.savez_compressed(out, empty=True)
                continue
            V = np.stack([_zoh(t, v, grid) for t, v in Vs], 1)
            T = np.stack([_zoh(t, v, grid) for t, v in Ts], 1)
            cah = np.interp(grid, ti, _cum_ah(ti, ii))
            dah = np.diff(cah, prepend=cah[0])
            np.savez_compressed(out, V=np.rint(V * 1e3).astype(np.int16), T=T.astype(np.float32), dah=dah,
                                grid=grid, i_med=float(np.median(ii)))
            n_out += 1
    return fn, n_out


# ---------------------------------------------------------------- stage 2: replay
def c_t(T, shift=0.0):
    return np.interp(T, CT_T + shift, CT_C)


def taper(mv, knee=KNEE_V):
    v = mv / 1e3
    lin = 1.0 - (1.0 - TAPER_END) * (v - knee) / (END_V - knee)
    return np.where(v >= CUT_V, 0.0, np.where(v <= knee, 1.0, np.clip(lin, TAPER_END, 1.0)))


def perms():
    base = (np.arange(NC) * NP) // NC
    return np.array([base] + [np.random.default_rng(s).permutation(base) for s in range(N_PERM)])


PMAPS = perms()


def limiters(V, T, shift=0.0, knee=KNEE_V, maps=PMAPS):
    ts = taper(V, knee)
    ctp = c_t(T, shift)
    Lcell = np.empty((len(maps), len(ts)))
    for i, pm in enumerate(maps):
        Lcell[i] = (ctp[:, pm] * ts).min(1)
    Lmm = np.minimum(c_t(T.min(1), shift), c_t(T.max(1), shift)) * taper(V.max(1), knee)
    return Lmm, Lcell, ts, ctp


def t_of(dah, L):
    return float((dah / np.maximum(L, 1e-6)).sum())


def one(path):
    Z = np.load(path)
    if "empty" in Z:
        return None
    V, T, dah = Z["V"].astype(np.float64), Z["T"].astype(np.float64), np.clip(Z["dah"], 0, None)
    if len(dah) < MIN_FRAMES or dah.sum() < 0.5:
        return None
    op = os.path.basename(path).rsplit("_rack", 1)[0]
    Lmm, Lcell, ts, ctp = limiters(V, T)
    tmm, tcell = t_of(dah, Lmm), np.array([t_of(dah, L) for L in Lcell])
    s_mm = 1 - tcell / tmm
    pm = PMAPS[0]
    vals = ctp[:, pm] * ts
    lc = vals.min(1)
    r_ = np.arange(len(lc))
    tol = lc * 1e-9 + 1e-12
    imaxV, iminV = V.argmax(1), V.argmin(1)
    ext = (pm[None, :] == T.argmin(1)[:, None]) | (pm[None, :] == T.argmax(1)[:, None])
    s = {"op": op, "n": int(len(dah)), "ah": float(dah.sum()), "S_mm_M1": float(s_mm[0]), "S_mm_M2": s_mm[1:].tolist(),
         "n_diff": int((np.abs(Lcell[0] - Lmm) > 1e-9).sum()),
         "tw_not_vmax": int((vals[r_, imaxV] > lc + tol).sum()), "tw_not_vmin": int((vals[r_, iminV] > lc + tol).sum()),
         "tw_not_text": int((np.where(ext, vals, np.inf).min(1) > lc + tol).sum()),
         "tmin_med": float(np.median(T.min(1))), "tmax_med": float(np.median(T.max(1))),
         "tspread_med": float(np.median(T.max(1) - T.min(1))), "vmax_med": float(np.median(V.max(1))),
         "vspread_med": float(np.median(V.max(1) - V.min(1)))}
    vmean, tmean = V.mean(1), T.mean(1)
    sw = {}
    for m in M_MV:
        tsp = taper(vmean + m)
        for mT in M_T:
            Lp = np.minimum(c_t(tmean - mT), c_t(tmean + mT)) * tsp
            sw[f"{m}_{mT}"] = (1 - tcell[0] / t_of(dah, Lp), int((Lp > Lcell[0] * UNSAFE_TOL).sum()))
    s["sweep"] = sw
    sens = {}
    for name, kw in [("shift-5", {"shift": -5.0}), ("shift+5", {"shift": 5.0}), ("knee3.35", {"knee": 3.35}),
                     ("knee3.45", {"knee": 3.45})]:
        Lmm2, Lc2, *_ = limiters(V, T, maps=PMAPS[:1], **kw)
        sens[name] = 1 - t_of(dah, Lc2[0]) / t_of(dah, Lmm2)
    s["sens"] = sens
    return s


def replay(out_dir, jobs):
    paths = sorted(glob.glob(f"{FR}/*.npz"))
    with Pool(jobs) as p:
        ss = [s for s in p.imap_unordered(one, paths, chunksize=4) if s]
    ss.sort(key=lambda s: s["op"])
    ops = np.array([s["op"] for s in ss])
    sm1 = np.array([s["S_mm_M1"] for s in ss])
    sm2 = np.array([s["S_mm_M2"] for s in ss])
    med_m2_each = np.median(sm2, axis=0)
    rng = np.random.default_rng(0)
    uops = np.unique(ops)
    idx = {o: np.flatnonzero(ops == o) for o in uops}
    bs = [np.median(sm1[np.concatenate([idx[o] for o in rng.choice(uops, len(uops))])]) for _ in range(1000)]
    tot = lambda k: int(sum(s[k] for s in ss))
    nfr = tot("n")
    res = {"tag": "DERIVED (replay on MEASURED Weihai cell states; limit map, mapping, ZOH, trajectory ASSUMED); "
                  "CC BY 4.0", "preregistered_in": "bf6ca52", "n_sessions": len(ss), "n_operations": int(len(uops)),
           "n_frames": nfr, "ah_total": float(sum(s["ah"] for s in ss)),
           "S_mm_M1_median": float(np.median(sm1)), "S_mm_M1_CI": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))],
           "S_mm_M1_p90": float(np.percentile(sm1, 90)), "S_mm_M1_max": float(sm1.max()),
           "S_mm_M2_median_of_medians": float(np.median(med_m2_each)),
           "S_mm_M2_range_5_95": [float(np.percentile(med_m2_each, 5)), float(np.percentile(med_m2_each, 95))],
           "frac_frames_cell_ne_mm": tot("n_diff") / nfr,
           "tieaware_frac_vmax_cell_not_constraining": tot("tw_not_vmax") / nfr,
           "tieaware_frac_vmin_cell_not_constraining": tot("tw_not_vmin") / nfr,
           "tieaware_frac_no_extreme_T_probe_cell_constraining": tot("tw_not_text") / nfr}
    tmin = np.array([s["tmin_med"] for s in ss])
    res["temperature_bands"] = {}
    for lo, hi in BANDS:
        m = (tmin >= lo) & (tmin < hi)
        res["temperature_bands"][f"{lo}..{hi}"] = ({"sessions": int(m.sum()), "S_mm_median": float(np.median(sm1[m])),
                                                    "S_mm_p90": float(np.percentile(sm1[m], 90))}
                                                   if m.any() else {"sessions": 0})
    res["charging_temperature"] = {k: {"p5": float(np.percentile(v, 5)), "median": float(np.median(v)),
                                       "p95": float(np.percentile(v, 95))}
                                   for k, v in [("tmin", tmin), ("tmax", np.array([s["tmax_med"] for s in ss])),
                                                ("spread", np.array([s["tspread_med"] for s in ss]))]}
    res["charging_voltage"] = {"vmax_med_mV": float(np.median([s["vmax_med"] for s in ss])),
                               "vspread_med_mV": float(np.median([s["vspread_med"] for s in ss]))}
    sweep = {}
    for m in M_MV:
        for mT in M_T:
            k = f"{m}_{mT}"
            sweep[k] = {"S_pack_median": float(np.median([s["sweep"][k][0] for s in ss])),
                        "unsafe_frac": sum(s["sweep"][k][1] for s in ss) / nfr}
    res["margin_sweep"] = sweep
    safe = [(m, mT) for m in M_MV for mT in M_T if sweep[f"{m}_{mT}"]["unsafe_frac"] <= 0.001]
    res["safe_margins"] = [f"{m}_{mT}" for m, mT in safe]
    res["sensitivity_M1"] = {n: float(np.median([s["sens"][n] for s in ss])) for n in ss[0]["sens"]}
    v1, v2 = res["S_mm_M1_median"] >= 0.01, res["S_mm_M2_median_of_medians"] >= 0.01
    if not v1 and not v2:
        res["decision"] = "NO BENEFIT over min/max"
    elif v1 and v2 and res["S_mm_M1_CI"][0] > 0:
        res["decision"] = "PER-CELL RECOVERS X"
    else:
        res["decision"] = "NOT ANSWERABLE from replay (mapping-dependent)"
    os.makedirs(out_dir, exist_ok=True)
    json.dump(res, open(f"{out_dir}/replay.json", "w"), indent=1)
    np.savez_compressed(f"{out_dir}/replay_sessions.npz", op=ops, S_mm_M1=sm1, S_mm_M2_med=np.median(sm2, 1),
                        tmin=tmin, tspread=np.array([s["tspread_med"] for s in ss]))
    print(json.dumps({k: v for k, v in res.items() if k != "margin_sweep"}, indent=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["extract", "replay"])
    ap.add_argument("--out", default="results/H2")
    ap.add_argument("--jobs", type=int, default=8)
    a = ap.parse_args()
    if a.mode == "extract":
        os.makedirs(FR, exist_ok=True)
        with Pool(a.jobs) as p:
            for fn, n in p.imap_unordered(extract_file, sorted(glob.glob(f"{RAW}/*.mat"))):
                print(fn, n, flush=True)
    else:
        replay(a.out, a.jobs)


if __name__ == "__main__":
    main()
