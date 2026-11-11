# usage: python3 -I refs.py TEXTFILE [min] [max]
# Prints only reference-list entries "[n] ..." (n in range), with S1 masking:
# digits, %, and time-unit tokens -> '#', except inside URLs (printed whole).
import re, sys
txt = open(sys.argv[1], encoding='utf-8', errors='replace').read()
lo = int(sys.argv[2]) if len(sys.argv) > 2 else 1
hi = int(sys.argv[3]) if len(sys.argv) > 3 else 999
lines = txt.split('\n')
starts = [(i, int(m.group(1))) for i, l in enumerate(lines) for m in [re.match(r'^\s*\[(\d+)\]\s+\S', l)] if m]
URL = re.compile(r'https?://\S+')
TU = re.compile(r'\b(ms|s|sec|secs|seconds?|min|mins|minutes?|h|hours?|cycles?|Hz)\b', re.I)
def mask(seg):
    seg = re.sub(r'\d', '#', seg); seg = seg.replace('%', '#'); return TU.sub('#', seg)
def masked(s):
    out, pos = [], 0
    for m in URL.finditer(s):
        out.append(mask(s[pos:m.start()])); out.append(m.group(0)); pos = m.end()
    out.append(mask(s[pos:])); return ''.join(out)
for k, (i, n) in enumerate(starts):
    if not (lo <= n <= hi): continue
    end = starts[k+1][0] if k+1 < len(starts) else min(i+4, len(lines))
    end = min(end, i+5)
    entry = ' '.join(x.strip() for x in lines[i:end] if x.strip())
    print(f'[{n}]', masked(re.sub(r'^\s*\[\d+\]\s*', '', entry))[:400])
