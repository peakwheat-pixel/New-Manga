"""TASK-023 document import: PDF rasterisation through the real pypdfium2
binding + real Managed Copy, plus diagnosable failure and cancellation
semantics. Test PDFs are built in-process (self-made material, no licensing
concerns); MOBI stays an unsupported-format case by design (no approved
parsing dependency).

TASK-043 revision tail (this file): **pixel-level** regression for the
rasteriser (F-1 — dimensions alone let the red/blue swap survive TASK-023),
remainder-as-pending on a mid-document failure (F-3) and a typed
``MISSING_DEPENDENCY`` when the PDFium binding is unusable (F-9)."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pytest

from application.importing.documents.ports import (
    DocumentDecodeError,
    RenderedDocumentPage,
)
from application.importing.documents.service import ImportDocumentsUseCase
from application.importing.images.ports import ImportSource
from application.importing.images.service import DuplicatePolicy
from infrastructure.filesystem.managed_storage import ManagedFileStorage
from infrastructure.importing import ManagedCopyStoreAdapter, PdfiumDocumentRaster


def _assemble_pdf(objects: dict[int, bytes]) -> bytes:
    """Serialise numbered objects into a minimal PDF with a valid xref.

    TASK-043 extracted this from ``minimal_pdf`` without changing its output
    (verified byte-identical via the imported page hashes) so the
    solid-colour and zero-page builders share exactly one writer.
    """
    out = bytearray(b"%PDF-1.4\n")
    offsets: dict[int, int] = {}
    for obj_id in sorted(objects):
        offsets[obj_id] = len(out)
        out += f"{obj_id} 0 obj\n".encode() + objects[obj_id] + b"\nendobj\n"
    xref_pos = len(out)
    count = max(objects) + 1
    out += f"xref\n0 {count}\n".encode()
    out += b"0000000000 65535 f \n"
    for obj_id in range(1, count):
        out += f"{offsets.get(obj_id, 0):010d} 00000 n \n".encode()
    out += (
        f"trailer\n<< /Size {count} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n"
    ).encode()
    return bytes(out)


def minimal_pdf(n_pages: int = 2) -> bytes:
    """Build a minimal valid multi-page PDF (US-Letter pages, distinct
    content per page) without any third-party writer."""
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
    return _assemble_pdf(objects)


def solid_colour_pdf(red: int, green: int, blue: int, size: int = 100) -> bytes:
    """A one-page PDF whose entire MediaBox is filled with one known colour.

    ``1 0 0 rg`` is *red* in PDF device RGB; the rasteriser must hand that
    back as red (F-1), which is exactly what a dimensions-only assertion
    cannot see.
    """
    stream = f"{red} {green} {blue} rg 0 0 {size} {size} re f".encode()
    return _assemble_pdf(
        {
            1: b"<< /Type /Catalog /Pages 2 0 R >>",
            2: b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
            3: (
                f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {size} {size}] "
                f"/Contents 4 0 R >>"
            ).encode(),
            4: b"<< /Length "
            + str(len(stream)).encode()
            + b" >>\nstream\n"
            + stream
            + b"\nendstream",
        }
    )


def zero_page_pdf() -> bytes:
    """A structurally valid PDF whose page tree declares zero pages (F-3)."""
    return _assemble_pdf(
        {
            1: b"<< /Type /Catalog /Pages 2 0 R >>",
            2: b"<< /Type /Pages /Kids [] /Count 0 >>",
        }
    )


class InMemoryPageSink:
    """Minimal ImportPageSink double with duplicate/ordering bookkeeping."""

    def __init__(self) -> None:
        self.pages: list = []

    def existing_source_hashes(self, chapter_id: str) -> set[str]:
        return {page.source_hash for page in self.pages}

    def max_source_order(self, chapter_id: str) -> int:
        return max((page.source_order for page in self.pages), default=0)

    def add_page(self, page) -> None:
        self.pages.append(page)


@pytest.fixture()
def workspace(tmp_path: Path):
    storage = ManagedFileStorage(tmp_path / "managed")
    copy_store = ManagedCopyStoreAdapter(storage, lambda chapter_id: "book-42")
    sink = InMemoryPageSink()
    use_case = ImportDocumentsUseCase(PdfiumDocumentRaster(), copy_store, sink)
    return {"use_case": use_case, "sink": sink, "storage": storage, "tmp_path": tmp_path}


def _source(name: str, data: bytes) -> ImportSource:
    return ImportSource(filename=name, data_provider=lambda data=data: data)


def test_pdf_import_materialises_one_managed_page_per_document_page(workspace) -> None:
    use_case, sink, storage = workspace["use_case"], workspace["sink"], workspace["storage"]

    report = use_case.import_documents(
        "chapter-7", [_source("chapter.pdf", minimal_pdf(3))]
    )

    assert len(report.imported) == 3
    assert [item.page.source_order for item in report.imported] == [1, 2, 3]
    assert report.failed == () and report.cancelled is False
    for item in report.imported:
        page = item.page
        # scale=2.0 over a 612x792pt MediaBox; PNG pages under Managed Copy
        assert (page.width, page.height) == (1224, 1584)
        assert page.source_hash == hashlib.sha256(
            Path(storage.absolute_path(page.managed_original_ref)).read_bytes()
        ).hexdigest()
        assert item.filename == f"chapter-page-{item.page.source_order:04d}.png"
    assert len(sink.pages) == 3


def test_duplicate_pdf_skips_and_import_as_new_reimports(workspace) -> None:
    use_case = workspace["use_case"]
    data = minimal_pdf(2)

    first = use_case.import_documents("chapter-7", [_source("a.pdf", data)])
    again_skip = use_case.import_documents("chapter-7", [_source("a.pdf", data)])
    again_new = use_case.import_documents(
        "chapter-7",
        [_source("a.pdf", data)],
        duplicate_policy=DuplicatePolicy.IMPORT_AS_NEW,
    )

    assert len(first.imported) == 2
    assert again_skip.skipped_duplicates == ("a.pdf",)
    assert again_skip.imported == ()
    assert len(again_new.imported) == 2
    # the same document rasterises to the same page bytes (stable source hash)
    assert [item.page.source_hash for item in first.imported] == [
        item.page.source_hash for item in again_new.imported
    ]


def test_corrupt_pdf_fails_diagnosably_and_keeps_imported_data(workspace) -> None:
    use_case, sink = workspace["use_case"], workspace["sink"]
    good = use_case.import_documents("chapter-7", [_source("good.pdf", minimal_pdf(2))])
    assert len(good.imported) == 2

    report = use_case.import_documents(
        "chapter-7", [_source("broken.pdf", b"%PDF-1.4 garbage that never parses")]
    )

    assert len(report.imported) == 0
    assert report.failed[0].filename == "broken.pdf"
    assert report.failed[0].reason == "INVALID_DOCUMENT"
    # previously imported data untouched
    assert len(sink.pages) == 2


def test_non_pdf_and_mobi_reported_unsupported(workspace) -> None:
    use_case = workspace["use_case"]

    report = use_case.import_documents(
        "chapter-7",
        [
            _source("book.mobi", b"BOOKMOBI\x00\x01fake mobi payload"),
            _source("notes.txt", b"plain text, not a document"),
        ],
    )

    assert len(report.imported) == 0
    assert {failure.filename for failure in report.failed} == {"book.mobi", "notes.txt"}
    assert all(
        failure.reason == "UNSUPPORTED_FORMAT" for failure in report.failed
    )
    assert "MOBI" in report.failed[0].detail


def test_cancel_stops_before_the_next_page_and_keeps_committed(workspace) -> None:
    use_case, sink = workspace["use_case"], workspace["sink"]

    def cancelled() -> bool:
        # deterministic on committed state: cancel once two pages are in
        return len(sink.pages) >= 2

    report = use_case.import_documents(
        "chapter-7", [_source("long.pdf", minimal_pdf(4))], cancelled=cancelled
    )

    assert report.cancelled is True
    assert len(report.imported) == 2  # pages 1-2 committed
    assert len(sink.pages) == 2
    assert report.pending_after_cancel  # remainder reported as pending


def test_encrypted_pdf_is_reported_not_guessed(tmp_path) -> None:
    """Unit-level: an adapter that reports encryption surfaces as a typed
    ``ENCRYPTED`` failure — credentials are never guessed."""

    class EncryptedRaster:
        def open(self, data: bytes):
            raise DocumentDecodeError("ENCRYPTED", "the PDF is password-protected")

    use_case = ImportDocumentsUseCase(
        EncryptedRaster(),
        ManagedCopyStoreAdapter(ManagedFileStorage(tmp_path / "m"), lambda c: "b"),
        InMemoryPageSink(),
    )

    report = use_case.import_documents(
        "chapter-7", [_source("secret.pdf", minimal_pdf(1))]
    )

    assert report.failed == (
        ("secret.pdf", "ENCRYPTED", "the PDF is password-protected"),
    ) or (
        report.failed[0].filename == "secret.pdf"
        and report.failed[0].reason == "ENCRYPTED"
    )
    assert report.imported == ()


# ---------------------------------------------------------------------------
# TASK-043 revision tail: F-1 pixel regression, F-3 remainder semantics,
# F-9 typed missing-dependency.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "fill", [(255, 0, 0), (0, 255, 0), (0, 0, 255)], ids=["red", "green", "blue"]
)
def test_imported_pdf_page_keeps_the_source_colour(workspace, fill) -> None:
    """F-1 (TASK-043): the rasteriser must keep PDFium's BGR byte order.

    Pre-fix, the ``BGR`` buffer went into ``QImage.Format_RGB888``, so a pure
    red page was decoded blue (and blue red). The old suite asserted only
    ``(width, height)``, which is blind to a channel swap — so this test
    samples the pixels of the PNG that the *production* Managed Copy
    persisted, through the real PDFium binding.
    """
    from PySide6.QtGui import QImage

    use_case, storage = workspace["use_case"], workspace["storage"]

    report = use_case.import_documents(
        "chapter-7", [_source("solid.pdf", solid_colour_pdf(*fill))]
    )

    assert len(report.imported) == 1 and report.failed == ()
    page = report.imported[0].page
    png_path = Path(storage.absolute_path(page.managed_original_ref))
    assert png_path.is_file()  # the managed copy really holds the page
    image = QImage.fromData(png_path.read_bytes(), "PNG")
    assert not image.isNull()
    assert (image.width(), image.height()) == (200, 200)  # 100pt MediaBox at scale 2.0
    samples = ((0.5, 0.5), (0.25, 0.25), (0.75, 0.25), (0.25, 0.75), (0.75, 0.75))
    for x_ratio, y_ratio in samples:
        colour = image.pixelColor(
            round(image.width() * x_ratio), round(image.height() * y_ratio)
        )
        assert (colour.red(), colour.green(), colour.blue()) == pytest.approx(
            fill, abs=8
        ), f"pixel at ratio ({x_ratio}, {y_ratio}) is not the source fill {fill}"
        assert colour.alpha() == 255


class _StubHandle:
    """Minimal ``DocumentHandle`` double; page payloads are opaque here (the
    pixel contract is covered by the production test above)."""

    def __init__(self, page_count: int, fail_on: int | None = None) -> None:
        self._page_count = page_count
        self._fail_on = fail_on
        self.closed = False

    @property
    def page_count(self) -> int:
        return self._page_count

    def render_page(self, index: int) -> RenderedDocumentPage:
        if index == self._fail_on:
            raise DocumentDecodeError("INVALID_DOCUMENT", f"page {index + 1} is broken")
        return RenderedDocumentPage(
            png=f"stub-page-{index + 1:04d}".encode(), width=1, height=1
        )

    def close(self) -> None:
        self.closed = True


class _StubRaster:
    """``DocumentRaster`` double that can fail on one chosen page."""

    def __init__(self, page_count: int, fail_on: int | None = None) -> None:
        self._page_count = page_count
        self._fail_on = fail_on
        self.handle: _StubHandle | None = None

    def open(self, data: bytes) -> _StubHandle:
        del data
        self.handle = _StubHandle(self._page_count, self._fail_on)
        return self.handle


def _stub_use_case(tmp_path: Path, page_count: int, fail_on: int | None = None):
    raster = _StubRaster(page_count, fail_on)
    storage = ManagedFileStorage(tmp_path / "managed")
    sink = InMemoryPageSink()
    use_case = ImportDocumentsUseCase(
        raster, ManagedCopyStoreAdapter(storage, lambda chapter_id: "book-42"), sink
    )
    return use_case, sink, raster


def test_failed_page_reports_the_rest_as_pending(tmp_path) -> None:
    """F-3 (TASK-043): a mid-document failure must account for the remainder.

    Pre-fix the loop simply ``break``-ed, so pages after the failure were
    neither failed nor pending and the caller could not tell that they were
    never attempted.
    """
    use_case, sink, raster = _stub_use_case(tmp_path, page_count=4, fail_on=1)

    report = use_case.import_documents("chapter-7", [_source("long.pdf", b"%PDF-1.4 stub")])

    assert len(report.imported) == 1 and len(sink.pages) == 1
    assert [failure.reason for failure in report.failed] == ["INVALID_DOCUMENT"]
    assert report.pending_after_cancel == ("long.pdf (page 3+)", "long.pdf (page 4+)")
    assert report.skipped_duplicates == ()
    # a failed page is not a cancellation: the flag must stay honest
    assert report.cancelled is False
    assert raster.handle is not None and raster.handle.closed is True


def test_copy_failure_reports_the_rest_as_pending(tmp_path) -> None:
    """F-3 (TASK-043): the Managed Copy failure path accounts for the
    remainder just like the decode failure path."""
    storage = ManagedFileStorage(tmp_path / "managed")
    inner = ManagedCopyStoreAdapter(storage, lambda chapter_id: "book-42")
    calls = {"count": 0}

    class FlakyStore:
        def store_original(self, chapter_id, source_filename, data, source_hash):
            calls["count"] += 1
            if calls["count"] == 2:
                raise OSError("injected copy failure")
            return inner.store_original(chapter_id, source_filename, data, source_hash)

    sink = InMemoryPageSink()
    use_case = ImportDocumentsUseCase(_StubRaster(page_count=3), FlakyStore(), sink)

    report = use_case.import_documents("chapter-7", [_source("long.pdf", b"%PDF-1.4 stub")])

    assert len(report.imported) == 1 and len(sink.pages) == 1
    assert [failure.reason for failure in report.failed] == ["COPY_FAILED"]
    assert report.pending_after_cancel == ("long.pdf (page 3+)",)
    assert report.cancelled is False


def test_cancel_reports_every_remaining_page_as_pending(tmp_path) -> None:
    """F-3 (TASK-043): cancellation lists every page that was never started."""
    use_case, sink, _ = _stub_use_case(tmp_path, page_count=4)

    report = use_case.import_documents(
        "chapter-7",
        [_source("long.pdf", b"%PDF-1.4 stub")],
        cancelled=lambda: len(sink.pages) >= 2,
    )

    assert report.cancelled is True
    assert len(report.imported) == 2
    assert report.pending_after_cancel == ("long.pdf (page 3+)", "long.pdf (page 4+)")


def test_zero_page_document_is_a_typed_failure_not_a_duplicate(tmp_path) -> None:
    """F-3 (TASK-043): a document yielding no pages is *unusable*, not a
    duplicate — pre-fix it landed in ``skipped_duplicates``."""
    use_case, sink, _ = _stub_use_case(tmp_path, page_count=0)

    report = use_case.import_documents("chapter-7", [_source("empty.pdf", b"%PDF-1.4 stub")])

    assert report.imported == () and sink.pages == []
    assert report.skipped_duplicates == ()
    assert [failure.reason for failure in report.failed] == ["INVALID_DOCUMENT"]
    assert report.pending_after_cancel == ()


def test_zero_page_pdf_through_the_production_raster_fails_typed(workspace) -> None:
    """F-3 end-to-end: a zero-page PDF is a typed failure through the real
    PDFium binding too (never a duplicate, never a partial import)."""
    use_case = workspace["use_case"]

    report = use_case.import_documents("chapter-7", [_source("empty.pdf", zero_page_pdf())])

    assert report.imported == ()
    assert report.skipped_duplicates == ()
    assert len(report.failed) == 1
    assert report.failed[0].reason == "INVALID_DOCUMENT"


def test_unavailable_pdfium_binding_is_a_typed_error(monkeypatch) -> None:
    """F-9 (TASK-043): an unusable PDF binding raises the typed
    ``DocumentDecodeError``, never a bare ``ImportError``."""
    monkeypatch.setitem(sys.modules, "pypdfium2", None)

    with pytest.raises(DocumentDecodeError) as caught:
        PdfiumDocumentRaster().open(minimal_pdf(1))

    assert caught.value.reason == "MISSING_DEPENDENCY"
    assert "pypdfium2" in caught.value.detail


def test_unavailable_pdfium_binding_is_reported_per_file(workspace, monkeypatch) -> None:
    """F-9 end-to-end: the use case reports the unusable binding as a typed
    per-file failure instead of crashing the whole import."""
    monkeypatch.setitem(sys.modules, "pypdfium2", None)
    use_case = workspace["use_case"]

    report = use_case.import_documents("chapter-7", [_source("a.pdf", minimal_pdf(1))])

    assert report.imported == ()
    assert report.skipped_duplicates == ()
    assert [failure.reason for failure in report.failed] == ["MISSING_DEPENDENCY"]
    assert "pypdfium2" in report.failed[0].detail
