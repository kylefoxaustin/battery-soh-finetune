"""Independent re-derivation of the FR1 headline numbers from ratings_A.csv and ratings_B.csv.

Written from the pre-registration (sections 4.3, 5 and 6) only; it does not import or read analysis/FR1_agreement.py.
Usage (from the repo root): python3 -I results/FR1/review/rederive_FR1.py results/FR1
"""
import csv
import math
import sys
from collections import Counter

# Ordinal window categories; 'cannot judge' is None.
WIN = {'<=1': 0, '(1,40]': 1, '(40,80]': 2, '(80,700]': 3, '>700': 4}


def window(s):
    s = s.replace(' ', '').replace('s', '')  # '(1, 40] s' -> '(1,40]'
    return None if s == 'cannotjudge' else WIN[s]


def collapsed(w):  # <=1 s / (1,80] s / >80 s
    return None if w is None else (0 if w == 0 else 1 if w <= 2 else 2)


def yes(s):
    return s.strip().lower() == 'yes'


def load(path):
    rows = {}
    with open(path, newline='') as f:
        for r in csv.DictReader(f):
            rows[r['case']] = r
    return rows


def kappa(pairs):
    n = len(pairs)
    po = sum(a == b for a, b in pairs) / n
    ca, cb = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / n ** 2
    return (po - pe) / (1 - pe)


def wilson(k, n, z=1.959964):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return p, c - h, c + h


def pct(k, n):
    p, lo, hi = wilson(k, n)
    return f'{k}/{n} = {100 * p:.0f} % [{100 * lo:.0f}, {100 * hi:.0f}]'


def main(d):
    A, B = load(f'{d}/ratings_A.csv'), load(f'{d}/ratings_B.csv')
    assert set(A) == set(B) and len(A) == 150
    cases = sorted(A)
    lst = {c: A[c]['list'] for c in cases}
    assert all(B[c]['list'] == lst[c] for c in cases)

    flags = [('no cause stated', 'item5_no_cause_stated'),
             ('software-only', 'item5_software_only'),
             ('out of scope', 'item5_component_out_of_scope')]
    excluded = set()
    print('## Exclusions (both raters set the same flag)')
    for name, col in flags:
        both = {c for c in cases if yes(A[c][col]) and yes(B[c][col])}
        excluded |= both
        print(f'- {name}: {len(both)} (PE {sum(lst[c] == "PE" for c in both)})')
    print(f'- any flag: {len(excluded)} (PE {sum(lst[c] == "PE" for c in excluded)}, '
          f'BR {sum(lst[c] == "BR" for c in excluded)})')

    wa = {c: window(A[c]['item3_window']) for c in cases}
    wb = {c: window(B[c]['item3_window']) for c in cases}

    print('\n## Kappa, item 3 collapsed, cases both raters rated with a category')
    for label, sel in [('all', cases), ('PE', [c for c in cases if lst[c] == 'PE']),
                       ('PE post-exclusion', [c for c in cases if lst[c] == 'PE' and c not in excluded]),
                       ('BR', [c for c in cases if lst[c] == 'BR'])]:
        pairs = [(collapsed(wa[c]), collapsed(wb[c])) for c in sel if wa[c] is not None and wb[c] is not None]
        print(f'- {label}: n = {len(pairs)}, kappa = {kappa(pairs):.3f}')

    for L in ('PE', 'BR'):
        kept = [c for c in cases if lst[c] == L and c not in excluded]
        den = [c for c in kept if wa[c] is not None and wb[c] is not None]
        cons = [min(wa[c], wb[c]) for c in den]
        print(f'\n## {L}: {len(kept)} after exclusions, {len(kept) - len(den)} cannot judge by either, '
              f'denominator {len(den)}')
        print(f'- conservative > 80 s: {pct(sum(w >= 3 for w in cons), len(den))}')
        print(f'- conservative > 40 s: {pct(sum(w >= 2 for w in cons), len(den))}')
        print(f'- conservative > 1 s: {pct(sum(w >= 1 for w in cons), len(den))}')
        print(f'- conservative distribution: {dict(sorted(Counter(cons).items()))}')
        for r, w in (('A', wa), ('B', wb)):
            own = [w[c] for c in kept if w[c] is not None]
            print(f'- rater {r} alone > 80 s: {pct(sum(x >= 3 for x in own), len(own))}')


if __name__ == '__main__':
    main(sys.argv[1])
