"""P09 scope guard: MOBI is excluded from the first release."""

from __future__ import annotations

from application.importing.documents.service import ImportDocumentsUseCase
from application.importing.images.ports import ImportSource
from infrastructure.filesystem.managed_storage import ManagedFileStorage
from infrastructure.importing import ManagedCopyStoreAdapter, PdfiumDocumentRaster


class InMemoryPageSink:
    def __init__(self) -> None:
        self.pages = []

    def existing_source_hashes(self, chapter_id: str) -> set[str]:
        return set()

    def max_source_order(self, chapter_id: str) -> int:
        return 0

    def add_page(self, page) -> None:
        self.pages.append(page)


def test_mobi_payload_is_rejected_without_managed_or_page_side_effects(tmp_path):
    storage = ManagedFileStorage(tmp_path / "managed")
    sink = InMemoryPageSink()
    use_case = ImportDocumentsUseCase(
        PdfiumDocumentRaster(),
        ManagedCopyStoreAdapter(storage, lambda chapter_id: "book-42"),
        sink,
    )

    report = use_case.import_documents(
        "chapter-7",
        [ImportSource("book.mobi", lambda: b"BOOKMOBI excluded by P09")],
    )

    assert report.imported == () and sink.pages == []
    assert [failed.reason for failed in report.failed] == ["UNSUPPORTED_FORMAT"]
    assert not list((tmp_path / "managed" / "books").rglob("*"))
