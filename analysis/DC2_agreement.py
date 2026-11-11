"""DC2 agreement analysis: implements results/DC2/DC2_preregistration.md §5-§6 with deviations DC2-1 and DC2-2 (§10).

Inputs (in --dir, default results/DC2): requirements_A.csv, requirements_B.csv, instruments_A.csv, instruments_B.csv;
instrument metadata from --list (default results/DC2/DC2_instruments.md §1). Output: <dir>/dc2.json (--out).

Written and committed before either rater branch existed; exercised on the synthetic files in analysis/DC2_selftest/.
Run from the repository root:  python3 -I analysis/DC2_agreement.py [--dir D] [--list L] [--out F]

Notes on the implementation (all from the pre-registration):
- shape is COMPUTED from each rater's window and allowance classes by the §2 table; the rater's written shape is only
  checked against it. DC2-2 conversions are made by the raters (allowance_class); rows whose note names DC2-2 are listed.
- primary = every listed instrument (the S3 and DC2-1 additions included, "FULL"); SEED drops them.
- the gates are computed once, over every instrument at least one rater could read, and apply to every variant.
"""
import argparse
import csv
import json
import math
import os
import re
from collections import Counter, defaultdict

WINDOWS = ["≤ 100 ms", "100 ms – 1 s", "1 – 60 s", "1 – 15 min", "> 15 min", "not stated"]
ALLOWANCES = ["hard", "tight", "loose", "very loose", "event count", "not stated"]
BINDING = ["mandatory", "planning level", "recommendation", "vendor capability"]
BINDS = {"mandatory", "planning level"}
QUANTITIES = ["ramp rate", "step change", "swing amplitude", "smoothing or capping response", "load change per interval",
              "flicker", "rapid voltage change", "harmonics", "power factor", "ride-through", "hold-up", "other"]
DECIDING_Q = set(QUANTITIES[:5])
POINTS = ["POI", "facility", "rack or row", "shelf or PSU", "device", "not stated"]
SHAPES = ["history", "reactive", "electronics", "cannot judge"]
ACCESS = ["full", "partial", "none"]
STATUS = ["in force", "pending", "no requirement"]
SEED_N, LIMIT_K = 50, 17  # §3b: access-limited when both raters record none for >= 17 of the 50 seeds
MIN_M1 = 10
UPSTREAM = {"POI", "facility"}
RACK = {"rack or row", "shelf or PSU", "device"}


def ckey(s):
    s = (s or "").strip().lower().replace("≤", "<=").replace("–", "-").replace("—", "-")
    return re.sub(r"\s+", "", s)


WIN_KEY = {ckey(w): w for w in WINDOWS}
WIN_KEY.update({"<=100ms": "≤ 100 ms", "100ms-1s": "100 ms – 1 s", "1-60s": "1 – 60 s", "1-15min": "1 – 15 min",
                ">15min": "> 15 min"})


def canon(v, allowed, extra=None):
    k = ckey(v)
    table = {ckey(a): a for a in allowed}
    if extra:
        table.update(extra)
    return table.get(k)


def shape_of(w, a):
    """§2 shape table (DC2-2 is applied by the raters, through allowance_class)."""
    if w in ("≤ 100 ms", "100 ms – 1 s"):
        return "electronics"
    if w in ("1 – 15 min", "> 15 min"):
        return "reactive"
    if w == "1 – 60 s":
        if a in ("hard", "tight"):
            return "reactive"
        if a in ("loose", "very loose"):
            return "history"
    return "cannot judge"


def kappa(pairs):
    n = len(pairs)
    if n == 0:
        return {"kappa": None, "n": 0, "observed_agreement": None}
    po = sum(a == b for a, b in pairs) / n
    ca, cb = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / (n * n)
    return {"kappa": None if pe == 1 else (po - pe) / (1 - pe), "n": n, "observed_agreement": po}


def instruments(path):
    sec = open(path).read().split("## 1. Instruments")[1].split("\n## ")[0]
    meta = {}
    for line in sec.splitlines():
        m = re.match(r"^\| ([GUEQVX]\d{2}) \| ([GUEQVX]) \|", line)
        if m:
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            body = re.split(r"\s*[(;/]", cells[4])[0].strip()
            body = "D-A-CH-CZ" if body.startswith("D-A-CH-CZ") else body
            meta[m.group(1)] = {"group": m.group(2), "seed": cells[11].startswith("seed"), "identifier": cells[2],
                                "body": body}
    assert sum(v["seed"] for v in meta.values()) == SEED_N, "seed count is not 50"
    return meta


