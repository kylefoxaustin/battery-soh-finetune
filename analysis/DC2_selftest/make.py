"""Writes synthetic DC2 scenarios for analysis/DC2_agreement.py (no real requirement content; every limit, URL and
quote is invented). Run from the repository root:  python3 -I analysis/DC2_selftest/make.py
Then, per scenario:  python3 -I analysis/DC2_agreement.py --dir analysis/DC2_selftest/sN --list analysis/DC2_selftest/list.md

list.md: 50 seeds (G01-G16, U01-U03, E01-E11, Q01-Q06, V01-V14) and two additions (Q07 via S3, X01 via DC2-1).

s1, HISTORY-SHAPED SPEC EXISTS (gated):
- 10 pass-1 pairs over 5 instruments, binding and deciding, reactive or electronics, all classes agreed;
- 1 pass-1 pair at the POI with window 1-60 s and allowance loose from both raters (history), on X01 (an addition);
- 2 pass-2 pairs (clauses written differently; same quantity and window class);
- 1 DC2-2 pair: A converts a recurrence + duration to `loose` (note names DC2-2), B keeps `event count`
  -> allowance disagreement, conservative shape cannot judge;
- 1 non-deciding flicker pair; 1 vendor-capability row in A only; 1 unmatched row in B;
- B writes shape `reactive` on one row whose computed shape is `electronics`.
Expected: M 15 (13 pass 1 + 2 pass 2), n_A 16, n_B 16, identification 15/17; kappa(window, M1) 1.0; primary
HISTORY-SHAPED SPEC EXISTS at POI / facility only. SEED (drops X01) has 13 binding deciding pairs from 6 instruments
but reads UNCLEAR, not NO HISTORY-SHAPED SPEC: A's DC2-2 row (1-60 s, loose, mandatory) is a history row from one
rater, which bars NO HISTORY-SHAPED SPEC (§6, "either rater, matched or unmatched").

s2, NO HISTORY-SHAPED SPEC (gated): 12 binding deciding pass-1 pairs from 5 instruments, none history; one pair's
window comes from the rate unit (`unit: MW/min`, 1 - 15 min) -> STATED turns it to `not stated` / cannot judge and the
verdict stays NO HISTORY-SHAPED SPEC.

s3, as s2 but both raters record access `none` on 17 seed instruments (G01-G11, U01-U03, E01-E03, none of which carry
rows) -> UNCLEAR (ACCESS-LIMITED: 17 of 50 seeds unread; NO HISTORY-SHAPED SPEC cannot be established).

s4, UNGATED: 6 pass-1 pairs and 3 pass-2 pairs, identification 1.0 -> M1 6 < 10 -> UNGATED.

s5, ANY differs from primary: as s2 plus one pass-1 pair with window 1-60 s, allowance loose from both raters, where A
writes `mandatory` and B `recommendation`. Primary: the pair is not binding (both required), but A's row is a binding
deciding history row -> NO HISTORY-SHAPED SPEC is barred -> UNCLEAR. ANY: HISTORY-SHAPED SPEC EXISTS.
"""
import csv
import os

here = os.path.dirname(os.path.abspath(__file__))
REQ = ["req_id", "instrument_id", "clause", "category", "measurement_point", "quantity", "limit", "basis",
       "window_class", "window_as_printed", "allowance_class", "allowance_as_printed", "binding_class", "deciding",
       "shape", "source_url", "quote", "confidence", "note"]
INS = ["instrument_id", "access", "edition_read", "status", "sources_tried", "note"]
SEEDS = ([f"G{i:02d}" for i in range(1, 17)] + [f"U{i:02d}" for i in range(1, 4)] + [f"E{i:02d}" for i in range(1, 12)]
         + [f"Q{i:02d}" for i in range(1, 7)] + [f"V{i:02d}" for i in range(1, 15)])
ADDS = {"Q07": "added via E08 clause 2.11", "X01": "DC2-1 (cited by locator L1)"}
DEC = {"ramp rate", "step change", "swing amplitude", "smoothing or capping response", "load change per interval"}


def shape(w, a):
    if w in ("≤ 100 ms", "100 ms – 1 s"):
        return "electronics"
    if w in ("1 – 15 min", "> 15 min"):
        return "reactive"
    if w == "1 – 60 s":
        return {"hard": "reactive", "tight": "reactive", "loose": "history", "very loose": "history"}.get(a, "cannot judge")
    return "cannot judge"


def r(inst, clause, q="ramp rate", w="1 – 15 min", a="hard", b="mandatory", p="POI", cat="", wp="", note="",
      shp=None):
    return {"instrument_id": inst, "clause": clause, "category": cat, "measurement_point": p, "quantity": q,
            "limit": "SYNTHETIC", "basis": "", "window_class": w, "window_as_printed": wp or "SYNTHETIC",
            "allowance_class": a, "allowance_as_printed": "SYNTHETIC", "binding_class": b,
            "deciding": "yes" if q in DEC else "no", "shape": shp or shape(w, a),
            "source_url": "https://example.invalid/synthetic", "quote": "synthetic", "confidence": "high", "note": note}


