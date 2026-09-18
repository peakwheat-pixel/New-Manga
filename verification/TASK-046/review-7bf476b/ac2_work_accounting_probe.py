"""TASK-046 Review probe (Qoder): AC ② work accounting, not just wall clock.

The author's AC ② table measures wall clock, and the disputed number is the
"extra cost of the second tile in the same call" (4.61-5.22 s after the fix vs
"noise level" as the AC words it). Wall clock alone cannot separate "the second
tile's own linear decode" from "a hidden rescan". This probe therefore counts
the *work* the decoder actually does — rows reconstructed (``_unfilter`` calls)
and cursor rewinds — and adds a measured **floor**: one sequential
``read_band(0, 8000)`` pass plus the two band encodes, i.e. the least work that
can possibly produce tiles 0 and 1 from a fresh reader.

Run against any tree by passing its root:

    python verification/TASK-046/review-7bf476b/ac2_work_accounting_probe.py [tree_root]

The default tree is this worktree (post-fix, default overlap=0); pointing it at
a pre-fix checkout (default overlap=64) measures both sides of the change with
the identical script.
"""

from __future__ import annotations

import sys
import tempfile
import time
from collections import Counter
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parents[3]
ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else DEFAULT_ROOT
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests" / "reading_export"))

from infrastructure.imaging import webtoon_tiles as wt  # noqa: E402
from infrastructure.imaging.webtoon_tiles import (  # noqa: E402
    TileGrid,
    TiledPageRasterizer,
)
from test_webtoon_tiles import write_streaming_png  # noqa: E402

FILTER_NAME = {0: "None", 1: "Sub", 2: "Up", 3: "Average", 4: "Paeth"}


def instrument(reader):
    """Count rewinds and reconstructed rows (per PNG filter type)."""
    stats = {"rewinds": 0, "rows": 0, "filters": Counter()}
    original_rewind = reader.rewind

    def counting_rewind() -> None:
        stats["rewinds"] += 1
        original_rewind()

    reader.rewind = counting_rewind
    original_unfilter = reader._unfilter

    def counting_unfilter(filter_type, cur, prev):
        stats["rows"] += 1
        stats["filters"][filter_type] += 1
        return original_unfilter(filter_type, cur, prev)

    reader._unfilter = counting_unfilter
    return stats


def fresh(name, source_path, tile_height, root_tmp, **kwargs):
    rasterizer = TiledPageRasterizer(
        source_path,
        cache_dir=root_tmp / f"tiles-{name}",
        tile_height=tile_height,
        prefetch=0,
        **kwargs,
    )
    stats = instrument(rasterizer._reader)
    return rasterizer, stats


def report(label, elapsed, stats, kept_rows=None):
    filters = ", ".join(
        f"{FILTER_NAME[t]}:{n}" for t, n in sorted(stats["filters"].items())
    )
    kept = "" if kept_rows is None else f" kept_rows={kept_rows}"
    print(
        f"  {label}: {elapsed:.3f}s rewinds={stats['rewinds']}"
        f" rows_reconstructed={stats['rows']}{kept} filters[{filters}]"
    )


print(f"== tree: {ROOT} | TileGrid default overlap={TileGrid(400, 20000, tile_height=800).overlap} ==")
root_tmp = Path(tempfile.mkdtemp(prefix="task046-review-a2-"))

# ---------------------------------------------------------------- 1. full sweep
WIDTH, HEIGHT = 400, 20000
long_source = root_tmp / "long.png"
write_streaming_png(long_source, WIDTH, HEIGHT)
tiles = TileGrid(WIDTH, HEIGHT, tile_height=800).tile_count
rasterizer, stats = fresh("sweep", long_source, 800, root_tmp)
started = time.monotonic()
rasterizer.ensure_viewport(0, HEIGHT)
report(f"400x20000 full sweep ({tiles} tiles)", time.monotonic() - started, stats, HEIGHT)

# ------------------------------------------------- 2/3. Qt page, tile 0 / 0+1
from PySide6.QtGui import QImage  # noqa: E402

qt_width, qt_height = 1600, 8000
raw = bytearray()
for page_y in range(qt_height):
    raw += bytes(((page_y * 7) % 256, (page_y * 13) % 256, (page_y * 29) % 256)) * qt_width
