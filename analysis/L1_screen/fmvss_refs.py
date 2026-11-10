import sys; sys.path.insert(0,"<home>/.local/lib/python3.10/site-packages")
import re,json,warnings
from bs4 import BeautifulSoup
warnings.filterwarnings("ignore")
s=BeautifulSoup(open(sys.argv[1],encoding='utf-8').read(),'xml')
for c in s.find_all('CITA'): c.decompose()   # source/amendment citations: never printed
for c in s.find_all(['EDNOTE','SECAUTH','AUTH','SOURCE']): c.decompose()
head=s.find('HEAD'); print('TITLE:',head.get_text(' ',strip=True) if head else None)
ps=[p.get_text(' ',strip=True) for p in s.find_all('P')]
# scope/purpose/application paragraphs
for p in ps:
    if re.match(r'^S[123]\.\s*(Scope|Purpose|Application)',p): print('SCOPE-PARA:',p[:900])
excl=False; refs={}; clause='?'
pat=re.compile(r'(§\s*571\.\d+[a-z]?|Standard No\.\s*\d+[a-z]?|FMVSS No\.\s*\d+[a-z]?|\bSAE (?:Recommended Practice |Standard |Information Report )?J\s?\d+(?:/\d+)?|\bISO(?:/IEC|/TS|/TR)?\s+\d+(?:-\d+)*|\bIEC\s+\d+(?:-\d+)*|\bASTM\s+[A-Z]\s?\d+|\bUL\s+\d+|49 CFR [Pp]art\s+\d+|\b[Pp]art\s+5\d\d\b|§\s*5\d\d\.\d+|\bUN(?:/ECE)? Regulation No\.?\s*\d+|\bECE R\d+)')
for p in ps:
    m=re.match(r'^(S\d+(?:\.\d+)*[a-z]?)\.?\s',p)
    if m:
        clause=m.group(1)
        top=re.match(r'^S\d+\.?\s',p)
        if top: excl=bool(re.search(r'phase-in|phase in|transition',p[:120],re.I))
        elif re.search(r'phase-in|phase in|transition',p[:80],re.I): pass
    if excl: continue
    for mm in pat.finditer(p):
        k=re.sub(r'\s+',' ',mm.group(1))
        refs.setdefault(k,[])
        if clause not in refs[k]: refs[k].append(clause)
json.dump(refs,open(sys.argv[2],'w'),indent=1)
print('NREFS',len(refs))
for k,v in refs.items(): print(' *',k,'|',v[:6])
