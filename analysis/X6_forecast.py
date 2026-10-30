"""X6 knee forecasting, exactly as results/X/X6_preregistration.md (2188950 + D-1, D-2 at 2881c7b, public hashes).
ISU-ILCC synthetic packs (CC BY 4.0), X5's units, split and truncation. Task A (warning AUC) and Task B (reserve with
knee adjustment). Every number DERIVED from MEASURED lab labels. Usage: nice python3 -E analysis/X6_forecast.py
"""
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import X5_estimate as X5                                         # noqa: E402
from X6_profile import onsets                                     # noqa: E402

OUT = "results/X/X6"
VGRID = np.linspace(3.0, 4.2, 1000)
LAM = 1.0
FAR = 0.10
NBOOT = 2000
SMOOTH = 21
ALPHAS = (0.05, 0.01, 0.001)
FLOOR_R = 0.001
FEAT = {"K1": ["slope", "curv"], "K2": ["slope", "curv"], "K3": ["slope", "curv", "f_var", "f_peak"]}


# ---------------------------------------------------------------- features
def win_feats(t, q):
    """slope and t^2 coefficient of OLS fits over the window (q: (W,) or (W, cells))."""
    A1 = np.vstack([t, np.ones_like(t)]).T
    A2 = np.vstack([t ** 2, t, np.ones_like(t)]).T
    s = np.linalg.lstsq(A1, q, rcond=None)[0][0]
    c = np.linalg.lstsq(A2, q, rcond=None)[0][0]
    return s, c


def peak_v(qv):
    """Voltage (V) of the largest |dQ/dV| after a centred 21-point nan-aware moving average."""
    ok = np.isfinite(qv)
    if ok.sum() < SMOOTH + 2:
        return np.nan
    k = np.ones(SMOOTH)
    num = np.convolve(np.where(ok, qv, 0.0), k, mode="same")
    den = np.convolve(ok.astype(float), k, mode="same")
    qs = np.where(den >= SMOOTH, num / np.maximum(den, 1), np.nan)
    f = np.isfinite(qs)
    if f.sum() < 3:
        return np.nan
    d = np.gradient(qs[f], VGRID[f])
    return float(VGRID[f][np.argmax(np.abs(d))])


def unit_features(u, W, perm=None, qv_only=False):
    """Per-check, per-cell features for checks j >= W. perm: per-check cell permutations (shuffle controls)."""
    t, Q, QV = u["t"], u["Q"].copy(), u["QV"].copy()
    if perm is not None:
        for j, p in enumerate(perm):
            QV[j] = QV[j, p]
            if not qv_only:
                Q[j] = Q[j, p]
    n, m = Q.shape
    q = Q / Q[0]
    U = Q.min(1)
    uq = U / U[0]
    pk = np.array([[peak_v(QV[j, c]) for c in range(m)] for j in range(n)])
    F = {}
    for j in range(W, n):
        sl = slice(j - W + 1, j + 1)
        s, c = win_feats(t[sl], q[sl])
        us, uc = win_feats(t[sl], uq[sl])
        dq = QV[j] - QV[j - W]
        with np.errstate(all="ignore"):
            fv = np.log10(np.maximum(np.nanvar(dq, axis=1), 1e-30))
        fp = 1e3 * (pk[j] - pk[j - W])
        F[j] = {"slope": s, "curv": c, "f_var": fv, "f_peak": fp, "u_slope": us, "u_curv": uc,
                "weakest": int(np.argmin(Q[j]))}
    return F


