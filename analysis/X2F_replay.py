"""Experiment X2-F (pre-registered in results/X/X2F_preregistration.md, commit 6cbfeb8, before this script existed):
fair comparison of per-cell vs min/max charge limiting. Each limiter (min/max, per-cell, shuffled per-cell) carries its
own kappa margin, calibrated on the calibration half against a per-cell safety reference whose R comes from disjoint
(odd-index) steps. Pre-registered RE-ANALYSIS of Beihang data X2-C already used. Every number DERIVED, limits ASSUMED.
Usage: python -E analysis/X2F_replay.py [--jobs 10]   (writes results/X/X2F/x2f.json, plots)
"""
import argparse
import json
import os
import sys
from multiprocessing import Pool

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import H_replay as H                                     # noqa: E402  (C_T map)
import X2C_profile as P                                  # noqa: E402  (load, constants)
import X2C_replay as C                                   # noqa: E402  (sessions, steps, split, frozen, boot)

OUT = "results/X/X2F"
KAPPAS = np.round(np.arange(1.00, 3.0001, 0.05), 2)
UNSAFE_TOL, UNSAFE_FRAC, MIN_STEPS, FLOOR_C, R_MIN = 1.001, 0.001, 20, 0.05, 0.05
LIMS = ("mm", "cell", "sh")
VARIANTS = {"base": dict(step=0.3, refall=False), "step0.2": dict(step=0.2, refall=False),
            "step0.5": dict(step=0.5, refall=False), "refall": dict(step=0.3, refall=True)}
WIN = 86400


def head(V, Ic, R, vlim):
    return np.maximum(vlim - (V - Ic * R), 0.0) / R


def d1(V, R, k, vlim):
    """Rule D1: margin in its conservative direction (R*k below V_lim, R/k above)."""
    return np.where(V <= vlim, R * k, R / k)


def clean(Rk, Rmm, rp_all):
    Rmm = Rmm if (np.isfinite(Rmm) and Rmm > R_MIN) else rp_all
    return np.where(np.isfinite(Rk) & (Rk > R_MIN), Rk, Rmm), Rmm


def vehicle(args):
    fleet, n, vname = args
    v = VARIANTS[vname]
    qref, vlim = C.FROZEN[fleet]["Q_ref_Ah"], C.FROZEN[fleet]["V_lim_V"] * 1e3
    V, Ic, T, _, valid = P.load(fleet, n)
    Vmv = V * 1e3
    vidx = np.cumsum(valid) - 1
    spos, r, rp = C.steps(Vmv, Ic, T, valid, qref, v["step"])
    sv = vidx[spos]
    rp_all = float(np.median(rp)) if len(rp) else 1.0
    rp_all = rp_all if rp_all > R_MIN else 1.0
    perm = np.random.default_rng(int(n)).permutation(V.shape[1])
    gpar = np.arange(len(sv)) % 2                       # global step parity (refall variant; DEV-1)
    if v["refall"]:
        odd_all = np.flatnonzero(gpar == 1)
        RkF_all = np.median(r[odd_all], 0) if len(odd_all) >= MIN_STEPS else None
    floor = FLOOR_C * qref
    nk = len(KAPPAS)
    rows, n_nohist = [], 0
    for idx in C.sessions(Ic, valid):
        v0 = vidx[idx[0]]
        w = np.flatnonzero((sv < v0) & (sv >= v0 - WIN))
        if v["refall"]:
            E = w[gpar[w] == 0]
            if RkF_all is None or len(E) < MIN_STEPS:
                n_nohist += 1
                continue
            RkF = RkF_all
        else:
            E, F = w[0::2], w[1::2]
            if len(E) < MIN_STEPS or len(F) < MIN_STEPS:
                n_nohist += 1
                continue
            RkF, _ = clean(np.median(r[F], 0), float(np.median(rp[F])), rp_all)
        if v["refall"]:
            RkF, _ = clean(RkF, rp_all, rp_all)
        RkE, RmmE = clean(np.median(r[E], 0), float(np.median(rp[E])), rp_all)
        Vs, Is, Ts = Vmv[idx], Ic[idx], T[idx]
        dah = Is * P.DT_S / 3600.0
        cap = H.c_t(Ts) * qref
        vmax = Vs.max(1)
        Ib = Is[:, None]
        Lref = np.maximum(np.minimum(cap, head(Vs, Ib, RkF[None, :], vlim).min(1)), floor)
        t_ref = float((dah / np.maximum(Lref, 1e-6)).sum())
        t = np.zeros((3, nk))
        uns = np.zeros((3, nk), np.int32)
        notv = np.zeros(nk, np.int32)
        amax = Vs.argmax(1)
        ar = np.arange(len(idx))
        for i, k in enumerate(KAPPAS):
            Lm = np.maximum(np.minimum(cap, head(vmax, Is, d1(vmax, RmmE, k, vlim), vlim)), floor)
            hk = head(Vs, Ib, d1(Vs, RkE[None, :], k, vlim), vlim)
            Lk = np.minimum(cap[:, None], hk)
            Lc = np.maximum(Lk.min(1), floor)
            Ls = np.maximum(np.minimum(cap, head(Vs, Ib, d1(Vs, RkE[perm][None, :], k, vlim), vlim).min(1)), floor)
            for j, L in enumerate((Lm, Lc, Ls)):
                t[j, i] = (dah / np.maximum(L, 1e-6)).sum()
                uns[j, i] = int((L > Lref * UNSAFE_TOL).sum())
            bind = Lk <= (Lk.min(1, keepdims=True) * (1 + 1e-9) + 1e-9)
            notv[i] = int((~bind[ar, amax]).sum())
        rows.append({"n": int(len(idx)), "gap_mv": float(vlim - vmax.max()), "t": t.astype(np.float64),
                     "t_ref": t_ref, "uns": uns, "notv": notv})
    return {"fleet": fleet, "veh": int(n), "variant": vname, "sessions": rows, "n_nohist": n_nohist}


