"""Reviewer re-derivation of L1 (pre-registration §5-6 with L-1, L-2, L-4). Own code; reads only the two ledgers
and the two instruments files. Usage: python3 -I l1_check.py <results/L1 dir>"""
import csv, json, math, re, sys
from collections import Counter, defaultdict
from datetime import date

D = sys.argv[1]
CLASSES = ["software-only", "memory-or-crypto", "hardware-or-recert", "cannot judge"]
ORDER = {"software-only": 0, "memory-or-crypto": 1, "hardware-or-recert": 2}
SEED_B = {f"B{i:02d}" for i in range(1, 36)}
SEED_S = {f"S{i:02d}" for i in range(1, 17)}
VEHICLE_LEVEL = {"B05", "B06", "B14", "B15"}
CHINA = {f"B{i:02d}" for i in range(8, 16)} | {"S14", "S15", "S16"}


def load(f):
    return list(csv.DictReader(open(f"{D}/{f}", encoding="utf-8")))


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


def kappa(pairs):
    n = len(pairs)
    po = sum(a == b for a, b in pairs) / n
    ca, cb = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    pe = sum(ca[c] * cb[c] for c in CLASSES) / (n * n)
    return (po - pe) / (1 - pe), po


def match(A, B):
    """Two passes within instrument_id: identical normalised act_id, then closest dates within ±90 d."""
    pairs, usedA, usedB = [], set(), set()
    byinst = defaultdict(lambda: ([], []))
    for i, r in enumerate(A):
        byinst[r["instrument_id"]][0].append(i)
    for j, r in enumerate(B):
        byinst[r["instrument_id"]][1].append(j)
    how = Counter()
    for inst, (ia, ib) in byinst.items():
        # pass 1
        for i in ia:
            for j in ib:
                if j in usedB or i in usedA:
                    continue
                if norm(A[i]["act_id"]) == norm(B[j]["act_id"]):
                    pairs.append((i, j)); usedA.add(i); usedB.add(j); how["act_id"] += 1
                    break
        # pass 2
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


def readouts(A, B, pairs, insts, variant):
    """variant: V2 (vehicle-level in both), V1 (B only), V0 (neither). insts: instrument set in play."""
    ev = []
    for i, j in pairs:
        inst = A[i]["instrument_id"]
        if inst not in insts:
            continue
        cls = conservative(A[i]["class"], B[j]["class"])
        yr = min(d(A[i]["adoption_date"]), d(B[j]["adoption_date"])).year
        ev.append((inst, cls, yr))
    vl = [e for e in ev if e[0] in VEHICLE_LEVEL]
    Bev = [e for e in ev if e[0].startswith("B")]
    Sev = [e for e in ev if e[0].startswith("S")]
    if variant == "V2":
        S_cnt = Sev + vl
        B_cnt = Bev
    elif variant == "V1":
        S_cnt, B_cnt = Sev, Bev
    elif variant == "V0":
        S_cnt = Sev
        B_cnt = [e for e in Bev if e[0] not in VEHICLE_LEVEL]
    NB, NS = len(B_cnt), len(S_cnt)
    judged = [e for e in B_cnt if e[1] != "cannot judge"]
    mc = sum(e[1] in ("memory-or-crypto", "hardware-or-recert") for e in judged)
    h = sum(e[1] == "hardware-or-recert" for e in judged)
    R = NB / NS if NS else float("inf")
    return dict(NB=NB, NS=NS, R=R, judged=len(judged), MC=mc, H=h,
                MC_f=mc / len(judged) if judged else float("nan"), MC_ci=wilson(mc, len(judged)),
                H_f=h / len(judged) if judged else float("nan"), H_ci=wilson(h, len(judged)),
                years_B=Counter(e[2] for e in B_cnt), years_S=Counter(e[2] for e in S_cnt),
                byinst_B=Counter(e[0] for e in B_cnt), classes_B=Counter(e[1] for e in B_cnt),
                n_vl=len(vl))


def verdict(r, limitedB, limitedS):
    NB, MCf, lb, R = r["NB"], r["MC_f"], r["MC_ci"][0], r["R"]
    vol = NB >= 11 and MCf >= 0.25 and lb > 0.10 and R >= 3
    stable = NB <= 5 or MCf < 0.10
    kill = stable or R < 1.5
    q = ""
    if limitedB and not limitedS:
        stable, kill = False, False  # cannot be established from a lower bound
        q = " (ACCESS-LIMITED, B)"
    elif limitedS and not limitedB:
        vol = False
        q = " (ACCESS-LIMITED, S)"
    elif limitedB and limitedS:
        vol = False; kill = stable; q = " (ACCESS-LIMITED, both)"
    v = "VOLATILE DOMAIN" if vol else ("STABLE DOMAIN" if stable else "UNCLEAR")
    return v + q, kill


A, B = load("ledger_A.csv"), load("ledger_B.csv")
IA = {r["instrument_id"]: r["history_access"] for r in load("instruments_A.csv")}
IB = {r["instrument_id"]: r["history_access"] for r in load("instruments_B.csv")}

