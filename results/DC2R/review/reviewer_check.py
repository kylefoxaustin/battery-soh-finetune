"""Reviewer re-derivation of DC2 (pre-registration §5-§6 with DC2-1, DC2-2). Own code; reads only the four rater
files. Usage: python3 -I dc2_check.py <results/DC2 dir>"""
import csv, re, sys, unicodedata
from collections import Counter, defaultdict

D = sys.argv[1]
WIN = ["≤ 100 ms", "100 ms – 1 s", "1 – 60 s", "1 – 15 min", "> 15 min", "not stated"]
ALW = ["hard", "tight", "loose", "very loose", "event count", "not stated"]
DECIDING_Q = {"ramp rate", "step change", "swing amplitude", "smoothing or capping response", "load change per interval"}
BINDING = {"mandatory", "planning level"}
SEEDS = {f"{g}{i:02d}" for g, n in (("G", 16), ("U", 3), ("E", 11), ("Q", 6), ("V", 14)) for i in range(1, n + 1)}
ADDS = {"Q07", "Q08", "Q09", "X01", "X02", "X03"}


def nfkc(s):
    return unicodedata.normalize("NFKC", s or "").strip()


def canon_win(s):
    s = nfkc(s).replace("—", "–").replace("-", "–").replace(" ", "")
    table = {"≤100ms": WIN[0], "<=100ms": WIN[0], "100ms–1s": WIN[1], "1–60s": WIN[2], "1–15min": WIN[3],
             ">15min": WIN[4], "notstated": WIN[5]}
    assert s in table, ("window", s)
    return table[s]


def canon_alw(s):
    s = nfkc(s).lower()
    assert s in ALW, ("allowance", s)
    return s


def shape_of(w, a):
    if w in (WIN[0], WIN[1]):
        return "electronics"
    if w == WIN[2]:
        return {"hard": "reactive", "tight": "reactive", "loose": "history", "very loose": "history"}.get(a, "cannot judge")
    if w in (WIN[3], WIN[4]):
        return "reactive"
    return "cannot judge"


def load(f):
    rows = list(csv.DictReader(open(f"{D}/{f}", encoding="utf-8")))
    for r in rows:
        r["window_class"] = canon_win(r["window_class"])
        r["allowance_class"] = canon_alw(r["allowance_class"])
        r["quantity"] = nfkc(r["quantity"]).lower()
        r["binding_class"] = nfkc(r["binding_class"]).lower()
        r["deciding"] = nfkc(r["deciding"]).lower()
        r["cshape"] = shape_of(r["window_class"], r["allowance_class"])
    return rows


STOP = re.compile(r"\b(section|clause|paragraph|table|annex|article|art)\b|§")


def norm(s):
    s = nfkc(s).lower()
    s = STOP.sub("", s)
    return re.sub(r"[\W_]+", "", s)


def kappa(pairs, cats):
    n = len(pairs)
    if n == 0:
        return float("nan"), float("nan")
    po = sum(a == b for a, b in pairs) / n
    ca, cb = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    pe = sum(ca[c] * cb[c] for c in cats) / (n * n)
    return (po - pe) / (1 - pe) if pe < 1 else float("nan"), po


def match_old(A, B):
    byI = defaultdict(lambda: ([], []))
    for i, r in enumerate(A):
        byI[r["instrument_id"]][0].append(i)
    for j, r in enumerate(B):
        byI[r["instrument_id"]][1].append(j)
    p1, p2, uA, uB = [], [], set(range(len(A))), set(range(len(B)))
    for inst, (ia, ib) in byI.items():
        for i in ia:
            k = (norm(A[i]["clause"]), norm(A[i]["category"]))
            for j in ib:
                if j in uB and (norm(B[j]["clause"]), norm(B[j]["category"])) == k:
                    p1.append((i, j)); uA.discard(i); uB.discard(j); break
        for i in ia:
            if i not in uA:
                continue
            for j in ib:
                if j in uB and A[i]["quantity"] == B[j]["quantity"] and A[i]["window_class"] == B[j]["window_class"]:
                    p2.append((i, j)); uA.discard(i); uB.discard(j); break
    return p1, p2, sorted(uA), sorted(uB)


