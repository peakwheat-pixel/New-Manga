"""FEA-14-READ-1: schema v10 + per-book preferences/bookmarks/whole-book progress."""

from __future__ import annotations

from pathlib import Path
import sqlite3
import sys

import pytest

THIS_DIR = Path(__file__).resolve().parent
SRC_ROOT = THIS_DIR.parents[1] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from application.reading.service import ReadingExtrasService  # noqa: E402
from infrastructure.sqlite.migrator import MigrationRunner, read_schema_version  # noqa: E402
from infrastructure.sqlite.reading_export import SqliteReadingExtrasStore  # noqa: E402
from infrastructure.sqlite.schema import default_migrations  # noqa: E402

MIGRATIONS = default_migrations()
LATEST = MIGRATIONS[-1].schema_version


def _connect(tmp_path: Path) -> sqlite3.Connection:
    return sqlite3.connect(tmp_path / "library.db")


def _migrate(conn: sqlite3.Connection, upto: int | None = None) -> None:
    chosen = MIGRATIONS if upto is None else MIGRATIONS[:upto]
    MigrationRunner(conn, chosen).apply_pending()


def _service(tmp_path: Path):
    conn = _connect(tmp_path)
    _migrate(conn)
    return conn, ReadingExtrasService(SqliteReadingExtrasStore(conn))


def test_v10_creates_tables_and_adds_progress_columns(tmp_path):
    conn = _connect(tmp_path)
    _migrate(conn)
    assert read_schema_version(conn) == LATEST == 10
    tables = {row[0] for row in conn.execute("select name from sqlite_master where type='table'")}
    assert {"reading_preferences", "reading_bookmarks"} <= tables
    indexes = {row[0] for row in conn.execute("select name from sqlite_master where type='index'")}
    assert "idx_reading_bookmarks_book" in indexes
    columns = {row[1] for row in conn.execute("pragma table_info(reading_progress)")}
    assert {"anchor_json", "viewport_json"} <= columns


def test_v10_migration_preserves_legacy_progress_rows(tmp_path):
    conn = _connect(tmp_path)
    _migrate(conn, upto=9)
    assert read_schema_version(conn) == 9
    conn.execute(
        "INSERT INTO reading_progress (progress_id, book_id, chapter_id, mode,"
        " last_page_id, scroll_offset_x, scroll_offset_y, progress_percent, updated_at)"
        " VALUES ('p1', 'b1', 'c1', 'original', 'page-1', 0.0, 0.0, 50.0, '2026-01-01')"
    )
    conn.commit()
    _migrate(conn)
    assert read_schema_version(conn) == 10
    row = conn.execute(
        "SELECT progress_percent, anchor_json, viewport_json FROM reading_progress WHERE progress_id = 'p1'"
    ).fetchone()
    assert row[0] == 50.0
    assert row[1] is None and row[2] is None


def test_preferences_roundtrip_defaults_and_validation(tmp_path):
    conn, service = _service(tmp_path)
    default = service.get_preferences("b1")
    assert default["is_default"] is True
    assert default["mode"] == "original" and default["zoom"] == 1.0

    saved = service.save_preferences(
        "b1", mode="translated", direction="rtl", zoom=1.5, double_page=True, layout="double"
    )
    assert saved["is_default"] is False
    assert saved["mode"] == "translated" and saved["direction"] == "rtl"
    assert saved["double_page"] is True and saved["layout"] == "double"
    again = service.get_preferences("b1")
    assert again["zoom"] == 1.5 and again["direction"] == "rtl"

    with pytest.raises(ValueError):
        service.save_preferences("b1", mode="unknown")
    with pytest.raises(ValueError):
        service.save_preferences("b1", direction="sideways")
    with pytest.raises(ValueError):
        service.save_preferences("b1", layout="grid")
    with pytest.raises(ValueError):
        service.save_preferences("b1", zoom=0.0)
    with pytest.raises(ValueError):
        service.save_preferences("b1", zoom=9.0)


