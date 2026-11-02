"""CORE-SLIM-1: decode format matrix for the Qt-free image decoder.

The PySide6 removal replaced ``QtImageDecoder`` with ``PillowImageDecoder``.
This module locks the capability matrix the product surface exposes
(``SUPPORTED_IMAGE_SUFFIXES``): PNG/JPEG/BMP/TIFF/WebP/GIF (including
multi-frame GIF, animated WebP and multi-page TIFF) plus the PDF raster path.
Fixtures are generated with Pillow itself, so the test needs no Qt and no
binary media assets in the tree.
"""

from __future__ import annotations

import io
import struct
import sys
import zlib
from pathlib import Path

import pytest

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from application.importing.images.ports import ImageDecodeError  # noqa: E402
from infrastructure.importing import PillowImageDecoder  # noqa: E402


def _png(width: int = 12, height: int = 8) -> bytes:
    from PIL import Image

    buffer = io.BytesIO()
    Image.new("RGB", (width, height), (10, 20, 30)).save(buffer, format="PNG")
    return buffer.getvalue()


def _encode(image, fmt: str, **kwargs) -> bytes:
    buffer = io.BytesIO()
    image.save(buffer, format=fmt, **kwargs)
    return buffer.getvalue()


def _gradient(width: int = 24, height: int = 16):
    from PIL import Image

    image = Image.new("RGB", (width, height))
    for y in range(height):
        for x in range(width):
            image.putpixel((x, y), (x * 7 % 256, y * 11 % 256, (x + y) * 5 % 256))
    return image


def _minimal_pdf(n_pages: int = 2) -> bytes:
    objects: dict[int, bytes] = {}
    objects[1] = b"<< /Type /Catalog /Pages 2 0 R >>"
    page_ids: list[int] = []
    next_id = 3
    for index in range(n_pages):
        content_id = next_id
        next_id += 1
        stream = f"BT /F1 24 Tf 72 700 Td (Page {index + 1}) Tj ET".encode()
        objects[content_id] = (
            b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n"
            + stream + b"\nendstream"
        )
        page_id = next_id
        next_id += 1
        page_ids.append(page_id)
        objects[page_id] = (
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            f"/Contents {content_id} 0 R >>"
        ).encode()
    objects[2] = (
        "<< /Type /Pages /Kids ["
        + " ".join(f"{pid} 0 R" for pid in page_ids)
        + f"] /Count {n_pages} >>"
    ).encode()
    out = bytearray(b"%PDF-1.4\n")
    offsets: dict[int, int] = {}
    for number in sorted(objects):
        offsets[number] = len(out)
        out += f"{number} 0 obj\n".encode() + objects[number] + b"\nendobj\n"
    xref = len(out)
    out += f"xref\n0 {len(objects) + 1}\n".encode()
    out += b"0000000000 65535 f \n"
    for number in sorted(objects):
        out += f"{offsets[number]:010d} 00000 n \n".encode()
    out += (
        b"trailer\n<< /Size " + str(len(objects) + 1).encode() + b" /Root 1 0 R >>\n"
        b"startxref\n" + str(xref).encode() + b"\n%%EOF\n"
    )
    return bytes(out)


def _thin_png(width: int, height: int, rows: int | None = None) -> bytes:
    def chunk(kind: bytes, payload: bytes) -> bytes:
        return (
            struct.pack(">I", len(payload))
            + kind
            + payload
            + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
        )

    scanlines = rows if rows is not None else height
    raw = b"".join(b"\x00" + b"\x00\x00\x00\x00" * width for _ in range(scanlines))
    header = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", header)
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b"")
    )


@pytest.mark.parametrize(
    ("name", "payload", "expected_mime", "expected_size"),
    [
        ("png", _png(11, 7), "image/png", (11, 7)),
        ("bmp", _encode(_gradient(20, 10), "BMP"), "image/bmp", (20, 10)),
        ("jpeg", _encode(_gradient(), "JPEG", quality=92), "image/jpeg", (24, 16)),
        ("webp_still", _encode(_gradient(), "WEBP", quality=90), "image/webp", (24, 16)),
        ("tiff_single", _encode(_gradient(), "TIFF"), "image/tiff", (24, 16)),
        ("gif_single", _encode(_gradient(), "GIF"), "image/gif", (24, 16)),
    ],
)
def test_decoder_reports_dimensions_and_mime_for_every_product_format(
    name: str, payload: bytes, expected_mime: str, expected_size: tuple[int, int]
) -> None:
    decoded = PillowImageDecoder().decode(payload)

    assert (decoded.width, decoded.height) == expected_size, name
    assert decoded.mime_type == expected_mime, name


