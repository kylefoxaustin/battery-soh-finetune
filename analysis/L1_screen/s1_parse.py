import sys; sys.path.insert(0,"<home>/.local/lib/python3.10/site-packages")
import re, warnings, json
from bs4 import BeautifulSoup
warnings.filterwarnings("ignore")
s=BeautifulSoup(open(sys.argv[1],encoding='utf-8'),'lxml')
# hit count
for el in s.find_all(string=re.compile(r'\d+\s+results? found|Results \d')):
    print('COUNT:', el.strip()[:100])
res=[]
for a in s.select('a.title'):
    href=a.get('href',''); m=re.search(r'CELEX[:%3A]+(\w+)',href)
    res.append({'celex':m.group(1) if m else href,'title':a.get_text(' ',strip=True)})
for r in res: print(r['celex'],'|',r['title'][:400])
if len(sys.argv)>2: json.dump(res,open(sys.argv[2],'w'),indent=1,ensure_ascii=False)
