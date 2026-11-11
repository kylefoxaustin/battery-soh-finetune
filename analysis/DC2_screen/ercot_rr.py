"""ercot_rr.py FILE TITLEREGEX : parse ERCOT revision-request listing; print id | title | status cells (no summary)."""
import sys, re, html
import re as _r
LIM=_r.compile(r"\d[\d.,]*\s*(?:%|percent|(?:ms|s|sec|second|seconds|min|minute|minutes|h|hr|hour|hours|Hz)\b|MW\s*/)", _r.I)
def SAFE(s): return _r.sub(r"\d","#",s) if LIM.search(s) else s
t = open(sys.argv[1], errors='replace').read()
rx = re.compile(sys.argv[2], re.I)
rows = re.findall(r'<tr>(.*?)</tr>', t, re.S)
n=0; tot=0
for r in rows:
    cells = re.findall(r'<td[^>]*>(.*?)</td>', r, re.S)
    if len(cells) < 3: continue
    clean = [html.unescape(re.sub(r'<[^>]+>', ' ', c)).split() for c in cells]
    clean = [" ".join(c) for c in clean]
    rid = clean[0]
    if not re.match(r'^[A-Z]+\d+', rid): continue
    tot+=1
    title = clean[1]
    dates = re.findall(r'rr-date">(.*?)</div>', r, re.S); ph = re.findall(r'rr-phase"><p>(.*?)</p>', r, re.S)
    if rx.search(title):
        n+=1
        import importlib; print(rid, "|", SAFE(title[:160]), "|", [html.unescape(re.sub('<[^>]+>',' ',x)).strip() for x in dates][:3], [html.unescape(re.sub('<[^>]+>',' ',x)).strip() for x in ph][:3])
print("-- rows:", tot, "title hits:", n)
