"""Reviewer re-derivation of L1b (L1B_preregistration.md §5 with L-1 … L-5 and L1B-D1). Own code; reads only the
rater files (ledger_*.csv, instruments_*.csv, stack_B_*.csv), B_events.csv, and L1's two ledgers for the calibration
reference. Usage: python3 -I reviewer_check.py results/L1B results/L1 (run from the repository root)"""
import csv, json, math, re, sys
from collections import Counter, defaultdict
from datetime import date
from itertools import groupby

D, D1 = sys.argv[1], sys.argv[2]
CLASSES = ["software-only", "memory-or-crypto", "hardware-or-recert", "cannot judge"]
STACK = ["yes", "no", "cannot judge"]
ORDER = {"software-only": 0, "memory-or-crypto": 1, "hardware-or-recert": 2}
SEED_L = {f"L{i:02d}" for i in range(1, 23)}
ADD_L = {f"L{i:02d}" for i in range(23, 48)}
SEED_S = {f"S{i:02d}" for i in range(1, 17)}
ADD_S = {f"S{i:02d}" for i in range(17, 27)}
SEED = SEED_L | SEED_S
ALL = SEED | ADD_L | ADD_S
CHINA_L = {f"L{i:02d}" for i in range(13, 20)}          # GB 4785, 4599, 25991, 23255, 17509, 5920, GB/T 30036
CHINA_S = {"S14", "S15", "S16"}
VL_INST = {"B05", "B06", "B14", "B15"}
N_B = 35
WIN = (date(2016, 1, 1), date(2026, 12, 31))


def load(d, f):
    return list(csv.DictReader(open(f"{d}/{f}", encoding="utf-8")))


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def d(s):
    return date.fromisoformat(s.strip())


def wilson(k, n, z=1.959964):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (c - h, c + h)


def ratio_ci(nb, nl):
    """L1-review method: Wilson on nb/(nb+nl), mapped to odds."""
    lo, hi = wilson(nb, nb + nl)
    return (lo / (1 - lo), hi / (1 - hi) if hi < 1 else float("inf"))


def kappa(pairs, cats):
    n = len(pairs)
    if n == 0:
        return float("nan"), float("nan")
    po = sum(a == b for a, b in pairs) / n
    ca, cb = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    pe = sum(ca[c] * cb[c] for c in cats) / (n * n)
    if pe == 1:
        return float("nan"), po
    return (po - pe) / (1 - pe), po


def fisher_one_sided(a, b, c, dd):
    """P(X >= a) for the 2x2 table [[a, b], [c, dd]] with fixed margins (alternative: row-1 share > row-2 share)."""
    n = a + b + c + dd
    r1, c1 = a + b, a + c
    lo, hi = max(0, r1 + c1 - n), min(r1, c1)
    def pmf(x):
        return (math.comb(r1, x) * math.comb(n - r1, c1 - x)) / math.comb(n, c1)
    return sum(pmf(x) for x in range(a, hi + 1))


def match(A, B):
    """L-4: within instrument_id, pass 1 identical normalised act_id, pass 2 closest adoption dates within ±90 d."""
    pairs, usedA, usedB = [], set(), set()
    byinst = defaultdict(lambda: ([], []))
    for i, r in enumerate(A):
        byinst[r["instrument_id"]][0].append(i)
    for j, r in enumerate(B):
        byinst[r["instrument_id"]][1].append(j)
    how = Counter()
    for inst, (ia, ib) in byinst.items():
        for i in ia:
            for j in ib:
                if j in usedB or i in usedA:
                    continue
                if norm(A[i]["act_id"]) == norm(B[j]["act_id"]):
                    pairs.append((i, j)); usedA.add(i); usedB.add(j); how["act_id"] += 1
                    break
        cands = []
        for i in ia:
            if i in usedA:
                continue
            for j in ib:
                if j in usedB:
                    continue
                gap = abs((d(A[i]["adoption_date"]) - d(B[j]["adoption_date"])).days)
                if gap <= 90:
                    cands.append((gap, i, j))
        for gap, i, j in sorted(cands):
            if i in usedA or j in usedB:
                continue
            pairs.append((i, j)); usedA.add(i); usedB.add(j); how["date"] += 1
    unA = [i for i in range(len(A)) if i not in usedA]
    unB = [j for j in range(len(B)) if j not in usedB]
    return pairs, unA, unB, how


