import sys; sys.path.insert(0,"<home>/.local/lib/python3.10/site-packages")
import sys,re
from bs4 import BeautifulSoup
s=BeautifulSoup(open(sys.argv[1],encoding='utf-8'),'lxml')
ids=[d.get('id') for d in s.find_all(id=True)]
top=[i for i in ids if re.match(r'^(art_\d+[a-z]*|anx_[A-Z0-9]+|rct_1|pbl_1|cit_1|fnp_1|enc_1)$',i)]
print(len(ids), top[:200])
t=s.find(class_='eli-main-title') or s.find(class_='doc-ti')
print('TITLE:', t.get_text(' ',strip=True) if t else None)
