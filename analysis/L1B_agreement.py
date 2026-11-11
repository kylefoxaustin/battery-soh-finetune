"""L1b agreement analysis: implements results/L1B/L1B_preregistration.md §5 with deviation L1B-D1 (§10).

L1's script (analysis/L1_agreement.py) extended to domains S and L, the `stack` class and the calibration readout.
L1's own functions are imported for matching (L-4), Wilson intervals, kappa and dates.

Inputs, in --dir (default results/L1B): ledger_A.csv, ledger_B.csv (domains S and L, L1 §2 columns plus `stack`),
stack_B_A.csv, stack_B_B.csv (act_id, domain, stack, confidence, note), instruments_A.csv, instruments_B.csv, and
B_events.csv (the 35 carried-over B events). Instrument metadata: results/L1B/L1B_instruments.md §1 (--meta).
Calibration reference: L1's committed ledgers and instrument files in --l1dir (default results/L1), with metadata
from results/L1/L1_instruments.md; N_S1 and E_S1 are computed here with L1's functions, never typed in.
Output: <dir>/l1b.json (--out).

Written and committed before either rater branch existed; exercised on the synthetic ledgers in
analysis/L1B_selftest/. Run from the repository root:  python3 -I analysis/L1B_agreement.py [--dir D] [--l1dir D1]
"""
import argparse
import csv
import json
import math
import os
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.join(os.getcwd(), "analysis"))
import L1_agreement as L1  # noqa: E402

STACK = ["yes", "no", "cannot judge"]
VEHICLE_LEVEL = L1.VEHICLE_LEVEL  # B05 R155, B06 R156, B14 GB 44495, B15 GB 44496 (L-1)
ORDER = L1.ORDER
L_SEEDS, S_SEEDS = 22, 16
L_LIMIT, S_LIMIT = 8, 6           # §3b: L access-limited at >= 8 of 22 seeds `none` for both; S as L1 (>= 6 of 16)
CAL_COUNT, CAL_ACTS = 3, 5        # §5 calibration: |N_S,specific - N_S1| <= 3 and >= 5 of E_S1
D1_MIN_NL = 10                    # L1B-D1: the share clause of NOT STACK-SPECIFIC applies only when n_L >= 10
wilson, kappa, norm, in_window = L1.wilson, L1.kappa, L1.norm, L1.in_window


def instruments(path):
    sec = open(path).read().split("## 1. Instruments")[1].split("\n## ")[0]
    meta = {}
    for line in sec.splitlines():
        m = re.match(r"^\| ([LS]\d{2}) \| ([LS]) \|", line)
        if m:
            c = [x.strip() for x in line.strip().strip("|").split(" | ")]
            meta[m.group(1)] = {"domain": m.group(2), "seed": c[8].startswith("seed"), "china": c[5] == "China",
                                "vehicle_level": False}
    assert len(meta) == 73, len(meta)
    assert sum(v["seed"] and v["domain"] == "L" for v in meta.values()) == L_SEEDS
    assert sum(v["seed"] and v["domain"] == "S" for v in meta.values()) == S_SEEDS
    return meta


def load_ledger(path, meta):
    rows, problems = L1.load_ledger(path, meta)
    for r in rows:
        if r.get("stack") not in STACK:
            problems.append(f"row {r['_i']} ({r['instrument_id']}): stack {r.get('stack')!r} not in the closed list")
        if r.get("domain") and r["domain"] != meta[r["instrument_id"]]["domain"]:
            problems.append(f"row {r['_i']} ({r['instrument_id']}): domain {r['domain']!r} differs from the list")
    return rows, problems


def load_b_events(path, l1meta):
    ev = [{k.strip(): (v or "").strip() for k, v in r.items() if k} for r in csv.DictReader(open(path, newline=""))]
    for r in ev:
        r["_adopt"] = L1.pdate(r["adoption_date"])
        r["_vl"] = r["instrument_id"] in VEHICLE_LEVEL
        r["_china"] = l1meta[r["instrument_id"]]["china"]
    assert len(ev) == 35 and sum(r["_vl"] for r in ev) == 8, (len(ev), sum(r["_vl"] for r in ev))
    assert len({norm(r["act_id"]) for r in ev}) == 35
    return ev


