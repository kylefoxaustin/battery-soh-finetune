"""Experiment X2-S (pre-registered in results/X/X2S_preregistration.md, commit dcd07e8, before this script existed):
X2-F replicated on Schaeffer et al. 28 LFP systems (CC BY-NC 4.0). Limiters exactly X2-F §3; kappa on a 0.01 grid at
0.01 % tolerance; two-fold cross-fitting (calibrate on one half, score the other, both ways); system-weighted
statistics. Every number DERIVED, limits ASSUMED, Q_ref SOURCED.
Usage: python -E analysis/XS_replay.py [--jobs 10]   (writes results/X/XS/x2s.json, plots)
"""
import argparse
import json
import os
import sys
from multiprocessing import Pool

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import H_replay as H                                     # noqa: E402  (C_T map)
import XS_common as X                                    # noqa: E402
from X2F_replay import head, d1, clean                   # noqa: E402  (X2-F limiter primitives, unchanged)

OUT = X.OUT
KAPPAS = np.round(np.arange(1.00, 2.0001, 0.01), 2)
UNSAFE_TOL, TOL, MIN_STEPS, FLOOR_C, R_MIN = 1.001, 1e-4, 20, 0.05, 0.05
VMAX_CAP = 3650.0
LIMS = ("mm", "cell", "sh")
SPLIT = json.load(open(f"{OUT}/split.json"))
FROZEN = json.load(open(f"{OUT}/frozen.json"))
VARIANTS = {"base": dict(win=30, step=0.3, bal=False), "W7": dict(win=7, step=0.3, bal=False),
            "bal": dict(win=30, step=0.3, bal=True), "step0.2": dict(win=30, step=0.2, bal=False),
            "DEV1_dirbal": dict(win=30, step=0.3, bal=False, dirbal=True)}
# DEV-1 (after dcd07e8, found in the smoke test on system 14): loads switch on and off in pairs, so plain even/odd
# parity puts mostly up-steps in one set and down-steps in the other, and up/down R differ ~2-3x here. DEV1_dirbal
# applies the parity split separately within up-steps and within down-steps. Reported beside, never instead of, base.


def system(args):
    sysid, vname = args
    v = VARIANTS[vname]
    vlim, qref = FROZEN["V_lim_mV"], X.Q_REF
    t, Ic, V, T, bal, valid = X.load(sysid)
    st, r, rp, sg = X.steps(t, Ic, V, T, bal, valid, v["step"], allow_bal=v["bal"], with_sign=True)
    rp_all = float(np.median(rp)) if len(rp) else 1.0
    rp_all = rp_all if rp_all > R_MIN else 1.0
    perm = np.random.default_rng(int(sysid)).permutation(V.shape[1])
    floor = FLOOR_C * qref
    nk = len(KAPPAS)
    rows, n_nohist, n_over = [], 0, 0
    for s, dah in X.sessions(t, Ic, valid):
        Vs = V[s]
        vmax = Vs.max(1)
        if vmax.max() > VMAX_CAP:
            n_over += 1
            continue
        t0 = t[s[0]]
        w = np.flatnonzero((st < t0) & (st >= t0 - v["win"] * 86400.0))
        if v.get("dirbal"):
            up, dn = w[sg[w] > 0], w[sg[w] < 0]
            E, F = np.sort(np.r_[up[0::2], dn[0::2]]), np.sort(np.r_[up[1::2], dn[1::2]])
        else:
            E, F = w[0::2], w[1::2]
        if len(E) < MIN_STEPS or len(F) < MIN_STEPS:
            n_nohist += 1
            continue
        RkF, _ = clean(np.median(r[F], 0), float(np.median(rp[F])), rp_all)
        RkE, RmmE = clean(np.median(r[E], 0), float(np.median(rp[E])), rp_all)
        Is, Ts = Ic[s], T[s]
        Ib = Is[:, None]
        cap = H.c_t(Ts) * qref
        Lref = np.maximum(np.minimum(cap, head(Vs, Ib, RkF[None, :], vlim).min(1)), floor)
        tt = np.zeros((3, nk))
        uns = np.zeros((3, nk), np.int32)
        notv = np.zeros(nk, np.int32)
        amax = Vs.argmax(1)
        ar = np.arange(len(s))
        RkEp = RkE[perm]
        for i, k in enumerate(KAPPAS):
            Lm = np.maximum(np.minimum(cap, head(vmax, Is, d1(vmax, RmmE, k, vlim), vlim)), floor)
            Lk = np.minimum(cap[:, None], head(Vs, Ib, d1(Vs, RkE[None, :], k, vlim), vlim))
            Lc = np.maximum(Lk.min(1), floor)
            Ls = np.maximum(np.minimum(cap, head(Vs, Ib, d1(Vs, RkEp[None, :], k, vlim), vlim).min(1)), floor)
            for j, L in enumerate((Lm, Lc, Ls)):
                tt[j, i] = (dah / np.maximum(L, 1e-6)).sum()
                uns[j, i] = int((L > Lref * UNSAFE_TOL).sum())
            bind = Lk <= (Lk.min(1, keepdims=True) * (1 + 1e-9) + 1e-9)
            notv[i] = int((~bind[ar, amax]).sum())
        rows.append({"n": int(len(s)), "gap_mv": float(vlim - vmax.max()), "t": tt,
                     "t_ref": float((dah / np.maximum(Lref, 1e-6)).sum()), "uns": uns, "notv": notv})
    return {"sys": int(sysid), "variant": vname, "sessions": rows, "n_nohist": n_nohist, "n_over": n_over}


