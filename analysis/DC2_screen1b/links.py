# usage: python3 -I links.py FILE.html [REGEX]  -> page <title>, <h1>, and links whose text or href matches REGEX
import sys, re, html
s = open(sys.argv[1], encoding='utf-8', errors='replace').read()
rx = re.compile(sys.argv[2], re.I) if len(sys.argv) > 2 else None
t = re.search(r'<title[^>]*>(.*?)</title>', s, re.S | re.I)
print('TITLE:', html.unescape(re.sub(r'\s+', ' ', t.group(1))).strip() if t else None)
for h in re.findall(r'<h1[^>]*>(.*?)</h1>', s, re.S | re.I)[:3]:
    print('H1:', html.unescape(re.sub(r'<[^>]+>|\s+', ' ', h)).strip())
if rx:
    seen = set()
    for href, txt in re.findall(r'<a\s[^>]*href="([^"]+)"[^>]*>(.*?)</a>', s, re.S | re.I):
        txt = html.unescape(re.sub(r'<[^>]+>|\s+', ' ', txt)).strip()
        if (rx.search(txt) or rx.search(href)) and (href, txt) not in seen:
            seen.add((href, txt)); print('LINK:', txt[:150], '|', href)
