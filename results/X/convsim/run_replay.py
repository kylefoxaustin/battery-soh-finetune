import numpy as np, json, time
import convsim as c
d_km = c.v_kmh.sum()/3600
res = {}
t0=time.time()
for age in (0.0, 0.5, 1.0):
    for T_amb in (25.0, 45.0):
        out, Tj = c.replay(age, T_amb)
        e = {k: v[0] for k, v in out.items()}
        Wh = {k: float(v[1].sum())/3600 for k, v in out.items()}
        key = f'age{age:.1f}_amb{int(T_amb)}'
        res[key] = {'eff_pct': {k: round(100*x, 4) for k, x in e.items()},
                    'loss_Wh_per_cycle': {k: round(x, 3) for k, x in Wh.items()},
                    'excess_loss_vs_oracle_pct': {k: round(100*(Wh[k]/Wh['oracle']-1), 2) for k in Wh},
                    'Tj_C': [round(float(Tj.min()),1), round(float(Tj.max()),1)]}
        r=res[key]
        print(f"{key:14s} eff% " + '  '.join(f"{k} {r['eff_pct'][k]:.3f}" for k in ('oracle','tierA','tierB','static'))
              + f"  | excess loss vs oracle: A {r['excess_loss_vs_oracle_pct']['tierA']:+.1f}%  B {r['excess_loss_vs_oracle_pct']['tierB']:+.1f}%  static {r['excess_loss_vs_oracle_pct']['static']:+.1f}%  Tj {r['Tj_C']}")
res['_meta'] = {'cycle':'WLTC class 3b (JRC wltp, EUPL)', 'km': round(d_km,2), 'load_W_p50': float(np.median(c.P_load)),
                'note':'All component values ASSUMED. Converter-loss replay, not a vehicle measurement.'}
json.dump(res, open('results_base.json','w'), indent=1)
print('runtime %.0fs' % (time.time()-t0))
