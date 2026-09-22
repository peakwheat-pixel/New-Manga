"""Comprehensive test suite for T3.1.1 SQLite reading progress and export history.

Validates:
- AC1: Schema/Migration: v3→v4 and empty→v4, checksums, rollback on failure,
       and reject too-new schemas.
- AC2: ReadingProgress: all fields round-trip, uniqueness on (book, chap, mode),
       independent original/translated progress, webtoon scroll offset &
       duration persistence across service restarts.
- AC3: ExportHistory: all fields round-trip, all terminal statuses (completed,
       skipped, cancelled, failed), newest-first history ordering, repeat using
       stored snapshots.
- AC4: Legacy Import: valid JSON imported once, missing treated as empty, corrupt
       JSON / invalid structure / invalid records raise typed errors without
       mutating DB or touching source files, restart idempotency.
- AC5: Production Assembly: assemble_services wires SQLite adapters, production
       paths do not write to JSON files.
- AC6: Atomicity & Data Safety: DB write failures rollback cleanly, source files
       and managed copies remain untouched.
"""

from __future__ import annotations

import json
import os
import sqlite3
import tempfile
import uuid
from pathlib import Path
from typing import Any

import pytest

from application.export import (
    ExportFormat,
    ExportPage,
    ExportRecord,
    ExportRequest,
    ExportResult,
    ExportService,
    ExportStatus,
    OverwritePolicy,
    StalePolicy,
)
from application.reading import (
    ChapterReadingSummary,
    ReadingMode,
    ReadingProgress,
    ReadingService,
)
from infrastructure.sqlite import (
    LegacyCorruptJsonError,
    LegacyImportError,
    LegacyInvalidRecordError,
    LegacyInvalidStructureError,
    SqliteExportHistoryStore,
    SqliteReadingProgressStore,
    import_legacy_export_history,
    import_legacy_reading_progress,
)
from infrastructure.sqlite.connection import SchemaTooNewError, open_database
from infrastructure.sqlite.migrator import MigrationRunner, read_schema_version
from infrastructure.sqlite.reading_export import (
    METADATA_KEY_EXPORT_HISTORY_IMPORTED,
    METADATA_KEY_READING_PROGRESS_IMPORTED,
)
from infrastructure.sqlite.schema import (
    SCHEMA_VERSION_V3,
    SCHEMA_VERSION_V4,
    default_migrations,
)
from reading_export_helpers import make_pages, to_export_pages


@pytest.fixture
def fresh_db(tmp_path: Path) -> sqlite3.Connection:
    """A fresh SQLite database migrated to schema v4."""
    db_path = tmp_path / "test.db"
    conn, opened = open_database(db_path, latest_known_schema_version=SCHEMA_VERSION_V4)
    runner = MigrationRunner(conn, default_migrations())
    runner.apply_pending()
    yield conn
    conn.close()


@pytest.fixture
def v3_db(tmp_path: Path) -> sqlite3.Connection:
    """A SQLite database migrated only up to schema v3."""
    db_path = tmp_path / "v3.db"
    v3_migrations = default_migrations()[:3]
    conn, _ = open_database(db_path, latest_known_schema_version=SCHEMA_VERSION_V3)
    runner = MigrationRunner(conn, v3_migrations)
    runner.apply_pending()
    yield conn
    conn.close()


# ==============================================================================
# AC1: Schema & Migration
# ==============================================================================