def norm_clause(s):
    s = (s or "").lower().replace("§", " ")
    s = re.sub(r"\b(section|clause|paragraph|table|annex|article|art)\b", " ", s)
    return re.sub(r"[\W_]+", "", s)


def load_reqs(path, meta, who):
    rows, problems = [], []
    for i, r in enumerate(csv.DictReader(open(path, newline="", encoding="utf-8"))):
        r = {k.strip(): (v or "").strip() for k, v in r.items() if k}
        r["_i"], r["_who"] = i, who
        if r.get("instrument_id") not in meta:
            problems.append(f"row {i} {r.get('req_id')}: instrument_id {r.get('instrument_id')!r} not in the list")
            continue
        r["_w"] = canon(r.get("window_class"), WINDOWS, WIN_KEY)
        r["_a"] = canon(r.get("allowance_class"), ALLOWANCES)
        r["_b"] = canon(r.get("binding_class"), BINDING)
        r["_q"] = canon(r.get("quantity"), QUANTITIES)
        r["_p"] = canon(r.get("measurement_point"), POINTS, {"poi": "POI"})
        r["_d"] = ckey(r.get("deciding")) == "yes"
        r["_s_written"] = canon(r.get("shape"), SHAPES)
        for f, k in (("window_class", "_w"), ("allowance_class", "_a"), ("binding_class", "_b"), ("quantity", "_q"),
                     ("measurement_point", "_p"), ("shape", "_s_written")):
            if r[k] is None:
                problems.append(f"row {i} {r.get('req_id')}: {f} {r.get(f)!r} not in the closed list")
        if ckey(r.get("deciding")) not in ("yes", "no"):
            problems.append(f"row {i} {r.get('req_id')}: deciding {r.get('deciding')!r} is not yes/no")
        r["_s"] = shape_of(r["_w"], r["_a"])
        r["_unit"] = (r.get("window_as_printed") or "").lower().startswith("unit:")
        r["_c"], r["_cat"] = norm_clause(r.get("clause")), norm_clause(r.get("category"))
        rows.append(r)
    return rows, problems


def load_access(path, meta):
    acc, status, problems = {}, {}, []
    for r in csv.DictReader(open(path, newline="", encoding="utf-8")):
        r = {k.strip(): (v or "").strip() for k, v in r.items() if k}
        i = r.get("instrument_id")
        if i not in meta:
            problems.append(f"instrument_id {i!r} not in the list")
            continue
        a, s = canon(r.get("access"), ACCESS), canon(r.get("status"), STATUS)
        if a is None:
            problems.append(f"{i}: access {r.get('access')!r} not in the closed list")
        if s is None:
            problems.append(f"{i}: status {r.get('status')!r} not in the closed list")
        acc[i], status[i] = a, s
    missing = sorted(set(meta) - set(acc))
    if missing:
        problems.append(f"no access row for {missing}")
    return acc, status, problems


def match(A, B):
    """§5: pass 1 = same instrument, normalised clause and category; pass 2 = same instrument, quantity and window
    class. One-to-one, in each rater's file order."""
    used_a, used_b, pairs = set(), set(), []
    for pas, key in ((1, lambda r: (r["instrument_id"], r["_c"], r["_cat"])),
                     (2, lambda r: (r["instrument_id"], r["_q"], r["_w"]))):
        for x in A:
            if x["_i"] in used_a:
                continue
            for y in B:
                if y["_i"] not in used_b and key(x) == key(y):
                    pairs.append((x, y, pas))
                    used_a.add(x["_i"])
                    used_b.add(y["_i"])
                    break
    ua = [x for x in A if x["_i"] not in used_a]
    ub = [y for y in B if y["_i"] not in used_b]
    return pairs, ua, ub


def row(r, stated=False):
    w = "not stated" if (stated and r["_unit"]) else r["_w"]
    return {"req_id": r.get("req_id"), "instrument_id": r["instrument_id"], "clause": r.get("clause"),
            "category": r.get("category"), "measurement_point": r["_p"], "quantity": r["_q"], "limit": r.get("limit"),
            "window_class": w, "window_as_printed": r.get("window_as_printed"), "allowance_class": r["_a"],
            "allowance_as_printed": r.get("allowance_as_printed"), "binding_class": r["_b"],
            "deciding": "yes" if r["_d"] else "no", "computed_shape": shape_of(w, r["_a"]),
            "written_shape": r["_s_written"], "confidence": r.get("confidence"), "source_url": r.get("source_url"),
            "quote": r.get("quote"), "note": r.get("note")}


