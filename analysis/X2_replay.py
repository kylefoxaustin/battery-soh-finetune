"""Experiment X2 / H3 (pre-registered in results/X/X2_preregistration.md, commit 0c4580a, before this script existed).
Per-cell charge-direction limiting with per-cell resistance (primary) and capacity (secondary) estimated causally
from each cell's own history, vs a min/max limiter given the same history as pack scalars and calibrated to be
equally safe (kappa_mm). Every number DERIVED; every limit ASSUMED.
Arms: X2-C (Changan, cold sessions = primary; all sessions), X2-M (McMaster 72S), X2-B (BATSS fast charge, report).
Usage: python analysis/X2_replay.py --arm changan|mcmaster|batss|all --out results/X/X2 [--jobs 10]
Open implementation choices the pre-registration left are marked OPEN-n; disclosed in results_X2.md.
"""
import argparse
import glob
import json
import os
import sys
from multiprocessing import Pool

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import H_replay as H                                   # noqa: E402  (C_T map, OCV table, M1/M2 probe maps)

KAPPAS = np.round(np.arange(1.00, 2.0001, 0.05), 2)
UNSAFE_TOL, UNSAFE_FRAC = 1.001, 0.001                 # H's unsafe-frame criterion
MIN_STEPS = 20
R_DEFAULT_MOHM = 0.5                                   # OPEN-2: used only when a window holds zero steps (no history)
STEP_DT_S = 30.0                                       # OPEN-1: "consecutive frames" = consecutive full frames <= 30 s apart
SPREAD_BANDS = [(0, 5), (5, 10), (10, 20), (20, 1e9)]


# ---------------------------------------------------------------- limiter core (V in mV, R in mOhm, I in A)
FLOOR_C = 0.05     # DEV-2: both limiters floored at 0.05 C (H's taper floor); without it any frame whose open-circuit
                   # estimate is at/above VLIM gives L = 0 and dominates the time sum (27 % of Changan charge frames
                   # have measured Vmax > 4.20 V)


def head_k(V, Ic, R):
    return np.maximum(VLIM - (V - Ic[:, None] * R[None, :]), 0.0) / R[None, :]


def head_mm(Vmax, Ic, Rmm, k):
    """DEV-1: kappa applied in its conservative direction per frame. I_adm = Ic + (VLIM - Vmax)/R is decreasing in R
    when Vmax < VLIM but increasing when Vmax > VLIM, so 'R * kappa' is the safe margin only below the limit."""
    R = np.where(Vmax <= VLIM, Rmm * k, Rmm / k)
    return np.maximum(VLIM - (Vmax - Ic * R), 0.0) / R


def t_of(dah, L):
    return float((dah / np.maximum(L, 1e-6)).sum())


def session_eval(V, Tc, Ic, dah, R, Rmm, Q, Qmm, pmaps, hist_ok, shift=0.0, kappas=KAPPAS, do_perm=False):
    """Per kappa: t_mm, unsafe count, t_cell (M1). If do_perm (single kappa): t_cell for every probe map.
    DEV-3: without per-cell history the per-cell limiter has no per-cell R either, so it uses the same uniform R and
    the same kappa margin as min/max (its only possible edge is then temperature mapping, as in H)."""
    ctp = H.c_t(Tc, shift)
    ct_lo = np.minimum(H.c_t(Tc.min(1), shift), H.c_t(Tc.max(1), shift))
    Vmax = V.max(1)
    floor = FLOOR_C * QREF
    hk = head_k(V, Ic, R) if hist_ok else None
    maps = pmaps if do_perm else pmaps[:1]
    ctQ = [(ctp[:, pm] * Q).min(1) if np.ndim(Q) == 0 else (ctp[:, pm] * Q[None, :]).min(1) for pm in maps]
    ctQk0 = ctp[:, maps[0]] * (Q if np.ndim(Q) == 0 else Q[None, :])
    out = {"t_mm": [], "unsafe": [], "t_cell": [], "n": int(len(dah)), "hist_ok": bool(hist_ok)}
    if hist_ok:                                        # per-cell limit does not depend on kappa
        Qa = Q if np.ndim(Q) == 0 else Q[None, :]
        Lc_hist = [np.maximum(np.minimum(ctp[:, pm] * Qa, hk).min(1), floor) for pm in maps]
    for k in kappas:
        hm = head_mm(Vmax, Ic, Rmm, k)
        Lm = np.maximum(np.minimum(ct_lo * Qmm, hm), floor)
        if hist_ok:
            Lk0 = np.minimum(ctQk0, hk)
            Lc = Lc_hist
        else:
            Lk0 = np.minimum(ctQk0, hm[:, None])
            Lc = [np.maximum(np.minimum(c, hm), floor) for c in ctQ]
        out["t_mm"].append(t_of(dah, Lm))
        out["unsafe"].append(int((Lm > Lc[0] * UNSAFE_TOL).sum()))
        out["t_cell"].append([t_of(dah, L) for L in Lc] if do_perm else t_of(dah, Lc[0]))
    # binding-cell control at the last kappa evaluated (M1, tie-aware)
    L0 = np.maximum(Lk0.min(1), floor)
    bind = np.maximum(Lk0, floor) <= (L0 * (1 + 1e-9) + 1e-9)[:, None]
    pm0 = maps[0]
    ext = (pm0[None, :] == Tc.argmin(1)[:, None]) | (pm0[None, :] == Tc.argmax(1)[:, None])
    not_vmax = ~bind[np.arange(len(L0)), V.argmax(1)]
    out["n_info"] = int((not_vmax & ~(bind & ext).any(1)).sum())
    hcol = hk if hist_ok else np.repeat(head_mm(Vmax, Ic, Rmm, kappas[-1])[:, None], V.shape[1], 1)
    out["n_head"] = int((hcol < ctQk0).any(1).sum())
    return out


