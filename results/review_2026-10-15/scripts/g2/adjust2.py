import sys, numpy as np, pandas as pd, warnings; warnings.filterwarnings("ignore")
sys.path.insert(0, "."); from stats_lib import *
from sklearn.linear_model import LogisticRegression
df = pd.read_csv("rescan_qas_checked.csv"); df["has_sent"] = (df.frac_sent > 0).astype(int)
P, N = df[df.label == 1], df[df.label == 0]
rng = np.random.default_rng(0)
def logit(d, feat, covs, nboot=600, C=1e6):
    cols = [feat] + covs
    def fit(dd):
        X = dd[cols].to_numpy(float); X = (X - X.mean(0)) / (X.std(0) + 1e-12)
        return LogisticRegression(C=C, max_iter=5000).fit(X, dd.label).coef_[0][0]
    pos, neg = d[d.label == 1], d[d.label == 0]
    bs = [fit(pd.concat([pos.sample(len(pos), replace=True, random_state=rng.integers(1 << 31)), neg.sample(len(neg), replace=True, random_state=rng.integers(1 << 31))])) for _ in range(nboot)]
    return fit(d), np.percentile(bs, 2.5), np.percentile(bs, 97.5)
print("== Adjusted logistic (no has_sent; it quasi-separates). season/gap covariates ==")
covs = ["E_T", "L_T", "T_max", "S_jumps02", "S_min", "E_n_rest"]
for f in ["E_A", "E_B", "L_A", "L_B", "L_perm_A", "L_A_abs"]:
    c, lo, hi = logit(df, f, covs); print(f"{f:9s} coef {c:+.2f} ({lo:+.2f},{hi:+.2f})")
print("\n== Same-processing-path subset: 17 sentinel-bearing faulty vs 335 normals, adjusted (prereg-5 covariates) ==")
sub = pd.concat([P[P.has_sent == 1], N])
for f in ["E_A", "L_A"]:
    c, lo, hi = logit(sub, f, ["E_T", "E_S", "n_valid", "E_restfrac", "I_med_valid"]); print(f"{f:9s} coef {c:+.2f} ({lo:+.2f},{hi:+.2f})")
print("\n== Stratified permutation: strata = L_T 3°C-bin x S_jumps02 tertile (late), E_T 3°C x E_n_rest tertile (early); 2000 perms ==")
df["LTb"] = (df.L_T // 3).astype(int); df["jt"] = pd.qcut(df.S_jumps02, 3, labels=False); df["stL"] = df.LTb.astype(str) + "_" + df.jt.astype(str)
df["ETb"] = (df.E_T // 3).astype(int); df["nt"] = pd.qcut(df.E_n_rest, 3, labels=False); df["stE"] = df.ETb.astype(str) + "_" + df.nt.astype(str)
for f, st in [("L_A", "stL"), ("L_B", "stL"), ("L_perm_A", "stL"), ("E_A", "stE"), ("E_B", "stE")]:
    sa, den = strat_auc(df, f, st); obs, p, null = strat_perm(df, f, st, nperm=2000)
    print(f"{f} strat AUC {sa:.3f} (pairs {int(den)}) perm p={p:.3f}")
obs, p, null = strat_perm(df, "L_A", "stL", nperm=2000, featB="L_B"); print(f"L A-B strat {obs:+.3f} perm p={p:.3f}")
obs, p, null = strat_perm(df, "E_A", "stE", nperm=2000, featB="E_B"); print(f"E A-B strat {obs:+.3f} perm p={p:.3f}")
print("\n== Caliper matching: |L_T diff|<=2, |S_jumps02 diff|<=10, same has_sent (only the 17 sentinel-bearing faulty can match) ==")
for f in ["L_A", "L_B", "E_A", "E_B"]:
    num = den = 0; nm = 0
    for _, r in P.iterrows():
        mm = N[(np.abs(N.L_T - r.L_T) <= 2) & (np.abs(N.S_jumps02 - r.S_jumps02) <= 10) & (N.has_sent == r.has_sent)]
        if len(mm): num += (r[f] > mm[f]).sum() + 0.5 * (r[f] == mm[f]).sum(); den += len(mm); nm += 1
    print(f"{f}: matched AUC {num/den:.3f} over {int(den)} pairs from {nm} faulty")
print("\n== Caliper matching ignoring has_sent: |L_T|<=2 and |S_jumps02|<=10 ==")
for f in ["L_A", "L_B", "E_A", "E_B"]:
    num = den = 0; nm = 0
    for _, r in P.iterrows():
        mm = N[(np.abs(N.L_T - r.L_T) <= 2) & (np.abs(N.S_jumps02 - r.S_jumps02) <= 10)]
        if len(mm): num += (r[f] > mm[f]).sum() + 0.5 * (r[f] == mm[f]).sum(); den += len(mm); nm += 1
    print(f"{f}: matched AUC {num/den:.3f} over {int(den)} pairs from {nm} faulty")
