"""X5 estimator run, exactly as results/X/X5_preregistration.md (059b818 + D-1, D-2 at bd7a2af; D-3 alignment).
ISU-ILCC synthetic packs (CC BY 4.0). P0-P4, shuffle control, label-noise floor, pack-level truth, sensitivity,
D-1 end-of-first-life co-primary, D-2 reserve by spread. Every number DERIVED from MEASURED lab labels.
Usage: nice python3 -E analysis/X5_estimate.py
"""
import glob
import json
import os
import re

import numpy as np
import pandas as pd

RAW = "data/raw/isu_ilcc"
OUT = "results/X/X5"
MATCH = 0.5                                   # same alignment rule as X5_profile.py
ALPHAS = (0.05, 0.01, 0.001)
FLOOR_R = 0.001                               # r floored at 0.1 % of median U before a ratio
SIGMA = 0.0024                                # median cell label noise (profile), for the noise floor
Z = {0.05: 1.6449, 0.01: 2.3263, 0.001: 3.0902}
RIDGE = 1.0
NBOOT = 2000
EST = ("P0", "P1", "P1h", "P2", "P3", "P4", "P3sh")


# ---------------------------------------------------------------- data
def load_cells():
    cells = {}
    for f in sorted(glob.glob(f"{RAW}/capacity_fade/Release */G*C*.csv")):
        b = os.path.basename(f)
        g, c = map(int, re.match(r"G(\d+)C(\d+)\.csv", b).groups())
        d = pd.read_csv(f)
        qv = pd.read_csv(f"{RAW}/Q_interpolated/{f.split('/')[-2]}/{b}", header=None).to_numpy(float)
        qv = qv[:, ~np.isnan(qv).all(0)]                      # D-3: drop the documented lost (all-empty) RPT columns
        ok = np.isfinite(d["Capacity"]).to_numpy() & (d["Capacity"] > 0).to_numpy()
        cells[(g, c)] = {"t": d["Time"].to_numpy(float)[ok], "q": d["Capacity"].to_numpy(float)[ok],
                         "qv": qv[:, ok] if qv.shape[1] == len(d) else None}
    return cells


def build_units(cells, groups):
    """Same alignment as the profile: grid = the group's longest cell; unit ends at the first check any cell lacks."""
    units = {}
    for g in groups:
        mem = sorted(c for gg, c in cells if gg == g)
        ref = max(mem, key=lambda c: len(cells[(g, c)]["t"]))
        grid = cells[(g, ref)]["t"]
        Q = np.full((len(grid), len(mem)), np.nan)
        idx = np.full((len(grid), len(mem)), -1)
        for j, c in enumerate(mem):
            t = cells[(g, c)]["t"]
            for i, tg in enumerate(grid):
                k = np.argmin(np.abs(t - tg))
                if abs(t[k] - tg) <= MATCH:
                    Q[i, j], idx[i, j] = cells[(g, c)]["q"][k], k
        full = np.isfinite(Q).all(1)
        n = int(np.flatnonzero(~full)[0]) if (~full).any() else len(grid)
        qv_ok = all(cells[(g, c)]["qv"] is not None for c in mem)
        QV = None
        if qv_ok:
            QV = np.stack([np.stack([cells[(g, c)]["qv"][:, idx[i, j]] for j, c in enumerate(mem)]) for i in range(n)])
        units[g] = {"t": grid[:n], "Q": Q[:n], "QV": QV}          # QV: (checks, cells, 1000)
    return units


def truncate(u):
    """D-1: keep checks before the first one where U < 0.8 U_0."""
    U = u["Q"].min(1)
    bad = np.flatnonzero(U < 0.8 * U[0])
    n = int(bad[0]) if len(bad) else len(U)
    return {"t": u["t"][:n], "Q": u["Q"][:n], "QV": None if u["QV"] is None else u["QV"][:n]}


# ---------------------------------------------------------------- estimators
def trend(t, x, tk):
    """OLS line of x against t over the given window, evaluated at tk. x may be (W,) or (W, cells)."""
    A = np.vstack([t, np.ones_like(t)]).T
    coef, *_ = np.linalg.lstsq(A, x, rcond=None)
    return coef[0] * tk + coef[1], coef[0]


def target_ks(n, W, warm):
    return list(range(max(int(np.ceil(warm * n)), W), n))


def p4_features(u, k, W, slope):
    """Per-cell P4 features at target k (fixed in the pre-registration)."""
    t, Q, QV = u["t"], u["Q"], u["QV"]
    f1 = slope * (t[k] - t[k - 1])
    d = QV[k - 1] - QV[k - 1 - W] if k - 1 - W >= 0 else QV[k - 1] - QV[0]
    f2 = np.log10(np.maximum(np.nanvar(d, axis=1), 1e-30))
    f3 = Q[k - 1] / Q[0]
    return np.column_stack([f1, f2, f3])


