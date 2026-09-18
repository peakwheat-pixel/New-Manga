"""TASK-046 Review probe (Qoder): AC ⑤ behavioural discrimination on any tree.

The shipped AC ⑤ log shows 4 failures on the pre-fix tree, but every one of
them trips on ``assert grid.overlap == 0`` *before* reaching the behavioural
assertions, so that log alone cannot say whether "the default sweep is one
sequential scan" is itself discriminating, nor whether the byte-identity body
really is only a pinned property. This probe skips the default-value asserts
and measures the behaviour directly, on whichever tree it points at.

Run: python verification/TASK-046/review-7bf476b/ac5_behaviour_probe.py [tree_root]
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parents[3]
ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else DEFAULT_ROOT
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests" / "reading_export"))

from infrastructure.imaging.webtoon_tiles import (  # noqa: E402
    TileGrid,
    TiledPageRasterizer,
)
from test_webtoon_tiles import qt_rows, write_row_pattern_png  # noqa: E402

tmp = Path(tempfile.mkdtemp(prefix="task046-review-a5-"))
width, height, tile = 400, 4000, 800
source = tmp / "sweep.png"
write_row_pattern_png(source, width, height)
default_overlap = TileGrid(width, height, tile_height=tile).overlap
print(f"== tree: {ROOT}")
print(f"== default overlap on this tree: {default_overlap}")


def swept_rewinds(rasterizer) -> int:
    counter = {"n": 0}
    reader = rasterizer._reader
    original = reader.rewind

    def counting() -> None:
        counter["n"] += 1
        original()

    reader.rewind = counting
    rasterizer.ensure_viewport(0, height)
    return counter["n"]


# 1. the behaviour the new test asserts, WITHOUT the default-value assert
on_default = TiledPageRasterizer(source, cache_dir=tmp / "sweep-default", tile_height=tile)
rewinds = swept_rewinds(on_default)
print(
    f"-- full sweep at this tree's default overlap: rewinds={rewinds}"
    f" -> test's 'rewinds == 0' would {'PASS' if rewinds == 0 else 'FAIL'}"
)

# 2. the byte-identity body WITHOUT the default-value asserts (pinned property?)
zero = TiledPageRasterizer(source, cache_dir=tmp / "cmp-0", tile_height=tile)
sixty_four = TiledPageRasterizer(
    source, cache_dir=tmp / "cmp-64", tile_height=tile, overlap=64
)
identical = all(
    zero.tile_file(t.index).read_bytes() == sixty_four.tile_file(t.index).read_bytes()
    for t in zero.grid.tiles
)
stitched: list[bytes] = []
for t in zero.grid.tiles:
    stitched.extend(qt_rows(zero.tile_file(t.index))[0])
page = qt_rows(source)[0]
print(
    f"-- overlap 0 vs 64 tile bytes identical: {identical}"
    f" | stitched == whole page: {stitched == page}"
    f" -> byte-identity body {'PASSES (pinned, as declared)' if identical else 'FAILS (would be discriminating)'}"
)

# 3. the explicit-overlap control branch the new test pins
on_64 = TiledPageRasterizer(source, cache_dir=tmp / "sweep-64", tile_height=tile, overlap=64)
print(
    f"-- full sweep with explicit overlap=64: rewinds={swept_rewinds(on_64)}"
    " (test pins == 4)"
)
