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
    assert all(not row["url"] for row in rows)

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


def test_oversize_page_geometry_and_decoder_limit_record(tmp_path, qapp) -> None:
    """1600x200000px 授权 fixture 的如实验证记录。

    - **几何（本切片交付，PASS）**：TileGrid 对 200000px 高的页面给出恰好
      划分（50 tiles、区间互斥并覆盖）、坐标回映与视口窗口全部正确——
      一页保持一 Page，tile 只是可重建缓存。
    - **像素解码（BLOCKED，非本切片可解）**：Qt PNG handler 在 rgb32 字节数
      ≳300MB 时即失败（实测高度 40000=256MB 成功、50000=305MB 失败；系统
      可用内存 19GB 排除内存不足），且 setClipRect 不改变该行为（handler
      先分配整图再裁剪）。因此 1600x200000（1.28GB）在当前依赖下无法解码。
      本测试把该限制固化为表征断言：若未来解码成功（依赖替换/上游修复），
      此断言失败即提醒更新 BLOCKED 口径。解锁条件：引入流式 PNG 解码依赖
      （需用户批准依赖变更）或 Qt 上游修复。
    """
    source = tmp_path / "huge.png"
    elapsed = write_streaming_png(source, 1600, 200000)

    # geometry: the full 200000px page is partitioned exactly
    grid = TileGrid(1600, 200000, tile_height=4000, overlap=64)
    assert grid.tile_count == 50
    bands = [(t.content_top, t.content_bottom) for t in grid.tiles]
    assert sum(end - start for start, end in bands) == 200000
    assert grid.to_page_coords(49, 10, 3999) == (10, 199999)
    assert [t.index for t in grid.visible_tiles(196000, 200000)] == [48, 49]

    # pixel decode: Qt limit, recorded as the BLOCKED evidence it is
    rasterizer = TiledPageRasterizer(
        source, cache_dir=tmp_path / "tiles", tile_height=4000, overlap=64
    )
    assert rasterizer.page_size == (1600, 200000)
    with pytest.raises(OSError, match="tile decode failed"):
        rasterizer.ensure_viewport(0, 4000)

    record = {
        "fixture": "1600x200000 RGB PNG",
        "fixture_bytes": source.stat().st_size,
        "fixture_write_seconds": round(elapsed, 3),
        "tile_grid": {"tile_count": grid.tile_count, "tile_height": 4000},
        "pixel_decode": "BLOCKED: Qt PNG handler fails above ~300MB rgb32 "
        "(probe: 40000px=256MB ok, 50000px=305MB fails; 19GB free RAM; "
        "setClipRect does not help — the handler allocates the whole image)",
        "unlock_conditions": [
            "approved streaming PNG decode dependency",
            "or upstream Qt fix",
        ],
        "note": "实测记录；几何交付可用，像素解码在当前依赖下不可行",
    }
    (tmp_path / "oversize-record.json").write_text(
        json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    assert record["fixture_bytes"] > 0 and elapsed > 0.0
