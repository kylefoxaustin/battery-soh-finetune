"""Experiment C (Analysis Brief §3C): rolling re-fine-tune vs frozen fleet model, RMSE vs prediction horizon.

Per held-out unit (never in fleet training), labels sorted by odometer. Forecast origins every STEP_KM. At each
origin tau:
  history  = the unit's labels with odometer <= tau; the FT window = the last WINDOW_KM of that history
  re-fine-tune FROM THE FLEET WEIGHTS (not cumulatively) on the window, then predict every later label whose
  odometer falls in a horizon band (tau + lo, tau + hi]
Methods (all fit on the window only — none ever sees a label after tau):
  frozen      fleet model as shipped
  bias        fleet model + mean residual on the window (1 param, closed form)
  last        final Linear(64,1), Adam FT_STEPS
  last_guard  same; step count chosen on the most recent GUARD_FRAC of the window (0 allowed = frozen)
  head_guard  whole head (8,321 params), guarded the same way
  persist     CONTROL, no model: predict the mean of the window's own labels. If fine-tuning only matches
              persistence, its short-horizon gain is label autocorrelation (slow label errors: season, OCV-table
              drift, BMS recalibration), not adaptation of the model.
  persist_recent  CONTROL, no model: mean of the window's labels in its last RECENT_KM only. Added AFTER the
              first preliminary results (2026-10-08) because `persist` averages the whole window and so lags
              the degradation trend — this stricter control can only make a positive result harder to claim.
Every method is scored on the SAME (origin, label) pairs as frozen. Per unit and band: RMSE over all its
(origin, label) pairs; across units: median, IQR, and how many units the method beats frozen on.

Gates (same run): fleet backbone + head[0] bit-identical after every last-layer FT (checked), trainable layer
changed, all losses finite. A unit/band with < MIN_PAIRS pairs is reported as such and not scored.

All CHOSEN inputs are module constants, declared before any rolling result was seen.
Usage: python analysis/rolling.py --run runs/ch85_p_f0 --out results/large/rolling_ch85_p_f0.json
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "model"))

import numpy as np  # noqa: E402
import torch  # noqa: E402

from common import Norm, SoHNet, make_features, trainable_params  # noqa: E402

STEP_KM = 10_000                     # CHOSEN: forecast origin every 10 k km
WINDOW_KM = 30_000                   # CHOSEN: FT on the most recent 30 k km of the unit's history
MIN_WINDOW_LABELS = 5                # CHOSEN: skip an origin with fewer labels in its window
BANDS_KM = [(0, 5e3), (5e3, 1e4), (1e4, 2e4), (2e4, 4e4), (4e4, 8e4)]  # CHOSEN horizon bands
FT_STEPS, FT_LR, FT_BS = 300, 1e-3, 32   # CHOSEN, same as E4
GUARD_FRAC, GUARD_STEPS = 0.25, [0, 25, 50, 100, 200, 300]  # same as E4
MIN_PAIRS = 3
RECENT_KM = 5_000                    # persist_recent window (added post hoc, see docstring)
METHODS = ["frozen", "bias", "last", "last_guard", "head_guard", "persist", "persist_recent"]


def adam_ft(model, scope, E, y, steps):
    params = trainable_params(model, scope)
    opt = torch.optim.Adam(params, lr=FT_LR)
    g = torch.Generator().manual_seed(0)
    losses = []
    model.train()
    for _ in range(steps):
        idx = torch.randint(0, len(E), (min(FT_BS, len(E)),), generator=g)
        loss = torch.nn.functional.mse_loss(model.head(E[idx]).squeeze(-1), y[idx])
        opt.zero_grad()
        loss.backward()
        opt.step()
        losses.append(loss.item())
    model.eval()
    return losses


def guarded(sd, scope, E, y):
    k = max(1, int(len(E) * (1 - GUARD_FRAC)))
    if k >= len(E):
        m = SoHNet(); m.load_state_dict(sd); m.eval()
        return m, 0, []
    m = SoHNet(); m.load_state_dict(sd)
    params = trainable_params(m, scope)
    opt = torch.optim.Adam(params, lr=FT_LR)
    g = torch.Generator().manual_seed(0)
    best = (float("inf"), 0, {kk: v.clone() for kk, v in m.head.state_dict().items()})
    losses = []
    for step in range(max(GUARD_STEPS) + 1):
        if step in GUARD_STEPS:
            m.eval()
            with torch.no_grad():
                v = torch.nn.functional.mse_loss(m.head(E[k:]).squeeze(-1), y[k:]).item()
            if v < best[0]:
                best = (v, step, {kk: t.clone() for kk, t in m.head.state_dict().items()})
            m.train()
        if step == max(GUARD_STEPS):
            break
        idx = torch.randint(0, k, (min(FT_BS, k),), generator=g)
        loss = torch.nn.functional.mse_loss(m.head(E[:k][idx]).squeeze(-1), y[:k][idx])
        opt.zero_grad()
        loss.backward()
        opt.step()
        losses.append(loss.item())
    m.head.load_state_dict(best[2])
    m.eval()
    return m, best[1], losses


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--threads", type=int, default=8)
    a = ap.parse_args()
    torch.set_num_threads(a.threads)
    torch.manual_seed(0)
    norm = Norm.from_state(json.load(open(os.path.join(a.run, "norm.json"))))
    sd = torch.load(os.path.join(a.run, "fleet.pt"), map_location="cpu")
    split = json.load(open(os.path.join(a.run, "split.json")))
    use_km = split.get("mileage_input", True)
    frozen_keys = [k for k in sd if not k.startswith("head.2")]

    units, gate_fail = [], []
    for car in split["targets"]:
        d = np.load(os.path.join(a.run, "cars", f"car_{car}.npz"))
        o = np.argsort(d["mileage"])
        km, y = d["mileage"][o].astype(np.float64), d["capacity"][o].astype(np.float64)
        X = torch.from_numpy(norm.x(make_features(d["X"][o], km if use_km else np.zeros_like(km))))
        base = SoHNet(); base.load_state_dict(sd); base.eval()
        with torch.no_grad():
            E = torch.cat([base.embed(X[i:i + 256]) for i in range(0, len(X), 256)])
            p_frozen = norm.y_inv(base.head(E).squeeze(-1).numpy())
        yz = torch.from_numpy(norm.y(y.astype(np.float32)))
        err = {m: [[] for _ in BANDS_KM] for m in METHODS}
        n_origins = 0
        for tau in np.arange(km[0] + STEP_KM, km[-1], STEP_KM):
            win = np.flatnonzero((km <= tau) & (km > tau - WINDOW_KM))
            fut = np.flatnonzero(km > tau)
            if len(win) < MIN_WINDOW_LABELS or not len(fut):
                continue
            n_origins += 1
            Ew, yw = E[win], yz[win]
            preds = {"frozen": p_frozen}
            preds["bias"] = p_frozen + float(np.mean(y[win] - p_frozen[win]))
            preds["persist"] = np.full_like(p_frozen, float(np.mean(y[win])))
            rec = win[km[win] > tau - RECENT_KM]
            preds["persist_recent"] = np.full_like(p_frozen, float(np.mean(y[rec if len(rec) else win[-1:]])))
            m = SoHNet(); m.load_state_dict(sd)
            losses = adam_ft(m, "last", Ew, yw, FT_STEPS)
            msd = m.state_dict()
            if not (all(torch.equal(msd[k], sd[k]) for k in frozen_keys)
                    and not torch.equal(msd["head.2.weight"], sd["head.2.weight"])
                    and np.all(np.isfinite(losses))):
                gate_fail.append((int(car), float(tau)))
            with torch.no_grad():
                preds["last"] = norm.y_inv(m.head(E).squeeze(-1).numpy())
            for name, scope in (("last_guard", "last"), ("head_guard", "head")):
                mg, _, gl = guarded(sd, scope, Ew, yw)
                if gl and not np.all(np.isfinite(gl)):
                    gate_fail.append((int(car), float(tau), name))
                with torch.no_grad():
                    preds[name] = norm.y_inv(mg.head(E).squeeze(-1).numpy())
            for b, (lo, hi) in enumerate(BANDS_KM):
                sel = fut[(km[fut] > tau + lo) & (km[fut] <= tau + hi)]
                for mth in METHODS:
                    err[mth][b].extend((preds[mth][sel] - y[sel]).tolist())
        unit = {"car": int(car), "n_labels": int(len(y)), "span_km": float(km[-1] - km[0]), "n_origins": n_origins,
                "bands": []}
        for b, band in enumerate(BANDS_KM):
            n = len(err["frozen"][b])
            row = {"band_km": list(band), "n_pairs": n}
            if n >= MIN_PAIRS:
                row["rmse"] = {mth: float(np.sqrt(np.mean(np.square(err[mth][b])))) for mth in METHODS}
            unit["bands"].append(row)
        units.append(unit)
        print(f"car {car}: {len(y)} labels, {n_origins} origins", flush=True)

    summary = []
    for b, band in enumerate(BANDS_KM):
        rows = [u["bands"][b]["rmse"] for u in units if "rmse" in u["bands"][b]]
        if not rows:
            summary.append({"band_km": list(band), "n_units": 0}); continue
        R = {mth: np.array([r[mth] for r in rows]) for mth in METHODS}
        s = {"band_km": list(band), "n_units": len(rows),
             "median_rmse": {mth: float(np.median(R[mth])) for mth in METHODS},
             "iqr_rmse": {mth: [float(np.percentile(R[mth], 25)), float(np.percentile(R[mth], 75))] for mth in METHODS},
             "beats_frozen": {mth: int((R[mth] < R["frozen"]).sum()) for mth in METHODS if mth != "frozen"},
             "beats_persist": {mth: int((R[mth] < R["persist"]).sum()) for mth in METHODS if mth != "persist"},
             "beats_persist_recent": {mth: int((R[mth] < R["persist_recent"]).sum()) for mth in METHODS if mth != "persist_recent"},
             "median_pct_change_vs_frozen": {mth: float(np.median(100 * (R[mth] / R["frozen"] - 1)))
                                             for mth in METHODS if mth != "frozen"}}
        summary.append(s)
    out = {"tag": "DERIVED labels -> MEASURED RMSE (host)", "run": a.run,
           "config": {"step_km": STEP_KM, "window_km": WINDOW_KM, "min_window_labels": MIN_WINDOW_LABELS,
                      "bands_km": BANDS_KM, "ft_steps": FT_STEPS, "ft_lr": FT_LR, "guard_frac": GUARD_FRAC,
                      "guard_steps": GUARD_STEPS, "mileage_input": use_km},
           "gate": {"fails": gate_fail, "pass": not gate_fail}, "summary": summary, "units": units}
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    json.dump(out, open(a.out, "w"), indent=1)
    for s in summary:
        if s["n_units"]:
            print(f"band {s['band_km']}: n_units {s['n_units']} " + " ".join(f"{m}={v:.2f}" for m, v in s["median_rmse"].items())
                  + f" | beats frozen {s['beats_frozen']}")
    print("gate", "PASS" if not gate_fail else f"FAIL {gate_fail[:5]}")


if __name__ == "__main__":
    main()
