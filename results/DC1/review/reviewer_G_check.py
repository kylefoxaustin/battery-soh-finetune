"""Reviewer re-derivation of DC1's headline from dc1.json per-job E* values (own code)."""
import json, sys, statistics as st
import numpy as np

d = json.load(open(sys.argv[1]))
prof = json.load(open(sys.argv[2]))
model = {str(j['idx']): j['model'] for j in prof['jobs']}
fold = {str(j['idx']): j['fold'] for j in prof['jobs']}


def medians_by_fold(jobs, num, den):
    """mean over folds of the per-fold median of E*(num)/E*(den), as pre-registered."""
    out = []
    for f in 'AB':
        vals = [jobs[i]['Estar'][num] / jobs[i]['Estar'][den] for i in jobs if fold[i] == f]
        if vals: out.append(st.median(vals))
    return sum(out) / len(out), out


def boot(jobs, num, den, n=1000, seed=0):
    rng = np.random.default_rng(seed)
    byf = {f: [jobs[i]['Estar'][num] / jobs[i]['Estar'][den] for i in jobs if fold[i] == f] for f in 'AB'}
    stats = []
    for _ in range(n):
        ms = [float(np.median(rng.choice(v, len(v), replace=True))) for v in byf.values() if v]
        stats.append(sum(ms) / len(ms))
    return np.percentile(stats, [2.5, 97.5])


for scen in ('primary', 'budget0.5%', 'R0.20', 'Pmax_s_1x'):
    s = d['scenarios'][scen]
    jobs = s['jobs']
    k0 = next(k for k in jobs[next(iter(jobs))]['Estar'] if k == 'K0')
    keys = list(jobs[next(iter(jobs))]['Estar'].keys())
    print(f'\n=== {scen}  spec={s["spec"]}  Estar keys: {keys}')
    for wl in ('llama2_70b_lora', 'stable_diffusion'):
        sub = {i: j for i, j in jobs.items() if model[i] == wl}
        G, fm = medians_by_fold(sub, 'K0', 'K1_30')
        ci = boot(sub, 'K0', 'K1_30')
        Gsh, _ = medians_by_fold(sub, 'K0', 'K1sh_30')
        kinf = 'Kinf' if 'Kinf' in keys else next((k for k in keys if 'inf' in k.lower()), None)
        kr = 'K1r'
        Ginf, _ = medians_by_fold(sub, 'K0', kinf) if kinf else (float('nan'), None)
        Gr, _ = medians_by_fold(sub, 'K0', kr) if kr else (float('nan'), None)
        M = G / Gr if kr else float('nan')
        print(f'{wl:20s} n={len(sub):2d} G(30s)={G:.3f} [{ci[0]:.3f},{ci[1]:.3f}] per-fold medians={[round(x,3) for x in fm]}  G_sh={Gsh:.3f}  G_inf={Ginf:.3f}  G_r(1s)={Gr:.3f}  M={M:.3f}')
    rep = s['populations']
    for wl in ('llama2_70b_lora', 'stable_diffusion'):
        r = rep.get(wl, {})
        print(f'   reported {wl}: ' + ', '.join(f'{k}={v}' for k, v in r.items() if not isinstance(v, (dict, list)))[:300])
