"""X2 shuffle diagnostic (POST-HOC, Changan already seen; not a confirmation). Asked for after X2-C (results_X2C.md)
showed that a per-cell limiter given another cell's R gains as much as the real one. Re-scores X2's POST-HOC
'all sessions with history' subset (+5.5 %) at X2's calibrated kappa_mm = 1.65, M1 mapping, base variant, with each
vehicle's R_k vector permuted once (default_rng(car)), exactly as X2-C did. Every number DERIVED; limits ASSUMED.
Changan is CC BY-NC-SA 4.0 (non-commercial).
Usage: python -E analysis/X2_shuffle_diag.py [--jobs 10]   (writes results/X/X2/x2_shuffle_diag.json)
"""
import argparse
import json
import os
import sys
from multiprocessing import Pool

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import H_replay as H                                     # noqa: E402
import X2_replay as X                                    # noqa: E402

KAPPA = 1.65                                             # X2 base kappa_mm (x2_changan.json)


def one(car):
    S = [f for f in X.changan_sessions(car) if f["dah"].sum() > 0.5]
    if not S:
        return {"car": car, "rows": []}
    hist = X.changan_history(car, 0.3)
    if hist["r"].size == 0:
        hist["r"] = np.zeros((0, 96))
    pm = H.PMAPS[0]
    floor = X.FLOOR_C * X.QREF_C
    rows = []
    perm = None
    for f in S:
        R, Rmm, nst, ok = X.r_from(hist, f["t0"], 30 * 86400.0)
        if not ok:
            continue
        R, Rmm = X._clean(R, Rmm)
        if perm is None or len(perm) != len(R):
            perm = np.random.default_rng(int(car)).permutation(len(R))
        V, Tc, Ic, dah = f["V"], f["T"], f["Ic"], f["dah"]
        ctQ = H.c_t(Tc)[:, pm] * X.QREF_C
        ct_lo = np.minimum(H.c_t(Tc.min(1)), H.c_t(Tc.max(1)))
        Lc = np.maximum(np.minimum(ctQ, X.head_k(V, Ic, R)).min(1), floor)
        Ls = np.maximum(np.minimum(ctQ, X.head_k(V, Ic, R[perm])).min(1), floor)
        Lm = np.maximum(np.minimum(ct_lo * X.QREF_C, X.head_mm(V.max(1), Ic, Rmm, KAPPA)), floor)
        tm = X.t_of(dah, Lm)
        rows.append((1 - X.t_of(dah, Lc) / tm, 1 - X.t_of(dah, Ls) / tm, len(dah),
                     int((Lm > Lc * X.UNSAFE_TOL).sum()), int((Ls > Lc * X.UNSAFE_TOL).sum()),
                     float(np.median(Tc.min(1)))))
    return {"car": car, "rows": rows}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=10)
    a = ap.parse_args()
    cars = sorted(int(f[3:-4]) for f in os.listdir(H.CELLS) if f.startswith("vin") and f[3:-4].isdigit())
    with Pool(a.jobs) as p:
        R = [r for r in p.imap_unordered(one, cars) if r["rows"]]
    car = np.concatenate([np.full(len(r["rows"]), r["car"]) for r in R])
    A = np.concatenate([np.array(r["rows"], float) for r in R])
    S, Ssh, n, um, ush, tmin = A.T
    rng = np.random.default_rng(0)
    d = S - Ssh
    out = {"tag": "DERIVED, POST-HOC diagnostic on seen Changan data (CC BY-NC-SA 4.0); limits ASSUMED",
           "kappa_mm": KAPPA, "n_sessions": int(len(S)), "n_vehicles": int(len(np.unique(car))),
           "S_median": float(np.median(S)), "S_CI": X.boot_median(S, car, rng),
           "S_shuffle_median": float(np.median(Ssh)), "S_shuffle_CI": X.boot_median(Ssh, car, rng),
           "paired_S_minus_shuffle_median": float(np.median(d)), "paired_CI": X.boot_median(d, car, rng),
           "mm_unsafe_vs_true_frac": float(um.sum() / n.sum()),
           "shuffle_unsafe_vs_true_frac": float(ush.sum() / n.sum()),
           "warm_S_median": float(np.median(S[tmin >= 10])), "warm_S_shuffle_median": float(np.median(Ssh[tmin >= 10])),
           "cold_S_median": float(np.median(S[tmin < 10])) if (tmin < 10).any() else None,
           "cold_S_shuffle_median": float(np.median(Ssh[tmin < 10])) if (tmin < 10).any() else None}
    json.dump(out, open("results/X/X2/x2_shuffle_diag.json", "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
