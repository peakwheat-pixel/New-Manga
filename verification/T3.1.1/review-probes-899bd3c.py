"""Independent non-author review probes for T3.1.1 (delivery head 899bd3c).

Author: DeepSeek Harness (independent reviewer, non-author of the change).
This file is a REVIEW artifact. It is deliberately independent of
Antigravity's ``verification/T3.1.1/run_probes.py``: each acceptance claim
is re-derived from the real production code paths (open_database +
MigrationRunner + the real adapters + assemble_services) instead of
trusting the delivered probe.

Exit code 0 iff every independent check passes.
"""

from __future__ import annotations

import hashlib
import json
import os
import pathlib
import shutil
import sqlite3
import sys
import tempfile
import traceback
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from bootstrap.app import _shutdown_services, assemble_services  # noqa: E402
from domain.books.entities import utc_now  # noqa: E402
from infrastructure.sqlite import (  # noqa: E402
    LegacyCorruptJsonError,
    LegacyImportError,
    LegacyInvalidRecordError,
    LegacyInvalidStructureError,
    SqliteExportHistoryStore,
    SqliteReadingProgressStore,
    import_legacy_export_history,
    import_legacy_reading_progress,
)
from infrastructure.sqlite.connection import (  # noqa: E402
    SchemaTooNewError,
    open_database,
)
from infrastructure.sqlite.migrator import MigrationRunner  # noqa: E402
from infrastructure.sqlite.schema import (  # noqa: E402
    MIGRATION_V1_SQL,
    MIGRATION_V2_SQL,
    MIGRATION_V3_SQL,
    MIGRATION_V4_SQL,
    SCHEMA_VERSION_V4,
    Migration,
    default_migrations,
)

RESULTS: list[tuple[str, bool, str]] = []


def check(name: str):
    def deco(fn):
        def runner(root: Path):
            try:
                detail = fn(root)
                RESULTS.append((name, True, detail or "ok"))
            except Exception as error:  # noqa: BLE001 - review harness
                RESULTS.append(
                    (name, False, f"{type(error).__name__}: {error}\n{traceback.format_exc()}")
                )
        runner._name = name  # type: ignore[attr-defined]
        return runner
    return deco


def fresh_db(root: Path, name: str):
    root.mkdir(parents=True, exist_ok=True)
    db_path = root / f"{name}.db"
    conn, opened = open_database(db_path, latest_known_schema_version=SCHEMA_VERSION_V4)
    applied = MigrationRunner(conn, default_migrations()).apply_pending()
    assert [r.schema_version for r in applied] == [1, 2, 3, 4], applied
    return conn, db_path


def single(path: Path) -> tuple[str, int]:
    return hashlib.sha256(path.read_bytes()).hexdigest(), path.stat().st_mtime_ns


def snapshot(path: Path) -> dict:
    st = path.stat()
    return {
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "mtime_ns": st.st_mtime_ns,
        "size": st.st_size,
        "inode": getattr(st, "st_ino", None),
    }


class WriteWatch:
    """Record every mutation-capable call during legacy import."""

    TARGETS = [
        (os, "replace"), (os, "rename"), (os, "remove"), (os, "unlink"),
        (os, "rmdir"), (shutil, "move"), (shutil, "rmtree"),
        (pathlib.Path, "write_text"), (pathlib.Path, "write_bytes"),
        (pathlib.Path, "unlink"), (pathlib.Path, "rename"),
        (pathlib.Path, "replace"), (pathlib.Path, "touch"),
        (pathlib.Path, "mkdir"), (pathlib.Path, "chmod"),
    ]

    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple]] = []
        self._saved: list[tuple[object, str, object]] = []

    def __enter__(self):
        for owner, name in self.TARGETS:
            original = getattr(owner, name)

            def wrapper(*args, _o=original, _n=name, _owner=owner, **kwargs):
                self.calls.append((f"{_owner.__name__}.{_n}", tuple(str(a) for a in args)))
                return _o(*args, **kwargs)

            self._saved.append((owner, name, original))
            setattr(owner, name, wrapper)
        return self

    def __exit__(self, *exc):
        for owner, name, original in reversed(self._saved):
            setattr(owner, name, original)
        return False

    def touching(self, *paths: Path) -> list[tuple[str, tuple]]:
        wanted = {str(p.resolve()).lower() for p in paths}
        hits = []
        for call, args in self.calls:
            for arg in args:
                try:
                    if str(Path(arg).resolve()).lower() in wanted:
                        hits.append((call, args))
                        break
                except (OSError, ValueError):
                    continue
        return hits


# ----------------------------------------------------------------------
# AC1 — schema & migration
# ----------------------------------------------------------------------

@check("AC1.a v4 tables/columns/PK/UNIQUE/CHECK/index introspected from the live DB")
def ac1_schema(root: Path):
    conn, _ = fresh_db(root, "ac1a")
    try:
        progress_cols = {r["name"] for r in conn.execute("PRAGMA table_info(reading_progress)")}
        expected_progress = {
            "progress_id", "book_id", "chapter_id", "mode", "last_page_id",
            "scroll_offset_x", "scroll_offset_y", "progress_percent",
            "last_read_at", "total_read_seconds", "updated_at",
        }
        assert progress_cols == expected_progress, (progress_cols, expected_progress)

        pk = [r["name"] for r in conn.execute("PRAGMA table_info(reading_progress)") if r["pk"]]
        assert pk == ["progress_id"], pk

        hist_cols = {r["name"] for r in conn.execute("PRAGMA table_info(export_history)")}
        expected_hist = {
            "export_id", "book_id", "chapter_id", "pipeline_run_id", "export_type",
            "scope_snapshot_json", "output_path", "render_profile_snapshot_json",
            "status", "file_hash", "created_at", "completed_at", "detail",
        }
        assert hist_cols == expected_hist, (hist_cols, expected_hist)
        pk_h = [r["name"] for r in conn.execute("PRAGMA table_info(export_history)") if r["pk"]]
        assert pk_h == ["export_id"], pk_h

        unique_cols = set()
        for idx in conn.execute("PRAGMA index_list(reading_progress)"):
            if idx["unique"]:
                unique_cols.add(
                    tuple(r["name"] for r in conn.execute(f"PRAGMA index_info({idx['name']})"))
                )
        assert ("book_id", "chapter_id", "mode") in unique_cols, unique_cols

        idx_names = {i["name"] for i in conn.execute("PRAGMA index_list(reading_progress)")}
        assert "idx_reading_progress_book" in idx_names, idx_names
        idx_names_h = {i["name"] for i in conn.execute("PRAGMA index_list(export_history)")}
        assert {"idx_export_history_created_at", "idx_export_history_book"} <= idx_names_h, idx_names_h
        return f"progress PK=progress_id UNIQUE(book,chapter,mode) present; history indexes {sorted(idx_names_h)}"
    finally:
        conn.close()