def stack_b_keys(ev):
    """The 51 expected stack_B rows: one (act_id, B) per event, plus (act_id, S) and (act_id, L) when vehicle-level."""
    keys = []
    for r in ev:
        keys += [(norm(r["act_id"]), d) for d in (("B", "S", "L") if r["_vl"] else ("B",))]
    assert len(keys) == 51
    return keys


def load_stack_b(path, keys):
    got, problems = {}, []
    for i, r in enumerate(csv.DictReader(open(path, newline=""))):
        r = {k.strip(): (v or "").strip() for k, v in r.items() if k}
        key = (norm(r.get("act_id")), r.get("domain"))
        if key not in keys:
            problems.append(f"row {i}: ({r.get('act_id')!r}, {r.get('domain')!r}) is not an expected stack_B row")
            continue
        if key in got:
            problems.append(f"row {i}: duplicate row for {key}")
            continue
        if r.get("stack") not in STACK:
            problems.append(f"row {i} {key}: stack {r.get('stack')!r} not in the closed list")
        got[key] = r
    problems += [f"missing stack_B row {k}" for k in keys if k not in got]
    return got, problems


def load_access(path, meta):
    return L1.load_access(path, meta)


def ratio(nb, nx):
    """R = nb / nx with the L1 review's interval: Wilson [lo, hi] on nb / (nb + nx), mapped to lo/(1-lo), hi/(1-hi)."""
    if nx == 0:
        return {"R": math.inf if nb else None, "lo": None, "hi": None, "N_num": nb, "N_den": nx}
    w = wilson(nb, nb + nx)
    m = lambda p: math.inf if p >= 1 else p / (1 - p)
    return {"R": nb / nx, "lo": m(w["lo"]), "hi": m(w["hi"]), "N_num": nb, "N_den": nx}


def fisher_greater(k1, n1, k2, n2):
    """One-sided Fisher exact p for 'share 1 > share 2' on [[k1, n1-k1], [k2, n2-k2]]."""
    if n1 == 0 or n2 == 0:
        return None
    N, K = n1 + n2, k1 + k2
    c = math.comb
    tot = c(N, n1)
    return sum(c(K, x) * c(N - K, n1 - x) for x in range(k1, min(K, n1) + 1)) / tot


def cons_stack(sa, sb):
    """Conservative stack: 'yes' only when both raters say yes; None (not judged) when either says cannot judge."""
    if sa not in ("yes", "no") or sb not in ("yes", "no"):
        return None
    return "yes" if sa == sb == "yes" else "no"


def calibration_reference(l1dir, l1meta_path):
    """N_S1 and E_S1 from L1's committed files, with L1's own functions: L1 primary matched domain-S pairs from
    non-vehicle-level seed instruments (V1 readout's S, which drops the vehicle-level events)."""
    meta = L1.instruments(l1meta_path)
    A, _ = L1.load_ledger(os.path.join(l1dir, "ledger_A.csv"), meta)
    B, _ = L1.load_ledger(os.path.join(l1dir, "ledger_B.csv"), meta)
    accA, _ = L1.load_access(os.path.join(l1dir, "instruments_A.csv"), meta)
    accB, _ = L1.load_access(os.path.join(l1dir, "instruments_B.csv"), meta)
    blocked = {i for i in meta if accA.get(i) == "none" and accB.get(i) == "none"}
    seed = {i for i, m in meta.items() if m["seed"]}
    pairs, ua, ub = L1.match(A, B)
    r = L1.readout(pairs, ua, ub, meta, seed, "V1", blocked)
    sp = [(a, b) for a, b, _ in r["_pairs"] if meta[a["instrument_id"]]["domain"] == "S"
          and not meta[a["instrument_id"]]["vehicle_level"]]
    assert len(sp) == r["N_S"]
    E = [{"instrument_id": a["instrument_id"], "keys": sorted({norm(a["act_id"]), norm(b["act_id"])} - {""})} for a, b in sp]
    return len(sp), E


