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
import sqlite3
import sys
from pathlib import Path
from unittest.mock import Mock

import pytest

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

import infrastructure.sqlite.backup as backup_module  # noqa: E402
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
    def test_create_backup_runs_readback_before_recording_completed(
        self, backup_workspace, monkeypatch
    ) -> None:
        workspace = backup_workspace
        original = backup_module.verify_backup_file
        verifier = Mock(side_effect=original)
        monkeypatch.setattr(backup_module, "verify_backup_file", verifier)

        backup_id = workspace["service"].create_backup("manual", "test")

        verifier.assert_called_once()
        verified = verifier.call_args.args[0]
        assert verified.parent == workspace["backup_root"]
        assert verified.name.startswith(f".{backup_id}.tmp-")
        assert verified.name.endswith(".db")

    def test_abrupt_publish_interruption_leaves_no_half_artifact(
        self, backup_workspace, monkeypatch
    ) -> None:
        workspace = backup_workspace
        real_replace = backup_module.os.replace

        def interrupt_after_database_publish(source, destination) -> None:
            real_replace(source, destination)
            published = Path(destination)
            if published.suffix == ".db" and not published.name.startswith("."):
                raise SystemExit("forced interruption")

        monkeypatch.setattr(backup_module.os, "replace", interrupt_after_database_publish)

        with pytest.raises(SystemExit, match="forced interruption"):
            workspace["service"].create_backup("manual", "test")

        assert list(workspace["backup_root"].iterdir()) == []
        assert workspace["conn"].execute(
            "SELECT COUNT(*) FROM backup_records"
        ).fetchone()[0] == 0

    def test_readback_failure_is_typed_and_leaves_no_artifacts(
        self, backup_workspace, monkeypatch
    ) -> None:
        workspace = backup_workspace
        monkeypatch.setattr(
            backup_module,
            "verify_backup_file",
            Mock(side_effect=BackupVerificationError("INTEGRITY_FAILED", "forced")),
        )

        with pytest.raises(BackupVerificationError) as excinfo:
            workspace["service"].create_backup("manual", "test")

        assert excinfo.value.code == "BACKUP_CREATE_FAILED"
        assert list(workspace["backup_root"].iterdir()) == []
        assert workspace["conn"].execute(
            "SELECT COUNT(*) FROM backup_records"
        ).fetchone()[0] == 0

    def test_sidecar_failure_is_typed_and_leaves_no_artifacts(
        self, backup_workspace, monkeypatch
    ) -> None:
        workspace = backup_workspace
        monkeypatch.setattr(
            backup_module,
            "write_sidecar",
            Mock(side_effect=OSError("forced sidecar failure")),
        )

        with pytest.raises(BackupVerificationError) as excinfo:
            workspace["service"].create_backup("manual", "test")

        assert excinfo.value.code == "BACKUP_CREATE_FAILED"
        assert list(workspace["backup_root"].iterdir()) == []
        assert workspace["conn"].execute(
            "SELECT COUNT(*) FROM backup_records"
        ).fetchone()[0] == 0

    def test_ledger_failure_is_typed_and_leaves_no_artifacts(
        self, backup_workspace
    ) -> None:
        workspace = backup_workspace
        workspace["conn"].execute(
            "CREATE TRIGGER reject_backup_record BEFORE INSERT ON backup_records "
            "BEGIN SELECT RAISE(ABORT, 'forced ledger failure'); END"
        )

        with pytest.raises(BackupVerificationError) as excinfo:
            workspace["service"].create_backup("manual", "test")

        assert excinfo.value.code == "BACKUP_CREATE_FAILED"
        assert list(workspace["backup_root"].iterdir()) == []
        assert workspace["conn"].execute(
            "SELECT COUNT(*) FROM backup_records"
        ).fetchone()[0] == 0

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
        # Q-008 前置②: this assertion used to carry a truthy tail (`or True`),
        # which made the AC③ boundary unpolicable — a regression writing a
        # user-side shadow into the managed root passed silently (pre-fix
        # discriminating evidence:
        # verification/TASK-057/pre-fix-probes/pre-fix-q008-truthy-run2.log).
        # Real boundaries now: no user-side shadow inside the managed root,
        # and the user-side directory keeps exactly the source file.
        assert not (workspace["managed_root"] / "user-side").exists(), (
            "AC③ breach: backup wrote a user-side shadow into the managed root"
        )
        assert [
            p.name for p in workspace["user_source"].parent.iterdir()
        ] == ["art.tiff"], (
            "AC③ breach: backup wrote files into the user source directory"
        )


