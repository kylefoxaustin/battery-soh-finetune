"""D: closed-form per-unit adaptation methods in the SAME rolling protocol as analysis/rolling.py (same origins,
same windows, same (origin,label) pairs, same bands), using the repo's trained fleet models for frozen
predictions. No training. Methods only ever see labels with odometer <= tau.

Methods:
  frozen          fleet model
  bias30          + mean residual over the 30 k km window           (== rolling.py 'bias')
  bias5           + mean residual over the last 5 k km of history   (fallback: last label)
  ewma10 / ewma5  + EWMA of ALL past residuals, km time-constant 10k / 5k
  shrink30_k      + window mean residual * n/(n+k), k in {2,5}
  kalman          + random-walk offset, q = (1 Ah)^2 per 10 k km, r = fleet noise var (4.76^2 Changan / 0.65^2 EVB)
  persist30 / persist5  label mean over window / last 5 k km         (== 'persist' / 'persist_recent')
  trend30         linear fit of labels vs km over the window, extrapolated (no model)
  oracle_bias     + mean residual over ALL the unit's labels (uses the future; an upper bound, not a method)
"""
import glob, json, math, os, sys
import numpy as np, torch
from scipy.stats import wilcoxon
sys.path.insert(0, "<repo>/model")
from common import Norm, SoHNet, make_features  # noqa

torch.set_num_threads(8)
STEP_KM, WINDOW_KM, MIN_WINDOW_LABELS, MIN_PAIRS, RECENT_KM = 10_000, 30_000, 5, 3, 5_000
BANDS = [(0, 5e3), (5e3, 1e4), (1e4, 2e4), (2e4, 4e4), (4e4, 8e4)]
OUT = "/tmp/claude-1000/-home-kyle-Documents-GitHub-batt-finetune/8fc251be-e160-42c8-b7ad-d2301080f5cc/scratchpad/review/s12"

def sign_test(a, b):
    d = np.asarray(a) - np.asarray(b); n_lt, n = int((d < 0).sum()), int((d != 0).sum())
    if n == 0: return 1.0
    k = min(n_lt, n - n_lt); return min(1.0, sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n * 2)

def wil(a, b):
    d = np.asarray(a) - np.asarray(b); d = d[d != 0]
    return float(wilcoxon(d).pvalue) if len(d) >= 6 else 1.0

def run_unit(km, y, pf, r_noise):
    res = y - pf
    err = {}
    def add(name, pred, sel):
        err.setdefault(name, [[] for _ in BANDS])
        return pred
    methods = ["frozen", "bias30", "bias5", "ewma10", "ewma5", "shrink30_k2", "shrink30_k5", "kalman", "persist30", "persist5", "trend30", "oracle_bias"]
    err = {m: [[] for _ in BANDS] for m in methods}
    oracle = pf + res.mean()
    n_orig = 0
    for tau in np.arange(km[0] + STEP_KM, km[-1], STEP_KM):
        win = np.flatnonzero((km <= tau) & (km > tau - WINDOW_KM)); past = np.flatnonzero(km <= tau); fut = np.flatnonzero(km > tau)
        if len(win) < MIN_WINDOW_LABELS or not len(fut): continue
        n_orig += 1
        rec = win[km[win] > tau - RECENT_KM]; rec = rec if len(rec) else win[-1:]
        P = {"frozen": pf, "oracle_bias": oracle}
        P["bias30"] = pf + res[win].mean(); P["bias5"] = pf + res[rec].mean()
        for name, tc in (("ewma10", 10_000.0), ("ewma5", 5_000.0)):
            w = np.exp(-(tau - km[past]) / tc); P[name] = pf + (w * res[past]).sum() / w.sum()
        n = len(win)
        P["shrink30_k2"] = pf + res[win].mean() * n / (n + 2); P["shrink30_k5"] = pf + res[win].mean() * n / (n + 5)
        # Kalman random-walk offset over the whole past
        b, Pv, q, r = 0.0, 1e6, (1.0 ** 2) / 10_000.0, r_noise ** 2
        last_km = km[past][0]
        for i in past:
            Pv += q * (km[i] - last_km); last_km = km[i]
            K = Pv / (Pv + r); b += K * (res[i] - b); Pv *= (1 - K)
        P["kalman"] = pf + b
        P["persist30"] = np.full_like(pf, y[win].mean()); P["persist5"] = np.full_like(pf, y[rec].mean())
        c = np.polyfit(km[win], y[win], 1) if np.ptp(km[win]) > 0 else np.array([0.0, y[win].mean()])
        P["trend30"] = np.polyval(c, km)
        for bi, (lo, hi) in enumerate(BANDS):
            sel = fut[(km[fut] > tau + lo) & (km[fut] <= tau + hi)]
            for m in methods: err[m][bi].extend((P[m][sel] - y[sel]).tolist())
    bands = []
    for bi in range(len(BANDS)):
        n = len(err["frozen"][bi]); row = {"n_pairs": n}
        if n >= MIN_PAIRS: row["rmse"] = {m: float(np.sqrt(np.mean(np.square(err[m][bi])))) for m in methods}
        bands.append(row)
    return bands, n_orig, methods

