#!/usr/bin/env python3
"""FR1 stage-2 analysis: inter-rater agreement and pre-event-window fractions.

Implements results/FR1/FR1_preregistration.md sections 4.3, 5 and 6 exactly, then a clearly
separated EXPLORATORY section (post hoc, UNGATED, non-deciding) that re-codes "not observable in
field data" from each rater's own free text.

Every rating is DERIVED-judgemental. Source of all rated documents: NHTSA, public domain.

Usage: python3 analysis/FR1_agreement.py  (from the repo root)
Writes results/FR1/fr1.json and prints the tables used in results_FR1.md.
"""
import csv, json, math, re, collections, datetime

ROOT = 'results/FR1'
WIN = ['<=1 s', '(1,40] s', '(40,80] s', '(80,700] s', '>700 s']          # ordinal 0..4
WIN3 = {0: '<=1 s', 1: '(1,80] s', 2: '(1,80] s', 3: '>80 s', 4: '>80 s'}  # kappa collapse
CAUSES = ['transient electrical', 'thermal cycling or thermal overload', 'manufacturing or component defect',
          'software or calibration', 'unknown / mixed']


def norm_win(s):
    t = re.sub(r'\s+', '', s.strip().lower())
    m = {'<=1s': 0, '≤1s': 0, '(1,40]s': 1, '(40,80]s': 2, '(80,700]s': 3, '>700s': 4, 'cannotjudge': None}
    if t not in m:
        raise ValueError(f'unknown window label {s!r}')
    return m[t]


def norm_cause(s):
    t = s.strip().lower()
    for c in CAUSES:
        if t.startswith(c.split(' ')[0]):
            return c
    raise ValueError(s)


def norm_flag(s):
    t = s.strip().lower()
    return {'yes': True, 'no': False, 'n/a': None, 'na': None, '': None}[t]


def load(r):
    out = {}
    for row in csv.DictReader(open(f'{ROOT}/ratings_{r}.csv')):
        out[row['case']] = dict(
            list=row['list'], win=norm_win(row['item3_window']), cause=norm_cause(row['item1_cause_type']),
            evidence=row['item2_evidence'].strip(), conf=row['item4_confidence'].strip().lower(),
            f_nocause=norm_flag(row['item5_no_cause_stated']), f_sw=norm_flag(row['item5_software_only']),
            f_oos=norm_flag(row['item5_component_out_of_scope']),
            signals=row['item3_signals_and_rate'], note=row['rater_note'])
    return out


def wilson(k, n, z=1.959964):
    if n == 0:
        return (float('nan'), float('nan'), float('nan'))
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (p, c - h, c + h)


def kappa(pairs):
    """Cohen's kappa over (a, b) label pairs."""
    pairs = [(a, b) for a, b in pairs if a is not None and b is not None]
    n = len(pairs)
    if n == 0:
        return float('nan'), 0, float('nan')
    labels = sorted(set(a for a, _ in pairs) | set(b for _, b in pairs), key=str)
    po = sum(a == b for a, b in pairs) / n
    pa = collections.Counter(a for a, _ in pairs)
    pb = collections.Counter(b for _, b in pairs)
    pe = sum(pa[l] * pb[l] for l in labels) / (n * n)
    k = (po - pe) / (1 - pe) if pe < 1 else float('nan')
    return k, n, po


A, B = load('A'), load('B')
cases = sorted(set(A) & set(B))
assert len(cases) == 150 and set(A) == set(B), (len(cases), set(A) ^ set(B))
screen = json.load(open(f'{ROOT}/FR1_screen.json'))
meta = {c['case']: c for c in screen['cases']}
meta['PE076'] = dict(case='PE076', nhtsa_id='25V-811', rcdate='20251124', groups=['HV BMS / contactor unit',
                     'Traction inverter / motor controller'], cluster='C53', mfgname='Bentley Motors, Inc.')
for c in screen['base_rate']:
    meta[c['case']] = c

PE = [c for c in cases if c.startswith('PE')]
BR = [c for c in cases if c.startswith('BR')]
assert len(PE) == 75 and len(BR) == 75 and 'PE006' not in PE and 'PE076' in PE