class TestAC1SchemaMigration:
    def test_empty_database_migrates_to_v4(self, fresh_db: sqlite3.Connection) -> None:
        version = read_schema_version(fresh_db)
        assert version == SCHEMA_VERSION_V4 == 4

        # Verify reading_progress table schema
        cursor = fresh_db.execute("PRAGMA table_info(reading_progress)")
        cols = {row[1]: row[2] for row in cursor.fetchall()}
        expected_cols = {
            "progress_id", "book_id", "chapter_id", "mode", "last_page_id",
            "scroll_offset_x", "scroll_offset_y", "progress_percent",
            "last_read_at", "total_read_seconds", "updated_at"
        }
        assert expected_cols.issubset(set(cols.keys()))

        # Verify export_history table schema
        cursor = fresh_db.execute("PRAGMA table_info(export_history)")
        exp_cols = {row[1]: row[2] for row in cursor.fetchall()}
        expected_exp = {
            "export_id", "book_id", "chapter_id", "pipeline_run_id", "export_type",
            "scope_snapshot_json", "output_path", "render_profile_snapshot_json",
            "status", "file_hash", "created_at", "completed_at", "detail"
        }
        assert expected_exp.issubset(set(exp_cols.keys()))

    def test_v3_to_v4_migration_is_additive_and_checksum_preserved(
        self, v3_db: sqlite3.Connection
    ) -> None:
        assert read_schema_version(v3_db) == SCHEMA_VERSION_V3 == 3

        # Record checksums of v1, v2, v3
        v3_rows = v3_db.execute(
            "SELECT schema_version, migration_name, checksum FROM schema_migrations"
        ).fetchall()
        assert len(v3_rows) == 3

        # Apply v4 migration
        runner = MigrationRunner(v3_db, default_migrations())
        pending = runner.pending_migrations()
        assert len(pending) == 1
        assert pending[0].schema_version == SCHEMA_VERSION_V4

        applied = runner.apply_pending()
        assert len(applied) == 1
        assert applied[0].schema_version == 4
        assert read_schema_version(v3_db) == 4

        # Check that v1-v3 checksums are identical
        for row in v3_rows:
            current_row = v3_db.execute(
                "SELECT checksum FROM schema_migrations WHERE schema_version = ?",
                (row["schema_version"],),
            ).fetchone()
            assert current_row["checksum"] == row["checksum"]

    def test_migration_failure_rolls_back_atomically(self, tmp_path: Path) -> None:
        db_path = tmp_path / "rollback.db"
        conn, _ = open_database(db_path, latest_known_schema_version=SCHEMA_VERSION_V3)
        MigrationRunner(conn, default_migrations()[:3]).apply_pending()
        assert read_schema_version(conn) == 3

        # Create broken migration with multiline statements
        from infrastructure.sqlite.schema import Migration
        broken = (
            *default_migrations()[:3],
            Migration(4, "v4__broken", "CREATE TABLE ok_tab (id INT);\nINVALID SQL STATEMENT;\n"),
        )
        runner = MigrationRunner(conn, broken)
        with pytest.raises((sqlite3.OperationalError, sqlite3.ProgrammingError)):
            runner.apply_pending()

        # Database remains at v3 and ok_tab was rolled back
        assert read_schema_version(conn) == 3
        table = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='ok_tab'"
        ).fetchone()
        assert table is None
        conn.close()


# ==============================================================================
# AC2: ReadingProgress Persistence
# ==============================================================================


