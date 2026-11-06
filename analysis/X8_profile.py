"""Experiment X8, mandatory first step (brief briefs/X8/README.md §3): profile of the bottom of the SOC range.
NO limiter quantity is computed here (no admissible current, no kappa, no S, no reference limit). Committed with the
pre-registration, before any limiter code.

Changan 300-EV (CC BY-NC-SA 4.0, research only), from data/changan/lowsoc/ (data/changan_lowsoc.py: every frame with
soc < 30 %, all 96 cell voltages at 1 mV). Beihang (CC BY 4.0) eligibility only, through X2C_profile.load (restricted
unpickler). Every number DERIVED from field telemetry; V_cut and 1 C are ASSUMED.
Usage: python -E analysis/X8_profile.py [--jobs 12]   (writes results/X/X8/profile.json, split.json)
"""
import argparse
import glob
import json
import os
import sys
from multiprocessing import Pool

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

OUT = "results/X/X8"
SRC = "data/changan/lowsoc"
Q_C = 120.0          # ASSUMED 1 C in A: X2's OPEN-3 (fleet fast-charge capacity label median ~120-126 Ah, DERIVED)
I_DIS = 1.0          # CHOSEN: a discharge frame carries > 1 A discharge (source sign: discharge > 0) and status != 1
SEG_GAP_S = 30.0     # CHOSEN: a segment breaks at a gap > 30 s (frames are 10 s)
SEG_MIN = 6          # brief §3.1: >= 6 frames
STEP_C, STEP_DT_S, STEP_DT_K = 0.3, 30.0, 1.0   # X2 identification: |dI| >= 0.3 C, <= 30 s apart, pack-mean T within 1 K
SOC_SCORE, SOC_DEEP, COLD_C = 20.0, 10.0, 10.0
MIN_STEPS, HIST_S = 20, 30 * 86400.0             # >= 20 steps per half (X2-F); history window 30 days (X2 base)
BINS = np.arange(2000, 4501)                     # mV histogram of the frame's minimum cell voltage
V_OK_MV = (2000, 4500)                           # validity as X2-C: every cell within 2.0-4.5 V (drops 0 mV readings)


def load(n):
    Z = np.load(f"{SRC}/vin{n}.npz")
    out = {k: Z[k] for k in ("t", "soc", "I", "status", "V_mv", "T_c", "sync")}
    vr = (out["V_mv"].min(1) >= V_OK_MV[0]) & (out["V_mv"].max(1) <= V_OK_MV[1])
    out["n_implausible"] = int((out["sync"] & ~vr).sum())
    out["sync"] = out["sync"] & vr
    return out


def segments(t, d):
    """Contiguous discharge runs (d True, gaps <= SEG_GAP_S) of >= SEG_MIN frames, as index arrays."""
    idx = np.flatnonzero(d)
    if not len(idx):
        return []
    brk = np.flatnonzero((np.diff(idx) != 1) | (np.diff(t[idx]) > SEG_GAP_S)) + 1
    return [s for s in np.split(idx, brk) if len(s) >= SEG_MIN]


def steps(Z, drive_only=True):
    t, I, st, sync = Z["t"], Z["I"].astype(np.float64), Z["status"], Z["sync"]
    V = Z["V_mv"].astype(np.float64)
    Ic = -I                                                   # charge-positive, as X2
    Tm = Z["T_c"].astype(np.float64).mean(1)
    ok = sync & np.isfinite(I)
    if drive_only:
        ok &= st != 1
    dI = np.diff(Ic)
    k = np.flatnonzero(ok[:-1] & ok[1:] & (np.diff(t) <= STEP_DT_S) & (np.diff(t) > 0)
                       & (np.abs(dI) >= STEP_C * Q_C) & (np.abs(np.diff(Tm)) <= STEP_DT_K))
    r = (V[k + 1] - V[k]) / dI[k][:, None]                    # mV/A = mOhm
    return t[k + 1], Z["soc"][k + 1], r


def spearman(a, b):
    ra, rb = np.argsort(np.argsort(a)), np.argsort(np.argsort(b))
    return float(np.corrcoef(ra, rb)[0, 1])