def pick(uns, nfr, tol):
    f = uns / max(nfr, 1)
    ok = np.flatnonzero(f <= tol)
    return (int(ok[0]) if len(ok) else len(KAPPAS) - 1), f


def calibrate(R, ids, vname, tol):
    ss = [s for x in R if x["variant"] == vname and x["sys"] in ids for s in x["sessions"]]
    nf = sum(s["n"] for s in ss)
    out = {}
    for j, lim in enumerate(LIMS):
        i, f = pick(np.sum([s["uns"][j] for s in ss], 0), nf, tol)
        out[lim] = (i, f)
    return out, nf


def boot_sys(sys_meds, rng, n=2000):
    a = np.array(sys_meds)
    m = [np.median(a[rng.integers(0, len(a), len(a))]) for _ in range(n)]
    return [float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))]


def analyse(R, vname, tol=TOL, depth=50.0, rng=None):
    rng = rng or np.random.default_rng(0)
    A, B = set(SPLIT["calibration"]), set(SPLIT["evaluation"])
    res = {"folds": {}}
    per_sys, pooled = {}, {"S": [], "Ssh": [], "D": [], "Sref": []}
    nf_p = notv_p = 0
    interp_fail = []
    for fold, cal, sc in (("1_calA_scoreB", A, B), ("2_calB_scoreA", B, A)):
        ck, _ = calibrate(R, cal, vname, tol)
        ss = [s for x in R if x["variant"] == vname and x["sys"] in sc for s in x["sessions"]]
        nfe = sum(s["n"] for s in ss)
        fd = {}
        for j, lim in enumerate(LIMS):
            i, fc = ck[lim]
            ue = float(np.sum([s["uns"][j][i] for s in ss]) / max(nfe, 1))
            fd[f"kappa_{lim}"] = float(KAPPAS[i])
            fd[f"kappa_{lim}_flagged"] = bool(fc[i] > tol)
            fd[f"unsafe_cal_{lim}"] = float(fc[i])
            fd[f"unsafe_heldout_{lim}"] = ue
            if ue > 0.002 or fc[i] > tol:
                interp_fail.append(f"{fold}:{lim}")
        ik = {lim: ck[lim][0] for lim in LIMS}
        nprim = 0
        for x in R:
            if x["variant"] != vname or x["sys"] not in sc:
                continue
            prim = [s for s in x["sessions"] if s["gap_mv"] <= depth]
            nprim += len(prim)
            if not prim:
                continue
            tm = np.array([s["t"][0, ik["mm"]] for s in prim])
            S = 1 - np.array([s["t"][1, ik["cell"]] for s in prim]) / tm
            Ssh = 1 - np.array([s["t"][2, ik["sh"]] for s in prim]) / tm
            Sref = 1 - np.array([s["t_ref"] for s in prim]) / tm
            for k, a in (("S", S), ("Ssh", Ssh), ("D", S - Ssh), ("Sref", Sref)):
                pooled[k].extend(a.tolist())
            nf_p += sum(s["n"] for s in prim)
            notv_p += sum(int(s["notv"][ik["cell"]]) for s in prim)
            per_sys[x["sys"]] = {"fold": fold, "n_primary": len(prim), "S_median": float(np.median(S)),
                                 "S_shuffle_median": float(np.median(Ssh)), "D_median": float(np.median(S - Ssh)),
                                 "S_ref_median": float(np.median(Sref))}
        fd["n_primary"] = nprim
        res["folds"][fold] = fd
    q = {s: v for s, v in per_sys.items() if v["n_primary"] >= 20}
    res["per_system"] = per_sys
    res["qualifying_systems"] = sorted(q)
    res["n_primary_total"] = len(pooled["S"])
    res["interpretability_failures"] = interp_fail
    if q:
        Sm = [v["S_median"] for v in q.values()]
        Dm = [v["D_median"] for v in q.values()]
        res.update({"S_sys": float(np.median(Sm)), "S_sys_CI": boot_sys(Sm, rng),
                    "S_sh_sys": float(np.median([v["S_shuffle_median"] for v in q.values()])),
                    "D_sys": float(np.median(Dm)), "D_sys_CI": boot_sys(Dm, rng),
                    "D_positive_systems": int(sum(d > 0 for d in Dm)), "n_qualifying": len(q),
                    "S_sys_leave_one_out": {int(s): float(np.median([v["S_median"] for k, v in q.items() if k != s]))
                                            for s in q} if len(q) > 1 else None})
    if pooled["S"]:
        res.update({f"pooled_{k}_median": float(np.median(v)) for k, v in pooled.items()})
        res["binding_not_vmax_frac_primary"] = float(notv_p / max(nf_p, 1))
    res["n_excluded_no_history"] = int(sum(x["n_nohist"] for x in R if x["variant"] == vname))
    res["n_excluded_over_3650"] = int(sum(x["n_over"] for x in R if x["variant"] == vname))
    res["_pooled"] = pooled
    return res


