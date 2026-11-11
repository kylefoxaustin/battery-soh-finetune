# usage: python3 -I htmltext.py FILE.html START_REGEX NCHARS -> redacted visible text from first match of START_REGEX
import sys, re, html
s = open(sys.argv[1], encoding='utf-8', errors='replace').read()
s = re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', s, flags=re.S | re.I)
t = html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', s)))
LIM = re.compile(r'(\d\s*%|%|\d\s*(ms|s|sec|seconds?|min|minutes?|cycles?|Hz|p\.?u\.?)\b|/\s*(s|sec|min|minute|second)\b|per\s+(second|minute|cycle)|\d\s*MW\s*/|\bramp\w*\b[^.]*\d|percentile)', re.I)
m = re.search(sys.argv[2], t, re.I)
if not m: print('no match'); sys.exit()
seg = t[m.start(): m.start() + int(sys.argv[3])]
print(' '.join('[…]' if LIM.search(p) else p for p in re.split(r'(?<=[.;:])\s+', seg)))