def calibrate(n_s_spec, s_pairs, N_S1, E_S1):
    new = set()
    for a, b in s_pairs:
        new |= {norm(a["act_id"]), norm(b["act_id"])} - {""}
    covered = [e for e in E_S1 if set(e["keys"]) & new]
    ok_count = abs(n_s_spec - N_S1) <= CAL_COUNT
    ok_acts = len(covered) >= CAL_ACTS
    return {"N_S_specific": n_s_spec, "N_S1": N_S1, "abs_diff": abs(n_s_spec - N_S1), "count_ok": ok_count,
            "E_S1_size": len(E_S1), "E_S1_covered": len(covered), "acts_ok": ok_acts,
            "status": "CALIBRATED" if ok_count and ok_acts else "MISCALIBRATED",
            "E_S1_not_covered": [e for e in E_S1 if e not in covered]}


def ev(r):
    return {k: r.get(k) for k in ("event_id", "instrument_id", "domain", "act_id", "adoption_date", "application_date",
                                  "class", "stack", "confidence", "what_changed", "source_url")}


def readout(pairs, ua, ub, meta, insts, vl_mode, blocked, bev, sbA, sbB):
    """Counts and stack readouts. vl_mode: 'V2' (vehicle-level events in B, S and L), 'V1' (B only), 'V0' (none).
    `blocked`: instruments `none` for both raters (no events, out of the gates). `insts`: the S and L instruments."""
    keep = lambda r: r["instrument_id"] in insts and r["instrument_id"] not in blocked
    P = [(a, b, how) for a, b, how in pairs if keep(a) and in_window(a["_adopt"]) and in_window(b["_adopt"])]
    straddle = [(a, b) for a, b, _ in pairs if keep(a) and (in_window(a["_adopt"]) != in_window(b["_adopt"]))]
    UA = [r for r in ua if keep(r) and in_window(r["_adopt"])]
    UB = [r for r in ub if keep(r) and in_window(r["_adopt"])]
    M, nA, nB = len(P), len(P) + len(UA), len(P) + len(UB)
    vl = [e for e in bev if e["_vl"]]
    b_spec = [e for e in bev if not e["_vl"]]
    if "CN0" in vl_mode:
        vl = [e for e in vl if not e["_china"]]
        b_spec = [e for e in b_spec if not e["_china"]]
    mode = vl_mode.split("+")[0]

    res = {"M": M, "n_A": nA, "n_B": nB, "identification": (M / (nA + nB - M)) if nA + nB - M else None,
           "kappa_class": kappa([(a["class"], b["class"]) for a, b, _ in P]),
           "matched_by": dict(Counter(h for _, _, h in P)), "window_straddling_pairs": len(straddle)}
    # kappa on stack: matched S and L pairs plus the 51 stack_B rows rated by both
    sb_pairs = [(sbA[k]["stack"], sbB[k]["stack"]) for k in sbA if k in sbB]
    res["kappa_stack"] = kappa([(a.get("stack"), b.get("stack")) for a, b, _ in P] + sb_pairs)
    res["kappa_stack_SL_only"] = kappa([(a.get("stack"), b.get("stack")) for a, b, _ in P])
    res["kappa_stack_B_rows_only"] = kappa(sb_pairs)

    n_vl = 0 if mode == "V0" else len(vl)
    res["N_B"] = len(b_spec) + n_vl
    for d in "SL":
        dp = [(a, b) for a, b, _ in P if meta[a["instrument_id"]]["domain"] == d]
        cls = [L1.cons_class(a, b) for a, b in dp]
        judged = [c for c in cls if c is not None]
        res[f"N_{d}_specific"] = len(dp)
        res[f"N_{d}"] = len(dp) + (n_vl if mode == "V2" else 0)
        res[f"MC_{d}"] = wilson(sum(ORDER[c] >= 1 for c in judged), len(judged))
        res[f"H_{d}"] = wilson(sum(ORDER[c] == 2 for c in judged), len(judged))
        res[f"cannot_judge_class_{d}"] = len(cls) - len(judged)
        res[f"class_{d}"] = dict(Counter(c or "cannot judge (either rater)" for c in cls))
        res[f"per_year_adoption_{d}"] = {y: sum(min(a["_adopt"], b["_adopt"]).year == y for a, b in dp) for y in range(2016, 2027)}
        res[f"per_year_application_{d}"] = dict(sorted(Counter(min(a["_apply"], b["_apply"]).year for a, b in dp).items()))
        res[f"by_instrument_{d}"] = dict(sorted(Counter(a["instrument_id"] for a, b in dp).items()))
        res[f"union_{d}"] = res[f"N_{d}"] + sum(1 for r in UA + UB if meta[r["instrument_id"]]["domain"] == d)
        st = [cons_stack(a.get("stack"), b.get("stack")) for a, b in dp]
        js = [s for s in st if s is not None]
        res[f"stack_{d}"] = {"k": sum(s == "yes" for s in js), "n_judged": len(js), "n_events": len(dp),
                             "share": wilson(sum(s == "yes" for s in js), len(js)),
                             "not_judged": [{"A": ev(a), "B": ev(b)} for (a, b), s in zip(dp, st) if s is None]}
    res["per_year_adoption_B"] = {y: sum(e["_adopt"].year == y for e in b_spec + (vl if n_vl else []))
                                  for y in range(2016, 2027)}
    # domain B stack on the specific (non-vehicle-level) events, from stack_B rows with domain B
    sb = []
    for e in b_spec:
        k = (norm(e["act_id"]), "B")
        sb.append((e, cons_stack(sbA.get(k, {}).get("stack"), sbB.get(k, {}).get("stack"))))
    js = [s for _, s in sb if s is not None]
    res["stack_B"] = {"k": sum(s == "yes" for s in js), "n_judged": len(js), "n_events": len(sb),
                      "share": wilson(sum(s == "yes" for s in js), len(js)),
                      "not_judged": [{"instrument_id": e["instrument_id"], "act_id": e["act_id"],
                                      "A": sbA.get((norm(e["act_id"]), "B"), {}).get("stack"),
                                      "B": sbB.get((norm(e["act_id"]), "B"), {}).get("stack")} for e, s in sb if s is None]}
    # vehicle-level stack counts per domain (reported separately, not in k_d)
    res["stack_vehicle_level"] = {}
    for d in "BSL":
        s = [cons_stack(sbA.get((norm(e["act_id"]), d), {}).get("stack"), sbB.get((norm(e["act_id"]), d), {}).get("stack"))
             for e in vl]
        res["stack_vehicle_level"][d] = {"k": sum(x == "yes" for x in s), "n_judged": sum(x is not None for x in s),
                                         "n_events": len(s)}
    kB, nBj = res["stack_B"]["k"], res["stack_B"]["n_judged"]
    kL, nLj = res["stack_L"]["k"], res["stack_L"]["n_judged"]
    res["fisher_B_gt_L_one_sided_p"] = fisher_greater(kB, nBj, kL, nLj)
    res["R_BL"] = ratio(res["N_B"], res["N_L"])
    res["R_BS"] = ratio(res["N_B"], res["N_S"])
    res["by_jurisdiction_SL"] = dict(Counter("China" if meta[a["instrument_id"]]["china"] else "non-China" for a, _, _ in P))
    res["_pairs"], res["_UA"], res["_UB"], res["_straddle"] = P, UA, UB, straddle
    return res


