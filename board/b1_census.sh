#!/bin/sh
# B1 Stage 1 census (briefs/B1/README.md §3). Run ON THE BOARD from the staged tree (/tmp/b1). Read-only except: the
# governor is pinned to `performance` for the baselines and the ORIGINAL governor restored on exit; two anonymous test
# mappings (512 MB, 2 GB) are created and released. No ring, producer or dump code exists at this stage.
#   cd /tmp/b1 && sh board/b1_census.sh out
set -u
OUT=${1:-out}
mkdir -p "$OUT"
ORIG_GOV=$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor)
restore() {
    for g in /sys/devices/system/cpu/cpu[0-9]*/cpufreq/scaling_governor; do echo "$ORIG_GOV" > "$g"; done
    echo "governor restored -> $(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor)"
}
trap restore EXIT INT TERM

sec() { echo; echo "### $1"; echo "\$ $2"; sh -c "$2" 2>&1; }
{
sec "1. kernel" "uname -a"
sec "1. online cores" "cat /sys/devices/system/cpu/online; nproc"
sec "1. max freq and governor per core (before pinning)" \
    'for c in /sys/devices/system/cpu/cpu[0-9]*; do echo "$(basename $c) max_khz=$(cat $c/cpufreq/cpuinfo_max_freq) gov=$(cat $c/cpufreq/scaling_governor)"; done'
sec "2. memory" "grep -E 'MemTotal|MemFree|MemAvailable|HugePages_Total|HugePages_Free|Hugepagesize|CmaTotal|CmaFree' /proc/meminfo"
sec "2. THP" "cat /sys/kernel/mm/transparent_hugepage/enabled /sys/kernel/mm/transparent_hugepage/defrag"
sec "2. anonymous mapping test (MAP_POPULATE, then MAP_HUGETLB), 512 MB and 2 GB; released" \
    "timeout -k 10 120 python3 - <<'EOF'
import mmap, time
for mb in (512, 2048):
    for lab, fl in (('POPULATE', mmap.MAP_PRIVATE | mmap.MAP_ANONYMOUS | getattr(mmap, 'MAP_POPULATE', 0x8000)),
                    ('HUGETLB+POPULATE', mmap.MAP_PRIVATE | mmap.MAP_ANONYMOUS | 0x40000 | getattr(mmap, 'MAP_POPULATE', 0x8000))):
        t = time.perf_counter()
        try:
            m = mmap.mmap(-1, mb << 20, flags=fl)
            m[0:1] = b'x'; m[-1:] = b'x'
            print(f'{mb} MB {lab}: OK in {time.perf_counter() - t:.2f} s'); m.close()
        except OSError as e:
            print(f'{mb} MB {lab}: FAILED ({e})')
EOF"
sec "3. block devices" "lsblk -o NAME,SIZE,TYPE,MOUNTPOINT,ROTA"
sec "3. mmc identity" 'for d in /sys/block/mmcblk[0-9]; do echo "$d type=$(cat $d/device/type) name=$(cat $d/device/name) sectors=$(cat $d/size) cid=$(cat $d/device/cid)"; done'
sec "3. filesystems, mount options, free space" "df -h / /run/media/root-mmcblk0p2 /tmp; mount | grep -E 'mmcblk|/tmp'"
sec "3. eMMC partition table and unallocated space" "parted -s /dev/mmcblk0 unit GB print free"
sec "census before baselines (CPU delta over 10 s, binaries by /proc/PID/exe)" "python3 board/census.py --interval 10 --json $OUT/census_before.json"
} > "$OUT/census_system.txt"

for g in /sys/devices/system/cpu/cpu[0-9]*/cpufreq/scaling_governor; do echo performance > "$g"; done
echo "governor pinned: $ORIG_GOV -> $(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor)" >> "$OUT/census_system.txt"

# 4. baselines, nothing else running: e1 on core 1, H-b limiter on core 2 (cores per brief §2)
timeout -k 10 600 taskset -c 1 python3 board/e1_inference.py --run runs/ds1 --threads 1 --out "$OUT/e1_baseline.json" \
    > "$OUT/e1_baseline.log" 2>&1
timeout -k 10 600 taskset -c 2 board/h_limiter h/luts.bin h/frames_96.bin "$OUT/gate_out_96.bin" > "$OUT/hb_96.json" 2> "$OUT/hb_96.err"
timeout -k 10 600 taskset -c 2 board/h_limiter_lfp h2/luts.bin h2/frames_3564.bin "$OUT/gate_out_3564.bin" \
    > "$OUT/hb_3564.json" 2> "$OUT/hb_3564.err"
python3 board/census.py --interval 10 --json "$OUT/census_after.json" > "$OUT/census_after.txt" 2>&1
echo "B1 census done"
