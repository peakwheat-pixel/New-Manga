"""FEA-12-CORE-C04B-INDEX-L4-1 evidence: the real v8 -> v9 migration.

``FEA-12-CORE-C04B-RESIDUAL-3`` moved the artifact membership predicate to
``media_artifacts.book_id = ?`` (C-04b v1.2 §0 第 1 条 / M2-C1 rev 2.15).
``media_artifacts`` only carried ``(page_id, artifact_type)``, so every
book-scoped artifact query degraded from an index ``SEARCH`` to a full
``SCAN ma`` whose cost grew with the WHOLE library artifact count (frozen
record ``doc/plan/FEA-CONTRACT-FROZEN-C04b.md`` §4A ``L-4``). The v9
migration adds exactly one index; v1-v8 stay byte-identical.

Every fixture is real: the production ``MigrationRunner`` builds the database
from the production ``default_migrations()`` chain, and the published
repository methods (never a hand-copied SQL) provide both the ``EXPLAIN QUERY
PLAN`` statements and the equivalence values.
"""

from __future__ import annotations

import inspect
import sqlite3

import pytest

from infrastructure.sqlite.connection import SchemaTooNewError, open_database
from infrastructure.sqlite.library import SqliteLibraryRepository
from infrastructure.sqlite.migrator import Migration, MigrationRunner, read_schema_version
from infrastructure.sqlite.schema import (
    MIGRATION_V9_NAME,
    MIGRATION_V9_SQL,
    SCHEMA_VERSION_V9,
    default_migrations,
)
from ports.repositories.database import SchemaState

MIGRATIONS = default_migrations()
LATEST = MIGRATIONS[-1].schema_version
V8 = MIGRATIONS[:8]
INDEX_NAME = "idx_media_artifacts_book"
NOW = "2026-11-08T00:00:00.000+00:00"

#: v1-v8 are applied history: version, name and SQL checksum (sha256 of the
#: SQL) must never change, or an existing database fails the checksum gate
#: (``migrator.py`` ``_verify_checksum``). Hard-coded so an edit to any
#: applied migration fails this tree instead of shipping silently.
FROZEN_V1_V8 = (
    (1, "v1__storage_base",
     "f68cb4ab8facda4b6e701a934ed14b240bce13c50fe1527a3989de1c987994bd"),
    (2, "v2__library_region_persistence",
     "b984eaeeb5a3a162040d2de458f09ecde1479519d30a48fd7c36118295875d5b"),
    (3, "v3__production_pipeline_persistence",
     "359d97f42cad9cb18d676ffc113abae4e81cb237c4841ef82262a8736518a0c2"),
    (4, "v4__reading_export_storage",
     "c8e0b4899026784bda958c49e6e1d13896f7ac083dafd1acf04a030677a88394"),
    (5, "v5__detach_pipeline_history",
     "6b12ad337ab2fe0fb0b4d6bdd6835a69166c080a36fc1ac80326ff4faa03597c"),
    (6, "v6__plugin_runtime",
     "eef3ddb5dadd819e3af6de030aec8edff010e1a0d012409bf14330fb5fb43331"),
    (7, "v7__source_storage",
     "abbf4e5f9415f392596faebc38690b6a58dd7f96941f51802621b68a2a3f8a91"),
    (8, "v8__source_sync",
     "d8e76e80a5abadcb335edc7be75c1cffbd8e5311d45d2fe3fa5d49f4c82b21d1"),
)


# ---------------------------------------------------------------------------
# helpers (production migrations only; no hand-built DDL)
# ---------------------------------------------------------------------------