# ---------------------------------------------------------------- Changan
QREF_C = 120.0                                         # OPEN-3: Changan nominal Ah (fleet fast-charge label median ~120-126)
QREF = QREF_C


def changan_history(car, step_c):
    Z = np.load(f"{H.CELLS}/vin{car}.npz")
    t, I, tf = Z["t"], Z["I"].astype(np.float64), Z["t_full"]
    j = np.clip(np.searchsorted(t, tf), 0, len(t) - 1)
    ok = t[j] == tf
    vm = Z["vmean_mv"][j].astype(np.float64)
    V = vm[:, None] + Z["dv_full"].astype(np.float64)
    Ic = np.nan_to_num(-I[j])
    tm = Z["tmean"][j].astype(np.float64)
    d = np.diff(tf)
    dI = np.diff(Ic)
    st = (d <= STEP_DT_S) & ok[1:] & ok[:-1] & (np.abs(dI) >= step_c * QREF_C) & (np.abs(np.diff(tm)) <= 1.0) \
        & np.isfinite(V[1:]).all(1) & np.isfinite(V[:-1]).all(1)
    k = np.flatnonzero(st)
    r = (V[k + 1] - V[k]) / dI[k][:, None]             # mV/A = mOhm, charge-positive current
    rp = (vm[k + 1] - vm[k]) / dI[k]
    return {"t": tf[k + 1], "r": r, "rp": rp}


def changan_rests(car):
    """OPEN-4: rest = |I| < 1 A continuously (summary frames, gaps <= 60 s) for > 1 h; per-cell V from the last full
    frame within the rest. Consecutive rest pairs -> per-cell capacity Q_k = dAh / dSOC_k (H's ASSUMED OCV table)."""
    Z = np.load(f"{H.CELLS}/vin{car}.npz")
    t, I, tf = Z["t"], Z["I"].astype(np.float64), Z["t_full"]
    rest = np.abs(np.nan_to_num(I, nan=99)) < 1.0
    dt = np.diff(t, prepend=t[0])
    brk = (~rest) | (dt > 60)
    seg_id = np.cumsum(brk)
    out = []
    dts = np.where((dt > 0) & (dt <= 60), dt, 0.0)
    cah = np.cumsum(np.nan_to_num(-I) * dts / 3600.0)
    for sid in np.unique(seg_id[rest]):
        m = np.flatnonzero((seg_id == sid) & rest)
        if len(m) < 2 or t[m[-1]] - t[m[0]] < 3600:
            continue
        lo, hi = np.searchsorted(tf, [t[m[0]], t[m[-1]]], side="left")
        if hi <= lo:
            continue
        fi = hi - 1
        jj = np.searchsorted(t, tf[fi])
        if jj >= len(t) or t[jj] != tf[fi]:
            continue
        V = Z["vmean_mv"][jj] + Z["dv_full"][fi].astype(np.float64)
        if not np.isfinite(V).all():
            continue
        out.append((tf[fi], cah[m[-1]], V, float(Z["vmean_mv"][jj])))
    Qs = []
    for (t1, a1, V1, m1), (t2, a2, V2, m2) in zip(out[:-1], out[1:]):
        ds = H.soc(V2) - H.soc(V1)
        dsp = H.soc(m2) - H.soc(m1)
        if abs(dsp) < 20 or abs(np.median(ds)) < 20:
            continue
        with np.errstate(divide="ignore", invalid="ignore"):
            qk = (a2 - a1) / (ds / 100.0)
        Qs.append((t2, qk, (a2 - a1) / (dsp / 100.0)))
    return Qs


