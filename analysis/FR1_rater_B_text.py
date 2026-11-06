"""FR1 rater B: extract text from the fetched NHTSA documents of one or more cases, for reading.

Usage (repo root):  python3 -I analysis/FR1_rater_B_text.py CASE [CASE ...]
Runs `pdftotext -layout` on each fetched PDF (untrusted data; nothing is executed) and prints the text, with
blank-line runs collapsed. Part 573 reports are printed newest first; the older versions are shown only as a
short note so the newest report and the chronology are read in full. Source: NHTSA, public domain.
"""
import json
import os
import re
import subprocess
import sys

ROOT = os.getcwd()
MAN = json.load(open(os.path.join(ROOT, "results/FR1/rater_B_documents.json")))


# Attachments fetched under the broad "Miscellaneous Document" rule that, on reading their heading, are not a
# Part 573 / Defect Information Report or a chronology (owner letters, FAQs, cover letters, part lists), or are
# image-only with no text layer; they are not rating sources.
NOT_RATING = {
    "RMISC-22V523-4836", "RMISC-22V523-0794", "RMISC-22V523-2243", "RMISC-22V523-4485", "RMISC-22V523-2022",
    "RMISC-22V523-4996", "RMISC-22V523-6047", "RMISC-24V715-8515", "RMISC-21V106-2656", "RMISC-26V309-7786",
    "RMISC-19V014-8250", "RMISC-24V574-1972", "RMISC-23V252-9785", "RMISC-25V566-4417", "RMISC-24V700-2020",
    "RMISC-240094531779-8676", "RMISC-25V655-0880", "RMISC-25V655-5793", "RMISC-25V642-2800",
}


def group(d):
    s = (d.get("summary") or "").lower()
    return "chronology" if "chronolog" in s else "dir"


def text(path):
    txt = path[:-4] + ".txt"
    if not os.path.exists(txt):
        subprocess.run(["pdftotext", "-layout", path, txt], check=False, timeout=120,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if not os.path.exists(txt):
        return None
    t = open(txt, encoding="utf-8", errors="replace").read()
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n\s*\n+", "\n", t)
    return t


BOILER = re.compile(r"^ ?(The information contained in this report was submitted|Page \d+ of \d+|Part 573 Safety Recall Report|"
                    r"OMB Control No|Address ?:|Country ?:|Tier of Supplier|Supplier Type|Component (Part Number|Description) ?:)")


def core(t):
    """Part 573 body: from the defect description to the remedy description; boilerplate lines dropped."""
    lo = t.lower()
    a = lo.find("description of the defect")
    b = lo.find("description of remedy", a + 1)
    if a < 0:
        body = t
    else:
        body = t[a:b if b > a else len(t)]
    return "\n".join(x for x in body.splitlines() if not BOILER.match(x))


def main(cases):
    for case in cases:
        info = MAN["cases"].get(case, {})
        docs = [d for d in MAN["documents"] if d["case"] == case]
        print("=" * 30, case, info.get("nhtsa_id"), "init:", info.get("initiated_by"),
              "inv:", info.get("investigations"))
        rpt = sorted([d for d in docs if os.path.basename(d.get("file", "")).upper().startswith("RCLRPT")],
                     key=lambda d: d.get("load_date") or "", reverse=True)
        other = sorted([d for d in docs if d not in rpt], key=lambda d: (d["kind"], d.get("load_date") or ""),
                       reverse=True)
        seen = set()
        for i, d in enumerate(rpt + other):
            if not d.get("ok"):
                print("--- NOT OPENED:", d.get("url"), d.get("error"))
                continue
            if os.path.basename(d["file"]).rsplit(".", 1)[0] in NOT_RATING:
                print("--- not a rating document (letter / FAQ / image-only):", os.path.basename(d["file"]))
                continue
            t = text(os.path.join(ROOT, d["file"]))
            print("---", d["kind"], d.get("summary"), os.path.basename(d["file"]))
            if t is None or len(t.strip()) < 50:
                print("[no extractable text]")
            elif d in rpt and i > 0:
                print("[older Part 573 version; %d chars]" % len(t))
            elif d not in rpt and d["kind"] == "part573_or_chronology" and group(d) in seen:
                print("[older %s version; %d chars]" % (group(d), len(t)))
            else:
                print(core(t) if d in rpt else t)
                if d not in rpt and d["kind"] == "part573_or_chronology":
                    seen.add(group(d))


if __name__ == "__main__":
    main(sys.argv[1:])
