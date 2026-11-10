"""L1 agreement analysis: implements results/L1/L1_preregistration.md §5-§6 with deviations L-1, L-2 and L-4 (§9).

Inputs (in --dir, default results/L1): ledger_A.csv, ledger_B.csv, instruments_A.csv, instruments_B.csv; instrument
metadata from results/L1/L1_instruments.md §1. Output: <dir>/l1.json (--out).

Written and committed before either rater branch existed or was fetched; exercised on the synthetic ledgers in
analysis/L1_selftest/. Run from the repository root:  python3 -I analysis/L1_agreement.py [--dir D] [--out F]
"""
import argparse
import csv
import json
import math
import os
import re
from collections import Counter, defaultdict
from datetime import date

CLASSES = ["software-only", "memory-or-crypto", "hardware-or-recert", "cannot judge"]
ORDER = {"software-only": 0, "memory-or-crypto": 1, "hardware-or-recert": 2}
ACCESS = ["full", "partial", "none"]
VEHICLE_LEVEL = {"B05", "B06", "B14", "B15"}  # UN R155, UN R156, GB 44495, GB 44496 (pre-registration §1, L-1)
WINDOW = (date(2016, 1, 1), date(2026, 12, 31))
YEARS = 11
Z = 1.96


def wilson(k, n):
    if n == 0:
        return {"k": 0, "n": 0, "p": None, "lo": None, "hi": None}
    p = k / n
    d = 1 + Z * Z / n
    c = (p + Z * Z / (2 * n)) / d
    h = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n)) / d
    return {"k": k, "n": n, "p": p, "lo": c - h, "hi": c + h}


def kappa(pairs):
    n = len(pairs)
    if n == 0:
        return {"kappa": None, "n": 0, "observed_agreement": None}
    po = sum(a == b for a, b in pairs) / n
    ca, cb = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / (n * n)
    return {"kappa": None if pe == 1 else (po - pe) / (1 - pe), "n": n, "observed_agreement": po}


def instruments(path="results/L1/L1_instruments.md"):
    sec = open(path).read().split("## 1. Instruments")[1].split("\n## ")[0]
    meta = {}
    for line in sec.splitlines():
        m = re.match(r"^\| ([BS]\d{2}) \| ([BS]) \|", line)
        if m:
            meta[m.group(1)] = {"domain": m.group(2), "seed": "| seed |" in line, "china": "| China |" in line,
                                "vehicle_level": m.group(1) in VEHICLE_LEVEL}
    assert len(meta) == 63 and sum(v["seed"] for v in meta.values()) == 51
    assert all(meta[i]["seed"] for i in VEHICLE_LEVEL)
    return meta


def pdate(s):
    s = (s or "").strip()
    try:
        return date.fromisoformat(s[:10])
    except ValueError:
        return None


def norm(act):
    return re.sub(r"[\s\W_]+", "", (act or "").lower())


def load_ledger(path, meta):
    rows, problems = [], []
    for i, r in enumerate(csv.DictReader(open(path, newline=""))):
        r = {k.strip(): (v or "").strip() for k, v in r.items() if k}
        r["_i"] = i
        r["_adopt"] = pdate(r.get("adoption_date"))
        r["_apply"] = pdate(r.get("application_date")) or r["_adopt"]
        if r.get("instrument_id") not in meta:
            problems.append(f"row {i}: instrument_id {r.get('instrument_id')!r} not in the list")
            continue
        if r.get("class") not in CLASSES:
            problems.append(f"row {i} ({r['instrument_id']}): class {r.get('class')!r} not in the closed list")
        if r["_adopt"] is None:
            problems.append(f"row {i} ({r['instrument_id']}): adoption_date {r.get('adoption_date')!r} unreadable")
            continue
        rows.append(r)
    return rows, problems


def load_access(path, meta):
    acc, problems = {}, []
    for r in csv.DictReader(open(path, newline="")):
        r = {k.strip(): (v or "").strip() for k, v in r.items() if k}
        if r.get("instrument_id") in meta:
            if r.get("history_access") not in ACCESS:
                problems.append(f"{r['instrument_id']}: history_access {r.get('history_access')!r}")
            acc[r["instrument_id"]] = r.get("history_access")
    problems += [f"{i}: no access row" for i in meta if i not in acc]
    return acc, problems


def in_window(d):
    return d is not None and WINDOW[0] <= d <= WINDOW[1]


