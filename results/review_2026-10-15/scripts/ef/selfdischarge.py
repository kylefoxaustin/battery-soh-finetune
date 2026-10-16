"""Review prototype of a MISSED analysis: per-cell relative self-discharge across long parking gaps.
For each gap in the summary timeline >= GAP_H hours, take the last rest full vector within PRE_S before the gap and
the first rest full vector within POST_S after the wake; delta_k = dv_after - dv_before (mV, relative to pack mean).
Per cell: OLS of delta on gap duration -> slope (mV/h = relative self-discharge; a relaxation offset goes to the
intercept). Flag cells whose slope is < -3 robust SD of the pack's 96 slopes.
Usage: python -I selfdischarge.py <cells_dir> <out_json> vin [vin ...]
"""
import json
import sys

import numpy as np

GAP_H, PRE_S, POST_S, REST_A = 6.0, 180.0, 180.0, 1.0
cells_dir, out = sys.argv[1], sys.argv[2]
res = {}
for car in sys.argv[3:]:
    C = np.load(f"{cells_dir}/vin{car}.npz")
    t, I, tf, dv = C["t"], C["I"], C["t_full"], C["dv_full"]
    gaps = np.flatnonzero(np.diff(t) >= GAP_H * 3600)
    rows, hrs, wake_i = [], [], []
    for g in gaps:
        t0, t1 = t[g], t[g + 1]
        if abs(I[g]) >= REST_A or abs(I[g + 1]) >= REST_A:
            continue
        a = np.searchsorted(tf, t0 - PRE_S); b = np.searchsorted(tf, t0, side="right")
        c = np.searchsorted(tf, t1); d = np.searchsorted(tf, t1 + POST_S, side="right")
        if b <= a or d <= c:
            continue
        before, after = dv[b - 1].astype(np.float64), dv[c].astype(np.float64)
        rows.append(after - before); hrs.append((t1 - t0) / 3600.0)
    if len(rows) < 30:
        res[car] = {"n_gaps": len(rows)}; continue
    Y, h = np.array(rows), np.array(hrs)
    X = np.c_[np.ones(len(h)), h]
    beta, *_ = np.linalg.lstsq(X, Y, rcond=None)
    sl, ic = beta[1], beta[0]
    mad = 1.4826 * np.median(np.abs(sl - np.median(sl))) + 1e-9
    z = (sl - np.median(sl)) / mad
    # per-cell median delta for long gaps (>= 24 h) as a robust alternative
    long = h >= 24
    med_long = np.median(Y[long], 0) if long.sum() >= 10 else np.full(96, np.nan)
    res[car] = {"n_gaps": int(len(h)), "gap_h_p50_p90_max": np.percentile(h, [50, 90, 100]).round(1).tolist(),
                "slope_mv_per_h": np.round(sl, 4).tolist(), "intercept_mv": np.round(ic, 2).tolist(),
                "slope_mad_mv_per_h": float(mad), "flagged_cells_z_lt_-3": [int(k) for k in np.flatnonzero(z < -3)],
                "worst_cell": int(sl.argmin()), "worst_slope_mv_per_h": float(sl.min()), "worst_z": float(z.min()),
                "n_long_gaps": int(long.sum()), "median_delta_long_gaps_worst_cell": ([int(np.nanargmin(med_long)), float(np.nanmin(med_long))] if np.isfinite(med_long).any() else None)}
    print(car, {k: v for k, v in res[car].items() if k not in ("slope_mv_per_h", "intercept_mv")}, flush=True)
json.dump(res, open(out, "w"))
