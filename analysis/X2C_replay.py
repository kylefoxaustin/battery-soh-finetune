"""Experiment X2-C (pre-registered in results/X/X2C_preregistration.md, commit d27093f, before this script existed):
per-cell-history charge limiter vs equally safe min/max on Beihang QAS normal vehicles; kappa calibrated on the
calibration half, scored on the evaluation half; shuffle / binding-cell / split-half controls. Every number DERIVED,
every limit ASSUMED. CC BY 4.0 (Beihang), MIT (BatICM).
Usage: python -E analysis/X2C_replay.py [--jobs 10]   (writes results/X/X2C/x2c.json, plots)
"""
import argparse
import json
import os
import re
import sys
from multiprocessing import Pool

import numpy as np
from scipy.stats import spearmanr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import H_replay as H                                     # noqa: E402  (C_T map)
import X2C_profile as P                                  # noqa: E402  (load, constants: identical definitions)

OUT = "results/X/X2C"
KAPPAS = np.round(np.arange(1.00, 2.0001, 0.05), 2)
UNSAFE_TOL, UNSAFE_FRAC, MIN_STEPS, FLOOR_C, R_MIN = 1.001, 0.001, 20, 0.05, 0.05
SPLIT = json.load(open(f"{OUT}/split.json"))
FROZEN = json.load(open(f"{OUT}/frozen.json"))
VARIANTS = {"base": dict(win=86400, step=0.3, dv=0.0), "W7": dict(win=20160, step=0.3, dv=0.0),
            "W90": dict(win=259200, step=0.3, dv=0.0), "step0.2": dict(win=86400, step=0.2, dv=0.0),
            "step0.5": dict(win=86400, step=0.5, dv=0.0), "vlim-20": dict(win=86400, step=0.3, dv=-20.0),
            "vlim+20": dict(win=86400, step=0.3, dv=20.0)}


def sessions(Ic, valid):
    ch = valid & (Ic > P.CH_A)
    out, start, miss, last = [], None, 0, None
    for i in range(len(ch) + 1):
        if i < len(ch) and ch[i]:
            start = i if start is None else start
            miss, last = 0, i
        elif start is not None:
            miss += 1
            if miss >= P.SESS_BREAK or i == len(ch):
                idx = np.arange(start, last + 1)
                idx = idx[ch[idx]]
                if Ic[idx].sum() * P.DT_S / 3600.0 >= 0.5:
                    out.append(idx)
                start, miss = None, 0
    return out


def steps(Vmv, Ic, T, valid, qref, c):
    m = valid[:-1] & valid[1:]
    dI = np.diff(Ic)
    st = np.flatnonzero(m & (np.abs(dI) >= c * qref) & (np.abs(np.diff(T)) <= 1.0))
    r = (Vmv[st + 1] - Vmv[st]) / dI[st][:, None]            # mV/A = mOhm, charge-positive
    rp = (Vmv[st + 1].mean(1) - Vmv[st].mean(1)) / dI[st]
    return st + 1, r, rp


def head(V, Ic, R, vlim):
    """Headroom limit per cell (V, R: frames x cells or per frame)."""
    return np.maximum(vlim - (V - Ic * R), 0.0) / R


