"""FEA-09 tests: referenced-source storage, import orchestration, grants.

Shared fixtures build a fully migrated (v7) in-memory library with the
production migration runner, mirroring tests/storage/conftest.py.
"""

from __future__ import annotations

import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[2] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import sqlite3  # noqa: E402

import pytest  # noqa: E402

from infrastructure.sqlite.library import SqliteLibraryRepository  # noqa: E402
from infrastructure.sqlite.migrator import MigrationRunner  # noqa: E402
from infrastructure.sqlite.schema import default_migrations  # noqa: E402

NOW = "2026-11-03T00:00:00.000+00:00"


@pytest.fixture()
def conn() -> sqlite3.Connection:
    # check_same_thread=False: the referenced-import runtime commits from a
    # worker thread (the production path uses ThreadRoutedConnection, which
    # gives each thread its own real connection to the same file; the
    # in-memory test stand-in shares one connection and the runtime is the
    # only writer while an operation runs).
    connection = sqlite3.connect(":memory:", check_same_thread=False)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    MigrationRunner(connection, default_migrations()).apply_pending()
    return connection


@pytest.fixture()
def repo(conn: sqlite3.Connection) -> SqliteLibraryRepository:
    return SqliteLibraryRepository(conn)


@pytest.fixture()
def book_chapter(conn: sqlite3.Connection) -> tuple[str, str]:
    """One live book + chapter ('b1' / 'c1')."""
    conn.execute(
        "INSERT INTO books (book_id, title, created_at, updated_at)"
        " VALUES ('b1', 'Book', ?, ?)",
        (NOW, NOW),
    )
    conn.execute(
        "INSERT INTO chapters (chapter_id, book_id, title, created_at, updated_at)"
        " VALUES ('c1', 'b1', 'Ch', ?, ?)",
        (NOW, NOW),
    )
    conn.commit()
    return "b1", "c1"


def add_managed_page(conn: sqlite3.Connection, page_id: str, chapter_id: str = "c1",
                     *, order: int = 1, digest: str | None = None,
                     soft_deleted: bool = False) -> str:
    """Direct-SQL managed page with complete import columns (C-15 §4.3)."""
    digest = digest or (page_id.encode("utf-8").hex() * 4)[:64]
    conn.execute(
        "INSERT INTO pages (page_id, chapter_id, sort_order, created_at,"
        " updated_at, source_filename, source_order, source_hash,"
        " source_size_bytes, width, height, managed_original_ref, deleted_at,"
        " source_mode, integrity_status)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 4, 3, ?, ?, 'managed', 'complete')",
        (page_id, chapter_id, order, NOW, NOW, f"{page_id}.png", order, digest,
         10, f"managed/{page_id}.png", NOW if soft_deleted else None),
    )
    conn.commit()
    return digest


def add_referenced_page(conn: sqlite3.Connection, page_id: str, chapter_id: str,
                        book_id: str, *, order: int, source_id: str,
                        version_id: str, entry_id: str, digest: str,
                        binding_status: str = "healthy",
                        integrity: str = "complete") -> None:
    """A referenced page + source rows + one binding (C-15 §2/§3)."""
    conn.execute(
        "INSERT INTO pages (page_id, chapter_id, sort_order, created_at,"
        " updated_at, source_filename, source_order, source_hash,"
        " source_size_bytes, width, height, managed_original_ref,"
        " source_mode, integrity_status)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 4, 3, NULL, 'referenced', ?)",
        (page_id, chapter_id, order, NOW, NOW, f"{page_id}.png", order, digest,
         10, integrity),
    )
    conn.execute(
        "INSERT INTO page_bindings (binding_id, page_id, project_id,"
        " binding_version, source_id, entry_id, accepted_source_version,"
        " status, authorization_generation, authorized_at, verified_digest,"
        " created_at, updated_at)"
        " VALUES (?, ?, ?, 1, ?, ?, ?, ?, 1, ?, ?, ?, ?)",
        (f"bind-{page_id}", page_id, book_id, source_id, entry_id, version_id,
         binding_status, NOW, digest, NOW, NOW),
    )
    conn.commit()


def add_source_tree(conn: sqlite3.Connection, source_id: str = "s1",
                    version_id: str = "sv1",
                    entries: tuple[tuple[str, str, int], ...] = (("e1", "001.png", 0),),
                    digest: str = "a" * 64) -> None:
    """sources + one current location + one version + entries rows."""
    conn.execute(
        "INSERT INTO sources (source_id, source_kind, created_at, updated_at)"
        " VALUES (?, 'zip', ?, ?)",
        (source_id, NOW, NOW),
    )
    conn.execute(
        "INSERT INTO source_locations (location_id, source_id, registry_id,"
        " authorization_generation, content_digest, volume_serial, file_id,"
        " size_bytes, observed_at, created_at)"
        " VALUES (?, ?, 'reg1', 1, ?, 7, 8, 100, ?, ?)",
        (f"loc-{source_id}", source_id, digest, NOW, NOW),
    )
    conn.execute(
        "INSERT INTO source_versions (version_id, source_id, location_id,"
        " content_digest, size_bytes, observed_at, created_at)"
        " VALUES (?, ?, ?, ?, 100, ?, ?)",
        (version_id, source_id, f"loc-{source_id}", digest, NOW, NOW),
    )
    for entry_id, locator, ordinal in entries:
        conn.execute(
            "INSERT INTO source_entries (source_id, version_id, entry_id,"
            " locator, ordinal, stable_sort_key, content_digest_kind,"
            " content_digest, encoded_digest, size_bytes, width, height,"
            " decoder_name, decoder_version, created_at)"
            " VALUES (?, ?, ?, ?, ?, ?, 'encoded', ?, ?, 9, 5, 5, 'zip', '1.0', ?)",
            (source_id, version_id, entry_id, locator, ordinal,
             f"{ordinal:08d}", digest, digest, NOW),
        )
    conn.commit()
