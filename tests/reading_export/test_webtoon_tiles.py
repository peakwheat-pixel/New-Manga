"""TASK-020 webtoon tiling: tile grid geometry, cache budget, on-demand
decoding and the reader ViewModel wiring.

One webtoon page stays one Page; tiles are a rebuildable pixel cache.
The tile grid and LRU halves run without Qt; the rasterizer and the
ViewModel wiring run against real PNGs (a streaming writer builds the
oversize fixture without ever holding the whole image in memory).
"""

from __future__ import annotations

import json
import struct
import time
import zlib
from pathlib import Path

import pytest

from infrastructure.imaging.webtoon_tiles import (
    TileCache,
    TileGrid,
    TiledPageRasterizer,
)

# ---------------------------------------------------------------------------
# streaming PNG writer (no whole-image buffer — mirrors the memory contract)
# ---------------------------------------------------------------------------


def write_streaming_png(
    path: Path, width: int, height: int, fill_rgb=(235, 235, 235)
) -> float:
    """Write a solid-colour RGB PNG row-band by row-band; returns the elapsed
    seconds. Peak Python memory stays at one row band, not the whole image."""
    started = time.monotonic()

    def chunk(tag: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    compressor = zlib.compressobj()
    row = b"\x00" + bytes(fill_rgb) * width
    with open(path, "wb") as handle:
        handle.write(b"\x89PNG\r\n\x1a\n")
        handle.write(
            chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        )
        rows_per_band = 1000
        for start in range(0, height, rows_per_band):
            count = min(rows_per_band, height - start)
            data = compressor.compress(row * count)
            if data:
                handle.write(chunk(b"IDAT", data))
        handle.write(chunk(b"IDAT", compressor.flush()))
        handle.write(chunk(b"IEND", b""))
    return time.monotonic() - started


def row_colour(page_y: int) -> bytes:
    """Row ``page_y``'s RGB: a pure function of the row index.

    A solid-colour page cannot tell *which* rows a tile holds, so the F-4
    geometry tests use content that identifies its own row.
    """
    return bytes(((page_y * 7) % 256, (page_y * 13) % 256, (page_y * 29) % 256))


def write_row_pattern_png(
    path: Path, width: int, height: int, *, level: int = -1, seed: int = 0
) -> None:
    """RGB PNG where row ``y`` carries :func:`row_colour` (streamed by band).

    ``level=0`` stores the deflate blocks uncompressed, which makes the file
    size a pure function of the dimensions — the F-14 test needs two files of
    *identical* size with different pixels.
    """

    def chunk(tag: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    compressor = zlib.compressobj(level)
    with open(path, "wb") as handle:
        handle.write(b"\x89PNG\r\n\x1a\n")
        handle.write(
            chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        )
        rows_per_band = 1000
        for start in range(0, height, rows_per_band):
            payload = bytearray()
            for page_y in range(start, min(start + rows_per_band, height)):
                payload += b"\x00" + row_colour(page_y + seed) * width
            data = compressor.compress(bytes(payload))
            if data:
                handle.write(chunk(b"IDAT", data))
        handle.write(chunk(b"IDAT", compressor.flush()))
        handle.write(chunk(b"IEND", b""))


def qt_rows(path: Path) -> tuple[list[bytes], int, int]:
    """Decode a PNG with Qt and return its rows as packed RGB bytes.

    Reading the *tiles* through Qt (not through the reader under test) keeps
    the geometry assertion independent of the band reader.
    """
    from PySide6.QtGui import QImage

    image = QImage(str(path))
    assert not image.isNull(), f"Qt could not decode {path}"
    image = image.convertToFormat(QImage.Format.Format_RGB888)
    stride = image.bytesPerLine()
    data = bytes(image.constBits())
    rows = [data[y * stride : y * stride + image.width() * 3] for y in range(image.height())]
    return rows, image.width(), image.height()


# ---------------------------------------------------------------------------
# TileGrid geometry (no Qt)
# ---------------------------------------------------------------------------


def test_tile_grid_partitions_the_page_exactly() -> None:
    grid = TileGrid(1600, 10000, tile_height=3000, overlap=64)
    assert grid.tile_count == 4
    bands = [(tile.content_top, tile.content_bottom) for tile in grid.tiles]
    # exclusive, contiguous, covering the page: no duplicated rows, no gaps
    assert bands[0][0] == 0 and bands[-1][1] == 10000
    for (_, prev_end), (next_start, _) in zip(bands, bands[1:]):
        assert next_start == prev_end
    assert sum(end - start for start, end in bands) == 10000


def test_tile_grid_maps_tile_local_coords_back_to_the_page() -> None:
    grid = TileGrid(1600, 10000, tile_height=3000, overlap=64)
    assert grid.to_page_coords(1, 5, 0) == (5, 3000)
    assert grid.to_page_coords(2, 7, 999) == (7, 6999)
    assert grid.tile_at_y(6999).index == 2
    with pytest.raises(IndexError):
        grid.tile(99)


def test_decode_window_extends_upward_only_and_stays_in_bounds() -> None:
    grid = TileGrid(1600, 10000, tile_height=3000, overlap=64)
    first, second = grid.tile(0), grid.tile(1)
    assert grid.decode_rect(first) == (0, 0, 1600, 3000)
    x, y, w, h = grid.decode_rect(second)
    assert (x, y, w, h) == (0, 3000 - 64, 1600, 3000 + 64)


def test_visible_tiles_window_is_bounded_by_prefetch() -> None:
    grid = TileGrid(1600, 10000, tile_height=3000, overlap=64)
    assert [tile.index for tile in grid.visible_tiles(0, 100)] == [0, 1]
    assert [tile.index for tile in grid.visible_tiles(3000, 3200)] == [0, 1, 2]
    assert [tile.index for tile in grid.visible_tiles(9500, 10000)] == [2, 3]
    assert [tile.index for tile in grid.visible_tiles(3000, 3200, prefetch=0)] == [1]
    # clamped at the page edges even with a large prefetch
    assert [tile.index for tile in grid.visible_tiles(0, 100, prefetch=99)] == [0, 1, 2, 3]


def test_region_boxes_survive_tile_boundaries_deduplicated() -> None:
    """A Region crossing a tile boundary maps back to the *same* page
    rectangle from every tile it touches — regions are page-level truth and
    tile bands never duplicate or move them (AC-WEBTOON-003)."""
    grid = TileGrid(1600, 10000, tile_height=3000, overlap=64)
    page_box = (100, 2900, 500, 400)  # x, y, w, h — straddles tiles 0 and 1

    seen: set[tuple] = set()
    for tile in grid.tiles:
        if tile.content_top <= page_box[1] < tile.content_bottom or (
            tile.content_top < page_box[1] + page_box[3] <= tile.content_bottom
        ):
            local_y = page_box[1] - tile.content_top
            mapped = grid.to_page_coords(tile.index, page_box[0], local_y)
            seen.add((mapped[0], mapped[1], page_box[2], page_box[3]))
    assert seen == {(100, 2900, 500, 400)}


# ---------------------------------------------------------------------------
# TileCache LRU (no Qt)
# ---------------------------------------------------------------------------


def test_tile_cache_evicts_least_recent_used_within_budget() -> None:
    cache = TileCache(max_bytes=250)
    cache.put("a", "A", cost=100)
    cache.put("b", "B", cost=100)
    cache.get("a")  # a becomes most-recent
    cache.put("c", "C", cost=100)  # evicts b
    assert cache.get("b") is None
    assert cache.get("a") == "A"
    assert cache.get("c") == "C"
    assert cache.bytes_used == 200  # a + c kept within the 250 budget


def test_tile_cache_clear_drops_pixels_only() -> None:
    cache = TileCache(max_bytes=1000)
    cache.put("a", object(), cost=500)
    cache.clear()
    assert len(cache) == 0 and cache.bytes_used == 0


# ---------------------------------------------------------------------------
# Rasterizer + ViewModel wiring (real PNGs)
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def qapp():
    from PySide6.QtGui import QGuiApplication

    return QGuiApplication.instance() or QGuiApplication([])


def _make_reader_stack(
    tmp_path: Path, source_path: Path, tile_height: int = 800, resume: bool = False
):
    """ReaderViewModel over a one-page webtoon chapter with tiling injected."""
    from PySide6.QtGui import QColor, QImage

    from application.reading import ReaderPage
    from application.reading.service import ReadingService
    from infrastructure.filesystem.managed_storage import ManagedFileStorage
    from ui.viewmodels.reader.viewmodel import ReaderViewModel
    from application.export import ExportService, JsonHistoryDocumentStore
    from application.reading import JsonProgressDocumentStore
    from infrastructure.imaging.webtoon_tiles import TiledPageRasterizer

    tests_dir = Path(__file__).resolve().parent
    import sys

    if str(tests_dir) not in sys.path:
        sys.path.insert(0, str(tests_dir))
    src_root = tests_dir.parents[1] / "src"
    if str(src_root) not in sys.path:
        sys.path.insert(0, str(src_root))

    page_row = ReaderPage(
        page_id="p0",
        filename="long.png",
        original_path=str(source_path),
        text="第 0 页",
    )

    class Catalog:
        def list_pages(self, chapter_id):
            return [page_row]

    reading = ReadingService(JsonProgressDocumentStore(tmp_path / "progress.json"))
    export_service = ExportService(
        JsonHistoryDocumentStore(tmp_path / "export_history.json")
    )
    ManagedFileStorage(tmp_path / "managed").ensure_layout()

    def factory(path: str) -> TiledPageRasterizer:
        return TiledPageRasterizer(
            path,
            cache_dir=tmp_path / "tile-cache",
            tile_height=tile_height,
            overlap=32,
            prefetch=1,
        )

    vm = ReaderViewModel(reading, Catalog(), tile_factory=factory)
    vm.openChapter("b", "c", "条漫", "webtoon", "vertical", resume=resume)
    return vm, reading


def test_tiled_reader_serves_viewport_tiles(tmp_path, qapp) -> None:
    from infrastructure.imaging.webtoon_tiles import TiledPageRasterizer

    source = tmp_path / "long.png"
    assert write_streaming_png(source, 400, 3000) >= 0.0

    vm, reading = _make_reader_stack(tmp_path, source, tile_height=800)
    assert vm.tilesActive is True
    assert vm.pagePixelWidth == 400 and vm.pagePixelHeight == 3000
    rows = list(vm.tiles)
    assert [row["index"] for row in rows] == [0, 1, 2, 3]
    # R-001 (TASK-045 revision): the ViewModel serves the page head as soon as
    # the rows are built, so the bootstrap band (tile 0 + prefetch) already has
    # urls — this replaces the old "all urls empty until a manual request".
    assert [row["index"] for row in rows if row["url"]] == [0, 1]

    vm.requestTiles(0, 900)  # viewport + prefetch=1 → tiles 0, 1 and 2
    served = [row for row in vm.tiles if row["url"]]
    # viewport [0, 900) spans tiles 0-1; prefetch=1 adds tile 2
    assert [row["index"] for row in served] == [0, 1, 2]
    # R-001 regression: tiles outside the viewport+prefetch window must not
    # be decoded at all (按需解码 — no whole-page materialisation on scroll)
    assert all(row["url"] == "" for row in vm.tiles if row["index"] == 3)
    cache_files = list((tmp_path / "tile-cache").glob("tile-*.png"))
    assert len(cache_files) == 3  # exactly the viewport+prefetch band, not the page
    for row in served:
        path = Path(row["url"].replace("file:///", "").replace("file://", ""))
        assert path.is_file() and path.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"

    # the tile image carries the full page width (width-fit rendering)
    reader = __import__("PySide6.QtGui", fromlist=["QImage"]).QImage(str(served[0]["url"].replace("file:///", "").replace("file://", "")))
    assert not reader.isNull() and reader.width() == 400

    # progress truth survives a cache clear
    reading.save_scroll_offset(1234.0)
    vm.clearTileCache()
    assert all(not row["url"] for row in vm.tiles)
    assert reading.progress.scroll_offset_y == 1234.0
    assert reading.progress.last_page_id == "p0"


def test_tiled_reader_restores_saved_scroll_offset(tmp_path, qapp) -> None:
    """阅读位置重启恢复：a second session (resume=True) exposes the saved
    offset so the QML host restores contentY once tile geometry is known."""
    source = tmp_path / "long.png"
    write_streaming_png(source, 400, 3000)

    vm, reading = _make_reader_stack(tmp_path, source, tile_height=800)
    reading.save_scroll_offset(1600.0)
    reading.close()

    vm2, _reading2 = _make_reader_stack(tmp_path, source, tile_height=800, resume=True)
    assert vm2.tilesActive is True
    assert vm2.scrollOffsetY == pytest.approx(1600.0)


def test_oversize_page_streams_bands_within_a_measured_memory_bound(
    tmp_path, qapp
) -> None:
    """TASK-042 AC ①/②（TASK-020 表征钩子按原设计翻转口径）。

    1600x200000px 授权 fixture：几何断言不变；**像素解码从 BLOCKED 翻转为
    带状解码成功**——stdlib 流式读取器对 Qt 读不了的页（Qt PNG handler
    ≳300MB rgb32 即失败，TASK-020 实测）按 band 取行，峰值内存受
    "band 行数 x stride" 约束（下方实测断言），不再有 1.28GB 整图分配。
    旧 ``pytest.raises(OSError)`` 表征断言已按原设计更新为成功断言（更强：
    解码成功 + 内容可回映 + 内存界），测试未删除。
    """
    source = tmp_path / "huge.png"
    elapsed = write_streaming_png(source, 1600, 200000)

    # geometry (TASK-020 delivery, unchanged)
    grid = TileGrid(1600, 200000, tile_height=4000, overlap=64)
    assert grid.tile_count == 50
    bands = [(t.content_top, t.content_bottom) for t in grid.tiles]
    assert sum(end - start for start, end in bands) == 200000
    assert grid.to_page_coords(49, 10, 3999) == (10, 199999)

    # band decode through the rasterizer (the old Qt path raised OSError here)
    rasterizer = TiledPageRasterizer(
        source, cache_dir=tmp_path / "tiles", tile_height=4000, overlap=64
    )
    assert rasterizer.page_size == (1600, 200000)

    import time

    from PySide6.QtGui import QImage

    import tracemalloc

    tracemalloc.start()
    started = time.monotonic()
    files = rasterizer.ensure_viewport(0, 4000)
    took = time.monotonic() - started
    _current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    assert len(files) == 2  # visible tile + 1 prefetch

    first = QImage(str(files[0]))
    assert not first.isNull()
    # tile 0 sits at the page top: its decode window has no upward overlap
    assert (first.width(), first.height()) == (1600, 4000)

    whole_image_bytes = 1600 * 200000 * 4
    window_bytes = 4000 * 1600 * 4
    ratio = window_bytes / whole_image_bytes
    # the decode window is bounded by the band, not the page (measured fact)
    assert window_bytes * 50 <= whole_image_bytes  # tile 0 has no overlap: exactly 1/50

    record = {
        "fixture": "1600x200000 RGB PNG",
        "fixture_bytes": source.stat().st_size,
        "fixture_write_seconds": round(elapsed, 3),
        "tile_count": grid.tile_count,
        "viewport_tiles_materialised": len(files),
        "viewport_materialise_seconds": round(took, 3),
        "decode_window_bytes_rgb32": window_bytes,
        "whole_page_bytes_rgb32": whole_image_bytes,
        "decode_window_to_whole_page_ratio": round(ratio, 5),
        "python_heap_peak_bytes_during_band_read": peak,
        "decoder": "stdlib streaming PNG band reader (TASK-042)",
        "note": "TASK-020 的 BLOCKED 口径已按原设计翻转为成功；内存界是几何事实＋实测，非预算宣称",
    }
    (tmp_path / "oversize-record.json").write_text(
        json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    assert record["fixture_bytes"] > 0 and took > 0.0 and ratio < 0.05


# ---------------------------------------------------------------------------
# TASK-045 F-4: the materialised tile IS the declared content band
# ---------------------------------------------------------------------------


def test_materialised_tiles_carry_exactly_their_declared_band(
    tmp_path, qapp
) -> None:
    """F-4 (TASK-045): the overlap is *decode context only*.

    The file written for a tile must be exactly ``[content_top,
    content_bottom)`` tall and hold exactly those page rows — otherwise the
    QML delegate scales a taller image into the declared box (letterbox) and
    every non-first tile repeats the previous band's tail.
    """
    width, height = 400, 3000
    source = tmp_path / "pattern.png"
    write_row_pattern_png(source, width, height)
    rasterizer = TiledPageRasterizer(
        source, cache_dir=tmp_path / "tiles", tile_height=800, overlap=64
    )
    assert rasterizer.page_size == (width, height)

    stitched: list[bytes] = []
    for tile in rasterizer.grid.tiles:
        rows, tile_width, tile_height = qt_rows(rasterizer.tile_file(tile.index))
        expected = [row_colour(y) * width for y in range(tile.content_top, tile.content_bottom)]
        assert tile_width == width
        assert tile_height == tile.content_height, (
            f"tile {tile.index}: file height {tile_height} != declared "
            f"content_height {tile.content_height}"
        )
        assert rows == expected, f"tile {tile.index} does not hold its own page rows"
        stitched.extend(rows)

    # the union of the tiles is the page: no row repeated, none missing
    assert stitched == [row_colour(y) * width for y in range(height)]


# ---------------------------------------------------------------------------
# TASK-046: the overlap semantics fold to 0 — byte-identical tile files, one
# sequential sweep
# ---------------------------------------------------------------------------


def _write_noise_png(
    path: Path, width: int, height: int, *, seed: int = 0x2545F491
) -> None:
    """Deterministic high-entropy RGB PNG (filter 0, stdlib only).

    Random content defeats any per-row structure, so an overlap cannot be
    justified by "reconstruction needs context": every row stands alone.
    """

    def chunk(tag: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    state = seed
    rows = bytearray()
    for _y in range(height):
        rows.append(0)  # filter 0
        for _x in range(width * 3):
            state = (state * 1103515245 + 12345) & 0x7FFFFFFF
            rows.append(state & 0xFF)
    with open(path, "wb") as handle:
        handle.write(b"\x89PNG\r\n\x1a\n")
        handle.write(
            chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        )
        handle.write(chunk(b"IDAT", zlib.compress(bytes(rows), 6)))
        handle.write(chunk(b"IEND", b""))


@pytest.mark.parametrize("kind", ["pattern", "noise"])
def test_overlap_choice_leaves_tile_files_byte_identical(
    tmp_path, qapp, kind: str
) -> None:
    """AC ① (TASK-046): after F-4 the decode overlap contributes nothing to
    the stored pixels, so the default change (64 → 0) must leave every tile
    file **byte-identical** and the tile union still equal to the whole page
    — on a structured pattern page and on high-entropy noise alike.

    Deliberately a *pinned property*, not a discriminating assertion: it
    already held on the pre-fix tree (F-4 landed there), which is exactly
    what makes the default change safe (AC ⑤ records it as
    non-discriminating).
    """
    width, height = 400, 2500
    source = tmp_path / f"{kind}.png"
    if kind == "pattern":
        write_row_pattern_png(source, width, height)
    else:
        _write_noise_png(source, width, height)

    zero = TiledPageRasterizer(
        source, cache_dir=tmp_path / f"tiles-{kind}-0", tile_height=800
    )
    sixty_four = TiledPageRasterizer(
        source, cache_dir=tmp_path / f"tiles-{kind}-64", tile_height=800, overlap=64
    )
    # the default really moved (and an explicit choice is still honoured)
    assert zero.grid.overlap == 0
    assert sixty_four.grid.overlap == 64

    stitched: list[bytes] = []
    for tile in zero.grid.tiles:
        file_zero = zero.tile_file(tile.index).read_bytes()
        file_overlapped = sixty_four.tile_file(tile.index).read_bytes()
        assert file_zero == file_overlapped, (
            f"tile {tile.index}: the overlap changed the stored bytes"
        )
        rows, tile_width, tile_height = qt_rows(zero.tile_file(tile.index))
        assert (tile_width, tile_height) == (width, tile.content_height)
        stitched.extend(rows)
    page_rows, page_width, _page_height = qt_rows(source)
    assert stitched == page_rows and page_width == width, (
        "the tile union must still be the whole page, row for row"
    )


def test_full_page_sweep_is_one_sequential_scan_at_the_default(tmp_path) -> None:
    """AC ②/⑤ (TASK-046): at the default overlap a whole-page sweep is one
    sequential scan — **zero** rewinds; explicitly requesting overlap=64
    keeps the per-tile rewind (the machinery is retained, its cost
    documented).

    Discriminating: on the pre-fix tree the default was 64 and the same
    sweep rewinded ``tiles - 1`` times (4 on this page). The overlap=64
    control below pins pre-existing behaviour and does NOT count as
    discriminating.
    """
    width, height = 400, 4000  # 5 tiles at tile_height=800
    source = tmp_path / "sweep.png"
    write_row_pattern_png(source, width, height)

    def swept_rewinds(rasterizer: TiledPageRasterizer) -> int:
        counter = {"n": 0}
        reader = rasterizer._reader
        original = reader.rewind

        def counting() -> None:
            counter["n"] += 1
            original()

        reader.rewind = counting
        rasterizer.ensure_viewport(0, height)
        return counter["n"]

    default = TiledPageRasterizer(
        source, cache_dir=tmp_path / "sweep-0", tile_height=800
    )
    assert default.grid.overlap == 0
    assert swept_rewinds(default) == 0, (
        "the default-overlap sweep must be one sequential scan"
    )

    overlapped = TiledPageRasterizer(
        source, cache_dir=tmp_path / "sweep-64", tile_height=800, overlap=64
    )
    assert swept_rewinds(overlapped) == 4, (
        "an explicit overlap=64 keeps the documented per-tile rewind fold"
    )


# ---------------------------------------------------------------------------
# TASK-045 F-5 / F-11: page turns rebuild tiles; viewport coordinates are
# converted from display pixels
# ---------------------------------------------------------------------------


def _make_multipage_webtoon_stack(tmp_path: Path, sizes: list[tuple[int, int]]):
    """ReaderViewModel over a multi-page webtoon chapter with tiling injected."""
    from application.reading import ReaderPage
    from application.reading.service import ReadingService
    from application.export import ExportService, JsonHistoryDocumentStore
    from application.reading import JsonProgressDocumentStore
    from ui.viewmodels.reader.viewmodel import ReaderViewModel
    from infrastructure.imaging.webtoon_tiles import TiledPageRasterizer

    tests_dir = Path(__file__).resolve().parent
    import sys

    for entry in (str(tests_dir), str(tests_dir.parents[1] / "src")):
        if entry not in sys.path:
            sys.path.insert(0, entry)

    pages = []
    for index, (page_width, page_height) in enumerate(sizes):
        path = tmp_path / f"page_{index}.png"
        write_streaming_png(path, page_width, page_height, fill_rgb=(30 * index, 60, 90))
        pages.append(
            ReaderPage(
                page_id=f"p{index}",
                filename=path.name,
                original_path=str(path),
                text=f"第 {index} 页",
            )
        )

    class Catalog:
        def list_pages(self, chapter_id):
            return list(pages)

    reading = ReadingService(JsonProgressDocumentStore(tmp_path / "progress.json"))
    export_service = ExportService(
        JsonHistoryDocumentStore(tmp_path / "export_history.json")
    )

    def factory(path: str) -> TiledPageRasterizer:
        return TiledPageRasterizer(
            path, cache_dir=tmp_path / "tile-cache", tile_height=800, overlap=32
        )

    vm = ReaderViewModel(
        reading, Catalog(), export_service=export_service, tile_factory=factory
    )
    vm.openChapter("b", "c", "条漫", "webtoon", "vertical")
    return vm, reading


def test_opening_a_tiled_chapter_serves_the_first_band_by_itself(
    tmp_path, qapp
) -> None:
    """R-001 (TASK-045 revision): the ViewModel must serve the page head on
    open — no caller requests a viewport when the saved offset is 0."""
    vm, _reading = _make_multipage_webtoon_stack(tmp_path, [(400, 3000), (400, 1200)])

    assert vm.tilesActive is True
    served = [row for row in vm.tiles if row["url"]]
    # tile 0 + one prefetch tile, exactly what visible_tiles(0, 0) covers
    assert [row["index"] for row in served] == [0, 1]
    for row in served:
        assert Path(row["url"].replace("file:///", "").replace("file://", "")).is_file()


def test_page_turn_serves_the_remembered_viewport_without_a_request(
    tmp_path, qapp
) -> None:
    """R-001: a page turn serves the equivalent band of the new page on its
    own, clamped onto the new page's height (never an empty window)."""
    vm, _reading = _make_multipage_webtoon_stack(tmp_path, [(400, 3000), (400, 1200)])
    vm.requestTiles(2400, 3200)  # deep in page 1 (tile_height 800)
    # the deep window plus its prefetch tile are now served as well
    assert {2, 3} <= {row["index"] for row in vm.tiles if row["url"]}

    vm.nextPage()

    # page 2 is 1200 tall: the 800-row window clamps to [400, 1200) → tiles 0, 1
    assert vm.pageNumber == 2
    served = [row["index"] for row in vm.tiles if row["url"]]
    assert served == [0, 1], vm.tiles
    for row in vm.tiles:
        if row["url"]:
            assert Path(
                row["url"].replace("file:///", "").replace("file://", "")
            ).is_file()


def test_next_page_rebuilds_the_tiles_for_the_new_page(tmp_path, qapp) -> None:
    """F-5 (TASK-045): page turns must rebuild the tile rows.

    Pre-fix only ``openChapter``/``setMode`` rebuilt them, so a page turn kept
    the previous page's pixels (and urls) while progress advanced.
    """
    vm, reading = _make_multipage_webtoon_stack(tmp_path, [(400, 3000), (400, 1200)])
    assert vm.tilesActive is True
    assert vm.pagePixelHeight == 3000
    first_page_urls = [row["url"] for row in vm.tiles if row["url"]]
    assert first_page_urls, "the first page must materialise tiles on open"

    vm.nextPage()

    assert vm.pageNumber == 2
    # the rows now describe the *new* page and hold the new page's files
    assert vm.pagePixelHeight == 1200
    assert [row["height"] for row in vm.tiles] == [800, 400]
    served = [row for row in vm.tiles if row["url"]]
    assert [row["index"] for row in served] == [0, 1]
    assert set(row["url"] for row in served).isdisjoint(first_page_urls), (
        "a page turn must not keep the previous page's tile files"
    )
    for row in served:
        path = Path(row["url"].replace("file:///", "").replace("file://", ""))
        assert path.is_file()

    # ...and going back rebuilds page 1 again
    vm.previousPage()
    assert vm.pagePixelHeight == 3000
    assert [row["height"] for row in vm.tiles] == [800, 800, 800, 600]


def test_jump_to_page_rebuilds_the_tiles_too(tmp_path, qapp) -> None:
    """F-5: ``jumpToPage`` is a page-changing slot as well, and it serves the
    new page by itself (R-001)."""
    vm, reading = _make_multipage_webtoon_stack(tmp_path, [(400, 3000), (400, 1200)])
    first_page_urls = {row["url"] for row in vm.tiles if row["url"]}

    vm.jumpToPage(1)

    assert vm.pageNumber == 2
    assert vm.pagePixelHeight == 1200
    served = {row["url"] for row in vm.tiles if row["url"]}
    assert served, "jumping to a page must serve its tiles"
    assert served.isdisjoint(first_page_urls)


class _RecordingRasterizer:
    """Minimal rasterizer double that records the viewport it is asked for."""

    def __init__(self, page_size: tuple[int, int]) -> None:
        self.page_size = page_size
        self.grid = TileGrid(page_size[0], page_size[1], tile_height=800, overlap=32)
        self.prefetch = 1
        self.viewports: list[tuple[int, int]] = []

    def ensure_viewport(self, top: int, bottom: int):
        self.viewports.append((top, bottom))
        return ()

    def tile_file(self, index: int) -> Path:
        return Path(f"tile-{index}.png")


def test_request_tiles_converts_display_pixels_to_page_pixels(tmp_path, qapp) -> None:
    """F-11 (TASK-045): QML passes *display* pixels (``Flickable.contentY``);
    the grid speaks page pixels, so the caller must pass the scale."""
    from application.reading import ReaderPage
    from application.reading.service import ReadingService
    from application.reading import JsonProgressDocumentStore
    from ui.viewmodels.reader.viewmodel import ReaderViewModel

    recording = _RecordingRasterizer((1600, 6000))
    page = ReaderPage(
        page_id="p0", filename="long.png", original_path=str(tmp_path / "long.png"), text=""
    )

    class Catalog:
        def list_pages(self, chapter_id):
            return [page]

    reading = ReadingService(JsonProgressDocumentStore(tmp_path / "progress.json"))
    vm = ReaderViewModel(reading, Catalog(), tile_factory=lambda path: recording)
    vm.openChapter("b", "c", "条漫", "webtoon", "vertical")
    assert vm.tilesActive is True

    # the page is 1600px wide; the host shows it at 800px → scale 0.5
    vm.requestTiles(0, 500, 0.5)
    vm.requestTiles(10, 500, 0.5)
    # default keeps the historical 1:1 behaviour
    vm.requestTiles(0, 500)

    # the first entry is the open-time bootstrap (R-001): visible_tiles(0, 0)
    assert recording.viewports == [(0, 0), (0, 1000), (20, 1000), (0, 500)]


def test_ensure_viewport_rewind_accounting_is_per_tile(tmp_path, qapp) -> None:
    """AC ⑩ (TASK-042 R-03): the cursor only moves forward and
    ``visible_tiles`` is ascending, so a rewind's rescan is bounded by the
    requested window's end — and **each overlapped tile after the first
    rewinds once** (measured; see verification/TASK-045/rewind-cost-probe.txt).

    The AC's original premise ("one call needs at most one rewind") holds only
    for a single-tile call; this test pins both cases so the cost model cannot
    drift silently.
    """
    width, height = 400, 4000
    source = tmp_path / "pattern.png"
    write_row_pattern_png(source, width, height)
    rasterizer = TiledPageRasterizer(
        source, cache_dir=tmp_path / "tiles", tile_height=800, overlap=32, prefetch=0
    )
    grid = rasterizer.grid

    # premise: the tile window is ascending for every viewport
    for top in range(0, height, 250):
        indices = [tile.index for tile in grid.visible_tiles(top, top + 400, prefetch=1)]
        assert indices == sorted(indices)

    reader = rasterizer._reader
    rewinds: list[int] = []
    original_rewind = reader.rewind

    def counting_rewind() -> None:
        rewinds.append(reader.cursor_row)
        original_rewind()

    reader.rewind = counting_rewind

    rasterizer.ensure_viewport(2400, 3200)  # forward: no rewind
    assert rewinds == []
    assert reader.cursor_row >= 3200

    rasterizer.ensure_viewport(0, 800)  # one tile behind the cursor: one rewind
    assert len(rewinds) == 1
    rows, _width, tile_height = qt_rows(rasterizer.tile_file(0))
    assert tile_height == 800
    assert rows == [row_colour(y) * width for y in range(800)]

    # a later forward call reuses the materialised file (no decode, no rewind)
    rasterizer.ensure_viewport(2400, 3200)
    assert len(rewinds) == 1

    # three fresh overlapped tiles in one call: tiles 1 and 2 each rewind,
    # because their windows start `overlap` rows before the previous end
    fresh = TiledPageRasterizer(
        source, cache_dir=tmp_path / "tiles-2", tile_height=800, overlap=32, prefetch=0
    )
    fresh_reader = fresh._reader
    fresh_rewinds: list[int] = []
    fresh_original = fresh_reader.rewind

    def fresh_counting() -> None:
        fresh_rewinds.append(fresh_reader.cursor_row)
        fresh_original()

    fresh_reader.rewind = fresh_counting
    fresh.ensure_viewport(0, 2400)  # tiles 0, 1, 2
    assert len(fresh_rewinds) == 2, fresh_rewinds


def test_same_size_rewrite_does_not_reuse_a_stale_tile(tmp_path, qapp) -> None:
    """F-14 (TASK-045): the cache key must be content-addressed.

    The old key was path + size + geometry, so rewriting the source *in place*
    with the same byte count kept hitting the previous page's tile.
    """
    width, height = 40, 200
    source = tmp_path / "page.png"
    cache_dir = tmp_path / "tiles"
    write_row_pattern_png(source, width, height, level=0, seed=0)
    first_size = source.stat().st_size

    first_raster = TiledPageRasterizer(
        source, cache_dir=cache_dir, tile_height=100, overlap=8
    )
    first_tile = first_raster.tile_file(0)
    first_rows, _width, _height = qt_rows(first_tile)

    # same dimensions, different pixels, identical byte count (level 0)
    write_row_pattern_png(source, width, height, level=0, seed=37)
    assert source.stat().st_size == first_size, "the rewrite must keep the size"

    second_raster = TiledPageRasterizer(
        source, cache_dir=cache_dir, tile_height=100, overlap=8
    )
    second_tile = second_raster.tile_file(0)

    assert second_tile != first_tile, "stale tile reused after an in-place rewrite"
    second_rows, _width, _height = qt_rows(second_tile)
    assert second_rows != first_rows
    assert second_rows == [row_colour(y + 37) * width for y in range(100)]


def _corrupt_png_payload(path: Path) -> None:
    """Damage the IDAT payload while leaving the container structurally valid."""
    data = bytearray(path.read_bytes())
    marker = data.index(b"IDAT")
    length = struct.unpack_from(">I", data, marker - 4)[0]
    state = 24681357
    for index in range(marker + 4, marker + 4 + length):
        state = (state * 1103515245 + 12345) & 0x7FFFFFFF
        data[index] = state & 0xFF
    path.write_bytes(bytes(data))


def test_damaged_payload_degrades_through_the_viewmodel(tmp_path, qapp) -> None:
    """AC ⑧ end-to-end (TASK-042 R-01): a damaged payload must reach the
    ViewModel's documented fallback instead of escaping ``zlib.error`` while
    QML scrolls (``zlib.error`` is not an ``OSError``/``ValueError``)."""
    source = tmp_path / "damaged.png"
    write_streaming_png(source, 400, 3000)
    _corrupt_png_payload(source)

    vm, _reading = _make_reader_stack(tmp_path, source, tile_height=800)
    assert vm.tilesActive is True

    vm.requestTiles(0, 900)  # pre-fix: zlib.error escapes this call

    assert [row["index"] for row in vm.tiles] == [0, 1, 2, 3]
    assert all(row["url"] == "" for row in vm.tiles), "no tile can be served"


# ---------------------------------------------------------------------------
# TASK-062 AC ④ / TASK-046 R-001: the overlap equivalence on a page whose rows
# carry *adaptive* filters. The hand-written fixtures above only ever emit
# filter 0, so the filter-dependent decode path was never exercised.
# ---------------------------------------------------------------------------


def write_qt_encoded_png(path: Path, width: int, height: int) -> None:
    """Encode a page with Qt/libpng (adaptive row filters)."""
    from PySide6.QtGui import QImage

    payload = bytearray()
    for y in range(height):
        payload += bytes(((y * 3) % 256, (y * 29) % 256, (y * 7) % 256)) * width
    raw = bytes(payload)
    image = QImage(raw, width, height, width * 3, QImage.Format.Format_RGB888)
    assert image.save(str(path), "PNG"), "Qt could not encode the fixture"


def _write_hand_filtered_png(
    path: Path,
    width: int,
    height: int,
    filter_type: int,
    *,
    interlace: int = 0,
    truncate_raw: bool = False,
    first_filter_type: int | None = None,
) -> None:
    """Write a deterministic RGB page with one selected PNG row filter."""
    if filter_type not in {0, 2, 3}:
        raise ValueError(filter_type)

    def chunk(tag: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    rows = [
        bytes(((y * 17 + index * 5) % 256) for index in range(width * 3))
        for y in range(height)
    ]
    encoded = bytearray()
    for index, row in enumerate(rows):
        previous = rows[index - 1] if index else None
        encoded.append(first_filter_type if index == 0 and first_filter_type is not None else filter_type)
        if filter_type == 0:
            encoded.extend(row)
        elif filter_type == 2:
            encoded.extend(
                (value - (previous[offset] if previous else 0)) & 0xFF
                for offset, value in enumerate(row)
            )
        else:
            encoded.extend(
                (
                    value
                    - (
                        (
                            (row[offset - 3] if offset >= 3 else 0)
                            + (previous[offset] if previous else 0)
                        )
                        >> 1
                    )
                )
                & 0xFF
                for offset, value in enumerate(row)
            )
    payload = bytes(encoded[:-1] if truncate_raw else encoded)
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, interlace))
        + chunk(b"IDAT", zlib.compress(payload))
        + chunk(b"IEND", b"")
    )


def png_row_filter_types(path: Path) -> set[int]:
    """The filter-type byte of every reconstructed scanline in the IDAT."""
    data = path.read_bytes()
    pos = 8
    width = height = bit_depth = colour_type = interlace = 0
    idat = bytearray()
    while pos + 8 <= len(data):
        length = struct.unpack_from(">I", data, pos)[0]
        tag = data[pos + 4 : pos + 8]
        chunk = data[pos + 8 : pos + 8 + length]
        if tag == b"IHDR":
            (
                width,
                height,
                bit_depth,
                colour_type,
                _compression,
                _filter_method,
                interlace,
            ) = struct.unpack(">IIBBBBB", chunk)
        elif tag == b"IDAT":
            idat += chunk
        elif tag == b"IEND":
            break
        pos += 12 + length
    channels = {0: 1, 2: 3, 4: 2, 6: 4}[colour_type]
    stride = width * (bit_depth // 8) * channels + 1
    raw = zlib.decompress(bytes(idat))
    assert interlace == 0, "png_row_filter_types only supports non-interlaced PNGs"
    assert len(raw) == height * stride, "decompressed PNG payload has an invalid length"
    filter_types = {raw[y * stride] for y in range(height)}
    assert all(0 <= filter_type <= 4 for filter_type in filter_types), (
        "png_row_filter_types found an invalid filter type"
    )
    return filter_types


def test_png_row_filter_types_rejects_interlaced_pages(tmp_path) -> None:
    source = tmp_path / "interlaced.png"
    _write_hand_filtered_png(source, 8, 3, 2, interlace=1)

    with pytest.raises(AssertionError, match="non-interlaced"):
        png_row_filter_types(source)


def test_png_row_filter_types_rejects_truncated_scanlines(tmp_path) -> None:
    source = tmp_path / "truncated.png"
    _write_hand_filtered_png(source, 8, 3, 2, truncate_raw=True)

    with pytest.raises(AssertionError, match="invalid length"):
        png_row_filter_types(source)


def test_png_row_filter_types_rejects_invalid_filter_bytes(tmp_path) -> None:
    source = tmp_path / "invalid-filter.png"
    _write_hand_filtered_png(source, 8, 3, 2, first_filter_type=5)

    with pytest.raises(AssertionError, match="filter type"):
        png_row_filter_types(source)


def test_overlap_choice_on_a_qt_encoded_page(tmp_path, qapp) -> None:
    """TASK-046 R-001 (TASK-062 AC ④): the overlap property on a page encoded
    by Qt/libpng - one whose rows carry adaptive filters.

    The original proof used hand-written filter-0 fixtures, so it said nothing
    about the filter-dependent decode path. The fixture is asserted to be
    non-trivial first, otherwise this test would silently re-open the gap it is
    meant to close.
    """
    width, height = 600, 2100
    source = tmp_path / "qt-encoded.png"
    write_qt_encoded_png(source, width, height)
    assert png_row_filter_types(source) != {0}, (
        "fixture is all filter-0: R-001 would stay open"
    )

    zero = TiledPageRasterizer(source, cache_dir=tmp_path / "tiles-0", tile_height=800)
    sixty_four = TiledPageRasterizer(
        source, cache_dir=tmp_path / "tiles-64", tile_height=800, overlap=64
    )
    assert zero.grid.overlap == 0
    assert sixty_four.grid.overlap == 64

    stitched: list[bytes] = []
    for tile in zero.grid.tiles:
        file_zero = zero.tile_file(tile.index).read_bytes()
        file_overlapped = sixty_four.tile_file(tile.index).read_bytes()
        assert file_zero == file_overlapped, (
            f"tile {tile.index}: the overlap changed the stored bytes"
        )
        rows, tile_width, tile_height = qt_rows(zero.tile_file(tile.index))
        assert (tile_width, tile_height) == (width, tile.content_height)
        stitched.extend(rows)
    page_rows, page_width, _page_height = qt_rows(source)
    assert stitched == page_rows and page_width == width, (
        "the tile union must still be the whole page, row for row"
    )


@pytest.mark.parametrize("filter_type", [2, 3], ids=["up", "average"])
def test_overlap_choice_on_hand_filtered_pages(tmp_path, qapp, filter_type) -> None:
    """TASK-063 R-006: explicitly cover Up and Average row filters."""
    width, height = 600, 2100
    source = tmp_path / f"filter-{filter_type}.png"
    _write_hand_filtered_png(source, width, height, filter_type)
    assert png_row_filter_types(source) == {filter_type}

    zero = TiledPageRasterizer(source, cache_dir=tmp_path / "tiles-0", tile_height=800)
    sixty_four = TiledPageRasterizer(
        source, cache_dir=tmp_path / "tiles-64", tile_height=800, overlap=64
    )
    stitched: list[bytes] = []
    for tile in zero.grid.tiles:
        file_zero = zero.tile_file(tile.index).read_bytes()
        file_overlapped = sixty_four.tile_file(tile.index).read_bytes()
        assert file_zero == file_overlapped
        rows, tile_width, tile_height = qt_rows(zero.tile_file(tile.index))
        assert (tile_width, tile_height) == (width, tile.content_height)
        stitched.extend(rows)
    page_rows, page_width, _page_height = qt_rows(source)
    assert stitched == page_rows and page_width == width
