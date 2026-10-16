import sys, numpy as np
sys.path.insert(0, "<repo>/analysis")
import G2_beihang as G
np.set_printoptions(precision=4, suppress=True, linewidth=160)
R = "<repo>/data/raw/beihang/x"
for mk, n in [("QAS", 0), ("QAS", 360), ("DTI", 0)]:
    print("=====", mk, n)
    for f in ("vin_1", "vin_2", "vin_3"):
        a = G.load(f"{R}/{mk}/{n}/{f}.pkl")
        print(f, a.shape, a.dtype)
    b = G.load(f"{R}/{mk}/{n}/vin_2.pkl")
    k = G.MAKERS[mk]["k"]
    x = b[:, :2]; y = b[:, 2:2+k]; z = b[:, 2+k:2+2*k]; q = b[:, 2+2*k:]
    print("x cols: min", x.min(0), "max", x.max(0), "nunique", [len(np.unique(x[:, i])) for i in range(2)])
    print("x first rows", x[:5]); print("x last rows", x[-3:])
    print("y: min %.3f max %.3f median %.3f ; per-frame range median %.4f" % (y.min(), y.max(), np.median(y), np.median(y.max(1)-y.min(1))))
    print("z: min %.3f max %.3f median %.3f ; per-frame range median %.4f ; nunique %d" % (z.min(), z.max(), np.median(z), np.median(z.max(1)-z.min(1)), len(np.unique(z))))
    print("q cols min", q.min(0), "max", q.max(0), "nunique", [len(np.unique(q[:, i])) for i in range(q.shape[1])])
    print("q first rows", q[:5])
    # resolution of y
    yy = np.unique(np.round(y, 6)); print("y unique values", len(yy), "min diff", np.min(np.diff(yy)) if len(yy) > 1 else None, yy[:5])
    zz = np.unique(z); print("z unique values", zz[:20])
    # row-order check: SOC continuity
    soc = q[:, 1]; print("SOC abs diff quantiles", np.quantile(np.abs(np.diff(soc)), [0.5, 0.9, 0.99, 1.0]))
    # vin_1 vs vin_2
    a1 = G.load(f"{R}/{mk}/{n}/vin_1.pkl").reshape(len(b), -1)
    print("vin_1 cols", a1.shape, "col ranges", a1.min(0)[:6], a1.max(0)[:6])
    a3 = G.load(f"{R}/{mk}/{n}/vin_3.pkl")
    print("vin_3", a3.shape, "ranges", a3.min(0)[:6], a3.max(0)[:6], "equal to vin_2?", np.allclose(a3.reshape(b.shape), b) if a3.size == b.size else "diff size")
