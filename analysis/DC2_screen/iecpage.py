"""iecpage.py HTMLFILE TXTFILE : print title, metadata fields, abstract (limit-safe), preview URLs from an IEC webstore page."""
import sys, re, html
raw = open(sys.argv[1], errors="replace").read()
L = [l.strip() for l in open(sys.argv[2], errors="replace").read().splitlines() if l.strip()]
LIM = re.compile(r"\d[\d.,]*\s*(%|percent|(ms|s|sec|min|minutes?|h|Hz|cycles?)\b)", re.I)
def safe(t): return " ".join("[…]" if LIM.search(s) else s for s in re.split(r"(?<=[.;])\s+", t))
i = next(k for k, l in enumerate(L) if re.match(r"^(IEC|ISO/IEC|IEC TR|IEC TS)\s", l) and k > 10)
print("ID:", L[i]); print("TITLE:", L[i+1]); print("LONGTITLE:", re.split(r"\s(?=This |The |IEC 61000-4-15 )", L[i+2])[0][:220])
for lab in ("Publication date", "Edition", "Stability date", "Status", "Withdrawal date", "Replaced by", "Replaces"):
    for k, l in enumerate(L):
        if l == lab and k + 1 < len(L): print(lab + ":", L[k+1][:80]); break
ab = []
for l in L[i+2:i+12]:
    if l in ("Publication date","Edition","Abstract") : break
    ab.append(l)
print("ABSTRACT:", safe(" ".join(ab))[:1500])
for m in sorted(set(re.findall(r'(?:https://webstore\.iec\.ch)?/[^"\']*preview[^"\']*', raw)))[:5]: print("PREVIEW:", html.unescape(m))
