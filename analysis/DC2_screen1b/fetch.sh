#!/bin/bash
# usage: fetch.sh URL OUTNAME ; appends to fetch log
B=<scratch>/dc2_screen1b
out="$B/web/$2"
r=$(curl -sS -L --max-time 60 -A 'DC2-screener research fetch (public grid and power-quality texts)' -o "$out" -w '%{http_code}\t%{url_effective}\t%{content_type}\t%{size_download}' "$1" 2>&1)
printf '%s\t%s\t%s\t%s\n' "$(date -Iseconds)" "$1" "$2" "$r" >> $B/scripts/fetch_log.tsv
printf '%s\t%s\n' "$2" "$r"
sleep 2
