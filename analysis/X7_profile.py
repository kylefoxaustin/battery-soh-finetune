"""X7 §3: profile of the McMaster 72S drive-cycle runs for a hottest-cell thermal-margin test. No observer, model, margin
or score is computed here. Every number DERIVED from MEASURED surface thermistors, voltages and current; conditions
SOURCED from file names and the dataset README. CC BY 4.0 (Naguib et al., Borealis doi:10.5683/SP3/UYPYDJ).

Fixed here, before any model exists (brief §3.3-3.4): the emulated probe layout (one per three cells, cells 1, 4, 7, ...,
next cell up if dead) and the two folds.
Usage: nice python3 -E analysis/X7_profile.py
"""
import glob
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from X2_replay import MCM, QREF_M                                 # noqa: E402  (loader constants reused, R not re-derived)

OUT = "results/X/X7"
STEP_C = 0.3                                                      # R-identification step, as X2 (|dI| >= 0.3 C)
PROBE_EVERY = {"1per3": 3, "1per2": 2, "percell": 1}
FOLDS = {                                                         # CHOSEN (brief §3.4): cycle pairs split across
    "A": ["HWCUST_15C", "HWFET_25C", "LA92_15C", "UDDS_25C", "US06_15C",           # temperatures; abnormal-cooling
          "Fanoffon_15C_Long", "UDDS_Blocked_25C"],                                # runs split: fan + blocking in
    "B": ["HWCUST_25C", "HWFET_15C", "LA92_25C", "UDDS_15C", "US06_25C",           # each fold
          "HWFET_15C_ModuleBlocked_Long", "LA92_HighFan_15C"],
}
GATE_K, GATE_FRAC, GATE_RUNS = 3.0, 0.10, 4


def run_name(p):
    return os.path.basename(p).replace("_with_TEM_data.mat", "").replace("_with_TEM.mat", "")


def condition(name):
    """SOURCED from the file name (README §1: fan malfunction, flow blockage)."""
    chamber = 25 if "_25C" in name else 15
    if "Fanoffon" in name:
        cool = "fan off then on"
    elif "ModuleBlocked" in name:
        cool = "module blocked"
    elif "Blocked" in name:
        cool = "blocked"
    elif "HighFan" in name:
        cool = "high fan"
    else:
        cool = "normal"
    return chamber, cool, name.split("_")[0]


def dead_channels(T):
    """X2_replay.mcm_load's rule (constant, or > 10 K below the pack median), plus channels stuck at one value for
    > 50 % of a run while the pack median moves >= 2 K (reported, not excluded unless also caught by the X2 rule)."""
    med = np.median(T)
    dead = [k for k in range(T.shape[1]) if np.ptp(T[:, k]) == 0 or np.median(T[:, k]) < med - 10]
    moving = np.ptp(np.median(T, 1)) >= 2
    stuck = []
    for k in range(T.shape[1]):
        if k in dead or not moving:
            continue
        _, cnt = np.unique(T[:, k], return_counts=True)
        if cnt.max() / len(T) > 0.5 and np.ptp(T[:, k]) < 1.0:
            stuck.append(k)
    return dead, stuck


def probes(live, every, offset=0):
    """1-indexed layout cells 1+offset, 1+offset+every, ...; a dead probe cell moves to the next live cell up."""
    out, moved = [], []
    for c in range(offset, 72, every):
        d = c
        while d < 72 and (d not in live or d in out):
            d += 1
        if d < 72:
            out.append(d)
            if d != c:
                moved.append((c + 1, d + 1))
    return out, moved