# ---------------------------------------------------------------- Task A rows
def task_rows(units, ids, W, L, H, T, feats):
    rows = []
    for g in ids:
        u = units[g]
        n = len(u["t"])
        ons = onsets(u["t"], u["Q"], H, T)
        F = feats[g]
        for c, k in enumerate(ons):
            ev_nw = None if k is None else (k - L >= 0 and int(np.argmin(u["Q"][k - L])) != c)
            for j in range(W, n - L):
                if k is not None and j >= k:
                    break
                f = F[j]
                rows.append({"g": g, "c": c, "j": j, "y": int(k is not None and k - L <= j),
                             "weakest": int(f["weakest"] == c), "event_not_weakest": ev_nw,
                             "slope": f["slope"][c], "curv": f["curv"][c], "f_var": f["f_var"][c],
                             "f_peak": f["f_peak"][c], "u_slope": f["u_slope"], "u_curv": f["u_curv"]})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- model
def fit_logit(X, y):
    mu, sd = X.mean(0), X.std(0)
    sd[sd == 0] = 1
    Z = np.column_stack([np.ones(len(X)), (X - mu) / sd])
    b = np.zeros(Z.shape[1])
    P = np.eye(Z.shape[1]) * LAM
    P[0, 0] = 0
    for _ in range(100):
        p = 1 / (1 + np.exp(-Z @ b))
        g = Z.T @ (p - y) + P @ b
        Hs = Z.T @ (Z * (p * (1 - p))[:, None]) + P
        step = np.linalg.solve(Hs, g)
        b -= step
        if np.max(np.abs(step)) < 1e-9:
            break
    return {"mu": mu, "sd": sd, "b": b}


def predict_logit(m, X):
    Z = np.column_stack([np.ones(len(X)), (X - m["mu"]) / m["sd"]])
    return 1 / (1 + np.exp(-Z @ m["b"]))


class Models:
    def __init__(self, cal):
        self.med = {f: float(np.nanmedian(cal[f])) for f in ("slope", "curv", "f_var", "f_peak", "u_slope", "u_curv")}
        self.imputed_cal = int((~np.isfinite(cal[["f_var", "f_peak"]].to_numpy())).any(1).sum())
        c = self.fill(cal)
        w = c[c["weakest"] == 1]
        self.k1 = fit_logit(w[["u_slope", "u_curv"]].to_numpy(), w["y"].to_numpy())
        self.k1_const = float(c.loc[c["weakest"] == 0, "y"].mean())
        self.k2 = fit_logit(c[FEAT["K2"]].to_numpy(), c["y"].to_numpy())
        self.k3 = fit_logit(c[FEAT["K3"]].to_numpy(), c["y"].to_numpy())

    def fill(self, d):
        d = d.copy()
        for f, v in self.med.items():
            d[f] = d[f].where(np.isfinite(d[f]), v)
        return d

    def score(self, d, which):
        d = self.fill(d)
        if which == "K0":
            return np.zeros(len(d))
        if which == "K1":
            s = np.full(len(d), self.k1_const)
            w = d["weakest"].to_numpy() == 1
            if w.any():
                s[w] = predict_logit(self.k1, d.loc[w, ["u_slope", "u_curv"]].to_numpy())
            return s
        m = self.k2 if which == "K2" else self.k3
        return predict_logit(m, d[FEAT["K2" if which == "K2" else "K3"]].to_numpy())


# ---------------------------------------------------------------- metrics
def auc(y, s):
    y = np.asarray(y)
    if y.sum() == 0 or y.sum() == len(y):
        return np.nan
    r = pd.Series(s).rank(method="average").to_numpy()
    n1 = y.sum()
    return float((r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * (len(y) - n1)))


def prec_at_far(y, s, far=FAR):
    y = np.asarray(y)
    thr = np.quantile(s[y == 0], 1 - far)
    f = s > thr
    tp = int((f & (y == 1)).sum())
    return {"precision": tp / max(f.sum(), 1), "recall": tp / max(y.sum(), 1),
            "far_achieved": float((f & (y == 0)).sum() / max((y == 0).sum(), 1))}


