"""TASK-062 AC ④ evidence: show the Qt-encoded fixture really carries adaptive
row filters (so the new overlap test is not vacuous), and that overlap 0/64
still yields byte-identical tile files with a page-equal union."""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tests" / "reading_export"))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from test_webtoon_tiles import (  # noqa: E402
    png_row_filter_types,
    qt_rows,
    write_qt_encoded_png,
)
from infrastructure.imaging.webtoon_tiles import TiledPageRasterizer  # noqa: E402

tmp = Path(tempfile.mkdtemp(prefix="t062-filter-"))
width, height = 600, 2100
source = tmp / "qt-encoded.png"
write_qt_encoded_png(source, width, height)
filters = sorted(png_row_filter_types(source))
print("qt-encoded page row filter types:", filters)
print("all filter-0?", filters == [0])

zero = TiledPageRasterizer(source, cache_dir=tmp / "t0", tile_height=800)
over = TiledPageRasterizer(source, cache_dir=tmp / "t64", tile_height=800, overlap=64)
stitched = []
identical = []
for tile in zero.grid.tiles:
    a = zero.tile_file(tile.index).read_bytes()
    b = over.tile_file(tile.index).read_bytes()
    identical.append(a == b)
    rows, tile_width, tile_height = qt_rows(zero.tile_file(tile.index))
    print(f"tile {tile.index}: file_bytes_equal={a == b} declared={tile.content_height}"
          f" file_height={tile_height} width={tile_width}")
    stitched.extend(rows)
page_rows, page_width, _ = qt_rows(source)
print("union == whole page:", stitched == page_rows, "page_width:", page_width)
print("ALL BYTE-IDENTICAL:", all(identical), "TILES:", len(identical))
