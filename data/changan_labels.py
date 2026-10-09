"""Derive capacity labels for the Changan 300-EV field data, following the paper's Methods as closely as the
public data allows (Liu et al., Nat Commun 16:1137, 2025; Methods "EV data processing"):

  t_s : wake-up after a rest >= REST_S (time gap between consecutive frames). SOC_s from the max-cell voltage
        at wake via an OCV->SOC table.  [the paper's OEM table is NOT public — see OCV below]
        Skip if SOC_s > SOC_S_MAX (the paper uses 0.6) so the segment spans a wide SOC interval.
  t_e : end of a charging session whose max cell reached VMAX_FULL (true full: the paper's 4.25 V cutoff).
        Taken as SOC_e = 100 %. The BMS's own SOC is NOT used here — it reads ~97 % at true full (stale).
  capacity = net charge into the pack over [t_s, t_e] / (1 - SOC_s)        (ampere-hour integral, Ah)

OCV (ASSUMED, the main caveat): with no public OCV table, we build one per fleet from EARLY-LIFE rests —
(max-cell voltage at wake, BMS SOC at wake) over each vehicle's first EARLY_KM of odometer — on the premise
that a new pack's BMS capacity estimate is still accurate. Every label is therefore DERIVED and inherits that
assumption. Labels are gated in profile (fleet trend vs the paper's published SOH-vs-mileage curve,
independence from charge current, within-vehicle noise floor).

Model input per label (CHOSEN): the CHARGE_LEN charging frames that end at t_e, as [N, 128, 8] with the same
8 columns as EVBattery (avg cell V, I, SOC, max V, min V, max T, min T, t) so model/common.py applies as is.

Usage: python data/changan_labels.py ocv  data/changan/slim data/changan/ocv.json
       python data/changan_labels.py label data/changan/slim data/changan/ocv.json data/changan/labels [--jobs 16]
"""
import argparse
import json
import os
import re
from multiprocessing import Pool

import numpy as np

REST_S = 3600          # paper: rest = gap > 1 h
SOC_S_MAX = 60.0       # paper: skip if calibrated SOC_s > 0.6
VMAX_FULL = 4.20       # paper: charging cuts off at max cell 4.25 V; allow a little slack
EARLY_KM = 20_000      # CHOSEN: "early life" window for the OCV table
SESSION_MERGE_S = 600  # CHOSEN: charging runs < 10 min apart are one session
MAX_SEG_S = 3 * 86400  # CHOSEN: a t_s->t_e window longer than 3 days is rejected
MAX_GAP_ACTIVE_S = 60  # CHOSEN: reject a segment with a data gap > 60 s while current is flowing
CHARGE_LEN = 128       # CHOSEN: frames per model input (= EVBattery snippet length)
N_CELLS = 96           # IMPOSED: series cells per pack (96 voltages per frame in the raw CSV)


def load(p):
    d = np.load(p)
    return {k: d[k] for k in d.files}


def wakes(d):
    """Indices of the first frame after each rest gap."""
    return np.flatnonzero(np.diff(d["t"]) > REST_S) + 1


def ocv_table(slim_dir, out):
    vm, sc = [], []
    for f in sorted(os.listdir(slim_dir)):
        d = load(os.path.join(slim_dir, f))
        w = wakes(d)
        early = d["odo"][w] <= d["odo"].min() + EARLY_KM
        ok = early & (d["soc"][w] > 0) & (d["vmax"][w] > 3.0)
        vm.append(d["vmax"][w][ok]); sc.append(d["soc"][w][ok])
    vm, sc = np.concatenate(vm), np.concatenate(sc)
    edges = np.arange(3.40, 4.26, 0.01)
    centers, med, n = [], [], []
    for lo, hi in zip(edges[:-1], edges[1:]):
        k = (vm >= lo) & (vm < hi)
        if k.sum() >= 20:
            centers.append(round((lo + hi) / 2, 3)); med.append(float(np.median(sc[k]))); n.append(int(k.sum()))
    med = np.maximum.accumulate(np.array(med))  # OCV->SOC must be monotone non-decreasing
    json.dump({"vmax_v": centers, "soc_pct": med.tolist(), "n": n, "n_rests": int(len(vm)),
               "early_km": EARLY_KM, "tag": "ASSUMED (built from early-life BMS SOC at wake)"}, open(out, "w"), indent=1)
    print(f"OCV table: {len(centers)} bins from {len(vm)} early-life rests -> {out}")


