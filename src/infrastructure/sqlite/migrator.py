"""Versioned migration runner with checksums and backup hook.

Implements D03 §34.2 (version/name/checksum/applied_at, pre-migration
backup), D07 §50 (migration inside one transaction, no half-migrated
database) and AC-DB-005 (a newer schema is never touched).
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from typing import Callable, Protocol

from infrastructure.sqlite.connection import SchemaTooNewError
from infrastructure.sqlite.schema import Migration
from ports.repositories.database import MigrationRecord

BackupHook = Callable[[int], str]


class _BackupProvider(Protocol):
    """Minimal shape used from :mod:`infrastructure.sqlite.backup`."""

    def create_backup(self, backup_type: str, source_reason: str) -> str: ...


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def read_schema_version(conn: sqlite3.Connection) -> int | None:
    """Return MAX(schema_version) or None when the table does not exist yet."""
    row = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='schema_migrations'"
    ).fetchone()
    if row is None:
        return None
    row = conn.execute("SELECT MAX(schema_version) FROM schema_migrations").fetchone()
    return int(row[0]) if row and row[0] is not None else None


class MigrationRunner:
    """Applies pending migrations, newest-first checks, one transaction each."""

    def __init__(
        self,
        conn: sqlite3.Connection,
        migrations: tuple[Migration, ...],
        backup_provider: _BackupProvider | None = None,
    ) -> None:
        self._conn = conn
        self._migrations = tuple(sorted(migrations, key=lambda m: m.schema_version))
        self._backup_provider = backup_provider

    def latest_known_version(self) -> int:
        return self._migrations[-1].schema_version if self._migrations else 0

    def current_version(self) -> int:
        return read_schema_version(self._conn) or 0

    def pending_migrations(self) -> list[MigrationRecord]:
        current = self.current_version()
        return [
            MigrationRecord(m.schema_version, m.migration_name, m.checksum)
            for m in self._migrations
            if m.schema_version > current
        ]

    def apply_pending(self) -> list[MigrationRecord]:
        """Apply pending migrations in order; failures roll back atomically.

        Raises :class:`SchemaTooNewError` when the stored version is newer
        than every known migration (stale application against a newer
        schema, AC-DB-005) without touching the database.
        """
        current = self.current_version()
        if current > self.latest_known_version():
            raise SchemaTooNewError(
                f"database schema v{current} is newer than known v{self.latest_known_version()}"
            )
        applied: list[MigrationRecord] = []
        for migration in self._migrations:
            if migration.schema_version <= current:
                continue
            self._verify_checksum(migration)
            if self._backup_provider is not None:
                # D07 §46/§50: pre-migration backup before any DDL runs. The
                # backup reads a consistent pre-migration snapshot outside
                # the migration transaction.
                self._backup_provider.create_backup(
                    "pre_migration",
                    f"before schema_version={migration.schema_version}",
                )
            self._apply_one(migration)
            applied.append(
                MigrationRecord(
                    migration.schema_version, migration.migration_name, migration.checksum
                )
            )
        return applied

    def _verify_checksum(self, migration: Migration) -> None:
        """Detect an edited migration history; nothing to check pre-v1."""
        table = self._conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='schema_migrations'"
        ).fetchone()
        if table is None:
            return
        row = self._conn.execute(
            "SELECT checksum FROM schema_migrations WHERE schema_version = ?",
            (migration.schema_version,),
        ).fetchone()
        if row is not None and row["checksum"] != migration.checksum:
            raise sqlite3.IntegrityError(
                f"checksum mismatch for schema_version={migration.schema_version}: "
                "migration content changed after being applied"
            )

    def _apply_one(self, migration: Migration) -> None:
        conn = self._conn
        conn.execute("BEGIN IMMEDIATE")
        try:
            for statement in filter(None, (s.strip() for s in migration.sql.split(";"))):
                conn.execute(statement)
            conn.execute(
                "INSERT INTO schema_migrations (schema_version, migration_name, applied_at, checksum)"
                " VALUES (?, ?, ?, ?)",
                (
                    migration.schema_version,
                    migration.migration_name,
                    _utc_now(),
                    migration.checksum,
                ),
            )
            conn.execute(
                "INSERT INTO application_metadata (metadata_key, value_json, updated_at)"
                " VALUES ('schema_version', ?, ?)"
                " ON CONFLICT(metadata_key) DO UPDATE SET value_json = excluded.value_json,"
                " updated_at = excluded.updated_at",
                (str(migration.schema_version), _utc_now()),
            )
            conn.commit()
        except sqlite3.Error:
            conn.rollback()
            raise
