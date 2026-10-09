"""Board census: every process, binary resolved via /proc/PID/exe, CPU as a DELTA over a real
interval (not ps's lifetime average), RSS, state. Standalone, stdlib only.

Usage: python3 census.py [--interval 5] [--json out.json]
Prints tenants using > 0.5% of one core over the interval, plus every process count by exe.
"""
import argparse
import json
import os
import time

HZ = os.sysconf("SC_CLK_TCK")


def snap():
    out = {}
    for p in os.listdir("/proc"):
        if not p.isdigit():
            continue
        try:
            st = open(f"/proc/{p}/stat").read()
            rest = st[st.rindex(")") + 2:].split()
            state, ppid, ut, stt = rest[0], int(rest[1]), int(rest[11]), int(rest[12])
            try:
                exe = os.readlink(f"/proc/{p}/exe")
            except OSError:
                exe = "[kernel]" if not open(f"/proc/{p}/cmdline").read() else "[unreadable]"
            cmd = open(f"/proc/{p}/cmdline").read().replace("\0", " ").strip()[:160]
            rss = 0
            for line in open(f"/proc/{p}/status"):
                if line.startswith("VmRSS:"):
                    rss = int(line.split()[1])
            out[int(p)] = {"exe": exe, "cmd": cmd, "state": state, "ppid": ppid, "ticks": ut + stt, "rss_kb": rss}
        except (OSError, ValueError):
            continue
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--interval", type=float, default=5.0)
    ap.add_argument("--json", default=None)
    a = ap.parse_args()
    s0, t0 = snap(), time.monotonic()
    time.sleep(a.interval)
    s1, dt = snap(), time.monotonic() - t0
    me = os.getpid()
    rows = []
    for pid, r in s1.items():
        d = r["ticks"] - s0.get(pid, {"ticks": r["ticks"]})["ticks"]
        r["cpu_pct"] = round(100.0 * d / HZ / dt, 2)
        r["pid"] = pid
        r["self"] = pid == me
        rows.append(r)
    load = open("/proc/loadavg").read().split()[:3]
    busy = sorted([r for r in rows if r["cpu_pct"] > 0.5 and not r["self"]], key=lambda r: -r["cpu_pct"])
    print(f"census interval={dt:.1f}s procs={len(rows)} loadavg={load}")
    for r in busy:
        print(f"  BUSY pid={r['pid']} cpu={r['cpu_pct']}% rss={r['rss_kb']}KB exe={r['exe']} cmd={r['cmd'][:80]}")
    if not busy:
        print("  no process > 0.5% of a core over the interval (self excluded)")
    if a.json:
        json.dump({"interval_s": dt, "loadavg": load, "procs": rows}, open(a.json, "w"), indent=1)


if __name__ == "__main__":
    main()
