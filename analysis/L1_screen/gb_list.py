import sys; sys.path.insert(0,"<home>/.local/lib/python3.10/site-packages")
import re,warnings
from bs4 import BeautifulSoup
warnings.filterwarnings("ignore")
s=BeautifulSoup(open(sys.argv[1],encoding='utf-8').read(),'lxml')
for el in s.find_all(string=re.compile(r'共\s*\d+\s*条|找到\s*\d+')): print('COUNT:',el.strip()[:60])
# rows: print only std number, title, hcno; never dates/status
for tr in s.find_all('tr'):
    tds=tr.find_all('td')
    if len(tds)<3: continue
    a=tr.find('a',onclick=True) or tr.find('a',href=True)
    hc=re.search(r"[0-9A-F]{32}", str(tr))
    txt=[t.get_text(' ',strip=True) for t in tds]
    no=[t for t in txt if re.match(r'^GB',t)]
    title=[t for t in txt if re.search(r'[一-鿿]',t) and not re.search(r'现行|废止|即将实施|强制性|推荐性',t)]
    print(no[:1],title[:1],hc.group(0) if hc else None)
