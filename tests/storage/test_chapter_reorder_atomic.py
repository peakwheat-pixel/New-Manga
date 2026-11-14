"""CHAPTER-MANUAL-SORT: the user reorder must be all-or-nothing.

The discriminating case is a failure on a *later* row: a per-row loop would
already have committed the earlier rows, so the book would keep a half-applied
display order. One transaction must roll every row back.
"""

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
from infrastructure.sqlite.library import SqliteLibraryRepository  # noqa: E402
from infrastructure.sqlite.migrator import MigrationRunner  # noqa: E402
from infrastructure.sqlite.schema import default_migrations  # noqa: E402

MIGRATIONS = default_migrations()


def _service(tmp_path: Path):
    conn = sqlite3.connect(tmp_path / "library.db")
    conn.row_factory = sqlite3.Row
    MigrationRunner(conn, MIGRATIONS).apply_pending()
    return conn, LibraryService(SqliteLibraryRepository(conn))


def _seed(tmp_path: Path):
    conn, service = _service(tmp_path)
    book = service.create_book("Atomic Book")
    chapters = [
        service.create_chapter(book.book_id, f"Ch {index}")
        for index in range(1, 4)
    ]
    # create_chapter appends max(sort_order)+1, so the initial display order is 1,2,3.
    assert [chapter.sort_order for chapter in chapters] == [1, 2, 3]
    return conn, service, book, chapters


def _sort_orders(service: LibraryService, book_id: str) -> dict[str, int]:
    return {chapter.chapter_id: chapter.sort_order for chapter in service.list_chapters(book_id)}


def _import_orders(service: LibraryService, book_id: str) -> dict[str, int]:
    return {chapter.chapter_id: chapter.import_order for chapter in service.list_chapters(book_id)}


def test_reorder_rolls_back_every_row_when_a_later_write_fails(tmp_path):
    conn, service, book, chapters = _seed(tmp_path)
    first, second, third = chapters
    before = _sort_orders(service, book.book_id)
    assert before == {first.chapter_id: 1, second.chapter_id: 2, third.chapter_id: 3}

    # Fail on a LATER update of the submitted order: a per-row loop has
    # already committed `third` by then, so only a single transaction can leave
    # the book exactly as it was.
    assert [chapter.import_order for chapter in chapters] == [1, 2, 3]
    # SQLite forbids bound parameters inside a trigger body, so the chapter id is
    # inlined (it is a generated UUID; quotes are escaped defensively).
    quoted_id = second.chapter_id.replace("'", "''")
    conn.execute(
        "CREATE TRIGGER fail_reorder_second_row"
        " BEFORE UPDATE ON chapters"
        f" WHEN NEW.chapter_id = '{quoted_id}'"
        " BEGIN SELECT RAISE(ABORT, 'injected reorder failure'); END"
    )
    conn.commit()

    with pytest.raises(sqlite3.Error):
        service.reorder_chapters_strict(
            book.book_id,
            [third.chapter_id, first.chapter_id, second.chapter_id],
        )

    # AC1/AC2: nothing may have moved -- especially `third`, which a per-row
    # implementation would have persisted as sort_order = 1 before failing.
    assert _sort_orders(service, book.book_id) == before

    # Clearing the trigger must leave a fully usable book (no poisoned state).
    conn.execute("DROP TRIGGER fail_reorder_second_row")
    conn.commit()
    applied = service.reorder_chapters_strict(
        book.book_id,
        [third.chapter_id, first.chapter_id, second.chapter_id],
    )
    assert [chapter.sort_order for chapter in applied] == [1, 2, 3]
    assert _sort_orders(service, book.book_id) == {
        third.chapter_id: 1,
        first.chapter_id: 2,
        second.chapter_id: 3,
    }


def test_reorder_persists_one_to_n_and_freezes_import_order(tmp_path):
    conn, service, book, chapters = _seed(tmp_path)
    first, second, third = chapters
    import_before = _import_orders(service, book.book_id)

    service.reorder_chapters_strict(
        book.book_id,
        [second.chapter_id, third.chapter_id, first.chapter_id],
    )

    assert _sort_orders(service, book.book_id) == {
        second.chapter_id: 1,
        third.chapter_id: 2,
        first.chapter_id: 3,
    }
    # D03 §5.3: import_order is provenance and must not be rewritten by a reorder.
    assert _import_orders(service, book.book_id) == import_before


def test_list_chapters_wire_order_stays_sort_order_after_reorder(tmp_path):
    conn, service, book, chapters = _seed(tmp_path)
    first, second, third = chapters
    service.reorder_chapters_strict(
        book.book_id,
        [third.chapter_id, second.chapter_id, first.chapter_id],
    )

    # AC6: the command still lists by sort_order; the reorder simply changed it.
    listed = [chapter.chapter_id for chapter in service.list_chapters(book.book_id)]
    assert listed == [third.chapter_id, second.chapter_id, first.chapter_id]


def test_chapter_created_after_manual_reorder_lands_at_the_end(tmp_path):
    conn, service, book, chapters = _seed(tmp_path)
    first, second, third = chapters
    service.reorder_chapters_strict(
        book.book_id,
        [third.chapter_id, first.chapter_id, second.chapter_id],
    )

    appended = service.create_chapter(book.book_id, "Ch 4")

    # AC7: a new chapter is appended after the manual order, not interleaved.
    assert _sort_orders(service, book.book_id) == {
        third.chapter_id: 1,
        first.chapter_id: 2,
        second.chapter_id: 3,
        appended.chapter_id: 4,
    }
    assert [chapter.chapter_id for chapter in service.list_chapters(book.book_id)][-1] == (
        appended.chapter_id
    )


def test_empty_book_reorder_is_a_noop(tmp_path):
    conn, service = _service(tmp_path)
    book = service.create_book("Empty Book")

    assert service.reorder_chapters_strict(book.book_id, []) == []
    assert service.list_chapters(book.book_id) == []
