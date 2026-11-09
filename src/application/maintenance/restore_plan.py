"""Merge-restore planning and application (FEA-13-RESTORE-4).

Implements the conflict model fixed by
``doc/reviews/ADJ-2026-11-09-FEA13-RESTORE-MODEL.md``:

* revision entities (``artifact_revisions`` / ``region_revisions``) and plain
  metadata rows (``books``/``chapters``/``pages``/...) are compared per primary
  key against the backup database;
* ``add``      - exists only in the backup -> safe to apply;
* ``noop``     - both sides identical -> nothing to do;
* ``conflict`` - both sides differ -> defer (keep the live value), list it;
* ``keep``     - exists only live -> never deleted by a restore.

The default mode applies ``add`` items only; ``UseBackup`` entries are applied
only after the live value has been preserved as a restorable copy. Planning is
strictly read-only: it only ``ATTACH``es the backup database and selects from
it, so the live database, the managed root and the package bytes are untouched.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
from dataclasses import dataclass, field
from pathlib import Path

#: Insertion order respects the schema's foreign keys.
RESTORE_TABLES = (
    ("books", "book_id"),
    ("chapters", "chapter_id"),
    ("pages", "page_id"),
    ("media_artifacts", "artifact_id"),
    ("artifact_revisions", "artifact_revision_id"),
    ("regions", "region_id"),
    ("region_revisions", "region_revision_id"),
)

ACTION_ADD = "add"
ACTION_NOOP = "noop"
ACTION_CONFLICT = "conflict"
ACTION_KEEP = "keep"


@dataclass(frozen=True)
class RestoreItem:
    kind: str  # "row" | "managed"
    table: str
    key: str
    action: str
    detail: dict = field(default_factory=dict)

    def as_dict(self) -> dict:
        return {
            "kind": self.kind,
            "table": self.table,
            "key": self.key,
            "action": self.action,
            "detail": self.detail,
        }


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _table_columns(conn, schema: str, table: str) -> list[str]:
    return [
        row[1]
        for row in conn.execute(f"PRAGMA {schema}.table_info({table})").fetchall()
    ]


def _fetch_rows(conn, schema: str, table: str) -> dict[str, tuple]:
    columns = _table_columns(conn, schema, table)
    rows = conn.execute(f"SELECT * FROM {schema}.{table}").fetchall()
    key_column = dict(RESTORE_TABLES)[table]
    key_index = columns.index(key_column)
    result: dict[str, tuple] = {}
    for row in rows:
        values = tuple(row)
        result[str(values[key_index])] = values
    return result


def plan_rows(conn, backup_db: Path | str) -> list[RestoreItem]:
    """Compare every covered table; strictly read-only on the live database."""
    conn.execute("ATTACH DATABASE ? AS restore_src", (str(backup_db),))
    try:
        items: list[RestoreItem] = []
        for table, _key in RESTORE_TABLES:
            live_rows = _fetch_rows(conn, "main", table)
            backup_rows = _fetch_rows(conn, "restore_src", table)
            for key, backup_row in backup_rows.items():
                live_row = live_rows.get(key)
                if live_row is None:
                    items.append(
                        RestoreItem("row", table, key, ACTION_ADD, {"source": "backup"})
                    )
                elif tuple(live_row) == tuple(backup_row):
                    items.append(RestoreItem("row", table, key, ACTION_NOOP))
                else:
                    items.append(RestoreItem("row", table, key, ACTION_CONFLICT))
            for key in live_rows:
                if key not in backup_rows:
                    items.append(RestoreItem("row", table, key, ACTION_KEEP))
        return items
    finally:
        conn.execute("DETACH DATABASE restore_src")


def plan_managed(
    managed_root: Path,
    backup_entries: dict[str, str],
) -> list[RestoreItem]:
    """Compare shipped managed/original files against the live managed root."""
    items: list[RestoreItem] = []
    for relative, digest in sorted(backup_entries.items()):
        live = Path(managed_root) / Path(relative)
        if not live.is_file():
            items.append(
                RestoreItem("managed", "managed", relative, ACTION_ADD, {"sha256": digest})
            )
        elif sha256_file(live) == digest:
            items.append(RestoreItem("managed", "managed", relative, ACTION_NOOP))
        else:
            items.append(RestoreItem("managed", "managed", relative, ACTION_CONFLICT))
    return items


def summarize(items: list[RestoreItem]) -> dict:
    summary = {ACTION_ADD: 0, ACTION_NOOP: 0, ACTION_CONFLICT: 0, ACTION_KEEP: 0}
    for item in items:
        summary[item.action] = summary.get(item.action, 0) + 1
    return summary


def plan_restore(
    conn,
    backup_db: Path | str,
    *,
    managed_root: Path | None = None,
    backup_entries: dict[str, str] | None = None,
) -> dict:
    items = plan_rows(conn, backup_db)
    if managed_root is not None and backup_entries:
        items.extend(plan_managed(managed_root, backup_entries))
    return {
        "items": [item.as_dict() for item in items],
        "summary": summarize(items),
        "mode": "defer",
    }


def _preserve_row(conn, undo_root: Path, table: str, key: str) -> Path:
    """Copy the live row into the undo area before overwriting it."""
    columns = _table_columns(conn, "main", table)
    key_column = dict(RESTORE_TABLES)[table]
    row = conn.execute(
        f"SELECT * FROM main.{table} WHERE {key_column} = ?", (key,)
    ).fetchone()
    payload = dict(zip(columns, tuple(row))) if row is not None else None
    target = Path(undo_root) / "rows" / table / f"{key}.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, indent=2))
        handle.flush()
        os.fsync(handle.fileno())
    return target


def _insert_row(conn, table: str, key: str) -> None:
    key_column = dict(RESTORE_TABLES)[table]
    columns = _table_columns(conn, "main", table)
    placeholders = ", ".join("?" for _ in columns)
    column_sql = ", ".join(columns)
    conn.execute(
        f"INSERT INTO main.{table} ({column_sql})"
        f" SELECT {column_sql} FROM restore_src.{table} WHERE {key_column} = ?",
        (key,),
    )


def _replace_row(conn, table: str, key: str) -> None:
    key_column = dict(RESTORE_TABLES)[table]
    live_columns = _table_columns(conn, "main", table)
    backup_columns = _table_columns(conn, "restore_src", table)
    row = conn.execute(
        f"SELECT * FROM restore_src.{table} WHERE {key_column} = ?", (key,)
    ).fetchone()
    if row is None:  # pragma: no cover - the plan was built from this database
        raise RuntimeError(f"backup row disappeared: {table}/{key}")
    # R4-007: map by column NAME so a schema that gained/lost columns between
    # the package and the live library can never shift values into the wrong
    # column.
    source = dict(zip(backup_columns, tuple(row)))
    assignments = ", ".join(
        f"{column} = ?" for column in live_columns if column != key_column
    )
    params = tuple(
        source[column] for column in live_columns if column != key_column
    ) + (key,)
    conn.execute(
        f"UPDATE main.{table} SET {assignments} WHERE {key_column} = ?", params
    )


def apply_restore(
    conn,
    backup_db: Path | str,
    items: list[dict] | list[RestoreItem],
    *,
    mode: str = "defer",
    use_backup_keys: set[tuple[str, str]] | None = None,
    undo_root: Path | None = None,
    managed_root: Path | None = None,
    staged_root: Path | None = None,
) -> dict:
    """Apply a plan. ``mode="defer"`` applies adds; ``UseBackup`` keys are
    applied only after their live value has been preserved.
    """
    if mode not in {"defer", "use_backup"}:
        raise ValueError(f"unsupported restore mode: {mode}")
    use_backup_keys = use_backup_keys or set()
    normalized = [
        item if isinstance(item, RestoreItem) else RestoreItem(**item) for item in items
    ]
    applied: list[dict] = []
    deferred: list[dict] = []
    failed: list[dict] = []
    conn.execute("ATTACH DATABASE ? AS restore_src", (str(backup_db),))
    try:
        conn.execute("BEGIN IMMEDIATE")
        try:
            for item in normalized:
                selected = mode == "use_backup" and (
                    item.table,
                    item.key,
                ) in use_backup_keys
                if item.kind == "row":
                    if item.action == ACTION_ADD or (
                        selected and item.action == ACTION_CONFLICT
                    ):
                        try:
                            if selected and item.action == ACTION_CONFLICT:
                                if undo_root is None:
                                    raise RuntimeError("undo area is required for UseBackup")
                                _preserve_row(conn, undo_root, item.table, item.key)
                                _replace_row(conn, item.table, item.key)
                            else:
                                _insert_row(conn, item.table, item.key)
                            applied.append(item.as_dict())
                        except Exception as error:  # noqa: BLE001 - per-item isolation
                            failed.append(
                                {**item.as_dict(), "error": str(error)}
                            )
                    else:
                        deferred.append(item.as_dict())
                else:
                    if item.action == ACTION_ADD or (
                        selected and item.action == ACTION_CONFLICT
                    ):
                        deferred.append(
                            {**item.as_dict(), "reason": "managed files need staging"}
                        )
                    else:
                        deferred.append(item.as_dict())
            conn.execute("COMMIT")
        except Exception:
            conn.execute("ROLLBACK")
            raise
    finally:
        conn.execute("DETACH DATABASE restore_src")
    return {
        "mode": mode,
        "applied": applied,
        "deferred": deferred,
        "failed": failed,
        "undo_root": str(undo_root) if undo_root is not None else None,
        "managed_root": str(managed_root) if managed_root is not None else None,
        "staged_root": str(staged_root) if staged_root is not None else None,
    }