def boot_diffs(df, pairs, ids):
    by = {g: d.index.to_numpy() for g, d in df.groupby("g")}
    ids = [g for g in ids if g in by]
    rng = np.random.default_rng(0)
    out = {k: [] for k in pairs}
    y = df["y"].to_numpy()
    S = {c: df[c].to_numpy() for c in set(sum(pairs.values(), ()))}
    for _ in range(NBOOT):
        ix = np.concatenate([by[g] for g in rng.choice(ids, len(ids), replace=True)])
        for k, (a, b) in pairs.items():
            out[k].append(auc(y[ix], S[a][ix]) - auc(y[ix], S[b][ix]))
    return {k: [float(np.nanpercentile(v, 2.5)), float(np.nanpercentile(v, 97.5))] for k, v in out.items()}


def ceiling_auc(df):
    """D-2: weakest positives on top, all non-weakest tied in the middle, weakest negatives at the bottom."""
    s = np.where(df["weakest"] == 1, np.where(df["y"] == 1, 2.0, 0.0), 1.0)
    return auc(df["y"], s)


# ---------------------------------------------------------------- Task B
def task_b(units, cal, ev, W, models, theta, delta, featsets, a_list=ALPHAS):
    """X5 targets (W, warm-up 30 %) with knee adjustments. featsets: {'real': feats, 'sh': feats_sh}."""
    par = X5.fit_cal(units, cal, W, 0.30)
    rows = []
    for g in ev:
        u = units[g]
        t, Q = u["t"], u["Q"]
        U, M = Q.min(1), Q.mean(1)
        rng = np.random.default_rng(g)
        perm = [rng.permutation(Q.shape[1]) for _ in range(len(t))]
        Qsh = np.array([Q[j, p] for j, p in enumerate(perm)])
        for k in X5.target_ks(len(t), W, 0.30):
            sl = slice(k - W, k)
            pc, _ = X5.trend(t[sl], Q[sl], t[k])
            psh, _ = X5.trend(t[sl], Qsh[sl], t[k])
            pM, _ = X5.trend(t[sl], M[sl], t[k])
            pU, _ = X5.trend(t[sl], U[sl], t[k])
            r = {"g": g, "k": k, "U": U[k], "P1": par["rho"] * pM, "P2": pU, "P3": pc.min(), "P3sh": psh.min()}
            j = k - 1
            flags = {}
            for name, fs, base in (("K1", "real", None), ("K2", "real", None), ("K3", "real", None),
                                   ("K3sh", "sh", None)):
                F = featsets[fs][g].get(j)
                if F is None:
                    flags[name] = np.zeros(Q.shape[1], bool)
                    continue
                d = pd.DataFrame({"slope": F["slope"], "curv": F["curv"], "f_var": F["f_var"], "f_peak": F["f_peak"],
                                  "u_slope": F["u_slope"], "u_curv": F["u_curv"],
                                  "weakest": (np.arange(Q.shape[1]) == F["weakest"]).astype(int)})
                sc = models.score(d, "K3" if name == "K3sh" else name)
                flags[name] = sc > theta[name]
            w = int(np.argmin(Q[j]))
            r["K1adj"] = pU - (delta * Q[0, w] if flags["K1"][w] else 0.0)
            r["K2adj"] = float((pc - delta * Q[0] * flags["K2"]).min())
            r["K3adj"] = float((pc - delta * Q[0] * flags["K3"]).min())
            r["K3shadj"] = float((psh - delta * Qsh[0] * flags["K3sh"]).min())
            r["n_flag_K3"] = int(flags["K3"].sum())
            r["n_flag_K1"] = int(flags["K1"][w])
            rows.append(r)
    df = pd.DataFrame(rows)
    ref = float(np.median(df["U"]))
    cols = ["P1", "P2", "P3", "P3sh", "K1adj", "K2adj", "K3adj", "K3shadj"]
    res = {c: {f"r{a}": float(np.quantile(df[c] - df["U"], 1 - a) / ref) for a in a_list} for c in cols}

    def g_b(d):
        rf = float(np.median(d["U"]))
        r1 = {c: max(float(np.quantile(d[c] - d["U"], 0.99) / rf), FLOOR_R) for c in cols}
        return r1["K1adj"] / r1["K3adj"], r1["P1"] / min(r1[c] for c in ("K1adj", "K2adj", "K3adj"))
    gb, g4 = g_b(df)
    by = {g: d for g, d in df.groupby("g")}
    ids = list(by)
    rng = np.random.default_rng(0)
    bs = [g_b(pd.concat([by[g] for g in rng.choice(ids, len(ids), replace=True)]))[0] for _ in range(NBOOT)]
    return {"n_targets": int(len(df)), "reserve": res, "G_B": gb, "G_B_ci": [float(np.percentile(bs, 2.5)),
                                                                            float(np.percentile(bs, 97.5))],
            "P1_over_best_adjusted": g4, "targets_flagged_K3": int((df["n_flag_K3"] > 0).sum()),
            "targets_flagged_K1": int(df["n_flag_K1"].sum())}, df