def changan_sessions(car):
    """H's session/frames logic plus per-frame time and charge-positive current."""
    Z = np.load(f"{H.CELLS}/vin{car}.npz")
    C = {k: Z[k] for k in ["t", "I", "status", "sync", "t_full", "vmean_mv", "tmean", "dv_full", "dt_full"]}
    t, I, st, sync = C["t"], C["I"].astype(np.float64), C["status"], C["sync"]
    tf = C["t_full"]
    j = np.clip(np.searchsorted(t, tf), 0, len(t) - 1)
    ok = (t[j] == tf) & (st[j] == 1) & sync[j]
    if ok.sum() < H.MIN_FULL:
        return []
    dt = np.diff(t, prepend=t[0])
    dt = np.where((dt > 0) & (dt <= H.GAP_INT), dt, 0.0)
    cah = np.cumsum(np.nan_to_num(np.where(st == 1, -I, 0.0)) * dt / 3600.0)
    ch = np.flatnonzero(st == 1)
    brk = np.flatnonzero(np.diff(t[ch]) > H.GAP_SESSION) + 1
    sid = np.zeros(len(t), np.int64) - 1
    for k, seg in enumerate(np.split(ch, brk)):
        sid[seg] = k
    fi = np.flatnonzero(ok)
    jj = j[fi]
    s_of = sid[jj]
    out = []
    for k in np.unique(s_of):
        if k < 0:
            continue
        m = s_of == k
        if m.sum() < H.MIN_FULL:
            continue
        rows, js = fi[m], jj[m]
        dah = np.diff(cah[js], prepend=cah[js[0]])
        dah[0] = 0.0
        Vf = C["vmean_mv"][js][:, None] + C["dv_full"][rows].astype(np.float64)
        Tf = C["tmean"][js][:, None] + C["dt_full"][rows].astype(np.float64)
        good = np.isfinite(Vf).all(1) & np.isfinite(Tf).all(1) & np.isfinite(dah)
        if good.sum() < H.MIN_FULL:
            continue
        js, dah, Vf, Tf = js[good], dah[good], Vf[good], Tf[good]
        out.append({"t0": float(t[js[0]]), "V": Vf, "T": Tf, "Ic": np.nan_to_num(-I[js]), "dah": np.clip(dah, 0, None)})
    return out


def r_from(hist, t0, win_s):
    m = (hist["t"] < t0) & (hist["t"] >= t0 - win_s)
    n = int(m.sum())
    if n >= MIN_STEPS:
        return np.median(hist["r"][m], 0), float(np.median(hist["rp"][m])), n, True
    rp = float(np.median(hist["rp"][m])) if n else R_DEFAULT_MOHM
    return np.full(hist["r"].shape[1] if hist["r"].ndim == 2 else 96, rp), rp, n, False


VARIANTS = {"base": dict(win=30, step=0.3, shift=0.0), "W7": dict(win=7, step=0.3, shift=0.0),
            "W90": dict(win=90, step=0.3, shift=0.0), "step0.2": dict(win=30, step=0.2, shift=0.0),
            "step0.5": dict(win=30, step=0.5, shift=0.0), "shift-5": dict(win=30, step=0.3, shift=-5.0),
            "shift+5": dict(win=30, step=0.3, shift=5.0)}


def _clean(R, Rmm):
    Rmm = Rmm if Rmm > 0.05 else R_DEFAULT_MOHM
    return np.where(np.isfinite(R) & (R > 0.05), R, Rmm), Rmm


