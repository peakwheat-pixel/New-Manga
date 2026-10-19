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

M2-DERIVED-GC-2 additions (design doc/contracts/M2_DERIVED_PREVIEW_GC_DESIGN.md,
both auxiliary tables live ONLY in this dedicated catalog -- never the product
schema):

- ``preview_lifecycle``: one origin row per Core-registered preview key
  (producer_root / artifact_id / artifact_revision_id / managed_rel_path /
  retired). The production Core is the ONLY authority that creates origin
  rows (one transaction with the catalog row, ``retired=0``); the channel
  may only flip ``retired`` on an already-registered own row
  (:meth:`ResourceCatalogStore.mark_preview_retired`); every loader
  upsert/remove invalidates the origin eligibility of the key instead.
- ``preview_namespace``: the single-row binding of the catalog to one
  derived deletion domain (protocol version + canonical roots + volume/file
  identities). A file-backed store serves business access ONLY under a
  verified shared namespace lease (design §2.3); an unbound catalog is a
  typed refusal, never an un-leased write channel. ``initialize_namespace``
  is the frozen narrow first-bind entry: it accepts only a brand-new/empty,
  self-owned catalog and registers the binding -- it never migrates unknown
  history and never enables any sweep by itself.

Imports stay on the standard library only so the sidecar entry keeps its
import isolation (M2-RC2 F-05).
"""

from __future__ import annotations

import re
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
from infrastructure.resource_channel.handle_resolver import (
    NamespaceBinding,
    PreviewNamespaceLease,
    acquire_shared_lease,
    close_lock_handle,
    namespace_unavailable,
    open_exclusive_lock_for_initialize,
    read_lock_content_if_any,
    resolve_namespace_identity,
    write_lock_content,
)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS resource_catalog (
    resource_id TEXT PRIMARY KEY,
    scope_class TEXT NOT NULL,
    rel_path    TEXT NOT NULL
)
"""

_PREVIEW_LIFECYCLE_SCHEMA = """
CREATE TABLE IF NOT EXISTS preview_lifecycle (
    resource_id          TEXT PRIMARY KEY,
    producer_root        TEXT NOT NULL,
    artifact_id          TEXT NOT NULL,
    artifact_revision_id TEXT NOT NULL,
    managed_rel_path     TEXT NOT NULL,
    retired              INTEGER NOT NULL DEFAULT 0
)
"""

_PREVIEW_NAMESPACE_SCHEMA = """
CREATE TABLE IF NOT EXISTS preview_namespace (
    singleton               INTEGER PRIMARY KEY CHECK (singleton = 1),
    protocol_version        INTEGER NOT NULL,
    derived_root            TEXT NOT NULL,
    derived_identity_volume INTEGER NOT NULL,
    derived_identity_index  INTEGER NOT NULL,
    catalog_root            TEXT NOT NULL,
    catalog_identity_volume INTEGER NOT NULL,
    catalog_identity_index  INTEGER NOT NULL
)
"""

#: Codex r8 F-01: an adopted preview_namespace table must be indistinguishable
#: from one this module creates. sqlite stores the DDL VERBATIM minus the
#: leading IF NOT EXISTS, so comparing lowercased text with whitespace FOLDED
#: to single spaces (token boundaries preserved) against this canonical form
#: is SEMANTIC: equal folded text means an equal token stream means equal DDL
#: semantics.
#:
#: Two normalization pitfalls are closed by construction:
#: - stripping whitespace ENTIRELY merges token boundaries (`TEXT NOT NULL`
#:   folds to the same text as the legal multi-word type name `TEXTN
#:   OTNULL`, which carries no NOT NULL constraint, Codex r9 F-01) -- so
#:   whitespace is FOLDED, not stripped;
#: - the fold set is EXACTLY the five characters sqlite's tokenizer treats
#:   as separators (0x09, 0x0A, 0x0C, 0x0D, 0x20). Python's str.split()
#:   would also fold Unicode whitespace such as NBSP (U+00A0), but sqlite
#:   treats every byte >= 0x80 as an identifier character -- `NOT NULL`
#:   is one identifier, not the NOT NULL constraint (Codex r10 F-01).
#:   Callers must refuse non-ASCII DDL before comparing (the canonical text
#:   is pure ASCII, and an ASCII-only lower() has no Unicode traps).
_SQLITE_DDL_WS = re.compile("[\x09\x0a\x0c\x0d ]+")
_NORMALIZED_NAMESPACE_SCHEMA = _SQLITE_DDL_WS.sub(
    " ", _PREVIEW_NAMESPACE_SCHEMA.replace("IF NOT EXISTS", "")
).strip().lower()

