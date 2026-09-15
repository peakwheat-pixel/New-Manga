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


def test_all_migrations_apply_with_checksum_and_metadata(db_conn):
    version = read_schema_version(db_conn)
    assert version == LATEST_KNOWN == 2

    for migration in default_migrations():
        row = db_conn.execute(
            "SELECT migration_name, checksum FROM schema_migrations WHERE schema_version = ?",
            (migration.schema_version,),
        ).fetchone()
        assert row["migration_name"] == migration.migration_name
        assert row["checksum"] == migration.checksum, (
            f"v1 checksum drift detected at version {migration.schema_version}"
            if migration.schema_version == 1
            else "v2 checksum mismatch"
        )

    metadata = db_conn.execute(
        "SELECT value_json FROM application_metadata WHERE metadata_key = 'schema_version'"
    ).fetchone()
    assert metadata["value_json"] == str(LATEST_KNOWN)


def test_v1_schema_is_unchanged():
    """TASK-028 §2.2: the v1 migration content is frozen — no v2 content
    may leak into it and no post-hoc ALTERs may appear there."""
    v1 = default_migrations()[0]
    assert v1.migration_name == "v1__storage_base"
    assert v1.schema_version == 1
    assert "CREATE TABLE media_artifacts" in v1.sql
    assert "CREATE TABLE regions" not in v1.sql
    assert "CREATE TABLE tags" not in v1.sql
    assert "ALTER TABLE" not in v1.sql


def test_reopening_is_idempotent(tmp_path):
    db_path = tmp_path / "x.db"
    conn, opened = open_database(db_path, latest_known_schema_version=LATEST_KNOWN)
    assert opened.state.value == "empty"
    runner = MigrationRunner(conn, default_migrations())
    applied = runner.apply_pending()
    assert [record.schema_version for record in applied] == [1, 2]
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
            " VALUES (3, 'future', '2026-01-01T00:00:00Z', 'nope')"
        )
        conn.execute(
            "UPDATE application_metadata SET value_json = '3'"
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

    # Full pending batch: one pre-migration backup fires per pending
    # migration (v1 and v2). The v0→v1 guard predates backup_records, so
    # exactly one row exists — for the v1→v2 backup, recorded with its
    # storage-relative managed path.
    records = conn.execute(
        "SELECT backup_type, managed_path, schema_version FROM backup_records"
    ).fetchall()
    assert len(records) == 1
    assert records[0]["backup_type"] == "pre_migration"
    assert records[0]["schema_version"] == 1  # snapshot taken at v1 state
    assert records[0]["managed_path"].startswith("backups/")
    assert (backups / records[0]["managed_path"].split("/", 1)[1]).is_file()

    backup_files = list(backups.glob("*.db"))
    assert len(backup_files) == 2  # v0→v1 guard (unrecorded) + v1→v2 (recorded)
    # The unrecorded file is the v0→v1 snapshot: it predates the schema.
    recorded_file = backups / records[0]["managed_path"].split("/", 1)[1]
    unrecorded_files = [f for f in backup_files if f.resolve() != recorded_file.resolve()]
    assert len(unrecorded_files) == 1
    first_snapshot = sqlite3.connect(str(unrecorded_files[0]))
    try:
        assert read_schema_version(first_snapshot) is None
    finally:
        first_snapshot.close()
    # The recorded v1→v2 snapshot sits at schema v1.
    recorded_snapshot = sqlite3.connect(
        str(backups / records[0]["managed_path"].split("/", 1)[1])
    )
    try:
        assert read_schema_version(recorded_snapshot) == 1
    finally:
        recorded_snapshot.close()
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
    # R-105: managed_path is the storage-relative managed path.
    assert record["managed_path"] == f"backups/{backup_id}.db"
    assert (backups / record["managed_path"].split("/", 1)[1]).is_file()
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


def test_v2_introduces_no_out_of_scope_tables(db_conn):
    """TASK-028 §6 boundary check: Pipeline/Candidate/TM/Constraint tables
    belong to later slices and must not silently appear in the schema."""
    tables = {
        row[0]
        for row in conn_tables(db_conn)
    }
    forbidden = {
        "pipeline_runs", "pipeline_run_targets", "pipeline_tasks", "step_runs",
        "step_run_input_refs", "step_run_output_refs", "step_result_candidates",
        "translation_memory", "translation_constraints", "constraint_revisions",
        "provider_profiles", "provider_bindings", "network_profiles",
    }
    assert not (tables & forbidden)


def conn_tables(conn):
    return conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
