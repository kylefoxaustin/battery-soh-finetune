#!/bin/bash
S=<scratch>/dc2_screen
m=$1; n=$2; shift 2
if [ "$m" = links ]; then python3 -I $S/scripts/show.py links "$S/web/$n" "$@"; else python3 -I $S/scripts/show.py $m "$S/web/$n.txt" "$@"; fi
