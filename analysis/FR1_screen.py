"""FR1 stage 1: blind case screen of NHTSA recall campaigns (brief briefs/FR1/README.md §3.1-§3.2).

Inclusion is decided from component fields only: COMPNAME (field 7), MFR_COMP_NAME (25) and MFR_COMP_DESC (26), plus
make / model / year for the plug-in rule. The defect summary (20), corrective action (22) and notes (23) are never
printed, written or matched against. The only use of field 20 is a count of campaigns where it is non-empty (the
"a cause is stated" proxy, results/FR1/FR1_preregistration.md §2).

Usage: python3 -I analysis/FR1_screen.py data/raw/nhtsa/x/FLAT_RCL_POST_2010.txt results/FR1
"""
import collections
import json
import os
import re
import sys

DATE_LO, DATE_HI = '20180101', '20261031'

# Component groups (brief §3.1). Matched case-insensitively on COMPNAME + MFR_COMP_NAME + MFR_COMP_DESC.
GROUPS = {
    'OBC / charging control': [
        r'ON[- ]?BOARD CHARG', r'\bOBCM?\b', r'\bICCU\b', r'INTEGRATED CHARGING', r'CHARGING CONTROL',
        r'CHARGE CONTROL', r'CHARGING:MODULE', r'CHARGING MODULE', r'(?<![A-Z])CHARGER\b'],
    'DC-DC converter': [
        r'DC ?[/-] ?DC', r'\bDCDC\b', r'DC TO DC', r'\bLDC\b', r'(?<!TORQUE )(?<!CATALYTIC )CONVERTER'],
    'Traction inverter / motor controller': [
        r'INVERTER', r'POWER CONTROL UNIT', r'\bH?PCU\b', r'MOTOR CONTROLLER', r'MOTOR CONTROL UNIT',
        r'TRACTION MOTOR:CONTROLLER', r'POWER ELECTRONIC'],
    'HV BMS / contactor unit': [
        r'\bBMS\b', r'\bBECM\b', r'BATTERY MANAGEMENT', r'BATTERY ENERGY CONTROL', r'ENERGY CONTROL MODULE',
        r'CONTACTOR', r'FUSES, RELAYS, CONTACTS', r'PYRO', r'BATTERY JUNCTION BOX', r'\bBJB\b',
        r'HIGH[- ]VOLTAGE RELAY', r'PRE-?CHARGE', r'BATTERY DISCONNECT UNIT', r'\bBDU\b'],
}
NOT_TERMS = [r'SUPERCHARG', r'TURBOCHARG', r'TORQUE CONVERTER', r'CATALYTIC CONVERTER',
             r'SOLAR[^|]*']   # revision 1: RV solar charge controllers (the rest of that component field is dropped)
NOT_COMP_PREFIX = ('EQUIPMENT:RECREATIONAL VEHICLE/TRAILER',)   # RV house electrical, not vehicle propulsion

# Plug-in rule P1: a charging component is a plug-in by construction. Rule P2: make or model name pattern.
P1_COMP = r'PROPULSION SYSTEM:CHARGING'
# S2b propulsion context: some record's COMPNAME is a propulsion category, or the campaign hits the OBC group
PROP_COMP = r'PROPULSION'
# revision 1: only these OBC terms stand in for a propulsion category / plug-in (a bare "CHARGER" does not)
OBC_STRICT = r'ON[- ]?BOARD CHARG|\bOBCM?\b|\bICCU\b|INTEGRATED CHARGING'
P2_MAKES = {'TESLA', 'RIVIAN', 'LUCID', 'POLESTAR', 'FISKER', 'LORDSTOWN', 'BRIGHTDROP', 'VINFAST', 'KARMA', 'CANOO',
            'PROTERRA', 'LION ELECTRIC', 'BYD', 'ARRIVAL', 'XOS', 'NIKOLA', 'BOLLINGER', 'WORKHORSE', 'LIGHTNING EMOTORS',
            'MULLEN', 'PHOENIX MOTORCARS', 'GREENPOWER', 'ZEUS', 'HARBINGER', 'SCOUT',
            # revision 1
            'ZERO', 'ARCIMOTO', 'LIVEWIRE', 'ELECTRAMECCANICA', 'MOTIV', 'SEA ELECTRIC', 'TROPOS'}
