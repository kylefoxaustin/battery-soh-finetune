"""D2: confirmatory — shrinkage factor fixed a priori from Experiment E's own variance decomposition
(kappa = sd_within^2 / sd_between^2: primary 4.11^2/2.18^2 = 3.55, strict 3.22^2/1.87^2 = 2.96), plus a stronger
no-model control (EWMA of labels, km time-constant 10k over all past labels), and the repo's full 'helps robustly'
rule (median < frozen, majority beats frozen, sign p < 0.0025 vs frozen AND vs persist_recent)."""
import json, math, sys, numpy as np, torch
from scipy.stats import wilcoxon
sys.path.insert(0, "<repo>/model")
from common import Norm, SoHNet, make_features
torch.set_num_threads(8)
STEP_KM, WINDOW_KM, MIN_WINDOW_LABELS, MIN_PAIRS, RECENT_KM = 10_000, 30_000, 5, 3, 5_000
BANDS = [(0, 5e3), (5e3, 1e4), (1e4, 2e4), (2e4, 4e4), (4e4, 8e4)]
def sign_test(a, b):
    d = np.asarray(a) - np.asarray(b); n_lt, n = int((d < 0).sum()), int((d != 0).sum())
    if n == 0: return 1.0
    k = min(n_lt, n - n_lt); return min(1.0, sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n * 2)
def wil(a, b):
    d = np.asarray(a) - np.asarray(b); d = d[d != 0]; return float(wilcoxon(d).pvalue) if len(d) >= 6 else 1.0
def frozen_preds(run, car):
    norm = Norm.from_state(json.load(open(f"{run}/norm.json"))); sd = torch.load(f"{run}/fleet.pt", map_location="cpu")
    d = np.load(f"{run}/cars/car_{car}.npz"); o = np.argsort(d["mileage"])
    km, y = d["mileage"][o].astype(np.float64), d["capacity"][o].astype(np.float64)
    X = torch.from_numpy(norm.x(make_features(d["X"][o], km))); m = SoHNet(); m.load_state_dict(sd); m.eval()
    with torch.no_grad(): pf = norm.y_inv(torch.cat([m(X[i:i + 512]) for i in range(0, len(X), 512)]).numpy()).astype(np.float64)
    return km, y, pf
def run_unit(km, y, pf, kappa):
    res = y - pf; methods = ["frozen", "bias30", "shrink_eb", "shrink_eb_ewma10", "persist30", "persist5", "ewma_label10"]
    err = {m: [[] for _ in BANDS] for m in methods}
    for tau in np.arange(km[0] + STEP_KM, km[-1], STEP_KM):
        win = np.flatnonzero((km <= tau) & (km > tau - WINDOW_KM)); past = np.flatnonzero(km <= tau); fut = np.flatnonzero(km > tau)
        if len(win) < MIN_WINDOW_LABELS or not len(fut): continue
        rec = win[km[win] > tau - RECENT_KM]; rec = rec if len(rec) else win[-1:]
        n = len(win); w = np.exp(-(tau - km[past]) / 10_000.0); neff = w.sum() ** 2 / (w ** 2).sum()
        P = {"frozen": pf, "bias30": pf + res[win].mean(), "shrink_eb": pf + res[win].mean() * n / (n + kappa),
             "shrink_eb_ewma10": pf + ((w * res[past]).sum() / w.sum()) * neff / (neff + kappa),
             "persist30": np.full_like(pf, y[win].mean()), "persist5": np.full_like(pf, y[rec].mean()),
             "ewma_label10": np.full_like(pf, (w * y[past]).sum() / w.sum())}
        for bi, (lo, hi) in enumerate(BANDS):
            sel = fut[(km[fut] > tau + lo) & (km[fut] <= tau + hi)]
            for m in methods: err[m][bi].extend((P[m][sel] - y[sel]).tolist())
    bands = []
    for bi in range(len(BANDS)):
        n = len(err["frozen"][bi]); row = {"n_pairs": n}
        if n >= MIN_PAIRS: row["rmse"] = {m: float(np.sqrt(np.mean(np.square(err[m][bi])))) for m in methods}
        bands.append(row)
    return bands, methods
for flt, kappa in (("primary", 4.11 ** 2 / 2.18 ** 2), ("strict", 3.22 ** 2 / 1.87 ** 2)):
    units = []
    for k in range(4):
        run = f"<repo>/runs/chf_{flt}_k{k}"
        for car in json.load(open(f"{run}/split.json"))["targets"]:
            km, y, pf = frozen_preds(run, car); bands, methods = run_unit(km, y, pf, kappa); units.append(bands)
    print(f"\n===== Changan {flt}: kappa = {kappa:.2f} (from E_power_analysis.md), {len(units)} units; Bonferroni alpha 0.0025")
    for bi, band in enumerate(BANDS):
        rows = [u[bi]["rmse"] for u in units if "rmse" in u[bi]]; R = {m: np.array([r[m] for r in rows]) for m in methods}; n = len(rows)
        print(f" band {band} n={n} frozen {np.median(R['frozen']):.3f}")
        for m in methods[1:]:
            bf, bp = int((R[m] < R["frozen"]).sum()), int((R[m] < R["persist5"]).sum()); pf_, pp = sign_test(R[m], R["frozen"]), sign_test(R[m], R["persist5"])
            robust = np.median(R[m]) < np.median(R["frozen"]) and bf > n / 2 and pf_ < 0.0025 and bp > n / 2 and pp < 0.0025
            print(f"   {m:17s} med {np.median(R[m]):.3f} ({np.median(100*(R[m]/R['frozen']-1)):+.1f}%; mean paired dRMSE {np.mean(R[m]-R['frozen']):+.3f}) beats frozen {bf}/{n} sign p={pf_:.2g} wilc p={wil(R[m],R['frozen']):.2g} | vs persist5 {bp}/{n} sign p={pp:.2g} | HELPS ROBUSTLY: {robust}")
