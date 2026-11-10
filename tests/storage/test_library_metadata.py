"""FEA-14-LIB-1: book/chapter metadata, strict reorder, create-with-metadata (schema v12)."""

from __future__ import annotations

from pathlib import Path
import sqlite3
import sys

import pytest

THIS_DIR = Path(__file__).resolve().parent
SRC_ROOT = THIS_DIR.parents[1] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from application.library.service import LibraryService  # noqa: E402
from application.library.errors import ChapterNotFound  # noqa: E402
from infrastructure.sqlite.library import SqliteLibraryRepository  # noqa: E402
from infrastructure.sqlite.migrator import MigrationRunner, read_schema_version  # noqa: E402
from infrastructure.sqlite.schema import default_migrations  # noqa: E402

MIGRATIONS = default_migrations()
LATEST = MIGRATIONS[-1].schema_version


def _service(tmp_path: Path):
    conn = sqlite3.connect(tmp_path / "library.db")
    conn.row_factory = sqlite3.Row
    MigrationRunner(conn, MIGRATIONS).apply_pending()
    return conn, LibraryService(SqliteLibraryRepository(conn))


def test_v12_adds_custom_rank_and_keeps_legacy_rows(tmp_path):
    conn = sqlite3.connect(tmp_path / "library.db")
    MigrationRunner(conn, MIGRATIONS[:-1]).apply_pending()
    assert read_schema_version(conn) == LATEST - 1
    MigrationRunner(conn, MIGRATIONS).apply_pending()
    assert read_schema_version(conn) == LATEST
    columns = {row[1] for row in conn.execute("pragma table_info(chapters)")}
    assert "custom_rank" in columns


def test_patch_book_keeps_unprovided_fields(tmp_path):
    conn, service = _service(tmp_path)
    book = service.create_book("Original", author="A")
    service.patch_book_metadata(book.book_id, {"title": "Renamed", "description": "d"})
    updated = service.get_book(book.book_id)
    assert updated.title == "Renamed" and updated.description == "d"
    assert updated.author == "A", "patch must keep fields it did not provide"
    with pytest.raises(ValueError):
        service.patch_book_metadata(book.book_id, {"title": "  "})
    with pytest.raises(ValueError):
        service.patch_book_metadata(book.book_id, {"bogus": "x"})
    with pytest.raises(Exception):
        service.patch_book_metadata("missing-book", {"title": "x"})


def test_patch_chapter_metadata_and_validation(tmp_path):
    conn, service = _service(tmp_path)
    book = service.create_book("Book")
    chapter = service.create_chapter(book.book_id, "Ch 1")
    updated = service.patch_chapter_metadata(
        chapter.chapter_id, {"kind": "webtoon", "number": "01", "custom_rank": 3, "notes": "n"}
    )
    assert updated.chapter_type.value == "webtoon"
    assert updated.chapter_number == "01"
    assert updated.custom_rank == 3
    assert updated.title == "Ch 1", "unprovided fields must be preserved"
    with pytest.raises(ValueError):
        service.patch_chapter_metadata(chapter.chapter_id, {"kind": "bogus"})
    with pytest.raises(ChapterNotFound):
        service.patch_chapter_metadata("missing-chapter", {"notes": "x"})


def test_reorder_chapters_requires_full_cover(tmp_path):
    conn, service = _service(tmp_path)
    book = service.create_book("Book")
    first = service.create_chapter(book.book_id, "Ch 1")
    second = service.create_chapter(book.book_id, "Ch 2")
    with pytest.raises(ValueError):
        service.reorder_chapters_strict(book.book_id, [first.chapter_id])
    with pytest.raises(ValueError):
        service.reorder_chapters_strict(book.book_id, [first.chapter_id, first.chapter_id])
    with pytest.raises(ValueError):
        service.reorder_chapters_strict(book.book_id, [first.chapter_id, second.chapter_id, "extra"])
    ordered = service.reorder_chapters_strict(book.book_id, [second.chapter_id, first.chapter_id])
    assert [item.chapter_id for item in ordered] == [second.chapter_id, first.chapter_id]
    assert [item.chapter_id for item in service.list_chapters(book.book_id)] == [
        second.chapter_id, first.chapter_id
    ]


def test_create_chapter_with_metadata(tmp_path):
    conn, service = _service(tmp_path)
    book = service.create_book("Book")
    chapter = service.create_chapter_with_metadata(
        book.book_id, "Extra", kind="webtoon", number="99", import_order=7
    )
    assert chapter.chapter_type.value == "webtoon"
    assert chapter.chapter_number == "99"
    assert chapter.import_order == 7
    assert service.get_chapter(chapter.chapter_id).title == "Extra"
    with pytest.raises(Exception):
        service.create_chapter_with_metadata("missing-book", "x")
