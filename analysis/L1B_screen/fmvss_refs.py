import sys,re,json
import xml.etree.ElementTree as ET
r=ET.parse(sys.argv[1]).getroot()
txt=''.join(r.itertext())
# cut source/citation notes (history) if present: drop anything in CITA / SOURCE elements
for tag in ('CITA','SOURCE','EDNOTE','AUTH'):
    for e in r.iter(tag):
        s=''.join(e.itertext())
        if s.strip(): txt=txt.replace(s,' ')
m=re.search(r"S1 Scope\.(.*?)\n\s*S2 ", txt, re.S)
print("SCOPE:", ' '.join(m.group(1).split()))
m=re.search(r"S3 Application\.(.*?)\n\s*S4 ", txt, re.S)
print("APPLICATION:", ' '.join(m.group(1).split())[:600])
# references with clause
pat=re.compile(r"(SAE (?:Recommended Practice |Standard |Information Report )?J\s?\d+[a-zA-Z]?(?:_\d+)?|ASTM [A-Z]\s?\d+(?:-\d+)?|ANSI[ /][A-Z0-9.\- ]{2,20}|ISO \d+(?:-\d+)?|IEC \d+|part 564|Part 564|§\s?571\.\d+[a-z]?|(?:FMVSS|Standard) No\. \d+[a-z]?|ECE R\s?\d+|Regulation No\. \d+|49 CFR [\d.]+|CIE \d+|Federal Specification [\w\-]+)")
clause=None; refs={}
for line in txt.split('\n'):
    mm=re.match(r"\s*(S\d+(?:\.\d+)*)\b", line)
    if mm: clause=mm.group(1)
    for x in pat.findall(line):
        k=re.sub(r"\s+"," ",x).replace('SAE Recommended Practice ','SAE ').replace('SAE Standard ','SAE ').replace('SAE Information Report ','SAE ')
        refs.setdefault(k,[]).append(clause or 'pre-S1/table')
for k in sorted(refs): print(k, '|', ','.join(sorted(set(refs[k]))[:12]), len(refs[k]))
json.dump(refs, open(sys.argv[2],'w'), indent=0)
