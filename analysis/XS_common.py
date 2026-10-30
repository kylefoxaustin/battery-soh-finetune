"""Shared definitions for X2-S (Schaeffer et al. 28 LFP systems, zenodo 13715694, CC BY-NC 4.0). Used identically by
the freeze/profile step (XS_freeze.py) and the replay (XS_replay.py). See results/X/X2S_preregistration.md."""
import numpy as np
import pandas as pd

SRC = "data/raw/schaeffer/field_data"
OUT = "results/X/XS"
Q_REF = 160.0                       # SOURCED (dataset README: "approx. 160 Ah")
I_MAX = 500.0                       # valid-frame current bound (A)
DT_MAX = 10.0                       # consecutive rows: 0 < dt <= 10 s
SESS_GAP = 60.0                     # a charge session breaks on a gap > 60 s ...
SESS_MISS = 2                       # ... or after >= 2 non-charge / invalid rows
CH_A = 1.0                          # charge-direction threshold (A)
BAL_A = 0.01                        # a row is "balancing" if any |I_CNV_Cell_k| > 10 mA
CELLS = [f"U_Cell_{k}" for k in range(1, 9)]
BAL = [f"I_CNV_Cell_{k}" for k in range(1, 9)]
TEMPS = [f"Temperature_{k}" for k in range(1, 5)]


def load(sysid):
    d = pd.read_csv(f"{SRC}/data_sys_{sysid}.csv", usecols=["Timestamp", "I_Battery"] + TEMPS + CELLS + BAL,
                    parse_dates=["Timestamp"], engine="c")
    t = d["Timestamp"].astype("int64").to_numpy() / 1e9
    o = np.argsort(t, kind="stable")
    t = t[o]
    Ic = d["I_Battery"].to_numpy(float)[o]           # file convention is charge-positive (checked in XS_freeze)
    V = d[CELLS].to_numpy(float)[o] * 1e3            # mV
    T = d[TEMPS].to_numpy(float)[o].min(1)           # pack-min temperature: one value for every limiter
    bal = (np.abs(np.nan_to_num(d[BAL].to_numpy(float)[o])) > BAL_A).any(1)
    valid = np.isfinite(V).all(1) & (V > 2000).all(1) & (V < 4500).all(1) & np.isfinite(Ic) & (np.abs(Ic) < I_MAX) \
        & np.isfinite(T)
    return t, Ic, V, T, bal, valid


def sessions(t, Ic, valid):
    """Charge sessions: valid rows with Ic > 1 A; break on a time gap > 60 s or >= 2 non-charge/invalid rows;
    >= 0.5 Ah. Returns (row indices, dAh per row) with dt clipped to <= 10 s."""
    ch = valid & (Ic > CH_A)
    idx = np.flatnonzero(ch)
    out = []
    if not len(idx):
        return out
    brk = np.flatnonzero((np.diff(idx) > SESS_MISS) | (np.diff(t[idx]) > SESS_GAP)) + 1
    dt = np.clip(np.diff(t, prepend=t[0]), 0, DT_MAX)
    for s in np.split(idx, brk):
        dah = Ic[s] * dt[s] / 3600.0
        dah[0] = Ic[s[0]] * 5.0 / 3600.0                # first row: nominal 5 s
        if dah.sum() >= 0.5:
            out.append((s, dah))
    return out


def steps(t, Ic, V, T, bal, valid, c, allow_bal=False, with_sign=False):
    """Current steps between consecutive valid rows (0 < dt <= 10 s), |dI| >= c*Q_ref, |dT| <= 1 C, neither row
    balancing (unless allow_bal). Returns step time (second row), per-cell r (mOhm), pack-mean r."""
    dt = np.diff(t)
    dI = np.diff(Ic)
    m = (dt > 0) & (dt <= DT_MAX) & valid[1:] & valid[:-1] & (np.abs(dI) >= c * Q_REF) & (np.abs(np.diff(T)) <= 1.0)
    if not allow_bal:
        m &= ~bal[1:] & ~bal[:-1]
    k = np.flatnonzero(m)
    r = (V[k + 1] - V[k]) / dI[k][:, None]
    rp = (V[k + 1].mean(1) - V[k].mean(1)) / dI[k]
    if with_sign:                                   # X2-S DEV-1: step direction (+1 up, -1 down)
        return t[k + 1], r, rp, np.sign(dI[k])
    return t[k + 1], r, rp
