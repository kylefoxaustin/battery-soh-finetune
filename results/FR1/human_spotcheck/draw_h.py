"""Reviewer draw of the FR1 human spot-check subset (D-3 / D-4). Prints NO rating content:
only case IDs, NHTSA IDs and document links. Stratification uses rater A's item-3 category
collapsed to the three kappa strata; the stratum of each drawn case is NOT written anywhere
the human rater can see."""
import csv, json, sys
import numpy as np

rows = [r for r in csv.DictReader(open('ratings_A.csv')) if r['list'] == 'PE']
man = json.load(open('rater_A_documents.json'))['cases']


def stratum(w):
    w = w.strip().lower()
    if 'cannot' in w: return None
    if w.startswith('<=1') or w.startswith('≤'): return 'S1'
    if w.startswith('(1,') or w.startswith('(40,'): return 'S2'   # (1,40] and (40,80] -> (1,80]
    if w.startswith('(80,') or w.startswith('>700') or w.startswith('> 700'): return 'S3'
    raise ValueError(w)

by = {'S1': [], 'S2': [], 'S3': []}
for r in rows:
    s = stratum(r['item3_window'])
    if s: by[s].append(r['case'])
for k in by: by[k].sort()
print('stratum sizes (counts only):', {k: len(v) for k, v in by.items()})

rng = np.random.default_rng(3)
drawn = []
for k in ('S1', 'S2', 'S3'):
    pool = by[k]
    n = min(5, len(pool))
    pick = list(rng.choice(pool, n, replace=False))
    drawn += pick
drawn = [str(x) for x in drawn]
order = list(rng.permutation(len(drawn)))
presented = [drawn[i] for i in order]      # shuffled so strata are not recoverable from position

# key file (reviewer-only, NOT to be shared): which stratum each case came from
with open('spotcheck_key_REVIEWER_ONLY.json', 'w') as f:
    json.dump({c: next(k for k, v in by.items() if c in v) for c in drawn}, f, indent=1)

with open('spotcheck_cases.json', 'w') as f:
    json.dump({'seed': 3, 'rule': '5 per kappa stratum of rater A item 3, shuffled; strata withheld',
               'cases': presented}, f, indent=1)

print('presented order:')
for c in presented:
    m = man[c]
    docs = '; '.join(f"[{d['summary']}]({d['url']})" for d in m['docs'])
    res = '; '.join((f"[ODI résumé]({x})" if isinstance(x,str) else f"[ODI {x.get('summary','résumé')}]({x.get('url','')})") for x in m.get('resume', [])) if m.get('resume') else ''
    print(f"| {c} | {m['nhtsa']} | https://www.nhtsa.gov/recalls?nhtsaId={m['nhtsa'].replace('-', '')} | {docs} {('| ' + res) if res else ''} |")