_MEMORY_TARGETS = (":memory:",)

#: The deterministic page-original keys are managed-original publishes and
#: never carry a recycable preview origin (design §2.1: the origin resource_id
#: is the random preview key only).
PREVIEW_ORIGIN_SCOPE = "derived-read-only"


class CatalogEntry(NamedTuple):
    resource_id: str
    scope_class: str
    rel_path: str


class PreviewOrigin(NamedTuple):
    """Verified source binding for one preview publish (Core-only input)."""

    producer_root: str
    artifact_id: str
    artifact_revision_id: str
    managed_rel_path: str


class RetiredPreviewCandidate(NamedTuple):
    """One retired preview row pair that passed the catalog-side shape gate."""

    resource_id: str
    producer_root: str
    artifact_id: str
    artifact_revision_id: str
    managed_rel_path: str


def _is_memory(db_path: Path | str) -> bool:
    return isinstance(db_path, str) and db_path in _MEMORY_TARGETS


def _rw_uri(db_path: Path) -> str:
    # §7: stdlib as_uri() percent-escaping only; frozen query params appended.
    return db_path.resolve().as_uri() + "?mode=rw"


def _ro_uri(db_path: Path) -> str:
    """Read-only WITHOUT immutable: sees un-checkpointed WAL rows (the
    authoritative initialize-claim check must not miss them)."""
    return db_path.resolve().as_uri() + "?mode=ro"


def _ro_immutable_uri(db_path: Path) -> str:
    return db_path.resolve().as_uri() + "?mode=ro&immutable=1"


def _read_namespace_row(connection: sqlite3.Connection) -> Optional[NamespaceBinding]:
    try:
        row = connection.execute(
            "SELECT protocol_version, derived_root, derived_identity_volume,"
            " derived_identity_index, catalog_root, catalog_identity_volume,"
            " catalog_identity_index FROM preview_namespace WHERE singleton = 1"
        ).fetchone()
    except sqlite3.OperationalError:
        return None  # no preview_namespace table: no binding row
    except sqlite3.DatabaseError as error:
        # "file is not a database" and friends: unusable, never "unbound"
        raise namespace_unavailable(f"catalog file unusable: {error}") from error
    if row is None:
        return None
    return NamespaceBinding(
        protocol_version=int(row[0]),
        derived_root=str(row[1]),
        derived_identity=(int(row[2]), int(row[3])),
        catalog_root=str(row[4]),
        catalog_identity=(int(row[5]), int(row[6])),
    )


