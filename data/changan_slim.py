"""Stream each Changan vinN.rar (one ~2 GB CSV inside, RAR5) into a slim per-vehicle .npz holding only the
scalar columns. The per-cell voltage / probe-temperature strings (most of the bytes) are not kept.

Never writes the CSV to disk: libarchive (RAR5-capable) -> chunked pandas parse -> numpy.
Frames with totalvoltage == 0 are invalid placeholders in the source and are dropped (count recorded).

Output: data/changan/slim/vinN.npz with float64 t (terminaltime, s) and float32 columns
  soc, speed, odo, status, V, I, vmin, vmax, tmin, tmax   (+ meta: n_raw, n_dropped)
Usage: python data/changan_slim.py data/raw/changan data/changan/slim [--jobs 12]
"""
import argparse
import io
import os
import re
from multiprocessing import Pool

import libarchive
import numpy as np
import pandas as pd

COLS = ["terminaltime", "soc", "speed", "totalodometer", "chargestatus", "totalvoltage", "totalcurrent",
        "minvoltagebattery", "maxvoltagebattery", "mintemperaturevalue", "maxtemperaturevalue"]
OUT = ["t", "soc", "speed", "odo", "status", "V", "I", "vmin", "vmax", "tmin", "tmax"]


class _Stream(io.RawIOBase):
    """File-like view over a libarchive entry's block iterator."""

    def __init__(self, blocks):
        self._it, self._buf = iter(blocks), b""

    def readable(self):
        return True

    def readinto(self, b):
        while not self._buf:
            try:
                self._buf = bytes(next(self._it))
            except StopIteration:
                return 0
        n = min(len(b), len(self._buf))
        b[:n], self._buf = self._buf[:n], self._buf[n:]
        return n


def slim(args):
    src, dst = args
    if os.path.exists(dst):
        return f"{os.path.basename(dst)}: exists"
    parts, n_raw = [], 0
    with libarchive.file_reader(src) as arc:
        for e in arc:
            stream = io.BufferedReader(_Stream(e.get_blocks()), buffer_size=16 << 20)
            for ch in pd.read_csv(stream, usecols=COLS, dtype={c: "float64" for c in COLS},
                                  chunksize=500_000, engine="c"):
                n_raw += len(ch)
                parts.append(ch[COLS].to_numpy())
            break  # one CSV per archive
    a = np.concatenate(parts)
    keep = a[:, 5] > 0
    a = a[keep]
    a = a[np.argsort(a[:, 0], kind="stable")]
    out = {"t": a[:, 0]}
    out.update({k: a[:, i].astype(np.float32) for i, k in enumerate(OUT) if k != "t"})
    np.savez(dst + ".part.npz", n_raw=n_raw, n_dropped=int((~keep).sum()), **out)
    os.replace(dst + ".part.npz", dst)
    return f"{os.path.basename(dst)}: {n_raw} rows, {int((~keep).sum())} invalid dropped"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--jobs", type=int, default=12)
    a = ap.parse_args()
    os.makedirs(a.dst, exist_ok=True)
    rars = sorted((f for f in os.listdir(a.src) if f.endswith(".rar")), key=lambda f: int(re.findall(r"\d+", f)[0]))
    todo = [(os.path.join(a.src, f), os.path.join(a.dst, f.replace(".rar", ".npz"))) for f in rars]
    with Pool(a.jobs) as p:
        for line in p.imap_unordered(slim, todo):
            print(line, flush=True)


if __name__ == "__main__":
    main()
