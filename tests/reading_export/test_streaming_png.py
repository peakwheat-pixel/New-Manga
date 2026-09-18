"""TASK-042 streaming PNG band reader: filter correctness (all five PNG
scanline filters, hand-encoded), pixel-identity against the Qt decoder,
cursor semantics, and the typed unsupported-variant matrix.

The hand-built PNG writer below encodes rows with a *chosen* filter type, so
every unfilter branch is exercised deterministically (a real encoder mixes
filters per row and would not let us pin each branch).
"""

from __future__ import annotations

import struct
import zlib
from pathlib import Path

import pytest

pytest.importorskip("PySide6", reason="pixel-identity comparison uses QImage")

from PySide6.QtGui import QImage  # noqa: E402

from infrastructure.imaging.streaming_png import (  # noqa: E402
    StreamingPngError,
    StreamingPngReader,
)


def _paeth(a: int, b: int, c: int) -> int:
    p = a + b - c
    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    if pb <= pc:
        return b
    return c


def _encode_row(filter_type: int, raw: bytes, prev: bytes | None, bpp: int) -> bytes:
    """Forward filter for one scanline (PNG spec §6.3)."""
    n = len(raw)
    if filter_type == 0:
        return raw
    if filter_type == 1:  # Sub
        return bytes(
            raw[i] if i < bpp else (raw[i] - raw[i - bpp]) & 0xFF for i in range(n)
        )
    if filter_type == 2:  # Up
        if prev is None:
            return raw
        return bytes((raw[i] - prev[i]) & 0xFF for i in range(n))
    if filter_type == 3:  # Average
        out = bytearray()
        for i in range(n):
            left = raw[i - bpp] if i >= bpp else 0
            up = prev[i] if prev is not None else 0
            out.append((raw[i] - ((left + up) >> 1)) & 0xFF)
        return bytes(out)
    if filter_type == 4:  # Paeth
        out = bytearray()
        for i in range(n):
            left = raw[i - bpp] if i >= bpp else 0
            up = prev[i] if prev is not None else 0
            up_left = prev[i - bpp] if (prev is not None and i >= bpp) else 0
            out.append((raw[i] - _paeth(left, up, up_left)) & 0xFF)
        return bytes(out)
    raise ValueError(filter_type)