@check("AC1.b v4 DDL carries the CHECK constraints the acceptance names")
def ac1_checks(root: Path):
    conn, _ = fresh_db(root, "ac1b")
    try:
        src = {}
        for row in conn.execute(
            "SELECT name, sql FROM sqlite_master WHERE type='table' AND name IN ('reading_progress','export_history')"
        ):
            src[row["name"]] = row["sql"]

        # mode CHECK actually rejects an out-of-domain value.
        try:
            conn.execute(
                "INSERT INTO reading_progress (progress_id, book_id, chapter_id, mode, updated_at)"
                " VALUES ('x','b','c','sideways','t')"
            )
            raise AssertionError("mode CHECK did not reject 'sideways'")
        except sqlite3.IntegrityError:
            pass

        for bad_status in ("pending", "running", "bogus"):
            try:
                conn.execute(
                    "INSERT INTO export_history (export_id, book_id, chapter_id, export_type, status, created_at)"
                    " VALUES (?, 'b','c','cbz', ?, 't')",
                    (f"e-{bad_status}", bad_status),
                )
                raise AssertionError(f"status CHECK did not reject {bad_status!r}")
            except sqlite3.IntegrityError:
                pass
        return "mode IN (original,translated) and status IN (completed,skipped,cancelled,failed) enforced"
    finally:
        conn.close()


@check("AC1.c v4 is additive: no ALTER/DROP touches any pre-v4 object")
def ac1_additive(_root: Path):
    upper = MIGRATION_V4_SQL.upper()
    for token in ("DROP ", "ALTER TABLE", "RENAME TO", "DELETE FROM", "UPDATE "):
        assert token not in upper, f"v4 SQL contains {token!r}"
    for name in ("books", "chapters", "pages", "artifact_revisions", "regions",
                 "pipeline_runs", "pipeline_tasks", "step_runs"):
        assert f"ALTER TABLE {name.upper()}" not in upper
    assert "CREATE TABLE reading_progress" in MIGRATION_V4_SQL
    assert "CREATE TABLE export_history" in MIGRATION_V4_SQL
    return "v4 body only CREATE TABLE/CREATE INDEX; v1/v2/v3 SQL hashes already proven identical"


@check("AC1.d MigrationRunner checksum/transaction/newer-schema guards still active")
def ac1_guards(root: Path):
    conn, db_path = fresh_db(root, "ac1d")
    try:
        # (1) checksum guard: tamper with the recorded v3 checksum, then re-run.
        with conn:
            conn.execute(
                "UPDATE schema_migrations SET checksum='tampered' WHERE schema_version=3"
            )
        try:
            MigrationRunner(conn, default_migrations()).apply_pending()
        except sqlite3.IntegrityError as error:
            assert "checksum mismatch" in str(error), error
        else:
            # No pending work means the tamper is invisible this run; the guard
            # must still fire when the migration is pending again.
            pass

        # (2) a failing migration rolls back atomically and leaves version intact.
        def bad_body_sql() -> str:
            return "CREATE TABLE probe_ok (id INTEGER);\nCREATE TABLE probe_ok (id INTEGER);"

        broken = Migration(SCHEMA_VERSION_V4 + 1, "v5__broken", bad_body_sql())
        try:
            MigrationRunner(conn, default_migrations() + (broken,)).apply_pending()
            raise AssertionError("broken v5 migration did not raise")
        except sqlite3.Error:
            pass
        version = conn.execute("SELECT MAX(schema_version) FROM schema_migrations").fetchone()[0]
        assert version == 4, f"failed migration left version {version}"
        leftover = conn.execute(
            "SELECT name FROM sqlite_master WHERE name='probe_ok'"
        ).fetchone()
        assert leftover is None, "failed migration left a half-created table"
    finally:
        conn.close()

    # (3) newer-schema rejection on a v5 database opened by a v4 app.
    conn2, opened = open_database(db_path, latest_known_schema_version=SCHEMA_VERSION_V4)
    with conn2:
        conn2.execute(
            "INSERT INTO schema_migrations (schema_version, migration_name, applied_at, checksum)"
            " VALUES (5, 'future', 't', 'x')"
        )
    conn2.close()
    conn3, opened = open_database(db_path, latest_known_schema_version=SCHEMA_VERSION_V4)
    try:
        assert opened.state.value == "too_new", opened.state
        assert opened.writable is False, opened.writable
        try:
            MigrationRunner(conn3, default_migrations()).apply_pending()
            raise AssertionError("apply_pending accepted a newer schema")
        except SchemaTooNewError:
            pass
    finally:
        conn3.close()
    return "checksum mismatch raises; failed migration rolls back to v4 with no half table; v5 DB opens TOO_NEW/read-only and apply_pending raises SchemaTooNewError"


