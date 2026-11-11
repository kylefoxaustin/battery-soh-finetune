# usage: scope_only.py txt -> prints the scope statement (<=3 sentences): first 'scope' heading followed within 3 lines by text containing 'appl'
import sys,re
L=open(sys.argv[1]).read().split('\n')
for i,l in enumerate(L):
    if re.match(r"^(?:\|\s*)?(?:1\.?|0\.?)?\s*(?:\|\s*)?(SCOPE|Scope)(?: AND PURPOSE| and purpose)?\s*(?:\(\d+\))?\s*(?:\|)?\s*$", l) or re.match(r"^(?:1\.)\s*(SCOPE|Scope)\s*$",l):
        nxt=[x for x in L[i+1:i+6] if not re.fullmatch(r"[\d.|\s]*",x)]
        txt=[]
        for x in nxt:
            if re.match(r"^(\d+\.?\s+)?[A-Z][A-Z ,]{4,}$",x) or re.match(r"^(?:\|\s*)?\d+\.\s*(?:\|\s*)?[A-Z][a-z]+(?: [a-z]+)*\s*$",x) and 'appl' not in x: break
            txt.append(x)
        s=' '.join(txt)
        if re.search(r"appl",s):
            s=re.sub(r"^\|\s*","",s); sents=re.split(r"(?<=\.)\s+(?=[A-Z])",s)
            print(' '.join(sents[:3])[:700]); sys.exit()
print("NO SCOPE FOUND")
