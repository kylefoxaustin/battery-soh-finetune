"""Extract per-vehicle .rar members from the split Changan archive RAW_DATA.z01 (volume 0) + RAW_DATA.zip
(volume 1, holds the central directory). Works with only RAW_DATA.zip present: then only members whose local
header starts on volume 1 are recoverable. A member that starts near the end of .z01 continues at the start of
.zip; reads cross the boundary. Streams in 16 MB chunks, verifies each member's CRC-32.

Usage: python data/changan_extract.py RAW_DATA.zip data/raw/changan [vin ...]   (no vins = all available)
       (RAW_DATA.z01 is picked up automatically if it sits next to RAW_DATA.zip)
"""
import os
import re
import struct
import sys
import zlib


def central_directory(path):
    size = os.path.getsize(path)
    with open(path, "rb") as f:
        f.seek(max(0, size - 65558 - 56))
        tail = f.read()
        j = tail.rfind(b"PK\x06\x06")
        _, _, _, _, disk, _, _, _, cd_size, cd_off = struct.unpack("<IQHHIIQQQQ", tail[j:j + 56])
        f.seek(cd_off)
        cd = f.read(cd_size)
    out, p = [], 0
    while cd[p:p + 4] == b"PK\x01\x02":
        (_, _, flag, meth, _, _, crc, csz, usz, nl, el, cl, dstart, _, _, lho) = struct.unpack("<HHHHHHIIIHHHHHII", cd[p + 4:p + 46])
        name = cd[p + 46:p + 46 + nl].decode()
        extra, q = cd[p + 46 + nl:p + 46 + nl + el], 0
        while q < len(extra):
            hid, hl = struct.unpack("<HH", extra[q:q + 4])
            body, k = extra[q + 4:q + 4 + hl], 0
            if hid == 1:
                if usz == 0xFFFFFFFF:
                    usz = struct.unpack("<Q", body[k:k + 8])[0]; k += 8
                if csz == 0xFFFFFFFF:
                    csz = struct.unpack("<Q", body[k:k + 8])[0]; k += 8
                if lho == 0xFFFFFFFF:
                    lho = struct.unpack("<Q", body[k:k + 8])[0]; k += 8
                if dstart == 0xFFFF:
                    dstart = struct.unpack("<I", body[k:k + 4])[0]
            q += 4 + hl
        out.append({"name": name, "disk": dstart, "lho": lho, "csz": csz, "usz": usz, "meth": meth, "crc": crc, "flag": flag})
        p += 46 + nl + el + cl
    return out, disk


class Volumes:
    """Sequential reader over split-zip volumes [.z01, .zip] addressed as (disk, offset)."""

    def __init__(self, paths):
        self.paths = paths
        self.sizes = [os.path.getsize(p) for p in paths]

    def open_at(self, disk, off):
        self.disk, self.f = disk, open(self.paths[disk], "rb")
        self.f.seek(off)

    def read(self, n):
        b = self.f.read(n)
        while len(b) < n and self.disk + 1 < len(self.paths):
            self.f.close()
            self.disk += 1
            self.f = open(self.paths[self.disk], "rb")
            b += self.f.read(n - len(b))
        return b

    def close(self):
        self.f.close()


def extract(vols, ent, dest):
    vols.open_at(ent["disk"], ent["lho"])
    try:
        h = vols.read(30)
        assert h[:4] == b"PK\x03\x04", "bad local header"
        nl, el = struct.unpack("<HH", h[26:30])
        vols.read(nl + el)
        assert ent["meth"] in (0, 8), f"unsupported method {ent['meth']}"
        d = zlib.decompressobj(-15) if ent["meth"] == 8 else None
        left, crc = ent["csz"], 0
        with open(dest + ".part", "wb") as o:
            while left:
                b = vols.read(min(left, 16 << 20))
                assert b, "unexpected end of archive"
                left -= len(b)
                if d:
                    b = d.decompress(b)
                crc = zlib.crc32(b, crc)
                o.write(b)
            if d:
                b = d.flush(); crc = zlib.crc32(b, crc); o.write(b)
    finally:
        vols.close()
    assert crc == ent["crc"], f"CRC mismatch for {ent['name']}"
    os.replace(dest + ".part", dest)


if __name__ == "__main__":
    zp, out = sys.argv[1], sys.argv[2]
    want = set(sys.argv[3:])
    os.makedirs(out, exist_ok=True)
    ents, this_disk = central_directory(zp)
    z01 = zp[:-4] + ".z01"
    paths = ([z01] if os.path.exists(z01) else []) + [zp]
    first = this_disk - (len(paths) - 1)  # disk number of paths[0]
    vols = Volumes(paths)
    avail = [dict(e, disk=e["disk"] - first) for e in ents if e["name"].endswith(".rar") and e["disk"] >= first]
    print(f"{len(paths)} volume(s) present; {len(avail)} of {sum(e['name'].endswith('.rar') for e in ents)} members recoverable", flush=True)
    for e in avail:
        vin = re.findall(r"vin(\d+)", e["name"])[0]
        if want and vin not in want:
            continue
        dest = os.path.join(out, f"vin{vin}.rar")
        if os.path.exists(dest):
            continue
        extract(vols, e, dest)
        print(f"vin{vin}: {e['usz'] / 1e6:.0f} MB, CRC ok", flush=True)
