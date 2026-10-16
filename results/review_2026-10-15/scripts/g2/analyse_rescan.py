import sys, numpy as np, pandas as pd
sys.path.insert(0, "/tmp/claude-1000/-home-kyle-Documents-GitHub-batt-finetune/8fc251be-e160-42c8-b7ad-d2301080f5cc/scratchpad/review/g2")
from stats_lib import *
pd.set_option("display.width", 220); pd.set_option("display.max_rows", 400)
D = "/tmp/claude-1000/-home-kyle-Documents-GitHub-batt-finetune/8fc251be-e160-42c8-b7ad-d2301080f5cc/scratchpad/review/g2"
df = pd.read_csv(f"{D}/rescan_qas.csv")
if "err" in df: print("errors:", df.err.dropna().tolist())
rep = pd.read_csv("<repo>/results/G2/features.csv"); rep = rep[rep.maker == "QAS"]
m = df.merge(rep[["veh", "E_A", "E_B", "L_A", "L_B"]], on="veh", suffixes=("", "_repo"))
print("== reproduction check vs repo features.csv: max |diff| E_A %.2e E_B %.2e L_A %.2e L_B %.2e" % tuple(np.nanmax(np.abs(m[c] - m[c + "_repo"])) for c in ["E_A", "E_B", "L_A", "L_B"]))
P, N = df[df.label == 1], df[df.label == 0]
def line(f):
    p, n = P[f].dropna().to_numpy(float), N[f].dropna().to_numpy(float)
    a, ci, se = delong_ci(p, n); return f"{f:22s} AUC {a:.3f} ({ci[0]:.3f},{ci[1]:.3f})  n={len(p)}/{len(n)}  med F {np.median(p):.4g} N {np.median(n):.4g}"
print("\n== COHORT FINGERPRINTS (should be ~0.5 if cohorts were sampled/processed alike) ==")
fp = ["n_rows", "n_valid", "frac_sent", "frac_vbad", "sent_mean", "sent_std", "T_first10", "T_last10", "T_min", "T_max", "T_nuniq", "S_nuniq", "S_med", "S_min", "S_jumps05", "S_jumps02", "V_nuniq", "V_med", "V_max", "V_min", "V_spread_med", "frac_alltie", "x0_med", "x0_std", "x1_med", "z_std", "z_absmax", "z_frac_big", "I_nuniq", "I_med_valid", "frac_Ipos", "frac_Ineg", "I_absmax", "corr_dV_I", "n_dup_cells", "v3_q3_med", "v3_q3_min", "v3_q3_max"]
for f in fp: print(line(f))
print("vin_1 constant cols by label:\n", df.groupby("label")[[c for c in df.columns if c.endswith("_const")]].mean())
print("vin_1 nondecreasing cols by label:\n", df.groupby("label")[[c for c in df.columns if c.endswith("_nondec")]].mean())
print("\n== WINDOW TIME-COURSE (base definition) ==")
for w in ["Q1", "Q2", "Q3", "Q4", "E", "L", "L90", "T10", "T5", "F1500", "L1500"]:
    for f in ["A", "B", "A_up", "A2", "A_raw", "A_lvl"]:
        if f"{w}_{f}" in df: print(line(f"{w}_{f}"))
    for f in ["T", "S", "restfrac"]:
        if f"{w}_{f}" in df: print(line(f"{w}_{f}"))
    print()
print("== SENSITIVITY VARIANTS (post-hoc) ==")
for w in ["E", "L"]:
    for v in ["", "b5_", "b20_", "r05_", "r3_", "r10_", "all_", "ts_", "mean_", "perm_"]:
        for f in ["A", "B"]:
            c = f"{w}_{v}{f}"
            if c in df: print(line(c))
        pa, na = P[f"{w}_{v}A"].dropna(), N[f"{w}_{v}A"].dropna()
        ok = P[f"{w}_{v}A"].notna() & P[f"{w}_{v}B"].notna(); okn = N[f"{w}_{v}A"].notna() & N[f"{w}_{v}B"].notna()
        d, ci, p, se = delong_diff(P.loc[ok, f"{w}_{v}A"].to_numpy(), N.loc[okn, f"{w}_{v}A"].to_numpy(), P.loc[ok, f"{w}_{v}B"].to_numpy(), N.loc[okn, f"{w}_{v}B"].to_numpy())
        print(f"   {w}_{v}: A-B {d:+.3f} ({ci[0]:+.3f},{ci[1]:+.3f}) p={p:.3f}")
print("\n== other controls ==")
for f in ["E_A_abs", "L_A_abs", "E_B_max", "L_B_max", "E_B_sprslope", "L_B_sprslope", "E_slope_kurt_proxy", "L_slope_kurt_proxy", "E_mad_slope", "L_mad_slope", "E_n_rest", "L_n_rest"]:
    print(line(f))
print("\n== A-flagged cell index: faulty vs normal, early/late; chi-square-ish check ==")
for w in ["E", "L"]:
    vc = pd.crosstab(df[f"{w}_A_cell"], df.label); top = vc.sort_values(1, ascending=False).head(6); print(w, "\n", top.T)
    same = (df.E_A_cell == df.L_A_cell); print(w, "E/L same flagged cell: faulty %.2f normal %.2f" % (same[df.label == 1].mean(), same[df.label == 0].mean()))
df.to_csv(f"{D}/rescan_qas_checked.csv", index=False)