def vehicle(n):
    Z = load(n)
    t, soc, I, st, sync = Z["t"], Z["soc"], Z["I"].astype(np.float64), Z["status"], Z["sync"]
    out = {"veh": n, "frames_lowsoc30": int(len(t)), "frames_implausible_cell": Z["n_implausible"]}
    hist = np.zeros(len(BINS), np.int64)
    if not len(t):
        return out, hist
    V = Z["V_mv"]
    vmin = V.min(1)
    tcold = Z["T_c"].min(1)
    d = sync & (I > I_DIS) & (st != 1)
    segs = segments(t, d)
    s20 = [s for s in segs if soc[s].min() < SOC_SCORE]
    s10 = [s for s in segs if soc[s].min() < SOC_DEEP]
    f20 = np.concatenate([s[soc[s] < SOC_SCORE] for s in s20]) if s20 else np.zeros(0, int)
    out.update({"segments": len(segs), "segments_lt20": len(s20), "segments_lt10": len(s10),
                "frames_lt20": int(len(f20)),
                "frames_lt10": int(sum((soc[s] < SOC_DEEP).sum() for s in s10)),
                "seg_frames_median": float(np.median([len(s) for s in s20])) if s20 else None})
    hd = vmin[d] - BINS[0]
    hist += np.bincount(np.clip(hd, 0, len(BINS) - 1).astype(np.int64), minlength=len(BINS))
    out["vmin_any_lowsoc_mv"] = int(vmin[sync].min()) if sync.any() else None
    if len(f20):
        Ii = I[f20] / Q_C
        out.update({"I_C_p5": float(np.percentile(Ii, 5)), "I_C_p50": float(np.percentile(Ii, 50)),
                    "I_C_p95": float(np.percentile(Ii, 95)), "I_A_p95": float(np.percentile(I[f20], 95)),
                    "vmin_reached_mv": int(vmin[f20].min()), "tcold_min_c": int(tcold[f20].min()),
                    "frames_lt20_cold": int((tcold[f20] < COLD_C).sum())})
    ts, ss, r = steps(Z)
    out["steps_drive_lt30"] = int(len(ts))
    out["steps_all_lt30"] = int(len(steps(Z, drive_only=False)[0]))
    m20 = ss < SOC_SCORE
    out["steps_drive_lt20"] = int(m20.sum())
    if m20.sum() >= 2 * MIN_STEPS:
        r20 = r[m20]
        Rc = np.median(r20, 0)
        out.update({"R_c_median_mohm": float(np.median(Rc)), "R_max_over_median": float(Rc.max() / np.median(Rc)),
                    "R_split_half_spearman": spearman(np.median(r20[0::2], 0), np.median(r20[1::2], 0))})
        if len(f20):
            # profile only, non-causal (whole-vehicle R): is the present minimum-voltage cell the highest-R cell?
            out["minV_is_maxR_frac"] = float((V[f20].argmin(1) == Rc.argmax()).mean())
            sag = I[f20] * np.median(Rc)                       # mV: |I_t * R_c| at the observed current
            out["sag_observed_median_mv"] = float(np.median(sag))
    # history: low-SOC drive steps (soc < 30) in the 30 days before each scored frame
    if len(f20):
        tf = t[f20]
        nh = np.searchsorted(ts, tf, "left") - np.searchsorted(ts, tf - HIST_S, "left")
        out["frames_lt20_hist20"] = int((nh >= MIN_STEPS).sum())
        out["frames_lt20_hist2x20"] = int((nh >= 2 * MIN_STEPS).sum())
        e = nh >= 2 * MIN_STEPS
        out["frames_lt10_hist2x20"] = int((e & (soc[f20] < SOC_DEEP)).sum())
        out["frames_cold_hist2x20"] = int((e & (tcold[f20] < COLD_C)).sum())
    return out, hist


