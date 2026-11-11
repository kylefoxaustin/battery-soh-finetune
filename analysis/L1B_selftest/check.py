"""Runs analysis/L1B_agreement.py on each synthetic scenario written by make.py and asserts the expected readouts.
Run from the repository root:  python3 -I analysis/L1B_selftest/make.py && python3 -I analysis/L1B_selftest/check.py
"""
import json
import os
import subprocess
import sys

here = os.path.relpath(os.path.dirname(os.path.abspath(__file__)))
EXPECT = {
    "t1": {"count": "SPECIFIC BY COUNT", "kind": "STACK-SPECIFIC", "cal": "CALIBRATED", "N_L": 10, "N_S": 14,
           "k": (4, 1, 0), "ident": 8 / 9},
    "t2": {"count": "NOT SPECIFIC BY COUNT", "kind": "NOT STACK-SPECIFIC", "cal": "MISCALIBRATED", "N_L": 28},
    "t3": {"count": "UNCLEAR BY COUNT", "kind": "UNCLEAR IN KIND", "cal": "CALIBRATED", "N_L": 13, "k": (2, 1, 0),
           "kind_note": "L1B-D1"},
    "t4": {"count": "UNCLEAR BY COUNT", "kind": "NOT STACK-SPECIFIC", "cal": "CALIBRATED", "N_L": 18, "k": (1, 1, 0),
           "cal_diff": 3, "cal_cov": 5},
    "t5": {"count": "UNCLEAR BY COUNT (ACCESS-LIMITED: L)", "kind": "STACK-SPECIFIC", "cal": "CALIBRATED",
           "ACC_count": "SPECIFIC BY COUNT", "limited_L": True},
    "t6": {"count": "UNGATED", "kind": "UNGATED", "gate_fail": "kappa_stack"},
}

log = []
for t, e in EXPECT.items():
    d = os.path.join(here, t)
    run = subprocess.run([sys.executable, "-I", "analysis/L1B_agreement.py", "--dir", d, "--l1dir",
                          os.path.join(here, "ref_L1")], capture_output=True, text=True)
    assert run.returncode == 0, run.stderr
    log.append(f"== {t}\n{run.stdout}")
    o = json.load(open(os.path.join(d, "l1b.json")))
    p = o["primary_V2"]
    assert not any(o["validation_problems"].values()), o["validation_problems"]
    assert p["verdict_count"] == e["count"], (t, p["verdict_count"])
    assert p["verdict_kind"] == e["kind"], (t, p["verdict_kind"])
    if "cal" in e:
        assert p["calibration"]["status"] == e["cal"], (t, p["calibration"])
    if "N_L" in e:
        assert p["N_L"] == e["N_L"], (t, p["N_L"])
    if "N_S" in e:
        assert p["N_S"] == e["N_S"], (t, p["N_S"])
    if "k" in e:
        assert (p["stack_B"]["k"], p["stack_L"]["k"], p["stack_S"]["k"]) == e["k"], t
    if "ident" in e:
        assert abs(p["identification"] - e["ident"]) < 1e-9, (t, p["identification"])
    if "kind_note" in e:
        assert any(e["kind_note"] in n for n in p["decision_notes_kind"]), (t, p["decision_notes_kind"])
    if "cal_diff" in e:
        assert p["calibration"]["abs_diff"] == e["cal_diff"] and p["calibration"]["E_S1_covered"] == e["cal_cov"], t
    if "ACC_count" in e:
        assert o["ACC"]["verdict_count"] == e["ACC_count"], (t, o["ACC"]["verdict_count"])
    if "limited_L" in e:
        assert o["access"]["limited_L"] == e["limited_L"], t
    if "gate_fail" in e:
        assert not p["gates"]["pass"][e["gate_fail"]], (t, p["gates"])
    assert p["stack_vehicle_level"]["S"]["n_events"] == 8 and p["N_B"] == 35, t
print("".join(log))
open(os.path.join(here, "expected.out"), "w").write("".join(log))
print("all scenarios pass")