# ---------------------------------------------------------------- 4.3 exclusions
excl = {}
single_flags = collections.Counter()
for c in cases:
    a, b = A[c], B[c]
    flags = ['no_cause'] if a['f_nocause'] and b['f_nocause'] else []
    if c.startswith('PE'):
        if a['f_sw'] and b['f_sw']:
            flags.append('software_only')
        if a['f_oos'] and b['f_oos']:
            flags.append('out_of_scope')
    for name, fa, fb in (('no_cause', a['f_nocause'], b['f_nocause']), ('software_only', a['f_sw'], b['f_sw']),
                         ('out_of_scope', a['f_oos'], b['f_oos'])):
        if (fa or fb) and not (fa and fb):
            single_flags[name] += 1
    excl[c] = flags
excluded = {c for c in cases if excl[c]}
excl_counts = collections.Counter(f for c in cases for f in excl[c])

# ---------------------------------------------------------------- 5 readouts
def fractions(ids, reading, denom_rule='strict'):
    """reading(c) -> ordinal or None. strict: drop None; cj_low: None -> 0."""
    vals = []
    for c in ids:
        if c in excluded:
            continue
        v = reading(c)
        if v is None:
            if denom_rule == 'cj_low':
                v = 0
            else:
                continue
        vals.append(v)
    n = len(vals)
    return dict(n=n, gt80=wilson(sum(v >= 3 for v in vals), n), gt40=wilson(sum(v >= 2 for v in vals), n),
                gt1=wilson(sum(v >= 1 for v in vals), n),
                dist={WIN[i]: sum(v == i for v in vals) for i in range(5)})


def conservative(c):
    a, b = A[c]['win'], B[c]['win']
    if a is None or b is None:
        return None
    return min(a, b)


readouts = {}
for label, ids in (('PE', PE), ('BR', BR)):
    readouts[label] = dict(
        conservative=fractions(ids, conservative),
        conservative_cj_low=fractions(ids, conservative, 'cj_low'),
        raterA=fractions(ids, lambda c: A[c]['win']),
        raterB=fractions(ids, lambda c: B[c]['win']),
        cannot_judge_either=sum(1 for c in ids if c not in excluded and (A[c]['win'] is None or B[c]['win'] is None)),
    )

# ---------------------------------------------------------------- 5 agreement gate
def k3(ids):
    return kappa([(WIN3.get(A[c]['win']), WIN3.get(B[c]['win'])) for c in ids])


def k6(ids):
    return kappa([(A[c]['win'] if A[c]['win'] is not None else 'cj', B[c]['win'] if B[c]['win'] is not None else 'cj')
                  for c in ids])


def k1(ids):
    return kappa([(A[c]['cause'], B[c]['cause']) for c in ids])


PE_post = [c for c in PE if c not in excluded]
agreement = {
    'gate_k3_all_rated': k3(cases), 'k3_PE': k3(PE), 'k3_BR': k3(BR), 'k3_PE_after_exclusions': k3(PE_post),
    'k6_all': k6(cases), 'k6_PE': k6(PE), 'k1_cause_all': k1(cases), 'k1_cause_PE': k1(PE),
}
# cross-tab of the collapsed categories, all rated cases
xt = collections.Counter((WIN3.get(A[c]['win'], 'cj'), WIN3.get(B[c]['win'], 'cj')) for c in cases)

# ---------------------------------------------------------------- 5 also reported
by_group, by_year = collections.defaultdict(list), collections.defaultdict(list)
for c in PE_post:
    v = conservative(c)
    if v is None:
        continue
    for g in meta[c]['groups']:
        by_group[g].append(v)
    by_year[meta[c]['rcdate'][:4]].append(v)


def frac_tab(d):
    return {k: dict(n=len(v), gt80=round(sum(x >= 3 for x in v) / len(v), 3), gt40=round(sum(x >= 2 for x in v) / len(v), 3),
                    gt1=round(sum(x >= 1 for x in v) / len(v), 3)) for k, v in sorted(d.items())}


# one case per cluster: earliest campaign (by rcdate) of each cluster among post-exclusion PE
first_in_cluster = {}
for c in sorted(PE_post, key=lambda c: meta[c]['rcdate']):
    first_in_cluster.setdefault(meta[c]['cluster'], c)
cluster_ids = sorted(first_in_cluster.values())
one_per_cluster = fractions(cluster_ids, conservative)

evidence = {r: collections.Counter(R[c]['evidence'] for c in PE_post) for r, R in (('A', A), ('B', B))}
cause_dist = {r: collections.Counter(R[c]['cause'] for c in PE_post) for r, R in (('A', A), ('B', B))}

