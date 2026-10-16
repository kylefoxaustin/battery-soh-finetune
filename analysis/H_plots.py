"""Experiment H plots: constraining-cell identity vs scalar extremes, benefit vs assumed margin, latency and
resident state vs cell count. Reads results/H/replay.json and results/H/footprint.json.
Usage: python analysis/H_plots.py
"""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

R = json.load(open("results/H/replay.json"))
F = json.load(open("results/H/footprint.json"))
LIC = "Changan 300-EV, NMC, 96S/32 probes · CC BY-NC-SA 4.0 (non-commercial) · DERIVED, limits ASSUMED"

# 1. constraining-cell identity
fig, ax = plt.subplots(figsize=(7.5, 3.6))
lab = ["max-V cell\nnot constraining", "min-V cell\nnot constraining", "no cell on an\nextreme-T probe\nconstraining",
       "per-cell limit\n≠ min/max limit"]
val = [R["tieaware_frac_vmax_cell_not_constraining"], R["tieaware_frac_vmin_cell_not_constraining"],
       R["tieaware_frac_no_extreme_T_probe_cell_constraining"], R["frac_frames_cell_gt_mm"]]
b = ax.bar(lab, np.array(val) * 100, color=["#4c72b0", "#8c8c8c", "#dd8452", "#c44e52"])
ax.bar_label(b, fmt="%.2f%%", fontsize=8)
ax.set_ylabel("% of charging frames")
ax.set_title(f"Which cell constrains a per-cell limiter? ({R['n_frames']/1e6:.1f} M frames, M1 mapping)", fontsize=10)
fig.text(0.01, 0.01, LIC, fontsize=6, color="gray")
fig.tight_layout(rect=(0, 0.04, 1, 1))
fig.savefig("results/H/h_constraining.png", dpi=150)

# 2. benefit vs assumed margin
M = sorted({int(k.split("_")[0]) for k in R["margin_sweep"]})
MT = sorted({int(k.split("_")[1]) for k in R["margin_sweep"]})
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 3.8))
for mt in MT:
    s = [R["margin_sweep"][f"{m}_{mt}"]["S_pack_median"] * 100 for m in M]
    u = [max(R["margin_sweep"][f"{m}_{mt}"]["unsafe_frac"] * 100, 1e-4) for m in M]
    a1.plot(M, s, "o-", label=f"temp margin {mt} °C")
    a2.semilogy(M, u, "o-", label=f"temp margin {mt} °C")
a1.axhline(R["S_mm_M1_median"] * 100, color="k", ls="--", lw=1, label="per-cell vs min/max")
a1.set_xlabel("pack-scalar voltage margin m (mV)"); a1.set_ylabel("median session time saved by per-cell (%)")
a1.set_title("Benefit of per-cell over pack-scalar vs assumed margin", fontsize=9); a1.legend(fontsize=7)
a2.axhline(0.1, color="r", ls=":", lw=1, label="0.1 % safe threshold")
a2.set_xlabel("pack-scalar voltage margin m (mV)"); a2.set_ylabel("frames where pack-scalar exceeds per-cell limit (%)")
a2.set_title("Unsafe fraction of a pack-scalar limiter (floor 1e-4 %)", fontsize=9); a2.legend(fontsize=7)
fig.text(0.01, 0.01, LIC, fontsize=6, color="gray")
fig.tight_layout(rect=(0, 0.04, 1, 1))
fig.savefig("results/H/h_margin.png", dpi=150)

# 3. latency + resident state vs cell count
N = sorted(int(k) for k in F["per_N"])
P = F["per_N"]
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 3.8))
a1.plot(N, [P[str(n)]["lat_ns_p50_median"] / 1e3 for n in N], "o-", label="p50")
a1.plot(N, [P[str(n)]["lat_ns_p99_median"] / 1e3 for n in N], "s-", label="p99")
a1.plot(N, [P[str(n)]["ns_per_update_sustained"] / 1e3 for n in N], "^--", label="sustained (1/rate)")
a1.set_xlabel("cells per pack"); a1.set_ylabel("µs per limiter update"); a1.legend(fontsize=8)
a1.set_title("Per-cell limiter update cost, one A55 core @1.8 GHz", fontsize=9)
a2.plot(N, [P[str(n)]["state_bytes"] / 1024 for n in N], "o-", label="per-cell state (10 B/cell)")
a2.plot(N, [(P[str(n)]["state_bytes"] + P[str(n)]["lut_bytes"]) / 1024 for n in N], "s-", label="state + shared LUTs")
a2.axhline(225544 / 1024, color="gray", ls="--", lw=1, label="E1 SoH model (220 KB)")
a2.set_xlabel("cells per pack"); a2.set_ylabel("KiB resident"); a2.legend(fontsize=8)
a2.set_title("Resident limiter state vs cell count", fontsize=9)
fig.text(0.01, 0.01, "MEASURED on NXP FRDM-IMX95-PRO, gated (20/20 runs bit-match the reference). "
         "Frames: Changan held-out vehicles (CC BY-NC-SA); N>96 tiles real frames (geometry ASSUMED).",
         fontsize=6, color="gray")
fig.tight_layout(rect=(0, 0.04, 1, 1))
fig.savefig("results/H/h_scaling.png", dpi=150)
print("ok")
