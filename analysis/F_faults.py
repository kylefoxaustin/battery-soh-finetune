"""Experiment F (pre-registered in results/F/F_preregistration.md, commit 2b9e629, before this script existed).
Per-cell anomaly catalogue, physics classification, and the primary test: does per-cell data forecast a later
anomaly better than a scalar min/max-only monitor?

Implements the pre-registration. Choices it left open are marked OPEN below and disclosed in the results:
  OPEN-1  "bins span >= 30 % SOC" is read as (max bin centre - min bin centre) >= 30 (the stricter reading)
  OPEN-2  pack SOC from vmean_mv through the inverse table, clipped to the table's ends
  OPEN-3  per-cell / min-only day agreement is computed over days valid in BOTH sources
  OPEN-4  ties in the OCV table's SOC column are merged (mean voltage) so the table is strictly monotone
Usage: python analysis/F_faults.py --out results/F [--jobs 10]
"""
import argparse
import json
import os
from multiprocessing import Pool

import numpy as np

CELLS, SLIM, LABELS = "data/changan/cells", "data/changan/slim", "data/changan/labels_full"
REST_A, DRIVE_A, MIN_REST, EV_MV, REC_MV = 1.0, 10.0, 20, -60.0, -30.0
GAP_D, QUAL_N, BASE_N, BASE_MIN, ABRUPT_D, REC_N = 14, 3, 30, 10, 3, 7
MIN_DAYS, BIN, MIN_BIN_N, MIN_BINS, MIN_SPAN = 120, 5.0, 20, 4, 30.0
COMP_TAP, SSE_RATIO, LAB_WIN = 0.5, 0.5, 180 * 86400


def ocv_funcs():
    o = json.load(open("data/changan/ocv_full.json"))
    v, s = np.array(o["vmax_v"]) * 1e3, np.maximum.accumulate(np.array(o["soc_pct"], float))
    us = np.unique(s)
    uv = np.array([v[s == x].mean() for x in us])                      # OPEN-4
    lo, hi = np.polyfit(us[:5], uv[:5], 1), np.polyfit(us[-5:], uv[-5:], 1)

    def ocv(x):                                                         # soc % -> mV, linear extrapolation
        x = np.asarray(x, float)
        return np.where(x < us[0], np.polyval(lo, x), np.where(x > us[-1], np.polyval(hi, x), np.interp(x, us, uv)))

    def soc(mv):                                                        # mV -> soc %, clipped (OPEN-2)
        return np.interp(mv, uv, us)
    return ocv, soc


OCV, SOC = ocv_funcs()


def runs(days, gap):
    """split sorted day numbers into runs with consecutive gaps <= gap"""
    if not len(days):
        return []
    cut = np.flatnonzero(np.diff(days) > gap) + 1
    return np.split(days, cut)


def slope(x, y):
    ok = np.isfinite(y)
    return float(np.polyfit(x[ok], y[ok], 1)[0]) if ok.sum() >= 3 else np.nan


def classify(k, ev_days, days, D, base_idx, dvk_rest, s_rest, day_rest, dvk_drv, I_drv, day_drv):
    out = {}
    # 2a shared-tap signature
    if base_idx is None:
        out["comp"], out["tap"] = None, None
    else:
        ei = np.searchsorted(days, ev_days)
        sh = {j: float(np.median(D[ei, j]) - np.median(D[base_idx, j])) for j in (k - 1, k, k + 1) if 0 <= j < 96}
        nb = [sh[j] for j in (k - 1, k + 1) if j in sh]
        out["shift"] = {str(j): round(v, 1) for j, v in sh.items()}
        out["comp"] = float(max(nb) / -sh[k]) if sh[k] < 0 else None
        out["tap"] = bool(out["comp"] is not None and out["comp"] >= COMP_TAP)
    # 2b SOC dependence
    m = np.isin(day_rest, ev_days)
    b = np.floor(s_rest[m] / BIN)
    ub, cnt = np.unique(b, return_counts=True)
    keep = ub[cnt >= MIN_BIN_N]
    sc = np.array([np.median(s_rest[m][b == u]) for u in keep])
    med = np.array([np.median(dvk_rest[m][b == u]) for u in keep])
    out["n_bins"] = int(len(keep))
    span = float((keep.max() - keep.min()) * BIN) if len(keep) else 0.0       # OPEN-1
    out["soc_span"] = span
    if len(keep) < MIN_BINS or span < MIN_SPAN:
        out["soc_class"] = "unresolved"
    else:
        sse_off = float(((med - med.mean()) ** 2).sum())
        grid = np.arange(-80, 80.001, 0.25)
        pred = OCV(sc[None, :] - grid[:, None]) - OCV(sc[None, :])
        sse = ((pred - med[None, :]) ** 2).sum(1)
        i = int(sse.argmin())
        out.update(sse_off=sse_off, sse_soc=float(sse[i]), delta_soc=float(grid[i]))
        out["soc_class"] = ("soc-like" if sse[i] <= SSE_RATIO * sse_off else
                            "offset-like" if sse_off <= SSE_RATIO * sse[i] else "unresolved")
    out["final_class"] = "tap-fault-like" if out.get("tap") else out["soc_class"]
    # 2c current dependence (attribute)
    def rs(sel):
        return float(np.polyfit(I_drv[sel], dvk_drv[sel], 1)[0]) if sel.sum() >= 50 else np.nan
    if base_idx is not None:
        se, sb = rs(np.isin(day_drv, ev_days)), rs(np.isin(day_drv, days[base_idx]))
        out["dR_mohm"] = None if np.isnan(se - sb) else round(se - sb, 2)
    else:
        out["dR_mohm"] = None
    return out


