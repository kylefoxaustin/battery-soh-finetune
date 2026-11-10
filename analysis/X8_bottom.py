"""Experiment X8 (pre-registered in results/X/X8_preregistration.md, commit 600b296, before this script existed; approved
without changes 2026-11-10): the bottom reserve. Per-cell-R vs min/max admissible DISCHARGE current at low SOC, each
limiter with its own kappa calibrated on one vehicle half against an independent per-cell reference (odd-index steps),
scored on the other half, both directions; shuffle control with a fresh permutation per frame.
Changan (CC BY-NC-SA 4.0, research only) primary; Beihang DTI then QAS (CC BY 4.0) replication arms.
Every number DERIVED (replay); V_cut, 1 C and every limit ASSUMED.

Because every limiter is I(kappa) = I(1) / kappa, a frame is unsafe at kappa iff kappa < I(1) / (1.001 * I_ref_h);
the whole kappa curve follows from that per-frame critical value.
Usage: python -E analysis/X8_bottom.py [--jobs 12]   (writes results/X/X8/x8.json, plots, margin table)
"""
import argparse
import json
import os
import sys
from multiprocessing import Pool

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import X8_profile as XP                                  # noqa: E402  (Changan low-SOC load, segments)

OUT = "results/X/X8"
KAPPAS = np.round(np.arange(1.00, 2.0001, 0.01), 2)
TOL, BAR, UNSAFE_TOL = 5e-4, 2e-3, 1.001
MIN_STEPS, R_MIN = 20, 0.05
SOC_SCORE, SOC_DEEP, COLD_C = 20.0, 10.0, 10.0
LIMS = ("cell", "mm", "sh")
SPLIT = json.load(open(f"{OUT}/split.json"))
PROFILE = json.load(open(f"{OUT}/profile.json"))["summary"]
ARMS = {
    "changan": dict(vcut=PROFILE["V_cut_mv"], win=30 * 86400.0, step_a=XP.STEP_C * XP.Q_C),
    "DTI": dict(vcut=PROFILE["beihang"]["DTI"]["V_cut_mv"], win=86400.0),
    "QAS": dict(vcut=PROFILE["beihang"]["QAS"]["V_cut_mv"], win=86400.0),
}


# ------------------------------------------------------------------ data (V in mV, I discharge-positive A)
def prep_changan(n, dither):
    Z = XP.load(n)
    t, I, st, ok = Z["t"], Z["I"].astype(np.float64), Z["status"], Z["sync"]
    V = Z["V_mv"].astype(np.float64)
    if dither:
        V = V + np.random.default_rng(0).uniform(-0.5, 0.5, V.shape)
    Ic = -I
    Tm = Z["T_c"].astype(np.float64).mean(1)
    sok = ok & (st != 1)
    dI = np.diff(Ic)
    k = np.flatnonzero(sok[:-1] & sok[1:] & (np.diff(t) <= XP.STEP_DT_S) & (np.diff(t) > 0)
                       & (np.abs(dI) >= XP.STEP_C * XP.Q_C) & (np.abs(np.diff(Tm)) <= XP.STEP_DT_K))
    r = (V[k + 1] - V[k]) / dI[k][:, None]
    d = ok & (I > XP.I_DIS) & (st != 1)
    return {"t": t, "soc": Z["soc"].astype(np.float64), "I": I, "V": V, "cold": Z["T_c"].min(1) < COLD_C,
            "segs": XP.segments(t, d), "ts": t[k + 1], "r": r}


def prep_beihang(fleet, n, dither):
    import X2C_profile as P
    V, Ic, T, S, valid = P.load(fleet, n)
    qref = json.load(open("results/X/X2C/frozen.json"))[fleet]["Q_ref_Ah"]
    Vmv = V * 1e3
    if dither:
        Vmv = Vmv + np.random.default_rng(0).uniform(-0.5, 0.5, Vmv.shape)
    t = np.arange(len(S), dtype=np.float64)
    ok = valid & (Ic < XP.I_DIS)
    k = np.flatnonzero(ok[:-1] & ok[1:] & (np.abs(np.diff(Ic)) >= XP.STEP_C * qref)
                       & (np.abs(np.diff(T)) <= XP.STEP_DT_K) & (S[1:] < 0.30))
    r = (Vmv[k + 1] - Vmv[k]) / np.diff(Ic)[k][:, None]
    d = valid & (Ic < -XP.I_DIS)
    return {"t": t, "soc": S * 100.0, "I": -Ic, "V": Vmv, "cold": T < COLD_C,
            "segs": XP.segments(t, d), "ts": t[k + 1], "r": r}


