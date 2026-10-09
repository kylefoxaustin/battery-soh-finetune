#!/bin/sh
# Full Analysis-Brief pipeline on the Changan 300-EV set. Run from the repo root once RAW_DATA.z01 and
# RAW_DATA.zip are both present. Idempotent: each stage skips work already done.
#
#   sh analysis/run_full.sh            (K folds = 4; ~1-2 h on a 32-core host, CPU only)
set -eu
K=${K:-4}
export CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=8 MKL_NUM_THREADS=8
mkdir -p runs results/large

echo "== 1. extract all recoverable vehicles (both volumes)"
python3 data/changan_extract.py RAW_DATA.zip data/raw/changan > runs/full_extract.log 2>&1
grep -m1 "recoverable" runs/full_extract.log
echo "== 2. slim (scalar columns only)"
python3 data/changan_slim.py data/raw/changan data/changan/slim --jobs 12 > runs/full_slim.log 2>&1
echo "   $(ls data/changan/slim/*.npz | wc -l) vehicles slimmed"
echo "== 3. OCV table (all vehicles' early-life rests) + labels + consolidate"
python3 data/changan_labels.py ocv data/changan/slim data/changan/ocv_full.json
rm -rf data/changan/labels_full
python3 data/changan_labels.py label data/changan/slim data/changan/ocv_full.json data/changan/labels_full --jobs 16 > runs/full_labels.log 2>&1
for f in primary strict; do
  python3 data/changan_consolidate.py data/changan/labels_full data/processed/changan_full_$f.npz --filter $f
done
echo "== 4. K-fold fleet models + experiments A/B (one-shot early FT) and C (rolling)"
for f in primary strict; do
  k=0
  while [ $k -lt $K ]; do
    R=runs/chf_${f}_k$k
    ( [ -f $R/fleet.pt ] || (cd model && timeout -k 10 3600 python3 -u train_fleet.py --data ../data/processed/changan_full_$f.npz \
        --device cpu --min-target 20 --min-span-km 50000 --nfolds $K --fold $k --epochs 60 --patience 10 --out ../$R > ../$R.train.log 2>&1) ) \
      && timeout -k 10 3600 python3 board/e4_pervehicle.py --run $R --threads 4 --out results/large/e4_${f}_k$k.json > $R.e4.log 2>&1 \
      && timeout -k 10 3600 python3 analysis/rolling.py --run $R --threads 4 --out results/large/rolling_${f}_k$k.json > $R.rolling.log 2>&1 &
    k=$((k + 1))
  done
  wait
done
echo "== 5. aggregate"
python3 analysis/aggregate.py --out results/large
echo "DONE"
