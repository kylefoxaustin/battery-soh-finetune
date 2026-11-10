"""FR1-R document set (brief §1): the URL and SHA-256 of every document either FR1 rater rated from.

Reads results/FR1/rater_{A,B}_documents.json for their url and sha256 fields only (no summary, file or rating field is
read or copied) and writes results/FR1R/FR1R_documents.json. Run with python3 -I from the repository root.
"""
import json

A = json.load(open("results/FR1/rater_A_documents.json"))["cases"]
B = json.load(open("results/FR1/rater_B_documents.json"))


def entries(x):
    for e in x if isinstance(x, list) else []:
        if isinstance(e, dict) and e.get("url"):
            yield e["url"], e.get("sha256")


cases = {}
for cid, c in A.items():
    for u, h in list(entries(c.get("docs"))) + list(entries(c.get("resume"))):
        cases.setdefault(cid, {}).setdefault(u, {"sha256_A": None, "sha256_B": None})["sha256_A"] = h
for e in B["documents"]:
    if e.get("used_for_rating") and e.get("url"):
        cases.setdefault(e["case"], {}).setdefault(e["url"], {"sha256_A": None, "sha256_B": None})["sha256_B"] = e.get("sha256")

out, n = {}, {"urls": 0, "both": 0, "A_only": 0, "B_only": 0, "both_same_hash": 0, "cases_without_url": 0}
for cid in sorted(set(A) | set(B["cases"])):
    docs = [{"url": u, **v} for u, v in sorted(cases.get(cid, {}).items())]
    out[cid] = docs
    n["cases_without_url"] += not docs
    for d in docs:
        n["urls"] += 1
        a, b = d["sha256_A"] is not None, d["sha256_B"] is not None
        n["both" if a and b else "A_only" if a else "B_only"] += 1
        n["both_same_hash"] += a and b and d["sha256_A"] == d["sha256_B"]
json.dump({"source": "results/FR1/rater_{A,B}_documents.json (url, sha256 only)", "counts": n, "cases": out},
          open("results/FR1R/FR1R_documents.json", "w"), indent=1)
print(len(out), n)
