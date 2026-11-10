import sys; sys.path.insert(0,"<home>/.local/lib/python3.10/site-packages")
import re,warnings
from bs4 import BeautifulSoup
warnings.filterwarnings("ignore")
s=BeautifulSoup(open(sys.argv[1],encoding='utf-8').read(),'lxml')
for x in s(['script','style']): x.decompose()
t=re.sub(r'\s+',' ',s.get_text(' ',strip=True))
m=re.search(r'中文标准名称[：:]\s*(.*?)\s*英文标准名称[：:]\s*(.*?)\s*标准状态',t)
if m: print('ZH:',m.group(1)); print('EN:',m.group(2))
else: print('NO MATCH')
print('ONLINE-PREVIEW-BUTTON:', '在线预览' in t, '| DOWNLOAD:', '下载标准' in t)