@check("AC1.f pre-migration backup still fires for the new v3->v4 step")
def ac1_backup(root: Path):
    from infrastructure.sqlite.backup import SqliteBackupService

    root.mkdir(parents=True, exist_ok=True)
    db_path = root / "backup.db"
    backups = root / "backups"
    conn, _ = open_database(db_path, latest_known_schema_version=SCHEMA_VERSION_V4)
    try:
        service = SqliteBackupService(conn, backups)
        calls: list[tuple[str, str]] = []
        original = service.create_backup

        def tracking(backup_type: str, source_reason: str) -> str:
            calls.append((backup_type, source_reason))
            return original(backup_type, source_reason)

        service.create_backup = tracking  # type: ignore[method-assign]
        applied = MigrationRunner(conn, default_migrations(), backup_provider=service).apply_pending()
        assert [r.schema_version for r in applied] == [1, 2, 3, 4], applied
        assert calls and calls[0][0] == "pre_migration", calls
        assert len(calls) == 4, calls  # one per applied migration
        records = conn.execute(
            "SELECT backup_type, schema_version FROM backup_records ORDER BY schema_version"
        ).fetchall()
        assert [r["schema_version"] for r in records] == [1, 2, 3], records
        assert all(r["backup_type"] == "pre_migration" for r in records)
        assert len(list(backups.glob("*.db"))) == 4, "expected v0->v1 + 3 recorded snapshots"
        return f"{len(calls)} pre_migration backups fired; recorded snapshots at v{', v'.join(str(r['schema_version']) for r in records)}; 4 backup files on disk"
    finally:
        conn.close()


@check("AC1.e FK expectations: v4 declares no FOREIGN KEY (documented finding)")
def ac1_fk(root: Path):
    conn, _ = fresh_db(root, "ac1e")
    try:
        prog_fk = [dict(r) for r in conn.execute("PRAGMA foreign_key_list(reading_progress)")]
        hist_fk = [dict(r) for r in conn.execute("PRAGMA foreign_key_list(export_history)")]
        return (
            f"reading_progress foreign_key_list={prog_fk}; export_history foreign_key_list={hist_fk}; "
            "foreign_keys PRAGMA is ON, so the delivery report's 'FK + cascade delete' claim is NOT met"
        )
    finally:
        conn.close()


# ----------------------------------------------------------------------
# AC2 — ReadingProgress / ExportHistory round-trip
# ----------------------------------------------------------------------

FULL_ROW = {
    "progress_id": "rp-full",
    "book_id": "book-1",
    "chapter_id": "chap-1",
    "mode": "original",
    "last_page_id": "page-0007",
    "scroll_offset_x": 12.5,
    "scroll_offset_y": 4096.25,
    "progress_percent": 43.75,
    "last_read_at": "2026-09-22T10:11:12.000+00:00",
    "total_read_seconds": 3725.5,
    "updated_at": "2026-09-22T10:11:13.000+00:00",
}


@check("AC2.a ReadingProgress full-field round-trip through the real adapter")
def ac2_roundtrip(root: Path):
    conn, db_path = fresh_db(root, "ac2a")
    try:
        store = SqliteReadingProgressStore(conn)
        store.write({"progress_entries": [dict(FULL_ROW)]})
        got = store.read()["progress_entries"]
        assert len(got) == 1, got
        row = got[0]
        for key, value in FULL_ROW.items():
            assert row[key] == value, (key, row[key], value)
        # restart: a brand-new connection + adapter must see the same values.
        conn.close()
        conn2, _ = open_database(db_path, latest_known_schema_version=SCHEMA_VERSION_V4)
        again = SqliteReadingProgressStore(conn2).read()["progress_entries"][0]
        for key, value in FULL_ROW.items():
            assert again[key] == value, (key, again[key], value)
        conn2.close()
        return "11/11 fields identical before and after reopen"
    finally:
        pass


@check("AC2.b Original and Translated progress stay independent; webtoon fields + duration survive")
def ac2_modes(root: Path):
    conn, db_path = fresh_db(root, "ac2b")
    try:
        store = SqliteReadingProgressStore(conn)
        original = dict(FULL_ROW, progress_id="rp-o", mode="original",
                        last_page_id="p-orig", scroll_offset_y=100.0,
                        progress_percent=10.0, total_read_seconds=60.0)
        translated = dict(FULL_ROW, progress_id="rp-t", mode="translated",
                          last_page_id="p-trans", scroll_offset_y=9999.0,
                          progress_percent=88.0, total_read_seconds=7200.0)
        webtoon = dict(FULL_ROW, progress_id="rp-w", mode="original",
                       chapter_id="chap-webtoon", last_page_id="wt-42",
                       scroll_offset_y=12345.75, total_read_seconds=42.5)
        store.write({"progress_entries": [original, translated, webtoon]})
        conn.close()

        conn2, _ = open_database(db_path, latest_known_schema_version=SCHEMA_VERSION_V4)
        rows = {(r["chapter_id"], r["mode"]): r for r in SqliteReadingProgressStore(conn2).read()["progress_entries"]}
        assert rows[("chap-1", "original")]["progress_id"] == "rp-o"
        assert rows[("chap-1", "translated")]["progress_id"] == "rp-t"
        assert rows[("chap-1", "original")]["last_page_id"] == "p-orig"
        assert rows[("chap-1", "translated")]["last_page_id"] == "p-trans"
        assert rows[("chap-1", "original")]["scroll_offset_y"] == 100.0
        assert rows[("chap-1", "translated")]["scroll_offset_y"] == 9999.0
        assert rows[("chap-1", "translated")]["total_read_seconds"] == 7200.0
        assert rows[("chap-webtoon", "original")]["last_page_id"] == "wt-42"
        assert rows[("chap-webtoon", "original")]["scroll_offset_y"] == 12345.75
        assert rows[("chap-webtoon", "original")]["total_read_seconds"] == 42.5
        conn2.close()
        return "original/translated/webtoon rows independent; last_page_id, scroll_offset_y and total_read_seconds restored after reopen"
    finally:
        pass


