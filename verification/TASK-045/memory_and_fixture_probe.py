"""TASK-045 probes: memory composition (AC ⑨) and the Qt-encoded oversized
fixture cost (AC ⑪).

Prints, per fixture, the numbers the docstrings now have to state honestly:

- resident compressed source,
- the largest IDAT chunk (the reader holds the current chunk plus the
  decompressor's unconsumed tail, so that term counts twice),
- the decode band,
- the measured Python-heap peak added by one band read,

and times each phase of the 1600x20000 Qt-encoded fixture so the test can stay
cheap without weakening what it covers.
"""

from __future__ import annotations

import random
import struct
import sys
import tempfile
import time
import tracemalloc
import zlib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from infrastructure.imaging.streaming_png import StreamingPngReader  # noqa: E402
from infrastructure.imaging.webtoon_tiles import TiledPageRasterizer  # noqa: E402

tmp = Path(tempfile.mkdtemp(prefix="task045-probe-"))
WIDTH, HEIGHT = 400, 10000


def chunk(tag: bytes, data: bytes) -> bytes:
    return (
        struct.pack(">I", len(data))
        + tag
        + data
        + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    )


def write_noise_png(path: Path, width: int, height: int, *, rows_per_chunk: int) -> None:
    """Incompressible payload, written as one or many IDAT chunks."""
    stride = width * 3 + 1
    payload = bytearray(random.Random(20260918).randbytes(stride * height))
    payload[0::stride] = b"\x00" * height
    with open(path, "wb") as handle:
        handle.write(b"\x89PNG\r\n\x1a\n")
        handle.write(chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)))
        compressor = zlib.compressobj(1)
        if rows_per_chunk >= height:
            handle.write(chunk(b"IDAT", compressor.compress(bytes(payload))))
            handle.write(chunk(b"IDAT", compressor.flush()))
        else:
            row_bytes = stride
            for start in range(0, height, rows_per_chunk):
                block = bytes(payload[start * row_bytes : (start + rows_per_chunk) * row_bytes])
                data = compressor.compress(block)
                if data:
                    handle.write(chunk(b"IDAT", data))
            handle.write(chunk(b"IDAT", compressor.flush()))
        handle.write(chunk(b"IEND", b""))


def max_idat(path: Path) -> int:
    data = path.read_bytes()
    offset, largest = 8, 0
    while offset + 8 <= len(data):
        length = struct.unpack_from(">I", data, offset)[0]
        if data[offset + 4 : offset + 8] == b"IDAT":
            largest = max(largest, length)
        offset += 12 + length
    return largest


print("== AC 9: memory composition per IDAT chunking ==")
for label, rows_per_chunk in (("single IDAT (whole payload)", HEIGHT), ("1000-row IDATs", 1000)):
    source = tmp / f"noise-{rows_per_chunk}.png"
    write_noise_png(source, WIDTH, HEIGHT, rows_per_chunk=rows_per_chunk)
    source_bytes = source.stat().st_size
    largest = max_idat(source)
    band_bytes = (800 + 64) * WIDTH * 3

    tracemalloc.start()
    rasterizer = TiledPageRasterizer(
        source, cache_dir=tmp / f"tiles-{rows_per_chunk}", tile_height=800, overlap=64
    )
    construction_peak = tracemalloc.get_traced_memory()[1]
    rasterizer.ensure_viewport(0, 800)
    read_peak = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()

    added = read_peak - source_bytes
    print(f"  {label}:")
    print(f"    source_bytes={source_bytes} largest_idat={largest} band_bytes={band_bytes}")
    print(f"    construction_peak={construction_peak} read_peak={read_peak}")
    print(
        f"    added={added} added/band={added / band_bytes:.2f}x "
        f"2*largest+6*band={2 * largest + 6 * band_bytes}"
    )

print()
print("== AC 11: phase costs of the Qt-encoded 1600x20000 fixture ==")
from PySide6.QtGui import QImage  # noqa: E402

width, height = 1600, 20000
started = time.monotonic()
payload = bytearray()
for page_y in range(height):
    payload += (
        bytes(((page_y * 7) % 256, (page_y * 13) % 256, (page_y * 29) % 256)) * width
    )
raw = bytes(payload)
print(f"  build raw ({len(raw) / 1e6:.0f} MB): {time.monotonic() - started:.2f}s")

started = time.monotonic()
image = QImage(raw, width, height, width * 3, QImage.Format.Format_RGB888)
path = tmp / "qt-large.png"
assert image.save(str(path), "PNG", 1)
print(f"  QImage.save(quality=1): {time.monotonic() - started:.2f}s -> {path.stat().st_size / 1e6:.1f} MB")

started = time.monotonic()
reader = StreamingPngReader(path.read_bytes())
band, bw, bh, bc = reader.read_band(12000, 2000)
print(f"  streaming band read (2000 rows): {time.monotonic() - started:.2f}s")

started = time.monotonic()
qt = QImage(str(path)).convertToFormat(QImage.Format.Format_RGB888)
bits = qt.constBits()
stride = qt.bytesPerLine()
expected = bytes(bits[12000 * stride : 14000 * stride])
print(f"  Qt load + convert + slice: {time.monotonic() - started:.2f}s identical={band == expected}")
print(f"  qt-encoded IDAT largest chunk: {max_idat(path)}")
