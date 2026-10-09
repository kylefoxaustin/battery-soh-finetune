"""Consolidate the EVBattery dataset (figshare 23301881, CC BY 4.0) into one .npz per sub-dataset.

Reads the downloaded archives data/raw/evbattery/battery_datasetN.tar.gz SEQUENTIALLY (no extraction:
1.28M ~12 KB files on a spinning disk are random-IO bound, >1 h per sub-dataset). Each data/<i>.pkl is a legacy
torch.save of (ndarray[128, 8], OrderedDict(label, car, charge_segment, mileage, capacity)).
Columns: avg cell V, current, SOC, max cell V, min cell V, max temp, min temp, time [s].
capacity == 0 means the snippet carries no capacity label; only labelled snippets are kept.

Output: data/processed/evbattery_dsN.npz with
  X        float32 [N, 128, 8]  raw snippet (time column kept; model code decides features)
  car      int32   [N]
  mileage  float32 [N]          odometer at snippet, km — used for chronological early/late splits
  capacity float32 [N]          Ah label
  segment  int32   [N]
Usage: python data/prepare_evbattery.py [--raw data/raw/evbattery] [--out data/processed]
"""
import argparse
import io
import os
import tarfile
from multiprocessing import Pool

import numpy as np
import torch


def _load(blob):
    x, meta = torch.load(io.BytesIO(blob), weights_only=False)
    cap = float(meta["capacity"])
    if cap <= 0:
        return None
    return (x.astype(np.float32), int(meta["car"]), float(meta["mileage"]), cap,
            int(meta["charge_segment"]))


def _one(args):
    raw, out_dir, n = args
    torch.set_num_threads(1)
    rows, total = [], 0
    with tarfile.open(os.path.join(raw, f"battery_dataset{n}.tar.gz"), "r|gz") as tf:
        for m in tf:
            if m.isfile() and m.name.endswith(".pkl"):
                total += 1
                r = _load(tf.extractfile(m).read())
                if r is not None:
                    rows.append(r)
    X, car, mil, cap, seg = zip(*rows)
    out = os.path.join(out_dir, f"evbattery_ds{n}.npz")
    np.savez(out, X=np.stack(X), car=np.array(car, np.int32), mileage=np.array(mil, np.float32),
             capacity=np.array(cap, np.float32), segment=np.array(seg, np.int32))
    return (f"ds{n}: {total} snippets, {len(rows)} labelled, {len(set(car))} cars, "
            f"capacity {min(cap):.2f}-{max(cap):.2f} Ah -> {out}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default="data/raw/evbattery")
    ap.add_argument("--out", default="data/processed")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    with Pool(3) as p:  # one sequential reader per archive
        for line in p.imap_unordered(_one, [(a.raw, a.out, n) for n in (1, 2, 3)]):
            print(line, flush=True)


if __name__ == "__main__":
    main()
