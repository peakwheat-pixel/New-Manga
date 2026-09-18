"""TASK-045 AC ⑩ (TASK-042 R-03) probe: the rewind cost, measured.

The cursor is forward-only, so a band behind it forces ``rewind()`` + a rescan
from row 0. ``visible_tiles`` is ascending, which bounds one
``ensure_viewport`` call to **one** rewind whose rescan stops at the target
band's end — this script records what that costs on a 20000-row page, both for
the solid fixture (filter 0, the fast path) and a Qt-encoded one (libpng's
per-row filters, the realistic path).
"""

from __future__ import annotations

import sys
import tempfile
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from infrastructure.imaging.webtoon_tiles import (  # noqa: E402
    TileGrid,
    TiledPageRasterizer,
)

tmp = Path(tempfile.mkdtemp(prefix="task045-rewind-"))
sys.path.insert(0, str(REPO_ROOT / "tests" / "reading_export"))
from test_webtoon_tiles import write_streaming_png  # noqa: E402

WIDTH, HEIGHT = 400, 20000
source = tmp / "long.png"
write_streaming_png(source, WIDTH, HEIGHT)


def fresh(name: str) -> TiledPageRasterizer:
    """A rasterizer with its own cache directory, so nothing is a file hit."""
    rasterizer = TiledPageRasterizer(
        source,
        cache_dir=tmp / f"tiles-{name}",
        tile_height=800,
        overlap=64,
        prefetch=0,
    )
    reader = rasterizer._reader
    counts = {"rewinds": 0}
    original = reader.rewind

    def counting() -> None:
        counts["rewinds"] += 1
        original()

    reader.rewind = counting
    rasterizer._probe_rewinds = counts
    return rasterizer


print("== AC 10: rewind cost on a 400x20000 page (tile_height=800, overlap=64) ==")
print("grid tiles:", TileGrid(WIDTH, HEIGHT, tile_height=800, overlap=64).tile_count)

rasterizer = fresh("sweep")
started = time.monotonic()
rasterizer.ensure_viewport(0, HEIGHT)  # full forward sweep: 25 tiles, no rewind
full_scan = time.monotonic() - started
print(
    f"  forward sweep of the whole page (25 tiles): {full_scan:.3f}s"
    f" rewinds={rasterizer._probe_rewinds['rewinds']}"
)

rasterizer = fresh("jump")
rasterizer.ensure_viewport(0, 800)  # cursor at 800; tile 15 is ahead
started = time.monotonic()
rasterizer.ensure_viewport(12000, 12800)
forward_jump = time.monotonic() - started
print(
    f"  forward jump to row 12000 (cursor 800 -> 12800): {forward_jump:.3f}s"
    f" rewinds={rasterizer._probe_rewinds['rewinds']}"
)

rasterizer = fresh("zero")
rasterizer.ensure_viewport(12000, 12800)  # cursor at 12800
started = time.monotonic()
rasterizer.ensure_viewport(0, 800)  # one rewind + rescan to row 800
rewind_to_zero = time.monotonic() - started
print(
    f"  rewind to row 0 (rescan 800 rows): {rewind_to_zero:.3f}s"
    f" rewinds={rasterizer._probe_rewinds['rewinds']}"
)

rasterizer = fresh("middle")
rasterizer.ensure_viewport(19600, 20000)  # cursor at the page end
started = time.monotonic()
rasterizer.ensure_viewport(11920, 12720)  # one rewind + rescan to row 12720
rewind_middle = time.monotonic() - started
print(
    f"  rewind to row 11920 (rescan 12720 rows): {rewind_middle:.3f}s"
    f" rewinds={rasterizer._probe_rewinds['rewinds']}"
)

print()
print("  cost per rescanned row:")
print(f"    rewind-to-zero  : {rewind_to_zero / 800 * 1e6:.1f} us/row")
print(f"    rewind-to-11920 : {rewind_middle / 12720 * 1e6:.1f} us/row")

# ---------------------------------------------------------------------------
# The production configuration is overlap=64 (src/bootstrap/app.py:547), and
# the decode window starts `overlap` rows *before* the previous window ended,
# so every tile after the first sits behind the cursor. This section measures
# what that costs on a page a real encoder wrote (libpng's per-row filters are
# the realistic unfilter path).
# ---------------------------------------------------------------------------
print()
print("== AC 10 addendum: overlap forces one rewind PER TILE (production overlap=64) ==")
from PySide6.QtGui import QImage  # noqa: E402

qt_width, qt_height = 1600, 8000
raw = bytearray()
for page_y in range(qt_height):
    raw += bytes(((page_y * 7) % 256, (page_y * 13) % 256, (page_y * 29) % 256)) * qt_width
qt_source = tmp / "qt-page.png"
qt_image = QImage(bytes(raw), qt_width, qt_height, qt_width * 3, QImage.Format.Format_RGB888)
assert qt_image.save(str(qt_source), "PNG", 1)


def qt_fresh(name: str, tile_height: int = 4000) -> TiledPageRasterizer:
    rasterizer = TiledPageRasterizer(
        qt_source,
        cache_dir=tmp / f"qt-tiles-{name}",
        tile_height=tile_height,
        overlap=64,
        prefetch=0,
    )
    reader = rasterizer._reader
    counts = {"rewinds": 0}
    original = reader.rewind

    def counting() -> None:
        counts["rewinds"] += 1
        original()

    reader.rewind = counting
    rasterizer._probe_rewinds = counts
    return rasterizer


one = qt_fresh("one")
started = time.monotonic()
one.ensure_viewport(0, 4000)  # tile 0: no rewind
tile0 = time.monotonic() - started
print(
    f"  1600x8000 Qt-encoded, tile 0 only (4000 rows): {tile0:.3f}s"
    f" rewinds={one._probe_rewinds['rewinds']}"
)

two = qt_fresh("two")
started = time.monotonic()
two.ensure_viewport(0, 8000)  # tiles 0 and 1: tile 1 rewinds (overlap=64)
tiles01 = time.monotonic() - started
print(
    f"  ... then tile 1 in the SAME call (rescan to 8000 rows): "
    f"{tiles01:.3f}s total rewinds={two._probe_rewinds['rewinds']}"
)
print(
    f"  => a 2-tile viewport costs {tiles01 - tile0:.3f}s of extra rescan for"
    " 64 overlap rows: the fold is quadratic in tiles, not linear"
)
print(
    "  => TASK-042's 'one sequential scan for the whole page' holds only with"
    " overlap=0; with the production overlap every tile re-scans from row 0"
)
