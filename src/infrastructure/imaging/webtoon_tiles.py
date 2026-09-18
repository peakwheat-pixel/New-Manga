"""Webtoon tile grid, cache and on-demand rasterizer (TASK-020/042).

A webtoon page is one Page entity and one source file — tiles are a
*rebuildable pixel cache* in front of it, never a second source of truth
(D03 §5, AC-WEBTOON-001/003):

- :class:`TileGrid` is pure geometry: it partitions the page into exclusive
  content bands (``union == page`` ``intersection == empty`` — the dedup
  property), maps tile-local coordinates back onto the page (坐标回映) and
  answers which tiles a viewport needs, with a bounded prefetch window.
- :class:`TileCache` is a byte-budgeted LRU over rebuildable entries;
  ``clear()`` only drops pixels, business truth (progress, regions, render
  revisions) lives in the reading service / repository and is untouched.
- :class:`TiledPageRasterizer` decodes one tile at a time through the
  stdlib streaming PNG band reader (:mod:`infrastructure.imaging.streaming_png`,
  TASK-042 — the Qt PNG handler allocates the whole image and fails above
  ~300 MB rgb32), stores decoded tiles as PNG files in a rebuildable cache
  directory and serves file paths (the reader ViewModel hands them to QML as
  file URIs; no engine-side image provider is needed).

The band reader is pure stdlib and the PNG encoder is pure stdlib — this
module has **no** Qt import at all, so the grid/cache/raster half is
unit-testable without PySide6.
"""

from __future__ import annotations

import hashlib
import os
import struct
import zlib
from collections import OrderedDict
from dataclasses import dataclass
from itertools import accumulate
from pathlib import Path
from typing import Sequence

from infrastructure.imaging.streaming_png import StreamingPngError, StreamingPngReader

_COLOUR_TYPE_FOR_CHANNELS = {1: 0, 2: 4, 3: 2, 4: 6}