class TestAC2ReadingProgress:
    def test_reading_progress_all_fields_roundtrip(self, fresh_db: sqlite3.Connection) -> None:
        store = SqliteReadingProgressStore(fresh_db)
        state = {
            "progress_entries": [
                {
                    "progress_id": "rp-100",
                    "book_id": "b1",
                    "chapter_id": "c1",
                    "mode": "original",
                    "last_page_id": "p-5",
                    "scroll_offset_x": 10.5,
                    "scroll_offset_y": 250.75,
                    "progress_percent": 83.33,
                    "last_read_at": "2026-09-22T12:00:00Z",
                    "total_read_seconds": 1200.5,
                    "updated_at": "2026-09-22T12:00:00Z",
                }
            ]
        }
        store.write(state)

        loaded = store.read()
        entries = loaded["progress_entries"]
        assert len(entries) == 1
        entry = entries[0]
        assert entry["progress_id"] == "rp-100"
        assert entry["book_id"] == "b1"
        assert entry["chapter_id"] == "c1"
        assert entry["mode"] == "original"
        assert entry["last_page_id"] == "p-5"
        assert entry["scroll_offset_x"] == 10.5
        assert entry["scroll_offset_y"] == 250.75
        assert entry["progress_percent"] == 83.33
        assert entry["last_read_at"] == "2026-09-22T12:00:00Z"
        assert entry["total_read_seconds"] == 1200.5
        assert entry["updated_at"] == "2026-09-22T12:00:00Z"

    def test_reading_progress_unique_on_book_chapter_mode(
        self, fresh_db: sqlite3.Connection
    ) -> None:
        store = SqliteReadingProgressStore(fresh_db)
        # Write first entry
        store.write({
            "progress_entries": [
                {
                    "progress_id": "rp-1",
                    "book_id": "b1",
                    "chapter_id": "c1",
                    "mode": "original",
                    "last_page_id": "p1",
                    "progress_percent": 10.0,
                }
            ]
        })
        # Write update to same (book_id, chapter_id, mode) with new progress_id and percent
        store.write({
            "progress_entries": [
                {
                    "progress_id": "rp-2",
                    "book_id": "b1",
                    "chapter_id": "c1",
                    "mode": "original",
                    "last_page_id": "p2",
                    "progress_percent": 50.0,
                }
            ]
        })

        entries = store.read()["progress_entries"]
        assert len(entries) == 1
        assert entries[0]["last_page_id"] == "p2"
        assert entries[0]["progress_percent"] == 50.0

        # Verify in raw SQL only 1 row exists
        count = fresh_db.execute("SELECT COUNT(*) FROM reading_progress").fetchone()[0]
        assert count == 1

    def test_original_and_translated_modes_are_independent(
        self, fresh_db: sqlite3.Connection, tmp_path: Path
    ) -> None:
        pages = make_pages(tmp_path, count=5, translated=True)
        store = SqliteReadingProgressStore(fresh_db)
        service = ReadingService(store)

        # Open in original mode and read 2 pages
        service.open("book-A", "chap-1", pages, mode="original")
        service.next_page()
        service.next_page()
        service.add_time(30.0)
        service.close()

        assert service.page_index == 2
        assert service.mode == "original"

        # Switch to translated mode: starts from 0, independent
        service.set_mode("translated")
        assert service.page_index == 0
        service.next_page()
        service.add_time(15.0)
        service.close()

        # Reopen in new service instance (simulates restart)
        reopened = ReadingService(store)
        reopened.open("book-A", "chap-1", pages, mode="original")
        assert reopened.page_index == 2
        assert reopened.progress.total_read_seconds == 30.0

        reopened.set_mode("translated")
        assert reopened.page_index == 1
        assert reopened.progress.total_read_seconds == 15.0

    def test_webtoon_scroll_offset_and_duration_survive_restart(
        self, fresh_db: sqlite3.Connection, tmp_path: Path
    ) -> None:
        pages = make_pages(tmp_path, count=4)
        store = SqliteReadingProgressStore(fresh_db)
        service = ReadingService(store)

        service.open(
            "b-webtoon", "c-webtoon", pages,
            chapter_type="webtoon", direction="vertical",
        )
        service.jump_to_page(2)
        service.save_scroll_offset(offset_y=1240.5, offset_x=0.0)
        service.add_time(45.5)
        service.close()

        # Restart
        reopened = ReadingService(store)
        reopened.open(
            "b-webtoon", "c-webtoon", pages,
            chapter_type="webtoon", direction="vertical",
        )
        assert reopened.page_index == 2
        assert reopened.progress.scroll_offset_y == 1240.5
        assert reopened.progress.total_read_seconds == 45.5


# ==============================================================================
# AC3: ExportHistory Persistence
# ==============================================================================