# sanity: window, domains
for name, L in (("A", A), ("B", B)):
    for r in L:
        assert date(2016, 1, 1) <= d(r["adoption_date"]) <= date(2026, 12, 31), (name, r["act_id"])
        assert r["domain"] == r["instrument_id"][0], (name, r["act_id"])
        assert r["class"] in CLASSES, (name, r["act_id"], r["class"])
print(f"ledger sizes: n_A={len(A)} n_B={len(B)}")

pairs, unA, unB, how = match(A, B)
M = len(pairs)
ident = M / (len(A) + len(B) - M)
k, po = kappa([(A[i]["class"], B[j]["class"]) for i, j in pairs])
print(f"matched M={M} ({dict(how)}); identification={ident:.3f}; kappa={k:.3f} (observed {po:.3f})")
print("unmatched A:", [(A[i]["instrument_id"], A[i]["act_id"], A[i]["adoption_date"]) for i in unA])
print("unmatched B:", [(B[j]["instrument_id"], B[j]["act_id"], B[j]["adoption_date"]) for j in unB])
print("class disagreements:", [(A[i]["act_id"], A[i]["class"], B[j]["class"]) for i, j in pairs if A[i]["class"] != B[j]["class"]])
# per-domain gates
for dom in "BS":
    pd = [(i, j) for i, j in pairs if A[i]["domain"] == dom]
    nA = sum(r["domain"] == dom for r in A); nB = sum(r["domain"] == dom for r in B)
    kd = kappa([(A[i]["class"], B[j]["class"]) for i, j in pd])[0] if pd else float("nan")
    print(f"  domain {dom}: M={len(pd)} n_A={nA} n_B={nB} ident={len(pd)/(nA+nB-len(pd)):.3f} kappa={kd:.3f}")

# access-limited test
noneB = sum(IA[i] == "none" and IB[i] == "none" for i in SEED_B)
noneS = sum(IA[i] == "none" and IB[i] == "none" for i in SEED_S)
limitedB, limitedS = noneB >= 12, noneS >= 6
print(f"access none/none: B {noneB}/35 (limited={limitedB}); S {noneS}/16 (limited={limitedS})")
tab = Counter()
for i in SEED_B:
    tab[("B", IA[i], IB[i])] += 1
for i in SEED_S:
    tab[("S", IA[i], IB[i])] += 1
print("access table:", dict(tab))

seed = SEED_B | SEED_S
ALL = seed | {f"B{i}" for i in (36, 37)} | {f"S{i:02d}" for i in range(17, 27)}
acc = {i for i in seed if IA[i] in ("full", "partial") and IB[i] in ("full", "partial")}
variants = {
    "primary V2": (seed, "V2"), "V1": (seed, "V1"), "V0": (seed, "V0"),
    "CN0": (seed - CHINA, "V2"), "FULL": (ALL, "V2"), "ACC": (acc, "V2"),
}
print("\nvariant        N_B  N_S     R   judged  MC        H         verdict / kill")
for name, (insts, var) in variants.items():
    r = readouts(A, B, pairs, insts, var)
    v, kill = verdict(r, limitedB, limitedS)
    print(f"{name:13s} {r['NB']:4d} {r['NS']:4d} {r['R']:6.2f} {r['judged']:6d}  "
          f"{r['MC_f']*100:4.1f}% [{r['MC_ci'][0]*100:.1f},{r['MC_ci'][1]*100:.1f}]  "
          f"{r['H_f']*100:4.1f}% [{r['H_ci'][0]*100:.1f},{r['H_ci'][1]*100:.1f}]  {v} / kill={'FIRES' if kill else 'no'}")

p = readouts(A, B, pairs, seed, "V2")
print("\nper-year B:", [p["years_B"].get(y, 0) for y in range(2016, 2027)], "sum", sum(p["years_B"].values()))
print("per-year S(V2):", [p["years_S"].get(y, 0) for y in range(2016, 2027)], "sum", sum(p["years_S"].values()))
print("vehicle-level matched events:", p["n_vl"])
print("B by instrument:", sorted(p["byinst_B"].items(), key=lambda x: -x[1]))
print("B classes (conservative):", dict(p["classes_B"]))
print("B events 2023-2025:", sum(p["years_B"].get(y, 0) for y in (2023, 2024, 2025)))
cn = sum(1 for i, j in pairs if A[i]["instrument_id"] in CHINA)
print("China-only matched events:", cn)
# each rater's own counts (seed instruments)
for name, L in (("A", A), ("B", B)):
    Bs = [r for r in L if r["instrument_id"] in SEED_B]
    Ss = [r for r in L if r["instrument_id"] in SEED_S]
    jB = [r for r in Bs if r["class"] != "cannot judge"]
    mc = sum(r["class"] in ("memory-or-crypto", "hardware-or-recert") for r in jB)
    print(f"rater {name} own: B {len(Bs)} (MC {mc}/{len(jB)} = {mc/len(jB)*100:.1f}%), S {len(Ss)}")
