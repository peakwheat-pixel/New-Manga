"""TASK-046 Review probe (Qoder): AC ① byte identity on *filtered* pages.

The two committed AC ① fixtures (`row pattern`, `noise`) are both hand-written
**filter 0** encodings, so the reproducible proof never reconstructs a page
whose rows actually carry filter context (Sub/Up/Average/Paeth) — which is what
production pages are. The code-level argument says the streaming reader always
reconstructs rows in order and therefore always has its own previous row, so
the decode window's overlap can never feed a pixel; this probe tests that on
the filter classes the shipped test does not reach.

Run: python verification/TASK-046/review-7bf476b/ac1_filtered_pages_probe.py [tree_root]
"""

from __future__ import annotations

import sys
import tempfile
from collections import Counter
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parents[3]
ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else DEFAULT_ROOT
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests" / "reading_export"))

from infrastructure.imaging.webtoon_tiles import (  # noqa: E402
    TiledPageRasterizer,
)
from test_streaming_png import build_png, make_raw_rows  # noqa: E402
from test_webtoon_tiles import qt_rows  # noqa: E402
from PySide6.QtGui import QImage  # noqa: E402

WIDTH, HEIGHT, TILE = 400, 2000, 800
tmp = Path(tempfile.mkdtemp(prefix="task046-review-a1-"))


def filter_histogram(path: Path) -> Counter:
    """Filter byte per row, read straight out of the file's IDAT stream."""
    import zlib

    data = path.read_bytes()
    payload = b""
    offset = 8
    while offset + 8 <= len(data):
        length = int.from_bytes(data[offset : offset + 4], "big")
        tag = data[offset + 4 : offset + 8]
        body = data[offset + 8 : offset + 8 + length]
        if tag == b"IDAT":
            payload += body
        elif tag == b"IEND":
            break
        offset += 12 + length
    raw = zlib.decompress(payload)
    stride = WIDTH * 3 + 1
    return Counter(raw[i * stride] for i in range(HEIGHT))


def compare(label: str, source: Path) -> None:
    zero = TiledPageRasterizer(source, cache_dir=tmp / f"{label}-0", tile_height=TILE)
    overlapped = TiledPageRasterizer(
        source, cache_dir=tmp / f"{label}-64", tile_height=TILE, overlap=64
    )
    print(f"-- {label}: file {source.name}, overlap {zero.grid.overlap} vs {overlapped.grid.overlap}")
    identical = True
    stitched: list[bytes] = []
    for tile in zero.grid.tiles:
        a = zero.tile_file(tile.index).read_bytes()
        b = overlapped.tile_file(tile.index).read_bytes()
        if a != b:
            identical = False
            print(f"   tile {tile.index}: DIFFERS ({len(a)} vs {len(b)} bytes)")
        stitched.extend(qt_rows(zero.tile_file(tile.index))[0])
    page = qt_rows(source)[0]
    print(
        f"   byte-identical across all {zero.grid.tile_count} tiles: {identical}"
        f" | stitched == whole page: {stitched == page}"
    )


# (a) hand-encoded Paeth page, high-entropy rows (the most context-dependent filter)
rows = make_raw_rows(WIDTH, HEIGHT, bpp=3, seed=7)
for name, filter_type in (("paeth", 4), ("average", 3), ("up", 2), ("sub", 1)):
    path = tmp / f"{name}.png"
    path.write_bytes(build_png(WIDTH, HEIGHT, rows, bpp=3, filter_type=filter_type))
    compare(name, path)

# (b) a Qt/libpng-encoded page (whatever filters the real encoder picks)
pattern = bytearray()
for page_y in range(HEIGHT):
    pattern += bytes(((page_y * 7) % 256, (page_y * 13) % 256, (page_y * 29) % 256)) * WIDTH
qt_path = tmp / "qt.png"
QImage(bytes(pattern), WIDTH, HEIGHT, WIDTH * 3, QImage.Format.Format_RGB888).save(
    str(qt_path), "PNG", 1
)
print(f"-- qt/libpng page filter histogram: {dict(filter_histogram(qt_path))}")
compare("qt", qt_path)