def pick(uns, nfr, tol):
    f = uns / max(nfr, 1)
    ok = np.flatnonzero(f <= tol)
    return (int(ok[0]) if len(ok) else len(KAPPAS) - 1), f


def analyse(R, fleet, vname, tol=UNSAFE_FRAC, depth=50.0, rng=None):
    rng = rng or np.random.default_rng(0)
    cal, ev = set(C.SPLIT[fleet]["calibration"]), set(C.SPLIT[fleet]["evaluation"])
    rs = [x for x in R if x["fleet"] == fleet and x["variant"] == vname]
    sc = [(x["veh"], s) for x in rs if x["veh"] in cal for s in x["sessions"]]
    se = [(x["veh"], s) for x in rs if x["veh"] in ev for s in x["sessions"]]
    nfc, nfe = sum(s["n"] for _, s in sc), sum(s["n"] for _, s in se)
    d = {"n_cal_sessions": len(sc), "n_eval_sessions": len(se),
         "n_excluded_no_history": int(sum(x["n_nohist"] for x in rs))}
    ik = {}
    for j, lim in enumerate(LIMS):
        i, fc = pick(np.sum([s["uns"][j] for _, s in sc], 0), nfc, tol)
        _, fe = pick(np.sum([s["uns"][j] for _, s in se], 0), nfe, tol)
        ik[lim] = i
        d[f"kappa_{lim}"] = float(KAPPAS[i])
        d[f"kappa_{lim}_flagged"] = bool(fc[i] > tol)
        d[f"unsafe_cal_{lim}"] = float(fc[i])
        d[f"unsafe_eval_realised_{lim}"] = float(fe[i])
        d[f"kappa_curve_cal_{lim}"], d[f"kappa_curve_eval_{lim}"] = fc.tolist(), fe.tolist()
    prim = [(vh, s) for vh, s in se if s["gap_mv"] <= depth]
    d["n_primary"], d["n_primary_vehicles"] = len(prim), len({vh for vh, _ in prim})
    if prim:
        tm = np.array([s["t"][0, ik["mm"]] for _, s in prim])
        S = 1 - np.array([s["t"][1, ik["cell"]] for _, s in prim]) / tm
        Ssh = 1 - np.array([s["t"][2, ik["sh"]] for _, s in prim]) / tm
        Sref = 1 - np.array([s["t_ref"] for _, s in prim]) / tm
        D = S - Ssh
        g = np.array([vh for vh, _ in prim])
        gap = np.array([s["gap_mv"] for _, s in prim])
        nfr_p = sum(s["n"] for _, s in prim)
        tm_all = np.array([s["t"][0, ik["mm"]] for _, s in se])
        d.update({"S_median": float(np.median(S)), "S_CI": C.boot(S, g, rng),
                  "S_shuffle_median": float(np.median(Ssh)), "S_shuffle_CI": C.boot(Ssh, g, rng),
                  "D_median": float(np.median(D)), "D_CI": C.boot(D, g, rng),
                  "S_ref_median": float(np.median(Sref)),
                  "S_p10": float(np.percentile(S, 10)), "S_p90": float(np.percentile(S, 90)),
                  "S_median_above_vlim": float(np.median(S[gap < 0])) if (gap < 0).any() else None,
                  "S_median_below_vlim": float(np.median(S[gap >= 0])) if (gap >= 0).any() else None,
                  "S_median_all_eval_history_sessions": float(np.median(
                      1 - np.array([s["t"][1, ik["cell"]] for _, s in se]) / tm_all)),
                  "binding_not_vmax_frac_primary": float(sum(s["notv"][ik["cell"]] for _, s in prim) / max(nfr_p, 1))})
        d["_S"], d["_Ssh"], d["_D"], d["_gap"] = S.tolist(), Ssh.tolist(), D.tolist(), gap.tolist()
    return d


