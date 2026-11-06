"""FR1 stage 2: fetch each case's rating documents (pre-registration §4.1) and fix the rating order (§4.2).

For every PE and BR case in results/FR1/FR1_cases.md (after reviewer deviation D-1):
  - the NHTSA recall record (api.nhtsa.gov), used only to locate documents;
  - the latest Part 573 Safety Recall Report (original or latest amendment, by load date);
  - the chronology attachment, where NHTSA publishes one (a document labelled "Chronology", or a miscellaneous
    document whose first page says it is a chronology);
  - the ODI investigation résumé, only when the campaign is "Initiated by: ODI" or the Part 573 / chronology cites
    that investigation.
Text is extracted with pdftotext. Downloads are untrusted data; run this with `python3 -I`.

Rating order: cases sorted PE001..PE076 then BR001..BR075, permuted by numpy.random.default_rng(<seed>).

Usage: python3 -I analysis/FR1_docs.py results/FR1/FR1_cases.md data/raw/nhtsa/fr1_docs <seed>
Source: NHTSA, public domain.
"""
import hashlib
import html
import json
import os
import re
import subprocess
import sys
import time
import urllib.request

import numpy as np

API = "https://api.nhtsa.gov/safetyIssues/byNhtsaId?filter=nhtsaId&nhtsaId={}&name=recalls"
UA = {"User-Agent": "FR1-documentary-study/1.0"}


def cases(md_path):
    """PE and BR rows of FR1_cases.md, with D-1 applied (PE006 out, PE076 in)."""
    rows = {}
    for line in open(md_path, encoding="utf-8"):
        m = re.match(r"\| (PE\d{3}|BR\d{3}) \| \[(\d\dV-\d{3})\]", line)
        if m:
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            rows[m.group(1)] = {"case": m.group(1), "nhtsa": m.group(2), "init": cells[-1]}
    m = re.search(r"\*\*PE076\*\* = \[(\d\dV-\d{3})\].*?initiated by (\w+)", open(md_path, encoding="utf-8").read())
    rows["PE076"] = {"case": "PE076", "nhtsa": m.group(1), "init": m.group(2)}
    rows.pop("PE006", None)
    ids = sorted(k for k in rows if k.startswith("PE")) + sorted(k for k in rows if k.startswith("BR"))
    return [rows[k] for k in ids]


def get(url, dest=None):
    for attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                data = r.read()
            if dest:
                with open(dest, "wb") as f:
                    f.write(data)
            return data
        except Exception as e:  # network only; retried, then raised
            err = e
            time.sleep(3 * (attempt + 1))
    raise err


def pdf_text(path):
    out = subprocess.run(["pdftotext", "-layout", path, "-"], capture_output=True, timeout=120)
    return out.stdout.decode("utf-8", errors="replace")


def amendment_no(summary):
    m = re.search(r"Amendment\s*(\d+)", summary or "")
    return int(m.group(1)) if m else 0


def main(md_path, out_dir, seed):
    os.makedirs(out_dir, exist_ok=True)
    cs = cases(md_path)
    order = np.random.default_rng(seed).permutation(len(cs))
    manifest = {"source": "NHTSA, public domain", "seed": seed,
                "order": [cs[i]["case"] for i in order], "cases": {}}
    for c in cs:
        nid = c["nhtsa"].replace("-", "")
        cdir = os.path.join(out_dir, c["case"])
        os.makedirs(cdir, exist_ok=True)
        jpath = os.path.join(cdir, "record.json")
        if not os.path.exists(jpath):
            get(API.format(nid), jpath)
            time.sleep(0.5)
        rec = json.load(open(jpath, encoding="utf-8"))["results"][0]["recalls"][0]
        docs = rec.get("associatedDocuments") or []
        p573 = [d for d in docs if d["fileName"].upper().startswith("RCLRPT")]
        p573.sort(key=lambda d: (d.get("loadDate", ""), amendment_no(d.get("summary"))))
        chron = [d for d in docs if "chronolog" in (d.get("summary") or "").lower()]
        # A chronology filed as a miscellaneous document counts when its own first page says it is one.
        for d in docs:
            if d["fileName"].upper().startswith("RMISC") and d not in chron:
                path = os.path.join(cdir, d["fileName"])
                if not os.path.exists(path):
                    try:
                        get(d["url"], path)
                    except Exception:
                        continue
                    time.sleep(0.5)
                if "chronolog" in pdf_text(path)[:3000].lower():
                    chron.append(d)
        picked = (p573[-1:] if p573 else []) + chron
        entry = {"nhtsa": c["nhtsa"], "init": c["init"], "docs": [], "resume": [], "missing": []}
        if not p573:
            entry["missing"].append("Part 573")
        text = []
        for d in picked:
            path = os.path.join(cdir, d["fileName"])
            if not os.path.exists(path):
                try:
                    get(d["url"], path)
                except Exception as e:
                    entry["missing"].append(f"{d['fileName']}: {e}")
                    continue
                time.sleep(0.5)
            sha = hashlib.sha256(open(path, "rb").read()).hexdigest()
            entry["docs"].append({"file": d["fileName"], "summary": d.get("summary"), "url": d["url"], "sha256": sha})
            text.append(f"===== {d.get('summary')} ({d['fileName']}) =====\n{pdf_text(path)}")
        cited = re.sub(r"[\s\-]", "", "\n".join(text)).upper()
        for inv in rec.get("investigations") or []:
            iid = inv.get("nhtsaId", "")
            if c["init"].upper() == "ODI" or (iid and iid.upper() in cited):
                desc = html.unescape(re.sub(r"<[^>]+>", " ", inv.get("description") or ""))
                entry["resume"].append(iid)
                text.append(f"===== ODI résumé {iid} ({inv.get('subject')}) =====\n{desc}")
        with open(os.path.join(cdir, "rating_docs.txt"), "w", encoding="utf-8") as f:
            f.write("\n\n".join(text))
        manifest["cases"][c["case"]] = entry
        print(c["case"], c["nhtsa"], len(entry["docs"]), entry["resume"], entry["missing"] or "", flush=True)
    with open(os.path.join(out_dir, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=1)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]))
