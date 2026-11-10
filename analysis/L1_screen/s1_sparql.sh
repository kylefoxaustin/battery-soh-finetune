#!/bin/bash
# usage: s1_sparql.sh CELEX outname
S=<scratch>/l1_screen
Q="PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
SELECT DISTINCT ?celex ?title WHERE {
 ?base cdm:resource_legal_id_celex \"$1\"^^<http://www.w3.org/2001/XMLSchema#string> .
 ?act cdm:resource_legal_based_on_resource_legal ?base .
 ?act cdm:resource_legal_id_celex ?celex .
 OPTIONAL { ?exp cdm:expression_belongs_to_work ?act ; cdm:expression_uses_language <http://publications.europa.eu/resource/authority/language/ENG> ; cdm:expression_title ?title . }
} ORDER BY ?celex"
sleep 2
curl -s -m 60 -A "L1-screener research fetch (public regulatory texts)" -H "Accept: application/sparql-results+json" --data-urlencode "query=$Q" https://publications.europa.eu/webapi/rdf/sparql -o $S/web/$2
printf "%s\t%s\t%s\t%s\n" "$(date -Is)" "$2" "SPARQL publications.europa.eu legal_based_on $1" "$(stat -c %s $S/web/$2)" >> $S/out/fetchlog.tsv
