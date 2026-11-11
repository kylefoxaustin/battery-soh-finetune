# usage: python3 -I maskrange.py TEXTFILE START END
# Prints lines START..END with S1 masking (digits, %, time units -> '#'), URLs kept whole.
import re, sys
lines = open(sys.argv[1], encoding='utf-8', errors='replace').read().split('\n')
a, b = int(sys.argv[2]), int(sys.argv[3])
URL = re.compile(r'https?://\S+')
TU = re.compile(r'\b(ms|s|sec|secs|seconds?|min|mins|minutes?|h|hours?|cycles?|Hz)\b', re.I)
def mask(seg):
    seg = re.sub(r'\d', '#', seg).replace('%', '#'); return TU.sub('#', seg)
for i in range(a-1, min(b, len(lines))):
    s = lines[i]; out, pos = [], 0
    for m in URL.finditer(s):
        out.append(mask(s[pos:m.start()])); out.append(m.group(0)); pos = m.end()
    out.append(mask(s[pos:]))
    t = ''.join(out).rstrip()
    if t.strip(): print(i+1, t)
