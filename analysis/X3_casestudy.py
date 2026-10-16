"""Experiment X3 (pre-registered in results/X/X3_preregistration.md, commit 0c4580a): lead time of per-cell drift
on located faults. Case study, n = 4 faulty packs (BatICM car2-4 + BATSS ISC) + 1 healthy (BatICM car1); no p-values.
Usage: python analysis/X3_casestudy.py   (writes results/X/X3/x3.json)
Implementation choices the pre-registration left open are marked OPEN-n; deviations are marked DEV-n.
"""
import json
import os
import re
import xml.etree.ElementTree as ET
import zipfile

import numpy as np
import pandas as pd

BAT = "data/raw/baticm"
BATSS = "data/raw/batss/BATSS_20-21-22_ISC_results.xlsx"
OUT = "results/X/X3"
Z_FLAG, N_CONSEC, B_MV = -3.5, 2, -60.0               # pre-registered (§2)
# DEV-1: BatICM pack capacity is not published; rest = |I| <= 2.5 A = 0.05 C of an ASSUMED 50 Ah pack (a larger pack
# would make the threshold looser; 2.5 A is the stricter choice). BATSS: 1C = 67 A (CC 1C steps) -> 0.05 C = 3.35 A.
REST_A = {"baticm": 2.5, "batss": 3.35}
# OPEN-1: minimum data per evaluation window: >= 50 rest frames spanning >= 25 % of the window.
MIN_FR, MIN_SPAN = 50, 0.25
FAULTS = {2: [83], 3: [3, 82], 4: [64], 1: []}       # paper's cell numbers (Nie et al., Energy 2025, Table 1)


def robust_z(x):
    med = np.nanmedian(x)
    mad = 1.4826 * np.nanmedian(np.abs(x - med))
    return (x - med) / mad if mad > 0 else np.zeros_like(x)


def slopes(t, D):
    """OLS slope of each column of D (frames x cells) against t."""
    tc = t - t.mean()
    return (tc[:, None] * (D - D.mean(0))).sum(0) / (tc ** 2).sum()


def evaluate(t, V, I, Vmin_bms, rest_a, eval_times, win, unit):
    """t: hours since start. Returns per-evaluation dicts (A, A_lvl, B, B_bms)."""
    rest = np.abs(I) <= rest_a
    med = np.median(V, 1)
    D = (V - med[:, None]) * 1e3                      # mV deviation from pack median
    m = (V.min(1) - med) * 1e3
    mb = (Vmin_bms - med) * 1e3 if Vmin_bms is not None else None
    rows = []
    prev_end = -np.inf
    for te in eval_times:
        w = rest & (t > te - win) & (t <= te)
        if w.sum() < MIN_FR or np.ptp(t[w]) < MIN_SPAN * win:
            rows.append(None)
            prev_end = te
            continue
        zs = robust_z(slopes(t[w], D[w]))
        zl = robust_z(np.median(D[w], 0))
        day = rest & (t > prev_end) & (t <= te)       # this evaluation period only, for B
        rows.append({"t": float(te), "zs": zs, "zl": zl,
                     "B": float(np.median(m[day])) if day.any() else None,
                     "B_bms": float(np.median(mb[day])) if (mb is not None and day.any()) else None})
        prev_end = te
    return rows


def first_flags(rows, key):
    """Per cell: first evaluation time at which z <= Z_FLAG on N_CONSEC consecutive valid evaluations."""
    first, run = {}, {}
    for r in rows:
        if r is None:
            run = {}                                   # a gap breaks consecutiveness
            continue
        hit = set(np.where(r[key] <= Z_FLAG)[0].tolist())
        run = {k: run.get(k, 0) + 1 for k in hit}
        for k, n in run.items():
            if n >= N_CONSEC and k not in first:
                first[k] = r["t"]
    return first


def first_b(rows, key):
    n = 0
    for r in rows:
        if r is None or r[key] is None:
            n = 0
            continue
        n = n + 1 if r[key] < B_MV else 0
        if n >= N_CONSEC:
            return r["t"]
    return None


def summarise(name, rows, faulty_cols, unit, refs):
    out = {"case": name, "n_evaluations": len(rows), "n_valid": sum(r is not None for r in rows), "unit": unit,
           "faulty_cols_primary": faulty_cols["primary"], "faulty_cols_alt": faulty_cols["alt"], "refs": refs}
    for key in ("zs", "zl"):
        ff = first_flags(rows, key)
        tag = "A" if key == "zs" else "A_lvl"
        flags = sorted(((t, k) for k, t in ff.items()))
        out[f"{tag}_flags"] = [{"col": k, "t": t} for t, k in flags]
        for conv in ("primary", "alt"):
            cols = faulty_cols[conv]
            hits = [ff[c] for c in cols if c in ff]
            t_hit = min(hits) if hits else None
            out[f"{tag}_{conv}_first_correct"] = t_hit
            out[f"{tag}_{conv}_first_flag_is_faulty"] = bool(flags and flags[0][1] in cols) if flags else None
            out[f"{tag}_{conv}_false_before_correct"] = sum(1 for t, k in flags if k not in cols and (t_hit is None or t < t_hit))
            out[f"{tag}_{conv}_false_total"] = sum(1 for t, k in flags if k not in cols)
            for rname, rt in refs.items():
                out[f"{tag}_{conv}_lead_vs_{rname}"] = (rt - t_hit) if (t_hit is not None and rt is not None) else None
    out["B_first_flag"] = first_b(rows, "B")
    out["B_bms_first_flag"] = first_b(rows, "B_bms")
    return out


