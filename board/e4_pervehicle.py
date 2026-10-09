"""E4 (H4): per-vehicle accuracy recovery — frozen fleet model vs last-layer fine-tune, per target car.

Each target car was EXCLUDED from fleet training (model/train_fleet.py). Its labelled snippets are
sorted by odometer; the first FT_FRAC are its "own early data", a GAP_FRAC gap follows (adjacent
snippets are correlated — no leakage across the boundary), the last TEST_FRAC is "later held-out".

Conditions, all scored on the same later held-out snippets (RMSE, Ah):
  frozen      fleet model as shipped
  early_mean  constant = mean of the car's own early labels       (naive baseline, no model)
  bias        fleet model + scalar offset fitted on early data      (1 param, closed form)
  last        final Linear(64,1) fine-tuned (65 params)             ← THE claim (brief E3/E4)
  head        whole dense head fine-tuned (8,321 params)            (sensitivity point)
  last_guard / head_guard  same, but the step count is chosen on a CHRONOLOGICAL holdout inside the
              car's own FT window (its most recent GUARD_FRAC), from GUARD_STEPS (0 = keep frozen).
              Never sees test data. Sensitivity point: unconstrained FT on a narrow early-mileage window
              was measured to destroy the fleet model's degradation trend (host run, 2026-10-08).
Last-layer FT is only "worth doing" if it beats frozen AND the two cheap baselines.

Data is REAL field data (EVBattery) => RMSE tag MEASURED. No synthetic drift is injected anywhere.

Usage: python3 board/e4_pervehicle.py --run runs/ds1 --out results/raw/e4.json [--ft-frac 0.3]
"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "model"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np  # noqa: E402
import torch  # noqa: E402

import cpustat  # noqa: E402
from common import Norm, SoHNet, make_features, trainable_params  # noqa: E402

GAP_FRAC, TEST_FRAC = 0.2, 0.5     # CHOSEN
FT_STEPS, FT_LR, FT_BS = 300, 1e-3, 32  # CHOSEN (Adam)
GUARD_FRAC = 0.25                        # CHOSEN: most recent quarter of the FT window = inner holdout
GUARD_STEPS = [0, 25, 50, 100, 200, 300]  # CHOSEN, declared before looking at guarded results


def rmse(p, y):
    return float(np.sqrt(np.mean((p - y) ** 2)))


def finetune(model, scope, Eft, yft_z):
    """Fine-tune on CACHED backbone embeddings. Exact: the backbone is frozen and has no dropout, so
    model.head(embed(x)) == model(x) — the frozen LSTM runs once per snippet instead of once per step.
    This is also the deployment design point E5 sizes (cache a feature vector, discard raw history)."""
    params = trainable_params(model, scope)
    opt = torch.optim.Adam(params, lr=FT_LR)
    g = torch.Generator().manual_seed(0)
    model.train()
    for _ in range(FT_STEPS):
        idx = torch.randint(0, len(Eft), (min(FT_BS, len(Eft)),), generator=g)
        loss = torch.nn.functional.mse_loss(model.head(Eft[idx]).squeeze(-1), yft_z[idx])
        opt.zero_grad()
        loss.backward()
        opt.step()
    model.eval()
    return model


def finetune_guarded(sd, scope, Eft, yft_z):
    """Pick the step count on the most recent GUARD_FRAC of the FT window (train on the earlier part).
    Returns (model, chosen_steps)."""
    k = int(len(Eft) * (1 - GUARD_FRAC))
    Etr, ytr, Eva, yva = Eft[:k], yft_z[:k], Eft[k:], yft_z[k:]
    m = SoHNet()
    m.load_state_dict(sd)
    params = trainable_params(m, scope)
    opt = torch.optim.Adam(params, lr=FT_LR)
    g = torch.Generator().manual_seed(0)
    best = (float("inf"), 0, {kk: v.clone() for kk, v in m.head.state_dict().items()})
    for step in range(max(GUARD_STEPS) + 1):
        if step in GUARD_STEPS:
            m.eval()
            with torch.no_grad():
                v = torch.nn.functional.mse_loss(m.head(Eva).squeeze(-1), yva).item()
            if v < best[0]:
                best = (v, step, {kk: t.clone() for kk, t in m.head.state_dict().items()})
            m.train()
        if step == max(GUARD_STEPS):
            break
        idx = torch.randint(0, len(Etr), (min(FT_BS, len(Etr)),), generator=g)
        loss = torch.nn.functional.mse_loss(m.head(Etr[idx]).squeeze(-1), ytr[idx])
        opt.zero_grad()
        loss.backward()
        opt.step()
    m.head.load_state_dict(best[2])
    m.eval()
    return m, best[1]


def embed_all(model, X, bs=256):
    with torch.no_grad():
        return torch.cat([model.embed(X[k:k + bs]) for k in range(0, len(X), bs)])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--ft-frac", type=float, default=0.3)  # CHOSEN; sensitivity: 0.1
    ap.add_argument("--threads", type=int, default=None)
    a = ap.parse_args()
    torch.set_num_threads(a.threads or len(os.sched_getaffinity(0)))
    torch.manual_seed(0)

    norm = Norm.from_state(json.load(open(os.path.join(a.run, "norm.json"))))
    sd = torch.load(os.path.join(a.run, "fleet.pt"), map_location="cpu")
    split = json.load(open(os.path.join(a.run, "split.json")))
    targets, use_km = split["targets"], split.get("mileage_input", True)
    t0 = time.monotonic()
    rows = []
    for car in targets:
        d = np.load(os.path.join(a.run, "cars", f"car_{car}.npz"))
        o = np.argsort(d["mileage"])
        km_in = d["mileage"][o] if use_km else np.zeros_like(d["mileage"][o])  # match the fleet model's training
        X = torch.from_numpy(norm.x(make_features(d["X"][o], km_in)))
        y = d["capacity"][o]
        mil = d["mileage"][o]
        n = len(y)
        ft = slice(0, int(a.ft_frac * n))
        te = slice(int((1 - TEST_FRAC) * n), n)
        assert int(a.ft_frac * n) <= int((1 - TEST_FRAC - GAP_FRAC) * n) + 1, "FT overlaps gap/test"
        yft_z = torch.from_numpy(norm.y(y[ft]))

        base = SoHNet().eval()
        base.load_state_dict(sd)
        E = embed_all(base, X)  # frozen backbone, once
        Eft, Ete = E[ft], E[te]

        def pred(m):
            with torch.no_grad():
                return norm.y_inv(m.head(Ete).squeeze(-1).numpy())

        p_frozen = pred(base)
        with torch.no_grad():
            p_full = norm.y_inv(base(X[te][:64]).numpy())  # spot-check: cached path == full forward
            assert np.max(np.abs(p_full - p_frozen[:64])) < 1e-4, "cached-embedding path != full forward"
            off = float(np.mean(y[ft] - norm.y_inv(base.head(Eft).squeeze(-1).numpy())))
        row = {"car": int(car), "n": n, "n_ft": ft.stop, "n_test": n - te.start,
               "mileage_ft_km": [float(mil[0]), float(mil[ft.stop - 1])],
               "mileage_test_km": [float(mil[te.start]), float(mil[-1])],
               "cap_ft_mean": float(y[ft].mean()), "cap_test_mean": float(y[te].mean()),
               "rmse": {"frozen": rmse(p_frozen, y[te]),
                        "early_mean": rmse(np.full(n - te.start, y[ft].mean()), y[te]),
                        "bias": rmse(p_frozen + off, y[te])}}
        for scope in ("last", "head"):
            m = SoHNet()
            m.load_state_dict(sd)
            m.eval()
            row["rmse"][scope] = rmse(pred(finetune(m, scope, Eft, yft_z)), y[te])
        row["guard_steps"] = {}
        for scope in ("last", "head"):
            m, st = finetune_guarded(sd, scope, Eft, yft_z)
            row["rmse"][scope + "_guard"] = rmse(pred(m), y[te])
            row["guard_steps"][scope] = st
        row["reduction_pct_last_vs_frozen"] = 100 * (1 - row["rmse"]["last"] / row["rmse"]["frozen"])
        rows.append(row)
        print(f"car {car}: n={n} " + " ".join(f"{k}={v:.3f}" for k, v in row["rmse"].items()), flush=True)

    R = {k: np.array([r["rmse"][k] for r in rows]) for k in rows[0]["rmse"]}
    red = np.array([r["reduction_pct_last_vs_frozen"] for r in rows])
    summ = {k: {"median": float(np.median(v)), "p25": float(np.percentile(v, 25)),
                "p75": float(np.percentile(v, 75)), "mean": float(v.mean())} for k, v in R.items()}
    summ["reduction_pct_last_vs_frozen"] = {"median": float(np.median(red)), "p25": float(np.percentile(red, 25)),
                                            "p75": float(np.percentile(red, 75)),
                                            "n_improved": int((red > 0).sum()), "n": len(red)}
    summ["last_beats"] = {b: int((R["last"] < R[b]).sum()) for b in ("frozen", "early_mean", "bias")}
    summ["last_guard_beats"] = {b: int((R["last_guard"] < R[b]).sum()) for b in ("frozen", "early_mean", "bias")}
    redg = 100 * (1 - R["last_guard"] / R["frozen"])
    summ["reduction_pct_last_guard_vs_frozen"] = {"median": float(np.median(redg)), "p25": float(np.percentile(redg, 25)),
                                                  "p75": float(np.percentile(redg, 75)),
                                                  "n_improved": int((redg > 1e-9).sum()), "n_unchanged": int((np.abs(redg) <= 1e-9).sum())}
    summ["guard_steps_chosen"] = {sc: [r["guard_steps"][sc] for r in rows] for sc in ("last", "head")}
    out = {"tag": "MEASURED (real field data, EVBattery; no synthetic drift)",
           "config": {"mileage_input": use_km, "ft_frac": a.ft_frac, "gap_frac": GAP_FRAC, "test_frac": TEST_FRAC,
                      "guard_frac": GUARD_FRAC, "guard_steps": GUARD_STEPS,
                      "ft_steps": FT_STEPS, "ft_lr": FT_LR, "ft_bs": FT_BS, "optimizer": "Adam",
                      "torch": torch.__version__},
           "wall_s": round(time.monotonic() - t0, 2), "summary": summ, "per_car": rows,
           "env": cpustat.environment(), "hwm_kb": cpustat.vm_hwm_kb()}
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    cpustat.dump(a.out, out)
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
