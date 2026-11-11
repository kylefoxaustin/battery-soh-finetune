"""scope.py TXT [HEADRX] [N] : find the body heading (not a TOC line) matching HEADRX (default Scope|Overview|Purpose|Introduction),
print the following N non-empty lines through the limit-safe filter."""
import sys, re
sys.argv += [None] * 3
L = [re.sub("[\u200b\u202c\u202d]", "", x) for x in open(sys.argv[1], errors="replace").read().splitlines()]
hx = re.compile(sys.argv[2] or r"^\s*(\d+(\.\d+)*\.?\s*)?(Scope|Overview|Purpose|Introduction|Applicability|Background)\s*$", re.I)
n = int(sys.argv[3] or 10)
LIM = re.compile(r"\d[\d.,]*\s*(?:%|percent|(?:ms|s|sec|second|seconds|min|minutes?|h|hr|hours?|Hz|cycles?)\b|MW\s*/|kW\s*/|A\s*/\s*[mµu]?s)", re.I)
def safe(t): return " ".join("[…]" if LIM.search(s) else s for s in re.split(r"(?<=[.;!?])\s+", t))
for i, l in enumerate(L):
    s = l.replace("‭","").replace("‬","").strip()
    if hx.search(s) and not re.search(r"(\.\s?){4,}|\s\d+\s*$", s):
        out = []
        for m in L[i+1:]:
            m = " ".join(m.replace("‭","").replace("‬","").split())
            if m: out.append(m)
            if len(out) >= n: break
        print("[%s] %s" % (i+1, s)); print(safe(" ".join(out))[:1600]); break
else:
    print("NO SCOPE HEADING FOUND")
