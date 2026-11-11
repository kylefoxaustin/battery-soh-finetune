#!/bin/bash
# usage: fetch.sh URL OUTFILE  -> logs url,status,out to web/fetchlog.tsv
D=<scratch>/l1b_screen
UA='L1B-screener research fetch (public regulatory texts)'
code=$(curl -sL --compressed -m 60 -A "$UA" -o "$2" -w '%{http_code}' "$1")
printf '%s\t%s\t%s\t%s\n' "$(date -u +%FT%TZ)" "$code" "$1" "$2" >> $D/web/fetchlog.tsv
echo "$code $(stat -c %s "$2" 2>/dev/null) $2"
sleep 1