def changan_one(args):
    """pass 1 (kstar None): every variant at every kappa, M1 only -> S [nsess, nk] + unsafe sums for calibration.
    pass 2 (kstar = index for 'base'): base variant at kappa*, all probe maps -> S [nsess, 1 + N_PERM] + controls."""
    car, kstar = args
    S = changan_sessions(car)
    S = [f for f in S if f["dah"].sum() > 0.5]
    empty = {"car": car, "n_sess": 0}
    if not S:
        return empty
    hists = {st: changan_history(car, st) for st in (0.2, 0.3, 0.5)}
    for h in hists.values():
        if h["r"].size == 0:
            h["r"] = np.zeros((0, 96))
    meta = {"car": car, "n_sess": len(S), "tmin_med": np.array([np.median(f["T"].min(1)) for f in S], np.float32),
            "tspread_med": np.array([np.median(f["T"].max(1) - f["T"].min(1)) for f in S], np.float32),
            "nfr": np.array([len(f["dah"]) for f in S], np.int32)}
    if kstar is not None:
        Sm, info, head, uns, hist = [], 0, 0, 0, []
        for f in S:
            R, Rmm, nst, ok = r_from(hists[0.3], f["t0"], 30 * 86400.0)
            R, Rmm = _clean(R, Rmm)
            e = session_eval(f["V"], f["T"], f["Ic"], f["dah"], R, Rmm, QREF_C, QREF_C, H.PMAPS, ok,
                             kappas=[KAPPAS[kstar]], do_perm=True)
            Sm.append(1 - np.array(e["t_cell"][0]) / e["t_mm"][0])
            info += e["n_info"]; head += e["n_head"]; uns += e["unsafe"][0]; hist.append(ok)
        meta.update({"S_maps": np.array(Sm, np.float32), "hist_ok": np.array(hist), "n_info": info, "n_head": head,
                     "n_unsafe": uns})
        return meta
    Q = changan_rests(car)
    for name, v in VARIANTS.items():
        Sv, uns, hist, nst_l = [], np.zeros(len(KAPPAS)), [], []
        for f in S:
            R, Rmm, nst, ok = r_from(hists[v["step"]], f["t0"], v["win"] * 86400.0)
            R, Rmm = _clean(R, Rmm)
            e = session_eval(f["V"], f["T"], f["Ic"], f["dah"], R, Rmm, QREF_C, QREF_C, H.PMAPS, ok, v["shift"])
            Sv.append(1 - np.array(e["t_cell"]) / np.array(e["t_mm"]))
            uns += e["unsafe"]; hist.append(ok); nst_l.append(nst)
        meta[f"S_{name}"] = np.array(Sv, np.float32)
        meta[f"uns_{name}"] = uns
        meta[f"hist_{name}"] = np.array(hist)
        meta[f"nsteps_{name}"] = np.array(nst_l, np.int32)
    # secondary: per-cell capacity (trailing 90 d, >= 3 rest pairs), base R; sessions without it are NaN
    Sq, unsq = [], np.zeros(len(KAPPAS))
    qspread = []
    for f in S:
        q = [x for x in Q if f["t0"] - 90 * 86400 <= x[0] < f["t0"]]
        if len(q) < 3:
            Sq.append(np.full(len(KAPPAS), np.nan)); qspread.append(np.nan)
            continue
        R, Rmm, nst, ok = r_from(hists[0.3], f["t0"], 30 * 86400.0)
        R, Rmm = _clean(R, Rmm)
        Qk = np.nanmedian(np.array([x[1] for x in q]), 0)
        Qp = float(np.nanmedian([x[2] for x in q]))
        Qk = np.where(np.isfinite(Qk) & (Qk > 30) & (Qk < 250), Qk, Qp)
        e = session_eval(f["V"], f["T"], f["Ic"], f["dah"], R, Rmm, Qk, Qp, H.PMAPS, True if ok else False)
        Sq.append(1 - np.array(e["t_cell"]) / np.array(e["t_mm"])); unsq += e["unsafe"]
        qspread.append(float(np.percentile(Qk, 95) / np.percentile(Qk, 5)))
    meta["S_capQ"] = np.array(Sq, np.float32)
    meta["uns_capQ"] = unsq
    meta["qspread"] = np.array(qspread, np.float32)
    return meta


def pick_kappa(uns, nfr, tol=UNSAFE_FRAC):
    frac = uns / max(nfr, 1)
    ok = np.flatnonzero(frac <= tol)
    i = int(ok[0]) if len(ok) else len(KAPPAS) - 1
    return i, float(KAPPAS[i]), float(frac[i]), frac.tolist()


def boot_median(vals, groups, rng, n=1000):
    ug = np.unique(groups)
    idx = {g: np.flatnonzero(groups == g) for g in ug}
    out = []
    for _ in range(n):
        pick = np.concatenate([idx[g] for g in rng.choice(ug, len(ug))])
        out.append(np.median(vals[pick]))
    return [float(np.percentile(out, 2.5)), float(np.percentile(out, 97.5))]


def decide(m1, m2, ci):
    v1, v2 = m1 >= 0.01, m2 >= 0.01
    if not v1 and not v2:
        return "NO BENEFIT"
    if v1 and v2 and ci[0] > 0:
        return "RECOVERS X"
    return "MAPPING-DEPENDENT"