P2_MODEL = [
    r'\bEV\d?\b', r'ELECTRIC', r'E-TRON', r'\bPHEV\b', r'PLUG-?IN', r'\bPLUG\b', r'\bPRIME\b', r'\b4XE\b', r'RECHARGE',
    r'E-HYBRID', r'ENERGI', r'IONIQ ?[56]', r'\bBOLT\b', r'\bLEAF\b', r'MACH-E', r'LIGHTNING', r'E-TRANSIT', r'TAYCAN',
    r'\bI[3457]\b', r'\bIX\d?\b', r'\bEQ[ABCES]\b', r'\bEQ\b', r'\bID\.? ?4\b', r'ID\.? ?BUZZ', r'BZ4X', r'SOLTERRA',
    r'ARIYA', r'LYRIQ', r'OPTIQ', r'VISTIQ', r'CELESTIQ', r'HUMMER', r'\bVOLT\b', r'PACIFICA HYBRID', r'\bC40\b',
    r'\bEX30\b', r'\bEX90\b', r'\bGV60\b', r'\bRZ\b', r'UX ?300E', r'450H\+', r'GRAND TOURING', r'\b\d{3}E\b',
    r'XDRIVE\d{2}E', r'I-PACE', r'PROLOGUE', r'\bZDX\b', r'CYBERTRUCK', r'HORNET R/T', r'E-GOLF', r'FORTWO',
    r'CROSSTREK HYBRID', r'EDV', r'\bR1[ST]\b', r'MODEL [3SXY]',
    # revision 1 (after inspecting make/model/component fields of the unresolved list only; pre-registration §2)
    r'MACH ?E\b', r'\bBEV\b', r'\bXH?E\d\d', r'RIZON', r'JOULEY', r'E-ACTT', r'\bBZ\b', r'D45CRTE', r'J4500E']

FIELDS = {'campno': 1, 'make': 2, 'model': 3, 'year': 4, 'compname': 6, 'mfgname': 7, 'rcltype': 10, 'potaff': 11,
          'influenced': 13, 'rcdate': 15, 'mfr_comp_name': 24, 'mfr_comp_desc': 25}
DESC_DEFECT = 19   # never read beyond a non-empty test

BASE_TOP = {'body': ('STRUCTURE', 'LATCHES/LOCKS/LINKAGES', 'SEATS'), 'chassis': ('SUSPENSION', 'WHEELS'),
            'restraint': ('AIR BAGS', 'SEAT BELTS')}


def rx(pats):
    return re.compile('|'.join(f'(?:{p})' for p in pats), re.I)


def load(path):
    camps = collections.defaultdict(list)
    n_all = 0
    with open(path, encoding='utf-8', errors='replace') as f:
        for line in f:
            r = line.rstrip('\n').split('\t')
            n_all += 1
            if len(r) < 27:
                continue
            rec = {k: r[i].strip() for k, i in FIELDS.items()}
            rec['has_summary'] = bool(r[DESC_DEFECT].strip())
            camps[rec['campno']].append(rec)
    return n_all, camps


