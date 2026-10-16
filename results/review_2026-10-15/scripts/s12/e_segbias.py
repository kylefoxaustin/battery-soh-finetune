"""E: (1) segment-duration bias in the derived label; (2) does the BMS SOC slope in the input snippet encode the
BMS's own capacity estimate (a proxy the LSTM can read)?"""
import glob, json, numpy as np
ROOT="<repo>"
targets=set(); [targets.update(json.load(open(f"{ROOT}/runs/chf_primary_k{k}/split.json"))["targets"]) for k in range(4)]
Y,SEG,KM,CAR,CB,TM,SOCS,IEND=[],[],[],[],[],[],[],[]
for f in sorted(glob.glob(f"{ROOT}/data/changan/labels_full/vin*.npz")):
    d=np.load(f); iend=-d["X"][:,-1,1]
    m=(iend>=48)&(iend<=51)&np.isfinite(d["mileage"])&np.isfinite(d["capacity"])&(d["capacity"]>=95)&(d["capacity"]<=145)
    if not m.any(): continue
    X=d["X"][m]; soc=X[:,:,2]; I=-X[:,:,1]; t=X[:,:,7]
    dsoc=soc[:,-1]-soc[:,0]; dt=t[:,-1]-t[:,0]
    cb=np.where(dsoc>0, I.mean(1)*dt/3600.0/(dsoc/100.0), np.nan)   # BMS-implied capacity from SOC slope during CC charge
    Y.append(d["capacity"][m]); SEG.append(d["seg_s"][m]); KM.append(d["mileage"][m]); CAR.append(d["car"][m]); CB.append(cb); TM.append(X[:,:,5].mean(1)); SOCS.append(d["soc_s"][m]); IEND.append(iend[m])
Y,SEG,KM,CAR,CB,TM,SOCS,IEND=map(np.concatenate,(Y,SEG,KM,CAR,CB,TM,SOCS,IEND))
print(f"primary labels {len(Y)} (dossier 6,638)")
h=SEG/3600; print("seg duration h: p5/25/50/75/95/99 =",np.percentile(h,[5,25,50,75,95,99]).round(2),"; frac >6h",(h>6).mean().round(3),"frac >24h",(h>24).mean().round(3))
# fleet-wide: label vs log seg within unit (unit-demeaned) for target units
tm=np.isin(CAR,list(targets))
def demean(v,c):
    out=v.astype(float).copy()
    for u in np.unique(c): out[c==u]-=out[c==u].mean()
    return out
yd=demean(Y[tm],CAR[tm]); ld=demean(np.log(SEG[tm]),CAR[tm]); kd=demean(KM[tm],CAR[tm])
A=np.c_[ld,kd,np.ones(len(yd))]; b=np.linalg.lstsq(A,yd,rcond=None)[0]
print(f"within-unit OLS: label = {b[0]:+.3f} Ah per e-fold of segment duration (+{b[1]*1e5:+.3f} Ah per 100k km)")
for lo,hi in ((0,2),(2,6),(6,24),(24,72)):
    s=(h[tm]>=lo)&(h[tm]<hi); print(f"  seg {lo}-{hi} h: n={s.sum()}, mean unit-demeaned label {yd[s].mean():+.2f} Ah")
# BMS-implied capacity proxy
ok=np.isfinite(CB)&(CB>60)&(CB<200)
print(f"BMS-SOC-slope capacity proxy: valid {ok.mean():.2%}; median {np.median(CB[ok]):.1f} Ah; corr with label (all) {np.corrcoef(CB[ok],Y[ok])[0,1]:.3f}")
cbd=demean(np.where(ok,CB,np.nan)[tm&ok],CAR[tm&ok]); ydd=demean(Y[tm&ok],CAR[tm&ok])
print(f"  within-unit corr(proxy, label) on target units: {np.corrcoef(cbd,ydd)[0,1]:.3f}")
# proxy's own trend with km and within-unit SD
sds=[np.std(CB[(CAR==u)&ok]) for u in targets if ((CAR==u)&ok).sum()>=10]
print(f"  within-unit SD of the proxy: median {np.median(sds):.2f} Ah (label noise 4.76); proxy by km bin:",[round(float(np.median(CB[ok&(KM>=a)&(KM<a+1e5)])),1) for a in (0,1e5,2e5,3e5)])
# temperature and start-SOC dependence of label (within-unit)
A=np.c_[demean(TM[tm],CAR[tm]),demean(SOCS[tm],CAR[tm]),demean(IEND[tm],CAR[tm]),ld,kd,np.ones(len(yd))]; b=np.linalg.lstsq(A,yd,rcond=None)[0]
print(f"within-unit OLS with T, soc_s, I_end, log seg, km: coefs T {b[0]:+.3f} Ah/°C, soc_s {b[1]:+.3f} Ah/%, I_end {b[2]:+.3f} Ah/A, log seg {b[3]:+.3f}")
