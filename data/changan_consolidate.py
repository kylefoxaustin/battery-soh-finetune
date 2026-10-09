"""Consolidate per-vehicle Changan labels (data/changan_labels.py output) into one .npz in the layout
model/train_fleet.py expects (X [N,128,8], car, mileage, capacity), under a NAMED label filter.

Filters (CHOSEN, declared before any model was trained on them):
  primary : fast-charge labels, end-of-charge current 48–51 A        (consistent charger = consistent label)
  strict  : primary + OCV start SOC 15–50 % + wake->full < 6 h + mean charge temperature 15–35 °C
  both    : plausibility band CAP_LO..CAP_HI Ah (≈ ±18 % of the fleet median label, 122 Ah). Measured before any
            model: per-vehicle medians span 116–132 Ah (p5–p95); 2.8 % of labels exceed 145 Ah — two whole
            vehicles (vin32 median 143, vin67 median 153) and 32 isolated spikes in otherwise normal vehicles.
Usage: python data/changan_consolidate.py data/changan/labels data/processed/changan_primary.npz --filter primary
"""
import argparse
import glob
import os

import numpy as np

CAP_LO, CAP_HI = 95.0, 145.0  # CHOSEN plausibility band (Ah), fixed before training


def mask(d, name):
    iend = -d["X"][:, -1, 1]
    m = (iend >= 48) & (iend <= 51) & np.isfinite(d["mileage"]) & np.isfinite(d["capacity"])
    m &= (d["capacity"] >= CAP_LO) & (d["capacity"] <= CAP_HI)
    if name == "strict":
        tmean = d["X"][:, :, 5].mean(1)
        m &= (d["soc_s"] >= 15) & (d["soc_s"] <= 50) & (d["seg_s"] < 6 * 3600) & (tmean >= 15) & (tmean <= 35)
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("labels")
    ap.add_argument("out")
    ap.add_argument("--filter", choices=["primary", "strict"], default="primary")
    a = ap.parse_args()
    parts = {k: [] for k in ("X", "car", "mileage", "capacity")}
    for f in sorted(glob.glob(os.path.join(a.labels, "vin*.npz"))):
        d = np.load(f)
        m = mask(d, a.filter)
        for k in parts:
            parts[k].append(d[k][m])
    out = {k: np.concatenate(v) for k, v in parts.items()}
    np.savez(a.out, **out)
    cars, n = np.unique(out["car"], return_counts=True)
    print(f"{a.filter}: {len(out['capacity'])} labels, {len(cars)} vehicles, labels/vehicle median {int(np.median(n))} -> {a.out}")


if __name__ == "__main__":
    main()
