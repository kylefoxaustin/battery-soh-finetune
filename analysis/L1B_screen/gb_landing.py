# usage: gb_landing.py <txt of openstd page> -> prints only identifier, zh title, en title, issuing body labels
import sys,re
t=open(sys.argv[1]).read()
out={}
for lab,key in [("标准号","id"),("中文标准名称","zh"),("英文标准名称","en")]:
    m=re.search(lab+r"：\s*([^\n]+)",t); out[key]=m.group(1).strip() if m else None
for lab,key in [("主管部门","dept"),("归口部门","tc"),("发布单位","issuer")]:
    m=re.search(r"\n"+lab+r"\n([^\n]+)",t); out[key]=m.group(1).strip() if m else None
print(out)
