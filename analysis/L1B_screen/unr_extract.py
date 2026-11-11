# usage: unr_extract.py txt selfnum out.json
# Prints scope (<=3 sentences) and identifier+clause references from the requirements text and annexes,
# excluding front matter (before '1. SCOPE'), transitional provisions sections, and bibliography.
import sys, re, json
lines=open(sys.argv[1]).read().split('\n'); self_n=sys.argv[2]
def _find(pats):
    for p in pats:
        for i,l in enumerate(lines):
            if re.match(p,l): return i
    raise SystemExit("no scope heading")
start=_find([r"^1\.?\s+(SCOPE|Scope)\s*$", r"^(SCOPE|Scope)\s*$", r"^1\.\s+(SCOPE|Scope)\b", r"^(?:\|\s*)?1\.?\s*\|\s*(SCOPE|Scope)\b"])
body=lines[start:]
# scope
sc=[]
for l in body[1:]:
    if re.match(r"^(\d+\.?\s+[A-Z]{3,}|2\.\s)", l): break
    sc.append(l)
scope=' '.join(sc)
sents=re.split(r"(?<=[.;])\s+(?=[A-Z(\d])", scope)
# skip transitional / bibliography
keep=[]; skip=False
for l in body:
    if re.match(r"^\d+\.?\s+(TRANSITIONAL PROVISIONS|Transitional provisions)\s*$", l, re.I): skip=True; continue
    if re.match(r"^\d+\.?\s+(BIBLIOGRAPHY)\s*$", l, re.I): skip=True; continue
    if skip and (re.match(r"^\d+\.?\s+[A-Z][A-Z ,'\-()]{3,}$", l) or re.match(r"^ANNEX\s+\d+", l, re.I)): skip=False
    if not skip: keep.append(l)
pat=re.compile(r"((?:UN\s+)?Regulations?\s+Nos?\.?\s*\d+(?:\s*(?:,|and)\s*\d+)*|ISO(?:/IEC)?\s+(?:[Ss]tandard\s+)?\d+(?:-\d+)*|IEC\s+(?:[Pp]ublication\s+)?(?:\d+|TR\s?\d+)(?:-\d+)*|CIE\s+(?:Publication\s+)?(?:No\.?\s*)?[\dS][\w.:/-]*|EN\s+\d+(?:-\d+)*|SAE\s+J\s?\d+|Directive\s+\d+/\d+/E[EC]+|Regulation\s+\((?:EU|EC|EEC)\)\s+(?:No\s+)?\d+/\d+|(?:UN\s+)?GTR\s+No\.?\s*\d+|Global Technical Regulation No\.?\s*\d+|(?:Consolidated |Mutual )?Resolution\s+(?:on\s+the\s+[^()]{0,90}?)?\(?(?:R\.E\.|M\.R\.|R\.)\s?\d|UN Rule No\.?\s*\d+)")
refs={}; clause='1.'
for l in keep:
    m=re.match(r"^(?:\|\s*)?((?:\d+\.)+\d*\.?)(?:\s|$)", l) or re.match(r"^(ANNEX\s+\d+[A-Z]?|Annex\s+\d+[A-Z]?)\b", l)
    if m: clause=m.group(1)
    if re.match(r"^ANNEX\s+\d+", l): annex=l
    for x in pat.findall(l):
        x=' '.join(x.split())
        mm=re.match(r"(?:UN\s+)?Regulations?\s+Nos?\.?\s*(.*)", x)
        if mm and not x.startswith('Regulation ('):
            for n in re.findall(r"\d+", mm.group(1)):
                if n!=self_n: refs.setdefault("UN R%s"%n, set()).add(clause)
        else:
            x=re.sub(r'(IEC|ISO) (?:[Pp]ublication|[Ss]tandard) ', r'\1 ', x); refs.setdefault(x, set()).add(clause)
out={"scope_sentences":sents[:3], "scope_sentence_count":len(sents), "refs":{k:sorted(v) for k,v in refs.items()}}
json.dump(out, open(sys.argv[3],'w'), indent=1, ensure_ascii=False)
print("SCOPE:", ' '.join(sents[:3])[:900], "| total sentences", len(sents))
for k in sorted(refs, key=lambda k:(k.split()[0], [int(t) if t.isdigit() else 0 for t in re.findall(r'\d+',k)][:1])): print(" ", k, "|", ', '.join(sorted(refs[k])[:6]), "(%d)"%len(refs[k]))
