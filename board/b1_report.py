"""B1 report (briefs/B1/README.md §4.6): raw per-phase JSON / JSONL from board/run_b1.sh -> results/B1/b1.json and the
capability tables. Host side. No verdict; two flags defined in the brief, computed exactly as below (fixed before any
producer-on block was read):

- SUSTAINED: achieved >= 99 % of target, zero drop events over the phase, all three dump gates PASS.
- RT DISTURBED: for a real-time load (inference; limiter per pack size), the median over producer-on blocks of the
  block p99 exceeds the median over the same round's P0 blocks of the block p99 by > 20 %. A block counts for a phase
  only if its whole 60 s lies inside the phase. The worst single producer-on block (which holds the dumps) is reported
  beside it, descriptive.

Usage: python3 board/b1_report.py results/B1/raw results/B1/b1.json
"""
import glob
import json
import os
import re
import sys

import numpy as np

PHASES = {"P1": (3.2, 512), "P2": (32, 512), "P3": (3.2, 2048), "P4": (32, 2048), "P5": (60, 2048)}
EMMC_BYTES = 62160896 * 512          # census: mmcblk0 sectors x 512 B (whole device)
PE = (3000, 500)                     # ASSUMED (brief §4.4): MLC-class, TLC-class; write amplification 1.0
YEAR_S = 365.25 * 86400


def jl(p):
    return [json.loads(x) for x in open(p) if x.strip()]


def windows(raw):
    w = {}
    for e in jl(f"{raw}/timeline.jsonl"):
        w.setdefault((e["round"], e["phase"]), {})[e["event"]] = e["wall"]
    return w


def inside(b0, w, blk=60.0):
    return w.get("start") is not None and w.get("end") is not None and b0 >= w["start"] and b0 + blk <= w["end"]


def q(vals):
    v = np.array(vals, float)
    return {"n": int(len(v)), "median": float(np.median(v)), "min": float(v.min()), "max": float(v.max())} if len(v) else None


def rt_tables(raw, w, rounds):
    """Per round: e1 and limiter block statistics in P0 and in each producer phase."""
    out = {}
    for r in rounds:
        e1 = jl(f"{raw}/e1loop_r{r}.jsonl")
        lim = jl(f"{raw}/limloop_r{r}.jsonl")
        rr = {"e1_gate_all_pass": all(b["gate_pass"] for b in e1), "e1_blocks": len(e1),
              "lim_gate_all_pass": all(b["gate_pass"] for b in lim), "lim_blocks": len(lim), "phases": {}}
        for ph in ["P0"] + list(PHASES):
            win = w.get((r, ph))
            if not win:
                continue
            eb = [b for b in e1 if not b["partial"] and inside(b["wall_start"], win)]
            row = {"e1_p50_ms": q([b["p50_ms"] for b in eb]), "e1_p99_ms": q([b["p99_ms"] for b in eb])}
            for n in (96, 3564):
                lb = [b for b in lim if b["n_cells"] == n and b["partial"] is False and inside(b["wall_start"], win)]
                row[f"lim{n}_p50_ns"] = q([b["lat_ns_p50"] for b in lb])
                row[f"lim{n}_p99_ns"] = q([b["lat_ns_p99"] for b in lb])
                row[f"lim{n}_tick_late_max_us"] = q([b["tick_late_max_us"] for b in lb])
            rr["phases"][ph] = row
        base = rr["phases"].get("P0", {})
        for ph, row in rr["phases"].items():
            if ph == "P0":
                continue
            flags = {}
            for key in ("e1_p99_ms", "lim96_p99_ns", "lim3564_p99_ns"):
                b, p = base.get(key), row.get(key)
                if b and p:
                    flags[key] = {"ratio_median": p["median"] / b["median"], "ratio_worst_block": p["max"] / b["median"],
                                  "disturbed": p["median"] > 1.2 * b["median"]}
            row["rt_disturbed"] = flags
            row["RT_DISTURBED"] = any(f["disturbed"] for f in flags.values())
        out[r] = rr
    return out


def monitor(raw, w, r, ph):
    win = w.get((r, ph))
    p = f"{raw}/cpumon_r{r}.jsonl"
    if not win or not os.path.exists(p):
        return None
    rows = [x for x in jl(p) if win["start"] <= x["wall"] - 10 and x["wall"] <= win["end"]]
    if not rows:
        return None
    return {"cpu3_producer_pct": q([x["util_pct"]["cpu3"] for x in rows]),
            "cpu4_dumper_pct": q([x["util_pct"]["cpu4"] for x in rows]),
            "min_cur_khz": min(min(v for v in x["cur_khz"].values() if v) for x in rows),
            "a55_thermal_max_c": max(x["thermal_c"].get("a55-thermal", float("nan")) for x in rows),
            "dirty_kb_max": max(x.get("Dirty_kb", 0) for x in rows)}


