#!/bin/sh
# Run E1-E4 on the FRDM-IMX95-PRO under the brief's measurement discipline. Run ON THE BOARD from the
# staged tree (default /tmp/batt_ft). Requires: nothing else running on the board.
#
#   cd /tmp/batt_ft && sh board/run_all.sh runs/ds1 results/raw          (SKIP_E4=1 to stop after E3; ONLY_E4=1 for E4 alone)
#
# - governor pinned to `performance` for the run, ORIGINAL governor restored on any exit (trap)
# - E1 pinned to one A55 core (5); training experiments pinned to cores 4,5 with 2 torch threads
# - a census (CPU delta over 5 s, binaries via /proc/PID/exe) is recorded before every experiment
# - every child is wrapped in `timeout -k` so a wedged run is SIGKILLed, not left as a corpse
set -eu
RUN=${1:-runs/ds1}
OUT=${2:-results/raw}
INF_CORES=5
TRAIN_CORES=4,5
mkdir -p "$OUT"

ORIG_GOV=$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor)
restore() {
    for g in /sys/devices/system/cpu/cpu[0-9]*/cpufreq/scaling_governor; do echo "$ORIG_GOV" > "$g"; done
    echo "governor restored -> $(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor)"
}
trap restore EXIT INT TERM
for g in /sys/devices/system/cpu/cpu[0-9]*/cpufreq/scaling_governor; do echo performance > "$g"; done
echo "governor: $ORIG_GOV -> $(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor)"

census() { python3 board/census.py --interval 5 --json "$OUT/census_$1.json"; }

if [ "${ONLY_E4:-0}" != 1 ]; then
census e1
timeout -k 10 600 taskset -c $INF_CORES python3 board/e1_inference.py --run "$RUN" --threads 1 --out "$OUT/e1.json"
timeout -k 10 600 taskset -c $INF_CORES python3 board/e1_inference.py --run "$RUN" --threads 1 \
    --model soh_fp32.tflite --out "$OUT/e1_fp32.json"

census e2
timeout -k 10 3600 taskset -c $TRAIN_CORES python3 board/e2_fullretrain.py --run "$RUN" --out "$OUT/e2" --threads 2
census e3
timeout -k 10 3600 taskset -c $TRAIN_CORES python3 board/e3_lastlayer.py --run "$RUN" --out "$OUT/e3" --threads 2

[ "${SKIP_E4:-0}" = 1 ] && { census end; echo "E1-E3 DONE (E4 skipped)"; exit 0; }
fi
census e4
timeout -k 10 7200 taskset -c $TRAIN_CORES python3 board/e4_pervehicle.py --run "$RUN" --threads 2 --out "$OUT/e4.json"
timeout -k 10 7200 taskset -c $TRAIN_CORES python3 board/e4_pervehicle.py --run "$RUN" --threads 2 \
    --ft-frac 0.1 --out "$OUT/e4_ft10.json"
census end
echo "ALL DONE"
