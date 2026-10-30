import numpy as np, json
import convsim as c
base_best=c.best
def excess(out,k): return 100*(out[k][1].sum()/out['oracle'][1].sum()-1)
rows=[]
def go(label, age=0.5, T_amb=45.0, **kw):
    out,_=c.replay(age,T_amb,**kw)
    r={k: round(excess(out,k),2) for k in ('tierA','tierB','static')}
    r['oracle_eff']=round(100*out['oracle'][0],3)
    rows.append((label,r)); print(f'{label:58s} excess loss vs oracle  A {r["tierA"]:+6.2f}%  B {r["tierB"]:+6.2f}%  static {r["static"]:+6.2f}%   (oracle eff {r["oracle_eff"]})')
go('BASE  age 0.5, 45 C')
go('Tier A refresh 5 s',  A_PERIOD=5)
go('Tier A refresh 10 s', A_PERIOD=10)
go('Tier B refresh 30 s, no delay',  B_DELAY=0)
go('Tier B refresh 10 s, 10 s delay', B_PERIOD=10, B_DELAY=10)
go('Tier B refresh 60 s, 60 s delay', B_PERIOD=60, B_DELAY=60)
go('Sensor noise 5 C', noise=5.0)
# ---- stress the static table: what if it is a single fixed setting (no load index)?
def single_fixed(age=0.5,T_amb=45.0):
    out,Tj=c.replay(age,T_amb)
    g=c.best(np.median(c.I_load),60.0,0.0)
    L=np.array([c.loss(c.I_load[i],Tj[i],age,*g) for i in range(c.T)])
    return 100*(L.sum()/out['oracle'][1].sum()-1)
print(f'{"Static = ONE fixed setting (no load index)":58s} excess {single_fixed():+6.2f}%')
# ---- end of life, hot: does age shift the optimum enough for the static table to miss?
go('EOL age 1.0, 45 C', age=1.0)
json.dump(rows, open('results_sens.json','w'), indent=1)
