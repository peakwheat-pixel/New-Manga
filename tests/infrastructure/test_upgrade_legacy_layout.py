"""Tests for the one-shot legacy data-root migration (UPGRADE-LEGACY-LAYOUT-1)."""

from __future__ import annotations

import shutil
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


def _book_count(db_path: Path) -> int:
    connection = sqlite3.connect(db_path)
    try:
        return int(connection.execute("SELECT COUNT(*) FROM books").fetchone()[0])
    finally:
        connection.close()


def _legacy_root(tmp_path: Path, *, managed: bool = True, backups: bool = True) -> Path:
    root = tmp_path / "data-root"
    _make_library(root / "data" / "library.db", books=2)
    if managed:
        (root / "data" / "managed" / "books" / "abc").mkdir(parents=True)
        (root / "data" / "managed" / "books" / "abc" / "page.png").write_bytes(b"png")
    if backups:
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
    assert not (root / ".upgrade-legacy-staging").exists()
    assert _book_count(root / "library.db") == 2


def test_current_database_is_never_overwritten(tmp_path: Path) -> None:
    root = _legacy_root(tmp_path)
    _make_library(root / "library.db", books=5)

    result = migrate_legacy_layout(root)

    # The database is skipped, but the missing managed/backups trees are filled
    # in so an earlier partial migration cannot hide the user's pages.
    assert result.migrated is True
    assert result.copied == ("managed/", "backups/")
    assert _book_count(root / "library.db") == 5
    assert (root / "managed" / "books" / "abc" / "page.png").is_file()


def test_fully_migrated_layout_is_noop_on_restart(tmp_path: Path) -> None:
    root = _legacy_root(tmp_path)

    first = migrate_legacy_layout(root)
    second = migrate_legacy_layout(root)

    assert first.migrated is True
    assert second.migrated is False
    assert second.skipped_reason is not None and "already present" in second.skipped_reason


def test_no_legacy_layout_is_a_noop(tmp_path: Path) -> None:
    root = tmp_path / "fresh-root"

    result = migrate_legacy_layout(root)

    assert result.migrated is False
    assert result.skipped_reason is not None and "not found" in result.skipped_reason
    assert not (root / "library.db").exists()


def test_migrates_wal_and_journal_sidecars(tmp_path: Path) -> None:
    root = _legacy_root(tmp_path)
    (root / "data" / "library.db-wal").write_bytes(b"")
    (root / "data" / "library.db-shm").write_bytes(b"")
    (root / "data" / "library.db-journal").write_bytes(b"")

    result = migrate_legacy_layout(root)

    assert result.migrated is True
    for suffix in ("-wal", "-shm", "-journal"):
        assert (root / f"library.db{suffix}").is_file()


def test_corrupt_legacy_database_is_refused(tmp_path: Path) -> None:
    root = tmp_path / "data-root"
    (root / "data").mkdir(parents=True)
    (root / "data" / "library.db").write_bytes(b"not a sqlite database")

    with pytest.raises(LegacyLayoutError):
        migrate_legacy_layout(root)

    assert not (root / "library.db").exists()
    assert (root / "data" / "library.db").is_file()  # untouched for rollback
    assert not (root / ".upgrade-legacy-staging").exists()


def test_io_error_is_wrapped_and_root_untouched(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = _legacy_root(tmp_path)

    def _locked(*_args: object, **_kwargs: object) -> None:
        raise PermissionError("file is locked")

    monkeypatch.setattr("infrastructure.sqlite.upgrade_legacy_layout.shutil.copy2", _locked)

    with pytest.raises(LegacyLayoutError) as excinfo:
        migrate_legacy_layout(root)

    assert "filesystem error" in str(excinfo.value)
    assert not (root / "library.db").exists()
    assert not (root / "managed").exists()
    assert not (root / ".upgrade-legacy-staging").exists()


def test_partial_directory_failure_leaves_database_unpromoted(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _legacy_root(tmp_path)
    real_copytree = shutil.copytree

    def _fail_managed(source: Path, destination: Path, *args: object, **kwargs: object) -> None:
        if Path(source).name == "managed":
            raise PermissionError("locked managed tree")
        return real_copytree(source, destination, *args, **kwargs)

    monkeypatch.setattr("infrastructure.sqlite.upgrade_legacy_layout.shutil.copytree", _fail_managed)

    with pytest.raises(LegacyLayoutError):
        migrate_legacy_layout(root)

    # Promotion happens only after every copy succeeded: nothing in the root yet.
    assert not (root / "library.db").exists()
    assert not (root / "managed").exists()
    assert not (root / "backups").exists()
    assert (root / "data" / "library.db").is_file()


def test_log_file_records_migration(tmp_path: Path) -> None:
    root = _legacy_root(tmp_path)

    migrate_legacy_layout(root)

    log = (root / "logs" / "upgrade-legacy.log").read_text(encoding="utf-8")
    assert "migrated from data/" in log


def test_only_legacy_subdirectories_still_migrate(tmp_path: Path) -> None:
    """A legacy managed/ tree without a database is still promoted."""
    root = tmp_path / "data-root"
    (root / "data" / "managed" / "books" / "x").mkdir(parents=True)
    (root / "data" / "managed" / "books" / "x" / "p.png").write_bytes(b"p")

    result = migrate_legacy_layout(root)

    assert result.migrated is True
    assert result.copied == ("managed/",)
    assert (root / "managed" / "books" / "x" / "p.png").read_bytes() == b"p"
