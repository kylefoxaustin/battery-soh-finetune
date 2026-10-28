"""Experiment X2-C, mandatory first step (Build Brief rev 6 §3): dataset profile and power check.
NO limiter quantity is computed here (no R_k, no L, no kappa, no S). Committed with the pre-registration.
Order: (1) split vehicles 50/50, seed 0, before anything else; (2) per-vehicle counts; (3) V_lim and Q_ref from the
calibration half only; (4) steps / sessions / charge depth / primary-population counts.
Usage: python -E analysis/X2C_profile.py   (writes results/X/X2C/profile.json; text in results/X/X2C_profile.md)
"""
import json
import os
import sys
from multiprocessing import Pool

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import G2_beihang as G                                   # noqa: E402  (restricted unpickler, layout)

OUT = "results/X/X2C"
FLEETS = {"QAS": dict(k=110, scale=1.0), "DTI": dict(k=85, scale=1e-3)}
DT_S = 30.0                      # brief §2.1: 30 s frames (SOURCED: G.2 layout); no timestamps
CH_A = 1.0                       # OPEN-P1: a charge-direction frame has charge current > 1 A
SESS_BREAK = 2                   # OPEN-P2: a session ends after >= 2 consecutive non-charge or invalid rows
WIN_FR = {"7d": 20160, "30d": 86400, "90d": 259200}     # brief §4.2 frame-count windows
DEPTH_MV = (25, 50, 100)


def labels(fleet):
    """Vehicle labels as G.2 read them from Labels.xls (Num, Label); taken from G.2's features.csv because xlrd is
    no longer installed. Labels are only used to EXCLUDE faulty vehicles."""
    df = pd.read_csv("results/G2/features.csv", usecols=["maker", "veh", "label"])
    df = df[df.maker == fleet]
    return dict(zip(df.veh.astype(int), df.label.astype(int)))


def load(fleet, n):
    cfg = FLEETS[fleet]
    k = cfg["k"]
    b = G.load(f"{G.ROOT}/{fleet}/{n}/vin_2.pkl")
    V = b[:, 2:2 + k].astype(np.float64) * cfg["scale"]
    q = b[:, 2 + 2 * k:].astype(np.float64)
    T, S, I = q[:, 0], q[:, 1], q[:, -1]
    if fleet == "DTI":
        S = S / 100.0
    valid = (np.abs(I) < 900) & np.all((V >= 2.0) & (V <= 4.5), 1) & np.isfinite(T)
    Ic = -I                                              # discharge-positive in the file (checked: corr(dSOC, I) < 0)
    return V, Ic, T, S, valid


def per_vehicle_basic(args):
    fleet, n = args
    V, Ic, T, S, valid = load(fleet, n)
    ch = valid & (Ic > CH_A)
    m = valid[:-1] & valid[1:]
    dS, Iv = np.diff(S)[m], Ic[:-1][m]
    sign_ok = float(np.corrcoef(dS, Iv)[0, 1]) if m.sum() > 10 and np.std(dS) > 0 else np.nan
    # charge segments for Q_ref: consecutive valid charge rows; dAh = sum(Ic)*30 s; need dSOC >= 0.20
    segs, start = [], None
    for i in range(len(ch) + 1):
        if i < len(ch) and ch[i]:
            start = i if start is None else start
        elif start is not None:
            segs.append((start, i)); start = None
    qr = [float((Ic[a:b].sum() * DT_S / 3600.0) / (S[b - 1] - S[a])) for a, b in segs
          if b - a >= 2 and (S[b - 1] - S[a]) >= 0.20]
    vmax_ch = V[ch].max(1) if ch.any() else np.zeros(0)
    return {"fleet": fleet, "veh": n, "rows": len(Ic), "valid": int(valid.sum()), "charge_frames": int(ch.sum()),
            "corr_dsoc_Ic": sign_ok, "q_ratios": qr, "vmax_ch_p995": float(np.percentile(vmax_ch, 99.5)) if len(vmax_ch) else None,
            "vmax_ch": vmax_ch.astype(np.float32)}