def gates(r):
    g = {"identification": r["identification"], "kappa_class": r["kappa_class"]["kappa"],
         "kappa_stack": r["kappa_stack"]["kappa"]}
    ok = {"identification": g["identification"] is not None and g["identification"] >= 0.80,
          "kappa_class": g["kappa_class"] is not None and g["kappa_class"] >= 0.60,
          "kappa_stack": g["kappa_stack"] is not None and g["kappa_stack"] >= 0.60}
    return {"values": g, "pass": ok, "all_pass": all(ok.values())}


def decide_count(r, g, limited_L):
    """§5 count table with the access qualifier: with L limited, N_L is a lower bound and R_BL an upper bound."""
    if not g["all_pass"]:
        return "UNGATED", []
    R, lo = r["R_BL"]["R"], r["R_BL"]["lo"]
    notes = []
    if R is not None and R >= 3 and lo is not None and lo > 1.5:
        if limited_L:
            notes.append("R_BL >= 3 with lower bound > 1.5, but R_BL is an upper bound (L access-limited)")
            v = "UNCLEAR BY COUNT"
        else:
            v = "SPECIFIC BY COUNT"
    elif R is not None and R < 1.5:
        v = "NOT SPECIFIC BY COUNT"
    else:
        v = "UNCLEAR BY COUNT"
    if limited_L:
        v += " (ACCESS-LIMITED: L)"
    return v, notes


