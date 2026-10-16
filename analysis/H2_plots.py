"""Experiment H2 plots: constraining-cell controls and pack-mean margin sweep (Weihai LFP BESS), with H (Changan)
alongside for comparison. Reads results/H2/replay.json and results/H/replay.json.
Usage: python analysis/H2_plots.py
"""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

R = json.load(open("results/H2/replay.json"))
H = json.load(open("results/H/replay.json"))
LIC = ("Weihai 9×396-cell LFP BESS (Zenodo 20094787, CC BY 4.0) · DERIVED, limits ASSUMED · "
       "H column: Changan 300 EVs (CC BY-NC-SA)")

fig, ax = plt.subplots(figsize=(8, 3.8))
lab = ["max-V cell\nnot constraining", "min-V cell\nnot constraining", "no extreme-T probe\ncell constraining",
       "per-cell limit\n≠ min/max limit", "median session\ntime saved"]
h2 = [R["tieaware_frac_vmax_cell_not_constraining"], R["tieaware_frac_vmin_cell_not_constraining"],
      R["tieaware_frac_no_extreme_T_probe_cell_constraining"], R["frac_frames_cell_ne_mm"], R["S_mm_M1_median"]]
h1 = [H["tieaware_frac_vmax_cell_not_constraining"], H["tieaware_frac_vmin_cell_not_constraining"],
      H["tieaware_frac_no_extreme_T_probe_cell_constraining"], H["frac_frames_cell_gt_mm"], H["S_mm_M1_median"]]
x = np.arange(len(lab))
b1 = ax.bar(x - 0.2, np.array(h1) * 100, 0.4, label="H: Changan NMC EVs, 96 cells", color="#8c8c8c")
b2 = ax.bar(x + 0.2, np.array(h2) * 100, 0.4, label="H2: Weihai LFP BESS, 396 cells/rack", color="#c44e52")
ax.bar_label(b1, fmt="%.2f%%", fontsize=7); ax.bar_label(b2, fmt="%.2f%%", fontsize=7)
ax.set_xticks(x); ax.set_xticklabels(lab, fontsize=8); ax.set_ylabel("% of charging frames (last: % time)")
ax.set_title("Per-cell vs min/max charge limiting: H and H2 (M1 mapping)", fontsize=10); ax.legend(fontsize=8)
fig.text(0.01, 0.01, LIC, fontsize=6, color="gray")
fig.tight_layout(rect=(0, 0.04, 1, 1))
fig.savefig("results/H2/h2_constraining.png", dpi=150)

M = sorted({int(k.split("_")[0]) for k in R["margin_sweep"]})
MT = sorted({int(k.split("_")[1]) for k in R["margin_sweep"]})
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 3.8))
for mt in MT:
    a1.plot(M, [R["margin_sweep"][f"{m}_{mt}"]["S_pack_median"] * 100 for m in M], "o-", label=f"temp margin {mt} °C")
    a2.semilogy(M, [max(R["margin_sweep"][f"{m}_{mt}"]["unsafe_frac"] * 100, 1e-4) for m in M], "o-",
                label=f"temp margin {mt} °C")
a1.axhline(R["S_mm_M1_median"] * 100, color="k", ls="--", lw=1, label="per-cell vs min/max")
a1.set_xlabel("pack-mean voltage margin m (mV)"); a1.set_ylabel("median session time saved by per-cell (%)")
a1.set_title("Per-cell vs pack-mean limiter, by assumed margin", fontsize=9); a1.legend(fontsize=7)
a2.axhline(0.1, color="r", ls=":", lw=1, label="0.1 % safe threshold")
a2.set_xlabel("pack-mean voltage margin m (mV)"); a2.set_ylabel("frames where pack-mean exceeds per-cell (%)")
a2.set_title("Unsafe fraction of a pack-mean limiter", fontsize=9); a2.legend(fontsize=7)
fig.text(0.01, 0.01, LIC, fontsize=6, color="gray")
fig.tight_layout(rect=(0, 0.04, 1, 1))
fig.savefig("results/H2/h2_margin.png", dpi=150)
print("ok")
