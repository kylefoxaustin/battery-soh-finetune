"""FR1-R rating orders (brief START HERE step 3): rater A default_rng(11), rater B default_rng(12).

The 150 case IDs (75 PE after FR1 D-1, 75 BR) are sorted ascending and permuted; PE and BR are interleaved.
Writes results/FR1R/FR1R_orders.json. Run with python3 -I from the repository root (numpy needed: use -E if -I hides it).
"""
import json
import re

import numpy as np

text = open("results/FR1/FR1_cases.md").read()
assert "**PE076** = [25V-811]" in text  # added by D-1, in the D-1 table rather than the PE table
ids = sorted((set(re.findall(r"^\| ((?:PE|BR)\d{3}) \|", text, re.M)) - {"PE006"}) | {"PE076"})
assert len(ids) == 150 and sum(i.startswith("PE") for i in ids) == 75
orders = {r: [ids[i] for i in np.random.default_rng(s).permutation(len(ids))] for r, s in (("A", 11), ("B", 12))}
json.dump({"rule": "sorted case IDs permuted by numpy.random.default_rng(seed)", "seeds": {"A": 11, "B": 12},
           "orders": orders}, open("results/FR1R/FR1R_orders.json", "w"), indent=1)
print({r: o[:5] for r, o in orders.items()})
