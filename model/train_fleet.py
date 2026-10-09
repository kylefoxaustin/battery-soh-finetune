"""Train the fleet-average SoH model on one EVBattery sub-dataset (one manufacturer), or any labelled .npz
with the same layout (--data, e.g. the Changan labels), host-side.

Split (by CAR, never by snippet — snippets of one car are highly correlated):
  targets : N_TARGETS cars with enough labelled history, EXCLUDED from fleet training (E4 subjects)
  val     : VAL_FRAC of the remaining cars, for early stopping
  train   : the rest
Outputs to --out: fleet.pt (state_dict), norm.json, split.json, train_log.json, targets.npz (raw snippets for
the E4 target cars, for the board) and cars/car_<id>.npz (the same, one file per target).

K-fold targets (--nfolds K --fold k): eligible units (>= --min-target labels spanning >= --min-span-km) are
permuted once (SEED) and fold k takes every K-th; running all K folds evaluates EVERY eligible unit while
each fleet model still trains on all the others. Default (--nfolds 0) = the original EVBattery split.

Usage: python model/train_fleet.py --ds 1 --device cuda --out runs/ds1
"""
import argparse
import json
import os
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import torch

from common import Norm, SoHNet, count, make_features

MIN_TARGET_SNIPPETS = 400  # CHOSEN: enough history for a 30% FT / 50% test chronological split
N_TARGETS = 20             # CHOSEN
VAL_FRAC = 0.15            # CHOSEN
SEED = 0


def load(ds, path=None):
    d = np.load(path or os.path.join(ROOT, f"data/processed/evbattery_ds{ds}.npz"))
    return d["X"], d["car"], d["mileage"], d["capacity"]


def split_cars(car, rng, mil=None, min_target=MIN_TARGET_SNIPPETS, min_span=0.0, nfolds=0, fold=0):
    cars, n = np.unique(car, return_counts=True)
    span = np.array([np.ptp(mil[car == c]) for c in cars]) if mil is not None else np.full(len(cars), np.inf)
    eligible = cars[(n >= min_target) & (span >= min_span)]
    if nfolds:
        targets = np.sort(rng.permutation(eligible)[fold::nfolds])
    else:
        targets = np.sort(rng.choice(eligible, size=min(N_TARGETS, len(eligible)), replace=False))
    rest = np.setdiff1d(cars, targets)
    val = np.sort(rng.choice(rest, size=max(1, int(len(rest) * VAL_FRAC)), replace=False))
    train = np.setdiff1d(rest, val)
    return train, val, targets


