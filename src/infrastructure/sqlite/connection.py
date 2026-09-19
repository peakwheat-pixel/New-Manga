"""Connection opening, PRAGMAs and schema compatibility gating.

Implements D07 §28 (PRAGMA profile), §36 (Unicode paths, no MAX_PATH
assumption) and AC-DB-001/002/005: foreign keys on, WAL journal, and
databases written by a newer schema are opened read-only so stale
applications cannot blind-write.

TASK-048 AC ① — thread ownership of the connection: the production
connection is created on the startup (GUI) thread but is also *used*
on the ``RunController`` worker thread (``PipelineService.execute_run``
runs there, TASK-013).

TASK-060 (Q-001, P0) — that single shared connection is *not* safe at
the transaction level: both threads commit and roll back the *same*
transaction, so a GUI ``BEGIN IMMEDIATE`` can land inside a worker
``with conn:`` block and vice versa (mid-batch snapshots published,
silently swallowed writes, runs killed with rows stuck at ``running``;
evidence: ``verification/POSTHOC-WINDOW-2026-09-19/Qoder/``).  The
ownership model is therefore **one real connection per thread**,
lazily created and routed by :class:`ThreadRoutedConnection`:

- Repositories keep a single ``self._conn`` handle (the facade), so
  the transaction ownership fix is structural: a thread can only ever
  begin/commit/roll back *its own* connection's transaction — the
  cross-thread transaction interleaving Q-001 exploits cannot be
  expressed any more.
- ``check_same_thread=False`` is kept for exactly one reason: the
  facade's ``close()`` (called from the GUI thread after the drain)
  must be able to close connections created on worker threads.  Every
  *statement* still runs on the connection's owning thread via the
  thread-local routing.
- Cross-connection visibility is the WAL read-committed model:
  after a writer commits, an independent connection (AC ② test)
  immediately reads the row back.  Write-lock contention between the
  two connections is bounded by ``busy_timeout`` below; production
  write transactions are short (region commits, DELETE+INSERT
  replays).
- The docstring line this replaces ("statements from two threads share
  the connection's single transaction … self-healed") described the
  defect this class removes; see TASK-060 AC ①.
"""

from __future__ import annotations

import sqlite3
import threading
import weakref
from collections.abc import Callable
from pathlib import Path

from ports.repositories.database import OpenedDatabase, SchemaState

BUSY_TIMEOUT_MS = 5000


class SchemaTooNewError(RuntimeError):
    """Raised when a migration runner meets a schema newer than known."""


class _ConnectionLease:
    """Weak-referenceable sentinel co-owned with one thread's connection.

    TASK-061 R-002: the lease lives in the same thread-local slot as the
    real connection, so both die *together* when the owning thread dies
    (CPython tears the thread's locals down at thread exit — verified for
    QThread workers).  The lease's weakref callback is the eviction hook;
    it can only ever fire once *no code* holds the lease any more, which
    is exactly "the owning thread cannot issue statements on this
    connection any more".
    """

    __slots__ = ("__weakref__",)  # no other state; weakref is the point


