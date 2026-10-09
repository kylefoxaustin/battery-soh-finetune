"""E2 (H2): full on-device retrain, all layers trainable — SGD (no momentum) vs Adam, peak RSS.

Usage (on the board, pinned):  taskset -c 2,3 python3 board/e2_fullretrain.py --run runs/ds1 --out results/raw/e2
"""
import argparse
import json
import os

from run_configs import run

ap = argparse.ArgumentParser()
ap.add_argument("--run", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--reps", type=int, default=3)
a, extra = ap.parse_known_args()
res = run([("full", "sgd"), ("full", "adam")], a.run, a.out, a.reps, extra)
json.dump(res, open(os.path.join(a.out, "e2_all.json"), "w"), indent=1)
