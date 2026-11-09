"""FEA-13-RESTORE-4: merge restore planning and application.

Covers the conflict model in ``ADJ-2026-11-09-FEA13-RESTORE-MODEL``: the plan is
strictly read-only, the default ``defer`` mode applies adds only, conflicts keep
the live value, live-only rows are never deleted, and ``UseBackup`` preserves the
live value before overwriting it.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from application.maintenance.restore_plan import (  # noqa: E402
    apply_restore,
    plan_restore,
)
from infrastructure.sqlite.nmbak import NmbakBackupService  # noqa: E402

NOW = "2026-11-09T15:00:00+00:00"


def _open(tmp_path: Path):
    from infrastructure.sqlite.connection import open_database
    from infrastructure.sqlite.migrator import MigrationRunner
    from infrastructure.sqlite.schema import default_migrations

    data_root = tmp_path / "data"
    managed_root = data_root / "managed"
    managed_root.mkdir(parents=True, exist_ok=True)
    conn, _opened = open_database(
        data_root / "library.db",
        latest_known_schema_version=max(m.schema_version for m in default_migrations()),
    )
    MigrationRunner(conn, default_migrations()).apply_pending()
    return conn, data_root, managed_root


def _seed(conn, managed_root: Path, *, title: str = "B") -> str:
    relative = "books/book-1/chapters/chapter-1/original/page-1.png"
    managed = managed_root / Path(relative)
    managed.parent.mkdir(parents=True, exist_ok=True)
    managed.write_bytes(b"PAGE-ONE")
    digest = hashlib.sha256(b"PAGE-ONE").hexdigest()
    with conn:
        conn.execute(
            "INSERT OR IGNORE INTO books (book_id, title, created_at, updated_at)"
            " VALUES ('book-1', ?, ?, ?)",
            (title, NOW, NOW),
        )
        conn.execute(
            "INSERT OR IGNORE INTO chapters (chapter_id, book_id, title,"
            " created_at, updated_at) VALUES ('chapter-1', 'book-1', 'C', ?, ?)",
            (NOW, NOW),
        )
        conn.execute(
            "INSERT OR IGNORE INTO pages (page_id, chapter_id, sort_order,"
            " created_at, updated_at) VALUES ('page-1', 'chapter-1', 1, ?, ?)",
            (NOW, NOW),
        )
        conn.execute(
            "INSERT OR IGNORE INTO media_artifacts (artifact_id, book_id,"
            " chapter_id, page_id, artifact_type, created_at, updated_at)"
            " VALUES ('art-1', 'book-1', 'chapter-1', 'page-1', 'original', ?, ?)",
            (NOW, NOW),
        )
        conn.execute(
            "INSERT OR IGNORE INTO artifact_revisions (artifact_revision_id,"
            " artifact_id, revision_no, managed_path, file_hash, mime_type,"
            " size_bytes, is_pinned, created_at)"
            " VALUES ('rev-1', 'art-1', 1, ?, ?, 'image/png', 8, 1, ?)",
            (relative, digest, NOW),
        )
        conn.execute(
            "UPDATE media_artifacts SET current_revision_id = 'rev-1'"
            " WHERE artifact_id = 'art-1'"
        )
    return relative


def _service(conn, data_root, managed_root):
    return NmbakBackupService(
        conn,
        data_root / "backups",
        managed_root,
        app_version="0.1.0",
        data_root=data_root,
    )


def _snapshot(conn, managed_root: Path, package: Path) -> dict:
    return {
        "books": [tuple(row) for row in conn.execute("SELECT * FROM books ORDER BY book_id")],
        "pages": [tuple(row) for row in conn.execute("SELECT * FROM pages ORDER BY page_id")],
        "managed": {
            path.relative_to(managed_root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in managed_root.rglob("*")
            if path.is_file()
        },
        "package": hashlib.sha256(package.read_bytes()).hexdigest(),
        "package_mtime": package.stat().st_mtime_ns,
        "managed_mtime": {
            path.relative_to(managed_root).as_posix(): path.stat().st_mtime_ns
            for path in managed_root.rglob("*")
            if path.is_file()
        },
    }


def test_plan_is_read_only_and_classifies_every_item(tmp_path):
    conn, data_root, managed_root = _open(tmp_path)
    _seed(conn, managed_root)
    service = _service(conn, data_root, managed_root)
    created = service.create("manual", "before edits")
    package = data_root / "backups" / f"{created['backup_id']}.nmbak"

    # Live changes after the backup: a conflicting title, a live-only row and a
    # conflicting managed file.
    with conn:
        conn.execute("UPDATE books SET title = 'CHANGED' WHERE book_id = 'book-1'")
        conn.execute(
            "INSERT INTO books (book_id, title, created_at, updated_at)"
            " VALUES ('book-2', 'LIVE-ONLY', ?, ?)",
            (NOW, NOW),
        )
    (managed_root / "books/book-1/chapters/chapter-1/original/page-1.png").write_bytes(
        b"CHANGED!"
    )
    before = _snapshot(conn, managed_root, package)  # state immediately before planning
    context = service.extract_for_plan(created["backup_id"])
    try:
        plan = plan_restore(
            conn,
            context["database_path"],
            managed_root=managed_root,
            backup_entries=context["managed_entries"],
        )
    finally:
        service.cleanup_plan(context)

    after = _snapshot(conn, managed_root, package)
    assert after == before  # planning changed nothing at all

    items = {(item["kind"], item["table"], item["key"]): item["action"] for item in plan["items"]}
    assert items[("row", "books", "book-1")] == "conflict"
    assert items[("row", "books", "book-2")] == "keep"
    assert items[("row", "pages", "page-1")] == "noop"
    managed_key = (
        "managed",
        "managed",
        "books/book-1/chapters/chapter-1/original/page-1.png",
    )
    assert items[managed_key] == "conflict"


def test_defer_applies_adds_only_and_never_overwrites_live(tmp_path):
    conn, data_root, managed_root = _open(tmp_path)
    _seed(conn, managed_root)
    service = _service(conn, data_root, managed_root)
    created = service.create("manual", "before edits")
    with conn:
        conn.execute("UPDATE books SET title = 'CHANGED' WHERE book_id = 'book-1'")
    context = service.extract_for_plan(created["backup_id"])
    try:
        plan = plan_restore(conn, context["database_path"], managed_root=managed_root,
                            backup_entries=context["managed_entries"])
        report = apply_restore(conn, context["database_path"], plan["items"], mode="defer")
    finally:
        service.cleanup_plan(context)

    assert report["failed"] == []
    assert any(item["action"] == "conflict" for item in report["deferred"])
    live_title = conn.execute("SELECT title FROM books WHERE book_id = 'book-1'").fetchone()[0]
    assert live_title == "CHANGED"  # defer kept the live value


def test_use_backup_preserves_the_live_value_then_overwrites(tmp_path):
    conn, data_root, managed_root = _open(tmp_path)
    _seed(conn, managed_root)
    service = _service(conn, data_root, managed_root)
    created = service.create("manual", "before edits")
    with conn:
        conn.execute("UPDATE books SET title = 'CHANGED' WHERE book_id = 'book-1'")
    context = service.extract_for_plan(created["backup_id"])
    try:
        plan = plan_restore(conn, context["database_path"], managed_root=managed_root,
                            backup_entries=context["managed_entries"])
        undo_root = service.plan_undo_root(created["backup_id"])
        report = apply_restore(
            conn,
            context["database_path"],
            plan["items"],
            mode="use_backup",
            use_backup_keys={("books", "book-1")},
            undo_root=undo_root,
        )
    finally:
        service.cleanup_plan(context)

    assert report["failed"] == []
    title = conn.execute("SELECT title FROM books WHERE book_id = 'book-1'").fetchone()[0]
    assert title == "B"  # UseBackup applied the packaged value
    preserved = undo_root / "rows" / "books" / "book-1.json"
    assert preserved.is_file()
    assert json.loads(preserved.read_text(encoding="utf-8"))["title"] == "CHANGED"


def test_use_backup_without_undo_area_fails_closed_per_item(tmp_path):
    conn, data_root, managed_root = _open(tmp_path)
    _seed(conn, managed_root)
    service = _service(conn, data_root, managed_root)
    created = service.create("manual", "before edits")
    with conn:
        conn.execute("UPDATE books SET title = 'CHANGED' WHERE book_id = 'book-1'")
    context = service.extract_for_plan(created["backup_id"])
    try:
        plan = plan_restore(conn, context["database_path"])
        report = apply_restore(
            conn,
            context["database_path"],
            plan["items"],
            mode="use_backup",
            use_backup_keys={("books", "book-1")},
        )
    finally:
        service.cleanup_plan(context)

    assert report["applied"] == []
    assert report["failed"] and "undo" in report["failed"][0]["error"]
    title = conn.execute("SELECT title FROM books WHERE book_id = 'book-1'").fetchone()[0]
    assert title == "CHANGED"  # nothing was overwritten


def test_defer_ignores_use_backup_entries(tmp_path):
    """R4-003: entries are only honoured in use_backup mode."""
    conn, data_root, managed_root = _open(tmp_path)
    _seed(conn, managed_root)
    service = _service(conn, data_root, managed_root)
    created = service.create("manual", "before edits")
    with conn:
        conn.execute("UPDATE books SET title = 'CHANGED' WHERE book_id = 'book-1'")
    context = service.extract_for_plan(created["backup_id"])
    try:
        plan = plan_restore(conn, context["database_path"])
        report = apply_restore(
            conn,
            context["database_path"],
            plan["items"],
            mode="defer",
            use_backup_keys={("books", "book-1")},  # must be ignored under defer
            undo_root=service.plan_undo_root(created["backup_id"]),
        )
    finally:
        service.cleanup_plan(context)

    assert report["applied"] == []
    title = conn.execute("SELECT title FROM books WHERE book_id = 'book-1'").fetchone()[0]
    assert title == "CHANGED"


def test_defer_applies_backup_only_rows(tmp_path):
    """R4-005 of the review: an ``add`` item is actually inserted by defer."""
    conn, data_root, managed_root = _open(tmp_path)
    _seed(conn, managed_root)
    service = _service(conn, data_root, managed_root)
    created = service.create("manual", "with row")
    # Remove the whole seeded tree (children first) so defer has real adds.
    with conn:
        for statement in (
            "DELETE FROM artifact_revisions WHERE artifact_id = 'art-1'",
            "DELETE FROM media_artifacts WHERE artifact_id = 'art-1'",
            "DELETE FROM pages WHERE page_id = 'page-1'",
            "DELETE FROM chapters WHERE chapter_id = 'chapter-1'",
            "DELETE FROM books WHERE book_id = 'book-1'",
        ):
            conn.execute(statement)
    context = service.extract_for_plan(created["backup_id"])
    try:
        plan = plan_restore(conn, context["database_path"])
        report = apply_restore(conn, context["database_path"], plan["items"], mode="defer")
    finally:
        service.cleanup_plan(context)

    added_tables = {item["table"] for item in report["applied"]}
    assert {"books", "chapters", "pages", "media_artifacts", "artifact_revisions"} <= added_tables
    assert conn.execute("SELECT COUNT(*) FROM books").fetchone()[0] == 1


def test_mode_is_validated_before_any_write(tmp_path):
    conn, data_root, managed_root = _open(tmp_path)
    _seed(conn, managed_root)
    service = _service(conn, data_root, managed_root)
    created = service.create("manual", "mode")
    context = service.extract_for_plan(created["backup_id"])
    try:
        plan = plan_restore(conn, context["database_path"])
        with pytest.raises(ValueError):
            apply_restore(conn, context["database_path"], plan["items"], mode="bogus")
    finally:
        service.cleanup_plan(context)
    title = conn.execute("SELECT title FROM books WHERE book_id = 'book-1'").fetchone()[0]
    assert title == "B"  # nothing was written by the rejected call
