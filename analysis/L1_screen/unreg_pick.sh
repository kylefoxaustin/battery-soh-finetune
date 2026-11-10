#!/bin/bash
# usage: unreg_pick.sh N  -> queries EUR-Lex metadata for OJ publications of UN Regulation No N; saves raw json; prints ONLY count + chosen CELEX + its title
S=<scratch>/l1_screen
N=$1
Q="PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
SELECT DISTINCT ?celex ?title ?date WHERE {
 ?exp cdm:expression_uses_language <http://publications.europa.eu/resource/authority/language/ENG> ; cdm:expression_title ?title ; cdm:expression_belongs_to_work ?act .
 ?act cdm:resource_legal_id_celex ?celex .
 OPTIONAL { ?act cdm:work_date_document ?date . }
 FILTER(STRSTARTS(STR(?celex),\"4\"))
 FILTER(REGEX(STR(?title),\"^(UN )?Regulation No[.]?[^0-9]?$N([^0-9]|$)\"))
}"
sleep 2
curl -s -m 120 -A "L1-screener research fetch (public regulatory texts)" -H "Accept: application/sparql-results+json" --data-urlencode "query=$Q" https://publications.europa.eu/webapi/rdf/sparql -o $S/web/unreg_$N.json
printf "%s\t%s\t%s\t%s\n" "$(date -Is)" "unreg_$N.json" "SPARQL publications.europa.eu OJ publications titled 'UN Regulation No $N'/'Regulation No $N'" "$(stat -c %s $S/web/unreg_$N.json)" >> $S/out/fetchlog.tsv
python3 -I - "$S/web/unreg_$N.json" <<'PY'
import json,sys,re
d=json.load(open(sys.argv[1]))['results']['bindings']
rows=[(b['celex']['value'],b['title']['value'],b.get('date',{}).get('value','')) for b in d]
# base texts only (not amendments/supplements/corrigenda); choose most recent by document date; print nothing else
base=[r for r in rows if not re.search(r'amend|supplement|corrig|addend|erratum',r[1],re.I)]
print('HITS',len(set(r[0] for r in rows)),'BASE-TEXT HITS',len(set(r[0] for r in base)))
if base:
    c=max(base,key=lambda r:r[2])
    t=re.sub(r'\s+',' ',c[1].replace(' ',' '))
    t=re.sub(r'\b(Revision|Rev\.?) ?\d+.*$','',t)
    print('CHOSEN',c[0],'|',t[:300])
PY
