"""Reviewer: (1) what sets H2's fleet-wide 'smallest safe margin' (75 mV / 10 C)? Attribute unsafe frames at
(30,10), (50,10), (75,10) to month / rack / L_cell level. (2) Per-cell value H2 did not look at: when vmax is high,
how many cells are in the taper, and is the top cell persistent within a rack across sessions?"""
import glob, os, collections
import numpy as np
from multiprocessing import Pool
import sys
sys.path.insert(0, "<repo>/analysis")
import H2_replay as H2

FR = "<repo>/data/weihai/frames"
KEYS = [(30, 10), (50, 10), (75, 10), (100, 10), (50, 5)]


def one(p):
    Z = np.load(p)
    if "empty" in Z: return None
    V, T, dah = Z["V"].astype(float), Z["T"].astype(float), np.clip(Z["dah"], 0, None)
    if len(dah) < 30 or dah.sum() < 0.5: return None
    Lmm, Lcell, ts, ctp = H2.limiters(V, T, maps=H2.PMAPS[:1]); Lc = Lcell[0]
    vmean, tmean = V.mean(1), T.mean(1)
    out = {"name": os.path.basename(p), "n": len(dah), "uns": {}, "uns_Lc0": {}, "uns_vmax": {}}
    for m, mT in KEYS:
        Lp = np.minimum(H2.c_t(tmean - mT), H2.c_t(tmean + mT)) * H2.taper(vmean + m)
        u = Lp > Lc * H2.UNSAFE_TOL
        out["uns"][(m, mT)] = int(u.sum()); out["uns_Lc0"][(m, mT)] = int((u & (Lc <= 1e-6)).sum())
        out["uns_vmax"][(m, mT)] = V.max(1)[u].tolist()[:50]
    out["vmm_p999"] = float(np.percentile(V.max(1) - vmean, 99.9)); out["vmm_max"] = float((V.max(1) - vmean).max())
    out["tmm_max"] = float((T.max(1) - tmean).max()); out["tmn_max"] = float((tmean - T.min(1)).max())
    out["n_Lc0"] = int((Lc <= 1e-6).sum()); out["vmax_max"] = float(V.max())
    # balancing view: frames with vmax >= 3450: number of cells > 3400
    hi = V.max(1) >= 3450
    out["n_hi"] = int(hi.sum())
    out["cells_in_taper_med"] = float(np.median((V[hi] > 3400).sum(1))) if hi.any() else None
    out["top_cell_end"] = int(V[-1].argmax()); out["top_cell_mode"] = int(np.bincount(V.argmax(1)).argmax())
    out["vmin_cell_end"] = int(V[-1].argmin())
    return out


if __name__ == "__main__":
    paths = sorted(glob.glob(f"{FR}/*.npz"))
    with Pool(8) as pool:
        R = [r for r in pool.imap_unordered(one, paths, chunksize=8) if r]
    nfr = sum(r["n"] for r in R)
    print("sessions", len(R), "frames", nfr)
    for k in KEYS:
        tot = sum(r["uns"][k] for r in R); lc0 = sum(r["uns_Lc0"][k] for r in R)
        bym = collections.Counter(); byr = collections.Counter(); sess = 0
        for r in R:
            if r["uns"][k]:
                sess += 1; bym[r["name"][:6]] += r["uns"][k]; byr[r["name"].rsplit("_rack", 1)[1][:-4]] += r["uns"][k]
        vm = np.concatenate([np.array(r["uns_vmax"][k]) for r in R if r["uns_vmax"][k]]) if tot else np.array([])
        print(f"({k[0]} mV,{k[1]} C): unsafe {tot/nfr*100:.3f}% = {tot} frames in {sess} sessions; of which L_cell==0: {lc0}; "
              f"by month {dict(bym)}; by rack {dict(byr)}; vmax in unsafe frames median {np.median(vm) if len(vm) else float('nan'):.0f} mV")
    print("frames with L_cell == 0 (a cell >= 3650 mV):", sum(r["n_Lc0"] for r in R), "; sessions with any cell >= 3650:", sum(r["vmax_max"] >= 3650 for r in R), "; >= 3600:", sum(r["vmax_max"] >= 3600 for r in R))
    vmm = np.array([r["vmm_p999"] for r in R]); print(f"per-session p99.9(vmax-vmean): median {np.median(vmm):.1f} p90 {np.percentile(vmm,90):.1f} max {vmm.max():.1f} mV; max over sessions of max {max(r['vmm_max'] for r in R):.0f}")
    print(f"max over sessions of tmax-tmean {max(r['tmm_max'] for r in R):.1f} C, tmean-tmin {max(r['tmn_max'] for r in R):.1f} C")
    # balancing / weak-cell persistence
    hi = [r for r in R if r["n_hi"] > 0]
    print(f"sessions with any frame vmax>=3450: {len(hi)}/{len(R)}; median #cells>3400 in those frames (median over sessions): {np.median([r['cells_in_taper_med'] for r in hi]):.0f} of 396")
    byrack = collections.defaultdict(list)
    for r in R: byrack[r["name"].rsplit("_rack", 1)[1][:-4]].append(r)
    for rk in sorted(byrack, key=int):
        ends = [r["top_cell_end"] for r in byrack[rk]]; c = collections.Counter(ends).most_common(3)
        mins = collections.Counter([r["vmin_cell_end"] for r in byrack[rk]]).most_common(2)
        print(f"  rack {rk}: sessions {len(ends)}; end-of-charge top cell: top-3 identities {c} -> {c[0][1]/len(ends)*100:.0f}% same cell; end min cell {mins}")
