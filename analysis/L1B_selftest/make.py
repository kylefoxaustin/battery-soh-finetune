"""Writes synthetic scenarios for analysis/L1B_agreement.py (no real ledger content; every act_id is invented).

Shared by every scenario:
- B_events.csv: 35 invented B events, 8 of them vehicle-level (B05, B06, B14, B15, two each), 27 not;
- an L1 calibration reference in ref_L1/: 6 matched seat events S01-S06 with act_ids SREF1-SREF6, so N_S1 = 6 and
  E_S1 has 6 acts.

Scenarios (expected readouts are asserted by check.py):
t1  CALIBRATED (6 S pairs = E_S1); 2 L pairs, one pass-2 date match, 1 unmatched L event in A; N_L 10, R_BL 3.5
    [lower bound 1.76] -> SPECIFIC BY COUNT; k_B 4/27, k_L 1, k_S 0 -> STACK-SPECIFIC.
t2  MISCALIBRATED (2 S pairs: diff 4, 2 of E_S1); 20 L pairs, N_L 28, R_BL 1.25 -> NOT SPECIFIC BY COUNT;
    k_L 3 -> NOT STACK-SPECIFIC.
t3  L1B-D1, share clause off: k_L 1 of n_L 5, k_B 2/27 (share L 0.20 >= B 0.07, but n_L < 10) -> UNCLEAR IN KIND
    (without D1 it would read NOT STACK-SPECIFIC); N_L 13, R_BL 2.69 -> UNCLEAR BY COUNT.
t4  L1B-D1, share clause on: k_L 1 of n_L 10, k_B 1/27 -> NOT STACK-SPECIFIC; calibration at both boundaries
    (9 S pairs: diff 3; 5 of E_S1) -> CALIBRATED; N_L 18 -> UNCLEAR BY COUNT.
t5  access branch: t1 with L13-L20 (8 L seeds) `none` for both -> UNCLEAR BY COUNT (ACCESS-LIMITED: L);
    ACC (drops unread instruments, no qualifier) -> SPECIFIC BY COUNT.
t6  t1 with the raters split on 20 of the 27 domain-B stack rows -> kappa stack < 0.60 -> UNGATED (both verdicts).
"""
import csv
import os

COLS = ["event_id", "instrument_id", "domain", "act_id", "adoption_date", "application_date", "jurisdiction",
        "what_changed", "class", "confidence", "source_url", "source_type", "note"]
SL_IDS = [f"L{i:02d}" for i in range(1, 48)] + [f"S{i:02d}" for i in range(1, 27)]
L1_IDS = [f"B{i:02d}" for i in range(1, 38)] + [f"S{i:02d}" for i in range(1, 27)]
SO, MC, HW = "software-only", "memory-or-crypto", "hardware-or-recert"
CL = [SO, MC, HW]
here = os.path.dirname(os.path.abspath(__file__))

# 35 invented B events: 27 specific (B01-B04, B07-B13, ...), 8 vehicle-level (two each on B05, B06, B14, B15)
SPEC = ["B01", "B02", "B03", "B04", "B07", "B08", "B09", "B10", "B11", "B12", "B13", "B16", "B17", "B18", "B19",
        "B20", "B21", "B22", "B23", "B24", "B25", "B26", "B27", "B28", "B29", "B30", "B31"]
BEV = [(inst, f"BEV{k:02d}", f"20{18 + k % 8}-03-01") for k, inst in enumerate(SPEC)]
BEV += [(inst, f"BVL{inst}{j}", f"202{2 + j}-06-01") for inst in ("B05", "B06", "B14", "B15") for j in (0, 1)]


def write_ledger(path, rows, cols, stack):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, cols + (["stack"] if stack else []))
        w.writeheader()
        for k, r in enumerate(rows):
            d = {"event_id": k + 1, "domain": r[0][0], "jurisdiction": "x", "what_changed": "synthetic",
                 "confidence": "medium", "source_url": "https://example.invalid", "source_type": "primary", "note": "",
                 "application_date": "", **dict(zip(["instrument_id", "act_id", "adoption_date", "class"], r))}
            if stack:
                d["stack"] = r[4]
            w.writerow(d)


