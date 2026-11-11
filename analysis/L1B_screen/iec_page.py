import sys,re,html
s=open(sys.argv[1],encoding='utf-8',errors='replace').read()
t=re.search(r'<title>([^<]*)',s); print("PAGE:",t.group(1) if t else None)
m=re.search(r'<h1[^>]*>(.*?)</h1>',s,re.S); print("H1:",' '.join(re.sub('<[^>]+>',' ',m.group(1)).split()) if m else None)
# title line: look for 'Lamps for road vehicles' style title field
for m in re.finditer(r'(?:class="[^"]*(?:title|subtitle)[^"]*"[^>]*>)([^<]{10,200})<',s):
    x=' '.join(m.group(1).split())
    if 'road' in x.lower() or 'lamp' in x.lower(): print("TITLE-FIELD:",html.unescape(x)); break
m=re.search(r'(IEC 60809:\d{4} (?:is|applies|specifies|covers)[^<]{0,1200})',s)
if m:
    txt=html.unescape(' '.join(m.group(1).split())); sents=re.split(r'(?<=\.)\s+',txt); print("ABSTRACT(<=3):",' '.join(sents[:3]))
else: print("no abstract match")