def match(A, B):
    """DC2-R pass 1 (DC2R-D1): non-deciding rows on normalised clause + quantity; deciding rows on normalised clause +
    category. Pass 2: same quantity + window class, file order."""
    byI = defaultdict(lambda: ([], []))
    for i, r in enumerate(A):
        byI[r["instrument_id"]][0].append(i)
    for j, r in enumerate(B):
        byI[r["instrument_id"]][1].append(j)
    p1, p2, uA, uB = [], [], set(range(len(A))), set(range(len(B)))
    def key(r):
        if r["quantity"] in DECIDING_Q:
            return ("d", norm(r["clause"]), norm(r["category"]))
        return ("n", norm(r["clause"]), r["quantity"])
    for inst, (ia, ib) in byI.items():
        for i in ia:
            k = key(A[i])
            for j in ib:
                if j in uB and key(B[j]) == k:
                    p1.append((i, j)); uA.discard(i); uB.discard(j); break
        for i in ia:
            if i not in uA:
                continue
            for j in ib:
                if j in uB and A[i]["quantity"] == B[j]["quantity"] and A[i]["window_class"] == B[j]["window_class"]:
                    p2.append((i, j)); uA.discard(i); uB.discard(j); break
    return p1, p2, sorted(uA), sorted(uB)


A, B = load("requirements_A.csv"), load("requirements_B.csv")
IA = {r["instrument_id"]: r for r in csv.DictReader(open(f"{D}/instruments_A.csv", encoding="utf-8"))}
IB = {r["instrument_id"]: r for r in csv.DictReader(open(f"{D}/instruments_B.csv", encoding="utf-8"))}
for name, L in (("A", A), ("B", B)):
    for r in L:
        assert r["shape"].strip().lower() == r["cshape"], (name, r["req_id"], r["shape"], r["cshape"])
print("written shape == computed shape for every row of both files")
for name, L in (("A", A), ("B", B)):
    bad=[r["req_id"] for r in L if (r["quantity"] in DECIDING_Q) != (r["deciding"]=="yes")]
    print(f"rater {name}: deciding flag follows quantity for all rows: {not bad} {bad[:5]}")
p1, p2, uA, uB = match(A, B)
M = len(p1) + len(p2)
nA, nB = len(A), len(B)
print(f"n_A {nA} n_B {nB}; M {M} = {len(p1)} (pass 1) + {len(p2)} (pass 2); identification {M/(nA+nB-M):.3f}")
kw, po = kappa([(A[i]["window_class"], B[j]["window_class"]) for i, j in p1], WIN)
print(f"kappa(window, M1={len(p1)}) {kw:.3f} observed {po:.3f}")
kwa, _ = kappa([(A[i]["window_class"], B[j]["window_class"]) for i, j in p1 + p2], WIN)
ka, poa = kappa([(A[i]["allowance_class"], B[j]["allowance_class"]) for i, j in p1], ALW)
ks, pos = kappa([(A[i]["cshape"], B[j]["cshape"]) for i, j in p1], ["history", "reactive", "electronics", "cannot judge"])
kb, pob = kappa([(A[i]["binding_class"], B[j]["binding_class"]) for i, j in p1 + p2], ["mandatory", "planning level", "recommendation", "vendor capability"])
kd, pod = kappa([(A[i]["deciding"], B[j]["deciding"]) for i, j in p1 + p2], ["yes", "no"])
print(f"kappa(window, all M) {kwa:.3f}; allowance(M1) {ka:.3f} obs {poa:.3f}; shape(M1) {ks:.3f} obs {pos:.3f}; binding(all) {kb:.3f} obs {pob:.3f}; deciding(all) {kd:.3f} obs {pod:.3f}")
dis = Counter()
for i, j in p1 + p2:
    for f in ("window_class", "allowance_class", "quantity", "measurement_point", "deciding", "cshape", "binding_class"):
        if nfkc(A[i][f]).lower() != nfkc(B[j][f]).lower():
            dis[f] += 1
print("field disagreements over all M:", dict(dis))
print("unmatched A:", len(uA), Counter(A[i]["quantity"] for i in uA))
print("unmatched B:", len(uB), Counter(B[j]["quantity"] for j in uB), "deciding among them:", sum(B[j]["deciding"] == "yes" for j in uB))

# access-limited test
none_both = [s for s in sorted(SEEDS) if IA[s]["access"].strip() == "none" and IB[s]["access"].strip() == "none"]
print(f"seeds none/none: {len(none_both)} (limited={len(none_both) >= 17}); seed access A/B:", Counter((IA[s]["access"].strip(), IB[s]["access"].strip()) for s in SEEDS))
print("status counts A:", Counter(r["status"].strip() for r in IA.values()), "B:", Counter(r["status"].strip() for r in IB.values()))


