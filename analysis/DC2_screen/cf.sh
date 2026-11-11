#!/bin/bash
# cf.sh URL NAME : curl fallback fetch (same UA, 60 s timeout), logs status, converts like f.sh
S=<scratch>/dc2_screen
sleep 2
F=$S/web/$2
code=$(curl -sS -L --max-time 60 --retry 2 -A "DC2-screener research fetch (public grid and power-quality texts)" -o "$F" -w '%{http_code} %{url_effective} %{content_type} %{size_download}' "$1" 2>&1)
python3 -c "import json,sys,time;c=sys.argv[2].split(' ');print(json.dumps({'url':sys.argv[1],'out':sys.argv[3],'t':time.strftime('%Y-%m-%dT%H:%M:%S'),'status':c[0],'final_url':c[1] if len(c)>1 else '','ctype':c[2] if len(c)>2 else '','bytes':c[3] if len(c)>3 else '','via':'curl'}))" "$1" "$code" "$2" | tee -a $S/out/fetchlog.jsonl | cut -c1-250
[ -s "$F" ] || exit 0
if head -c 2 "$F" | grep -q 'PK'; then python3 -I $S/scripts/docx2txt.py "$F" "$F.txt";
elif head -c 5 "$F" | grep -q '%PDF'; then pdftotext -layout "$F" "$F.txt" && echo "pdf pages: $(pdfinfo "$F" 2>/dev/null | grep Pages)";
else python3 -I $S/scripts/show.py html2txt "$F" "$F.txt"; fi