def clean(Rk, Rmm, rp_all):
    Rmm = Rmm if (np.isfinite(Rmm) and Rmm > R_MIN) else rp_all
    return np.where(np.isfinite(Rk) & (Rk > R_MIN), Rk, Rmm), Rmm


def head(V, I, R, vcut):
    """Per-cell admissible current at kappa = 1: (V + I R - V_cut) / R, frames x cells."""
    return (V + I[:, None] * R - vcut) / R


# ------------------------------------------------------------------ one vehicle, one variant
def vehicle(args):
    arm, n, var = args
    cfg = ARMS[arm]
    vcut = cfg["vcut"] + var.get("dvcut", 0)
    hz = var.get("hz", 1)
    D = prep_changan(n, var.get("dither", False)) if arm == "changan" else prep_beihang(arm, n, var.get("dither", False))
    ts, r = D["ts"], D["r"]
    rp = r.mean(1) if len(r) else np.zeros(0)
    rp_all = float(np.median(rp)) if len(rp) else 1.0
    rp_all = rp_all if rp_all > R_MIN else 1.0
    held = None
    if var.get("held"):
        if len(r) < 2 * MIN_STEPS:
            return {"veh": n, "nohist": len(D["segs"]), "frames": None}
        e, f = np.arange(0, 2 * MIN_STEPS, 2), np.arange(1, 2 * MIN_STEPS, 2)
        held = (clean(np.median(r[e], 0), float(np.median(rp[e])), rp_all),
                clean(np.median(r[f], 0), float(np.median(rp[f])), rp_all)[0])
    soc, I, V, t = D["soc"], D["I"], D["V"], D["t"]
    acc = {k: [] for k in ("cell", "mm", "sh", "ref", "refh", "soc", "cold", "sid", "notmin")}
    sess, nohist = [], 0
    for seg in D["segs"]:
        sc = soc[seg] < SOC_SCORE
        if not sc.any():
            continue
        t0 = t[seg[0]]
        lo, hi = np.searchsorted(ts, [t0 - cfg["win"], t0], "left")
        w = np.arange(lo, hi)
        E, F = w[0::2], w[1::2]
        if len(E) < MIN_STEPS or len(F) < MIN_STEPS:
            nohist += 1
            continue
        if held is None:
            (RE, Rpk), RF = clean(np.median(r[E], 0), float(np.median(rp[E])), rp_all), \
                clean(np.median(r[F], 0), float(np.median(rp[F])), rp_all)[0]
        else:
            (RE, Rpk), RF = held
        Vs, Is = V[seg], I[seg]
        iref = np.maximum(head(Vs, Is, RF[None, :], vcut).min(1), 0.0)
        refh = iref.copy()
        for j in range(1, hz + 1):
            refh[:-j] = np.minimum(refh[:-j], iref[j:])
        fi = seg[sc]
        Vf, If = V[fi], I[fi]
        hc = head(Vf, If, RE[None, :], vcut)
        acc["cell"].append(np.maximum(hc.min(1), 0.0))
        acc["notmin"].append(hc.argmin(1) != Vf.argmin(1))
        acc["mm"].append(np.maximum((Vf.min(1) + If * Rpk - vcut) / Rpk, 0.0))
        Rp = np.stack([RE[np.random.default_rng([n, int(x)]).permutation(len(RE))] for x in fi])
        acc["sh"].append(np.maximum(head(Vf, If, Rp, vcut).min(1), 0.0))
        acc["ref"].append(iref[sc])
        acc["refh"].append(refh[sc])
        acc["soc"].append(soc[fi])
        acc["cold"].append(D["cold"][fi])
        acc["sid"].append(np.full(len(fi), len(sess)))
        sess.append((float(t0), float(np.percentile(Is, 95)), int(len(fi))))
        if var.get("keep_trace") and len(fi) >= 30 and "trace" not in acc:
            acc["trace"] = {"t": (t[fi] - t0).tolist(), "I": If.tolist(), "ref": iref[sc].tolist(),
                            "cell": acc["cell"][-1].tolist(), "mm": acc["mm"][-1].tolist(),
                            "sh": acc["sh"][-1].tolist(), "soc": soc[fi].tolist()}
    out = {"veh": n, "nohist": nohist, "sessions": np.array(sess, np.float64).reshape(-1, 3)}
    if not sess:
        out["frames"] = None
        return out
    out["frames"] = {k: np.concatenate(acc[k]).astype(np.float32 if k not in ("sid", "notmin", "cold") else
                                                     (np.int32 if k == "sid" else bool))
                     for k in ("cell", "mm", "sh", "ref", "refh", "soc", "cold", "sid", "notmin")}
    if "trace" in acc:
        out["trace"] = acc["trace"]
    return out


