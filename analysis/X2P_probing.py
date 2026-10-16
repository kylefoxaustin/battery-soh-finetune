"""Experiment X2-P (pre-registered in results/X/X2P_preregistration.md, commit ea9f714, before this script existed):
active probing as a precision + coverage curve for per-cell R on Changan. Natural current steps stand in for injected
ones. Every number DERIVED; safety envelope ASSUMED. CC BY-NC-SA 4.0 (non-commercial).
Usage: python -E analysis/X2P_probing.py [--jobs 10]   (writes results/X/X2P/x2p.json)
"""
import argparse
import json
import os
import sys
from multiprocessing import Pool

import numpy as np
from scipy.stats import spearmanr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import H_replay as H                                   # noqa: E402
import X2_replay as X                                  # noqa: E402

OUT = "results/X/X2P"
Q = X.QREF_C
BINS = {"a1": (0.05, 0.10), "a2": (0.10, 0.20), "a3": (0.20, 0.30), "a4": (0.30, np.inf)}   # x Q_ref (prereg §1)
NS = [1, 2, 5, 10, 20, 40, 80]
N_DRAW, MIN_REF, MIN_VEH = 50, 40, 30
RHO_T, HIT_T, COV_T = 0.90, 0.80, 0.90
MS = [0, 1, 2, 5, 10]
WINS = {"7d": 7 * 86400.0, "30d": 30 * 86400.0}
ENV_DV, ENV_TLO, ENV_THI = 50.0, 10.0, 45.0            # §4 envelope (ASSUMED): Vmax <= VLIM - 50 mV, probes 10-45 C


def steps(car):
    """All steps |dI| >= 0.05 C (X2 step definition otherwise): time, |dI|/Q, per-cell r (mOhm)."""
    Z = np.load(f"{H.CELLS}/vin{car}.npz")
    t, I, tf = Z["t"], Z["I"].astype(np.float64), Z["t_full"]
    j = np.clip(np.searchsorted(t, tf), 0, len(t) - 1)
    ok = t[j] == tf
    vm = Z["vmean_mv"][j].astype(np.float64)
    V = vm[:, None] + Z["dv_full"].astype(np.float64)
    Ic = np.nan_to_num(-I[j])
    tm = Z["tmean"][j].astype(np.float64)
    dI = np.diff(Ic)
    st = (np.diff(tf) <= X.STEP_DT_S) & ok[1:] & ok[:-1] & (np.abs(dI) >= 0.05 * Q) & (np.abs(np.diff(tm)) <= 1.0) \
        & np.isfinite(V[1:]).all(1) & np.isfinite(V[:-1]).all(1)
    k = np.flatnonzero(st)
    return tf[k + 1], np.abs(dI[k]) / Q, (V[k + 1] - V[k]) / dI[k][:, None]


def precision(car):
    t, a, r = steps(car)
    idx = np.arange(len(t))
    ref_m = (idx % 2 == 0) & (a >= 0.30)
    if ref_m.sum() < MIN_REF:
        return None
    ref = np.median(r[ref_m], 0)
    top3 = set(np.argsort(ref)[-3:].tolist())
    rr = ref.max() / np.median(ref)
    rng = np.random.default_rng(car)                   # seed per vehicle (0-based family; reproducible)
    out = {"car": car, "n_ref": int(ref_m.sum())}
    for b, (lo, hi) in BINS.items():
        pool = np.flatnonzero((idx % 2 == 1) & (a >= lo) & (a < hi))
        out[f"n_pool_{b}"] = int(len(pool))
        for n in NS:
            if len(pool) < n:
                continue
            rho, hit, rerr = [], [], []
            for _ in range(N_DRAW):
                p = np.median(r[rng.choice(pool, n, replace=False)], 0)
                rho.append(spearmanr(p, ref).correlation)
                hit.append(int(np.argmax(p) in top3))
                rerr.append(abs((p.max() / np.median(p)) / rr - 1))
            # per vehicle: median over draws (prereg §2; for binary hit3 this is the majority value), plus hit3 mean
            out[f"{b}_{n}"] = (float(np.nanmedian(rho)), float(np.median(hit)), float(np.median(rerr)),
                               float(np.mean(hit)))
    return out


