"""Minimal decoder for MATLAB datetime objects in v7.3 MAT files (#subsystem#/MCOS, metadata v4).
obj_cells(f) -> dict object_id -> FileWrapper cell index of its 'data' property (ms since 1970, UTC-naive)."""
import h5py, numpy as np

def obj_cells(f):
    refs = f['#subsystem#/MCOS'][()].ravel()
    meta = f[refs[0]][()].ravel().astype(np.uint8).tobytes()
    u = np.frombuffer(meta[:40], '<u4'); off = u[2:]
    p = 40; names = []
    for _ in range(u[1]):
        e = meta.index(b'\0', p); names.append(meta[p:e].decode()); p = e + 1
    info = np.frombuffer(meta[off[2]:off[3]], '<u4').reshape(-1, 6)       # [class, 0, 0, type1, type2, dep]
    blk = meta[off[3]:off[4]]
    # type2 property blocks, sequential: n, then n*(name_idx, flag, value), padded to 8 bytes; first block is a dummy
    blocks = []; q = 0
    while q < len(blk):
        n = int(np.frombuffer(blk[q:q + 4], '<u4')[0]); trip = np.frombuffer(blk[q + 4:q + 4 + 12 * n], '<u4').reshape(n, 3)
        blocks.append(trip); q += 4 + 12 * n; q += (-q) % 8
    data_idx = names.index('data') + 1                                     # name indices are 1-based
    out = {}
    for oid in range(1, len(info)):
        t2 = int(info[oid, 4])
        if t2 == 0 or t2 >= len(blocks): continue
        for name, flag, val in blocks[t2]:
            if name == data_idx and flag == 1:
                out[oid] = int(val) + 2                                    # cell index (cells 0,1 = metadata, empty)
    return refs, out, names, len(info), len(blocks)

def dt_ms(f, refs, cells, ref_attr_arr):
    """ref_attr_arr: the (1,6) uint32 array stored in a datetime field -> np.array of ms"""
    oid = int(ref_attr_arr.ravel()[4])
    return f[refs[cells[oid]]][()].ravel()
