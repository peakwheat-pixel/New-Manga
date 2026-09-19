"""TASK-060: connection/transaction ownership (Q-001, P0).

The pre-fix tree (``be558ca``..``9522f2d``) handed ONE ``sqlite3``
connection to both the GUI thread and the run worker, so both threads
committed and rolled back *the same transaction* (Qoder probe
``w1_thread_collision_probe.py``: orphan revisions 10/10, silently
swallowed writes 7/7, runs killed with rows stuck at ``running`` 3/10).
``open_database`` now returns a thread-routed facade — one real
connection per thread — which makes that interleaving structurally
impossible.

These tests drive TWO threads against the SAME connection handle with
Event-forced interleaving (no scheduling luck):

- AC ①/③ (discriminating): a half-open writer transaction whose
  revision row gets committed by the other thread's ``with conn:``
  must not survive the writer's rollback — pre-fix this deterministically
  leaves an orphan ``region_revisions`` row;
- AC ②/D3 (discriminating): a writer returning success must leave the
  row readable through an independent connection even when the other
  thread's error path rolls back mid-write — pre-fix the row was
  silently gone;
- pinning-only (not discriminating): per-thread routing itself — the
  facade is the fix under test, covered by the two discriminating
  cases above.
"""

from __future__ import annotations

import sqlite3
import sys
import threading
from pathlib import Path

_SRC = Path(__file__).resolve().parents[2] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

import pytest

from infrastructure.sqlite.connection import open_database
from infrastructure.sqlite.migrator import MigrationRunner
from infrastructure.sqlite.schema import default_migrations


@pytest.fixture()
def owned_db(tmp_path: Path) -> tuple[object, Path]:
    """One connection handle (facade post-fix, shared real connection
    pre-fix) over a fully migrated library — plus the db path so an
    independent judge connection can be opened against the file."""
    db_path = tmp_path / "library.db"
    conn, _opened = open_database(
        db_path,
        latest_known_schema_version=default_migrations()[-1].schema_version,
    )
    MigrationRunner(conn, default_migrations()).apply_pending()
    return conn, db_path


_NOW = "2026-01-01T00:00:00.000+00:00"


def _seed_region(conn) -> None:
    with conn:
        conn.execute(
            "INSERT INTO books (book_id, title, created_at, updated_at)"
            " VALUES ('b1', 'B', ?, ?)",
            (_NOW, _NOW),
        )
        conn.execute(
            "INSERT INTO chapters (chapter_id, book_id, title, created_at,"
            " updated_at) VALUES ('c1', 'b1', 'C', ?, ?)",
            (_NOW, _NOW),
        )
        conn.execute(
            "INSERT INTO pages (page_id, chapter_id, source_filename,"
            " source_hash, sort_order, created_at, updated_at)"
            " VALUES ('p1', 'c1', 'p1.png', 'h', 1, ?, ?)",
            (_NOW, _NOW),
        )
        conn.execute(
            "INSERT INTO regions (region_id, page_id, region_type,"
            " reading_order, geometry_json, text_json, style_json,"
            " sfx_policy, created_at, updated_at, current_revision_id)"
            " VALUES ('r1', 'p1', 'speech', 1, '{}', '{}', '{}', 'skip',"
            " ?, ?, NULL)",
            (_NOW, _NOW),
        )


def test_interleaved_commit_cannot_orphan_a_revision(owned_db):
    """AC ①/③ (discriminating): the writer's rollback must take its own
    half-open revision row with it even though the other thread commits
    in the middle.  Pre-fix both threads shared one transaction, so the
    other thread's commit published the half-open row and the rollback
    had nothing left to undo — an orphan revision, deterministically."""
    conn, db_path = owned_db
    _seed_region(conn)
    begin_inserted = threading.Event()
    other_committed = threading.Event()

    def writer() -> None:
        # half-open transaction: revision row inserted, NOT committed
        conn.execute("BEGIN IMMEDIATE")
        conn.execute(
            "INSERT INTO region_revisions (region_revision_id, region_id,"
            " revision_no, snapshot_json, origin, review_state, is_pinned,"
            " created_at) VALUES ('rev-x', 'r1', 1, '{}', 'user',"
            " 'confirmed', 0, ?)",
            (_NOW,),
        )
        begin_inserted.set()
        other_committed.wait(5)
        # pre-fix: the other thread's bare commit() already published this
        # half-open row (one shared transaction), so the rollback below is
        # a no-op and the row is orphaned on disk.
        # post-fix: the other thread's commit() is a no-op on its OWN
        # connection and the rollback undoes the writer's row.
        conn.rollback()

    def other_thread() -> None:
        begin_inserted.wait(5)
        # no DML, no write lock needed post-fix; pre-fix this single
        # commit() ended the shared transaction holding the writer's row
        conn.commit()
        other_committed.set()

    t1 = threading.Thread(target=writer)
    t2 = threading.Thread(target=other_thread)
    t1.start()
    t2.start()
    t1.join(10)
    t2.join(10)

    judge = sqlite3.connect(str(db_path))
    try:
        orphans = judge.execute(
            "SELECT COUNT(*) FROM region_revisions WHERE region_revision_id = 'rev-x'"
        ).fetchone()[0]
    finally:
        judge.close()
    assert orphans == 0, (
        "a half-open revision row survived its own writer's rollback"
        " because the other thread's commit published it (orphan revision)"
    )


def test_writer_success_survives_the_other_threads_rollback(owned_db):
    """AC ②/D3 (discriminating): a writer that returns success (its
    ``with conn:`` block committed) must have its row on disk even if
    the other thread's error path called ``conn.rollback()`` mid-write.
    Pre-fix the rollback ate the writer's uncommitted insert — the
    writer still returned success and the row was silently gone."""
    conn, db_path = owned_db
    begin_inserted = threading.Event()
    rollback_done = threading.Event()
    committed = threading.Event()

    def writer() -> None:
        with conn:
            conn.execute(
                "INSERT INTO books (book_id, title, created_at, updated_at)"
                " VALUES ('b-d3', 'D3', ?, ?)",
                (_NOW, _NOW),
            )
            begin_inserted.set()
            rollback_done.wait(5)
        committed.set()

    def error_path() -> None:
        # the shape of pipeline.py's failure path: rollback on the shared
        # connection while another thread has an open transaction
        begin_inserted.wait(5)
        conn.rollback()
        rollback_done.set()

    t1 = threading.Thread(target=writer)
    t2 = threading.Thread(target=error_path)
    t1.start()
    t2.start()
    t1.join(10)
    t2.join(10)
    assert committed.is_set(), "writer never finished"

    judge = sqlite3.connect(str(db_path))
    try:
        rows = judge.execute(
            "SELECT COUNT(*) FROM books WHERE book_id = 'b-d3'"
        ).fetchone()[0]
    finally:
        judge.close()
    assert rows == 1, (
        "writer returned success but an independent connection cannot"
        " read the row back (silently swallowed write)"
    )
