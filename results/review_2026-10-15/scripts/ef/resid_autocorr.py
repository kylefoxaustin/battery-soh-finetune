"""Review: is the within-unit FLEET RESIDUAL (the E pre-check target) slowly varying (so a 5 k km-window feature could
explain it) or session-to-session noise (so no pre-session feature can)?  Uses the repo's frozen fold models exactly
as analysis/E_power.py does. Also: slow- vs fast-charge label offset within unit (labels_full), for the F label-rise.
Run from repo root: CUDA_VISIBLE_DEVICES= python resid_autocorr.py
"""
import os
import sys

import numpy as np

sys.path.insert(0, "analysis")
import torch  # noqa: E402

torch.set_num_threads(4)
from E_power import residuals  # noqa: E402

for ls in ["primary", "strict"]:
    units = []
    for k in range(4):
        units += residuals(f"runs/chf_{ls}_k{k}")
    within = []
    pairs = {300: [], 1000: [], 3000: []}
    lag1 = []
    for u in units:
        r = u["y"] - u["p"]
        rc = r - r.mean()
        within.append(rc)
        km = u["km"]
        for a, b in zip(range(len(r) - 1), range(1, len(r))):
            dk = km[b] - km[a]
            for DK in pairs:
                if dk <= DK:
                    pairs[DK].append(r[b] - r[a])
        if len(r) >= 12:
            lag1.append(np.corrcoef(rc[:-1], rc[1:])[0, 1])
    w = np.concatenate(within)
    print(f"{ls}: within-unit residual SD {w.std():.2f} Ah (n={len(w)})")
    for DK, d in pairs.items():
        d = np.array(d)
        print(f"  consecutive-label pairs <= {DK} km apart: n={len(d)}, SD(diff)/sqrt2 = {d.std() / np.sqrt(2):.2f} Ah "
              f"-> share of within-unit variance that is NOT pair-to-pair noise: {max(0, 1 - (d.var() / 2) / w.var()):.2f}")
    print(f"  median lag-1 autocorrelation of within-unit residual: {np.median(lag1):+.3f} (units {len(lag1)})")
    # slowly varying share via 5-label running mean: var of running mean vs var of residual
    rm = []
    for rc in within:
        if len(rc) >= 15:
            m = np.convolve(rc, np.ones(5) / 5, mode="valid")
            rm.append(m.var() - rc.var() / 5)  # excess variance of running mean over pure-noise expectation
    print(f"  excess variance of 5-label running mean over white-noise expectation, median over units: {np.median(rm):+.2f} Ah^2 "
          f"(within var {w.var():.1f} Ah^2)")

# slow vs fast charge offset within unit
lab_dir = "data/changan/labels_full"
off = []
for f in sorted(os.listdir(lab_dir)):
    L = np.load(os.path.join(lab_dir, f))
    I, cap, km = L["charge_current"].astype(float), L["capacity"].astype(float), L["mileage"].astype(float)
    ok = (cap >= 95) & (cap <= 145)
    fast, slow = ok & (I >= 40), ok & (I < 25)
    if fast.sum() >= 5 and slow.sum() >= 5:
        b = np.polyfit(km[fast], cap[fast], 1)  # fast-charge trend, evaluated at slow-charge km
        off.append(float(np.median(cap[slow] - np.polyval(b, km[slow]))))
off = np.array(off)
print(f"\nslow-charge (<25 A) label minus the unit's fast-charge (>=40 A) trend: median {np.median(off):+.2f} Ah, "
      f"IQR {np.percentile(off, 25):+.2f}..{np.percentile(off, 75):+.2f}, units {len(off)}")