def beihang(args):
    import X2C_profile as P
    fleet, n = args
    V, Ic, T, S, valid = P.load(fleet, n)
    dis = valid & (Ic < -I_DIS)
    qref = json.load(open("results/X/X2C/frozen.json"))[fleet]["Q_ref_Ah"]
    ok = valid & (Ic < I_DIS)                               # not charging (no status column)
    k = np.flatnonzero(ok[:-1] & ok[1:] & (np.abs(np.diff(Ic)) >= STEP_C * qref) & (np.abs(np.diff(T)) <= STEP_DT_K)
                       & (S[1:] < 0.30))
    f20 = np.flatnonzero(dis & (S < 0.20))
    nh = np.searchsorted(k + 1, f20, "left") - np.searchsorted(k + 1, f20 - 86400, "left")
    vm = np.rint(V.min(1) * 1e3).astype(np.int64)[dis & (S < 0.30)] - BINS[0]
    hist = np.bincount(np.clip(vm, 0, len(BINS) - 1), minlength=len(BINS))
    Vmv = V * 1e3
    rp = (Vmv[k + 1].mean(1) - Vmv[k].mean(1)) / np.diff(Ic)[k]          # mean-cell step R, mOhm
    u = np.unique(np.rint(Vmv[valid][:20000] * 1000).astype(np.int64)) / 1000.0
    return {"fleet": fleet, "veh": n, "frames": int(len(S)), "dis": int(dis.sum()), "_hist": hist.tolist(),
            "lsb_mv": float(np.diff(u).min()) if len(u) > 1 else None,
            "R_mean_cell_mohm": float(np.median(rp)) if len(k) >= 2 * MIN_STEPS else None,
            "I_A_p95": float(np.percentile(-Ic[f20], 95)) if len(f20) else None,
            "steps_lt30": int(len(k)), "dis_lt20_hist2x20": int((nh >= 2 * MIN_STEPS).sum()),
            "dis_lt20": int((dis & (S < 0.20)).sum()), "dis_lt10": int((dis & (S < 0.10)).sum()),
            "soc_min": float(np.nanmin(S[valid])) if valid.any() else None}


