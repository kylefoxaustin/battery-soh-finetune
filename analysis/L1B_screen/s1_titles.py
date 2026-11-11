import json, sys, re
KEEP = re.compile(r"lighting|lamp|headlamp|adaptive driving beam|light-signal|light signal", re.I)
UNR = re.compile(r"(?:UN(?:/ECE)?|UNECE|Economic Commission for Europe)[^.;]{0,60}?Regulations? No\.? ?(\d+)|Regulations? No\.? ?(\d+) of the (?:Economic Commission|UN)", re.I)
LIST = {"48","148","149","150","123","45","37","99","128"}
def strip_date(t):
    return re.sub(r"[\s\u00a0]+of[\s\u00a0]+\d{1,2}[\s\u00a0]+[A-Z][a-z]+[\s\u00a0]+\d{4}", "", t)
def nums(t):
    # every 'Regulation(s) No N' mention where context is UN
    out=set()
    for m in re.finditer(r"(?:UN|UNECE|UN/ECE)\s+Regulations?\s+(?:Nos?\.?\s*)?([\d ,and]+)", t):
        out |= set(re.findall(r"\d+", m.group(1)))
    for m in re.finditer(r"Regulations?\s+Nos?\.?\s*([\d ,and]+)\s+of the (?:Economic Commission|UN)", t):
        out |= set(re.findall(r"\d+", m.group(1)))
    return out
res=[]
for f in sys.argv[1:]:
    d=json.load(open(f))
    for x in sorted(d['results']['bindings'], key=lambda x:x['celex']['value']):
        t=strip_date(x.get('title',{}).get('value','(no English title)')).replace('\n',' ')
        n=nums(t)
        keep = bool(KEEP.search(t)) or bool(n & LIST)
        res.append((f.split('/')[-1], x['celex']['value'], 'KEEP' if keep else 'drop', t))
for r in res: print('\t'.join(r))
