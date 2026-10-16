"""Experiment E §2.1 — re-ingest the per-cell columns that changan_slim.py deliberately dropped.

`batteryvoltage` (96 '~'-separated cell voltages, 1 mV) and `probetemperatures` (32 '~'-separated probes, 1 degC).
Streams each vinN.rar with libarchive (decodes the RAR5 method that 7z rejects with "Unsupported Method").

Per vehicle -> data/changan/cells/vinN.npz:
  every valid frame:  t, odo, I, status, vmean_mv, vsd_mv, vmin_mv, vmax_mv, imin, imax (cell index of min/max),
                      tmean, tsd, tmin, tmax, itmax
  every SUB-th valid frame (+ every frame in charge with max cell >= 4.15 V): t_full, dv_full = int16 per-cell
                      deviation from the frame's cell mean (mV), [n, 96]; dt_full = int8 probe deviation, [n, 32]
  sync: bool per valid frame — min AND max of the cell list match the scalar min/max columns within 0.5 mV.
        On vin3, 2 % of frames (28 of 332 days) carry a cell list up to 0.4 V away from the same frame's scalars,
        i.e. a stale/misaligned vector; full vectors are kept for synced frames only.
  meta: n_raw, n_placeholder (totalvoltage <= 0), n_malformed (cell list != 96 or probe list != 32 values; on vin3
        these include 6 % of frames with valid scalar telemetry and NO cell list, clustered in 46 days),
        n_minmax_mismatch (frames with sync == False)
Usage: python data/changan_cells.py data/raw/changan data/changan/cells [--jobs 12] [vin ...]
"""
import argparse
import io
import os
import re
from multiprocessing import Pool

import libarchive
import numpy as np
import pandas as pd

NC, NP = 96, 32
SUB = 6            # CHOSEN: keep the full cell vector every 6th frame (~1 min)
CHG_FULL_V = 4.15  # CHOSEN: and every frame near the top of charge (where the pack label is decided)
COLS = ["terminaltime", "totalodometer", "chargestatus", "totalvoltage", "totalcurrent",
        "minvoltagebattery", "maxvoltagebattery", "batteryvoltage", "probetemperatures"]


class _Stream(io.RawIOBase):
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


def parse_lists(s, n):
    """Series of '~'-joined strings -> (float array [k, n], mask of rows that had exactly n values)."""
    ok = (s.str.count("~") == n - 1).to_numpy()
    if not ok.any():
        return np.zeros((0, n)), ok
    tok = "~".join(s[ok].tolist()).split("~")
    try:
        a = np.array(tok, dtype=np.float64).reshape(-1, n)
    except ValueError:  # corrupted token(s), e.g. '\\24\\"' — the whole row counts as malformed
        a = pd.to_numeric(pd.Series(tok), errors="coerce").to_numpy().reshape(-1, n)
        good = ~np.isnan(a).any(1)
        ok[np.flatnonzero(ok)[~good]] = False
        a = a[good]
    return a, ok


