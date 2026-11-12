"""AUDIT-08 synthetic SQLite probes.

All databases live under pytest's caller-supplied temporary directory. These
probes exercise the production connection facade without opening user data.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import hashlib
from pathlib import Path
import sqlite3
import subprocess
import sys
import threading

import pytest

from infrastructure.sqlite.connection import open_database
from infrastructure.sqlite.migrator import MigrationRunner, read_schema_version
from infrastructure.sqlite.schema import default_migrations


MIGRATIONS = default_migrations()
LATEST = MIGRATIONS[-1].schema_version
NOW = "2026-11-13T00:00:00.000+00:00"


def _new_database(path: Path):
    connection, opened = open_database(path, latest_known_schema_version=LATEST)
    assert opened.state.value == "empty"
    MigrationRunner(connection, MIGRATIONS).apply_pending()
    return connection


def test_thread_routed_connection_serializes_synthetic_concurrent_writes(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "concurrent.sqlite"
    connection = _new_database(db_path)
    with connection:
        connection.execute(
            "INSERT INTO books (book_id, title, created_at, updated_at)"
            " VALUES ('seed', 'seed', ?, ?)",
            (NOW, NOW),
        )

    start = threading.Barrier(4)

    def writer(prefix: str) -> int:
        start.wait(timeout=10)
        with connection:
            for index in range(40):
                book_id = f"{prefix}-{index}"
                connection.execute(
                    "INSERT INTO books (book_id, title, created_at, updated_at)"
                    " VALUES (?, ?, ?, ?)",
                    (book_id, book_id, NOW, NOW),
                )
        return 40

    def reader() -> int:
        start.wait(timeout=10)
        observations = []
        for _ in range(100):
            count = connection.execute("SELECT COUNT(*) FROM books").fetchone()[0]
            assert 1 <= count <= 81
            observations.append(count)
        return len(observations)

    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = [
            pool.submit(writer, "writer-a"),
            pool.submit(writer, "writer-b"),
            pool.submit(reader),
            pool.submit(reader),
        ]
        results = [future.result(timeout=30) for future in futures]

    assert results == [40, 40, 100, 100]
    assert connection.execute("SELECT COUNT(*) FROM books").fetchone()[0] == 81
    assert connection.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    assert connection.execute("PRAGMA foreign_key_check").fetchall() == []
    connection.close()


def test_wal_reopens_after_process_exit_with_uncommitted_transaction(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "crash-recovery.sqlite"
    connection = _new_database(db_path)
    with connection:
        connection.execute(
            "INSERT INTO books (book_id, title, created_at, updated_at)"
            " VALUES ('book-1', 'initial', ?, ?)",
            (NOW, NOW),
        )
    connection.close()

    child = r"""
import os
import sys
from infrastructure.sqlite.connection import open_database
from infrastructure.sqlite.schema import default_migrations

conn, _ = open_database(
    sys.argv[1], latest_known_schema_version=default_migrations()[-1].schema_version
)
with conn:
    conn.execute("UPDATE books SET title='committed' WHERE book_id='book-1'")
conn.execute("BEGIN IMMEDIATE")
conn.execute("UPDATE books SET title='uncommitted' WHERE book_id='book-1'")
os._exit(23)
"""
    result = subprocess.run(
        [sys.executable, "-c", child, str(db_path)],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert result.returncode == 23, result.stderr

    reopened, opened = open_database(db_path, latest_known_schema_version=LATEST)
    assert opened.state.value == "ready"
    assert reopened.execute(
        "SELECT title FROM books WHERE book_id='book-1'"
    ).fetchone()[0] == "committed"
    assert reopened.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    assert reopened.execute("PRAGMA foreign_key_check").fetchall() == []
    reopened.close()


def test_clean_database_can_be_reopened_after_path_move(tmp_path: Path) -> None:
    old_path = tmp_path / "old" / "library.sqlite"
    old_path.parent.mkdir(parents=True)
    connection = _new_database(old_path)
    with connection:
        connection.execute(
            "INSERT INTO books (book_id, title, created_at, updated_at)"
            " VALUES ('moved-book', 'after move', ?, ?)",
            (NOW, NOW),
        )
    connection.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    connection.close()

    moved_path = tmp_path / "new" / "library.sqlite"
    moved_path.parent.mkdir(parents=True)
    old_path.replace(moved_path)
    reopened, opened = open_database(moved_path, latest_known_schema_version=LATEST)
    assert opened.state.value == "ready"
    assert read_schema_version(reopened) == LATEST
    assert reopened.execute(
        "SELECT title FROM books WHERE book_id='moved-book'"
    ).fetchone()[0] == "after move"
    reopened.close()


def test_corrupt_database_is_rejected_without_reinitializing_bytes(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "corrupt.sqlite"
    original = b"synthetic corrupt sqlite bytes\x00\xff"
    db_path.write_bytes(original)
    original_hash = hashlib.sha256(original).hexdigest()

    with pytest.raises(sqlite3.DatabaseError):
        open_database(db_path, latest_known_schema_version=LATEST)

    after = db_path.read_bytes()
    assert hashlib.sha256(after).hexdigest() == original_hash
    assert after == original
