"""Experiment E §3 — power analysis BEFORE any bound is modelled. Changan part.

Re-scores the already-trained frozen fleet models (runs/chf_{primary,strict}_k{0..3}) on their held-out target
units — no new training, no bound estimator fitted — and answers:

  1. variance decomposition of fleet residuals r = label - frozen_pred over held-out units:
     between-unit (persistent per-unit offset, the only thing per-unit history could remove) vs within-unit,
     and how much of within-unit is label noise (noise floor from dataset_profile.md).
  2. ORACLE upper bound on tightening: fleet bound offset = -Q_alpha(r) pooled over units (unit-balanced weights)
     vs per-unit bounds that are told each unit's TRUE mean offset (and, for the shift+scale oracle, its true
     spread) from the test data itself. Real estimators can only do worse than an oracle. All DERIVED.
  3. is coverage at alpha verifiable? Cluster bootstrap (units) of the realized violation rate of an exactly
     calibrated bound -> CI width per alpha; expected violation counts.
  4. resolvability of a per-unit tightening (gap L_b - L_a) with the realistic 'bias' estimator from k early labels,
     paired across units: minimum detectable gap at Bonferroni alpha', 80 % power.

Everything is relative to DERIVED labels: a "violation" is label < bound. A bound on TRUE capacity cannot be
gated against labels whose noise (~3-4 %) is the same size as the effect (§3 of the brief).
Usage: python analysis/E_power.py --out results/E/power_changan.json
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "model"))

import numpy as np  # noqa: E402
import torch  # noqa: E402
from scipy import stats  # noqa: E402

from common import Norm, SoHNet, make_features  # noqa: E402

ALPHAS = [0.10, 0.05, 0.01, 0.001]   # candidates evaluated; the brief's example is 0.001
K_EARLY = [5, 10, 20]                # labels of per-unit history for the realistic bias estimator
N_BOOT = 2000
SEED = 0


def residuals(run):
    norm = Norm.from_state(json.load(open(os.path.join(run, "norm.json"))))
    sd = torch.load(os.path.join(run, "fleet.pt"), map_location="cpu")
    split = json.load(open(os.path.join(run, "split.json")))
    net = SoHNet(); net.load_state_dict(sd); net.eval()
    out = []
    for car in split["targets"]:
        d = np.load(os.path.join(run, "cars", f"car_{car}.npz"))
        o = np.argsort(d["mileage"])
        km, y = d["mileage"][o].astype(np.float64), d["capacity"][o].astype(np.float64)
        X = torch.from_numpy(norm.x(make_features(d["X"][o], km)))
        with torch.no_grad():
            p = np.concatenate([norm.y_inv(net(X[i:i + 256]).squeeze(-1).numpy()) for i in range(0, len(X), 256)])
        out.append({"car": int(car), "km": km, "y": y, "p": p.astype(np.float64)})
    return out


def wquantile(x, w, q):
    o = np.argsort(x)
    c = np.cumsum(w[o]) / w.sum()
    return float(x[o][np.searchsorted(c, q)])


def pooled(units, f):
    x = np.concatenate([f(u) for u in units])
    w = np.concatenate([np.full(len(f(u)), 1.0 / len(f(u))) for u in units])
    return x, w


def analyse(units, c_nom, noise_sd):
    rng = np.random.default_rng(SEED)
    r_all = [u["y"] - u["p"] for u in units]
    n_u = np.array([len(r) for r in r_all])
    means = np.array([r.mean() for r in r_all])
    sds = np.array([r.std(ddof=1) for r in r_all])
    # one-way random effects (method of moments, unbalanced)
    N, U = n_u.sum(), len(units)
    grand = np.concatenate(r_all).mean()
    msw = sum(((r - r.mean()) ** 2).sum() for r in r_all) / (N - U)
    msb = (n_u * (means - grand) ** 2).sum() / (U - 1)
    n0 = (N - (n_u ** 2).sum() / N) / (U - 1)
    var_b = max(0.0, (msb - msw) / n0)
    res = {"n_units": U, "n_labels": int(N), "labels_per_unit_median": float(np.median(n_u)),
           "resid_mean": float(grand), "sd_between": float(np.sqrt(var_b)), "sd_within": float(np.sqrt(msw)),
           "frac_var_between": float(var_b / (var_b + msw)), "label_noise_sd": noise_sd,
           "frac_within_that_is_label_noise": float(min(1.0, noise_sd ** 2 / msw)),
           "icc_F_p": float(stats.f.sf(msb / msw, U - 1, N - U)), "alphas": {}}

    for a in ALPHAS:
        # fleet bound: one offset for everyone (calibrated in-sample: the most favourable case for (a) too)
        r, w = pooled(units, lambda u: u["y"] - u["p"])
        q_fleet = -wquantile(r, w, a)
        # oracle shift: unit told its own true mean offset
        r1, w1 = pooled(units, lambda u: (u["y"] - u["p"]) - (u["y"] - u["p"]).mean())
        q_shift = -wquantile(r1, w1, a)
        gap_shift = np.array([(m - q_shift) - (-q_fleet) for m in means])  # L_b - L_a per unit, Ah
        # oracle shift+scale: unit told its own mean and sd; bound = m - k*sd, k calibrated to pooled alpha
        z, wz = pooled(units, lambda u: ((u["y"] - u["p"]) - (u["y"] - u["p"]).mean()) / (u["y"] - u["p"]).std(ddof=1))
        k = -wquantile(z, wz, a)
        gap_scale = np.array([(m - k * s) + q_fleet for m, s in zip(means, sds)])
        # floor: a perfect predictor of TRUE capacity still faces label noise when gated against labels
        floor = -stats.norm.ppf(a) * noise_sd
        # coverage verifiability: exactly calibrated fleet bound, cluster bootstrap of realized alpha
        viol = [((u["y"] - u["p"]) < -q_fleet).astype(float) for u in units]
        rate = lambda idx: np.mean([viol[i].mean() for i in idx])  # noqa: E731
        boots = np.array([rate(rng.integers(0, U, U)) for _ in range(N_BOOT)])
        lo, hi = np.percentile(boots, [2.5, 97.5])
        res["alphas"][str(a)] = {
            "fleet_offset_ah": q_fleet, "fleet_buffer_pct": 100 * q_fleet / c_nom,
            "label_noise_floor_offset_ah": float(floor), "label_noise_floor_pct": float(100 * floor / c_nom),
            "oracle_shift_offset_ah": q_shift,
            "oracle_shift_recovered_pct_median": float(100 * np.median(gap_shift) / c_nom),
            "oracle_shift_recovered_pct_mean": float(100 * np.mean(gap_shift) / c_nom),
            "oracle_shift_units_tighter": int((gap_shift > 0).sum()),
            "oracle_shift_scale_recovered_pct_median": float(100 * np.median(gap_scale) / c_nom),
            "oracle_shift_scale_recovered_pct_mean": float(100 * np.mean(gap_scale) / c_nom),
            "oracle_shift_scale_units_tighter": int((gap_scale > 0).sum()),
            "expected_violations_total": float(a * N), "expected_violations_per_unit": float(a * np.median(n_u)),
            "realized_alpha_unit_balanced": float(rate(range(U))),
            "realized_alpha_boot95": [float(lo), float(hi)],
            "realized_alpha_boot95_rel": [float(lo / a), float(hi / a)],
            "units_with_any_violation": int(sum(v.any() for v in viol)),
        }

    # realistic per-unit estimator: mean residual of the unit's first k labels (cross-fit: scored on the rest)
    res["bias_estimator"] = {}
    for k in K_EARLY:
        ok = [u for u in units if len(u["y"]) >= k + 10]
        b = np.array([(u["y"][:k] - u["p"][:k]).mean() for u in ok])
        # sampling SD of the offset estimate = what the per-unit bound must ADD back to stay calibrated
        se = res["sd_within"] / np.sqrt(k)
        res["bias_estimator"][str(k)] = {"n_units": len(ok), "sd_of_estimated_offset": float(b.std(ddof=1)),
                                         "sampling_se_of_offset": float(se),
                                         "true_between_sd": res["sd_between"],
                                         "estimate_is_mostly_noise": bool(se > res["sd_between"])}
    # minimum detectable mean gap (paired over units), Bonferroni over the brief's grid
    return res


def mde(sd_gap, n, alpha_prime, power=0.8):
    return float((stats.norm.ppf(1 - alpha_prime / 2) + stats.norm.ppf(power)) * sd_gap / np.sqrt(n))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--grid", type=int, default=48,
                    help="Bonferroni family size: 4 estimators x 3 horizons x 2 label sets x 2 datasets (brief §5.5)")
    a = ap.parse_args()
    torch.set_num_threads(8)
    nf = json.load(open("results/large/noise_floor_full.json"))
    out = {"tag": "DERIVED (fleet residuals MEASURED against DERIVED labels; oracle bounds are upper bounds)",
           "grid": a.grid}
    for ls in ["primary", "strict"]:
        units = []
        for k in range(4):
            units += residuals(f"runs/chf_{ls}_k{k}")
        c_nom = nf[ls]["cap_median"]
        r = analyse(units, c_nom, nf[ls]["noise_sd_median"])
        r["c_nominal_ah"] = c_nom
        # gap SD across units for the shift oracle = sd of unit means; realistic estimator's is larger
        sd_gap = r["sd_between"]
        r["mde_recovered_pct_if_gap_sd_equals_between_sd"] = 100 * mde(sd_gap, r["n_units"], 0.05 / a.grid) / c_nom
        out[ls] = r
        print(ls, json.dumps({k: v for k, v in r.items() if k != "alphas"}, indent=1))
        for al, v in r["alphas"].items():
            print(" alpha", al, {k: (round(x, 3) if isinstance(x, float) else x) for k, x in v.items()})
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(out, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
