"""Schema migration, checksum, backup hook and stale-app gating tests."""

from __future__ import annotations

import sqlite3

import pytest

from infrastructure.sqlite.backup import SqliteBackupService
from infrastructure.sqlite.connection import (
    SchemaTooNewError,
    open_database,
)
from infrastructure.sqlite.migrator import MigrationRunner, read_schema_version
from infrastructure.sqlite.schema import default_migrations

LATEST_KNOWN = default_migrations()[-1].schema_version


def test_v1_applies_with_checksum_and_metadata(db_conn):
    version = read_schema_version(db_conn)
    assert version == LATEST_KNOWN == 1

    row = db_conn.execute(
        "SELECT migration_name, checksum FROM schema_migrations WHERE schema_version = 1"
    ).fetchone()
    migration = default_migrations()[0]
    assert row["migration_name"] == migration.migration_name
    assert row["checksum"] == migration.checksum

    metadata = db_conn.execute(
        "SELECT value_json FROM application_metadata WHERE metadata_key = 'schema_version'"
    ).fetchone()
    assert metadata["value_json"] == str(LATEST_KNOWN)


def test_reopening_is_idempotent(tmp_path):
    db_path = tmp_path / "x.db"
    conn, opened = open_database(db_path, latest_known_schema_version=LATEST_KNOWN)
    assert opened.state.value == "empty"
    runner = MigrationRunner(conn, default_migrations())
    applied = runner.apply_pending()
    assert [record.schema_version for record in applied] == [LATEST_KNOWN]
    assert runner.pending_migrations() == []
    assert runner.apply_pending() == []

    conn2, opened2 = open_database(db_path, latest_known_schema_version=LATEST_KNOWN)
    assert opened2.state.value == "ready"
    assert opened2.schema_version == LATEST_KNOWN
    assert opened2.writable
    conn.close()
    conn2.close()


def test_newer_schema_is_rejected_and_readonly(tmp_path):
    db_path = tmp_path / "future.db"
    conn, _ = open_database(db_path, latest_known_schema_version=LATEST_KNOWN)
    runner = MigrationRunner(conn, default_migrations())
    runner.apply_pending()
    with conn:
        conn.execute(
            "INSERT INTO schema_migrations (schema_version, migration_name, applied_at, checksum)"
            " VALUES (2, 'future', '2026-01-01T00:00:00Z', 'nope')"
        )
        conn.execute(
            "UPDATE application_metadata SET value_json = '2'"
            " WHERE metadata_key = 'schema_version'"
        )
    conn.close()

    reopened, opened = open_database(db_path, latest_known_schema_version=LATEST_KNOWN)
    assert opened.state.value == "too_new"
    assert not opened.writable
    with pytest.raises(sqlite3.OperationalError):
        reopened.execute(
            "INSERT INTO application_metadata (metadata_key, value_json, updated_at)"
            " VALUES ('x', '1', '2026-01-01T00:00:00Z')"
        )
    with pytest.raises(SchemaTooNewError):
        MigrationRunner(reopened, default_migrations()).apply_pending()
    reopened.close()


def test_pre_migration_backup_created_before_first_ddl(tmp_path):
    db_path = tmp_path / "app.db"
    backups = tmp_path / "backups"
    conn, _ = open_database(db_path, latest_known_schema_version=LATEST_KNOWN)
    service = SqliteBackupService(conn, backups)

    calls: list[tuple[str, str]] = []
    original = service.create_backup

    def tracking(backup_type: str, source_reason: str) -> str:
        calls.append((backup_type, source_reason))
        return original(backup_type, source_reason)

    service.create_backup = tracking  # type: ignore[method-assign]
    runner = MigrationRunner(conn, default_migrations(), backup_provider=service)

    assert runner.apply_pending()
    assert calls and calls[0][0] == "pre_migration"

    # The v0 → v1 backup predates every table, so no BackupRecord row can
    # exist yet; the backup file itself is the verifiable deliverable.
    record = conn.execute(
        "SELECT COUNT(*) AS n FROM backup_records"
    ).fetchone()
    assert record["n"] == 0
    backup_files = list(backups.glob("*.db"))
    assert len(backup_files) == 1
    assert backup_files[0].stat().st_size > 0

    # The pre-migration snapshot predates the schema, so it has no migrations.
    snapshot = sqlite3.connect(str(backup_files[0]))
    try:
        assert read_schema_version(snapshot) is None
    finally:
        snapshot.close()
    conn.close()


def test_post_schema_backup_is_recorded(tmp_path):
    db_path = tmp_path / "app.db"
    backups = tmp_path / "backups"
    conn, _ = open_database(db_path, latest_known_schema_version=LATEST_KNOWN)
    MigrationRunner(conn, default_migrations()).apply_pending()

    service = SqliteBackupService(conn, backups)
    backup_id = service.create_backup("manual", "post-schema sanity")

    record = conn.execute(
        "SELECT backup_type, managed_path, status, schema_version, database_hash, size_bytes"
        " FROM backup_records WHERE backup_id = ?",
        (backup_id,),
    ).fetchone()
    assert record["backup_type"] == "manual"
    assert record["status"] == "completed"
    assert record["schema_version"] == LATEST_KNOWN
    assert record["size_bytes"] > 0 and record["database_hash"]
    assert (backups / record["managed_path"]).is_file()
    conn.close()


def test_checksum_mismatch_detects_edited_history(tmp_path):
    db_path = tmp_path / "app.db"
    conn, _ = open_database(db_path, latest_known_schema_version=LATEST_KNOWN)
    MigrationRunner(conn, default_migrations()).apply_pending()
    with conn:
        conn.execute(
            "UPDATE schema_migrations SET checksum = 'tampered' WHERE schema_version = 1"
        )
    runner = MigrationRunner(conn, default_migrations())
    with pytest.raises(sqlite3.IntegrityError):
        runner._verify_checksum(default_migrations()[0])
    conn.close()
