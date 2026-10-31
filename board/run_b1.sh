#!/bin/sh
# B1 protocol (briefs/B1/README.md §4.5). Run ON THE BOARD from the staged tree (/tmp/b1), detached:
#   cd /tmp/b1 && setsid nohup sh board/run_b1.sh out /mnt/b1 1 2 3 > out/run.log 2>&1 &
# Rounds (one session each): P0 baseline 10 min with the real-time loads running, then P1-P4 (30 min each; P5 10 min in
# rounds 1-2), the real-time loads continuing throughout; then the loads stop and P6 (eMMC, rounds 1-2) runs alone.
# Cores (brief §2): 0 OS + runner + census, 1 inference, 2 limiter, 3 producer, 4 dumper, 5 monitor.
# Governor pinned to performance, ORIGINAL restored on exit; census before and after every phase; timeout -k on every
# child. A phase that fails is recorded and the protocol continues (brief §4.5: no silent rerun).
set -u
OUT=$1; DUMP=$2; shift 2
ROUNDS=${*:-1 2 3}
mkdir -p "$OUT"
TL="$OUT/timeline.jsonl"
ORIG_GOV=$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor)
LOADS=""
restore() {
    for p in $LOADS; do kill -TERM "$p" 2>/dev/null; done
    for g in /sys/devices/system/cpu/cpu[0-9]*/cpufreq/scaling_governor; do echo "$ORIG_GOV" > "$g"; done
    echo "governor restored -> $(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor)"
}
trap restore EXIT INT TERM
for g in /sys/devices/system/cpu/cpu[0-9]*/cpufreq/scaling_governor; do echo performance > "$g"; done
mark() { echo "{\"round\": $1, \"phase\": \"$2\", \"event\": \"$3\", \"wall\": $(date +%s.%N)}" >> "$TL"; }
census() { taskset -c 0 python3 board/census.py --interval 10 --json "$OUT/census_r$1_$2.json" > /dev/null 2>&1; }

[ -f "$OUT/rand1g.bin" ] || head -c 1073741824 /dev/urandom > "$OUT/rand1g.bin"
R96="h/luts.bin h/frames_96.bin ref/gate_out_96.bin"
R3564="h2/luts.bin h2/frames_3564.bin ref/gate_out_3564.bin"

ring() {  # round phase rate ring_mb duration triggers...
    r=$1; ph=$2; rate=$3; mb=$4; dur=$5; shift 5
    census "$r" "${ph}_before"
    mark "$r" "$ph" start
    timeout -k 10 $(( ${dur%.*} + 900 )) taskset -c 3,4 board/b1_ring "$rate" "$mb" "$dur" 3 4 "$DUMP" \
        "$OUT/ring_r${r}_${ph}.json" "$@" >> "$OUT/ring.log" 2>&1 || echo "PHASE FAILED r$r $ph rc=$?" >> "$OUT/ring.log"
    mark "$r" "$ph" end
    census "$r" "${ph}_after"
}

for r in $ROUNDS; do
    LEN=9000                                   # upper bound on the round's real-time phase (s)
    census "$r" "P0_before"
    timeout -k 10 $((LEN + 600)) taskset -c 5 python3 board/b1_cpumon.py --duration $((LEN + 300)) --out "$OUT/cpumon_r$r.jsonl" &
    P1=$!
    timeout -k 10 $((LEN + 600)) taskset -c 1 python3 board/b1_e1loop.py --run runs/ds1 --duration $((LEN + 300)) --out "$OUT/e1loop_r$r.jsonl" &
    P2=$!
    timeout -k 10 $((LEN + 600)) taskset -c 2 board/b1_limloop $((LEN + 300)) "$OUT/limloop_r$r.jsonl" $R96 $R3564 &
    P3=$!
    LOADS="$P1 $P2 $P3"
    mark "$r" P0 start; sleep 600; mark "$r" P0 end
    census "$r" "P0_after"
    ring "$r" P1 3.2 512 1800 600:10 1200:60 1680:300
    ring "$r" P2 32 512 1800 600:10 1200:60 1680:300
    ring "$r" P3 3.2 2048 1800 600:10 1200:60 1680:300
    ring "$r" P4 32 2048 1800 600:10 1200:60 1680:300
    [ "$r" -le 2 ] && ring "$r" P5 60 2048 600 200:10 400:60 560:300   # D-2: 10-min cell, triggers at 1/3 scale
    mark "$r" loads stop
    for p in $LOADS; do kill -TERM "$p" 2>/dev/null; done
    for p in $LOADS; do wait "$p" 2>/dev/null; done
    LOADS=""
    if [ "$r" -le 2 ]; then
        census "$r" "P6_before"; mark "$r" P6 start
        sh board/b1_emmc.sh "$DUMP" "$OUT/rand1g.bin" "$OUT/emmc_r$r.jsonl" 300
        mark "$r" P6 end; census "$r" "P6_after"
    fi
done
rm -f "$OUT/rand1g.bin" "$DUMP"/b1_* 2>/dev/null
echo "B1 PROTOCOL DONE"
