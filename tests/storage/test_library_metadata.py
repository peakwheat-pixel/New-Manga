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
from application.library.errors import ChapterNotFound, TagNotFound  # noqa: E402
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
    conn.row_factory = sqlite3.Row
    MigrationRunner(conn, MIGRATIONS[:-1]).apply_pending()
    assert read_schema_version(conn) == LATEST - 1
    # R-10: a real v11 chapter row must survive the migration with custom_rank NULL.
    conn.execute(
        "INSERT INTO books (book_id, title, created_at, updated_at)"
        " VALUES ('legacy-b', 'Legacy', '2026-01-01', '2026-01-01')"
    )
    conn.execute(
        "INSERT INTO chapters (chapter_id, book_id, title, chapter_number, subtitle,"
        " import_order, sort_order, chapter_type, reading_direction, notes, created_at, updated_at)"
        " VALUES ('legacy-c', 'legacy-b', 'Old Ch', '3', '', 1, 1, 'paged', 'rtl', 'n',"
        " '2026-01-01', '2026-01-01')"
    )
    conn.commit()
    MigrationRunner(conn, MIGRATIONS).apply_pending()
    assert read_schema_version(conn) == LATEST
    columns = {row[1] for row in conn.execute("pragma table_info(chapters)")}
    assert "custom_rank" in columns
    row = conn.execute(
        "SELECT title, chapter_number, notes, custom_rank FROM chapters WHERE chapter_id = 'legacy-c'"
    ).fetchone()
    assert row["title"] == "Old Ch" and row["chapter_number"] == "3" and row["notes"] == "n"
    assert row["custom_rank"] is None


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


def test_patch_book_tags_replaces_associations(tmp_path):
    conn, service = _service(tmp_path)
    book = service.create_book("Book")
    first = service.create_tag("first")
    second = service.create_tag("second")
    service.patch_book_metadata(book.book_id, {"tags": [first.tag_id]})
    assert [tag.tag_id for tag in service.tags_of_book(book.book_id)] == [first.tag_id]
    # R-02: replacement (not append) and validation-before-write.
    service.patch_book_metadata(book.book_id, {"tags": [second.tag_id]})
    assert [tag.tag_id for tag in service.tags_of_book(book.book_id)] == [second.tag_id]
    with pytest.raises(TagNotFound):
        service.patch_book_metadata(book.book_id, {"tags": ["missing-tag"]})
    assert [tag.tag_id for tag in service.tags_of_book(book.book_id)] == [second.tag_id]
    # R-02 (r2): an unknown tag id must fail before the text fields are written.
    half = service.create_book("HalfWrite")
    with pytest.raises(TagNotFound):
        service.patch_book_metadata(half.book_id, {"title": "HalfWrite!", "tags": ["missing-tag"]})
    assert service.get_book(half.book_id).title == "HalfWrite"
    # R-05 (r2): P5 text fields are strings only; no silent str() coercion.
    with pytest.raises(ValueError):
        service.patch_book_metadata(half.book_id, {"title": 5})


def test_create_with_import_order_keeps_sort_order_unique(tmp_path):
    conn, service = _service(tmp_path)
    book = service.create_book("Book")
    first = service.create_chapter(book.book_id, "Ch 1")
    second = service.create_chapter(book.book_id, "Ch 2")
    created = service.create_chapter_with_metadata(book.book_id, "Extra", import_order=1)
    # R-04: import_order is provenance; sort_order must stay appended/unique.
    assert created.import_order == 1
    assert created.sort_order == max(first.sort_order, second.sort_order) + 1
    orders = [chapter.sort_order for chapter in service.list_chapters(book.book_id)]
    assert len(set(orders)) == len(orders), "sort_order must stay unique"


def test_repeated_import_order_keeps_sort_order_appended(tmp_path):
    conn, service = _service(tmp_path)
    book = service.create_book("Book")
    service.create_chapter(book.book_id, "C1")
    service.create_chapter(book.book_id, "C2")
    # R-04 (r2): three P8 creates may share the same caller import_order...
    extras = [
        service.create_chapter_with_metadata(book.book_id, f"Extra {index}", import_order=1)
        for index in range(3)
    ]
    tail = service.create_chapter(book.book_id, "Tail")
    chapters = service.list_chapters(book.book_id)
    assert [chapter.sort_order for chapter in chapters] == [1, 2, 3, 4, 5, 6]
    assert [chapter.import_order for chapter in extras] == [1, 1, 1]
    # ...while import_order keeps its own max+1 provenance sequence.
    assert tail.import_order == 3


def test_patch_chapter_rejects_non_integer_custom_rank(tmp_path):
    conn, service = _service(tmp_path)
    book = service.create_book("Book")
    chapter = service.create_chapter(book.book_id, "Ch 1")
    # R-13: bool/float/str/negative must raise instead of being silently coerced.
    for bad in (True, 1.5, -1, "3"):
        with pytest.raises(ValueError):
            service.patch_chapter_metadata(chapter.chapter_id, {"custom_rank": bad})
    assert service.get_chapter(chapter.chapter_id).custom_rank is None
    service.patch_chapter_metadata(chapter.chapter_id, {"custom_rank": 0})
    assert service.get_chapter(chapter.chapter_id).custom_rank == 0
    service.patch_chapter_metadata(chapter.chapter_id, {"custom_rank": None})
    assert service.get_chapter(chapter.chapter_id).custom_rank is None
    # P3 (r2): text fields are strings only.
    for key in ("kind", "number", "title", "subtitle", "notes"):
        with pytest.raises(ValueError):
            service.patch_chapter_metadata(chapter.chapter_id, {key: 5})
