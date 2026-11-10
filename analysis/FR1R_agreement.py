"""FR1-R agreement analysis: implements results/FR1R/FR1R_preregistration.md §5-§7 exactly.

Inputs: results/FR1R/ratings_A.csv and ratings_B.csv (one row per case; pre-registration §3), rater_{A,B}_fetch.json,
and the case metadata in results/FR1/FR1_cases.md. Output: results/FR1R/fr1r.json.

Written after rater A launched and before either ratings file was read; tested on synthetic ratings only.
Run from the repository root:  python3 -I analysis/FR1R_agreement.py [--dir results/FR1R] [--out fr1r.json]
"""
import argparse
import csv
import json
import math
import os
import re
from collections import Counter

STATES = {"not observable": 0, "<=1 s": 1, "(1,40] s": 2, "(40,80] s": 3, "(80,700] s": 4, ">700 s": 5,
          "cannot judge": None}
RATES = {"<=10 Hz": 0, "10 Hz-1 kHz": 1, ">=1 kHz": 2}
CAUSES = ["transient electrical", "thermal", "manufacturing or component defect", "software or calibration",
          "unknown / mixed"]
EVIDENCE = ["DTC freeze-frame", "bench reproduction", "fleet statistics", "waveform or high-rate capture",
            "teardown only", "not stated"]
FLAGS = ["flag_no_cause", "flag_software_only", "flag_out_of_scope"]
COLLAPSE4 = {0: "not observable", 1: "<=1 s", 2: "(1,80] s", 3: "(1,80] s", 4: ">80 s", 5: ">80 s"}
Z = 1.96


def wilson(k, n):
    if n == 0:
        return None, None, None
    p = k / n
    d = 1 + Z * Z / n
    c = (p + Z * Z / (2 * n)) / d
    h = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n)) / d
    return p, c - h, c + h


def kappa(pairs):
    """Unweighted Cohen's kappa over (a, b) label pairs."""
    n = len(pairs)
    if n == 0:
        return {"kappa": None, "n": 0}
    po = sum(a == b for a, b in pairs) / n
    ca, cb = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / (n * n)
    return {"kappa": None if pe == 1 else (po - pe) / (1 - pe), "n": n, "observed_agreement": po}


def cases_meta(path="results/FR1/FR1_cases.md"):
    text = open(path).read()
    pe_block = text.split("## Power-electronics cases")[1].split("\n## ")[0]
    br_block = text.split("## Base-rate sample")[1].split("\n## ")[0]
    meta = {}
    for line in pe_block.splitlines():
        m = re.match(r"^\| (PE\d{3}) \|", line)
        if m and m.group(1) != "PE006":  # FR1 D-1
            f = [x.strip() for x in line.strip("|").split("|")]
            meta[f[0]] = {"date": f[2], "groups": [g.strip() for g in f[7].split(";")], "cluster": f[9],
                          "initiated": f[11]}
    m = re.search(r"\*\*PE076\*\* = \[25V-811\].*?, (\d{4})-(\d\d)-(\d\d),.*?groups (.*?), plug-in rule.*?cluster (C\d+), "
                  r"initiated by (\w+)", text)
    meta["PE076"] = {"date": "".join(m.group(1, 2, 3)), "groups": [g.strip() for g in m.group(4).split(";")],
                     "cluster": m.group(5), "initiated": m.group(6)}
    for line in br_block.splitlines():
        mm = re.match(r"^\| (BR\d{3}) \|", line)
        if mm:
            f = [x.strip() for x in line.strip("|").split("|")]
            meta[f[0]] = {"date": f[2], "groups": [f[6]], "cluster": None, "initiated": None}
    assert sum(k.startswith("PE") for k in meta) == 75 and sum(k.startswith("BR") for k in meta) == 75
    return meta


def load(path, ids):
    rows, problems = {}, []
    for r in csv.DictReader(open(path, newline="")):
        r = {k.strip(): (v or "").strip() for k, v in r.items() if k}
        c = r["case"]
        if c in rows:
            problems.append(f"{c}: duplicate row")
        if r["window"] not in STATES:
            problems.append(f"{c}: window {r['window']!r} not in the closed list")
        s = STATES.get(r["window"])
        if s is not None and s >= 2 and r["rate_class"] not in RATES:
            problems.append(f"{c}: rate_class {r['rate_class']!r} missing or not in the closed list for state {s}")
        if (s is None or s < 2) and r["rate_class"] not in ("n/a", ""):
            problems.append(f"{c}: rate_class {r['rate_class']!r} given for a state that takes n/a")
        if r["cause_type"] not in CAUSES:
            problems.append(f"{c}: cause_type {r['cause_type']!r} not in the closed list")
        if r["evidence"] not in EVIDENCE:
            problems.append(f"{c}: evidence {r['evidence']!r} not in the closed list")
        r["state"] = s
        r["rate"] = RATES.get(r["rate_class"]) if s is not None and s >= 2 else None
        r["flags"] = {f for f in FLAGS if r.get(f, "").lower() in ("yes", "y", "true", "1")}
        rows[c] = r
    missing = sorted(set(ids) - set(rows))
    extra = sorted(set(rows) - set(ids))
    problems += [f"{c}: no row" for c in missing] + [f"{c}: not a case" for c in extra]
    return rows, problems