# ------------------------------------------------------------------ analysis
def kstar(I1, refh):
    with np.errstate(divide="ignore", invalid="ignore"):
        k = I1 / (UNSAFE_TOL * refh.astype(np.float64))
    k[(refh <= 0) & (I1 > 0)] = np.inf
    k[I1 <= 0] = 0.0
    return k


def curve(ks):
    s = np.sort(ks)
    return 1.0 - np.searchsorted(s, KAPPAS, "right") / max(len(s), 1)


def gather(R):
    """Flatten per-vehicle results into one frame table and one session table (global session ids)."""
    F, S, off = {k: [] for k in ("cell", "mm", "sh", "ref", "refh", "soc", "cold", "sid", "notmin", "veh")}, [], 0
    for x in R:
        if x["frames"] is None:
            continue
        f = x["frames"]
        for k in ("cell", "mm", "sh", "ref", "refh", "soc", "cold", "notmin"):
            F[k].append(f[k])
        F["sid"].append(f["sid"] + off)
        F["veh"].append(np.full(len(f["sid"]), x["veh"], np.int32))
        S.append(np.column_stack([np.full(len(x["sessions"]), x["veh"]), x["sessions"]]))
        off += len(x["sessions"])
    F = {k: np.concatenate(v) for k, v in F.items()}
    return F, np.concatenate(S)                          # S columns: veh, t0, p95 current, scored frames


def boot_dir(vals_by_dir, rng, n=1000):
    """Direction-averaged median: resample vehicles within each evaluation half."""
    out = np.empty((n, len(vals_by_dir[0][1])))
    prep = []
    for g, vals in vals_by_dir:
        ug = np.unique(g)
        order = np.argsort(g, kind="stable")
        starts = np.searchsorted(g[order], ug)
        ends = np.searchsorted(g[order], ug, "right")
        prep.append((ug, order, starts, ends, vals))
    for b in range(n):
        acc = 0.0
        for ug, order, starts, ends, vals in prep:
            pick = rng.integers(0, len(ug), len(ug))
            ix = order[np.concatenate([np.arange(starts[p], ends[p]) for p in pick])]
            acc = acc + np.array([np.median(v[ix]) for v in vals])
        out[b] = acc / len(prep)
    return np.percentile(out, [2.5, 97.5], 0).T.tolist()


