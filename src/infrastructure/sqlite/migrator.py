"""Versioned migration runner with checksums and backup hook.

Implements D03 §34.2 (version/name/checksum/applied_at, pre-migration
backup), D07 §50 (migration inside one transaction, no half-migrated
database) and AC-DB-005 (a newer schema is never touched).
"""

from __future__ import annotations

import sqlite3
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable, Protocol

from infrastructure.sqlite.connection import SchemaTooNewError
from infrastructure.sqlite.schema import Migration
from ports.repositories.database import MigrationRecord

BackupHook = Callable[[int], str]


class MigrationError(RuntimeError):
    """Typed migration failure (startup aborts; the DB stays on its previous
    version). ``code`` is a stable wire-facing identifier (C-15 §1)."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


class MigrationValidationError(Exception):
    """Raised by a migration ``validate`` callback; wrapped by the runner into
    :class:`MigrationError` with ``SOURCE_MIGRATION_FAILED`` (C-15 §1)."""

    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


class ResourceVerifier(Protocol):
    """``IResourceVerifier`` seam (C-15 §1): read-only existence/readability
    check against the managed root. No writes, no network, no Host calls, no
    second SQLite connection."""

    def verify_readable(self, managed_paths: Sequence[str]) -> list[str]:
        """Return the subset of ``managed_paths`` that is missing/unreadable."""
        ...


class _ReadOnlyMigrationView:
    """Connection facade handed to a ``validate`` callback: SELECT/pragma
    queries only. Any DML/DDL/transaction-control attempt raises
    :class:`MigrationValidationError` (C-15 §1: 禁止 commit/rollback/close、
    禁止 DDL/DML; violations are wrapped by the runner)."""

    _FORBIDDEN_PREFIXES = (
        "insert", "update", "delete", "replace", "create", "drop", "alter",
        "begin", "commit", "rollback", "end", "savepoint", "release", "vacuum",
        "attach", "detach", "reindex",
    )

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def _check(self, sql: str) -> None:
        head = sql.lstrip(" \t\r\n(;").split(None, 1)
        keyword = head[0].lower() if head else ""
        if keyword.startswith("pragma"):
            # read-only pragmas only: "PRAGMA foo" (query) is allowed,
            # "PRAGMA foo = value" (write) is not.
            body = sql.lstrip(" \t\r\n;")[6:].lstrip()
            if "=" in body.split("--")[0] or body.lower().startswith(("(", "writable")):
                raise MigrationValidationError(
                    "MIGRATION_CALLBACK_FORBIDDEN", f"pragma write in validate callback: {sql[:60]}"
                )
            return
        if keyword in self._FORBIDDEN_PREFIXES:
            raise MigrationValidationError(
                "MIGRATION_CALLBACK_FORBIDDEN", f"forbidden statement in validate callback: {keyword}"
            )

    def execute(self, sql: str, params: Sequence[object] = ()) -> sqlite3.Cursor:
        self._check(sql)
        return self._conn.execute(sql, params)

    def commit(self) -> None:  # pragma: no cover - guarded by contract
        raise MigrationValidationError("MIGRATION_CALLBACK_FORBIDDEN", "commit in validate callback")

    def rollback(self) -> None:
        raise MigrationValidationError("MIGRATION_CALLBACK_FORBIDDEN", "rollback in validate callback")

    def close(self) -> None:
        raise MigrationValidationError("MIGRATION_CALLBACK_FORBIDDEN", "close in validate callback")


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
        validate: Callable[[sqlite3.Connection], None] | None = None,
    ) -> None:
        self._conn = conn
        self._migrations = tuple(sorted(migrations, key=lambda m: m.schema_version))
        self._backup_provider = backup_provider
        self._validate = validate

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

    @staticmethod
    def _split_statements(sql: str) -> list[str]:
        """Split a migration script into complete statements.

        Uses :func:`sqlite3.complete_statement` so semicolons inside string
        literals or ``BEGIN...END`` trigger bodies (future migrations) do not
        split a statement prematurely.
        """
        statements: list[str] = []
        buffer = ""
        for line in sql.splitlines(keepends=True):
            buffer += line
            if sqlite3.complete_statement(buffer):
                stripped = buffer.strip()
                if stripped:
                    statements.append(stripped)
                buffer = ""
        tail = buffer.strip()
        if tail:
            statements.append(tail)
        return statements

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
        needs_fk_off = migration.schema_version == 5
        try:
            if needs_fk_off:
                conn.execute("PRAGMA foreign_keys = OFF")
            try:
                conn.execute("BEGIN IMMEDIATE")
                for statement in self._split_statements(migration.sql):
                    conn.execute(statement)
                if needs_fk_off:
                    fk_errors = conn.execute("PRAGMA foreign_key_check").fetchall()
                    if fk_errors:
                        raise sqlite3.IntegrityError(
                            f"foreign key check failed on migration {migration.schema_version}: {fk_errors}"
                        )
                if self._validate is not None and migration.schema_version == 7:
                    # C-15 §1: the validate callback is the **v7** pre-commit
                    # validation — it runs inside the v7 transaction, after all
                    # v7 statements ran, before schema_migrations/application_
                    # metadata are written. v1–v6 carry no data relocation and
                    # never invoke it (their databases lack the v7 columns the
                    # assertions read). The callback receives a read-only view;
                    # a MigrationValidationError (or any non-sqlite error)
                    # rolls back and surfaces as a typed MigrationError.
                    try:
                        self._validate(_ReadOnlyMigrationView(conn))  # type: ignore[arg-type]
                    except MigrationValidationError as exc:
                        raise MigrationError("SOURCE_MIGRATION_FAILED", str(exc)) from exc
                    except sqlite3.Error:
                        raise
                    except Exception as exc:  # noqa: BLE001 - frozen contract wording
                        raise MigrationError("SOURCE_MIGRATION_FAILED", str(exc)) from exc
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
            except MigrationError:
                conn.rollback()
                raise
        finally:
            if conn.in_transaction:
                try:
                    conn.rollback()
                except Exception:
                    pass
            if needs_fk_off:
                conn.execute("PRAGMA foreign_keys = ON")


# ----------------------------------------------------------------------
# FEA-09 / C-15 §1: v7 source-storage migration validation.
#
# The runner above owns the callback mechanics; everything below captures
# the pre-migration baseline on a separate read-only connection and turns
# it into the frozen v7 assertions. The callback itself only receives the
# migration transaction connection wrapped in a read-only view.
# ----------------------------------------------------------------------


@dataclass(frozen=True)
class V7MigrationBaseline:
    """In-memory snapshot captured *before* the v7 migration runs.

    Frozen fields per C-15 §1: page id/order, source_hash,
    managed_original_ref, width/height, Lock, manual-data row counts and
    the reader-projection visible page id order. The baseline is passed to
    the callback as an in-memory object; the callback never re-queries the
    Host side.
    """

    page_rows: tuple[tuple[str, int, int, str | None, str | None, int | None, int | None, int], ...]
    #: (page_id, source_order, sort_order, source_hash, managed_original_ref,
    #:  width, height, page_locked) — one row per page, ordered by page_id.
    region_rows: int
    region_revision_rows: int
    complete_page_ids: frozenset[str]
    #: Pages satisfying the legacy **positive-dimension** copy predicate
    #: (soft-deleted rows included, per C-15 v1.1 §1 assertion 1).
    v_artifact_page_ids: tuple[str, ...]
    #: Reader-projection visible order under the old C-05 v1.0 V_artifact
    #: predicate (same t / parent conditions, ordered by chapter + sort).
    expected_managed_v_ids: tuple[str, ...]
    #: C-05 v1.2 managed V expected set in canonical order:
    #: old V_artifact ∪ old positive-dimension copy visible set, deduplicated
    #: and ordered by (chapter_id, sort_order, page_id).
    v_original_paths: tuple[tuple[str, str], ...]
    #: (page_id, managed_path) pairs resolvable for V pages: the original
    #: revision path when present, else pages.managed_original_ref.


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


#: C-15 v1.1 §1 positive-dimension legacy baseline (the v7 backfill predicate).
_LEGACY_COMPLETE_WHERE = (
    "source_hash IS NOT NULL AND managed_original_ref IS NOT NULL"
    " AND width IS NOT NULL AND width > 0"
    " AND height IS NOT NULL AND height > 0"
)

#: Old C-05 v1.0 ``V_artifact`` predicate (judgement SQL from C-05 §3; the
#: ``?`` parameter pins the same instant for the pre/post comparison).
_V_ARTIFACT_SQL = """
SELECT DISTINCT p.page_id
FROM pages p
JOIN chapters c ON c.chapter_id = p.chapter_id
JOIN books b ON b.book_id = c.book_id
JOIN media_artifacts a ON a.page_id = p.page_id
JOIN artifact_revisions r ON r.artifact_revision_id = a.current_revision_id
WHERE p.deleted_at IS NULL AND c.deleted_at IS NULL AND b.deleted_at IS NULL
  AND a.artifact_type IN ('original','thumbnail','clean','translated','render_preview','export')
  AND r.integrity_status = 'valid'
  AND r.created_at <= ?
