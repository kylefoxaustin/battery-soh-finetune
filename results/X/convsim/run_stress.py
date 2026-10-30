import numpy as np, json
import convsim as c
"""Stress cases chosen to give the static table every chance to be wrong:
   cold start and hot soak (Tj far from its 60 C build point), strong ageing,
   and a more aggressive ageing law."""
def ex(out,k): return 100*(out[k][1].sum()/out['oracle'][1].sum()-1)
rows={}
for label,age,T_amb in [('cold -10 C, new',0.0,-10.0),('cold -10 C, EOL',1.0,-10.0),
                        ('hot 70 C ambient, EOL',1.0,70.0),('base 45 C, EOL',1.0,45.0)]:
    out,Tj=c.replay(age,T_amb)
    rows[label]={k:round(ex(out,k),2) for k in ('tierA','tierB','static')}
    rows[label]['Tj']=[round(float(Tj.min()),1),round(float(Tj.max()),1)]
    print(f'{label:26s} A {rows[label]["tierA"]:+6.2f}%  B {rows[label]["tierB"]:+6.2f}%  static {rows[label]["static"]:+6.2f}%   Tj {rows[label]["Tj"]}')
# aggressive ageing: Rds +80 %, Qoss +40 % at EOL
orig=c.loss
def loss_aggr(I,Tj,age,n,f,td):
    return orig(I,Tj,age*8/3*0+age*(0.8/0.30) if False else age,n,f,td)
import types
src=open('convsim.py').read().replace('(1 + 0.30*age)','(1 + 0.80*age)').replace('(1 + 0.15*age)','(1 + 0.40*age)')
m=types.ModuleType('cs2'); exec(compile(src,'cs2','exec'),m.__dict__)
for label,age,T_amb in [('AGGRESSIVE ageing, EOL, 45 C',1.0,45.0),('AGGRESSIVE ageing, EOL, -10 C',1.0,-10.0)]:
    out,Tj=m.replay(age,T_amb)
    rows[label]={k:round(100*(out[k][1].sum()/out['oracle'][1].sum()-1),2) for k in ('tierA','tierB','static')}
    print(f'{label:26s} A {rows[label]["tierA"]:+6.2f}%  B {rows[label]["tierB"]:+6.2f}%  static {rows[label]["static"]:+6.2f}%')
json.dump(rows,open('results_stress.json','w'),indent=1)