def analyse(R, arm, tol=TOL, rng=None, boot=True):
    rng = rng or np.random.default_rng(0)
    F, S = gather(R)
    halves = SPLIT["changan"] if arm == "changan" else SPLIT["beihang"][arm]
    ks = {l: kstar(F[l].astype(np.float64), F["refh"]) for l in LIMS}
    d = {"n_frames": int(len(F["sid"])), "n_sessions": int(len(S)), "n_vehicles": int(len(np.unique(F["veh"]))),
         "n_sessions_no_history": int(sum(x["nohist"] for x in R)),
         "frac_iref0": float((F["refh"] <= 0).mean()),
         "frac_iref0_t": float((F["ref"] <= 0).mean()),
         "binding_not_minV_frac": float(F["notmin"].mean())}
    for l in LIMS:
        d[f"frac_iref0_and_{l}_pos"] = float(((F["refh"] <= 0) & (F[l] > 0)).mean())
    dirs, per_dir = [("A", "B"), ("B", "A")], []
    for ca, ev in dirs:
        cm = np.isin(F["veh"], halves[ca])
        em = np.isin(F["veh"], halves[ev])
        dd = {}
        kap = {}
        for l in LIMS:
            cc, ce = curve(ks[l][cm]), curve(ks[l][em])
            ok = np.flatnonzero(cc <= tol)
            i = int(ok[0]) if len(ok) else len(KAPPAS) - 1
            kap[l] = float(KAPPAS[i])
            dd.update({f"kappa_{l}": kap[l], f"flagged_{l}": bool(not len(ok)), f"unsafe_cal_{l}": float(cc[i]),
                       f"unsafe_eval_{l}": float(ce[i]), f"curve_cal_{l}": cc.tolist(), f"curve_eval_{l}": ce.tolist()})
        # sessions of the evaluation half
        sid = F["sid"][em]
        nS = len(S)
        sums = {l: np.bincount(sid, F[l][em] / kap[l], nS) for l in LIMS}
        sums["ref"] = np.bincount(sid, F["ref"][em], nS)
        has = np.bincount(sid, minlength=nS) > 0
        good = has & (sums["mm"] > 0)
        dd["n_eval_sessions"], dd["n_eval_sessions_mm0"] = int(good.sum()), int((has & ~good).sum())
        Sx = sums["cell"][good] / sums["mm"][good] - 1
        Ssh = sums["sh"][good] / sums["mm"][good] - 1
        Sref = sums["ref"][good] / sums["mm"][good] - 1
        g = S[good, 0].astype(int)
        dd.update({"S": float(np.median(Sx)), "S_sh": float(np.median(Ssh)), "D": float(np.median(Sx - Ssh)),
                   "S_ref": float(np.median(Sref)), "S_p10_p90": np.percentile(Sx, [10, 90]).tolist()})
        dd["_vals"] = (g, [Sx, Ssh, Sx - Ssh])
        # subsets, same kappa
        for name, m in (("lt10", F["soc"][em] < SOC_DEEP), ("cold", F["cold"][em])):
            ss = {l: np.bincount(sid[m], F[l][em][m] / kap[l], nS) for l in LIMS}
            hs = (np.bincount(sid[m], minlength=nS) > 0) & (ss["mm"] > 0)
            if hs.any():
                a, b = ss["cell"][hs] / ss["mm"][hs] - 1, ss["sh"][hs] / ss["mm"][hs] - 1
                dd[f"{name}"] = {"n_sessions": int(hs.sum()), "n_vehicles": int(len(np.unique(S[hs, 0]))),
                                 "S": float(np.median(a)), "S_sh": float(np.median(b)), "D": float(np.median(a - b))}
                dd[f"_vals_{name}"] = (S[hs, 0].astype(int), [a, b, a - b])
        # usable depth: highest SOC (scored frames) where the admissible current < the session's p95 discharge current
        p95 = S[sid, 2]
        for l in LIMS:
            below = (F[l][em] / kap[l]) < p95
            top = np.full(nS, -1.0)
            np.maximum.at(top, sid[below], F["soc"][em][below])
            sel = top[good]
            dd[f"depth_{l}_median_soc"] = float(np.median(sel[sel >= 0])) if (sel >= 0).any() else None
            dd[f"depth_{l}_never_frac"] = float((sel < 0).mean())
        per_dir.append(dd)
    d["directions"] = {f"{ca}->{ev}": dd for (ca, ev), dd in zip(dirs, per_dir)}
    for k in ("S", "S_sh", "D", "S_ref"):
        d[k] = float(np.mean([dd[k] for dd in per_dir]))
    if boot:
        ci = boot_dir([dd["_vals"] for dd in per_dir], rng)
        d["S_CI"], d["S_sh_CI"], d["D_CI"] = ci
        for name in ("lt10", "cold"):
            if all(f"_vals_{name}" in dd for dd in per_dir):
                d[name] = {k: float(np.mean([dd[name][k] for dd in per_dir])) for k in ("S", "S_sh", "D")}
                d[name]["n_vehicles"] = int(sum(dd[name]["n_vehicles"] for dd in per_dir))
                d[name]["n_sessions"] = int(sum(dd[name]["n_sessions"] for dd in per_dir))
                c = boot_dir([dd[f"_vals_{name}"] for dd in per_dir], rng)
                d[name]["S_CI"], d[name]["S_sh_CI"], d[name]["D_CI"] = c
    for dd in per_dir:
        for k in [k for k in dd if k.startswith("_")]:
            dd.pop(k)
    return d