def run_changan(jobs):
    cars = sorted(int(f[3:-4]) for f in os.listdir(H.CELLS) if f.startswith("vin") and f[3:-4].isdigit())
    with Pool(jobs) as p:
        P1 = [r for r in p.imap_unordered(changan_one, [(c, None) for c in cars]) if r["n_sess"]]
    P1.sort(key=lambda r: r["car"])
    nfr = int(sum(r["nfr"].sum() for r in P1))
    out = {"tag": "DERIVED (replay on MEASURED Changan cell states; limit map, mapping, OCV table ASSUMED); "
                  "CC BY-NC-SA 4.0 non-commercial", "preregistered_in": "0c4580a", "Q_ref_Ah": QREF_C,
           "n_vehicles": len(P1), "n_sessions": int(sum(r["n_sess"] for r in P1)), "n_frames": nfr}
    car_of = np.concatenate([np.full(r["n_sess"], r["car"]) for r in P1])
    tmin = np.concatenate([r["tmin_med"] for r in P1])
    tspr = np.concatenate([r["tspread_med"] for r in P1])
    cold = tmin < 10
    kap = {}
    for name in list(VARIANTS) + ["capQ"]:
        uns = np.sum([r[f"uns_{name}"] for r in P1], 0)
        kap[name] = pick_kappa(uns, nfr)
    out["kappa_mm"] = {n: {"kappa": k[1], "unsafe_frac": k[2]} for n, k in kap.items()}
    out["kappa_curve_base"] = dict(zip(KAPPAS.tolist(), kap["base"][3]))
    rng = np.random.default_rng(0)
    # pass 2: base at kappa*, all maps
    with Pool(jobs) as p:
        P2 = {r["car"]: r for r in p.imap_unordered(changan_one, [(r["car"], kap["base"][0]) for r in P1])}
    Smaps = np.concatenate([P2[r["car"]]["S_maps"] for r in P1])
    hist = np.concatenate([P2[r["car"]]["hist_ok"] for r in P1])

    def arm(sel, label, decide_rule=True):
        if sel.sum() == 0:
            return {"n_sessions": 0}
        s1 = Smaps[sel, 0]
        m2 = np.median(Smaps[sel, 1:], 0)
        ci = boot_median(s1, car_of[sel], rng)
        d = {"n_sessions": int(sel.sum()), "n_vehicles": int(len(np.unique(car_of[sel]))),
             "n_sessions_with_history": int(hist[sel].sum()),
             "S_M1_median": float(np.median(s1)), "S_M1_mean": float(np.mean(s1)),
             "S_M1_p90": float(np.percentile(s1, 90)), "S_M1_p10": float(np.percentile(s1, 10)), "S_M1_CI": ci,
             "S_M2_median_of_medians": float(np.median(m2)),
             "S_M2_range_5_95": [float(np.percentile(m2, 5)), float(np.percentile(m2, 95))],
             "S_M1_median_history_sessions": float(np.median(s1[hist[sel]])) if hist[sel].any() else None,
             "S_M1_p90_history_sessions": float(np.percentile(s1[hist[sel]], 90)) if hist[sel].any() else None,
             "S_M1_median_no_history_sessions": float(np.median(s1[~hist[sel]])) if (~hist[sel]).any() else None}
        if decide_rule:
            if label == "cold" and d["n_sessions_with_history"] < 200:
                d["decision"] = "UNDERPOWERED"
            else:
                d["decision"] = decide(d["S_M1_median"], d["S_M2_median_of_medians"], ci)
        return d

    out["X2_C_cold_primary"] = arm(cold, "cold")
    out["X2_C_all"] = arm(np.ones(len(cold), bool), "all")
    out["X2_C_history_sessions_only_posthoc"] = arm(hist, "hist", decide_rule=False)
    out["X2_C_cold_history_sessions_only_posthoc"] = arm(cold & hist, "hist", decide_rule=False)
    out["by_spread_band"] = {f"{a}-{b:g}": arm((tspr >= a) & (tspr < b), "band", decide_rule=False)
                             for a, b in SPREAD_BANDS}
    out["controls_base_kappa"] = {
        "frac_frames_binding_cell_not_vmax_not_extreme_probe": sum(P2[c]["n_info"] for c in P2) / nfr,
        "frac_frames_headroom_binds_some_cell": sum(P2[c]["n_head"] for c in P2) / nfr,
        "frac_frames_mm_unsafe_at_kappa": sum(P2[c]["n_unsafe"] for c in P2) / nfr}
    sens = {}
    for name in VARIANTS:
        if name == "base":
            continue
        Sv = np.concatenate([r[f"S_{name}"] for r in P1])[:, kap[name][0]]
        hv = np.concatenate([r[f"hist_{name}"] for r in P1])
        sens[name] = {"kappa": kap[name][1], "cold_S_M1_median": float(np.median(Sv[cold])),
                      "all_S_M1_median": float(np.median(Sv)), "cold_sessions_with_history": int((hv & cold).sum()),
                      "all_sessions_with_history": int(hv.sum()),
                      "S_M1_median_history_sessions": float(np.median(Sv[hv])) if hv.any() else None}
    Sb = np.concatenate([r["S_base"] for r in P1])
    for tol, nm in ((1e-4, "kappa_tol0.01%"), (1e-2, "kappa_tol1%")):
        ik = pick_kappa(np.sum([r["uns_base"] for r in P1], 0), nfr, tol)
        sens[nm] = {"kappa": ik[1], "cold_S_M1_median": float(np.median(Sb[cold, ik[0]])),
                    "all_S_M1_median": float(np.median(Sb[:, ik[0]]))}
    out["sensitivity"] = sens
    nst = np.concatenate([r["nsteps_base"] for r in P1])
    out["history_steps_in_30d_window"] = {"p10": float(np.percentile(nst, 10)), "median": float(np.median(nst)),
                                          "p90": float(np.percentile(nst, 90)), "frac_ge_20": float((nst >= 20).mean())}
    Sq = np.concatenate([r["S_capQ"] for r in P1])[:, kap["capQ"][0]]
    hq = np.isfinite(Sq)
    qs = np.concatenate([r["qspread"] for r in P1])
    out["secondary_capacity"] = {"n_sessions": int(hq.sum()), "kappa": kap["capQ"][1],
                                 "S_M1_median": float(np.median(Sq[hq])) if hq.any() else None,
                                 "S_M1_p90": float(np.percentile(Sq[hq], 90)) if hq.any() else None,
                                 "cold_S_M1_median": float(np.median(Sq[hq & cold])) if (hq & cold).any() else None,
                                 "n_cold": int((hq & cold).sum()),
                                 "Q_k_p95_over_p5_median": float(np.nanmedian(qs)) if hq.any() else None}
    np.savez_compressed("results/X/X2/x2_changan_sessions.npz", car=car_of, tmin=tmin, tspread=tspr,
                        S_M1=Smaps[:, 0], S_M2_med=np.median(Smaps[:, 1:], 1), hist_ok=hist)
    return out


