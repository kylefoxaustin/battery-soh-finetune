#!/bin/bash
# f.sh URL NAME : fetch into web/, log; if pdf, pdftotext -layout to web/NAME.txt; if html, html2txt to NAME.txt
S=<scratch>/dc2_screen
python3 -I $S/scripts/fetch.py "$1" "$2" $S/out/fetchlog.jsonl $S/web | cut -c1-400
F=$S/web/$2
[ -f "$F" ] || exit 0
if head -c 2 "$F" | grep -q 'PK'; then python3 -I $S/scripts/docx2txt.py "$F" "$F.txt";
elif head -c 5 "$F" | grep -q '%PDF'; then pdftotext -layout "$F" "$F.txt" && echo "pdf pages: $(pdfinfo "$F" 2>/dev/null | grep Pages)"; 
else python3 -I $S/scripts/show.py html2txt "$F" "$F.txt"; fi
