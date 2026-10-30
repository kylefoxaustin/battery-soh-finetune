"""X4 — per-cell vs pack-scalar usable-energy estimation (public domain, CC0).
See X4_preregistration.md (incl. Deviation 1). One Changan vehicle, CC BY-NC-SA.
"""
import numpy as np, pandas as pd, json, os

d = pd.read_pickle(os.environ.get('CHANGAN_PKL', 'all.pkl')).sort_values('terminaltime').reset_index(drop=True)
t = d.terminaltime.values.astype(float); I = d.totalcurrent.values.astype(float)
soc = d.soc.values.astype(float); cs = d.chargestatus.values
dt = np.diff(t, prepend=t[0]); dt_int = np.where(dt > 60, 0.0, dt)   # gaps = parked, zero current

# ---- per-cell voltages (only the frames we need) ---------------------------
def cells(i):
    s = d.batteryvoltage.values[i]
    try:
        v = np.array(s.split('~'), dtype=float)
        return v if v.size == 96 else None
    except Exception:
        return None

# ---- OCV table from this vehicle's rests (ASSUMED, as in E/F) --------------
rest = np.abs(I) < 1.0
ri = np.where(rest & (dt <= 60))[0]
ri = ri[::25]                                   # thin for speed
vv, ss = [], []
for i in ri:
    c = cells(i)
    if c is not None and 2.8 < c.mean() < 4.3:
        vv.append(c.mean()); ss.append(soc[i])
vv, ss = np.array(vv), np.array(ss)
# early-life only (first 20 % of the record) so OCV is not built from aged cells
early = np.arange(len(vv)) < 0.2*len(vv)
bins = np.arange(0, 101, 2)
ocv_v = np.array([np.median(vv[early][(ss[early] >= b) & (ss[early] < b+2)]) if np.any((ss[early] >= b) & (ss[early] < b+2)) else np.nan for b in bins])
ok = ~np.isnan(ocv_v)
ocv_v, ocv_s = np.maximum.accumulate(ocv_v[ok]), bins[ok] + 1.0
def v2soc(v): return np.interp(v, ocv_v, ocv_s)

# ---- labelled discharges (Deviation 1) --------------------------------------
segs = []; i = 0; n = len(d)
while i < n:
    if cs[i] != 1:
        j = i
        while j+1 < n and cs[j+1] != 1: j += 1
        segs.append((i, j)); i = j+1
    else:
        i += 1
runs = []
for a, b in segs:
    if soc[a] - soc[b] < 40: continue
    idx = np.arange(a, b+1)
    r_idx = idx[np.abs(I[idx]) < 1.0]
    if len(r_idx) < 2: continue
    i0, i1 = r_idx[0], r_idx[-1]
    c0, c1 = cells(i0), cells(i1)
    if c0 is None or c1 is None: continue
    Ah = np.sum(I[i0+1:i1+1] * dt_int[i0+1:i1+1]) / 3600.0
    s0, s1 = v2soc(c0), v2soc(c1)
    dk = (s0 - s1) / 100.0
    if Ah <= 5 or np.any(dk < 0.25): continue
    Qk = Ah / dk
    dpack = (soc[i0] - soc[i1]) / 100.0
    runs.append(dict(odo=float(d.totalodometer.values[i1]), Ah=Ah, dsoc_bms=dpack*100,
                     Qpack=Ah/dpack if dpack > 0.2 else np.nan,
                     Qk=Qk, U=float(Qk.min()), weak=int(Qk.argmin()),
                     vmin_cell0=int(c0.argmin()), vmin_cell1=int(c1.argmin())))
R = pd.DataFrame(runs).dropna(subset=['Qpack']).reset_index(drop=True)
print('labelled discharges:', len(R))
if len(R) == 0: raise SystemExit
# drop gross outliers in labels (>5 MAD) — labelled, reported
med, mad = np.median(R.U), 1.4826*np.median(np.abs(R.U - np.median(R.U)))
keep = np.abs(R.U - med) < 5*mad
print('label outliers dropped:', int((~keep).sum()))
R = R[keep].reset_index(drop=True)
Qk_mat = np.vstack(R.Qk.values)