def match(A, B):
    """L-4: within instrument_id, pass 1 identical normalised act_id, pass 2 adoption dates within +-90 days."""
    pairs, ua, ub = [], [], []
    by = defaultdict(lambda: ([], []))
    for r in A:
        by[r["instrument_id"]][0].append(r)
    for r in B:
        by[r["instrument_id"]][1].append(r)
    for inst, (ea, eb) in sorted(by.items()):
        ra, rb = list(ea), list(eb)
        for a in list(ra):  # pass 1, in A's ledger order
            k = norm(a.get("act_id"))
            if not k:
                continue
            for b in rb:
                if norm(b.get("act_id")) == k:
                    pairs.append((a, b, "act_id"))
                    ra.remove(a)
                    rb.remove(b)
                    break
        cand = sorted(((abs((a["_adopt"] - b["_adopt"]).days), a["_i"], b["_i"], a, b) for a in ra for b in rb
                       if abs((a["_adopt"] - b["_adopt"]).days) <= 90), key=lambda x: x[:3])
        usedA, usedB = set(), set()
        for _, ia, ib, a, b in cand:  # pass 2: closest first, ties by A's then B's ledger order
            if ia in usedA or ib in usedB:
                continue
            usedA.add(ia)
            usedB.add(ib)
            pairs.append((a, b, "date"))
        ua += [a for a in ra if a["_i"] not in usedA]
        ub += [b for b in rb if b["_i"] not in usedB]
    return pairs, ua, ub


def cons_class(a, b):
    ca, cb = a["class"], b["class"]
    if ca not in ORDER or cb not in ORDER:
        return None
    return ca if ORDER[ca] <= ORDER[cb] else cb


def pair_dates(a, b):
    return min(a["_adopt"], b["_adopt"]), min(a["_apply"], b["_apply"])


def readout(pairs, ua, ub, meta, insts, vl_mode, blocked):
    """Counts on the matched pairs of instruments `insts`. vl_mode: 'V2' (vehicle-level in B and S), 'V1' (B only),
    'V0' (neither). `blocked`: instruments with history_access none from both raters (no events, out of the gates)."""
    keep = lambda r: r["instrument_id"] in insts and r["instrument_id"] not in blocked
    P = [(a, b, how) for a, b, how in pairs if keep(a) and in_window(a["_adopt"]) and in_window(b["_adopt"])]
    straddle = [(a, b) for a, b, _ in pairs if keep(a) and (in_window(a["_adopt"]) != in_window(b["_adopt"]))]
    UA = [r for r in ua if keep(r) and in_window(r["_adopt"])]
    UB = [r for r in ub if keep(r) and in_window(r["_adopt"])]
    M, nA, nB = len(P), len(P) + len(UA), len(P) + len(UB)

    def dom_pairs(d):
        out = []
        for a, b, how in P:
            m = meta[a["instrument_id"]]
            if m["vehicle_level"]:
                if vl_mode == "V0":
                    continue
                if d == "B" or (d == "S" and vl_mode == "V2"):
                    out.append((a, b))
            elif m["domain"] == d:
                out.append((a, b))
        return out

    res = {"M": M, "n_A": nA, "n_B": nB, "identification": (M / (nA + nB - M)) if nA + nB - M else None,
           "kappa": kappa([(a["class"], b["class"]) for a, b, _ in P]),
           "matched_by": dict(Counter(h for _, _, h in P)), "window_straddling_pairs": len(straddle)}
    for d in "BS":
        dp = dom_pairs(d)
        cls = [cons_class(a, b) for a, b in dp]
        judged = [c for c in cls if c is not None]
        res[f"N_{d}"] = len(dp)
        res[f"MC_{d}"] = wilson(sum(ORDER[c] >= 1 for c in judged), len(judged))
        res[f"H_{d}"] = wilson(sum(ORDER[c] == 2 for c in judged), len(judged))
        res[f"cannot_judge_{d}"] = len(cls) - len(judged)
        res[f"class_{d}"] = dict(Counter(c or "cannot judge (either rater)" for c in cls))
        res[f"per_year_adoption_{d}"] = {y: sum(pair_dates(a, b)[0].year == y for a, b in dp) for y in range(2016, 2027)}
        res[f"per_year_application_{d}"] = dict(sorted(Counter(pair_dates(a, b)[1].year for a, b in dp).items()))
        res[f"by_instrument_{d}"] = dict(sorted(Counter(a["instrument_id"] for a, b in dp).items()))
        res[f"union_{d}"] = len(dp) + sum(1 for r in UA + UB if meta[r["instrument_id"]]["domain"] == d
                                          or (d == "S" and vl_mode == "V2" and meta[r["instrument_id"]]["vehicle_level"]))
    nb, ns = res["N_B"], res["N_S"]
    res["R"] = (nb / ns) if ns else (math.inf if nb else None)
    res["by_jurisdiction"] = dict(Counter("China" if meta[a["instrument_id"]]["china"] else "non-China" for a, _, _ in P))
    res["_pairs"], res["_UA"], res["_UB"], res["_straddle"] = P, UA, UB, straddle
    return res


