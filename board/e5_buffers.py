"""E5 (H5): history-buffer sizing. Pure arithmetic — every number here is DERIVED from the stated
ASSUMED/CHOSEN inputs below; none is measured.

  raw buffer bytes = channels x bytes_per_sample x sample_rate_hz x window_s
Two regimes:
  full retrain : must keep RAW multichannel history (the backbone re-learns from it)
  last-layer FT: backbone + head[0] are frozen, so each training example can be cached as its
                 64-dim penultimate feature (fp32) + 1 label — the raw window is consumed once and
                 discarded. The FT set size actually used in E4 is read from e4.json if present.

Usage: python3 board/e5_buffers.py [--e4 results/raw/e4.json] --out results/raw/e5.json
"""
import argparse
import json
import os

CHANNELS = 7               # IMPOSED by the dataset: avgV, I, SOC, Vmax, Vmin, Tmax, Tmin
BYTES_PER_SAMPLE = 2       # ASSUMED: int16 ADC codes (fp32 would double every raw figure)
RATES_HZ = [1, 10, 100]    # brief §E5
WINDOWS_S = {"10 min": 600, "1 h": 3600, "8 h (drive day)": 8 * 3600, "7 days": 7 * 86400}
SNIPPET_LEN = 128          # IMPOSED by the dataset (one charge snippet, 10 s cadence = 21.3 min)
FEAT_DIM, FEAT_BYTES = 64, 4  # CHOSEN by the model (HEAD_HIDDEN, fp32)


def human(b):
    for u in ("B", "KB", "MB", "GB"):
        if b < 1024:
            return f"{b:.0f} {u}" if u == "B" else f"{b:.1f} {u}"
        b /= 1024
    return f"{b:.1f} TB"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--e4", default=None)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    raw = {w: {r: CHANNELS * BYTES_PER_SAMPLE * r * s for r in RATES_HZ} for w, s in WINDOWS_S.items()}
    per_snip_raw = CHANNELS * BYTES_PER_SAMPLE * SNIPPET_LEN
    per_snip_feat = FEAT_DIM * FEAT_BYTES + 4
    ft = {"per_example_raw_B": per_snip_raw, "per_example_cached_feature_B": per_snip_feat}
    if a.e4 and os.path.exists(a.e4):
        n_ft = [r["n_ft"] for r in json.load(open(a.e4))["per_car"]]
        n_ft.sort()
        med = n_ft[len(n_ft) // 2]
        ft.update({"e4_n_ft_median": med, "e4_n_ft_max": n_ft[-1],
                   "raw_bytes_median_car": med * per_snip_raw, "feat_bytes_median_car": med * per_snip_feat,
                   "raw_bytes_max_car": n_ft[-1] * per_snip_raw, "feat_bytes_max_car": n_ft[-1] * per_snip_feat})
    res = {"tag": "DERIVED", "assumptions": {"channels": CHANNELS, "bytes_per_sample": BYTES_PER_SAMPLE,
                                             "snippet_len": SNIPPET_LEN, "feat_dim": FEAT_DIM,
                                             "feat_bytes": FEAT_BYTES},
           "raw_history_bytes": raw, "last_layer_ft": ft}
    json.dump(res, open(a.out, "w"), indent=1)
    print("| window | " + " | ".join(f"{r} Hz" for r in RATES_HZ) + " |")
    print("|---|" + "---|" * len(RATES_HZ))
    for w in WINDOWS_S:
        print(f"| {w} | " + " | ".join(human(raw[w][r]) for r in RATES_HZ) + " |")
    print(json.dumps(ft, indent=1))


if __name__ == "__main__":
    main()
