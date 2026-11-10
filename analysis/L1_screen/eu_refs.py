import sys; sys.path.insert(0,"<home>/.local/lib/python3.10/site-packages")
import re, json, warnings
from bs4 import BeautifulSoup
warnings.filterwarnings("ignore")
# usage: eu_refs.py file.html scope_ids(comma or "") out.json [extra_excluded_ids]
f=sys.argv[1]
raw=open(f,encoding='utf-8').read().replace(' ',' ').replace('&nbsp;',' ')
s=BeautifulSoup(raw,'lxml')
full_with_notes=s.get_text(' ',strip=True)
for n in s.find_all(class_=re.compile(r'^(oj-note|note)$')): n.decompose()
t=s.find(class_='eli-main-title') or s.find(class_='doc-ti') or s.find(class_='oj-doc-ti')
print('TITLE:', t.get_text(' ',strip=True)[:600] if t else None)
arts=[u for u in s.find_all(id=re.compile(r'^art_\d+[a-z]*$'))]
heads={}
for u in arts:
    h=u.find(class_=re.compile('stitle-article-norm|oj-sti-art|eli-title'))
    heads[u['id']]=(h.get_text(' ',strip=True) if h else u.get_text(' ',strip=True)[:100])
excl=[k for k,v in heads.items() if re.search(r'transitional',v,re.I)]
if len(sys.argv)>4: excl+=sys.argv[4].split(',')
print('ARTICLES:',len(arts),'EXCLUDED (transitional):',excl, [heads.get(e,'')[:60] for e in excl])
for sid in [x for x in sys.argv[2].split(',') if x]:
    u=s.find(id=sid); print('SCOPE',sid,':',u.get_text(' ',strip=True)[:2500])
texts=[(u['id'],u.get_text(' ',strip=True)) for u in arts if u['id'] not in excl]
# annex region: everything after the final part (fnp_1) / signature
full=s.get_text(' ',strip=True)
fnp=s.find(id='fnp_1')
ann=''
if fnp:
    ft=fnp.get_text(' ',strip=True)
    i=full.find(ft)
    if i>=0: ann=full[i+len(ft):]
texts.append(('annexes',ann))
print('ANNEX REGION CHARS',len(ann))
pat=re.compile(r'(Regulation \((?:EU|EC|EEC)\) (?:No )?\d+/\d+|(?:Council |Commission )?Directive (?:\(EU\) )?\d+/\d+(?:/E[CU]|/EEC)?|Decision (?:No )?\d+/\d+/E[CU]|UN(?:/ECE)? Regulation No\.? ?\d+|UN Regulation \d+|(?:UN )?GTR (?:No\.? )?\d+|global technical regulation (?:No\.? )?\d+|\bISO(?:/IEC)? \d+(?:-\d+)*|\bIEC \d+(?:-\d+)*|\bEN \d+(?:-\d+)*|\bSAE J\d+(?:/\d+)?|\bCISPR \d+|\bDIN \d+|\bSAE [A-Z]+\d+)')
refs={}
for uid,txt in texts:
    for m in pat.finditer(txt):
        k=re.sub(r'\s+',' ',m.group(1))
        refs.setdefault(k,{}).setdefault(uid,0); refs[k][uid]+=1
out={}
for k,v in refs.items():
    ms=[m.group(0) for m in re.finditer(re.escape(k)+r'[^()]{0,40}?(?: of [^()]{0,60}?)? (?:on|concerning|laying down|establishing|relating to|setting|—|-|–)[^.;()]{0,220}', full_with_notes)]
    ti=max(ms,key=len) if ms else ''
    out[k]={'cited_in':v,'title_ctx':ti[:300]}
json.dump(out,open(sys.argv[3],'w'),indent=1,ensure_ascii=False)
print('NREFS',len(out))
for k,v in out.items(): print(' *',k,'|',list(v['cited_in'])[:6],'|',v['title_ctx'][:160])