def decide_kind(r, g):
    """§5 kind table, checked in order, with L1B-D1 (share clause only when n_L >= 10)."""
    if not g["all_pass"]:
        return "UNGATED", []
    kB, nB = r["stack_B"]["k"], r["stack_B"]["n_judged"]
    kL, nL = r["stack_L"]["k"], r["stack_L"]["n_judged"]
    kS = r["stack_S"]["k"]
    specific = kB >= 3 and kL <= 1 and kS <= 1
    share_clause = nL >= D1_MIN_NL and nB > 0 and kL / nL >= kB / nB
    not_specific = kL >= 2 or share_clause
    notes = []
    if nL > 0 and nL < D1_MIN_NL and nB > 0 and kL / nL >= kB / nB:
        notes.append(f"L1B-D1: share k_L/n_L = {kL}/{nL} >= k_B/n_B = {kB}/{nB}, but n_L < {D1_MIN_NL}: share clause not applied")
    if specific and not_specific:
        notes.append("both STACK-SPECIFIC and NOT STACK-SPECIFIC conditions hold; table order gives STACK-SPECIFIC (§5)")
    if specific:
        return "STACK-SPECIFIC", notes
    if not_specific:
        return "NOT STACK-SPECIFIC", notes
    return "UNCLEAR IN KIND", notes


