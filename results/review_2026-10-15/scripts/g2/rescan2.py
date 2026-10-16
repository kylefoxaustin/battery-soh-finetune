"""Second pass: SOC-restricted rest frames, run/gap structure, block-SOC dispersion, explicit variability feature."""
import sys, numpy as np, pandas as pd
from multiprocessing import Pool
sys.path.insert(0, "<repo>/analysis")
sys.path.insert(0, "/tmp/claude-1000/-home-kyle-Documents-GitHub-batt-finetune/8fc251be-e160-42c8-b7ad-d2301080f5cc/scratchpad/review/g2")
import G2_beihang as G
from rescan import ols, rz, R, OUT, K

def feats(V, I, S, T, nblk=10, prefix="", soc_lo=0.0, soc_hi=1.0):
    rest = (np.abs(I) < 1.0) & (S >= soc_lo) & (S <= soc_hi)
    n = rest.sum()
    if n < nblk * 20: return {}
    Vr = V[rest]; mean = Vr.mean(1, keepdims=True); d = (Vr - mean) * 1e3; m = (Vr.min(1) - mean[:, 0]) * 1e3
    blocks = np.array_split(np.arange(n), nblk)
    bd = np.array([np.median(d[b], 0) for b in blocks]); bm = np.array([np.median(m[b]) for b in blocks])
    bsoc = np.array([np.median(S[rest][b]) for b in blocks]); bT = np.array([np.median(T[rest][b]) for b in blocks])
    sl = ols(bd); z = rz(sl)
    zvar = rz(bd.std(0))                       # explicit between-block variability per cell
    zrng = rz(np.ptp(bd, 0))
    # deviation-vs-SOC slope per cell on rest frames (how much a cell's deviation depends on pack SOC)
    Sr = S[rest]; Sc = Sr - Sr.mean(); dsoc = (Sc @ (d - d.mean(0))) / (Sc @ Sc) if Sc @ Sc > 0 else np.zeros(K)
    o = {"A": -z.min(), "B": -ols(bm[:, None])[0], "A_var": zvar.max(), "A_rng": zrng.max(),
         "blk_soc_sd": float(bsoc.std()), "blk_soc_slope": float(ols(bsoc[:, None])[0]), "blk_T_sd": float(bT.std()),
         "blk_T_slope": float(ols(bT[:, None])[0]), "rest_soc_sd": float(Sr.std()), "rest_soc_min": float(Sr.min()),
         "rest_soc_p05": float(np.quantile(Sr, 0.05)), "dsoc_absmax_z": float(rz(np.abs(dsoc)).max()),
         "corr_Acell_soc": float(np.corrcoef(d[:, np.argmin(z)], Sr)[0, 1]) if Sr.std() > 0 else np.nan,
         "n_rest": int(n), "corr_zsl_zvar": float(np.corrcoef(-z, zvar)[0, 1])}
    return {prefix + k: v for k, v in o.items()}

def vehicle(n):
    try:
        b = G.load(f"{R}/QAS/{n}/vin_2.pkl"); Vall = b[:, 2:2 + K]; q = b[:, 2 + 2 * K:]
        T, S, I = q[:, 0], q[:, 1], q[:, 2]
        valid = (np.abs(I) < 900) & np.all((Vall >= 2.0) & (Vall <= 4.5), 1)
        V, I, T, S = Vall[valid], I[valid], T[valid], S[valid]
        N = len(I); h = N // 2
        r = {"veh": n}
        # run structure: break where |dSOC|>0.02 or |dT|>=3
        brk = (np.abs(np.diff(S)) > 0.02) | (np.abs(np.diff(T)) >= 3)
        runs = np.diff(np.r_[0, np.where(brk)[0] + 1, N])
        r["n_runs"] = len(runs); r["run_med"] = float(np.median(runs)); r["run_max"] = int(runs.max())
        r["frac_frames_in_long_runs"] = float(runs[runs >= 500].sum() / N)
        # temperature "season" proxies within windows and the temp step at breaks
        r["T_range_E"] = float(np.ptp(T[:h])); r["T_range_L"] = float(np.ptp(T[h:]))
        r["dT_at_breaks_med"] = float(np.median(np.abs(np.diff(T))[brk])) if brk.any() else 0.0
        r["n_Tjumps3"] = int((np.abs(np.diff(T)) >= 3).sum())
        for w, sl in {"E": slice(0, h), "L": slice(h, N)}.items():
            r.update(feats(V[sl], I[sl], S[sl], T[sl], prefix=f"{w}_"))
            r.update(feats(V[sl], I[sl], S[sl], T[sl], prefix=f"{w}_socmid_", soc_lo=0.35, soc_hi=0.9))
            r.update(feats(V[sl], I[sl], S[sl], T[sl], prefix=f"{w}_sochi_", soc_lo=0.9, soc_hi=1.0))
        return r
    except Exception as e:
        return {"veh": n, "err": repr(e)}

if __name__ == "__main__":
    lab = pd.read_excel(f"{R}/QAS/Labels.xls")
    with Pool(8) as p: res = p.map(vehicle, [int(v) for v in lab.Num], chunksize=4)
    df = pd.DataFrame(res).merge(lab.rename(columns={"Num": "veh", "Label": "label"}), on="veh")
    df.to_csv(f"{OUT}/rescan2_qas.csv", index=False); print(df.shape)