def main(src, outdir):
    n_all, camps = load(src)
    g_rx = {g: rx(p) for g, p in GROUPS.items()}
    not_rx = rx(NOT_TERMS)
    p1 = re.compile(P1_COMP, re.I)
    p2 = rx(P2_MODEL)
    steps = {'records_in_file': n_all, 'campaigns_in_file': len(camps)}
    win = {c: rs for c, rs in camps.items()
           if any(r['rcltype'] == 'V' and DATE_LO <= r['rcdate'][:8] <= DATE_HI for r in rs)}
    steps['S1_vehicle_campaigns_2018-01-01_to_2026-10-31'] = len(win)

    hit = {}
    for c, rs in win.items():
        groups = set()
        for r in rs:
            if r['compname'].upper().startswith(NOT_COMP_PREFIX):
                continue
            txt = ' | '.join((r['compname'], r['mfr_comp_name'], r['mfr_comp_desc']))
            clean = not_rx.sub(' ', txt)
            for g, x in g_rx.items():
                if x.search(clean):
                    groups.add(g)
        if groups:
            hit[c] = groups
    steps['S2_component_term_hit'] = len(hit)
    steps['S2_by_group'] = {g: sum(g in v for v in hit.values()) for g in GROUPS}
    pc = re.compile(PROP_COMP, re.I)
    ob = re.compile(OBC_STRICT, re.I)
    hit = {c: g for c, g in hit.items()
           if any(pc.search(r['compname']) or ob.search(' | '.join((r['mfr_comp_name'], r['mfr_comp_desc'])))
                  for r in win[c])}
    steps['S2b_propulsion_context'] = len(hit)

    inc, unres = {}, {}
    for c, groups in hit.items():
        rs = win[c]
        rule = None
        if any(p1.search(r['compname']) or ob.search(' | '.join((r['compname'], r['mfr_comp_name'],
                                                                   r['mfr_comp_desc']))) for r in rs):
            rule = 'P1'
        elif any(r['make'].upper() in P2_MAKES or p2.search(r['model']) for r in rs):
            rule = 'P2'
        (inc if rule else unres)[c] = (groups, rule)
    steps['S3_plug_in'] = len(inc)
    steps['S3_plug_in_by_rule'] = {k: sum(v[1] == k for v in inc.values()) for k in ('P1', 'P2')}
    steps['S3_plug_in_unresolved'] = len(unres)
    steps['S4_included_with_defect_summary_present'] = sum(any(r['has_summary'] for r in win[c]) for c in inc)

    # clusters: same manufacturer and group with any shared model name (union-find)
    ids = sorted(inc)
    par = {c: c for c in ids}

    def find(c):
        while par[c] != c:
            par[c] = par[par[c]]
            c = par[c]
        return c
    for i, a in enumerate(ids):
        ma = {r['model'].upper() for r in win[a]}
        for b in ids[i + 1:]:
            if win[a][0]['mfgname'] == win[b][0]['mfgname'] and inc[a][0] & inc[b][0] and \
                    ma & {r['model'].upper() for r in win[b]}:
                par[find(a)] = find(b)
    clusters = {c: find(c) for c in ids}
    steps['S5_mechanical_clusters'] = len(set(clusters.values()))

    # base-rate sample (brief §3.2): vehicle campaigns in the window whose every record is body / chassis / restraint
    tops = {t: k for k, v in BASE_TOP.items() for t in v}
    base_pool = sorted(c for c, rs in win.items()
                       if all(r['compname'].split(':')[0].strip().upper() in tops for r in rs))
    n = len(inc)
    k = len(base_pool) // n
    base = [base_pool[k // 2 + i * k] for i in range(n)]
    steps['base_pool'] = len(base_pool)
    steps['base_k'] = k

    def summ(c, rs):
        mk = sorted({r['make'] for r in rs})
        models = sorted({f"{r['model']}" for r in rs})
        yrs = sorted({r['year'] for r in rs if r['year'] != '9999'})
        return {
            'campno': c, 'nhtsa_id': f'{c[:3]}-{c[3:6]}', 'rcdate': min(r['rcdate'] for r in rs),
            'mfgname': rs[0]['mfgname'], 'makes': mk, 'models': models,
            'years': f'{yrs[0]}-{yrs[-1]}' if yrs else 'n/a',
            'compname': sorted({r['compname'] for r in rs}),
            'mfr_comp_name': sorted({r['mfr_comp_name'] for r in rs if r['mfr_comp_name']}),
            'potaff': max((int(r['potaff']) for r in rs if r['potaff'].isdigit()), default=None),
            'influenced_by': sorted({r['influenced'] for r in rs if r['influenced']}),
            'url': f'https://www.nhtsa.gov/recalls?nhtsaId={c[:6]}',
        }
    cases = []
    for i, c in enumerate(sorted(inc, key=lambda c: min(r['rcdate'] for r in win[c]))):
        d = summ(c, win[c])
        d.update({'case': f'PE{i + 1:03d}', 'groups': sorted(inc[c][0]), 'plugin_rule': inc[c][1],
                  'cluster': clusters[c]})
        cases.append(d)
    cl_name = {}
    for d in cases:
        cl_name.setdefault(d['cluster'], f'C{len(cl_name) + 1:02d}')
        d['cluster'] = cl_name[d['cluster']]
    unresolved = [dict(summ(c, win[c]), groups=sorted(unres[c][0])) for c in sorted(unres)]
    basecases = []
    for i, c in enumerate(base):
        d = summ(c, win[c])
        d.update({'case': f'BR{i + 1:03d}',
                  'class': sorted({tops[r['compname'].split(':')[0].strip().upper()] for r in win[c]})})
        basecases.append(d)

    os.makedirs(outdir, exist_ok=True)
    json.dump({'source': os.path.basename(src), 'steps': steps, 'groups': GROUPS, 'not_terms': NOT_TERMS,
               'p2_makes': sorted(P2_MAKES), 'p2_model': P2_MODEL, 'base_top': BASE_TOP, 'cases': cases,
               'unresolved': unresolved, 'base_rate': basecases},
              open(os.path.join(outdir, 'FR1_screen.json'), 'w'), indent=1)
    print(json.dumps(steps, indent=1))




def render(js, path):
    """Write results/FR1/FR1_cases.md from FR1_screen.json. Component, model and date fields only."""
    d = json.load(open(js))
    st = d['steps']
    L = ['# FR1 case list (fixed blind, before rating)', '',
         '**Source:** NHTSA ODI recall flat file `FLAT_RCL_POST_2010.txt` (US Government work, public domain). Fields '
         'used: campaign number, dates, make, model, year, manufacturer, NHTSA component (COMPNAME), the '
         'manufacturer-supplied component name and description, potentially affected units, and "influenced by". '
         '**No defect summary, consequence, remedy or notes text was read, printed or written to build this list.** '
         'Screen: [`analysis/FR1_screen.py`](../../analysis/FR1_screen.py); rules: '
         '[`FR1_preregistration.md`](FR1_preregistration.md) §2; machine-readable copy: '
         '[`FR1_screen.json`](FR1_screen.json).', '',
         '## Screen counts', '', '| Step | Count |', '|---|---|']
    for k, v in st.items():
        L.append(f'| {k} | {json.dumps(v)} |')
    L += ['', f"## Power-electronics cases ({len(d['cases'])})", '',
          'Each row is one NHTSA campaign. The document to rate from is the campaign\'s Part 573 Safety Recall Report '
          '(pre-registration §4.1), reached from the NHTSA link.', '',
          '| Case | NHTSA ID | Part 573 received | Manufacturer | Models (years) | NHTSA component | Manufacturer component '
          '| Group | Plug-in rule | Cluster | Units | Initiated by |',
          '|---|---|---|---|---|---|---|---|---|---|---|---|']

    def cell(x, n=None):
        s = '; '.join(x) if isinstance(x, list) else str(x)
        s = s.replace('|', '/')
        return s if n is None or len(s) <= n else s[:n - 1] + '…'
    for c in d['cases']:
        L.append(f"| {c['case']} | [{c['nhtsa_id']}]({c['url']}) | {c['rcdate']} | {cell(c['mfgname'])} | "
                 f"{cell(c['models'], 90)} ({c['years']}) | {cell(c['compname'], 140)} | {cell(c['mfr_comp_name'], 90)} | "
                 f"{cell(c['groups'])} | {c['plugin_rule']} | {c['cluster']} | {c['potaff']} | {cell(c['influenced_by'])} |")
    L += ['', f"## Component hits not resolved as plug-in ({len(d['unresolved'])}; **not** in the case list)", '',
          'Passed S2b (component term in a propulsion context) but neither plug-in rule. Listed for the reviewer; '
          'model names only were used to classify.', '',
          '| NHTSA ID | Part 573 received | Manufacturer | Models (years) | Group |', '|---|---|---|---|---|']
    for c in d['unresolved']:
        L.append(f"| [{c['nhtsa_id']}]({c['url']}) | {c['rcdate']} | {cell(c['mfgname'])} | {cell(c['models'], 90)} "
                 f"({c['years']}) | {cell(c['groups'])} |")
    L += ['', f"## Base-rate sample ({len(d['base_rate'])}; brief §3.2)", '',
          f"Every {st['base_k']}-th campaign (starting at index {st['base_k'] // 2}) of the {st['base_pool']} vehicle "
          'campaigns in the window whose every record is a body, chassis or restraint component, ordered by campaign '
          'number.', '',
          '| Case | NHTSA ID | Part 573 received | Manufacturer | Models (years) | NHTSA component | Class |',
          '|---|---|---|---|---|---|---|']
    for c in d['base_rate']:
        L.append(f"| {c['case']} | [{c['nhtsa_id']}]({c['url']}) | {c['rcdate']} | {cell(c['mfgname'])} | "
                 f"{cell(c['models'], 70)} ({c['years']}) | {cell(c['compname'], 100)} | {cell(c['class'])} |")
    open(path, 'w').write('\n'.join(L) + '\n')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
    render(os.path.join(sys.argv[2], 'FR1_screen.json'), os.path.join(sys.argv[2], 'FR1_cases.md'))