ORDER BY p.chapter_id, p.sort_order
"""

#: Original-revision path lookup for the V_artifact pages (assertion 5).
_V_ORIGINAL_PATH_SQL = """
SELECT DISTINCT p.page_id, r.managed_path
FROM pages p
JOIN media_artifacts a ON a.page_id = p.page_id
JOIN artifact_revisions r ON r.artifact_revision_id = a.current_revision_id
WHERE p.deleted_at IS NULL
  AND a.artifact_type = 'original'
  AND r.integrity_status = 'valid'
ORDER BY p.page_id
"""

#: New C-05 v1.2 managed-branch V predicate: artifact witness OR
#: copy-original witness (the ``?`` parameters pin the same instant twice).
_V7_MANAGED_V_SQL = """
SELECT DISTINCT p.page_id
FROM pages p
JOIN chapters c ON c.chapter_id = p.chapter_id
JOIN books b ON b.book_id = c.book_id
WHERE p.source_mode = 'managed'
  AND p.deleted_at IS NULL AND c.deleted_at IS NULL AND b.deleted_at IS NULL
  AND (
    EXISTS (SELECT 1 FROM media_artifacts a
            JOIN artifact_revisions r
              ON r.artifact_revision_id = a.current_revision_id
            WHERE a.page_id = p.page_id
              AND a.artifact_type IN ('original','thumbnail','clean','translated','render_preview','export')
              AND r.integrity_status = 'valid'
              AND r.created_at <= ?)
    OR (p.integrity_status = 'complete'
        AND p.source_hash IS NOT NULL AND p.managed_original_ref IS NOT NULL
        AND p.width > 0 AND p.height > 0
        AND p.created_at <= ?)
  )