def frac(k, n):
    p, lo, hi = wilson(k, n)
    return {"k": k, "n": n, "p": p, "lo": lo, "hi": hi}


def readouts(ids, A, B, sens=None):
    """Pre-registration §5-§6 on a set of case IDs. sens: None (primary), 'A' or 'B' (the §6 sensitivities)."""
    out = {"n_cases": len(ids), "excluded": [], "cannot_judge": [], "not_observable_one": [], "not_observable_both": []}
    den = []
    for c in ids:
        a, b = A[c], B[c]
        if a["flags"] & b["flags"]:
            out["excluded"].append(c)
            continue
        sa, sb, ra, rb = a["state"], b["state"], a["rate"], b["rate"]
        if sens == "B":
            sa = 1 if sa is None else sa
            sb = 1 if sb is None else sb
        if sa is None or sb is None:
            out["cannot_judge"].append(c)
            continue
        if sa == 0 and sb == 0:
            out["not_observable_both"].append(c)
            continue
        if sa == 0 or sb == 0:
            if sens == "A":
                s, r = (sb, rb) if sa == 0 else (sa, ra)
                den.append((c, s, r if s >= 2 else None))
            else:
                out["not_observable_one"].append(c)
            continue
        s = min(sa, sb)
        r = min(ra, rb) if sa >= 2 and sb >= 2 else None
        den.append((c, s, r))
    n = len(den)
    out["denominator"] = n
    out["P80"] = frac(sum(s >= 4 for _, s, _ in den), n)
    out["P40"] = frac(sum(s >= 3 for _, s, _ in den), n)
    out["RB"] = frac(sum(2 <= s <= 4 and r == 2 for _, s, r in den), n)
    out["P1"] = frac(sum(s >= 2 for _, s, _ in den), n)
    out["conservative_state_distribution"] = dict(sorted(Counter(s for _, s, _ in den).items()))
    out["conservative_rate_distribution_states_2_5"] = dict(sorted(Counter(r for _, s, r in den if s >= 2).items(),
                                                                   key=lambda x: (x[0] is None, x[0])))
    out["cases"] = {c: {"state": s, "rate": r} for c, s, r in den}
    return out


def own(ids, R):
    """One rater's own P80 and RB: its cases with a state other than not observable (exclusion needs both raters, so none)."""
    den = [(R[c]["state"], R[c]["rate"]) for c in ids if R[c]["state"] not in (None, 0)]
    n = len(den)
    return {"denominator": n, "P80": frac(sum(s >= 4 for s, _ in den), n),
            "RB": frac(sum(2 <= s <= 4 and r == 2 for s, r in den), n)}


def decide(gate_kappa, den_n, P80, P40, RB):
    if gate_kappa is None or gate_kappa < 0.6 or den_n < 10:
        return "UNGATED", None
    if P80["p"] >= 0.5 and P80["lo"] > 0.2:
        v = "RETENTION IS A NECESSITY"
    elif P40["p"] < 0.2:
        v = "RETENTION IS A CONVENIENCE"
    else:
        v = "UNCLEAR"
    if RB["p"] >= 0.25 and RB["lo"] > 0.10:
        shape = "RING BUFFER SHAPED"
    elif P80["p"] >= 0.5 and RB["p"] < 0.10:
        shape = "FLASH/CLOUD SHAPED"
    else:
        shape = "MIXED"
    return v, shape


