# usage: gb_find.py mode term out.json ; mode=num (exact 'GB <num>-yyyy', current only) or title (title contains term, current only)
import sys,json,re,urllib.request,urllib.parse,time
mode,term,out=sys.argv[1:4]
url="https://std.samr.gov.cn/gb/search/gbQueryPage?"+urllib.parse.urlencode({"searchText":term,"ics":"","state":"","ISSUE_DATE":"","sortOrder":"asc","pageSize":50,"pageNumber":1})
req=urllib.request.Request(url,headers={"User-Agent":"L1B-screener research fetch (public regulatory texts)"})
d=json.load(urllib.request.urlopen(req,timeout=60))
rows=d.get('rows',[])
def code(r): return re.sub(r"<[^>]+>","",r['C_STD_CODE']).strip()
def name(r): return re.sub(r"<[^>]+>","",r['C_C_NAME']).strip()
if mode=='num':
    m=[r for r in rows if re.fullmatch(r"GB(/T)? %s-\d{4}"%re.escape(term), code(r))]
else:
    m=[r for r in rows if term in name(r)]
cur=[r for r in m if r['STATE']=='现行'] or [r for r in m if r['STATE']=='即将实施']
if not cur and m:
    # no current edition: take only the most recent edition (by identifier year); other editions are not printed
    if mode=='num': cur=[max(m,key=lambda r:code(r)[-4:])]
    else:
        by={}
        for r in m: k=code(r)[:-5]; by[k]=max([by.get(k,r),r],key=lambda r:code(r)[-4:])
        cur=list(by.values())
res={"query_url":url,"total_hits":d.get('total'),"rows_returned":len(rows),"matching_identifier_or_title":len(m),"current":[{"id":r['id'],"code":code(r),"title_zh":name(r),"nature":r['STD_NATURE'],"state":r['STATE']} for r in cur]}
json.dump(res,open(out,'w'),ensure_ascii=False,indent=1)
print(term, "hits",d.get('total'),"matching",len(m),"current:",[(x['code'],x['title_zh'],x['nature'],x['id']) for x in res['current']])
