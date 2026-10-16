# Probe: in sessions WITH history, how often does any cell's voltage-headroom term bind (< its temperature cap)?
# cold (tmin_med < 10) vs warm; plus frames with Vmax >= 4200 mV.
import os, sys, numpy as np
from multiprocessing import Pool
sys.path.insert(0, "analysis")
import X2_replay as X
import H_replay as H

def one(car):
    S = [f for f in X.changan_sessions(car) if f["dah"].sum() > 0.5]
    if not S:
        return []
    h = X.changan_history(car, 0.3)
    if h["r"].size == 0:
        return []
    out = []
    for f in S:
        R, Rmm, n, ok = X.r_from(h, f["t0"], 30 * 86400.0)
        if not ok:
            continue
        R, Rmm = X._clean(R, Rmm)
        ctp = H.c_t(f["T"], 0.0)
        cap = ctp[:, H.PMAPS[0]] * X.QREF_C
        hk = X.head_k(f["V"], f["Ic"], R)
        cold = np.median(f["T"].min(1)) < 10
        out.append((cold, float((hk < cap).any(1).mean()), float((f["V"].max(1) >= X.VLIM).mean()),
                    float(np.median(f["T"].min(1))), float(f["V"].max(1).max())))
    return out

if __name__ == "__main__":
    cars = sorted(int(f[3:-4]) for f in os.listdir(H.CELLS) if f.startswith("vin") and f[3:-4].isdigit())
    with Pool(10) as p:
        R = [x for r in p.map(one, cars) for x in r]
    A = np.array(R)
    for lab, m in (("cold", A[:, 0] == 1), ("warm", A[:, 0] == 0)):
        print(lab, "n=%d" % m.sum(), "head-binds frac: med %.3f mean %.3f" % (np.median(A[m, 1]), A[m, 1].mean()),
              "| Vmax>=VLIM frac: med %.3f mean %.3f" % (np.median(A[m, 2]), A[m, 2].mean()),
              "| session max Vmax med %.0f" % np.median(A[m, 4]))