# ---------------------------------------------------------------- McMaster (1 Hz drive cycles; I > 0 = charge)
MCM = "data/raw/mcmaster/x/Drive Cycle Data"
QREF_M = 5.2
# X2-M2 (results/X/X2M2_preregistration.md, ea9f714): 1.0 = X2-M pre-registered; 4.0 = SOURCED 6 C (dataset README,
# primary); 16.0 = SOURCED 125 A peak (Kim slide, sensitivity). Any other value is POST-HOC (e.g. the 10.0 tried earlier).
X2M2_QSCALES = (1.0, 4.0, 16.0)


def mcm_load(p):
    import scipy.io as sio
    m = sio.loadmat(p, squeeze_me=True)
    V = m["Voltages_R2"].astype(np.float64) * 1e3
    T = m["CellTemp_R"].astype(np.float64)
    I = m["Current_R2"].astype(np.float64)
    dead = [k for k in range(T.shape[1]) if np.ptp(T[:, k]) == 0 or np.median(T[:, k]) < np.median(T) - 10]
    for k in dead:                                     # prereg §1: neighbour median replaces dead channels
        nb = [x for x in (k - 1, k + 1) if 0 <= x < T.shape[1] and x not in dead]
        T[:, k] = np.median(T[:, nb], 1)
    return V, T, I, dead


