"""Review: how much of the Changan within-unit label scatter is irreducible session-to-session noise, and how much is
explained by SESSION covariates the E pre-check excluded by design (soc_s, charge current, segment length, start/end
temperature)?  Also: label-rise mechanism for the F post-hoc D3 vehicles.
Usage: python -I label_noise.py <labels_full_dir> <events_json> <diag_json>
"""
import json
import os
import sys

import numpy as np

lab_dir, ev_json, diag_json = sys.argv[1:4]
rows = []
for f in sorted(os.listdir(lab_dir)):
    L = np.load(os.path.join(lab_dir, f))
    n = len(L["capacity"])
    car = int(L["car"][0])
    X = L["X"]
    rows.append(dict(car=np.full(n, car), km=L["mileage"].astype(float), t=L["t_end"], cap=L["capacity"].astype(float),
                     soc_s=L["soc_s"].astype(float), ah=L["ah"].astype(float), I=L["charge_current"].astype(float),
                     seg=L["seg_s"].astype(float), tmax_end=X[:, -1, 5].astype(float), tmin_end=X[:, -1, 6].astype(float),
                     tmax0=X[:, 0, 5].astype(float), vmax_end=X[:, -1, 3].astype(float), soc_bms_end=X[:, -1, 2].astype(float)))
A = {k: np.concatenate([r[k] for r in rows]) for k in rows[0]}
# primary-like filter: fast-charge labels 48-51 A, 95-145 Ah (dossier §2.2)
prim = (A["I"] >= 48) & (A["I"] <= 51) & (A["cap"] >= 95) & (A["cap"] <= 145)
print("all labels", len(A["cap"]), "primary-band", prim.sum(), file=sys.stderr)


def within_unit(mask, min_n=20):
    """deviation of each label from its unit's linear-in-km fit (the noise_floor definition), per unit"""
    dev, keep, unit_sd = np.zeros(mask.sum()), np.zeros(mask.sum(), bool), {}
    idx = np.flatnonzero(mask)
    cars = A["car"][idx]
    for c in np.unique(cars):
        m = cars == c
        if m.sum() < min_n:
            continue
        km, y = A["km"][idx][m], A["cap"][idx][m]
        b = np.polyfit(km, y, 1)
        dev[m] = y - np.polyval(b, km)
        keep[m] = True
        unit_sd[int(c)] = float(dev[m].std(ddof=2))
    return idx[keep], dev[keep], unit_sd


idx, dev, usd = within_unit(prim)
print(f"primary-band units>=20 labels: {len(usd)}, labels {len(idx)}, median per-unit SD about linear fit "
      f"{np.median(list(usd.values())):.2f} Ah, pooled SD {dev.std():.2f} Ah")

# 1. close-pair noise: consecutive labels of the same unit within DK km and DT days -> SD(diff)/sqrt(2)
for DK, DT in [(300, 20), (1000, 45), (2000, 90)]:
    d = []
    for c in np.unique(A["car"][idx]):
        m = idx[A["car"][idx] == c]
        o = m[np.argsort(A["km"][m])]
        for a_, b_ in zip(o[:-1], o[1:]):
            if abs(A["km"][b_] - A["km"][a_]) <= DK and abs(A["t"][b_] - A["t"][a_]) <= DT * 86400:
                d.append(A["cap"][b_] - A["cap"][a_])
    d = np.array(d)
    mad = 1.4826 * np.median(np.abs(d - np.median(d)))
    print(f"close pairs (<= {DK} km, <= {DT} d): n={len(d)}, SD(diff)/sqrt2 = {d.std() / np.sqrt(2):.2f} Ah, "
          f"robust (MAD) = {mad / np.sqrt(2):.2f} Ah")

# 2. what session covariates explain of the within-unit deviation (OLS, in-sample; by-unit CV too)
F = np.c_[A["soc_s"][idx], A["I"][idx], np.log(A["seg"][idx]), A["tmax_end"][idx], A["tmax_end"][idx] - A["tmin_end"][idx],
          A["tmax0"][idx], A["vmax_end"][idx], A["soc_bms_end"][idx]]