def conservative(ca, cb):
    if ca == "cannot judge" or cb == "cannot judge":
        return "cannot judge"
    return ca if ORDER[ca] <= ORDER[cb] else cb


def cons_stack(sa, sb):
    if sa == "cannot judge" or sb == "cannot judge":
        return "cannot judge"
    return "yes" if sa == "yes" and sb == "yes" else "no"


# ----------------------------------------------------------------------------------------------------------------
A, B = load(D, "ledger_A.csv"), load(D, "ledger_B.csv")
IA = {r["instrument_id"]: r["history_access"] for r in load(D, "instruments_A.csv")}
IB = {r["instrument_id"]: r["history_access"] for r in load(D, "instruments_B.csv")}
SA, SB = load(D, "stack_B_A.csv"), load(D, "stack_B_B.csv")
BE = load(D, "B_events.csv")

# ---- sanity
for name, L in (("A", A), ("B", B)):
    for r in L:
        assert WIN[0] <= d(r["adoption_date"]) <= WIN[1], (name, r["act_id"], r["adoption_date"])
        assert r["domain"] == r["instrument_id"][0] and r["domain"] in "SL", (name, r["act_id"])
        assert r["instrument_id"] in ALL, (name, r["instrument_id"])
        assert r["class"] in CLASSES, (name, r["act_id"], r["class"])
        assert r["stack"] in STACK, (name, r["act_id"], r["stack"])
    ids = [r["event_id"] for r in L]
    assert len(ids) == len(set(ids))
assert set(IA) == set(IB) == ALL, (set(IA) ^ ALL, set(IB) ^ ALL)
assert all(v in ("full", "partial", "none") for v in list(IA.values()) + list(IB.values()))
assert len(BE) == N_B
vl_acts = [r["act_id"] for r in BE if r["instrument_id"] in VL_INST]
sp_acts = [r["act_id"] for r in BE if r["instrument_id"] not in VL_INST]
assert len(vl_acts) == 8 and len(sp_acts) == 27
for name, S in (("A", SA), ("B", SB)):
    assert len(S) == 51, (name, len(S))
    keys = Counter((r["act_id"], r["domain"]) for r in S)
    assert all(v == 1 for v in keys.values()), (name, [k for k, v in keys.items() if v > 1])
    for a in vl_acts:
        assert all((a, dom) in keys for dom in "BSL"), (name, a)
    for a in sp_acts:
        assert (a, "B") in keys and (a, "S") not in keys and (a, "L") not in keys, (name, a)
    assert all(r["stack"] in STACK for r in S)
print(f"ledger sizes: n_A={len(A)} n_B={len(B)}  (A: L {sum(r['domain']=='L' for r in A)}, S {sum(r['domain']=='S' for r in A)};"
      f" B: L {sum(r['domain']=='L' for r in B)}, S {sum(r['domain']=='S' for r in B)})")
print("sanity: window, domains, classes, stack values, 51 stack_B rows joined on act_id+domain, 8 VL x 3 + 27: OK")

# ---- access (L-2, L-3)
noneL = sorted(i for i in SEED_L if IA[i] == "none" and IB[i] == "none")
noneS = sorted(i for i in SEED_S if IA[i] == "none" and IB[i] == "none")
limitedL, limitedS = len(noneL) >= 8, len(noneS) >= 6
tab = Counter()
for i in sorted(SEED):
    tab[(i[0], IA[i], IB[i])] += 1
print(f"\naccess none/none: L {len(noneL)}/22 {noneL} (limited={limitedL}, threshold 8); S {len(noneS)}/16 {noneS} (limited={limitedS}, threshold 6)")
print("access table (domain, A, B):", sorted(tab.items()))
print("additions access:", {i: (IA[i], IB[i]) for i in sorted(ADD_L | ADD_S) if IA[i] == "none" or IB[i] == "none"})
excluded = set(noneL) | set(noneS)        # L-2: instruments none for both raters excluded from the identification gate

# ---- matching over ALL events (so FULL can reuse it); gates over seed instruments minus excluded
pairs, unA, unB, how = match(A, B)
def in_set(r, insts):
    return r["instrument_id"] in insts
