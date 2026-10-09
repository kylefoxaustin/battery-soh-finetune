"""Merge K-fold results (each eligible unit is a target in exactly one fold) into one summary + the brief's
three plots. Every number written here traces to results/large/{e4,rolling}_<filter>_k*.json.

Robustness test: two-sided sign test on per-unit RMSE (method vs frozen; method vs persist_recent). A method
"helps robustly" in a band only if it beats frozen at the median AND on a majority of units AND both sign
tests reject at the BONFERRONI-corrected level ALPHA / (n_bands x n_FT_methods) — 5 horizon bands x 4
fine-tune methods = 20 tests per label filter. Added after a preliminary run showed one band at p = 0.022 out
of ~20 tested: that is what chance produces. Raw p-values are reported alongside.

Usage: python analysis/aggregate.py --out results/large [--prefix ""]   (reads e4_*/rolling_* in --out)
"""
import argparse
import glob
import json
import math
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

ALPHA = 0.05
FT_METHODS = ("bias", "last", "last_guard", "head_guard")
C_BLUE, C_ORANGE, C_AQUA, C_GRAY = "#2a78d6", "#eb6834", "#1baf7a", "#8a8984"
INK, INK2 = "#0b0b0b", "#52514e"


def sign_test(a, b):
    """Two-sided exact sign test that a < b more/less often than chance (ties dropped)."""
    d = np.asarray(a) - np.asarray(b)
    n_lt, n = int((d < 0).sum()), int((d != 0).sum())
    if n == 0:
        return 1.0
    k = min(n_lt, n - n_lt)
    p = sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n * 2
    return min(1.0, p)


def style(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(INK2)
    ax.tick_params(colors=INK2, labelsize=9)
    ax.grid(axis="y", color="#e4e3df", linewidth=0.8)
    ax.set_axisbelow(True)


def summarize_e4(files):
    rows = [r for f in files for r in json.load(open(f))["per_car"]]
    keys = list(rows[0]["rmse"])
    R = {k: np.array([r["rmse"][k] for r in rows]) for k in keys}
    out = {"n_units": len(rows), "conditions": {}}
    for k in keys:
        s = {"median": float(np.median(R[k])), "iqr": [float(np.percentile(R[k], 25)), float(np.percentile(R[k], 75))]}
        if k != "frozen":
            s["beats_frozen"] = int((R[k] < R["frozen"]).sum())
            s["sign_p_vs_frozen"] = sign_test(R[k], R["frozen"])
            s["median_pct_change_vs_frozen"] = float(np.median(100 * (R[k] / R["frozen"] - 1)))
        out["conditions"][k] = s
    return out, rows


def summarize_rolling(files):
    units = [u for f in files for u in json.load(open(f))["units"]]
    gates = [json.load(open(f))["gate"]["pass"] for f in files]
    bands = [tuple(b["band_km"]) for b in units[0]["bands"]]
    methods = None
    n_tests = sum(1 for b in units[0]["bands"]) * len(FT_METHODS)
    alpha_c = ALPHA / n_tests
    out = {"n_units_total": len(units), "all_gates_pass": all(gates), "bonferroni_alpha": alpha_c,
           "n_tests": n_tests, "bands": []}
    for bi, band in enumerate(bands):
        rows = [u["bands"][bi]["rmse"] for u in units if "rmse" in u["bands"][bi]]
        if not rows:
            out["bands"].append({"band_km": list(band), "n_units": 0}); continue
        methods = list(rows[0])
        R = {m: np.array([r[m] for r in rows]) for m in methods}
        b = {"band_km": list(band), "n_units": len(rows), "methods": {}}
        for m in methods:
            s = {"median": float(np.median(R[m])), "iqr": [float(np.percentile(R[m], 25)), float(np.percentile(R[m], 75))]}
            if m != "frozen":
                s["beats_frozen"] = int((R[m] < R["frozen"]).sum())
                s["sign_p_vs_frozen"] = sign_test(R[m], R["frozen"])
            if m not in ("persist_recent", "frozen") and "persist_recent" in R:
                s["beats_persist_recent"] = int((R[m] < R["persist_recent"]).sum())
                s["sign_p_vs_persist_recent"] = sign_test(R[m], R["persist_recent"])
            if m in FT_METHODS:
                s["helps_robustly"] = bool(s["median"] < b["methods"]["frozen"]["median"]
                                           and s["beats_frozen"] > len(rows) / 2 and s["sign_p_vs_frozen"] < alpha_c
                                           and s.get("beats_persist_recent", 0) > len(rows) / 2
                                           and s.get("sign_p_vs_persist_recent", 1) < alpha_c)
            b["methods"][m] = s
        out["bands"].append(b)
    return out, units


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="results/large")
    ap.add_argument("--filters", default="primary,strict")
    a = ap.parse_args()
    os.makedirs(os.path.join(a.out, "plots"), exist_ok=True)
    S = {}
    for flt in a.filters.split(","):
        e4f = sorted(glob.glob(os.path.join(a.out, f"e4_{flt}_k*.json")))
        rof = sorted(glob.glob(os.path.join(a.out, f"rolling_{flt}_k*.json")))
        if not e4f and not rof:
            continue
        S[flt] = {}
        if e4f:
            S[flt]["A_B_one_shot"], e4rows = summarize_e4(e4f)
        if rof:
            S[flt]["C_rolling"], units = summarize_rolling(rof)
        if flt == "primary" and e4f and rof:
            plots(a.out, e4rows, S[flt]["C_rolling"], S[flt]["A_B_one_shot"])
    json.dump(S, open(os.path.join(a.out, "summary_large.json"), "w"), indent=1)
    print(json.dumps({f: {"A_n": v.get("A_B_one_shot", {}).get("n_units"),
                          "C_n": v.get("C_rolling", {}).get("n_units_total")} for f, v in S.items()}))