def fit_cal(units, cal, W, warm):
    """Calibration-half parameters: rho (P1) and the P4 ridge model."""
    ratios = [u["Q"].min(1) / u["Q"].mean(1) for g, u in units.items() if g in cal]
    rho = float(np.median(np.concatenate(ratios)))
    X, y = [], []
    for g in cal:
        u = units[g]
        if u["QV"] is None:
            continue
        for k in target_ks(len(u["t"]), W, warm):
            sl = slice(k - W, k)
            _, slope = trend(u["t"][sl], u["Q"][sl], u["t"][k])
            X.append(p4_features(u, k, W, slope))
            y.append(u["Q"][k] - u["Q"][k - 1])
    X, y = np.vstack(X), np.concatenate(y)
    m = np.all(np.isfinite(X), 1)
    X, y = X[m], y[m]
    mu, sd = X.mean(0), X.std(0)
    Xs = (X - mu) / sd
    ym = y.mean()
    beta = np.linalg.solve(Xs.T @ Xs + RIDGE * np.eye(Xs.shape[1]), Xs.T @ (y - ym))
    med = np.median(X, 0)
    return {"rho": rho, "mu": mu, "sd": sd, "beta": beta, "b0": ym, "med": med, "n_train": int(len(y)),
            "n_train_dropped_nonfinite": int((~m).sum())}


def predict_unit(g, u, W, warm, par, p3_last=False):
    """All estimators for every target of one unit. Returns a list of dicts."""
    t, Q = u["t"], u["Q"]
    U, M = Q.min(1), Q.mean(1)
    rng = np.random.default_rng(g)
    Qsh = np.array([rng.permutation(row) for row in Q])            # P-2: permute cells independently per check
    rows = []
    for k in target_ks(len(t), W, warm):
        sl = slice(k - W, k)
        pc, slope = trend(t[sl], Q[sl], t[k])
        if p3_last:
            pc = Q[k - 1]
        pM, _ = trend(t[sl], M[sl], t[k])
        pU, _ = trend(t[sl], U[sl], t[k])
        psh, _ = trend(t[sl], Qsh[sl], t[k])
        r = {"g": g, "k": k, "t": float(t[k]), "U": float(U[k]), "M": float(M[k]),
             "spread": float((Q[k].max() - Q[k].min()) / Q[k].mean()),
             "P0": float(U[k - 1]), "P1": float(par["rho"] * pM),
             "P1h": float(pM * np.median(U[:k] / M[:k])), "P2": float(pU), "P3": float(pc.min()),
             "P3sh": float(psh.min()),
             # pack-level truth versions (control 3)
             "pk_P0": float(M[k - 1]), "pk_P1": float(pM), "pk_P1h": float(pM), "pk_P2": float(pU / par["rho"]),
             "pk_P3": float(pc.mean()), "pk_P3sh": float(psh.mean())}
        if u["QV"] is not None:
            X = p4_features(u, k, W, slope)
            nf = ~np.isfinite(X)
            r["p4_imputed"] = int(nf.any(1).sum())
            X = np.where(nf, par["med"], X)
            dq = par["b0"] + ((X - par["mu"]) / par["sd"]) @ par["beta"]
            p4 = Q[k - 1] + dq
            r["P4"], r["pk_P4"] = float(p4.min()), float(p4.mean())
        else:
            r["P4"] = r["pk_P4"] = np.nan
        rows.append(r)
    return rows


# ---------------------------------------------------------------- metrics
def reserve(e, ref, a):
    return float(np.quantile(e, 1 - a) / ref) if len(e) else np.nan


def table(df, truth="U", prefix=""):
    """r_alpha both tails, MAE, per estimator."""
    ref = float(np.median(df[truth]))
    out = {}
    for p in EST:
        col = prefix + p
        if col not in df:
            continue
        d = df[np.isfinite(df[col])]
        e = (d[col] - d[truth]).to_numpy()
        out[p] = {"n": int(len(e)), "mae_pct": float(100 * np.mean(np.abs(e)) / ref),
                  **{f"r{a}": reserve(e, ref, a) for a in ALPHAS},
                  **{f"r_under{a}": reserve(-e, ref, a) for a in ALPHAS}}
    return out


def gain(rn, rd):
    return max(rn, FLOOR_R) / max(rd, FLOOR_R)