def slim_daily(car):
    S = np.load(f"{SLIM}/vin{car}.npz")
    r = np.abs(S["I"]) < REST_A
    d = (S["t"][r] // 86400).astype(np.int64)
    x = (S["vmin"][r].astype(np.float64) - S["V"][r].astype(np.float64) / 96) * 1e3
    ud, inv, cnt = np.unique(d, return_inverse=True, return_counts=True)
    val = np.bincount(inv, x) / cnt
    ok = cnt >= MIN_REST
    return ud[ok], val[ok]


def one(car):
    C = np.load(f"{CELLS}/vin{car}.npz")
    t, I, odo, vmean = C["t"], C["I"], C["odo"], C["vmean_mv"]
    tf = C["t_full"]
    j = np.clip(np.searchsorted(t, tf), 0, len(t) - 1)
    match = t[j] == tf
    rest = match & (np.abs(I[j]) < REST_A)
    drv = match & (np.abs(I[j]) >= DRIVE_A)
    dv = C["dv_full"]
    dvr = dv[rest].astype(np.float32)
    day_r = (tf[rest] // 86400).astype(np.int64)
    ud, inv, cnt = np.unique(day_r, return_inverse=True, return_counts=True)
    M = np.zeros((len(ud), 96))
    np.add.at(M, inv, dvr)
    M /= cnt[:, None]
    okd = cnt >= MIN_REST
    days, D = ud[okd], M[okd]
    day_odo = (np.bincount(inv, odo[j[rest]].astype(np.float64)) / cnt)[okd]      # mean odometer per valid day
    s_rest = SOC(vmean[j[rest]])
    I_drv, day_drv, dvd = I[j[drv]], (tf[drv] // 86400).astype(np.int64), dv[drv]
    res = {"car": car, "n_valid_days": int(len(days)), "events": []}
    sd_days, sd_val = slim_daily(car)
    # per-cell event-days and events
    evmask = D < EV_MV
    for k in np.flatnonzero(evmask.any(0)):
        for r in runs(days[evmask[:, k]], GAP_D):
            qual = len(r) >= QUAL_N
            on, en = int(r[0]), int(r[-1])
            e = {"cell": int(k), "n_event_days": int(len(r)), "qualifying": bool(qual),
                 "onset_day": on, "end_day": en, "duration_days": en - on + 1,
                 "onset_km": float(day_odo[days == on][0]), "end_km": float(day_odo[days == en][0]),
                 "depth_mv": float(D[np.isin(days, r), k].min())}
            after = days > en
            va = D[after, k]
            e["recovered"] = bool((va > REC_MV).sum() >= REC_N)
            e["abrupt"] = bool(e["recovered"] and va[0] > REC_MV and days[after][0] - en <= ABRUPT_D)
            if qual:
                pre = np.flatnonzero(days < on)[-BASE_N:]
                post = np.flatnonzero(days > en)[:BASE_N]
                base = pre if len(pre) >= BASE_MIN else post if len(post) >= BASE_MIN else None
                e["baseline"] = "pre" if base is pre else "post" if base is not None else "none"
                e.update(classify(k, r, days, D, base, dvr[:, k], s_rest, day_r,
                                  dvd[:, k].astype(np.float64), I_drv, day_drv))
            res["events"].append(e)
    # agreement: day level over days valid in both (OPEN-3)
    both = np.intersect1d(days, sd_days)
    pc = set(days[evmask.any(1)].tolist()) & set(both.tolist())
    mo = set(sd_days[sd_val < EV_MV].tolist()) & set(both.tolist())
    mo_runs = runs(np.sort(sd_days[sd_val < EV_MV]), GAP_D)
    res["agree"] = {"n_both": int(len(both)), "pc_days": len(pc), "mo_days": len(mo), "both_days": len(pc & mo),
                    "pc_qual": any(e["qualifying"] for e in res["events"]),
                    "mo_qual": any(len(r) >= QUAL_N for r in mo_runs)}
    # forecast split
    if len(days) >= MIN_DAYS:
        nF = (len(days) - 1) // 2 + 1
        Fd = days[:nF]
        evF = bool(evmask[:nF].any())
        qualS = any(e["qualifying"] and e["onset_day"] > Fd[-1] for e in res["events"])
        anyS = bool(evmask[nF:].any())
        grp = "neg" if not evF and not anyS else "pos" if not evF and qualS else "excl"
        x = (Fd - Fd[0]) / 100.0
        sl = np.array([np.polyfit(x, D[:nF, c], 1)[0] for c in range(96)])
        mad = 1.4826 * np.median(np.abs(sl - np.median(sl)))
        A = float(-((sl - np.median(sl)) / mad).min()) if mad > 0 else np.nan
        mF = np.isin(sd_days, Fd)
        B = -slope((sd_days[mF] - Fd[0]) / 100.0, sd_val[mF])
        lead = [e["onset_day"] - int(Fd[-1]) for e in res["events"] if e["qualifying"] and e["onset_day"] > Fd[-1]]
        res["forecast"] = {"group": grp, "A": A, "B": B, "F_end_day": int(Fd[-1]), "median_day": int(Fd[-1]),
                           "lead_days": min(lead) if lead else None, "n_F_slim_days": int(mF.sum())}
    # labels for the consequence check
    if os.path.exists(f"{LABELS}/vin{car}.npz"):
        L = np.load(f"{LABELS}/vin{car}.npz")
        res["labels"] = {"t": L["t_end"].tolist(), "cap": L["capacity"].astype(float).tolist()}
    return res


def auc(pos, neg):
    pos, neg = np.asarray(pos), np.asarray(neg)
    gt = (pos[:, None] > neg[None, :]).sum() + 0.5 * (pos[:, None] == neg[None, :]).sum()
    return float(gt / (len(pos) * len(neg)))


def label_delta(lab, t0):
    t, c = np.array(lab["t"]), np.array(lab["cap"])
    b, a = c[(t >= t0 - LAB_WIN) & (t < t0)], c[(t > t0) & (t <= t0 + LAB_WIN)]
    return float(np.median(a) - np.median(b)) if len(b) >= 2 and len(a) >= 2 else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--jobs", type=int, default=10)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    cars = sorted(int(f[3:-4]) for f in os.listdir(CELLS) if f.startswith("vin") and f.endswith(".npz") and f[3:-4].isdigit())
    with Pool(a.jobs) as p:
        R = [r for r in p.imap_unordered(one, cars)]
    R.sort(key=lambda r: r["car"])
    tag = "MEASURED (Changan per-cell telemetry; CC BY-NC-SA 4.0, non-commercial)"

    # ---- step 1+2: catalogue
    ev = [dict(car=r["car"], **e) for r in R for e in r["events"]]
    q = [e for e in ev if e["qualifying"]]
    cls = {c: sum(e["final_class"] == c for e in q) for c in ["tap-fault-like", "soc-like", "offset-like", "unresolved"]}
    cat = {"tag": tag + "; classes DERIVED (evidence, not ground truth)", "n_vehicles": len(R),
           "n_vehicles_with_event_day": len({e["car"] for e in ev}),
           "n_vehicles_with_qualifying_event": len({e["car"] for e in q}),
           "n_events_all": len(ev), "n_qualifying": len(q),
           "qualifying_recovered": sum(e["recovered"] for e in q), "qualifying_abrupt": sum(e["abrupt"] for e in q),
           "baseline": {b: sum(e["baseline"] == b for e in q) for b in ["pre", "post", "none"]},
           "classes": cls, "tap_comp_values": sorted(round(e["comp"], 3) for e in q if e.get("comp") is not None),
           "events": q}
    json.dump(cat, open(f"{a.out}/events.json", "w"), indent=1)

    # ---- primary forecast test
    fc = [r["forecast"] | {"car": r["car"]} for r in R if "forecast" in r]
    pos = [f for f in fc if f["group"] == "pos" and np.isfinite(f["A"]) and np.isfinite(f["B"])]
    neg = [f for f in fc if f["group"] == "neg" and np.isfinite(f["A"]) and np.isfinite(f["B"])]
    out = {"tag": "DERIVED (AUC of MEASURED features vs MEASURED anomaly occurrence)", "preregistered_in": "2b9e629",
           "n_eligible": len(fc), "n_pos": len(pos), "n_neg": len(neg),
           "n_excl": sum(f["group"] == "excl" for f in fc),
           "n_dropped_nonfinite": sum(f["group"] in ("pos", "neg") for f in fc) - len(pos) - len(neg)}
    if len(pos) and len(neg):
        pa, na = np.array([f["A"] for f in pos]), np.array([f["A"] for f in neg])
        pb, nb = np.array([f["B"] for f in pos]), np.array([f["B"] for f in neg])
        aA, aB = auc(pa, na), auc(pb, nb)
        rng = np.random.default_rng(0)
        bs = []
        for _ in range(2000):
            ip, ineg = rng.integers(0, len(pa), len(pa)), rng.integers(0, len(na), len(na))
            x, y = auc(pa[ip], na[ineg]), auc(pb[ip], nb[ineg])
            bs.append((x, y, x - y))
        bs = np.array(bs)
        ci = lambda c: [float(np.percentile(bs[:, c], 2.5)), float(np.percentile(bs[:, c], 97.5))]
        out.update(AUC_A=aA, AUC_B=aB, diff=aA - aB, CI_A=ci(0), CI_B=ci(1), CI_diff=ci(2),
                   lead_days_pos=sorted(f["lead_days"] for f in pos),
                   pos_cars=[f["car"] for f in pos])
        if len(pos) < 8:
            out["decision"] = "UNDERPOWERED (< 8 positives) - descriptive only"
        elif aA >= 0.70 and out["CI_A"][0] > 0.5 and out["CI_diff"][0] > 0:
            out["decision"] = "Per-cell early warning SUPPORTED"
        elif out["CI_A"][0] > 0.5:
            out["decision"] = "Early warning exists but per-cell adds nothing resolvable over min/max"
        else:
            out["decision"] = "NOT SUPPORTED"
    json.dump(out | {"per_vehicle": fc}, open(f"{a.out}/forecast.json", "w"), indent=1)

    # ---- agreement
    ag = [r["agree"] for r in R]
    pcd, mod, bd = sum(x["pc_days"] for x in ag), sum(x["mo_days"] for x in ag), sum(x["both_days"] for x in ag)
    agr = {"tag": tag, "pc_event_days": pcd, "mo_event_days": mod, "both": bd,
           "frac_pc_days_seen_by_minonly": bd / pcd if pcd else None,
           "frac_mo_days_seen_by_percell": bd / mod if mod else None,
           "vehicles_pc_qual": sum(x["pc_qual"] for x in ag), "vehicles_mo_qual": sum(x["mo_qual"] for x in ag),
           "vehicles_both_qual": sum(x["pc_qual"] and x["mo_qual"] for x in ag),
           "vehicles_pc_only": [r["car"] for r in R if r["agree"]["pc_qual"] and not r["agree"]["mo_qual"]],
           "vehicles_mo_only": [r["car"] for r in R if r["agree"]["mo_qual"] and not r["agree"]["pc_qual"]]}
    json.dump(agr, open(f"{a.out}/agreement.json", "w"), indent=1)

    # ---- secondary consequence
    byc = {r["car"]: r for r in R}
    d_ev = []
    for e in q:
        lab = byc[e["car"]].get("labels")
        if lab:
            dd = label_delta(lab, e["onset_day"] * 86400.0)
            if dd is not None:
                d_ev.append({"car": e["car"], "cell": e["cell"], "delta_ah": dd})
    d_pl = []
    for f in neg:
        lab = byc[f["car"]].get("labels")
        if lab:
            dd = label_delta(lab, f["median_day"] * 86400.0)
            if dd is not None:
                d_pl.append(dd)
    con = {"tag": "DERIVED (DERIVED labels)", "n_event": len(d_ev), "n_placebo": len(d_pl), "events": d_ev,
           "median_event": float(np.median([x["delta_ah"] for x in d_ev])) if d_ev else None,
           "median_placebo": float(np.median(d_pl)) if d_pl else None}
    if len(d_ev) >= 2 and len(d_pl) >= 2:
        from scipy.stats import mannwhitneyu
        con["mannwhitney_p"] = float(mannwhitneyu([x["delta_ah"] for x in d_ev], d_pl).pvalue)
    json.dump(con, open(f"{a.out}/consequence.json", "w"), indent=1)

    print(json.dumps({k: v for k, v in cat.items() if k not in ("events", "tap_comp_values")}, indent=1))
    print(json.dumps({k: v for k, v in out.items()}, indent=1))
    print(json.dumps(agr, indent=1))
    print(json.dumps({k: v for k, v in con.items() if k != "events"}, indent=1))


if __name__ == "__main__":
    main()
