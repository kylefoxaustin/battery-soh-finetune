"""X5 dataset audit and profile (brief §2-§3). No estimator (P0-P4), reserve or gain is computed here.

Per candidate: units, cells per unit, capacity checks, label noise, within-unit spread, weakest-cell persistence and
target counts (power), plus the frozen unit split (seed 0) for the datasets that pass.

Data (all downloaded, untrusted; run with python -E):
  ISU-ILCC      data/raw/isu_ilcc/capacity_fade/Release */G<g>C<c>.csv   (RPT C/5 discharge capacity; CC BY 4.0)
  BatICM c2p    data/raw/baticm_c2p/<pair>/{pack,cells}/*.pkl          (Zenodo 20132842; CC BY 4.0)
                pandas pickles: loaded only through an allowlisted Unpickler (numpy/pandas reconstruction only)
  UMich 3P      data/raw/umich_ppm/summary/Module_*_and_its_Cells.csv  (Mendeley ssrgfmb8vw v2; CC BY 4.0)
Every number DERIVED. Usage: nice python3 -E analysis/X5_profile.py
"""
import glob
import json
import os
import pickle
import re

import numpy as np
import pandas as pd

OUT = "results/X/X5"
RAW = "data/raw"
WARM = 0.30                       # brief §4.2: warm-up = first 30 % of checks per unit
WS = (3, 4, 6)                    # W and its sensitivity values; a target needs >= W earlier checks
GATE_NOISE = 0.01                 # brief §3.1
GATE_TARGETS = 40                 # brief §3.5 (evaluation half)
ISU_MATCH = 0.5                   # a cell's RPT matches the group grid if within 0.5 time units


# ---------------------------------------------------------------- label noise (shared definition)
def noise(t, y):
    """Robust single-measurement noise of a slowly varying series, as a fraction of its median.
    e_k = y_k - (a*y_{k-1} + b*y_{k+1}) with linear-interpolation weights; for white noise sigma,
    var(e) = sigma^2 (1 + a^2 + b^2). sigma = 1.4826 MAD(e) / sqrt(1 + a^2 + b^2) (median of that factor).
    Curvature and genuine short-term recovery also enter e, so this is an UPPER bound on measurement noise."""
    t, y = np.asarray(t, float), np.asarray(y, float)
    if len(y) < 5:
        return None
    a = (t[2:] - t[1:-1]) / (t[2:] - t[:-2])
    b = 1 - a
    e = y[1:-1] - (a * y[:-2] + b * y[2:])
    f = np.sqrt(1 + a ** 2 + b ** 2)
    s = 1.4826 * np.median(np.abs(e - np.median(e))) / np.median(f)
    return float(s / np.median(y))


def lag1(y):
    """Median |y_k - y_{k-1}| / y_{k-1} (X4's '5.9 % between consecutive labels' statistic)."""
    y = np.asarray(y, float)
    return float(np.median(np.abs(np.diff(y)) / y[:-1])) if len(y) > 1 else None


def targets(n):
    """Scored targets in a unit with n checks: k >= ceil(0.3 n) and k >= W (0-based), per W."""
    w0 = int(np.ceil(WARM * n))
    return {f"W{w}": max(0, n - max(w0, w)) for w in WS}


def split(ids):
    """Brief §4.3: 50/50 at random, seed 0. First half fits (calibration), second half is scored (evaluation)."""
    ids = sorted(ids)
    p = np.random.default_rng(0).permutation(len(ids))
    h = len(ids) // 2
    return sorted(ids[i] for i in p[:h]), sorted(ids[i] for i in p[h:])


def q(x, p):
    x = [v for v in x if v is not None]
    return float(np.percentile(x, p)) if x else None