def cons_shape(sa, sb):
    if sa == "history" and sb == "history":
        return "history"
    if "cannot judge" in (sa, sb):
        return "cannot judge"
    if "reactive" in (sa, sb):
        return "reactive"
    return "electronics"


def readout(pairs, A, B, meta, insts, mode, stated, limited, unread):
    both = mode == "both"
    sw = lambda r: "not stated" if (stated and r["_unit"]) else r["_w"]
    sh = lambda r: shape_of(sw(r), r["_a"])
    binding = lambda x, y: (x["_b"] in BINDS and y["_b"] in BINDS) if both else (x["_b"] in BINDS or y["_b"] in BINDS)
    deciding = lambda x, y: (x["_d"] and y["_d"]) if both else (x["_d"] or y["_d"])
    P = [(x, y, p) for x, y, p in pairs if x["instrument_id"] in insts]
    bd = [(x, y, p) for x, y, p in P if binding(x, y) and deciding(x, y)]
    cs = [cons_shape(sh(x), sh(y)) for x, y, _ in bd]
    hist = [(x, y) for (x, y, _), s in zip(bd, cs) if s == "history"]
    # "none with shape history from either rater, matched or unmatched" (§6)
    either = [row(r, stated) for r in A + B if r["instrument_id"] in insts and r["_b"] in BINDS and r["_d"]
              and sh(r) == "history"]
    n_inst = len({x["instrument_id"] for x, _, _ in bd})

    def tab(f):
        t = {"agree": Counter(), "disagree": 0}
        for x, y, _ in bd:
            if f(x) == f(y):
                t["agree"][f(x)] += 1
            else:
                t["disagree"] += 1
        t["agree"] = dict(t["agree"])
        t["A"] = dict(Counter(f(x) for x, _, _ in bd))
        t["B"] = dict(Counter(f(y) for _, y, _ in bd))
        return t

    fastest = {}
    for who, k in (("A", 0), ("B", 1)):
        per = defaultdict(list)
        for pr in bd:
            r = pr[k]
            if sw(r) != "not stated":
                per[meta[r["instrument_id"]]["body"]].append(WINDOWS.index(sw(r)))
        for body, v in per.items():
            fastest.setdefault(body, {})[who] = WINDOWS[min(v)]

    hist_points = sorted({p for x, y in hist for p in (x["_p"], y["_p"])})
    if hist:
        verdict = "HISTORY-SHAPED SPEC EXISTS"
    elif len(bd) >= 8 and n_inst >= 4 and not either:
        verdict = "NO HISTORY-SHAPED SPEC"
    else:
        verdict = "UNCLEAR"
    qual = f"ACCESS-LIMITED: {len(unread)} of {SEED_N} seeds unread" if limited else None
    if limited and verdict == "NO HISTORY-SHAPED SPEC":
        verdict = f"UNCLEAR ({qual}; NO HISTORY-SHAPED SPEC cannot be established)"
    elif limited:
        verdict = f"{verdict} ({qual})"
    return {"binding_deciding_pairs": len(bd), "instruments_with_binding_deciding": n_inst,
            "conservative_shape": dict(Counter(cs)),
            "history_pairs": [{"A": row(x, stated), "B": row(y, stated)} for x, y in hist],
            "history_measurement_points": hist_points,
            "history_at_poi_or_facility_only": bool(hist) and set(hist_points) <= UPSTREAM,
            "either_rater_history_rows": either,
            "window_class_table": tab(sw), "allowance_class_table": tab(lambda r: r["_a"]),
            "fastest_binding_window_per_body": fastest, "verdict": verdict}


CONSEQUENCE = {
    "NO HISTORY-SHAPED SPEC": "closes the anticipation leg of ANGLES §B.2: DC1's primary regime is the real one",
    "HISTORY-SHAPED SPEC EXISTS": "re-opens the leg as DC1's sensitivity; the named spec (window, allowance, point) is "
                                  "the input to a pre-registered DC1b re-run, not run here",
    "UNCLEAR": "the leg stays where DC1 left it",
}


