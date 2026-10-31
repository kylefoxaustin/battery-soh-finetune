#!/bin/sh
# B1 P6 (briefs/B1/README.md §4.4): the eMMC as a sequential writer. 1 GB files of incompressible data (a 1 GB
# /dev/urandom file staged in RAM), written back to back with O_DIRECT for >= 300 s; per-file MB/s from wall time
# around each dd (data + fsync). Each file is deleted right after it is timed, because 300 s at the eMMC's rate exceeds
# the partition; the delete is outside the timed span.
#   sh board/b1_emmc.sh DUMP_DIR SRC_1G OUT.jsonl [min_seconds=300]
set -u
DIR=$1; SRC=$2; OUT=$3; MIN=${4:-300}
: > "$OUT"
FLAG="oflag=direct"
dd if="$SRC" of="$DIR/b1_emmc_probe.bin" bs=4M count=1 $FLAG 2>/dev/null || FLAG="conv=fsync"
rm -f "$DIR/b1_emmc_probe.bin"
echo "{\"event\": \"start\", \"mode\": \"$FLAG\", \"free_kb_before\": $(df -k --output=avail "$DIR" | tail -1)}" >> "$OUT"
t0=$(date +%s.%N); i=0
while :; do
    now=$(date +%s.%N)
    awk -v a="$now" -v b="$t0" -v m="$MIN" 'BEGIN{exit !(a-b<m)}' || break
    s=$(date +%s.%N)
    timeout -k 10 600 dd if="$SRC" of="$DIR/b1_emmc_$i.bin" bs=4M count=256 $FLAG conv=fsync 2>/dev/null
    rc=$?
    e=$(date +%s.%N)
    sz=$(stat -c %s "$DIR/b1_emmc_$i.bin" 2>/dev/null || echo 0)
    rm -f "$DIR/b1_emmc_$i.bin"
    echo "{\"file\": $i, \"rc\": $rc, \"bytes\": $sz, \"t_start\": $s, \"t_end\": $e}" >> "$OUT"
    i=$((i + 1))
done
sync
echo "{\"event\": \"end\", \"files\": $i, \"free_kb_after\": $(df -k --output=avail "$DIR" | tail -1)}" >> "$OUT"
