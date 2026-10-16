"""Experiment G.2 (pre-registered in results/G2/G2_preregistration.md, commit 05af194): per-cell vs min/max flagging of
teardown-labelled faulty packs, Beihang (Cao et al. Nat Commun 2025, zenodo 10656500, CC BY 4.0).
Pickles are torch tensors; loaded through a restricted unpickler (tensor rebuild + OrderedDict only), map_location=cpu.
Usage: python analysis/G2_beihang.py   (writes results/G2/features.csv, results/G2/g2.json)
"""
import collections
import io
import json
import os
import pickle

import numpy as np
import pandas as pd
import torch
import torch._utils

ROOT = "data/raw/beihang/x"
OUT = "results/G2"
SEED, NBOOT = 0, 2000
MAKERS = {"QAS": dict(k=110, scale=1.0, vlo=2.0, vhi=4.5), "DTI": dict(k=85, scale=1e-3, vlo=2.0, vhi=4.5)}
NBLK, MIN_REST = 10, 20
CONTROLS = ["C1_temp", "C2_soc", "C3_nvalid", "C4_restfrac", "C5_absI"]


def _lfb(b):
    return torch.load(io.BytesIO(b), weights_only=True, map_location="cpu")


_OK = {("torch._utils", "_rebuild_tensor_v2"): torch._utils._rebuild_tensor_v2,
       ("torch.storage", "_load_from_bytes"): _lfb, ("collections", "OrderedDict"): collections.OrderedDict}


class _U(pickle.Unpickler):
    def find_class(self, m, n):
        if (m, n) in _OK:
            return _OK[(m, n)]
        raise pickle.UnpicklingError(f"blocked {m}.{n}")


def load(p):
    with open(p, "rb") as f:
        return _U(f).load().cpu().numpy()


def robust_z(x):
    med = np.median(x)
    mad = 1.4826 * np.median(np.abs(x - med))
    return (x - med) / mad if mad > 0 else np.zeros_like(x)


def slope(y):
    return np.polyfit(np.arange(len(y)), y, 1)[0]


def window_features(V, I, T, S):
    """V: frames x cells (V); I, T, S per frame. Returns dict of features, or None if ineligible."""
    rest = np.abs(I) < 1.0
    n_rest = rest.sum()
    if n_rest < NBLK * MIN_REST:
        return None
    Vr = V[rest]
    mean = Vr.mean(1, keepdims=True)
    d = (Vr - mean) * 1e3                                   # mV
    m = (Vr.min(1) - mean[:, 0]) * 1e3
    s = (Vr.max(1) - Vr.min(1)) * 1e3
    blocks = np.array_split(np.arange(n_rest), NBLK)        # equal rest-frame counts, row order
    bd = np.array([np.median(d[b], 0) for b in blocks])     # NBLK x cells
    bm = np.array([np.median(m[b]) for b in blocks])
    zs = robust_z(np.array([slope(bd[:, k]) for k in range(bd.shape[1])]))
    zl = robust_z(np.median(d, 0))
    a_cell = int(np.argmin(zs))
    mincell = np.bincount(Vr.argmin(1), minlength=V.shape[1])
    drive = ~rest
    return {"A": float(-zs.min()), "B": float(-slope(bm)), "A_lvl": float(-zl.min()), "B_lvl": float(-np.median(m)),
            "B_spr": float(np.median(s)), "A_cell": a_cell, "A_cell_minfrac": float(mincell[a_cell] / n_rest),
            "A_cell_is_modal_min": bool(a_cell == int(mincell.argmax())),
            "C1_temp": float(np.median(T)), "C2_soc": float(np.median(S)), "C3_nvalid": float(len(I)),
            "C4_restfrac": float(rest.mean()), "C5_absI": float(np.median(np.abs(I[drive]))) if drive.any() else 0.0,
            "n_rest": int(n_rest)}


def vehicle(maker, n):
    cfg = MAKERS[maker]
    k = cfg["k"]
    b = load(f"{ROOT}/{maker}/{n}/vin_2.pkl")
    V = b[:, 2:2 + k] * cfg["scale"]
    q = b[:, 2 + 2 * k:]
    T, S, I = q[:, 0], q[:, 1], q[:, -1]
    valid = (np.abs(I) < 900) & np.all((V >= cfg["vlo"]) & (V <= cfg["vhi"]), 1)
    V, I, T, S = V[valid], I[valid], T[valid], S[valid]
    half = len(I) // 2
    early = window_features(V[:half], I[:half], T[:half], S[:half])
    late = window_features(V[half:], I[half:], T[half:], S[half:])
    mil = load(f"{ROOT}/{maker}/{n}/vin_1.pkl").reshape(len(b), -1)[:, 2]
    row = {"maker": maker, "veh": n, "n_rows": len(b), "n_valid": int(valid.sum()),
           "mileage_nondecreasing": bool(np.all(np.diff(mil) >= -1e-12))}
    for tag, f in (("E", early), ("L", late)):
        row[f"eligible_{tag}"] = f is not None
        if f:
            row.update({f"{tag}_{key}": v for key, v in f.items()})
    return row


def auc(pos, neg):
    allv = np.concatenate([pos, neg])
    r = pd.Series(allv).rank().to_numpy()
    return (r[: len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg))


def boot_aucs(df, feats, rng):
    pos = df[df.label == 1]
    neg = df[df.label == 0]
    out = {f: [] for f in feats}
    for _ in range(NBOOT):
        p = pos.sample(len(pos), replace=True, random_state=rng.integers(1 << 31))
        q = neg.sample(len(neg), replace=True, random_state=rng.integers(1 << 31))
        for f in feats:
            out[f].append(auc(p[f].to_numpy(), q[f].to_numpy()))
    return {f: np.array(v) for f, v in out.items()}


