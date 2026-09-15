"""SQLite backup service writing BackupRecord metadata (D03 §34.3)."""

from __future__ import annotations

import hashlib
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

from infrastructure.sqlite.migrator import read_schema_version


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class SqliteBackupService:
    """Creates consistent backups via the SQLite backup API (D07 §48)."""

    def __init__(self, conn: sqlite3.Connection, backup_root: str | Path) -> None:
        self._conn = conn
        self._backup_root = Path(backup_root)
        self._backup_root.mkdir(parents=True, exist_ok=True)

    def create_backup(
        self,
        backup_type: str,
        source_reason: str,
        *,
        app_version: str | None = None,
    ) -> str:
        if backup_type not in {"automatic", "manual", "pre_migration", "pre_restore"}:
            raise ValueError(f"unsupported backup_type: {backup_type}")
        backup_id = uuid.uuid4().hex
        target = self._backup_root / f"{backup_id}.db"
        destination = sqlite3.connect(str(target))
        try:
            self._conn.backup(destination)
            destination.commit()
        finally:
            destination.close()

        created_at = _utc_now()
        schema_version = read_schema_version(self._conn)
        size_bytes = target.stat().st_size
        database_hash = sha256_file(target)
        if not self._backup_records_table_exists():
            # The v0 → v1 pre-migration backup runs before any schema exists,
            # so there is nowhere to record metadata yet; the backup file
            # itself remains the deliverable. Later backups are recorded.
            return backup_id
        with self._conn:
            self._conn.execute(
                "INSERT INTO backup_records (backup_id, backup_type, managed_path, status,"
                " app_version, schema_version, database_hash, size_bytes, created_at,"
                " completed_at, source_reason)"
                " VALUES (?, ?, ?, 'completed', ?, ?, ?, ?, ?, ?, ?)",
                (
                    backup_id,
                    backup_type,
                    target.name,
                    app_version,
                    schema_version,
                    database_hash,
                    size_bytes,
                    created_at,
                    _utc_now(),
                    source_reason,
                ),
            )
        return backup_id

    def _backup_records_table_exists(self) -> bool:
        row = self._conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='backup_records'"
        ).fetchone()
        return row is not None