def plots(out, e4rows, C, AB):
    # A: per-unit frozen vs last-layer FT (one-shot early data)
    fz = np.array([r["rmse"]["frozen"] for r in e4rows]); la = np.array([r["rmse"]["last"] for r in e4rows])
    fig, ax = plt.subplots(figsize=(5.2, 5), dpi=150)
    lim = [0, max(fz.max(), la.max()) * 1.05]
    ax.plot(lim, lim, color=INK2, linewidth=1, linestyle=":", label="equal (y = x)")
    ax.scatter(fz, la, s=22, color=C_BLUE, edgecolor="white", linewidth=0.6, zorder=3,
               label=f"one unit ({(la < fz).sum()} of {len(fz)} below the line = FT helped)")
    style(ax); ax.set_xlim(lim); ax.set_ylim(lim)
    ax.set_xlabel("Frozen fleet model RMSE (Ah)", color=INK2, fontsize=9)
    ax.set_ylabel("Last-layer FT on early data, RMSE (Ah)", color=INK2, fontsize=9)
    ax.set_title("A — one-shot early-data fine-tune, per unit", color=INK, fontsize=10, loc="left")
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    fig.tight_layout(); fig.savefig(os.path.join(out, "plots", "A_per_unit_frozen_vs_ft.png")); plt.close(fig)

    # B: variant comparison (one-shot), median + IQR per condition
    order = ["frozen", "early_mean", "bias", "last", "last_guard", "head", "head_guard"]
    order = [k for k in order if k in AB["conditions"]]
    fig, ax = plt.subplots(figsize=(8, 4), dpi=150)
    for i, k in enumerate(order):
        c = AB["conditions"][k]
        col = C_GRAY if k == "frozen" else C_BLUE
        ax.errorbar(i, c["median"], yerr=[[c["median"] - c["iqr"][0]], [c["iqr"][1] - c["median"]]], fmt="o",
                    color=col, ecolor=col, elinewidth=1.5, capsize=4, markersize=7, zorder=3)
        lab = "" if k == "frozen" else f"{c['beats_frozen']}/{AB['n_units']}\np={c['sign_p_vs_frozen']:.2g}"
        ax.text(i, c["iqr"][1] * 1.02, lab, ha="center", va="bottom", fontsize=7.5, color=INK)
    ax.axhline(AB["conditions"]["frozen"]["median"], color=C_GRAY, linewidth=1, linestyle=":", zorder=1)
    ax.set_ylim(top=max(AB["conditions"][k]["iqr"][1] for k in order) * 1.14)
    style(ax); ax.set_xticks(range(len(order)), order, fontsize=8)
    ax.set_ylabel("RMSE on later held-out data (Ah)\nmedian and IQR across units", color=INK2, fontsize=9)
    ax.set_title("B — adaptation variants, one-shot early-data protocol (label: units beating frozen, sign-test p)",
                 color=INK, fontsize=10, loc="left")
    fig.tight_layout(); fig.savefig(os.path.join(out, "plots", "B_variants.png")); plt.close(fig)

    # C: rolling RMSE vs horizon
    bands = [b for b in C["bands"] if b["n_units"]]
    xs = np.arange(len(bands))
    fig, ax = plt.subplots(figsize=(8, 4.2), dpi=150)
    for m, col, lab, ls in (("frozen", C_GRAY, "Frozen fleet model", "-"), ("last", C_BLUE, "Rolling last-layer FT", "-"),
                            ("head_guard", C_AQUA, "Rolling whole-head FT + guard", "-"),
                            ("persist_recent", C_ORANGE, "Persistence control (no model)", "--")):
        med = [b["methods"][m]["median"] for b in bands]
        lo = [b["methods"][m]["iqr"][0] for b in bands]; hi = [b["methods"][m]["iqr"][1] for b in bands]
        ax.plot(xs, med, color=col, linewidth=2, linestyle=ls, marker="o", markersize=6, label=lab, zorder=3)
        if m in ("frozen", "last"):
            ax.fill_between(xs, lo, hi, color=col, alpha=0.12, linewidth=0, zorder=1)
    for i, b in enumerate(bands):
        s = b["methods"]["last"]
        ax.text(i, min(b["methods"][k]["iqr"][0] for k in ("frozen", "last")) * 0.97,
                f"{s['beats_frozen']}/{b['n_units']}", ha="center", va="top", fontsize=7.5, color=INK2)
    style(ax)
    ax.set_xticks(xs, [f"{int(b['band_km'][0] / 1e3)}–{int(b['band_km'][1] / 1e3)}k" for b in bands], fontsize=8)
    ax.set_xlabel("Prediction horizon beyond the fine-tune origin (km)   [numbers: units where rolling FT beats frozen]",
                  color=INK2, fontsize=8.5)
    ax.set_ylabel("RMSE (Ah), median across units\n(shaded: IQR)", color=INK2, fontsize=9)
    ax.set_title("C — rolling re-fine-tune vs frozen, by horizon", color=INK, fontsize=10, loc="left")
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    fig.tight_layout(); fig.savefig(os.path.join(out, "plots", "C_rolling_vs_horizon.png")); plt.close(fig)


if __name__ == "__main__":
    main()