def consequence(v):
    for k in ("NO HISTORY-SHAPED SPEC", "HISTORY-SHAPED SPEC EXISTS"):
        if v.startswith(k):
            return CONSEQUENCE[k]
    return CONSEQUENCE["UNCLEAR"] if not v.startswith("UNGATED") else "UNGATED: no reading"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="results/DC2")
    ap.add_argument("--list", default="results/DC2/DC2_instruments.md")
    ap.add_argument("--out", default="dc2.json")
    a = ap.parse_args()
    meta = instruments(a.list)
    A, pa = load_reqs(os.path.join(a.dir, "requirements_A.csv"), meta, "A")
    B, pb = load_reqs(os.path.join(a.dir, "requirements_B.csv"), meta, "B")
    accA, stA, qa = load_access(os.path.join(a.dir, "instruments_A.csv"), meta)
    accB, stB, qb = load_access(os.path.join(a.dir, "instruments_B.csv"), meta)
    problems = {"requirements_A": pa, "requirements_B": pb, "instruments_A": qa, "instruments_B": qb}
    if any(problems.values()):
        print("VALIDATION PROBLEMS:", json.dumps(problems, indent=1, ensure_ascii=False))

    seed = {i for i, m in meta.items() if m["seed"]}
    both_none = {i for i in meta if accA.get(i) == "none" and accB.get(i) == "none"}
    unread = sorted(seed & both_none)
    limited = len(unread) >= LIMIT_K
    readable = set(meta) - both_none
    # identification over instruments at least one rater could read (§5, L1 L-2)
    A = [r for r in A if r["instrument_id"] in readable]
    B = [r for r in B if r["instrument_id"] in readable]
    pairs, ua, ub = match(A, B)
    M, M1 = len(pairs), sum(p == 1 for _, _, p in pairs)
    ident = M / (len(A) + len(B) - M) if (len(A) + len(B) - M) else None
    p1 = [(x, y) for x, y, p in pairs if p == 1]
    k_win = kappa([(x["_w"], y["_w"]) for x, y in p1])
    gates = {
        "n_A": len(A), "n_B": len(B), "M": M, "M1": M1, "M2": M - M1, "identification": ident,
        "kappa_window_M1": k_win,
        "kappa_window_all_M (reported; pass-2 pairs agree by construction)": kappa([(x["_w"], y["_w"]) for x, y, _ in pairs]),
        "kappa_allowance_M1": kappa([(x["_a"], y["_a"]) for x, y in p1]),
        "kappa_computed_shape_M1": kappa([(x["_s"], y["_s"]) for x, y in p1]),
        "binding_class_all_M": kappa([(x["_b"], y["_b"]) for x, y, _ in pairs]),
        "deciding_all_M": kappa([(x["_d"], y["_d"]) for x, y, _ in pairs]),
    }
    reasons = []
    if ident is None or ident < 0.80:
        reasons.append(f"identification {ident} < 0.80")
    if M1 < MIN_M1:
        reasons.append(f"M1 {M1} < {MIN_M1}")
    elif k_win["kappa"] is None or k_win["kappa"] < 0.60:
        reasons.append(f"kappa(window, M1) {k_win['kappa']} < 0.60")
    gates["ungated_reasons"] = reasons

    additions = {i for i, m in meta.items() if not m["seed"]}
    variants = {"primary": (set(meta), "both", False), "STATED": (set(meta), "both", True),
                "ANY": (set(meta), "any", False), "SEED": (seed, "both", False)}
    out = {"preregistration": "results/DC2/DC2_preregistration.md (60f7595; deviations DC2-1, DC2-2, 1dda7d3)",
           "tags": "requirements SOURCED; classes DERIVED-judgemental; both raters are language-model sessions",
           "validation_problems": problems, "gates": gates,
           "access": {"A": accA, "B": accB, "status_A": stA, "status_B": stB,
                      "counts_seed": {f"{x}/{y}": sum(1 for i in seed if accA.get(i) == x and accB.get(i) == y)
                                      for x in ACCESS for y in ACCESS},
                      "counts_by_group": {g: dict(Counter(f"{accA.get(i)}/{accB.get(i)}" for i in meta
                                                          if meta[i]["group"] == g)) for g in "GUEQVX"},
                      "unread_seed": unread, "threshold": f">= {LIMIT_K} of {SEED_N}", "limited": limited},
           "additions": sorted(additions)}
    for name, (insts, mode, stated) in variants.items():
        r = readout(pairs, A, B, meta, insts, mode, stated, limited, unread)
        if reasons:
            r["verdict"] = "UNGATED (" + "; ".join(reasons) + ")"
        r["consequence"] = consequence(r["verdict"])
        out[name] = r

    # records (never reconciled)
    fields = (("window_class", "_w"), ("allowance_class", "_a"), ("binding_class", "_b"), ("quantity", "_q"),
              ("measurement_point", "_p"), ("deciding", "_d"), ("computed_shape", "_s"))
    out["requirement_table"] = [{"pass": p, "A": row(x), "B": row(y),
                                 "disagree_on": [f for f, k in fields if x[k] != y[k]]} for x, y, p in pairs]
    out["unmatched_A"] = [row(x) for x in ua]
    out["unmatched_B"] = [row(y) for y in ub]
    out["disagreements"] = {f: sum(f in t["disagree_on"] for t in out["requirement_table"]) for f, _ in fields}
    out["written_vs_computed_shape"] = [row(r) for r in A + B if r["_s_written"] != r["_s"]]
    out["deciding_vs_quantity"] = [row(r) for r in A + B if r["_q"] and r["_d"] != (r["_q"] in DECIDING_Q)]
    out["DC2_2_conversions"] = [dict(row(r), rater=r["_who"]) for r in A + B if "dc2-2" in (r.get("note") or "").lower()]
    out["vendor_capability_rows"] = [dict(row(r), rater=r["_who"]) for r in A + B if r["_b"] == "vendor capability"]
    out["power_quality_pairs"] = [{"A": row(x), "B": row(y)} for x, y, _ in pairs if not x["_d"] and not y["_d"]]
    out["own"] = {}
    for who, X in (("A", A), ("B", B)):
        bdx = [r for r in X if r["_b"] in BINDS and r["_d"]]
        out["own"][who] = {"rows": len(X), "binding_deciding": len(bdx),
                           "window": dict(Counter(r["_w"] for r in bdx)),
                           "allowance": dict(Counter(r["_a"] for r in bdx)),
                           "computed_shape": dict(Counter(r["_s"] for r in bdx)),
                           "instruments": len({r["instrument_id"] for r in bdx})}

    p = out["primary"]
    extra = [f"{k}: {out[k]['verdict']}" for k in ("ANY", "STATED") if out[k]["verdict"] != p["verdict"]]
    line = p["verdict"] + (" [" + "; ".join(extra) + "]" if extra else "")
    if p["history_pairs"]:
        line += (" — history-shaped requirement at POI / facility only (a weaker match to DC1's node / rack model)"
                 if p["history_at_poi_or_facility_only"] else
                 " — history-shaped requirement at: " + ", ".join(p["history_measurement_points"]))
    out["verdict_line"] = line
    out["consequence_line"] = p["consequence"]
    json.dump(out, open(os.path.join(a.dir, a.out), "w"), indent=1, ensure_ascii=False, default=str)

    g = gates
    fk = lambda k: "n/a" if k["kappa"] is None else f"{k['kappa']:.3f} (n {k['n']})"
    print("verdict:", out["verdict_line"])
    print("consequence:", out["consequence_line"])
    print(f"identification {g['identification']} (M {M} = {M1} + {M - M1}, n_A {len(A)}, n_B {len(B)}); "
          f"kappa window M1 {fk(k_win)}; allowance {fk(g['kappa_allowance_M1'])}; shape {fk(g['kappa_computed_shape_M1'])}")
    print(f"unread seeds {len(unread)} {unread}; limited {limited}")
    for k in ("primary", "STATED", "ANY", "SEED"):
        q = out[k]
        print(f"  {k}: {q['verdict']}; binding-deciding pairs {q['binding_deciding_pairs']} from "
              f"{q['instruments_with_binding_deciding']} instruments; shapes {q['conservative_shape']}; "
              f"either-rater history rows {len(q['either_rater_history_rows'])}")
    print(f"unmatched A {len(ua)}, B {len(ub)}; disagreements {out['disagreements']}; "
          f"written-vs-computed shape {len(out['written_vs_computed_shape'])}; DC2-2 rows {len(out['DC2_2_conversions'])}")


if __name__ == "__main__":
    main()
