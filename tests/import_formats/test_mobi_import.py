"""TASK-041 document import: picture-MOBI extraction through the real
``mobi`` binding (user-approved mobi==0.4.1) + real Managed Copy, plus the
typed fail-closed matrix (AC ③).

Containers are built in-process from the raw PalmDB/MOBI layout (self-made
material): record 0 is a 16-byte PalmDoc header + 232-byte MOBI header laid
out the way the binding reads it (``crypto_type`` at record-0 offset 0x0C,
``firstresource`` at 0x6C, no NCX), record 1 is the HTML, the remaining
records are the page images. Pixel-level assertions (the TASK-043 lesson:
dimensions alone cannot see a channel swap or a wrong page order).
"""

from __future__ import annotations

import hashlib
import struct
import sys
from pathlib import Path

import pytest

TESTS_DIR = Path(__file__).resolve().parent
SRC_ROOT = TESTS_DIR.parents[1] / "src"
for entry in (str(TESTS_DIR), str(SRC_ROOT)):
    if entry not in sys.path:
        sys.path.insert(0, entry)

pytest.importorskip("PySide6")

from PySide6.QtCore import QBuffer, QIODevice  # noqa: E402
from PySide6.QtGui import QColor, QImage  # noqa: E402

from application.importing.documents.ports import (  # noqa: E402
    DocumentDecodeError,
    DocumentRaster,
)
from application.importing.documents.service import ImportDocumentsUseCase  # noqa: E402
from application.importing.images.ports import ImportSource  # noqa: E402
from infrastructure.filesystem.managed_storage import ManagedFileStorage  # noqa: E402
from infrastructure.importing import (  # noqa: E402
    ManagedCopyStoreAdapter,
    MobiDocumentRaster,
    PdfiumDocumentRaster,
)
from test_document_import import InMemoryPageSink  # noqa: E402


def _make_jpeg(width: int, height: int, bgr: tuple[int, int, int]) -> bytes:
    image = QImage(width, height, QImage.Format.Format_RGB32)
    image.fill(QColor(*bgr))
    buffer = QBuffer()
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    assert image.save(buffer, "JPG")
    return bytes(buffer.data())


def _decode_png(png: bytes) -> QImage:
    image = QImage()
    assert image.loadFromData(png)
    return image.convertToFormat(QImage.Format.Format_RGB32)


def _assert_colour(actual: QColor, expected: tuple[int, int, int]) -> None:
    """JPEG is lossy: a solid red block decodes as (254,0,0). A ±2
    tolerance still has full discriminative power for the failure this
    guards against (a red/blue channel swap is 254 units away)."""
    for channel, want in zip((actual.red(), actual.green(), actual.blue()), expected):
        assert abs(channel - want) <= 2, (actual.name(), expected)


def _mobi_record0(
    html_len: int,
    *,
    crypto_type: int = 0,
    first_resource: int | None = 2,
) -> bytes:
    """One 248-byte record 0: PalmDoc header + MOBI header, in the layout
    mobi 0.4.1 reads (offsets relative to the record start)."""
    buf = bytearray(0x10 + 0xE8)
    struct.pack_into(">H", buf, 0x00, 1)  # compression: none
    struct.pack_into(">I", buf, 0x04, html_len)
    struct.pack_into(">H", buf, 0x08, 1)  # text records
    struct.pack_into(">H", buf, 0x0A, 4096)
    struct.pack_into(">H", buf, 0x0C, crypto_type)
    buf[0x10:0x14] = b"MOBI"
    struct.pack_into(">I", buf, 0x14, 0xE8)  # MOBI header length
    struct.pack_into(">I", buf, 0x18, 2)  # type: book
    struct.pack_into(">I", buf, 0x1C, 65001)  # utf-8
    struct.pack_into(">I", buf, 0x20, 424242)  # unique id
    struct.pack_into(">I", buf, 0x24, 6)  # version
    for offset in range(0x28, 0x50, 4):
        struct.pack_into(">i", buf, offset, -1)  # no indices
    struct.pack_into(">I", buf, 0x54, 0)  # title offset
    struct.pack_into(">I", buf, 0x58, 0)  # title length
    struct.pack_into(">I", buf, 0x5C, 9)  # language: en
    struct.pack_into(">I", buf, 0x68, 6)  # min version
    if first_resource is not None:
        struct.pack_into(">I", buf, 0x50, first_resource)
        struct.pack_into(">I", buf, 0x6C, first_resource)
    struct.pack_into(">I", buf, 0x80, 0)  # no EXTH
    struct.pack_into(">i", buf, 0xA8, -1)  # DRM offset: none
    struct.pack_into(">H", buf, 0xC0, 0)  # first content record
    struct.pack_into(">H", buf, 0xC2, 1)  # last content record
    struct.pack_into(">i", buf, 0xF4, -1)  # no NCX
    return bytes(buf)


