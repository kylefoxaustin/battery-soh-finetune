import sys, json, urllib.request, urllib.parse, re, time
base = sys.argv[1]  # e.g. 32019R2144
out = sys.argv[2]
q = """PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
SELECT DISTINCT ?celex ?title WHERE {
 ?b cdm:resource_legal_id_celex ?bc . FILTER(str(?bc)="%s")
 ?w cdm:resource_legal_based_on_resource_legal ?b .
 ?w cdm:resource_legal_id_celex ?celex .
 OPTIONAL { ?e cdm:expression_belongs_to_work ?w ; cdm:expression_uses_language <http://publications.europa.eu/resource/authority/language/ENG> ; cdm:expression_title ?title . }
}""" % base
url = "https://publications.europa.eu/webapi/rdf/sparql?" + urllib.parse.urlencode({"query": q, "format": "application/sparql-results+json"})
req = urllib.request.Request(url, headers={"User-Agent": "L1B-screener research fetch (public regulatory texts)"})
data = urllib.request.urlopen(req, timeout=60).read()
open(out, "wb").write(data)
print(url[:120])
