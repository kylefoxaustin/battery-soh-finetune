"""fetch.py URL OUTNAME LOGFILE WEBDIR -- download one URL into WEBDIR/OUTNAME, log status. Never executes content."""
import sys, json, time, urllib.request, urllib.error, os, ssl

url, outname, logf, webdir = sys.argv[1:5]
UA = "DC2-screener research fetch (public grid and power-quality texts)"
time.sleep(2.0)
rec = {"url": url, "out": outname, "t": time.strftime("%Y-%m-%dT%H:%M:%S")}
try:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
        rec.update(status=r.status, final_url=r.geturl(), ctype=r.headers.get("Content-Type"), bytes=len(data))
        with open(os.path.join(webdir, outname), "wb") as f:
            f.write(data)
except urllib.error.HTTPError as e:
    rec.update(status=e.code, error=str(e.reason))
    try:
        body = e.read(4000)
        rec["challenge_hint"] = any(k in body.lower() for k in [b"captcha", b"challenge", b"cloudflare", b"verify you are", b"access denied", b"incapsula", b"akamai"])
    except Exception:
        pass
except Exception as e:
    rec.update(status=None, error=repr(e)[:300])
with open(logf, "a") as f:
    f.write(json.dumps(rec) + "\n")
print(json.dumps(rec))