def initialize_namespace(catalog_db: Path | str, derived_root: Path | str) -> NamespaceBinding:
    """The frozen narrow first-bind initializer (design §2.3).

    Accepts ONLY a brand-new or empty, self-owned catalog together with a
    verified self-owned derived root (test assets already inside the root are
    kept). An existing catalog with resource rows, origin rows or a binding
    -- or an unknown-history database -- is refused, never auto-migrated.
    The function registers the namespace binding only: it opens no GC, mints
    no origin rows and deletes no bytes.
    """

    db_path = Path(catalog_db)
    _preflight_initialize_target(db_path)
    lock_handle, derived_str, derived_identity = open_exclusive_lock_for_initialize(derived_root)
    try:
        existing = read_lock_content_if_any(lock_handle)
        if existing is not None:
            raise namespace_unavailable(
                "namespace lock already bound; re-initialization would overwrite a binding"
            )
        # Authoritative re-check UNDER the exclusive lock (Codex r1 F-01/r2):
        # a PLAIN read-only connection -- NOT immutable -- so rows sitting in
        # an un-checkpointed WAL are visible (design §7 forbids initializing
        # from an immutable-miss). The pre-lock immutable probe stays a
        # fast-fail only; this is the claim decision.
        if db_path.exists():
            recheck = sqlite3.connect(_ro_uri(db_path), uri=True)
            try:
                _assert_catalog_claimable(recheck)
            finally:
                recheck.close()
        db_path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(str(db_path), check_same_thread=False)
        try:
            connection.execute(_SCHEMA)
            connection.execute(_PREVIEW_LIFECYCLE_SCHEMA)
            connection.execute(_PREVIEW_NAMESPACE_SCHEMA)
            connection.commit()
        finally:
            connection.close()
        catalog_str, catalog_identity = resolve_namespace_identity(db_path)
        binding = NamespaceBinding(
            protocol_version=1,
            derived_root=derived_str,
            derived_identity=derived_identity,
            catalog_root=catalog_str,
            catalog_identity=catalog_identity,
        )
        connection = sqlite3.connect(_rw_uri(db_path), uri=True, check_same_thread=False)
        try:
            connection.execute(
                "INSERT INTO preview_namespace(singleton, protocol_version, derived_root,"
                " derived_identity_volume, derived_identity_index, catalog_root,"
                " catalog_identity_volume, catalog_identity_index)"
                " VALUES(1, ?, ?, ?, ?, ?, ?, ?)",
                (
                    binding.protocol_version,
                    binding.derived_root,
                    binding.derived_identity[0],
                    binding.derived_identity[1],
                    binding.catalog_root,
                    binding.catalog_identity[0],
                    binding.catalog_identity[1],
                ),
            )
            connection.commit()
        finally:
            connection.close()
        write_lock_content(lock_handle, binding)
        return binding
    finally:
        close_lock_handle(lock_handle)


def restore_namespace_lock(catalog_db: Path | str, derived_root: Path | str) -> bool:
    """Restore a missing or unreadable lock only from its existing catalog binding.

    An unbound catalog returns ``False`` for the existing narrow initializer;
    a bound catalog is copied back only after the exclusive lock and both
    filesystem identities are verified.
    """
    db_path = Path(catalog_db)
    lock_handle, derived_str, derived_identity = open_exclusive_lock_for_initialize(derived_root)
    try:
        existing = read_lock_content_if_any(lock_handle)
        catalog_str, catalog_identity = resolve_namespace_identity(db_path)
        try:
            connection = sqlite3.connect(_ro_uri(db_path), uri=True)
        except sqlite3.Error as error:
            raise namespace_unavailable(f"catalog probe failed: {error}") from error
        try:
            binding = _read_namespace_row(connection)
            if binding is None:
                if existing is not None:
                    raise namespace_unavailable(
                        "namespace lock is bound but catalog binding is missing"
                    )
                return False
            (row_count,) = connection.execute(
                "SELECT COUNT(*) FROM preview_namespace"
            ).fetchone()
            (table_sql,) = connection.execute(
                "SELECT sql FROM sqlite_master WHERE type='table' AND name='preview_namespace'"
            ).fetchone()
        except (sqlite3.Error, ValueError, TypeError, IndexError) as error:
            raise namespace_unavailable(f"catalog namespace binding unusable: {error}") from error
        finally:
            connection.close()
        if (
            row_count != 1
            or table_sql is None
            or not table_sql.isascii()
            or _SQLITE_DDL_WS.sub(" ", table_sql).strip().lower()
            != _NORMALIZED_NAMESPACE_SCHEMA
        ):
            raise namespace_unavailable("catalog namespace binding is not canonical")
        _verify_catalog_binding(
            binding, derived_str, derived_identity, catalog_str, catalog_identity
        )
        if existing is not None:
            if existing != binding:
                raise namespace_unavailable("namespace lock and catalog bindings differ")
            return True
        write_lock_content(lock_handle, binding)
        return True
    finally:
        close_lock_handle(lock_handle)


def _verify_catalog_binding(
    binding: NamespaceBinding,
    derived_root: str,
    derived_identity: tuple[int, int],
    catalog_root: str,
    catalog_identity: tuple[int, int],
) -> None:
    if (
        binding.protocol_version != 1
        or binding.derived_root != derived_root
        or binding.derived_identity != derived_identity
        or binding.catalog_root != catalog_root
        or binding.catalog_identity != catalog_identity
    ):
        raise namespace_unavailable("namespace binding identity mismatch")


