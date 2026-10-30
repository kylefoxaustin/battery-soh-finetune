"""X6 §3: knee definition and profile on ISU-ILCC (X5's data, units and split, unchanged). No forecaster (K0-K3),
warning score, AUC or reserve is computed here. Every number DERIVED from MEASURED lab labels. CC BY 4.0.

Knee onset (brief §3.1): for a cell, the first check k (with >= MIN_HIST earlier intervals) where
  drop_H(k) = (Q_k - Q_{k+H}) / Q_0 > T   and   drop_H(k) / (t_{k+H} - t_k) >= 2 x the median of the cell's own
  per-interval drop rates (Q_{j-1} - Q_j) / Q_0 / (t_j - t_{j-1}) over intervals j <= k.
Usage: nice python3 -E analysis/X6_profile.py
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import X5_estimate as X5                                         # noqa: E402  (data loading and units only)

OUT = "results/X/X6"
GRID_H = (1, 2, 3)
GRID_T = (0.03, 0.05, 0.08)
H0, T0 = 2, 0.05                                                 # brief defaults
RATE_X = 2.0
MIN_HIST = 3                                                     # >= 3 earlier intervals for the "so far" median
W = 4                                                            # X5's W: a warning at check j needs j >= W (Q(V) W checks earlier)
GATE = 30


def onsets(t, Q, H, T):
    """Per cell (column of Q): first knee onset index or None."""
    n, m = Q.shape
    out = []
    for c in range(m):
        q = Q[:, c] / Q[0, c]
        rate = (q[:-1] - q[1:]) / np.diff(t)                    # rate[j-1] = interval ending at check j
        k_on = None
        for k in range(MIN_HIST, n - H):
            d = q[k] - q[k + H]
            base = np.median(rate[:k])                           # intervals ending at checks 1..k
            if d > T and d / (t[k + H] - t[k]) >= RATE_X * max(base, 0.0):
                k_on = k
                break
        out.append(k_on)
    return out


def profile(units, ids, H, T, full=True):
    ev = []
    for g in ids:
        u = units[g]
        t, Q = u["t"], u["Q"]
        ons = onsets(t, Q, H, T)
        for c, k in enumerate(ons):
            if k is None:
                continue
            rec = {"g": g, "c": c, "k": k, "n": len(t), "drop": float((Q[k, c] - Q[k + H, c]) / Q[0, c]),
                   "cap_rel_at_onset": float(Q[k, c] / Q[0, c]), "first_in_unit": k == min(x for x in ons if
                                                                                       x is not None)}
            for L in (1, 2, 3):
                j = k - L
                rec[f"warnable_L{L}"] = j >= W                    # check j - W exists at the warning point
                rec[f"weakest_at_L{L}"] = bool(j >= 0 and int(np.argmin(Q[j])) == c)
            ev.append(rec)
    cells = sum(units[g]["Q"].shape[1] for g in ids)
    return ev, cells


def summarise(ev, cells, ids):
    s = {"events": len(ev), "cells": cells, "units_with_event": len({e["g"] for e in ev}), "units": len(ids)}
    if not ev:
        return s
    s["drop_median"] = float(np.median([e["drop"] for e in ev]))
    s["cap_rel_at_onset_median"] = float(np.median([e["cap_rel_at_onset"] for e in ev]))
    s["onset_check_median"] = float(np.median([e["k"] for e in ev]))
    for L in (1, 2, 3):
        w = [e for e in ev if e[f"warnable_L{L}"]]
        f = [e for e in w if e["first_in_unit"]]
        s[f"L{L}"] = {"warnable_events": len(w),
                      "already_weakest_all": float(np.mean([e[f"weakest_at_L{L}"] for e in w])) if w else None,
                      "first_in_unit_events": len(f),
                      "first_in_unit_already_weakest": float(np.mean([e[f"weakest_at_L{L}"] for e in f])) if f
                      else None,
                      "not_weakest_events": int(sum(not e[f"weakest_at_L{L}"] for e in w))}
    return s


def task_a_counts(units, ids, H, T):
    """Task A cell-checks: j >= W, j < the cell's onset, j + L <= n - 1. Positive: onset in (j, j + L]."""
    out = {}
    for L in (1, 2):
        pos = neg = 0
        for g in ids:
            t, Q = units[g]["t"], units[g]["Q"]
            for k in onsets(t, Q, H, T):
                for j in range(W, len(t) - L):
                    if k is not None and j >= k:
                        break
                    if k is not None and k - L <= j:
                        pos += 1
                    else:
                        neg += 1
        out[f"L{L}"] = {"positive": pos, "negative": neg}
    return out


def drop_distribution(units, ids):
    """H-check drops (fraction of Q_0) over all cells and checks with >= MIN_HIST history, and the ratio to the
    cell's running median rate; used only to justify H and T."""
    out = {}
    for H in GRID_H:
        d, r = [], []
        for g in ids:
            t, Q = units[g]["t"], units[g]["Q"]
            for c in range(Q.shape[1]):
                q = Q[:, c] / Q[0, c]
                rate = (q[:-1] - q[1:]) / np.diff(t)
                for k in range(MIN_HIST, len(t) - H):
                    dd = q[k] - q[k + H]
                    d.append(dd)
                    b = np.median(rate[:k])
                    r.append(dd / (t[k + H] - t[k]) / b if b > 0 else np.nan)
        d, r = np.array(d), np.array(r)
        out[f"H{H}"] = {"n": len(d), "drop_p50": float(np.percentile(d, 50)), "drop_p90": float(np.percentile(d, 90)),
                        "drop_p99": float(np.percentile(d, 99)),
                        "rate_ratio_p50": float(np.nanpercentile(r, 50)),
                        "rate_ratio_p90": float(np.nanpercentile(r, 90))}
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    sp = json.load(open("results/X/X5/split.json"))["ISU-ILCC"]
    cal, ev_ids = sp["calibration"], sp["evaluation"]
    cells = X5.load_cells()
    units = X5.build_units(cells, cal + ev_ids)
    first = {g: X5.truncate(u) for g, u in units.items()}
    res = {"split": sp, "rule": {"H": H0, "T": T0, "rate_x": RATE_X, "min_hist_intervals": MIN_HIST, "W": W},
           "drops_calibration": drop_distribution(units, cal), "grid": {}}
    for H in GRID_H:
        for T in GRID_T:
            key = f"H{H}_T{int(round(100 * T))}"
            row = {}
            for half, ids in (("calibration", cal), ("evaluation", ev_ids)):
                for life, U in (("full", units), ("first", first)):
                    e, nc = profile(U, ids, H, T)
                    row[f"{half}_{life}"] = summarise(e, nc, ids)
                    row[f"{half}_{life}"]["task_a"] = task_a_counts(U, ids, H, T)
                    if (H, T) == (H0, T0):
                        res.setdefault("events_default", {})[f"{half}_{life}"] = e
            res["grid"][key] = row
    json.dump(res, open(f"{OUT}/profile.json", "w"), indent=1, default=float)
    print(json.dumps(res["drops_calibration"], indent=1))
    for key, row in res["grid"].items():
        print(key, {k: (v["events"], v["units_with_event"]) for k, v in row.items()})
    print(json.dumps(res["grid"][f"H{H0}_T{int(100 * T0)}"], indent=1, default=float))


if __name__ == "__main__":
    main()
