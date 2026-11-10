"""X8 exploratory diagnostic (NOT pre-registered; written after the X8 results, decides nothing).
For the base variant of each arm: vehicles with >= 20 scored history frames in the replay, and, among the frames each
limiter leaves unsafe at its calibrated kappa, how small the reference headroom is (the APPROVED-box expectation 1:
zero- and near-zero-reference frames). Usage: python -E analysis/X8_diag.py  (writes results/X/X8/x8_diag.json)
"""
import json
import os
import sys
from multiprocessing import Pool

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import X8_bottom as X                                    # noqa: E402

ONE_C = {"changan": 120.0, "DTI": 140.6, "QAS": 84.4}


def main():
    res = json.load(open(f"{X.OUT}/x8.json"))
    out = {"tag": "EXPLORATORY, not pre-registered, decides nothing; DERIVED replay"}
    with Pool(12) as pool:
        for arm in ("changan", "DTI", "QAS"):
            R = X.run(pool, arm, {})
            F, S = X.gather(R)
            halves = X.SPLIT["changan"] if arm == "changan" else X.SPLIT["beihang"][arm]
            vc = np.bincount(F["veh"])
            c = ONE_C[arm]
            d = {"vehicles_with_sessions": int((vc > 0).sum()), "vehicles_ge20_scored_frames": int((vc >= 20).sum()),
                 "frac_frames_ref_lt_0.1C": float((F["refh"] < 0.1 * c).mean()),
                 "frac_frames_ref_lt_0.5C": float((F["refh"] < 0.5 * c).mean()),
                 "ref_p50_A": float(np.median(F["refh"])), "ref_p50_C": float(np.median(F["refh"]) / c)}
            for (ca, ev) in (("A", "B"), ("B", "A")):
                dd = res[arm]["base"]["directions"][f"{ca}->{ev}"]
                em = np.isin(F["veh"], halves[ev])
                for l in X.LIMS:
                    k = dd[f"kappa_{l}"]
                    uns = em & (F[l] / k > X.UNSAFE_TOL * F["refh"])
                    r = F["refh"][uns]
                    d[f"{ca}->{ev}_{l}"] = {
                        "kappa": k, "unsafe_frames": int(uns.sum()),
                        "unsafe_ref_p50_A": float(np.median(r)) if len(r) else None,
                        "unsafe_with_ref0": int((r <= 0).sum()),
                        "unsafe_with_ref_lt_0.1C": int((r < 0.1 * c).sum()),
                        "unsafe_soc_p50": float(np.median(F["soc"][uns])) if len(r) else None}
            out[arm] = d
            print(arm, json.dumps(d, indent=1), flush=True)
    json.dump(out, open(f"{X.OUT}/x8_diag.json", "w"), indent=1)


if __name__ == "__main__":
    main()
