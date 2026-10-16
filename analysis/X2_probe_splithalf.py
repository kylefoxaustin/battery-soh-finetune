# Probe: is per-cell R_k cross-cell structure reproducible (split-half), or estimation noise?
import os, sys, numpy as np
from multiprocessing import Pool
sys.path.insert(0, "analysis")
import X2_replay as X
import H_replay as H
from scipy.stats import spearmanr

def one(car):
    h = X.changan_history(car, 0.3)
    r = h["r"]
    if r.shape[0] < 80:
        return None
    ok = np.isfinite(r).all(1)
    r = r[ok]
    n = len(r)
    out = {"car": car, "n": n}
    for nm, (a, b) in {"oddeven": (r[0::2], r[1::2]), "time": (r[: n // 2], r[n // 2:])}.items():
        ma, mb = np.median(a, 0), np.median(b, 0)
        out[nm + "_rho"] = spearmanr(ma, mb).correlation
        out[nm + "_top_same"] = int(np.argmax(ma) == np.argmax(mb))
        out[nm + "_top_in_top5"] = int(np.argmax(mb) in np.argsort(ma)[-5:])
    m = np.median(r, 0)
    out["max_over_med"] = float(m.max() / np.median(m))
    out["sd_over_med"] = float(np.std(m) / np.median(m))
    return out

if __name__ == "__main__":
    cars = sorted(int(f[3:-4]) for f in os.listdir(H.CELLS) if f.startswith("vin") and f[3:-4].isdigit())
    with Pool(10) as p:
        R = [x for x in p.map(one, cars) if x]
    import json
    for k in ["oddeven_rho", "time_rho", "oddeven_top_same", "time_top_same", "time_top_in_top5", "max_over_med", "sd_over_med"]:
        v = np.array([x[k] for x in R], float)
        print(k, "n=%d" % len(v), "p10 %.3f med %.3f p90 %.3f mean %.3f" % (np.nanpercentile(v, 10), np.nanmedian(v), np.nanpercentile(v, 90), np.nanmean(v)))
    print("steps median", np.median([x["n"] for x in R]))
