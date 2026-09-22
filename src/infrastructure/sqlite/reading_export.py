"""SQLite persistence adapters for reading progress and export history (T3.1.1).

Replaces JSON file storage (reading_progress.json, export_history.json) with
unified SQLite persistence, satisfying D03 §29, D03 §31, AC-READ-002, and
AC-EXPORT-002.

Adapters implement the application-layer ProgressDocumentStore and
HistoryDocumentStore protocols, enabling seamless dependency injection without
rewriting ReadingService or ExportService logic.
"""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from domain.books.entities import utc_now


METADATA_KEY_READING_PROGRESS_IMPORTED = "legacy_reading_progress_imported"
METADATA_KEY_EXPORT_HISTORY_IMPORTED = "legacy_export_history_imported"


class LegacyImportError(Exception):
    """Base exception for legacy JSON import failures."""


class LegacyCorruptJsonError(LegacyImportError):
    """Raised when a legacy JSON file cannot be decoded."""


class LegacyInvalidStructureError(LegacyImportError):
    """Raised when the top-level structure of a legacy JSON file is invalid."""


class LegacyInvalidRecordError(LegacyImportError):
    """Raised when one or more entries in a legacy JSON file are invalid."""


class SqliteReadingProgressStore:
    """SQLite adapter for reading progress implementing ProgressDocumentStore."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def read(self) -> dict[str, Any]:
        """Read all reading progress rows from SQLite into progress_entries."""
        cursor = self._conn.execute(
            """
            SELECT progress_id, book_id, chapter_id, mode,
                   last_page_id, scroll_offset_x, scroll_offset_y,
                   progress_percent, last_read_at, total_read_seconds, updated_at
            FROM reading_progress
            """
        )
        rows = [
            {
                "progress_id": row[0],
                "book_id": row[1],
                "chapter_id": row[2],
                "mode": row[3],
                "last_page_id": row[4],
                "scroll_offset_x": float(row[5]),
                "scroll_offset_y": float(row[6]),
                "progress_percent": float(row[7]),
                "last_read_at": row[8],
                "total_read_seconds": float(row[9]),
                "updated_at": row[10],
            }
            for row in cursor.fetchall()
        ]
        return {"progress_entries": rows}

    def write(self, state: dict[str, Any]) -> None:
        """Atomically persist progress entries into SQLite."""
        entries = state.get("progress_entries", [])
        if not isinstance(entries, list):
            entries = []

        with self._conn:
            if not entries:
                self._conn.execute("DELETE FROM reading_progress")
                return

            active_ids: set[str] = set()
            for entry in entries:
                if not isinstance(entry, dict):
                    continue
                book_id = str(entry.get("book_id", ""))
                chapter_id = str(entry.get("chapter_id", ""))
                if not book_id or not chapter_id:
                    continue
                pid = str(entry.get("progress_id") or f"rp-{uuid.uuid4().hex[:12]}")
                mode = str(entry.get("mode", "original"))
                last_page_id = str(entry.get("last_page_id", ""))
                scroll_offset_x = float(entry.get("scroll_offset_x", 0.0) or 0.0)
                scroll_offset_y = float(entry.get("scroll_offset_y", 0.0) or 0.0)
                progress_percent = float(entry.get("progress_percent", 0.0) or 0.0)
                last_read_at = str(entry.get("last_read_at", ""))
                total_read_seconds = float(entry.get("total_read_seconds", 0.0) or 0.0)
                updated_at = str(entry.get("updated_at") or utc_now())

                self._conn.execute(
                    """
                    INSERT INTO reading_progress (
                        progress_id, book_id, chapter_id, mode,
                        last_page_id, scroll_offset_x, scroll_offset_y,
                        progress_percent, last_read_at, total_read_seconds, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(book_id, chapter_id, mode) DO UPDATE SET
                        progress_id = excluded.progress_id,
                        last_page_id = excluded.last_page_id,
                        scroll_offset_x = excluded.scroll_offset_x,
                        scroll_offset_y = excluded.scroll_offset_y,
                        progress_percent = excluded.progress_percent,
                        last_read_at = excluded.last_read_at,
                        total_read_seconds = excluded.total_read_seconds,
                        updated_at = excluded.updated_at
                    """,
                    (
                        pid, book_id, chapter_id, mode,
                        last_page_id, scroll_offset_x, scroll_offset_y,
                        progress_percent, last_read_at, total_read_seconds, updated_at
                    ),
                )
                active_ids.add(pid)

            if active_ids:
                placeholders = ",".join("?" for _ in active_ids)
                self._conn.execute(
                    f"DELETE FROM reading_progress WHERE progress_id NOT IN ({placeholders})",
                    tuple(active_ids),
                )


class SqliteExportHistoryStore:
    """SQLite adapter for export history implementing HistoryDocumentStore."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def read(self) -> list[dict[str, Any]]:
        """Read export records from SQLite, ordered newest-first."""
        cursor = self._conn.execute(
            """
            SELECT export_id, book_id, chapter_id, pipeline_run_id, export_type,
                   scope_snapshot_json, output_path, render_profile_snapshot_json,
                   status, file_hash, created_at, completed_at, detail
            FROM export_history
            ORDER BY created_at DESC
            """
        )
        return [
            {
                "export_id": row[0],
                "book_id": row[1],
                "chapter_id": row[2],
                "pipeline_run_id": row[3],
                "export_type": row[4],
                "scope_snapshot_json": row[5],
                "output_path": row[6],
                "render_profile_snapshot_json": row[7],
                "status": row[8],
                "file_hash": row[9],
                "created_at": row[10],
                "completed_at": row[11],
                "detail": row[12],
            }
            for row in cursor.fetchall()
        ]

    def write(self, records: list[dict[str, Any]]) -> None:
        """Atomically persist export records into SQLite."""
        if not isinstance(records, list):
            records = []

        with self._conn:
            if not records:
                self._conn.execute("DELETE FROM export_history")
                return

            active_ids: set[str] = set()
            for record in records:
                if not isinstance(record, dict):
                    continue
                export_id = str(record.get("export_id") or f"exp-{uuid.uuid4().hex[:12]}")
                book_id = str(record.get("book_id", ""))
                chapter_id = str(record.get("chapter_id", ""))
                pipeline_run_id = record.get("pipeline_run_id")
                if pipeline_run_id is not None:
                    pipeline_run_id = str(pipeline_run_id)
                export_type = str(record.get("export_type", "single_image"))
                scope_snapshot_json = str(record.get("scope_snapshot_json") or "{}")
                output_path = str(record.get("output_path", ""))
                render_profile_snapshot_json = str(record.get("render_profile_snapshot_json") or "{}")
                status = str(record.get("status", "completed"))
                file_hash = str(record.get("file_hash", ""))
                created_at = str(record.get("created_at") or utc_now())
                completed_at = str(record.get("completed_at", ""))
                detail = str(record.get("detail", ""))

                self._conn.execute(
                    """
                    INSERT INTO export_history (
                        export_id, book_id, chapter_id, pipeline_run_id, export_type,
                        scope_snapshot_json, output_path, render_profile_snapshot_json,
                        status, file_hash, created_at, completed_at, detail
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(export_id) DO UPDATE SET
                        book_id = excluded.book_id,
                        chapter_id = excluded.chapter_id,
                        pipeline_run_id = excluded.pipeline_run_id,
                        export_type = excluded.export_type,
                        scope_snapshot_json = excluded.scope_snapshot_json,
                        output_path = excluded.output_path,
                        render_profile_snapshot_json = excluded.render_profile_snapshot_json,
                        status = excluded.status,
                        file_hash = excluded.file_hash,
                        created_at = excluded.created_at,
                        completed_at = excluded.completed_at,
                        detail = excluded.detail
                    """,
                    (
                        export_id, book_id, chapter_id, pipeline_run_id, export_type,
                        scope_snapshot_json, output_path, render_profile_snapshot_json,
                        status, file_hash, created_at, completed_at, detail
                    ),
                )
                active_ids.add(export_id)

            if active_ids:
                placeholders = ",".join("?" for _ in active_ids)
                self._conn.execute(
                    f"DELETE FROM export_history WHERE export_id NOT IN ({placeholders})",
                    tuple(active_ids),
                )


# Convenience aliases for parity with JSON stores
SqliteProgressDocumentStore = SqliteReadingProgressStore
SqliteHistoryDocumentStore = SqliteExportHistoryStore


def import_legacy_reading_progress(conn: sqlite3.Connection, path: str | Path) -> int:
    """One-time import of legacy reading_progress.json into SQLite.

    Guarantees:
    - Checks application_metadata; if already imported, returns 0.
    - If file does not exist, marks as empty check and returns 0.
    - If file exists but is corrupted, raises LegacyCorruptJsonError without altering DB or file.
    - If top-level structure is invalid, raises LegacyInvalidStructureError.
    - If any entry is invalid, raises LegacyInvalidRecordError.
    - On success, imports all valid rows and records marker in a single atomic transaction.
    - Original file is preserved untouched (read-only).
    """
    row = conn.execute(
        "SELECT value_json FROM application_metadata WHERE metadata_key = ?",
        (METADATA_KEY_READING_PROGRESS_IMPORTED,),
    ).fetchone()
    if row is not None:
        return 0

    json_file = Path(path)
    if not json_file.exists():
        now = utc_now()
        with conn:
            conn.execute(
                """
                INSERT INTO application_metadata (metadata_key, value_json, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(metadata_key) DO UPDATE SET
                    value_json = excluded.value_json,
                    updated_at = excluded.updated_at
                """,
                (
                    METADATA_KEY_READING_PROGRESS_IMPORTED,
                    json.dumps({"status": "missing_empty", "imported_count": 0, "checked_at": now}),
                    now,
                ),
            )
        return 0

    try:
        raw_text = json_file.read_text(encoding="utf-8")
    except Exception as error:
        raise LegacyCorruptJsonError(f"Cannot read legacy file {json_file}: {error}") from error

    try:
        data = json.loads(raw_text)
    except Exception as error:
        raise LegacyCorruptJsonError(f"Corrupt JSON in legacy file {json_file}: {error}") from error

    if not isinstance(data, dict):
        raise LegacyInvalidStructureError(
            f"Top-level structure in {json_file} must be a JSON object, got {type(data).__name__}"
        )

    entries = data.get("progress_entries")
    if not isinstance(entries, list):
        raise LegacyInvalidStructureError(
            f"'progress_entries' in {json_file} must be a list, got {type(entries).__name__}"
        )

    seen_keys: set[tuple[str, str, str]] = set()
    validated_rows: list[tuple[Any, ...]] = []
    for idx, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise LegacyInvalidRecordError(f"Entry {idx} in {json_file} is not an object: {entry!r}")
        book_id = entry.get("book_id")
        chapter_id = entry.get("chapter_id")
        mode = entry.get("mode")
        if not book_id or not isinstance(book_id, str):
            raise LegacyInvalidRecordError(f"Entry {idx} in {json_file} missing valid 'book_id'")
        if not chapter_id or not isinstance(chapter_id, str):
            raise LegacyInvalidRecordError(f"Entry {idx} in {json_file} missing valid 'chapter_id'")
        if mode not in ("original", "translated"):
            raise LegacyInvalidRecordError(f"Entry {idx} in {json_file} has invalid mode: {mode!r}")

        key = (book_id, chapter_id, mode)
        if key in seen_keys:
            raise LegacyInvalidRecordError(
                f"Duplicate reading progress entry for book={book_id}, chapter={chapter_id}, mode={mode}"
            )
        seen_keys.add(key)

        pid = entry.get("progress_id")
        if not pid or not isinstance(pid, str):
            pid = f"rp-{uuid.uuid4().hex[:12]}"

        last_page_id = str(entry.get("last_page_id", ""))
        try:
            scroll_x = float(entry.get("scroll_offset_x", 0.0) or 0.0)
            scroll_y = float(entry.get("scroll_offset_y", 0.0) or 0.0)
            percent = float(entry.get("progress_percent", 0.0) or 0.0)
            total_seconds = float(entry.get("total_read_seconds", 0.0) or 0.0)
        except (TypeError, ValueError) as error:
            raise LegacyInvalidRecordError(
                f"Entry {idx} in {json_file} has invalid numeric value: {error}"
            ) from error

        last_read_at = str(entry.get("last_read_at", ""))
        updated_at = str(entry.get("updated_at") or utc_now())

        validated_rows.append((
            pid, book_id, chapter_id, mode,
            last_page_id, scroll_x, scroll_y,
            percent, last_read_at, total_seconds, updated_at
        ))

    now = utc_now()
    with conn:
        for row in validated_rows:
            conn.execute(
                """
                INSERT INTO reading_progress (
                    progress_id, book_id, chapter_id, mode,
                    last_page_id, scroll_offset_x, scroll_offset_y,
                    progress_percent, last_read_at, total_read_seconds, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(book_id, chapter_id, mode) DO UPDATE SET
                    progress_id = excluded.progress_id,
                    last_page_id = excluded.last_page_id,
                    scroll_offset_x = excluded.scroll_offset_x,
                    scroll_offset_y = excluded.scroll_offset_y,
                    progress_percent = excluded.progress_percent,
                    last_read_at = excluded.last_read_at,
                    total_read_seconds = excluded.total_read_seconds,
                    updated_at = excluded.updated_at
                """,
                row,
            )
        conn.execute(
            """
            INSERT INTO application_metadata (metadata_key, value_json, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(metadata_key) DO UPDATE SET
                value_json = excluded.value_json,
                updated_at = excluded.updated_at
            """,
            (
                METADATA_KEY_READING_PROGRESS_IMPORTED,
                json.dumps({
                    "status": "imported",
                    "imported_count": len(validated_rows),
                    "imported_at": now,
                    "source_file": str(json_file),
                }),
                now,
            ),
        )
    return len(validated_rows)


def import_legacy_export_history(conn: sqlite3.Connection, path: str | Path) -> int:
    """One-time import of legacy export_history.json into SQLite.

    Guarantees:
    - Checks application_metadata; if already imported, returns 0.
    - If file does not exist, marks as empty check and returns 0.
    - If file exists but is corrupted, raises LegacyCorruptJsonError without altering DB or file.
    - If top-level structure is not a list, raises LegacyInvalidStructureError.
    - If any record is invalid, raises LegacyInvalidRecordError.
    - On success, imports all valid rows and records marker in a single atomic transaction.
    - Original file is preserved untouched (read-only).
    """
    row = conn.execute(
        "SELECT value_json FROM application_metadata WHERE metadata_key = ?",
        (METADATA_KEY_EXPORT_HISTORY_IMPORTED,),
    ).fetchone()
    if row is not None:
        return 0

    json_file = Path(path)
    if not json_file.exists():
        now = utc_now()
        with conn:
            conn.execute(
                """
                INSERT INTO application_metadata (metadata_key, value_json, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(metadata_key) DO UPDATE SET
                    value_json = excluded.value_json,
                    updated_at = excluded.updated_at
                """,
                (
                    METADATA_KEY_EXPORT_HISTORY_IMPORTED,
                    json.dumps({"status": "missing_empty", "imported_count": 0, "checked_at": now}),
                    now,
                ),
            )
        return 0

    try:
        raw_text = json_file.read_text(encoding="utf-8")
    except Exception as error:
        raise LegacyCorruptJsonError(f"Cannot read legacy file {json_file}: {error}") from error

    try:
        data = json.loads(raw_text)
    except Exception as error:
        raise LegacyCorruptJsonError(f"Corrupt JSON in legacy file {json_file}: {error}") from error

    if not isinstance(data, list):
        raise LegacyInvalidStructureError(
            f"Top-level structure in {json_file} must be a JSON list, got {type(data).__name__}"
        )

    valid_statuses = {"completed", "skipped", "cancelled", "failed"}
    seen_ids: set[str] = set()
    validated_records: list[tuple[Any, ...]] = []

    for idx, record in enumerate(data):
        if not isinstance(record, dict):
            raise LegacyInvalidRecordError(f"Record {idx} in {json_file} is not an object: {record!r}")
        export_id = record.get("export_id")
        if not export_id or not isinstance(export_id, str):
            raise LegacyInvalidRecordError(f"Record {idx} in {json_file} missing valid 'export_id'")
        if export_id in seen_ids:
            raise LegacyInvalidRecordError(f"Duplicate export_id {export_id!r} in {json_file}")
        seen_ids.add(export_id)

        book_id = str(record.get("book_id", ""))
        chapter_id = str(record.get("chapter_id", ""))
        pipeline_run_id = record.get("pipeline_run_id")
        if pipeline_run_id is not None:
            pipeline_run_id = str(pipeline_run_id)
        export_type = str(record.get("export_type", "single_image"))
        scope_snapshot_json = str(record.get("scope_snapshot_json") or "{}")
        output_path = str(record.get("output_path", ""))
        render_profile_snapshot_json = str(record.get("render_profile_snapshot_json") or "{}")
        status = str(record.get("status", "completed"))
        if status not in valid_statuses:
            raise LegacyInvalidRecordError(f"Record {idx} in {json_file} has invalid status: {status!r}")

        file_hash = str(record.get("file_hash", ""))
        created_at = str(record.get("created_at") or utc_now())
        completed_at = str(record.get("completed_at", ""))
        detail = str(record.get("detail", ""))

        validated_records.append((
            export_id, book_id, chapter_id, pipeline_run_id, export_type,
            scope_snapshot_json, output_path, render_profile_snapshot_json,
            status, file_hash, created_at, completed_at, detail
        ))

    now = utc_now()
    with conn:
        for rec in validated_records:
            conn.execute(
                """
                INSERT INTO export_history (
                    export_id, book_id, chapter_id, pipeline_run_id, export_type,
                    scope_snapshot_json, output_path, render_profile_snapshot_json,
                    status, file_hash, created_at, completed_at, detail
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(export_id) DO UPDATE SET
                    book_id = excluded.book_id,
                    chapter_id = excluded.chapter_id,
                    pipeline_run_id = excluded.pipeline_run_id,
                    export_type = excluded.export_type,
                    scope_snapshot_json = excluded.scope_snapshot_json,
                    output_path = excluded.output_path,
                    render_profile_snapshot_json = excluded.render_profile_snapshot_json,
                    status = excluded.status,
                    file_hash = excluded.file_hash,
                    created_at = excluded.created_at,
                    completed_at = excluded.completed_at,
                    detail = excluded.detail
                """,
                rec,
            )
        conn.execute(
            """
            INSERT INTO application_metadata (metadata_key, value_json, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(metadata_key) DO UPDATE SET
                value_json = excluded.value_json,
                updated_at = excluded.updated_at
            """,
            (
                METADATA_KEY_EXPORT_HISTORY_IMPORTED,
                json.dumps({
                    "status": "imported",
                    "imported_count": len(validated_records),
                    "imported_at": now,
                    "source_file": str(json_file),
                }),
                now,
            ),
        )
    return len(validated_records)
