import re,sys,html
# prints ONLY designation (revision suffix stripped), title, and scope panel text (truncated before any history wording)
raw=open(sys.argv[1],encoding='utf-8').read()
m=re.search(r'<h1 class="si-title[^>]*>\s*(J[\d/]+)(?:_\d+)?\s*<span class="si-title__details">([^<]*)</span>',raw)
print('H1:', (m.group(1)+' | '+html.unescape(m.group(2)).strip()) if m else 'none')
m=re.search(r'si-impact__title[^>]*>\s*Scope\s*<.*?<div[^>]*class="[^"]*(?:panel-body|mat-expansion-panel-body)[^"]*"[^>]*>(.*?)</div>\s*</div>',raw,re.S)
if m:
    t=re.sub(r'<!--.*?-->|<[^>]+>',' ',m.group(1)); t=html.unescape(re.sub(r'\s+',' ',t)).strip()
    t=re.split(r'(?i)this (?:document|revision|version) (?:has been|was) (?:revised|updated|reaffirmed)|revision|supersed|reaffirm|stabiliz',t)[0]
    print('SCOPE:',t[:1500])
else: print('SCOPE: none')