gate_inst = SEED - excluded
gp = [(i, j) for i, j in pairs if in_set(A[i], gate_inst)]
nA = sum(in_set(r, gate_inst) for r in A); nB = sum(in_set(r, gate_inst) for r in B)
M = len(gp)
ident = M / (nA + nB - M)
howg = Counter("act_id" if norm(A[i]["act_id"]) == norm(B[j]["act_id"]) else "date" for i, j in gp)
kc, poc = kappa([(A[i]["class"], B[j]["class"]) for i, j in gp], CLASSES)
print(f"\nGATE identification: M={M} ({dict(howg)}) n_A={nA} n_B={nB} -> {ident:.3f} (bar 0.80) {'PASS' if ident >= 0.8 else 'FAIL'}")
print(f"GATE kappa classes over {len(gp)} matched S+L pairs: {kc:.3f} (observed {poc:.3f}) (bar 0.60) {'PASS' if kc >= 0.6 else 'FAIL'}")
# kappa stack: matched pairs + 51 stack_B rows joined on act_id+domain
sb = {(r["act_id"], r["domain"]): r["stack"] for r in SB}
stack_pairs = [(A[i]["stack"], B[j]["stack"]) for i, j in gp] + [(r["stack"], sb[(r["act_id"], r["domain"])]) for r in SA]
ks, pos = kappa(stack_pairs, STACK)
print(f"GATE kappa stack over {len(stack_pairs)} rows ({len(gp)} pairs + 51): {ks:.3f} (observed {pos:.3f}) (bar 0.60) {'PASS' if ks >= 0.6 else 'FAIL'}")
print(f"   stack over matched pairs only: {Counter(stack_pairs[:len(gp)])}; stack_B rows: A {Counter(r['stack'] for r in SA)}, B {Counter(r['stack'] for r in SB)}")
gated = ident >= 0.8 and kc >= 0.6 and ks >= 0.6
print("ALL GATES PASS" if gated else "=> UNGATED")
# per-domain breakdown of the identification gate
for dom in "LS":
    pd = [(i, j) for i, j in gp if A[i]["domain"] == dom]
    na = sum(in_set(r, gate_inst) and r["domain"] == dom for r in A); nb = sum(in_set(r, gate_inst) and r["domain"] == dom for r in B)
    kd = kappa([(A[i]["class"], B[j]["class"]) for i, j in pd], CLASSES)[0]
    print(f"   domain {dom}: M={len(pd)} n_A={na} n_B={nb} ident={len(pd)/(na+nb-len(pd)):.3f} kappa_class={kd:.3f}")

# ---- lists, never reconciled
print("\nunmatched A (seed):", len([i for i in unA if in_set(A[i], gate_inst)]))
for i in unA:
    if in_set(A[i], gate_inst):
        print(f"   {A[i]['instrument_id']} {A[i]['act_id']} {A[i]['adoption_date']} {A[i]['class']} stack={A[i]['stack']}")
print("unmatched B (seed):", len([j for j in unB if in_set(B[j], gate_inst)]))
for j in unB:
    if in_set(B[j], gate_inst):
        print(f"   {B[j]['instrument_id']} {B[j]['act_id']} {B[j]['adoption_date']} {B[j]['class']} stack={B[j]['stack']}")
cd = [(A[i]["instrument_id"], A[i]["act_id"], A[i]["adoption_date"], A[i]["class"], B[j]["class"]) for i, j in gp if A[i]["class"] != B[j]["class"]]
print(f"class disagreements (seed pairs): {len(cd)}")
for x in cd:
    print("   ", x)
sd = [(A[i]["act_id"], A[i]["stack"], B[j]["stack"]) for i, j in gp if A[i]["stack"] != B[j]["stack"]]
sdB = [(r["act_id"], r["domain"], r["stack"], sb[(r["act_id"], r["domain"])]) for r in SA if r["stack"] != sb[(r["act_id"], r["domain"])]]
print("stack disagreements (pairs):", sd, "(stack_B):", sdB)
straddle = [(A[i]["act_id"], A[i]["adoption_date"], B[j]["adoption_date"]) for i, j in pairs if (d(A[i]["adoption_date"]) < WIN[0]) != (d(B[j]["adoption_date"]) < WIN[0])]
print("window-straddling pairs:", straddle)
print("date-matched pairs with different act_id:", [(A[i]["act_id"], B[j]["act_id"]) for i, j in pairs if norm(A[i]["act_id"]) != norm(B[j]["act_id"])])

