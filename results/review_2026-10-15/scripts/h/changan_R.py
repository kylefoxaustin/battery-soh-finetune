"""Post-hoc (reviewer) model: per-cell effective resistance from Changan current steps, and a voltage-headroom
limiter that uses per-cell R vs one that uses only vmax + worst-case R. Every number DERIVED, model ASSUMED.
Usage: python changan_R.py N_CARS
"""
import sys, os, json
import numpy as np
from multiprocessing import Pool

CELLS = "<repo>/data/changan/cells"
VLIM = 4250.0          # mV, same as board VLIM for H
DI_MIN = 20.0          # A
DT_MAX = 30.0          # s between consecutive full frames
MIN_EV = 10


def one(car):
    Z = np.load(f"{CELLS}/vin{car}.npz")
    t, I, st, sync, tf = Z["t"], Z["I"].astype(float), Z["status"], Z["sync"], Z["t_full"]
    j = np.clip(np.searchsorted(t, tf), 0, len(t) - 1)
    ok = (t[j] == tf) & (st[j] == 1) & sync[j]
    rows = np.flatnonzero(ok); jj = j[rows]
    V = Z["vmean_mv"][jj][:, None] + Z["dv_full"][rows].astype(float)
    Ic = I[jj]; tt = tf[rows]
    # consecutive pairs
    dt = np.diff(tt); dI = np.diff(Ic)
    ev = np.flatnonzero((dt > 0) & (dt <= DT_MAX) & (np.abs(dI) >= DI_MIN) & np.isfinite(dI))
    if len(ev) < MIN_EV:
        return None
    dV = V[ev + 1] - V[ev]                       # [n_ev, 96] mV ; charging I<0, more negative I -> higher V
    R = dV / dI[ev][:, None]                     # mV/A = mOhm ; expect negative sign convention (dV>0 when dI<0)
    R = -R                                       # make positive for charging convention
    Rk = np.median(R, 0)                         # per-cell effective R (mOhm)
    # quality: sign consistency
    pos = (R > 0).mean()
    # headroom limiter on charging frames near the top (vmax >= 4000 mV), non-event frames
    top = np.flatnonzero(V.max(1) >= 4000)
    if len(top) == 0 or np.any(Rk <= 0):
        return {"car": car, "n_ev": int(len(ev)), "pos": float(pos), "Rk": Rk.tolist(), "n_top": 0}
    Vt, It = V[top], Ic[top]
    Rmax, Rmed = Rk.max(), np.median(Rk)
    h_cell = ((VLIM - Vt) / Rk[None, :]).min(1)                 # A of extra charge current before first cell hits VLIM
    h_mm = (VLIM - Vt.max(1)) / Rmax                             # min/max with worst-case R
    h_mm_med = (VLIM - Vt.max(1)) / Rmed                         # min/max with typical R (not guaranteed safe)
    Inow = np.clip(-It, 0, None)
    gain = (Inow + h_cell) / np.maximum(Inow + h_mm, 1e-6) - 1    # relative extra admissible current
    unsafe_med = (h_mm_med > h_cell * 1.001).mean()
    argc = ((VLIM - Vt) / Rk[None, :]).argmin(1)
    not_vmax = (argc != Vt.argmax(1)).mean()
    return {"car": car, "n_ev": int(len(ev)), "pos": float(pos), "Rk": Rk.tolist(), "n_top": int(len(top)),
            "R_med": float(Rmed), "R_max": float(Rmax), "R_min": float(Rk.min()), "R_cv": float(Rk.std() / Rmed),
            "gain_med": float(np.median(gain)), "gain_p90": float(np.percentile(gain, 90)),
            "gain_mean": float(gain.mean()), "unsafe_mm_medR": float(unsafe_med), "constr_not_vmax": float(not_vmax),
            "I_top_med": float(np.median(Inow))}


if __name__ == "__main__":
    n = int(sys.argv[1])
    cars = sorted(int(f[3:-4]) for f in os.listdir(CELLS) if f.startswith("vin"))[:n]
    with Pool(8) as p:
        R = [r for r in p.imap_unordered(one, cars) if r]
    R.sort(key=lambda r: r["car"])
    good = [r for r in R if r.get("n_top", 0) > 0]
    print(f"vehicles with >= {MIN_EV} step events: {len(R)}/{len(cars)}; with top frames & positive R: {len(good)}")
    for k in ["n_ev", "pos", "R_med", "R_max", "R_min", "R_cv", "gain_med", "gain_p90", "gain_mean", "unsafe_mm_medR",
              "constr_not_vmax", "I_top_med", "n_top"]:
        v = np.array([r[k] for r in good])
        print(f"{k:16s} median {np.median(v):.4f}  p10 {np.percentile(v,10):.4f}  p90 {np.percentile(v,90):.4f}")
    json.dump(R, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "changan_R.json"), "w"))
