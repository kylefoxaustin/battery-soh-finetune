import re,sys
# usage: iec_page.py page.html -> prints h1, scope abstract truncated BEFORE any edition/history sentence, preview path
raw=open(sys.argv[1],encoding='utf-8').read()
m=re.search(r'<h1[^>]*>(.*?)</h1>',raw,re.S); print('H1:',re.sub(r'<[^>]+>|\s+',' ',m.group(1)).strip() if m else None)
m=re.search(r'<title>([^<]*)',raw); print('TITLE TAG:',m.group(1) if m else None)
txt=re.sub(r'<[^>]+>',' ',raw); txt=re.sub(r'\s+',' ',txt)
m=re.search(r'(IEC [0-9\-]+(?::\d{4})?(?:\+AMD\d:\d{4})*(?: CSV)? (?:applies to|specifies|is applicable|provides|gives|defines|describes|covers|establishes|deals with)[^<]*?)(?=This (?:\w+ )?edition|This consolidated|The contents of the corrigend|It constitutes|IEC [0-9\-]+:\d{4} (?:has|is) |$)',txt)
print('ABSTRACT:',m.group(1)[:1500] if m else None)
pv=sorted(set(re.findall(r'preview/info_[^"\'\s<>]+?\.pdf',raw)))
print('PREVIEW:',pv[:3])
