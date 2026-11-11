"""epri_titles.py HTML : print (title, product URL) pairs from a DCFlex listing page (text before each 'Read More')."""
import sys, re, html
raw = open(sys.argv[1], errors="replace").read()
for m in re.finditer(r'href="(https://www\.epri\.com/research/products/\d+)"[^>]*>\s*Read More', raw):
    before = raw[max(0, m.start() - 2500):m.start()]
    txt = [html.unescape(x).strip() for x in re.findall(r">([^<>]{8,200})<", before)]
    txt = [x for x in txt if x and not x.startswith(("{", "var ", "//"))]
    print(" | ".join(txt[-3:])[:260], "=>", m.group(1))