def write_list():
    with open(os.path.join(here, "list.md"), "w") as f:
        f.write("# synthetic DC2 instrument list (self-test only)\n\n## 1. Instruments\n\n")
        f.write("| instrument_id | group | identifier | exact title | issuing body | jurisdiction | landing URL | scope | "
                "headings | access | status | origin | references |\n" + "|---" * 13 + "|\n")
        for i in SEEDS + list(ADDS):
            body = {"G": "Grid body " + i[1:], "U": "Utility", "E": "EU body", "Q": "Standards body", "V": "Vendor",
                    "X": "Other operator"}[i[0]]
            f.write(f"| {i} | {i[0]} | SYN-{i} | Synthetic {i} | {body} (synthetic) | n/a | https://example.invalid | "
                    f"synthetic | | full | in force | {ADDS.get(i, 'seed')} | n/a |\n")
        f.write("\n## 2. Locators\n")


def write(name, A, B, none=()):
    d = os.path.join(here, name)
    os.makedirs(d, exist_ok=True)
    for R, rows in (("A", A), ("B", B)):
        with open(os.path.join(d, f"requirements_{R}.csv"), "w", newline="") as f:
            w = csv.DictWriter(f, REQ)
            w.writeheader()
            for k, x in enumerate(rows, 1):
                w.writerow(dict(x, req_id=f"{R}{k:03d}"))
        with open(os.path.join(d, f"instruments_{R}.csv"), "w", newline="") as f:
            w = csv.DictWriter(f, INS)
            w.writeheader()
            for i in SEEDS + list(ADDS):
                acc = "none" if i in none else "full"
                w.writerow({"instrument_id": i, "access": acc, "edition_read": "synthetic", "status": "in force",
                            "sources_tried": "synthetic", "note": ""})


def base12():
    """12 agreed binding deciding pass-1 pairs from 5 instruments, reactive or electronics."""
    spec = [("G12", "9.1(a)", "1 – 15 min", "hard"), ("G12", "9.1(b)", "> 15 min", "tight"),
            ("G12", "9.2", "1 – 60 s", "hard"), ("E04", "CC.6.1.7", "≤ 100 ms", "hard"),
            ("E04", "CC.6.1.8", "100 ms – 1 s", "loose"), ("E01", "Art. 12(3)", "1 – 15 min", "loose"),
            ("E01", "Art. 13", "1 – 60 s", "tight"), ("U01", "Sheet 2, 4(c)", "1 – 15 min", "very loose"),
            ("U01", "Sheet 2, 4(d)", "> 15 min", "hard"), ("V01", "5.3.2", "≤ 100 ms", "hard"),
            ("V01", "5.3.3", "1 – 60 s", "hard"), ("V01", "Table 7", "100 ms – 1 s", "tight")]
    return [r(i, c, w=w, a=a, cat="row 1" if c == "Table 7" else "") for i, c, w, a in spec]


def main():
    write_list()
    # s1
    A, B = base12()[:10], base12()[:10]
    A.append(r("X01", "4.2", w="1 – 60 s", a="loose", p="POI"))
    B.append(r("X01", "Section 4.2", w="1 – 60 s", a="loose", p="POI"))
    A.append(r("E04", "CC.6.1.9", q="step change", w="1 – 15 min", a="hard"))
    B.append(r("E04", "CC 6.1.9 (step)", q="step change", w="1 – 15 min", a="hard"))
    A.append(r("G12", "9.4", q="load change per interval", w="> 15 min", a="tight"))
    B.append(r("G12", "9.4.1", q="load change per interval", w="> 15 min", a="tight"))
    A.append(r("V02", "6.1", w="1 – 60 s", a="loose", p="rack or row", note="DC2-2: synthetic recurrence and duration"))
    B.append(r("V02", "6.1", w="1 – 60 s", a="event count", p="rack or row"))
    A.append(r("Q01", "Table 2", q="flicker", w="> 15 min", a="loose", b="planning level", cat="HV"))
    B.append(r("Q01", "Table 2", q="flicker", w="> 15 min", a="loose", b="planning level", cat="HV"))
    A.append(r("V11", "power smoothing", q="smoothing or capping response", w="1 – 60 s", a="not stated",
               b="vendor capability", p="device"))
    B.append(r("U02", "Rider 3", w="1 – 15 min", a="hard"))
    B[3] = dict(B[3], shape="reactive")  # E04 CC.6.1.7 is electronics by the table
    write("s1", A, B)
    # s2
    A, B = base12(), base12()
    A[0] = dict(A[0], window_as_printed="unit: MW/min")
    B[0] = dict(B[0], window_as_printed="unit: MW/min")
    write("s2", A, B)
    # s3
    write("s3", A, B, none=[f"G{i:02d}" for i in range(1, 12)] + ["U02", "U03", "E02", "E03", "E05", "E06"])
    # s4
    A, B = base12()[:6], base12()[:6]
    for k, (i, c) in enumerate((("E07", "1"), ("E07", "2"), ("E07", "3"))):
        A.append(r(i, c, q="ramp rate", w="1 – 15 min"))
        B.append(r(i, "para " + c + "a", q="ramp rate", w="1 – 15 min"))
    write("s4", A, B)
    # s5
    A, B = base12(), base12()
    A.append(r("G13", "25.194(k)", w="1 – 60 s", a="loose", b="mandatory"))
    B.append(r("G13", "25.194(k)", w="1 – 60 s", a="loose", b="recommendation"))
    write("s5", A, B)


if __name__ == "__main__":
    main()
