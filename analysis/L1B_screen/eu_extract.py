# usage: eu_extract.py txt out.json ; scope=Article 2; refs from Article 1 onward, excluding 'Transitional provisions' article.
# In annex tables of UN Regulations, a line that is a bare number followed by a subject line is read as 'UN R<n>' (subject kept; series/OJ columns not read).
import sys,re,json
L=open(sys.argv[1]).read().split('\n')
s=next(i for i,l in enumerate(L) if l=='Article 1')
body=L[s:]
i2=body.index('Article 2'); sc=[]
for l in body[i2+2:]:
    if re.match(r'^Article \d+$',l): break
    sc.append(l)
scope=' '.join(sc); sents=re.split(r"(?<=[.;])\s+(?=[A-Z(\d])", scope)
keep=[]; skip=False; clause='Art 1'; annex=None
for j,l in enumerate(body):
    if re.match(r'^Article \d+$',l):
        clause='Art '+l.split()[1]; annex=None
        skip = (j+1<len(body) and re.match(r'(?i)transitional provisions',body[j+1]) is not None)
    if re.match(r'^ANNEX [IVX]+$',l):
        clause=l.replace('ANNEX','Annex'); skip=False
        annex = (j+1<len(body) and re.match(r'(?i)list of (UN|UNECE) Regulations',body[j+1]) is not None)
    if not skip: keep.append((clause,l,j))
pat=re.compile(r"((?:UN(?:ECE)?\s+)?Regulations?\s+Nos?\.?\s*\d+(?:\s*(?:,|and)\s*\d+)*|ISO(?:/IEC)?\s+\d+(?:-\d+)*|IEC\s+\d+(?:-\d+)*|CIE\s+[\dS][\w.:/-]*|EN\s+\d+(?:-\d+)*|SAE\s+J\s?\d+|Directive\s+\d+/\d+/E[EC]+|Regulation\s+\((?:EU|EC|EEC)\)\s+(?:No\s+)?\d+/\d+|(?:Council |Commission )?(?:Implementing |Delegated )?Regulation\s+\((?:EU|EC)\)\s+No\s+\d+/\d+|(?:UN\s+)?GTR\s+No\.?\s*\d+)")
refs={}; subj={}
_ann={}
cur=False
for k,(c,l,j) in enumerate(keep):
    if re.match(r'^ANNEX [IVX]+$',l): cur=(j+1<len(body) and re.match(r'(?i)list of (UN|UNECE) Regulations',body[j+1]) is not None)
    if re.match(r'^Article \\d+$',l): cur=False
    _ann[k]=cur
for k,(clause,l,j) in enumerate(keep):
    for x in pat.findall(l):
        x=' '.join(x.split())
        mm=re.match(r"(?:UN(?:ECE)?\s+)?Regulations?\s+Nos?\.?\s*(.*)",x)
        if mm and not re.match(r'.*Regulation \(',x):
            for n in re.findall(r"\d+",mm.group(1)): refs.setdefault("UN R%s"%n,set()).add(clause)
        else: refs.setdefault(re.sub(r'^(Council |Commission )?(Implementing |Delegated )?','',x),set()).add(clause)
    if clause.startswith('Annex') and keep[k][2] is not None and _ann.get(k) and re.match(r'^\d{1,3}$',l) and k+1<len(keep):
        nxt=keep[k+1][1]
        if re.match(r'^[A-Z][a-z]',nxt) and not re.match(r'^\d',nxt):
            n=l; refs.setdefault("UN R%s"%n,set()).add(clause+' table'); subj.setdefault("UN R%s"%n,nxt)
json.dump({"scope_sentences":sents[:3],"refs":{k:sorted(v) for k,v in refs.items()},"table_subjects":subj},open(sys.argv[2],'w'),indent=1,ensure_ascii=False)
print("SCOPE:",' '.join(sents[:3])[:700])
def key(k):
    d=re.findall(r'\d+',k); return (k.split()[0], int(d[0]) if d else 0)
for k in sorted(refs,key=key): print(" ",k,"|",', '.join(sorted(refs[k])[:5]),"|",subj.get(k,'')[:110])