def cells(args):
    src, dst = args
    if os.path.exists(dst):
        return f"{os.path.basename(dst)}: exists"
    acc = {k: [] for k in ["t", "odo", "I", "status", "vmean_mv", "vsd_mv", "vmin_mv", "vmax_mv", "imin", "imax",
                           "tmean", "tsd", "tmin", "tmax", "itmax", "sync"]}
    full_t, full_dv, full_dt = [], [], []
    n_raw = n_ph = n_bad = n_mm = 0
    k_global = 0
    with libarchive.file_reader(src) as arc:
        for e in arc:
            stream = io.BufferedReader(_Stream(e.get_blocks()), buffer_size=16 << 20)
            for ch in pd.read_csv(stream, usecols=COLS, chunksize=200_000, engine="c",
                                  dtype={"batteryvoltage": str, "probetemperatures": str}):
                n_raw += len(ch)
                ph = (ch["totalvoltage"].to_numpy() <= 0)
                n_ph += int(ph.sum())
                ch = ch[~ph]
                v, okv = parse_lists(ch["batteryvoltage"].fillna(""), NC)
                tp, okt = parse_lists(ch["probetemperatures"].fillna(""), NP)
                ok = okv & okt
                n_bad += int((~ok).sum())
                v, tp = v[ok[okv]], tp[ok[okt]]
                ch = ch[ok]
                vm = v.mean(1)
                sync = ((np.abs(v.min(1) - ch["minvoltagebattery"].to_numpy()) <= 5e-4)
                        & (np.abs(v.max(1) - ch["maxvoltagebattery"].to_numpy()) <= 5e-4))
                n_mm += int((~sync).sum())
                cur = ch["totalcurrent"].to_numpy()
                stat = ch["chargestatus"].to_numpy()
                acc["t"].append(ch["terminaltime"].to_numpy(np.float64))
                acc["odo"].append(ch["totalodometer"].to_numpy(np.float32))
                acc["I"].append(cur.astype(np.float32))
                acc["status"].append(stat.astype(np.int8))
                acc["vmean_mv"].append((vm * 1e3).astype(np.float32))
                acc["vsd_mv"].append((v.std(1) * 1e3).astype(np.float32))
                acc["vmin_mv"].append((v.min(1) * 1e3).astype(np.float32))
                acc["vmax_mv"].append((v.max(1) * 1e3).astype(np.float32))
                acc["imin"].append(v.argmin(1).astype(np.int8))
                acc["imax"].append(v.argmax(1).astype(np.int8))
                acc["tmean"].append(tp.mean(1).astype(np.float32))
                acc["tsd"].append(tp.std(1).astype(np.float32))
                acc["tmin"].append(tp.min(1).astype(np.float32))
                acc["tmax"].append(tp.max(1).astype(np.float32))
                acc["itmax"].append(tp.argmax(1).astype(np.int8))
                acc["sync"].append(sync)
                idx = np.arange(k_global, k_global + len(v))
                k_global += len(v)
                keep = sync & ((idx % SUB == 0) | ((stat == 1) & (v.max(1) >= CHG_FULL_V)))
                full_t.append(ch["terminaltime"].to_numpy(np.float64)[keep])
                full_dv.append(np.clip(np.rint((v[keep] - vm[keep, None]) * 1e3), -32767, 32767).astype(np.int16))
                full_dt.append(np.clip(np.rint(tp[keep] - tp[keep].mean(1, keepdims=True)), -127, 127).astype(np.int8))
            break  # one CSV per archive
    out = {k: np.concatenate(x) for k, x in acc.items()}
    o = np.argsort(out["t"], kind="stable")
    out = {k: x[o] for k, x in out.items()}
    ft = np.concatenate(full_t)
    fo = np.argsort(ft, kind="stable")
    np.savez(dst + ".part.npz", n_raw=n_raw, n_placeholder=n_ph, n_malformed=n_bad, n_minmax_mismatch=n_mm,
             t_full=ft[fo], dv_full=np.concatenate(full_dv)[fo], dt_full=np.concatenate(full_dt)[fo], **out)
    os.replace(dst + ".part.npz", dst)
    nv = len(out["t"])
    return (f"{os.path.basename(dst)}: raw {n_raw}, placeholder {n_ph}, malformed {n_bad} "
            f"({100 * n_bad / max(1, n_raw - n_ph):.2f}% of non-placeholder), valid {nv}, "
            f"min-mismatch {n_mm}, full-vector frames {len(ft)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--jobs", type=int, default=12)
    ap.add_argument("vins", nargs="*")
    a = ap.parse_args()
    os.makedirs(a.dst, exist_ok=True)
    rars = sorted((f for f in os.listdir(a.src) if f.endswith(".rar")), key=lambda f: int(re.findall(r"\d+", f)[0]))
    if a.vins:
        rars = [f for f in rars if re.findall(r"\d+", f)[0] in a.vins]
    todo = [(os.path.join(a.src, f), os.path.join(a.dst, f.replace(".rar", ".npz"))) for f in rars]
    with Pool(a.jobs) as p:
        for line in p.imap_unordered(cells, todo):
            print(line, flush=True)


if __name__ == "__main__":
    main()
