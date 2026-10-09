#!/bin/sh
# Decompose E3's training-phase memory delta: is it per-step workload or a one-time runtime cost?
# Same configs as E2/E3, but --steps 1 vs the standard 60. If delta(1 step) ~= delta(60 steps), the
# delta is a fixed cost of the first backward/optimizer step (autograd engine, allocator), not memory
# that scales with what is being trained. Run on the board, governor pinned, cores 4,5.
set -eu
RUN=${1:-runs/ds1}
OUT=${2:-results/raw/probe}
mkdir -p "$OUT"
ORIG_GOV=$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor)
restore() { for g in /sys/devices/system/cpu/cpu[0-9]*/cpufreq/scaling_governor; do echo "$ORIG_GOV" > "$g"; done; echo "governor restored -> $ORIG_GOV"; }
trap restore EXIT INT TERM
for g in /sys/devices/system/cpu/cpu[0-9]*/cpufreq/scaling_governor; do echo performance > "$g"; done
python3 board/census.py --interval 5 --json "$OUT/census_probe.json"
for cfg in "last sgd" "full sgd"; do
  set -- $cfg
  for r in 0 1; do
    timeout -k 10 900 taskset -c 4,5 python3 board/train_mem.py --scope $1 --opt $2 --run "$RUN" --threads 2 \
        --steps 1 --out "$OUT/${1}_${2}_steps1_r$r.json"
  done
done
echo "PROBE DONE"
