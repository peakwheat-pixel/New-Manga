"""SEC-03: nmbak restore failures must surface as typed incomplete restores.

Discriminating power: before the fix, a managed-file write failure during
restore escaped as a bare OSError (``typed_error=false``,
``rollback_id_in_error=false`` in SEG-B-PROBES-002). These tests pin the typed
contract: ``BACKUP_RESTORE_INCOMPLETE`` with the actual pre_restore backup id.
"""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

import pytest

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from infrastructure.sqlite.nmbak import NmbakBackupError, NmbakBackupService  # noqa: E402

NOW = "2026-11-14T00:30:00+00:00"


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


def _seed(conn, managed_root: Path) -> str:
    relative = "books/book-1/chapters/chapter-1/original/page-1.png"
    managed = managed_root / Path(relative)
    managed.parent.mkdir(parents=True, exist_ok=True)
    managed.write_bytes(b"PAGE-ONE")
    digest = hashlib.sha256(b"PAGE-ONE").hexdigest()
    with conn:
        conn.execute(
            "INSERT OR IGNORE INTO books (book_id, title, created_at, updated_at)"
            " VALUES ('book-1', 'B', ?, ?)",
            (NOW, NOW),
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


def _service(conn, data_root: Path, managed_root: Path) -> NmbakBackupService:
    return NmbakBackupService(
        conn,
        data_root / "backups",
        managed_root,
        app_version="0.1.0",
        data_root=data_root,
    )


def test_managed_write_failure_is_typed_and_carries_rollback_id(tmp_path, monkeypatch):
    conn, data_root, managed_root = _open(tmp_path)
    _seed(conn, managed_root)
    service = _service(conn, data_root, managed_root)
    created = service.create("manual", "before restore")

    books_root = str(managed_root / "books")
    original_write = Path.write_bytes

    def failing_write(self: Path, data: bytes) -> int:
        if str(self).startswith(books_root):
            raise OSError("simulated disk full during restore")
        return original_write(self, data)

    monkeypatch.setattr(Path, "write_bytes", failing_write)

    with pytest.raises(NmbakBackupError) as excinfo:
        service.restore(created["backup_id"], confirm_restore=True)

    error = excinfo.value
    assert error.code == "BACKUP_RESTORE_INCOMPLETE"
    assert "rollback package: pre_restore" not in error.detail
    match = re.search(r"rollback package: ([0-9a-f]{32})", error.detail)
    assert match, error.detail
    rollback_id = match.group(1)
    assert (data_root / "backups" / f"{rollback_id}.nmbak").is_file()
    assert rollback_id != created["backup_id"]

    # The pre_restore package must remain a usable rollback point.
    listed = {item["backup_id"]: item for item in service.list_backups()}
    assert rollback_id in listed
    assert listed[rollback_id]["backup_type"] == "pre_restore"


def test_successful_restore_unchanged(tmp_path):
    conn, data_root, managed_root = _open(tmp_path)
    _seed(conn, managed_root)
    service = _service(conn, data_root, managed_root)
    created = service.create("manual", "before restore")

    report = service.restore(created["backup_id"], confirm_restore=True)

    assert report["restored_from"] == created["backup_id"]
    assert report["pre_restore_backup_id"]
    assert (data_root / "backups" / f"{report['pre_restore_backup_id']}.nmbak").is_file()
    assert (managed_root / "books/book-1/chapters/chapter-1/original/page-1.png").read_bytes() == b"PAGE-ONE"
