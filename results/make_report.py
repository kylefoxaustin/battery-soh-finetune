"""Build results/summary.json + plots from the raw JSONs. results.md is written by hand FROM summary.json
(so every number in it traces to a file); this script refuses to emit a number without a tag.

Usage: python results/make_report.py [--raw results/raw] [--host results/host]
"""
import argparse
import glob
import json
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SRAM_BUDGET_KB = 512  # ASSUMED: a representative small MCU on-chip SRAM budget (e.g. MCX N94x class)
# reference palette (dataviz skill, light mode): slots 1-3 + neutral for the frozen reference
C_BLUE, C_ORANGE, C_AQUA, C_GRAY = "#2a78d6", "#eb6834", "#1baf7a", "#8a8984"
INK, INK2 = "#0b0b0b", "#52514e"


def tagged(value, tag, how):
    assert tag in ("MEASURED", "DERIVED", "ASSUMED", "UNGATED", "MEASURED (gated)"), tag
    return {"value": value, "tag": tag, "how": how}


def med(xs):
    return float(np.median(xs))


def noise_floor(run, cars):
    """DERIVED: how well can ANY per-car model do? SD of labels around a per-car linear-in-odometer fit."""
    sds = []
    for c in cars:
        p = os.path.join(run, "cars", f"car_{c}.npz")
        if not os.path.exists(p):
            return None
        d = np.load(p)
        A = np.vstack([d["mileage"], np.ones(len(d["mileage"]))]).T
        res = d["capacity"] - A @ np.linalg.lstsq(A, d["capacity"], rcond=None)[0]
        sds.append(res.std())
    return float(np.median(sds))


