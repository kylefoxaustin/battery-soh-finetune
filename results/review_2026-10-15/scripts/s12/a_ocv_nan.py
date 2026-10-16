"""A: does NaN odometer silently exclude vehicles from the OCV table? Replicate ocv_table's selection logic."""
import glob, json, sys
import numpy as np

REST_S, EARLY_KM = 3600, 20_000
slim = sorted(glob.glob("<repo>/data/changan/slim/*.npz"))
n_nan_veh, contrib, contrib_fixed, frac_nan = 0, [], [], []
start_odo = []
for i, f in enumerate(slim):
    if i % 25 == 0: print("progress", i, flush=True)
    d = np.load(f, mmap_mode="r")
    odo, t, soc, vmax = d["odo"], d["t"], d["soc"], d["vmax"]
    w = np.flatnonzero(np.diff(t) > REST_S) + 1
    has_nan = np.isnan(odo).any()
    n_nan_veh += has_nan
    frac_nan.append(np.isnan(odo).mean())
    early = odo[w] <= odo.min() + EARLY_KM                      # as written (NaN-poisoned)
    ok = early & (soc[w] > 0) & (vmax[w] > 3.0)
    contrib.append(int(ok.sum()))
    early2 = odo[w] <= np.nanmin(odo) + EARLY_KM                # intended
    ok2 = early2 & (soc[w] > 0) & (vmax[w] > 3.0)
    contrib_fixed.append(int(ok2.sum()))
    start_odo.append(float(np.nanmin(odo)))
contrib, contrib_fixed, start_odo = map(np.array, (contrib, contrib_fixed, start_odo))
print(f"vehicles: {len(slim)}; with any NaN odometer: {n_nan_veh}; median frac NaN frames among them: {np.median([x for x in frac_nan if x>0]):.4f}")
print(f"OCV-table contributors as written: {(contrib>0).sum()} vehicles, {contrib.sum()} rests  (ocv_full.json says 62,877)")
print(f"OCV-table contributors with nanmin: {(contrib_fixed>0).sum()} vehicles, {contrib_fixed.sum()} rests")
print(f"odometer at record start (nanmin): p5/25/50/75/95 = {np.percentile(start_odo,[5,25,50,75,95]).round(0)}; >20k km: {(start_odo>20000).sum()} vehicles")