def ci(x):
    return [float(np.percentile(x, 2.5)), float(np.percentile(x, 97.5))]


def logit_coef(df, feat, rng):
    """standardised logistic regression label ~ feat + controls; bootstrap CI of feat coefficient"""
    from sklearn.linear_model import LogisticRegression
    cols = [feat] + [f"E_{c}" for c in CONTROLS]

    def fit(d):
        X = d[cols].to_numpy(float)
        X = (X - X.mean(0)) / X.std(0)
        return LogisticRegression(C=1e6, max_iter=5000).fit(X, d.label).coef_[0][0]

    pos, neg = df[df.label == 1], df[df.label == 0]
    bs = [fit(pd.concat([pos.sample(len(pos), replace=True, random_state=rng.integers(1 << 31)),
                         neg.sample(len(neg), replace=True, random_state=rng.integers(1 << 31))]))
          for _ in range(NBOOT)]
    return {"coef": float(fit(df)), "ci": ci(bs)}


def main():
    os.makedirs(OUT, exist_ok=True)
    rows = []
    for maker in MAKERS:
        lab = pd.read_excel(f"{ROOT}/{maker}/Labels.xls")
        for n, y in zip(lab.Num, lab.Label):
            r = vehicle(maker, int(n))
            r["label"] = int(y)
            rows.append(r)
            print(maker, n, y, r["eligible_E"], flush=True)
    df = pd.DataFrame(rows)
    df.to_csv(f"{OUT}/features.csv", index=False)

    res = {"n_vehicles": {m: int((df.maker == m).sum()) for m in MAKERS},
           "mileage_nondecreasing_frac": float(df.mileage_nondecreasing.mean())}
    q = df[(df.maker == "QAS") & df.eligible_E]
    npos, nneg = int((q.label == 1).sum()), int((q.label == 0).sum())
    res["QAS_eligible"] = {"pos": npos, "neg": nneg}
    rng = np.random.default_rng(SEED)
    if npos < 20 or nneg < 100:
        res["verdict"] = "UNDERPOWERED"
    feats = ["E_A", "E_B", "E_A_lvl", "E_B_lvl", "E_B_spr"] + [f"E_{c}" for c in CONTROLS]
    B = boot_aucs(q, feats, rng)
    point = {f: float(auc(q[q.label == 1][f].to_numpy(), q[q.label == 0][f].to_numpy())) for f in feats}
    res["early"] = {f: {"auc": point[f], "ci": ci(B[f])} for f in feats}
    diff = B["E_A"] - B["E_B"]
    res["early"]["A_minus_B"] = {"diff": point["E_A"] - point["E_B"], "ci": ci(diff)}
    lo_a = res["early"]["E_A"]["ci"][0]
    dlo, dhi = res["early"]["A_minus_B"]["ci"]
    if "verdict" not in res:
        if point["E_A"] >= 0.70 and lo_a > 0.5 and dlo > 0:
            res["verdict"] = "Per-cell early flagging SUPPORTED over min/max"
        elif lo_a > 0.5 and dlo > 0:
            # gap in the pre-registered table (deviation 1): A beats B resolvably but AUC_A < 0.70
            res["verdict"] = ("Early flagging exists (weak, AUC_A < 0.70); per-cell resolvably better than min/max "
                              "(not covered by the pre-registered table; below the SUPPORTED bar)")
        elif lo_a > 0.5:
            res["verdict"] = "Early flagging exists but per-cell adds nothing resolvable over min/max"
        else:
            res["verdict"] = "NOT SUPPORTED"
        if dhi < 0:
            res["verdict_note"] = "min/max better (report-only)"
    flagged = [c for c in CONTROLS if not (0.35 <= res["early"][f"E_{c}"]["ci"][0] and
                                           res["early"][f"E_{c}"]["ci"][1] <= 0.65)]
    res["confound_flag"] = bool(flagged)
    res["confound_controls_outside"] = flagged
    res["adjusted"] = {"A": logit_coef(q, "E_A", rng), "B": logit_coef(q, "E_B", rng)}

    ql = df[(df.maker == "QAS") & df.eligible_L]
    BL = boot_aucs(ql, ["L_A", "L_B"], rng)
    pl = {f: float(auc(ql[ql.label == 1][f].to_numpy(), ql[ql.label == 0][f].to_numpy())) for f in ["L_A", "L_B"]}
    res["late"] = {f: {"auc": pl[f], "ci": ci(BL[f])} for f in pl}
    res["late"]["A_minus_B"] = {"diff": pl["L_A"] - pl["L_B"], "ci": ci(BL["L_A"] - BL["L_B"]),
                                "n_pos": int((ql.label == 1).sum()), "n_neg": int((ql.label == 0).sum())}
    fp = q[q.label == 1]
    res["concordance_faulty"] = {"A_cell_is_modal_min_frac": float(fp.E_A_cell_is_modal_min.mean()),
                                 "A_cell_minfrac_median": float(fp.E_A_cell_minfrac.median())}
    d = df[(df.maker == "DTI") & df.eligible_E]
    res["DTI"] = {"eligible": int(len(d)), "eligible_pos": int((d.label == 1).sum()),
                  "pos_rank_pct": {f: [float((d[f] < v).mean()) for v in d[d.label == 1][f]] for f in ["E_A", "E_B"]}}
    json.dump(res, open(f"{OUT}/g2.json", "w"), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
