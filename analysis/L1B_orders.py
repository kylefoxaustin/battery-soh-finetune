"""L1b rating orders (pre-registration §7): rater A default_rng(51), rater B default_rng(52).

The S and L instrument IDs of results/L1B/L1B_instruments.md §1 are sorted and permuted; domains are interleaved.
Writes results/L1B/L1B_orders.json. Run from the repository root with python3 -I (numpy needed; -E if -I hides it).
"""
import json
import re

import numpy as np

text = open("results/L1B/L1B_instruments.md").read().split("## 2.")[0]
ids = sorted(set(re.findall(r"^\| ([LS]\d{2}) \|", text, re.M)))
assert len(ids) == 73 and sum(i.startswith("S") for i in ids) == 26
orders = {r: [ids[i] for i in np.random.default_rng(s).permutation(len(ids))] for r, s in (("A", 51), ("B", 52))}
json.dump({"rule": "sorted S and L instrument IDs permuted by numpy.random.default_rng(seed); the 35 B events "
                   "(stack only) follow in B_events.csv order", "seeds": {"A": 51, "B": 52}, "n": len(ids),
           "orders": orders}, open("results/L1B/L1B_orders.json", "w"), indent=1)
print({r: o[:6] for r, o in orders.items()})
