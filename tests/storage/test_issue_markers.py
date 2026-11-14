"""FEA-14-EDIT-1: issue markers over schema v13 (additive; v14 is current LATEST)."""

from __future__ import annotations

from pathlib import Path
import sqlite3
import sys

import pytest

THIS_DIR = Path(__file__).resolve().parent
SRC_ROOT = THIS_DIR.parents[1] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from application.editing.issue_markers import IssueMarkerError, IssueMarkerService  # noqa: E402
from domain.books.entities import Book, Chapter  # noqa: E402
from domain.editing.entities import IssueMarkerState  # noqa: E402
from domain.pages.entities import Page  # noqa: E402
from infrastructure.sqlite.issue_markers import SqliteIssueMarkerStore  # noqa: E402
from infrastructure.sqlite.library import SqliteLibraryRepository  # noqa: E402
from infrastructure.sqlite.migrator import MigrationRunner, read_schema_version  # noqa: E402
from infrastructure.sqlite.schema import default_migrations  # noqa: E402

MIGRATIONS = default_migrations()
LATEST = MIGRATIONS[-1].schema_version


def _stack(tmp_path: Path):
    conn = sqlite3.connect(tmp_path / "library.db")
    conn.row_factory = sqlite3.Row
    MigrationRunner(conn, MIGRATIONS).apply_pending()
    repository = SqliteLibraryRepository(conn)
    service = IssueMarkerService(SqliteIssueMarkerStore(conn))
    return conn, repository, service


def _seed(tmp_path: Path):
    conn, repository, service = _stack(tmp_path)
    repository.add_book(Book(book_id="book-1", title="Marker Book"))
    repository.add_chapter(Chapter(chapter_id="chapter-1", book_id="book-1", title="Ch 1"))
    repository.add_page(Page(
        page_id="page-1",
        chapter_id="chapter-1",
        source_filename="1.png",
        source_order=1,
        sort_order=1,
        source_hash="hash-1",
        source_size_bytes=1,
        width=10,
        height=10,
        managed_original_ref="books/book-1/chapters/chapter-1/1.png",
    ))
    return conn, repository, service


