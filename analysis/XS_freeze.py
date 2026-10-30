"""X2-S freeze + power check (before any X2-S limiter code). Schaeffer et al. 28 LFP systems, CC BY-NC 4.0.
1. Stratified system split (seed 0): rank systems by >= 0.3 C step count from the feasibility profile, pair adjacent
   ranks, assign one of each pair to each half at random.
2. Current-sign check (median pack-mean dV/dI over steps must be > 0 for charge-positive current).
3. V_lim from the calibration half only (p99.5 of per-frame max cell V over charge-direction frames, rounded down to
   10 mV, capped at 3,650 mV). Q_ref SOURCED 160 Ah.
4. Session / history / depth counts for both halves (power check). No per-cell R, limiter, kappa or S is computed.
Every number DERIVED. Usage: python -E analysis/XS_freeze.py [--jobs 6]
"""
import argparse
import json
import os
import sys
from multiprocessing import Pool

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import XS_common as X                                    # noqa: E402

WIN_S = 30 * 86400.0
VLIM_CAP = 3650.0
VMAX_SESSION_CAP = 3650.0


def per_sys(sysid):
    t, Ic, V, T, bal, valid = X.load(sysid)
    ch = valid & (Ic > X.CH_A)
    vmax_ch = V[ch].max(1) if ch.any() else np.zeros(0)
    st, r, rp = X.steps(t, Ic, V, T, bal, valid, 0.3)
    st_all, _, rp_all = X.steps(t, Ic, V, T, bal, valid, 0.3, allow_bal=True)
    sess = []
    for s, dah in X.sessions(t, Ic, valid):
        t0 = t[s[0]]
        n_w = int(((st < t0) & (st >= t0 - WIN_S)).sum())
        sess.append((float(V[s].max()), n_w, float(dah.sum())))
    return {"sys": sysid, "vmax_ch": vmax_ch.astype(np.float32), "n_steps": int(len(st)),
            "n_steps_incl_bal": int(len(st_all)), "rp_median": float(np.median(rp)) if len(rp) else None,
            "rp_median_incl_bal": float(np.median(rp_all)) if len(rp_all) else None,
            "frac_charge_rows_bal": float(bal[ch].mean()) if ch.any() else None, "sessions": sess}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=6)
    a = ap.parse_args()
    prof = json.load(open(f"{X.OUT}/profile.json"))["systems"]
    order = [p["sys"] for p in sorted(prof, key=lambda p: (-p["steps"]["0.3C"], p["sys"]))]
    rng = np.random.default_rng(0)
    cal, ev = [], []
    for i in range(0, len(order), 2):
        pair = order[i:i + 2]
        if len(pair) == 2 and rng.random() < 0.5:
            pair = pair[::-1]
        cal.append(pair[0])
        if len(pair) == 2:
            ev.append(pair[1])
    split = {"rule": "rank by >=0.3C steps (feasibility profile), pair adjacent ranks, seed 0 coin per pair",
             "calibration": sorted(cal), "evaluation": sorted(ev)}
    json.dump(split, open(f"{X.OUT}/split.json", "w"), indent=1)
    with Pool(a.jobs) as p:
        R = {r["sys"]: r for r in p.map(per_sys, sorted(order, key=lambda s: -dict((q["sys"], q["rows"]) for q in prof)[s]),
                                         chunksize=1)}
    vc = np.concatenate([R[s]["vmax_ch"] for s in cal])
    vlim = min(np.floor(np.percentile(vc, 99.5) / 10.0) * 10.0, VLIM_CAP)
    frozen = {"V_lim_mV": float(vlim), "V_lim_uncapped_p99.5_mV": float(np.percentile(vc, 99.5)),
              "Q_ref_Ah": X.Q_REF, "tag": "ASSUMED limits; V_lim from calibration half only; Q_ref SOURCED (README)"}
    json.dump(frozen, open(f"{X.OUT}/frozen.json", "w"), indent=1)
    out = {"split": split, "frozen": frozen, "systems": {}, "halves": {}}
    for s, r in sorted(R.items()):
        out["systems"][s] = {k: r[k] for k in ("n_steps", "n_steps_incl_bal", "rp_median", "rp_median_incl_bal",
                                                "frac_charge_rows_bal")}
        out["systems"][s]["n_sessions"] = len(r["sessions"])
    for half, ids in (("calibration", cal), ("evaluation", ev)):
        h = {}
        for band in (25.0, 50.0, 100.0):
            for minst in (40,):
                prim = [(s, x) for s in ids for x in R[s]["sessions"]
                        if x[1] >= minst and x[0] >= vlim - band and x[0] <= VMAX_SESSION_CAP]
                h[f"primary_{int(band)}mV"] = {"sessions": len(prim), "systems": len({s for s, _ in prim}),
                                               "per_system": {int(s): sum(1 for q, _ in prim if q == s) for s in ids}}
        h["sessions"] = sum(len(R[s]["sessions"]) for s in ids)
        h["sessions_with_history"] = sum(1 for s in ids for x in R[s]["sessions"] if x[1] >= 40)
        h["sessions_above_3650"] = sum(1 for s in ids for x in R[s]["sessions"] if x[0] > VMAX_SESSION_CAP)
        out["halves"][half] = h
    json.dump(out, open(f"{X.OUT}/freeze.json", "w"), indent=1, default=float)
    print(json.dumps({k: out[k] for k in ("split", "frozen", "halves")}, indent=1, default=float))
    for s, v in sorted(out["systems"].items()):
        print(s, v)


if __name__ == "__main__":
    main()