def quiet_noise(T, I):
    """1 Hz thermistor noise at rest: first 30 s, and the quietest 30 s window of |I| (by mean |I|)."""
    w = 30
    s = np.convolve(np.abs(I), np.ones(w) / w, mode="valid")
    j = int(np.argmin(s))
    out = {}
    for lab, a in (("first30s", 0), ("quietest30s", j)):
        X = T[a:a + w]
        dx = np.diff(X, axis=0)
        out[lab] = {"start_s": a, "mean_abs_I_A": float(np.abs(I[a:a + w]).mean()),
                    "sd_per_channel_median_K": float(np.median(X.std(0))),
                    "frac_frames_channel_changes": float((dx != 0).mean())}
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    import scipy.io as sio
    runs, allT = [], {}
    for p in sorted(glob.glob(f"{MCM}/*.mat")):
        name = run_name(p)
        m = sio.loadmat(p, squeeze_me=True)
        T = m["CellTemp_R"].astype(np.float64)
        I = m["Current_R2"].astype(np.float64)
        t = m["Temptime"].astype(np.float64)
        dead, stuck = dead_channels(T)
        live = [c for c in range(72) if c not in dead]
        Tl = T[:, live]
        fin = np.isfinite(Tl).all(1) & np.isfinite(I)
        Th, Tm = Tl.max(1), np.median(Tl, 1)
        sp = (Th - Tm)[fin]
        dI = np.abs(np.diff(I))
        chamber, cool, cycle = condition(name)
        q = np.unique(np.round(np.diff(np.unique(T[np.isfinite(T)])), 3))
        hot = np.argmax(np.where(np.isfinite(Tl), Tl, -np.inf), 1)
        r = {"run": name, "chamber_C": chamber, "cooling": cool, "cycle": cycle, "frames": int(len(t)),
             "duration_s": float(t[-1] - t[0] + 1), "time_steps_s": sorted(set(np.round(np.diff(t), 3).tolist())),
             "nonfinite_frames": int((~fin).sum()),
             "I_A_p5_p50_p95": [float(np.percentile(I, x)) for x in (5, 50, 95)],
             "I_C_p5_p50_p95": [float(np.percentile(I, x) / QREF_M) for x in (5, 50, 95)],
             "absI_C_p95": float(np.percentile(np.abs(I), 95) / QREF_M),
             "steps_ge_0p3C": int((dI >= STEP_C * QREF_M).sum()),
             "dead_1idx": [d + 1 for d in dead], "stuck_reported_1idx": [d + 1 for d in stuck],
             "thermistor_resolution_K": float(q[q > 0].min()) if (q > 0).any() else None,
             "T_range_C": [float(np.nanmin(Tl)), float(np.nanmax(Tl))],
             "T_median_start_end_C": [float(Tm[0]), float(Tm[-1])],
             "spread_hot_minus_median_p50_p95_max_K": [float(np.percentile(sp, 50)), float(np.percentile(sp, 95)),
                                                       float(sp.max())],
             "spread_hot_minus_min_p50_p95_max_K": [float(np.percentile((Th - Tl.min(1))[fin], x)) for x in
                                                    (50, 95, 100)],
             "frac_spread_ge_2K": float((sp >= 2).mean()), "frac_spread_ge_3K": float((sp >= 3).mean()),
             "frac_spread_ge_4K": float((sp >= 4).mean()),
             "hottest_cell_mode_1idx": int(np.array(live)[np.bincount(hot).argmax()] + 1),
             "hottest_cell_mode_frac": float(np.bincount(hot).max() / len(hot)),
             "noise": quiet_noise(Tl, I), "probe": {}}
        for lay, ev in PROBE_EVERY.items():
            for off in ((0, 1) if lay == "1per3" else (0,)):
                pr, moved = probes(set(live), ev, off)
                pi = [live.index(c) for c in pr]
                seen = Tl[:, pi].max(1) >= Th                    # the probe max equals T_hot (ties count as seen)
                strict = np.isin(np.array(live)[hot], pr)        # argmax (first index) is a probe cell
                unobs = [c for c in live if c not in pr]
                dist = [min(abs(c - x) for x in pr) for c in unobs]
                gap = Th - Tl[:, pi].max(1)
                r["probe"][f"{lay}_off{off}"] = {
                    "n_probes": len(pr), "probes_1idx": [c + 1 for c in pr], "moved_1idx": moved,
                    "mean_dist_unobserved_to_probe_cells": float(np.mean(dist)) if dist else 0.0,
                    "frac_hottest_value_seen_by_a_probe": float(seen[fin].mean()),
                    "frac_hottest_argmax_is_probe": float(strict[fin].mean()),
                    "gap_Thot_minus_probe_max_p50_p95_p99_max_K": [float(np.percentile(gap[fin], x)) for x in
                                                                   (50, 95, 99, 100)]}
        # index adjacency: is cell c+1 thermally closer to c than a random cell? (layout of interpolation and M2)
        dev = Tl - Tm[:, None]
        mean_dev = dev[fin].mean(0)
        adj = [abs(mean_dev[i + 1] - mean_dev[i]) for i in range(len(live) - 1) if live[i + 1] == live[i] + 1]
        rng = np.random.default_rng(0)
        rnd = [abs(mean_dev[a] - mean_dev[b]) for a, b in rng.integers(0, len(live), (2000, 2)) if a != b]
        r["adjacency"] = {"mean_dev_by_cell_1idx": {int(c + 1): round(float(v), 2) for c, v in zip(live, mean_dev)},
                          "median_abs_meandev_adjacent_K": float(np.median(adj)),
                          "median_abs_meandev_random_pair_K": float(np.median(rnd))}
        runs.append(r)
        allT[name] = (Tl, live, fin)
    by = {r["run"]: r for r in runs}
    assert sorted(sum(FOLDS.values(), [])) == sorted(by), "fold lists must cover the 14 runs exactly"
    gate = {}
    for f, names in FOLDS.items():
        ok = [n for n in names if by[n]["frac_spread_ge_3K"] >= GATE_FRAC]
        frames = sum(by[n]["frames"] for n in names)
        gate[f] = {"runs": names, "runs_passing": ok, "n_pass": len(ok), "pass": len(ok) >= GATE_RUNS,
                   "frames": frames, "longest_run_share": max(by[n]["frames"] for n in names) / frames,
                   "chambers": sorted(by[n]["chamber_C"] for n in names),
                   "cooling": sorted(by[n]["cooling"] for n in names)}
    res = {"tag": "DERIVED from MEASURED (McMaster 72S, CC BY 4.0; surface thermistors)",
           "layout": "1-indexed cells 1, 4, 7, ... (1per3); dead probe -> next live cell up", "folds": FOLDS,
           "gate": {"rule": f">= {GATE_RUNS} runs per fold with (T_hot - T_median) >= {GATE_K} K for >= "
                            f"{int(GATE_FRAC * 100)} % of frames", "result": gate,
                    "pass": all(g["pass"] for g in gate.values())},
           "runs": runs}
    json.dump(res, open(f"{OUT}/profile.json", "w"), indent=1, default=float)
    for r in runs:
        p = r["probe"]["1per3_off0"]
        print(f"{r['run']:30s} {r['frames']:6d} {r['chamber_C']} {r['cooling']:16s} I_C {np.round(r['I_C_p5_p50_p95'], 2)}"
              f" steps {r['steps_ge_0p3C']:5d} dead {r['dead_1idx']} stuck {r['stuck_reported_1idx']} res "
              f"{r['thermistor_resolution_K']} spread {np.round(r['spread_hot_minus_median_p50_p95_max_K'], 1)} "
              f">=2/3/4K {r['frac_spread_ge_2K']:.2f}/{r['frac_spread_ge_3K']:.2f}/{r['frac_spread_ge_4K']:.2f} "
              f"seen {p['frac_hottest_value_seen_by_a_probe']:.2f} argmax {p['frac_hottest_argmax_is_probe']:.2f} "
              f"gap {np.round(p['gap_Thot_minus_probe_max_p50_p95_p99_max_K'], 1)} hotmode {r['hottest_cell_mode_1idx']}"
              f"({r['hottest_cell_mode_frac']:.2f}) adj/rnd {r['adjacency']['median_abs_meandev_adjacent_K']:.2f}/"
              f"{r['adjacency']['median_abs_meandev_random_pair_K']:.2f} noise {r['noise']}")
    print(json.dumps(res["gate"], indent=1, default=float))


if __name__ == "__main__":
    main()
