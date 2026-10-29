"""Fixtures for library/import tests (see helpers.py for fakes/factories)."""

from __future__ import annotations

import pytest

import helpers  # noqa: F401  (injects src into sys.path first)
from application.importing.images.service import ImportImagesUseCase
from application.library.service import LibraryService

from helpers import (
    FakeManagedCopyStore,
    InMemoryLibraryRepository,
    InMemoryPageSink,
    QtImageDecoder,
)


@pytest.fixture()
def library() -> LibraryService:
    return LibraryService(InMemoryLibraryRepository())


@pytest.fixture()
def import_use_case():
    def _factory(
        fail_on: set[str] | None = None,
    ) -> tuple[ImportImagesUseCase, FakeManagedCopyStore, InMemoryPageSink]:
        store = FakeManagedCopyStore(fail_on=fail_on)
        sink = InMemoryPageSink()
        return ImportImagesUseCase(QtImageDecoder(), store, sink), store, sink

    return _factory


@pytest.fixture()
def book(library):
    return library.create_book(
        "進撃テスト",
        original_title="進撃の巨人",
        author="Hajime Isayama",
        source_language="ja",
        target_language="zh",
    )


@pytest.fixture()
def chapter(library, book):
    return library.create_chapter(book.book_id, "第1话", chapter_type="paged")
