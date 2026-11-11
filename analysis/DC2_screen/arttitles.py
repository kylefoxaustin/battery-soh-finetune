"""arttitles.py FILE : print 'Article N — title' using the line right after a bare 'Article N' line; also TITLE/CHAPTER headings."""
import sys, re
L=[l.strip() for l in open(sys.argv[1],errors='replace').read().splitlines() if l.strip()]
LIM=re.compile(r"\d[\d.,]*\s*(%|(ms|s|min|Hz|h)\b)")
for i,l in enumerate(L[:-1]):
    if re.fullmatch(r"(Article \d+[a-z]?|TITLE [IVX]+|CHAPTER \d+|ANNEX [IVX]+)", l):
        t=L[i+1][:120]
        print(l, "—", re.sub(r"\d","#",t) if LIM.search(t) else t)
