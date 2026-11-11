# usage: python3 -I write_1b.py OUTDIR FETCHLOG
import sys, json, csv, os
out, flog = sys.argv[1], sys.argv[2]
md_p = os.path.join(out, 'DC2_instruments.md'); js_p = os.path.join(out, 'DC2_screen.json')
md = open(md_p, encoding='utf-8').read()

ORIG = 'DC2-1 (cited by OCP DCF LVDC white paper, locator; reference list, ‘{}’)'
X = [
 dict(instrument_id='X01', group='X', identifier='AESO guide, date of issue June 12, 2026',
  title='Guide to AESO Connection Requirements for Transmission-Connected Data Centres', issuing_body='Alberta Electric System Operator (AESO)', jurisdiction='CA-AB (AIES)',
  landing_url='https://www.aeso.ca/assets/Uploads/grid/Guide-to-AESO-Connection-Requirements-for-Transmission-Connected-Data-Centres.pdf',
  scope='“The AESO will review all transmission-connected data centre facilities, regardless of size, to determine whether the TCDC requirements and mitigations referred to in this guide are appropriate. The connection of data centres on distribution systems could also impact the transmission system. … Data centres connecting to the distribution system can review this guide of TCDC requirements and mitigations for specific reliability concerns the AESO and DFOs may seek to address.” (1. Applicability)',
  headings='3 ARS, ISO Rules and Functional Specifications; 5 Facility Design (5.1 Transmission and Substation Design; 5.2 Emergency Back-up Design; 5.3 Reactive Power Capability; 5.4 Protection and Control; 5.5 Monitoring); 6 Disturbance Response (6.1 Ride-Through Capability; UFLS); 7 Operations and Balancing (7.1 Oscillatory Behaviours; 7.2 Ramping; 7.3 Operational Procedures; 7.4 Reconnection; 7.5 Real-Time Coordination); 8 Connection Studies (8.1 Connection Study Requirements)',
  access='full', status='in force (issued; “Date of issue: June 12, 2026”, as printed)',
  origin=ORIG.format('AESO — Guide to AESO Connection Requirements for Transmission-Connected Data Centres'),
  references='not screened (DC2-1 addition; one level)'),
 dict(instrument_id='X02', group='X', identifier='Fingrid Oyj, 12.6.2026 (Finnish text, 46 pp.)',
  title='Suurten kulutuslaitosten tekniset vaatimukset (English title on Fingrid’s page: “Technical requirements for large demand facilities”)', issuing_body='Fingrid Oyj (TSO)', jurisdiction='FI',
  landing_url='https://www.fingrid.fi/en/grid/grid-connection-agreement-phases/grid-code-specifications/draft-for-comments-kjv2026-grid-code-specifications-for-demand-connections/ (attachment: https://www.fingrid.fi/globalassets/dokumentit/fi/palvelut/kulutuksen-ja-tuotannon-liittaminen-kantaverkkoon/fingrid---suurten-kulutuslaitosten-tekniset-vaatimukset.pdf)',
  scope='“Fingrid has also published on 12 June 2026 a separate document entitled “Technical requirements for large demand facilities” (Suurten kulutuslaitosten tekniset vaatimukset, see attachments). The technical requirements presented in this document are applied immediately to demand facilities directly connected to the Fingrid’s transmission grid. The requirements described in the document do not apply to demand facilities connected to distribution networks.” (Fingrid landing page)',
  headings='2 Sovellusala; 4 Kulutuslaitosten erityistarkasteluvaatimukset; 8 Reaaliaikaiset mittaukset ja tiedonvaihto; 9 Kulutuslaitoksia koskevat vaatimukset (9.1.1 Sähkölaitteiston taajuuden muutosnopeuden sietokyky; 9.1.3 Jännitteen kulmamuutokset; 9.1.6 Ohjaukset ja kaukokäyttö; 9.1.7 Pätötehon säätö ja pätötehon muutokset; 9.1.8 Pätötehon nopea rajoitustoiminto; 9.1.9 Alijännitteestä aiheutuva pätötehon nopea rajoitus; 9.1.10 Toiminta jännitehäiriön yhteydessä; 9.1.11 Pätötehon palautuminen jännitehäiriön jälkeen; 9.1.13 Vuorovaikutusilmiöt; 9.1.14 Sähkön laatu; 9.1.15 Instrumentointivaatimukset; 9.1.16 Mallinnusvaatimukset); 10 Vaatimustenmukaisuuden todentaminen',
  access='full', status='in force (as printed on the landing page: “applied immediately to demand facilities directly connected to the Fingrid’s transmission grid”; the related KJV2026 draft is a separate, pending document and is not listed)',
  origin=ORIG.format('Fingrid — Technical requirements for large demand facilities'),
  references='not screened (DC2-1 addition; one level)'),
 dict(instrument_id='X03', group='X', identifier='IESO, Version 1.0, 01/May/2026',
  title='Technical Requirements for Large Computational Loads Connecting to the Ontario Power System', issuing_body='Independent Electricity System Operator (IESO)', jurisdiction='CA-ON',
  landing_url='https://ieso.ca/-/media/Files/IESO/Document-Library/engage/large-computational-loads/LargeComputationalLoads-20260501-Technical-Requirements.pdf',
  scope='“This document has been developed to set out the complete technical requirements for connecting large computational loads to the Ontario power system. It includes both the existing technical requirements for general load facilities and newly developed technical requirements that aim to address potential adverse impacts on system reliability caused by the specific load behaviors of large computational loads.” (1. Purpose) “This document is applicable to all existing and future large computational loads connected to the IESO-controlled grid including: Large computational loads of any size that are directly connected to the Ontario transmission system and, Large computational loads rated higher than 10 MW connected to a distribution system.” (2. Applicability)',
  headings='3 Interconnection Process; 4 Applicable Reliability Standards; 5 Project Data Requirement; 6 Interconnection Requirements for Large Computational Loads (6.1 Connection Arrangement; 6.2 Power Factor/Reactive Power Capability; 6.3 Damping; 6.4 Periodic Oscillation; 6.5 Load Fluctuation; 6.6 [heading withheld by the screener’s redaction filter]; 6.7 Ride-through Capabilities; 6.8 Automatic Under-Frequency Load Shedding (UFLS); 6.9 Phasor Measurement; 6.10 Dynamic Disturbance Recording; 6.13 Protection Systems; 6.16 Commissioning Tests and Performance Validation; 6.18 Specific Interconnection Requirements)',
  access='full', status='pending (as printed: “New requirements proposed in this document will be updated into the Market Rules or relevant standards after the IESO external stakeholdering over these requirements is completed.”)',
  origin=ORIG.format('IESO — Technical Requirements for Large Computational Loads Connecting to the Ontario Power System'),
  references='not screened (DC2-1 addition; one level)'),
]
cols = ['instrument_id','group','identifier','title','issuing_body','jurisdiction','landing_url','scope','headings','access','status','origin','references']
rows = '\n'.join('| ' + ' | '.join(r[c].replace('|', '/') for c in cols) + ' |' for r in X)
anchor = next(l for l in md.split('\n') if l.startswith('| V14 |'))
assert md.count(anchor) == 1
md = md.replace(anchor, anchor + '\n' + rows)

