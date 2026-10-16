"""Experiment H-b reference + gate (pre-registered in results/H/H_preregistration.md, commit 43485e8).
  build : LUTs (same limit map as analysis/H_replay.py), held-out frame files (vehicles with id % 10 == 0, charging,
          synced full vectors) for N = 96, 192, 324, 1000, and the Python reference outputs for each.
          N > 96 tiles consecutive real 96-cell frames into one wider pack (real values, synthetic geometry; ASSUMED).
  gate  : compare the board's gate_out_N.bin against ref_N.npz.
Usage: python board/h_ref.py build OUTDIR [--frames 10000]
       python board/h_ref.py gate OUTDIR N gate_out_N.bin
"""
import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "analysis"))
import H_replay as H  # noqa: E402  (same limit map, OCV table)

V0, NV, T0, NT = 2500, 2001, -400, 1401
VLIM, ALPHA, DI_MIN, C_NOM = 4250, np.float32(0.05), np.float32(5.0), np.float32(120.0)
NS = [96, 192, 324, 1000]


def luts():
    mv = np.arange(V0, V0 + NV, dtype=float)
    taper = H.taper(H.soc(mv)).astype(np.float32)
    ct = H.c_t((T0 + np.arange(NT)) / 10.0).astype(np.float32)
    return taper, ct


def stream(n_needed):
    """real charging synced full frames from held-out vehicles, round-robin in chunks so no vehicle dominates"""
    Vs, Ts, Is = [], [], []
    per = max(1, n_needed // 25)
    for car in range(10, 301, 10):
        p = f"{H.CELLS}/vin{car}.npz"
        if not os.path.exists(p):
            continue
        Z = np.load(p)
        t, st, sync, I = Z["t"], Z["status"], Z["sync"], Z["I"]
        tf = Z["t_full"]
        j = np.clip(np.searchsorted(t, tf), 0, len(t) - 1)
        ok = np.flatnonzero((t[j] == tf) & (st[j] == 1) & sync[j])[:per]
        if not len(ok):
            continue
        jj = j[ok]
        Vs.append(np.rint(Z["vmean_mv"][jj][:, None] + Z["dv_full"][ok]).astype(np.int16))
        Ts.append(np.rint((Z["tmean"][jj][:, None] + Z["dt_full"][ok]) * 10).astype(np.int16))
        Is.append(I[jj].astype(np.float32))
        if sum(len(x) for x in Is) >= n_needed:
            break
    return np.concatenate(Vs)[:n_needed], np.concatenate(Ts)[:n_needed], np.concatenate(Is)[:n_needed]


def reference(V, T, I, taper, ct):
    F, N = V.shape
    pidx = (np.arange(N) * T.shape[1]) // N           # = k // 3 for N=96, P=32 (H); generalised for H2
    vi = np.clip(V.astype(np.int32) - V0, 0, NV - 1)
    ti = np.clip(T[:, pidx].astype(np.int32) - T0, 0, NT - 1)
    c = ct[ti] * taper[vi]                                     # float32 * float32
    c = np.where(V >= VLIM, np.float32(0.0), c)
    arg = c.argmin(1).astype(np.int32)
    L = c.min(1)
    sp = (L * C_NOM).astype(np.float32)
    r = np.zeros(N, np.float32)
    vprev = np.zeros(N, np.int16)
    iprev, have = np.float32(0.0), False
    for f in range(F):
        di = np.float32(I[f] - iprev)
        if have and (di > DI_MIN or di < -DI_MIN):
            rk = (V[f].astype(np.int32) - vprev.astype(np.int32)).astype(np.float32) / di
            r = (r + ALPHA * (rk - r)).astype(np.float32)
        vprev = V[f].copy()
        iprev, have = np.float32(I[f]), True
    return arg, sp, r, c


def build(out, nframes):
    os.makedirs(out, exist_ok=True)
    taper, ct = luts()
    with open(f"{out}/luts.bin", "wb") as fh:
        fh.write(taper.tobytes()); fh.write(ct.tobytes())
    k_max = -(-max(NS) // 96)
    V96, T96, I96 = stream(nframes * k_max)
    meta = {"n_stream_frames": int(len(I96))}
    for N in NS:
        k, P = -(-N // 96), -(-N // 3)
        F = min(nframes, len(I96) // k)
        V = V96[: F * k].reshape(F, k * 96)[:, :N].copy()
        T = T96[: F * k].reshape(F, k * 32)
        T = np.concatenate([T, T[:, : max(0, P - T.shape[1])]], 1)[:, :P].copy()
        I = I96[: F * k : k].copy()
        with open(f"{out}/frames_{N}.bin", "wb") as fh:
            fh.write(np.array([N, P, F], np.int32).tobytes())
            fh.write(I.astype(np.float32).tobytes()); fh.write(V.tobytes()); fh.write(T.tobytes())
        arg, sp, r, c = reference(V, T, I, taper, ct)
        np.savez(f"{out}/ref_{N}.npz", arg=arg, sp=sp, r=r, cmin=c.min(1),
                 ntie=(c <= c.min(1, keepdims=True) * (1 + 1e-9) + 1e-12).sum(1))
        meta[N] = {"P": P, "F": int(F)}
    json.dump(meta, open(f"{out}/build.json", "w"), indent=1)
    print(json.dumps(meta))


def gate(out, N, path):
    R = np.load(f"{out}/ref_{N}.npz")
    F = len(R["arg"])
    raw = open(path, "rb").read()
    arg = np.frombuffer(raw, np.int32, F)
    sp = np.frombuffer(raw, np.float32, F, offset=4 * F)
    r = np.frombuffer(raw, np.float32, N, offset=8 * F)
    # tie rule: board argmin counts as a match if its own value equals the minimum (recomputed by reference)
    V = np.fromfile(f"{out}/frames_{N}.bin", np.int16, offset=12 + 4 * F, count=F * N).reshape(F, N)
    T = np.fromfile(f"{out}/frames_{N}.bin", np.int16, offset=12 + 4 * F + 2 * F * N, count=-1).reshape(F, -1)
    taper, ct = luts()
    pidx = (np.arange(N) * T.shape[1]) // N
    rows = np.arange(F)
    vb = ct[np.clip(T[rows, pidx[arg]].astype(np.int32) - T0, 0, NT - 1)] * taper[np.clip(V[rows, arg].astype(np.int32) - V0, 0, NV - 1)]
    vb = np.where(V[rows, arg] >= VLIM, np.float32(0), vb)
    exact = float((arg == R["arg"]).mean())
    tie_ok = float(((arg == R["arg"]) | (vb <= R["cmin"] * (1 + 1e-9) + 1e-12)).mean())
    dsp_c = float(np.abs(sp - R["sp"]).max() / float(C_NOM))
    dr = float(np.abs(r - R["r"]).max())
    res = {"N": N, "frames": F, "argmin_exact": exact, "argmin_tie_ok": tie_ok, "max_abs_dsetpoint_C": dsp_c,
           "max_abs_dR": dr, "frames_with_ties": int((R["ntie"] > 1).sum()),
           "PASS": bool(tie_ok == 1.0 and dsp_c <= 1e-4 and dr <= 1e-3)}
    print(json.dumps(res))
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["build", "gate"])
    ap.add_argument("out")
    ap.add_argument("N", nargs="?", type=int)
    ap.add_argument("path", nargs="?")
    ap.add_argument("--frames", type=int, default=10000)
    a = ap.parse_args()
    build(a.out, a.frames) if a.mode == "build" else gate(a.out, a.N, a.path)