def label_vehicle(args):
    path, ocv, out_dir = args
    vin = int(re.findall(r"\d+", os.path.basename(path))[0])
    d = load(path)
    t, I, soc, st, vmax, odo = d["t"], d["I"].astype(np.float64), d["soc"], d["status"], d["vmax"], d["odo"]
    ov, os_ = np.array(ocv["vmax_v"]), np.array(ocv["soc_pct"])
    # full-charge ends: the last frame of a charging SESSION whose max cell reached VMAX_FULL. Sessions merge
    # status-1 runs separated by < SESSION_MERGE_S (status flickers mid-charge). NOT "BMS SOC == 100": measured
    # on all 85 vehicles, cells reach ~4.2 V while the BMS still reports a median 97 % (its capacity estimate is
    # stale — the paper's own finding), so SOC==100 almost never fires (vin3: 7 frames in 1,328 days).
    chg = st == 1
    ci = np.flatnonzero(chg)
    if not len(ci):
        return f"vin{vin}: 0 labels (never charges)"
    brk = np.flatnonzero(np.diff(t[ci]) > SESSION_MERGE_S)
    s_start, s_end = np.r_[ci[0], ci[brk + 1]], np.r_[ci[brk], ci[-1]]
    ends = np.array([e for a0, e in zip(s_start, s_end) if vmax[a0:e + 1][chg[a0:e + 1]].max() >= VMAX_FULL], int)
    w = wakes(d)
    rows, X = [], []
    for e in ends:
        cand = w[w < e]
        if not len(cand):
            continue
        s = cand[-1]  # most recent wake before this full charge
        if t[e] - t[s] > MAX_SEG_S or vmax[s] < ov[0] or vmax[s] > ov[-1]:
            continue
        soc_s = float(np.interp(vmax[s], ov, os_))
        if soc_s > SOC_S_MAX:
            continue
        seg = slice(s, e + 1)
        dt = np.diff(t[seg])
        ii = I[seg]
        active = (np.abs(ii[1:]) > 1) | (np.abs(ii[:-1]) > 1)
        if np.any((dt > MAX_GAP_ACTIVE_S) & active):
            continue
        ah = -np.sum(0.5 * (ii[1:] + ii[:-1]) * dt) / 3600.0  # charge positive
        cap = ah / (1 - soc_s / 100.0)
        # model input: CHARGE_LEN charging frames ending at e
        k = np.flatnonzero(chg[:e + 1])[-CHARGE_LEN:]
        if len(k) < CHARGE_LEN or t[k[-1]] - t[k[0]] > CHARGE_LEN * 10 * 3:
            continue
        x = np.stack([d["V"][k] / N_CELLS, d["I"][k], soc[k], vmax[k], d["vmin"][k], d["tmax"][k], d["tmin"][k],
                      (t[k] - t[k[0]])], axis=1).astype(np.float32)
        rows.append((vin, odo[e], t[e], cap, soc_s, ah, float(np.median(-I[k])), t[e] - t[s]))
        X.append(x)
    if not rows:
        return f"vin{vin}: 0 labels"
    R = np.array(rows)
    np.savez(os.path.join(out_dir, f"vin{vin}.npz"), X=np.stack(X), car=R[:, 0].astype(np.int32),
             mileage=R[:, 1].astype(np.float32), t_end=R[:, 2], capacity=R[:, 3].astype(np.float32),
             soc_s=R[:, 4].astype(np.float32), ah=R[:, 5].astype(np.float32),
             charge_current=R[:, 6].astype(np.float32), seg_s=R[:, 7].astype(np.float32))
    return f"vin{vin}: {len(R)} labels, cap median {np.median(R[:, 3]):.1f} Ah"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["ocv", "label"])
    ap.add_argument("slim")
    ap.add_argument("ocv")
    ap.add_argument("out", nargs="?")
    ap.add_argument("--jobs", type=int, default=16)
    a = ap.parse_args()
    if a.mode == "ocv":
        return ocv_table(a.slim, a.ocv)
    os.makedirs(a.out, exist_ok=True)
    ocv = json.load(open(a.ocv))
    files = sorted((os.path.join(a.slim, f) for f in os.listdir(a.slim) if f.endswith(".npz")),
                   key=lambda p: int(re.findall(r"\d+", os.path.basename(p))[0]))
    with Pool(a.jobs) as p:
        for line in p.imap_unordered(label_vehicle, [(f, ocv, a.out) for f in files]):
            print(line, flush=True)


if __name__ == "__main__":
    main()
