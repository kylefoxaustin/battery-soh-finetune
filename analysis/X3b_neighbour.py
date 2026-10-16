"""Experiment X3-b (pre-registered in results/X/X3b_preregistration.md, commit ea9f714, before this script existed):
neighbour-referenced per-cell drift (A_nb) vs X3's pack-wide A; false-alarm rate on Changan vehicles with zero F event
days (healthy control); BatICM cars 2-4 POST-HOC descriptive. No p-values. Every number DERIVED.
Usage: python -E analysis/X3b_neighbour.py [--jobs 10]   (writes results/X/X3b/x3b.json)
"""
import argparse
import json
import os
import re
import sys
from multiprocessing import Pool

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import X3_casestudy as X3                              # noqa: E402

CELLS = "data/changan/cells"
OUT = "results/X/X3b"
Z_FLAG, N_CONSEC = X3.Z_FLAG, X3.N_CONSEC
MIN_FR, MIN_SPAN = X3.MIN_FR, X3.MIN_SPAN
NB_W, NB_MIN = 5, 3                                    # prereg §1: 5 cells each side, a side needs >= 3 cells
REST_C = {"changan": 6.0, "baticm": X3.REST_A["baticm"]}    # 0.05 C of 120 Ah (ASSUMED); BatICM as X3 DEV-1
F_REST_A, F_MIN_REST, F_EV_MV = 1.0, 20, -60.0         # F's event-day rule (F_faults.py)
BLOCK_SIZES = (6, 8, 12, 16, 24, 32, 48)
FEATS = ("A", "A_lvl", "A_nb", "A_nb_lvl", "A_mod")


def nb_ref(s):
    """Per cell: the closer of the left/right 5-cell medians (a side needs >= 3 cells). Vectorised."""
    n = len(s)
    pad = np.concatenate([np.full(NB_W, np.nan), s, np.full(NB_W, np.nan)])
    W = np.lib.stride_tricks.sliding_window_view(pad, NB_W)        # W[i] = pad[i : i+NB_W]
    L, R = W[np.arange(n)], W[np.arange(n) + NB_W + 1]             # cells k-5..k-1 and k+1..k+5
    with np.errstate(all="ignore"), __import__("warnings").catch_warnings():
        __import__("warnings").simplefilter("ignore")
        mL = np.where(np.isfinite(L).sum(1) >= NB_MIN, np.nanmedian(L, 1), np.nan)
        mR = np.where(np.isfinite(R).sum(1) >= NB_MIN, np.nanmedian(R, 1), np.nan)
    dL, dR = np.abs(s - mL), np.abs(s - mR)
    ref = np.where(np.isnan(dR) | (dL <= dR), mL, mR)
    return np.where(np.isnan(ref), np.median(s), ref)


def block_geometry(days_dev):
    """module_structure.py method: best (size, offset) by within- minus between-block corr of daily rest deviations."""
    M = days_dev - days_dev.mean(0)
    with np.errstate(invalid="ignore", divide="ignore"):
        R = np.corrcoef(M.T)
    np.fill_diagonal(R, np.nan)
    n = M.shape[1]
    best = (-np.inf, None, None)
    for size in BLOCK_SIZES:
        if size >= n:
            continue
        for off in range(size):
            blk = (np.arange(n) + off) // size
            same = blk[:, None] == blk[None, :]
            sc = np.nanmean(R[same]) - np.nanmean(R[~same])
            if sc > best[0]:
                best = (float(sc), size, off)
    return best


def evaluate(t, V, I, rest_a, eval_times, win, blk):
    rest = np.abs(I) <= rest_a
    tr, Vr = t[rest], V[rest]
    D = (Vr - np.median(Vr, 1)[:, None]) * 1e3
    rows = []
    for te in eval_times:
        lo, hi = np.searchsorted(tr, [te - win, te], side="right")
        if hi - lo < MIN_FR or (tr[hi - 1] - tr[lo]) < MIN_SPAN * win:
            rows.append(None)
            continue
        s = X3.slopes(tr[lo:hi], D[lo:hi])
        lv = np.median(D[lo:hi], 0)
        r = {"t": float(te), "A": X3.robust_z(s), "A_lvl": X3.robust_z(lv),
             "A_nb": X3.robust_z(s - nb_ref(s)), "A_nb_lvl": X3.robust_z(lv - nb_ref(lv))}
        if blk is not None:
            bm = np.array([np.median(s[blk == b]) for b in blk])
            r["A_mod"] = X3.robust_z(s - bm)
        rows.append(r)
    return rows