# ---------------------------------------------------------------- ISU-ILCC (Candidate C)
def isu():
    files = sorted(glob.glob(f"{RAW}/isu_ilcc/capacity_fade/Release */G*C*.csv"))
    cells = {}
    for f in files:
        g, c = map(int, re.match(r"G(\d+)C(\d+)\.csv", os.path.basename(f)).groups())
        d = pd.read_csv(f)
        d = d[np.isfinite(d["Time"]) & np.isfinite(d["Capacity"]) & (d["Capacity"] > 0)]
        cells[(g, c)] = (d["Time"].to_numpy(float), d["Capacity"].to_numpy(float))
    groups = sorted({g for g, _ in cells})
    cell_noise = {f"G{g}C{c}": noise(*v) for (g, c), v in cells.items()}
    cell_lag1 = {f"G{g}C{c}": lag1(v[1]) for (g, c), v in cells.items()}
    units = {}
    for g in groups:
        mem = sorted(c for gg, c in cells if gg == g)
        if len(mem) < 3:
            units[g] = {"cells": len(mem), "excluded": "fewer than 3 cells"}
            continue
        ref = max(mem, key=lambda c: len(cells[(g, c)][0]))
        grid = cells[(g, ref)][0]
        Q = np.full((len(grid), len(mem)), np.nan)
        for j, c in enumerate(mem):
            t, y = cells[(g, c)]
            for i, tg in enumerate(grid):
                k = np.argmin(np.abs(t - tg))
                if abs(t[k] - tg) <= ISU_MATCH:
                    Q[i, j] = y[k]
        full = np.isfinite(Q).all(1)
        # a unit's life ends at the last check where every cell is present (first cell to stop ends the "pack")
        last = np.flatnonzero(~full)
        n = int(last[0]) if len(last) else len(grid)
        Qc = Q[:n]
        u = {"cells": len(mem), "checks_common": n, "checks_dropped_after_first_gap": int(full[n:].sum()),
             "time_span": float(grid[n - 1] - grid[0]) if n else 0.0}
        if n >= 2:
            sp = (Qc.max(1) - Qc.min(1)) / Qc.mean(1)
            w = Qc.argmin(1)
            u.update({"spread_first": float(sp[0]), "spread_last": float(sp[-1]),
                      "U_first": float(Qc[0].min()), "U_last": float(Qc[-1].min()),
                      "fade_U": float(1 - Qc[-1].min() / Qc[0].min()),
                      "weakest_persist": float(np.mean(w[1:] == w[:-1])),
                      "weakest_switches": int(np.sum(w[1:] != w[:-1])),
                      "noise_U": noise(grid[:n], Qc.min(1))})
        u["targets"] = targets(n)
        units[g] = u
    ok = [g for g, u in units.items() if "excluded" not in u and u["checks_common"] >= 6]
    cal, ev = split(ok)
    nz = list(cell_noise.values())
    out = {
        "source": "ISU-ILCC battery aging dataset, figshare 10.25380/iastate.22582234 (CC BY 4.0); Li-polymer "
                  "NMC/graphite 502030, 250 mAh rated; RPT C/5 discharge capacity, weekly, 30 C chamber",
        "cells": len(cells), "groups": len(groups), "units_usable": len(ok),
        "label_noise_cell": {"median": q(nz, 50), "p90": q(nz, 90), "max": q(nz, 100),
                             "frac_cells_le_1pct": float(np.mean([v <= GATE_NOISE for v in nz if v is not None]))},
        "lag1_cell_median": q(list(cell_lag1.values()), 50),
        "spread_first": {"median": q([units[g]["spread_first"] for g in ok], 50),
                         "p10": q([units[g]["spread_first"] for g in ok], 10),
                         "p90": q([units[g]["spread_first"] for g in ok], 90)},
        "spread_last": {"median": q([units[g]["spread_last"] for g in ok], 50),
                        "p10": q([units[g]["spread_last"] for g in ok], 10),
                        "p90": q([units[g]["spread_last"] for g in ok], 90)},
        "weakest_persist": {"median": q([units[g]["weakest_persist"] for g in ok], 50),
                            "pooled": float(sum(units[g]["weakest_persist"] * (units[g]["checks_common"] - 1)
                                                for g in ok) / sum(units[g]["checks_common"] - 1 for g in ok))},
        "fade_U": {"median": q([units[g]["fade_U"] for g in ok], 50), "min": q([units[g]["fade_U"] for g in ok], 0),
                   "max": q([units[g]["fade_U"] for g in ok], 100)},
        "checks_common": {"median": q([units[g]["checks_common"] for g in ok], 50),
                          "min": q([units[g]["checks_common"] for g in ok], 0),
                          "max": q([units[g]["checks_common"] for g in ok], 100)},
        "split": {"rule": "groups with >= 3 cells and >= 6 common checks; seed-0 permutation, 50/50",
                  "calibration": cal, "evaluation": ev},
        "targets_eval": {f"W{w}": sum(units[g]["targets"][f"W{w}"] for g in ev) for w in WS},
        "targets_cal": {f"W{w}": sum(units[g]["targets"][f"W{w}"] for g in cal) for w in WS},
        "units": {str(g): u for g, u in units.items()},
        "cell_noise": cell_noise,
    }
    return out


