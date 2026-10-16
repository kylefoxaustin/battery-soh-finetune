import numpy as np, pandas as pd
from scipy.stats import norm

def auc(pos, neg):
    allv = np.concatenate([pos, neg]); r = pd.Series(allv).rank().to_numpy()
    return (r[:len(pos)].sum() - len(pos)*(len(pos)+1)/2)/(len(pos)*len(neg))

def _placements(pos, neg):
    # structural components (DeLong 1988 via Sun & Xu 2014 midranks)
    m, n = len(pos), len(neg)
    allv = np.concatenate([pos, neg]); r = pd.Series(allv).rank().to_numpy()
    rp = pd.Series(pos).rank().to_numpy(); rn = pd.Series(neg).rank().to_numpy()
    V10 = (r[:m] - rp) / n          # placement of each positive
    V01 = 1 - (r[m:] - rn) / m      # placement of each negative
    return V10, V01

def delong(pos_feats, neg_feats):
    """pos_feats/neg_feats: list of arrays (one per feature). Returns aucs, covariance matrix."""
    V10 = []; V01 = []
    for p, q in zip(pos_feats, neg_feats):
        a, b = _placements(p, q); V10.append(a); V01.append(b)
    V10 = np.array(V10); V01 = np.array(V01)
    aucs = V10.mean(1)
    m, n = V10.shape[1], V01.shape[1]
    S10 = np.cov(V10) if len(pos_feats) > 1 else np.array([[np.var(V10[0], ddof=1)]])
    S01 = np.cov(V01) if len(pos_feats) > 1 else np.array([[np.var(V01[0], ddof=1)]])
    return aucs, S10 / m + S01 / n

def delong_ci(pos, neg, alpha=0.05):
    a, S = delong([pos], [neg]); se = np.sqrt(S[0, 0]); zq = norm.ppf(1 - alpha / 2)
    return a[0], (a[0] - zq * se, a[0] + zq * se), se

def delong_diff(posA, negA, posB, negB):
    a, S = delong([posA, posB], [negA, negB]); d = a[0] - a[1]
    var = S[0, 0] + S[1, 1] - 2 * S[0, 1]; se = np.sqrt(var); z = d / se
    return d, (d - 1.96 * se, d + 1.96 * se), 2 * norm.sf(abs(z)), se

def strat_auc(df, feat, strata):
    """Stratified (pooled within-stratum pairs) AUC."""
    num = 0.0; den = 0.0
    for _, g in df.groupby(strata):
        p = g[g.label == 1][feat].to_numpy(); q = g[g.label == 0][feat].to_numpy()
        if len(p) and len(q):
            num += auc(p, q) * len(p) * len(q); den += len(p) * len(q)
    return num / den if den else np.nan, den

def strat_perm(df, feat, strata, nperm=5000, seed=0, featB=None):
    """permutation of labels within strata; returns observed stat, p-value, null quantiles. If featB given, stat = AUC_A - AUC_B (stratified)."""
    rng = np.random.default_rng(seed)
    d = df.copy()
    def stat(dd):
        a = strat_auc(dd, feat, strata)[0]
        return a - strat_auc(dd, featB, strata)[0] if featB else a
    obs = stat(d)
    null = np.empty(nperm)
    groups = [g.index.to_numpy() for _, g in d.groupby(strata)]
    lab = d.label.to_numpy().copy()
    for i in range(nperm):
        l2 = lab.copy()
        for idx in groups:
            pos = d.index.get_indexer(idx); l2[pos] = rng.permutation(lab[pos])
        d["label"] = l2
        null[i] = stat(d)
    d["label"] = lab
    return obs, float(np.mean(null >= obs)), null
