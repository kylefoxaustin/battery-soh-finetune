"""Experiment E §3 — power analysis, Yuasa part. Reads the per-cell (Q, Q_sigma) exported by the paper's own
324-cell joint fit (validation_cells.json). These are MODEL ESTIMATES from a 12.5 h field window (paper §Methods);
the paper's reference check (96 cells, same onboard sensors) gives 1.25 Ah absolute / 0.55 Ah module-centred RMSE
and states the absolute capacity scale is unverified. Tag: DERIVED from SOURCED estimates.
Usage: python analysis/E_power_yuasa.py --out results/E/power_yuasa.json
"""
import argparse
import json
from collections import defaultdict

import numpy as np

SRC = "data/raw/yuasa/src/martincornejo-BatteryRecursiveGPs.jl-e330f2d/yuasa/data/validation/validation_cells.json"
ALPHAS = [0.10, 0.05, 0.01, 0.001]

ap = argparse.ArgumentParser()
ap.add_argument("--out", required=True)
a = ap.parse_args()
cells = json.load(open(SRC))["cells"]
mods = defaultdict(list)
for c in cells:
    p, m, _ = c["id"].split("_")
    mods[(int(p), int(m))].append((c["Q"], c["Q_sigma"]))
Q = np.array([c["Q"] for c in cells]); S = np.array([c["Q_sigma"] for c in cells])
mmin = np.array([min(q for q, _ in v) for v in mods.values()])
mmean = np.array([np.mean([q for q, _ in v]) for v in mods.values()])
heter = 100 * (mmean - mmin) / mmean
out = {"tag": "DERIVED from SOURCED per-cell model estimates", "n_cells": len(Q), "n_modules": len(mods),
       "cells_per_module": sorted({len(v) for v in mods.values()}),
       "Q_median": float(np.median(Q)), "Q_min": float(Q.min()), "Q_max": float(Q.max()),
       "Q_between_cell_sd": float(Q.std(ddof=1)),
       "Q_between_cell_sd_excl_2_faulty": float(np.sort(Q)[2:].std(ddof=1)),
       "Q_sigma_median": float(np.median(S)), "Q_sigma_median_pct": float(100 * np.median(S / Q)),
       "Q_sigma_max": float(S.max()),
       "ref_check_rmse_abs_ah_SOURCED": 1.25, "ref_check_rmse_module_centred_ah_SOURCED": 0.55,
       "module_mean_minus_min_pct": {"median": float(np.median(heter)), "min": float(heter.min()),
                                     "max": float(heter.max()), "per_module": [round(float(x), 2) for x in heter]},
       "coverage_verifiability": {str(al): {"units": len(mods), "expected_violations": len(mods) * al,
                                            "P_zero_violations_if_calibrated": float((1 - al) ** len(mods))}
                                  for al in ALPHAS},
       "time_axis": "single 12.5 h snapshot; one capacity estimate per cell; no forecast origin/horizon possible"}
print(json.dumps(out, indent=1))
json.dump(out, open(a.out, "w"), indent=1)
