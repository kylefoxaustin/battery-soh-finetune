"""Independent re-scan of Beihang QAS: cohort fingerprints + sensitivity variants of A/B. CPU only, 8 procs."""
import sys, os, json, numpy as np, pandas as pd
from multiprocessing import Pool
sys.path.insert(0, "<repo>/analysis")
import G2_beihang as G
R = "<repo>/data/raw/beihang/x"
OUT = "/tmp/claude-1000/-home-kyle-Documents-GitHub-batt-finetune/8fc251be-e160-42c8-b7ad-d2301080f5cc/scratchpad/review/g2"
K = 110

def ols(y):
    x = np.arange(len(y)); x = x - x.mean()
    return (x @ (y - y.mean(0))) / (x @ x)            # vectorised over columns

def theil(y):                                        # y: nblk x cells
    n = len(y); i, j = np.triu_indices(n, 1)
    return np.median((y[j] - y[i]) / (j - i)[:, None], 0)

def rz(x):
    med = np.median(x); mad = 1.4826 * np.median(np.abs(x - med))
    return (x - med) / mad if mad > 0 else np.zeros_like(x)

def feats(V, I, nblk=10, rest_thr=1.0, agg="median", slope="ols", perm_seed=None, use_rest=True, prefix=""):
    rest = np.abs(I) < rest_thr if use_rest else np.ones(len(I), bool)
    n = rest.sum()
    if n < nblk * 20:
        return {}
    Vr = V[rest]; mean = Vr.mean(1, keepdims=True); d = (Vr - mean) * 1e3
    m = (Vr.min(1) - mean[:, 0]) * 1e3; mx = (Vr.max(1) - mean[:, 0]) * 1e3; s = (Vr.max(1) - Vr.min(1)) * 1e3
    blocks = np.array_split(np.arange(n), nblk)
    if perm_seed is not None:
        blocks = [blocks[i] for i in np.random.default_rng(perm_seed).permutation(nblk)]
    f = np.median if agg == "median" else np.mean
    bd = np.array([f(d[b], 0) for b in blocks]); bm = np.array([f(m[b]) for b in blocks])
    bmx = np.array([f(mx[b]) for b in blocks]); bs = np.array([f(s[b]) for b in blocks])
    sl = ols(bd) if slope == "ols" else theil(bd)
    z = rz(sl); zs = np.sort(z)
    o = {"A": -z.min(), "A2": -zs[1], "A_up": z.max(), "A_abs": np.abs(z).max(), "A_raw": -sl.min(),
         "A_cell": int(np.argmin(z)), "B": -ols(bm[:, None])[0], "B_max": ols(bmx[:, None])[0],
         "B_sprslope": ols(bs[:, None])[0], "A_lvl": -rz(np.median(d, 0)).min(), "n_rest": int(n),
         "slope_kurt_proxy": float(np.mean(np.abs(z) > 3)), "mad_slope": float(1.4826 * np.median(np.abs(sl - np.median(sl))))}
    return {prefix + k: v for k, v in o.items()}

