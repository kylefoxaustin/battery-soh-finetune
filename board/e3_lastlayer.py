"""E3 (H3): frozen backbone. 'last' = final Linear(64,1) only (THE brief's last layer);
'head' = whole dense head (sensitivity point). Both SGD and Adam.

Usage (on the board, pinned):  taskset -c 2,3 python3 board/e3_lastlayer.py --run runs/ds1 --out results/raw/e3
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
res = run([("last", "sgd"), ("last", "adam"), ("head", "sgd"), ("head", "adam")], a.run, a.out, a.reps, extra)
json.dump(res, open(os.path.join(a.out, "e3_all.json"), "w"), indent=1)