def strip(r):
    return {k: v for k, v in r.items() if not k.startswith("_")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="results/L1B")
    ap.add_argument("--l1dir", default="results/L1")
    ap.add_argument("--meta", default="results/L1B/L1B_instruments.md")
    ap.add_argument("--l1meta", default="results/L1/L1_instruments.md")
    ap.add_argument("--out", default="l1b.json")
    a = ap.parse_args()
    meta = instruments(a.meta)
    l1meta = L1.instruments(a.l1meta)
    bev = load_b_events(os.path.join(a.dir, "B_events.csv"), l1meta)
    keys = stack_b_keys(bev)
    A, pa = load_ledger(os.path.join(a.dir, "ledger_A.csv"), meta)
    B, pb = load_ledger(os.path.join(a.dir, "ledger_B.csv"), meta)
    sbA, sa = load_stack_b(os.path.join(a.dir, "stack_B_A.csv"), keys)
    sbB, sb = load_stack_b(os.path.join(a.dir, "stack_B_B.csv"), keys)
    accA, qa = load_access(os.path.join(a.dir, "instruments_A.csv"), meta)
    accB, qb = load_access(os.path.join(a.dir, "instruments_B.csv"), meta)
    problems = {"ledger_A": pa, "ledger_B": pb, "stack_B_A": sa, "stack_B_B": sb, "instruments_A": qa, "instruments_B": qb}
    if any(problems.values()):
        print("VALIDATION PROBLEMS:", json.dumps(problems, indent=1))

    both_none = {i for i in meta if accA.get(i) == "none" and accB.get(i) == "none"}
    seed = {i for i, m in meta.items() if m["seed"]}
    seedL = sorted(i for i in seed if meta[i]["domain"] == "L")
    seedS = sorted(i for i in seed if meta[i]["domain"] == "S")
    unread_L, unread_S = sorted(set(seedL) & both_none), sorted(set(seedS) & both_none)
    limited_L, limited_S = len(unread_L) >= L_LIMIT, len(unread_S) >= S_LIMIT

    N_S1, E_S1 = calibration_reference(a.l1dir, a.l1meta)
    pairs, ua, ub = L1.match(A, B)
    acc_ok = {i for i in meta if accA.get(i) in ("full", "partial") and accB.get(i) in ("full", "partial")}
    china = {i for i, m in meta.items() if m["china"]}
    variants = {
        "primary_V2": (seed, "V2"),
        "V1": (seed, "V1"),
        "V0": (seed, "V0"),
        "CN0": (seed - china, "V2+CN0"),
        "FULL": (set(meta), "V2"),
        "ACC": (seed & acc_ok, "V2"),
    }
    out = {"preregistration": "results/L1B/L1B_preregistration.md (7c3896c; approved with L1B-D1, b56f1b4)",
           "tags": "events SOURCED; classes and stack DERIVED-judgemental; both raters are language-model sessions",
           "validation_problems": problems,
           "access": {"A": accA, "B": accB,
                      "counts": {d: {f"{x}/{y}": sum(1 for i in ids if accA.get(i) == x and accB.get(i) == y)
                                     for x in L1.ACCESS for y in L1.ACCESS}
                                 for d, ids in (("L_seed", seedL), ("S_seed", seedS))},
                      "unread_L_seed": unread_L, "unread_S_seed": unread_S,
                      "limited_L": limited_L, "limited_S": limited_S,
                      "thresholds": {"L": f">= {L_LIMIT} of {L_SEEDS}", "S": f">= {S_LIMIT} of {S_SEEDS}"}},
           "ledger_sizes_raw": {"A": len(A), "B": len(B)},
           "stack_B_rows": {"expected": len(keys), "A": len(sbA), "B": len(sbB), "both": sum(k in sbB for k in sbA)}}
    for name, (insts, mode) in variants.items():
        r = readout(pairs, ua, ub, meta, insts, mode, both_none, bev, sbA, sbB)
        g = gates(r)
        lim = limited_L if name != "ACC" else False
        vc, nc = decide_count(r, g, lim)
        vk, nk = decide_kind(r, g)
        r.update(gates=g, verdict_count=vc, verdict_kind=vk, decision_notes_count=nc, decision_notes_kind=nk)
        if name == "primary_V2":
            r["calibration"] = calibrate(r["N_S_specific"], [(x, y) for x, y, _ in r["_pairs"]
                                                            if meta[x["instrument_id"]]["domain"] == "S"], N_S1, E_S1)
            r["unmatched_A"] = [ev(x) for x in r["_UA"]]
            r["unmatched_B"] = [ev(x) for x in r["_UB"]]
            r["class_disagreements"] = [{"A": ev(x), "B": ev(y)} for x, y, _ in r["_pairs"] if x["class"] != y["class"]]
            r["stack_disagreements_SL"] = [{"A": ev(x), "B": ev(y)} for x, y, _ in r["_pairs"]
                                           if x.get("stack") != y.get("stack")]
            r["window_straddling"] = [{"A": ev(x), "B": ev(y)} for x, y in r["_straddle"]]
        out[name] = strip(r)
    out["stack_disagreements_B_rows"] = [{"act_id": sbA[k].get("act_id"), "domain": k[1], "A": sbA[k]["stack"],
                                          "B": sbB[k]["stack"], "A_note": sbA[k].get("note"), "B_note": sbB[k].get("note")}
                                         for k in keys if k in sbA and k in sbB and sbA[k]["stack"] != sbB[k]["stack"]]
    for R_, X, SB in (("A", A, sbA), ("B", B, sbB)):
        own = {}
        for d in "SL":
            rows = [x for x in X if in_window(x["_adopt"]) and x["instrument_id"] in seed and meta[x["instrument_id"]]["domain"] == d]
            judged = [x["class"] for x in rows if x["class"] in ORDER]
            own[d] = {"n": len(rows), "MC": wilson(sum(ORDER[c] >= 1 for c in judged), len(judged)),
                      "H": wilson(sum(ORDER[c] == 2 for c in judged), len(judged)),
                      "class": dict(Counter(x["class"] for x in rows)), "stack": dict(Counter(x.get("stack") for x in rows))}
        own["stack_B_rows"] = {d: dict(Counter(v["stack"] for k, v in SB.items() if k[1] == d)) for d in "BSL"}
        out.setdefault("own", {})[R_] = own
    p = out["primary_V2"]
    cal = p["calibration"]["status"]
    out["verdict_line"] = {"count": p["verdict_count"], "kind": p["verdict_kind"], "calibration": cal,
                           "sensitivities_differing": {k: {"count": out[k]["verdict_count"], "kind": out[k]["verdict_kind"]}
                                                       for k in ("V1", "V0", "CN0", "FULL", "ACC")
                                                       if (out[k]["verdict_count"], out[k]["verdict_kind"]) != (p["verdict_count"], p["verdict_kind"])}}
    json.dump(out, open(os.path.join(a.dir, a.out), "w"), indent=1, default=str)

    f = lambda w: f"{w['k']}/{w['n']} = {100 * w['p']:.1f} % [{100 * w['lo']:.1f}, {100 * w['hi']:.1f}]" if w["n"] else "n = 0"
    fr = lambda x: f"{x['R']:.2f} [{x['lo']:.2f}, {x['hi']:.2f}]" if x["lo"] is not None else f"{x['R']}"
    print(f"count: {p['verdict_count']} | kind: {p['verdict_kind']} | calibration: {cal}")
    for n in p["decision_notes_count"] + p["decision_notes_kind"]:
        print(f"  note: {n}")
    g = p["gates"]["values"]
    print(f"gates: identification {g['identification']} (M {p['M']}, n_A {p['n_A']}, n_B {p['n_B']}); "
          f"kappa class {g['kappa_class']} (n {p['kappa_class']['n']}); kappa stack {g['kappa_stack']} (n {p['kappa_stack']['n']})")
    c = p["calibration"]
    print(f"calibration: N_S,specific {c['N_S_specific']} vs N_S1 {c['N_S1']} (diff {c['abs_diff']}); E_S1 covered {c['E_S1_covered']}/{c['E_S1_size']}")
    print(f"N_B {p['N_B']}  N_L {p['N_L']}  N_S {p['N_S']}  R_BL {fr(p['R_BL'])}  R_BS {fr(p['R_BS'])}")
    print(f"stack: B {f(p['stack_B']['share'])}  L {f(p['stack_L']['share'])}  S {f(p['stack_S']['share'])}  "
          f"Fisher B>L p {p['fisher_B_gt_L_one_sided_p']}")
    print(f"unread seeds: L {len(unread_L)} {unread_L}; S {len(unread_S)} {unread_S}")
    for k in ("V1", "V0", "CN0", "FULL", "ACC"):
        q = out[k]
        print(f"  {k}: {q['verdict_count']} / {q['verdict_kind']}; N_B {q['N_B']} N_L {q['N_L']} N_S {q['N_S']} R_BL {fr(q['R_BL'])}")


if __name__ == "__main__":
    main()
