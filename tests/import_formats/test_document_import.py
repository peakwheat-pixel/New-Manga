"""TASK-023 document import: PDF rasterisation through the real pypdfium2
binding + real Managed Copy, plus diagnosable failure and cancellation
semantics. Test PDFs are built in-process (self-made material, no licensing
concerns); MOBI stays an unsupported-format case by design (no approved
parsing dependency)."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from application.importing.documents.ports import DocumentDecodeError
from application.importing.documents.service import ImportDocumentsUseCase
from application.importing.images.ports import ImportSource
from application.importing.images.service import DuplicatePolicy
from infrastructure.filesystem.managed_storage import ManagedFileStorage
from infrastructure.importing import ManagedCopyStoreAdapter, PdfiumDocumentRaster


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