def decide(d):
    dirs = d["directions"].values()
    if any(dd[f"unsafe_eval_{l}"] > BAR or dd[f"flagged_{l}"] for dd in dirs for l in LIMS):
        return "NOT INTERPRETABLE"
    if d["S"] >= 0.01 and d["S_CI"][0] > 0 and d["D"] >= 0.01 and d["D_CI"][0] > 0:
        return "PER-CELL HELPS AT THE BOTTOM"
    if (d["S"] < 0.01 and d["S_CI"][1] < 0.01) or d["S_sh"] >= d["S"]:
        return "NO BENEFIT"
    return "UNCLEAR"


def run(pool, arm, var):
    vins = (sorted(SPLIT["changan"]["A"] + SPLIT["changan"]["B"]) if arm == "changan"
            else sorted(SPLIT["beihang"][arm]["A"] + SPLIT["beihang"][arm]["B"]))
    return pool.map(vehicle, [(arm, v, var) for v in vins], chunksize=1)


def margin_table(d):
    rows = []
    for name, dd in d["directions"].items():
        for l in LIMS:
            sel = [1.00, 1.02, 1.05, 1.10, 1.15, 1.20, 1.30, 1.40, 1.50, 1.75, 2.00]
            ix = [int(np.argmin(np.abs(KAPPAS - k))) for k in sel]
            rows.append({"direction": name, "limiter": l, "kappa_selected": dd[f"kappa_{l}"],
                         "unsafe_pct_cal_eval": {f"{KAPPAS[i]:.2f}": [round(100 * dd[f"curve_cal_{l}"][i], 4),
                                                                      round(100 * dd[f"curve_eval_{l}"][i], 4)]
                                                 for i in ix}})
    return rows


def plots(res, traces):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    arms = [a for a in ("changan", "DTI", "QAS") if a in res]
    fig, ax = plt.subplots(len(arms), 2, figsize=(13, 4 * len(arms)), squeeze=False)
    for i, a in enumerate(arms):
        b = res[a]["base"]
        for (name, dd), ls in zip(b["directions"].items(), ("-", "--")):
            for l, c in zip(LIMS, ("C0", "C1", "C2")):
                ax[i, 0].plot(KAPPAS, np.array(dd[f"curve_cal_{l}"]) * 100, ls, c=c, lw=1, label=f"{l} cal {name}")
                ax[i, 0].plot(KAPPAS, np.array(dd[f"curve_eval_{l}"]) * 100, ls, c=c, lw=2.2, alpha=.5,
                              label=f"{l} held-out {name}")
        ax[i, 0].axhline(TOL * 100, ls=":", c="k")
        ax[i, 0].axhline(BAR * 100, ls=":", c="r")
        ax[i, 0].set_yscale("symlog", linthresh=0.01)
        ax[i, 0].set_xlabel("kappa"); ax[i, 0].set_ylabel("unsafe frames vs reference (%)")
        ax[i, 0].set_title(f"{a}: kappa curves (thin = calibration, thick = held-out)")
        ax[i, 0].legend(fontsize=6, ncol=2)
        if a in traces:
            tr = traces[a]
            for k, c in (("ref", "k"), ("cell", "C0"), ("mm", "C1"), ("sh", "C2")):
                kap = b["directions"]["A->B"].get(f"kappa_{k}", 1.0) if k != "ref" else 1.0
                ax[i, 1].plot(tr["t"], np.array(tr[k]) / kap, c=c, label=k + ("" if k == "ref" else f" / {kap:.2f}"))
            ax[i, 1].plot(tr["t"], tr["I"], c="0.6", label="present current")
            ax[i, 1].set_xlabel("s (Changan) / rows (Beihang) from session start")
            ax[i, 1].set_ylabel("A"); ax[i, 1].legend(fontsize=7)
            ax[i, 1].set_title(f"{a}: one session's admissible currents (headroom estimates)")
    fig.suptitle("X8. DERIVED replay; V_cut and limits ASSUMED. Changan CC BY-NC-SA (research only); Beihang CC BY",
                 fontsize=10)
    fig.tight_layout()
    fig.savefig(f"{OUT}/x8_kappa_and_session.png", dpi=110)


def plot_S(Svals):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, len(Svals), figsize=(5 * len(Svals), 3.6), squeeze=False)
    for i, (a, (s, ssh)) in enumerate(Svals.items()):
        lo, hi = np.percentile(np.concatenate([s, ssh]), [1, 99])
        bins = np.linspace(lo, hi, 80)
        ax[0, i].hist(s * 100, bins=bins * 100, alpha=.6, label="S (per-cell)")
        ax[0, i].hist(ssh * 100, bins=bins * 100, alpha=.6, label="S_sh (shuffled)")
        ax[0, i].axvline(1, ls=":", c="r")
        ax[0, i].set_xlabel("% vs min/max, per session (A->B held-out)")
        ax[0, i].set_title(a); ax[0, i].legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(f"{OUT}/x8_S_distribution.png", dpi=110)


