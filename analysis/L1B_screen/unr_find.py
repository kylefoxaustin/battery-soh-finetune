# Find the most recent EUR-Lex OJ publication of the full text of UN Regulation No N.
# Prints only: N, number of matching full-text publications, chosen CELEX, title (bracketed OJ ref stripped).
import sys, json, urllib.request, urllib.parse, re, time
ns = sys.argv[1].split(',')
out = sys.argv[2]
res = {}
for n in ns:
    q = """PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
SELECT DISTINCT ?celex ?title ?d WHERE {
 ?e cdm:expression_belongs_to_work ?w ; cdm:expression_uses_language <http://publications.europa.eu/resource/authority/language/ENG> ; cdm:expression_title ?title .
 FILTER(REGEX(STR(?title), "^(UN\\\\s+)?Regulation\\\\s+No\\\\.?\\\\s*%s\\\\s*(of the|–|-|—|:)", "i"))
 ?w cdm:resource_legal_id_celex ?celex . OPTIONAL { ?w cdm:work_date_document ?d }
}""" % n
    url = "https://publications.europa.eu/webapi/rdf/sparql?" + urllib.parse.urlencode({"query": q, "format": "application/sparql-results+json"})
    req = urllib.request.Request(url, headers={"User-Agent": "L1B-screener research fetch (public regulatory texts)"})
    try:
        b = json.load(urllib.request.urlopen(req, timeout=120))['results']['bindings']
    except Exception as ex:
        print(n, "ERROR", ex); res[n] = {"error": str(ex)}; continue
    b = [x for x in b if not re.search(r"corrigendum|amendments? to|supplement", x['title']['value'], re.I) and not re.search(r"R\(\d+\)", x['celex']['value'])]
    b.sort(key=lambda x: (x.get('d', {}).get('value', ''), x['celex']['value']))
    if not b:
        print(n, 0); res[n] = {"hits": 0}; continue
    c = b[-1]
    t = re.sub(r"\s*\[\d{4}/\d+\]\s*$", "", c['title']['value']).strip()
    res[n] = {"hits": len(b), "celex": c['celex']['value'], "title": t, "query": q}
    print(n, len(b), c['celex']['value'], t[:250])
    time.sleep(1)
json.dump(res, open(out, "w"), indent=1, ensure_ascii=False)