def evaluate(model, Xn, y, norm, device, bs=4096):
    model.eval()
    out = []
    with torch.no_grad():
        for i in range(0, len(Xn), bs):
            out.append(model(torch.from_numpy(Xn[i:i + bs]).to(device)).cpu().numpy())
    pred = norm.y_inv(np.concatenate(out))
    return float(np.sqrt(np.mean((pred - y) ** 2))), pred


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ds", type=int, default=1)
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--epochs", type=int, default=30)
    ap.add_argument("--bs", type=int, default=256)        # CHOSEN
    ap.add_argument("--lr", type=float, default=1e-3)     # CHOSEN
    ap.add_argument("--patience", type=int, default=5)
    ap.add_argument("--no-mileage", action="store_true",
                    help="sensitivity: hold the odometer channel at 0 (same architecture, no age information)")
    ap.add_argument("--data", default=None, help="labelled .npz (X, car, mileage, capacity); overrides --ds")
    ap.add_argument("--min-target", type=int, default=MIN_TARGET_SNIPPETS)
    ap.add_argument("--min-span-km", type=float, default=0.0)
    ap.add_argument("--nfolds", type=int, default=0)
    ap.add_argument("--fold", type=int, default=0)
    ap.add_argument("--out", default="runs/ds1")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    rng = np.random.default_rng(SEED)
    torch.manual_seed(SEED)

    X, car, mil, cap = load(a.ds, a.data)
    train_c, val_c, tgt_c = split_cars(car, rng, mil, a.min_target, a.min_span_km, a.nfolds, a.fold)
    tr, va, tg = np.isin(car, train_c), np.isin(car, val_c), np.isin(car, tgt_c)
    F = make_features(X, np.zeros_like(mil) if a.no_mileage else mil)
    norm = Norm().fit(F[tr], cap[tr])
    Xtr, ytr = norm.x(F[tr]), norm.y(cap[tr])
    Xva, yva = norm.x(F[va]), cap[va]

    model = SoHNet().to(a.device)
    opt = torch.optim.Adam(model.parameters(), lr=a.lr)
    print(f"ds{a.ds}: train {tr.sum()} snippets/{len(train_c)} cars, val {va.sum()}/{len(val_c)}, "
          f"targets {tg.sum()}/{len(tgt_c)}; params {count(model.parameters())}")

    Xtr_t, ytr_t = torch.from_numpy(Xtr), torch.from_numpy(ytr)
    best, best_ep, log = float("inf"), -1, []
    for ep in range(a.epochs):
        model.train()
        t0 = time.time()
        perm = torch.randperm(len(Xtr_t))
        tot = 0.0
        for i in range(0, len(perm), a.bs):
            idx = perm[i:i + a.bs]
            xb, yb = Xtr_t[idx].to(a.device), ytr_t[idx].to(a.device)
            loss = torch.nn.functional.mse_loss(model(xb), yb)
            opt.zero_grad()
            loss.backward()
            opt.step()
            tot += loss.item() * len(idx)
        va_rmse, _ = evaluate(model, Xva, yva, norm, a.device)
        log.append({"epoch": ep, "train_mse_z": tot / len(perm), "val_rmse_ah": va_rmse,
                    "sec": round(time.time() - t0, 1)})
        print(log[-1], flush=True)
        if va_rmse < best:
            best, best_ep = va_rmse, ep
            torch.save(model.state_dict(), os.path.join(a.out, "fleet.pt"))
        elif ep - best_ep >= a.patience:
            break

    # Baselines the fleet model must beat on the SAME val cars, or E4's "frozen" reference is a strawman.
    triv = float(np.sqrt(np.mean((cap[va] - cap[tr].mean()) ** 2)))
    A = np.vstack([mil[tr], np.ones(tr.sum())]).T
    coef = np.linalg.lstsq(A, cap[tr], rcond=None)[0]
    mlin = float(np.sqrt(np.mean((cap[va] - (coef[0] * mil[va] + coef[1])) ** 2)))
    baselines = {"train_mean_rmse_ah": triv, "mileage_linear_rmse_ah": mlin, "lstm_beats_both": best < min(triv, mlin)}
    print(f"baselines on val cars: train-mean {triv:.3f} Ah, mileage-linear {mlin:.3f} Ah; LSTM {best:.3f} Ah")

    with open(os.path.join(a.out, "norm.json"), "w") as f:
        json.dump(norm.state(), f)
    with open(os.path.join(a.out, "split.json"), "w") as f:
        json.dump({"ds": a.ds, "data": a.data, "nfolds": a.nfolds, "fold": a.fold, "min_target": a.min_target,
               "min_span_km": a.min_span_km, "seed": SEED, "train": train_c.tolist(), "val": val_c.tolist(),
                   "targets": tgt_c.tolist(), "best_epoch": best_ep, "best_val_rmse_ah": best, "baselines": baselines,
                   "bs": a.bs, "lr": a.lr, "optimizer": "Adam",
                   "mileage_input": not a.no_mileage}, f, indent=1)
    with open(os.path.join(a.out, "train_log.json"), "w") as f:
        json.dump(log, f, indent=1)
    np.savez(os.path.join(a.out, "targets.npz"), X=X[tg], car=car[tg], mileage=mil[tg], capacity=cap[tg])
    os.makedirs(os.path.join(a.out, "cars"), exist_ok=True)
    for c in tgt_c:
        s = car == c
        np.savez(os.path.join(a.out, "cars", f"car_{c}.npz"), X=X[s], car=car[s], mileage=mil[s], capacity=cap[s])
    print(f"best val RMSE {best:.3f} Ah @ epoch {best_ep}")


if __name__ == "__main__":
    main()
