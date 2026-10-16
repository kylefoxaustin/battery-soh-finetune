"""Reviewer check: Weihai logging structure. Are cell voltage logs synchronous across the 396 cells? gap vs step
cross-tab (deadband/heartbeat?), staleness at the 10 s grid, and the spread inflation from asynchronous sampling.
Also hour-of-day of charge starts (timezone check) across all months' frames."""
import sys, glob, os, collections
import numpy as np, h5py
sys.path.insert(0, "<repo>/analysis")
import mcos_dt

fn = "<repo>/data/raw/weihai/OperationCondition_202410_All.mat"
f = h5py.File(fn, "r")
refs, cells, *_ = mcos_dt.obj_cells(f)
top = [k for k in f.keys() if not k.startswith("#")][0]; G = f[top]
charge_ops = [op for op in G.keys() if "".join(map(chr, G[op]["Type"][()].ravel())) == "Charge"]
print("charge ops in Oct:", len(charge_ops), charge_ops[:5])
for op in charge_ops[:2]:
    g = G[op]; R = g["Rack1"]
    st = mcos_dt.dt_ms(f, refs, cells, g["StartTime"][()])[0] / 1e3
    en = mcos_dt.dt_ms(f, refs, cells, g["EndTime"][()])[0] / 1e3
    T = []; Vv = []
    for k in range(1, 397):
        T.append(mcos_dt.dt_ms(f, refs, cells, R[f"Voltage{k}"]["t"][()]) / 1e3); Vv.append(R[f"Voltage{k}"]["value"][()].ravel())
    # synchronicity: fraction of log instants shared by all cells
    allt = np.concatenate(T); u, c = np.unique(np.round(allt, 1), return_counts=True)
    print(f"{op}: dur {en-st:.0f}s; distinct log instants {len(u)}; instants with all 396 cells {np.sum(c==396)}; "
          f"with >=390 {np.sum(c>=390)}; with 1 cell {np.sum(c==1)}; counts hist: {dict(collections.Counter(np.minimum(c,400)//50*50))}")
    # gap vs step crosstab for a cell
    gaps = []; steps = []
    for tt, vv in zip(T, Vv):
        gaps += np.diff(tt).tolist(); steps += np.abs(np.rint(np.diff(vv) * 1e3)).astype(int).tolist()
    gaps = np.array(gaps); steps = np.array(steps)
    for lo, hi in [(0, 30), (30, 90), (90, 150), (150, 599), (599, 601)]:
        m = (gaps >= lo) & (gaps < hi)
        if m.any():
            print(f"   gap {lo}-{hi}s: n={m.sum()} frac_step0={np.mean(steps[m]==0):.2f} median_step={np.median(steps[m]):.0f} mV")
    # frames: staleness at the 10 s grid; and spread inflation (spread at grid vs spread at synchronous instants)
    grid = np.arange(st, en, 10.0)
    age = np.stack([grid - tt[np.clip(np.searchsorted(tt, grid, side="right") - 1, 0, None)] for tt in T], 1)
    print(f"   ZOH age at grid (s): median {np.median(age):.0f} p90 {np.percentile(age,90):.0f} max {age.max():.0f}")
    Vg = np.stack([vv[np.clip(np.searchsorted(tt, grid, side="right") - 1, 0, None)] for tt, vv in zip(T, Vv)], 1)
    spread_grid = (Vg.max(1) - Vg.min(1)) * 1e3
    sync_t = u[c == 396]
    if len(sync_t):
        Vs = np.stack([vv[np.searchsorted(tt, sync_t)] for tt, vv in zip(T, Vv)], 1)
        spread_sync = (Vs.max(1) - Vs.min(1)) * 1e3
        print(f"   spread vmax-vmin: grid median {np.median(spread_grid):.1f} mV p99 {np.percentile(spread_grid,99):.1f}; "
              f"synchronous instants median {np.median(spread_sync):.1f} p99 {np.percentile(spread_sync,99):.1f} (n={len(sync_t)})")
        # vmax-vmean
        print(f"   vmax-vmean: grid p99.9 {np.percentile((Vg.max(1)-Vg.mean(1))*1e3,99.9):.1f} mV; sync p99.9 {np.percentile((Vs.max(1)-Vs.mean(1))*1e3,99.9):.1f}")
        # rate of voltage rise at the top
        vm = Vs.max(1); dv = np.diff(vm) * 1e3 / np.diff(sync_t)
        print(f"   dVmax/dt at synchronous instants (mV/s): p50 {np.median(dv):.3f} p99 {np.percentile(dv,99):.3f}; top V {vm.max():.3f}")
    # rack SOC & Ah
    ti = mcos_dt.dt_ms(f, refs, cells, g["Rack1CurrentTime"][()]) / 1e3; ii = g["Rack1CurrentValue"][()].ravel()
    ah = np.trapz(np.clip(-ii, 0, None), ti) / 3600
    ss = g["Rack1SOCValue"][()].ravel()
    print(f"   rack Ah charged {ah:.1f}; SOC {ss[0]:.0f}->{ss[-1]:.0f} => implied rack capacity {ah/((ss[-1]-ss[0])/100):.0f} Ah; "
          f"median I {np.median(ii):.1f} A => {abs(np.median(ii))/(ah/((ss[-1]-ss[0])/100)):.2f} C")

# hour-of-day of charge starts, all months (frames grid[0]), naive-UTC interpretation
hrs = []
for p in sorted(glob.glob("<repo>/data/weihai/frames/*_rack1.npz")):
    Z = np.load(p)
    if "empty" in Z: continue
    hrs.append((Z["grid"][0] % 86400) / 3600)
hrs = np.array(hrs)
h, _ = np.histogram(hrs, bins=24, range=(0, 24))
print("charge-start hour histogram (as decoded, UTC-naive):", h.tolist())
print("if local (UTC+8) wall-clock, decoded hour == local hour; if true UTC, local = decoded+8")
