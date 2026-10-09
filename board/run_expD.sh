#!/bin/sh
# Analysis Brief Exp D: re-confirm the training-memory numbers on the board with the LARGE-data (Changan)
# fleet model. Same harness/discipline as run_all.sh (governor pinned + restored, cores 4-5, census first,
# timeout -k), E2 (full SGD/Adam) + E3 (last/head x SGD/Adam), 2 reps each.
#   cd /tmp/batt_ft && sh board/run_expD.sh runs/chf_primary_k0 results/expD
set -eu
RUN=${1:?run dir}
OUT=${2:-results/expD}
mkdir -p "$OUT"
ORIG_GOV=$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor)
restore() { for g in /sys/devices/system/cpu/cpu[0-9]*/cpufreq/scaling_governor; do echo "$ORIG_GOV" > "$g"; done; echo "governor restored -> $ORIG_GOV"; }
trap restore EXIT INT TERM
for g in /sys/devices/system/cpu/cpu[0-9]*/cpufreq/scaling_governor; do echo performance > "$g"; done
python3 board/census.py --interval 5 --json "$OUT/census_expD.json"
timeout -k 10 3000 taskset -c 4,5 python3 board/e3_lastlayer.py --run "$RUN" --out "$OUT/e3" --reps 2 --threads 2
timeout -k 10 3000 taskset -c 4,5 python3 board/e2_fullretrain.py --run "$RUN" --out "$OUT/e2" --reps 2 --threads 2
echo "EXPD DONE"