def trend_pred(y, W):
    """predict next value from a linear trend over the last W points (causal)."""
    p = np.full(len(y), np.nan)
    for k in range(W, len(y)):
        x = np.arange(W); yy = y[k-W:k]
        if np.isnan(yy).any(): continue
        b = np.polyfit(x, yy, 1); p[k] = np.polyval(b, W)
    return p

def evaluate(W, Qk_mat, label='U'):
    U = Qk_mat.min(axis=1)
    truth = U if label == 'U' else R.Qpack.values * np.nanmedian(U / R.Qpack.values)
    P0 = np.r_[np.nan, U[:-1]]
    ratio = np.array([np.nanmedian((U/R.Qpack.values)[max(0,k-W):k]) if k > 0 else np.nan for k in range(len(U))])
    P1 = trend_pred(R.Qpack.values, W) * ratio
    # P2: min/max view — the cell that is MIN at end-of-discharge rest, tracked as a single series
    vmin_series = np.array([Qk_mat[k, R.vmin_cell1[k]] for k in range(len(U))])
    P2 = trend_pred(vmin_series, W)
    # P3: per-cell trend, min over cells
    per = np.vstack([trend_pred(Qk_mat[:, c], W) for c in range(96)]).T
    P3 = np.nanmin(per, axis=1)
    warm = int(0.3*len(U))
    out = {}
    for name, P in [('P0', P0), ('P1', P1), ('P2', P2), ('P3', P3)]:
        e = (P - truth)[warm:]; e = e[~np.isnan(e)]
        if len(e) < 5: out[name] = None; continue
        Um = np.nanmedian(truth)
        out[name] = dict(n=int(len(e)), mae_pct=round(100*np.mean(np.abs(e))/Um, 3),
                         r95=round(100*np.quantile(-e, 0.95)/Um, 3) if len(e) else None,
                         r99=round(100*np.quantile(-e, 0.99)/Um, 3) if len(e) else None,
                         r999=round(100*np.quantile(-e, 0.999)/Um, 3) if len(e) else None)
    # head-to-head P3 vs P1
    m = ~np.isnan(P1[warm:]) & ~np.isnan(P3[warm:])
    win = float(np.mean(np.abs((P3-truth)[warm:][m]) < np.abs((P1-truth)[warm:][m]))) if m.any() else None
    return out, win, P1, P3, truth

res = {}
for W in (4, 8, 16):
    o, win, *_ = evaluate(W, Qk_mat)
    res[f'W{W}'] = dict(est=o, P3_beats_P1=win)
# shuffle control: permute cell index of each discharge's Qk independently
rng = np.random.default_rng(0)
Qsh = np.vstack([rng.permutation(row) for row in Qk_mat])
o, win, *_ = evaluate(8, Qsh); res['shuffle_W8'] = dict(est=o, P3_beats_P1=win)
# label-circularity control: score against pack-level truth
o, win, *_ = evaluate(8, Qk_mat, label='pack'); res['packtruth_W8'] = dict(est=o, P3_beats_P1=win)
# descriptive
res['_desc'] = dict(n_labels=int(len(R)), odo_range=[round(R.odo.min()), round(R.odo.max())],
                    U_median_Ah=round(float(np.median(R.U)), 2), Qpack_median_Ah=round(float(np.nanmedian(R.Qpack)), 2),
                    weak_cell_mode=int(pd.Series(R.weak).mode()[0]),
                    weak_cell_same_as_mode_pct=round(100*float(np.mean(R.weak == pd.Series(R.weak).mode()[0])), 1),
                    weak_is_endrest_vmin_pct=round(100*float(np.mean(R.weak == R.vmin_cell1)), 1),
                    cell_spread_Q_pct_median=round(100*float(np.median((Qk_mat.max(1)-Qk_mat.min(1))/Qk_mat.mean(1))), 2))
json.dump(res, open('x4_results.json', 'w'), indent=1)
for k, v in res.items(): print(k, v)
R.drop(columns='Qk').to_csv('x4_labels.csv', index=False)