ORDER BY c.chapter_id, p.sort_order, p.page_id
"""

#: Legacy positive-dimension copy visible set (pre-v7 columns only).
_LEGACY_COPY_VISIBLE_SQL = """
SELECT p.page_id, c.chapter_id, p.sort_order
FROM pages p
JOIN chapters c ON c.chapter_id = p.chapter_id
JOIN books b ON b.book_id = c.book_id
WHERE p.deleted_at IS NULL AND c.deleted_at IS NULL AND b.deleted_at IS NULL
  AND {predicate}
  AND p.created_at <= ?
""".format(predicate=_LEGACY_COMPLETE_WHERE)

#: New C-05 v1.1 managed-branch V predicate (source_mode dispatch added on
#: top of the unchanged V_artifact judgement SQL).
_V7_MANAGED_SQL = _V_ARTIFACT_SQL.replace(
    "WHERE p.deleted_at IS NULL",
    "WHERE p.source_mode = 'managed' AND p.deleted_at IS NULL",
)

_V7_MANAGED_COMPLETE_SQL = """
SELECT page_id FROM pages
WHERE source_mode = 'managed' AND integrity_status = 'complete'
  AND source_hash IS NOT NULL AND managed_original_ref IS NOT NULL
  AND width IS NOT NULL AND width > 0
  AND height IS NOT NULL AND height > 0
