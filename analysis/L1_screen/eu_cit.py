import sys; sys.path.insert(0,"<home>/.local/lib/python3.10/site-packages")
import re, warnings
from bs4 import BeautifulSoup
warnings.filterwarnings("ignore")
s=BeautifulSoup(open(sys.argv[1],encoding='utf-8').read().replace(' ',' '),'lxml')
for c in s.find_all(id=re.compile(r'^cit_\d+$')): print('CIT:',c.get_text(' ',strip=True)[:300])
