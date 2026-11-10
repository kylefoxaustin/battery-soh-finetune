import sys,re
# usage: section.py file startline_regex endline_regex [occurrence index, default last]
L=open(sys.argv[1],encoding='utf-8',errors='replace').read().split('\n')
idx=[i for i,l in enumerate(L) if re.search(sys.argv[2],l)]
k=int(sys.argv[4]) if len(sys.argv)>4 else -1
i0=idx[k]; out=[]
for l in L[i0:i0+200]:
    if out and re.search(sys.argv[3],l): break
    out.append(l.strip())
print(re.sub(r'\s+',' ',' '.join(out))[:3000])
