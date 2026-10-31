"""Reviewer re-check of B1's RT DISTURBED computation from the raw logs (own code)."""
import json, sys, statistics as st
root = sys.argv[1]
tl = [json.loads(l) for l in open(f'{root}/timeline.jsonl')]
phases = {}
for e in tl:
    phases.setdefault((e['round'], e['phase']), {})[e['event']] = e['wall']

def blocks(path):
    return [json.loads(l) for l in open(path)]

def inside(b, win, dur=60.0):
    return b['wall_start'] >= win['start'] and b['wall_start'] + dur <= win['end']

worst = {}
for r in (1, 2, 3):
    try:
        e1 = blocks(f'{root}/e1loop_r{r}.jsonl'); lim = blocks(f'{root}/limloop_r{r}.jsonl')
    except FileNotFoundError:
        continue
    p0 = phases[(r, 'P0')]
    base_e1 = st.median([b['p99_ms'] for b in e1 if inside(b, p0)])
    base_l96 = st.median([b['lat_ns_p99'] for b in lim if inside(b, p0) and b['n_cells'] == 96])
    base_l3564 = st.median([b['lat_ns_p99'] for b in lim if inside(b, p0) and b['n_cells'] == 3564])
    for ph in ('P1', 'P2', 'P3', 'P4', 'P5'):
        if (r, ph) not in phases: continue
        w = phases[(r, ph)]
        e = [b['p99_ms'] for b in e1 if inside(b, w)]
        l96 = [b['lat_ns_p99'] for b in lim if inside(b, w) and b['n_cells'] == 96]
        l3564 = [b['lat_ns_p99'] for b in lim if inside(b, w) and b['n_cells'] == 3564]
        gates = all(b['gate_pass'] for b in e1 if inside(b, w)) and all(b['gate_pass'] for b in lim if inside(b, w))
        med = (st.median(e) / base_e1, st.median(l96) / base_l96, st.median(l3564) / base_l3564)
        mx = (max(e) / base_e1, max(l96) / base_l96, max(l3564) / base_l3564)
        print(f'r{r} {ph}: n_e1={len(e)} n_l96={len(l96)} n_l3564={len(l3564)} gates_ok={gates} '
              f'median_ratio e1/L96/L3564 = {med[0]:.3f}/{med[1]:.3f}/{med[2]:.3f}  worst_block = {mx[0]:.3f}/{mx[1]:.3f}/{mx[2]:.3f}  '
              f'RT_DISTURBED={"YES" if max(med) > 1.20 else "no"}')
        for k, v in zip(('e1', 'L96', 'L3564'), med): worst[k] = max(worst.get(k, 0), v)
        for k, v in zip(('e1w', 'L96w', 'L3564w'), mx): worst[k] = max(worst.get(k, 0), v)
print('max median ratios:', {k: round(v, 3) for k, v in worst.items()})
