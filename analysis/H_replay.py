"""Experiment H-a (pre-registered in results/H/H_preregistration.md, commit 43485e8, before this script existed).
Counterfactual replay: on recorded charging cell states, what C-rate would a per-cell limiter allow vs a min/max
scalar limiter vs a pack-scalar limiter with margins? Every number DERIVED; every limit ASSUMED.
Usage: python analysis/H_replay.py --out results/H [--jobs 10]
"""
import argparse
import json
import os
from multiprocessing import Pool

import numpy as np

CELLS = "data/changan/cells"
CT_T = np.array([-20, 0, 10, 25, 40, 50, 60], float)
CT_C = np.array([0.05, 0.2, 0.6, 1.5, 1.5, 0.8, 0.0])
KNEE, TAPER_END = 60.0, 0.05
GAP_SESSION, GAP_INT, MIN_FULL = 300.0, 60.0, 10
M_MV = [0, 5, 10, 20, 30, 50, 75, 100]
M_T = [0, 2, 5, 10]
N_PERM = 100
UNSAFE_TOL = 1.001


def ocv():
    o = json.load(open("data/changan/ocv_full.json"))
    v, s = np.array(o["vmax_v"]) * 1e3, np.maximum.accumulate(np.array(o["soc_pct"], float))
    return v, s


OV, OS = ocv()


def soc(mv):
    return np.interp(mv, OV, OS)          # table v is strictly increasing; s monotone; clipped at ends


def c_t(T, shift=0.0):
    return np.interp(T, CT_T + shift, CT_C)


def taper(s, knee=KNEE):
    return np.where(s <= knee, 1.0, 1.0 - (1.0 - TAPER_END) * (s - knee) / (100.0 - knee))


def perms():
    base = (np.arange(96) * 32) // 96
    out = [base]
    for seed in range(N_PERM):
        out.append(np.random.default_rng(seed).permutation(base))
    return np.array(out)                  # [1 + N_PERM, 96]: row 0 = M1, rows 1.. = M2


PMAPS = perms()


def frames(car):
    """charging full-vector frames grouped into sessions -> list of dicts of arrays"""
    Z = np.load(f"{CELLS}/vin{car}.npz")
    C = {k: Z[k] for k in ["t", "I", "status", "sync", "t_full", "vmean_mv", "tmean", "vmax_mv", "vmin_mv", "tmin",
                           "tmax", "dv_full", "dt_full"]}                 # load each array once (NpzFile re-reads)
    t, I, st, sync = C["t"], C["I"].astype(np.float64), C["status"], C["sync"]
    tf = C["t_full"]
    j = np.clip(np.searchsorted(t, tf), 0, len(t) - 1)
    ok = (t[j] == tf) & (st[j] == 1) & sync[j]
    if ok.sum() < MIN_FULL:
        return []
    # cumulative charged Ah on summary frames (charging: I < 0 -> +Ah), gaps > GAP_INT contribute 0
    dt = np.diff(t, prepend=t[0])
    dt = np.where((dt > 0) & (dt <= GAP_INT), dt, 0.0)
    cah = np.cumsum(np.nan_to_num(np.where(st == 1, -I, 0.0)) * dt / 3600.0)    # NaN current contributes 0
    # sessions over charging summary frames
    ch = np.flatnonzero(st == 1)
    brk = np.flatnonzero(np.diff(t[ch]) > GAP_SESSION) + 1
    sid = np.zeros(len(t), np.int64) - 1
    for k, seg in enumerate(np.split(ch, brk)):
        sid[seg] = k
    fi = np.flatnonzero(ok)
    jj = j[fi]
    s_of = sid[jj]
    out = []
    for k in np.unique(s_of):
        if k < 0:
            continue
        m = s_of == k
        if m.sum() < MIN_FULL:
            continue
        rows, js = fi[m], jj[m]
        dah = np.diff(cah[js], prepend=cah[js[0]])
        dah[0] = 0.0
        Vf = C["vmean_mv"][js][:, None] + C["dv_full"][rows].astype(np.float64)
        Tf = C["tmean"][js][:, None] + C["dt_full"][rows].astype(np.float64)
        good = np.isfinite(Vf).all(1) & np.isfinite(Tf).all(1) & np.isfinite(dah)   # DEVIATION (disclosed): drop NaN frames
        if good.sum() < MIN_FULL:
            continue
        rows, js, dah, Vf, Tf = rows[good], js[good], dah[good], Vf[good], Tf[good]
        out.append({"V": Vf, "T": Tf, "n_nan_dropped": int((~good).sum()),
                    "vmean": C["vmean_mv"][js].astype(np.float64), "tmean": C["tmean"][js].astype(np.float64),
                    "vmax": C["vmax_mv"][js].astype(np.float64), "vmin": C["vmin_mv"][js].astype(np.float64),
                    "tmin": C["tmin"][js].astype(np.float64), "tmax": C["tmax"][js].astype(np.float64),
                    "dah": np.clip(dah, 0, None)})
    return out


