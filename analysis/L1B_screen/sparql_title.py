import sys, urllib.request, urllib.parse
needle, out = sys.argv[1], sys.argv[2]
q = """PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
SELECT DISTINCT ?celex ?title WHERE {
 ?e cdm:expression_belongs_to_work ?w ; cdm:expression_uses_language <http://publications.europa.eu/resource/authority/language/ENG> ; cdm:expression_title ?title .
 FILTER(CONTAINS(STR(?title), "%s"))
 ?w cdm:resource_legal_id_celex ?celex . FILTER(STRSTARTS(STR(?celex), "3"))
}""" % needle
url = "https://publications.europa.eu/webapi/rdf/sparql?" + urllib.parse.urlencode({"query": q, "format": "application/sparql-results+json"})
req = urllib.request.Request(url, headers={"User-Agent": "L1B-screener research fetch (public regulatory texts)"})
open(out, "wb").write(urllib.request.urlopen(req, timeout=120).read())