def decide(d):
    if d["n_primary"] < 200:
        return "UNDERPOWERED"
    if any(d[f"unsafe_eval_realised_{l}"] > 0.002 or d[f"kappa_{l}_flagged"] for l in LIMS):
        return "NOT INTERPRETABLE"
    if d["S_median"] < 0.01:
        return "NO BENEFIT"
    if d["S_CI"][0] <= 0:
        return "NOT CONFIRMED (CI)"
    if d["D_median"] >= 0.01 and d["D_CI"][0] > 0:
        return "CONFIRMED"
    return "MECHANISM UNCLEAR"


def plots(res):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    b = res["QAS"]["base"]
    fig, ax = plt.subplots(1, 3, figsize=(15, 4))
    for lim, c in zip(LIMS, ("C0", "C1", "C2")):
        ax[0].plot(KAPPAS, np.array(b[f"kappa_curve_cal_{lim}"]) * 100, "-", c=c, label=f"{lim} cal")
        ax[0].plot(KAPPAS, np.array(b[f"kappa_curve_eval_{lim}"]) * 100, "--", c=c, label=f"{lim} eval")
    ax[0].axhline(0.1, ls=":", c="k"); ax[0].axhline(0.2, ls=":", c="r")
    ax[0].set_yscale("symlog", linthresh=0.01); ax[0].set_xlabel("kappa"); ax[0].set_ylabel("unsafe vs reference (%)")
    ax[0].legend(fontsize=7); ax[0].set_title("kappa curves (QAS)")
    if "_S" in b:
        S, Ssh, D, gap = (np.array(b[k]) * (100 if k != "_gap" else 1) for k in ("_S", "_Ssh", "_D", "_gap"))
        bands = [(-1e9, 0, "above V_lim"), (0, 25, "0-25 mV"), (25, 50.01, "25-50 mV")]
        pos = np.arange(len(bands))
        ax[1].boxplot([S[(gap >= lo) & (gap < hi)] for lo, hi, _ in bands], positions=pos - 0.18, widths=0.3,
                      showfliers=False)
        ax[1].boxplot([Ssh[(gap >= lo) & (gap < hi)] for lo, hi, _ in bands], positions=pos + 0.18, widths=0.3,
                      showfliers=False)
        ax[1].set_xticks(pos); ax[1].set_xticklabels([l for *_, l in bands])
        ax[1].axhline(1, ls=":", c="r"); ax[1].set_ylabel("S (%), left real / right shuffled")
        ax[1].set_title("S by depth band (primary, eval)")
        ax[2].hist(D, bins=60); ax[2].axvline(1, ls=":", c="r")
        ax[2].set_xlabel("D = S - S_shuffle (pp)"); ax[2].set_title(f"paired D (median {np.median(D):.2f} pp)")
    fig.suptitle("X2-F, Beihang QAS normal vehicles (CC BY 4.0). DERIVED; limits ASSUMED; pre-registered re-analysis",
                 fontsize=10)
    fig.tight_layout()
    fig.savefig(f"{OUT}/x2f_plots.png", dpi=110)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=10)
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    jobs = [(f, n, vn) for vn in VARIANTS for f in ("QAS", "DTI") if (f == "QAS" or vn == "base")
            for part in ("calibration", "evaluation") for n in C.SPLIT[f][part]]
    with Pool(a.jobs) as p:
        R = p.map(vehicle, jobs, chunksize=4)
    res = {"tag": "DERIVED; Beihang CC BY 4.0; limits ASSUMED; pre-registered RE-ANALYSIS (data used by X2-C)",
           "preregistered_in": "6cbfeb8", "QAS": {}, "DTI": {}}
    rng = np.random.default_rng(0)
    for vn in VARIANTS:
        res["QAS"][vn] = analyse(R, "QAS", vn, rng=rng)
    res["QAS"]["base"]["verdict"] = decide(res["QAS"]["base"])
    res["QAS"]["depth25"] = analyse(R, "QAS", "base", depth=25.0, rng=rng)
    res["QAS"]["depth100"] = analyse(R, "QAS", "base", depth=100.0, rng=rng)
    res["QAS"]["tol0.01%"] = analyse(R, "QAS", "base", tol=1e-4, rng=rng)
    res["QAS"]["tol1%"] = analyse(R, "QAS", "base", tol=1e-2, rng=rng)
    for vn, x in res["QAS"].items():
        if vn != "base" and x.get("S_median") is not None:
            x["reading_same_rules"] = decide(x)
    res["DTI"]["base"] = analyse(R, "DTI", "base", rng=rng)
    if res["DTI"]["base"].get("S_median") is not None:
        res["DTI"]["base"]["verdict_same_rules"] = decide(res["DTI"]["base"])
    plots(res)
    for f in ("QAS", "DTI"):
        for x in res[f].values():
            for k in [k for k in x if k.startswith("_")]:
                x.pop(k)
    json.dump(res, open(f"{OUT}/x2f.json", "w"), indent=1, default=float)
    short = {f: {vn: {k: x[k] for k in x if not k.startswith("kappa_curve")} for vn, x in res[f].items()}
             for f in ("QAS", "DTI")}
    print(json.dumps(short, indent=1, default=float))


if __name__ == "__main__":
    main()
