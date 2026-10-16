"""Experiment F POST-HOC diagnostics (NOT pre-registered; written after seeing results/F/*.json). They change no
pre-registered decision. Questions:
  D1 do vehicles share a calendar (so same-date onsets across vehicles mean a fleet-wide cause)?
  D2 is the recurrence of one cell index across vehicles more than chance?
  D3 does the label rise after onset survive (a) one value per vehicle and (b) a calendar-matched placebo
     (same pseudo-onset date in every negative vehicle)? Tests the season / fleet-wide-time explanation.
  D4 are event-days colder than the vehicle's other valid days (pack mean probe temperature at rest)?
Usage: python analysis/F_diag.py --out results/F/diag.json
"""
import argparse, json
from collections import Counter
import numpy as np
from scipy.stats import wilcoxon

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); a = ap.parse_args()
    ev = json.load(open("results/F/events.json"))["events"]
    fc = json.load(open("results/F/forecast.json"))["per_vehicle"]
    neg = [f["car"] for f in fc if f["group"] == "neg"]
    out = {"tag": "POST-HOC, DERIVED"}
    # D1 calendar spans
    span = {}
    for c in sorted({e["car"] for e in ev} | set(neg)):
        t = np.load(f"data/changan/cells/vin{c}.npz")["t"]; t = t[np.isfinite(t)]
        span[c] = (int(t[0] // 86400), int(t[-1] // 86400))
    s = np.array(list(span.values()))
    out["D1_first_day_pct"] = np.percentile(s[:, 0], [0, 25, 50, 75, 100]).tolist()
    out["D1_last_day_pct"] = np.percentile(s[:, 1], [0, 25, 50, 75, 100]).tolist()
    on = sorted(e["onset_day"] for e in ev)
    out["D1_onset_days"] = on
    # D2 cell recurrence: deepest qualifying event's cell per vehicle; max multiplicity vs uniform-random null
    deep = {}
    for e in ev:
        if e["car"] not in deep or e["depth_mv"] < deep[e["car"]]["depth_mv"]:
            deep[e["car"]] = e
    cells = [e["cell"] for e in deep.values()]
    mx = max(Counter(cells).values())
    rng = np.random.default_rng(0)
    sim = [max(Counter(rng.integers(0, 96, len(cells))).values()) for _ in range(100000)]
    out["D2"] = {"n_vehicles": len(cells), "cell_counts": Counter(cells).most_common(5), "max_mult": mx,
                 "p_null_max_ge": float(np.mean(np.array(sim) >= mx)),
                 "cell31_events": [(e["car"], e["onset_day"], round(e["depth_mv"])) for e in ev if e["cell"] == 31]}
    # D3 labels
    W = 180 * 86400
    lab = {}
    for c in set(neg) | {e["car"] for e in ev}:
        try:
            L = np.load(f"data/changan/labels_full/vin{c}.npz"); lab[c] = (L["t_end"], L["capacity"].astype(float))
        except FileNotFoundError:
            pass
    def delta(c, t0):
        if c not in lab: return None
        t, y = lab[c]; b = y[(t >= t0 - W) & (t < t0)]; f = y[(t > t0) & (t <= t0 + W)]
        return float(np.median(f) - np.median(b)) if len(b) >= 2 and len(f) >= 2 else None
    rows = []
    for c in sorted({e["car"] for e in ev}):
        for e in sorted([e for e in ev if e["car"] == c], key=lambda e: e["onset_day"]):
            d = delta(c, e["onset_day"] * 86400.0)
            if d is None: continue
            pl = [x for x in (delta(n, e["onset_day"] * 86400.0) for n in neg) if x is not None]
            if len(pl) < 10: continue
            rows.append({"car": c, "cell": e["cell"], "onset_day": e["onset_day"], "delta": d,
                         "placebo_median_same_date": float(np.median(pl)), "n_placebo": len(pl),
                         "excess": d - float(np.median(pl)),
                         "placebo_pct_rank": float(np.mean(np.array(pl) < d))})
            break                                                       # first eligible event per vehicle
    out["D3"] = {"per_vehicle": rows, "n": len(rows),
                 "median_excess": float(np.median([r["excess"] for r in rows])) if rows else None,
                 "median_placebo_same_date": float(np.median([r["placebo_median_same_date"] for r in rows])) if rows else None,
                 "wilcoxon_p_excess": float(wilcoxon([r["excess"] for r in rows]).pvalue) if len(rows) >= 5 else None}
    # D4 temperature on event-days vs other valid days
    t4 = []
    for c in sorted({e["car"] for e in ev}):
        C = np.load(f"data/changan/cells/vin{c}.npz")
        r = np.abs(C["I"]) < 1.0
        d = (C["t"][r] // 86400).astype(np.int64); tm = C["tmean"][r].astype(float)
        ud, inv, cnt = np.unique(d, return_inverse=True, return_counts=True)
        dm = np.bincount(inv, tm) / cnt
        evd = set()
        for e in ev:
            if e["car"] == c: evd |= set(range(e["onset_day"], e["end_day"] + 1))
        m = np.isin(ud, list(evd)) & (cnt >= 20)
        o = ~np.isin(ud, list(evd)) & (cnt >= 20)
        if m.any() and o.any():
            t4.append({"car": c, "event_days_tmean": float(np.median(dm[m])), "other_days_tmean": float(np.median(dm[o]))})
    out["D4"] = {"per_vehicle": t4, "n_colder": sum(x["event_days_tmean"] < x["other_days_tmean"] for x in t4),
                 "median_diff_C": float(np.median([x["event_days_tmean"] - x["other_days_tmean"] for x in t4]))}
    json.dump(out, open(a.out, "w"), indent=1, default=int)
    print(json.dumps({k: (v if k != "D1_onset_days" else None) for k, v in out.items()}, indent=1, default=int))

if __name__ == "__main__":
    main()