print("union B:", len([r for r in A if r["domain"] == "B"]) + len([j for j in unB if B[j]["domain"] == "B"]),
      "union S(V2):", len([r for r in A if r["domain"] == "S"]) + len([j for j in unB if B[j]["domain"] == "S"]) + p["n_vl"])

# ---- compare with the session's l1.json where keys are findable
try:
    J = json.load(open(f"{D}/l1.json"))
    print("\nl1.json top keys:", list(J.keys())[:30])
except Exception as e:
    print("l1.json not read:", e)

# ---------------------------------------------------------------------------------------------------------------
# Reviewer EXPLORATORY readings (not pre-registered; written after the ledgers were read; none deciding)
# ---------------------------------------------------------------------------------------------------------------
print("\n=== exploratory (reviewer; not pre-registered) ===")
# (i) a confidence interval on R, treating the 51 matched seed events as a binomial split B vs S (V2)
nB, nS = p["NB"], p["NS"]
lo, hi = wilson(nB, nB + nS)
print(f"R = {nB}/{nS} = {nB/nS:.2f}; binomial (Wilson) 95% interval on R: [{lo/(1-lo):.2f}, {hi/(1-hi):.2f}]")
# (ii) split of the above-software domain-B events by what the raters' own lines name.
# Rule (written after reading the lines, so exploratory): `stack` if either rater's what_changed/note names a
# cryptographic, key-storage, update-authenticity, secure-communication, data-access-interface, data-storage /
# retention, telemetry or OTA requirement; `recert-or-function` if they name only re-approval / phase-out dates,
# new warning or monitoring functions, scope extensions, or test / verification / documentation requirements.
CODING = {
    "89 FR 104318": "recert-or-function",  # REESS protections, warnings, Part 561 documentation, compliance date
    "32023R1542": "stack",                 # BMS holds SoH data, read-only access interface, reset function
    "R155-00": "stack",                    # CSMS; secure communication / key storage on connected ECUs
    "R155-00-S3": "recert-or-function",    # scope extended to category L
    "R100-03": "recert-or-function",       # REESS warnings, isolation monitoring, phase-out of earlier series
    "R100-05": "recert-or-function",       # thermal-propagation verification, warning logic, documentation
    "R156-00": "stack",                    # SUMS; authenticity / integrity of updates, RXSWIN
    "R156-01": "recert-or-function",       # RXSWIN per approval, phase-out
    "32024R1257": "stack",                 # OBM monitors and EVP data obligations
    "32025R1707": "stack",                 # OBM data storage, OBD access, OTA transmission under R155, EVP format
}
above = [(A[i]["act_id"], conservative(A[i]["class"], B[j]["class"])) for i, j in pairs
         if A[i]["domain"] == "B" and A[i]["instrument_id"] in SEED_B
         and conservative(A[i]["class"], B[j]["class"]) in ("memory-or-crypto", "hardware-or-recert")]
assert {a for a, _ in above} == set(CODING), ({a for a, _ in above} ^ set(CODING))
stack = sum(CODING[a] == "stack" for a, _ in above)
print(f"above-software B events: {len(above)}; coded stack: {stack}, recert-or-function: {len(above)-stack}")
print(f"stack / judged = {stack}/{p['judged']} = {stack/p['judged']*100:.1f}% Wilson [{wilson(stack,p['judged'])[0]*100:.1f}, {wilson(stack,p['judged'])[1]*100:.1f}]")
print("stack events:", [a for a, _ in above if CODING[a] == "stack"])
# (iii) parallel supplements adopted as two documents for two series in force (counted twice under the rule)
DUP_B = {"R100-04-S1", "R100-04-S2"}; DUP_S = {"R16-08-S2"}
# (iv) scope extensions that do not touch an in-service M1 design
SCOPE = {"R100-03-S4", "R100-04-S1", "R100-04-S3", "R100-05-S1", "R155-00-S3"}
def count(excl):
    nb = sum(1 for i, j in pairs if A[i]["instrument_id"] in SEED_B and A[i]["act_id"] not in excl)
    ns = sum(1 for i, j in pairs if A[i]["instrument_id"] in SEED_S and A[i]["act_id"] not in excl)
    nvl = sum(1 for i, j in pairs if A[i]["instrument_id"] in VEHICLE_LEVEL and A[i]["act_id"] not in excl)
    jud = [(A[i], B[j]) for i, j in pairs if A[i]["instrument_id"] in SEED_B and A[i]["act_id"] not in excl
           and conservative(A[i]["class"], B[j]["class"]) != "cannot judge"]
    mc = sum(conservative(a["class"], b["class"]) != "software-only" for a, b in jud)
    return nb, ns + nvl, nb / (ns + nvl), mc, len(jud)
for name, excl in (("unique changes (parallel supplements once)", DUP_B | DUP_S), ("no scope-extension events", SCOPE)):
    nb, ns, r, mc, nj = count(excl)
    print(f"{name}: N_B {nb}, N_S(V2) {ns}, R {r:.2f}, MC {mc}/{nj} = {mc/nj*100:.1f}%")
