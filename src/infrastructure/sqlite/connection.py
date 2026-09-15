"""Connection opening, PRAGMAs and schema compatibility gating.

Implements D07 §28 (PRAGMA profile), §36 (Unicode paths, no MAX_PATH
assumption) and AC-DB-001/002/005: foreign keys on, WAL journal, and
databases written by a newer schema are opened read-only so stale
applications cannot blind-write.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from ports.repositories.database import OpenedDatabase, SchemaState

BUSY_TIMEOUT_MS = 5000


class SchemaTooNewError(RuntimeError):
    """Raised when a migration runner meets a schema newer than known."""


def _read_schema_version(conn: sqlite3.Connection) -> int | None:
    """Return the stored schema version, or None for an empty database."""
    row = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='schema_migrations'"
    ).fetchone()
    if row is None:
        return None
    row = conn.execute("SELECT MAX(schema_version) FROM schema_migrations").fetchone()
    version = row[0] if row else None
    return int(version) if version is not None else None


def _apply_pragmas(conn: sqlite3.Connection) -> None:
    conn.execute(f"PRAGMA busy_timeout = {BUSY_TIMEOUT_MS}")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = NORMAL")


def open_database(
    db_path: str | Path,
    *,
    latest_known_schema_version: int,
) -> tuple[sqlite3.Connection, OpenedDatabase]:
    """Open ``db_path`` with the approved PRAGMA profile.

    A database whose stored schema version exceeds
    ``latest_known_schema_version`` is reopened read-only (``query_only``) and
    reported as :class:`SchemaState.TOO_NEW`; the caller must treat it as
    unusable for writes (AC-DB-005). An empty file reports
    :class:`SchemaState.EMPTY` and stays writable so the migrator can create
    the schema.
    """
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    _apply_pragmas(conn)

    stored = _read_schema_version(conn)
    if stored is None:
        return conn, OpenedDatabase(SchemaState.EMPTY, 0, True)
    if stored > latest_known_schema_version:
        conn.execute("PRAGMA query_only = ON")
        return conn, OpenedDatabase(SchemaState.TOO_NEW, stored, False)
    return conn, OpenedDatabase(SchemaState.READY, stored, True)


def open_readonly(db_path: str | Path) -> sqlite3.Connection:
    """Open a database strictly read-only via the SQLite URI mechanism."""
    uri = f"file:{Path(db_path).as_posix()}?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA query_only = ON")
    return conn