# ---------------------------------------------------------------- BatICM cell-to-pack (Candidate A, lab packs)
ALLOW = {("builtins", "slice"), ("functools", "partial"), ("numpy", "ndarray"), ("numpy", "dtype"),
         ("numpy.core.multiarray", "_reconstruct"), ("pandas.core.frame", "DataFrame"),
         ("pandas.core.indexes.base", "_new_Index"), ("pandas.core.indexes.base", "Index"),
         ("pandas.core.indexes.range", "RangeIndex"), ("pandas.core.indexes.numeric", "Int64Index"),
         ("pandas.core.internals.blocks", "new_block"), ("pandas.core.internals.managers", "BlockManager")}


class SafeUnpickler(pickle.Unpickler):
    """Only the numpy/pandas reconstruction globals that a static scan of every BatICM pickle found; anything else
    raises. Translates pandas 1.3 pickles (Int64Index, slice/array block placements) for pandas 2.x."""

    def find_class(self, mod, name):
        if (mod, name) not in ALLOW:
            raise pickle.UnpicklingError(f"blocked global {mod}.{name}")
        if mod == "pandas.core.indexes.numeric":
            return pd.Index
        if (mod, name) == ("pandas.core.internals.blocks", "new_block"):
            from pandas._libs.internals import BlockPlacement
            from pandas.core.internals import blocks

            def nb(values, placement, ndim, **kw):
                if not isinstance(placement, BlockPlacement):
                    placement = BlockPlacement(placement)
                return blocks.new_block(values, placement=placement, ndim=ndim, **kw)
            return nb
        if mod == "numpy.core.multiarray" and hasattr(np, "_core"):
            mod = "numpy._core.multiarray"
        return super().find_class(mod, name)


def load_pkl(p):
    with open(p, "rb") as f:
        return SafeUnpickler(f).load()


BAT_PAIRS = {"ESSL1": "LFP 102 Ah", "ESSL2": "LFP 105 Ah", "ESSH1": "LFP 302 Ah", "PBSL1": "NMC 4 Ah"}


