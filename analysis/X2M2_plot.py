"""X2-M2 first-class figure (prereg §2): median G and unsafe fraction vs kappa_mm, twin axes, one panel per map."""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

RUNS = [("x2_mcmaster", "x1 (X2-M, 1.5 C)"), ("x2_mcmaster_M2_qscale4", "x4 = 6 C (X2-M2 primary, SOURCED)"),
        ("x2_mcmaster_posthoc_qscale10", "x10 (POST-HOC)"), ("x2_mcmaster_M2_qscale16", "x16 = 125 A (sensitivity, SOURCED)")]
fig, axs = plt.subplots(1, 4, figsize=(16, 3.8), sharey=False)
for ax, (f, lab) in zip(axs, RUNS):
    d = json.load(open(f"results/X/X2/{f}.json"))
    k = [float(x) for x in d["unsafe_curve"]]
    u = [100 * v for v in d["unsafe_curve"].values()]
    g = [100 * v for v in d.get("G_median_curve", {x: 0.0 for x in d["unsafe_curve"]}).values()]
    ax.plot(k, g, "C0-o", ms=3, label="median G (%)")
    ax.axhline(0, color="0.6", lw=0.6)
    ax.set_xlabel("kappa_mm (min/max R margin)")
    ax.set_title(lab, fontsize=9)
    ax2 = ax.twinx()
    ax2.plot(k, u, "C3-s", ms=3, label="unsafe frames (%)")
    ax2.axhline(0.1, color="C3", ls=":", lw=0.8)
    ax.axvline(d["kappa_mm"], color="k", ls="--", lw=0.8)
    if ax is axs[0]:
        ax.set_ylabel("median G over 14 runs (%)", color="C0")
    if ax is axs[-1]:
        ax2.set_ylabel("min/max unsafe frames (%)", color="C3")
fig.suptitle("X2-M2 (McMaster 72S, DERIVED; maps ASSUMED/SOURCED): dashed = calibrated kappa (unsafe <= 0.1 %, dotted)",
             fontsize=10)
fig.tight_layout()
fig.savefig("results/X/X2M2/x2m2_kappa_curves.png", dpi=110)
