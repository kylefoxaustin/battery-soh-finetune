import sys,re,json
# usage: unreg_refs.py text.txt out.json  (UN regulation text via pdftotext -layout)
L=open(sys.argv[1],encoding='utf-8',errors='replace').read().split('\n')
sc=[i for i,l in enumerate(L) if re.match(r'^\s*1\.\s+Scope\b',l,re.I)]
start=sc[1] if len(sc)>1 else (sc[0] if sc else 0)
# if first 'Scope' is followed within 3 lines by '2. Definitions' it's the contents list
for i in sc:
    nxt=' '.join(L[i+1:i+4])
    if not re.search(r'^\s*2\.\s+Definitions',nxt,re.M) and not re.search(r'\n\s*2\.\s+\w',('\n'.join(L[i+1:i+3]))):
        start=i;break
if len(sys.argv)>3:
    b=[i for i,l in enumerate(L) if re.match(sys.argv[3],l)]
    start=b[-1]
# scope text
sc_txt=[]
for l in L[start:start+60]:
    if re.match(r'^\s*2\.\s+\S',l) and sc_txt: break
    sc_txt.append(l.strip())
print('BODY START LINE',start)
print('SCOPE:',re.sub(r'\s+',' ',' '.join(sc_txt))[:1500])
# transitional section
tr=None
for i in range(start,len(L)):
    m=re.match(r'^\s*(\d+)\.\s+Transitional provisions',L[i],re.I)
    if m: tr=(i,int(m.group(1)));break
excl=set()
if tr:
    i0,n=tr
    for j in range(i0+1,len(L)):
        if re.match(r'^\s*Annex\s+\d',L[j],re.I) or re.match(r'^\s*%d\.\s+[A-Z]'%(n+1),L[j]):
            break
    excl=set(range(i0,j))
    print('TRANSITIONAL EXCLUDED LINES',i0,'-',j,'(not printed)')
pat=re.compile(r'(UN\s+Regulations?\s+Nos?\.?\s*\d+(?:\s*(?:,|and)\s*\d+)*|(?<!UN )Regulations?\s+Nos?\.?\s*\d+(?:\s*(?:,|and)\s*\d+)*|UN\s+GTR\s+No\.?\s*\d+|(?:UN\s+)?Global\s+Technical\s+Regulation\s+No\.?\s*\d+|\bGTR\s+No\.?\s*\d+|\bISO(?:/IEC|/TS|/TR|/PAS)?\s+\d+(?:[-‑]\d+)*|\bIEC(?:/TS|/TR)?\s+\d+(?:[-‑]\d+)*|\bCISPR\s+\d+|\bSAE\s+J\s?\d+(?:/\d+)?|\bEN\s+\d+(?:[-‑]\d+)*|\bASTM\s+[A-Z]\s?\d+|\bJIS\s+[A-Z]\s?\d+|\bECE/TRANS/WP\.29/\d+(?:/Rev\.\d+)?|\bGB(?:/T)?\s+\d+(?:\.\d+)?|\bFMVSS\s+(?:No\.?\s*)?\d+|\bDirective\s+\d+/\d+/E[CU]+|\bRegulation\s+\((?:EU|EC)\)\s+(?:No\s+)?\d+/\d+|\bUN\s+Rule\s+No\.?\s*\d+|\bRule\s+No\.?\s*\d+)')
refs={}; clause='?'; annex=''
for i in range(start,len(L)):
    l=L[i]
    m=re.match(r'^\s*Annex\s+(\d+[A-Z]?)\b',l,re.I)
    if m: annex='Annex '+m.group(1); clause=''
    m=re.match(r'^\s*(\d+(?:\.\d+)*\.?)\s{2,}\S',l)
    if m and not re.match(r'^\d{1,2}\.\d{1,2}\.(19|20)\d\d',m.group(1)): clause=m.group(1)
    if i in excl: continue
    seg=l+' '+(L[i+1] if i+1<len(L) else '')
    for m in pat.finditer(l):
        k=re.sub(r'\s+',' ',m.group(1)).replace('‑','-')
        loc=(annex+' ' if annex else '')+clause
        refs.setdefault(k,[])
        if loc not in refs[k]: refs[k].append(loc)
json.dump(refs,open(sys.argv[2],'w'),indent=1,ensure_ascii=False)
print('NREFS',len(refs))
for k,v in sorted(refs.items()): print(' *',k,'|',v[:6])
