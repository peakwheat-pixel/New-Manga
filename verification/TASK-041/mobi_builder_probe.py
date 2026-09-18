"""Probe: can a hand-built picture MOBI be extracted by mobi 0.4.1?

Builds a minimal PalmDB/MOBI container (KF7, no DRM, no compression):
record0 = PalmDoc header + MOBI header (232-byte variant, firstImageIndex=2),
record1 = html, records 2..3 = JPEG images. Then runs mobi.extract and
prints the extracted tree so the adapter can pin its contract.
"""

from __future__ import annotations

import struct
import sys
import tempfile
from pathlib import Path


def make_jpeg(width: int, height: int, bgr: tuple[int, int, int]) -> bytes:
    from PySide6.QtCore import QBuffer, QIODevice
    from PySide6.QtGui import QColor, QImage

    image = QImage(width, height, QImage.Format.Format_RGB32)
    image.fill(QColor(*bgr))
    buffer = QBuffer()
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    ok = image.save(buffer, "JPG")
    assert ok, "jpeg encode failed"
    return bytes(buffer.data())


def record0(html_len: int, unique_id: int) -> bytes:
    """One 248-byte record0 laid out the way mobi 0.4.1 (kindleunpack)
    reads it: 16-byte PalmDoc header + 232-byte MOBI header (0xF4 ncxidx
    included, set to 0xFFFFFFFF = no NCX index)."""
    buf = bytearray(0x10 + 0xE8)
    struct.pack_into(">H", buf, 0x00, 1)  # compression: none
    struct.pack_into(">H", buf, 0x02, 0)  # fill0
    struct.pack_into(">I", buf, 0x04, html_len)
    struct.pack_into(">H", buf, 0x08, 1)  # text records
    struct.pack_into(">H", buf, 0x0A, 4096)  # max section size
    struct.pack_into(">H", buf, 0x0C, 0)  # crypto type: none
    struct.pack_into(">H", buf, 0x0E, 0)  # fill1
    buf[0x10:0x14] = b"MOBI"
    struct.pack_into(">I", buf, 0x14, 0xE8)  # MOBI header length
    struct.pack_into(">I", buf, 0x18, 2)  # type: book
    struct.pack_into(">I", buf, 0x1C, 65001)  # codepage: utf-8
    struct.pack_into(">I", buf, 0x20, unique_id)
    struct.pack_into(">I", buf, 0x24, 6)  # version
    struct.pack_into(">i", buf, 0x28, -1)  # meta orth index: none
    struct.pack_into(">i", buf, 0x2C, -1)  # meta infl index: none
    for off in range(0x30, 0x50, 4):
        struct.pack_into(">i", buf, off, -1)  # extra indexes: none
    struct.pack_into(">I", buf, 0x50, 2)  # first non-text record
    struct.pack_into(">I", buf, 0x54, 0)  # title offset
    struct.pack_into(">I", buf, 0x58, 0)  # title length
    struct.pack_into(">I", buf, 0x5C, 9)  # language code: en
    struct.pack_into(">i", buf, 0x60, -1)  # dict in language: none
    struct.pack_into(">i", buf, 0x64, -1)  # dict out language: none
    struct.pack_into(">I", buf, 0x68, 6)  # min version
    struct.pack_into(">I", buf, 0x6C, 2)  # first resource record: the first image
    struct.pack_into(">I", buf, 0x80, 0)  # exth flags: none
    struct.pack_into(">i", buf, 0xA8, -1)  # drm offset: none
    struct.pack_into(">I", buf, 0xAC, 0)  # drm count
    struct.pack_into(">I", buf, 0xB0, 0)  # drm size
    struct.pack_into(">I", buf, 0xB4, 0)  # drm flags
    struct.pack_into(">H", buf, 0xC0, 0)  # first content record
    struct.pack_into(">H", buf, 0xC2, 1)  # last content record
    struct.pack_into(">i", buf, 0xC8, -1)  # fcis offset: none
    struct.pack_into(">i", buf, 0xD0, -1)  # flis offset: none
    struct.pack_into(">i", buf, 0xF4, -1)  # NCX index: none
    return bytes(buf)


def build_picture_mobi(images: list[bytes]) -> tuple[bytes, bytes]:
    html = (
        "<html><head></head><body>"
        + "".join(
            f'<div><img recindex="{i:05d}"></div>'
            for i in range(1, len(images) + 1)
        )
        + "</body></html>"
    ).encode("utf-8")
    records = [record0(len(html), 12345), html] + images
    return pack_pdb(records), records[1]


def pack_pdb(records: list[bytes]) -> bytes:
    header = bytearray()
    name = b"probe manga".ljust(32, b"\x00")
    header += name
    header += struct.pack(">H", 0)  # attributes
    header += struct.pack(">H", 0)  # version
    header += struct.pack(">III", 0, 0, 0)  # creation/modification/backup
    header += struct.pack(">I", 0)  # modification number
    header += struct.pack(">I", 0)  # app info id
    header += struct.pack(">I", 0)  # sort info id
    header += b"BOOK"  # type
    header += b"MOBI"  # creator
    header += struct.pack(">I", 0)  # unique id seed
    header += struct.pack(">I", 0)  # next record list id
    header += struct.pack(">H", len(records))
    offset = 78 + 8 * len(records) + 2
    entries = bytearray()
    for index, record in enumerate(records):
        entries += struct.pack(">I", offset)
        entries += struct.pack(">B", 0)
        entries += struct.pack(">I", index)[1:]
        offset += len(record)
    header += entries
    header += struct.pack(">H", 0)  # padding
    return bytes(header) + b"".join(records)


def main() -> int:
    import mobi

    images = [make_jpeg(8, 6, (255, 0, 0)), make_jpeg(9, 7, (0, 255, 0))]
    data, html = build_picture_mobi(images)
    workdir = Path(tempfile.mkdtemp(prefix="mobi-probe-"))
    source = workdir / "probe.mobi"
    source.write_bytes(data)
    print(f"container {len(data)} bytes -> {source}")
    try:
        tempdir, extracted = mobi.extract(str(source))
    except Exception as error:  # noqa: BLE001 - probe reports the raw failure
        print(f"extract FAILED: {type(error).__name__}: {error}")
        for line in Path(sys.argv[0]).read_text(encoding="utf-8").splitlines()[:3]:
            print(line)
        return 1
    print(f"extract returned tempdir={tempdir} path={extracted}")
    root = Path(tempdir)
    for path in sorted(root.rglob("*")):
        if path.is_file():
            print(f"  {path.relative_to(root)}  ({path.stat().st_size} B)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
