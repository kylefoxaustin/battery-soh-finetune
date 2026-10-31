"""B1 monitor, core 5 (briefs/B1/README.md §2, §4.5): every 10 s, per-core utilisation as a /proc/stat delta
(cpustat.py), each core's current frequency, every thermal zone's temperature and the page-cache dirty/writeback
totals, so a thermal throttle or frequency drop is seen, not assumed.

Usage: taskset -c 5 python3 board/b1_cpumon.py --duration 9000 --out cpumon.jsonl
"""
import argparse
import glob
import json
import os
import signal
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cpustat  # noqa: E402

STOP = False


def _stop(*_):
    global STOP
    STOP = True


def thermal():
    out = {}
    for z in sorted(glob.glob("/sys/class/thermal/thermal_zone*")):
        try:
            out[open(f"{z}/type").read().strip() or os.path.basename(z)] = int(open(f"{z}/temp").read()) / 1000
        except OSError:
            pass
    return out


def meminfo(keys=("Dirty", "Writeback", "MemAvailable", "Cached")):
    out = {}
    for line in open("/proc/meminfo"):
        k = line.split(":")[0]
        if k in keys:
            out[k + "_kb"] = int(line.split()[1])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--duration", type=float, required=True)
    ap.add_argument("--interval", type=float, default=10.0)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    signal.signal(signal.SIGTERM, _stop)
    signal.signal(signal.SIGINT, _stop)
    t_end = time.monotonic() + a.duration
    with open(a.out, "w") as f:
        while not STOP and time.monotonic() < t_end:
            s = cpustat.CpuSampler().start()
            nxt = time.monotonic() + a.interval
            while not STOP and time.monotonic() < nxt:
                time.sleep(0.5)
            u = s.stop()
            gov = cpustat.governor_state()
            f.write(json.dumps({"wall": round(time.time(), 1), "util_pct": u,
                                "cur_khz": {c: v["cur_khz"] for c, v in gov.items()},
                                "governor": sorted({v["governor"] for v in gov.values()}),
                                "thermal_c": thermal(), **meminfo()}) + "\n")
            f.flush()


if __name__ == "__main__":
    main()