old_counts = '**Counts.** G: 16 seed + 0 added; U: 3 seed + 0 added; E: 11 seed + 0 added; Q: 6 seed + 3 added; V: 14 seed + 0 added. Total 53 instruments (50 seed, 3 added). Access: full 40, partial 13, none 0. Pending (status as printed): G07, G08, G09, G11, G15, E03, E06.'
new_counts = '**Counts.** G: 16 seed + 0 added; U: 3 seed + 0 added; E: 11 seed + 0 added; Q: 6 seed + 3 added; V: 14 seed + 0 added; X (other grid operators, DC2-1, stage 1b): 0 seed + 3 added. Total 56 instruments (50 seed, 6 added: 3 by S3, 3 by DC2-1). Access: full 43, partial 13, none 0. Pending (status as printed): G07, G08, G09, G11, G15, E03, E06, X03.'
assert md.count(old_counts) == 1
md = md.replace(old_counts, new_counts)

C = [
 # id, body, title judged (exact, from body's own site unless noted), citing, outcome, reason
 ('C01','NERC','BAL-001-2 — Real Power Balancing Control Performance','NERC white paper (seed locator); NERC gap white paper (seed locator)','fail','no load term; no connection / interconnection / technical / performance requirements'),
 ('C02','NERC','TOP standards family (record names the family only): TOP-001-6 Transmission Operations; TOP-002-5 Operations Planning; TOP-003-7 Transmission Operator and Balancing Authority Data and Information; TOP-010-1(i) Real-time Reliability Monitoring and Analysis Capabilities','NERC gap white paper (seed locator)','fail','no load term in any title'),
 ('C03','NERC','Reliability Guideline: Primary Frequency Control (title as cited; not resolved on nerc.com, guessed URL 404)','G05','fail','no load term'),
 ('C04','NERC','TPL-001-5.1 — Transmission System Planning Performance Requirements (cited as TPL-001-5)','G05','fail','names performance requirements, but no data-centre / large-load / computational-load term'),
 ('C05','NERC','Disturbance monitoring and analysis of oscillatory events (title as cited, ref. [11])','arXiv 2508.14318 (S1 locator)','fail','no load term; no requirements term'),
 ('C06','NERC','Interconnection oscillation analysis (title as cited, ref. [12])','arXiv 2508.14318 (S1 locator)','fail','no load term; no requirements term'),
 ('C07','NERC','Incident Review — Considering Simultaneous Voltage-Sensitive Load Reductions','OCP DCF LVDC white paper (locator)','fail','“voltage-sensitive load”, not large / data-centre / computational; no requirements term'),
 ('C08','NERC','Characteristics and Risks of Emerging Large Loads — Large Loads Task Force White Paper (cited as “Characterization and Risks …”)','OCP DCF LVDC white paper (locator)','fail','names large loads, but no requirements term (it is also an S0 locator already)'),
 ('C09','NERC','Risk Mitigation for Emerging Large Loads — Reliability Guideline','OCP DCF LVDC white paper (locator)','already listed (G05)','no new row; title alone would fail (no requirements term)'),
 ('C10','NERC','Essential Action to Industry — Computational Load Modeling, Studies, Instrumentation, Commissioning, Operations, Protection, and Control (Level 3 Alert, May 4, 2026)','EPRI DCFlex 3002036343 (S1 locator; named in its title)','fail','names computational load, but no connection / interconnection / technical / performance requirements'),
 ('C11','ERCOT','NOGRR282 — Board Priority – Large Computational Load Ride-Through Requirements','V09; OCP DCF LVDC white paper (locator, twice)','already listed (in G03)','no new row; title names large computational loads with ride-through requirements, which is not one of the four named requirement kinds (see deviation DC2-1b-1)'),
 ('C12','SPP','HIGH IMPACT LARGE LOAD RIDE-THROUGH REQUIREMENTS, Version 0.1, published 08/15/2025 (cited as “SPP HILL Fault Ride Through Requirements, Version …” and “High Impact Large Load Ride-Through Requirements”)','OCP DCF LVDC white paper (locator, refs [12,13,21])','fail (borderline)','names high-impact large loads, but the requirement kind is ride-through, not connection / interconnection / technical / performance (deviation DC2-1b-1)'),
 ('C13','SPP','RR696 — Integrate & Operate High Impact Large Loads (link text on spp.org HILL page)','OCP DCF LVDC white paper (locator)','fail (borderline)','names high-impact large loads, but “Integrate & Operate” is not connection / interconnection / technical / performance requirements (deviation DC2-1b-1)'),
 ('C14','IESO','Technical Requirements for Large Computational Loads Connecting to the Ontario Power System','OCP DCF LVDC white paper (locator, ref. [23], twice)','PASS → X03','large computational loads + technical requirements (+ connecting)'),
 ('C15','EirGrid / SONI','Grid Code Modification Recommendation Form — MPID 345 Fault Ride Through, Rate of Change of Frequency and Post Fault Active Power Recovery for Demand Facilities (cited as “Demand Facilities FRT Recommendation Paper”)','OCP DCF LVDC white paper (locator, ref. [25])','fail','“demand facilities” without “large”; no requirements term'),
 ('C16','EirGrid / SONI','Large Demand Facility Fault Ride-Through Issue and Proposed Solutions — Information Paper prepared by EirGrid and SONI, November 2025','OCP DCF LVDC white paper (locator, ref. [25])','fail','names large demand facility, but no connection / interconnection / technical / performance requirements'),
 ('C17','ATC (American Transmission Co.)','Transmission System Planning Criteria, PLG-CR-0001-V26 (copy cited is on cdn.misoenergy.org)','OCP DCF LVDC white paper (locator, ref. [22])','fail','no load term'),
 ('C18','AESO','Guide to AESO Connection Requirements for Transmission-Connected Data Centres','OCP DCF LVDC white paper (locator, ref. [24])','PASS → X01','data centres + connection requirements'),
 ('C19','Energinet','Technical Regulation 3.4.3 Requirements for Transmission-Connected Demand Facilities, Revision 1','OCP DCF LVDC white paper (locator, ref. [26])','fail','“demand facilities” without “large”; no data-centre term'),
 ('C20','RTE','Documentation Technique de Référence — Article 8.3.5 – Cahier des Charges des capacités constructives d’une Installation de consommation (v1.0)','OCP DCF LVDC white paper (locator, ref. [27])','fail','“installation de consommation” (any consumer installation), not large / data-centre / computational'),
 ('C21','Fingrid','Suurten kulutuslaitosten tekniset vaatimukset — “Technical requirements for large demand facilities”','OCP DCF LVDC white paper (locator, ref. [28])','PASS → X02','large demand facilities + technical requirements'),
 ('C22','European Commission','Commission Regulation (EU) 2016/1388 — Network Code on Demand Connection','OCP DCF LVDC white paper (locator, ref. [29])','already listed (E01)','no new row; title alone would fail (demand connection, no large-load term)'),
 ('C23','FERC','195 FERC ¶ 61,211, Docket No. EL26-67-000 (PJM Interconnection, L.L.C. et al.) — Order Instituting Proceeding Under Section 206 of the Federal Power Act (issued June 18, 2026)','PJM presentation (S1 locator)','fail','no load term; no requirements term'),
]
lines = ['', '### DC2-1 title test (stage 1b)', '',
 'Applied by a fresh-context stage-1b screener on 2026-11-10, before any limit is read. Candidates are the documents of a grid operator, TSO, ISO / RTO or energy regulator that a listed instrument or an S1 locator cites in the `DC2_screen.json` record, whatever they were cited for. Exact titles were taken from the body’s own document or page; the OCP DCF LVDC white paper’s reference-list entries were re-read (masked) only to identify which documents were cited. The title is judged alone: it passes when it names data centres, large loads, large demand facilities, (large) computational loads or high-impact loads **and** connection, interconnection, technical or performance requirements. Result: **23 candidates, 3 pass (X01–X03), 20 fail** (of which 3 are already listed: G05, G03, E01).', '',
 '| # | body | title judged | cited by | outcome | reason |', '|---|---|---|---|---|---|']
