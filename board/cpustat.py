"""Dependency-free measurement helpers for the board (no sysstat, no psutil).

- CPU utilisation: delta of /proc/stat jiffies over a real interval, per pinned core.
- Memory: VmHWM / VmRSS read from /proc/self/status (kernel's own peak-RSS counter),
  never from an allocator self-report.

VmHWM is a monotonic high-water mark for the life of the process. To attribute memory to a
phase (e.g. "training") we snapshot VmHWM/VmRSS at phase boundaries and, for the phase of
interest, run it in a FRESH process so its high-water mark is not contaminated by an earlier
phase. Every experiment records: absolute peak, the same-process baseline (interpreter +
libraries + model built, before the phase), and the delta.
"""
import json
import os
import platform
import time


def _status_kb(field, pid="self"):
    with open(f"/proc/{pid}/status") as f:
        for line in f:
            if line.startswith(field + ":"):
                return int(line.split()[1])
    raise KeyError(field)


def vm_hwm_kb(pid="self"):
    return _status_kb("VmHWM", pid)


def vm_rss_kb(pid="self"):
    return _status_kb("VmRSS", pid)


def _cpu_jiffies():
    """Return {cpuN: (busy, total)} from /proc/stat."""
    out = {}
    with open("/proc/stat") as f:
        for line in f:
            if not line.startswith("cpu"):
                break
            parts = line.split()
            vals = list(map(int, parts[1:]))
            idle = vals[3] + (vals[4] if len(vals) > 4 else 0)  # idle + iowait
            total = sum(vals[:8])  # exclude guest columns (already counted in user)
            out[parts[0]] = (total - idle, total)
    return out


class CpuSampler:
    """Delta-over-interval CPU utilisation. start() ... stop() -> {cpu: pct}."""

    def start(self):
        self._t0 = time.monotonic()
        self._j0 = _cpu_jiffies()
        return self

    def stop(self):
        j1 = _cpu_jiffies()
        dt = time.monotonic() - self._t0
        res = {"interval_s": round(dt, 3)}
        for k, (b1, t1) in j1.items():
            b0, t0 = self._j0.get(k, (0, 0))
            res[k] = round(100.0 * (b1 - b0) / (t1 - t0), 1) if t1 > t0 else None
        return res


def governor_state():
    """Per-cpu governor + cur freq, read-only. Missing cpufreq -> recorded as such."""
    st = {}
    base = "/sys/devices/system/cpu"
    for d in sorted(os.listdir(base)):
        if not (d.startswith("cpu") and d[3:].isdigit()):
            continue
        cf = os.path.join(base, d, "cpufreq")
        try:
            gov = open(os.path.join(cf, "scaling_governor")).read().strip()
            cur = int(open(os.path.join(cf, "scaling_cur_freq")).read())
        except OSError:
            gov, cur = "n/a", None
        st[d] = {"governor": gov, "cur_khz": cur}
    return st


def environment():
    """What the run was measured ON — rides with every MEASURED number."""
    env = {
        "host": platform.node(),
        "machine": platform.machine(),
        "python": platform.python_version(),
        "affinity": sorted(os.sched_getaffinity(0)),
        "loadavg": open("/proc/loadavg").read().split()[:3],
        "time": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }
    try:
        env["model"] = open("/proc/device-tree/model").read().strip("\x00\n")
    except OSError:
        env["model"] = "n/a"
    env["cpufreq"] = governor_state()
    return env


def dump(path, obj):
    with open(path, "w") as f:
        json.dump(obj, f, indent=2, sort_keys=True)
    print(f"wrote {path}")