def test_bookmarks_create_list_delete_and_book_isolation(tmp_path):
    conn, service = _service(tmp_path)
    first = service.create_bookmark(
        "b1", chapter_id="c1", page_id="p1", side="left", note="keep this"
    )
    second = service.create_bookmark("b1", chapter_id="c1", page_id="p2")
    other = service.create_bookmark("b2", chapter_id="c9", page_id="p9")
    listed = service.list_bookmarks("b1")
    assert [item["bookmark_id"] for item in listed] == [first["bookmark_id"], second["bookmark_id"]]
    assert listed[0]["side"] == "left" and listed[0]["note"] == "keep this"
    assert {item["bookmark_id"] for item in service.list_bookmarks("b2")} == {other["bookmark_id"]}

    assert service.delete_bookmark(second["bookmark_id"]) is True
    assert service.delete_bookmark(second["bookmark_id"]) is False
    assert [item["bookmark_id"] for item in service.list_bookmarks("b1")] == [first["bookmark_id"]]

    with pytest.raises(ValueError):
        service.create_bookmark("b1", chapter_id="c1", page_id="p3", side="middle")


def test_book_progress_and_reset_requires_confirm(tmp_path):
    conn, service = _service(tmp_path)
    conn.execute(
        "INSERT INTO books (book_id, title, created_at, updated_at)"
        " VALUES ('b1', 'A4 Book', '2026-01-01', '2026-01-01')"
    )
    conn.execute(
        "INSERT INTO chapters (chapter_id, book_id, title, chapter_type, sort_order, created_at, updated_at)"
        " VALUES ('c1', 'b1', 'Ch 1', 'paged', 1, '2026-01-01', '2026-01-01')"
    )
    conn.execute(
        "INSERT INTO chapters (chapter_id, book_id, title, chapter_type, sort_order, created_at, updated_at)"
        " VALUES ('c2', 'b1', 'Ch 2', 'paged', 2, '2026-01-01', '2026-01-01')"
    )
    for index in (1, 2):
        conn.execute(
            "INSERT INTO pages (page_id, chapter_id, sort_order, created_at, updated_at)"
            " VALUES (?, 'c1', ?, '2026-01-01', '2026-01-01')",
            (f"c1p{index}", index),
        )
    conn.execute(
        "INSERT INTO reading_progress (progress_id, book_id, chapter_id, mode,"
        " last_page_id, scroll_offset_x, scroll_offset_y, progress_percent, updated_at)"
        " VALUES ('p1', 'b1', 'c1', 'original', 'c1p2', 0.0, 0.0, 100.0, '2026-01-01')"
    )
    conn.commit()
    progress = service.book_progress("b1")
    # R-001: page based -- c1 has 2 pages and is fully read.
    assert progress["total_pages"] == 2
    assert progress["read_pages"] == 2
    assert progress["progress_percent"] == 100.0
    assert progress["finished"] is True

    with pytest.raises(ValueError):
        service.reset_book_progress("b1")
    removed = service.reset_book_progress("b1", confirm=True)
    assert removed == 1
    after = service.book_progress("b1")
    assert after["completed_chapters"] == 0 and after["progress_percent"] == 0.0


def test_partial_preferences_patch_keeps_other_fields(tmp_path):
    conn, service = _service(tmp_path)
    service.save_preferences("b1", mode="translated", direction="rtl", zoom=1.5, layout="double")
    # R-004: only zoom is provided; the other fields must survive.
    updated = service.save_preferences("b1", zoom=2.0)
    assert updated["zoom"] == 2.0
    assert updated["mode"] == "translated" and updated["direction"] == "rtl"
    assert updated["layout"] == "double"


def test_preferences_survive_reopen_two_assemblies(tmp_path):
    conn, service = _service(tmp_path)
    service.save_preferences("b1", mode="translated", direction="rtl", zoom=2.0)
    conn.close()
    # R-011: a second assembly (fresh connection) reads the persisted row.
    conn2 = _connect(tmp_path)
    _migrate(conn2)
    again = ReadingExtrasService(SqliteReadingExtrasStore(conn2)).get_preferences("b1")
    assert again["mode"] == "translated" and again["direction"] == "rtl" and again["zoom"] == 2.0


def test_explicit_default_values_can_reset_preferences(tmp_path):
    conn, service = _service(tmp_path)
    service.save_preferences("b1", mode="translated", direction="rtl", zoom=2.0, double_page=True, layout="double")
    # R3-001: explicit defaults must reset, not be ignored as "not provided".
    reset = service.save_preferences(
        "b1", mode="original", direction="ltr", zoom=1.0, double_page=False, layout="single"
    )
    assert reset["mode"] == "original" and reset["direction"] == "ltr"
    assert reset["zoom"] == 1.0 and reset["double_page"] is False and reset["layout"] == "single"