def fetch_summary(path):
    if not os.path.exists(path):
        return {"missing_file": path}
    d = json.load(open(path))
    recs = d if isinstance(d, list) else d.get("records") or d.get("documents") or list(d.values())[-1]
    bad = [r for r in recs if isinstance(r, dict) and not r.get("ok", True)]
    mism = [r for r in recs if isinstance(r, dict) and r.get("ok", True) and str(r.get("match")).lower() in ("false", "no")]
    return {"records": len(recs), "not_ok": [(r.get("case"), r.get("url")) for r in bad],
            "hash_mismatch": [(r.get("case"), r.get("url")) for r in mism]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="results/FR1R")
    ap.add_argument("--out", default="fr1r.json")
    a = ap.parse_args()
    meta = cases_meta()
    ids = sorted(meta)
    PE = [c for c in ids if c.startswith("PE")]
    BR = [c for c in ids if c.startswith("BR")]
    A, pa = load(os.path.join(a.dir, "ratings_A.csv"), ids)
    B, pb = load(os.path.join(a.dir, "ratings_B.csv"), ids)
    if pa or pb:
        print("VALIDATION PROBLEMS\n  A: " + "\n  A: ".join(pa) + "\n  B: " + "\n  B: ".join(pb))
    if [p for p in pa + pb if p.endswith("no row")]:
        raise SystemExit("a case has no row")

    both_state = [c for c in ids if A[c]["state"] is not None and B[c]["state"] is not None]
    gate = kappa([(COLLAPSE4[A[c]["state"]], COLLAPSE4[B[c]["state"]]) for c in both_state])
    k7 = kappa([(A[c]["window"], B[c]["window"]) for c in ids])
    k1 = kappa([(A[c]["cause_type"], B[c]["cause_type"]) for c in ids])
    both25 = [c for c in ids if (A[c]["state"] or 0) >= 2 and (B[c]["state"] or 0) >= 2]
    k3b = kappa([(A[c]["rate_class"], B[c]["rate_class"]) for c in both25])

    pe = readouts(PE, A, B)
    verdict, shape = decide(gate["kappa"], pe["denominator"], pe["P80"], pe["P40"], pe["RB"])

    # one case per cluster: the earliest campaign (Part 573 received, then case ID) of each PE cluster
    first = {}
    for c in sorted(PE, key=lambda c: (meta[c]["date"], c)):
        first.setdefault(meta[c]["cluster"], c)
    groups = sorted({g for c in PE for g in meta[c]["groups"]})

    def dist(R, field, cases):
        return dict(Counter(R[c][field] for c in cases).most_common())

    disagreements = []
    for c in ids:
        d = {f: (A[c][f], B[c][f]) for f in ["cause_type", "evidence", "window", "rate_class", "confidence"] + FLAGS
             if A[c][f] != B[c][f]}
        if d:
            disagreements.append({"case": c, "differs": d, "signals_A": A[c]["signals"], "signals_B": B[c]["signals"]})

    out = {
        "preregistration": "results/FR1R/FR1R_preregistration.md (2541d02)",
        "tags": "every rating DERIVED-judgemental; source NHTSA, public domain; both raters are language-model sessions",
        "validation_problems": {"A": pa, "B": pb},
        "verdict": verdict, "shape": shape,
        "gate": {"kappa4": gate, "pe_denominator": pe["denominator"], "pass": verdict != "UNGATED"},
        "kappa": {"item3_four_class": gate, "item3_seven_way": k7, "item1": k1, "item3b_both_states_2_5": k3b},
        "PE": pe,
        "BR": readouts(BR, A, B),
        "sensitivity_A_one_rater_not_observable_takes_other": readouts(PE, A, B, "A"),
        "sensitivity_B_cannot_judge_as_le1s": readouts(PE, A, B, "B"),
        "own": {"A": own(PE, A), "B": own(PE, B)},
        "state_distribution_PE": {"A": dist(A, "window", PE), "B": dist(B, "window", PE)},
        "state_distribution_BR": {"A": dist(A, "window", BR), "B": dist(B, "window", BR)},
        "rate_distribution_PE_states_2_5": {R: dict(Counter(X[c]["rate_class"] for c in PE if (X[c]["state"] or 0) >= 2))
                                            for R, X in (("A", A), ("B", B))},
        "cause_distribution_PE": {"A": dist(A, "cause_type", PE), "B": dist(B, "cause_type", PE)},
        "evidence_distribution_PE": {"A": dist(A, "evidence", PE), "B": dist(B, "evidence", PE)},
        "evidence_distribution_BR": {"A": dist(A, "evidence", BR), "B": dist(B, "evidence", BR)},
        "flags_single_rater": {R: {f: [c for c in ids if f in X[c]["flags"] and f not in Y[c]["flags"]] for f in FLAGS}
                               for R, X, Y in (("A", A, B), ("B", B, A))},
        "by_component_group": {g: readouts([c for c in PE if g in meta[c]["groups"]], A, B) for g in groups},
        "one_case_per_cluster": dict(readouts(sorted(first.values()), A, B), clusters=len(first)),
        "signals_named": {c: {"A": A[c]["signals"], "B": B[c]["signals"]} for c in ids},
        "fetch": {"A": fetch_summary(os.path.join(a.dir, "rater_A_fetch.json")),
                  "B": fetch_summary(os.path.join(a.dir, "rater_B_fetch.json"))},
        "docs_missing": {R: {c: X[c]["docs_missing"] for c in ids if X[c].get("docs_missing")} for R, X in (("A", A), ("B", B))},
        "disagreements": disagreements,
    }
    json.dump(out, open(os.path.join(a.dir, a.out), "w"), indent=1, default=str)
    p = lambda f: f"{f['k']}/{f['n']} = {100 * f['p']:.1f} % [{100 * f['lo']:.1f}, {100 * f['hi']:.1f}]" if f["n"] else "n = 0"
    print(f"verdict {verdict}; shape {shape}")
    print(f"kappa4 {gate['kappa']} (n {gate['n']}); kappa7 {k7['kappa']}; kappa item1 {k1['kappa']}; kappa 3b {k3b['kappa']} (n {k3b['n']})")
    print(f"PE denominator {pe['denominator']}; excluded {len(pe['excluded'])}; cannot judge {len(pe['cannot_judge'])}; "
          f"not observable one {len(pe['not_observable_one'])}, both {len(pe['not_observable_both'])}")
    for k in ("P80", "P40", "RB", "P1"):
        print(f"  {k}: {p(pe[k])}")
    print(f"disagreements: {len(disagreements)} cases")


if __name__ == "__main__":
    main()