def gains_with_ci(df, ev_units, a=0.01):
    """G = r(P1)/r(P3) etc. at alpha, with a unit bootstrap (seed 0)."""
    pairs = {"G_P3": ("P1", "P3"), "G_P4": ("P1", "P4"), "G_sh": ("P1", "P3sh"), "G_P2_over_P3": ("P2", "P3"),
             "G_P0_over_P3": ("P0", "P3"), "G_P1h_over_P3": ("P1h", "P3")}

    def gs(d):
        ref = float(np.median(d["U"]))
        r = {}
        for p in ("P0", "P1", "P1h", "P2", "P3", "P4", "P3sh"):
            dd = d[np.isfinite(d[p])]
            r[p] = reserve((dd[p] - dd["U"]).to_numpy(), ref, a)
        return {k: gain(r[n], r[m]) for k, (n, m) in pairs.items()}

    point = gs(df)
    by = {g: d for g, d in df.groupby("g")}
    ids = [g for g in ev_units if g in by]
    rng = np.random.default_rng(0)
    boot = {k: [] for k in pairs}
    for _ in range(NBOOT):
        pick = rng.choice(ids, len(ids), replace=True)
        b = gs(pd.concat([by[g] for g in pick]))
        for k in pairs:
            boot[k].append(b[k])
    return {k: {"G": point[k], "ci": [float(np.percentile(boot[k], 2.5)), float(np.percentile(boot[k], 97.5))]}
            for k in pairs}


def decide(n, G, lo, G_sh):
    if n < 40:
        return "UNDERPOWERED"
    if G >= 1.5 and lo > 1 and G_sh < 1.2:
        return "PER-CELL HELPS"
    if G < 1.2:
        return "NO GAIN"
    return "UNCLEAR"


def run(units, cal, ev, W=4, warm=0.30, p3_last=False):
    par = fit_cal(units, cal, W, warm)
    rows = []
    for g in ev:
        rows += predict_unit(g, units[g], W, warm, par, p3_last)
    df = pd.DataFrame(rows)
    res = {"n_targets": int(len(df)), "n_units": int(df["g"].nunique()) if len(df) else 0,
           "rho": par["rho"], "p4_train_rows": par["n_train"], "p4_train_dropped": par["n_train_dropped_nonfinite"],
           "p4_beta_std": par["beta"].tolist(), "p4_targets_with_imputed_feature": int(df.get("p4_imputed",
                                                                                              pd.Series([0])).sum()),
           "units_without_qv": [int(g) for g in ev if units[g]["QV"] is None]}
    if len(df) == 0:
        return res, df
    res["reserve"] = table(df)
    res["pack_truth"] = table(df, truth="M", prefix="pk_")
    res["gains_a1"] = gains_with_ci(df, ev)
    res["share_P3_abs_lt_P1"] = float(np.mean(np.abs(df["P3"] - df["U"]) < np.abs(df["P1"] - df["U"])))
    gp3, gp4, gsh = res["gains_a1"]["G_P3"], res["gains_a1"]["G_P4"], res["gains_a1"]["G_sh"]["G"]
    res["verdict_P3"] = decide(len(df), gp3["G"], gp3["ci"][0], gsh)
    res["verdict_P4"] = decide(int(np.isfinite(df["P4"]).sum()), gp4["G"], gp4["ci"][0], gsh)
    res["reaches_4x"] = {"P3": gp3["G"] >= 4, "P4": gp4["G"] >= 4}
    res["noise_floor"] = {str(a): Z[a] * SIGMA for a in ALPHAS}
    return res, df


# ---------------------------------------------------------------- plots
def plots(df, units, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 4, figsize=(20, 4.6))
    al = np.geomspace(0.001, 0.2, 40)
    ref = float(np.median(df["U"]))
    for p, c in zip(("P0", "P1", "P2", "P3", "P4", "P3sh"), ("grey", "C0", "C2", "C3", "C1", "k")):
        d = df[np.isfinite(df[p])]
        e = (d[p] - d["U"]).to_numpy()
        ax[0].plot(100 * al, [100 * reserve(e, ref, a) for a in al], color=c, ls="--" if p == "P3sh" else "-",
                   label=p)
    ax[0].plot(100 * al, [100 * SIGMA * _z(a) for a in al], color="m", ls=":", label="noise floor")
    ax[0].set_xscale("log")
    ax[0].invert_xaxis()
    ax[0].set_xlabel("risk α (%)")
    ax[0].set_ylabel("reserve r_α (% of median U), over-statement tail")
    ax[0].set_title("Reserve vs risk, full life, W = 4 (evaluation half)")
    ax[0].legend(fontsize=8)
    for i, g in enumerate(EXAMPLES):
        a = ax[i + 1]
        u = units[g]
        a.plot(u["t"], 1e3 * u["Q"], color="0.8", lw=1)
        a.plot(u["t"], 1e3 * u["Q"].min(1), "k.-", label="measured U (weakest cell)")
        d = df[df["g"] == g]
        for p, c in (("P1", "C0"), ("P3", "C3"), ("P4", "C1")):
            a.plot(d["t"], 1e3 * d[p], "o", ms=3, color=c, label=p)
        a.set_title(f"Group {g} (evaluation)")
        a.set_xlabel("time on test (dataset units)")
        a.set_ylabel("capacity (mAh)")
        a.legend(fontsize=7)
    fig.suptitle("X5, ISU-ILCC synthetic packs (separately tested cells; no coupling). DERIVED. CC BY 4.0",
                 fontsize=10)
    fig.tight_layout()
    fig.savefig(path, dpi=110)


