import sys, numpy as np, pandas as pd, warnings; warnings.filterwarnings("ignore")
sys.path.insert(0, "."); from stats_lib import *
from scipy.stats import spearmanr, mannwhitneyu
from sklearn.linear_model import LogisticRegression
df = pd.read_csv("rescan_qas_checked.csv")
df["has_sent"] = (df.frac_sent > 0).astype(int)
P, N = df[df.label == 1], df[df.label == 0]
print("faulty with any sentinel frames: %d/58 ; normals: %d/335" % (P.has_sent.sum(), N.has_sent.sum()))
print("\n== Within-normals Spearman of A with cohort-distinguishing covariates (does A respond to the confounders?) ==")
for f in ["E_A", "L_A", "E_B", "L_B", "L_A_up", "L_A_abs"]:
    out = []
    for c in ["E_T", "L_T", "T_last10", "T_max", "S_jumps02", "S_min", "V_min", "E_n_rest", "L_n_rest", "frac_sent", "frac_Ipos", "E_restfrac", "L_restfrac", "n_valid"]:
        r, p = spearmanr(N[f], N[c]); out.append(f"{c} {r:+.2f}{'*' if p < 0.01 else ''}")
    print(f, ":", "  ".join(out))
print("\n== A: faulty subgroups vs normals (processing-path split) ==")
for f in ["E_A", "L_A", "E_B", "L_B"]:
    for nm, sub in [("faulty WITH sentinels", P[P.has_sent == 1]), ("faulty WITHOUT sentinels", P[P.has_sent == 0])]:
        a, ci, se = delong_ci(sub[f].to_numpy(), N[f].to_numpy()); print(f"{f} {nm:26s} n={len(sub)} AUC {a:.3f} ({ci[0]:.3f},{ci[1]:.3f})")
    u = mannwhitneyu(P[P.has_sent == 1][f], P[P.has_sent == 0][f]); print(f"   {f} with vs without (within faulty) MWU p={u.pvalue:.3f}")
print("\n== Adjusted logistic regression (standardised), 2000 vehicle bootstraps; coefficient of feature ==")
rng = np.random.default_rng(0)
def logit(d, feat, covs, nboot=2000):
    cols = [feat] + covs
    def fit(dd):
        X = dd[cols].to_numpy(float); X = (X - X.mean(0)) / (X.std(0) + 1e-12)
        return LogisticRegression(C=1e6, max_iter=5000).fit(X, dd.label).coef_[0][0]
    pos, neg = d[d.label == 1], d[d.label == 0]
    bs = [fit(pd.concat([pos.sample(len(pos), replace=True, random_state=rng.integers(1 << 31)), neg.sample(len(neg), replace=True, random_state=rng.integers(1 << 31))])) for _ in range(nboot)]
    return fit(d), np.percentile(bs, 2.5), np.percentile(bs, 97.5)
sets = {"prereg-5 (E_T,E_S,n_valid,E_restfrac,|I|)": ["E_T", "E_S", "n_valid", "E_restfrac", "I_med_valid"],
        "season/gap set (E_T, L_T, T_max, S_jumps02, S_min, has_sent, E_n_rest)": ["E_T", "L_T", "T_max", "S_jumps02", "S_min", "has_sent", "E_n_rest"],
        "gap-only (S_jumps02, S_min, has_sent)": ["S_jumps02", "S_min", "has_sent"],
        "temp-only (E_T, L_T, T_max)": ["E_T", "L_T", "T_max"]}
for f in ["E_A", "E_B", "L_A", "L_B", "L_A_perm", "L_A_abs"]:
    for nm, covs in sets.items():
        c, lo, hi = logit(df, f, covs, nboot=600); print(f"{f:9s} | {nm:70s} coef {c:+.2f} ({lo:+.2f},{hi:+.2f})")
print("\n== Stratified permutation: strata = L_T 3°C-bin x S_jumps02 tertile (late), E_T 3°C x E_n_rest tertile (early) ==")
df["LTb"] = (df.L_T // 3).astype(int); df["jt"] = pd.qcut(df.S_jumps02, 3, labels=False); df["stL"] = df.LTb.astype(str) + "_" + df.jt.astype(str)
df["ETb"] = (df.E_T // 3).astype(int); df["nt"] = pd.qcut(df.E_n_rest, 3, labels=False); df["stE"] = df.ETb.astype(str) + "_" + df.nt.astype(str)
for f, st in [("L_A", "stL"), ("L_B", "stL"), ("L_A_perm", "stL"), ("E_A", "stE"), ("E_B", "stE")]:
    sa, den = strat_auc(df, f, st); obs, p, null = strat_perm(df, f, st, nperm=2000)
    print(f"{f} strat AUC {sa:.3f} (pairs {int(den)}) perm p={p:.3f}")
obs, p, null = strat_perm(df, "L_A", "stL", nperm=2000, featB="L_B"); print(f"L A-B strat {obs:+.3f} perm p={p:.3f}")
obs, p, null = strat_perm(df, "E_A", "stE", nperm=2000, featB="E_B"); print(f"E A-B strat {obs:+.3f} perm p={p:.3f}")
print("\n== Caliper matching: each faulty matched to normals with |L_T diff|<=2, |S_jumps02 diff|<=10, same has_sent ==")
for f in ["L_A", "L_B", "E_A", "E_B"]:
    num = den = 0
    for _, r in P.iterrows():
        mm = N[(np.abs(N.L_T - r.L_T) <= 2) & (np.abs(N.S_jumps02 - r.S_jumps02) <= 10) & (N.has_sent == r.has_sent)]
        if len(mm): num += (r[f] > mm[f]).sum() + 0.5 * (r[f] == mm[f]).sum(); den += len(mm)
    print(f"{f}: matched AUC {num/den:.3f} over {int(den)} pairs")
