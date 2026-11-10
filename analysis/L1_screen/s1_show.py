import json,sys,re
d=json.load(open(sys.argv[1]))
seen={}
for b in d['results']['bindings']:
    c=b['celex']['value']; t=b.get('title',{}).get('value','')
    t=re.sub(r'\s+',' ',t.replace(' ',' '))
    t=re.sub(r' of \d{1,2} \w+ \d{4}','',t)  # strip adoption date
    seen.setdefault(c,t)
print('HITS',len(seen))
for c,t in seen.items(): print(c,'|',t[:500])