def bat_pack(path, pair):
    L = load_pkl(path)
    rows = []
    for x in L:
        t, m = x["timeseries_data"], x["constant_metadata"].iloc[0]
        I = t["current(A)"].to_numpy(float)
        tt = t["time(s)"].to_numpy(float)
        dt = np.diff(tt, prepend=tt[0])
        vc = [c for c in t.columns if re.fullmatch(r"V\d+", c)]
        V = t[vc].to_numpy(float)
        ch = I > 0
        r = {"cycle": float(m["cycle"]), "rated": float(m["rate_capacity (Ah)"]), "SOH": float(m["SOH"]),
             "Q_ch": float((I.clip(0) * dt).sum() / 3600), "Q_dis": float((-I.clip(None, 0) * dt).sum() / 3600),
             "I_ch_med": float(np.median(I[ch])) if ch.any() else 0.0, "n_cells": len(vc)}
        if ch.any():
            k = np.flatnonzero(ch)[-1]               # last charging row: end of charge
            r.update({"eoc_vmax": float(V[k].max()), "eoc_vmin": float(V[k].min()), "eoc_vmean": float(V[k].mean()),
                      "eoc_argmax": int(V[k].argmax()) + 1, "eoc_vpack": float(t["Vpack"].iloc[k])})
        rows.append(r)
    d = pd.DataFrame(rows).sort_values("cycle").reset_index(drop=True)
    lab = d["SOH"] * d["rated"]
    # same-rate subset for the noise estimate: charge current within 10 % of the modal rate
    mode = d["I_ch_med"].round(0).mode().iloc[0]
    same = (np.abs(d["I_ch_med"] - mode) <= 0.1 * mode).to_numpy()
    agree = float(np.median(np.abs(lab - d["Q_ch"]) / lab))
    a = d["eoc_argmax"].to_numpy()
    out = {"pair": pair, "chem": BAT_PAIRS[pair], "cells_in_series": int(d["n_cells"].iloc[0]),
           "records": len(d), "cycle_first": float(d["cycle"].iloc[0]), "cycle_last": float(d["cycle"].iloc[-1]),
           "SOH_first": float(d["SOH"].iloc[0]), "SOH_last": float(d["SOH"].iloc[-1]),
           "records_with_discharge": int((d["Q_dis"] > 0.5 * lab).sum()),
           "label_vs_Qch_median_reldiff": agree, "modal_charge_A": float(mode),
           "modal_charge_C": float(mode / d["rated"].iloc[0]), "records_same_rate": int(same.sum()),
           "label_noise": noise(d["cycle"][same], lab[same]), "lag1": lag1(lab[same]),
           "eoc_spread_mV": {"first": float(1e3 * (d["eoc_vmax"] - d["eoc_vmin"]).iloc[0]),
                             "median": float(1e3 * (d["eoc_vmax"] - d["eoc_vmin"]).median()),
                             "last": float(1e3 * (d["eoc_vmax"] - d["eoc_vmin"]).iloc[-1])},
           "eoc_vmax_median": float(d["eoc_vmax"].median()), "eoc_vmean_median": float(d["eoc_vmean"].median()),
           "eoc_vmax_p05_p95": [float(d["eoc_vmax"].quantile(.05)), float(d["eoc_vmax"].quantile(.95))],
           "eoc_vpack_p05_p95": [float(d["eoc_vpack"].quantile(.05)), float(d["eoc_vpack"].quantile(.95))],
           "eoc_top_cell_persist": float(np.mean(a[1:] == a[:-1])),
           "eoc_top_cell_mode_share": float(pd.Series(a).value_counts(normalize=True).iloc[0]),
           "targets": targets(len(d))}
    return out


def bat_cell(path):
    L = load_pkl(path)
    cyc, lab = [], []
    for x in L:
        m = x["constant_metadata"].iloc[0]
        cyc.append(float(m["cycle"]))
        lab.append(float(m["SOH"]) * float(m["rate_capacity (Ah)"]))
    o = np.argsort(cyc)
    cyc, lab = np.array(cyc)[o], np.array(lab)[o]
    return {"records": len(cyc), "label_noise": noise(cyc, lab), "lag1": lag1(lab),
            "SOH_first": float(lab[0] / L[0]["constant_metadata"].iloc[0]["rate_capacity (Ah)"]),
            "SOH_last": float(lab[-1] / L[0]["constant_metadata"].iloc[0]["rate_capacity (Ah)"])}