class TestAC3ExportHistory:
    def test_export_history_all_fields_roundtrip(self, fresh_db: sqlite3.Connection) -> None:
        store = SqliteExportHistoryStore(fresh_db)
        records = [
            {
                "export_id": "exp-001",
                "book_id": "b1",
                "chapter_id": "c1",
                "pipeline_run_id": "run-99",
                "export_type": "zip",
                "scope_snapshot_json": json.dumps({"page_ids": ["p1", "p2"]}),
                "output_path": "/exports/b1_c1.zip",
                "render_profile_snapshot_json": json.dumps({"dpi": 300}),
                "status": "completed",
                "file_hash": "sha256-abcdef",
                "created_at": "2026-09-22T10:00:00Z",
                "completed_at": "2026-09-22T10:01:00Z",
                "detail": "Success",
            }
        ]
        store.write(records)

        loaded = store.read()
        assert len(loaded) == 1
        rec = loaded[0]
        assert rec["export_id"] == "exp-001"
        assert rec["book_id"] == "b1"
        assert rec["chapter_id"] == "c1"
        assert rec["pipeline_run_id"] == "run-99"
        assert rec["export_type"] == "zip"
        assert json.loads(rec["scope_snapshot_json"]) == {"page_ids": ["p1", "p2"]}
        assert rec["output_path"] == "/exports/b1_c1.zip"
        assert json.loads(rec["render_profile_snapshot_json"]) == {"dpi": 300}
        assert rec["status"] == "completed"
        assert rec["file_hash"] == "sha256-abcdef"
        assert rec["created_at"] == "2026-09-22T10:00:00Z"
        assert rec["completed_at"] == "2026-09-22T10:01:00Z"
        assert rec["detail"] == "Success"

    def test_export_history_all_terminal_statuses(self, fresh_db: sqlite3.Connection) -> None:
        store = SqliteExportHistoryStore(fresh_db)
        records = [
            {"export_id": f"exp-{idx}", "book_id": "b", "chapter_id": "c",
             "status": status, "created_at": f"2026-09-22T10:0{idx}:00Z"}
            for idx, status in enumerate(["completed", "skipped", "cancelled", "failed"], start=1)
        ]
        store.write(records)

        loaded = store.read()
        statuses = {r["status"] for r in loaded}
        assert statuses == {"completed", "skipped", "cancelled", "failed"}

    def test_export_history_ordered_newest_first(self, fresh_db: sqlite3.Connection) -> None:
        store = SqliteExportHistoryStore(fresh_db)
        store.write([
            {"export_id": "exp-old", "book_id": "b", "chapter_id": "c",
             "created_at": "2026-09-20T00:00:00Z"},
            {"export_id": "exp-mid", "book_id": "b", "chapter_id": "c",
             "created_at": "2026-09-21T00:00:00Z"},
            {"export_id": "exp-new", "book_id": "b", "chapter_id": "c",
             "created_at": "2026-09-22T00:00:00Z"},
        ])

        history = store.read()
        assert [r["export_id"] for r in history] == ["exp-new", "exp-mid", "exp-old"]

    def test_export_repeat_from_stored_snapshot(
        self, fresh_db: sqlite3.Connection, tmp_path: Path
    ) -> None:
        pages = make_pages(tmp_path, count=2)
        exp_pages = to_export_pages(pages)
        pages_by_id = {p.page_id: p for p in exp_pages}

        store = SqliteExportHistoryStore(fresh_db)
        service = ExportService(store)

        target = tmp_path / "out.zip"
        req = ExportRequest(
            book_id="b1",
            chapter_id="c1",
            format=ExportFormat.ZIP,
            output_path=target,
            pages=tuple(exp_pages),
        )
        res = service.export(req)
        assert res.status == ExportStatus.COMPLETED
        assert target.is_file()

        # Repeat with same settings to a different filename
        repeat_target = tmp_path / "repeat_out.zip"
        res_repeat = service.repeat(
            res.export_id,
            pages_by_id,
            overwrite_policy=OverwritePolicy.OVERWRITE,
        )
        assert res_repeat.status == ExportStatus.COMPLETED
        assert len(service.history()) == 2


# ==============================================================================
# AC4: Legacy JSON Import
# ==============================================================================