def write_access(path, ids, acc):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["instrument_id", "history_access", "sources_tried", "note"])
        for i in ids:
            w.writerow([i, acc.get(i, "full"), "synthetic", ""])


def write(name, A, B, sb_yes_A, sb_yes_B, none=()):
    d = os.path.join(here, name)
    os.makedirs(d, exist_ok=True)
    write_ledger(os.path.join(d, "ledger_A.csv"), A, COLS, True)
    write_ledger(os.path.join(d, "ledger_B.csv"), B, COLS, True)
    acc = {i: "none" for i in none}
    write_access(os.path.join(d, "instruments_A.csv"), SL_IDS, acc)
    write_access(os.path.join(d, "instruments_B.csv"), SL_IDS, acc)
    with open(os.path.join(d, "B_events.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["instrument_id", "act_id", "adoption_date", "jurisdiction", "what_changed", "source_url"])
        for inst, act, dt in BEV:
            w.writerow([inst, act, dt, "x", "synthetic", "https://example.invalid"])
    for R, yes in (("A", sb_yes_A), ("B", sb_yes_B)):
        with open(os.path.join(d, f"stack_B_{R}.csv"), "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["act_id", "domain", "stack", "confidence", "note"])
            for inst, act, _ in BEV:
                for dom in (("B", "S", "L") if inst in ("B05", "B06", "B14", "B15") else ("B",)):
                    w.writerow([act, dom, "yes" if (act, dom) in yes else "no", "medium", ""])


def s_pairs(refs, extra=0):
    """Matched S rows: the given SREF acts (identical act_id) plus `extra` new acts, on S01-S16, all stack no."""
    rows = [(f"S{k + 1:02d}", f"SREF{k + 1}", f"2019-0{1 + k % 9}-10", CL[k % 3], "no") for k in refs]
    rows += [(f"S{10 + k:02d}", f"SNEW{k}", "2021-04-01", CL[k % 3], "no") for k in range(extra)]
    return rows


def l_pairs(n, yes, insts=None):
    insts = insts or [f"L{(k % 12) + 1:02d}" for k in range(n)]
    return [(insts[k], f"LACT{k}", f"20{17 + k % 9}-05-0{1 + k % 9}", CL[k % 3], "yes" if k < yes else "no")
            for k in range(n)]


def by_yes(k, start=0):
    return {(f"BEV{j:02d}", "B") for j in range(start, start + k)}


# L1 calibration reference: 6 matched S events, all instruments full
ref = os.path.join(here, "ref_L1")
os.makedirs(ref, exist_ok=True)
R6 = [(f"S{k + 1:02d}", f"SREF{k + 1}", f"2019-0{1 + k % 9}-10", CL[k % 3]) for k in range(6)]
write_ledger(os.path.join(ref, "ledger_A.csv"), R6, COLS, False)
write_ledger(os.path.join(ref, "ledger_B.csv"), R6, COLS, False)
write_access(os.path.join(ref, "instruments_A.csv"), L1_IDS, {})
write_access(os.path.join(ref, "instruments_B.csv"), L1_IDS, {})

# t1
S = s_pairs(range(6))
L = [("L01", "LACT0", "2020-05-01", MC, "yes")]
A = S + L + [("L02", "L02-X", "2022-03-01", SO, "no"), ("L05", "LONLYA", "2023-01-01", SO, "no")]
B = S + L + [("L02", "L02-Y", "2022-04-15", SO, "no")]          # 45 days apart: pass 2
write("t1", A, B, by_yes(4), by_yes(4))
# t2
S = s_pairs(range(2))
L = l_pairs(20, 3)
write("t2", S + L, S + L, by_yes(4), by_yes(4))
# t3
S = s_pairs(range(6))
L = l_pairs(5, 1)
write("t3", S + L, S + L, by_yes(2), by_yes(2))
# t4
S = s_pairs(range(5), extra=4)
L = l_pairs(10, 1)
write("t4", S + L, S + L, by_yes(1), by_yes(1))
# t5
write("t5", A, B, by_yes(4), by_yes(4), none=[f"L{i:02d}" for i in range(13, 21)])
# t6
write("t6", A, B, by_yes(4) | by_yes(10, 4), by_yes(4) | by_yes(10, 14))
print("written")