def _encode_png(raw: bytes, width: int, height: int, channels: int) -> bytes:
    """Encode reconstructed scanlines (filter 0) as a PNG — pure stdlib.

    ``raw`` is ``height`` rows of ``width x channels`` bytes (channel order
    matches the source PNG colour type). Filter 0 keeps encoding O(bytes) at
    C speed; the streaming reader already did the reconstruction work.
    """

    def chunk(tag: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    colour_type = _COLOUR_TYPE_FOR_CHANNELS[channels]
    stride = width * channels
    scanlines = b"".join(
        b"\x00" + raw[i * stride : (i + 1) * stride] for i in range(height)
    )
    return b"".join(
        (
            b"\x89PNG\r\n\x1a\n",
            chunk(
                b"IHDR",
                struct.pack(
                    ">IIBBBBB", width, height, 8, colour_type, 0, 0, 0
                ),
            ),
            chunk(b"IDAT", zlib.compress(scanlines, 6)),
            chunk(b"IEND", b""),
        )
    )


@dataclass(frozen=True)
class TileSpec:
    """One tile's responsibility band, in *page* pixel coordinates.

    ``[content_top, content_bottom)`` bands are exclusive and contiguous:
    neighbouring tiles share no rows (拼接去重 happens by construction, not
    by post-processing), and the band coordinates are the coordinate
    round-trip anchor — a tile-local ``(x, y)`` maps back to
    ``(x, content_top + y)``.
    """

    index: int
    content_top: int
    content_bottom: int

    @property
    def content_height(self) -> int:
        return self.content_bottom - self.content_top


class TileGrid:
    """Immutable geometry for one page's tile partition."""

    def __init__(
        self,
        page_width: int,
        page_height: int,
        tile_height: int = 4000,
        overlap: int = 64,
    ) -> None:
        page_width = int(page_width)
        page_height = int(page_height)
        tile_height = max(1, int(tile_height))
        overlap = max(0, int(overlap))
        if page_width <= 0 or page_height <= 0:
            raise ValueError("page dimensions must be positive")
        self.page_width = page_width
        self.page_height = page_height
        self.tile_height = min(tile_height, page_height)
        self.overlap = min(overlap, self.tile_height)
        self.tiles: tuple[TileSpec, ...] = self._partition()

    def _partition(self) -> tuple[TileSpec, ...]:
        bands: list[TileSpec] = []
        top = 0
        index = 0
        while top < self.page_height:
            bottom = min(top + self.tile_height, self.page_height)
            bands.append(TileSpec(index=index, content_top=top, content_bottom=bottom))
            top = bottom
            index += 1
        return tuple(bands)

    @property
    def tile_count(self) -> int:
        return len(self.tiles)

    def tile(self, index: int) -> TileSpec:
        return self.tiles[self._wrap(index)]

    def _wrap(self, index: int) -> int:
        if not 0 <= index < len(self.tiles):
            raise IndexError(f"tile index {index} out of range")
        return index

    def decode_rect(self, tile: TileSpec) -> tuple[int, int, int, int]:
        """``(x, y, w, h)`` decode window including the context overlap.

        The overlap extends *upwards* into the previous tile's tail so a
        region sitting on a boundary decodes with its full context; the
        displayed band stays ``[content_top, content_bottom)``.
        """
        y = max(0, tile.content_top - self.overlap)
        bottom = min(self.page_height, tile.content_bottom)
        return (0, y, self.page_width, bottom - y)

    def tile_at_y(self, page_y: int) -> TileSpec:
        page_y = max(0, min(int(page_y), self.page_height - 1))
        index = page_y // self.tile_height
        return self.tiles[index]

    def visible_tiles(
        self, viewport_top: int, viewport_bottom: int, *, prefetch: int = 1
    ) -> tuple[TileSpec, ...]:
        """Tiles covering ``[viewport_top, viewport_bottom)`` plus a bounded
        prefetch window of ``prefetch`` tiles beyond each edge."""
        viewport_top = max(0, int(viewport_top))
        viewport_bottom = min(self.page_height, max(viewport_top, int(viewport_bottom)))
        first = viewport_top // self.tile_height
        last = max(first, (viewport_bottom - 1) // self.tile_height)
        lo = max(0, first - max(0, int(prefetch)))
        hi = min(self.tile_count - 1, last + max(0, int(prefetch)))
        return tuple(self.tiles[index] for index in range(lo, hi + 1))

    def to_page_coords(self, tile_index: int, x: int, y: int) -> tuple[int, int]:
        """坐标回映：tile-local ``(x, y)`` → page coordinates."""
        tile = self.tile(tile_index)
        return (int(x), tile.content_top + int(y))


class TileCache:
    """Byte-budgeted LRU over rebuildable entries.

    Entries are opaque (callers hand in the cost); ``clear()`` drops
    everything cached — by contract nothing outside rebuildable pixels ever
    enters the cache, so clearing can never damage business truth
    (AC-WEBTOON-003).
    """

    def __init__(self, max_bytes: int) -> None:
        self.max_bytes = max(1, int(max_bytes))
        self._entries: OrderedDict[str, object] = OrderedDict()
        self._costs: dict[str, int] = {}
        self._bytes = 0

    def __len__(self) -> int:
        return len(self._entries)

    @property
    def bytes_used(self) -> int:
        return self._bytes

    def get(self, key: str):
        if key not in self._entries:
            return None
        self._entries.move_to_end(key)
        return self._entries[key]

    def put(self, key: str, value, *, cost: int) -> None:
        cost = max(0, int(cost))
        if key in self._entries:
            self._bytes -= self._costs[key]
            del self._entries[key]
        self._entries[key] = value
        self._costs[key] = cost
        self._bytes += cost
        self._trim()

    def clear(self) -> None:
        self._entries.clear()
        self._costs.clear()
        self._bytes = 0

    def _trim(self) -> None:
        while self._bytes > self.max_bytes and len(self._entries) > 1:
            evicted, _ = self._entries.popitem(last=False)
            self._bytes -= self._costs.pop(evicted, 0)


class TiledPageRasterizer:
    """On-demand tile decoder with a rebuildable file cache.

    Peak memory is one decode window (tile + upward overlap), never the
    whole page: the stdlib streaming PNG reader reconstructs exactly the
    requested band. Decoded tiles become PNG files under ``cache_dir``
    (keyed by source hash + tile index + geometry), so QML consumes ordinary
    file URIs and the whole cache directory can be wiped and rebuilt at any
    time. The streaming cursor only moves forward; a request behind it (after
    a cache wipe) transparently rewinds and re-scans.
    """

    def __init__(
        self,
        source_path: str | Path,
        *,
        cache_dir: str | Path,
        tile_height: int = 4000,
        overlap: int = 64,
        prefetch: int = 1,
        cache: TileCache | None = None,
    ) -> None:
        self.source_path = Path(source_path)
        self.cache_dir = Path(cache_dir)
        self.prefetch = max(0, int(prefetch))
        self._cache = cache if cache is not None else TileCache(max_bytes=256 * 1024 * 1024)
        self._reader = StreamingPngReader(self.source_path.read_bytes())
        self.grid = TileGrid(
            self._reader.width,
            self._reader.height,
            tile_height=tile_height,
            overlap=overlap,
        )
        self._file_keys: dict[int, Path] = {}
        self._in_flight: set[int] = set()

    # ------------------------------------------------------------------
    # geometry
    # ------------------------------------------------------------------

    @property
    def page_size(self) -> tuple[int, int]:
        return (self.grid.page_width, self.grid.page_height)

    # ------------------------------------------------------------------
    # tile materialisation
    # ------------------------------------------------------------------

    def tile_file(self, index: int) -> Path:
        """Materialise one tile (cache hit or band decode) and return its PNG
        path. Concurrent callers for the same index get the same file."""
        tile = self.grid.tile(index)
        cached = self._file_keys.get(index)
        if cached is not None and cached.is_file():
            return cached
        key = self._cache_key(index)
        target = self.cache_dir / f"{key}.png"
        if target.is_file():
            self._file_keys[index] = target
            return target
        if index in self._in_flight:
            raise RuntimeError(f"tile {index} is already being decoded")
        self._in_flight.add(index)
        try:
            png_bytes = self._decode(self.grid.decode_rect(tile))
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            target.write_bytes(png_bytes)
            self._file_keys[index] = target
            self._cache.put(key, target, cost=max(1, len(png_bytes)))
            return target
        finally:
            self._in_flight.discard(index)

    def ensure_viewport(
        self, viewport_top: int, viewport_bottom: int
    ) -> tuple[Path, ...]:
        """Decode the visible tiles plus the bounded prefetch window."""
        return tuple(
            self.tile_file(tile.index)
            for tile in self.grid.visible_tiles(
                viewport_top, viewport_bottom, prefetch=self.prefetch
            )
        )

    def _decode(self, rect: tuple[int, int, int, int]) -> bytes:
        """Rasterise the band ``(x, y, w, h)`` into PNG bytes.

        ``x`` is always 0 (bands span the full width). The streaming cursor
        only moves forward; a request behind it (possible after a cache wipe)
        rewinds and re-scans once — correctness first, re-scan cost recorded
        in the TASK-042 handoff."""
        _x, y, _width, height = rect
        try:
            raw, width, band_height, channels = self._reader.read_band(y, height)
        except StreamingPngError as error:
            if error.reason != "REWIND_REQUIRED":
                raise OSError(
                    f"tile decode failed for {self.source_path}: {error}"
                ) from error
            self._reader.rewind()
            raw, width, band_height, channels = self._reader.read_band(y, height)
        return _encode_png(raw, width, band_height, channels)

    def _cache_key(self, index: int) -> str:
        stat = os.stat(self.source_path)
        digest = hashlib.sha256(
            f"{self.source_path}|{stat.st_size}|{self.grid.page_width}x"
            f"{self.grid.page_height}|{self.grid.tile_height}|{self.grid.overlap}|{index}".encode()
        ).hexdigest()[:24]
        return f"tile-{digest}-{index:05d}"

    # ------------------------------------------------------------------
    # cache maintenance
    # ------------------------------------------------------------------

    def clear(self) -> None:
        """Drop every rebuildable pixel (memory LRU + cache files). Business
        data lives elsewhere and is untouched."""
        self._cache.clear()
        self._file_keys.clear()
        if self.cache_dir.is_dir():
            for entry in self.cache_dir.glob("tile-*.png"):
                try:
                    entry.unlink()
                except OSError:
                    pass


__all__ = [
    "TileCache",
    "TileGrid",
    "TileSpec",
    "TiledPageRasterizer",
]