def baticm(car):
    d = pd.read_csv(f"{BAT}/car{car}/car{car}_processed.csv")
    vc = [c for c in d.columns if re.fullmatch(r"V_\d+", c)]
    vc.sort(key=lambda c: int(c[2:]))
    ts = pd.to_datetime(d["tboxTime"])
    t0 = ts.iloc[0]
    t_all = ((ts - t0).dt.total_seconds() / 3600).to_numpy()
    warn = d["BMSWarningInformation"].to_numpy() if "BMSWarningInformation" in d else None
    ok = d[vc].notna().all(1) & d["BMSBatteryCurrent"].notna()
    d, ts = d[ok], ts[ok]
    t = ((ts - t0).dt.total_seconds() / 3600).to_numpy()
    V = d[vc].to_numpy(float)
    I = d["BMSBatteryCurrent"].to_numpy(float)
    vmin = d["BMSCellVoltageMin"].to_numpy(float) if "BMSCellVoltageMin" in d else None
    day0 = t0.normalize()
    ends = [((day0 + pd.Timedelta(days=k + 1)) - t0).total_seconds() / 3600
            for k in range(int(np.ceil(t[-1] / 24)) + 1)]
    ends = [e for e in ends if e <= t[-1] + 24]
    rows = evaluate(t, V, I, vmin, REST_A["baticm"], ends, 7 * 24.0, "h")
    refs = {"end_of_record": float(t_all[-1])}
    if warn is not None:                               # from the UNFILTERED record (rows lacking cell data still carry warnings)
        w3 = np.where(warn >= 3)[0]
        refs["first_level3"] = float(t_all[w3[0]]) if len(w3) else None
    cols = {"primary": [c - 2 for c in FAULTS[car]],   # paper #n -> V_(n-1) -> 0-based index n-2
            "alt": [c - 1 for c in FAULTS[car]]}       # paper #n -> V_n
    s = summarise(f"BatICM car{car}", rows, cols, "h", refs)
    s.update({"n_frames": int(len(t)), "n_cells_csv": len(vc), "start": str(ts.iloc[0]), "end": str(ts.iloc[-1]),
              "rest_frac": float((np.abs(I) <= REST_A["baticm"]).mean())})
    return s


def read_xlsx(path):
    z = zipfile.ZipFile(path)
    strs = re.findall(r"<t[^>]*>([^<]*)</t>", z.read("xl/sharedStrings.xml").decode("utf8", "replace"))
    ns = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"

    def ci(ref):
        n = 0
        for ch in re.match(r"[A-Z]+", ref).group(0):
            n = n * 26 + ord(ch) - 64
        return n - 1
    hdr, rows = None, []
    with z.open("xl/worksheets/sheet1.xml") as f:
        for _, el in ET.iterparse(f, events=("end",)):
            if el.tag != ns + "row":
                continue
            vals = {}
            for c in el.findall(ns + "c"):
                v = c.find(ns + "v")
                if v is not None:
                    vals[ci(c.get("r"))] = strs[int(v.text)] if c.get("t") == "s" else v.text
            if hdr is None:
                hdr = [vals.get(i, "") for i in range(max(vals) + 1)]
            else:
                rows.append(vals)
            el.clear()
    H = {h: i for i, h in enumerate(hdr)}
    return H, rows


def batss():
    H, rows = read_xlsx(BATSS)
    col = lambda n: np.array([float(r.get(H[n], "nan")) for r in rows])
    t = col("Time_s") / 3600
    V = np.column_stack([col(f"Vcell_{k}_V_") for k in range(1, 11)])
    I = col("Current_A_")
    ok = np.isfinite(V).all(1) & np.isfinite(I)
    t, V, I = t[ok], V[ok], I[ok]
    ends = list(np.arange(1.0, np.ceil(t[-1]) + 1))
    rows_ = evaluate(t, V, I, None, REST_A["batss"], ends, 3.0, "h")
    refs = {"end_of_record": float(t[-1]), "start_of_record_as_resistor_on": 0.0}   # DEV-2: resistor-on time not in file
    s = summarise("BATSS ISC", rows_, {"primary": [7], "alt": [1]}, "h", refs)    # primary = predicted cell 8; alt = cell 2
    s["note"] = "faulty cell unconfirmed: 'primary' = prediction (cell 8), 'alt' = cell 2 (the min cell); prediction pending"
    s.update({"n_frames": int(len(t)), "rest_frac": float((np.abs(I) <= REST_A["batss"]).mean())})
    return s


def main():
    os.makedirs(OUT, exist_ok=True)
    res = [baticm(c) for c in (2, 3, 4, 1)] + [batss()]
    json.dump(res, open(f"{OUT}/x3.json", "w"), indent=1, default=float)
    for r in res:
        keep = {k: v for k, v in r.items() if not k.endswith("_flags")}
        print(json.dumps(keep, default=float))
        print("  A flags:", r["A_flags"][:8], "| A_lvl flags:", r["A_lvl_flags"][:8])


if __name__ == "__main__":
    main()