def session_S(R, arm, d):
    """Per-session S and S_sh in the A->B direction at its kappas (for the distribution plot)."""
    F, S = gather(R)
    halves = SPLIT["changan"] if arm == "changan" else SPLIT["beihang"][arm]
    dd = d["directions"]["A->B"]
    em = np.isin(F["veh"], halves["B"])
    sid = F["sid"][em]
    sm = {l: np.bincount(sid, F[l][em] / dd[f"kappa_{l}"], len(S)) for l in LIMS}
    g = sm["mm"] > 0
    return sm["cell"][g] / sm["mm"][g] - 1, sm["sh"][g] / sm["mm"][g] - 1


def strip(d):
    return {k: v for k, v in d.items() if k != "directions"} | {
        "directions": {n: {k: v for k, v in dd.items() if not k.startswith("curve_")} for n, dd in d["directions"].items()}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=12)
    ap.add_argument("--arms", default="changan,DTI,QAS")
    a = ap.parse_args()
    variants = {"base": {"keep_trace": True}, "vcut-50": {"dvcut": -50}, "vcut+50": {"dvcut": 50},
                "horizon20s": {"hz": 2}, "R_held": {"held": True}, "dither": {"dither": True}}
    res, traces, Svals = {}, {}, {}
    rng = np.random.default_rng(0)
    with Pool(a.jobs) as pool:
        for arm in a.arms.split(","):
            res[arm] = {}
            for vn, var in variants.items():
                if vn == "horizon20s" and arm != "changan":
                    continue
                R = run(pool, arm, var)
                d = analyse(R, arm, rng=rng)
                d["verdict_same_rules"] = decide(d)
                res[arm][vn] = d
                if vn == "base":
                    tr = next((x["trace"] for x in R if "trace" in x), None)
                    if tr:
                        traces[arm] = tr
                    Svals[arm] = session_S(R, arm, d)
                    for tol, name in ((1e-3, "bar0.1%"), (5e-3, "bar0.5%")):
                        e = analyse(R, arm, tol=tol, rng=rng)
                        e["verdict_same_rules"] = decide(e)
                        res[arm][name] = e
                del R
                print(arm, vn, res[arm][vn]["verdict_same_rules"], f"S {res[arm][vn]['S']:.4f}",
                      f"S_sh {res[arm][vn]['S_sh']:.4f}", f"D {res[arm][vn]['D']:.4f}", flush=True)
            b = res[arm]["base"]
            b["verdict"] = decide(b)
            dz = res[arm]["dither"]
            width = b["S_CI"][1] - b["S_CI"][0]
            b["dither_shift"] = dz["S"] - b["S"]
            b["dither_ci_width"] = width
            b["rounding_label"] = bool(abs(dz["S"] - b["S"]) > width)
            json.dump({"preregistered_in": "600b296", "partial": True,
                       **{k: {vn: strip(x) for vn, x in v.items()} for k, v in res.items()}},
                      open(f"{OUT}/x8_partial.json", "w"), indent=1, default=float)
    plots(res, traces)
    plot_S(Svals)
    table = {arm: margin_table(res[arm]["base"]) for arm in res}
    json.dump(table, open(f"{OUT}/x8_margin_table.json", "w"), indent=1)
    out = {"tag": "DERIVED replay; V_cut, 1 C and limits ASSUMED; Changan CC BY-NC-SA 4.0 research only; "
                  "Beihang CC BY 4.0", "preregistered_in": "600b296", "kappa_grid": KAPPAS.tolist(), **res}
    json.dump(out, open(f"{OUT}/x8.json", "w"), indent=1, default=float)
    if os.path.exists(f"{OUT}/x8_partial.json"):
        os.remove(f"{OUT}/x8_partial.json")
    print(json.dumps({arm: {vn: {k: x[k] for k in ("S", "S_sh", "D", "verdict_same_rules") if k in x}
                            for vn, x in v.items()} for arm, v in res.items()}, indent=1, default=float))


if __name__ == "__main__":
    main()
