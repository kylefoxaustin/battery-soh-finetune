"""Reviewer re-derivation of FR1-R from the two ratings CSVs (own code; does not import the repo analysis)."""
import csv, math, sys, collections
root = sys.argv[1]
STATE = {'not observable': 0, '<=1 s': 1, '(1,40] s': 2, '(40,80] s': 3, '(80,700] s': 4, '>700 s': 5}
RATE = {'<=10 Hz': 0, '10 Hz-1 kHz': 1, '>=1 kHz': 2}


def load(r):
    out = {}
    for row in csv.DictReader(open(f'{root}/ratings_{r}.csv')):
        w = row['window'].strip()
        out[row['case']] = dict(
            st=STATE.get(w), cj=(w == 'cannot judge'), rate=RATE.get(row['rate_class'].strip()),
            cause=row['cause_type'].strip(),
            f_nc=row['flag_no_cause'].strip().lower() == 'yes', f_sw=row['flag_software_only'].strip().lower() == 'yes',
            f_oos=row['flag_out_of_scope'].strip().lower() == 'yes')
    return out


A, B = load('A'), load('B')
cases = sorted(set(A) & set(B)); assert len(cases) == 150 and set(A) == set(B)
PE = [c for c in cases if c.startswith('PE')]; BR = [c for c in cases if c.startswith('BR')]
assert len(PE) == 75 and 'PE006' not in PE and 'PE076' in PE


def wilson(k, n, z=1.959964):
    p = k / n; den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return p, c - h, c + h


def kappa(pairs):
    pairs = [(a, b) for a, b in pairs if a is not None and b is not None]
    n = len(pairs); po = sum(a == b for a, b in pairs) / n
    ca, cb = collections.Counter(a for a, _ in pairs), collections.Counter(b for _, b in pairs)
    pe = sum(ca[l] * cb[l] for l in set(ca) | set(cb)) / (n * n)
    return (po - pe) / (1 - pe), n, po


excl = {}
for c in PE:
    f = []
    if A[c]['f_nc'] and B[c]['f_nc']: f.append('no_cause')
    if A[c]['f_sw'] and B[c]['f_sw']: f.append('software_only')
    if A[c]['f_oos'] and B[c]['f_oos']: f.append('out_of_scope')
    excl[c] = f
for c in BR:
    excl[c] = ['no_cause'] if (A[c]['f_nc'] and B[c]['f_nc']) else []
ex_counts = collections.Counter(f for c in PE for f in excl[c])
pe_post = [c for c in PE if not excl[c]]
cj_either = [c for c in pe_post if A[c]['cj'] or B[c]['cj']]
no_both = [c for c in pe_post if A[c]['st'] == 0 and B[c]['st'] == 0]
no_one = [c for c in pe_post if (A[c]['st'] == 0) != (B[c]['st'] == 0) and not (A[c]['cj'] or B[c]['cj'])]
den = [c for c in pe_post if not (A[c]['cj'] or B[c]['cj']) and A[c]['st'] != 0 and B[c]['st'] != 0]
print(f'PE excluded (any) = {sum(1 for c in PE if excl[c])}: {dict(ex_counts)}')
print(f'PE post-exclusion = {len(pe_post)}; cannot-judge either = {len(cj_either)}; NO both = {len(no_both)}; NO one = {len(no_one)} {no_one}; denominator = {len(den)}')

cons = {c: min(A[c]['st'], B[c]['st']) for c in den}
rate = {c: min(A[c]['rate'], B[c]['rate']) for c in den if 2 <= A[c]['st'] <= 5 and 2 <= B[c]['st'] <= 5 and A[c]['rate'] is not None and B[c]['rate'] is not None}
n = len(den)
p80 = sum(cons[c] >= 4 for c in den); p40 = sum(cons[c] >= 3 for c in den); p1 = sum(cons[c] >= 2 for c in den)
rb = sum(1 for c in den if 2 <= cons[c] <= 4 and rate.get(c) == 2)
f = lambda k: f'{k}/{n} = {100*k/n:.1f} % [{100*wilson(k,n)[1]:.1f}, {100*wilson(k,n)[2]:.1f}]'
print('P80', f(p80), '| P40', f(p40), '| RB', f(rb), '| P1', f(p1))
print('conservative state dist:', dict(collections.Counter(cons[c] for c in den)))
print('conservative rate dist (states 2-5):', dict(collections.Counter(rate[c] for c in den if c in rate and cons[c] >= 2)))
rb_cases = sorted(c for c in den if 2 <= cons[c] <= 4 and rate.get(c) == 2); print('RB cases:', rb_cases)


def four(x):
    return None if x['cj'] else {0: 'NO', 1: 'S1', 2: 'S2', 3: 'S2', 4: 'S3', 5: 'S3'}[x['st']]


k4 = kappa([(four(A[c]), four(B[c])) for c in cases]); print('kappa four-class all:', round(k4[0], 3), 'n', k4[1], 'po', round(k4[2], 3))
k4pe = kappa([(four(A[c]), four(B[c])) for c in PE]); print('kappa four-class PE:', round(k4pe[0], 3), 'n', k4pe[1])
k7 = kappa([('cj' if A[c]['cj'] else A[c]['st'], 'cj' if B[c]['cj'] else B[c]['st']) for c in cases]); print('kappa seven-way:', round(k7[0], 3), 'n', k7[1])
k1 = kappa([(A[c]['cause'], B[c]['cause']) for c in cases]); print('kappa cause:', round(k1[0], 3))
krate = kappa([(A[c]['rate'], B[c]['rate']) for c in cases if A[c]['st'] and B[c]['st'] and 2 <= A[c]['st'] <= 5 and 2 <= B[c]['st'] <= 5]); print('kappa rate class:', round(krate[0], 3), 'n', krate[1])
print('BR not-observable by both:', sum(1 for c in BR if A[c]['st'] == 0 and B[c]['st'] == 0), '| BR excluded:', sum(1 for c in BR if excl[c]))
print('window disagreements (A != B incl. cj):', sum(1 for c in cases if (A[c]['cj'] != B[c]['cj']) or (A[c]['st'] != B[c]['st'])))
# decision
verdict = 'UNGATED' if (k4[0] < 0.6 or n < 10) else ('RETENTION IS A NECESSITY' if (p80 / n >= 0.5 and wilson(p80, n)[1] > 0.2) else ('RETENTION IS A CONVENIENCE' if p40 / n < 0.2 else 'UNCLEAR'))
shape = 'RING BUFFER SHAPED' if (rb / n >= 0.25 and wilson(rb, n)[1] > 0.10) else ('FLASH/CLOUD SHAPED' if (p80 / n >= 0.5 and rb / n < 0.10) else 'MIXED')
print('VERDICT:', verdict, '| SHAPE:', shape)