def decide(r, limited_B, limited_S):
    """Pre-registration §6 with L-2's bound logic. Returns (verdict, kill, notes)."""
    if r["identification"] is None or r["identification"] < 0.80 or r["kappa"]["kappa"] is None or r["kappa"]["kappa"] < 0.60:
        return "UNGATED", None, []
    nb, R, mc = r["N_B"], r["R"], r["MC_B"]
    mc_ok = mc["p"] is not None and mc["p"] >= 0.25 and mc["lo"] > 0.10
    mc_low = mc["p"] is not None and mc["p"] < 0.10
    can_R_ge3 = not limited_S          # with S limited, R is an upper bound
    can_R_lt15 = not limited_B         # with B limited, R is a lower bound
    can_count_low = not limited_B      # with B limited, N_B is a lower bound
    notes = []
    volatile_raw = nb >= 11 and mc_ok and R is not None and R >= 3
    if volatile_raw and can_R_ge3:
        v = "VOLATILE DOMAIN"
    else:
        if volatile_raw:
            notes.append("VOLATILE conditions met but R >= 3 cannot be established with S access-limited")
        stable_count = nb <= 5
        if stable_count and not can_count_low:
            notes.append("N_B <= 5 but N_B is a lower bound (B access-limited): STABLE by count cannot fire")
        if (stable_count and can_count_low) or mc_low:
            v = "STABLE DOMAIN"
        else:
            v = "UNCLEAR"
    kill_R = R is not None and R < 1.5
    if kill_R and not can_R_lt15:
        notes.append("R < 1.5 but R is a lower bound (B access-limited): the kill on R cannot fire")
    kill = v == "STABLE DOMAIN" or (kill_R and can_R_lt15)
    if limited_B or limited_S:
        q = ", ".join(x for x, f in (("B", limited_B), ("S", limited_S)) if f)
        v = f"{v} (ACCESS-LIMITED: {q})"
    return v, kill, notes


def strip(r):
    return {k: v for k, v in r.items() if not k.startswith("_")}