# ---------------------------------------------------------------- one full run
def shuffle_perms(units, ids):
    out = {}
    for g in ids:
        m, n = units[g]["Q"].shape[1], len(units[g]["t"])
        rng = np.random.default_rng(g)
        out[g] = [rng.permutation(m) for _ in range(n)]
    return out


def run(units, cal, ev, W=4, H=2, T=0.05, far_b=FAR, first=None, do_b=True):
    ids = cal + ev
    feats = {g: unit_features(units[g], W) for g in ids}
    perms = shuffle_perms(units, ids)
    feats_sh = {g: unit_features(units[g], W, perms[g]) for g in ev}
    feats_shq = {g: unit_features(units[g], W, perms[g], qv_only=True) for g in ev}
    res = {}
    models_l1 = None
    for L in (1, 2):
        cal_rows = task_rows(units, cal, W, L, H, T, feats)
        ev_rows = task_rows(units, ev, W, L, H, T, feats)
        sh_rows = task_rows(units, ev, W, L, H, T, feats_sh)
        shq_rows = task_rows(units, ev, W, L, H, T, feats_shq)
        mdl = Models(cal_rows)
        if L == 1:
            models_l1, cal_l1 = mdl, cal_rows
        d = ev_rows.copy()
        for kname in ("K0", "K1", "K2", "K3"):
            d[kname] = mdl.score(ev_rows, kname)
        d["K3sh"] = mdl.score(sh_rows, "K3")
        d["K3shQ"] = mdl.score(shq_rows, "K3")
        y = d["y"].to_numpy()
        A = {k: auc(y, d[k].to_numpy()) for k in ("K0", "K1", "K2", "K3", "K3sh", "K3shQ")}
        P = {k: prec_at_far(y, d[k].to_numpy()) for k in ("K1", "K2", "K3", "K3sh", "K3shQ")}
        pairs = {"K3-K1": ("K3", "K1"), "K3sh-K1": ("K3sh", "K1"), "K2-K1": ("K2", "K1"),
                 "K3-K3sh": ("K3", "K3sh"), "K3-K2": ("K3", "K2")}
        ci = boot_diffs(d, pairs, ev)
        # control 2: positives only from knees in cells not the weakest at onset - L
        c2 = d[(d["y"] == 0) | (d["event_not_weakest"] == True)]                      # noqa: E712
        A2 = {k: auc(c2["y"].to_numpy(), c2[k].to_numpy()) for k in ("K1", "K2", "K3", "K3sh")}
        res[f"L{L}"] = {"n_pos": int(y.sum()), "n_neg": int((y == 0).sum()), "n_events": int(
            d.loc[d["y"] == 1, ["g", "c"]].drop_duplicates().shape[0]), "auc": A, "prec_at_far10": P,
            "diff": {k: A[pairs[k][0]] - A[pairs[k][1]] for k in pairs}, "diff_ci": ci,
            "K1_ceiling_auc": ceiling_auc(d), "control2": {"n_pos": int(c2["y"].sum()), "auc": A2},
            "imputed_features_eval": int((~np.isfinite(ev_rows[["f_var", "f_peak"]].to_numpy())).any(1).sum()),
            "imputed_features_cal": mdl.imputed_cal}
        if L == 1:
            res["_roc_L1"] = d[["y", "K1", "K2", "K3", "K3sh"]]
        else:
            res["_roc_L2"] = d[["y", "K1", "K2", "K3", "K3sh"]]
    # decision (L = 1)
    r1 = res["L1"]
    n_ev = sum(1 for g in ev for k in onsets(units[g]["t"], units[g]["Q"], H, T) if k is not None)
    res["knee_events_eval"] = n_ev
    if do_b:
        cal_sc = {k: models_l1.score(cal_l1, k) for k in ("K1", "K2", "K3")}
        neg = cal_l1["y"].to_numpy() == 0
        theta = {k: float(np.quantile(cal_sc[k][neg], 1 - far_b)) for k in cal_sc}
        theta["K3sh"] = theta["K3"]
        dl = []
        for g in cal:
            u = units[g]
            for c, k in enumerate(onsets(u["t"], u["Q"], H, T)):
                if k is not None:
                    dl.append((u["Q"][k, c] - u["Q"][k + 1, c]) / u["Q"][0, c])
        delta = float(np.median(dl))
        b, bdf = task_b(units, cal, ev, W, models_l1, theta, delta, {"real": feats, "sh": feats_sh})
        b.update({"theta": theta, "delta": delta})
        res["task_b"], res["_bdf"] = b, bdf
        gb = b["G_B"]
    else:
        gb = np.nan
    d31, lo31 = r1["diff"]["K3-K1"], r1["diff_ci"]["K3-K1"][0]
    dsh = r1["diff"]["K3sh-K1"]
    if n_ev < 30:
        v = "UNDERPOWERED"
    elif d31 >= 0.10 and lo31 > 0 and dsh < 0.05 and gb >= 1.5:
        v = "HISTORY FORECASTS KNEES"
    elif d31 < 0.05:
        v = "WEAKEST-CELL VIEW SUFFICES"
    else:
        v = "UNCLEAR"
    res["verdict"] = v
    return res, models_l1