def test_v13_adds_issue_markers_and_keeps_legacy_rows(tmp_path):
    # F-06 (AI-1 r1): this test now runs v13 -> latest (v14+); the assertions pin
    # the v13 table/index shape plus "existing rows are untouched", so the name
    # stays scoped to the v13 contribution it guards.
    conn = sqlite3.connect(tmp_path / "library.db")
    conn.row_factory = sqlite3.Row
    MigrationRunner(conn, MIGRATIONS[:-1]).apply_pending()
    assert read_schema_version(conn) == LATEST - 1 == 13
    # A real pre-upgrade book/chapter/page row (pre-state now = v13) must survive
    # the v13 -> latest upgrade. (F-06: the pre-state moved off v12 when v14 landed.)
    conn.execute(
        "INSERT INTO books (book_id, title, created_at, updated_at)"
        " VALUES ('legacy-b', 'Legacy', '2026-01-01', '2026-01-01')"
    )
    conn.execute(
        "INSERT INTO chapters (chapter_id, book_id, title, created_at, updated_at)"
        " VALUES ('legacy-c', 'legacy-b', 'Old Ch', '2026-01-01', '2026-01-01')"
    )
    conn.execute(
        "INSERT INTO pages (page_id, chapter_id, sort_order, created_at, updated_at)"
        " VALUES ('legacy-p', 'legacy-c', 1, '2026-01-01', '2026-01-01')"
    )
    conn.commit()
    # F-04 (r1): take a row-level snapshot of the pre-upgrade tables and compare it
    # after the upgrade, not just one column.
    rows_before = {
        table: [tuple(row) for row in conn.execute(f"SELECT * FROM {table} ORDER BY rowid")]
        for table in ("books", "chapters", "pages")
    }
    MigrationRunner(conn, MIGRATIONS).apply_pending()
    assert read_schema_version(conn) == LATEST == 14
    tables = {row["name"] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert "issue_markers" in tables
    indexes = {row["name"] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='index'")}
    assert {"idx_issue_markers_book_state", "idx_issue_markers_page"} <= indexes
    for table, expected in rows_before.items():
        actual = [tuple(row) for row in conn.execute(f"SELECT * FROM {table} ORDER BY rowid")]
        assert actual == expected, f"v13 must not change existing {table} rows"
    assert conn.execute("SELECT title FROM chapters WHERE chapter_id='legacy-c'").fetchone()["title"] == "Old Ch"
    assert conn.execute("SELECT COUNT(*) FROM issue_markers").fetchone()[0] == 0


def test_create_list_state_machine_and_delete(tmp_path):
    conn, repository, service = _seed(tmp_path)

    whole_page = service.create_marker("book-1", "chapter-1", "page-1", "translation-check")
    positioned = service.create_marker(
        "book-1", "chapter-1", "page-1", "sfx", note="check bubble", position=(0.25, 0.75)
    )
    assert whole_page.state is IssueMarkerState.OPEN
    assert whole_page.position is None and whole_page.created_at
    assert positioned.position == {"x": 0.25, "y": 0.75}
    assert whole_page.marker_id != positioned.marker_id

    listed = service.list_markers("book-1")
    assert [marker.marker_id for marker in listed] == [whole_page.marker_id, positioned.marker_id]
    assert service.list_markers("book-1", "resolved") == []

    resolved = service.resolve_marker(whole_page.marker_id)
    assert resolved.state is IssueMarkerState.RESOLVED and resolved.resolved_at
    # resolve is idempotent: the timestamp does not move on a second call.
    assert service.resolve_marker(whole_page.marker_id).resolved_at == resolved.resolved_at
    assert [marker.marker_id for marker in service.list_markers("book-1")] == [positioned.marker_id]
    assert [marker.marker_id for marker in service.list_markers("book-1", "resolved")] == [
        whole_page.marker_id
    ]

    reopened = service.reopen_marker(whole_page.marker_id)
    assert reopened.state is IssueMarkerState.OPEN and reopened.resolved_at is None
    service.resolve_marker(whole_page.marker_id)

    assert service.delete_marker(positioned.marker_id) is True
    assert service.list_markers("book-1", "resolved") and len(service.list_markers("book-1")) == 0
    # Deleting a marker never touches the page/chapter/book rows.
    assert conn.execute("SELECT COUNT(*) FROM pages").fetchone()[0] == 1
    assert conn.execute("SELECT COUNT(*) FROM chapters").fetchone()[0] == 1
    assert conn.execute("SELECT COUNT(*) FROM books").fetchone()[0] == 1


def test_create_validates_ownership_and_position(tmp_path):
    conn, repository, service = _seed(tmp_path)
    repository.add_book(Book(book_id="book-2", title="Other"))
    repository.add_chapter(Chapter(chapter_id="chapter-2", book_id="book-2", title="Other Ch"))

    for bad in (
        ("missing-book", "chapter-1", "page-1", "kind"),
        ("book-1", "chapter-2", "page-1", "kind"),   # chapter belongs to another book
        ("book-1", "chapter-1", "missing-page", "kind"),
        ("book-1", "chapter-2", "page-1", "kind"),
    ):
        with pytest.raises(IssueMarkerError) as caught:
            service.create_marker(*bad)
        assert caught.value.code == "TARGET_NOT_FOUND"

    for bad_position in ((0.5,), (0.5, 0.5, 0.5), (1.5, 0.5), (True, 0.5), ("x", 0.5)):
        with pytest.raises(IssueMarkerError) as caught:
            service.create_marker(
                "book-1", "chapter-1", "page-1", "kind", position=bad_position
            )
        assert caught.value.code == "INVALID_REQUEST"

    for bad_kind in ("", "   ", "x" * 65):
        with pytest.raises(IssueMarkerError) as caught:
            service.create_marker("book-1", "chapter-1", "page-1", bad_kind)
        assert caught.value.code == "INVALID_REQUEST"

    with pytest.raises(IssueMarkerError) as caught:
        service.list_markers("book-1", "deleted")
    assert caught.value.code == "INVALID_REQUEST"
    with pytest.raises(IssueMarkerError) as caught:
        service.list_markers("missing-book")
    assert caught.value.code == "TARGET_NOT_FOUND"
    with pytest.raises(IssueMarkerError) as caught:
        service.resolve_marker("missing-marker")
    assert caught.value.code == "TARGET_NOT_FOUND"
