"""Read-only probe of the BATSS ISC xlsx (stdlib + numpy only). Usage: python3 -I batss_isc_probe.py <xlsx> <out.npz>"""
import sys, zipfile, re
import numpy as np
import xml.etree.ElementTree as ET

path, out = sys.argv[1], sys.argv[2]
z = zipfile.ZipFile(path)
ss = z.read('xl/sharedStrings.xml').decode('utf8', 'replace')
strs = re.findall(r'<t[^>]*>([^<]*)</t>', ss)
NS = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'

def col_idx(ref):
    letters = re.match(r'[A-Z]+', ref).group(0)
    n = 0
    for ch in letters:
        n = n * 26 + (ord(ch) - 64)
    return n - 1

rows = []
header = None
with z.open('xl/worksheets/sheet1.xml') as f:
    for ev, el in ET.iterparse(f, events=('end',)):
        if el.tag != NS + 'row':
            continue
        vals = {}
        for c in el.findall(NS + 'c'):
            v = c.find(NS + 'v')
            if v is None:
                continue
            t = c.get('t')
            txt = v.text
            if t == 's':
                txt = strs[int(txt)]
            vals[col_idx(c.get('r'))] = txt
        if header is None:
            header = [vals.get(i, '') for i in range(max(vals) + 1)]
        else:
            rows.append(vals)
        el.clear()
        if len(rows) % 200000 == 0 and rows:
            print('rows', len(rows), file=sys.stderr)

print('header', header)
ncol = len(header)
n = len(rows)
print('rows', n)
mode_col = header.index('StepMode')
num = np.full((n, ncol), np.nan, dtype=np.float64)
modes = np.empty(n, dtype=object)
for i, r in enumerate(rows):
    for k, v in r.items():
        if k == mode_col:
            modes[i] = v
        else:
            try:
                num[i, k] = float(v)
            except Exception:
                pass
np.savez_compressed(out, header=np.array(header), num=num, modes=np.array(modes, dtype=str))

t = num[:, header.index('Time_s')]
I = num[:, header.index('Current_A_')]
V = num[:, header.index('Voltage_V_')]
vc = num[:, [header.index(f'Vcell_{k}_V_') for k in range(1, 11)]]
tc = num[:, [header.index(f'T{k}_C_') for k in range(1, 56)]]
print('time span s', np.nanmin(t), np.nanmax(t), 'dt median', np.nanmedian(np.diff(t)))
# run boundaries: time resets
resets = np.where(np.diff(t) < 0)[0]
print('time resets at rows', resets[:20], 'count', len(resets))
print('modes', {m: int((modes == m).sum()) for m in set(modes.tolist())})
print('current min/max', np.nanmin(I), np.nanmax(I), 'pack V min/max', np.nanmin(V), np.nanmax(V))
print('cell V min/max per cell', np.round(np.nanmin(vc, 0), 3), np.round(np.nanmax(vc, 0), 3))
print('cell T min/max', np.nanmin(tc), np.nanmax(tc))
dev = vc - np.nanmean(vc, 1, keepdims=True)
# rest segments: |I|<0.05 A for >= 600 s contiguous
rest = np.abs(I) < 0.05
seg = []
start = None
for i in range(n):
    if rest[i] and start is None:
        start = i
    if (not rest[i] or i == n - 1) and start is not None:
        if i - start > 10:
            seg.append((start, i))
        start = None
print('rest segments (>10 rows):', len(seg))
print('Per rest segment: start_t, dur_h, per-cell dV over segment (mV) and dev at end (mV)')
for s, e in seg:
    dur = (t[e - 1] - t[s])
    if dur < 1800:
        continue
    dV = (vc[e - 1] - vc[s]) * 1000
    print(f'  t0={t[s]:9.0f}s dur={dur/3600:6.2f}h  dV(mV)=', np.round(dV, 1), ' dev_end(mV)=', np.round(dev[e - 1] * 1000, 1))
# overall per-cell dev trend by run
for ri, (a, b) in enumerate(zip(np.r_[0, resets + 1], np.r_[resets + 1, n])):
    d0 = np.nanmedian(dev[a:min(a + 50, b)], 0) * 1000
    d1 = np.nanmedian(dev[max(b - 50, a):b], 0) * 1000
    print(f'run {ri}: rows {a}-{b}, t {t[a]:.0f}->{t[b-1]:.0f}s ({(t[b-1]-t[a])/3600:.1f} h); dev start(mV)=', np.round(d0, 1), ' dev end(mV)=', np.round(d1, 1))