# ---------------------------------------------------------------- plots
def plots(res, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 3, figsize=(17, 4.8))
    for i, L in enumerate((1, 2)):
        d = res[f"_roc_L{L}"]
        y = d["y"].to_numpy()
        for k, c in (("K1", "C0"), ("K2", "C2"), ("K3", "C3"), ("K3sh", "k")):
            s = d[k].to_numpy()
            thr = np.unique(s)[::-1]
            tpr = [((s >= t) & (y == 1)).sum() / y.sum() for t in thr]
            fpr = [((s >= t) & (y == 0)).sum() / (y == 0).sum() for t in thr]
            ax[i].plot([0] + fpr, [0] + tpr, color=c, ls="--" if k == "K3sh" else "-",
                       label=f"{k} AUC {res[f'L{L}']['auc'][k]:.2f}")
        ax[i].plot([0, 1], [0, 1], color="0.7", lw=0.8)
        ax[i].axvline(0.1, color="0.8", ls=":")
        ax[i].set_title(f"Knee warning ROC, L = {L} (evaluation; K1 ceiling {res[f'L{L}']['K1_ceiling_auc']:.2f})")
        ax[i].set_xlabel("false-alarm rate")
        ax[i].set_ylabel("hit rate")
        ax[i].legend(fontsize=8)
    b = res["_bdf"]
    ref = float(np.median(b["U"]))
    al = np.geomspace(0.001, 0.2, 40)
    for k, c, ls in (("P1", "C0", ":"), ("P2", "C2", ":"), ("P3", "C3", ":"), ("K1adj", "C2", "-"),
                     ("K3adj", "C3", "-"), ("K3shadj", "k", "--")):
        ax[2].plot(100 * al, [100 * np.quantile(b[k] - b["U"], 1 - a) / ref for a in al], color=c, ls=ls, label=k)
    ax[2].set_xscale("log")
    ax[2].invert_xaxis()
    ax[2].set_xlabel("risk α (%)")
    ax[2].set_ylabel("reserve r_α (% of median U)")
    ax[2].set_title("Task B: knee-adjusted (solid) vs not (dotted)")
    ax[2].legend(fontsize=8)
    fig.suptitle("X6, ISU-ILCC synthetic packs (separately tested cells; no coupling; upper bound). DERIVED. "
                 "CC BY 4.0", fontsize=10)
    fig.tight_layout()
    fig.savefig(path, dpi=110)