_KNOWN_CATALOG_TABLES = {"resource_catalog", "preview_lifecycle", "preview_namespace"}

#: The exact column shapes the initializer is allowed to adopt. Anything
#: else -- including an empty table with a foreign schema -- is unknown
#: history and is refused (Codex r3 F-01).
#: (column name, PRAGMA table_info pk position) in table order -- the pk
#: value 0 means "not the primary key", 1..N the position in the primary
#: key. The runtime leans on these keys: catalog upsert uses
#: ON CONFLICT(resource_id), the lifecycle mark/candidates key on
#: resource_id, and the namespace row on the singleton CHECK primary key
#: (Codex r4 F-01: names alone would let a key-less foreign table be
#: adopted and break every write).
_EXPECTED_LAYOUT = {
    "resource_catalog": (
        ("resource_id", 1), ("scope_class", 0), ("rel_path", 0),
    ),
    "preview_lifecycle": (
        ("resource_id", 1), ("producer_root", 0), ("artifact_id", 0),
        ("artifact_revision_id", 0), ("managed_rel_path", 0), ("retired", 0),
    ),
    "preview_namespace": (
        ("singleton", 1), ("protocol_version", 0), ("derived_root", 0),
        ("derived_identity_volume", 0), ("derived_identity_index", 0),
        ("catalog_root", 0), ("catalog_identity_volume", 0),
        ("catalog_identity_index", 0),
    ),
}


def _assert_catalog_claimable(connection: sqlite3.Connection) -> None:
    """Refuse anything that is not a brand-new or empty self-owned catalog.

    Each table is probed INDEPENDENTLY so a missing ``preview_lifecycle``
    table can never zero out the resource count (Codex r1 F-01): an
    old-schema catalog that carries resource rows predates the lifecycle
    schema and is UNKNOWN history -- never claimed. An unknown/corrupt
    database file (sqlite3.DatabaseError) is likewise a refusal.

    Codex r2 F-01 additions: (a) ANY user table outside the known set is an
    unknown schema -> refusal (history data may live in tables this version
    does not know); (b) the AUTHORITATIVE check must run on a connection
    that sees un-checkpointed WAL rows -- the pre-lock probe may legally use
    ``immutable=1`` as a fast-fail only, because an immutable read can
    silently miss rows sitting in the WAL (design §7 forbids initializing
    from an immutable-miss)."""

    if _read_namespace_row(connection) is not None:
        raise namespace_unavailable("catalog already carries a namespace binding")
    try:
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            ).fetchall()
        }
        unknown = {
            name
            for name in tables
            if name not in _KNOWN_CATALOG_TABLES and not name.startswith("sqlite_")
        }
        if unknown:
            raise namespace_unavailable(
                "catalog carries unknown tables (unknown schema/history):"
                f" {sorted(unknown)}"
            )
        for known_table, expected_layout in _EXPECTED_LAYOUT.items():
            if known_table not in tables:
                continue
            actual = tuple(
                (row[1], int(row[5]))
                for row in connection.execute(
                    f"PRAGMA table_info({known_table})"
                ).fetchall()
            )
            if actual != expected_layout:
                raise namespace_unavailable(
                    f"table {known_table} has a foreign layout"
                    f" (expected name+pk {expected_layout}, found {actual})"
                )
        (count,) = connection.execute("SELECT COUNT(*) FROM resource_catalog").fetchone()
        origin_count = 0
        if "preview_lifecycle" in tables:
            (origin_count,) = connection.execute(
                "SELECT COUNT(*) FROM preview_lifecycle"
            ).fetchone()
        elif count:
            raise namespace_unavailable(
                "catalog carries resource rows but predates the lifecycle schema;"
                " unknown history is never claimed"
            )
    except sqlite3.OperationalError as error:
        raise namespace_unavailable(f"catalog probe failed: {error}") from error
    except sqlite3.DatabaseError as error:
        raise namespace_unavailable(f"catalog file unusable: {error}") from error
    if count or origin_count:
        raise namespace_unavailable(
            "catalog already carries resource/origin rows; unknown history is never claimed"
        )
    # The namespace table gets TWO extra guards (Codex r5 F-01): ANY
    # pre-existing row is unknown history (the binding query reads only
    # singleton=1 and would not even SEE a foreign singleton=2 row), and
    # the adopted table must match the canonical namespace schema exactly
    # (Codex r8 F-01) -- an empty look-alike with different constraint
    # semantics would later accept rows the real schema forbids.
    if "preview_namespace" in tables:
        (namespace_rows,) = connection.execute(
            "SELECT COUNT(*) FROM preview_namespace"
        ).fetchone()
        if namespace_rows:
            raise namespace_unavailable(
                "preview_namespace already carries rows; unknown history is never claimed"
            )
        (table_sql,) = connection.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name='preview_namespace'"
        ).fetchone()
        # Codex r7/r8 F-01: any weaker predicate (a "CHECK" substring, an
        # exact-substring match, behavioral probing of selected values) is
        # evadeable -- a comment can smuggle the literal past a text scan
        # while CHECK(singleton IN (1, 3)) passes a singleton=2 probe yet
        # still allows 3. The only non-evasive test is CANONICAL SCHEMA
        # EQUALITY: sqlite stores the DDL verbatim (minus IF NOT EXISTS), so
        # requiring normalized full-text equality with this module's own
        # schema accepts exactly the tables this module could have created
        # and refuses every construction with different semantics.
        if (
            table_sql is None
            or not table_sql.isascii()
            or _SQLITE_DDL_WS.sub(" ", table_sql).strip().lower()
            != _NORMALIZED_NAMESPACE_SCHEMA
        ):
            raise namespace_unavailable(
                "preview_namespace table does not match the canonical"
                " namespace schema; unknown history is never claimed"
            )


