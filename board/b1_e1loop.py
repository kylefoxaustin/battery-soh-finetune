"""B1 concurrent real-time load, core 1 (briefs/B1/README.md §4.2): Study 1's int8 inference in a continuous loop over
the 256-snippet set, p50/p99 per 60 s block, its bit-identity gate once per block. Interpreter setup and the gate are
e1_inference.setup() / gate_pass(), unchanged; only the loop is new. Each inference is timed exactly as e1 times it
(reset_all_variables + set_tensor + invoke + get_tensor).

Usage: taskset -c 1 python3 board/b1_e1loop.py --run runs/ds1 --duration 9000 --out e1loop.jsonl
"""
import argparse
import json
import os
import signal
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import e1_inference as E1  # noqa: E402
import numpy as np  # noqa: E402

BLOCK_S = 60
STOP = False


def _stop(*_):
    global STOP
    STOP = True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--duration", type=float, required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    signal.signal(signal.SIGTERM, _stop)
    signal.signal(signal.SIGINT, _stop)
    ctx = E1.setup(a.run, "soh_int8.tflite", 1)
    it, i, o, Xq = ctx["it"], ctx["i"], ctx["o"], ctx["Xq"]
    for k in range(E1.WARMUP):
        it.reset_all_variables()
        it.set_tensor(i["index"], Xq[k % len(Xq):k % len(Xq) + 1])
        it.invoke()
    t_start = time.monotonic()
    t_end = t_start + a.duration
    k = 0
    with open(a.out, "w") as f:
        b = 0
        while not STOP and time.monotonic() < t_end:
            wall0, blk0 = time.time(), time.monotonic()
            gate = E1.gate_pass(ctx)
            gate_s = time.monotonic() - blk0
            lat = []
            stop_at = min(blk0 + BLOCK_S, t_end)
            while not STOP and time.monotonic() < stop_at:
                x = Xq[k % len(Xq):k % len(Xq) + 1]
                t0 = time.perf_counter_ns()
                it.reset_all_variables()
                it.set_tensor(i["index"], x)
                it.invoke()
                it.get_tensor(o["index"])
                lat.append((time.perf_counter_ns() - t0) / 1e6)
                k += 1
            if lat:
                la = np.array(lat)
                f.write(json.dumps({"block": b, "wall_start": round(wall0, 3), "t_s": round(blk0 - t_start, 2),
                                    "gate_pass": bool(gate["pass"]), "gate_max_lsb": gate["max_lsb_vs_host_int8"],
                                    "gate_s": round(gate_s, 2), "n": len(la),
                                    "p50_ms": float(np.percentile(la, 50)), "p99_ms": float(np.percentile(la, 99)),
                                    "p999_ms": float(np.percentile(la, 99.9)), "max_ms": float(la.max()),
                                    "mean_ms": float(la.mean()),
                                    "partial": bool(time.monotonic() < blk0 + BLOCK_S - 0.5)}) + "\n")
                f.flush()
            b += 1


if __name__ == "__main__":
    main()
