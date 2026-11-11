# usage: python3 -I scope.py TEXTFILE MODE [ARG] [NLINES]
# MODE head N        : first N non-empty lines
# MODE toc           : table-of-contents lines (dot leaders), headings only
# MODE sect REGEX N  : N lines after the first heading line matching REGEX (outside TOC)
# All output is redacted: any sentence with a limit-type pattern is replaced by […].
import re, sys
txt = open(sys.argv[1], encoding='utf-8', errors='replace').read()
lines = [l.rstrip() for l in txt.split('\n')]
LIM = re.compile(r'(\d\s*%|%|\d\s*(ms|s|sec|seconds?|min|minutes?|cycles?|Hz|p\.?u\.?)\b|/\s*(s|sec|min|minute|second)\b|per\s+(second|minute|cycle)|\d\s*MW\s*/|\bramp\w*\b[^.]*\d|\bP\s*max\b[^.]*\d|\d[^.]*\bP\s*max\b|percentile)', re.I)
def red(s):
    parts = re.split(r'(?<=[.;:])\s+', s)
    return ' '.join('[…]' if LIM.search(p) else p for p in parts)
mode = sys.argv[2]
if mode == 'head':
    n = int(sys.argv[3]); out = [l for l in lines if l.strip()][:n]
    for l in out: print(red(l.strip()))
elif mode == 'toc':
    for l in lines:
        if re.search(r'\.{5,}\s*\d+\s*$', l):
            h = re.sub(r'\.{5,}\s*\d+\s*$', '', l).strip()
            print(red(h))
elif mode == 'sect':
    rx = re.compile(sys.argv[3], re.I); n = int(sys.argv[4])
    for i, l in enumerate(lines):
        if rx.search(l) and not re.search(r'\.{5,}', l):
            blk = ' '.join(x.strip() for x in lines[i:i+n] if x.strip())
            print(f'@line {i+1}:', red(blk)); break