# ---- calibration against L1
sys_argv_save = sys.argv
A1, B1 = load(D1, "ledger_A.csv"), load(D1, "ledger_B.csv")
p1, _, _, _ = match(A1, B1)
S1 = [(A1[i], B1[j]) for i, j in p1 if A1[i]["instrument_id"] in SEED_S]
N_S1 = len(S1)
E_S1 = [{norm(a["act_id"]), norm(b["act_id"])} for a, b in S1]
S_pairs = [(i, j) for i, j in gp if A[i]["domain"] == "S"]
N_S_spec = len(S_pairs)
new_ids = {norm(A[i]["act_id"]) for i, j in S_pairs} | {norm(B[j]["act_id"]) for i, j in S_pairs}
found = [e for e in E_S1 if e & new_ids]
print(f"\nCALIBRATION: N_S1={N_S1} (L1 matched seat events, non-VL) E_S1={[sorted(e)[0] for e in E_S1]}")
print(f"   N_S,specific={N_S_spec} {Counter(A[i]['instrument_id'] for i,j in S_pairs)}; |diff|={abs(N_S_spec-N_S1)} (bar <=3); E_S1 found={len(found)}/8 (bar >=5)")
print(f"   not found: {[sorted(e) for e in E_S1 if not (e & new_ids)]}")
calibrated = abs(N_S_spec - N_S1) <= 3 and len(found) >= 5
print("   =>", "CALIBRATED" if calibrated else "MISCALIBRATED")

# ---- count readouts
def readouts(insts, variant, pairs=pairs):
    ev = []
    for i, j in pairs:
        if not in_set(A[i], insts):
            continue
        cls = conservative(A[i]["class"], B[j]["class"])
        st = cons_stack(A[i]["stack"], B[j]["stack"])
        yr = min(d(A[i]["adoption_date"]), d(B[j]["adoption_date"])).year
        app = (A[i]["application_date"] or B[j]["application_date"] or "").strip()
        ev.append((A[i]["instrument_id"], cls, yr, st, A[i]["act_id"], app))
    Lev = [e for e in ev if e[0].startswith("L")]
    Sev = [e for e in ev if e[0].startswith("S")]
    nvl = 8 if variant == "V2" else 0
    # VL rows: China instruments B14, B15 (GB 44495/44496) excluded under CN0
    vl_in = [r for r in BE if r["instrument_id"] in VL_INST and not (variant == "CN0v2" and r["instrument_id"] in ("B14", "B15"))]
    if variant == "CN0v2":
        nvl = len(vl_in)
    NB = N_B if variant != "V0" else 27
    if variant == "CN0v2":
        NB = sum(1 for r in BE if r["instrument_id"] not in {f"B{i:02d}" for i in range(8, 16)})
    NL, NS = len(Lev) + nvl, len(Sev) + nvl
    def cls_stats(evs):
        judged = [e for e in evs if e[1] != "cannot judge"]
        mc = sum(e[1] in ("memory-or-crypto", "hardware-or-recert") for e in judged)
        h = sum(e[1] == "hardware-or-recert" for e in judged)
        return dict(n=len(evs), judged=len(judged), MC=mc, H=h, MC_ci=wilson(mc, len(judged)), H_ci=wilson(h, len(judged)),
                    classes=Counter(e[1] for e in evs))
    return dict(NB=NB, NL=NL, NS=NS, R_BL=NB / NL if NL else float("inf"), R_BL_ci=ratio_ci(NB, NL),
                R_BS=NB / NS if NS else float("inf"), R_BS_ci=ratio_ci(NB, NS),
                L=cls_stats(Lev), S=cls_stats(Sev), Lev=Lev, Sev=Sev)

acc = {i for i in SEED if IA[i] in ("full", "partial") and IB[i] in ("full", "partial")}
variants = {"V2 (primary)": (SEED, "V2"), "V1": (SEED, "V1"), "V0": (SEED, "V0"),
            "CN0": (SEED - CHINA_L - CHINA_S, "CN0v2"), "FULL": (ALL, "V2"), "ACC": (acc, "V2")}
