"""Database schema, migration and backup ports (D03 §34, D08 AC-DB)."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Protocol


class SchemaState(str, Enum):
    """Compatibility verdict for an opened database (D08 AC-DB-005)."""

    READY = "ready"
    TOO_NEW = "too_new"
    EMPTY = "empty"


@dataclass(frozen=True)
class OpenedDatabase:
    state: SchemaState
    schema_version: int
    #: True when the connection must not perform writes. ``TOO_NEW`` databases
    #: are opened with SQLite ``query_only`` so stale applications fail fast.
    writable: bool


class DatabaseBackupPort(Protocol):
    """Entry point for consistent SQLite backups (D07 §45~48, AC-DB-003)."""

    def create_backup(
        self,
        backup_type: str,
        source_reason: str,
        *,
        app_version: str | None = None,
    ) -> str:
        """Create a backup and return its ``backup_id``."""
        ...


@dataclass(frozen=True)
class MigrationRecord:
    schema_version: int
    migration_name: str
    checksum: str


class SchemaMigrationPort(Protocol):
    """Applies versioned migrations with checksums (D03 §34.2)."""

    def current_version(self) -> int:
        ...

    def pending_migrations(self) -> list[MigrationRecord]:
        ...

    def apply_pending(self) -> list[MigrationRecord]:
        """Apply pending migrations; each runs inside its own transaction."""
        ...
