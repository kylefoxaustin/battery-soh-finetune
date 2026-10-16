"""Experiment G.2 plots: ROC of per-cell (A) vs min/max (B) flagging, early and late windows; AUCs of all features
and negative controls. Reads results/G2/features.csv and results/G2/g2.json.
Usage: python analysis/G2_plots.py
"""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

df = pd.read_csv("results/G2/features.csv")
R = json.load(open("results/G2/g2.json"))
q = df[(df.maker == "QAS") & df.eligible_E]
LIC = ("Beihang QAS (Cao et al. Nat Commun 2025, zenodo 10656500, CC BY 4.0): 58 teardown-labelled faulty / 335 "
       "normal EVs, 110 cells · DERIVED")


def roc(pos, neg):
    t = np.unique(np.r_[pos, neg])[::-1]
    return np.r_[0, [(neg >= x).mean() for x in t]], np.r_[0, [(pos >= x).mean() for x in t]]


fig, axs = plt.subplots(1, 2, figsize=(10, 4.2))
for ax, w, title in [(axs[0], "E", "Early window (first half of record)"), (axs[1], "L", "Late window (second half)")]:
    key = "early" if w == "E" else "late"
    for f, lab, c in [("A", "per-cell drift (A)", "#c44e52"), ("B", "min/max drift (B)", "#4c72b0")]:
        x, y = roc(q[q.label == 1][f"{w}_{f}"].to_numpy(), q[q.label == 0][f"{w}_{f}"].to_numpy())
        a = R[key][f"{w}_{f}"]
        ax.plot(x, y, color=c, label=f"{lab}: AUC {a['auc']:.2f} [{a['ci'][0]:.2f}, {a['ci'][1]:.2f}]")
    ax.plot([0, 1], [0, 1], "k:", lw=1)
    d = R[key]["A_minus_B"]
    ax.set_title(f"{title}\nA − B = {d['diff']:+.2f} [{d['ci'][0]:+.2f}, {d['ci'][1]:+.2f}]", fontsize=9)
    ax.set_xlabel("false-positive rate (normal vehicles)"); ax.set_ylabel("true-positive rate (faulty vehicles)")
    ax.legend(fontsize=7, loc="lower right")
fig.text(0.01, 0.01, LIC, fontsize=6, color="gray")
fig.tight_layout(rect=(0, 0.04, 1, 1))
fig.savefig("results/G2/g2_roc.png", dpi=150)

fig, ax = plt.subplots(figsize=(8, 3.8))
names = ["E_A", "E_A_lvl", "E_B", "E_B_lvl", "E_B_spr", "E_C1_temp", "E_C2_soc", "E_C3_nvalid", "E_C4_restfrac",
         "E_C5_absI"]
labels = ["A drift\n(per-cell)", "A level\n(per-cell)", "B drift\n(min/max)", "B level\n(min/max)",
          "B spread\n(min/max)", "C1 temp", "C2 SOC", "C3 length", "C4 rest\nfraction", "C5 |I|"]
cols = ["#c44e52"] * 2 + ["#4c72b0"] * 3 + ["#8c8c8c"] * 5
for i, n in enumerate(names):
    a = R["early"][n]
    ax.errorbar(i, a["auc"], yerr=[[a["auc"] - a["ci"][0]], [a["ci"][1] - a["auc"]]], fmt="o", color=cols[i], capsize=3)
ax.axhline(0.5, color="k", lw=1, ls=":")
ax.axhspan(0.35, 0.65, color="gray", alpha=0.08, label="control band [0.35, 0.65]")
ax.set_xticks(range(len(names))); ax.set_xticklabels(labels, fontsize=7)
ax.set_ylabel("AUC, faulty vs normal (95 % CI)"); ax.legend(fontsize=7)
ax.set_title("Early-window features and negative controls (QAS)", fontsize=9)
fig.text(0.01, 0.01, LIC, fontsize=6, color="gray")
fig.tight_layout(rect=(0, 0.04, 1, 1))
fig.savefig("results/G2/g2_auc.png", dpi=150)
print("ok")
