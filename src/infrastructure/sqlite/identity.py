"""Database identity primitive (C-01b SC-18; FEA-13-ID-3).

The library identity lives in the existing ``application_metadata`` table -- no
new DDL, no schema pin. Semantics fixed by C-01b SC-18 and the FEA-13 scope:

* a fresh writable library gets one UUID4, written atomically and idempotently;
* a legacy library (no row yet) is back-filled on first ``ensure`` and reads as
  **unknown (None)** until then -- never an empty string, a title or a hash;
* every caller treats ``None`` as "unknown", never as a mismatch.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

DATABASE_ID_KEY = "database_id"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def read_database_id(conn) -> str | None:
    """The stored identity, or ``None`` when the library has none yet."""
    row = conn.execute(
        "SELECT value_json FROM application_metadata WHERE metadata_key = ?",
        (DATABASE_ID_KEY,),
    ).fetchone()
    if row is None:
        return None
    raw = row[0]
    try:
        value = json.loads(raw)
    except (TypeError, ValueError):
        return None
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def ensure_database_id(conn, *, uuid_factory=uuid.uuid4) -> str:
    """Return the library identity, creating it atomically on first use.

    ``INSERT OR IGNORE`` makes concurrent/first-boot races harmless: the first
    writer wins and every caller reads back the single stored value.

    Contract: call this with **no active caller transaction**. It owns a
    ``with conn:`` block, so calling it inside a migration transaction would
    commit that transaction early (the assembly calls it after
    ``apply_pending`` has committed). A corrupted stored value reads as
    ``None`` (unknown) rather than raising -- identity must never block a
    backup, and the mismatch gate treats unknown as "cannot compare".
    """
    existing = read_database_id(conn)
    if existing is not None:
        return existing
    candidate = str(uuid_factory())
    with conn:
        conn.execute(
            "INSERT OR IGNORE INTO application_metadata"
            " (metadata_key, value_json, updated_at) VALUES (?, ?, ?)",
            (DATABASE_ID_KEY, json.dumps(candidate), _utc_now()),
        )
    stored = read_database_id(conn)
    if stored is None:  # pragma: no cover - defensive: table/row vanished
        raise RuntimeError("database_id could not be persisted")
    return stored