def coverage_inputs(car):
    S = [f for f in X.changan_sessions(car) if f["dah"].sum() > 0.5]
    if not S:
        return None
    t, a, _ = steps(car)
    t0 = np.array([f["t0"] for f in S])
    cold = np.array([np.median(f["T"].min(1)) < 10 for f in S])
    env = np.array([int(((f["Ic"] > 0) & (f["V"].max(1) <= X.VLIM - ENV_DV) & (f["T"].min(1) >= ENV_TLO)
                         & (f["T"].max(1) <= ENV_THI)).sum()) for f in S])
    # natural steps of amplitude >= lo in the trailing window, per session
    nat = {}
    for b, (lo, _) in BINS.items():
        ts = np.sort(t[a >= lo])
        for w, ws in WINS.items():
            nat[(b, w)] = np.searchsorted(ts, t0, "left") - np.searchsorted(ts, t0 - ws, "left")
    prior = {w: np.searchsorted(t0, t0, "left") - np.searchsorted(t0, t0 - ws, "left") for w, ws in WINS.items()}
    return {"car": car, "t0": t0, "cold": cold, "env": env, "nat": nat, "prior_sess": prior}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=10)
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    cars = sorted(int(f[3:-4]) for f in os.listdir(H.CELLS) if f.startswith("vin") and f[3:-4].isdigit())
    with Pool(a.jobs) as p:
        P = [x for x in p.map(precision, cars) if x]
    res = {"tag": "DERIVED (Changan natural steps as stand-ins for injected ones; envelope ASSUMED); CC BY-NC-SA 4.0",
           "preregistered_in": "ea9f714", "n_vehicles_with_reference": len(P), "precision": {}, "n_star": {}}
    for b in BINS:
        res["precision"][b] = {}
        nstar = None
        for n in NS:
            v = [x[f"{b}_{n}"] for x in P if f"{b}_{n}" in x]
            if not v:
                res["precision"][b][n] = {"n_vehicles": 0}
                continue
            v = np.array(v)
            d = {"n_vehicles": len(v), "rho_med": float(np.median(v[:, 0])), "rho_p10": float(np.percentile(v[:, 0], 10)),
                 "rho_p90": float(np.percentile(v[:, 0], 90)), "hit3_med": float(np.median(v[:, 1])),
                 "hit3_rate_mean": float(np.mean(v[:, 3])), "ratio_err_med": float(np.median(v[:, 2]))}
            res["precision"][b][n] = d
            if nstar is None and len(v) >= MIN_VEH and d["rho_med"] >= RHO_T and d["hit3_med"] >= HIT_T:
                nstar = n
        res["n_star"][b] = nstar if nstar is not None else "> 80"
        res["precision"][b]["pool_size_median"] = float(np.median([x[f"n_pool_{b}"] for x in P]))
    print(json.dumps(res["n_star"]), flush=True)
    with Pool(a.jobs) as p:
        C = [x for x in p.map(coverage_inputs, cars) if x]
    cold = np.concatenate([c["cold"] for c in C])
    env = np.concatenate([c["env"] for c in C])
    res["n_sessions"], res["n_cold_sessions"] = int(len(cold)), int(cold.sum())
    res["envelope_feasible_frac"] = {m: float((env >= m).mean()) for m in MS if m}
    cov = {}
    for b in BINS:
        ns = res["n_star"][b]
        if not isinstance(ns, int):
            continue
        for w in WINS:
            nat = np.concatenate([c["nat"][(b, w)] for c in C])
            for m in MS:
                inj_u = np.concatenate([c["prior_sess"][w] for c in C]) * m
                # constrained: injected steps only from prior sessions in the window that can host m envelope frames
                inj_c = []
                for c in C:
                    okm = (c["env"] >= m) if m else np.ones(len(c["t0"]), bool)
                    ts = c["t0"][okm]
                    inj_c.append((np.searchsorted(ts, c["t0"], "left") - np.searchsorted(ts, c["t0"] - WINS[w], "left")) * m)
                inj_c = np.concatenate(inj_c)
                for lab, inj in (("unconstrained", inj_u), ("envelope", inj_c)):
                    hit = (nat + inj) >= ns
                    cov[f"{b}|{w}|m{m}|{lab}"] = {"all": float(hit.mean()), "cold": float(hit[cold].mean())}
    res["coverage"] = cov
    res["smallest_m_cov90_7d_envelope"] = {
        b: next((m for m in MS if cov.get(f"{b}|7d|m{m}|envelope", {}).get("all", 0) >= COV_T), None)
        for b in BINS if isinstance(res["n_star"][b], int)}
    json.dump(res, open(f"{OUT}/x2p.json", "w"), indent=1, default=str)
    print(json.dumps({k: v for k, v in res.items() if k not in ("precision", "coverage")}, indent=1, default=str))


if __name__ == "__main__":
    main()