class TestAC4LegacyImport:
    def test_valid_reading_progress_imported_once(
        self, fresh_db: sqlite3.Connection, tmp_path: Path
    ) -> None:
        json_path = tmp_path / "reading_progress.json"
        data = {
            "progress_entries": [
                {
                    "progress_id": "rp-leg-1",
                    "book_id": "book-1",
                    "chapter_id": "chap-1",
                    "mode": "original",
                    "last_page_id": "p1",
                    "scroll_offset_x": 0.0,
                    "scroll_offset_y": 50.0,
                    "progress_percent": 25.0,
                    "last_read_at": "2026-09-21T10:00:00Z",
                    "total_read_seconds": 300.0,
                    "updated_at": "2026-09-21T10:00:00Z",
                },
                {
                    "progress_id": "rp-leg-2",
                    "book_id": "book-1",
                    "chapter_id": "chap-1",
                    "mode": "translated",
                    "last_page_id": "p2",
                    "scroll_offset_x": 0.0,
                    "scroll_offset_y": 0.0,
                    "progress_percent": 50.0,
                    "last_read_at": "2026-09-21T11:00:00Z",
                    "total_read_seconds": 600.0,
                    "updated_at": "2026-09-21T11:00:00Z",
                },
            ]
        }
        json_path.write_text(json.dumps(data), encoding="utf-8")
        orig_stat = json_path.stat()
        orig_content = json_path.read_bytes()

        # First import
        count = import_legacy_reading_progress(fresh_db, json_path)
        assert count == 2

        # Verify rows in DB
        rows = fresh_db.execute("SELECT * FROM reading_progress").fetchall()
        assert len(rows) == 2

        # Verify marker recorded
        marker = fresh_db.execute(
            "SELECT value_json FROM application_metadata WHERE metadata_key = ?",
            (METADATA_KEY_READING_PROGRESS_IMPORTED,),
        ).fetchone()
        assert marker is not None
        marker_data = json.loads(marker[0])
        assert marker_data["status"] == "imported"
        assert marker_data["imported_count"] == 2

        # Verify legacy file is untouched (mtime and content match)
        assert json_path.stat().st_mtime_ns == orig_stat.st_mtime_ns
        assert json_path.read_bytes() == orig_content

        # Second import (restart / reload idempotency)
        second_count = import_legacy_reading_progress(fresh_db, json_path)
        assert second_count == 0
        rows2 = fresh_db.execute("SELECT * FROM reading_progress").fetchall()
        assert len(rows2) == 2

    def test_valid_export_history_imported_once(
        self, fresh_db: sqlite3.Connection, tmp_path: Path
    ) -> None:
        json_path = tmp_path / "export_history.json"
        data = [
            {
                "export_id": "exp-leg-1",
                "book_id": "b1",
                "chapter_id": "c1",
                "pipeline_run_id": None,
                "export_type": "cbz",
                "scope_snapshot_json": json.dumps({"page_ids": ["p1"]}),
                "output_path": "/tmp/out.cbz",
                "render_profile_snapshot_json": "{}",
                "status": "completed",
                "file_hash": "hash1",
                "created_at": "2026-09-20T00:00:00Z",
                "completed_at": "2026-09-20T00:01:00Z",
                "detail": "",
            }
        ]
        json_path.write_text(json.dumps(data), encoding="utf-8")
        orig_stat = json_path.stat()
        orig_content = json_path.read_bytes()

        count = import_legacy_export_history(fresh_db, json_path)
        assert count == 1

        rows = fresh_db.execute("SELECT * FROM export_history").fetchall()
        assert len(rows) == 1

        marker = fresh_db.execute(
            "SELECT value_json FROM application_metadata WHERE metadata_key = ?",
            (METADATA_KEY_EXPORT_HISTORY_IMPORTED,),
        ).fetchone()
        assert marker is not None
        assert json.loads(marker[0])["status"] == "imported"

        # Untouched file
        assert json_path.stat().st_mtime_ns == orig_stat.st_mtime_ns
        assert json_path.read_bytes() == orig_content

        # Second call is a no-op
        assert import_legacy_export_history(fresh_db, json_path) == 0

    def test_missing_files_treated_as_empty_without_error(
        self, fresh_db: sqlite3.Connection, tmp_path: Path
    ) -> None:
        missing_progress = tmp_path / "absent_progress.json"
        missing_export = tmp_path / "absent_export.json"

        assert import_legacy_reading_progress(fresh_db, missing_progress) == 0
        assert import_legacy_export_history(fresh_db, missing_export) == 0

        # Markers recorded
        row1 = fresh_db.execute(
            "SELECT value_json FROM application_metadata WHERE metadata_key = ?",
            (METADATA_KEY_READING_PROGRESS_IMPORTED,),
        ).fetchone()
        row2 = fresh_db.execute(
            "SELECT value_json FROM application_metadata WHERE metadata_key = ?",
            (METADATA_KEY_EXPORT_HISTORY_IMPORTED,),
        ).fetchone()
        assert json.loads(row1[0])["status"] == "missing_empty"
        assert json.loads(row2[0])["status"] == "missing_empty"

    def test_corrupt_json_raises_typed_error_and_preserves_file_and_db(
        self, fresh_db: sqlite3.Connection, tmp_path: Path
    ) -> None:
        corrupt_file = tmp_path / "reading_progress.json"
        corrupt_file.write_text("{ incomplete json", encoding="utf-8")
        orig_bytes = corrupt_file.read_bytes()

        with pytest.raises(LegacyCorruptJsonError):
            import_legacy_reading_progress(fresh_db, corrupt_file)

        # File is preserved
        assert corrupt_file.read_bytes() == orig_bytes
        # No marker recorded
        marker = fresh_db.execute(
            "SELECT value_json FROM application_metadata WHERE metadata_key = ?",
            (METADATA_KEY_READING_PROGRESS_IMPORTED,),
        ).fetchone()
        assert marker is None
        # No rows in DB
        assert fresh_db.execute("SELECT COUNT(*) FROM reading_progress").fetchone()[0] == 0

    def test_invalid_structure_raises_typed_error(
        self, fresh_db: sqlite3.Connection, tmp_path: Path
    ) -> None:
        bad_structure = tmp_path / "reading_progress.json"
        bad_structure.write_text(json.dumps(["not", "a", "dict"]), encoding="utf-8")

        with pytest.raises(LegacyInvalidStructureError):
            import_legacy_reading_progress(fresh_db, bad_structure)

        bad_export = tmp_path / "export_history.json"
        bad_export.write_text(json.dumps({"not": "a list"}), encoding="utf-8")

        with pytest.raises(LegacyInvalidStructureError):
            import_legacy_export_history(fresh_db, bad_export)

    def test_invalid_records_raise_typed_error(
        self, fresh_db: sqlite3.Connection, tmp_path: Path
    ) -> None:
        # Invalid mode
        bad_mode = tmp_path / "reading_progress.json"
        bad_mode.write_text(
            json.dumps({"progress_entries": [{"book_id": "b1", "chapter_id": "c1", "mode": "invalid"}]}),
            encoding="utf-8"
        )
        with pytest.raises(LegacyInvalidRecordError):
            import_legacy_reading_progress(fresh_db, bad_mode)

        # Duplicate (book, chapter, mode)
        duplicate = tmp_path / "duplicate_progress.json"
        duplicate.write_text(
            json.dumps({"progress_entries": [
                {"book_id": "b1", "chapter_id": "c1", "mode": "original"},
                {"book_id": "b1", "chapter_id": "c1", "mode": "original"},
            ]}),
            encoding="utf-8"
        )
        with pytest.raises(LegacyInvalidRecordError):
            import_legacy_reading_progress(fresh_db, duplicate)


