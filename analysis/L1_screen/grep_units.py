import sys; sys.path.insert(0,"<home>/.local/lib/python3.10/site-packages")
import re, warnings
from bs4 import BeautifulSoup
warnings.filterwarnings("ignore")
s=BeautifulSoup(open(sys.argv[1],encoding='utf-8'),'lxml')
pat=re.compile(sys.argv[2])
excl=set(sys.argv[3].split(',')) if len(sys.argv)>3 else set()
for u in s.find_all(id=re.compile(r'^(art_\d+[a-z]*|anx_[A-Z0-9]+)$')):
    if u['id'] in excl: continue
    txt=u.get_text(' ',strip=True)
    for m in pat.finditer(txt):
        print(u['id'],'|',txt[max(0,m.start()-100):m.end()+120])