def style(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.spines["left"].set_color(INK2)
    ax.spines["bottom"].set_color(INK2)
    ax.tick_params(colors=INK2, labelsize=9)
    ax.grid(axis="y", color="#e4e3df", linewidth=0.8)
    ax.set_axisbelow(True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default=os.path.join(HERE, "raw"))
    ap.add_argument("--host", default=os.path.join(HERE, "host"))
    a = ap.parse_args()
    os.makedirs(os.path.join(HERE, "plots"), exist_ok=True)
    S = {}

    # ---------------- E1 ----------------
    e1 = {m: json.load(open(os.path.join(a.raw, f))) for m, f in (("int8", "e1.json"), ("fp32", "e1_fp32.json"))}
    for m, d in e1.items():
        t = "MEASURED" if d["gate"]["pass"] else "UNGATED"
        S[f"e1_{m}"] = {
            "stored_bytes": tagged(d["tflite_bytes"], "MEASURED", ".tflite file size"),
            "latency_p50_ms": tagged(d["latency_ms"]["p50"], t, f"wall clock, {d['latency_ms']['n']} invokes, 1 thread, core {d['env']['affinity']}, output gated same run"),
            "latency_p99_ms": tagged(d["latency_ms"]["p99"], t, "as above"),
            "interp_delta_kb": tagged(d["mem_kb"]["interp_delta"], t, "VmRSS after allocate_tensors minus before interpreter"),
            "hwm_kb": tagged(d["mem_kb"]["hwm"], t, "VmHWM, whole python process"),
            "gate": d["gate"], "governor": d["env"]["cpufreq"][f"cpu{d['env']['affinity'][0]}"]}

    # ---------------- E2 / E3 ----------------
    runs = [json.load(open(f)) for f in sorted(glob.glob(os.path.join(a.raw, "e[23]", "*_r*.json")))]
    mem = {}
    for r in runs:
        k = f"{r['config']['scope']}_{r['config']['opt']}"
        mem.setdefault(k, []).append(r)
    for k, rs in mem.items():
        ok = all(r["gate"]["pass"] for r in rs)
        t = "MEASURED" if ok else "UNGATED"
        S[f"train_{k}"] = {
            "n_reps": len(rs), "all_gates_pass": ok,
            "params_trainable": rs[0]["params_trainable"],
            "hwm_peak_kb": tagged([r["mem_kb"]["hwm_peak"] for r in rs], t, "VmHWM after training loop, per rep"),
            "train_delta_kb": tagged([r["mem_kb"]["train_delta"] for r in rs], t, "VmHWM(after train) - VmHWM(before train), fresh process"),
            "rss_baseline_kb": tagged([r["mem_kb"]["rss_baseline"] for r in rs], t, "VmRSS before training (torch+model+one car)"),
            "opt_state_bytes": tagged(rs[0]["opt_state_bytes_actual"], "MEASURED", "sum of live optimizer state tensors"),
            "derived_bytes_per_brief": tagged(rs[0]["derived_bytes"]["total_per_brief"], "DERIVED", "trainable params x (8 SGD | 16 Adam) B"),
            "ms_per_step": tagged([r["ms_per_step"] for r in rs], t, f"bs {rs[0]['config']['bs']}, {rs[0]['config']['threads']} threads"),
            "heldout_rmse_ah": [r["heldout_rmse_ah"] for r in rs],
            "config": rs[0]["config"]}

    # ---------------- E4 ----------------
    for name, f in (("e4", "e4.json"), ("e4_ft10", "e4_ft10.json")):
        p = os.path.join(a.raw, f)
        if os.path.exists(p):
            S[name] = json.load(open(p))["summary"]
    for name, f in (("e4_host", "e4_host.json"), ("e4_host_nokm", "e4_host_nokm.json")):
        p = os.path.join(a.host, f)
        if os.path.exists(p):
            S[name] = json.load(open(p))["summary"]

    json.dump(S, open(os.path.join(HERE, "summary.json"), "w"), indent=1)

    # ---------------- plot 1: per-target RMSE ----------------
    e4p = os.path.join(a.raw, "e4.json") if os.path.exists(os.path.join(a.raw, "e4.json")) else os.path.join(a.host, "e4_host.json")
    e4 = json.load(open(e4p))
    rows = sorted(e4["per_car"], key=lambda r: r["rmse"]["frozen"])
    x = np.arange(len(rows))
    w = 0.27
    fig, ax = plt.subplots(figsize=(10, 4.2), dpi=150)
    series = [("frozen", "Frozen fleet model", C_GRAY), ("last", "Last-layer FT (brief protocol)", C_BLUE),
              ("last_guard", "Last-layer FT + chronological guard", C_ORANGE)]
    for j, (k, lab, c) in enumerate(series):
        ax.bar(x + (j - 1) * w, [r["rmse"][k] for r in rows], w - 0.03, color=c, label=lab, zorder=2)
    floor = noise_floor(os.path.join(HERE, "..", "runs", "ds1"), [r["car"] for r in rows])
    if floor is not None:
        ax.axhline(floor, color=INK2, linewidth=1, linestyle=":", zorder=3,
                   label=f"Label-noise floor ≈ {floor:.2f} Ah (DERIVED: median within-car residual SD)")
        S["e4_noise_floor_ah"] = tagged(floor, "DERIVED", "median over target cars of SD of capacity labels "
                                        "around a per-car linear fit vs odometer (all of the car's data)")
        json.dump(S, open(os.path.join(HERE, "summary.json"), "w"), indent=1)
    style(ax)
    ax.set_xticks(x, [str(r["car"]) for r in rows], fontsize=8)
    ax.set_xlabel("Target car (held out of fleet training), sorted by frozen RMSE", color=INK2, fontsize=9)
    ax.set_ylabel("RMSE on car's later held-out data (Ah)", color=INK2, fontsize=9)
    src = "board" if "e4.json" in e4p and a.raw in e4p else "host"
    ax.set_title(f"E4 — per-vehicle RMSE, frozen vs last-layer fine-tuned (MEASURED, real field data, {src} run)",
                 color=INK, fontsize=10, loc="left")
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    fig.tight_layout()
    fig.savefig(os.path.join(HERE, "plots", "e4_rmse_per_target.png"))
    plt.close(fig)

    # ---------------- plot 2: training-phase memory ----------------
    order = [("last_sgd", "Last layer\nSGD"), ("last_adam", "Last layer\nAdam"), ("head_sgd", "Head\nSGD"),
             ("head_adam", "Head\nAdam"), ("full_sgd", "Full retrain\nSGD"), ("full_adam", "Full retrain\nAdam")]
    order = [(k, l) for k, l in order if f"train_{k}" in S]
    fig, ax = plt.subplots(figsize=(9, 4.2), dpi=150)
    xs = np.arange(len(order))
    d_med = [med(S[f"train_{k}"]["train_delta_kb"]["value"]) for k, _ in order]
    d_min = [min(S[f"train_{k}"]["train_delta_kb"]["value"]) for k, _ in order]
    d_max = [max(S[f"train_{k}"]["train_delta_kb"]["value"]) for k, _ in order]
    der = [max(S[f"train_{k}"]["derived_bytes_per_brief"]["value"] / 1024, 1e-3) for k, _ in order]
    ax.bar(xs - 0.18, d_med, 0.34, color=C_BLUE, zorder=2, label="Training-phase VmHWM increase (MEASURED, median of reps)")
    ax.errorbar(xs - 0.18, d_med, yerr=[np.subtract(d_med, d_min), np.subtract(d_max, d_med)], fmt="none",
                ecolor=INK2, elinewidth=1, capsize=3, zorder=3)
    ax.bar(xs + 0.18, der, 0.34, color=C_AQUA, zorder=2, label="Weights+grads+optimizer state (DERIVED, brief §E2)")
    ax.axhline(SRAM_BUDGET_KB, color=C_ORANGE, linewidth=1.5, linestyle="--", zorder=1,
               label=f"{SRAM_BUDGET_KB} KB MCU on-chip SRAM budget (ASSUMED)")
    for xi, v in zip(xs - 0.18, d_med):
        ax.text(xi, v * 1.12, f"{v / 1024:.1f} MB" if v >= 1024 else f"{v:.0f} KB", ha="center", fontsize=7.5, color=INK)
    for xi, v in zip(xs + 0.18, der):
        ax.text(xi, v * 1.12, f"{v / 1024:.2f} MB" if v >= 1024 else f"{v * 1024:.0f} B" if v < 1 else f"{v:.1f} KB",
                ha="center", fontsize=7.5, color=INK)
    style(ax)
    ax.set_yscale("log")
    ax.set_ylim(0.3, 3e6)
    ax.set_xticks(xs, [l for _, l in order], fontsize=8)
    ax.set_ylabel("KB (log scale)", color=INK2, fontsize=9)
    ax.set_title("E2/E3 — memory added by training on the i.MX95 A55 (PyTorch fp32, bs 32, seq 128)",
                 color=INK, fontsize=10, loc="left")
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    fig.tight_layout()
    fig.savefig(os.path.join(HERE, "plots", "train_memory_by_mode.png"))
    plt.close(fig)
    print("wrote summary.json + plots/")


if __name__ == "__main__":
    main()