qt_source = root_tmp / "qt-page.png"
qt_image = QImage(bytes(raw), qt_width, qt_height, qt_width * 3, QImage.Format.Format_RGB888)
assert qt_image.save(str(qt_source), "PNG", 1)
qt_bytes = qt_source.read_bytes()
print(f"== 1600x8000 Qt-encoded page: {len(qt_bytes) / 1e6:.1f} MB file ==")

one, one_stats = fresh("qt-one", qt_source, 4000, root_tmp)
started = time.monotonic()
one.ensure_viewport(0, 4000)
tile0 = time.monotonic() - started
report("tile 0 only (rows 0-4000)", tile0, one_stats, 4000)

two, two_stats = fresh("qt-two", qt_source, 4000, root_tmp)
started = time.monotonic()
two.ensure_viewport(0, 8000)
tiles01 = time.monotonic() - started
report("tiles 0+1 in one call (rows 0-8000)", tiles01, two_stats, 8000)
print(
    f"  => measured extra for the second tile: {tiles01 - tile0:.3f}s"
    f" | extra rewinds={two_stats['rewinds'] - one_stats['rewinds']}"
    f" | extra rows_reconstructed={two_stats['rows'] - one_stats['rows']}"
)

# ------------------------------------------------------------- 4. measured floor
reader = wt.StreamingPngReader(qt_bytes)
floor_stats = instrument(reader)
started = time.monotonic()
band8000, _w, _h, _c = reader.read_band(0, 8000)
decode8000 = time.monotonic() - started
report("FLOOR a: read_band(0,8000) one sequential pass", decode8000, floor_stats)

reader = wt.StreamingPngReader(qt_bytes)
floor4_stats = instrument(reader)
started = time.monotonic()
band4000 = reader.read_band(0, 4000)[0]
decode4000 = time.monotonic() - started
report("FLOOR b: read_band(0,4000) one sequential pass", decode4000, floor4_stats)

stride = qt_width * 3
started = time.monotonic()
encoded = wt._encode_png(band4000, qt_width, 4000, 3)
encode_one = time.monotonic() - started
print(f"  FLOOR c: _encode_png(4000 rows) {encode_one:.3f}s -> {len(encoded) / 1e6:.1f} MB")
del band8000, band4000, encoded
floor = decode8000 + 2 * encode_one
print(
    f"  FLOOR for tiles 0+1 (one 8000-row pass + two band encodes): {floor:.3f}s"
    f" | measured {tiles01:.3f}s -> ratio {tiles01 / floor:.3f}"
)
print(
    f"  FLOOR for tile 0 only (one 4000-row pass + one encode): {decode4000 + encode_one:.3f}s"
    f" | measured {tile0:.3f}s -> ratio {tile0 / (decode4000 + encode_one):.3f}"
)
print(
    f"  unavoidable work of the SECOND tile (rows 4000-8000 + its encode):"
    f" {decode8000 - decode4000 + encode_one:.3f}s"
    f" | measured extra {tiles01 - tile0:.3f}s"
)

# ------------------------------------------- 5. rows 4000-8000 in isolation
reader = wt.StreamingPngReader(qt_bytes)
band1_stats = instrument(reader)
started = time.monotonic()
reader.read_band(4000, 4000)  # skips (still reconstructs) rows 0-4000 first
band1 = time.monotonic() - started
report("rows 4000-8000 reached via read_band(4000,4000)", band1, band1_stats)
band0_stats_rows = floor4_stats["rows"]
print(
    f"  per-row cost band0 (rows 0-4000): {(decode4000) / max(1, band0_stats_rows) * 1e3:.3f} ms"
    f" | band1 (rows 0-8000 pass): {(decode8000) / max(1, floor_stats['rows']) * 1e3:.3f} ms"
)

# ---------------------------------------------------- 6. overlap=64 (pre-fix shape)
control, control_stats = fresh("control", qt_source, 4000, root_tmp, overlap=64)
started = time.monotonic()
control.ensure_viewport(0, 8000)
control_time = time.monotonic() - started
report("CONTROL tiles 0+1 with explicit overlap=64", control_time, control_stats, 8000)
print(
    f"  => overlap=64 costs {control_stats['rows'] - two_stats['rows']}"
    f" extra reconstructed rows vs this tree's default"
    f" ({control_time / max(0.001, tiles01):.2f}x wall clock of the default call)"
)