def build_png(
    width: int,
    height: int,
    raw_rows: list[bytes],
    *,
    bpp: int = 3,
    filter_type: int = 0,
    bit_depth: int = 8,
    colour_type: int = 2,
    interlace: int = 0,
    with_palette: bool = False,
    truncate: bool = False,
) -> bytes:
    """Assemble a PNG byte-by-byte; ``raw_rows`` are the *reconstructed*
    scanlines the decoder must reproduce."""
    def chunk(tag: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    out = bytearray(b"\x89PNG\r\n\x1a\n")
    out += chunk(
        b"IHDR",
        struct.pack(
            ">IIBBBBB", width, height, bit_depth, colour_type, 0, 0, interlace
        ),
    )
    if with_palette:
        out += chunk(b"PLTE", bytes(256 * 3))
    if raw_rows is not None:
        compressed = bytearray()
        for index, raw in enumerate(raw_rows):
            prev = raw_rows[index - 1] if index > 0 else None
            compressed += bytes([filter_type])
            compressed += _encode_row(filter_type, raw, prev, bpp)
        out += chunk(b"IDAT", zlib.compress(bytes(compressed)))
    out += chunk(b"IEND", b"")
    if truncate:
        marker = out.index(b"IDAT")
        return bytes(out[: marker - 4])  # cut before the IDAT data lands
    return bytes(out)


def make_raw_rows(width: int, height: int, bpp: int = 3, seed: int = 7) -> list[bytes]:
    """Deterministic pseudo-random rows (all byte values occur)."""
    rows = []
    state = seed
    for _ in range(height):
        row = bytearray()
        for _ in range(width * bpp):
            state = (state * 1103515245 + 12345) & 0x7FFFFFFF
            row.append(state & 0xFF)
        rows.append(bytes(row))
    return rows


# ---------------------------------------------------------------------------
# unfilter correctness: all five filters reconstruct the same raw rows
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("filter_type", [0, 1, 2, 3, 4])
def test_all_five_filters_reconstruct_raw_rows(filter_type: int) -> None:
    width, height, bpp = 13, 6, 3
    raw_rows = make_raw_rows(width, height, bpp=bpp)
    png = build_png(width, height, raw_rows, bpp=bpp, filter_type=filter_type)

    reader = StreamingPngReader(png)
    assert (reader.width, reader.height) == (width, height)
    raw, w, h, channels = reader.read_band(0, height)
    assert (w, h, channels) == (width, height, bpp)
    assert raw == b"".join(raw_rows)


def test_mixed_filters_per_row_reconstruct() -> None:
    """A row-per-filter page (what real encoders emit) also reconstructs."""
    width, height, bpp = 9, 5, 3
    width, height, bpp = 9, 5, 3
    raw_rows = make_raw_rows(width, height, bpp=bpp)
    # row i uses filter i % 5 (build_png only pins one type; assemble here)
    def chunk(tag: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    out = bytearray(b"\x89PNG\r\n\x1a\n")
    out += chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    compressed = bytearray()
    for index, raw in enumerate(raw_rows):
        ftype = index % 5
        prev = raw_rows[index - 1] if index > 0 else None
        compressed += bytes([ftype])
        compressed += _encode_row(ftype, raw, prev, bpp)
    out += chunk(b"IDAT", zlib.compress(bytes(compressed)))
    out += chunk(b"IEND", b"")
    png = bytes(out)

    reader = StreamingPngReader(png)
    raw, w, h, _channels = reader.read_band(0, height)
    assert raw == b"".join(raw_rows)


# ---------------------------------------------------------------------------
# pixel identity against the Qt decoder
# ---------------------------------------------------------------------------


def test_decodes_qt_encoded_png_pixel_identical(tmp_path: Path) -> None:
    """A Qt-*encoded* PNG (libpng's own per-row filter choices, random
    content) must decode to the exact same pixels QImage reports."""
    from PySide6.QtCore import QBuffer, QIODevice

    width, height = 48, 32
    image = QImage(width, height, QImage.Format.Format_RGBA8888)
    state = 11
    for y in range(height):
        for x in range(width):
            state = (state * 48271) % 2147483647
            r, g, b = state & 0xFF, (state >> 8) & 0xFF, (state >> 16) & 0xFF
            image.setPixel(x, y, 0xFF000000 | (r << 16) | (g << 8) | b)

    buffer = QBuffer()
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    assert image.save(buffer, "PNG")
    data = bytes(buffer.data())

    reader = StreamingPngReader(data)
    raw, w, h, channels = reader.read_band(0, height)
    assert (w, h, channels) == (width, height, 4)

    # pixel-identity against QImage (both RGBA8888, stride = width*4)
    qt = QImage()
    assert qt.loadFromData(data)
    qt = qt.convertToFormat(QImage.Format.Format_RGBA8888)
    mismatch = 0
    for y in range(height):
        row = raw[y * width * 4 : (y + 1) * width * 4]
        for x in range(width):
            qr = qt.pixelColor(x, y)
            expected = bytes(
                (qr.red(), qr.green(), qr.blue(), qr.alpha())
            )
            if row[x * 4 : x * 4 + 4] != expected:
                mismatch += 1
    assert mismatch == 0


def test_band_reads_match_the_full_read(tmp_path: Path) -> None:
    width, height, bpp = 20, 12, 3
    raw_rows = make_raw_rows(width, height, bpp=bpp)
    png = build_png(width, height, raw_rows, bpp=bpp, filter_type=4)

    whole = StreamingPngReader(png).read_band(0, height)[0]

    reader = StreamingPngReader(png)
    band_a = reader.read_band(0, 5)[0]
    band_b = reader.read_band(5, 4)[0]
    band_c = reader.read_band(9, 10)[0]  # clamped to the page end
    assert band_a + band_b + band_c == whole


# ---------------------------------------------------------------------------
# cursor semantics
# ---------------------------------------------------------------------------


def test_cursor_rejects_rewind_and_rewind_restarts(tmp_path: Path) -> None:
    raw_rows = make_raw_rows(8, 6, bpp=3)
    png = build_png(8, 6, raw_rows, bpp=3, filter_type=0)

    reader = StreamingPngReader(png)
    reader.read_band(0, 3)
    with pytest.raises(StreamingPngError, match="REWIND_REQUIRED"):
        reader.read_band(1, 2)

    reader.rewind()
    raw, _w, _h, _c = reader.read_band(0, 6)
    assert raw == b"".join(raw_rows)


def test_cursor_advances_without_rewind_between_bands() -> None:
    raw_rows = make_raw_rows(8, 6, bpp=3)
    reader = StreamingPngReader(build_png(8, 6, raw_rows, bpp=3, filter_type=2))
    assert reader.cursor_row == 0
    reader.read_band(0, 2)
    assert reader.cursor_row == 2
    reader.read_band(2, 4)
    assert reader.cursor_row == 6


# ---------------------------------------------------------------------------
# typed unsupported-variant matrix (AC ③)
# ---------------------------------------------------------------------------


def test_variant_matrix_fails_typed() -> None:
    ok = build_png(4, 2, make_raw_rows(4, 2, bpp=3), bpp=3, filter_type=0)

    cases = [
        (b"definitely not a png", "NOT_PNG"),
        (build_png(4, 2, make_raw_rows(4, 2), bpp=3, interlace=1), "INTERLACED"),
        (
            build_png(
                4, 2, make_raw_rows(4, 2), bpp=3, bit_depth=16, colour_type=2
            ),
            "UNSUPPORTED_BIT_DEPTH",
        ),
        (
            build_png(4, 2, None, bpp=3, colour_type=3, with_palette=True),
            "PALETTED",
        ),
        (
            build_png(4, 2, None, bpp=3, colour_type=2)[: 8 + 25],
            "TRUNCATED",
        ),  # signature + full IHDR, no IDAT at all
        (b"", "NOT_PNG"),
    ]
    for index, (data, expected_reason) in enumerate(cases):
        with pytest.raises(StreamingPngError, match=expected_reason):
            StreamingPngReader(data)
    # the well-formed page still reads (matrix sanity)
    assert StreamingPngReader(ok).read_band(0, 2)[2] == 2


# ---------------------------------------------------------------------------
# TASK-045 AC ⑧ (TASK-042 R-01): damaged payload, valid container
# ---------------------------------------------------------------------------


def test_corrupt_idat_payload_fails_typed() -> None:
    """AC ⑧: ``zlib.error`` must not escape as itself.

    ``zlib.error``'s MRO is ``(zlib.error, Exception)``, so callers guarding
    on ``OSError``/``ValueError`` (the reader ViewModel's graceful fallback)
    never caught it: a damaged page crashed the tiling call instead of
    falling back. The failure stays fail-closed either way (no wrong pixels
    are produced) — only its *type* changes.
    """
    width, height, bpp = 16, 8, 3
    raw_rows = make_raw_rows(width, height, bpp=bpp)
    png = bytearray(build_png(width, height, raw_rows, bpp=bpp, filter_type=0))

    marker = png.index(b"IDAT")
    length = struct.unpack_from(">I", png, marker - 4)[0]
    state = 987654321
    for index in range(marker + 4, marker + 4 + length):
        state = (state * 1103515245 + 12345) & 0x7FFFFFFF
        png[index] = state & 0xFF

    reader = StreamingPngReader(bytes(png))
    with pytest.raises(StreamingPngError) as caught:
        reader.read_band(0, height)
    assert caught.value.reason == "CORRUPT_DATA"

    # the whole point of the typed error: the callers' guard now sees it
    assert issubclass(StreamingPngError, ValueError)


# ---------------------------------------------------------------------------
# TASK-045 AC ⑨ (TASK-042 R-02): measured memory composition
# ---------------------------------------------------------------------------


def _largest_idat_chunk(data: bytes) -> int:
    offset, largest = 8, 0
    while offset + 8 <= len(data):
        length = struct.unpack_from(">I", data, offset)[0]
        if data[offset + 4 : offset + 8] == b"IDAT":
            largest = max(largest, length)
        offset += 12 + length
    return largest


@pytest.mark.parametrize(
    ("height", "rows_per_chunk"),
    [(10000, 10000), (10000, 1000)],
    ids=["single-idat", "banded-idat"],
)
def test_band_read_peak_composition(
    tmp_path: Path, height: int, rows_per_chunk: int
) -> None:
    """AC ⑨ (TASK-042 R-02): peak = resident source + 2 × largest IDAT chunk
    + O(decode band) — **measured**, with both terms visible.

    The compressed source is read whole by the rasterizer, and ``_pump`` holds
    the current IDAT chunk plus the decompressor's ``unconsumed_tail``, so the
    chunk term counts twice. "Peak ≈ one decode window" was never true: with a
    single-IDAT encoder the chunk term *is* the whole payload (measured at
    400x20000: 48 MB added for a 24 MB source = 46× the 1 MB band), while a
    libpng-style banded encoder brings it back to a few band widths
    (verification/TASK-045/memory-and-fixture-probe.txt).
    """
    import tracemalloc

    from infrastructure.imaging.webtoon_tiles import TiledPageRasterizer

    width = 400
    source = tmp_path / f"noise-{rows_per_chunk}.png"
    _write_incompressible_png(source, width, height, rows_per_chunk=rows_per_chunk)
    data = source.read_bytes()
    source_bytes = len(data)
    largest_chunk = _largest_idat_chunk(data)
    whole_page_raw = width * height * 3
    assert source_bytes > whole_page_raw // 2, "fixture must not compress away"

    tracemalloc.start()
    rasterizer = TiledPageRasterizer(
        source, cache_dir=tmp_path / "tiles", tile_height=800, overlap=64
    )
    construction_peak = tracemalloc.get_traced_memory()[1]
    files = rasterizer.ensure_viewport(0, 800)
    read_peak = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()

    assert len(files) == 2  # tile 0 + one prefetch
    band_bytes = (800 + 64) * width * 3  # decoded window (RGB), overlap included
    added = read_peak - source_bytes

    # 1) the compressed source is resident for the object's lifetime
    assert construction_peak >= source_bytes
    # 2) one band read adds the chunk pair plus a bounded multiple of the band
    assert added <= 2 * largest_chunk + 6 * band_bytes, (
        f"source={source_bytes} largest_idat={largest_chunk} band={band_bytes} "
        f"added={added}"
    )
    # 3) the band term is real and smaller than the page: the page is never
    #    materialised as pixels (only the compressed chunk pair is ever copied)
    assert 6 * band_bytes < whole_page_raw
    if rows_per_chunk < height:
        assert added < source_bytes


def _write_incompressible_png(
    path: Path, width: int, height: int, *, rows_per_chunk: int | None = None
) -> None:
    """Write a PNG whose payload is random (so it really is ~raw-size)."""
    import random

    stride = width * 3 + 1  # filter byte + RGB row
    payload = bytearray(random.Random(20260918).randbytes(stride * height))
    payload[0::stride] = b"\x00" * height  # filter 0 on every scanline

    def chunk(tag: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    with open(path, "wb") as handle:
        handle.write(b"\x89PNG\r\n\x1a\n")
        handle.write(
            chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        )
        compressor = zlib.compressobj(1)
        block = rows_per_chunk or height
        for start in range(0, height, block):
            data = compressor.compress(
                bytes(payload[start * stride : (start + block) * stride])
            )
            if data:
                handle.write(chunk(b"IDAT", data))
        handle.write(chunk(b"IDAT", compressor.flush()))
        handle.write(chunk(b"IEND", b""))


# ---------------------------------------------------------------------------
# TASK-045 AC ⑪ (TASK-042 R-04): real encoder × oversized page
# ---------------------------------------------------------------------------


def row_bytes(page_y: int, width: int) -> bytes:
    return bytes(((page_y * 7) % 256, (page_y * 13) % 256, (page_y * 29) % 256)) * width


def test_qt_encoded_oversized_page_bands_match_qt_pixels(tmp_path: Path) -> None:
    """AC ⑪: 1600x20000 (≈128 MB rgb32 — below Qt's ~300 MB failure point)
    written by a **real encoder** (libpng via QImage.save), then read band by
    band and compared byte-for-byte against Qt's own pixels.

    TASK-042 left this gap: the oversized fixture was produced by the test's
    own stdlib writer (filter 0), so no real encoder's filter choices were
    ever exercised at size.
    """
    from PySide6.QtGui import QImage

    width, height = 1600, 20000
    payload = bytearray()
    for page_y in range(height):
        payload += row_bytes(page_y, width)
    raw = bytes(payload)

    image = QImage(raw, width, height, width * 3, QImage.Format.Format_RGB888)
    assert not image.isNull()
    path = tmp_path / "qt-large.png"
    # libpng's fastest setting: this fixture only has to be *really* encoded,
    # not small — full compression would add ~10 s per suite run.
    assert image.save(str(path), "PNG", 1), "Qt failed to encode the fixture"

    data = path.read_bytes()
    reader = StreamingPngReader(data)
    assert (reader.width, reader.height) == (width, height)
    assert reader.bytes_per_pixel == 3

    # rows 500..2000: a non-zero start, and small enough that the forward
    # scan (pure-Python unfilter of libpng's Average/Paeth rows) stays cheap —
    # reading from row 12000 would scan 14000 rows and take ~16 s.
    start, count = 500, 1500
    band, band_width, band_height, channels = reader.read_band(start, count)
    assert (band_width, band_height, channels) == (width, count, 3)

    qt = QImage(str(path))
    assert not qt.isNull()
    assert (qt.width(), qt.height()) == (width, height)
    qt = qt.convertToFormat(QImage.Format.Format_RGB888)
    stride = qt.bytesPerLine()
    assert stride == width * 3  # tightly packed → the band is one contiguous slice
    bits = qt.constBits()
    expected = bytes(bits[start * stride : (start + count) * stride])
    assert band == expected

    # the pixel comparison is meaningful: neighbouring rows differ
    assert expected[:3] != expected[stride : stride + 3]