def _z(a):
    from statistics import NormalDist
    return NormalDist().inv_cdf(1 - a)


EXAMPLES = None


def main():
    global EXAMPLES
    sp = json.load(open(f"{OUT}/split.json"))["ISU-ILCC"]
    cal, ev = sp["calibration"], sp["evaluation"]
    EXAMPLES = ev[:3]
    cells = load_cells()
    units = build_units(cells, cal + ev)
    tr = {g: truncate(u) for g, u in units.items()}
    out = {"split": sp, "examples": EXAMPLES,
           "caveat": "synthetic packs of separately tested cells; no thermal or electrical coupling; an upper bound "
                     "on what per-cell history can do",
           "licence": "ISU-ILCC CC BY 4.0"}
    out["full"], dfa = run(units, cal, ev)
    out["truncated"], dfb = run(tr, cal, ev)                                  # D-1
    out["truncated"]["units_by_checks"] = {int(g): len(tr[g]["t"]) for g in ev}
    sens = {}
    for name, kw in (("W3", {"W": 3}), ("W6", {"W": 6}), ("warm20", {"warm": 0.2}), ("warm40", {"warm": 0.4}),
                     ("P3_last_value", {"p3_last": True})):
        r, _ = run(units, cal, ev, **kw)
        sens[name] = {k: r[k] for k in ("n_targets", "verdict_P3", "verdict_P4", "gains_a1")} | {
            "r1": {p: r["reserve"][p]["r0.01"] for p in r["reserve"]}}
    out["sensitivity"] = sens
    bins = [(0, .02, "<2 %"), (.02, .05, "2-5 %"), (.05, .15, "5-15 %"), (.15, 9, ">15 %")]      # D-2
    d2 = []
    for lo, hi, lab in bins:
        d = dfa[(dfa["spread"] >= lo) & (dfa["spread"] < hi)]
        if len(d) == 0:
            d2.append({"bin": lab, "n": 0, "units": 0})
            continue
        ref = float(np.median(d["U"]))
        d2.append({"bin": lab, "n": int(len(d)), "units": int(d["g"].nunique()),
                   "r1_P1": reserve((d["P1"] - d["U"]).to_numpy(), ref, 0.01),
                   "r1_P3": reserve((d["P3"] - d["U"]).to_numpy(), ref, 0.01),
                   "r1_P3sh": reserve((d["P3sh"] - d["U"]).to_numpy(), ref, 0.01)})
    out["by_spread"] = d2
    json.dump(out, open(f"{OUT}/x5.json", "w"), indent=1, default=float)
    dfa.to_csv(f"{OUT}/x5_targets_full.csv", index=False)
    plots(dfa, units, f"{OUT}/x5_plots.png")
    for key in ("full", "truncated"):
        o = out[key]
        print("==", key, o["n_targets"], "targets", o.get("n_units"), "units; rho", round(o["rho"], 4),
              "| P3:", o.get("verdict_P3"), "| P4:", o.get("verdict_P4"))
        if "reserve" in o:
            for p, v in o["reserve"].items():
                print(f"  {p:5s} n={v['n']:4d} mae={v['mae_pct']:.2f}% r5={100*v['r0.05']:.2f} r1={100*v['r0.01']:.2f}"
                      f" r0.1={100*v['r0.001']:.2f} | under r1={100*v['r_under0.01']:.2f}")
            for k, v in o["gains_a1"].items():
                print(f"  {k}: {v['G']:.2f} CI {v['ci'][0]:.2f}-{v['ci'][1]:.2f}")
            print("  pack truth r1:", {p: round(100 * v["r0.01"], 2) for p, v in o["pack_truth"].items()})
            print("  share P3 better", round(o["share_P3_abs_lt_P1"], 3), "P4 imputed", o[
                "p4_targets_with_imputed_feature"], "no qv", o["units_without_qv"])
    for k, v in sens.items():
        print("sens", k, v["n_targets"], v["verdict_P3"], v["verdict_P4"],
              {g: round(x["G"], 2) for g, x in v["gains_a1"].items()})
    print("by spread", json.dumps(d2, default=float))


if __name__ == "__main__":
    main()