def main():
    raw, out = sys.argv[1], sys.argv[2]
    w = windows(raw)
    rounds = sorted({r for r, _ in w})
    res = {"tag": "MEASURED on FRDM-IMX95-PRO (CPU producer: CPU cost is an upper bound on a DMA path)", "cells": {},
           "rt": rt_tables(raw, w, rounds), "emmc": {}}
    for ph, (rate, mb) in PHASES.items():
        reps = []
        for p in sorted(glob.glob(f"{raw}/ring_r*_{ph}.json")):
            r = int(re.search(r"ring_r(\d+)_", p).group(1))
            d = json.load(open(p))
            dumps = {int(x["window_s"]): x for x in d["dumps"]}
            sustained = d["achieved_frac"] >= 0.99 and d["drop_events"] == 0 and all(
                x.get("gate") == "PASS" for x in d["dumps"]) and len(d["dumps"]) == 3
            reps.append({"round": r, "achieved_mbps": d["achieved_mbps"], "achieved_frac": d["achieved_frac"],
                         "drop_events": d["drop_events"], "max_lag_ms": d["max_lag_ms"],
                         "bursts_late_gt_ms": d["bursts_late_gt_ms"],
                         "producer_thread_cpu_pct": d["producer_thread_cpu_pct"],
                         "depth_s_measured": d["measured_depth_s_final"], "depth_s_arithmetic": d["arithmetic_depth_s"],
                         "dumps": dumps, "SUSTAINED": bool(sustained), "monitor": monitor(raw, w, r, ph),
                         "RT_DISTURBED": res["rt"].get(r, {}).get("phases", {}).get(ph, {}).get("RT_DISTURBED")})
        res["cells"][ph] = {"rate_mbps": rate, "ring_mb": mb, "repeats": reps}
    for p in sorted(glob.glob(f"{raw}/emmc_r*.jsonl")):
        rows = jl(p)
        files = [x for x in rows if "file" in x and x["rc"] == 0 and x["bytes"] > 0]
        mbps = [x["bytes"] / 1e6 / (x["t_end"] - x["t_start"]) for x in files]
        tot = sum(x["bytes"] for x in files) / 1e6 / sum(x["t_end"] - x["t_start"] for x in files)
        res["emmc"][os.path.basename(p)] = {"mode": rows[0].get("mode"), "files": len(files),
                                           "seconds": sum(x["t_end"] - x["t_start"] for x in files),
                                           "per_file_mbps": q(mbps), "overall_mbps": tot,
                                           "free_kb_before": rows[0].get("free_kb_before"),
                                           "free_kb_after": rows[-1].get("free_kb_after")}
    if res["emmc"]:
        wr = float(np.median([v["overall_mbps"] for v in res["emmc"].values()]))
        res["emmc_derived"] = {
            "tag": "DERIVED from the MEASURED write rate and the census capacity; endurance ASSUMED (P/E 3000 MLC-class, "
                   "500 TLC-class; write amplification 1.0)",
            "write_mbps_used": wr, "capacity_bytes": EMMC_BYTES,
            "years_to_wearout": {f"{rate} MB/s": {f"PE{pe}": EMMC_BYTES * pe / (rate * 1e6) / YEAR_S for pe in PE}
                                 for rate in (3.2, 32, 60)},
            "can_sustain_as_ring_medium": {f"{rate} MB/s": wr >= rate for rate in (3.2, 32, 60)},
            "predicted_dump_s_N300": {f"{rate} MB/s": 300 * rate / wr for rate in (3.2, 32, 60)}}
    json.dump(res, open(out, "w"), indent=1, default=float)
    print(f"wrote {out}")
    for ph, c in res["cells"].items():
        for rep in c["repeats"]:
            ds = " ".join(f"N{n}:{x.get('gate')}({x.get('total_s', 0):.1f}s,{x.get('mismatched_frames', 0)})"
                          for n, x in rep["dumps"].items())
            print(ph, rep["round"], f"{rep['achieved_mbps']:.3f}", rep["drop_events"], f"{rep['max_lag_ms']:.2f}",
                  f"{rep['producer_thread_cpu_pct']:.2f}%", f"{rep['depth_s_measured']:.1f}s", ds,
                  "SUSTAINED" if rep["SUSTAINED"] else "-", "RT_DISTURBED" if rep["RT_DISTURBED"] else "")


if __name__ == "__main__":
    main()
