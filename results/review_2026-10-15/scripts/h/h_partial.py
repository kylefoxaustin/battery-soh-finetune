"""Reviewer partial re-run of H_replay on a few vehicles: Ah-weighted (total-time) saving vs median-session saving,
tolerance sensitivity for the unsafe test, OCV slope at the top, and decomposition of where L_cell > L_mm comes from."""
import sys, os
import numpy as np
os.chdir("<repo>")
sys.path.insert(0, "analysis")
import H_replay as H

cars = [int(c) for c in sys.argv[1:]] or [100, 101, 102, 103, 104]
tc_tot = tm_tot = 0.0
tp_tot = {k: 0.0 for k in ["30_10", "50_5", "0_0"]}
uns = {tol: 0 for tol in [1.0, 1.001, 1.01, 1.05]}
nfr = 0
S_list = []
cold_gain_frames = 0; diff_frames = 0
for car in cars:
    for f in H.frames(car):
        if f["dah"].sum() <= 0.5:
            continue
        Lmm, Lcell, a0, ts, ctp = H.limiters(f, maps=H.PMAPS[:1])
        tc, tm = H.t_of(f["dah"], Lcell[0]), H.t_of(f["dah"], Lmm)
        tc_tot += tc; tm_tot += tm; S_list.append(1 - tc / tm)
        nfr += len(Lmm)
        d = np.abs(Lcell[0] - Lmm) > 1e-9
        diff_frames += d.sum()
        # in differing frames, is the min/max-limiting probe cold (<25) or hot (>40)?
        cold_gain_frames += (d & (f["T"].min(1) < 25)).sum()
        for k in tp_tot:
            m, mT = map(int, k.split("_"))
            Lp = np.minimum(H.c_t(f["tmean"] - mT), H.c_t(f["tmean"] + mT)) * H.taper(H.soc(f["vmean"] + m))
            tp_tot[k] += H.t_of(f["dah"], Lp)
            if k == "30_10":
                for tol in uns:
                    uns[tol] += int((Lp > Lcell[0] * tol).sum())
S = np.array(S_list)
print(f"cars {cars}: sessions {len(S)}, frames {nfr}")
print(f"median session S_mm = {np.median(S)*100:.4f}%  mean = {S.mean()*100:.3f}%  Ah/time-weighted total S = {(1-tc_tot/tm_tot)*100:.3f}%")
print(f"frames L_cell != L_mm: {diff_frames/nfr*100:.2f}%  of which coldest probe < 25 C: {cold_gain_frames/max(diff_frames,1)*100:.1f}%")
for k, v in tp_tot.items():
    print(f"pack-mean {k}: total-time S_pack = {(1-tc_tot/v)*100:.1f}%")
for tol, v in uns.items():
    print(f"unsafe frac at (30 mV,10 C) with tol {tol}: {v/nfr*100:.3f}%")
# OCV slope at top: mV per % SOC and what 30 mV means in SOC near the knee and near the top
OV, OS = H.OV, H.OS
for v in [3900, 4000, 4050, 4100, 4150, 4200]:
    print(f"V={v} mV -> SOC {H.soc(v):.1f}%, SOC(V+30) = {H.soc(v+30):.1f}% -> taper {H.taper(H.soc(v)):.3f} vs {H.taper(H.soc(v+30)):.3f}")
print("SOC 60% knee at V =", np.interp(60, OS, OV), "mV")
