import sys, numpy as np, pandas as pd, warnings; warnings.filterwarnings("ignore")
sys.path.insert(0, "."); from stats_lib import *
from scipy.stats import spearmanr
d2 = pd.read_csv("rescan2_qas.csv"); d1 = pd.read_csv("rescan_qas_checked.csv")
if "err" in d2: print("errors", d2.err.dropna().tolist())
df = d1.merge(d2.drop(columns=["label"]), on="veh", suffixes=("", "_2"))
P, N = df[df.label == 1], df[df.label == 0]
def line(f):
    p, n = P[f].dropna().to_numpy(float), N[f].dropna().to_numpy(float)
    a, ci, se = delong_ci(p, n); return f"{f:22s} AUC {a:.3f} ({ci[0]:.3f},{ci[1]:.3f})  n={len(p)}/{len(n)}  med F {np.median(p):.4g} N {np.median(n):.4g}"
print("== reproduce base A in pass 2:", np.nanmax(np.abs(df.E_A - df.E_A_2)), np.nanmax(np.abs(df.L_A - df.L_A_2)))
print("\n== run/gap structure ==")
for f in ["n_runs", "run_med", "run_max", "frac_frames_in_long_runs", "T_range_E", "T_range_L", "dT_at_breaks_med", "n_Tjumps3"]: print(line(f))
print("\n== block-SOC dispersion and SOC-dependence (mechanism check) ==")
for w in ["E", "L"]:
    for f in ["blk_soc_sd", "blk_soc_slope", "blk_T_sd", "blk_T_slope", "rest_soc_sd", "rest_soc_min", "rest_soc_p05", "dsoc_absmax_z", "corr_Acell_soc", "A_var", "A_rng", "corr_zsl_zvar"]: print(line(f"{w}_{f}"))
    print()
print("== Spearman within normals / within faulty: A vs block-SOC dispersion, A vs A_var ==")
for w in ["E", "L"]:
    for g, nm in [(N, "normals"), (P, "faulty")]:
        print(w, nm, "A~blk_soc_sd r=%.2f" % spearmanr(g[f"{w}_A"], g[f"{w}_blk_soc_sd"])[0], "A~rest_soc_min r=%.2f" % spearmanr(g[f"{w}_A"], g[f"{w}_rest_soc_min"])[0], "A~A_var r=%.2f" % spearmanr(g[f"{w}_A"], g[f"{w}_A_var"])[0], "A~dsoc_absmax_z r=%.2f" % spearmanr(g[f"{w}_A"], g[f"{w}_dsoc_absmax_z"])[0])
print("\n== SOC-restricted rest frames (post-hoc sensitivity) ==")
for w in ["E", "L"]:
    for v in ["", "socmid_", "sochi_"]:
        for f in ["A", "B", "A_var"]:
            c = f"{w}_{v}{f}" + ("_2" if v == "" and f != "A_var" else "")
            if c in df: print(line(c))
        ca, cb = f"{w}_{v}A" + ("_2" if v == "" else ""), f"{w}_{v}B" + ("_2" if v == "" else "")
        ok = P[ca].notna() & P[cb].notna(); okn = N[ca].notna() & N[cb].notna()
        d, ci, p, se = delong_diff(P.loc[ok, ca].to_numpy(), N.loc[okn, ca].to_numpy(), P.loc[ok, cb].to_numpy(), N.loc[okn, cb].to_numpy())
        print(f"   {w}_{v}: A-B {d:+.3f} ({ci[0]:+.3f},{ci[1]:+.3f}) p={p:.3f}\n")
print("== Stratified (L_T 3°C x S_jumps02 tertile) for socmid late A ==")
df["LTb"] = (df.L_T // 3).astype(int); df["jt"] = pd.qcut(df.S_jumps02, 3, labels=False); df["stL"] = df.LTb.astype(str) + "_" + df.jt.astype(str)
for f in ["L_socmid_A", "L_A_var", "L_socmid_A_var"]:
    sa, den = strat_auc(df.dropna(subset=[f]), f, "stL"); obs, p, null = strat_perm(df.dropna(subset=[f]), f, "stL", nperm=1000); print(f"{f} strat AUC {sa:.3f} perm p={p:.3f}")
print("\n== cross-vehicle duplicate check (identical n_rows & V_nuniq & T_nuniq & S_nuniq) ==")
key = ["n_rows", "V_nuniq", "T_nuniq", "S_nuniq"]; dup = df[df.duplicated(key, keep=False)]; print(len(dup), dup[["veh", "label"] + key].to_string() if len(dup) else "")
print("\n== ID-adjacency: AUC of L_A/E_A vs ID among normals in sliding 50-ID windows (is there a trend toward the 335 boundary?) ==")
for lo in range(0, 335, 50):
    g = N[(N.veh >= lo) & (N.veh < lo + 50)]; print(f"IDs {lo}-{lo+49}: median E_A {g.E_A.median():.2f} L_A {g.L_A.median():.2f} L_T {g.L_T.median():.0f} S_jumps02 {g.S_jumps02.median():.0f} frac_sent {g.frac_sent.median():.3f}")
g = P; print(f"faulty 335-392: median E_A {g.E_A.median():.2f} L_A {g.L_A.median():.2f} L_T {g.L_T.median():.0f} S_jumps02 {g.S_jumps02.median():.0f} frac_sent {g.frac_sent.median():.3f}")
print("faulty split by ID halves: 335-363 L_A med %.2f, 364-392 L_A med %.2f; has_sent by half: %s" % (P[P.veh < 364].L_A.median(), P[P.veh >= 364].L_A.median(), P.groupby(P.veh >= 364).apply(lambda g: (g.frac_sent > 0).mean()).to_dict()))
df.to_csv("rescan_merged.csv", index=False)
