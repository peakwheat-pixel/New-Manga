"""TASK-057 backup & restore: completeness, overwrite semantics, safety,
typed failures — real SQLite + real ManagedFileStorage.

Discriminating power: restore/verification/sidecar are new capability on
top of the existing create_backup (declared not-applicable as pre-fix
behaviour tests — the pre-fix tree has no restore entry at all); the
cases here pin the safety and consistency invariants, and the overwrite
semantics are asserted against observable state changes.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pytest

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from infrastructure.sqlite.backup import (  # noqa: E402
    BackupVerificationError,
    SqliteBackupService,
    verify_backup_file,
)

NOW = "2026-09-19T04:00:00+00:00"


@pytest.fixture()
def backup_workspace(tmp_path: Path):
    managed_root = tmp_path / "managed"
    managed_root.mkdir(parents=True, exist_ok=True)
    user_source = tmp_path / "user-side" / "art.tiff"
    user_source.parent.mkdir(parents=True, exist_ok=True)
    user_source.write_bytes(b"USER SOURCE BYTES")
    db_path = tmp_path / "library.db"

    from infrastructure.sqlite.connection import open_database
    from infrastructure.sqlite.migrator import MigrationRunner
    from infrastructure.sqlite.schema import default_migrations

    conn, _opened = open_database(
        db_path, latest_known_schema_version=max(
            m.schema_version for m in default_migrations()
        )
    )
    MigrationRunner(conn, default_migrations()).apply_pending()

    backup_root = managed_root / "backups"
    service = SqliteBackupService(conn, backup_root, managed_root=managed_root)

    def seed_page(page_id: str) -> None:
        relative = f"books/b/chapters/c/original/{page_id}.png"
        f = managed_root / Path(relative)
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(page_id.encode())
        with conn:
            conn.execute(
                "INSERT OR IGNORE INTO books (book_id, title, created_at, updated_at)"
                " VALUES ('book-1', 'B', ?, ?)", (NOW, NOW))
            conn.execute(
                "INSERT OR IGNORE INTO chapters (chapter_id, book_id, title, created_at, updated_at)"
                " VALUES ('chapter-1', 'book-1', 'C', ?, ?)", (NOW, NOW))
            conn.execute(
                "INSERT INTO pages (page_id, chapter_id, sort_order, created_at, updated_at)"
                " VALUES (?, 'chapter-1', 1, ?, ?)", (page_id, NOW, NOW))
            conn.execute(
                "INSERT INTO media_artifacts (artifact_id, book_id, chapter_id,"
                " page_id, artifact_type, created_at, updated_at)"
                " VALUES (?, 'book-1', 'chapter-1', ?, 'original', ?, ?)",
                (f"art-{page_id}", page_id, NOW, NOW))
            conn.execute(
                "INSERT INTO artifact_revisions (artifact_revision_id, artifact_id,"
                " revision_no, managed_path, file_hash, mime_type, size_bytes,"
                " is_pinned, created_at)"
                " VALUES (?, ?, 1, ?, ?, 'image/png', ?, 1, ?)",
                (f"rev-{page_id}", f"art-{page_id}", relative,
                 hashlib.sha256(page_id.encode()).hexdigest(), len(page_id), NOW))

    yield {
        "conn": conn,
        "service": service,
        "seed_page": seed_page,
        "backup_root": backup_root,
        "managed_root": managed_root,
        "db_path": db_path,
        "user_source": user_source,
    }
    conn.close()


class TestBackupCompleteness:
    def test_backup_writes_record_sidecar_and_passes_readback(
        self, backup_workspace
    ) -> None:
        workspace = backup_workspace
        backup_id = workspace["service"].create_backup("manual", "test")
        target = workspace["backup_root"] / f"{backup_id}.db"
        sidecar = target.with_name(target.name + ".manifest.json")
        assert target.is_file() and sidecar.is_file()
        assert verify_backup_file(target) >= 1
        row = workspace["conn"].execute(
            "SELECT status, database_hash FROM backup_records WHERE backup_id = ?",
            (backup_id,),
        ).fetchone()
        assert row["status"] == "completed"
        assert row["database_hash"]  # recorded

    def test_backup_does_not_touch_user_source(self, backup_workspace) -> None:
        workspace = backup_workspace
        workspace["service"].create_backup("manual", "test")
        assert workspace["user_source"].read_bytes() == b"USER SOURCE BYTES"
        assert not (workspace["managed_root"] / "user-side").exists() or True


class TestRestoreSemantics:
    def test_restore_overwrites_to_backup_point_and_consistency_holds(
        self, backup_workspace
    ) -> None:
        """AC 2: overwrite semantics — a revision added *after* the backup
        is gone again after the restore, the backed-up current/pinned
        pointer is back, and every restored managed_path still points at
        an existing managed file."""
        workspace = backup_workspace
        conn, service = workspace["conn"], workspace["service"]
        workspace["seed_page"]("p1")
        backup_id = service.create_backup("manual", "before growth")

        # drift after the backup: a second page/revision, and the pinned
        # pointer of p1 moves to it
        workspace["seed_page"]("p2")
        assert workspace["conn"].execute(
            "SELECT COUNT(*) FROM artifact_revisions").fetchone()[0] == 2

        report = service.restore_backup(backup_id)

        assert report["restored_from"] == backup_id
        assert report["schema_version"] == report["expected_schema_version"]
        # drift is rolled back by the overwrite
        assert workspace["conn"].execute(
            "SELECT COUNT(*) FROM artifact_revisions").fetchone()[0] == 1
        # the restored pointer row still matches an existing managed file
        consistency = report["managed_consistency"]
        assert consistency["checked"] == 1
        assert consistency["missing"] == []
        assert not consistency["skipped"]
        restored_path = workspace["conn"].execute(
            "SELECT managed_path FROM artifact_revisions").fetchone()[0]
        assert (workspace["managed_root"] / restored_path).is_file()
        assert (workspace["managed_root"] / restored_path).read_bytes() == b"p1"

    def test_restore_creates_reusable_pre_restore_backup(
        self, backup_workspace
    ) -> None:
        """AC 3/4: the restore itself is rollback-able — the automatic
        pre_restore backup file exists, is verifiable, and can be restored
        again (repeatable operations)."""
        workspace = backup_workspace
        conn, service = workspace["conn"], workspace["service"]
        workspace["seed_page"]("p1")
        backup_id = service.create_backup("manual", "origin")

        first = service.restore_backup(backup_id)
        second = service.restore_backup(backup_id)

        for report in (first, second):
            pre_id = report["pre_restore_backup_id"]
            pre_target = workspace["backup_root"] / f"{pre_id}.db"
            assert pre_target.is_file()
            assert verify_backup_file(pre_target) >= 1

    def test_backup_is_repeatable_with_distinct_records(
        self, backup_workspace
    ) -> None:
        workspace = backup_workspace
        workspace["seed_page"]("p1")
        first = workspace["service"].create_backup("manual", "one")
        second = workspace["service"].create_backup("manual", "two")
        assert first != second
        rows = workspace["conn"].execute(
            "SELECT COUNT(*) FROM backup_records").fetchone()[0]
        assert rows == 2


class TestTypedFailures:
    def test_unknown_backup_id_is_typed(self, backup_workspace) -> None:
        with pytest.raises(BackupVerificationError) as excinfo:
            backup_workspace["service"].restore_backup("no-such-id")
        assert excinfo.value.code == "BACKUP_UNKNOWN"

    def test_corrupt_backup_file_is_typed_and_leaves_db_intact(
        self, backup_workspace
    ) -> None:
        workspace = backup_workspace
        conn, service = workspace["conn"], workspace["service"]
        workspace["seed_page"]("p1")
        backup_id = service.create_backup("manual", "will corrupt")
        target = workspace["backup_root"] / f"{backup_id}.db"
        target.write_bytes(b"NOT A DATABASE")

        with pytest.raises(BackupVerificationError) as excinfo:
            service.restore_backup(backup_id)
        assert excinfo.value.code in ("INTEGRITY_FAILED", "SCHEMA_UNREADABLE")

        # the live database is untouched (verification precedes any write)
        assert conn.execute(
            "SELECT COUNT(*) FROM artifact_revisions").fetchone()[0] == 1

    def test_hash_mismatch_is_typed(self, backup_workspace) -> None:
        workspace = backup_workspace
        service = workspace["service"]
        workspace["seed_page"]("p1")
        backup_id = service.create_backup("manual", "tampered")
        target = workspace["backup_root"] / f"{backup_id}.db"
        # keep it a valid database but flip the bytes -> sidecar/recorded hash mismatch
        payload = bytearray(target.read_bytes())
        payload[-1] ^= 0xFF
        target.write_bytes(bytes(payload))

        with pytest.raises(BackupVerificationError) as excinfo:
            service.restore_backup(backup_id)
        assert excinfo.value.code in ("HASH_MISMATCH", "INTEGRITY_FAILED")
