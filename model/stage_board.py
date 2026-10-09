"""Split a run's targets.npz into one small file per target car (so a board process loads only the car
it uses — a 300 MB all-cars array would inflate every absolute RSS figure), then stream the code and
the run artifacts to the board (tar over ssh — the board has no rsync).

Usage: python model/stage_board.py --run runs/ds1 [--host imx95] [--dest /tmp/batt_ft]
"""
import argparse
import os
import subprocess

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUN_FILES = ["fleet.pt", "norm.json", "split.json", "soh_int8.tflite", "soh_fp32.tflite",
             "gate_samples.npz", "export_report.json"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default="runs/ds1")
    ap.add_argument("--host", default="imx95")
    ap.add_argument("--dest", default="/tmp/batt_ft")
    a = ap.parse_args()
    run = os.path.join(ROOT, a.run)
    d = np.load(os.path.join(run, "targets.npz"))
    os.makedirs(os.path.join(run, "cars"), exist_ok=True)
    for c in np.unique(d["car"]):
        s = d["car"] == c
        np.savez(os.path.join(run, "cars", f"car_{c}.npz"), X=d["X"][s], car=d["car"][s],
                 mileage=d["mileage"][s], capacity=d["capacity"][s])
    print(f"split {len(np.unique(d['car']))} target cars -> {a.run}/cars/")
    # the board has no rsync: stream a tarball over ssh (code + this run's artifacts only)
    files = ["model", "board"] + [os.path.join(a.run, f) for f in RUN_FILES + ["cars"]
                                  if os.path.exists(os.path.join(run, f))]
    tar = subprocess.Popen(["tar", "-C", ROOT, "--exclude=__pycache__", "-cf", "-", *files], stdout=subprocess.PIPE)
    subprocess.run(["timeout", "-k", "5", "600", "ssh", a.host,
                    f"rm -rf {a.dest}/model {a.dest}/board {a.dest}/{a.run} && mkdir -p {a.dest} && tar -C {a.dest} -xf -"],
                   stdin=tar.stdout, check=True)
    tar.stdout.close()
    assert tar.wait() == 0, "tar failed"
    print(f"staged -> {a.host}:{a.dest}")


if __name__ == "__main__":
    main()