disagreements = []
for c in cases:
    a, b = A[c]['win'], B[c]['win']
    if (a is None) != (b is None) or (a is not None and a != b):
        disagreements.append(dict(case=c, nhtsa=meta[c]['nhtsa_id'], A=WIN[a] if a is not None else 'cannot judge',
                                  B=WIN[b] if b is not None else 'cannot judge', excluded=bool(excl[c]),
                                  A_signals=A[c]['signals'][:140], B_signals=B[c]['signals'][:140]))

# ---------------------------------------------------------------- 6 decision (conservative reading, PE)
pe = readouts['PE']['conservative']
n_pe = pe['n']
gate_k = agreement['gate_k3_all_rated'][0]
if gate_k < 0.6 or n_pe < 10:
    verdict = 'UNGATED'
elif pe['gt80'][0] >= 0.50 and pe['gt80'][1] > 0.20:
    verdict = 'RETENTION IS A NECESSITY'
elif pe['gt40'][0] < 0.20:
    verdict = 'RETENTION IS A CONVENIENCE'
else:
    verdict = 'UNCLEAR'
# the same table applied to each alternative kappa reading, so the reader can see whether any reading passes the gate
gate_alternatives = {k: (round(v[0], 3), v[1]) for k, v in agreement.items() if k.startswith('k3')}

# ---------------------------------------------------------------- EXPLORATORY (post hoc, UNGATED, non-deciding)
# Re-code "not observable in field data at any window" from each rater's own free text. The two raters' written
# conventions mapped this situation to opposite ends of the scale (A: >700 s; B: <=1 s). The regexes below were
# written after reading both conventions files and are disclosed here; this section decides nothing.
NOT_OBS_A = re.compile(r'not observable|no in-vehicle signal|no field data|none;', re.I)
NOT_OBS_B = re.compile(r'static|teardown|snapshot|inspection|cause is (a |the )?(fastener|bracket|weld|torque|wrong|mis)', re.I)


def not_obs(r, c):
    R, pat = (A, NOT_OBS_A) if r == 'A' else (B, NOT_OBS_B)
    txt = R[c]['signals'] + ' ' + R[c]['note']
    return bool(pat.search(txt))


recode = {}
for c in cases:
    recode[c] = dict(A_notobs=not_obs('A', c) and A[c]['win'] == 4,
                     B_notobs=not_obs('B', c) and B[c]['win'] == 0)
xt_notobs = collections.Counter((recode[c]['A_notobs'], recode[c]['B_notobs']) for c in cases)
both_obs = [c for c in cases if not recode[c]['A_notobs'] and not recode[c]['B_notobs']]
explor = {
    'regex_A': NOT_OBS_A.pattern, 'regex_B': NOT_OBS_B.pattern,
    'crosstab_A_notobs_x_B_notobs': {f'A={a},B={b}': n for (a, b), n in sorted(xt_notobs.items())},
    'k3_on_cases_neither_flagged_notobs': k3(both_obs),
    'k3_PE_neither_flagged': k3([c for c in both_obs if c.startswith('PE')]),
    'n_both_obs': len(both_obs),
    'PE_fractions_conservative_on_observable_cases': fractions([c for c in PE if c in both_obs], conservative),
    'PE_fractions_A_on_its_observable_cases': fractions([c for c in PE if not recode[c]['A_notobs']], lambda c: A[c]['win']),
    'PE_fractions_B_on_its_observable_cases': fractions([c for c in PE if not recode[c]['B_notobs']], lambda c: B[c]['win']),
    # four-state kappa: treat "not observable" as its own category, using each rater's own marking
    'k4_notobs_as_category_all': kappa([
        ('NO' if recode[c]['A_notobs'] else WIN3.get(A[c]['win']),
         'NO' if recode[c]['B_notobs'] else WIN3.get(B[c]['win'])) for c in cases]),
}