print("\nvariant        N_B  N_L  N_S   R_BL [95%]          R_BS [95%]")
res = {}
for name, (insts, var) in variants.items():
    r = readouts(insts, var)
    res[name] = r
    # gate values for the variant's instrument set (FULL / ACC change them)
    gi = insts - excluded
    gpv = [(i, j) for i, j in pairs if in_set(A[i], gi)]
    nAv = sum(in_set(x, gi) for x in A); nBv = sum(in_set(x, gi) for x in B)
    idv = len(gpv) / (nAv + nBv - len(gpv))
    kcv = kappa([(A[i]["class"], B[j]["class"]) for i, j in gpv], CLASSES)[0]
    print(f"{name:13s} {r['NB']:4d} {r['NL']:4d} {r['NS']:4d}  {r['R_BL']:5.2f} [{r['R_BL_ci'][0]:.2f}, {r['R_BL_ci'][1]:.2f}]   "
          f"{r['R_BS']:5.2f} [{r['R_BS_ci'][0]:.2f}, {r['R_BS_ci'][1]:.2f}]   ident {idv:.3f} kappa {kcv:.3f}")

p = res["V2 (primary)"]
print(f"\nPRIMARY V2: N_L = {p['L']['n']} matched L seed + 8 = {p['NL']}; N_S = {p['S']['n']} + 8 = {p['NS']}; R_BL = {p['R_BL']:.3f}; R_BS = {p['R_BS']:.3f}")
print("L by instrument:", sorted(Counter(e[0] for e in p["Lev"]).items(), key=lambda x: -x[1]))
print("S by instrument:", sorted(Counter(e[0] for e in p["Sev"]).items()))
print(f"L classes (conservative): {dict(p['L']['classes'])}; MC_L = {p['L']['MC']}/{p['L']['judged']} = {p['L']['MC']/p['L']['judged']*100:.1f}% [{p['L']['MC_ci'][0]*100:.0f}, {p['L']['MC_ci'][1]*100:.0f}]; H_L = {p['L']['H']} [{p['L']['H_ci'][0]*100:.0f}, {p['L']['H_ci'][1]*100:.0f}]")
print(f"S classes (conservative): {dict(p['S']['classes'])}; MC_S = {p['S']['MC']}/{p['S']['judged']} = {p['S']['MC']/p['S']['judged']*100:.1f}% [{p['S']['MC_ci'][0]*100:.0f}, {p['S']['MC_ci'][1]*100:.0f}]")
yrs = range(2016, 2027)
yB = Counter(d(r["adoption_date"]).year for r in BE)
print("per-year B (35):      ", [yB.get(y, 0) for y in yrs], sum(yB.values()))
yL = Counter(e[2] for e in p["Lev"]); yS = Counter(e[2] for e in p["Sev"])
print("per-year L specific:  ", [yL.get(y, 0) for y in yrs], sum(yL.values()))
print("per-year S specific:  ", [yS.get(y, 0) for y in yrs], sum(yS.values()))
yLa = Counter((d(e[5]).year if e[5] else e[2]) for e in p["Lev"])
print("L by application year (fallback adoption):", [yLa.get(y, 0) for y in yrs])
print("union (either rater) L seed:", sum(r["domain"] == "L" and in_set(r, gate_inst) for r in A) + sum(B[j]["domain"] == "L" and in_set(B[j], gate_inst) for j in unB),
      " S seed:", sum(r["domain"] == "S" and in_set(r, gate_inst) for r in A) + sum(B[j]["domain"] == "S" and in_set(B[j], gate_inst) for j in unB))
for name, L in (("A", A), ("B", B)):
    for dom in "LS":
        rows = [r for r in L if r["domain"] == dom and in_set(r, gate_inst)]
        print(f"rater {name} own {dom} (seed): {len(rows)} {dict(Counter(r['class'] for r in rows))} stack {dict(Counter(r['stack'] for r in rows))}")
gb_matched = [e for e in p["Lev"] if e[0] in CHINA_L] + [e for e in p["Sev"] if e[0] in CHINA_S]
print("matched events on GB (China) seeds:", gb_matched)
full = res["FULL"]
print(f"FULL adds L {full['L']['n'] - p['L']['n']} (by instrument: {sorted(Counter(e[0] for e in full['Lev'] if e[0] in ADD_L).items(), key=lambda x:-x[1])}), S {full['S']['n'] - p['S']['n']}")

# ---- count decision (V2)
def count_verdict(r, limitedL):
    R, lo = r["R_BL"], r["R_BL_ci"][0]
    if not gated:
        return "UNGATED"
    if R >= 3 and lo > 1.5:
        return "UNCLEAR BY COUNT (ACCESS-LIMITED)" if limitedL else "SPECIFIC BY COUNT"
    if R < 1.5:
        return "NOT SPECIFIC BY COUNT"
    return "UNCLEAR BY COUNT"
