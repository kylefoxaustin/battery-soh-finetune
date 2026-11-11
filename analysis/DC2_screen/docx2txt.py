"""docx2txt.py IN OUT : extract paragraph text from a .docx (zip/XML parsing only)."""
import sys, zipfile, re
z = zipfile.ZipFile(sys.argv[1])
x = z.read("word/document.xml").decode("utf-8", "replace")
paras = re.findall(r"<w:p[ >].*?</w:p>", x, re.S)
out = []
for p in paras:
    t = "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", p))
    t = t.replace("&amp;","&").replace("&lt;","<").replace("&gt;",">").replace("&quot;",'"').replace("&apos;","'")
    out.append(t)
open(sys.argv[2], "w").write("\n".join(out))
print("docx paragraphs:", len(out))