out = dict(
    generated=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'),
    provenance='DERIVED-judgemental ratings; NHTSA, public domain',
    n_cases=len(cases), n_PE=len(PE), n_BR=len(BR),
    exclusions=dict(both_rater_flags=dict(excl_counts), n_excluded=len(excluded),
                    excluded_cases=sorted(excluded), single_rater_flags_reported_not_excluding=dict(single_flags),
                    n_PE_after_exclusions=len(PE_post)),
    readouts=readouts, agreement={k: dict(kappa=v[0], n=v[1], observed_agreement=v[2]) for k, v in agreement.items()},
    crosstab_collapsed_A_x_B={f'A={a}|B={b}': n for (a, b), n in sorted(xt.items(), key=str)},
    by_group=frac_tab(by_group), by_year=frac_tab(by_year), one_per_cluster=one_per_cluster,
    evidence={r: dict(v) for r, v in evidence.items()}, cause_dist={r: dict(v) for r, v in cause_dist.items()},
    disagreements=disagreements, n_disagreements=len(disagreements),
    decision=dict(verdict=verdict, gate_kappa_used=gate_k, gate_alternatives=gate_alternatives, n_PE_denominator=n_pe),
    exploratory_post_hoc_UNGATED=explor,
    deviations_applied=['D-1 list edits', 'D-2 branch blindness', 'D-3 disclosure (both raters are language-model sessions)',
                        'D-4 human subset drawn', 'D-5 human subset NOT rated (reviewer decision 2026-11-06)',
                        'D-6 rater B launched as a fresh-context sub-agent from the rater A session in a main-only clone (disclosed by B)'],
)
json.dump(out, open(f'{ROOT}/fr1.json', 'w'), indent=1, default=lambda o: dict(o) if isinstance(o, collections.Counter) else str(o))

# ---------------------------------------------------------------- print
def pf(t):
    return f'{100*t[0]:.0f} % [{100*t[1]:.0f}, {100*t[2]:.0f}]'

print('VERDICT:', verdict, '| gate kappa (3-way, all rated cases) =', round(gate_k, 3), '| PE denominator =', n_pe)
print('kappa alternatives:', gate_alternatives)
print('exclusions (both raters):', dict(excl_counts), '| excluded', len(excluded), '| PE after exclusions', len(PE_post))
print('single-rater flags (reported, not excluding):', dict(single_flags))
for label in ('PE', 'BR'):
    r = readouts[label]
    print(f'{label} conservative: n={r["conservative"]["n"]}  >80 s {pf(r["conservative"]["gt80"])}  >40 s {pf(r["conservative"]["gt40"])}  >1 s {pf(r["conservative"]["gt1"])}  dist={r["conservative"]["dist"]}')
    print(f'{label} rater A:      n={r["raterA"]["n"]}  >80 s {pf(r["raterA"]["gt80"])}  >40 s {pf(r["raterA"]["gt40"])}  >1 s {pf(r["raterA"]["gt1"])}')
    print(f'{label} rater B:      n={r["raterB"]["n"]}  >80 s {pf(r["raterB"]["gt80"])}  >40 s {pf(r["raterB"]["gt40"])}  >1 s {pf(r["raterB"]["gt1"])}')
    print(f'{label} cannot-judge by either (post-exclusion): {r["cannot_judge_either"]}; cj->low sensitivity >80 s {pf(r["conservative_cj_low"]["gt80"])}')
print('crosstab collapsed (A x B):', dict(xt))
print('kappa 6-way all:', round(agreement['k6_all'][0], 3), '| kappa cause all:', round(agreement['k1_cause_all'][0], 3), 'PE:', round(agreement['k1_cause_PE'][0], 3))
print('by group:', frac_tab(by_group)); print('by year:', frac_tab(by_year))
print('one per cluster: n', one_per_cluster['n'], '>80 s', pf(one_per_cluster['gt80']), '>40 s', pf(one_per_cluster['gt40']))
print('evidence A:', dict(evidence['A'])); print('evidence B:', dict(evidence['B']))
print('cause A:', dict(cause_dist['A'])); print('cause B:', dict(cause_dist['B']))
print('disagreements on item 3:', len(disagreements), 'of', len(cases))
print('--- EXPLORATORY (post hoc, UNGATED):')
print(' not-observable crosstab:', explor['crosstab_A_notobs_x_B_notobs'])
print(' kappa3 on cases neither flagged not-observable:', explor['k3_on_cases_neither_flagged_notobs'], '| PE only:', explor['k3_PE_neither_flagged'])
print(' kappa4 (not-observable as a category):', explor['k4_notobs_as_category_all'])
e = explor['PE_fractions_conservative_on_observable_cases']
print(f' PE conservative on observable cases: n={e["n"]} >80 s {pf(e["gt80"])} >40 s {pf(e["gt40"])} >1 s {pf(e["gt1"])} dist={e["dist"]}')
for r in ('A', 'B'):
    e = explor[f'PE_fractions_{r}_on_its_observable_cases']
    print(f' PE rater {r} on its own observable cases: n={e["n"]} >80 s {pf(e["gt80"])} >40 s {pf(e["gt40"])} >1 s {pf(e["gt1"])}')
