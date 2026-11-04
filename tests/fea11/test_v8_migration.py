"""AC11-10 evidence: the real v7 -> v8 migration chain.

Every legacy start version (v1..v7) upgrades through the production
``MigrationRunner`` to v8; legacy rows survive, the four new source-sync
tables appear, the schema version records v8, and a runner that only knows
v1..v7 refuses to write (SchemaTooNewError) instead of silently degrading.
"""

from __future__ import annotations

import sqlite3

import pytest

from infrastructure.sqlite.migrator import MigrationRunner, SchemaTooNewError
from infrastructure.sqlite.schema import default_migrations

MIGRATIONS = default_migrations()
LATEST = MIGRATIONS[-1].schema_version
V8_TABLES = (
    "source_sync_plans",
    "source_operations",
    "source_binding_publications",
    "source_revision_lineage",
)


def _table_names(conn):
    return {
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        )
    }


def test_upgrade_from_every_legacy_version_yields_v8_tables():
    assert LATEST >= 8, "the v8 source-sync migration must be part of the chain"
    for start in range(1, LATEST):
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        MigrationRunner(conn, MIGRATIONS[:start]).apply_pending()
        applied = MigrationRunner(conn, MIGRATIONS).apply_pending()
        assert [record.schema_version for record in applied] == list(
            range(start + 1, LATEST + 1)
        )
        names = _table_names(conn)
        for table in V8_TABLES:
            assert table in names, f"{table} missing after upgrading from v{start}"
        version = conn.execute(
            "SELECT value_json FROM application_metadata"
            " WHERE metadata_key = 'schema_version'"
        ).fetchone()
        assert int(str(version[0]).strip('"')) == LATEST
        conn.close()


def test_legacy_rows_survive_the_v8_upgrade():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    MigrationRunner(conn, MIGRATIONS[:7]).apply_pending()
    now = "2026-11-04T00:00:00.000+00:00"
    conn.execute(
        "INSERT INTO books (book_id, title, created_at, updated_at)"
        " VALUES ('b1', 'Legacy', ?, ?)",
        (now, now),
    )
    conn.execute(
        "INSERT INTO chapters (chapter_id, book_id, title, created_at, updated_at)"
        " VALUES ('c1', 'b1', 'Ch', ?, ?)",
        (now, now),
    )
    conn.commit()
    MigrationRunner(conn, MIGRATIONS).apply_pending()
    row = conn.execute(
        "SELECT title FROM books WHERE book_id = 'b1'"
    ).fetchone()
    assert row["title"] == "Legacy"
    chapter = conn.execute(
        "SELECT chapter_id FROM chapters WHERE chapter_id = 'c1'"
    ).fetchone()
    assert chapter is not None
    conn.close()


def test_old_runner_refuses_v8_schema():
    """A Core that only ships v1..v7 must refuse to open the v8 database."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    MigrationRunner(conn, MIGRATIONS).apply_pending()
    legacy = sqlite3.connect(":memory:")
    legacy.row_factory = sqlite3.Row
    # Simulate the old binary by opening a database file that is already v8.
    dump = conn.iterdump()
    for statement in dump:
        legacy.execute(statement)
    legacy.commit()
    conn.close()
    with pytest.raises(SchemaTooNewError):
        MigrationRunner(legacy, MIGRATIONS[:7]).apply_pending()
    legacy.close()


def test_v8_tables_reject_unknown_enum_and_orphan_rows():
    """The new tables keep their CHECK/FK guards (contract shape)."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    MigrationRunner(conn, MIGRATIONS).apply_pending()
    now = "2026-11-04T00:00:00.000+00:00"
    conn.execute(
        "INSERT INTO sources (source_id, source_kind, created_at, updated_at)"
        " VALUES ('s1', 'zip', ?, ?)",
        (now, now),
    )
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO source_sync_plans (plan_id, source_id, kind, state,"
            " plan_digest, body_json, created_at, expires_at)"
            " VALUES ('p1', 's1', 'bogus-kind', 'draft', ?, '{}', ?, ?)",
            ("0" * 64, now, now),
        )
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO source_operations (operation_id, plan_id, plan_digest,"
            " kind, request_digest, state, authorization_digest,"
            " authorization_json, host_receipt_id, created_at, updated_at)"
            " VALUES ('op1', 'p1', ?, 'bogus-kind', ?, 'started', ?, '{}',"
            " 'h1', ?, ?)",
            ("0" * 64, "1" * 64, "2" * 64, now, now),
        )
    conn.close()