def mcmaster(qscale=1.0):
    """qscale = 1 is the pre-registered map. qscale > 1 (POST-HOC, not pre-registered) scales the C_T current cap for a
    power cell (H's map assumes an energy cell: 1.5 C = 7.8 A here vs recorded regen up to ~150 A)."""
    files = sorted(glob.glob(f"{MCM}/*.mat"))
    groups = {}
    for p in files:
        groups.setdefault("25C" if "_25C" in os.path.basename(p) else "15C", []).append(p)
    pm = np.arange(72)[None, :]
    rows = []
    for g, ps in groups.items():
        pool_r, pool_rp = [], []
        for p in ps:
            V, T, I, dead = mcm_load(p)
            dI = np.diff(I)
            fin = np.isfinite(V).all(1)                    # drop non-finite frames (as H; 9 frames in one run)
            st = (np.abs(dI) >= 0.3 * QREF_M) & (np.abs(np.diff(T.mean(1))) <= 1.0) & fin[1:] & fin[:-1]
            k = np.flatnonzero(st)
            r_run = (V[k + 1] - V[k]) / dI[k][:, None]
            rp_run = (V[k + 1].mean(1) - V[k].mean(1)) / dI[k]
            ch = (I > 0.05 * QREF_M) & fin
            Rk = np.zeros_like(V)
            Rp = np.zeros(len(I))
            hist_ok = np.zeros(len(I), bool)
            for blk in range(0, len(I), 60):          # OPEN-5: R re-estimated every 60 s from steps strictly before
                before = k[k + 1 < blk]
                rr = pool_r + [r_run[np.isin(k, before)]]
                rr = np.concatenate([x for x in rr if len(x)], 0) if any(len(x) for x in rr) else np.zeros((0, 72))
                rpp = np.concatenate([x for x in (pool_rp + [rp_run[np.isin(k, before)]]) if len(x)]) \
                    if any(len(x) for x in pool_rp + [rp_run[np.isin(k, before)]]) else np.zeros(0)
                if len(rr) >= MIN_STEPS:
                    Rk[blk:blk + 60] = np.median(rr, 0)
                    Rp[blk:blk + 60] = np.median(rpp)
                    hist_ok[blk:blk + 60] = True
                else:
                    rp0 = np.median(rpp) if len(rpp) else 1.0
                    Rk[blk:blk + 60] = rp0
                    Rp[blk:blk + 60] = rp0
            Rk = np.where(Rk > 0.05, Rk, np.maximum(Rp[:, None], 0.05))
            Rp = np.maximum(Rp, 0.05)
            # per-frame limits on charge-direction frames (R varies by block, so evaluate frame-wise)
            f = np.flatnonzero(ch)
            ctc = H.c_t(T[f]) * qscale
            vocv = V[f] - I[f, None] * Rk[f]
            hk = np.maximum(VLIM - vocv, 0) / Rk[f]
            floor = FLOOR_C * QREF_M                       # DEV-2
            ct_lo = np.minimum(H.c_t(T[f].min(1)), H.c_t(T[f].max(1))) * qscale
            ho = hist_ok[f]
            Lc_hist = np.maximum(np.minimum(ctc * QREF_M, hk).min(1), floor)
            Lc, Lm = {}, {}
            for kk in KAPPAS:
                hm = head_mm(V[f].max(1), I[f], Rp[f], kk)      # DEV-1
                Lm[float(kk)] = np.maximum(np.minimum(ct_lo * QREF_M, hm), floor)
                # DEV-3: frames without per-cell history use min/max's uniform R and margin
                Lc[float(kk)] = np.where(ho, Lc_hist, np.maximum(np.minimum((ctc * QREF_M).min(1), hm), floor))
            head = (hk < ctc * QREF_M).any(1)
            rows.append({"run": os.path.basename(p), "group": g, "dead_thermistors": [d + 1 for d in dead],
                         "n_charge_frames": int(len(f)), "frac_with_history": float(hist_ok[f].mean()) if len(f) else 0,
                         "Lc": Lc, "Lm": Lm, "head_frac": float(head.mean()) if len(f) else 0,
                         "spread_med": float(np.median(T.max(1) - T.min(1))), "Tmax": float(T.max())})
            pool_r.append(r_run)
            pool_rp.append(rp_run)
    n = sum(r["n_charge_frames"] for r in rows)
    uns = [sum(int((r["Lm"][float(kk)] > r["Lc"][float(kk)] * UNSAFE_TOL).sum()) for r in rows) / n for kk in KAPPAS]
    ok = np.flatnonzero(np.array(uns) <= UNSAFE_FRAC)
    kap = float(KAPPAS[ok[0]]) if len(ok) else float(KAPPAS[-1])
    G = []
    g_curve = {float(kk): float(np.median([r["Lc"][float(kk)].mean() / r["Lm"][float(kk)].mean() - 1
                                           for r in rows if r["n_charge_frames"]])) for kk in KAPPAS}   # X2-M2 figure
    for r in rows:
        if r["n_charge_frames"]:
            r["G"] = float(r["Lc"][kap].mean() / r["Lm"][kap].mean() - 1)
            G.append(r["G"])
        del r["Lc"], r["Lm"]
    rng = np.random.default_rng(0)
    G = np.array(G)
    bs = [np.median(rng.choice(G, len(G))) for _ in range(1000)]
    ci = [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]
    dec = ("descriptive (CI spans 0)" if ci[0] <= 0 <= ci[1] else
           "RECOVERS X" if np.median(G) >= 0.01 and ci[0] > 0 else "NO BENEFIT")
    return {"tag": "DERIVED (McMaster 72S, CC BY 4.0; limit map ASSUMED)", "qscale": qscale,
            "post_hoc": qscale not in X2M2_QSCALES, "kappa_mm": kap,
            "unsafe_curve": dict(zip(KAPPAS.tolist(), uns)), "G_median_curve": g_curve,
            "head_frac_all": float(np.average([r["head_frac"] for r in rows], weights=[r["n_charge_frames"] for r in rows])), "G_median": float(np.median(G)), "G_CI": ci,
            "decision": dec, "runs": rows}