def baticm():
    packs, cells = {}, {}
    for pair in BAT_PAIRS:
        for p in sorted(glob.glob(f"{RAW}/baticm_c2p/{pair}/pack/Pack#*.pkl")):
            packs[os.path.basename(p)[:-4]] = bat_pack(p, pair)
        for p in sorted(glob.glob(f"{RAW}/baticm_c2p/{pair}/cells/Cell#*.pkl")):
            cells[os.path.basename(p)[:-4]] = dict(bat_cell(p), pair=pair)
    cal, ev = split(list(packs))
    nz = [c["label_noise"] for c in cells.values()]
    return {"source": "BatICM cell-to-pack degradation, Zenodo 10.5281/zenodo.20132842 (CC BY 4.0); lab packs and "
                      "same-batch single lab cells. Field packs (16 x 416s, Pack_field#*) not downloaded: field-"
                      "derived labels are excluded by brief §7",
            "packs": packs, "lab_cells": cells,
            "lab_cell_label_noise": {"median": q(nz, 50), "p90": q(nz, 90)},
            "split_packs": {"rule": "seed-0 permutation of the 6 lab packs, 50/50", "calibration": cal,
                            "evaluation": ev},
            "targets_eval": {f"W{w}": sum(packs[p]["targets"][f"W{w}"] for p in ev) for w in WS}}


# ---------------------------------------------------------------- UMich parallel modules (Candidate A, named)
def umich():
    fs = sorted(glob.glob(f"{RAW}/umich_ppm/summary/Module_*_and_its_Cells.csv"))
    rows = []
    for f in fs:
        d = pd.read_csv(f).iloc[0]
        c = np.array([d[f"Cell_{k}_Capacity_Ah"] for k in "ABC"], float)
        rows.append({"spread": float((c.max() - c.min()) / c.mean()), "ctcv": float(d[
            "Population_Standard_Deviation_of_Cell_SOH_Percent"]), "msoh": float(d["Module_SOH_Percent"]),
            "module_over_sum": float(d["Module_Capacity_Ah"] / c.sum())})
    r = pd.DataFrame(rows)
    return {"source": "UMich parallel-module set, Mendeley 10.17632/ssrgfmb8vw.2 (CC BY 4.0); only Summary.csv "
                      "files downloaded (Raw time series not needed for the audit)",
            "modules": len(r), "cells_per_module": 3,
            "spread": {"median": float(r["spread"].median()), "max": float(r["spread"].max())},
            "ctcv_pct": {"min": float(r["ctcv"].min()), "max": float(r["ctcv"].max())},
            "module_SOH_pct": {"min": float(r["msoh"].min()), "max": float(r["msoh"].max())},
            "module_cap_over_sum_cells": {"median": float(r["module_over_sum"].median()),
                                          "p05": float(r["module_over_sum"].quantile(.05)),
                                          "p95": float(r["module_over_sum"].quantile(.95))},
            "cell_ids_in_files": False, "checks_per_module": 1}


def main():
    os.makedirs(OUT, exist_ok=True)
    res = {"isu": isu(), "baticm": baticm(), "umich": umich()}
    json.dump(res, open(f"{OUT}/profile.json", "w"), indent=1, default=float)
    sp = {"ISU-ILCC": res["isu"]["split"], "BatICM_lab_packs": res["baticm"]["split_packs"]}
    json.dump(sp, open(f"{OUT}/split.json", "w"), indent=1)
    s = {k: v for k, v in res["isu"].items() if k not in ("units", "cell_noise")}
    print(json.dumps(s, indent=1, default=float))
    b = res["baticm"]
    for k, v in b["packs"].items():
        print(k, json.dumps(v, default=float))
    print("lab cells", json.dumps(b["lab_cells"], default=float))
    print(json.dumps({k: b[k] for k in ("lab_cell_label_noise", "split_packs", "targets_eval")}, default=float))
    print(json.dumps(res["umich"], indent=1, default=float))


if __name__ == "__main__":
    main()