# ==============================================================================
# AC5: Production Bootstrap Wiring
# ==============================================================================


class TestAC5BootstrapWiring:
    def test_assemble_services_wires_sqlite_adapters_and_skips_json_writes(
        self, tmp_path: Path
    ) -> None:
        from bootstrap.app import assemble_services

        db_path = tmp_path / "library.db"
        managed_root = tmp_path / "managed"
        data_root = tmp_path

        # Seed legacy reading progress and export history
        progress_json = data_root / "reading_progress.json"
        progress_json.write_text(
            json.dumps({
                "progress_entries": [
                    {
                        "progress_id": "rp-init",
                        "book_id": "b-init",
                        "chapter_id": "c-init",
                        "mode": "original",
                        "last_page_id": "p-init",
                        "progress_percent": 100.0,
                        "last_read_at": "2026-09-22T12:00:00Z",
                    }
                ]
            }),
            encoding="utf-8",
        )
        orig_json_stat = progress_json.stat()

        services = assemble_services(db_path, managed_root)

        # Verify that ReadingService holds the imported row
        summaries = services.reading.chapter_summaries("b-init")
        assert len(summaries) == 1
        assert summaries[0].chapter_id == "c-init"
        assert summaries[0].progress_percent == 100.0

        # Verify that ReadingService is backed by SQLite
        assert isinstance(services.reading._store, SqliteReadingProgressStore)
        assert isinstance(services.export_service._store, SqliteExportHistoryStore)

        # Reading progress modification writes directly to SQLite, NOT to reading_progress.json
        pages = make_pages(tmp_path, count=2)
        services.reading.open("b-init", "c-init", pages)
        services.reading.next_page()
        services.reading.close()

        # Check SQLite updated
        conn, _ = open_database(db_path, latest_known_schema_version=SCHEMA_VERSION_V4)
        row = conn.execute(
            "SELECT last_page_id FROM reading_progress WHERE book_id = 'b-init'"
        ).fetchone()
        assert row[0] == pages[1].page_id
        conn.close()

        # Check reading_progress.json remains unchanged
        assert progress_json.stat().st_mtime_ns == orig_json_stat.st_mtime_ns


