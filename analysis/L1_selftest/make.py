"""Writes two synthetic L1 scenarios for analysis/L1_agreement.py (no real ledger content).

s1, nothing access-limited:
- 12 domain-B events: 8 matched by act_id, 4 by the +-90-day rule with differently written act_ids;
- 1 vehicle-level event (B05), matched by act_id although its two dates are 7 months apart;
- 2 domain-S events;
- 1 unmatched event on each side, and 1 pair outside the window.
Expected: identification 15/17; N_B 13, N_S 3 (V2) / 2 (V1); VOLATILE DOMAIN; CN0 (drops B08-B13) UNCLEAR on R 7/3.

s2, domain B access-limited (13 B seeds 'none' from both raters):
- 3 matched B events and 4 S events.
N_B <= 5 and R < 1.5 must NOT fire STABLE or the kill. Expected: UNCLEAR (ACCESS-LIMITED: B). ACC, which
drops the unread instruments, reads STABLE DOMAIN.
"""
import csv
import os

COLS = ["event_id", "instrument_id", "domain", "act_id", "adoption_date", "application_date", "jurisdiction",
        "what_changed", "class", "confidence", "source_url", "source_type", "note"]
IDS = [f"B{i:02d}" for i in range(1, 38)] + [f"S{i:02d}" for i in range(1, 27)]
here = os.path.dirname(os.path.abspath(__file__))


def write(d, A, B, accA, accB):
    os.makedirs(d, exist_ok=True)
    for name, rows in (("ledger_A.csv", A), ("ledger_B.csv", B)):
        with open(os.path.join(d, name), "w", newline="") as f:
            w = csv.DictWriter(f, COLS)
            w.writeheader()
            for k, r in enumerate(rows):
                w.writerow({"event_id": k + 1, "domain": r[0][0], "jurisdiction": "x", "what_changed": "synthetic",
                            "confidence": "medium", "source_url": "https://example.invalid", "source_type": "primary",
                            "note": "", "application_date": "", **dict(zip(["instrument_id", "act_id", "adoption_date", "class"], r))})
    for name, acc in (("instruments_A.csv", accA), ("instruments_B.csv", accB)):
        with open(os.path.join(d, name), "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["instrument_id", "history_access", "sources_tried", "note"])
            for i in IDS:
                w.writerow([i, acc.get(i, "full"), "synthetic", ""])


MC, SO, HW = "memory-or-crypto", "software-only", "hardware-or-recert"
# s1
A, B = [], []
for k, inst in enumerate(["B01", "B02", "B03", "B04", "B07", "B08", "B09", "B10"]):
    A.append((inst, f"ACT-{k}", f"2018-0{1 + k % 9}-10", MC))
    B.append((inst, f"act {k}", f"2018-0{1 + k % 9}-25", MC if k != 3 else HW))
for k, inst in enumerate(["B11", "B12", "B13", "B16"]):
    A.append((inst, f"X{k}", "2021-03-01", MC if k else SO))
    B.append((inst, f"Y{k}", "2021-05-15", MC))          # 75 days apart: pass 2
A.append(("B05", "R155-00-S1", "2022-06-22", SO)); B.append(("B05", "R155 00 S1", "2023-01-15", SO))  # act_id match
A.append(("S01", "R14-07-S3", "2019-03-01", SO)); B.append(("S01", "R14-07-S3", "2019-03-01", SO))
A.append(("S07", "84 FR 1", "2020-01-01", SO)); B.append(("S07", "84 FR 1", "2020-01-02", SO))
A.append(("B20", "IEC 61851-1:2017", "2017-02-07", SO))                 # unmatched in A
B.append(("B21", "IEC 61851-23:2023", "2023-06-01", "cannot judge"))     # unmatched in B
A.append(("B01", "OLD", "2014-01-01", SO)); B.append(("B01", "OLD", "2014-01-01", SO))  # outside the window
write(os.path.join(here, "s1"), A, B, {}, {})
# s2
none = {i: "none" for i in [f"B{i:02d}" for i in range(16, 29)]}  # 13 domain-B seeds unread by both
A = [("B01", "a1", "2024-01-01", MC), ("B02", "a2", "2024-02-01", SO), ("B03", "a3", "2024-03-01", SO),
     ("S01", "s1", "2020-01-01", SO), ("S02", "s2", "2021-01-01", SO), ("S03", "s3", "2022-01-01", SO), ("S04", "s4", "2023-01-01", SO)]
write(os.path.join(here, "s2"), A, list(A), none, none)
print("written")