def episodes(rows, key):
    """Flag episodes: a cell's transition unflagged -> flagged (z <= -3.5 on 2 consecutive valid evaluations)."""
    run, flagged, ep = {}, set(), []
    for r in rows:
        if r is None or key not in r:
            run, flagged = {}, set()
            continue
        hit = set(np.where(r[key] <= Z_FLAG)[0].tolist())
        run = {k: run.get(k, 0) + 1 for k in hit}
        now = {k for k, n in run.items() if n >= N_CONSEC}
        new = sorted(now - flagged)
        if new:
            ep.append((r["t"], new))
        flagged = now
    return ep


# ---------------------------------------------------------------- Changan healthy control
def changan(car):
    C = np.load(f"{CELLS}/vin{car}.npz")
    t, I, tf = C["t"], C["I"].astype(np.float64), C["t_full"]
    j = np.clip(np.searchsorted(t, tf), 0, len(t) - 1)
    ok = t[j] == tf
    Ij = np.nan_to_num(I[j], nan=99.0)
    dv = C["dv_full"].astype(np.float64)
    # F's event-day rule (daily mean rest dv vs pack mean, |I| < 1 A, >= 20 frames, any cell < -60 mV)
    fr = ok & (np.abs(Ij) < F_REST_A)
    day = (tf[fr] // 86400).astype(np.int64)
    ud, inv, cnt = np.unique(day, return_inverse=True, return_counts=True)
    M = np.zeros((len(ud), 96))
    np.add.at(M, inv, dv[fr])
    M /= np.maximum(cnt, 1)[:, None]
    Mv = M[cnt >= F_MIN_REST]
    f_event_days = int((Mv < F_EV_MV).any(1).sum())
    geo = block_geometry(Mv) if len(Mv) >= 30 else (np.nan, None, None)
    blk = ((np.arange(96) + geo[2]) // geo[1]) if geo[1] else None
    V = (C["vmean_mv"][j].astype(np.float64)[:, None] + dv) / 1e3
    keep = ok & np.isfinite(V).all(1)
    th = tf[keep] / 3600.0
    ends = np.arange(np.floor(th[0] / 24) * 24 + 24, th[-1] + 24, 24.0)
    rows = evaluate(th, V[keep], Ij[keep], REST_C["changan"], ends, 7 * 24.0, blk)
    n_valid = sum(r is not None for r in rows)
    out = {"car": car, "f_event_days": f_event_days, "n_valid_days": n_valid, "geometry": geo[1:], "geo_score": geo[0]}
    for k in FEATS:
        ep = episodes(rows, k)
        out[f"ep_{k}"] = sum(len(c) for _, c in ep)
        out[f"sizes_{k}"] = [len(c) for _, c in ep]
    return out


# ---------------------------------------------------------------- BatICM (POST-HOC descriptive)
def baticm(car):
    d = pd.read_csv(f"{X3.BAT}/car{car}/car{car}_processed.csv")
    vc = sorted([c for c in d.columns if re.fullmatch(r"V_\d+", c)], key=lambda c: int(c[2:]))
    ts = pd.to_datetime(d["tboxTime"])
    t0 = ts.iloc[0]
    t_all = ((ts - t0).dt.total_seconds() / 3600).to_numpy()
    warn = d["BMSWarningInformation"].to_numpy()
    okr = d[vc].notna().all(1) & d["BMSBatteryCurrent"].notna()
    d, ts = d[okr], ts[okr]
    t = ((ts - t0).dt.total_seconds() / 3600).to_numpy()
    V = d[vc].to_numpy(float)
    I = d["BMSBatteryCurrent"].to_numpy(float)
    rest = np.abs(I) <= REST_C["baticm"]
    dd = (t[rest] // 24).astype(np.int64)
    ud, inv, cnt = np.unique(dd, return_inverse=True, return_counts=True)
    Dm = (V[rest] - np.median(V[rest], 1)[:, None]) * 1e3
    M = np.zeros((len(ud), V.shape[1]))
    np.add.at(M, inv, Dm)
    M /= cnt[:, None]
    M = M[cnt >= F_MIN_REST]
    geo = block_geometry(M) if len(M) >= 5 else (np.nan, None, None)
    blk = ((np.arange(V.shape[1]) + geo[2]) // geo[1]) if geo[1] else None
    day0 = t0.normalize()
    ends = [((day0 + pd.Timedelta(days=k + 1)) - t0).total_seconds() / 3600 for k in range(int(np.ceil(t[-1] / 24)) + 1)]
    ends = [e for e in ends if e <= t[-1] + 24]
    rows = evaluate(t, V, I, REST_C["baticm"], ends, 7 * 24.0, blk)
    w3 = np.where(warn >= 3)[0]
    l3 = float(t_all[w3[0]]) if len(w3) else None
    faulty = [c - 2 for c in X3.FAULTS[car]]          # primary convention V_(n-1), as X3
    out = {"case": f"BatICM car{car}", "faulty_cols": faulty, "first_level3_h": l3, "geometry": geo[1:]}
    for k in FEATS:
        ep = episodes(rows, k)
        first = {}
        for tt, cells in ep:
            for c in cells:
                first.setdefault(c, tt)
        hits = [first[c] for c in faulty if c in first]
        th = min(hits) if hits else None
        fl = sorted((tt, c) for c, tt in first.items())
        first_t = fl[0][0] if fl else None
        out[k] = {"first_correct_h": th, "first_correct_day": th / 24 if th is not None else None,
                  "first_flag_cells": [c for tt, c in fl if tt == first_t],
                  "first_flag_is_faulty": bool(fl and any(c in faulty for tt, c in fl if tt == first_t)),
                  "first_flag_tied": bool(fl and sum(tt == first_t for tt, c in fl) > 1),
                  "false_before": sum(1 for tt, c in fl if c not in faulty and (th is None or tt < th)),
                  "false_total": sum(1 for tt, c in fl if c not in faulty),
                  "episodes_total": sum(len(c) for _, c in ep),
                  "lead_vs_level3_days": (l3 - th) / 24 if (th is not None and l3 is not None) else None}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=10)
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    bat = [baticm(c) for c in (2, 3, 4)]
    print(json.dumps(bat, default=float)[:3000], flush=True)
    cars = sorted(int(f[3:-4]) for f in os.listdir(CELLS) if f.startswith("vin") and f[3:-4].isdigit())
    with Pool(a.jobs) as p:
        R = list(p.imap_unordered(changan, cars))
    R.sort(key=lambda r: r["car"])
    rng = np.random.default_rng(0)

    def rate(sel, k):
        ep = np.array([r[f"ep_{k}"] for r in sel], float)
        vd = np.array([r["n_valid_days"] for r in sel], float)
        return ep, vd

    res = {"tag": "DERIVED; Changan CC BY-NC-SA 4.0 (non-commercial), BatICM MIT", "preregistered_in": "ea9f714",
           "baticm_posthoc": bat}
    groups = {"control_no_F_event_days": [r for r in R if r["f_event_days"] == 0 and r["n_valid_days"] > 0],
              "context_F_event_vehicles": [r for r in R if r["f_event_days"] > 0 and r["n_valid_days"] > 0]}
    for g, sel in groups.items():
        d = {"n_vehicles": len(sel), "vehicle_days": int(sum(r["n_valid_days"] for r in sel))}
        for k in FEATS:
            ep, vd = rate(sel, k)
            d[k] = {"fa_per_100_vd": float(100 * ep.sum() / vd.sum()),
                    "frac_vehicles_ge1": float((ep > 0).mean()),
                    "episode_size_hist": np.bincount(np.minimum([s for r in sel for s in r[f"sizes_{k}"]], 10),
                                                     minlength=11).tolist() if any(r[f"sizes_{k}"] for r in sel) else []}
        epA, vd = rate(sel, "A")
        epN, _ = rate(sel, "A_nb")
        bs = []
        for _ in range(1000):
            i = rng.integers(0, len(sel), len(sel))
            bs.append(epN[i].sum() / max(epA[i].sum(), 1e-9))
        d["ratio_A_nb_over_A"] = float(epN.sum() / max(epA.sum(), 1e-9))
        d["ratio_CI"] = [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]
        if g.startswith("control"):
            r_, ci = d["ratio_A_nb_over_A"], d["ratio_CI"]
            d["reading"] = ("REDUCES FALSE ALARMS" if (r_ <= 0.5 and ci[1] < 1) else
                            "NO REDUCTION" if (r_ >= 0.8 or ci[0] <= 1 <= ci[1]) else "PARTIAL")
            d["A_nb_usable_bar_le_1_per_100vd"] = d["A_nb"]["fa_per_100_vd"] <= 1.0
        res[g] = d
    res["detection_retained_baticm"] = {k: sum(b[k]["first_correct_h"] is not None for b in bat) for k in FEATS}
    json.dump(res, open(f"{OUT}/x3b.json", "w"), indent=1, default=float)
    json.dump(R, open(f"{OUT}/x3b_changan_per_vehicle.json", "w"), default=float)
    print(json.dumps({k: v for k, v in res.items() if k != "baticm_posthoc"}, indent=1, default=float))


if __name__ == "__main__":
    main()