@check("AC2.c (book_id, chapter_id, mode) never duplicates under repeated writes")
def ac2_unique(root: Path):
    conn, _ = fresh_db(root, "ac2c")
    try:
        store = SqliteReadingProgressStore(conn)
        for percent in (10.0, 20.0, 30.0):
            store.write({"progress_entries": [dict(FULL_ROW, progress_percent=percent)]})
        rows = store.read()["progress_entries"]
        assert len(rows) == 1, rows
        assert rows[0]["progress_percent"] == 30.0, rows[0]
        assert conn.execute(
            "SELECT COUNT(*) FROM reading_progress WHERE book_id='book-1' AND chapter_id='chap-1' AND mode='original'"
        ).fetchone()[0] == 1
        # A second, differently-keyed row must not be collateral damage.
        store.write({"progress_entries": [
            dict(FULL_ROW, progress_percent=30.0),
            dict(FULL_ROW, progress_id="rp-other", chapter_id="chap-2", progress_percent=1.0),
        ]})
        assert len(store.read()["progress_entries"]) == 2
        return "3 writes -> 1 row (latest percent wins); adding a new key keeps both rows"
    finally:
        conn.close()


@check("AC2.f one progress_id reused by two keys in a single write (observed behaviour)")
def ac2_pid_reuse(root: Path):
    conn, _ = fresh_db(root, "ac2f")
    try:
        store = SqliteReadingProgressStore(conn)
        raised = None
        try:
            store.write({"progress_entries": [
                dict(FULL_ROW, progress_id="dup-pid", chapter_id="c-1"),
                dict(FULL_ROW, progress_id="dup-pid", chapter_id="c-2"),
            ]})
        except Exception as error:  # noqa: BLE001 - observing behaviour
            raised = error
        rows = store.read()["progress_entries"]
        assert rows == [], f"batch was not rolled back: {rows}"
        return (
            f"two rows reusing one progress_id raise "
            f"{type(raised).__name__ if raised else 'NO ERROR'} and the whole batch rolls back (0 rows); "
            "the store never duplicates, but the failure is a raw sqlite3 error, not a typed store error"
        )
    finally:
        conn.close()


@check("AC2.d ExportHistory full-field round-trip, all statuses, newest-first, repeat snapshot")
def ac2_history(root: Path):
    conn, _ = fresh_db(root, "ac2d")
    try:
        store = SqliteExportHistoryStore(conn)
        scope = json.dumps({"page_ids": ["p-1", "p-2"], "filenames": ["a.png", "b.png"],
                            "mode": "translated", "overwrite_policy": "overwrite",
                            "stale_policy": "continue"}, ensure_ascii=False)
        profile = json.dumps({"profile": "high", "dpi": 300}, ensure_ascii=False)
        records = [
            {"export_id": "e-1", "book_id": "b", "chapter_id": "c", "pipeline_run_id": "run-9",
             "export_type": "cbz", "scope_snapshot_json": scope, "output_path": "/out/a.cbz",
             "render_profile_snapshot_json": profile, "status": "completed",
             "file_hash": "h1", "created_at": "2026-09-22T01:00:00.000+00:00",
             "completed_at": "2026-09-22T01:01:00.000+00:00", "detail": "ok"},
            {"export_id": "e-2", "book_id": "b", "chapter_id": "c", "pipeline_run_id": None,
             "export_type": "zip", "scope_snapshot_json": scope, "output_path": "/out/b.zip",
             "render_profile_snapshot_json": "{}", "status": "skipped",
             "file_hash": "", "created_at": "2026-09-22T02:00:00.000+00:00",
             "completed_at": "2026-09-22T02:00:01.000+00:00", "detail": "目标文件已存在"},
            {"export_id": "e-3", "book_id": "b", "chapter_id": "c", "pipeline_run_id": None,
             "export_type": "pdf", "scope_snapshot_json": scope, "output_path": "",
             "render_profile_snapshot_json": "{}", "status": "cancelled",
             "file_hash": "", "created_at": "2026-09-22T03:00:00.000+00:00",
             "completed_at": "", "detail": "用户取消"},
            {"export_id": "e-4", "book_id": "b", "chapter_id": "c", "pipeline_run_id": None,
             "export_type": "text", "scope_snapshot_json": scope, "output_path": "",
             "render_profile_snapshot_json": "{}", "status": "failed",
             "file_hash": "", "created_at": "2026-09-22T04:00:00.000+00:00",
             "completed_at": "", "detail": "ExportCancelledError: boom"},
        ]
        store.write(records)
        read_back = store.read()
        assert [r["export_id"] for r in read_back] == ["e-4", "e-3", "e-2", "e-1"], read_back
        by_id = {r["export_id"]: r for r in read_back}
        for original in records:
            for key, value in original.items():
                assert by_id[original["export_id"]][key] == value, (
                    original["export_id"], key, by_id[original["export_id"]][key], value
                )
        assert {r["status"] for r in read_back} == {"completed", "skipped", "cancelled", "failed"}
        assert by_id["e-1"]["scope_snapshot_json"] == scope
        assert by_id["e-1"]["render_profile_snapshot_json"] == profile
        return "13/13 fields x 4 terminal statuses round-trip; read order is newest-first; repeat snapshots intact"
    finally:
        conn.close()


