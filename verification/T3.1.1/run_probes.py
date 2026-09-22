"""Independent verification probes for T3.1.1 SQLite convergence.

Runs standalone verification probes for:
1. Legacy JSON import & idempotency & file preservation
2. Error diagnosis on corrupt/invalid legacy input
3. Production bootstrap assembly & SQLite write verification
4. Transaction atomicity & failure rollback
5. Clean shutdown
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import sqlite3
import sys
import tempfile
from pathlib import Path

# Ensure src is on path
REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from bootstrap.app import _shutdown_services, assemble_services
from infrastructure.sqlite import (
    LegacyCorruptJsonError,
    LegacyInvalidRecordError,
    LegacyInvalidStructureError,
    SqliteExportHistoryStore,
    SqliteReadingProgressStore,
    import_legacy_export_history,
    import_legacy_reading_progress,
)
from infrastructure.sqlite.connection import open_database
from infrastructure.sqlite.migrator import MigrationRunner, read_schema_version
from infrastructure.sqlite.schema import SCHEMA_VERSION_V4, default_migrations


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def probe_1_legacy_import(work_dir: Path) -> None:
    print("--- [PROBE 1] Legacy JSON Import, Idempotency & File Preservation ---")
    db_path = work_dir / "probe1.db"
    conn, _ = open_database(db_path, latest_known_schema_version=SCHEMA_VERSION_V4)
    MigrationRunner(conn, default_migrations()).apply_pending()

    # Create sample legacy files
    prog_file = work_dir / "reading_progress.json"
    exp_file = work_dir / "export_history.json"

    prog_data = {
        "progress_entries": [
            {
                "progress_id": "rp-probe-1",
                "book_id": "book-A",
                "chapter_id": "chap-1",
                "mode": "original",
                "last_page_id": "p-10",
                "scroll_offset_x": 0.0,
                "scroll_offset_y": 150.0,
                "progress_percent": 45.0,
                "last_read_at": "2026-09-22T08:00:00Z",
                "total_read_seconds": 900.0,
                "updated_at": "2026-09-22T08:00:00Z",
            }
        ]
    }
    exp_data = [
        {
            "export_id": "exp-probe-1",
            "book_id": "book-A",
            "chapter_id": "chap-1",
            "pipeline_run_id": None,
            "export_type": "cbz",
            "scope_snapshot_json": json.dumps({"pages": ["p-10"]}),
            "output_path": "/tmp/bookA.cbz",
            "render_profile_snapshot_json": "{}",
            "status": "completed",
            "file_hash": "hash-abc",
            "created_at": "2026-09-22T08:05:00Z",
            "completed_at": "2026-09-22T08:06:00Z",
            "detail": "ok",
        }
    ]

    prog_file.write_text(json.dumps(prog_data), encoding="utf-8")
    exp_file.write_text(json.dumps(exp_data), encoding="utf-8")

    prog_h_before, prog_m_before = file_hash(prog_file), prog_file.stat().st_mtime_ns
    exp_h_before, exp_m_before = file_hash(exp_file), exp_file.stat().st_mtime_ns

    # First import
    prog_imported = import_legacy_reading_progress(conn, prog_file)
    exp_imported = import_legacy_export_history(conn, exp_file)
    assert prog_imported == 1, f"Expected 1 progress imported, got {prog_imported}"
    assert exp_imported == 1, f"Expected 1 export imported, got {exp_imported}"

    # Verify rows in SQLite
    row = conn.execute("SELECT progress_id, book_id, chapter_id FROM reading_progress").fetchone()
    assert row["progress_id"] == "rp-probe-1"
    row_e = conn.execute("SELECT export_id, book_id, status FROM export_history").fetchone()
    assert row_e["export_id"] == "exp-probe-1"

    # Verify file preservation
    assert file_hash(prog_file) == prog_h_before
    assert prog_file.stat().st_mtime_ns == prog_m_before
    assert file_hash(exp_file) == exp_h_before
    assert exp_file.stat().st_mtime_ns == exp_m_before

    # Second import (restart / reload idempotency)
    assert import_legacy_reading_progress(conn, prog_file) == 0
    assert import_legacy_export_history(conn, exp_file) == 0
    assert conn.execute("SELECT COUNT(*) FROM reading_progress").fetchone()[0] == 1
    assert conn.execute("SELECT COUNT(*) FROM export_history").fetchone()[0] == 1

    conn.close()
    print("PASS: Probe 1 completed successfully.")


def probe_2_error_diagnosis(work_dir: Path) -> None:
    print("--- [PROBE 2] Error Diagnosis on Corrupt / Invalid Input ---")
    db_path = work_dir / "probe2.db"
    conn, _ = open_database(db_path, latest_known_schema_version=SCHEMA_VERSION_V4)
    MigrationRunner(conn, default_migrations()).apply_pending()

    # Corrupt JSON
    corrupt = work_dir / "corrupt.json"
    corrupt.write_text("{ unclosed json", encoding="utf-8")
    try:
        import_legacy_reading_progress(conn, corrupt)
        raise AssertionError("Failed to raise on corrupt JSON")
    except LegacyCorruptJsonError:
        pass

    # Invalid Structure
    bad_struct = work_dir / "bad_struct.json"
    bad_struct.write_text(json.dumps(["not", "dict"]), encoding="utf-8")
    try:
        import_legacy_reading_progress(conn, bad_struct)
        raise AssertionError("Failed to raise on invalid structure")
    except LegacyInvalidStructureError:
        pass

    # Invalid Record (missing book_id)
    bad_rec = work_dir / "bad_rec.json"
    bad_rec.write_text(json.dumps({"progress_entries": [{"chapter_id": "c"}]}), encoding="utf-8")
    try:
        import_legacy_reading_progress(conn, bad_rec)
        raise AssertionError("Failed to raise on invalid record")
    except LegacyInvalidRecordError:
        pass

    # Missing file handled cleanly
    assert import_legacy_reading_progress(conn, work_dir / "non_existent.json") == 0

    # Ensure DB has 0 rows
    assert conn.execute("SELECT COUNT(*) FROM reading_progress").fetchone()[0] == 0
    conn.close()
    print("PASS: Probe 2 completed successfully.")


def probe_3_production_assembly(work_dir: Path) -> None:
    print("--- [PROBE 3] Production Bootstrap Assembly & SQLite Writes ---")
    db_path = work_dir / "library.db"
    managed_root = work_dir / "managed"
    data_root = work_dir

    services = assemble_services(db_path, managed_root)
    assert isinstance(services.reading._store, SqliteReadingProgressStore)
    assert isinstance(services.export_service._store, SqliteExportHistoryStore)

    # Perform a reading progress update
    store = services.reading._store
    store.write({
        "progress_entries": [
            {
                "progress_id": "rp-live-1",
                "book_id": "live-book",
                "chapter_id": "live-chap",
                "mode": "original",
                "last_page_id": "p-1",
                "progress_percent": 50.0,
                "last_read_at": "2026-09-22T12:00:00Z",
                "total_read_seconds": 120.0,
            }
        ]
    })

    # Verify directly in SQLite
    conn, _ = open_database(db_path, latest_known_schema_version=SCHEMA_VERSION_V4)
    row = conn.execute("SELECT * FROM reading_progress WHERE progress_id = 'rp-live-1'").fetchone()
    assert row is not None
    assert row["book_id"] == "live-book"
    assert row["progress_percent"] == 50.0
    conn.close()

    # Verify no JSON files created
    assert not (data_root / "reading_progress.json").exists()
    assert not (data_root / "export_history.json").exists()

    _shutdown_services(services)
    print("PASS: Probe 3 completed successfully.")


def probe_4_atomicity_and_rollback(work_dir: Path) -> None:
    print("--- [PROBE 4] Transaction Atomicity & Failure Rollback ---")
    db_path = work_dir / "probe4.db"
    conn, _ = open_database(db_path, latest_known_schema_version=SCHEMA_VERSION_V4)
    MigrationRunner(conn, default_migrations()).apply_pending()

    store = SqliteReadingProgressStore(conn)
    store.write({
        "progress_entries": [
            {"progress_id": "rp-orig", "book_id": "b1", "chapter_id": "c1", "mode": "original"}
        ]
    })

    # Injected trigger abort
    conn.execute(
        """
        CREATE TRIGGER trg_test_abort
        BEFORE INSERT ON reading_progress
        WHEN NEW.book_id = 'b-fail'
        BEGIN
            SELECT RAISE(ABORT, 'intentional abort');
        END;
        """
    )

    try:
        store.write({
            "progress_entries": [
                {"progress_id": "rp-orig", "book_id": "b1", "chapter_id": "c1", "mode": "original"},
                {"progress_id": "rp-new", "book_id": "b-fail", "chapter_id": "c2", "mode": "original"},
            ]
        })
        raise AssertionError("Write should have aborted")
    except sqlite3.IntegrityError:
        pass

    # Assert existing row remains intact and no partial row added
    rows = store.read()["progress_entries"]
    assert len(rows) == 1
    assert rows[0]["progress_id"] == "rp-orig"

    conn.close()
    print("PASS: Probe 4 completed successfully.")


def main() -> int:
    temp_dir = Path(tempfile.mkdtemp(prefix="t3_1_1_probe_"))
    try:
        probe_1_legacy_import(temp_dir / "p1")
        probe_2_error_diagnosis(temp_dir / "p2")
        probe_3_production_assembly(temp_dir / "p3")
        probe_4_atomicity_and_rollback(temp_dir / "p4")
        print("\nALL T3.1.1 PROBES PASSED.")
        return 0
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
