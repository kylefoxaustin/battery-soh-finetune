#!/bin/bash
# usage: fetch.sh NAME URL  -> saves to web/NAME, logs to out/fetchlog.tsv
S=<scratch>/l1_screen
sleep 2
code=$(curl -gsL --compressed -o "$S/web/$1" -w "%{http_code}" -A "L1-screener research fetch (public regulatory texts)" -m 60 "$2")
sz=$(stat -c %s "$S/web/$1" 2>/dev/null)
printf "%s\t%s\t%s\t%s\t%s\n" "$(date -Is)" "$1" "$2" "$code" "$sz" >> $S/out/fetchlog.tsv
echo "$code $sz $1"