def test_decoder_accepts_multi_frame_gif() -> None:
    from PIL import Image

    frames = [
        Image.new("RGB", (48, 32), color)
        for color in ((250, 10, 10), (10, 250, 10), (10, 10, 250), (90, 90, 90))
    ]
    payload = _encode(
        frames[0], "GIF", save_all=True, append_images=frames[1:], duration=100
    )
    with Image.open(io.BytesIO(payload)) as probe:
        assert getattr(probe, "n_frames", 1) == 4  # the fixture really is animated

    decoded = PillowImageDecoder().decode(payload)

    assert (decoded.width, decoded.height) == (48, 32)
    assert decoded.mime_type == "image/gif"


def test_decoder_accepts_animated_webp() -> None:
    from PIL import Image

    frames = [
        Image.new("RGB", (32, 24), color)
        for color in ((255, 0, 0), (0, 255, 0), (0, 0, 255))
    ]
    payload = _encode(
        frames[0], "WEBP", save_all=True, append_images=frames[1:], duration=120
    )
    with Image.open(io.BytesIO(payload)) as probe:
        assert getattr(probe, "n_frames", 1) == 3

    decoded = PillowImageDecoder().decode(payload)

    assert (decoded.width, decoded.height) == (32, 24)
    assert decoded.mime_type == "image/webp"


def test_decoder_accepts_multi_page_tiff() -> None:
    from PIL import Image

    page_a = Image.new("RGB", (40, 30), (255, 0, 0))
    page_b = Image.new("RGB", (40, 30), (0, 0, 255))
    payload = _encode(page_a, "TIFF", save_all=True, append_images=[page_b])
    with Image.open(io.BytesIO(payload)) as probe:
        assert getattr(probe, "n_frames", 1) == 2
        assert (probe.width, probe.height) == (40, 30)

    decoded = PillowImageDecoder().decode(payload)

    assert (decoded.width, decoded.height) == (40, 30)
    assert decoded.mime_type == "image/tiff"


def test_decoder_accepts_avif_when_pillow_supports_it() -> None:
    # Capability NOTE (CORE-SLIM-1 evidence): the shipped Qt plugin set had no
    # AVIF handler, so AVIF was a declared-but-undecodable suffix before.
    # Pillow 12 decodes it; this is a capability GAIN and the test skips only
    # on a builder whose Pillow lacks the codec.
    from PIL import Image

    try:
        payload = _encode(Image.new("RGB", (32, 24), (5, 200, 90)), "AVIF")
    except Exception as error:  # noqa: BLE001 - codec absent in this Pillow build
        pytest.skip(f"Pillow AVIF encoder unavailable: {error}")

    decoded = PillowImageDecoder().decode(payload)

    assert (decoded.width, decoded.height) == (32, 24)
    assert decoded.mime_type == "image/avif"


def test_decoder_rejects_garbage_with_a_bounded_detail() -> None:
    with pytest.raises(ImageDecodeError) as excinfo:
        PillowImageDecoder().decode(b"not-an-image")

    detail = str(excinfo.value)
    assert detail.strip()
    assert len(detail) <= 303


def test_decoder_fails_closed_above_the_decode_ceiling() -> None:
    # 8192x65536 RGBA = 2048 MiB > the 2047 MiB ceiling; the fail-closed path
    # is typed, bounded and never allocates the buffer.
    with pytest.raises(ImageDecodeError) as excinfo:
        PillowImageDecoder().decode(_thin_png(8192, 65536, rows=1))

    assert "decode ceiling" in str(excinfo.value)


def test_pdf_raster_pages_are_real_png_pages() -> None:
    from PIL import Image

    from infrastructure.importing import PdfiumDocumentRaster

    handle = PdfiumDocumentRaster(scale=2.0).open(_minimal_pdf(2))
    try:
        assert handle.page_count == 2
        sizes = []
        for index in range(handle.page_count):
            rendered = handle.render_page(index)
            with Image.open(io.BytesIO(rendered.png)) as page:
                page.load()
                assert page.size == (rendered.width, rendered.height)
                sizes.append(page.size)
            # a US-Letter page at scale 2 rasterises to ~1224x1584
            assert rendered.width > 1000 and rendered.height > 1000
        assert sizes[0] == sizes[1]
    finally:
        handle.close()


def test_supported_suffixes_still_cover_the_declared_format_surface() -> None:
    from infrastructure.importing import SUPPORTED_IMAGE_SUFFIXES

    assert SUPPORTED_IMAGE_SUFFIXES == frozenset(
        {".avif", ".bmp", ".gif", ".heic", ".heif", ".jpeg", ".jpg",
         ".png", ".tif", ".tiff", ".webp"}
    )
