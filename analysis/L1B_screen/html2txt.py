# Convert EUR-Lex HTML to plain text lines (stdlib only). usage: html2txt.py in.html out.txt
import sys, html
from html.parser import HTMLParser
class P(HTMLParser):
    def __init__(s): super().__init__(); s.buf=[]; s.skip=0
    def handle_starttag(s,t,a):
        if t in ('script','style'): s.skip+=1
        if t in ('p','div','tr','br','h1','h2','h3','h4','li','table'): s.buf.append('\n')
        if t in ('td','th'): s.buf.append(' | ')
    def handle_endtag(s,t):
        if t in ('script','style'): s.skip-=1
        if t in ('p','div','tr','h1','h2','h3','h4','li'): s.buf.append('\n')
    def handle_data(s,d):
        if not s.skip: s.buf.append(d)
p=P(); p.feed(open(sys.argv[1],encoding='utf-8',errors='replace').read())
txt=''.join(p.buf).replace(' ',' ')
lines=[' '.join(l.split()) for l in txt.split('\n')]
lines=[l for l in lines if l and l!='|']
open(sys.argv[2],'w').write('\n'.join(lines))
print(len(lines))
