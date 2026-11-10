"""L1 rating orders (pre-registration §4): rater A default_rng(21), rater B default_rng(22).

The instrument IDs of results/L1/L1_instruments.md §1 are sorted and permuted; domains are interleaved.
Writes results/L1/L1_orders.json. Run from the repository root with python3 -I (numpy needed; -E if -I hides it).
"""
import json
import re

import numpy as np

text = open("results/L1/L1_instruments.md").read().split("## 2.")[0]
ids = sorted(set(re.findall(r"^\| ([BS]\d{2}) \|", text, re.M)))
assert len(ids) == 63 and sum(i.startswith("B") for i in ids) == 37
orders = {r: [ids[i] for i in np.random.default_rng(s).permutation(len(ids))] for r, s in (("A", 21), ("B", 22))}
json.dump({"rule": "sorted instrument IDs permuted by numpy.random.default_rng(seed)", "seeds": {"A": 21, "B": 22},
           "orders": orders}, open("results/L1/L1_orders.json", "w"), indent=1)
print({r: o[:6] for r, o in orders.items()})
