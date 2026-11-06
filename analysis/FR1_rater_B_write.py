"""FR1 rater B: assemble results/FR1/ratings_B.csv and annotate results/FR1/rater_B_documents.json.

Usage (repo root):  python3 -I analysis/FR1_rater_B_write.py <ratings-worksheet>
The worksheet is rater B's own pipe-separated record, one line per case:
case|item1|item2|item3|signals_and_rate|confidence|no_cause|software_only|out_of_scope|note
written by hand while reading each case's documents (pre-registration §3, §4.1); it is kept with the gitignored
document cache. Every value is checked against the closed lists. All ratings are DERIVED-judgemental.
Source of the rated records: NHTSA (US Government work, public domain).
"""
import csv
import json
import os
import sys

ROOT = os.getcwd()
MAN_PATH = os.path.join(ROOT, "results/FR1/rater_B_documents.json")
OUT = os.path.join(ROOT, "results/FR1/ratings_B.csv")
sys.path.insert(0, os.path.join(ROOT, "analysis"))
from FR1_rater_B_text import NOT_RATING  # noqa: E402

ITEM1 = {"transient electrical (over-current / over-voltage / short)", "thermal cycling or thermal overload",
         "manufacturing or component defect", "software or calibration", "unknown / mixed"}
ITEM2 = {"DTC freeze-frame", "bench reproduction", "fleet statistics", "waveform or high-rate capture",
         "teardown only", "not stated"}
ITEM3 = {"<= 1 s", "(1, 40] s", "(40, 80] s", "(80, 700] s", "> 700 s", "cannot judge"}
CONF = {"low", "medium", "high"}

# Fetched documents that have no usable text layer and were not read as images (not rating sources), and the
# image-only DIRs that were read as rendered page images.
NO_TEXT_NOT_READ = {"RMISC-23V067-4545", "RMISC-23V067-3022", "RMISC-23V067-7581", "RMISC-18V698-7241",
                    "RMISC-24V700-4145", "INOA-PE23011-2700"}
READ_AS_IMAGES = {"RMISC-24V560-1690", "RMISC-23V657-1502"}
# ODI resumes fetched through the API link but not usable under section 4.1 for this case (campaign not
# ODI-initiated and its Part 573 does not cite the investigation).
RESUME_NOT_ALLOWED = {("BR012", "INOA-EA15001-4970")}


def stem(d):
    return os.path.basename(d.get("file", d.get("url", ""))).rsplit(".", 1)[0]


def main(work):
    man = json.load(open(MAN_PATH))
    for d in man["documents"]:
        s = stem(d)
        if not d.get("ok"):
            d["used_for_rating"] = False
            d["use_note"] = "could not be fetched"
        elif s in NOT_RATING:
            d["used_for_rating"] = False
            d["use_note"] = "not a Part 573 / DIR / chronology / resume (letter, FAQ, cover, image-only notice)"
        elif (d["case"], s) in RESUME_NOT_ALLOWED:
            d["used_for_rating"] = False
            d["use_note"] = "resume not allowed by pre-registration 4.1 for this case"
        elif s in NO_TEXT_NOT_READ:
            d["used_for_rating"] = False
            d["use_note"] = "no usable text layer; the case was rated from its other documents"
        elif s in READ_AS_IMAGES:
            d["used_for_rating"] = True
            d["use_note"] = "image-only DIR, read as rendered page images"
        else:
            d["used_for_rating"] = True
    man["ratings_file"] = "results/FR1/ratings_B.csv"
    json.dump(man, open(MAN_PATH, "w"), indent=1)

    rows = {}
    for line in open(work, encoding="utf-8"):
        if not line.strip():
            continue
        f = line.rstrip("\n").split("|")
        assert len(f) == 10, line
        case, i1, i2, i3, sig, conf, nc, sw, oos, note = f
        assert i1 in ITEM1 and i2 in ITEM2 and i3 in ITEM3 and conf in CONF, (case, i1, i2, i3, conf)
        assert nc in {"yes", "no"}, case
        if case.startswith("PE"):
            assert sw in {"yes", "no"} and oos in {"yes", "no"}, case
        else:
            assert sw == "NA" and oos == "NA", case
        rows[case] = f
    cases = man["cases"]
    assert set(rows) == set(cases), set(rows) ^ set(cases)

    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["order", "case", "list", "nhtsa_id", "rating_documents", "odi_resume", "item1_cause_type",
                    "item2_evidence", "item3_window", "item3_signals_and_rate", "item4_confidence",
                    "item5_no_cause_stated", "item5_software_only", "item5_component_out_of_scope",
                    "rater_note", "rater", "provenance", "source"])
        for case, info in sorted(cases.items(), key=lambda kv: kv[1]["order"]):
            docs = [d for d in man["documents"] if d["case"] == case and d.get("used_for_rating")]
            main_docs = [os.path.basename(d["file"]) for d in docs if d["kind"] == "part573_or_chronology"]
            res = sorted({d["kind"].split(":", 1)[1] for d in docs if d["kind"].startswith("odi_resume")})
            _, i1, i2, i3, sig, conf, nc, sw, oos, note = rows[case]
            w.writerow([info["order"], case, "PE" if case.startswith("PE") else "BR", info["nhtsa_id"],
                        "; ".join(main_docs), "; ".join(res) if res else "none", i1, i2, i3, sig, conf, nc, sw,
                        oos, note, "B", "DERIVED-judgemental", "NHTSA, public domain"])
    print("wrote", OUT, len(rows))


if __name__ == "__main__":
    main(sys.argv[1])