# ---------------------------------------------------------------- BATSS fast charge (report-only)
def batss():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from X3_casestudy import read_xlsx
    Q = 67.0
    res = []
    rng = np.random.default_rng(0)
    for p in sorted(glob.glob("data/raw/batss/BATSS_1[6-9]_FastCharge_*_results.xlsx")):
        Hh, rows = read_xlsx(p)
        col = lambda n: np.array([float(r.get(Hh[n], "nan")) for r in rows])
        tc = [h for h in Hh if h.startswith("T") and h.endswith("_C_") and h[1:-3].isdigit()]
        tc.sort(key=lambda h: int(h[1:-3]))
        t = col("Time_s")
        V = np.column_stack([col(f"Vcell_{k}_V_") for k in range(1, 11)]) * 1e3
        T = np.column_stack([col(h) for h in tc])
        I = col("Current_A_")
        mode = np.array([r.get(Hh["StepMode"], "") for r in rows])
        good = np.isfinite(V).all(1) & np.isfinite(I) & np.isfinite(T).all(1)
        dI = np.diff(I)
        k = np.flatnonzero((np.abs(dI) >= 0.3 * Q) & good[1:] & good[:-1])
        r = (V[k + 1] - V[k]) / dI[k][:, None]
        ch = (mode == "CC-CV Charge") & good
        seg = np.split(np.flatnonzero(ch), np.flatnonzero(np.diff(np.flatnonzero(ch)) > 1) + 1)
        # M1: contiguous split of thermocouples across 10 cells; M2: 100 random orders then contiguous split
        orders = [np.arange(len(tc))] + [rng.permutation(len(tc)) for _ in range(100)]
        for sgi, s in enumerate(seg):
            if len(s) < 30:
                continue
            before = k[k + 1 < s[0]]
            n_st = len(before)
            Rk = np.median(r[np.isin(k, before)], 0) if n_st >= MIN_STEPS else np.full(10, np.median(r[np.isin(k, before)]) if n_st else 1.0)
            Rk = np.maximum(Rk, 0.05)
            Rp = float(np.median(Rk))
            ok_h = n_st >= MIN_STEPS
            floor = FLOOR_C * Q
            dt = np.diff(t[s], prepend=t[s][0])
            dah = np.clip(I[s], 0, None) * np.where(dt <= 60, dt, 0) / 3600
            S = []
            for o in orders:
                grp = np.array_split(o, 10)
                ctc = np.column_stack([H.c_t(T[s][:, g]).min(1) for g in grp])
                hm1 = head_mm(V[s].max(1), I[s], Rp, 1.0)
                hc = (np.maximum(VLIM - (V[s] - I[s, None] * Rk), 0) / Rk) if ok_h else hm1[:, None]   # DEV-3
                Lc = np.maximum(np.minimum(ctc * Q, hc).min(1), floor)
                S.append(t_of(dah, Lc))
            ct_lo = np.minimum(H.c_t(T[s].min(1)), H.c_t(T[s].max(1)))
            tm = {float(kk): t_of(dah, np.maximum(np.minimum(ct_lo * Q, head_mm(V[s].max(1), I[s], Rp, kk)), floor))
                  for kk in KAPPAS}
            res.append({"run": os.path.basename(p), "segment": sgi, "n": int(len(s)), "n_steps_before": n_st,
                        "hist_ok": n_st >= MIN_STEPS, "t_cell": S, "t_mm": tm,
                        "Tmax": float(T[s].max()), "spread_med": float(np.median(T[s].max(1) - T[s].min(1)))})
    for x in res:                                      # report at kappa = 1 (no calibration possible on report arm)
        x["S_M1_kappa1"] = 1 - x["t_cell"][0] / x["t_mm"][1.0]
        x["S_M2_median_kappa1"] = float(np.median([1 - tc / x["t_mm"][1.0] for tc in x["t_cell"][1:]]))
        del x["t_cell"], x["t_mm"]
    return {"tag": "DERIVED, report-only (BATSS, CC BY 4.0; TC->cell mapping ASSUMED M1/M2)", "sessions": res}


VLIM = 4200.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", default="all")
    ap.add_argument("--out", default="results/X/X2")
    ap.add_argument("--jobs", type=int, default=10)
    ap.add_argument("--mcm-qscale", type=float, default=1.0)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    if a.arm in ("mcmaster", "all"):
        m = mcmaster(a.mcm_qscale)
        sfx = ("" if a.mcm_qscale == 1.0 else f"_M2_qscale{a.mcm_qscale:g}" if a.mcm_qscale in X2M2_QSCALES
               else f"_posthoc_qscale{a.mcm_qscale:g}")
        json.dump(m, open(f"{a.out}/x2_mcmaster{sfx}.json", "w"), indent=1)
        print(json.dumps({k: v for k, v in m.items() if k != "runs"}, indent=1))
    if a.arm in ("batss", "all"):
        b = batss()
        json.dump(b, open(f"{a.out}/x2_batss.json", "w"), indent=1)
        print(json.dumps(b, indent=1)[:3000])
    if a.arm in ("changan", "all"):
        out = run_changan(a.jobs)
        json.dump(out, open(f"{a.out}/x2_changan.json", "w"), indent=1)
        print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