def vehicle(args):
    fleet, n, vname = args
    v = VARIANTS[vname]
    qref, vlim = FROZEN[fleet]["Q_ref_Ah"], FROZEN[fleet]["V_lim_V"] * 1e3 + v["dv"]
    V, Ic, T, _, valid = P.load(fleet, n)
    Vmv = V * 1e3
    vidx = np.cumsum(valid) - 1
    spos, r, rp = steps(Vmv, Ic, T, valid, qref, v["step"])
    sv = vidx[spos]
    rp_all = float(np.median(rp)) if len(rp) else 1.0
    rp_all = rp_all if rp_all > R_MIN else 1.0
    rng = np.random.default_rng(int(n))
    perm = rng.permutation(V.shape[1])
    floor = FLOOR_C * qref
    nk = len(KAPPAS)
    rows = []
    for idx in sessions(Ic, valid):
        v0 = vidx[idx[0]]
        w = (sv < v0) & (sv >= v0 - v["win"])
        nst = int(w.sum())
        hist = nst >= MIN_STEPS
        Rmm = float(np.median(rp[w])) if nst else rp_all
        Rmm = Rmm if Rmm > R_MIN else rp_all
        Rk = np.median(r[w], 0) if hist else np.full(V.shape[1], Rmm)
        Rk = np.where(np.isfinite(Rk) & (Rk > R_MIN), Rk, Rmm)
        Vs, Is, Ts = Vmv[idx], Ic[idx], T[idx]
        dah = Is * P.DT_S / 3600.0
        cap = H.c_t(Ts) * qref                         # one temperature column: identical for both limiters
        vmax = Vs.max(1)
        if hist:
            hk = head(Vs, Is[:, None], Rk[None, :], vlim)
            Lc = np.maximum(np.minimum(cap, hk.min(1)), floor)
            hks = head(Vs, Is[:, None], Rk[perm][None, :], vlim)
            Ls = np.maximum(np.minimum(cap, hks.min(1)), floor)
            Lk = np.minimum(cap[:, None], hk)
            bind = Lk <= (Lk.min(1, keepdims=True) * (1 + 1e-9) + 1e-9)
            n_notvmax = int((~bind[np.arange(len(idx)), Vs.argmax(1)]).sum())
        S, Ssh, uns, unsh, tmm = (np.zeros(nk) for _ in range(5))
        for i, k in enumerate(KAPPAS):
            R = np.where(vmax <= vlim, Rmm * k, Rmm / k)        # Rule D1
            Lm = np.maximum(np.minimum(cap, head(vmax, Is, R, vlim)), floor)
            if not hist:                                         # Rule D3: per-cell gets min/max's uniform R and kappa
                Lc_k = np.maximum(np.minimum(cap, head(Vs, Is[:, None], R[:, None], vlim).min(1)), floor)
                Ls_k = Lc_k
            else:
                Lc_k, Ls_k = Lc, Ls
            t_m = float((dah / np.maximum(Lm, 1e-6)).sum())
            S[i] = 1 - float((dah / np.maximum(Lc_k, 1e-6)).sum()) / t_m
            Ssh[i] = 1 - float((dah / np.maximum(Ls_k, 1e-6)).sum()) / t_m
            uns[i] = int((Lm > Lc_k * UNSAFE_TOL).sum())
            unsh[i] = int((Ls_k > Lc_k * UNSAFE_TOL).sum())
        rows.append({"hist": hist, "nsteps": nst, "gap_mv": float(vlim - vmax.max()), "n": int(len(idx)),
                     "S": S.astype(np.float32), "Ssh": Ssh.astype(np.float32), "uns": uns.astype(np.int32),
                     "unsh": unsh.astype(np.int32), "n_notvmax": n_notvmax if hist else 0})
    out = {"fleet": fleet, "veh": int(n), "variant": vname, "sessions": rows}
    if vname == "base" and len(r) >= 40:                 # split-half stability (all steps)
        a, b = np.median(r[0::2], 0), np.median(r[1::2], 0)
        out["split_rho"] = float(spearmanr(a, b).correlation)
        out["split_same_worst"] = bool(np.argmax(a) == np.argmax(b))
        out["worst_over_median"] = float(np.max(np.median(r, 0)) / np.median(np.median(r, 0)))
    return out


def pick(uns, nfr, tol):
    f = uns / max(nfr, 1)
    ok = np.flatnonzero(f <= tol)
    i = int(ok[0]) if len(ok) else len(KAPPAS) - 1
    return i, f


def boot(vals, groups, rng, n=1000):
    ug = np.unique(groups)
    ix = {g: np.flatnonzero(groups == g) for g in ug}
    out = [np.median(vals[np.concatenate([ix[g] for g in rng.choice(ug, len(ug))])]) for _ in range(n)]
    return [float(np.percentile(out, 2.5)), float(np.percentile(out, 97.5))]