def _preflight_initialize_target(db_path: Path) -> None:
    """Pre-lock probe of the initialize target (fail-closed on unreadable
    files); the authoritative re-check runs again under the exclusive lock
    in :func:`initialize_namespace` before any table is created."""
    if not db_path.exists():
        return
    try:
        connection = sqlite3.connect(_ro_immutable_uri(db_path), uri=True)
    except sqlite3.Error as error:
        raise namespace_unavailable(f"catalog probe failed: {error}") from error
    try:
        _assert_catalog_claimable(connection)
    finally:
        connection.close()


class ResourceCatalogStore:
    """SQLite-backed catalog authority (single connection, mutex-serialised).

    ``:memory:`` keeps the legacy isolation-experiment behaviour (all tables,
    no namespace row, no lease, no GC authority). A file-backed store is a
    namespace participant: it either borrows the caller's lease (production
    Core assembly) or runs the frozen bootstrap (refuse reparse -> fix the
    catalog file identity -> read-only immutable hint connection -> shared
    lease on the hinted derived root -> business-connection re-verification)
    before any business access. Unbound/unknown catalogs are a typed
    refusal; a missing lease can never degrade into an un-leased connection.
    """

    def __init__(
        self,
        db_path: Path | str,
        *,
        namespace_lease: PreviewNamespaceLease | None = None,
    ) -> None:
        self._lock = threading.Lock()
        self._db_path: Path | None = None
        self._namespace_lease: PreviewNamespaceLease | None = None
        self._owns_lease = False
        if _is_memory(db_path):
            self._connection = sqlite3.connect(":memory:", check_same_thread=False)
            self._connection.row_factory = sqlite3.Row
            with self._lock:
                self._connection.execute(_SCHEMA)
                self._connection.execute(_PREVIEW_LIFECYCLE_SCHEMA)
                self._connection.execute(_PREVIEW_NAMESPACE_SCHEMA)
                self._connection.commit()
            return

        resolved = Path(db_path)
        self._db_path = resolved
        if namespace_lease is not None:
            self._namespace_lease = namespace_lease
            self._owns_lease = False
        else:
            self._namespace_lease = _bootstrap_namespace_lease(resolved)
            self._owns_lease = True
        self._connection = self._open_business_connection()
        with self._lock:
            self._connection.execute(_SCHEMA)
            self._connection.execute(_PREVIEW_LIFECYCLE_SCHEMA)
            self._connection.commit()

    # ------------------------------------------------------------ namespace

    def _open_business_connection(self) -> sqlite3.Connection:
        db_path = self._db_path
        assert db_path is not None
        if self._namespace_lease is None:
            raise namespace_unavailable("store opened without a namespace lease")
        try:
            connection = sqlite3.connect(_rw_uri(db_path), uri=True, check_same_thread=False)
        except sqlite3.Error as error:
            raise namespace_unavailable(f"catalog business connection failed: {error}") from error
        connection.row_factory = sqlite3.Row
        try:
            row = _read_namespace_row(connection)
        except sqlite3.Error as error:
            connection.close()
            raise namespace_unavailable(f"namespace row unreadable: {error}") from error
        if row is None:
            connection.close()
            raise namespace_unavailable("catalog carries no preview_namespace binding")
        lease_binding = self._namespace_lease.binding
        if (
            row.protocol_version != lease_binding.protocol_version
            or row.derived_root != lease_binding.derived_root
            or row.derived_identity != lease_binding.derived_identity
            or row.catalog_root != lease_binding.catalog_root
            or row.catalog_identity != lease_binding.catalog_identity
        ):
            connection.close()
            raise namespace_unavailable("namespace binding mismatch under lease")
        return connection

    def close(self) -> None:
        with self._lock:
            self._connection.close()
        if self._owns_lease and self._namespace_lease is not None:
            self._namespace_lease.release()
        self._namespace_lease = None

    @property
    def namespace_lease(self) -> Optional[PreviewNamespaceLease]:
        """The lease protecting this store (None only for :memory:)."""
        return self._namespace_lease

    # --------------------------------------------------------------- writes

    def upsert(self, resource_id: str, scope_class: str, rel_path: str) -> None:
        """Insert or replace one catalog row; both columns are validated here
        so a poisoned write can never mint a servable grant.

        M2-DERIVED-GC-2: a loader/operator upsert INVALIDATES the key's
        origin eligibility in the same transaction -- a re-bound row must
        never inherit the old origin (or its retired flag), even when the
        path later matches again.
        """

        if not isinstance(resource_id, str) or not resource_id:
            raise TypedResourceChannelError(E_MALFORMED, "resource_id must be a non-empty string")
        if scope_class not in ALLOWED_SCOPE_CLASSES:
            raise TypedResourceChannelError(
                E_SCOPE_DENIED, f"scope class not servable: {scope_class}"
            )
        validate_rel_path(rel_path)
        with self._lock:
            try:
                self._connection.execute(
                    "INSERT INTO resource_catalog(resource_id, scope_class, rel_path) "
                    "VALUES(?, ?, ?) "
                    "ON CONFLICT(resource_id) DO UPDATE SET scope_class=excluded.scope_class, "
                    "rel_path=excluded.rel_path",
                    (resource_id, scope_class, rel_path),
                )
                self._connection.execute(
                    "DELETE FROM preview_lifecycle WHERE resource_id = ?", (resource_id,)
                )
                self._connection.commit()
            except sqlite3.Error:
                self._connection.rollback()
                raise

    def register_preview_with_origin(
        self, resource_id: str, rel_path: str, origin: PreviewOrigin
    ) -> None:
        """The Core-only origin registration (design §2.1): catalog row AND
        ``preview_lifecycle`` row (retired=0) commit in ONE SQLite
        transaction. A conflict (the random key colliding, or a stale retry)
        refuses instead of silently rebinding."""

        if scope_class_of_origin(rel_path) != PREVIEW_ORIGIN_SCOPE:
            raise TypedResourceChannelError(
                E_SCOPE_DENIED, "origin registration is preview-scope only"
            )
        validate_rel_path(rel_path)
        with self._lock:
            try:
                self._connection.execute(
                    "INSERT INTO resource_catalog(resource_id, scope_class, rel_path)"
                    " VALUES(?, ?, ?)",
                    (resource_id, PREVIEW_ORIGIN_SCOPE, rel_path),
                )
                self._connection.execute(
                    "INSERT INTO preview_lifecycle(resource_id, producer_root, artifact_id,"
                    " artifact_revision_id, managed_rel_path, retired)"
                    " VALUES(?, ?, ?, ?, ?, 0)",
                    (
                        resource_id,
                        origin.producer_root,
                        origin.artifact_id,
                        origin.artifact_revision_id,
                        origin.managed_rel_path,
                    ),
                )
                self._connection.commit()
            except sqlite3.Error:
                self._connection.rollback()
                raise

    def remove(self, resource_id: str) -> bool:
        with self._lock:
            try:
                cursor = self._connection.execute(
                    "DELETE FROM resource_catalog WHERE resource_id = ?", (resource_id,)
                )
                self._connection.execute(
                    "DELETE FROM preview_lifecycle WHERE resource_id = ?", (resource_id,)
                )
                self._connection.commit()
            except sqlite3.Error:
                self._connection.rollback()
                raise
        return cursor.rowcount > 0

    # ------------------------------------------------- lifecycle (GC-2)

    def mark_preview_retired(self, resource_id: str) -> bool:
        """The channel's ONLY lifecycle write (design §2.2): flip ``retired``
        on an already-registered own preview row.

        Independent short connection with ``timeout=0`` (zero busy wait, zero
        retries -- a busy catalog keeps the copy, never stalls the bridge);
        no schema work, no journal-mode changes, no missing-DB creation, one
        statement, closed in ``finally``. Unknown keys and page-original /
        managed rows are a no-op. Callers MUST catch sqlite/OSError/Exception
        here as no-op + diagnostics (design §2.2); this method raises so the
        bridge branch owns the policy.
        """

        if not isinstance(resource_id, str) or not resource_id:
            return False
        db_path = self._db_path
        if db_path is None:
            # :memory: experiment store: no cross-connection busy dimension
            # exists in-memory, so the flip runs on the shared connection.
            with self._lock:
                cursor = self._connection.execute(
                    "UPDATE preview_lifecycle SET retired = 1"
                    " WHERE resource_id = ? AND retired = 0",
                    (resource_id,),
                )
                self._connection.commit()
            return cursor.rowcount > 0
        connection = sqlite3.connect(_rw_uri(db_path), uri=True, timeout=0)
        try:
            cursor = connection.execute(
                "UPDATE preview_lifecycle SET retired = 1"
                " WHERE resource_id = ? AND retired = 0",
                (resource_id,),
            )
            connection.commit()
            return cursor.rowcount > 0
        finally:
            connection.close()

    def retired_preview_candidates(self, producer_root: str) -> list[RetiredPreviewCandidate]:
        """Retired+origin rows that pass the catalog-side shape gate (design
        §2.4): derived-read-only scope AND rel_path exactly
        ``previews/<resource_id>.png`` AND the registered producer root.
        Everything else never becomes a candidate."""

        with self._lock:
            rows = self._connection.execute(
                "SELECT lc.resource_id, lc.producer_root, lc.artifact_id,"
                " lc.artifact_revision_id, lc.managed_rel_path"
                " FROM preview_lifecycle AS lc"
                " JOIN resource_catalog AS c ON c.resource_id = lc.resource_id"
                " WHERE lc.retired = 1 AND lc.producer_root = ?"
                " AND c.scope_class = 'derived-read-only'"
                " AND c.rel_path = 'previews/' || lc.resource_id || '.png'"
                " ORDER BY lc.resource_id",
                (producer_root,),
            ).fetchall()
        return [
            RetiredPreviewCandidate(
                resource_id=row["resource_id"],
                producer_root=row["producer_root"],
                artifact_id=row["artifact_id"],
                artifact_revision_id=row["artifact_revision_id"],
                managed_rel_path=row["managed_rel_path"],
            )
            for row in rows
        ]

    def reclaim_orphan_lifecycle_rows(self) -> int:
        """D2 recovery (metadata only): origin rows whose catalog row is gone
        (the copy was already deleted when the catalog transaction failed).
        Never deletes a file and never implies anything about other files."""

        with self._lock:
            cursor = self._connection.execute(
                "DELETE FROM preview_lifecycle"
                " WHERE resource_id NOT IN (SELECT resource_id FROM resource_catalog)"
            )
            self._connection.commit()
        return cursor.rowcount

    def reclaim_retired_preview_metadata(self, resource_id: str) -> None:
        """One catalog transaction deleting the catalog row AND the origin
        record of an already-unlinked copy (design §3: file first, metadata
        second; no cross-database atomicity is claimed)."""

        with self._lock:
            try:
                self._connection.execute(
                    "DELETE FROM resource_catalog WHERE resource_id = ?", (resource_id,)
                )
                self._connection.execute(
                    "DELETE FROM preview_lifecycle WHERE resource_id = ?", (resource_id,)
                )
                self._connection.commit()
            except sqlite3.Error:
                self._connection.rollback()
                raise

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

    def preview_resource_ids_for_artifacts(self, artifact_ids) -> list[str]:
        """AC4: publish-style resource_ids whose origin artifact is in this set.

        The publish key is ``preview-<uuid4>`` with rel_path
        ``previews/<key>.png``: it carries no book, chapter or page component, so
        it cannot be selected by path (measured R189).  ``artifact_id`` is the only
        link back to a page, which is why the caller must snapshot before the
        delete removes the mapping.
        """
        ids = [a for a in (artifact_ids or []) if a]
        if not ids:
            return []
        placeholders = ",".join("?" for _ in ids)
        with self._lock:
            rows = self._connection.execute(
                "SELECT resource_id FROM preview_lifecycle WHERE artifact_id IN (%s)"
                % placeholders,
                tuple(ids),
            ).fetchall()
        return [row[0] for row in rows if row[0]]

    def preview_lifecycle_row(self, resource_id: str) -> Optional[dict]:
        """Diagnostic read (GC-2 evidence/tests): the origin row of a key."""
        with self._lock:
            row = self._connection.execute(
                "SELECT resource_id, producer_root, artifact_id, artifact_revision_id,"
                " managed_rel_path, retired FROM preview_lifecycle WHERE resource_id = ?",
                (resource_id,),
            ).fetchone()
        if row is None:
            return None
        return {
            "resource_id": row["resource_id"],
            "producer_root": row["producer_root"],
            "artifact_id": row["artifact_id"],
            "artifact_revision_id": row["artifact_revision_id"],
            "managed_rel_path": row["managed_rel_path"],
            "retired": bool(row["retired"]),
        }


