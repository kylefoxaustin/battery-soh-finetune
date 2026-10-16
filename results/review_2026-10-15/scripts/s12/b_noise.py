"""B: noise-floor decomposition. Reproduce the 4.76 Ah 'noise floor' (SD about per-unit linear fit vs odometer) on the
94 primary target units, then ask how much of it is explained by label covariates the model's inputs carry
(charge temperature, start SOC, end current, segment duration, season)."""
import glob, json
import numpy as np

ROOT = "<repo>"
CAP_LO, CAP_HI = 95.0, 145.0
targets = set()
for k in range(4):
    targets |= set(json.load(open(f"{ROOT}/runs/chf_primary_k{k}/split.json"))["targets"])
print("primary targets:", len(targets))

rows = {"sd_lin": [], "sd_lin_dof": [], "sd_cov": [], "sd_cov_dof": [], "sd_cov_fleet": [], "n": [], "r2_cov": [],
        "sd_mad": [], "fade": []}
units = []
for f in sorted(glob.glob(f"{ROOT}/data/changan/labels_full/vin*.npz")):
    d = np.load(f)
    vin = int(d["car"][0])
    if vin not in targets:
        continue
    iend = -d["X"][:, -1, 1]
    m = (iend >= 48) & (iend <= 51) & np.isfinite(d["mileage"]) & np.isfinite(d["capacity"])
    m &= (d["capacity"] >= CAP_LO) & (d["capacity"] <= CAP_HI)
    km, y = d["mileage"][m].astype(float), d["capacity"][m].astype(float)
    tmean = d["X"][m][:, :, 5].mean(1).astype(float)
    tmin = d["X"][m][:, :, 6].mean(1).astype(float)
    soc_s, seg_s, I = d["soc_s"][m].astype(float), d["seg_s"][m].astype(float), d["charge_current"][m].astype(float)
    t_end = d["t_end"][m].astype(float)
    doy = (t_end / 86400.0) % 365.25
    n = len(y)
    assert n >= 20 and np.ptp(km) >= 50_000, (vin, n, np.ptp(km))
    A = np.c_[km, np.ones(n)]
    r_lin = y - A @ np.linalg.lstsq(A, y, rcond=None)[0]
    C = np.c_[km, np.ones(n), tmean, tmin, soc_s, np.log(seg_s), I, np.sin(2 * np.pi * doy / 365.25), np.cos(2 * np.pi * doy / 365.25)]
    coef = np.linalg.lstsq(C, y, rcond=None)[0]
    r_cov = y - C @ coef
    units.append(dict(vin=vin, km=km, y=y, cov=C[:, 2:], r_lin=r_lin))
    rows["n"].append(n)
    rows["sd_lin"].append(r_lin.std())
    rows["sd_lin_dof"].append(np.sqrt((r_lin ** 2).sum() / (n - 2)))
    rows["sd_cov"].append(r_cov.std())
    rows["sd_cov_dof"].append(np.sqrt((r_cov ** 2).sum() / (n - C.shape[1])))
    rows["r2_cov"].append(1 - (r_cov ** 2).sum() / (r_lin ** 2).sum())
    rows["sd_mad"].append(1.4826 * np.median(np.abs(r_lin - np.median(r_lin))))
    rows["fade"].append(-np.polyfit(km, y, 1)[0] * np.ptp(km))
R = {k: np.array(v) for k, v in rows.items()}
print(f"n units {len(R['n'])}, labels/unit median {np.median(R['n']):.0f}")
print(f"noise SD about linear fit (as published): median {np.median(R['sd_lin']):.3f}  (dossier 4.76); MAD-based {np.median(R['sd_mad']):.3f} (dossier 3.91)")
print(f"same with dof correction (n-2): median {np.median(R['sd_lin_dof']):.3f}")
print(f"residual SD after per-unit covariate OLS (9 params): median {np.median(R['sd_cov']):.3f}; dof-corrected {np.median(R['sd_cov_dof']):.3f}; within-unit R2 of covariates median {np.median(R['r2_cov']):.3f}")
print(f"fade median {np.median(R['fade']):.2f} Ah (dossier 6.5)")

# Fleet-wise (out-of-unit) covariate model: fit a single covariate correction on all OTHER target units' linear
# residuals, apply to this unit -> honest estimate of how much 'noise' a fleet model with these inputs can remove.
allC = np.vstack([np.c_[u["cov"], np.ones(len(u["y"]))] for u in units]); allr = np.concatenate([u["r_lin"] for u in units])
owner = np.concatenate([[i] * len(u["y"]) for i, u in enumerate(units)])
sd_oof = []
for i, u in enumerate(units):
    msk = owner != i
    beta = np.linalg.lstsq(allC[msk], allr[msk], rcond=None)[0]
    pred = np.c_[u["cov"], np.ones(len(u["y"]))] @ beta
    # re-fit the unit's own linear trend after removing the fleet covariate effect
    y2 = u["y"] - pred
    A = np.c_[u["km"], np.ones(len(y2))]
    r = y2 - A @ np.linalg.lstsq(A, y2, rcond=None)[0]
    sd_oof.append(r.std())
sd_oof = np.array(sd_oof)
print(f"residual SD after OUT-OF-UNIT fleet covariate correction (then own linear trend): median {np.median(sd_oof):.3f}; units improved {(sd_oof < R['sd_lin']).sum()}/{len(sd_oof)}")
beta = np.linalg.lstsq(allC, allr, rcond=None)[0]
names = ["tmean", "tmin", "soc_s", "log_seg_s", "I_end", "sin_doy", "cos_doy", "const"]
print("fleet covariate coefficients on linear residual (Ah per unit):", {n: round(b, 3) for n, b in zip(names, beta)})
# fraction of units whose one-shot frozen RMSE is below their own noise SD
e4 = [r for k in range(4) for r in json.load(open(f"{ROOT}/results/large/e4_primary_k{k}.json"))["per_car"]]
fz = {r["car"]: r["rmse"]["frozen"] for r in e4}
sdmap = {u["vin"]: s for u, s in zip(units, R["sd_lin"])}
below = sum(fz[v] < sdmap[v] for v in fz if v in sdmap)
print(f"one-shot frozen RMSE below the unit's own 'noise floor' SD in {below}/{len(fz)} units; median ratio frozen/noise {np.median([fz[v]/sdmap[v] for v in fz if v in sdmap]):.3f}")