def frozen_preds(run, car):
    norm = Norm.from_state(json.load(open(f"{run}/norm.json"))); sd = torch.load(f"{run}/fleet.pt", map_location="cpu")
    split = json.load(open(f"{run}/split.json")); use_km = split.get("mileage_input", True)
    d = np.load(f"{run}/cars/car_{car}.npz"); o = np.argsort(d["mileage"])
    km, y = d["mileage"][o].astype(np.float64), d["capacity"][o].astype(np.float64)
    X = torch.from_numpy(norm.x(make_features(d["X"][o], km if use_km else np.zeros_like(km))))
    m = SoHNet(); m.load_state_dict(sd); m.eval()
    with torch.no_grad():
        pf = norm.y_inv(torch.cat([m(X[i:i + 512]) for i in range(0, len(X), 512)]).numpy()).astype(np.float64)
    return km, y, pf

def summarize(units, methods, tag, check=None):
    print(f"\n===== {tag}: {len(units)} units")
    out = {}
    for bi, band in enumerate(BANDS):
        rows = [u["bands"][bi]["rmse"] for u in units if "rmse" in u["bands"][bi]]
        R = {m: np.array([r[m] for r in rows]) for m in methods}
        n = len(rows)
        print(f" band {band} n={n}  frozen med {np.median(R['frozen']):.3f}")
        if check is not None:
            # compare with the repo's own rolling JSON for the same units
            cb = check[bi]
            print(f"   [repo rolling json] frozen {cb['frozen']:.3f} bias {cb['bias']:.3f} persist {cb['persist']:.3f} persist_recent {cb['persist_recent']:.3f}")
        for m in methods:
            if m == "frozen": continue
            bf = int((R[m] < R["frozen"]).sum()); bp = int((R[m] < R["persist5"]).sum())
            print(f"   {m:12s} med {np.median(R[m]):.3f} ({np.median(100*(R[m]/R['frozen']-1)):+.1f}%)  beats frozen {bf}/{n} sign p={sign_test(R[m],R['frozen']):.3g} wilc p={wil(R[m],R['frozen']):.3g} | beats persist5 {bp}/{n} wilc p={wil(R[m],R['persist5']):.3g}")
        out[str(band)] = {m: {"median": float(np.median(R[m])), "beats_frozen": int((R[m] < R["frozen"]).sum()), "sign_p": sign_test(R[m], R["frozen"]), "wil_p": wil(R[m], R["frozen"]), "wil_p_vs_persist5": wil(R[m], R["persist5"]), "beats_persist5": int((R[m] < R["persist5"]).sum())} for m in methods}
    return out

results = {}
for flt, r_noise in (("primary", 4.76), ("strict", 3.84)):
    units = []
    repo = [u for k in range(4) for u in json.load(open(f"<repo>/results/large/rolling_{flt}_k{k}.json"))["units"]]
    for k in range(4):
        run = f"<repo>/runs/chf_{flt}_k{k}"
        for car in json.load(open(f"{run}/split.json"))["targets"]:
            km, y, pf = frozen_preds(run, car)
            bands, n_orig, methods = run_unit(km, y, pf, r_noise)
            units.append({"car": car, "bands": bands, "n_origins": n_orig})
    check = []
    for bi in range(5):
        rows = [u["bands"][bi]["rmse"] for u in repo if "rmse" in u["bands"][bi]]
        check.append({m: float(np.median([r[m] for r in rows])) for m in ("frozen", "bias", "persist", "persist_recent")})
    results[flt] = summarize(units, methods, f"Changan {flt}", check)

# EVBattery ds1 (Study-1 model, its 20 held-out cars)
run = "<repo>/runs/ds1"
units = []
for car in json.load(open(f"{run}/split.json"))["targets"]:
    km, y, pf = frozen_preds(run, car)
    bands, n_orig, methods = run_unit(km, y, pf, 0.65)
    units.append({"car": car, "bands": bands, "n_origins": n_orig})
    print("evb car", car, "origins", n_orig, flush=True)
repo = json.load(open("<repo>/results/large/rolling_evb_ds1.json"))["units"]
check = []
for bi in range(5):
    rows = [u["bands"][bi]["rmse"] for u in repo if "rmse" in u["bands"][bi]]
    check.append({m: float(np.median([r[m] for r in rows])) for m in ("frozen", "bias", "persist", "persist_recent")})
results["evb_ds1"] = summarize(units, methods, "EVBattery ds1", check)
json.dump(results, open(f"{OUT}/d_closed_form.json", "w"), indent=1)
print("DONE")
