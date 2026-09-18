"""TASK-045 post-hoc review, target 1 (ZCode): F-4 crop equivalence on
multi-filter pages.

The shipped F-4 test (``test_materialised_tiles_carry_exactly_their_declared_band``)
pins the crop on a hand-written **filter-0** page only (the reviewer probe had
the same gap, self-declared in the review brief). This probe re-verifies the
same three assertions on pages whose scanlines are encoded with *mixed*
filters:

  1. every tile file is exactly ``content_height`` tall (the declared band);
  2. every tile row equals the corresponding page row, pixel for pixel;
  3. the concatenation of all tile rows is the whole page (no row repeated,
     none missing).

Suites:

- ``a``: a real Qt/libpng-encoded page (800x4000 RGB) whose content is zoned
  to push libpng towards different per-row filters (gradient -> Sub, vertical
  repeat -> Up, smooth blend -> Average/Paeth, noise -> None/Sub). The actual
  filter-type histogram is recovered from the encoded file and must show >= 3
  distinct filter types, else the probe fails itself (the page did not
  exercise the claim). Ground truth = the Qt decoder.
- ``b``: hand-encoded pages (RGB / RGBA / Gray / Gray+Alpha) whose rows cycle
  deterministically through filters 0,1,2,3,4 - guaranteeing every unfilter
  branch crosses the crop boundary. Ground truth = the construction matrix;
  tile files are decoded with a minimal filter-0 PNG reader (tiles are
  written by the production ``_encode_png``, always filter 0).
- ``c``: behaviour record (not pass/fail): out-of-range ``read_band`` calls
  (OUT_OF_RANGE vs silent truncation) and the R-004 short-read guard not
  firing on well-formed pages (implied by suites a/b completing).

Run (from any checkout of the code under test):
    set PYTHONPATH=<src> && python f4_multifilter_probe.py [--suite all|a|b|c]

Discriminating power: on 6ea3dd3 (pre-F-4) suites a and b must exit non-zero -
tile files there hold the whole decode window (content band + overlap), so the
height assertion and the row-offset assertion both break.
"""

from __future__ import annotations

import argparse
import struct
import sys
import zlib
from pathlib import Path

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
FILTER_NAMES = {0: "None", 1: "Sub", 2: "Up", 3: "Average", 4: "Paeth"}


# ---------------------------------------------------------------------------
# minimal PNG tooling (probe-local; no dependency on the code under test)
# ---------------------------------------------------------------------------


def _chunks(data: bytes):
    offset = 8
    while offset + 8 <= len(data):
        length = struct.unpack_from(">I", data, offset)[0]
        tag = data[offset + 4 : offset + 8]
        body = data[offset + 8 : offset + 8 + length]
        yield tag, body
        offset += 12 + length


def _inflate_idat(png_bytes: bytes) -> bytes:
    """Concatenate every IDAT chunk, then decompress once."""
    compressed = bytearray()
    for tag, body in _chunks(png_bytes):
        if tag == b"IDAT":
            compressed += body
    return zlib.decompress(bytes(compressed))


def filter_histogram(png_bytes: bytes) -> dict[int, int]:
    """Recover the per-row filter types of an 8-bit non-interlaced PNG."""
    ihdr = next(body for tag, body in _chunks(png_bytes) if tag == b"IHDR")
    width, height, depth, colour = struct.unpack_from(">IIBB", ihdr)
    assert depth == 8, f"probe assumes 8-bit, got {depth}"
    channels = {0: 1, 2: 3, 4: 2, 6: 4}[colour]
    raw = _inflate_idat(png_bytes)
    stride = width * channels
    histogram: dict[int, int] = {}
    for row in range(height):
        offset = row * (stride + 1)
        ftype = raw[offset]
        histogram[ftype] = histogram.get(ftype, 0) + 1
    return histogram


