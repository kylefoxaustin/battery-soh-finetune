# Broader: titles containing 'No N' or 'No. N' and 'Regulation', CELEX sector 4 or 3. Prints only non-amendment titles; counts excluded.
import sys, json, urllib.request, urllib.parse, re, time
ns=sys.argv[1].split(','); out=sys.argv[2]; res={}
for n in ns:
    q = """PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
SELECT DISTINCT ?celex ?title ?d WHERE {
 ?e cdm:expression_belongs_to_work ?w ; cdm:expression_uses_language <http://publications.europa.eu/resource/authority/language/ENG> ; cdm:expression_title ?title .
 FILTER(CONTAINS(STR(?title), "Regulation No %s ") || CONTAINS(STR(?title), "Regulation No. %s ") || CONTAINS(STR(?title), "Regulation No %s "))
 ?w cdm:resource_legal_id_celex ?celex . OPTIONAL { ?w cdm:work_date_document ?d }
}""" % (n,n,n)
    url = "https://publications.europa.eu/webapi/rdf/sparql?" + urllib.parse.urlencode({"query": q, "format": "application/sparql-results+json"})
    req = urllib.request.Request(url, headers={"User-Agent": "L1B-screener research fetch (public regulatory texts)"})
    try: b = json.load(urllib.request.urlopen(req, timeout=300))['results']['bindings']
    except Exception as ex: print(n,"ERROR",ex); res[n]={"error":str(ex)}; continue
    full=[x for x in b if re.match(r"^(UN\s+)?Regulation\s+No\.?\s*%s\b"%n, x['title']['value'].strip(), re.I) and not re.search(r"corrigendum|amendments? to|supplement", x['title']['value'], re.I) and not re.search(r"R\(\d+\)", x["celex"]["value"]) and x["celex"]["value"].startswith("4") and re.search(r"Economic Commission|UN Regulation", x["title"]["value"])]
    full.sort(key=lambda x:(x.get('d',{}).get('value',''), x['celex']['value']))
    print(n, "all hits", len(b), "full-text", len(full))
    if full:
        c=full[-1]; t=re.sub(r"\s*\[\d{4}/\d+\]\s*$","",c['title']['value']).strip()
        print("  ->", c['celex']['value'], t[:250]); res[n]={"hits_all":len(b),"hits_full":len(full),"celex":c['celex']['value'],"title":t,"query":q}
    else: res[n]={"hits_all":len(b),"hits_full":0,"query":q}
    time.sleep(1)
json.dump(res, open(out,"w"), indent=1, ensure_ascii=False)