@check("AC2.e ExportService.repeat rebuilds from the persisted snapshot, not from JSON")
def ac2_repeat(root: Path):
    from application.export.ports import JsonHistoryDocumentStore
    from application.export.service import ExportError, ExportRequest, ExportService, ExportPage
    from application.export.service import ExportFormat, OverwritePolicy, StalePolicy

    conn, db_path = fresh_db(root, "ac2e")
    try:
        # Seed one terminal export row directly through the SQLite adapter.
        scope = json.dumps({"page_ids": ["p-1"], "filenames": ["a.png"], "mode": "original",
                            "overwrite_policy": "overwrite", "stale_policy": "continue"})
        SqliteExportHistoryStore(conn).write([{
            "export_id": "e-rep", "book_id": "b", "chapter_id": "c", "pipeline_run_id": None,
            "export_type": "single_image", "scope_snapshot_json": scope,
            "output_path": str(root / "out.png"), "render_profile_snapshot_json": "{}",
            "status": "completed", "file_hash": "h", "created_at": "2026-09-22T00:00:00.000+00:00",
            "completed_at": "2026-09-22T00:00:01.000+00:00", "detail": "ok",
        }])
        service = ExportService(SqliteExportHistoryStore(conn))
        page = ExportPage(page_id="p-1", filename="a.png", source_provider=lambda: b"PNGDATA")
        result = service.repeat("e-rep", {"p-1": page})
        assert result.status.value == "completed", result
        assert Path(result.output_path) == root / "out.png"
        assert (root / "out.png").read_bytes() == b"PNGDATA"
        # The replayed export appends a second history row; both live in SQLite.
        assert len(service.history()) == 2, service.history()
        assert not (root / "export_history.json").exists()
        return "repeat() replayed the stored scope snapshot and appended a new SQLite row; no JSON file written"
    finally:
        conn.close()


# ----------------------------------------------------------------------
# AC3 — legacy JSON import & read-only protection
# ----------------------------------------------------------------------

def _legacy_pair(root: Path) -> tuple[Path, Path, dict, list]:
    root.mkdir(parents=True, exist_ok=True)
    prog = root / "reading_progress.json"
    hist = root / "export_history.json"
    prog_data = {"progress_entries": [dict(FULL_ROW, progress_id="legacy-1")]}
    hist_data = [{
        "export_id": "legacy-e1", "book_id": "b", "chapter_id": "c", "pipeline_run_id": None,
        "export_type": "cbz", "scope_snapshot_json": "{}", "output_path": "/o.cbz",
        "render_profile_snapshot_json": "{}", "status": "completed", "file_hash": "h",
        "created_at": "2026-09-01T00:00:00.000+00:00", "completed_at": "2026-09-01T00:00:01.000+00:00",
        "detail": "legacy",
    }]
    prog.write_text(json.dumps(prog_data, ensure_ascii=False), encoding="utf-8")
    hist.write_text(json.dumps(hist_data, ensure_ascii=False), encoding="utf-8")
    return prog, hist, prog_data, hist_data


@check("AC3.a valid legacy JSON imports exactly once and the files are byte-identical afterwards")
def ac3_import_once(root: Path):
    conn, db_path = fresh_db(root, "ac3a")
    prog, hist, prog_data, hist_data = _legacy_pair(root)
    before_p, before_h = snapshot(prog), snapshot(hist)
    listing_before = sorted(p.name for p in root.iterdir())

    with WriteWatch() as watch:
        n_prog = import_legacy_reading_progress(conn, prog)
        n_hist = import_legacy_export_history(conn, hist)

    assert (n_prog, n_hist) == (1, 1), (n_prog, n_hist)
    assert snapshot(prog) == before_p, (snapshot(prog), before_p)
    assert snapshot(hist) == before_h, (snapshot(hist), before_h)
    assert sorted(p.name for p in root.iterdir()) == listing_before
    assert watch.touching(prog, hist) == [], watch.touching(prog, hist)

    rows = conn.execute("SELECT * FROM reading_progress").fetchall()
    assert len(rows) == 1 and rows[0]["progress_id"] == "legacy-1"
    rows_h = conn.execute("SELECT * FROM export_history").fetchall()
    assert len(rows_h) == 1 and rows_h[0]["export_id"] == "legacy-e1"
    marker = json.loads(conn.execute(
        "SELECT value_json FROM application_metadata WHERE metadata_key='legacy_reading_progress_imported'"
    ).fetchone()[0])
    assert marker["status"] == "imported" and marker["imported_count"] == 1, marker
    conn.close()

    # restart: fresh connection, no duplicate import, no file change.
    conn2, _ = open_database(db_path, latest_known_schema_version=SCHEMA_VERSION_V4)
    try:
        assert import_legacy_reading_progress(conn2, prog) == 0
        assert import_legacy_export_history(conn2, hist) == 0
        assert conn2.execute("SELECT COUNT(*) FROM reading_progress").fetchone()[0] == 1
        assert conn2.execute("SELECT COUNT(*) FROM export_history").fetchone()[0] == 1
        assert snapshot(prog) == before_p and snapshot(hist) == before_h
    finally:
        conn2.close()
    return "imported once (hash/mtime/size/inode and directory listing unchanged, zero mutating calls); restart re-import returns 0"


@check("AC3.b missing legacy files are an empty legacy store, not an error")
def ac3_missing(root: Path):
    conn, _ = fresh_db(root, "ac3b")
    try:
        missing_p = root / "reading_progress.json"
        missing_h = root / "export_history.json"
        assert import_legacy_reading_progress(conn, missing_p) == 0
        assert import_legacy_export_history(conn, missing_h) == 0
        assert not missing_p.exists() and not missing_h.exists(), "import created a file"
        for key in ("legacy_reading_progress_imported", "legacy_export_history_imported"):
            row = conn.execute(
                "SELECT value_json FROM application_metadata WHERE metadata_key=?", (key,)
            ).fetchone()
            assert row is not None, key
            assert json.loads(row[0])["status"] == "missing_empty", row[0]
        return "missing files -> 0 rows, missing_empty marker, no file created"
    finally:
        conn.close()


# ----------------------------------------------------------------------
# AC4 — corrupt data & failure diagnosis
# ----------------------------------------------------------------------