def clean(o):
    return {k: v for k, v in o.items() if not k.startswith("_")}


def main():
    os.makedirs(OUT, exist_ok=True)
    sp = json.load(open("results/X/X5/split.json"))["ISU-ILCC"]
    cal, ev = sp["calibration"], sp["evaluation"]
    units = X5.build_units(X5.load_cells(), cal + ev)
    base, models = run(units, cal, ev)
    out = {"caveat": "synthetic packs of separately tested cells; no thermal or electrical coupling; an upper bound",
           "licence": "ISU-ILCC CC BY 4.0", "base": clean(base)}
    # first life: descriptive; full-life models applied to truncated units (no refit)
    first = {g: X5.truncate(u) for g, u in units.items()}
    fl = {}
    for L in (1, 2):
        ff = {g: unit_features(first[g], 4) for g in ev if len(first[g]["t"]) > 4}
        rows = task_rows(first, [g for g in ev if g in ff], 4, L, 2, 0.05, ff)
        rows_cal = task_rows(units, cal, 4, L, 2, 0.05, {g: unit_features(units[g], 4) for g in cal})
        m = Models(rows_cal)
        fl[f"L{L}"] = {"n_pos": int(rows["y"].sum()), "n_neg": int((rows["y"] == 0).sum()),
                       "auc": {k: auc(rows["y"].to_numpy(), m.score(rows, k)) for k in ("K1", "K2", "K3")}}
    out["first_life_descriptive"] = fl
    sens = {}
    for name, kw in (("W3", {"W": 3}), ("W6", {"W": 6}), ("H1_T3", {"H": 1, "T": 0.03}),
                     ("H3_T8", {"H": 3, "T": 0.08}), ("FAR5_taskB", {"far_b": 0.05}),
                     ("FAR20_taskB", {"far_b": 0.20})):
        r, _ = run(units, cal, ev, **kw)
        sens[name] = {"verdict": r["verdict"], "knee_events_eval": r["knee_events_eval"],
                      "auc_L1": r["L1"]["auc"], "diff_L1": r["L1"]["diff"], "diff_ci_L1": r["L1"]["diff_ci"],
                      "G_B": r["task_b"]["G_B"], "G_B_ci": r["task_b"]["G_B_ci"],
                      "P1_over_best_adjusted": r["task_b"]["P1_over_best_adjusted"]}
        print("sens", name, sens[name]["verdict"], {k: round(v, 3) for k, v in r["L1"]["auc"].items()},
              "G_B", round(r["task_b"]["G_B"], 2))
    out["sensitivity"] = sens
    json.dump(out, open(f"{OUT}/x6.json", "w"), indent=1, default=float)
    base["_bdf"].to_csv(f"{OUT}/x6_taskB_targets.csv", index=False)
    plots(base, f"{OUT}/x6_plots.png")
    print(json.dumps(clean(base), indent=1, default=float))
    print(json.dumps(fl, indent=1, default=float))


if __name__ == "__main__":
    main()