lines += ['| ' + ' | '.join(c) + ' |' for c in C]
lines += ['',
 'Not candidates: the DOE Section 403 letter (named in the title of EPRI DCFlex 3002034369; DOE is not a grid operator, TSO, ISO / RTO or energy regulator); Texas SB 6 (named in EPRI DCFlex 3002033410; a statute); documents of IEC, IEEE, CENELEC, ESIG, EPRI, OCP and NVIDIA (not grid bodies). Citations that the stage-1 record gives only as counts (for example G01 “read 34”) name no document and could not be judged (deviation DC2-1b-6).',
 '',
 'Stage-1b deviations (DC2-1b-1 … 1b-8) are in `DC2_screen.json` → `stage_1b.deviations`. The main one: **DC2-1b-1** reads the rule literally, so a title whose only requirement word is “ride-through” or “Integrate & Operate” (C11–C13) fails; if the reviewer reads ride-through requirements as performance requirements, C12 (SPP) would pass and C11 is already listed.',
 '']
sec6 = '\n## 6. Screener deviations'
assert md.count(sec6) == 1
md = md.replace(sec6, '\n'.join(lines) + sec6)
open(md_p, 'w', encoding='utf-8').write(md)

# JSON
d = json.load(open(js_p, encoding='utf-8'))
fetches = []
for r in csv.reader(open(flog, encoding='utf-8'), delimiter='\t'):
    t, url, name, code, final, ctype, size = r[:7]
    e = dict(t=t, url=url, out=name, status=int(code), final_url=final, ctype=ctype, bytes=int(float(size)))
    if 'Error-404' in final: e['note'] = 'HTTP 200 but redirected to the IESO Error-404 page (not found)'
    if code == '403': e['note'] = 'Access denied page; not bypassed (PDF fetched directly instead)'
    fetches.append(e)
