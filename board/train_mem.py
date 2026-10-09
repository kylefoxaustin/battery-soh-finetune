"""E2 / E3 core: peak training RSS for one (scope, optimizer) config, in a FRESH process.

Run ONE config per process — VmHWM is a lifetime high-water mark, so two configs in one
process would contaminate each other. e2_fullretrain.py / e3_lastlayer.py loop over configs by
spawning this file.

Memory protocol (all from /proc/self/status, kernel counters):
  rss_baseline_kb : VmRSS after imports + model + data + one no_grad forward (the "inference floor")
  hwm_baseline_kb : VmHWM at the same point
  hwm_peak_kb     : VmHWM after the training loop
  train_delta_kb  : hwm_peak_kb - hwm_baseline_kb  (memory the TRAINING phase added above the floor)

Gates, evaluated in the SAME run (brief §0.3) — the RSS number is only quotable if gate.pass:
  - every loss is finite, and the full fine-tune-set loss (deterministic, no_grad) is lower after training
    than before (minibatch-loss trends are too noisy from a good init to gate on)
  - frozen parameters are BIT-IDENTICAL after training (proves the freeze), trainable ones changed
  - held-out RMSE after training is finite

Usage: python train_mem.py --scope full|head|last --opt sgd|adam --run <dir> --out res.json
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
from common import Norm, SoHNet, count, make_features, trainable_params  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scope", choices=["full", "head", "last"], required=True)
    ap.add_argument("--opt", choices=["sgd", "adam"], required=True)
    ap.add_argument("--run", required=True, help="dir with fleet.pt, norm.json, split.json, cars/")
    ap.add_argument("--car", type=int, default=None, help="target car (default: first target)")
    ap.add_argument("--bs", type=int, default=32)       # CHOSEN
    ap.add_argument("--steps", type=int, default=60)    # CHOSEN
    ap.add_argument("--lr", type=float, default=None)
    ap.add_argument("--threads", type=int, default=None)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    nthreads = a.threads or len(os.sched_getaffinity(0))
    torch.set_num_threads(nthreads)
    torch.manual_seed(0)
    rss_import_kb = cpustat.vm_rss_kb()

    norm = Norm.from_state(json.load(open(os.path.join(a.run, "norm.json"))))
    model = SoHNet()
    model.load_state_dict(torch.load(os.path.join(a.run, "fleet.pt"), map_location="cpu"))
    car = a.car if a.car is not None else json.load(open(os.path.join(a.run, "split.json")))["targets"][0]
    d = np.load(os.path.join(a.run, "cars", f"car_{car}.npz"))  # ONE car only — keeps the RSS floor honest
    order = np.argsort(d["mileage"])
    Xc = norm.x(make_features(d["X"][order], d["mileage"][order]))
    yc = d["capacity"][order]
    n = len(yc)
    ft, te = slice(0, int(0.3 * n)), slice(int(0.5 * n), n)  # chronological: early FT, later test
    Xft, yft = torch.from_numpy(Xc[ft]), torch.from_numpy(norm.y(yc[ft]))
    Xte = torch.from_numpy(Xc[te])

    params = trainable_params(model, a.scope)
    frozen = {k: v.detach().clone() for k, v in model.named_parameters() if not v.requires_grad}
    train0 = {k: v.detach().clone() for k, v in model.named_parameters() if v.requires_grad}
    lr = a.lr or (1e-3 if a.opt == "adam" else 1e-2)
    opt = torch.optim.Adam(params, lr=lr) if a.opt == "adam" else torch.optim.SGD(params, lr=lr, momentum=0.0)

    def ft_loss():  # deterministic full-FT-set loss, chunked so it never sets a new high-water mark
        model.eval()
        with torch.no_grad():
            return float(sum(torch.nn.functional.mse_loss(model(Xft[k:k + a.bs]), yft[k:k + a.bs], reduction="sum")
                             for k in range(0, len(Xft), a.bs)) / len(Xft))

    loss_before = ft_loss()  # also serves as the inference floor (batch-sized no_grad forwards)
    rss_base, hwm_base = cpustat.vm_rss_kb(), cpustat.vm_hwm_kb()

    cpu = cpustat.CpuSampler().start()
    t0 = time.monotonic()
    losses = []
    g = torch.Generator().manual_seed(0)
    model.train()
    for _ in range(a.steps):
        idx = torch.randint(0, len(Xft), (a.bs,), generator=g)
        loss = torch.nn.functional.mse_loss(model(Xft[idx]), yft[idx])
        opt.zero_grad(set_to_none=False)
        loss.backward()
        opt.step()
        losses.append(loss.item())
    train_s = time.monotonic() - t0
    cpu_res = cpu.stop()
    hwm_peak = cpustat.vm_hwm_kb()
    loss_after = ft_loss()

    model.eval()
    with torch.no_grad():
        pred = norm.y_inv(model(Xte).numpy())
    rmse = float(np.sqrt(np.mean((pred - yc[te]) ** 2)))

    frozen_ok = all(torch.equal(v, dict(model.named_parameters())[k]) for k, v in frozen.items())
    changed = all(not torch.equal(v, dict(model.named_parameters())[k]) for k, v in train0.items())
    first, last = float(np.mean(losses[:10])), float(np.mean(losses[-10:]))
    gate = {"losses_finite": bool(np.all(np.isfinite(losses))), "ft_set_loss_decreased": loss_after < loss_before,
            "frozen_bit_identical": frozen_ok, "trainable_changed": changed,
            "heldout_rmse_finite": bool(np.isfinite(rmse))}
    gate["pass"] = all(gate.values())

    n_tr = count(params)
    opt_state_b = sum(t.numel() * t.element_size() for s in opt.state.values()
                      for t in s.values() if torch.is_tensor(t) and t.dim() > 0)
    res = {
        "tag": "MEASURED" if gate["pass"] else "UNGATED",
        "config": {"scope": a.scope, "opt": a.opt, "lr": lr, "bs": a.bs, "steps": a.steps,
                   "threads": nthreads, "car": car, "n_ft": int(len(yft)), "n_test": int(len(Xte)),
                   "seq_len": int(Xft.shape[1]), "precision": "fp32", "torch": torch.__version__},
        "params_total": count(model.parameters()), "params_trainable": n_tr,
        "mem_kb": {"rss_after_import": rss_import_kb, "rss_baseline": rss_base, "hwm_baseline": hwm_base,
                   "hwm_peak": hwm_peak, "train_delta": hwm_peak - hwm_base},
        "opt_state_bytes_actual": opt_state_b,  # MEASURED from the live optimizer tensors
        "derived_bytes": {  # DERIVED: brief §E2 accounting, trainable params only, fp32
            "weights_plus_grads": n_tr * 8, "adam_extra_m_v": n_tr * 8 if a.opt == "adam" else 0,
            "total_per_brief": n_tr * (16 if a.opt == "adam" else 8)},
        "train_s": round(train_s, 3), "ms_per_step": round(1000 * train_s / a.steps, 2),
        "loss_first10": first, "loss_last10": last, "ft_loss_before": loss_before, "ft_loss_after": loss_after,
        "heldout_rmse_ah": rmse,
        "gate": gate, "cpu_pct": cpu_res, "env": cpustat.environment(),
    }
    cpustat.dump(a.out, res)
    print(f"{a.scope}/{a.opt}: trainable={n_tr} delta={res['mem_kb']['train_delta']} KB "
          f"peak={hwm_peak} KB gate={'PASS' if gate['pass'] else 'FAIL ' + str(gate)}")


if __name__ == "__main__":
    main()
