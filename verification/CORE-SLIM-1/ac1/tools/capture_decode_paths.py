"""CORE-SLIM-1 / AC1 — capture the Qt decode/pixel paths BEFORE and AFTER the
PySide6 removal, so the replacement can be proven pixel-equivalent.

Two implementations, one harness:

  --impl qt      current code (``QtImageDecoder`` + the QImage pixel helpers)
  --impl pillow  the Pillow/pypdfium2 replacement (``PillowImageDecoder`` +
                 the Pillow pixel helpers)

Outputs land under ``verification/CORE-SLIM-1/ac1/``:

  fixtures/          deterministic decode inputs (images + a 2-page PDF)
  qt/                Qt reference results (JSON + raw/PNG artefacts)
  pillow/            replacement results (same shape)
  comparison.json    machine comparison produced by ``--compare``

The pixel-path captures mirror the exact transformations of
``bootstrap/core_assembly.py`` (``page_frame`` -> RGB32/BGRA bytes,
``region_crop`` -> RGB PNG, ``page_png`` -> PNG, ``_render_content_decoder`` ->
PNG from an rgb32 buffer). They mirror rather than constructing the real
``_ManagedPageImageSource`` because that object needs a live SQLite repository;
the real wiring is covered by the existing unit tests
(``tests/providers/test_bootstrap_providers.py``,
``tests/security/test_p09_managed_read_root_trust.py``) which stay green.

Usage (from the worktree root):
    python verification/CORE-SLIM-1/ac1/tools/capture_decode_paths.py --impl qt
    python verification/CORE-SLIM-1/ac1/tools/capture_decode_paths.py --impl pillow
    python verification/CORE-SLIM-1/ac1/tools/capture_decode_paths.py --compare
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import struct
import sys
import zlib
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve()
REPO_ROOT = HERE.parents[4]
SRC_ROOT = REPO_ROOT / "src"
AC1_ROOT = REPO_ROOT / "verification" / "CORE-SLIM-1" / "ac1"
FIXTURES = AC1_ROOT / "fixtures"

sys.path.insert(0, str(SRC_ROOT))


# ---------------------------------------------------------------------------
# deterministic fixtures (no third-party writer needed for the PDF)
# ---------------------------------------------------------------------------
def _thin_png(width: int, height: int, rows: int | None = None) -> bytes:
    """A tiny PNG that declares a huge size (same trick as the product tests).

    ``rows=None`` emits a single full transparent scanline repeated via zlib
    compression; ``rows=k`` emits only ``k`` scanlines so a declared-huge image
    stays a few hundred bytes on disk.
    """
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


def _minimal_pdf(n_pages: int = 2) -> bytes:
    """A minimal valid multi-page PDF (same construction as the product tests)."""
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


def build_fixtures() -> dict[str, Path]:
    from PIL import Image

    FIXTURES.mkdir(parents=True, exist_ok=True)
    made: dict[str, Path] = {}

    def save(name: str, image: "Image.Image", **kwargs: Any) -> None:
        path = FIXTURES / name
        image.save(path, **kwargs)
        made[name] = path

    save("basic.png", Image.new("RGB", (11, 7), (10, 20, 30)))
    save("plain.bmp", Image.new("RGB", (20, 10), (200, 100, 50)))

    gradient = Image.new("RGB", (64, 48))
    for y in range(48):
        for x in range(64):
            gradient.putpixel((x, y), (x * 4 % 256, y * 5 % 256, (x + y) * 3 % 256))
    save("photo.jpg", gradient, quality=92)

    palette = Image.new("P", (24, 16))
    palette.putpalette([i % 256 for i in range(768)])
    save("palette.png", palette)

    rgba = Image.new("RGBA", (40, 30), (12, 34, 56, 128))
    save("alpha.png", rgba)

    page_a = Image.new("RGB", (40, 30), (255, 0, 0))
    page_b = Image.new("RGB", (40, 30), (0, 0, 255))
    page_a.save(FIXTURES / "multi.tiff", save_all=True, append_images=[page_b])
    made["multi.tiff"] = FIXTURES / "multi.tiff"

    save("still.webp", gradient, quality=90)

    frames = [
        Image.new("RGB", (32, 24), color)
        for color in ((255, 0, 0), (0, 255, 0), (0, 0, 255))
    ]
    frames[0].save(
        FIXTURES / "anim.webp", save_all=True, append_images=frames[1:], duration=120
    )
    made["anim.webp"] = FIXTURES / "anim.webp"

    gif_frames = [
        Image.new("RGB", (48, 32), color)
        for color in ((250, 10, 10), (10, 250, 10), (10, 10, 250), (90, 90, 90))
    ]
    gif_frames[0].save(
        FIXTURES / "anim.gif", save_all=True, append_images=gif_frames[1:], duration=100
    )
    made["anim.gif"] = FIXTURES / "anim.gif"

    avif = Image.new("RGB", (32, 24), (5, 200, 90))
    try:
        avif.save(FIXTURES / "still.avif")
        made["still.avif"] = FIXTURES / "still.avif"
    except Exception as error:  # Pillow built without AVIF support
        (FIXTURES / "still.avif.unsupported.txt").write_text(str(error), encoding="utf-8")

    (FIXTURES / "long.png").write_bytes(_thin_png(690, 4000))
    made["long.png"] = FIXTURES / "long.png"
    (FIXTURES / "declared-huge.png").write_bytes(_thin_png(8192, 65536, rows=1))
    made["declared-huge.png"] = FIXTURES / "declared-huge.png"
    (FIXTURES / "book.pdf").write_bytes(_minimal_pdf(2))
    made["book.pdf"] = FIXTURES / "book.pdf"

    manifest = {
        name: {
            "bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
        for name, path in sorted(made.items())
    }
    (AC1_ROOT / "fixtures-manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    return made


# ---------------------------------------------------------------------------
# Qt implementation (the code under replacement)
# ---------------------------------------------------------------------------
def _qt_frame_bytes(data: bytes) -> dict[str, Any]:
    from PySide6.QtGui import QImage

    image = QImage.fromData(data)
    if image.isNull():
        raise RuntimeError("qt: page image not decodable")
    rgb = image.convertToFormat(QImage.Format.Format_RGB32)
    raw = bytes(rgb.constBits())
    if len(raw) != rgb.width() * rgb.height() * 4:
        # constBits() may expose padding; normalise row-stride to tight rows.
        stride = rgb.bytesPerLine()
        raw = b"".join(
            raw[y * stride : y * stride + rgb.width() * 4] for y in range(rgb.height())
        )
    return {"width": rgb.width(), "height": rgb.height(), "bytes": raw}


def _qt_page_png(data: bytes) -> bytes:
    from PySide6.QtCore import QBuffer, QIODevice
    from PySide6.QtGui import QImage

    image = QImage.fromData(data)
    if image.isNull():
        raise RuntimeError("qt: page image not decodable")
    buffer = QBuffer()
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    if not image.save(buffer, "PNG"):
        raise RuntimeError("qt: PNG encode failed")
    return bytes(buffer.data())


def _qt_crop_png(data: bytes, rect: tuple[int, int, int, int]) -> bytes:
    from PySide6.QtCore import QBuffer, QIODevice, QRect
    from PySide6.QtGui import QImage

    image = QImage.fromData(data)
    x, y, width, height = rect
    clipped = QRect(x, y, width, height).intersected(
        QRect(0, 0, image.width(), image.height())
    )
    if clipped.isEmpty():
        raise RuntimeError("qt: empty crop")
    crop = image.copy(clipped).convertToFormat(QImage.Format.Format_RGB888)
    buffer = QBuffer()
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    if not crop.save(buffer, "PNG"):
        raise RuntimeError("qt: crop PNG encode failed")
    return bytes(buffer.data())


def _qt_bridge_png(raw_rgb32: bytes, width: int, height: int) -> bytes:
    from PySide6.QtCore import QBuffer, QIODevice
    from PySide6.QtGui import QImage

    image = QImage(raw_rgb32, width, height, width * 4, QImage.Format.Format_RGB32)
    if image.isNull():
        raise RuntimeError("qt: frame buffer not decodable")
    buffer = QBuffer()
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    if not image.save(buffer, "PNG"):
        raise RuntimeError("qt: bridge PNG encode failed")
    return bytes(buffer.data())


def _qt_pdf_pages(pdf: bytes, scale: float = 2.0) -> list[dict[str, Any]]:
    from infrastructure.importing import PdfiumDocumentRaster

    handle = PdfiumDocumentRaster(scale=scale).open(pdf)
    try:
        pages = []
        for index in range(handle.page_count):
            rendered = handle.render_page(index)
            pages.append(
                {
                    "width": rendered.width,
                    "height": rendered.height,
                    "png": rendered.png,
                }
            )
        return pages
    finally:
        handle.close()


# ---------------------------------------------------------------------------
# Pillow implementation (the replacement)
# ---------------------------------------------------------------------------
def _pillow_open(data: bytes):
    from PIL import Image

    return Image.open(io.BytesIO(data))


def _pillow_frame_bytes(data: bytes) -> dict[str, Any]:
    image = _pillow_open(data)
    image.load()
    rgba = image.convert("RGBA")
    # Format_RGB32 is 0xffRRGGBB in memory == little-endian BGRA with the
    # alpha byte FORCED to 0xff (Qt's RGB32 conversion drops alpha); the
    # consumers reshape (h, w, 4) and drop the alpha channel.
    rgba.putalpha(255)
    return {
        "width": rgba.width,
        "height": rgba.height,
        "bytes": rgba.tobytes("raw", "BGRA"),
    }


def _pillow_page_png(data: bytes) -> bytes:
    image = _pillow_open(data)
    image.load()
    out = io.BytesIO()
    if image.mode not in ("RGB", "RGBA", "L", "LA"):
        image = image.convert("RGB")
    image.save(out, format="PNG")
    return out.getvalue()


def _pillow_crop_png(data: bytes, rect: tuple[int, int, int, int]) -> bytes:
    image = _pillow_open(data)
    image.load()
    x, y, width, height = rect
    left = max(0, x)
    top = max(0, y)
    right = min(image.width, x + width)
    bottom = min(image.height, y + height)
    if right <= left or bottom <= top:
        raise RuntimeError("pillow: empty crop")
    crop = image.convert("RGB").crop((left, top, right, bottom))
    out = io.BytesIO()
    crop.save(out, format="PNG")
    return out.getvalue()


def _pillow_bridge_png(raw_rgb32: bytes, width: int, height: int) -> bytes:
    from PIL import Image

    image = Image.frombuffer("RGBA", (width, height), raw_rgb32, "raw", "BGRA", 0, 1)
    rgb = image.convert("RGB")
    out = io.BytesIO()
    rgb.save(out, format="PNG")
    return out.getvalue()


def _pillow_pdf_pages(pdf: bytes, scale: float = 2.0) -> list[dict[str, Any]]:
    from infrastructure.importing import PdfiumDocumentRaster

    handle = PdfiumDocumentRaster(scale=scale).open(pdf)
    try:
        pages = []
        for index in range(handle.page_count):
            rendered = handle.render_page(index)
            pages.append(
                {
                    "width": rendered.width,
                    "height": rendered.height,
                    "png": rendered.png,
                }
            )
        return pages
    finally:
        handle.close()


# ---------------------------------------------------------------------------
# record/compare plumbing
# ---------------------------------------------------------------------------
IMAGE_CASES = [
    "basic.png",
    "plain.bmp",
    "photo.jpg",
    "palette.png",
    "alpha.png",
    "multi.tiff",
    "still.webp",
    "anim.webp",
    "anim.gif",
    "still.avif",
    "long.png",
    "declared-huge.png",
]

PIXEL_CASES = ["basic.png", "photo.jpg", "alpha.png", "palette.png"]


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def capture(impl: str) -> dict[str, Any]:
    fixtures = build_fixtures()
    out_dir = AC1_ROOT / impl
    (out_dir / "pixels").mkdir(parents=True, exist_ok=True)
    (out_dir / "pdf").mkdir(parents=True, exist_ok=True)

    if impl == "qt":
        from infrastructure.importing import QtImageDecoder as Decoder
        frame_bytes = _qt_frame_bytes
        page_png = _qt_page_png
        crop_png = _qt_crop_png
        bridge_png = _qt_bridge_png
        pdf_pages = _qt_pdf_pages
    else:
        from infrastructure.importing import PillowImageDecoder as Decoder
        frame_bytes = _pillow_frame_bytes
        page_png = _pillow_page_png
        crop_png = _pillow_crop_png
        bridge_png = _pillow_bridge_png
        pdf_pages = _pillow_pdf_pages

    decoder = Decoder()
    results: dict[str, Any] = {"impl": impl, "decode": {}, "pixels": {}, "pdf": {}}

    for name in IMAGE_CASES:
        path = fixtures.get(name) or (FIXTURES / name)
        if not path.is_file():
            results["decode"][name] = {"skipped": "fixture unavailable"}
            continue
        data = path.read_bytes()
        entry: dict[str, Any] = {}
        try:
            decoded = decoder.decode(data)
            entry.update(
                {
                    "ok": True,
                    "width": decoded.width,
                    "height": decoded.height,
                    "mime_type": decoded.mime_type,
                }
            )
        except Exception as error:  # noqa: BLE001 - the matrix records the typed failure
            entry.update(
                {"ok": False, "error": type(error).__name__, "detail": str(error)}
            )
        results["decode"][name] = entry

    for name in PIXEL_CASES:
        data = (FIXTURES / name).read_bytes()
        case: dict[str, Any] = {}
        frame = frame_bytes(data)
        (out_dir / "pixels" / f"frame-{name}.raw").write_bytes(frame["bytes"])
        case["frame"] = {
            "width": frame["width"],
            "height": frame["height"],
            "sha256": _sha(frame["bytes"]),
            "bytes": len(frame["bytes"]),
        }
        page = page_png(data)
        (out_dir / "pixels" / f"page-{name}.png").write_bytes(page)
        case["page_png"] = {"sha256": _sha(page), "bytes": len(page)}
        crop = crop_png(data, (3, 2, 20, 10))
        (out_dir / "pixels" / f"crop-{name}.png").write_bytes(crop)
        case["crop_png"] = {"sha256": _sha(crop), "bytes": len(crop)}
        bridge = bridge_png(frame["bytes"], frame["width"], frame["height"])
        (out_dir / "pixels" / f"bridge-{name}.png").write_bytes(bridge)
        case["bridge_png"] = {"sha256": _sha(bridge), "bytes": len(bridge)}
        results["pixels"][name] = case

    pdf_bytes = (FIXTURES / "book.pdf").read_bytes()
    pages = pdf_pages(pdf_bytes)
    pdf_entries = []
    for index, page in enumerate(pages):
        (out_dir / "pdf" / f"page{index}.png").write_bytes(page["png"])
        pdf_entries.append(
            {
                "index": index,
                "width": page["width"],
                "height": page["height"],
                "sha256": _sha(page["png"]),
                "bytes": len(page["png"]),
            }
        )
    results["pdf"] = {"pages": pdf_entries}

    (out_dir / "results.json").write_text(
        json.dumps(results, indent=2), encoding="utf-8"
    )
    return results


def _png_pixels(path: Path) -> tuple[str, int, int, bytes]:
    from PIL import Image

    with Image.open(path) as image:
        image.load()
        rgba = image.convert("RGBA")
        return rgba.mode, rgba.width, rgba.height, rgba.tobytes()


def compare() -> dict[str, Any]:
    qt = json.loads((AC1_ROOT / "qt" / "results.json").read_text(encoding="utf-8"))
    pillow = json.loads(
        (AC1_ROOT / "pillow" / "results.json").read_text(encoding="utf-8")
    )
    report: dict[str, Any] = {
        "impls": {"qt": qt["impl"], "pillow": pillow["impl"]},
        "decode": {},
        "pixels": {},
        "pdf": {},
        "summary": {},
    }

    decode_ok = 0
    decode_total = 0
    for name, qt_entry in qt["decode"].items():
        pillow_entry = pillow["decode"].get(name, {})
        decode_total += 1
        same = (
            qt_entry.get("ok") == pillow_entry.get("ok")
            and qt_entry.get("width") == pillow_entry.get("width")
            and qt_entry.get("height") == pillow_entry.get("height")
            and qt_entry.get("mime_type") == pillow_entry.get("mime_type")
        )
        if same:
            decode_ok += 1
        report["decode"][name] = {
            "equal": same,
            "qt": qt_entry,
            "pillow": pillow_entry,
        }

    pixel_total = 0
    pixel_ok = 0
    for name, qt_case in qt["pixels"].items():
        pillow_case = pillow["pixels"][name]
        case_report: dict[str, Any] = {}
        for artifact in ("frame", "page_png", "crop_png", "bridge_png"):
            pixel_total += 1
            left = qt_case[artifact]
            right = pillow_case[artifact]
            if artifact == "frame":
                equal = left["sha256"] == right["sha256"]
                if not equal:
                    qa = (AC1_ROOT / "qt" / "pixels" / f"frame-{name}.raw").read_bytes()
                    pa = (
                        AC1_ROOT / "pillow" / "pixels" / f"frame-{name}.raw"
                    ).read_bytes()
                    equal = qa == pa
            else:
                suffix = {"page_png": "page", "crop_png": "crop", "bridge_png": "bridge"}[
                    artifact
                ]
                qpath = AC1_ROOT / "qt" / "pixels" / f"{suffix}-{name}.png"
                ppath = AC1_ROOT / "pillow" / "pixels" / f"{suffix}-{name}.png"
                qt_mode, w1, h1, raw1 = _png_pixels(qpath)
                pl_mode, w2, h2, raw2 = _png_pixels(ppath)
                equal = (w1, h1) == (w2, h2) and raw1 == raw2
            if equal:
                pixel_ok += 1
            case_report[artifact] = {
                "pixel_equal": equal,
                "qt_sha256": left["sha256"],
                "pillow_sha256": right["sha256"],
                "byte_identical": left["sha256"] == right["sha256"],
            }
        report["pixels"][name] = case_report

    pdf_total = 0
    pdf_ok = 0
    for qt_page in qt["pdf"]["pages"]:
        index = qt_page["index"]
        pillow_page = pillow["pdf"]["pages"][index]
        qpath = AC1_ROOT / "qt" / "pdf" / f"page{index}.png"
        ppath = AC1_ROOT / "pillow" / "pdf" / f"page{index}.png"
        _, w1, h1, raw1 = _png_pixels(qpath)
        _, w2, h2, raw2 = _png_pixels(ppath)
        equal = (w1, h1) == (w2, h2) and raw1 == raw2
        pdf_total += 1
        if equal:
            pdf_ok += 1
        report["pdf"][f"page{index}"] = {
            "pixel_equal": equal,
            "qt_sha256": qt_page["sha256"],
            "pillow_sha256": pillow_page["sha256"],
            "byte_identical": qt_page["sha256"] == pillow_page["sha256"],
            "width": qt_page["width"],
            "height": qt_page["height"],
        }

    report["summary"] = {
        "decode_matrix_equal": f"{decode_ok}/{decode_total}",
        "pixel_artifacts_equal": f"{pixel_ok}/{pixel_total}",
        "pdf_pages_equal": f"{pdf_ok}/{pdf_total}",
    }
    (AC1_ROOT / "comparison.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--impl", choices=["qt", "pillow"])
    parser.add_argument("--compare", action="store_true")
    args = parser.parse_args()
    if args.compare:
        report = compare()
        print(json.dumps(report["summary"], indent=2))
        for section in ("decode", "pixels", "pdf"):
            bad = [
                key
                for key, value in report[section].items()
                if (
                    value.get("equal") is False
                    or any(
                        isinstance(v, dict) and v.get("pixel_equal") is False
                        for v in (value.values() if isinstance(value, dict) else [])
                    )
                )
            ]
            if bad:
                print(f"MISMATCH {section}: {bad}")
        return 0
    if not args.impl:
        parser.error("--impl or --compare required")
    results = capture(args.impl)
    print(json.dumps({"impl": args.impl, "decode": len(results["decode"])}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
