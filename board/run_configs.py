"""Spawn train_mem.py once per (scope, opt, rep) in a FRESH process; collect JSONs into one file."""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def run(configs, run_dir, out_dir, reps=3, extra=()):
    os.makedirs(out_dir, exist_ok=True)
    results = []
    for scope, opt in configs:
        for r in range(reps):
            out = os.path.join(out_dir, f"{scope}_{opt}_r{r}.json")
            cmd = [sys.executable, os.path.join(HERE, "train_mem.py"), "--scope", scope, "--opt", opt,
                   "--run", run_dir, "--out", out, *extra]
            subprocess.run(cmd, check=True)
            results.append(json.load(open(out)))
    return results