"""


def capture_pre_v7_baseline(conn: sqlite3.Connection) -> V7MigrationBaseline:
    """Capture the frozen baseline on a **separate read-only connection**
    before the v7 migration transaction starts (C-15 §1).

    A brand-new database (no ``pages`` table yet) yields an empty baseline —
    every assertion then compares empty sets, which trivially holds for a
    fresh install that never carried legacy rows.
    """

    def _table_exists(name: str) -> bool:
        return conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name = ?", (name,)
        ).fetchone() is not None

    empty = V7MigrationBaseline(
        page_rows=(),
        region_rows=0,
        region_revision_rows=0,
        complete_page_ids=frozenset(),
        v_artifact_page_ids=(),
        expected_managed_v_ids=(),
        v_original_paths=(),
    )
    if not _table_exists("pages"):
        return empty

    def _count(sql: str, table: str) -> int:
        if not _table_exists(table):
            return 0
        row = conn.execute(sql).fetchone()
        return int(row[0]) if row and row[0] is not None else 0

    page_rows = tuple(
        (
            row["page_id"], row["source_order"], row["sort_order"],
            row["source_hash"], row["managed_original_ref"],
            row["width"], row["height"], row["page_locked"],
        )
        for row in conn.execute(
            "SELECT page_id, source_order, sort_order, source_hash,"
            " managed_original_ref, width, height, page_locked"
            " FROM pages ORDER BY page_id"
        ).fetchall()
    )
    complete_ids = frozenset(
        row["page_id"] for row in conn.execute(
            f"SELECT page_id FROM pages WHERE {_LEGACY_COMPLETE_WHERE}"
        ).fetchall()
    )
    now = _utc_now_iso()
    v_ids = tuple(
        row["page_id"] for row in conn.execute(_V_ARTIFACT_SQL, (now,)).fetchall()
    )
    copy_ids = {
        row["page_id"]
        for row in conn.execute(_LEGACY_COPY_VISIBLE_SQL, (now,)).fetchall()
    }
    expected_set = set(v_ids) | copy_ids
    order_rows = conn.execute(
        "SELECT p.page_id, c.chapter_id, p.sort_order FROM pages p"
        " JOIN chapters c ON c.chapter_id = p.chapter_id"
        " JOIN books b ON b.book_id = c.book_id"
    ).fetchall()
    order_map = {
        row["page_id"]: (row["chapter_id"], row["sort_order"], row["page_id"])
        for row in order_rows
    }
    expected_v_ids = tuple(
        sorted(expected_set, key=lambda page_id: order_map.get(
            page_id, ("", 0, page_id)))
    )
    original_paths: dict[str, str] = {}
    for row in conn.execute(_V_ORIGINAL_PATH_SQL).fetchall():
        original_paths[row["page_id"]] = row["managed_path"]
    refs = {
        row["page_id"]: row["managed_original_ref"]
        for row in conn.execute(
            "SELECT page_id, managed_original_ref FROM pages"
            " WHERE managed_original_ref IS NOT NULL"
        ).fetchall()
    }
    resolved = tuple(
        (page_id, original_paths.get(page_id) or refs.get(page_id) or "")
        for page_id in expected_v_ids
    )
    return V7MigrationBaseline(
        page_rows=page_rows,
        region_rows=_count("SELECT COUNT(*) FROM regions", "regions"),
        region_revision_rows=_count("SELECT COUNT(*) FROM region_revisions", "region_revisions"),
        complete_page_ids=complete_ids,
        v_artifact_page_ids=v_ids,
        expected_managed_v_ids=expected_v_ids,
        v_original_paths=resolved,
    )


def make_v7_validator(
    baseline: V7MigrationBaseline,
    resource_verifier: ResourceVerifier | None = None,
    now: str | None = None,
) -> Callable[[sqlite3.Connection], None]:
    """Build the frozen v7 pre-commit validation callback (C-15 §1
    assertions 1–5). Runs inside the migration transaction on a read-only
    view; resource verification goes exclusively through the injected
    ``IResourceVerifier`` seam."""

    moment = now or _utc_now_iso()

    def _validate(conn: sqlite3.Connection) -> None:
        # Assertion 1: legacy _COMPLETE_PAGE_WHERE set (soft-deleted rows
        # included) equals the post-migration managed is_complete_page set.
        managed_complete = {
            row["page_id"] for row in conn.execute(_V7_MANAGED_COMPLETE_SQL).fetchall()
        }
        legacy_complete = set(baseline.complete_page_ids)
        if managed_complete != legacy_complete:
            missing = sorted(legacy_complete - managed_complete)
            extra = sorted(managed_complete - legacy_complete)
            raise MigrationValidationError(
                "V7_COMPLETE_SET_DIVERGED",
                f"legacy complete set != managed is_complete_page set;"
                f" missing={missing[:10]} extra={extra[:10]}",
            )

        # Assertion 2 (C-15 v1.1): managed V v1.2 (artifact ∪ copy witness)
        # equals the frozen union baseline in canonical order.
        new_v = tuple(
            row["page_id"]
            for row in conn.execute(_V7_MANAGED_V_SQL, (moment, moment)).fetchall()
        )
        if new_v != baseline.expected_managed_v_ids:
            raise MigrationValidationError(
                "V7_MANAGED_V_DIVERGED",
                f"managed V set diverged from expected union baseline;"
                f" baseline={list(baseline.expected_managed_v_ids)[:10]}"
                f" actual={list(new_v)[:10]}",
            )

        # Assertion 2b (C-15 v1.1): the same transaction's production read
        # paths (get/list/pure projection) must agree with the expected union;
        # no second connection, no publish/resolve, fixed moment.
        from infrastructure.sqlite.library import SqliteLibraryRepository

        repository = SqliteLibraryRepository(conn)
        chapter_ids = [
            row["chapter_id"]
            for row in conn.execute(
                "SELECT chapter_id FROM chapters ORDER BY chapter_id"
            ).fetchall()
        ]
        page_objects = [
            page for chapter_id in chapter_ids
            for page in repository.list_pages(chapter_id, at=moment)
        ]
        ordered_ids = tuple(
            page.page_id
            for page in sorted(
                page_objects,
                key=lambda page: (page.chapter_id, page.sort_order, page.page_id),
            )
        )
        if ordered_ids != baseline.expected_managed_v_ids:
            raise MigrationValidationError(
                "V7_PROJECTION_DIVERGED",
                "production list path disagreed with expected managed V set",
            )
        for chapter_id in chapter_ids:
            repository.list_page_views(chapter_id, at=moment)
        for page_id in baseline.expected_managed_v_ids:
            if repository.get_page(page_id, at=moment) is None:
                raise MigrationValidationError(
                    "V7_PROJECTION_DIVERGED",
                    f"production get path dropped visible page {page_id}",
                )

        # Assertion 3: backfill touched exactly the legacy complete set —
        # half-written/placeholder rows stay incomplete, V-invisible legacy
        # complete rows stay complete (not flipped), nothing is promoted.
        statuses = {
            row["page_id"]: row["integrity_status"]
            for row in conn.execute(
                "SELECT page_id, integrity_status FROM pages WHERE source_mode='managed'"
            ).fetchall()
        }
        for page_id, status in statuses.items():
            expected = "complete" if page_id in legacy_complete else "incomplete"
            if status != expected:
                raise MigrationValidationError(
                    "V7_BACKFILL_MISMATCH",
                    f"page {page_id} integrity_status={status} expected={expected}",
                )
        soft_deleted_complete = {
            row["page_id"]
            for row in conn.execute(
                "SELECT page_id FROM pages"
                " WHERE integrity_status='complete' AND deleted_at IS NOT NULL"
            ).fetchall()
        }
        legacy_soft_deleted_complete = {
            row["page_id"]
            for row in conn.execute(
                f"SELECT page_id FROM pages WHERE deleted_at IS NOT NULL"
                f" AND {_LEGACY_COMPLETE_WHERE}"
            ).fetchall()
        }
        if soft_deleted_complete != legacy_soft_deleted_complete:
            raise MigrationValidationError(
                "V7_SOFT_DELETED_COMPLETE_DIVERGED",
                "soft-deleted complete rows diverged from legacy set",
            )

        # Assertion 4: per-page column conservation + manual-data counts.
        current_rows = tuple(
            (
                row["page_id"], row["source_order"], row["sort_order"],
                row["source_hash"], row["managed_original_ref"],
                row["width"], row["height"], row["page_locked"],
            )
            for row in conn.execute(
                "SELECT page_id, source_order, sort_order, source_hash,"
                " managed_original_ref, width, height, page_locked"
                " FROM pages WHERE source_mode='managed' ORDER BY page_id"
            ).fetchall()
        )
        if current_rows != baseline.page_rows:
            raise MigrationValidationError(
                "V7_PAGE_COLUMNS_DIVERGED",
                "managed page columns (order/hash/ref/dimensions/lock) diverged from baseline",
            )
        for sql, expected, label in (
            ("SELECT COUNT(*) FROM regions", baseline.region_rows, "regions"),
            ("SELECT COUNT(*) FROM region_revisions", baseline.region_revision_rows, "region_revisions"),
        ):
            row = conn.execute(sql).fetchone()
            actual = int(row[0]) if row and row[0] is not None else 0
            if actual != expected:
                raise MigrationValidationError(
                    "V7_MANUAL_DATA_DIVERGED",
                    f"{label} row count {actual} != baseline {expected}",
                )

        # Assertion 5: legacy managed resource readability through the
        # injected IResourceVerifier seam (read-only; no Host calls).
        if resource_verifier is None:
            if baseline.v_original_paths:
                raise MigrationValidationError(
                    "SOURCE_MIGRATION_RESOURCE_UNVERIFIED",
                    "non-empty managed V resource set requires an injected resource verifier",
                )
            return
        unverifiable: list[str] = []
        to_check: list[str] = []
        for page_id, path in baseline.v_original_paths:
            if not path:
                unverifiable.append(page_id)
            else:
                to_check.append(path)
        missing = resource_verifier.verify_readable(to_check) if to_check else []
        missing_set = set(missing)
        if missing or unverifiable:
            missing_pages = sorted(
                page_id
                for page_id, path in baseline.v_original_paths
                if (not path) or (path and path in missing_set)
            )
            raise MigrationValidationError(
                "SOURCE_MIGRATION_RESOURCE_UNVERIFIED",
                f"pages={missing_pages[:10]} missing_paths={len(missing)}"
                f" unresolvable={len(unverifiable)}",
            )

    return _validate

