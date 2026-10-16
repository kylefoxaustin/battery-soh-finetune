"""Experiment H2-b reference + gate (pre-registered in results/H2/H2_preregistration.md, commit bf6ca52).
Reuses board/h_ref.py (reference model, gate) with the H2 LFP limit map (voltage taper, VLIM 3650 mV) and real
Weihai geometry: N=396 cells / P=216 probes per rack; N=3564 / P=1944 = the 9 racks of one operation at the same
grid time, concatenated (whole cluster as one limiter).
Frames: charge-operation grid frames (analysis/H2_replay.py extract), round-robin across operations.
Current per frame = rack charge current from dAh over the 10 s grid (charge negative), as the H frames used.
Usage: python board/h2_ref.py build OUTDIR [--frames 10000]
       python board/h2_ref.py gate OUTDIR N gate_out_N.bin
"""
import argparse
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "analysis"))
import h_ref  # noqa: E402
import H2_replay as H2  # noqa: E402

h_ref.VLIM = 3650                                   # LFP cell limit (H2 prereg); compile the C side with -DVLIM=3650
FR = os.path.join(HERE, "..", "data", "weihai", "frames")
NS = {396: 216, 3564: 1944}


def luts():
    mv = np.arange(h_ref.V0, h_ref.V0 + h_ref.NV, dtype=float)
    taper = H2.taper(mv).astype(np.float32)
    ct = H2.c_t((h_ref.T0 + np.arange(h_ref.NT)) / 10.0).astype(np.float32)
    return taper, ct


h_ref.luts = luts                                   # gate() calls h_ref.luts()


def _load(p):
    Z = np.load(p)
    return None if "empty" in Z else (Z["V"], np.rint(Z["T"] * 10).astype(np.int16), (-Z["dah"] * 360.0).astype(np.float32),
                                      Z["grid"])


def stream(nframes):
    """per-op: (V [n, 3564], T [n, 1944], I [n]) on grid times common to all 9 racks; round-robin over ops"""
    ops = sorted({os.path.basename(p).rsplit("_rack", 1)[0] for p in glob.glob(f"{FR}/*.npz")})
    per = max(1, nframes // 40)
    Vs, Ts, Is = [], [], []
    for op in ops:
        R = [_load(f"{FR}/{op}_rack{r}.npz") for r in range(1, 10)]
        if any(x is None for x in R):
            continue
        common = R[0][3]
        for x in R[1:]:
            common = np.intersect1d(common, x[3])
        if len(common) < per:
            continue
        common = common[:per]
        sel = [np.searchsorted(x[3], common) for x in R]
        Vs.append(np.concatenate([x[0][s] for x, s in zip(R, sel)], 1))
        Ts.append(np.concatenate([x[1][s] for x, s in zip(R, sel)], 1))
        Is.append(R[0][2][sel[0]])
        if sum(len(i) for i in Is) >= nframes:
            break
    return np.concatenate(Vs)[:nframes], np.concatenate(Ts)[:nframes], np.concatenate(Is)[:nframes]


def build(out, nframes):
    os.makedirs(out, exist_ok=True)
    taper, ct = luts()
    with open(f"{out}/luts.bin", "wb") as fh:
        fh.write(taper.tobytes()); fh.write(ct.tobytes())
    V9, T9, I = stream(nframes)
    meta = {"n_frames": int(len(I)), "VLIM": h_ref.VLIM}
    for N, P in NS.items():
        V, T = V9[:, :N].copy(), T9[:, :P].copy()   # N=396: rack 1 of each op; N=3564: all 9 racks
        F = len(I)
        with open(f"{out}/frames_{N}.bin", "wb") as fh:
            fh.write(np.array([N, P, F], np.int32).tobytes())
            fh.write(I.tobytes()); fh.write(V.tobytes()); fh.write(T.tobytes())
        arg, sp, r, c = h_ref.reference(V, T, I, taper, ct)
        np.savez(f"{out}/ref_{N}.npz", arg=arg, sp=sp, r=r, cmin=c.min(1),
                 ntie=(c <= c.min(1, keepdims=True) * (1 + 1e-9) + 1e-12).sum(1))
        meta[N] = {"P": P, "F": F}
    json.dump(meta, open(f"{out}/build.json", "w"), indent=1)
    print(json.dumps(meta))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["build", "gate"])
    ap.add_argument("out")
    ap.add_argument("N", nargs="?", type=int)
    ap.add_argument("path", nargs="?")
    ap.add_argument("--frames", type=int, default=10000)
    a = ap.parse_args()
    build(a.out, a.frames) if a.mode == "build" else h_ref.gate(a.out, a.N, a.path)