def decode_filter0_png(png_bytes: bytes) -> tuple[int, int, int, bytes]:
    """Decode a filter-0, single-IDAT PNG (the shape ``_encode_png`` writes).

    Returns ``(width, height, channels, raw_rows)`` with ``raw_rows`` the
    concatenation of the reconstructed scanlines.
    """
    ihdr = next(body for tag, body in _chunks(png_bytes) if tag == b"IHDR")
    width, height, depth, colour = struct.unpack_from(">IIBB", ihdr)
    assert depth == 8 and colour in (0, 2, 4, 6), "unexpected tile shape"
    channels = {0: 1, 2: 3, 4: 2, 6: 4}[colour]
    raw = _inflate_idat(png_bytes)
    stride = width * channels
    out = bytearray()
    for row in range(height):
        offset = row * (stride + 1)
        assert raw[offset] == 0, "tile rows are written with filter 0"
        out += raw[offset + 1 : offset + 1 + stride]
    return width, height, channels, bytes(out)


def paeth(a: int, b: int, c: int) -> int:
    p = a + b - c
    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    if pb <= pc:
        return b
    return c


def encode_mixed_filter_png(
    raw_rows: list[bytes], width: int, colour_type: int, filters: list[int]
) -> bytes:
    """Encode ``raw_rows`` (8-bit, non-interlaced) with a per-row filter choice.

    ``filters[y]`` is the forward filter for row ``y``; bpp follows the
    colour type exactly as in the PNG spec.
    """
    channels = {0: 1, 2: 3, 4: 2, 6: 4}[colour_type]
    bpp = channels
    stride = width * channels

    def chunk(tag: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    scanlines = bytearray()
    prev = bytes(stride)
    for y, raw in enumerate(raw_rows):
        ftype = filters[y]
        cur = raw
        if ftype == 0:
            filtered = cur
        elif ftype == 1:  # Sub
            filtered = bytes(
                (cur[i] - (cur[i - bpp] if i >= bpp else 0)) & 0xFF
                for i in range(stride)
            )
        elif ftype == 2:  # Up
            filtered = bytes((cur[i] - prev[i]) & 0xFF for i in range(stride))
        elif ftype == 3:  # Average
            filtered = bytes(
                (
                    cur[i]
                    - (
                        ((cur[i - bpp] if i >= bpp else 0) + prev[i]) >> 1
                    )
                )
                & 0xFF
                for i in range(stride)
            )
        elif ftype == 4:  # Paeth
            filtered = bytes(
                (
                    cur[i]
                    - paeth(
                        cur[i - bpp] if i >= bpp else 0,
                        prev[i],
                        prev[i - bpp] if i >= bpp else 0,
                    )
                )
                & 0xFF
                for i in range(stride)
            )
        else:
            raise ValueError(ftype)
        scanlines += bytes([ftype]) + filtered
        prev = raw
    ihdr = struct.pack(">IIBBBBB", width, len(raw_rows), 8, colour_type, 0, 0, 0)
    return b"".join(
        (
            PNG_SIGNATURE,
            chunk(b"IHDR", ihdr),
            chunk(b"IDAT", zlib.compress(bytes(scanlines), 6)),
            chunk(b"IEND", b""),
        )
    )


# ---------------------------------------------------------------------------
# suites
# ---------------------------------------------------------------------------


def build_qt_page(path: Path, width: int = 800, height: int = 4000) -> None:
    """Write a Qt-encoded RGB page whose zones push libpng across filters."""
    from PySide6.QtGui import QImage

    stride = width * 3
    buf = bytearray(stride * height)
    for y in range(height):
        row = y * stride
        if y < 1000:  # horizontal gradient -> Sub territory
            for x in range(width):
                buf[row + x * 3] = (x * 255 // width) & 0xFF
                buf[row + x * 3 + 1] = (x * 137 // width) & 0xFF
                buf[row + x * 3 + 2] = (x * 91 // width) & 0xFF
        elif y < 2000:  # vertical repeat -> Up territory
            base = bytes((x * 97 // width) & 0xFF for x in range(width))
            buf[row : row + stride] = base * 3  # same row content every time
        elif y < 3000:  # smooth blend -> Average/Paeth territory
            for x in range(width):
                buf[row + x * 3] = (y + x) & 0xFF
                buf[row + x * 3 + 1] = (y * 2 + x) & 0xFF
                buf[row + x * 3 + 2] = (y + x // 2) & 0xFF
        else:  # deterministic noise -> filter-agnostic high entropy
            seed = (y * 2654435761) & 0xFFFFFFFF
            for x in range(width):
                seed = (seed * 1103515245 + 12345) & 0xFFFFFFFF
                buf[row + x * 3] = (seed >> 16) & 0xFF
                buf[row + x * 3 + 1] = (seed >> 8) & 0xFF
                buf[row + x * 3 + 2] = seed & 0xFF
    image = QImage(bytes(buf), width, height, stride, QImage.Format.Format_RGB888)
    if not image.save(str(path), "PNG"):
        raise SystemExit("Qt refused to save the probe page")


def qt_rows_rgb(path: Path) -> list[bytes]:
    """Ground-truth rows via the Qt decoder (production render surface)."""
    from PySide6.QtGui import QImage

    image = QImage(str(path))
    assert not image.isNull(), f"Qt could not decode {path}"
    image = image.convertToFormat(QImage.Format.Format_RGB888)
    stride = image.bytesPerLine()
    data = bytes(image.constBits())
    return [
        data[y * stride : y * stride + image.width() * 3]
        for y in range(image.height())
    ]


def suite_a() -> bool:
    from infrastructure.imaging.webtoon_tiles import TiledPageRasterizer

    work = Path(__file__).parent / "_probe_a_work"
    work.mkdir(parents=True, exist_ok=True)
    page_path = work / "qt-page.png"
    build_qt_page(page_path)

    histogram = filter_histogram(page_path.read_bytes())
    kinds = sorted(histogram)
    print(f"[a] Qt page filter histogram: "
          f"{{{', '.join(f'{FILTER_NAMES[k]}: {v}' for k, v in sorted(histogram.items()))}}}")
    if len(kinds) < 3:
        print(f"[a] FAIL(self): the Qt page only exercised {len(kinds)} filter "
              f"types {kinds}; the multi-filter claim needs >= 3")
        return False

    page_rows = qt_rows_rgb(page_path)
    width, height = 800, 4000
    rasterizer = TiledPageRasterizer(
        page_path, cache_dir=work / "tiles", tile_height=1500, overlap=64
    )
    assert rasterizer.page_size == (width, height)

    ok = True
    stitched: list[bytes] = []
    for tile in rasterizer.grid.tiles:
        tile_bytes = rasterizer.tile_file(tile.index).read_bytes()
        t_width, t_height, t_channels, raw = decode_filter0_png(tile_bytes)
        expected_rows = page_rows[tile.content_top : tile.content_bottom]
        actual_rows = [
            raw[i * t_width * t_channels : (i + 1) * t_width * t_channels]
            for i in range(t_height)
        ]
        if t_width != width or t_channels != 3:
            print(f"[a] tile {tile.index}: unexpected shape "
                  f"{t_width}x{t_height}x{t_channels}")
            ok = False
        if t_height != tile.content_height:
            print(f"[a] tile {tile.index}: file height {t_height} != declared "
                  f"content_height {tile.content_height} (top {tile.content_top})")
            ok = False
        if actual_rows != expected_rows:
            first_bad = next(
                (i for i, (g, e) in enumerate(zip(actual_rows, expected_rows)) if g != e),
                min(len(actual_rows), len(expected_rows)),
            )
            print(f"[a] tile {tile.index}: row mismatch, first bad row {first_bad} "
                  f"(rows {len(actual_rows)} vs expected {len(expected_rows)})")
            ok = False
        stitched.extend(actual_rows)
    if stitched != page_rows:
        print(f"[a] FAIL: tile concatenation != page rows "
              f"({len(stitched)} rows vs {height})")
        ok = False
    print(f"[a] crop equivalence on the Qt multi-filter page: "
          f"{'OK' if ok else 'FAILED'}")
    return ok


def suite_b() -> bool:
    from infrastructure.imaging.webtoon_tiles import TiledPageRasterizer

    work = Path(__file__).parent / "_probe_b_work"
    work.mkdir(parents=True, exist_ok=True)
    width, height = 100, 450
    tile_height, overlap = 90, 13
    ok = True
    for colour_type, label in ((2, "RGB"), (6, "RGBA"), (0, "Gray"), (4, "Gray+Alpha")):
        channels = {0: 1, 2: 3, 4: 2, 6: 4}[colour_type]
        stride = width * channels
        # deterministic construction matrix; filters cycle 0,1,2,3,4 per row
        raw_rows = [
            bytes((y * 31 + i * 7) & 0xFF for i in range(stride))
            for y in range(height)
        ]
        filters = [y % 5 for y in range(height)]
        png = encode_mixed_filter_png(raw_rows, width, colour_type, filters)
        histogram = filter_histogram(png)
        page_path = work / f"mixed-{label}.png"
        page_path.write_bytes(png)
        assert histogram.get(0, 0) < height, "filters must not all collapse to 0"

        rasterizer = TiledPageRasterizer(
            page_path,
            cache_dir=work / f"tiles-{label}",
            tile_height=tile_height,
            overlap=overlap,
        )
        assert rasterizer.page_size == (width, height)
        stitched: list[bytes] = []
        for tile in rasterizer.grid.tiles:
            t_width, t_height, t_channels, raw = decode_filter0_png(
                rasterizer.tile_file(tile.index).read_bytes()
            )
            expected = b"".join(
                raw_rows[y] for y in range(tile.content_top, tile.content_bottom)
            )
            if (t_width, t_channels) != (width, channels):
                print(f"[b:{label}] tile {tile.index}: shape {t_width}x{t_channels} "
                      f"!= {width}x{channels}")
                ok = False
            if t_height != tile.content_height:
                print(f"[b:{label}] tile {tile.index}: file height {t_height} != "
                      f"declared {tile.content_height} (top {tile.content_top})")
                ok = False
            if raw != expected:
                print(f"[b:{label}] tile {tile.index}: pixels != page rows "
                      f"[{tile.content_top}, {tile.content_bottom})")
                ok = False
            stitched.append(raw)
        if b"".join(stitched) != b"".join(raw_rows):
            print(f"[b:{label}] FAIL: tile concatenation != page")
            ok = False
        print(f"[b:{label}] filters={dict(sorted(histogram.items()))} tiles="
              f"{rasterizer.grid.tile_count}: {'OK' if ok else 'FAILED'}")
    return ok


def suite_c() -> bool:
    """Behaviour record: out-of-range read_band; R-004 stays silent on good pages."""
    from infrastructure.imaging.streaming_png import (
        StreamingPngError,
        StreamingPngReader,
    )

    width, height = 20, 30
    raw_rows = [bytes((y * 5 + i) & 0xFF for i in range(width * 3)) for y in range(height)]
    png = encode_mixed_filter_png(raw_rows, width, 2, [y % 5 for y in range(height)])
    reader = StreamingPngReader(png)
    ok = True
    try:
        reader.read_band(height, 10)
        print("[c] read_band(past EOF) returned silently - no OUT_OF_RANGE")
        ok = False
    except StreamingPngError as error:
        print(f"[c] read_band(past EOF) -> {error.reason} (typed)")
    reader.rewind()
    raw, w, h, ch = reader.read_band(height - 5, 100)
    print(f"[c] read_band(height-5, 100) -> {h} rows (silent clamp to EOF: "
          f"{'yes' if h == 5 else 'no'}) - callers must self-check "
          f"(production _decode does via R-004)")
    if h != 5:
        print("[c] unexpected clamp result")
        ok = False
    print(f"[c] behaviour record {'consistent' if ok else 'INCONSISTENT'}")
    return ok


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite", default="all", choices=["all", "a", "b", "c"])
    args = parser.parse_args()
    results: dict[str, bool] = {}
    if args.suite in ("all", "a"):
        results["a"] = suite_a()
    if args.suite in ("all", "b"):
        results["b"] = suite_b()
    if args.suite in ("all", "c"):
        results["c"] = suite_c()
    for name, ok in results.items():
        print(f"suite {name}: {'OK' if ok else 'FAILED'}")
    print(f"overall: {'OK' if all(results.values()) else 'FAILED'}")
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