def scope_class_of_origin(rel_path: str) -> str:
    """The only origin-eligible shape is the preview publish shape."""
    parts = rel_path.replace("\\", "/").split("/")
    if len(parts) == 2 and parts[0] == "previews" and parts[1].endswith(".png"):
        return PREVIEW_ORIGIN_SCOPE
    return ""


def _bootstrap_namespace_lease(db_path: Path) -> PreviewNamespaceLease:
    """The frozen file-backed bootstrap order (design §2.3).

    1. refuse reparse components and fix the catalog file identity;
    2. read-only + immutable temporary connection: read the single namespace
       row only (no _SCHEMA, no DDL, no pragma writes, no checkpoint; a
       missing database is never created);
    3. close it and treat the row as an untrusted location HINT;
    4. take the shared lease on the hinted derived root (lock content is
       re-verified against the real derived identity and the fixed catalog
       identity);
    5. the business connection re-reads and verifies the namespace row (the
       constructor's ``_open_business_connection``) before any table is
       initialised or served.
    """

    if not db_path.exists():
        raise namespace_unavailable(
            "catalog database does not exist (unbound namespace;"
            " run the controlled initializer first)"
        )
    _, catalog_identity = resolve_namespace_identity(db_path)
    try:
        probe = sqlite3.connect(_ro_immutable_uri(db_path), uri=True)
    except sqlite3.Error as error:
        raise namespace_unavailable(f"catalog bootstrap connection failed: {error}") from error
    try:
        hint = _read_namespace_row(probe)
    finally:
        probe.close()
    if hint is None:
        raise namespace_unavailable(
            "catalog has no preview_namespace binding; run the controlled initializer"
        )
    return acquire_shared_lease(
        Path(hint.derived_root), expected_catalog_identity=catalog_identity
    )


__all__ = [
    "CatalogEntry",
    "PreviewOrigin",
    "RetiredPreviewCandidate",
    "ResourceCatalogStore",
    "initialize_namespace",
    "restore_namespace_lock",
]
