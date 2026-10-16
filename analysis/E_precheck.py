"""Experiment E §5 pre-check (pre-registered in results/E/E_power_analysis.md §5, commit fc9c79c, before this script
existed). Does causal per-cell state explain the within-unit residual that pack-scalar data treats as label noise?

Implements §5 exactly:
  units / residuals   frozen fold models runs/chf_{ls}_k{0..3}, held-out targets (as analysis/E_power.py)
  label time          charge-session start = t_end - seg_s (labels_full), matched to the fold's car file by
                      (mileage, capacity); features use frames with t < session start only
  window              frames with odo in (odo_label - 5 k km, odo_label]; if the unit has < 5 k km of data before
                      the label, the 30 days before session start instead
  centring            each unit's offset = mean residual of its first 10 labels (by odometer); those labels are not
                      scored; target = residual - offset for labels 11..
  features (per-cell) 1 median top-of-charge spread (status 1, max cell >= 4150 mV, synced)
                      2 median rest spread (|I| < 1 A, synced)
                      3 weakest cell's mean deviation from pack mean, rest frames (full vectors)
                      4 cross-cell SD of per-cell mean deviation, rest frames
                      5 slope of feature 3 over the preceding 30 k km, in 5 k km sub-windows (mV / 10 k km)
                      6 median probe-temperature spread
  features (min/max)  1, 2 from the scalar min/max columns (slim files: every frame, no cell list needed)
  model               OLS, standardised features, missing values -> training-fold median (NOT pre-registered;
                      the only implementation choice the pre-registration left open), CV by the same 4 unit folds
  metric              pooled out-of-fold R^2 = 1 - SSE / sum (y - mean_train)^2
  decision            GO iff R2_cell >= 0.26 (primary) and >= 0.39 (strict) AND R2_cell - R2_minmax >= 0.05 on both
Also: descriptive fleet-wide re-check of the brief's per-cell signal table (persistent weakest cell, spread growth).
Usage: python analysis/E_precheck.py --out results/E/precheck.json
"""
import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from E_power import residuals  # noqa: E402

THRESH = {"primary": 0.26, "strict": 0.39}   # pre-registered (α = 0.05 row of §5)
MARGIN = 0.05                                 # pre-registered per-cell-over-min/max margin
N_CENTRE = 10
WIN_KM, FALLBACK_S, SLOPE_KM, SUB_KM = 5_000, 30 * 86400, 30_000, 5_000
TOP_MV, REST_A = 4150, 1.0
CELLF = ["top_spread", "rest_spread", "weak_dev", "cross_sd", "weak_slope", "probe_spread"]
MMF = ["top_spread_mm", "rest_spread_mm"]


def label_times(car, km, cap):
    d = np.load(f"data/changan/labels_full/vin{car}.npz")
    t0 = d["t_end"] - d["seg_s"]
    out = np.full(len(km), np.nan)
    for i, (k, c) in enumerate(zip(km.astype(np.float32), cap.astype(np.float32))):
        j = np.flatnonzero((d["mileage"] == k) & (d["capacity"] == c))
        if len(j):
            out[i] = t0[j[0]]
    return out


def rest_dev(C, lo, hi, rest_full):
    """per-cell mean deviation over rest full-vectors with t in [lo, hi) -> (weak_dev, cross_sd) or nans"""
    a, b = np.searchsorted(C["t_full"], [lo, hi])
    m = rest_full[a:b]
    if m.sum() < 10:
        return np.nan, np.nan
    mu = C["dv_full"][a:b][m].astype(np.float64).mean(0)
    return float(mu.min()), float(mu.std())