def decide(d):
    if d.get("n_qualifying", 0) < 6 or d["n_primary_total"] < 200:
        return "UNDERPOWERED"
    if d["interpretability_failures"]:
        return "NOT INTERPRETABLE"
    if d["S_sys"] < 0.01:
        return "NO BENEFIT"
    if d["S_sys_CI"][0] <= 0:
        return "NOT CONFIRMED (CI)"
    if d["D_sys"] >= 0.01 and d["D_sys_CI"][0] > 0 and d["D_positive_systems"] >= 0.75 * d["n_qualifying"]:
        return "REPLICATED"
    return "MECHANISM UNCLEAR"


def plots(res):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    b = res["base"]
    fig, ax = plt.subplots(1, 2, figsize=(12, 4))
    ps = sorted(b["per_system"].items(), key=lambda kv: -kv[1]["n_primary"])
    lab = [f"{s}\n(n={v['n_primary']})" for s, v in ps]
    x = np.arange(len(ps))
    ax[0].bar(x - 0.2, [v["S_median"] * 100 for _, v in ps], 0.4, label="S (real)")
    ax[0].bar(x + 0.2, [v["S_shuffle_median"] * 100 for _, v in ps], 0.4, label="S_sh (shuffled)")
    ax[0].axhline(1, ls=":", c="r"); ax[0].axhline(0, c="k", lw=0.5)
    ax[0].set_xticks(x); ax[0].set_xticklabels(lab, fontsize=7); ax[0].set_ylabel("median S (%)")
    ax[0].legend(); ax[0].set_title("per system (scored by the other half's kappa)")
    ax[1].hist(np.array(b["_pooled"]["D"]) * 100, bins=60); ax[1].axvline(1, ls=":", c="r")
    ax[1].set_xlabel("D = S - S_sh (pp), pooled sessions"); ax[1].set_title("paired D")
    fig.suptitle("X2-S, Schaeffer 28 LFP systems (CC BY-NC 4.0). DERIVED; limits ASSUMED", fontsize=10)
    fig.tight_layout()
    fig.savefig(f"{OUT}/x2s_plots.png", dpi=110)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=10)
    a = ap.parse_args()
    sizes = {s: os.path.getsize(f"{X.SRC}/data_sys_{s}.csv") for s in SPLIT["calibration"] + SPLIT["evaluation"]}
    jobs = sorted([(s, vn) for vn in VARIANTS for s in sizes], key=lambda j: -sizes[j[0]])
    with Pool(a.jobs) as p:
        R = p.map(system, jobs, chunksize=1)
    rng = np.random.default_rng(0)
    res = {"tag": "DERIVED; Schaeffer et al. CC BY-NC 4.0; limits ASSUMED; Q_ref SOURCED", "preregistered_in": "dcd07e8"}
    for vn in VARIANTS:
        res[vn] = analyse(R, vn, rng=rng)
    res["base"]["verdict"] = decide(res["base"])
    res["tol0.1%"] = analyse(R, "base", tol=1e-3, rng=rng)
    res["depth25"] = analyse(R, "base", depth=25.0, rng=rng)
    res["depth100"] = analyse(R, "base", depth=100.0, rng=rng)
    for k, x in res.items():
        if isinstance(x, dict) and k != "base" and "n_primary_total" in x:
            x["reading_same_rules"] = decide(x)
    plots(res)
    for x in res.values():
        if isinstance(x, dict):
            x.pop("_pooled", None)
    json.dump(res, open(f"{OUT}/x2s.json", "w"), indent=1, default=float)
    print(json.dumps(res, indent=1, default=float)[:12000])


if __name__ == "__main__":
    main()