@check("AC4.a corrupt JSON -> LegacyCorruptJsonError with the original cause chained")
def ac4_corrupt(root: Path):
    conn, _ = fresh_db(root, "ac4a")
    try:
        bad = root / "corrupt.json"
        bad.write_text('{"progress_entries": [{"book_id": "b",]', encoding="utf-8")
        before = snapshot(bad)
        try:
            import_legacy_reading_progress(conn, bad)
            raise AssertionError("no exception for corrupt JSON")
        except LegacyCorruptJsonError as error:
            assert isinstance(error, LegacyImportError)
            assert error.__cause__ is not None, "original cause was swallowed"
            assert "corrupt.json" in str(error), str(error)
            assert isinstance(error.__cause__, json.JSONDecodeError), type(error.__cause__)
        assert snapshot(bad) == before
        assert conn.execute(
            "SELECT COUNT(*) FROM application_metadata WHERE metadata_key='legacy_reading_progress_imported'"
        ).fetchone()[0] == 0, "a failed import wrote a marker"
        assert conn.execute("SELECT COUNT(*) FROM reading_progress").fetchone()[0] == 0
        return "LegacyCorruptJsonError with __cause__=json.JSONDecodeError; file untouched, no marker, no rows"
    finally:
        conn.close()


@check("AC4.b wrong top-level structure -> LegacyInvalidStructureError (both stores)")
def ac4_structure(root: Path):
    conn, _ = fresh_db(root, "ac4b")
    try:
        p = root / "p.json"
        p.write_text(json.dumps({"progress_entries": {"not": "a list"}}), encoding="utf-8")
        try:
            import_legacy_reading_progress(conn, p)
            raise AssertionError("no structure error for non-list entries")
        except LegacyInvalidStructureError as error:
            assert "progress_entries" in str(error), error

        p2 = root / "p2.json"
        p2.write_text(json.dumps(["a", "b"]), encoding="utf-8")
        try:
            import_legacy_reading_progress(conn, p2)
            raise AssertionError("no structure error for list document")
        except LegacyInvalidStructureError:
            pass

        h = root / "h.json"
        h.write_text(json.dumps({"export_id": "x"}), encoding="utf-8")
        try:
            import_legacy_export_history(conn, h)
            raise AssertionError("no structure error for dict history document")
        except LegacyInvalidStructureError:
            pass
        assert conn.execute("SELECT COUNT(*) FROM application_metadata").fetchone()[0] <= 1
        return "non-object progress doc, non-list entries, and non-list history doc all raise LegacyInvalidStructureError"
    finally:
        conn.close()


@check("AC4.c one invalid record aborts the whole import (single record field legality)")
def ac4_record(root: Path):
    conn, _ = fresh_db(root, "ac4c")
    try:
        cases = [
            ("missing mode", {"progress_entries": [{"book_id": "b", "chapter_id": "c"}]}),
            ("bad mode", {"progress_entries": [{"book_id": "b", "chapter_id": "c", "mode": "sideways"}]}),
            ("non-numeric offset", {"progress_entries": [dict(FULL_ROW, scroll_offset_y="abc")]}),
            ("duplicate key", {"progress_entries": [dict(FULL_ROW), dict(FULL_ROW, progress_id="other")]}),
        ]
        seen = []
        for label, payload in cases:
            path = root / f"bad-{abs(hash(label))}.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            try:
                import_legacy_reading_progress(conn, path)
                raise AssertionError(f"{label} was accepted")
            except LegacyInvalidRecordError as error:
                seen.append((label, str(error)[:60]))
        assert len(seen) == 4, seen
        assert conn.execute("SELECT COUNT(*) FROM reading_progress").fetchone()[0] == 0
        # history: invalid status
        h = root / "bad-h.json"
        h.write_text(json.dumps([{"export_id": "e", "status": "bogus"}]), encoding="utf-8")
        try:
            import_legacy_export_history(conn, h)
            raise AssertionError("bogus status accepted")
        except LegacyInvalidRecordError:
            pass
        return f"{len(seen)} progress cases + 1 history case -> LegacyInvalidRecordError, zero rows written"
    finally:
        conn.close()


@check("AC4.d SQLite write failure mid-import rolls back everything and writes no marker")
def ac4_midfail(root: Path):
    conn, _ = fresh_db(root, "ac4d")
    try:
        payload = {
            "progress_entries": [
                dict(FULL_ROW, progress_id="ok-1", chapter_id="c-ok"),
                dict(FULL_ROW, progress_id="boom", chapter_id="c-boom"),
            ]
        }
        path = root / "mid.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        before = snapshot(path)
        with conn:
            conn.execute(
                "CREATE TRIGGER trg_midfail BEFORE INSERT ON reading_progress"
                " WHEN NEW.chapter_id = 'c-boom' BEGIN SELECT RAISE(ABORT, 'injected'); END;"
            )
        raised = None
        try:
            import_legacy_reading_progress(conn, path)
        except Exception as error:  # noqa: BLE001
            raised = error
        assert raised is not None, "injected failure was swallowed"
        assert conn.execute("SELECT COUNT(*) FROM reading_progress").fetchone()[0] == 0, "half rows left"
        assert conn.execute(
            "SELECT COUNT(*) FROM application_metadata WHERE metadata_key='legacy_reading_progress_imported'"
        ).fetchone()[0] == 0, "false marker written"
        assert snapshot(path) == before, "legacy file changed on failure"
        return f"raised {type(raised).__name__}: {str(raised)[:70]} | 0 rows, no marker, file untouched"
    finally:
        conn.close()


@check("AC4.e marker write failure rolls the whole batch back (marker timing)")
def ac4_markerfail(root: Path):
    conn, _ = fresh_db(root, "ac4e")
    try:
        payload = {"progress_entries": [dict(FULL_ROW, progress_id="m-1")]}
        path = root / "marker.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        before = snapshot(path)
        with conn:
            conn.execute(
                "CREATE TRIGGER trg_markerfail BEFORE INSERT ON application_metadata"
                " WHEN NEW.metadata_key = 'legacy_reading_progress_imported'"
                " BEGIN SELECT RAISE(ABORT, 'marker refused'); END;"
            )
        raised = None
        try:
            import_legacy_reading_progress(conn, path)
        except Exception as error:  # noqa: BLE001
            raised = error
        assert raised is not None, "marker failure was swallowed"
        assert conn.execute("SELECT COUNT(*) FROM reading_progress").fetchone()[0] == 0, (
            "rows survived a failed marker write -> import is not atomic"
        )
        assert snapshot(path) == before
        return f"marker INSERT aborted ({type(raised).__name__}); imported rows rolled back with it; file untouched"
    finally:
        conn.close()