def count_table_only(r):
    R, lo = r["R_BL"], r["R_BL_ci"][0]
    return "SPECIFIC BY COUNT" if (R >= 3 and lo > 1.5) else ("NOT SPECIFIC BY COUNT" if R < 1.5 else "UNCLEAR BY COUNT")
print(f"\nCOUNT verdict (V2): {count_verdict(p, limitedL)}   [table without gates: {count_table_only(p)}; access-limited L: {limitedL}]")

# ---- stack readouts
sa = {(r["act_id"], r["domain"]): r["stack"] for r in SA}
spec_B = [(a, cons_stack(sa[(a, 'B')], sb[(a, 'B')])) for a in sp_acts]
jB = [x for x in spec_B if x[1] != "cannot judge"]; kB = sum(x[1] == "yes" for x in jB); nB_ = len(jB)
jL = [e for e in p["Lev"] if e[3] != "cannot judge"]; kL = sum(e[3] == "yes" for e in jL); nL_ = len(jL)
jS = [e for e in p["Sev"] if e[3] != "cannot judge"]; kS = sum(e[3] == "yes" for e in jS); nS_ = len(jS)
print(f"\nSTACK specific (conservative yes): B {kB}/{nB_} = {kB/nB_*100:.0f}% [{wilson(kB,nB_)[0]*100:.0f}, {wilson(kB,nB_)[1]*100:.0f}];"
      f" L {kL}/{nL_} [{wilson(kL,nL_)[0]*100:.0f}, {wilson(kL,nL_)[1]*100:.0f}]; S {kS}/{nS_} [{wilson(kS,nS_)[0]*100:.0f}, {wilson(kS,nS_)[1]*100:.0f}]")
print("   B yes:", [a for a, s in spec_B if s == "yes"])
print("   B no:", [a for a, s in spec_B if s == "no"], " cannot judge:", [a for a, s in spec_B if s == "cannot judge"])
print(f"   Fisher one-sided B>L: p = {fisher_one_sided(kB, nB_ - kB, kL, nL_ - kL):.2e}")
for dom in "BSL":
    rows = [(a, cons_stack(sa[(a, dom)], sb[(a, dom)])) for a in vl_acts]
    print(f"   VL stack rated for domain {dom}: {sum(s=='yes' for _, s in rows)}/8 yes: {[a for a, s in rows if s=='yes']}")
# any stack yes anywhere in L or S, either rater, any instrument
print("   any L/S 'yes' or 'cannot judge' by either rater (all instruments):",
      [(r["instrument_id"], r["act_id"], r["stack"]) for r in A + B if r["stack"] != "no"])
# kind decision with L1B-D1
def kind_verdict():
    if not gated:
        return "UNGATED"
    if kB >= 3 and kL <= 1 and kS <= 1:
        return "STACK-SPECIFIC"
    if kL >= 2 or (nL_ >= 10 and kL / nL_ >= kB / nB_):
        return "NOT STACK-SPECIFIC"
    return "UNCLEAR IN KIND"
rows_met = []
if kB >= 3 and kL <= 1 and kS <= 1: rows_met.append("STACK-SPECIFIC")
if kL >= 2 or (nL_ >= 10 and kL / nL_ >= kB / nB_): rows_met.append("NOT STACK-SPECIFIC")
print(f"KIND verdict: {kind_verdict()}   [rows met without gates: {rows_met or ['UNCLEAR IN KIND']}; overlap: {len(rows_met) > 1}]")

# ---- exploratory: one change per instrument per adoption date (parallel-series supplements collapsed)
def collapse(evs):
    return len({(e[0], e[2], e[4] and None) for e in evs}) if False else len({(e[0], min_date[e[4]]) for e in evs})
min_date = {}
for i, j in pairs:
    min_date[A[i]["act_id"]] = min(A[i]["adoption_date"], B[j]["adoption_date"])
