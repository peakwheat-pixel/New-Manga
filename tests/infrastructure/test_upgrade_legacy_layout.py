"""Tests for the one-shot legacy data-root migration (UPGRADE-LEGACY-LAYOUT-1)."""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pytest

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:  # mirrors tests/core|packaging conftest.py
    sys.path.insert(0, str(SRC_ROOT))

from infrastructure.sqlite.upgrade_legacy_layout import (  # noqa: E402
    LegacyLayoutError,
    migrate_legacy_layout,
)


def _make_library(path: Path, books: int = 1) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    try:
        connection.execute("CREATE TABLE books (id INTEGER PRIMARY KEY, title TEXT)")
        for index in range(books):
            connection.execute("INSERT INTO books (title) VALUES (?)", (f"book-{index}",))
        connection.commit()
    finally:
        connection.close()


def _legacy_root(tmp_path: Path) -> Path:
    root = tmp_path / "data-root"
    _make_library(root / "data" / "library.db", books=2)
    (root / "data" / "managed" / "books" / "abc").mkdir(parents=True)
    (root / "data" / "managed" / "books" / "abc" / "page.png").write_bytes(b"png")
    (root / "data" / "backups").mkdir(parents=True)
    (root / "data" / "backups" / "old.zip").write_bytes(b"zip")
    (root / "catalog").mkdir(parents=True, exist_ok=True)
    return root


def test_migrates_database_managed_and_backups(tmp_path: Path) -> None:
    root = _legacy_root(tmp_path)

    result = migrate_legacy_layout(root)

    assert result.migrated is True
    assert "library.db" in result.copied
    assert "managed/" in result.copied
    assert "backups/" in result.copied
    assert (root / "library.db").is_file()
    assert (root / "managed" / "books" / "abc" / "page.png").read_bytes() == b"png"
    assert (root / "backups" / "old.zip").is_file()
    # Only copies: the legacy tree remains for rollback.
    assert (root / "data" / "library.db").is_file()
    # Staging directory is always cleaned up.
    assert not (root / ".upgrade-legacy-staging").exists()
    # The copied database is readable and keeps its rows.
    connection = sqlite3.connect(root / "library.db")
    try:
        assert connection.execute("SELECT COUNT(*) FROM books").fetchone()[0] == 2
    finally:
        connection.close()


def test_current_layout_wins(tmp_path: Path) -> None:
    root = _legacy_root(tmp_path)
    _make_library(root / "library.db", books=5)

    result = migrate_legacy_layout(root)

    assert result.migrated is False
    assert result.skipped_reason is not None and "already present" in result.skipped_reason
    connection = sqlite3.connect(root / "library.db")
    try:
        assert connection.execute("SELECT COUNT(*) FROM books").fetchone()[0] == 5
    finally:
        connection.close()


def test_no_legacy_layout_is_a_noop(tmp_path: Path) -> None:
    root = tmp_path / "fresh-root"

    result = migrate_legacy_layout(root)

    assert result.migrated is False
    assert result.skipped_reason is not None and "not found" in result.skipped_reason
    assert not (root / "library.db").exists()


def test_is_idempotent(tmp_path: Path) -> None:
    root = _legacy_root(tmp_path)

    first = migrate_legacy_layout(root)
    second = migrate_legacy_layout(root)

    assert first.migrated is True
    assert second.migrated is False
    assert second.skipped_reason is not None and "already present" in second.skipped_reason


def test_migrates_wal_sidecars(tmp_path: Path) -> None:
    root = _legacy_root(tmp_path)
    (root / "data" / "library.db-wal").write_bytes(b"")
    (root / "data" / "library.db-shm").write_bytes(b"")

    result = migrate_legacy_layout(root)

    assert result.migrated is True
    assert (root / "library.db-wal").is_file()
    assert (root / "library.db-shm").is_file()


def test_corrupt_legacy_database_is_refused(tmp_path: Path) -> None:
    root = tmp_path / "data-root"
    (root / "data").mkdir(parents=True)
    (root / "data" / "library.db").write_bytes(b"not a sqlite database")

    with pytest.raises(LegacyLayoutError):
        migrate_legacy_layout(root)

    assert not (root / "library.db").exists()
    assert (root / "data" / "library.db").is_file()  # untouched for rollback
    assert not (root / ".upgrade-legacy-staging").exists()


def test_log_file_records_migration(tmp_path: Path) -> None:
    root = _legacy_root(tmp_path)

    migrate_legacy_layout(root)

    log = (root / "logs" / "upgrade-legacy.log").read_text(encoding="utf-8")
    assert "migrated from data/" in log