def _connect(db_path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _max_version(conn: sqlite3.Connection) -> int:
    row = conn.execute("SELECT MAX(schema_version) FROM schema_migrations").fetchone()
    return int(row[0])


def _metadata_version(conn: sqlite3.Connection) -> int:
    row = conn.execute(
        "SELECT value_json FROM application_metadata WHERE metadata_key = 'schema_version'"
    ).fetchone()
    return int(str(row[0]).strip('"'))


def _index_names(conn: sqlite3.Connection, table: str = "media_artifacts") -> set[str]:
    return {row["name"] for row in conn.execute(f"PRAGMA index_list({table})")}


def _explain(conn: sqlite3.Connection, sql: str, params: tuple) -> str:
    rows = conn.execute("EXPLAIN QUERY PLAN " + sql, params).fetchall()
    return " | ".join(str(row["detail"]) for row in rows)


def _production_plan(
    conn: sqlite3.Connection, repo: SqliteLibraryRepository, method_name: str, book_id: str
) -> tuple[str, str]:
    """Run a published repository method and EXPLAIN the SQL it really sent."""
    seen: list[str] = []
    conn.set_trace_callback(seen.append)
    try:
        getattr(repo, method_name)(book_id)
    finally:
        conn.set_trace_callback(None)
    assert len(seen) == 1, f"{method_name} sent {len(seen)} statements: {seen}"
    sql = seen[0]
    return sql, _explain(conn, sql, (book_id,) * sql.count("?"))


def _seed_v8_library(conn: sqlite3.Connection) -> None:
    """Two books; current and current-less artifacts; one pinned revision."""
    for book_id, title in (("book-a", "A"), ("book-b", "B")):
        conn.execute(
            "INSERT INTO books (book_id, title, created_at, updated_at)"
            " VALUES (?, ?, ?, ?)",
            (book_id, title, NOW, NOW),
        )
    for chapter_id, book_id in (("c-a", "book-a"), ("c-b", "book-b")):
        conn.execute(
            "INSERT INTO chapters (chapter_id, book_id, title, sort_order,"
            " created_at, updated_at) VALUES (?, ?, 'Ch', 1, ?, ?)",
            (chapter_id, book_id, NOW, NOW),
        )
    for page_id, chapter_id, sort_order in (
        ("p-a1", "c-a", 1), ("p-a2", "c-a", 2), ("p-b1", "c-b", 1)
    ):
        conn.execute(
            "INSERT INTO pages (page_id, chapter_id, sort_order, created_at, updated_at)"
            " VALUES (?, ?, ?, ?, ?)",
            (page_id, chapter_id, sort_order, NOW, NOW),
        )
    for artifact_id, book_id, chapter_id, page_id, artifact_type, current in (
        ("ma-a1", "book-a", "c-a", "p-a1", "original", "ar-a1"),
        ("ma-a2", "book-a", "c-a", "p-a1", "thumbnail", None),
        ("ma-a3", "book-a", "c-a", "p-a2", "original", "ar-a3"),
        ("ma-b1", "book-b", "c-b", "p-b1", "original", "ar-b1"),
    ):
        conn.execute(
            "INSERT INTO media_artifacts (artifact_id, book_id, chapter_id, page_id,"
            " artifact_type, current_revision_id, created_at, updated_at)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (artifact_id, book_id, chapter_id, page_id, artifact_type, current, NOW, NOW),
        )
    for revision_id, artifact_id, pinned in (
        ("ar-a1", "ma-a1", 0), ("ar-a3", "ma-a3", 1), ("ar-b1", "ma-b1", 0)
    ):
        conn.execute(
            "INSERT INTO artifact_revisions (artifact_revision_id, artifact_id,"
            " revision_no, managed_path, file_hash, mime_type, size_bytes,"
            " integrity_status, is_pinned, created_at)"
            " VALUES (?, ?, 1, ?, ?, 'image/png', 10, 'valid', ?, ?)",
            (revision_id, artifact_id, f"managed/{revision_id}.png", "a" * 64, pinned, NOW),
        )
    conn.commit()


def _snapshot(conn: sqlite3.Connection, repo: SqliteLibraryRepository) -> dict:
    return {
        "pointers_a": repo.list_book_artifact_current_pointers("book-a"),
        "pointers_b": repo.list_book_artifact_current_pointers("book-b"),
        "revision_ids_a": repo.list_book_artifact_revision_ids("book-a"),
        "revision_ids_b": repo.list_book_artifact_revision_ids("book-b"),
        "pinned_a": repo.list_book_pinned_revision_ids("book-a"),
        "pinned_b": repo.list_book_pinned_revision_ids("book-b"),
        "counts": {
            table: conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            for table in (
                "books", "chapters", "pages", "media_artifacts", "artifact_revisions"
            )
        },
        "rows": [
            tuple(row)
            for row in conn.execute(
                "SELECT artifact_id, book_id, current_revision_id FROM media_artifacts"
                " ORDER BY artifact_id"
            )
        ],
    }


# ---------------------------------------------------------------------------
# AC-1: migration shape and byte preservation of v1-v8
# ---------------------------------------------------------------------------


def test_v9_shape_and_v1_v8_bytes_are_frozen() -> None:
    assert SCHEMA_VERSION_V9 == 9
    assert MIGRATION_V9_NAME == "v9__media_artifacts_book_index"
    assert MIGRATION_V9_SQL == (
        "CREATE INDEX idx_media_artifacts_book ON media_artifacts(book_id);"
    )
    # Fail-loud by design: the version gate already provides idempotence, so a
    # pre-existing conflicting index must abort instead of "silently already
    # indexed" (frozen record §4A L-4 / scope review §2.4).
    assert "IF NOT EXISTS" not in MIGRATION_V9_SQL.upper()
    assert len(MIGRATIONS) == 9
    assert [m.schema_version for m in MIGRATIONS] == list(range(1, 10))
    assert tuple(
        (m.schema_version, m.migration_name, m.checksum) for m in MIGRATIONS[:8]
    ) == FROZEN_V1_V8
    assert MIGRATIONS[-1] == Migration(SCHEMA_VERSION_V9, MIGRATION_V9_NAME, MIGRATION_V9_SQL)


# ---------------------------------------------------------------------------
# AC-2: real upgrades from every legacy start version, conservation, idempotence
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("start", range(1, 9), ids=[f"v{start}" for start in range(1, 9)])
def test_upgrade_from_legacy_version_creates_the_book_index(tmp_path, start: int) -> None:
    db = tmp_path / f"legacy-v{start}.db"
    conn = _connect(db)
    MigrationRunner(conn, MIGRATIONS[:start]).apply_pending()
    applied = MigrationRunner(conn, MIGRATIONS).apply_pending()
    assert [record.schema_version for record in applied] == list(
        range(start + 1, LATEST + 1)
    )
    assert applied[-1].schema_version == 9
    assert applied[-1].migration_name == MIGRATION_V9_NAME
    assert _max_version(conn) == 9
    assert _metadata_version(conn) == 9
    assert INDEX_NAME in _index_names(conn)
    assert [row["name"] for row in conn.execute(f"PRAGMA index_info({INDEX_NAME})")] == [
        "book_id"
    ]
    # Idempotence comes from the version gate, not from IF NOT EXISTS.
    assert MigrationRunner(conn, MIGRATIONS).apply_pending() == []
    conn.close()

    # A second open of the already-migrated file neither re-runs nor errors.
    reopened, opened = open_database(db, latest_known_schema_version=LATEST)
    assert opened.state is SchemaState.READY
    assert opened.schema_version == 9
    assert opened.writable is True
    assert MigrationRunner(reopened, MIGRATIONS).apply_pending() == []
    assert INDEX_NAME in _index_names(reopened)
    reopened.close()


def test_v8_upgrade_preserves_rows_and_query_results(tmp_path) -> None:
    db = tmp_path / "library.db"
    conn = _connect(db)
    MigrationRunner(conn, V8).apply_pending()
    _seed_v8_library(conn)
    repo = SqliteLibraryRepository(conn)
    before = _snapshot(conn, repo)
    assert before["pointers_a"], "seed must produce non-trivial preview rows"

    applied = MigrationRunner(conn, MIGRATIONS).apply_pending()
    assert [record.schema_version for record in applied] == [9]
    assert _max_version(conn) == 9
    assert _metadata_version(conn) == 9
    assert INDEX_NAME in _index_names(conn)
    assert _snapshot(conn, repo) == before
    conn.close()


def test_book_delete_inventory_is_unchanged_by_the_index(tmp_path) -> None:
    db = tmp_path / "inventory.db"
    conn = _connect(db)
    MigrationRunner(conn, V8).apply_pending()
    _seed_v8_library(conn)
    repo = SqliteLibraryRepository(conn)
    before = repo.book_delete_inventory("book-a", [], storage=None)
    assert before is not None
    assert before["artifacts"] == 3

    MigrationRunner(conn, MIGRATIONS).apply_pending()
    after = repo.book_delete_inventory("book-a", [], storage=None)
    assert after == before
    conn.close()


# ---------------------------------------------------------------------------
# AC-2: failure paths stay fail-closed
# ---------------------------------------------------------------------------


def test_v9_failure_leaves_the_database_at_v8_without_the_index(tmp_path) -> None:
    db = tmp_path / "failure.db"
    conn = _connect(db)
    MigrationRunner(conn, V8).apply_pending()
    _seed_v8_library(conn)
    v9 = MIGRATIONS[-1]
    poisoned = Migration(
        9, v9.migration_name, v9.sql + "\nINSERT INTO no_such_table VALUES (1);"
    )
    with pytest.raises(sqlite3.Error):
        MigrationRunner(conn, V8 + (poisoned,)).apply_pending()
    assert read_schema_version(conn) == 8
    assert INDEX_NAME not in _index_names(conn)
    # v8 stays usable: no half-applied DDL residue.
    conn.execute(
        "INSERT INTO books (book_id, title, created_at, updated_at)"
        " VALUES ('book-c', 'C', ?, ?)",
        (NOW, NOW),
    )
    conn.commit()
    assert read_schema_version(conn) == 8
    conn.close()


def test_old_v8_runner_refuses_the_v9_database(tmp_path) -> None:
    db = tmp_path / "stale.db"
    conn = _connect(db)
    MigrationRunner(conn, MIGRATIONS).apply_pending()
    stale = _connect(db)
    with pytest.raises(SchemaTooNewError):
        MigrationRunner(stale, V8).apply_pending()
    assert _max_version(stale) == 9
    stale.close()
    conn.close()


def test_open_database_reports_too_new_to_a_v8_reader(tmp_path) -> None:
    db = tmp_path / "too-new.db"
    conn = _connect(db)
    MigrationRunner(conn, MIGRATIONS).apply_pending()
    conn.close()

    opened_conn, opened = open_database(db, latest_known_schema_version=8)
    assert opened.state is SchemaState.TOO_NEW
    assert opened.schema_version == 9
    assert opened.writable is False
    with pytest.raises(sqlite3.OperationalError):
        opened_conn.execute(
            "INSERT INTO books (book_id, title, created_at, updated_at)"
            " VALUES ('book-x', 'X', ?, ?)",
            (NOW, NOW),
        )
    opened_conn.close()


# ---------------------------------------------------------------------------
# AC-3: the published statements become index searches; results stay identical
# ---------------------------------------------------------------------------


def test_preview_statement_scans_on_v8_and_searches_the_index_on_v9(tmp_path) -> None:
    db = tmp_path / "plan-preview.db"
    conn = _connect(db)
    MigrationRunner(conn, V8).apply_pending()
    _seed_v8_library(conn)
    repo = SqliteLibraryRepository(conn)

    preview_sql_v8, plan_v8 = _production_plan(
        conn, repo, "list_book_artifact_current_pointers", "book-a"
    )
    assert "SCAN ma" in plan_v8
    assert INDEX_NAME not in plan_v8
    rows_v8 = repo.list_book_artifact_current_pointers("book-a")

    MigrationRunner(conn, MIGRATIONS).apply_pending()

    preview_sql_v9, plan_v9 = _production_plan(
        conn, repo, "list_book_artifact_current_pointers", "book-a"
    )
    assert preview_sql_v9 == preview_sql_v8, "v9 must not edit the preview statement"
    assert "SEARCH ma USING INDEX" in plan_v9
    assert INDEX_NAME in plan_v9
    assert "SCAN" not in plan_v9
    assert repo.list_book_artifact_current_pointers("book-a") == rows_v8
    conn.close()


def test_delete_face_enumeration_and_count_use_the_book_index(tmp_path) -> None:
    db = tmp_path / "plan-delete.db"
    conn = _connect(db)
    MigrationRunner(conn, V8).apply_pending()
    _seed_v8_library(conn)
    repo = SqliteLibraryRepository(conn)
    revision_ids_before = repo.list_book_artifact_revision_ids("book-a")
    pinned_before = repo.list_book_pinned_revision_ids("book-a")

    MigrationRunner(conn, MIGRATIONS).apply_pending()

    for method in ("list_book_artifact_revision_ids", "list_book_pinned_revision_ids"):
        _, plan = _production_plan(conn, repo, method, "book-a")
        assert INDEX_NAME in plan, f"{method}: {plan}"
        assert "SCAN" not in plan, f"{method}: {plan}"

    assert repo.list_book_artifact_revision_ids("book-a") == revision_ids_before
    assert repo.list_book_pinned_revision_ids("book-a") == pinned_before

    # The transaction's DELETE and the inventory COUNT share the predicate;
    # both literals are the production ones, asserted against library.py.
    count_sql = "SELECT COUNT(*) FROM media_artifacts WHERE book_id = ?"
    delete_sql = "DELETE FROM media_artifacts WHERE book_id = ?"
    library_source = inspect.getsource(SqliteLibraryRepository)
    assert count_sql in library_source
    assert delete_sql in library_source

    count_plan = _explain(conn, count_sql, ("book-a",))
    assert INDEX_NAME in count_plan, count_plan
    assert "SCAN" not in count_plan, count_plan
    delete_plan = _explain(conn, delete_sql, ("book-a",))
    assert INDEX_NAME in delete_plan, delete_plan
    assert "SCAN" not in delete_plan, delete_plan
    conn.close()