def vehicle(n):
    try:
        b = G.load(f"{R}/QAS/{n}/vin_2.pkl")
        x = b[:, :2]; Vall = b[:, 2:2 + K]; z = b[:, 2 + K:2 + 2 * K]; q = b[:, 2 + 2 * K:]
        T, S, I = q[:, 0], q[:, 1], q[:, 2]
        sent = np.abs(I) >= 900
        vok = np.all((Vall >= 2.0) & (Vall <= 4.5), 1)
        valid = (~sent) & vok
        r = {"veh": n, "n_rows": len(b), "n_valid": int(valid.sum()), "frac_sent": float(sent.mean()),
             "frac_vbad": float((~vok).mean()), "sent_mean": float(I[sent].mean()) if sent.any() else np.nan,
             "sent_std": float(I[sent].std()) if sent.any() else np.nan,
             "T_first10": float(np.median(T[: len(T) // 10])), "T_last10": float(np.median(T[-(len(T) // 10):])),
             "T_min": float(T.min()), "T_max": float(T.max()), "T_nuniq": int(len(np.unique(T))),
             "S_nuniq": int(len(np.unique(S))), "S_med": float(np.median(S)), "S_min": float(S.min()),
             "S_jumps05": int((np.abs(np.diff(S)) > 0.05).sum()), "S_jumps02": int((np.abs(np.diff(S)) > 0.02).sum()),
             "V_nuniq": int(len(np.unique(Vall))), "V_med": float(np.median(Vall)), "V_max": float(Vall.max()), "V_min": float(Vall.min()),
             "V_spread_med": float(np.median((Vall.max(1) - Vall.min(1))[valid]) * 1e3),
             "frac_alltie": float(np.mean((Vall.max(1) - Vall.min(1)) == 0)),
             "x0_med": float(np.median(x[:, 0])), "x0_std": float(x[:, 0].std()), "x1_med": float(np.median(x[:, 1])),
             "z_std": float(np.median(z.std(0))), "z_absmax": float(np.abs(z).max()), "z_frac_big": float(np.mean(np.abs(z) > 1)),
             "I_nuniq": int(len(np.unique(I[~sent]))), "I_med_valid": float(np.median(I[~sent])) if (~sent).any() else np.nan,
             "frac_Ipos": float(np.mean(I[~sent] > 1)), "frac_Ineg": float(np.mean(I[~sent] < -1)),
             "I_absmax": float(np.abs(I[~sent]).max()) if (~sent).any() else np.nan}
        # current sign convention: corr(dV_mean, I) on valid consecutive frames
        Vm = Vall.mean(1); dv = np.diff(Vm); ok = valid[1:] & valid[:-1] & (np.abs(I[1:]) > 5)
        r["corr_dV_I"] = float(np.corrcoef(dv[ok], I[1:][ok])[0, 1]) if ok.sum() > 50 else np.nan
        # duplicated cell channels
        r["n_dup_cells"] = int(K - len({tuple(np.round(Vall[valid][::50, k], 4)) for k in range(K)}))
        a1 = G.load(f"{R}/QAS/{n}/vin_1.pkl").reshape(len(b), -1)
        for c in range(a1.shape[1]):
            r[f"v1c{c}_const"] = bool(np.ptp(a1[:, c]) == 0); r[f"v1c{c}_nondec"] = bool(np.all(np.diff(a1[:, c]) >= -1e-12))
        a3 = G.load(f"{R}/QAS/{n}/vin_3.pkl"); q3 = a3[:, 2 + 2 * K:]
        r["v3_ncol"] = a3.shape[1]; r["v3_q3_med"] = float(np.median(q3[:, 3])) if q3.shape[1] > 3 else np.nan
        r["v3_q3_min"] = float(q3[:, 3].min()) if q3.shape[1] > 3 else np.nan; r["v3_q3_max"] = float(q3[:, 3].max()) if q3.shape[1] > 3 else np.nan
        V, I, T, S = Vall[valid], I[valid], T[valid], S[valid]
        N = len(I); h = N // 2
        wins = {"E": slice(0, h), "L": slice(h, N), "Q1": slice(0, N // 4), "Q2": slice(N // 4, h), "Q3": slice(h, 3 * N // 4),
                "Q4": slice(3 * N // 4, N), "L90": slice(h, 9 * N // 10), "T10": slice(9 * N // 10, N), "T5": slice(19 * N // 20, N)}
        for w, sl in wins.items():
            r.update(feats(V[sl], I[sl], prefix=f"{w}_"))
            r[f"{w}_T"] = float(np.median(T[sl])); r[f"{w}_S"] = float(np.median(S[sl])); r[f"{w}_restfrac"] = float(np.mean(np.abs(I[sl]) < 1))
        for w in ("E", "L"):
            sl = wins[w]
            r.update(feats(V[sl], I[sl], nblk=5, prefix=f"{w}_b5_"))
            r.update(feats(V[sl], I[sl], nblk=20, prefix=f"{w}_b20_"))
            r.update(feats(V[sl], I[sl], rest_thr=0.5, prefix=f"{w}_r05_"))
            r.update(feats(V[sl], I[sl], rest_thr=3.0, prefix=f"{w}_r3_"))
            r.update(feats(V[sl], I[sl], rest_thr=10.0, prefix=f"{w}_r10_"))
            r.update(feats(V[sl], I[sl], use_rest=False, prefix=f"{w}_all_"))
            r.update(feats(V[sl], I[sl], slope="theil", prefix=f"{w}_ts_"))
            r.update(feats(V[sl], I[sl], agg="mean", prefix=f"{w}_mean_"))
            r.update(feats(V[sl], I[sl], perm_seed=1000 + n, prefix=f"{w}_perm_"))
        # fixed-count windows: first 1500 rest frames, last 1500 rest frames
        rest_idx = np.where(np.abs(I) < 1.0)[0]
        if len(rest_idx) >= 3000:
            r.update(feats(V[rest_idx[:1500]], I[rest_idx[:1500]], prefix="F1500_"))
            r.update(feats(V[rest_idx[-1500:]], I[rest_idx[-1500:]], prefix="L1500_"))
        # per-cell E/L slopes saved
        return r, None
    except Exception as e:
        return {"veh": n, "err": repr(e)}, None

if __name__ == "__main__":
    lab = pd.read_excel(f"{R}/QAS/Labels.xls")
    ids = [int(v) for v in lab.Num]
    with Pool(8) as p:
        res = p.map(vehicle, ids, chunksize=4)
    df = pd.DataFrame([r for r, _ in res]).merge(lab.rename(columns={"Num": "veh", "Label": "label"}), on="veh")
    df.to_csv(f"{OUT}/rescan_qas.csv", index=False)
    print(df.shape, df.get("err", pd.Series(dtype=object)).notna().sum() if "err" in df else 0)
