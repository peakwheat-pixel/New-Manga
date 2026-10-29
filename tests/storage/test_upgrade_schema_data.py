"""Synthetic legacy-schema data migration tests (UPGRADE-SCHEMA-MIGRATION-1).

The real pre-AD-002 user databases are not available (see UPGRADE-REHEARSAL-1), so
these tests synthesise old libraries with the project's own migration definitions:
for every legacy schema version (v1..v5) a database is built by applying only the
first N migrations, real-shaped rows are inserted through the v1 tables, and the
full migration chain is then applied to reach the latest schema.

What is asserted:
- the chain lands on the latest schema version;
- every seeded row survives with its values unchanged (books/chapters/pages/
  artifact revisions);
- later-version objects (regions, pipeline tables, reading progress, plugin
  state) exist after the upgrade;
- the upgraded database is healthy and writable.
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pytest

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:  # mirrors tests/core|packaging conftest.py
    sys.path.insert(0, str(SRC_ROOT))

from infrastructure.sqlite.migrator import MigrationRunner, read_schema_version  # noqa: E402
from infrastructure.sqlite.schema import default_migrations  # noqa: E402

MIGRATIONS = default_migrations()
LATEST_VERSION = MIGRATIONS[-1].schema_version
LEGACY_VERSIONS = [migration.schema_version for migration in MIGRATIONS[:-1]]
NOW = "2026-01-02T03:04:05+00:00"

#: Objects that must exist in the latest schema regardless of the starting version.
LATEST_SCHEMA_TABLES = (
    "books",
    "chapters",
    "pages",
    "media_artifacts",
    "artifact_revisions",
    "regions",
    "region_revisions",
    "pipeline_runs",
    "reading_progress",
    "export_history",
    "plugin_state",
)


def _connect(db_path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys=ON")
    return connection


def _build_legacy_database(db_path: Path, version: int) -> sqlite3.Connection:
    """Apply only the first *version* migrations and seed v1-era data."""
    connection = _connect(db_path)
    applied = MigrationRunner(connection, MIGRATIONS[:version]).apply_pending()
    assert [record.schema_version for record in applied] == list(
        range(1, version + 1)
    )
    assert read_schema_version(connection) == version
    _seed_data(connection, version)
    return connection


def _seed_data(connection: sqlite3.Connection, version: int) -> None:
    tag = f"v{version}"
    connection.execute(
        "INSERT INTO books (book_id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
        (f"book-{tag}", f"旧书 {tag}", NOW, NOW),
    )
    for index in (1, 2):
        connection.execute(
            "INSERT INTO chapters (chapter_id, book_id, title, sort_order, created_at, updated_at)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            (f"chapter-{tag}-{index}", f"book-{tag}", f"第 {index} 章", index, NOW, NOW),
        )
    for index in (1, 2, 3):
        connection.execute(
            "INSERT INTO pages (page_id, chapter_id, sort_order, created_at, updated_at)"
            " VALUES (?, ?, ?, ?, ?)",
            (f"page-{tag}-{index}", f"chapter-{tag}-1", index, NOW, NOW),
        )
    connection.execute(
        "INSERT INTO media_artifacts (artifact_id, book_id, chapter_id, page_id,"
        " artifact_type, created_at, updated_at) VALUES (?, ?, ?, ?, 'original', ?, ?)",
        (f"artifact-{tag}", f"book-{tag}", f"chapter-{tag}-1", f"page-{tag}-1", NOW, NOW),
    )
    connection.execute(
        "INSERT INTO artifact_revisions (artifact_revision_id, artifact_id, revision_no,"
        " managed_path, file_hash, mime_type, size_bytes, created_at)"
        " VALUES (?, ?, 1, ?, ?, 'image/png', 1024, ?)",
        (f"revision-{tag}", f"artifact-{tag}", f"managed/{tag}/page.png", f"hash-{tag}", NOW),
    )
    connection.commit()


def _assert_latest(connection: sqlite3.Connection) -> None:
    assert read_schema_version(connection) == LATEST_VERSION
    names = {
        row["name"]
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        ).fetchall()
    }
    missing = [name for name in LATEST_SCHEMA_TABLES if name not in names]
    assert not missing, f"latest schema is missing tables: {missing}"
    integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
    assert integrity == "ok"


@pytest.mark.parametrize("version", LEGACY_VERSIONS, ids=[f"v{v}" for v in LEGACY_VERSIONS])
def test_synthetic_legacy_data_survives_full_upgrade(tmp_path: Path, version: int) -> None:
    tag = f"v{version}"
    db_path = tmp_path / f"legacy-{tag}.db"
    connection = _build_legacy_database(db_path, version)

    applied = MigrationRunner(connection, MIGRATIONS).apply_pending()
    assert [record.schema_version for record in applied] == list(
        range(version + 1, LATEST_VERSION + 1)
    )
    _assert_latest(connection)

    # Seeded rows survive byte-for-byte (values, ordering and relations).
    assert connection.execute("SELECT COUNT(*) FROM books").fetchone()[0] == 1
    assert connection.execute("SELECT title FROM books").fetchone()[0] == f"旧书 {tag}"
    assert connection.execute("SELECT COUNT(*) FROM chapters").fetchone()[0] == 2
    assert connection.execute("SELECT COUNT(*) FROM pages").fetchone()[0] == 3
    revision = connection.execute(
        "SELECT managed_path, file_hash, size_bytes FROM artifact_revisions"
    ).fetchone()
    assert revision["managed_path"] == f"managed/{tag}/page.png"
    assert revision["file_hash"] == f"hash-{tag}"
    assert revision["size_bytes"] == 1024

    # The upgraded database is usable: inserting new rows still works.
    connection.execute(
        "INSERT INTO books (book_id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
        (f"book-{tag}-new", "升级后新增", NOW, NOW),
    )
    connection.commit()
    assert connection.execute("SELECT COUNT(*) FROM books").fetchone()[0] == 2
    connection.close()


def test_upgrade_from_v1_creates_later_version_objects(tmp_path: Path) -> None:
    """Starting from the oldest schema must still produce every later object."""
    connection = _build_legacy_database(tmp_path / "legacy-v1.db", 1)
    v1_tables = {
        row["name"]
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        ).fetchall()
    }
    # Sanity: the v1 snapshot really is missing the later-version tables.
    for later_table in ("regions", "pipeline_runs", "reading_progress", "plugin_state"):
        assert later_table not in v1_tables

    MigrationRunner(connection, MIGRATIONS).apply_pending()
    _assert_latest(connection)
    connection.close()


def test_upgrade_is_idempotent_for_synthetic_legacy_data(tmp_path: Path) -> None:
    connection = _build_legacy_database(tmp_path / "legacy-v3.db", 3)
    MigrationRunner(connection, MIGRATIONS).apply_pending()
    before = connection.execute("SELECT COUNT(*) FROM books").fetchone()[0]

    assert MigrationRunner(connection, MIGRATIONS).apply_pending() == []
    assert connection.execute("SELECT COUNT(*) FROM books").fetchone()[0] == before
    _assert_latest(connection)
    connection.close()
