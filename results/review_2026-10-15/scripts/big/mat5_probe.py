"""Minimal read-only MAT-file v5 reader (numeric arrays, cells skipped) for the McMaster files. stdlib+numpy.
Usage: python3 -I mat5_probe.py file.mat [file.mat ...]"""
import sys, struct, zlib
import numpy as np

MI = {1: np.int8, 2: np.uint8, 3: np.int16, 4: np.uint16, 5: np.int32, 6: np.uint32, 7: np.float32, 9: np.float64,
      12: np.int64, 13: np.uint64}
CLS = {6: np.float64, 7: np.float32, 8: np.int8, 9: np.uint8, 10: np.int16, 11: np.uint16, 12: np.int32, 13: np.uint32,
       14: np.int64, 15: np.uint64}


def elements(buf, le='<'):
    pos = 0
    while pos + 8 <= len(buf):
        typ, nb = struct.unpack(le + 'II', buf[pos:pos + 8])
        if typ & 0xFFFF0000:  # small data element
            nb = typ >> 16
            typ = typ & 0xFFFF
            data = buf[pos + 4:pos + 4 + nb]
            pos += 8
        else:
            data = buf[pos + 8:pos + 8 + nb]
            pos += 8 + nb
            if typ != 15:  # miCOMPRESSED elements are not padded to 8 bytes
                pos += (-nb) % 8
        yield typ, data


def parse_matrix(data, le='<'):
    it = elements(data, le)
    _, flags = next(it)
    cls = flags[0]
    _, dims = next(it)
    dims = np.frombuffer(dims, dtype=le + 'i4')
    _, name = next(it)
    name = name.decode('latin1')
    if cls not in CLS:
        return name, f'<class {cls} dims {tuple(dims)} (not parsed)>'
    typ, real = next(it)
    arr = np.frombuffer(real, dtype=np.dtype(MI[typ]).newbyteorder(le)).astype(CLS[cls])
    arr = arr.reshape(tuple(dims), order='F')
    return name, arr


def read(path):
    with open(path, 'rb') as f:
        raw = f.read()
    le = '<' if raw[126:128] == b'IM' else '>'
    out = {}
    for typ, data in elements(raw[128:], le):
        if typ == 15:
            data = zlib.decompress(data)
            typ, data = next(elements(data, le))
        if typ == 14:
            name, arr = parse_matrix(data, le)
            out[name] = arr
    return out


for p in sys.argv[1:]:
    print('==', p.split('/')[-1])
    try:
        d = read(p)
    except Exception as e:
        print('  FAILED', repr(e))
        continue
    for k, v in d.items():
        if isinstance(v, str):
            print(' ', k, v)
            continue
        fin = v[np.isfinite(v)] if v.dtype.kind == 'f' else v
        print(f'  {k:22s} {str(v.shape):16s} {v.dtype}  min={fin.min():.4g} max={fin.max():.4g}' if fin.size else f'  {k} {v.shape} empty')
    # extra: per-cell voltage/temperature spread summary if present
    V = d.get('Voltages_R2'); T = d.get('CellTemp_R'); tt = d.get('Temptime')
    if isinstance(V, np.ndarray) and V.ndim == 2:
        if V.shape[0] < V.shape[1]:
            V = V.T
        dev = (V - np.nanmean(V, 1, keepdims=True)) * 1000
        print('   cells x samples:', V.shape[1], 'x', V.shape[0], '| median spread max-min (mV):', np.nanmedian(np.nanmax(V, 1) - np.nanmin(V, 1)) * 1000,
              '| worst cell idx (mean dev):', int(np.nanargmin(np.nanmean(dev, 0))), np.round(np.nanmin(np.nanmean(dev, 0)), 1), 'mV')
    if isinstance(T, np.ndarray) and T.ndim == 2:
        if T.shape[0] < T.shape[1]:
            T = T.T
        print('   temps x samples:', T.shape[1], 'x', T.shape[0], '| T range', np.nanmin(T), np.nanmax(T), '| median spread (C):', np.nanmedian(np.nanmax(T, 1) - np.nanmin(T, 1)))
    if isinstance(tt, np.ndarray):
        tt = tt.ravel()
        print('   time span h:', (tt.max() - tt.min()) / 3600, 'dt median s:', np.median(np.diff(tt)))