def analyse(R, fleet, vname, tol=UNSAFE_FRAC, depth=50.0, rng=None):
    rng = rng or np.random.default_rng(0)
    cal, ev = set(SPLIT[fleet]["calibration"]), set(SPLIT[fleet]["evaluation"])
    rs = [x for x in R if x["fleet"] == fleet and x["variant"] == vname]

    def flat(ids):
        ss = [(x["veh"], s) for x in rs if x["veh"] in ids for s in x["sessions"]]
        return ss
    sc, se = flat(cal), flat(ev)
    nfc, nfe = sum(s["n"] for _, s in sc), sum(s["n"] for _, s in se)
    uc = np.sum([s["uns"] for _, s in sc], 0)
    ue = np.sum([s["uns"] for _, s in se], 0)
    ik, fc = pick(uc, nfc, tol)
    ike, fe = pick(ue, nfe, tol)
    prim = [(vh, s) for vh, s in se if s["hist"] and s["gap_mv"] <= depth]
    d = {"kappa_cal": float(KAPPAS[ik]), "kappa_cal_capped": bool(fc[ik] > tol), "unsafe_cal": float(fc[ik]),
         "unsafe_eval_realised": float(fe[ik]), "kappa_eval_comparison": float(KAPPAS[ike]),
         "kappa_curve_cal": fc.tolist(), "kappa_curve_eval": fe.tolist(),
         "n_primary": len(prim), "n_primary_vehicles": len({vh for vh, _ in prim}),
         "n_eval_sessions": len(se)}
    if prim:
        S = np.array([s["S"][ik] for _, s in prim])
        Ssh = np.array([s["Ssh"][ik] for _, s in prim])
        g = np.array([vh for vh, _ in prim])
        nfr_p = sum(s["n"] for _, s in prim)
        d.update({"S_median": float(np.median(S)), "S_CI": boot(S, g, rng), "S_p10": float(np.percentile(S, 10)),
                  "S_p90": float(np.percentile(S, 90)), "S_mean": float(S.mean()),
                  "S_shuffle_median": float(np.median(Ssh)), "S_shuffle_CI": boot(Ssh, g, rng),
                  "unsafe_eval_primary": float(sum(s["uns"][ik] for _, s in prim) / max(nfr_p, 1)),
                  "shuffle_unsafe_vs_true_primary": float(sum(s["unsh"][ik] for _, s in prim) / max(nfr_p, 1)),
                  "binding_not_vmax_frac_primary": float(sum(s["n_notvmax"] for _, s in prim) / max(nfr_p, 1)),
                  "S_median_above_vlim": float(np.median([s["S"][ik] for _, s in prim if s["gap_mv"] < 0]))
                  if any(s["gap_mv"] < 0 for _, s in prim) else None,
                  "S_median_below_vlim": float(np.median([s["S"][ik] for _, s in prim if s["gap_mv"] >= 0]))
                  if any(s["gap_mv"] >= 0 for _, s in prim) else None,
                  "S_median_all_eval_sessions": float(np.median([s["S"][ik] for _, s in se]))})
        d["_S"], d["_Ssh"], d["_gap"] = S.tolist(), Ssh.tolist(), [s["gap_mv"] for _, s in prim]
    return d


def decide(d):
    if d["n_primary"] < 200:
        return "UNDERPOWERED"
    if d["unsafe_eval_realised"] > 0.002:
        return "NOT INTERPRETABLE"
    if d["S_median"] < 0.01:
        return "NOT CONFIRMED"
    if d["S_shuffle_median"] >= 0.01:
        return "MECHANISM UNCLEAR"
    if d["S_CI"][0] > 0:
        return "CONFIRMED"
    return "NOT CONFIRMED (CI)"


def baticm():
    import pandas as pd
    out = {}
    for car, q in ((1, 50.0), (4, 50.0)):              # ASSUMED 50 Ah (X3 DEV-1)
        d = pd.read_csv(f"data/raw/baticm/car{car}/car{car}_processed.csv")
        vc = sorted([c for c in d.columns if re.fullmatch(r"V_\d+", c)], key=lambda c: int(c[2:]))
        ok = d[vc].notna().all(1) & d["BMSBatteryCurrent"].notna()
        V = d.loc[ok, vc].to_numpy(float) * (1e3 if d[vc].stack().median() < 10 else 1.0)
        Ic = -d.loc[ok, "BMSBatteryCurrent"].to_numpy(float)
        res = {}
        for lab, stride in (("native", 1), ("decim30", 30)) if car == 1 else (("native", 1),):
            Vs, Is = V[::stride], Ic[::stride]
            dI = np.diff(Is)
            st = np.flatnonzero(np.abs(dI) >= 0.3 * q)
            r = (Vs[st + 1] - Vs[st]) / dI[st][:, None]
            if len(r) < 40:
                res[lab] = {"n_steps": int(len(r))}
                continue
            m = np.median(r, 0)
            a, b = np.median(r[0::2], 0), np.median(r[1::2], 0)
            res[lab] = {"n_steps": int(len(r)), "R_median_mohm": float(np.median(m)), "_Rk": m,
                        "split_rho": float(spearmanr(a, b).correlation), "split_same_worst": bool(np.argmax(a) == np.argmax(b))}
        if "decim30" in res and "_Rk" in res["decim30"] and "_Rk" in res["native"]:
            res["rho_native_vs_decim30"] = float(spearmanr(res["native"]["_Rk"], res["decim30"]["_Rk"]).correlation)
            res["same_worst_native_vs_decim30"] = bool(np.argmax(res["native"]["_Rk"]) == np.argmax(res["decim30"]["_Rk"]))
        for x in res.values():
            if isinstance(x, dict):
                x.pop("_Rk", None)
        out[f"car{car}"] = res
    return out