def unit_features(car, km_lab, t_start):
    C = dict(np.load(f"data/changan/cells/vin{car}.npz"))
    S = dict(np.load(f"data/changan/slim/vin{car}.npz"))
    t, odo, sync = C["t"], C["odo"], C["sync"]
    spread = C["vmax_mv"] - C["vmin_mv"]
    top = (C["status"] == 1) & (C["vmax_mv"] >= TOP_MV) & sync
    rest = (np.abs(C["I"]) < REST_A) & sync
    pspread = C["tmax"] - C["tmin"]
    # rest flag for full vectors: nearest summary frame at the same timestamp
    j = np.clip(np.searchsorted(t, C["t_full"]), 0, len(t) - 1)
    rest_full = (np.abs(C["I"][j]) < REST_A) & (t[j] == C["t_full"])
    s_spread = (S["vmax"] - S["vmin"]) * 1e3
    s_top = (S["status"] == 1) & (S["vmax"] * 1e3 >= TOP_MV)
    s_rest = np.abs(S["I"]) < REST_A
    first_odo = float(odo[0]) if len(odo) else np.inf
    rows = []
    for k, ts in zip(km_lab, t_start):
        f = dict.fromkeys(CELLF + MMF, np.nan)
        if not np.isfinite(ts):
            rows.append(f); continue
        if first_odo > k - WIN_KM:
            lo_t = ts - FALLBACK_S
            w = (t >= lo_t) & (t < ts)
            ws = (S["t"] >= lo_t) & (S["t"] < ts)
        else:
            w = (odo > k - WIN_KM) & (odo <= k) & (t < ts)
            ws = (S["odo"] > k - WIN_KM) & (S["odo"] <= k) & (S["t"] < ts)
            lo_t = float(t[w].min()) if w.any() else ts
        if (w & top).any():
            f["top_spread"] = float(np.median(spread[w & top]))
        if (w & rest).any():
            f["rest_spread"] = float(np.median(spread[w & rest]))
        if w.any():
            f["probe_spread"] = float(np.median(pspread[w]))
        f["weak_dev"], f["cross_sd"] = rest_dev(C, lo_t, ts, rest_full)
        # slope of weak_dev over the preceding 30 k km in 5 k km sub-windows (by odometer -> time bounds)
        xs, ys = [], []
        for e in np.arange(k, k - SLOPE_KM, -SUB_KM):
            sw = (odo > e - SUB_KM) & (odo <= e) & (t < ts)
            if sw.sum() < 100:
                continue
            wd, _ = rest_dev(C, float(t[sw].min()), min(float(t[sw].max()) + 1, ts), rest_full)
            if np.isfinite(wd):
                xs.append(e - SUB_KM / 2); ys.append(wd)
        if len(xs) >= 2:
            f["weak_slope"] = float(np.polyfit(np.array(xs) / 1e4, ys, 1)[0])
        if (ws & s_top).any():
            f["top_spread_mm"] = float(np.median(s_spread[ws & s_top]))
        if (ws & s_rest).any():
            f["rest_spread_mm"] = float(np.median(s_spread[ws & s_rest]))
        rows.append(f)
    # descriptive: persistent weakest cell over life (rest full vectors, first vs last third of odometer)
    desc = {}
    if rest_full.sum() > 300:
        tf = C["t_full"][rest_full]
        dv = C["dv_full"][rest_full].astype(np.float64)
        thirds = np.array_split(np.arange(len(tf)), 3)
        mus = [dv[ix].mean(0) for ix in thirds]
        desc = {"weak_first": int(mus[0].argmin()), "weak_last": int(mus[2].argmin()),
                "weak_dev_first": float(mus[0].min()), "weak_dev_last": float(mus[2].min()),
                "cross_sd_first": float(mus[0].std()), "cross_sd_last": float(mus[2].std()),
                "rest_spread_med_first": float(np.median(spread[rest][: rest.sum() // 3])),
                "rest_spread_med_last": float(np.median(spread[rest][-(rest.sum() // 3):]))}
    return rows, desc


def ols_oof(F, y, fold):
    yhat = np.full_like(y, np.nan)
    sst = 0.0
    for k in np.unique(fold):
        tr, te = fold != k, fold == k
        med = np.nanmedian(F[tr], axis=0)
        Ft = np.where(np.isnan(F), med, F)
        mu, sd = Ft[tr].mean(0), Ft[tr].std(0) + 1e-9
        X = np.c_[np.ones(len(Ft)), (Ft - mu) / sd]
        beta, *_ = np.linalg.lstsq(X[tr], y[tr], rcond=None)
        yhat[te] = X[te] @ beta
        sst += float(((y[te] - y[tr].mean()) ** 2).sum())
    return 1 - float(((y - yhat) ** 2).sum()) / sst


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = {"tag": "DERIVED (OLS on MEASURED per-cell features vs residuals against DERIVED labels)",
           "preregistered_in": "results/E/E_power_analysis.md §5 @ fc9c79c", "thresholds": THRESH, "margin": MARGIN}
    desc_all, cache = {}, {}
    for ls in ["primary", "strict"]:
        Fc, Fm, Y, FO, UN = [], [], [], [], []
        n_unmatched = 0
        for k in range(4):
            for u in residuals(f"runs/chf_{ls}_k{k}"):
                car, km, y, p = u["car"], u["km"], u["y"], u["p"]
                if len(y) <= N_CENTRE:
                    continue
                r = y - p
                tgt = r[N_CENTRE:] - r[:N_CENTRE].mean()
                ts = label_times(car, km, y)
                n_unmatched += int(np.isnan(ts).sum())
                key = (car, tuple(km[N_CENTRE:]))
                if key not in cache:
                    rows, desc = unit_features(car, km[N_CENTRE:], ts[N_CENTRE:])
                    cache[key] = rows
                    desc_all[car] = desc
                rows = cache[key]
                Fc += [[f[c] for c in CELLF] for f in rows]
                Fm += [[f[c] for c in MMF] for f in rows]
                Y += list(tgt); FO += [k] * len(tgt); UN += [car] * len(tgt)
        Fc, Fm, Y, FO = np.array(Fc, float), np.array(Fm, float), np.array(Y), np.array(FO)
        r2c, r2m = ols_oof(Fc, Y, FO), ols_oof(Fm, Y, FO)
        out[ls] = {"n_units": len(set(UN)), "n_scored_labels": len(Y), "labels_unmatched_to_time": n_unmatched,
                   "missing_frac_per_feature": dict(zip(CELLF + MMF, np.r_[np.isnan(Fc).mean(0), np.isnan(Fm).mean(0)].round(3).tolist())),
                   "r2_oof_percell": r2c, "r2_oof_minmax": r2m, "r2_gain": r2c - r2m,
                   "threshold": THRESH[ls], "pass_r2": bool(r2c >= THRESH[ls]), "pass_margin": bool(r2c - r2m >= MARGIN)}
        print(ls, json.dumps(out[ls], indent=1), flush=True)
    out["decision"] = "E4 GO" if all(out[ls]["pass_r2"] and out[ls]["pass_margin"] for ls in THRESH) else \
        "NO-GO -> INCONCLUSIVE"
    d = [v for v in desc_all.values() if v]
    out["percell_signal_fleetwide"] = {
        "n_vehicles": len(d),
        "same_weakest_cell_first_vs_last_third": int(sum(v["weak_first"] == v["weak_last"] for v in d)),
        "weak_dev_mv_median_first_last": [float(np.median([v["weak_dev_first"] for v in d])),
                                          float(np.median([v["weak_dev_last"] for v in d]))],
        "cross_sd_mv_median_first_last": [float(np.median([v["cross_sd_first"] for v in d])),
                                          float(np.median([v["cross_sd_last"] for v in d]))],
        "rest_spread_mv_median_first_last": [float(np.median([v["rest_spread_med_first"] for v in d])),
                                             float(np.median([v["rest_spread_med_last"] for v in d]))],
        "per_vehicle": {str(k): v for k, v in desc_all.items()}}
    print("decision:", out["decision"])
    print(json.dumps({k: v for k, v in out["percell_signal_fleetwide"].items() if k != "per_vehicle"}, indent=1))
    json.dump(out, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
