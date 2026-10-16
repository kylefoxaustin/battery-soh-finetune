"""C: re-test the published per-unit RMSEs with Wilcoxon signed-rank (and sign test as a check), both label sets,
plus EVBattery; report Holm-adjusted p. Also check the 'majority' criterion with ties."""
import glob, json, math
import numpy as np
from scipy.stats import wilcoxon

ROOT = "<repo>/results/large"

def sign_test(a, b):
    d = np.asarray(a) - np.asarray(b); n_lt, n = int((d < 0).sum()), int((d != 0).sum())
    if n == 0: return 1.0
    k = min(n_lt, n - n_lt); return min(1.0, sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n * 2)

def wil(a, b):
    d = np.asarray(a) - np.asarray(b); d = d[d != 0]
    return wilcoxon(d).pvalue if len(d) >= 6 else 1.0

for flt in ("primary", "strict", "evb"):
    files = sorted(glob.glob(f"{ROOT}/rolling_{flt}_k*.json")) if flt != "evb" else [f"{ROOT}/rolling_evb_ds1.json"]
    units = [u for f in files for u in json.load(open(f))["units"]]
    print(f"===== {flt}: {len(units)} units")
    ps = []
    for bi in range(5):
        rows = [u["bands"][bi]["rmse"] for u in units if "rmse" in u["bands"][bi]]
        band = units[0]["bands"][bi]["band_km"]
        R = {m: np.array([r[m] for r in rows]) for m in rows[0]}
        out = []
        for m in ("bias", "last", "last_guard", "head_guard"):
            d = R[m] - R["frozen"]
            pw, psg = wil(R[m], R["frozen"]), sign_test(R[m], R["frozen"])
            pwp = wil(R[m], R["persist_recent"])
            ps.append((flt, band, m, pw))
            out.append(f"{m}: med d={np.median(d):+.3f} mean d={d.mean():+.3f} sign p={psg:.3g} wilcoxon p={pw:.3g} | vs persist_recent wilcoxon p={pwp:.3g}")
        print(f" band {band} n={len(rows)}"); [print("   ", o) for o in out]
    # Holm over the 20 Wilcoxon tests vs frozen
    pv = np.array([p for *_, p in ps]); order = np.argsort(pv); m = len(pv)
    holm = np.minimum.accumulate((pv[order] * (m - np.arange(m)))[::-1])[::-1]
    sig = [(ps[i][1], ps[i][2], round(pv[i], 4), round(holm[j], 4)) for j, i in enumerate(order) if holm[j] < 0.05]
    print(" Holm-significant (Wilcoxon vs frozen, either direction):", sig)
# one-shot
for flt in ("primary", "strict"):
    rows = [r for f in sorted(glob.glob(f"{ROOT}/e4_{flt}_k*.json")) for r in json.load(open(f))["per_car"]]
    R = {k: np.array([r["rmse"][k] for r in rows]) for k in rows[0]["rmse"]}
    print(f"===== one-shot {flt} n={len(rows)}")
    for m in ("bias", "last", "last_guard", "head", "head_guard"):
        print(f"   {m}: med d={np.median(R[m]-R['frozen']):+.3f} sign p={sign_test(R[m],R['frozen']):.3g} wilcoxon p={wil(R[m],R['frozen']):.3g}")
# EVBattery study 1
d = json.load(open("<repo>/results/raw/e4.json"))["per_car"]
R = {k: np.array([r["rmse"][k] for r in d]) for k in d[0]["rmse"]}
print("===== Study 1 one-shot n=20")
for m in ("bias", "last", "last_guard", "head", "head_guard"):
    print(f"   {m}: med d={np.median(R[m]-R['frozen']):+.3f} sign p={sign_test(R[m],R['frozen']):.3g} wilcoxon p={wil(R[m],R['frozen']):.3g}")
