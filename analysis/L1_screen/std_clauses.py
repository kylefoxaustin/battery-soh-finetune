import sys,re
# usage: std_clauses.py text.txt  -> prints ONLY clause 1 (Scope, first 1200 chars) and clause 2 (Normative references) of a standard; foreword/history never printed
L=open(sys.argv[1],encoding='utf-8',errors='replace').read().split('\n')
def body_idx(rx):
    return [i for i,l in enumerate(L) if re.match(rx,l,re.I) and '....' not in l and '. . .' not in l]
sc=body_idx(r'^\s*1\s+Scope\s*$'); nr=body_idx(r'^\s*2\s+Normative references\s*$'); td=body_idx(r'^\s*3\s+(Terms|Definitions)')
print('IDX',sc[:3],nr[:3],td[:3])
if sc:
    end=nr[0] if nr and nr[0]>sc[0] else sc[0]+40
    t=re.sub(r'\s+',' ',' '.join(L[sc[0]:end]))
    t=re.split(r'This (?:\w+ )?edition cancels|significant technical changes',t)[0]
    print('SCOPE:',t[:1200])
else: print('SCOPE: not found in accessible text')
if nr:
    end=next((j for j in td if j>nr[0]),nr[0]+80)
    print('NORMREFS:'); print('\n'.join(l.rstrip() for l in L[nr[0]:end] if l.strip()))
else: print('NORMREFS: not found in accessible text')