def _pack_pdb(records: list[bytes]) -> bytes:
    header = bytearray()
    header += b"probe manga".ljust(32, b"\x00")
    header += struct.pack(">H", 0)  # attributes
    header += struct.pack(">H", 0)  # version
    header += struct.pack(">III", 0, 0, 0)  # timestamps
    header += struct.pack(">I", 0)  # modification number
    header += struct.pack(">I", 0)  # app info id
    header += struct.pack(">I", 0)  # sort info id
    header += b"BOOK"  # type
    header += b"MOBI"  # creator
    header += struct.pack(">I", 0)  # unique id seed
    header += struct.pack(">I", 0)  # next record list id
    header += struct.pack(">H", len(records))
    offset = 78 + 8 * len(records) + 2
    entries = bytearray()
    for index, record in enumerate(records):
        entries += struct.pack(">I", offset)
        entries += struct.pack(">B", 0)
        entries += struct.pack(">I", index)[1:]
        offset += len(record)
    header += entries
    header += struct.pack(">H", 0)  # padding
    return bytes(header) + b"".join(records)


def picture_mobi(
    images: list[bytes],
    *,
    crypto_type: int = 0,
) -> bytes:
    """A minimal picture MOBI: record 0 header, record 1 html, then images."""
    html = (
        "<html><head></head><body>"
        + "".join(
            f'<div><img recindex="{index:05d}"></div>'
            for index in range(1, len(images) + 1)
        ).encode("utf-8").decode("utf-8")
        + "</body></html>"
    ).encode("utf-8")
    records = [_mobi_record0(len(html), crypto_type=crypto_type), html] + images
    return _pack_pdb(records)


def text_only_mobi() -> bytes:
    """A reflowable text-only MOBI: no image records, no image references."""
    html = b"<html><head></head><body><p>reflowable text</p></body></html>"
    records = [_mobi_record0(len(html), first_resource=2), html]
    return _pack_pdb(records)


class InMemoryRaster(DocumentRaster):
    """A raster double that always reports the given typed failure."""

    def __init__(self, reason: str, detail: str) -> None:
        self._reason = reason
        self._detail = detail

    def open(self, data: bytes):
        raise DocumentDecodeError(self._reason, self._detail)


@pytest.fixture()
def workspace(tmp_path: Path):
    storage = ManagedFileStorage(tmp_path / "managed")
    copy_store = ManagedCopyStoreAdapter(storage, lambda chapter_id: "book-42")
    sink = InMemoryPageSink()
    use_case = ImportDocumentsUseCase(
        PdfiumDocumentRaster(),
        copy_store,
        sink,
        mobi_raster=MobiDocumentRaster(),
    )
    return {"use_case": use_case, "sink": sink, "storage": storage}


def _source(name: str, data: bytes) -> ImportSource:
    return ImportSource(filename=name, data_provider=lambda data=data: data)


def test_picture_mobi_imports_one_managed_page_per_image(workspace) -> None:
    use_case, sink, storage = workspace["use_case"], workspace["sink"], workspace["storage"]
    images = [_make_jpeg(8, 6, (255, 0, 0)), _make_jpeg(9, 7, (0, 255, 0))]

    report = use_case.import_documents(
        "chapter-7", [_source("manga.mobi", picture_mobi(images))]
    )

    assert report.failed == () and report.cancelled is False
    assert len(report.imported) == 2
    assert [item.page.source_order for item in report.imported] == [1, 2]
    first, second = (item.page for item in report.imported)
    assert (first.width, first.height) == (8, 6)
    assert (second.width, second.height) == (9, 7)
    assert first.source_hash == hashlib.sha256(
        Path(storage.absolute_path(first.managed_original_ref)).read_bytes()
    ).hexdigest()
    # pixel-level page order: record order is red then green (the TASK-043
    # lesson — dimensions alone cannot see a channel swap or a page swap)
    _assert_colour(
        _decode_png(
            Path(storage.absolute_path(first.managed_original_ref)).read_bytes()
        ).pixelColor(4, 3),
        (255, 0, 0),
    )
    _assert_colour(
        _decode_png(
            Path(storage.absolute_path(second.managed_original_ref)).read_bytes()
        ).pixelColor(5, 4),
        (0, 255, 0),
    )
    assert len(sink.pages) == 2


def test_duplicate_picture_mobi_skips_like_pdf(workspace) -> None:
    use_case = workspace["use_case"]
    data = picture_mobi([_make_jpeg(8, 6, (255, 0, 0))])

    first = use_case.import_documents("chapter-7", [_source("a.mobi", data)])
    again = use_case.import_documents("chapter-7", [_source("a.mobi", data)])

    assert len(first.imported) == 1
    assert again.imported == ()
    assert again.skipped_duplicates == ("a.mobi",)