def cons_shape(sa, sb):
    if sa == "history" and sb == "history":
        return "history"
    if "cannot judge" in (sa, sb):
        return "cannot judge"
    return "reactive" if "reactive" in (sa, sb) else "electronics"


def readout(pairs, insts, mode="both", stated=False):
    def sh(r):
        w = WIN[5] if stated and nfkc(r["window_as_printed"]).lower().startswith("unit:") else r["window_class"]
        return shape_of(w, r["allowance_class"])
    bd = []
    for i, j in pairs:
        a, b = A[i], B[j]
        if a["instrument_id"] not in insts:
            continue
        bind = (a["binding_class"] in BINDING, b["binding_class"] in BINDING)
        dec = (a["deciding"] == "yes", b["deciding"] == "yes")
        ok = (all(bind) and all(dec)) if mode == "both" else (any(bind) and any(dec))
        if ok:
            bd.append((a["instrument_id"], cons_shape(sh(a), sh(b)), a["req_id"], b["req_id"]))
    shapes = Counter(s for _, s, _, _ in bd)
    either = [r["req_id"] for r in A + B if r["instrument_id"] in insts and r["binding_class"] in BINDING
              and r["deciding"] == "yes" and r["cshape"] == "history"]
    ninst = len({x[0] for x in bd})
    if shapes["history"] >= 1:
        v = "HISTORY-SHAPED SPEC EXISTS"
    elif len(bd) >= 8 and ninst >= 4 and not either:
        v = "NO HISTORY-SHAPED SPEC"
    else:
        v = "UNCLEAR"
    return bd, shapes, ninst, either, v


ALL = SEEDS | ADDS
gate_ok = (M / (nA + nB - M) >= 0.80) and len(p1) >= 10 and kw >= 0.60
print("\nGATE:", "passes" if gate_ok else f"UNGATED (identification {M/(nA+nB-M):.3f} < 0.80)" if M/(nA+nB-M) < 0.80 else "UNGATED (kappa)")
for name, (insts, mode, stated) in {"primary": (ALL, "both", False), "STATED": (ALL, "both", True),
                                    "ANY": (ALL, "any", False), "SEED": (SEEDS, "both", False)}.items():
    bd, shapes, ninst, either, v = readout(p1 + p2, insts, mode, stated)
    print(f"  {name:8s} binding-deciding pairs {len(bd):2d} from {ninst} instruments; shapes {dict(shapes)}; either-rater history rows {len(either)}; would-be verdict {v}")
bd, *_ = readout(p1 + p2, ALL)
print("history pairs:", [(x[0], x[2], x[3]) for x in bd if x[1] == "history"])
print("binding-deciding pairs by instrument:", Counter(x[0] for x in bd))
for name, L in (("A", A), ("B", B)):
    own = [r for r in L if r["binding_class"] in BINDING and r["deciding"] == "yes"]
    print(f"rater {name} own binding-deciding rows {len(own)} from {len({r['instrument_id'] for r in own})} instruments; shapes {dict(Counter(r['cshape'] for r in own))}")
# non-deciding pairs: window/allowance table (rater A classes)
nd = [(A[i], B[j]) for i, j in p1 + p2 if not (A[i]["deciding"] == "yes" and B[j]["deciding"] == "yes" and A[i]["binding_class"] in BINDING and B[j]["binding_class"] in BINDING)]
print("non-binding-deciding pairs:", len(nd), "by quantity (A):", Counter(a["quantity"] for a, _ in nd).most_common())
print("top window/allowance (A):", Counter((a["window_class"], a["allowance_class"]) for a, _ in nd).most_common(8))
# exploratory: identification restricted to deciding rows (either rater says deciding)
decA = {i for i, r in enumerate(A) if r["deciding"] == "yes"}; decB = {j for j, r in enumerate(B) if r["deciding"] == "yes"}
md = [(i, j) for i, j in p1 + p2 if i in decA or j in decB]
print(f"exploratory: deciding-row identification {len(md)}/({len(md)} + {len([i for i in uA if i in decA])} + {len([j for j in uB if j in decB])}) = {len(md)/(len(md)+len([i for i in uA if i in decA])+len([j for j in uB if j in decB])):.2f}")