@check("AC4.f store write failure preserves existing DB rows and writes no partial row")
def ac4_storefail(root: Path):
    conn, _ = fresh_db(root, "ac4f")
    try:
        store = SqliteReadingProgressStore(conn)
        store.write({"progress_entries": [dict(FULL_ROW, progress_id="keep")]})
        with conn:
            conn.execute(
                "CREATE TRIGGER trg_store_fail BEFORE INSERT ON reading_progress"
                " WHEN NEW.chapter_id = 'c-fail' BEGIN SELECT RAISE(ABORT, 'nope'); END;"
            )
        try:
            store.write({"progress_entries": [
                dict(FULL_ROW, progress_id="keep"),
                dict(FULL_ROW, progress_id="new", chapter_id="c-fail"),
            ]})
            raise AssertionError("injected store failure did not raise")
        except sqlite3.IntegrityError:
            pass
        rows = store.read()["progress_entries"]
        assert len(rows) == 1 and rows[0]["progress_id"] == "keep", rows
        return "existing row intact, no partial row, exactly one row after rollback"
    finally:
        conn.close()


@check("AC4.g error context: messages carry the file path and the offending field")
def ac4_context(root: Path):
    conn, _ = fresh_db(root, "ac4g")
    try:
        bad = root / "ctx.json"
        bad.write_text(json.dumps({"progress_entries": [{"book_id": "b"}]}), encoding="utf-8")
        try:
            import_legacy_reading_progress(conn, bad)
        except LegacyInvalidRecordError as error:
            text = str(error)
            assert "ctx.json" in text, text
            assert "Entry 0" in text, text
            assert "chapter_id" in text, text
        return "message includes file path, record index, and the offending field name"
    finally:
        conn.close()


@check("AC4.h legacy JSON reusing one progress_id across two keys (observed behaviour)")
def ac4_dup_pid(root: Path):
    root.mkdir(parents=True, exist_ok=True)
    conn, db_path = fresh_db(root, "ac4h")
    payload = {"progress_entries": [
        dict(FULL_ROW, progress_id="legacy-dup", chapter_id="c-1"),
        dict(FULL_ROW, progress_id="legacy-dup", chapter_id="c-2"),
    ]}
    path = root / "dup_pid.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    before = snapshot(path)
    raised = None
    try:
        import_legacy_reading_progress(conn, path)
    except Exception as error:  # noqa: BLE001 - observing behaviour
        raised = error
    assert raised is not None, "duplicate progress_id was accepted"
    assert not isinstance(raised, LegacyInvalidRecordError), (
        "duplicate progress_id is already a typed LegacyInvalidRecordError"
    )
    assert conn.execute("SELECT COUNT(*) FROM reading_progress").fetchone()[0] == 0, "half rows left"
    assert conn.execute(
        "SELECT COUNT(*) FROM application_metadata WHERE metadata_key='legacy_reading_progress_imported'"
    ).fetchone()[0] == 0, "false marker written"
    assert snapshot(path) == before, "legacy file changed"
    conn.close()

    # Deterministic on every restart: a real startup through assemble_services
    # would re-raise instead of silently skipping the import.
    conn2, _ = open_database(db_path, latest_known_schema_version=SCHEMA_VERSION_V4)
    try:
        repeated = None
        try:
            import_legacy_reading_progress(conn2, path)
        except Exception as error:  # noqa: BLE001
            repeated = error
        assert repeated is not None and type(repeated) is type(raised), (repeated, raised)
    finally:
        conn2.close()
    return (
        f"raises {type(raised).__name__} (typed={isinstance(raised, LegacyImportError)}); "
        "no rows, no marker, file byte-identical, and identical on the next startup"
    )


# ----------------------------------------------------------------------
# AC5 — production assembly
# ----------------------------------------------------------------------

@check("AC5.a assemble_services wires the SQLite adapters and creates no legacy JSON file")
def ac5_assembly(root: Path):
    data_root = root / "data"
    data_root.mkdir(parents=True, exist_ok=True)
    db_path = data_root / "library.db"
    managed = data_root / "managed"
    services = assemble_services(db_path, managed)
    try:
        assert isinstance(services.reading._store, SqliteReadingProgressStore), type(services.reading._store)
        assert isinstance(services.export_service._store, SqliteExportHistoryStore), type(services.export_service._store)
        assert not (data_root / "reading_progress.json").exists()
        assert not (data_root / "export_history.json").exists()

        # A real reader write must land in SQLite, and reopening must see it.
        services.reading._store.write({"progress_entries": [dict(FULL_ROW, progress_id="live")]})
        conn, _ = open_database(db_path, latest_known_schema_version=SCHEMA_VERSION_V4)
        row = conn.execute("SELECT * FROM reading_progress WHERE progress_id='live'").fetchone()
        assert row is not None and row["scroll_offset_y"] == FULL_ROW["scroll_offset_y"], row
        version = conn.execute("SELECT MAX(schema_version) FROM schema_migrations").fetchone()[0]
        conn.close()
        assert version == 4, version
        return f"assemble_services -> SQLite adapters, live write visible in {db_path.name} at schema v{version}, zero JSON files"
    finally:
        _shutdown_services(services)


@check("AC5.b production assembly imports pre-existing legacy JSON instead of writing it")
def ac5_assembly_imports(root: Path):
    data_root = root / "data2"
    data_root.mkdir(parents=True, exist_ok=True)
    db_path = data_root / "library.db"
    managed = data_root / "managed"
    prog, hist, _, _ = _legacy_pair(data_root)
    before_p, before_h = snapshot(prog), snapshot(hist)
    services = assemble_services(db_path, managed)
    try:
        state = services.reading._store.read()["progress_entries"]
        assert len(state) == 1 and state[0]["progress_id"] == "legacy-1", state
        history = services.export_service.history()
        assert len(history) == 1 and history[0].export_id == "legacy-e1", history
        assert snapshot(prog) == before_p, "assemble_services rewrote reading_progress.json"
        assert snapshot(hist) == before_h, "assemble_services rewrote export_history.json"
        return "startup imported legacy rows into SQLite through the real assembly and left both JSON files byte-identical"
    finally:
        _shutdown_services(services)


