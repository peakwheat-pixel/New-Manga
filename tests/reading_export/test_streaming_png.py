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