def per_vehicle_sessions(args):
    fleet, n, qref, vlim = args
    V, Ic, T, S, valid = load(fleet, n)
    m = valid[:-1] & valid[1:]                          # OPEN-1: steps only between consecutive valid ROWS
    dI = np.diff(Ic)
    dT = np.abs(np.diff(T))
    out = {"fleet": fleet, "veh": n}
    vidx = np.cumsum(valid) - 1                          # valid-frame counter (window unit)
    steps = {}
    for c in (0.2, 0.3, 0.5):
        st = m & (np.abs(dI) >= c * qref) & (dT <= 1.0)
        steps[c] = vidx[1:][st]                          # valid-frame index of the post-step frame
        out[f"steps_{c}"] = int(st.sum())
    ch = valid & (Ic > CH_A)
    sess, start, miss = [], None, 0
    for i in range(len(ch) + 1):
        if i < len(ch) and ch[i]:
            start = i if start is None else start
            miss, last = 0, i
        elif start is not None:
            miss += 1
            if miss >= SESS_BREAK or i == len(ch):
                sess.append((start, last + 1)); start, miss = None, 0
    rows = []
    for a, b in sess:
        idx = np.arange(a, b)[ch[a:b]]
        ah = Ic[idx].sum() * DT_S / 3600.0
        if ah < 0.5:
            continue
        vmax = float(V[idx].max())
        v0 = vidx[a]
        hist = {w: int(((steps[0.3] < v0) & (steps[0.3] >= v0 - fr)).sum()) for w, fr in WIN_FR.items()}
        rows.append({"ah": float(ah), "vmax": vmax, "gap_mv": (vlim - vmax) * 1e3, "hist": hist,
                     "tmed": float(np.median(T[idx]))})
    out["sessions"] = rows
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    res = {"tag": "DERIVED (Beihang CC BY 4.0); V_lim and Q_ref ASSUMED (frozen here from the calibration half)"}
    rng = np.random.default_rng(0)
    split = {}
    for fleet in FLEETS:
        lab = labels(fleet)
        normal = sorted(v for v, l in lab.items() if l == 0 and os.path.exists(f"{G.ROOT}/{fleet}/{v}/vin_2.pkl"))
        perm = rng.permutation(normal)
        h = len(perm) // 2
        split[fleet] = {"calibration": sorted(int(x) for x in perm[:h]), "evaluation": sorted(int(x) for x in perm[h:]),
                        "n_normal": len(normal), "n_faulty_excluded": sum(1 for l in lab.values() if l == 1)}
    json.dump(split, open(f"{OUT}/split.json", "w"), indent=1)
    res["split_counts"] = {f: {k: (len(v) if isinstance(v, list) else v) for k, v in s.items()} for f, s in split.items()}
    with Pool(10) as p:
        B = p.map(per_vehicle_basic, [(f, n) for f in FLEETS for part in ("calibration", "evaluation")
                                      for n in split[f][part]])
    frozen = {}
    for fleet in FLEETS:
        cal = set(split[fleet]["calibration"])
        bf = [b for b in B if b["fleet"] == fleet]
        bc = [b for b in bf if b["veh"] in cal]
        vm = np.concatenate([b["vmax_ch"] for b in bc if len(b["vmax_ch"])])
        vlim = float(np.floor(np.percentile(vm, 99.5) * 100) / 100)             # round DOWN to 10 mV
        qr = np.concatenate([b["q_ratios"] for b in bc]) if any(b["q_ratios"] for b in bc) else np.zeros(0)
        qref = float(np.median(qr)) if len(qr) else None
        frozen[fleet] = {"V_lim_V": vlim, "Q_ref_Ah": qref, "n_q_segments_cal": int(len(qr)),
                         "q_ratio_p10_p90": [float(np.percentile(qr, 10)), float(np.percentile(qr, 90))] if len(qr) else None}
        res[fleet] = {"vehicles": len(bf), "rows": int(sum(b["rows"] for b in bf)),
                      "valid_frames": int(sum(b["valid"] for b in bf)),
                      "charge_frames": int(sum(b["charge_frames"] for b in bf)),
                      "corr_dsoc_Ic_median": float(np.nanmedian([b["corr_dsoc_Ic"] for b in bf])),
                      "rows_per_vehicle_p10_med_p90": [float(np.percentile([b["rows"] for b in bf], q)) for q in (10, 50, 90)]}
    res["frozen"] = frozen
    json.dump(frozen, open(f"{OUT}/frozen.json", "w"), indent=1)
    print(json.dumps(res, indent=1), flush=True)
    args = [(f, n, frozen[f]["Q_ref_Ah"], frozen[f]["V_lim_V"]) for f in FLEETS if frozen[f]["Q_ref_Ah"]
            for part in ("calibration", "evaluation") for n in split[f][part]]
    with Pool(10) as p:
        P = p.map(per_vehicle_sessions, args)
    for fleet in FLEETS:
        if not frozen[fleet]["Q_ref_Ah"]:
            continue
        pf = [x for x in P if x["fleet"] == fleet]
        d = res[fleet]
        for c in (0.2, 0.3, 0.5):
            v = [x[f"steps_{c}"] for x in pf]
            d[f"steps_ge_{c}C_per_vehicle_p10_med_p90"] = [float(np.percentile(v, q)) for q in (10, 50, 90)]
        for part in ("calibration", "evaluation"):
            ids = set(split[fleet][part])
            ss = [s for x in pf if x["veh"] in ids for s in x["sessions"]]
            gap = np.array([s["gap_mv"] for s in ss])
            dd = {"sessions_ge_0p5Ah": len(ss),
                  "session_vmax_gap_mV_p10_med_p90": [float(np.percentile(gap, q)) for q in (10, 50, 90)] if len(gap) else None}
            for mv in DEPTH_MV:
                dd[f"within_{mv}mV"] = int((gap <= mv).sum())
            for w in WIN_FR:
                h = np.array([s["hist"][w] >= 20 for s in ss])
                dd[f"hist20_{w}"] = int(h.sum())
                for mv in DEPTH_MV:
                    sel = h & (gap <= mv)
                    dd[f"primary_{w}_{mv}mV"] = int(sel.sum())
                    dd[f"primary_{w}_{mv}mV_vehicles"] = int(len({x["veh"] for x in pf if x["veh"] in ids
                                                                   for s in x["sessions"]
                                                                   if s["hist"][w] >= 20 and s["gap_mv"] <= mv}))
            d[part] = dd
    json.dump(res, open(f"{OUT}/profile.json", "w"), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
