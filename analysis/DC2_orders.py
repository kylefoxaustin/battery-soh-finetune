"""DC2 rating orders (pre-registration §7): rater A default_rng(31), rater B default_rng(32).

The instrument IDs of results/DC2/DC2_instruments.md (the instrument table, before the first "## 2.") are sorted and
permuted; groups (X included, DC2-1) are interleaved. Writes results/DC2/DC2_orders.json. Run from the repository
root with python3 -I (numpy needed; -E if -I hides it).
"""
import json
import re

import numpy as np

text = open("results/DC2/DC2_instruments.md").read().split("## 2.")[0]
ids = sorted(set(re.findall(r"^\| ([GUEQVX]\d{2}) \|", text, re.M)))
assert ids, "no instrument IDs found"
orders = {r: [ids[i] for i in np.random.default_rng(s).permutation(len(ids))] for r, s in (("A", 31), ("B", 32))}
json.dump({"rule": "sorted instrument IDs permuted by numpy.random.default_rng(seed)", "seeds": {"A": 31, "B": 32},
           "n": len(ids), "orders": orders}, open("results/DC2/DC2_orders.json", "w"), indent=1)
print(len(ids), {r: o[:6] for r, o in orders.items()})
