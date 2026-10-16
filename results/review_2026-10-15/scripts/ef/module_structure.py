"""Review prototype of a MISSED analysis: infer module / sense-board structure from the per-cell data.
 (1) 96x96 correlation of per-cell rest deviations (daily means, to suppress frame noise) -> block structure:
     for each candidate block size (8, 12, 16, 24, 32) compute mean within-block minus between-block correlation
     for each phase offset; the best (size, offset) is the inferred module geometry.
 (2) cell -> temperature-probe mapping: correlation of each cell's dv with each probe's dt over all full vectors.
 (3) adjacent-cell correlation profile corr(k, k+1): dips mark boundaries.
Usage: python -I module_structure.py <cells_dir> <out_json> vin [vin ...]
"""
import json
import sys

import numpy as np

cells_dir, out = sys.argv[1], sys.argv[2]
res = {}
for car in sys.argv[3:]:
    C = np.load(f"{cells_dir}/vin{car}.npz")
    t, I, tf, dv, dt = C["t"], C["I"], C["t_full"], C["dv_full"], C["dt_full"]
    j = np.clip(np.searchsorted(t, tf), 0, len(t) - 1)
    rest = (t[j] == tf) & (np.abs(I[j]) < 1.0)
    day = (tf[rest] // 86400).astype(np.int64)
    ud, inv, cnt = np.unique(day, return_inverse=True, return_counts=True)
    M = np.zeros((len(ud), 96)); np.add.at(M, inv, dv[rest].astype(np.float64)); M /= cnt[:, None]
    M = M[cnt >= 20]
    Md = M - M.mean(0)                              # remove each cell's persistent offset
    # remove the day-level common mode already zero (dv sums to 0); correlation of day-to-day fluctuations
    R = np.corrcoef(Md.T)
    np.fill_diagonal(R, np.nan)
    adj = np.array([R[k, k + 1] for k in range(95)])
    best = []
    for size in (6, 8, 12, 16, 24, 32, 48):
        for off in range(size):
            blk = ((np.arange(96) + off) // size)
            same = blk[:, None] == blk[None, :]
            w = np.nanmean(R[same]); b = np.nanmean(R[~same])
            best.append((float(w - b), size, off))
    best.sort(reverse=True)
    # cell->probe mapping over ALL full vectors (thermal gradients during driving/charging)
    sub = slice(None, None, max(1, len(tf) // 60000))
    X = dv[sub].astype(np.float64); Y = dt[sub].astype(np.float64)
    X -= X.mean(0); Y -= Y.mean(0)
    Cxy = (X.T @ Y) / len(X)
    Cxy /= (X.std(0)[:, None] * Y.std(0)[None, :] + 1e-9)
    probe_of_cell = Cxy.argmax(1)
    res[car] = {"n_days": int(len(M)), "adjacent_corr": np.round(adj, 3).tolist(),
                "weakest_adjacent_links(k,k+1)": [int(k) for k in np.argsort(adj)[:8]],
                "best_block_geometries(within-between, size, offset)": [(round(a, 3), s, o) for a, s, o in best[:6]],
                "probe_of_cell": probe_of_cell.tolist(), "cells_per_probe": np.bincount(probe_of_cell, minlength=32).tolist(),
                "corr_cell31_with_neighbors": [float(R[31, 30]), float(R[31, 32])],
                "mean_offdiag_corr": float(np.nanmean(R))}
    print(car, {k: v for k, v in res[car].items() if k not in ("adjacent_corr", "probe_of_cell")}, flush=True)
    print("  adjacent corr:", " ".join(f"{k}:{a:.2f}" for k, a in enumerate(adj)), flush=True)
json.dump(res, open(out, "w"))