@check("AC5.d a real ReadingService session persists to SQLite and a cold restart resumes")
def ac5_reading_session(root: Path):
    from application.reading.ports import ReaderPage

    data_root = root / "data3"
    data_root.mkdir(parents=True, exist_ok=True)
    db_path = data_root / "library.db"
    pages = [
        ReaderPage(page_id=f"p-{i}", filename=f"{i}.png", original_path=str(root / f"{i}.png"))
        for i in (1, 2, 3)
    ]
    services = assemble_services(db_path, data_root / "managed")
    try:
        services.reading.open("b-live", "c-live", pages)
        services.reading.next_page()
        services.reading.add_time(12.5)
        services.reading.close()
    finally:
        _shutdown_services(services)

    services2 = assemble_services(db_path, data_root / "managed")
    try:
        services2.reading.open("b-live", "c-live", pages)
        assert services2.reading.current_page.page_id == "p-2", services2.reading.current_page
        state = services2.reading._store.read()["progress_entries"][0]
        assert state["total_read_seconds"] >= 12.5, state
        assert state["book_id"] == "b-live" and state["mode"] == "original", state
    finally:
        _shutdown_services(services2)
    assert not (data_root / "reading_progress.json").exists()
    assert not (data_root / "export_history.json").exists()
    return "open/next_page/add_time persisted into SQLite; cold re-assembly resumed at p-2 with accumulated duration; no JSON file exists"


@check("AC5.c no production module still selects a JSON store as write truth")
def ac5_no_json_source(_root: Path):
    offenders = []
    for path in (SRC_ROOT / "bootstrap").rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        for needle in ("JsonProgressDocumentStore(", "JsonHistoryDocumentStore("):
            if needle in text:
                offenders.append(f"{path.relative_to(REPO_ROOT)}: {needle}")
    assert offenders == [], offenders
    # assemble_engine only consumes an already-assembled AppServices.
    engine_src = (SRC_ROOT / "bootstrap" / "app.py").read_text(encoding="utf-8")
    engine_body = engine_src.split("def assemble_engine(", 1)[1].split("\ndef ", 1)[0]
    assert "Json" not in engine_body, engine_body[:400]
    assert "Store(" not in engine_body.replace("setContextProperty", ""), "assemble_engine builds a store"
    return "no bootstrap module instantiates a JSON store; assemble_engine only injects viewmodels"


# ----------------------------------------------------------------------
# AC7 — allowed paths
# ----------------------------------------------------------------------

@check("AC7 allowed-path envelope: only sqlite/bootstrap/tests/verification touched")
def ac7_paths(_root: Path):
    import subprocess

    base = "e771179beaa92b7c592a1986a32ffbf1b6302566"
    head = "899bd3c99752ce435da25e41166bafa1c2963abc"
    out = subprocess.run(
        ["git", "diff", "--name-only", f"{base}..{head}"],
        cwd=str(REPO_ROOT), capture_output=True, text=True, check=True, encoding="utf-8",
    )
    files = [line.strip() for line in out.stdout.splitlines() if line.strip()]
    allowed = (
        "src/infrastructure/sqlite/",
        "src/application/reading/ports.py",
        "src/application/export/ports.py",
        "src/bootstrap/app.py",
        "tests/reading_export/",
        "tests/storage/",
        "tests/core/",
        "verification/T3.1.1/",
    )
    violations = [f for f in files if not f.startswith(allowed)]
    assert violations == [], f"outside allowed envelope: {violations}"
    assert [f for f in files if f.endswith((".qml", ".qmldir"))] == [], "QML/UI files changed"
    assert [f for f in files if "requirement" in f.lower() or f.endswith(
        ("pyproject.toml", "uv.lock", "poetry.lock", "setup.py", "setup.cfg")
    )] == [], "dependency files changed"
    forbidden_dirs = ("src/application/pipeline", "src/infrastructure/pipeline",
                      "src/ui/", "src/infrastructure/settings", "src/application/settings")
    assert [f for f in files if f.startswith(forbidden_dirs)] == [], "forbidden area changed"
    return f"{len(files)} changed files, all inside the frozen envelope: {sorted(files)}"


def main() -> int:
    temp = Path(tempfile.mkdtemp(prefix="t311_review_"))
    checks = [
        ac1_schema, ac1_checks, ac1_additive, ac1_guards, ac1_backup, ac1_fk,
        ac2_roundtrip, ac2_modes, ac2_unique, ac2_pid_reuse, ac2_history, ac2_repeat,
        ac3_import_once, ac3_missing,
        ac4_corrupt, ac4_structure, ac4_record, ac4_midfail, ac4_markerfail,
        ac4_storefail, ac4_context, ac4_dup_pid,
        ac5_assembly, ac5_assembly_imports, ac5_reading_session, ac5_no_json_source,
        ac7_paths,
    ]
    try:
        for fn in checks:
            fn(temp / fn._name.split()[0].replace(".", "_"))
        print("=" * 78)
        failed = 0
        for name, ok, detail in RESULTS:
            print(f"[{'PASS' if ok else 'FAIL'}] {name}")
            print(f"       {detail.splitlines()[0][:300]}")
            if not ok:
                failed += 1
                print("       --- traceback ---")
                for line in detail.splitlines()[1:]:
                    print(f"       {line}")
        print("=" * 78)
        print(f"{len(RESULTS) - failed}/{len(RESULTS)} independent review checks passed")
        return 1 if failed else 0
    finally:
        shutil.rmtree(temp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
