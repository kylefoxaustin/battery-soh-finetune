"""FR1 rater B: rating order and document fetcher (pre-registration §4.1).

Run from the repo root:  nice python3 -I analysis/FR1_rater_B_fetch.py
Writes documents (untrusted data) under data/raw/nhtsa/fr1_docs_B/ (gitignored) and the manifest
results/FR1/rater_B_documents.json. Fetches, per campaign, every NHTSA document whose listing summary is a
Part 573 report or a chronology; and, for an investigation linked to the campaign, its opening / closing résumé.
Text is extracted afterwards with `pdftotext -layout`. Nothing downloaded is executed.
Source: NHTSA (US Government work, public domain).
"""
import hashlib
import json
import os
import re
import time
import urllib.request
from datetime import datetime, timezone

import numpy as np

ROOT = os.getcwd()
CASES_MD = os.path.join(ROOT, "results/FR1/FR1_cases.md")
OUT = os.path.join(ROOT, "data/raw/nhtsa/fr1_docs_B")
MANIFEST = os.path.join(ROOT, "results/FR1/rater_B_documents.json")
API = "https://api.nhtsa.gov/safetyIssues/byNhtsaId?filter=true&nhtsaId={}&issueType={}"
UA = {"User-Agent": "FR1-rater-B research fetch (public NHTSA documents)"}


def case_list():
    """PE001-PE005, PE007-PE076 then BR001-BR075, with NHTSA IDs and 'initiated by' from FR1_cases.md."""
    rows = {}
    for line in open(CASES_MD, encoding="utf-8"):
        m = re.match(r"\| (PE\d{3}|BR\d{3}) \| \[(\d\dV-\d{3})\]", line)
        if m:
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            init = cells[-1] if m.group(1).startswith("PE") else ""
            rows[m.group(1)] = (m.group(2), init)
    rows["PE076"] = ("25V-811", "MFR")  # D-1
    pe = ["PE%03d" % i for i in range(1, 77) if i != 6]
    br = ["BR%03d" % i for i in range(1, 76)]
    return [(c, rows[c][0], rows[c][1]) for c in pe + br]


def order():
    cases = case_list()
    perm = np.random.default_rng(2).permutation(len(cases))
    return [(k + 1,) + cases[i] for k, i in enumerate(perm)]


def get(url, tries=4):
    for t in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                data = r.read()
            time.sleep(0.5)
            return data
        except Exception as e:  # retry politely
            err = e
            time.sleep(2 * (t + 1))
    raise RuntimeError(f"{url}: {err}")


def wanted(summary, fname):
    s = (summary or "").lower()
    f = (fname or "").upper()
    # The Part 573 report and its chronology, including a manufacturer-format Defect Information Report (DIR)
    # attached as a miscellaneous document; bare "Miscellaneous Document" attachments are fetched and checked by
    # reading their heading, and used only if they are a DIR or a chronology (see rater_B_notes.md).
    return (("573" in s) or ("chronolog" in s) or f.startswith("RCLRPT") or ("defect information report" in s)
            or re.search(r"\bdir\b", s) is not None or ("regulatory recall report" in s)
            or s.strip() == "miscellaneous document")


def resume(summary, fname):
    s = (summary or "").lower()
    f = (fname or "").upper()
    if f.startswith("INCV"):  # list of ODI report numbers, not the résumé text
        return False
    return ("opening resume" in s or "closing resume" in s or f.startswith("INOA") or f.startswith("INCLA"))


def fetch_doc(case, kind, d, man):
    url = d["url"]
    fname = os.path.basename(url)
    path = os.path.join(OUT, case, fname)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    entry = {"case": case, "kind": kind, "summary": d.get("summary"), "load_date": d.get("loadDate"), "url": url,
             "file": os.path.relpath(path, ROOT)}
    try:
        if not os.path.exists(path):
            data = get(url)
            with open(path, "wb") as fh:
                fh.write(data)
        data = open(path, "rb").read()
        entry.update(bytes=len(data), sha256=hashlib.sha256(data).hexdigest(),
                     fetched_utc=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), ok=True)
    except Exception as e:
        entry.update(ok=False, error=str(e)[:200])
    man.append(entry)


def main():
    os.makedirs(OUT, exist_ok=True)
    man, listing = [], {}
    for k, case, nid, init in order():
        cid = nid.replace("-", "")
        try:
            js = json.loads(get(API.format(cid, "recall")))
            recs = [r for res in js.get("results", []) for r in res.get("recalls", [])]
        except Exception as e:
            man.append({"case": case, "kind": "listing", "url": API.format(cid, "recall"), "ok": False,
                        "error": str(e)[:200]})
            continue
        invs = sorted({i["nhtsaId"] for r in recs for i in (r.get("investigations") or [])})
        listing[case] = {"order": k, "nhtsa_id": nid, "initiated_by": init, "investigations": invs}
        for r in recs:
            for d in r.get("associatedDocuments") or []:
                if wanted(d.get("summary"), d.get("fileName")):
                    fetch_doc(case, "part573_or_chronology", d, man)
        for inv in invs:
            try:
                ij = json.loads(get(API.format(inv, "investigation")))
            except Exception as e:
                man.append({"case": case, "kind": "odi_listing", "url": API.format(inv, "investigation"),
                            "ok": False, "error": str(e)[:200]})
                continue
            for res in ij.get("results", []):
                for iv in res.get("investigations", []):
                    for d in iv.get("associatedDocuments") or []:
                        if resume(d.get("summary"), d.get("fileName")):
                            fetch_doc(case, "odi_resume:" + inv, d, man)
        print(k, case, nid, init, invs, flush=True)
    json.dump({"source": "NHTSA, public domain", "fetched_by": "rater B",
               "script": "analysis/FR1_rater_B_fetch.py", "cases": listing, "documents": man},
              open(MANIFEST, "w"), indent=1)


if __name__ == "__main__":
    main()