def limiters(f, shift=0.0, knee=KNEE, maps=PMAPS):
    """returns per-frame L_mm, L_cell[map] and argmin info for map 0"""
    ts = taper(soc(f["V"]), knee)                                   # [n, 96]
    ctp = c_t(f["T"], shift)                                        # [n, 32]
    Lcell = np.empty((len(maps), len(ts)))
    for i, pm in enumerate(maps):
        Lcell[i] = (ctp[:, pm] * ts).min(1)
    a0 = (ctp[:, maps[0]] * ts).argmin(1)
    # scalar extremes as min/max data would give them; computed from the cell list (sync frames: identical to the
    # scalar columns within 0.5 mV) so that L_cell >= L_mm holds exactly
    Vmax, Tmin, Tmax = f["V"].max(1), f["T"].min(1), f["T"].max(1)
    Lmm = np.minimum(c_t(Tmin, shift), c_t(Tmax, shift)) * taper(soc(Vmax), knee)
    return Lmm, Lcell, a0, ts, ctp


def t_of(dah, L):
    L = np.maximum(L, 1e-6)
    return float((dah / L).sum())


def one(car):
    S = frames(car)
    res = {"car": car, "sessions": []}
    for f in S:
        if f["dah"].sum() <= 0.5:          # sessions delivering < 0.5 Ah contribute no time; skip (also no ratio)
            continue
        Lmm, Lcell, a0, ts, ctp = limiters(f)
        tmm, tcell = t_of(f["dah"], Lmm), np.array([t_of(f["dah"], L) for L in Lcell])
        s_mm = 1 - tcell / tmm
        V, T = f["V"], f["T"]
        diff = np.abs(Lcell[0] - Lmm) > 1e-9          # prereg text had "<" (typo; L_cell >= L_mm by construction)
        pm = PMAPS[0]
        imaxV, iminV = V.argmax(1), V.argmin(1)
        p_of_a = pm[a0]
        not_vmax = a0 != imaxV
        not_vmin = a0 != iminV
        not_textreme = (p_of_a != T.argmin(1)) & (p_of_a != T.argmax(1))
        # tie-aware (clarification, disclosed): a reference cell "constrains" if its own limit equals the minimum
        vals = ctp[:, pm] * ts
        lc = vals.min(1)
        r_ = np.arange(len(lc))
        tol = lc * 1e-9 + 1e-12
        tw_not_vmax = vals[r_, imaxV] > lc + tol
        tw_not_vmin = vals[r_, iminV] > lc + tol
        ext = (pm[None, :] == T.argmin(1)[:, None]) | (pm[None, :] == T.argmax(1)[:, None])
        tw_not_text = np.where(ext, vals, np.inf).min(1) > lc + tol
        sess = {"n": int(len(Lmm)), "n_nan_dropped": f["n_nan_dropped"], "ah": float(f["dah"].sum()), "S_mm_M1": float(s_mm[0]),
                "S_mm_M2": s_mm[1:].tolist(), "frac_frames_cell_gt_mm": float(diff.mean()),
                "ratio_med": float(np.median(Lcell[0] / np.maximum(Lmm, 1e-9))),
                "n_not_vmax": int(not_vmax.sum()), "n_not_vmin": int(not_vmin.sum()),
                "n_not_textreme_probe": int(not_textreme.sum()),
                "tw_not_vmax": int(tw_not_vmax.sum()), "tw_not_vmin": int(tw_not_vmin.sum()),
                "tw_not_textreme_probe": int(tw_not_text.sum()),
                "n_diff": int(diff.sum()), "n_diff_not_vmax": int((diff & not_vmax).sum()),
                "tmin_med": float(np.median(T.min(1))), "tmax_med": float(np.median(T.max(1))),
                "tspread_med": float(np.median(T.max(1) - T.min(1))),
                "vmax_med": float(np.median(V.max(1)))}
        # margin sweep (M1)
        sw = {}
        for m in M_MV:
            tsp = taper(soc(f["vmean"] + m))
            for mT in M_T:
                Lp = np.minimum(c_t(f["tmean"] - mT), c_t(f["tmean"] + mT)) * tsp
                sw[f"{m}_{mT}"] = (1 - tcell[0] / t_of(f["dah"], Lp), int((Lp > Lcell[0] * UNSAFE_TOL).sum()))
        sess["sweep"] = sw
        # sensitivity (M1 only)
        sens = {}
        for name, kw in [("shift-5", {"shift": -5.0}), ("shift+5", {"shift": 5.0}), ("knee50", {"knee": 50.0}),
                         ("knee70", {"knee": 70.0})]:
            Lmm2, Lc2, *_ = limiters(f, maps=PMAPS[:1], **kw)
            sens[name] = 1 - t_of(f["dah"], Lc2[0]) / t_of(f["dah"], Lmm2)
        sess["sens"] = sens
        res["sessions"].append(sess)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--jobs", type=int, default=10)
    a = ap.parse_args()
    cars = sorted(int(f[3:-4]) for f in os.listdir(CELLS) if f.startswith("vin") and f.endswith(".npz") and f[3:-4].isdigit())
    with Pool(a.jobs) as p:
        R = sorted(p.imap_unordered(one, cars), key=lambda r: r["car"])
    ss = [(r["car"], s) for r in R for s in r["sessions"]]
    car_of = np.array([c for c, _ in ss])
    sm1 = np.array([s["S_mm_M1"] for _, s in ss])
    sm2 = np.array([s["S_mm_M2"] for _, s in ss])                   # [n_sess, N_PERM]
    med_m2_each = np.median(sm2, axis=0)                            # median session S per permutation
    rng = np.random.default_rng(0)
    ucars = np.unique(car_of)
    idx = {c: np.flatnonzero(car_of == c) for c in ucars}
    bs = []
    for _ in range(1000):
        pick = np.concatenate([idx[c] for c in rng.choice(ucars, len(ucars))])
        bs.append(np.median(sm1[pick]))
    tot = lambda k: int(sum(s[k] for _, s in ss))
    out = {"tag": "DERIVED (replay on MEASURED Changan cell states; limit map, mapping, trajectory ASSUMED); "
                  "CC BY-NC-SA 4.0 non-commercial",
           "preregistered_in": "43485e8", "n_vehicles": int(len(ucars)), "n_sessions": len(ss),
           "n_frames": tot("n"), "n_frames_nan_dropped": tot("n_nan_dropped"), "ah_total": float(sum(s["ah"] for _, s in ss)),
           "S_mm_M1_median": float(np.median(sm1)), "S_mm_M1_CI": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))],
           "S_mm_M1_p90": float(np.percentile(sm1, 90)), "S_mm_M1_max": float(sm1.max()),
           "S_mm_M2_median_of_medians": float(np.median(med_m2_each)),
           "S_mm_M2_range_5_95": [float(np.percentile(med_m2_each, 5)), float(np.percentile(med_m2_each, 95))],
           "frac_frames_cell_gt_mm": tot("n_diff") / tot("n"),
           "frac_constraining_not_vmax_cell": tot("n_not_vmax") / tot("n"),
           "frac_constraining_not_vmin_cell": tot("n_not_vmin") / tot("n"),
           "frac_constraining_not_on_extreme_T_probe": tot("n_not_textreme_probe") / tot("n"),
           "tieaware_frac_vmax_cell_not_constraining": tot("tw_not_vmax") / tot("n"),
           "tieaware_frac_vmin_cell_not_constraining": tot("tw_not_vmin") / tot("n"),
           "tieaware_frac_no_extreme_T_probe_cell_constraining": tot("tw_not_textreme_probe") / tot("n"),
           "frac_differing_frames_not_vmax": (tot("n_diff_not_vmax") / tot("n_diff")) if tot("n_diff") else None,
           "charging_T_median": {"tmin": float(np.median([s["tmin_med"] for _, s in ss])),
                                 "tmax": float(np.median([s["tmax_med"] for _, s in ss])),
                                 "spread": float(np.median([s["tspread_med"] for _, s in ss])),
                                 "spread_p90": float(np.percentile([s["tspread_med"] for _, s in ss], 90)),
                                 "tmin_p5": float(np.percentile([s["tmin_med"] for _, s in ss], 5))}}
    sweep = {}
    nfr = tot("n")
    for m in M_MV:
        for mT in M_T:
            k = f"{m}_{mT}"
            sweep[k] = {"S_pack_median": float(np.median([s["sweep"][k][0] for _, s in ss])),
                        "unsafe_frac": sum(s["sweep"][k][1] for _, s in ss) / nfr}
    out["margin_sweep"] = sweep
    safe = [(m, mT) for m in M_MV for mT in M_T if sweep[f"{m}_{mT}"]["unsafe_frac"] <= 0.001]
    out["smallest_safe_margin"] = ({"m_mV": safe[0][0], "mT_C": safe[0][1], **sweep[f"{safe[0][0]}_{safe[0][1]}"]}
                                   if safe else None)
    # smallest by m then mT is lexicographic; also report the full safe set
    out["safe_margins"] = [f"{m}_{mT}" for m, mT in safe]
    out["sensitivity_M1"] = {n: float(np.median([s["sens"][n] for _, s in ss])) for n in ss[0][1]["sens"]}
    v1, v2 = out["S_mm_M1_median"] >= 0.01, out["S_mm_M2_median_of_medians"] >= 0.01
    if not v1 and not v2:
        out["decision"] = "NO BENEFIT over min/max"
    elif v1 and v2 and out["S_mm_M1_CI"][0] > 0:
        out["decision"] = "PER-CELL RECOVERS X"
    else:
        out["decision"] = "NOT ANSWERABLE from replay (mapping-dependent)"
    json.dump(out, open(f"{a.out}/replay.json", "w"), indent=1)
    np.savez_compressed(f"{a.out}/replay_sessions.npz", car=car_of, S_mm_M1=sm1, S_mm_M2_med=np.median(sm2, 1),
                        frac_diff=np.array([s["frac_frames_cell_gt_mm"] for _, s in ss]),
                        not_vmax=np.array([s["n_not_vmax"] / s["n"] for _, s in ss]),
                        tspread=np.array([s["tspread_med"] for _, s in ss]),
                        tmin=np.array([s["tmin_med"] for _, s in ss]))
    print(json.dumps({k: v for k, v in out.items() if k != "margin_sweep"}, indent=1))


if __name__ == "__main__":
    main()