def plots(res):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    b = res["QAS"]["base"]
    fig, ax = plt.subplots(1, 3, figsize=(15, 4))
    ax[0].plot(KAPPAS, np.array(b["kappa_curve_cal"]) * 100, "o-", ms=3, label="calibration half")
    ax[0].plot(KAPPAS, np.array(b["kappa_curve_eval"]) * 100, "s-", ms=3, label="evaluation half")
    ax[0].axhline(0.1, ls=":", c="k"); ax[0].axhline(0.2, ls=":", c="r")
    ax[0].axvline(b["kappa_cal"], ls="--", c="k")
    ax[0].set_yscale("symlog", linthresh=0.01); ax[0].set_xlabel("kappa_mm"); ax[0].set_ylabel("min/max unsafe frames (%)")
    ax[0].legend(); ax[0].set_title("kappa curve (QAS)")
    S, Ssh, gap = np.array(b["_S"]) * 100, np.array(b["_Ssh"]) * 100, np.array(b["_gap"])
    bands = [(-1e9, 0, "above V_lim"), (0, 25, "0-25 mV"), (25, 50.01, "25-50 mV")]
    ax[1].boxplot([S[(gap >= lo) & (gap < hi)] for lo, hi, _ in bands], labels=[l for *_, l in bands], showfliers=False)
    ax[1].axhline(1, ls=":", c="r"); ax[1].set_ylabel("S (%)"); ax[1].set_title("S by charge-depth band (primary, eval)")
    ax[2].hist(S, bins=60, alpha=0.6, label=f"real (median {np.median(S):.2f} %)")
    ax[2].hist(Ssh, bins=60, alpha=0.6, label=f"shuffled R (median {np.median(Ssh):.2f} %)")
    ax[2].axvline(1, ls=":", c="r"); ax[2].set_xlabel("S (%)"); ax[2].legend(); ax[2].set_title("shuffle control")
    fig.suptitle("X2-C, Beihang QAS normal vehicles (CC BY 4.0). DERIVED; limits ASSUMED", fontsize=10)
    fig.tight_layout()
    fig.savefig(f"{OUT}/x2c_plots.png", dpi=110)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=10)
    a = ap.parse_args()
    jobs = [(f, n, vn) for vn in VARIANTS for f in ("QAS", "DTI") if (f == "QAS" or vn == "base")
            for part in ("calibration", "evaluation") for n in SPLIT[f][part]]
    with Pool(a.jobs) as p:
        R = p.map(vehicle, jobs, chunksize=4)
    res = {"tag": "DERIVED; Beihang CC BY 4.0; limits ASSUMED (frozen in X2C/frozen.json)", "preregistered_in": "d27093f",
           "QAS": {}, "DTI": {}}
    rng = np.random.default_rng(0)
    for vn in VARIANTS:
        res["QAS"][vn] = analyse(R, "QAS", vn, rng=rng)
    b = res["QAS"]["base"]
    b["verdict"] = decide(b)
    res["QAS"]["depth25"] = analyse(R, "QAS", "base", depth=25.0, rng=rng)
    res["QAS"]["depth100"] = analyse(R, "QAS", "base", depth=100.0, rng=rng)
    res["QAS"]["tol0.01%"] = analyse(R, "QAS", "base", tol=1e-4, rng=rng)
    res["QAS"]["tol1%"] = analyse(R, "QAS", "base", tol=1e-2, rng=rng)
    res["DTI"]["base"] = analyse(R, "DTI", "base", rng=rng)
    res["DTI"]["base"]["verdict_same_rules"] = decide(res["DTI"]["base"]) if res["DTI"]["base"].get("S_median") is not None else None
    for f in ("QAS", "DTI"):
        sh = [x for x in R if x["fleet"] == f and x["variant"] == "base" and "split_rho" in x]
        res[f]["split_half"] = {"n_vehicles": len(sh), "rho_median": float(np.median([x["split_rho"] for x in sh])),
                                "rho_p10": float(np.percentile([x["split_rho"] for x in sh], 10)),
                                "same_worst_frac": float(np.mean([x["split_same_worst"] for x in sh])),
                                "worst_over_median_median": float(np.median([x["worst_over_median"] for x in sh]))}
    res["BatICM_sampling"] = baticm()
    plots(res)
    for f in res:
        if isinstance(res[f], dict):
            for v in res[f].values():
                if isinstance(v, dict):
                    for k in [k for k in v if k.startswith("_")]:
                        v.pop(k)
    json.dump(res, open(f"{OUT}/x2c.json", "w"), indent=1, default=float)
    print(json.dumps(res, indent=1, default=float)[:6000])


if __name__ == "__main__":
    main()
