"""Core/SQLite catalog authority for the resource channel (M2-RC2, F-03).

The catalog (``resource_id -> (scope_class, rel_path)``) is Core-owned state:
the Tauri host cannot name file paths over the control bridge, and the
WebView has no command that can write catalog rows. Writes go through the
loader entry point (``catalog_loader``) or the product Core; reads happen at
issue time inside the sidecar.

Storage is a dedicated SQLite database file passed in by the launcher (lab:
``M2RC2_CATALOG_DB``). It intentionally does **not** touch the shared product
schema/migrations (out of this Task's allowed paths); the product wiring swaps
this adapter for the product DB in a later slice. The store is read at issue
time and never trusts caller-supplied paths: rows are validated at write time
with the same rel-path gate the service applies at issue time.

Imports stay on the standard library only so the sidecar entry keeps its
import isolation (M2-RC2 F-05).
"""

from __future__ import annotations

import sqlite3
import threading
from pathlib import Path
from typing import NamedTuple, Optional

from application.resource_channel.dto import (
    ALLOWED_SCOPE_CLASSES,
    TypedResourceChannelError,
    E_MALFORMED,
    E_SCOPE_DENIED,
    validate_rel_path,
)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS resource_catalog (
    resource_id TEXT PRIMARY KEY,
    scope_class TEXT NOT NULL,
    rel_path    TEXT NOT NULL
)
"""


class CatalogEntry(NamedTuple):
    resource_id: str
    scope_class: str
    rel_path: str


class ResourceCatalogStore:
    """SQLite-backed catalog authority (single connection, mutex-serialised)."""

    def __init__(self, db_path: Path | str) -> None:
        self._lock = threading.Lock()
        self._connection = sqlite3.connect(str(db_path), check_same_thread=False)
        with self._lock:
            self._connection.execute(_SCHEMA)
            self._connection.commit()

    # --------------------------------------------------------------- writes

    def upsert(self, resource_id: str, scope_class: str, rel_path: str) -> None:
        """Insert or replace one catalog row; both columns are validated here
        so a poisoned write can never mint a servable grant."""

        if not isinstance(resource_id, str) or not resource_id:
            raise TypedResourceChannelError(E_MALFORMED, "resource_id must be a non-empty string")
        if scope_class not in ALLOWED_SCOPE_CLASSES:
            raise TypedResourceChannelError(
                E_SCOPE_DENIED, f"scope class not servable: {scope_class}"
            )
        validate_rel_path(rel_path)
        with self._lock:
            self._connection.execute(
                "INSERT INTO resource_catalog(resource_id, scope_class, rel_path) "
                "VALUES(?, ?, ?) "
                "ON CONFLICT(resource_id) DO UPDATE SET scope_class=excluded.scope_class, "
                "rel_path=excluded.rel_path",
                (resource_id, scope_class, rel_path),
            )
            self._connection.commit()

    def remove(self, resource_id: str) -> bool:
        with self._lock:
            cursor = self._connection.execute(
                "DELETE FROM resource_catalog WHERE resource_id = ?", (resource_id,)
            )
            self._connection.commit()
        return cursor.rowcount > 0

    # ---------------------------------------------------------------- reads

    def lookup(self, resource_id: str) -> Optional[CatalogEntry]:
        with self._lock:
            row = self._connection.execute(
                "SELECT resource_id, scope_class, rel_path FROM resource_catalog "
                "WHERE resource_id = ?",
                (resource_id,),
            ).fetchone()
        return CatalogEntry(*row) if row is not None else None

    def count(self) -> int:
        with self._lock:
            (count,) = self._connection.execute(
                "SELECT COUNT(*) FROM resource_catalog"
            ).fetchone()
        return int(count)

    def entries(self) -> list[CatalogEntry]:
        with self._lock:
            rows = self._connection.execute(
                "SELECT resource_id, scope_class, rel_path FROM resource_catalog "
                "ORDER BY resource_id"
            ).fetchall()
        return [CatalogEntry(*row) for row in rows]

    def close(self) -> None:
        with self._lock:
            self._connection.close()