class TestRestoreSemantics:
    def test_restore_migrates_a_v0_pre_migration_backup(self, tmp_path) -> None:
        from infrastructure.sqlite.connection import open_database
        from infrastructure.sqlite.migrator import MigrationRunner
        from infrastructure.sqlite.schema import default_migrations

        latest = default_migrations()[-1].schema_version
        conn, _opened = open_database(
            tmp_path / "library.db", latest_known_schema_version=latest
        )
        service = SqliteBackupService(conn, tmp_path / "backups")
        try:
            backup_id = service.create_backup("pre_migration", "v0 snapshot")
            MigrationRunner(conn, default_migrations()).apply_pending()
            assert backup_module.read_schema_version(conn) == latest

            report = service.restore_backup(backup_id)

            assert report["schema_version"] == latest
            assert report["expected_schema_version"] == latest
            assert backup_module.read_schema_version(conn) == latest
        finally:
            conn.close()

    def test_restore_failure_is_typed_and_rolls_back_live_database(
        self, backup_workspace, monkeypatch
    ) -> None:
        workspace = backup_workspace
        conn, service = workspace["conn"], workspace["service"]
        workspace["seed_page"]("p1")
        backup_id = service.create_backup("manual", "restore target")
        original_restore = service._restore_database
        calls = 0

        def fail_once(target: Path) -> None:
            nonlocal calls
            calls += 1
            if calls == 1:
                raise sqlite3.ProgrammingError("forced destination failure")
            original_restore(target)

        monkeypatch.setattr(service, "_restore_database", fail_once)

        with pytest.raises(BackupVerificationError) as excinfo:
            service.restore_backup(backup_id)

        assert excinfo.value.code == "RESTORE_FAILED"
        assert "pre_restore=" in excinfo.value.detail
        assert calls == 2
        assert backup_module.read_schema_version(conn) == 4
        assert conn.execute(
            "SELECT COUNT(*) FROM artifact_revisions"
        ).fetchone()[0] == 1

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
        translated_path = "books/b/chapters/c/translated/p1.png"
        translated_file = workspace["managed_root"] / translated_path
        translated_file.parent.mkdir(parents=True, exist_ok=True)
        translated_file.write_bytes(b"translated-v1")
        with conn:
            conn.execute(
                "UPDATE media_artifacts SET current_revision_id = 'rev-p1'"
                " WHERE artifact_id = 'art-p1'"
            )
            conn.execute(
                "INSERT INTO media_artifacts (artifact_id, book_id, chapter_id,"
                " page_id, artifact_type, created_at, updated_at)"
                " VALUES ('art-translated-p1', 'book-1', 'chapter-1', 'p1',"
                " 'translated', ?, ?)",
                (NOW, NOW),
            )
            conn.execute(
                "INSERT INTO artifact_revisions (artifact_revision_id, artifact_id,"
                " revision_no, managed_path, file_hash, mime_type, size_bytes,"
                " is_pinned, created_at)"
                " VALUES ('rev-translated-p1', 'art-translated-p1', 1, ?, ?,"
                " 'image/png', ?, 1, ?)",
                (
                    translated_path,
                    hashlib.sha256(b"translated-v1").hexdigest(),
                    len(b"translated-v1"),
                    NOW,
                ),
            )
            conn.execute(
                "UPDATE media_artifacts"
                " SET current_revision_id = 'rev-translated-p1'"
                " WHERE artifact_id = 'art-translated-p1'"
            )
        backup_id = service.create_backup("manual", "before growth")

        # Drift both current pointers and both pinned revisions after backup.
        original_v2 = "books/b/chapters/c/original/p1-v2.png"
        translated_v2 = "books/b/chapters/c/translated/p1-v2.png"
        for relative, payload in (
            (original_v2, b"original-v2"),
            (translated_v2, b"translated-v2"),
        ):
            candidate = workspace["managed_root"] / relative
            candidate.parent.mkdir(parents=True, exist_ok=True)
            candidate.write_bytes(payload)
        with conn:
            conn.execute("UPDATE artifact_revisions SET is_pinned = 0")
            for revision_id, artifact_id, relative, payload in (
                ("rev-p1-v2", "art-p1", original_v2, b"original-v2"),
                (
                    "rev-translated-p1-v2",
                    "art-translated-p1",
                    translated_v2,
                    b"translated-v2",
                ),
            ):
                conn.execute(
                    "INSERT INTO artifact_revisions (artifact_revision_id,"
                    " artifact_id, revision_no, managed_path, file_hash, mime_type,"
                    " size_bytes, is_pinned, created_at)"
                    " VALUES (?, ?, 2, ?, ?, 'image/png', ?, 1, ?)",
                    (
                        revision_id,
                        artifact_id,
                        relative,
                        hashlib.sha256(payload).hexdigest(),
                        len(payload),
                        NOW,
                    ),
                )
                conn.execute(
                    "UPDATE media_artifacts SET current_revision_id = ?"
                    " WHERE artifact_id = ?",
                    (revision_id, artifact_id),
                )

        report = service.restore_backup(backup_id)

        assert report["restored_from"] == backup_id
        assert report["schema_version"] == report["expected_schema_version"]
        pointers = {
            row["artifact_type"]: row["current_revision_id"]
            for row in conn.execute(
                "SELECT artifact_type, current_revision_id FROM media_artifacts"
            )
        }
        assert pointers == {
            "original": "rev-p1",
            "translated": "rev-translated-p1",
        }
        pinned = {
            row[0]
            for row in conn.execute(
                "SELECT artifact_revision_id FROM artifact_revisions"
                " WHERE is_pinned = 1"
            )
        }
        assert pinned == {"rev-p1", "rev-translated-p1"}
        assert conn.execute(
            "SELECT COUNT(*) FROM artifact_revisions"
        ).fetchone()[0] == 2
        consistency = report["managed_consistency"]
        assert consistency["checked"] == 2
        assert consistency["missing"] == []
        assert not consistency["skipped"]
        restored = {
            row[0]: (workspace["managed_root"] / row[1]).read_bytes()
            for row in conn.execute(
                "SELECT artifact_revision_id, managed_path FROM artifact_revisions"
            )
        }
        assert restored == {
            "rev-p1": b"p1",
            "rev-translated-p1": b"translated-v1",
        }

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

    def test_hash_read_failure_is_typed_and_leaves_live_untouched(
        self, backup_workspace, monkeypatch
    ) -> None:
        workspace = backup_workspace
        conn, service = workspace["conn"], workspace["service"]
        workspace["seed_page"]("p1")
        backup_id = service.create_backup("manual", "unreadable")
        records_before = conn.execute(
            "SELECT COUNT(*) FROM backup_records"
        ).fetchone()[0]
        monkeypatch.setattr(
            backup_module,
            "sha256_file",
            Mock(side_effect=OSError("forced read failure")),
        )

        with pytest.raises(BackupVerificationError) as excinfo:
            service.restore_backup(backup_id)

        assert excinfo.value.code == "BACKUP_FILE_UNREADABLE"
        assert conn.execute(
            "SELECT COUNT(*) FROM artifact_revisions"
        ).fetchone()[0] == 1
        assert conn.execute(
            "SELECT COUNT(*) FROM backup_records"
        ).fetchone()[0] == records_before

    def test_restore_rejects_backup_id_path_escape(self, backup_workspace) -> None:
        workspace = backup_workspace
        service = workspace["service"]
        workspace["seed_page"]("p1")
        backup_id = service.create_backup("manual", "move outside root")
        target = workspace["backup_root"] / f"{backup_id}.db"
        sidecar = target.with_name(target.name + ".manifest.json")
        outside = workspace["backup_root"].parent / "escaped.db"
        outside_sidecar = outside.with_name(outside.name + ".manifest.json")
        target.replace(outside)
        sidecar.replace(outside_sidecar)

        for invalid_id in ("../escaped", str(outside.with_suffix(""))):
            with pytest.raises(BackupVerificationError) as excinfo:
                service.restore_backup(invalid_id)
            assert excinfo.value.code == "BACKUP_UNKNOWN"
        assert workspace["conn"].execute(
            "SELECT COUNT(*) FROM artifact_revisions"
        ).fetchone()[0] == 1

    def test_restore_rejects_schema_metadata_mismatch(
        self, backup_workspace
    ) -> None:
        workspace = backup_workspace
        service = workspace["service"]
        backup_id = service.create_backup("manual", "mismatched metadata")
        target = workspace["backup_root"] / f"{backup_id}.db"
        backup_module.write_sidecar(
            target,
            schema_version=999,
            database_hash=backup_module.sha256_file(target),
            app_version=None,
            created_at=NOW,
        )

        with pytest.raises(BackupVerificationError) as excinfo:
            service.restore_backup(backup_id)

        assert excinfo.value.code == "SCHEMA_MISMATCH"

    def test_restore_rejects_schema_newer_than_application(
        self, backup_workspace
    ) -> None:
        workspace = backup_workspace
        conn, service = workspace["conn"], workspace["service"]
        workspace["seed_page"]("p1")
        backup_id = service.create_backup("manual", "future schema")
        target = workspace["backup_root"] / f"{backup_id}.db"
        future = sqlite3.connect(target)
        try:
            future.execute(
                "INSERT INTO schema_migrations"
                " (schema_version, migration_name, applied_at, checksum)"
                " VALUES (999, 'future', ?, 'future')",
                (NOW,),
            )
            future.commit()
        finally:
            future.close()
        database_hash = backup_module.sha256_file(target)
        backup_module.write_sidecar(
            target,
            schema_version=999,
            database_hash=database_hash,
            app_version=None,
            created_at=NOW,
        )
        with conn:
            conn.execute(
                "UPDATE backup_records SET schema_version = 999, database_hash = ?"
                " WHERE backup_id = ?",
                (database_hash, backup_id),
            )

        with pytest.raises(BackupVerificationError) as excinfo:
            service.restore_backup(backup_id)

        assert excinfo.value.code == "SCHEMA_TOO_NEW"
        assert backup_module.read_schema_version(conn) == 4
        assert conn.execute(
            "SELECT COUNT(*) FROM artifact_revisions"
        ).fetchone()[0] == 1
