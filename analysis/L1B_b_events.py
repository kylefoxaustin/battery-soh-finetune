"""L1b: writes results/L1B/B_events.csv, the 35 matched domain-B events of L1 (brief §4), identity columns only.

The events are L1's primary (V2) domain-B matched pairs: seed instruments, both adoption dates in the window, the
vehicle-level instruments included (L-1). l1.json does not store the pairs themselves, so this script recomputes them
with analysis/L1_agreement.py's own functions from results/L1/ledger_A.csv and ledger_B.csv, and checks the count
against l1.json (primary_V2.N_B). It writes, from rater A's row of each pair: instrument_id, act_id, adoption_date,
jurisdiction, what_changed, source_url. No class, confidence or note column, and nothing from rater B's row, is written
or printed. Run from the repository root:  python3 -I analysis/L1B_b_events.py
"""
import csv
import json
import os
import sys

sys.path.insert(0, os.path.join(os.getcwd(), "analysis"))
import L1_agreement as L1  # noqa: E402

COLS = ["instrument_id", "act_id", "adoption_date", "jurisdiction", "what_changed", "source_url"]


def main():
    meta = L1.instruments("results/L1/L1_instruments.md")
    A, _ = L1.load_ledger("results/L1/ledger_A.csv", meta)
    B, _ = L1.load_ledger("results/L1/ledger_B.csv", meta)
    accA, _ = L1.load_access("results/L1/instruments_A.csv", meta)
    accB, _ = L1.load_access("results/L1/instruments_B.csv", meta)
    blocked = {i for i in meta if accA.get(i) == "none" and accB.get(i) == "none"}
    seed = {i for i, m in meta.items() if m["seed"]}
    pairs, ua, ub = L1.match(A, B)
    r = L1.readout(pairs, ua, ub, meta, seed, "V2", blocked)
    P = [a for a, b, _ in r["_pairs"] if meta[a["instrument_id"]]["domain"] == "B"]
    n_l1 = json.load(open("results/L1/l1.json"))["primary_V2"]["N_B"]
    assert len(P) == r["N_B"] == n_l1, (len(P), r["N_B"], n_l1)
    P.sort(key=lambda a: (a["instrument_id"], a["_adopt"], a["_i"]))
    os.makedirs("results/L1B", exist_ok=True)
    with open("results/L1B/B_events.csv", "w", newline="") as f:
        w = csv.DictWriter(f, COLS)
        w.writeheader()
        for a in P:
            w.writerow({k: a.get(k, "") for k in COLS})
    print(f"wrote results/L1B/B_events.csv: {len(P)} events (l1.json primary_V2.N_B = {n_l1}); columns {COLS}")


if __name__ == "__main__":
    main()