def pct(h, q):
    c = np.cumsum(h)
    return int(BINS[np.searchsorted(c, q / 100.0 * c[-1])])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=12)
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    vins = sorted(int(os.path.basename(p)[3:-4]) for p in glob.glob(f"{SRC}/vin*.npz"))
    with Pool(a.jobs) as p:
        res = p.map(vehicle, vins, chunksize=2)
    rows = [r for r, _ in res]
    h = np.sum([x for _, x in res], 0)
    Z = load(vins[0])
    lsb_v = int(np.diff(np.unique(Z["V_mv"][:20000])).min())
    lsb_i = float(np.round(np.diff(np.unique(Z["I"])).min(), 3))
    fleet_min = min(r["vmin_any_lowsoc_mv"] for r in rows if r.get("vmin_any_lowsoc_mv") is not None)
    p01 = pct(h, 0.1)
    vcut = int(np.floor(p01 / 10.0) * 10)
    R = np.array([r["R_c_median_mohm"] for r in rows if "R_c_median_mohm" in r])
    I95 = np.array([r["I_A_p95"] for r in rows if "I_A_p95" in r])
    sag_obs = np.array([r["sag_observed_median_mv"] for r in rows if "sag_observed_median_mv" in r])
    g = lambda k, v: sum(1 for r in rows if r.get(k, 0) >= v)
    summary = {
        "tag": "DERIVED; Changan CC BY-NC-SA 4.0 (research only); V_cut and 1 C ASSUMED; profile, no limiter quantity",
        "vehicles": len(rows), "frames_implausible_cell": int(sum(r["frames_implausible_cell"] for r in rows)),
        "lsb_cell_mv": lsb_v, "lsb_current_a": lsb_i, "one_C_A_assumed": Q_C,
        "fleet_min_cell_mv_lowsoc_any": fleet_min, "discharge_min_cell_p0.1_mv": p01,
        "discharge_min_cell_p1_mv": pct(h, 1.0), "discharge_min_cell_p50_mv": pct(h, 50.0),
        "V_cut_mv": vcut, "V_cut_sensitivity_mv": [vcut - 50, vcut + 50],
        "fleet_median_R_mohm": float(np.median(R)), "fleet_p95_current_A_median_vehicle": float(np.median(I95)),
        "sag_admitted_approx_mv": float(np.median(R) * np.median(I95)),
        "sag_admitted_approx_lsb": float(np.median(R) * np.median(I95) / lsb_v),
        "sag_observed_median_mv_median_vehicle": float(np.median(sag_obs)),
        "vehicles_with_lt20_segment": g("segments_lt20", 1), "vehicles_with_lt10_segment": g("segments_lt10", 1),
        "power_vehicles_20frames_hist20": g("frames_lt20_hist20", 20),
        "power_vehicles_20frames_hist2x20": g("frames_lt20_hist2x20", 20),
        "lt10_vehicles_20frames_hist2x20": g("frames_lt10_hist2x20", 20),
        "cold_vehicles_20frames_hist2x20": g("frames_cold_hist2x20", 20),
        "scored_frames_hist2x20": int(sum(r.get("frames_lt20_hist2x20", 0) for r in rows)),
    }
    for k in ("R_c_median_mohm", "R_max_over_median", "R_split_half_spearman", "minV_is_maxR_frac", "steps_drive_lt20",
              "steps_drive_lt30", "frames_lt20", "segments_lt20", "I_C_p5", "I_C_p50", "I_C_p95", "vmin_reached_mv",
              "tcold_min_c"):
        x = np.array([r[k] for r in rows if r.get(k) is not None], float)
        summary[f"{k}_vehicle_p10_p50_p90"] = [float(v) for v in np.percentile(x, [10, 50, 90])] if len(x) else None
    # folds (CHOSEN): serpentine by eligible-frame count (ties by vin), all 300 vehicles
    order = sorted(rows, key=lambda r: (-r.get("frames_lt20_hist2x20", 0), r["veh"]))
    half = {"A": [], "B": []}
    for i, r in enumerate(order):
        half["AB"[(i % 4) in (1, 2)]].append(r["veh"])
    summary["fold_frames"] = {k: int(sum(next(x for x in rows if x["veh"] == v).get("frames_lt20_hist2x20", 0)
                                         for v in vs)) for k, vs in half.items()}
    import X2C_profile as P                                     # noqa: F401  (Beihang, restricted unpickler)
    G = sys.modules["G2_beihang"]
    bj = [(f, int(p.split("/")[-2])) for f in ("QAS", "DTI") for p in sorted(glob.glob(f"{G.ROOT}/{f}/*/vin_2.pkl"))]
    with Pool(a.jobs) as p:
        bh = p.map(beihang, bj, chunksize=4)
    summary["beihang"], bsplit = {}, {}
    for f in ("QAS", "DTI"):
        lab = P.labels(f)
        B = [b for b in bh if b["fleet"] == f and lab.get(b["veh"]) == 0]           # normal vehicles, as X2-C
        hb = np.sum([b["_hist"] for b in B], 0)
        p01b = pct(hb, 0.1)
        elig = [b for b in B if b["dis_lt20_hist2x20"] >= 20]
        ob = sorted(B, key=lambda b: (-b["dis_lt20_hist2x20"], b["veh"]))
        bsplit[f] = {"A": [b["veh"] for i, b in enumerate(ob) if (i % 4) not in (1, 2)],
                     "B": [b["veh"] for i, b in enumerate(ob) if (i % 4) in (1, 2)]}
        summary["beihang"][f] = {
            "vehicles_all": sum(b["fleet"] == f for b in bh), "vehicles_normal": len(B),
            "discharge_frames": sum(b["dis"] for b in B), "discharge_frames_soc_lt20": sum(b["dis_lt20"] for b in B),
            "discharge_frames_soc_lt10": sum(b["dis_lt10"] for b in B),
            "vehicles_ge20_discharge_lt20": sum(b["dis_lt20"] >= 20 for b in B),
            "power_vehicles_20frames_hist2x20": len(elig),
            "scored_frames_hist2x20": int(sum(b["dis_lt20_hist2x20"] for b in B)),
            "steps_lt30_vehicle_p50": float(np.median([b["steps_lt30"] for b in B])),
            "discharge_min_cell_p0.1_mv": p01b, "V_cut_mv": int(np.floor(p01b / 10.0) * 10),
            "lsb_cell_mv": min(b["lsb_mv"] for b in B if b["lsb_mv"]),
            "fleet_median_R_mohm": float(np.median([b["R_mean_cell_mohm"] for b in B if b["R_mean_cell_mohm"]])),
            "fleet_p95_current_A_median_vehicle": float(np.median([b["I_A_p95"] for b in B if b["I_A_p95"]])),
            "fold_frames": {k: int(sum(b["dis_lt20_hist2x20"] for b in B if b["veh"] in v))
                            for k, v in bsplit[f].items()},
            "soc_min_p10_p50": [float(v) for v in np.percentile(
                [b["soc_min"] for b in B if b["soc_min"] is not None], [10, 50])]}
        x = summary["beihang"][f]
        x["sag_admitted_approx_mv"] = x["fleet_median_R_mohm"] * x["fleet_p95_current_A_median_vehicle"]
        x["sag_admitted_approx_lsb"] = x["sag_admitted_approx_mv"] / x["lsb_cell_mv"]
    for b in bh:
        b.pop("_hist")
    json.dump({"summary": summary, "vehicles": rows, "beihang": bh}, open(f"{OUT}/profile.json", "w"), indent=1)
    json.dump({"rule": "serpentine ABBA by frames_lt20_hist2x20 desc, ties by vin; fixed before limiter code",
               "changan": half, "beihang": bsplit}, open(f"{OUT}/split.json", "w"), indent=1)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