queries = [
 dict(tool='WebSearch', query='IESO Large Computational Loads engagement technical requirements', allowed_domains=['ieso.ca'], hits=10, note='located IESO PDF; summary leaked limit content (DC2-1b-3)'),
 dict(tool='WebSearch', query='Fingrid technical requirements for large demand facilities', allowed_domains=['fingrid.fi'], hits=10, note='located Fingrid pages; summary leaked limit content (DC2-1b-3)'),
 dict(tool='WebSearch', query='Energinet Technical Regulation 3.4.3', allowed_domains=['energinet.dk','en.energinet.dk'], hits=10, note='located TR 3.4.3 PDF; summary carried applicability thresholds and topic names only'),
 dict(tool='WebSearch', query='RTE Documentation Technique de Référence article 8.3.5', allowed_domains=['rte-france.com','services-rte.com'], hits=10, note='located DTR 8.3.5 PDF; summary named topics, no values'),
 dict(tool='WebSearch', query='MPID345 Large Demand Facility FRT Information Paper', allowed_domains=['eirgrid.ie','cms.eirgrid.ie','soni.ltd.uk'], hits=9, note='located EirGrid information paper; summary carried no values'),
 dict(tool='WebSearch', query='NERC Level 3 alert computational load essential actions 2026', allowed_domains=['nerc.com'], hits=10, note='located Level 3 alert PDF; summary listed the essential actions (procedural, no values)'),
 dict(tool='WebSearch', query='FERC EL26-67 order to show cause large load', allowed_domains=['ferc.gov'], hits=10, note='located EL26-67-000 PDF; summary procedural (response days), no load limits'),
 dict(tool='script', query='OCP DCF LVDC white paper reference list (S1 masking; URLs kept)', hits=18, note='entries naming NERC, ERCOT, SPP, IESO, EirGrid/SONI, ATC, AESO, Energinet, RTE, Fingrid, EU documents'),
 dict(tool='script', query='arXiv 2508.14318 reference entries [11], [12] (S1 masking)', hits=2, note='two NERC reports'),
 dict(tool='page links', query='spp.org HILL integration page', hits=1, note='RR696 title from link text'),
 dict(tool='page links', query='fingrid.fi demand-connection pages', hits=2, note='attachment “Fingrid - Suurten kulutuslaitosten tekniset vaatimukset.pdf” found on the KJV2026 page'),
]
devs = [
 'DC2-1b-1. Title test read literally. A title passes only if it names one of the four requirement kinds (connection, interconnection, technical, performance) with a normative noun (requirements). “Ride-Through Requirements” (ERCOT NOGRR282, SPP HILL) and “Integrate & Operate” (SPP RR696) therefore fail. NOGRR282 is already listed (G03). Under a broader reading (ride-through requirements counted as performance requirements), the SPP ride-through document (C12) would pass. Flagged for the reviewer; no row added for it.',
 'DC2-1b-2. Re-reading locator reference lists. The record named the OCP LVDC citations only by body and short description, so the screener re-read that paper’s reference-list entries and arXiv 2508.14318 refs [11]–[12] with S1 masking (digits, %, time units → #), keeping URLs unmasked to locate documents. The first parser attempt matched two lines of the LVDC paper’s ride-through table instead of references (RTE and Fingrid rows). All digits were masked; they showed only that those rows concern post-fault active-power recovery. No value was read.',
 'DC2-1b-3. WebSearch summaries exposed limit content that was not asked for, and it is not repeated here. (a) IESO query: values from the IESO draft for a normal-operation ramp limit, the power-factor range, a load-loss cap and a monitoring threshold, plus third-party comment on the ride-through and ramp requirements. (b) Fingrid query: values for fault ride-through and post-fault active-power recovery, active-power limitation levels with a setpoint time, disturbance-recording rate and storage, and a frequency band and RoCoF value from KJV2026 draft slides. (c) Energinet, RTE, EirGrid, NERC and FERC queries: no limit values (applicability thresholds, topics and procedural deadlines only). None of this drove a decision: X01–X03 pass on title alone and would pass had nothing been seen. The screener is not a rater.',
 'DC2-1b-4. Heading extraction for IESO X03 used a numbered-line pattern, which also printed three rows of the §6.8 UFLS table (load-size bands with frequency, delay and share settings). That is UFLS (non-deciding), and the values are not repeated. The redaction filter withheld IESO heading 6.6 and Fingrid heading 9.1.12; they were not recovered.',
 'DC2-1b-5. Landing pages. No HTML landing page was found for AESO X01 or IESO X03. Two IESO engagement-page guesses returned the IESO Error-404 page. The landing URL is therefore the PDF on the body’s own site. For Fingrid X02 the landing is the fingrid.fi page that hosts the attachment and states its scope and status; the document is in Finnish, and the English title is the one Fingrid prints on that page. The EirGrid information-paper HTML page returned 403 (Access denied) and was not bypassed; the title was read from the PDF at the same host (redirected to eirgrid.ie). The ATC criteria were read from the copy the locator cites, on cdn.misoenergy.org.',
 'DC2-1b-6. Scope of the candidate set. Candidates are the grid-body documents named in the record (S3 logs, locator candidate fields), the LVDC reference list behind the record’s LVDC entry, the arXiv refs behind “NERC oscillation reports”, the FERC order the PJM presentation mentions, and a NERC alert named in an EPRI locator title. Citations the stage-1 record gives only as counts (for example “read 34” for G01) name no document. They were not re-read from the instruments and could not be judged.',
 'DC2-1b-7. Titles judged as cited, not resolved on the body’s site: NERC Primary Frequency Control guideline (guessed URL 404) and the two NERC oscillation reports cited by arXiv 2508.14318. Each fails on any title that names no load term. For the TOP family, the record names no specific standard, so four current TOP titles were checked on nerc.com.',
 'DC2-1b-8. Not edited, as instructed: the §1 group legend line (group X is defined in the counts line and in the rows), §2–§4 and §6 of DC2_instruments.md, and every pre-existing key of DC2_screen.json. DC2_orders.json is not in the screener’s files and was not regenerated; the main session should regenerate it over the 56 sorted IDs with rng 31 / 32 (§10 DC2-1).',
]
d['stage_1b'] = dict(
  screener='fresh-context stage-1b screener (sub-agent, not a rater)', date='2026-11-10',
  rule='DC2_preregistration.md §10 DC2-1 (title test), with §2 and §3 S2',
  candidates=[dict(id=c[0], body=c[1], title_judged=c[2], cited_by=c[3], outcome=c[4], reason=c[5]) for c in C],
  not_candidates=['DOE Section 403 letter (EPRI 3002034369 title; DOE is not a grid operator / TSO / ISO / regulator)', 'Texas SB 6 (EPRI 3002033410 title; statute)', 'IEC / IEEE / CENELEC / ESIG / EPRI / OCP / NVIDIA documents (not grid bodies)'],
  title_test_summary=dict(candidates=23, passed=3, failed=20, failed_already_listed=['C09→G05','C11→G03','C22→E01']),
  added=X, queries=queries, fetch_log=fetches, deviations=devs)
json.dump(d, open(js_p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('ok')
