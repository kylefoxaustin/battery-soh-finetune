"""Review scan over all 300 Changan vehicles (read-only). Per vehicle:
 (a) tautology check: on the SAME rest synced full-vector frames, daily mean of per-frame min(dv) vs min over cells
     of the daily mean dv  -> is every per-cell event-day (min_k mean_d dv_k < -60) also a min-only event-day?
 (b) silent relative drift: per cell, baseline = median of first 60 valid days; flag runs >= 3 valid days with
     (daily - baseline) < -30 mV; on those days, is the cell the daily argmin? would a min-only monitor
     (daily min over cells, relative to ITS OWN first-60-day baseline) have moved by < -30 mV too?
 (c) weakest-cell identity: modal imin over rest frames; mean rest dv weakest cell; hottest probe modal index.
 (d) per-cell relative resistance from driving frames: slope of dv_k on I (mOhm) over all driving full vectors;
     max |z| cell.
Usage: python -I fleet_scan.py <cells_dir> <out_json> [--jobs 8]
"""
import argparse
import json
import os
import sys
from multiprocessing import Pool

import numpy as np

REST_A, MIN_REST, EV_MV, BASE_D, DRIFT_MV, RUN_N = 1.0, 20, -60.0, 60, -30.0, 3


def one(args):
    cells_dir, car = args
    try:
        C = np.load(f"{cells_dir}/vin{car}.npz")
        t, I, tf = C["t"], C["I"], C["t_full"]
        j = np.clip(np.searchsorted(t, tf), 0, len(t) - 1)
        match = t[j] == tf
        rest = match & (np.abs(I[j]) < REST_A)
        drv = match & (np.abs(I[j]) >= 10.0)
        dv = C["dv_full"]
        dvr = dv[rest].astype(np.float32)
        day_r = (tf[rest] // 86400).astype(np.int64)
        ud, inv, cnt = np.unique(day_r, return_inverse=True, return_counts=True)
        M = np.zeros((len(ud), 96))
        np.add.at(M, inv, dvr)
        M /= cnt[:, None]
        okd = cnt >= MIN_REST
        days, D = ud[okd], M[okd]
        out = {"car": car, "n_valid_days": int(len(days))}
        # (a) tautology on identical frames
        fmin = dvr.min(1)
        dmin_mean = (np.bincount(inv, fmin) / cnt)[okd]          # daily mean of per-frame min
        min_dmean = D.min(1)                                        # min over cells of daily mean
        pc_ev = min_dmean < EV_MV
        mo_ev = dmin_mean < EV_MV
        out["a"] = {"pc_days": int(pc_ev.sum()), "mo_days_same_frames": int(mo_ev.sum()),
                    "pc_and_mo": int((pc_ev & mo_ev).sum()),
                    "ineq_violations": int((dmin_mean > min_dmean + 1e-6).sum())}
        # (b) silent relative drift
        res_b = {"n_cells_flagged": 0, "n_flag_days": 0, "flag_days_cell_is_argmin": 0,
                 "flag_days_minonly_also_drifted": 0, "cells": []}
        if len(days) >= BASE_D + 30:
            base = np.median(D[:BASE_D], 0)
            drift = D - base
            argmin = D.argmin(1)
            mo_series = D.min(1)
            mo_drift = mo_series - np.median(mo_series[:BASE_D])
            for k in range(96):
                fl = np.flatnonzero(drift[BASE_D:, k] < DRIFT_MV) + BASE_D
                if len(fl) < RUN_N:
                    continue
                cut = np.flatnonzero(np.diff(fl) > 14) + 1
                runs = [r for r in np.split(fl, cut) if len(r) >= RUN_N]
                if not runs:
                    continue
                fd = np.concatenate(runs)
                res_b["n_cells_flagged"] += 1
                res_b["n_flag_days"] += int(len(fd))
                res_b["flag_days_cell_is_argmin"] += int((argmin[fd] == k).sum())
                res_b["flag_days_minonly_also_drifted"] += int((mo_drift[fd] < DRIFT_MV).sum())
                res_b["cells"].append({"cell": k, "n_days": int(len(fd)), "frac_argmin": float((argmin[fd] == k).mean()),
                                       "frac_mo_drift": float((mo_drift[fd] < DRIFT_MV).mean()),
                                       "min_drift": float(drift[fd, k].min()), "base": float(base[k]),
                                       "first_day": int(days[fd[0]])})
        out["b"] = res_b
        # (c) weakest cell identity
        r_all = np.abs(I) < REST_A
        im = C["imin"][r_all].astype(np.int64)
        out["c"] = {"modal_imin_rest": int(np.bincount(im, minlength=96).argmax()) if len(im) else None,
                    "imin_hist_rest": np.bincount(im, minlength=96).tolist(),
                    "weakest_mean_rest_dv": int(dvr.mean(0).argmin()) if len(dvr) else None,
                    "weakest_dev_mv": float(dvr.mean(0).min()) if len(dvr) else None,
                    "itmax_hist": np.bincount(C["itmax"].astype(np.int64), minlength=32).tolist(),
                    "cross_sd_mv": float(dvr.mean(0).std()) if len(dvr) else None}
        # (d) relative resistance
        if drv.sum() >= 500:
            Id = I[j[drv]].astype(np.float64)
            X = np.c_[np.ones(len(Id)), Id]
            beta, *_ = np.linalg.lstsq(X, dv[drv].astype(np.float64), rcond=None)
            sl = beta[1]  # mV/A = mOhm relative to pack mean cell
            mad = 1.4826 * np.median(np.abs(sl - np.median(sl))) + 1e-9
            z = (sl - np.median(sl)) / mad
            out["d"] = {"n_drv": int(drv.sum()), "dR_mohm": np.round(sl, 4).tolist(), "max_abs_z_cell": int(np.abs(z).argmax()),
                        "max_abs_z": float(np.abs(z).max()), "dR_sd_mohm": float(sl.std())}
        return out
    except Exception as e:  # noqa: BLE001
        return {"car": car, "error": repr(e)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cells_dir")
    ap.add_argument("out")
    ap.add_argument("--jobs", type=int, default=8)
    a = ap.parse_args()
    cars = sorted(int(f[3:-4]) for f in os.listdir(a.cells_dir) if f.startswith("vin") and f.endswith(".npz"))
    with Pool(a.jobs) as p:
        R = list(p.imap_unordered(one, [(a.cells_dir, c) for c in cars]))
    R.sort(key=lambda r: r["car"])
    json.dump(R, open(a.out, "w"))
    print("done", len(R), "errors", sum("error" in r for r in R), file=sys.stderr)


if __name__ == "__main__":
    main()