names = ["soc_s", "I_chg", "log_seg_s", "tmax_end", "tspread_end", "tmax_start128", "vmax_end", "soc_bms_end"]
ok = np.isfinite(F).all(1)
F, y, cars = F[ok], dev[ok], A["car"][idx][ok]
for i, nm in enumerate(names):
    print(f"  corr(dev, {nm}) = {np.corrcoef(F[:, i], y)[0, 1]:+.3f}")
Xd = np.c_[np.ones(len(y)), (F - F.mean(0)) / F.std(0)]
b, *_ = np.linalg.lstsq(Xd, y, rcond=None)
r2 = 1 - ((y - Xd @ b) ** 2).sum() / ((y - y.mean()) ** 2).sum()
print(f"in-sample R2 of within-unit deviation on 8 session covariates: {r2:.3f}")
# 4-fold by unit CV
uc = np.unique(cars); rng = np.random.default_rng(0); rng.shuffle(uc); fold = {c: i % 4 for i, c in enumerate(uc)}
fv = np.array([fold[c] for c in cars]); yhat = np.zeros_like(y)
for k in range(4):
    tr, te = fv != k, fv == k
    bb, *_ = np.linalg.lstsq(Xd[tr], y[tr], rcond=None); yhat[te] = Xd[te] @ bb
print(f"out-of-fold (by unit) R2: {1 - ((y - yhat) ** 2).sum() / ((y - y.mean()) ** 2).sum():.3f}")
# soc_s alone, quadratic
Xs = np.c_[np.ones(len(y)), F[:, 0], F[:, 0] ** 2]
bs, *_ = np.linalg.lstsq(Xs, y, rcond=None)
print(f"R2 soc_s quadratic alone: {1 - ((y - Xs @ bs) ** 2).sum() / ((y - y.mean()) ** 2).sum():.3f}; "
      f"soc_s range p5-p95 {np.percentile(F[:, 0], [5, 95])}")
# binned: mean dev by soc_s decile
q = np.percentile(F[:, 0], np.linspace(0, 100, 11))
for lo, hi in zip(q[:-1], q[1:]):
    m = (F[:, 0] >= lo) & (F[:, 0] <= hi)
    print(f"   soc_s {lo:5.1f}-{hi:5.1f}%: mean dev {y[m].mean():+.2f} Ah (n={m.sum()})")

# 3. label-rise mechanism for D3 vehicles: before/after onset medians of cap, soc_s, ah, I, seg
D = json.load(open(diag_json))["D3"]["per_vehicle"]
W = 180 * 86400
print("\nlabel-rise decomposition (all labels of the vehicle, +-180 d around onset; medians before -> after):")
for r in D:
    c = r["car"]; m = A["car"] == c; t0 = r["onset_day"] * 86400.0
    b = m & (A["t"] >= t0 - W) & (A["t"] < t0); a_ = m & (A["t"] > t0) & (A["t"] <= t0 + W)
    def med(k, s):
        return float(np.median(A[k][s])) if s.sum() else float("nan")
    print(f" vin{c:3d} n={b.sum()}/{a_.sum()}  cap {med('cap', b):6.1f}->{med('cap', a_):6.1f}  soc_s {med('soc_s', b):5.1f}->{med('soc_s', a_):5.1f}"
          f"  ah {med('ah', b):5.1f}->{med('ah', a_):5.1f}  I {med('I', b):5.1f}->{med('I', a_):5.1f}  seg_h {med('seg', b) / 3600:5.1f}->{med('seg', a_) / 3600:5.1f}"
          f"  tmax_end {med('tmax_end', b):4.1f}->{med('tmax_end', a_):4.1f}  km {med('km', b) / 1e3:5.1f}->{med('km', a_) / 1e3:5.1f}k")
