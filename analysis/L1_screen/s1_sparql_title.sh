#!/bin/bash
# usage: s1_sparql_title.sh "2023/1542" outname   -> sector-3 acts (CELEX 3...) adopted 2016+ whose English title contains the base act number
S=<scratch>/l1_screen
Q="PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
SELECT DISTINCT ?celex ?title WHERE {
 ?exp cdm:expression_uses_language <http://publications.europa.eu/resource/authority/language/ENG> ; cdm:expression_title ?title ; cdm:expression_belongs_to_work ?act .
 ?act cdm:resource_legal_id_celex ?celex .
 FILTER(STRSTARTS(STR(?celex),\"3201\") || STRSTARTS(STR(?celex),\"3202\"))
 FILTER(CONTAINS(REPLACE(STR(?title),\"\\\\s\",\" \"),\"$1\"))
} ORDER BY ?celex"
sleep 2
curl -s -m 120 -A "L1-screener research fetch (public regulatory texts)" -H "Accept: application/sparql-results+json" --data-urlencode "query=$Q" https://publications.europa.eu/webapi/rdf/sparql -o $S/web/$2
printf "%s\t%s\t%s\t%s\n" "$(date -Is)" "$2" "SPARQL publications.europa.eu title-contains $1 (CELEX 3201*/3202*)" "$(stat -c %s $S/web/$2)" >> $S/out/fetchlog.tsv
