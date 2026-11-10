import sys; sys.path.insert(0,"<home>/.local/lib/python3.10/site-packages")
import re,warnings,json
from bs4 import BeautifulSoup
warnings.filterwarnings("ignore")
# usage: gb_pick.py list.html "GB 38031"  -> prints hit count, chosen hcno and title only (no years/status/editions)
s=BeautifulSoup(open(sys.argv[1],encoding='utf-8').read(),'lxml')
want=sys.argv[2].replace(' ','').replace('/','/')
rows=[]
for tr in s.find_all('tr'):
    hc=re.search(r"[0-9A-F]{32}", str(tr))
    if not hc: continue
    txt=[t.get_text(' ',strip=True) for t in tr.find_all('td')]
    no=next((t for t in txt if re.match(r'^GB',t)),'')
    base=re.sub(r'-\d{4}$','',no).replace(' ','')
    if base!=want: continue
    st='current' if any('现行' in t for t in txt) else ('upcoming' if any('即将' in t for t in txt) else 'other')
    title=next((t for t in txt if re.search(r'[一-鿿]',t) and not re.search(r'现行|废止|即将实施|强制性|推荐性|^GB',t)),'')
    rows.append((st,hc.group(0),title))
print('HITS(exact identifier)',len(rows))
pick=[r for r in rows if r[0]=='current'] or [r for r in rows if r[0]=='upcoming'] or rows
if pick: print('CHOSEN',pick[0][1],'|',pick[0][2])