class ThreadRoutedConnection:
    """Thread-aware facade over one real ``sqlite3.Connection`` per thread.

    Every access (``execute``/``cursor``/``commit``/``rollback``,
    ``with conn:``/attribute reads) is routed to the calling thread's own
    real connection, created on first use through the ``opener``.  This
    makes the TASK-060 ownership invariant structural: two threads can no
    longer interleave statements into one shared transaction.

    Reading attributes not explicitly routed here (``in_transaction``,
    ``row_factory``, …) forwards to the *calling thread's* connection and
    therefore **opens that thread's connection as a side effect** — the
    per-connection property answers "this thread", never "this database"
    (TASK-060 review R-004).  Use :meth:`any_in_transaction` for the
    aggregated, database-wide answer.
    """

    def __init__(self, opener: Callable[[], sqlite3.Connection]) -> None:
        self._opener = opener
        self._local = threading.local()
        # Registry of the real connections this facade handed out.  Entries
        # whose owning thread died are evicted by the lease's weakref
        # callback (TASK-061 R-002), so the registry is bounded by the
        # number of *live* threads, not by the number of completed runs.
        self._connections: dict[int, sqlite3.Connection] = {}
        self._leases: dict[int, weakref.ref] = {}
        self._registry_lock = threading.Lock()
        self._closed = False

    def _evict(self, ident: int, conn: sqlite3.Connection) -> None:
        """Drop one dead thread's connection from the registry and close it.

        Concurrency argument (TASK-061 AC ①): the callback fires only when
        the *lease* has been garbage-collected, and the lease is held
        exclusively in the owning thread's thread-local slot — so at fire
        time the owning thread is gone and no code path can reach the
        connection any more (this closure holds the last reference).
        Registry mutation takes the lock; ``conn.close()`` needs no
        coordination because no other party can reference ``conn``.
        """
        with self._registry_lock:
            if self._connections.get(ident) is conn:
                del self._connections[ident]
            if self._leases.get(ident) is not None and self._leases[
                ident
            ]() is None:
                del self._leases[ident]
        try:
            conn.close()
        except sqlite3.Error:  # already closed by a concurrent shutdown close
            pass

    def _current(self) -> sqlite3.Connection:
        conn = getattr(self._local, "conn", None)
        if conn is None:
            if self._closed:
                raise sqlite3.ProgrammingError(
                    "connection facade is closed"
                )
            conn = self._opener()
            lease = _ConnectionLease()
            ident = threading.get_ident()
            self._local.conn = conn
            self._local.lease = lease
            with self._registry_lock:
                # A surviving registry entry under this ident can only be
                # a stale slot of a *dead* thread whose ident got reused:
                # its lease is dead too, so closing it races with nobody.
                stale = self._connections.get(ident)
                if stale is not None:
                    self._leases.pop(ident, None)
                    try:
                        stale.close()
                    except sqlite3.Error:
                        pass
                self._connections[ident] = conn
                self._leases[ident] = weakref.ref(
                    lease, lambda _ref, _ident=ident, _conn=conn: self._evict(
                        _ident, _conn
                    )
                )
        return conn

    def execute(self, sql: str, parameters: tuple = ()) -> sqlite3.Cursor:
        return self._current().execute(sql, parameters)

    def cursor(self) -> sqlite3.Cursor:
        return self._current().cursor()

    def commit(self) -> None:
        self._current().commit()

    def rollback(self) -> None:
        self._current().rollback()

    # ------------------------------------------------------------------
    # lifecycle & observability (TASK-061)
    # ------------------------------------------------------------------

    def release_current_thread_connection(self) -> None:
        """Close and evict the *calling thread's* real connection now.

        Safe by construction: a thread can only ever release the
        connection it itself holds, and it must not call this while a
        statement/transaction is in flight on that connection (the
        production call sites release after the run reached its end).
        Dropping the thread-local slot lets the lease be collected; the
        eviction callback is idempotent against this manual path.
        """
        if getattr(self._local, "conn", None) is None:
            return
        ident = threading.get_ident()
        conn = self._local.conn
        with self._registry_lock:
            if self._connections.get(ident) is conn:
                del self._connections[ident]
            self._leases.pop(ident, None)
        del self._local.conn
        del self._local.lease
        try:
            conn.close()
        except sqlite3.Error:
            pass

    def any_in_transaction(self) -> bool:
        """``True`` when *any* live registered connection is in a transaction.

        This is the aggregated "is anyone writing right now" answer that
        the per-connection ``in_transaction`` cannot give (TASK-060 review
        R-004).  It reads the registered connections directly — never
        opens a new one — so it is safe to poll from any thread.

        TASK-057 precondition ① is defined against this predicate:
        ``workbench.shutdown() is True`` (drained ⇒ the run worker is
        gone) **and** ``not conn.any_in_transaction()`` (⇒ no other
        thread holds an open write) together mean "no other writer".
        """
        with self._registry_lock:
            conns = list(self._connections.values())
        return any(conn.in_transaction for conn in conns)

    def registry_size(self) -> int:
        """How many slots the registry currently holds (bounded by live threads)."""
        with self._registry_lock:
            return len(self._connections)

    def open_connection_count(self) -> int:
        """How many registered real connections are still open."""
        with self._registry_lock:
            conns = list(self._connections.values())
        count = 0
        for conn in conns:
            try:
                conn.execute("SELECT 1").fetchone()
            except sqlite3.ProgrammingError:  # closed
                continue
            count += 1
        return count

    def close(self) -> None:
        """Close every real connection this facade created.

        The caller must guarantee no worker is still writing (TASK-058
        drain runs first; if the drain timed out, ``_shutdown_services``
        skips close entirely — Q-003).
        """
        with self._registry_lock:
            for conn in self._connections.values():
                try:
                    conn.close()
                except sqlite3.Error:  # evicted/closed already
                    pass
            self._connections.clear()
            self._leases.clear()
            self._closed = True

    def __enter__(self) -> sqlite3.Connection:
        return self._current().__enter__()

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self._current().__exit__(exc_type, exc_value, traceback)

    def __getattr__(self, name: str):
        # in_transaction, row_factory, create_function, … — anything not
        # explicitly routed above forwards to the calling thread's
        # connection.  Note this *opens* the calling thread's connection;
        # see the class docstring (R-004).
        return getattr(self._current(), name)


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
) -> tuple[ThreadRoutedConnection, OpenedDatabase]:
    """Open ``db_path`` with the approved PRAGMA profile.

    The returned handle is a :class:`ThreadRoutedConnection`: each thread
    gets its own real connection (TASK-060 Q-001 transaction-ownership
    fix), all sharing the same PRAGMA profile.

    A database whose stored schema version exceeds
    ``latest_known_schema_version`` is reopened read-only (``query_only``)
    and reported as :class:`SchemaState.TOO_NEW`; the caller must treat it
    as unusable for writes (AC-DB-005). An empty file reports
    :class:`SchemaState.EMPTY` and stays writable so the migrator can create
    the schema.
    """
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    profile = {"query_only": False}

    def _open_one() -> sqlite3.Connection:
        conn = sqlite3.connect(str(path), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        _apply_pragmas(conn)
        if profile["query_only"]:
            conn.execute("PRAGMA query_only = ON")
        return conn

    conn = ThreadRoutedConnection(_open_one)
    stored = _read_schema_version(conn)
    if stored is None:
        return conn, OpenedDatabase(SchemaState.EMPTY, 0, True)
    if stored > latest_known_schema_version:
        # Every thread's connection must be read-only, including ones not
        # created yet — the profile flag is applied by _open_one.
        profile["query_only"] = True
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