def test_drm_mobi_fails_typed_and_leaves_no_data(workspace) -> None:
    use_case, sink = workspace["use_case"], workspace["sink"]
    images = [_make_jpeg(8, 6, (255, 0, 0))]

    report = use_case.import_documents(
        "chapter-7",
        [_source("drm.mobi", picture_mobi(images, crypto_type=1))],
    )

    assert report.imported == ()
    assert len(report.failed) == 1
    reason, detail = report.failed[0].reason, report.failed[0].detail
    assert reason == "ENCRYPTED"
    assert "DRM" in detail
    assert sink.pages == []


def test_truncated_mobi_fails_invalid_document(workspace) -> None:
    use_case, sink = workspace["use_case"], workspace["sink"]
    images = [_make_jpeg(8, 6, (255, 0, 0)), _make_jpeg(9, 7, (0, 255, 0))]
    container = picture_mobi(images)

    report = use_case.import_documents(
        "chapter-7", [_source("cut.mobi", container[: len(container) // 2])]
    )

    assert report.imported == ()
    assert len(report.failed) == 1
    assert report.failed[0].reason == "INVALID_DOCUMENT"
    assert sink.pages == []


def test_text_only_mobi_fails_closed_with_scope_note(workspace) -> None:
    use_case, sink = workspace["use_case"], workspace["sink"]

    report = use_case.import_documents(
        "chapter-7", [_source("novel.mobi", text_only_mobi())]
    )

    assert report.imported == ()
    assert len(report.failed) == 1
    assert report.failed[0].reason == "INVALID_DOCUMENT"
    assert "text-only" in report.failed[0].detail
    assert sink.pages == []


def test_undecodable_page_image_fails_that_page(workspace) -> None:
    """JPEG magic that imghdr accepts but Qt cannot decode: the page fails
    typed and (F-3, single page) there is nothing left pending."""
    use_case, sink = workspace["use_case"], workspace["sink"]
    broken = b"\xff\xd8\xff\xd9"  # JPEG magic + EOI, no frame data

    report = use_case.import_documents(
        "chapter-7", [_source("bad.mobi", picture_mobi([broken]))]
    )

    assert report.imported == ()
    assert len(report.failed) == 1
    assert report.failed[0].reason == "INVALID_DOCUMENT"
    assert "decoded" in report.failed[0].detail
    assert sink.pages == []


def test_without_injected_mobi_raster_mobi_stays_unsupported(tmp_path: Path) -> None:
    """The TASK-023 fallback is preserved byte-for-byte when the assembly
    does not inject a MOBI binding (pre-TASK-041 constructions)."""
    storage = ManagedFileStorage(tmp_path / "managed")
    copy_store = ManagedCopyStoreAdapter(storage, lambda chapter_id: "book-42")
    use_case = ImportDocumentsUseCase(
        PdfiumDocumentRaster(), copy_store, InMemoryPageSink()
    )
    data = picture_mobi([_make_jpeg(8, 6, (255, 0, 0))])

    report = use_case.import_documents("chapter-7", [_source("m.mobi", data)])

    assert report.imported == ()
    assert report.failed[0].reason == "UNSUPPORTED_FORMAT"
    assert "TASK-023" in report.failed[0].detail


def test_missing_binding_reports_missing_dependency(tmp_path: Path) -> None:
    """A binding that cannot load (readiness) is a typed failure, not a
    crash and not a skip (F-9 caliber)."""
    storage = ManagedFileStorage(tmp_path / "managed")
    copy_store = ManagedCopyStoreAdapter(storage, lambda chapter_id: "book-42")
    use_case = ImportDocumentsUseCase(
        PdfiumDocumentRaster(),
        copy_store,
        InMemoryPageSink(),
        mobi_raster=InMemoryRaster(
            "MISSING_DEPENDENCY", "the mobi binding is unavailable"
        ),
    )
    data = picture_mobi([_make_jpeg(8, 6, (255, 0, 0))])

    report = use_case.import_documents("chapter-7", [_source("m.mobi", data)])

    assert report.imported == ()
    assert report.failed[0].reason == "MISSING_DEPENDENCY"


def test_non_mobi_non_pdf_payloads_still_unsupported(workspace) -> None:
    use_case = workspace["use_case"]

    report = use_case.import_documents(
        "chapter-7", [_source("x.epub", b"PK\x03\x04 not a mobi")]
    )

    assert report.imported == ()
    assert report.failed[0].reason == "UNSUPPORTED_FORMAT"
