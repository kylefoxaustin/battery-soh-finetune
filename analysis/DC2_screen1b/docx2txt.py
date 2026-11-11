# usage: python3 -I docx2txt.py IN.docx OUT.txt  (text only; one paragraph per line)
import sys, zipfile, re
z = zipfile.ZipFile(sys.argv[1])
x = z.read('word/document.xml').decode('utf-8', 'replace')
paras = re.findall(r'<w:p[ >].*?</w:p>', x, re.S)
out = []
for p in paras:
    t = ''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', p))
    out.append(t)
open(sys.argv[2], 'w').write('\n'.join(out))
try:
    core = z.read('docProps/core.xml').decode('utf-8', 'replace')
    m = re.search(r'<dc:title>([^<]*)</dc:title>', core); print('core title:', m.group(1) if m else None)
except KeyError: print('no core.xml')