def ev(r):
    return {k: r.get(k) for k in ("event_id", "instrument_id", "act_id", "adoption_date", "application_date", "class",
                                  "confidence", "what_changed", "source_url")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="results/L1")
    ap.add_argument("--out", default="l1.json")
    a = ap.parse_args()
    meta = instruments()
    A, pa = load_ledger(os.path.join(a.dir, "ledger_A.csv"), meta)
    B, pb = load_ledger(os.path.join(a.dir, "ledger_B.csv"), meta)
    accA, qa = load_access(os.path.join(a.dir, "instruments_A.csv"), meta)
    accB, qb = load_access(os.path.join(a.dir, "instruments_B.csv"), meta)
    problems = {"ledger_A": pa, "ledger_B": pb, "instruments_A": qa, "instruments_B": qb}
    if any(problems.values()):
        print("VALIDATION PROBLEMS:", json.dumps(problems, indent=1))

    both_none = {i for i in meta if accA.get(i) == "none" and accB.get(i) == "none"}
    seed = {i for i, m in meta.items() if m["seed"]}
    seedB = sorted(i for i in seed if meta[i]["domain"] == "B")
    seedS = sorted(i for i in seed if meta[i]["domain"] == "S")
    unread_B = sorted(set(seedB) & both_none)
    unread_S = sorted(set(seedS) & both_none)
    limited_B, limited_S = len(unread_B) >= 12, len(unread_S) >= 6
    assert len(seedB) == 35 and len(seedS) == 16

    pairs, ua, ub = match(A, B)
    acc_ok = {i for i in meta if accA.get(i) in ("full", "partial") and accB.get(i) in ("full", "partial")}
    china = {i for i, m in meta.items() if m["china"]}
    variants = {
        "primary_V2": (seed, "V2"),
        "V1": (seed, "V1"),
        "V0": (seed, "V0"),
        "CN0": (seed - china, "V2"),
        "FULL": (set(meta), "V2"),
        "ACC": (seed & acc_ok, "V2"),
    }
    out = {"preregistration": "results/L1/L1_preregistration.md (af2d5cb; deviations L-1..L-5, e98f8b3)",
           "tags": "events SOURCED; classifications DERIVED-judgemental; both raters are language-model sessions",
           "validation_problems": problems,
           "access": {"A": accA, "B": accB,
                      "counts": {d: {f"{x}/{y}": sum(1 for i in ids if accA.get(i) == x and accB.get(i) == y)
                                     for x in ACCESS for y in ACCESS}
                                 for d, ids in (("B_seed", seedB), ("S_seed", seedS))},
                      "unread_B_seed": unread_B, "unread_S_seed": unread_S,
                      "limited_B": limited_B, "limited_S": limited_S},
           "ledger_sizes_raw": {"A": len(A), "B": len(B)}}
    for name, (insts, mode) in variants.items():
        r = readout(pairs, ua, ub, meta, insts, mode, both_none)
        lb = limited_B if name != "ACC" else False
        ls = limited_S if name != "ACC" else False
        v, kill, notes = decide(r, lb, ls)
        r.update(verdict=v, kill=kill, decision_notes=notes)
        if name == "primary_V2":
            r["unmatched_A"] = [ev(x) for x in r["_UA"]]
            r["unmatched_B"] = [ev(x) for x in r["_UB"]]
            r["class_disagreements"] = [{"A": ev(x), "B": ev(y)} for x, y, _ in r["_pairs"] if x["class"] != y["class"]]
            r["window_straddling"] = [{"A": ev(x), "B": ev(y)} for x, y in r["_straddle"]]
            # domain-S class fractions without the vehicle-level events (L-1, non-deciding)
            rs = readout(pairs, ua, ub, meta, seed, "V1", both_none)
            r["S_without_vehicle_level"] = {k: rs[k] for k in ("N_S", "MC_S", "H_S", "class_S")}
        out[name] = strip(r)
    for R_, X, acc in (("A", A, accA), ("B", B, accB)):
        own = {}
        for d in "BS":
            rows = [x for x in X if in_window(x["_adopt"]) and x["instrument_id"] in seed
                    and (meta[x["instrument_id"]]["domain"] == d)]
            judged = [x["class"] for x in rows if x["class"] in ORDER]
            own[d] = {"n": len(rows), "MC": wilson(sum(ORDER[c] >= 1 for c in judged), len(judged)),
                      "H": wilson(sum(ORDER[c] == 2 for c in judged), len(judged)), "class": dict(Counter(x["class"] for x in rows))}
        out.setdefault("own", {})[R_] = own
    p = out["primary_V2"]
    verdict_line = p["verdict"]
    extra = [f"{k}: {out[k]['verdict']}" for k in ("FULL", "V1") if out[k]["verdict"] != p["verdict"]]
    out["verdict_line"] = verdict_line + (" [" + "; ".join(extra) + "]" if extra else "")
    out["kill_line"] = {"primary": p["kill"], "V1": out["V1"]["kill"], "FULL": out["FULL"]["kill"]}
    json.dump(out, open(os.path.join(a.dir, a.out), "w"), indent=1, default=str)

    f = lambda w: f"{w['k']}/{w['n']} = {100 * w['p']:.1f} % [{100 * w['lo']:.1f}, {100 * w['hi']:.1f}]" if w["n"] else "n = 0"
    print("verdict:", out["verdict_line"], "| kill:", out["kill_line"])
    print(f"identification {p['identification']} (M {p['M']}, n_A {p['n_A']}, n_B {p['n_B']}); kappa {p['kappa']['kappa']} (n {p['kappa']['n']})")
    print(f"N_B {p['N_B']}  N_S {p['N_S']}  R {p['R']}  MC_B {f(p['MC_B'])}  H_B {f(p['H_B'])}")
    print(f"unread seeds: B {len(unread_B)} {unread_B}; S {len(unread_S)} {unread_S}")
    for k in ("V1", "V0", "CN0", "FULL", "ACC"):
        q = out[k]
        print(f"  {k}: {q['verdict']}; N_B {q['N_B']} N_S {q['N_S']} R {q['R']} MC_B {f(q['MC_B'])}")


if __name__ == "__main__":
    main()
