"""Schaeffer et al. 28 LFP systems (zenodo 13715694, CC BY-NC 4.0): FEASIBILITY profile for a possible X2-F
confirmation. Computes only rows, sampling interval, current range/sign, current-step counts, charge-session depth and
balancing activity. NO per-cell R, limiter, kappa or S is computed. Every number DERIVED.
Usage: python -E analysis/XS_profile.py [--jobs 8]   (writes results/X/XS/profile.json)
"""
import argparse
import glob
import json
import os
from multiprocessing import Pool

import numpy as np
import pandas as pd

SRC = "data/raw/schaeffer/field_data"
OUT = "results/X/XS"
Q_NOM = 160.0          # SOURCED (README: "approx. 160 Ah")
CELLS = [f"U_Cell_{k}" for k in range(1, 9)]
BAL = [f"I_CNV_Cell_{k}" for k in range(1, 9)]


def one(path):
    sysid = int(os.path.basename(path)[9:-4])
    cols = ["Timestamp", "I_Battery", "SOC_Battery", "Temperature_1"] + CELLS + BAL
    d = pd.read_csv(path, usecols=cols, parse_dates=["Timestamp"], engine="c")
    t = d["Timestamp"].astype("int64").to_numpy() / 1e9
    I = d["I_Battery"].to_numpy(float)
    V = d[CELLS].to_numpy(float)
    B = d[BAL].to_numpy(float)
    dt = np.diff(t)
    ok = np.isfinite(V).all(1) & np.isfinite(I) & (V > 2.0).all(1) & (V < 4.5).all(1)
    cons = (dt > 0) & (dt <= 10) & ok[1:] & ok[:-1]
    dI = np.diff(I)
    dT = np.abs(np.diff(d["Temperature_1"].to_numpy(float)))
    steps = {f"{c}C": int((cons & (np.abs(dI) >= c * Q_NOM) & (dT <= 1)).sum()) for c in (0.1, 0.2, 0.3)}
    soc = d["SOC_Battery"].to_numpy(float)
    corr = float(np.corrcoef(np.diff(soc)[cons], I[1:][cons])[0, 1]) if cons.sum() > 100 else None
    sign = 1.0 if (corr is None or corr >= 0) else -1.0          # make charge positive
    Ic = I * sign
    # charge sessions: Ic > 1 A, break on gap > 60 s or >= 2 non-charge rows
    ch = ok & (Ic > 1.0)
    sess = []
    idx = np.flatnonzero(ch)
    if len(idx):
        brk = np.flatnonzero((np.diff(idx) > 2) | (np.diff(t[idx]) > 60)) + 1
        for s in np.split(idx, brk):
            ah = float((Ic[s] * 5.0).sum() / 3600.0)
            if ah >= 0.5:
                sess.append((float(V[s].max()), ah, float(t[s[0]])))
    vmax = np.array([x[0] for x in sess]) if sess else np.zeros(0)
    days = (t[-1] - t[0]) / 86400.0
    return {"sys": sysid, "rows": int(len(d)), "valid_rows": int(ok.sum()), "days_span": days,
            "dt_median_s": float(np.median(dt[dt > 0])) if len(dt) else None,
            "frac_dt_le_10s": float((dt <= 10).mean()) if len(dt) else None,
            "I_p1_p99": [float(np.percentile(I, 1)), float(np.percentile(I, 99))], "corr_dSOC_I": corr,
            "I_charge_p99_A": float(np.percentile(Ic[Ic > 1], 99)) if (Ic > 1).any() else None,
            "steps": steps, "n_charge_sessions": len(sess),
            "sess_vmax_p50_p90": [float(np.percentile(vmax, 50)), float(np.percentile(vmax, 90))] if len(vmax) else None,
            "sess_reach_3p50": int((vmax >= 3.50).sum()), "sess_reach_3p55": int((vmax >= 3.55).sum()),
            "sess_reach_3p60": int((vmax >= 3.60).sum()),
            "frac_rows_balancing": float((np.abs(B) > 0.01).any(1).mean()),
            "frac_charge_rows_balancing": float((np.abs(B[ch]) > 0.01).any(1).mean()) if ch.any() else None}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=6)
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    files = sorted(glob.glob(f"{SRC}/data_sys_*.csv"), key=os.path.getsize)
    with Pool(a.jobs) as p:
        R = sorted(p.map(one, files, chunksize=1), key=lambda r: r["sys"])
    json.dump({"tag": "DERIVED feasibility profile; Schaeffer et al. CC BY-NC 4.0; no limiter quantity computed",
               "Q_nom_Ah_SOURCED": Q_NOM, "systems": R}, open(f"{OUT}/profile.json", "w"), indent=1)
    for r in R:
        print(r["sys"], r["rows"], round(r["days_span"]), r["dt_median_s"], r["corr_dSOC_I"] and round(r["corr_dSOC_I"], 2),
              r["I_charge_p99_A"] and round(r["I_charge_p99_A"]), r["steps"], r["n_charge_sessions"],
              r["sess_vmax_p50_p90"], r["sess_reach_3p50"], r["sess_reach_3p55"], round(r["frac_charge_rows_balancing"] or 0, 2))


if __name__ == "__main__":
    main()