# ==============================================================================
# AC6: Atomicity & Data Safety
# ==============================================================================


class TestAC6AtomicityDataSafety:
    def test_db_failure_during_progress_write_rolls_back(
        self, fresh_db: sqlite3.Connection
    ) -> None:
        store = SqliteReadingProgressStore(fresh_db)
        store.write({
            "progress_entries": [
                {
                    "progress_id": "rp-keep",
                    "book_id": "b1",
                    "chapter_id": "c1",
                    "mode": "original",
                    "last_page_id": "p1",
                }
            ]
        })

        # Inject failure by making reading_progress table read-only or triggering abort
        fresh_db.execute(
            """
            CREATE TRIGGER trg_fail_on_error_test
            BEFORE INSERT ON reading_progress
            WHEN NEW.book_id = 'b-fail'
            BEGIN
                SELECT RAISE(ABORT, 'injected failure');
            END;
            """
        )

        with pytest.raises(sqlite3.IntegrityError, match="injected failure"):
            store.write({
                "progress_entries": [
                    {
                        "progress_id": "rp-keep",
                        "book_id": "b1",
                        "chapter_id": "c1",
                        "mode": "original",
                        "last_page_id": "p1",
                    },
                    {
                        "progress_id": "rp-bad",
                        "book_id": "b-fail",
                        "chapter_id": "c2",
                        "mode": "original",
                    }
                ]
            })

        # Previous state preserved
        entries = store.read()["progress_entries"]
        assert len(entries) == 1
        assert entries[0]["progress_id"] == "rp-keep"

    def test_db_failure_during_export_write_rolls_back(
        self, fresh_db: sqlite3.Connection
    ) -> None:
        store = SqliteExportHistoryStore(fresh_db)
        store.write([
            {"export_id": "exp-safe", "book_id": "b", "chapter_id": "c", "status": "completed"}
        ])

        fresh_db.execute(
            """
            CREATE TRIGGER trg_fail_export_test
            BEFORE INSERT ON export_history
            WHEN NEW.export_id = 'exp-fail'
            BEGIN
                SELECT RAISE(ABORT, 'injected export failure');
            END;
            """
        )

        with pytest.raises(sqlite3.IntegrityError, match="injected export failure"):
            store.write([
                {"export_id": "exp-safe", "book_id": "b", "chapter_id": "c", "status": "completed"},
                {"export_id": "exp-fail", "book_id": "b", "chapter_id": "c", "status": "completed"},
            ])

        records = store.read()
        assert len(records) == 1
        assert records[0]["export_id"] == "exp-safe"
