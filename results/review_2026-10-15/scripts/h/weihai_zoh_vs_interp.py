"""Reviewer: how much do H2's margin-sweep numbers depend on zero-order hold of staggered ~60 s cell logs?
Rebuild rack-1 frames for the Oct charge ops two ways: ZOH (as H2_replay.extract) and linear interpolation in time
(non-causal, removes most staleness skew). Run the H2 limiters + margin sweep on both. All DERIVED, limits ASSUMED."""
import sys, os
import numpy as np, h5py
sys.path.insert(0, "<repo>/analysis")
import mcos_dt
import H2_replay as H2

fn = "<repo>/data/raw/weihai/OperationCondition_202410_All.mat"
f = h5py.File(fn, "r")
refs, cells, *_ = mcos_dt.obj_cells(f)
top = [k for k in f.keys() if not k.startswith("#")][0]; G = f[top]
ops = [op for op in G.keys() if "".join(map(chr, G[op]["Type"][()].ravel())) == "Charge"]
NOPS = int(sys.argv[1]) if len(sys.argv) > 1 else 6
rack = 1
acc = {"zoh": [], "interp": []}
for op in ops[:NOPS]:
    g = G[op]; R = g[f"Rack{rack}"]
    st = mcos_dt.dt_ms(f, refs, cells, g["StartTime"][()])[0] / 1e3
    en = mcos_dt.dt_ms(f, refs, cells, g["EndTime"][()])[0] / 1e3
    Vs = [H2._series(f, refs, cells, R[f"Voltage{k}"]) for k in range(1, 397)]
    Ts = [H2._series(f, refs, cells, R[f"Temperature{p}"]) for p in range(1, 217)]
    t0 = max([s[0][0] for s in Vs] + [s[0][0] for s in Ts])
    grid = np.arange(max(st, t0), en, 10.0)
    ti, ii = H2._series(f, refs, cells, {"t": g[f"Rack{rack}CurrentTime"], "value": g[f"Rack{rack}CurrentValue"]})
    cah = np.interp(grid, ti, H2._cum_ah(ti, ii)); dah = np.clip(np.diff(cah, prepend=cah[0]), 0, None)
    frames = {"zoh": (np.stack([H2._zoh(t, v, grid) for t, v in Vs], 1) * 1e3, np.stack([H2._zoh(t, v, grid) for t, v in Ts], 1)),
              "interp": (np.stack([np.interp(grid, t, v) for t, v in Vs], 1) * 1e3, np.stack([np.interp(grid, t, v) for t, v in Ts], 1))}
    for mode, (V, T) in frames.items():
        V = np.rint(V); T = np.rint(T) if mode == "zoh" else T
        Lmm, Lcell, ts, ctp = H2.limiters(V, T, maps=H2.PMAPS[:1])
        tmm, tcell = H2.t_of(dah, Lmm), H2.t_of(dah, Lcell[0])
        vmean, tmean = V.mean(1), T.mean(1)
        sw = {}
        for m in H2.M_MV:
            tsp = H2.taper(vmean + m)
            for mT in H2.M_T:
                Lp = np.minimum(H2.c_t(tmean - mT), H2.c_t(tmean + mT)) * tsp
                sw[(m, mT)] = (H2.t_of(dah, Lp), int((Lp > Lcell[0] * H2.UNSAFE_TOL).sum()))
        acc[mode].append({"op": op, "n": len(grid), "tmm": tmm, "tcell": tcell, "sw": sw,
                          "vspread_med": float(np.median(V.max(1) - V.min(1))),
                          "vmax_minus_vmean_p999": float(np.percentile(V.max(1) - V.mean(1), 99.9)),
                          "vmax_minus_vmean_p99": float(np.percentile(V.max(1) - V.mean(1), 99)),
                          "vmax_med": float(np.median(V.max(1))), "vmax_max": float(V.max()),
                          "ndiff": int((np.abs(Lcell[0] - Lmm) > 1e-9).sum())})
    print(op, "frames", len(grid), flush=True)
for mode in ["zoh", "interp"]:
    A = acc[mode]; nfr = sum(a["n"] for a in A)
    S_mm = [1 - a["tcell"] / a["tmm"] for a in A]
    print(f"\n== {mode}: ops {len(A)} frames {nfr}")
    print(f"   S_mm per op median {np.median(S_mm)*100:.3f}% max {max(S_mm)*100:.3f}%; frames L_cell!=L_mm {sum(a['ndiff'] for a in A)/nfr*100:.2f}%")
    print(f"   vspread median {np.median([a['vspread_med'] for a in A]):.1f} mV; vmax-vmean p99 median-over-ops {np.median([a['vmax_minus_vmean_p99'] for a in A]):.1f}, p99.9 {np.median([a['vmax_minus_vmean_p999'] for a in A]):.1f} mV; vmax med {np.median([a['vmax_med'] for a in A]):.0f} max {max(a['vmax_max'] for a in A):.0f}")
    safe = []
    for m in H2.M_MV:
        for mT in H2.M_T:
            u = sum(a["sw"][(m, mT)][1] for a in A) / nfr
            Sp = np.median([1 - a["tcell"] / a["sw"][(m, mT)][0] for a in A])
            if u <= 0.001: safe.append((m, mT, round(u * 100, 3), round(Sp * 100, 1)))
    print("   safe margins (m mV, mT C, unsafe %, median S_pack %):", safe[:6])
    for key in [(30, 10), (50, 5), (50, 10), (75, 10), (100, 10)]:
        u = sum(a["sw"][key][1] for a in A) / nfr; Sp = np.median([1 - a["tcell"] / a["sw"][key][0] for a in A])
        print(f"   {key}: unsafe {u*100:.3f}%  S_pack median {Sp*100:.1f}%")
