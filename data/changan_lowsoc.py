"""Experiment X8 §3 loader: every Changan frame at low SOC, with the full per-cell vector.

changan_cells.py keeps the 96-cell vector only every 6th frame (~1 min) outside the top of charge, so consecutive-frame
current steps (X2's R identification) cannot be formed at the bottom of the SOC range. This re-streams each vinN.rar
(libarchive, never writing the CSV) and keeps **every** valid frame with soc < SOC_KEEP, with all 96 cell voltages and
32 probe temperatures. Reuses changan_cells.py's stream wrapper and list parser.

Per vehicle -> data/changan/lowsoc/vinN.npz:
  t (s), soc (%), I (A, source sign: discharge > 0), status, V_mv [n, 96] int16 (absolute cell voltage, 1 mV),
  T_c [n, 32] int8 (probe temperature, 1 degC), sync (cell-list min/max match the scalar columns within 0.5 mV)
  meta: n_raw, n_placeholder, n_lowsoc_rows, n_malformed (cell or probe list not 96 / 32 values)
Usage: python -E data/changan_lowsoc.py data/raw/changan data/changan/lowsoc [--jobs 10] [vin ...]
"""
import argparse
import io
import os
import re
import sys
from multiprocessing import Pool

import libarchive
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from changan_cells import NC, NP, _Stream, parse_lists  # noqa: E402

SOC_KEEP = 30.0    # CHOSEN: wider than the 20 % scored band so R history and the 20-30 % context are available
COLS = ["terminaltime", "soc", "chargestatus", "totalvoltage", "totalcurrent",
        "minvoltagebattery", "maxvoltagebattery", "batteryvoltage", "probetemperatures"]


def lowsoc(args):
    src, dst = args
    if os.path.exists(dst):
        return f"{os.path.basename(dst)}: exists"
    acc = {k: [] for k in ["t", "soc", "I", "status", "V_mv", "T_c", "sync"]}
    n_raw = n_ph = n_low = n_bad = 0
    with libarchive.file_reader(src) as arc:
        for e in arc:
            stream = io.BufferedReader(_Stream(e.get_blocks()), buffer_size=16 << 20)
            for ch in pd.read_csv(stream, usecols=COLS, chunksize=200_000, engine="c",
                                  dtype={"batteryvoltage": str, "probetemperatures": str}):
                n_raw += len(ch)
                ph = ch["totalvoltage"].to_numpy() <= 0
                n_ph += int(ph.sum())
                ch = ch[(~ph) & (ch["soc"].to_numpy() < SOC_KEEP)]
                n_low += len(ch)
                if not len(ch):
                    continue
                v, okv = parse_lists(ch["batteryvoltage"].fillna(""), NC)
                tp, okt = parse_lists(ch["probetemperatures"].fillna(""), NP)
                ok = okv & okt
                n_bad += int((~ok).sum())
                v, tp = v[ok[okv]], tp[ok[okt]]
                ch = ch[ok]
                acc["sync"].append((np.abs(v.min(1) - ch["minvoltagebattery"].to_numpy()) <= 5e-4)
                                   & (np.abs(v.max(1) - ch["maxvoltagebattery"].to_numpy()) <= 5e-4))
                acc["t"].append(ch["terminaltime"].to_numpy(np.float64))
                acc["soc"].append(ch["soc"].to_numpy(np.float32))
                acc["I"].append(ch["totalcurrent"].to_numpy(np.float32))
                acc["status"].append(ch["chargestatus"].to_numpy().astype(np.int8))
                acc["V_mv"].append(np.clip(np.rint(v * 1e3), -32767, 32767).astype(np.int16))
                acc["T_c"].append(np.clip(np.rint(tp), -127, 127).astype(np.int8))
            break  # one CSV per archive
    if acc["t"]:
        out = {k: np.concatenate(x) for k, x in acc.items()}
    else:
        out = {"t": np.zeros(0), "soc": np.zeros(0, np.float32), "I": np.zeros(0, np.float32),
               "status": np.zeros(0, np.int8), "V_mv": np.zeros((0, NC), np.int16),
               "T_c": np.zeros((0, NP), np.int8), "sync": np.zeros(0, bool)}
    o = np.argsort(out["t"], kind="stable")
    out = {k: x[o] for k, x in out.items()}
    np.savez(dst + ".part.npz", n_raw=n_raw, n_placeholder=n_ph, n_lowsoc_rows=n_low, n_malformed=n_bad, **out)
    os.replace(dst + ".part.npz", dst)
    return f"{os.path.basename(dst)}: raw {n_raw}, low-SOC {n_low}, malformed {n_bad}, kept {len(out['t'])}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--jobs", type=int, default=10)
    ap.add_argument("vins", nargs="*")
    a = ap.parse_args()
    os.makedirs(a.dst, exist_ok=True)
    rars = sorted((f for f in os.listdir(a.src) if f.endswith(".rar")), key=lambda f: int(re.findall(r"\d+", f)[0]))
    if a.vins:
        rars = [f for f in rars if re.findall(r"\d+", f)[0] in a.vins]
    todo = [(os.path.join(a.src, f), os.path.join(a.dst, f.replace(".rar", ".npz"))) for f in rars]
    with Pool(a.jobs) as p:
        for line in p.imap_unordered(lowsoc, todo):
            print(line, flush=True)


if __name__ == "__main__":
    main()
