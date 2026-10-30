"""X2-F fine-grid exploration (EXPLORATORY, POST-HOC on data X2-C and X2-F already used; not a test).
X2-F (results/X/X2F/results_X2F.md) showed S jumps with the 0.05 kappa grid (+0.6 % to +4.2 %). This re-runs X2-F's
base definitions unchanged on a 0.01 grid (1.00-2.00) to size the gain, for deciding whether a confirmation on new
data is worth seeking. Reports, per calibration tolerance, kappa, held-out unsafe and S / S_sh / D; plus an ORACLE
row with each kappa picked on the evaluation half itself. Every number DERIVED, limits ASSUMED. Beihang CC BY 4.0.
Usage: python -E analysis/X2F_finegrid.py [--jobs 10]   (writes results/X/X2F/x2f_finegrid.json)
"""
import argparse
import json
import os
import sys
from multiprocessing import Pool

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import X2F_replay as F                                   # noqa: E402

F.KAPPAS = np.round(np.arange(1.00, 2.0001, 0.01), 2)    # set before the pool forks
TOLS = (1e-4, 5e-4, 1e-3, 2e-3)


def summarise(R, fleet):
    rng = np.random.default_rng(0)
    out = {}
    for tol in TOLS:
        d = F.analyse(R, fleet, "base", tol=tol, rng=rng)
        out[f"tol{tol * 100:g}%"] = {k: v for k, v in d.items() if not k.startswith(("_", "kappa_curve"))}
    # ORACLE: each limiter's kappa = smallest with realised EVALUATION unsafe <= 0.1 % (picked on the scored half)
    d = F.analyse(R, fleet, "base", rng=rng)
    ev = set(F.C.SPLIT[fleet]["evaluation"])
    se = [(x["veh"], s) for x in R if x["fleet"] == fleet and x["veh"] in ev for s in x["sessions"]]
    ik = {lim: int(np.flatnonzero(np.array(d[f"kappa_curve_eval_{lim}"]) <= 1e-3)[0]) for lim in F.LIMS}
    prim = [(vh, s) for vh, s in se if s["gap_mv"] <= 50.0]
    tm = np.array([s["t"][0, ik["mm"]] for _, s in prim])
    S = 1 - np.array([s["t"][1, ik["cell"]] for _, s in prim]) / tm
    Ssh = 1 - np.array([s["t"][2, ik["sh"]] for _, s in prim]) / tm
    g = np.array([vh for vh, _ in prim])
    out["ORACLE_eval0.1%"] = {**{f"kappa_{l}": float(F.KAPPAS[ik[l]]) for l in F.LIMS},
                              "S_median": float(np.median(S)), "S_CI": F.C.boot(S, g, rng),
                              "S_shuffle_median": float(np.median(Ssh)), "D_median": float(np.median(S - Ssh)),
                              "D_CI": F.C.boot(S - Ssh, g, rng), "n_primary": len(prim)}
    out["kappa_curves"] = {f"{h}_{l}": d[f"kappa_curve_{h}_{l}"] for h in ("cal", "eval") for l in F.LIMS}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=10)
    a = ap.parse_args()
    jobs = [(f, n, "base") for f in ("QAS", "DTI") for part in ("calibration", "evaluation") for n in F.C.SPLIT[f][part]]
    with Pool(a.jobs) as p:
        R = p.map(F.vehicle, jobs, chunksize=4)
    res = {"tag": "EXPLORATORY, POST-HOC on seen Beihang data (CC BY 4.0); DERIVED; limits ASSUMED; not a test",
           "kappas": F.KAPPAS.tolist(), "QAS": summarise(R, "QAS"), "DTI": summarise(R, "DTI")}
    json.dump(res, open(f"{F.OUT}/x2f_finegrid.json", "w"), indent=1, default=float)
    print(json.dumps({f: {k: v for k, v in res[f].items() if k != "kappa_curves"} for f in ("QAS", "DTI")},
                     indent=1, default=float))


if __name__ == "__main__":
    main()
