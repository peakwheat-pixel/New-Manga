"""TASK-046 AC ② probe: rewind count and wall clock, before vs after.

Same measurement shape as ``verification/TASK-045/rewind_cost_probe.py`` (the
AC ⑩ baseline), with two changes:

- every rasterizer is built with the **default** ``overlap`` (no explicit
  argument), so the same script run against the pre-fix tree (default 64) and
  the post-fix tree (default 0) measures the semantic change directly;
- an explicit ``overlap=64`` control section stays at the end, to show the
  overlap machinery itself is retained (the fix removes its *production use*,
  not the parameter).

Sections (each on a fresh rasterizer with its own cache dir, so nothing is a
file hit):

1. 400x20000 (tile_height=800) full forward sweep — the O(tiles^2) fold:
   pre-fix = 24 rewinds (tiles-1); post-fix = 0.
2. 1600x8000 Qt-encoded page, tile 0 only vs tiles 0+1 in one call — the
   extra rescan TASK-045 measured at ~8.9-9.7 s; post-fix = noise level.
3. explicit overlap=64 control: the per-tile rewind behaviour is unchanged.

Run: python verification/TASK-046/rewind_cost_probe.py
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

tmp = Path(tempfile.mkdtemp(prefix="task046-rewind-"))
sys.path.insert(0, str(REPO_ROOT / "tests" / "reading_export"))
from test_webtoon_tiles import write_streaming_png  # noqa: E402

WIDTH, HEIGHT = 400, 20000
source = tmp / "long.png"
write_streaming_png(source, WIDTH, HEIGHT)


def fresh(name: str, source_path, tile_height: int, **kwargs) -> TiledPageRasterizer:
    """A rasterizer with its own cache directory, so nothing is a file hit.

    ``overlap`` is intentionally NOT passed unless the caller does: the
    default is the production semantic this task moves (64 -> 0).
    """
    rasterizer = TiledPageRasterizer(
        source_path,
        cache_dir=tmp / f"tiles-{name}",
        tile_height=tile_height,
        prefetch=0,
        **kwargs,
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


print(
    "== TASK-046 AC 2: default-overlap full sweep, 400x20000"
    f" (tile_height=800, default overlap={TileGrid(WIDTH, HEIGHT, tile_height=800).overlap}) =="
)
print("grid tiles:", TileGrid(WIDTH, HEIGHT, tile_height=800).tile_count)

rasterizer = fresh("sweep", source, 800)
started = time.monotonic()
rasterizer.ensure_viewport(0, HEIGHT)  # full forward sweep: 25 tiles
full_scan = time.monotonic() - started
print(
    f"  full sweep: {full_scan:.3f}s"
    f" rewinds={rasterizer._probe_rewinds['rewinds']}"
)

print()
print(
    "== TASK-046 AC 2: 1600x8000 Qt-encoded, default overlap, tile 0 vs tiles 0+1 =="
)
from PySide6.QtGui import QImage  # noqa: E402

qt_width, qt_height = 1600, 8000
raw = bytearray()
for page_y in range(qt_height):
    raw += bytes(((page_y * 7) % 256, (page_y * 13) % 256, (page_y * 29) % 256)) * qt_width
qt_source = tmp / "qt-page.png"
qt_image = QImage(bytes(raw), qt_width, qt_height, qt_width * 3, QImage.Format.Format_RGB888)
assert qt_image.save(str(qt_source), "PNG", 1)

one = fresh("qt-one", qt_source, 4000)
started = time.monotonic()
one.ensure_viewport(0, 4000)  # tile 0
tile0 = time.monotonic() - started
print(
    f"  tile 0 only (4000 rows): {tile0:.3f}s"
    f" rewinds={one._probe_rewinds['rewinds']}"
)

two = fresh("qt-two", qt_source, 4000)
started = time.monotonic()
two.ensure_viewport(0, 8000)  # tiles 0 and 1 in the SAME call
tiles01 = time.monotonic() - started
print(
    f"  tiles 0+1 in one call: {tiles01:.3f}s"
    f" rewinds={two._probe_rewinds['rewinds']}"
)
print(
    f"  => extra cost of the second tile in the same call:"
    f" {tiles01 - tile0:.3f}s (TASK-045 baseline: ~8.9-9.7s of pure rescan)"
)

print()
print("== control: explicit overlap=64 keeps the per-tile rewind (machinery retained) ==")
control = fresh("control", qt_source, 4000, overlap=64)
started = time.monotonic()
control.ensure_viewport(0, 8000)
control_time = time.monotonic() - started
print(
    f"  tiles 0+1 with overlap=64: {control_time:.3f}s"
    f" rewinds={control._probe_rewinds['rewinds']}"
)