L_coll = len({(e[0], min_date[e[4]]) for e in p["Lev"]})
B_coll = len({(r["instrument_id"], r["adoption_date"]) for r in BE if r["instrument_id"] not in VL_INST})
VL_coll = len({(r["instrument_id"], r["adoption_date"]) for r in BE if r["instrument_id"] in VL_INST})
print(f"\nEXPLORATORY collapse (one change per instrument per adoption date): L specific {p['L']['n']} -> {L_coll}; B specific 27 -> {B_coll}; VL 8 -> {VL_coll};"
      f" R_BL (session form, VL kept at 8) = {(B_coll+8)/(L_coll+8):.2f}; with VL collapsed too = {(B_coll+VL_coll)/(L_coll+VL_coll):.2f}")

# ---- reviewer EXPLORATORY readings (not pre-registered; written after the files were read; none deciding)
print("\n=== exploratory (reviewer; not pre-registered) ===")
nA_L = sum(r["domain"] == "L" and in_set(r, SEED_L) for r in A); nB_L = sum(r["domain"] == "L" and in_set(r, SEED_L) for r in B)
union_L = nA_L + nB_L - p["L"]["n"]
print(f"R_BL under every counting of the two ledgers: matched {N_B/(p['L']['n']+8):.2f}; A alone {N_B/(nA_L+8):.2f}; B alone {N_B/(nB_L+8):.2f};"
      f" union {N_B/(union_L+8):.2f}; L collapsed to instrument-dates with B as counted {N_B/(L_coll+8):.2f}; both collapsed {(B_coll+8)/(L_coll+8):.2f};"
      f" FULL {res['FULL']['R_BL']:.2f}  -> the 3x row is out of reach of this data")
cat_only = [r["act_id"] for r in BE if "catalogue entry only" in r["what_changed"]]
yesB = [a for a, s in spec_B if s == "yes"]
k1 = len([a for a in yesB if a not in cat_only]); n1 = nB_ - len([a for a in sp_acts if a in cat_only])
iec = [a for a in sp_acts if a.startswith("IEC 61851")]
k2 = len([a for a in yesB if a not in cat_only and a not in iec]); n2 = n1 - len(iec)
print(f"B stack-yes events judged from a catalogue entry only (class 'cannot judge' in L1): {len([a for a in yesB if a in cat_only])} {[a for a in yesB if a in cat_only]}")
print(f"k_B without catalogue-only events: {k1}/{n1} [{wilson(k1,n1)[0]*100:.0f}, {wilson(k1,n1)[1]*100:.0f}], Fisher p = {fisher_one_sided(k1, n1-k1, kL, nL_-kL):.1e};"
      f" also without the three IEC 61851 charging-communication editions: {k2}/{n2} [{wilson(k2,n2)[0]*100:.0f}, {wilson(k2,n2)[1]*100:.0f}], p = {fisher_one_sided(k2, n2-k2, kL, nL_-kL):.1e}")
linux = [a for a in yesB if a in ("32023R1542", "32024R1257", "32025R1707")]
print(f"Linux-class-forcing subset of POSITION §1 among the 27 specific B events (crypto / authenticated update / data retention with access / OTA): {len(linux)}/27 {linux}"
      f" (R155-00 and R156-00 are vehicle-level, rated yes for all three domains); the other {kB-len(linux)} stack-yes events name telemetry, charging communication or data read-out")
late = {dom: sum(v for y, v in c.items() if y >= 2025) for dom, c in (("B", yB), ("L", yL), ("S", yS))}
print(f"events adopted 2025-2026: B {late['B']}/35, L specific {late['L']}/40, S specific {late['S']}/6")

# ---- compare with l1b.json
try:
    J = json.load(open(f"{D}/l1b.json"))
    print("\nl1b.json top keys:", list(J.keys()))
    def walk(o, pre=""):
        if any(t in pre for t in ("per_year", "access", "by_instrument", "unmatched", "disagreements", ".own", "ledger_sizes", "by_jurisdiction", "class_", "MC_", "H_", "stack_vehicle", "cannot_judge", "notes", "tags", "preregistration", "straddling", "matched_by")):
            return
        if isinstance(o, dict):
            for k, v in o.items():
                walk(v, pre + "." + k)
        elif isinstance(o, (int, float, str)) and not isinstance(o, bool):
            if any(t in pre for t in ("identification", "kappa", "N_", "R_", "fisher", "k_", "n_", "verdict", "calibrat")) and not isinstance(o, str):
                print(f"   {pre} = {o}")
            elif "verdict" in pre or "status" in pre:
                print(f"   {pre} = {o}")
    walk(J)
except Exception as e:
    print("l1b.json not read:", e)
