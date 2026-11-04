"""FEA-09 Phase A — v7 source-storage migration (C-15 §1/§2).

Covers: full-chain apply + frozen backfill, failure stays at v6, stale
writer refuses (SchemaTooNewError), the frozen validation callback
(assertions 1–5) including read-only enforcement and the resource
verifier seam, and per-column conservation.
"""

from __future__ import annotations

import sqlite3

import pytest

from infrastructure.sqlite.connection import SchemaTooNewError
from infrastructure.sqlite.migrator import (
    Migration,
    MigrationError,
    MigrationRunner,
    capture_pre_v7_baseline,
    make_v7_validator,
)
from infrastructure.sqlite.schema import default_migrations

NOW = "2026-11-03T00:00:00.000+00:00"


def fresh_v6() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    migrations = default_migrations()
    MigrationRunner(conn, migrations[:6]).apply_pending()
    return conn


def seed_v6_library(conn: sqlite3.Connection) -> None:
    """One book/chapter with a complete managed page, a soft-deleted complete
    page, a half-written row (hash but no managed ref) and a v1 placeholder."""
    conn.execute(
        "INSERT INTO books (book_id, title, created_at, updated_at)"
        " VALUES ('b1', 'Book', ?, ?)", (NOW, NOW))
    conn.execute(
        "INSERT INTO chapters (chapter_id, book_id, title, created_at, updated_at)"
        " VALUES ('c1', 'b1', 'Ch', ?, ?)", (NOW, NOW))
    conn.execute(
        "INSERT INTO pages (page_id, chapter_id, sort_order, created_at,"
        " updated_at, source_filename, source_order, source_hash,"
        " source_size_bytes, width, height, managed_original_ref, page_locked)"
        " VALUES ('p_ok', 'c1', 1, ?, ?, 'a.png', 1, ?, 10, 10, 10, 'managed/a.png', 1)",
        (NOW, NOW, "a" * 64))
    conn.execute(
        "INSERT INTO pages (page_id, chapter_id, sort_order, created_at,"
        " updated_at, source_filename, source_order, source_hash,"
        " source_size_bytes, width, height, managed_original_ref, deleted_at)"
        " VALUES ('p_del', 'c1', 2, ?, ?, 'b.png', 2, ?, 10, 10, 10,"
        " 'managed/b.png', ?)",
        (NOW, NOW, "b" * 64, NOW))
    conn.execute(
        "INSERT INTO pages (page_id, chapter_id, sort_order, created_at,"
        " updated_at, source_hash, width, height)"
        " VALUES ('p_half', 'c1', 3, ?, ?, ?, 10, 10)",
        (NOW, NOW, "c" * 64))
    conn.execute(
        "INSERT INTO pages (page_id, chapter_id, sort_order, created_at, updated_at)"
        " VALUES ('p_v1', 'c1', 4, ?, ?)", (NOW, NOW))
    conn.commit()


def test_v7_full_chain_backfill_and_conservation() -> None:
    conn = fresh_v6()
    seed_v6_library(conn)
    MigrationRunner(conn, default_migrations()).apply_pending()

    assert conn.execute(
        "SELECT MAX(schema_version) FROM schema_migrations").fetchone()[0] == 8
    rows = {
        row["page_id"]: (row["source_mode"], row["integrity_status"])
        for row in conn.execute("SELECT page_id, source_mode, integrity_status FROM pages")
    }
    # C-15 §1 assertion 3 shape: complete set == legacy column predicate set;
    # half-written/placeholder stay incomplete (soft-deleted complete stays
    # complete but invisible).
    assert rows == {
        "p_ok": ("managed", "complete"),
        "p_del": ("managed", "complete"),
        "p_half": ("managed", "incomplete"),
        "p_v1": ("managed", "incomplete"),
    }
    # per-column conservation (assertion 4): order/hash/ref/lock untouched.
    ok = conn.execute(
        "SELECT source_order, sort_order, source_hash, managed_original_ref,"
        " width, height, page_locked FROM pages WHERE page_id='p_ok'").fetchone()
    assert (ok["source_order"], ok["sort_order"], ok["source_hash"],
            ok["managed_original_ref"], ok["width"], ok["height"],
            ok["page_locked"]) == (1, 1, "a" * 64, "managed/a.png", 10, 10, 1)
    assert conn.execute("PRAGMA foreign_key_check").fetchall() == []


def test_v7_failure_stays_at_v6() -> None:
    conn = fresh_v6()
    seed_v6_library(conn)
    v7 = default_migrations()[-1]
    poisoned = Migration(7, v7.migration_name, v7.sql + "\nINSERT INTO no_such_table VALUES (1);")
    runner = MigrationRunner(conn, default_migrations()[:6] + (poisoned,))
    with pytest.raises(sqlite3.Error):
        runner.apply_pending()
    assert conn.execute(
        "SELECT MAX(schema_version) FROM schema_migrations").fetchone()[0] == 6
    assert conn.execute(
        "SELECT COUNT(*) FROM sqlite_master WHERE name='sources'").fetchone()[0] == 0
    # the pre-v7 rows are untouched
    assert conn.execute("SELECT COUNT(*) FROM pages WHERE page_id='p_ok'").fetchone()[0] == 1


def test_stale_writer_refuses_v7_database() -> None:
    conn = fresh_v6()
    MigrationRunner(conn, default_migrations()).apply_pending()
    stale = MigrationRunner(conn, default_migrations()[:6])
    with pytest.raises(SchemaTooNewError):
        stale.apply_pending()


def test_validator_passes_on_conserved_library() -> None:
    conn = fresh_v6()
    seed_v6_library(conn)
    baseline = capture_pre_v7_baseline(conn)
    assert baseline.expected_managed_v_ids == ("p_ok",)

    class OkVerifier:
        def verify_readable(self, paths):
            return []

    MigrationRunner(
        conn, default_migrations(),
        validate=make_v7_validator(baseline, resource_verifier=OkVerifier()),
    ).apply_pending()
    assert conn.execute(
        "SELECT MAX(schema_version) FROM schema_migrations").fetchone()[0] == 8


def test_validator_rejects_tampered_backfill() -> None:
    """If something flips a half-written row to complete during the migration
    transaction, assertion 1/3 must abort with SOURCE_MIGRATION_FAILED and the
    database stays at v6."""
    conn = fresh_v6()
    seed_v6_library(conn)
    baseline = capture_pre_v7_baseline(conn)

    def sabotage(view) -> None:
        view._conn.execute(  # reach through the view deliberately: tamper
            "UPDATE pages SET integrity_status='complete' WHERE page_id='p_half'")
        make_v7_validator(baseline)(view)

    with pytest.raises(MigrationError) as excinfo:
        MigrationRunner(conn, default_migrations(), validate=sabotage).apply_pending()
    assert excinfo.value.code == "SOURCE_MIGRATION_FAILED"
    assert conn.execute(
        "SELECT MAX(schema_version) FROM schema_migrations").fetchone()[0] == 6


def test_validator_enforces_readonly_callback() -> None:
    """C-15 §1: the callback must not write; DML attempts raise
    MigrationValidationError which the runner wraps as typed failure."""
    conn = fresh_v6()
    seed_v6_library(conn)
    baseline = capture_pre_v7_baseline(conn)

    seen = {}

    def malicious(view) -> None:
        seen["first"] = True
        view.execute("DELETE FROM pages WHERE page_id='p_ok'")

    with pytest.raises(MigrationError) as excinfo:
        MigrationRunner(
            conn, default_migrations(),
            validate=lambda view: (malicious(view), make_v7_validator(baseline)(view)),
        ).apply_pending()
    assert "MIGRATION_CALLBACK_FORBIDDEN" in str(excinfo.value)
    assert conn.execute(
        "SELECT MAX(schema_version) FROM schema_migrations").fetchone()[0] == 6
    assert conn.execute("SELECT COUNT(*) FROM pages WHERE page_id='p_ok'").fetchone()[0] == 1


def test_resource_verifier_blocks_missing_original() -> None:
    """C-15 §1 assertion 5: V pages whose original revision path cannot be
    verified fail the migration with SOURCE_MIGRATION_RESOURCE_UNVERIFIED."""
    conn = fresh_v6()
    seed_v6_library(conn)
    # give p_ok a valid original artifact+revision so it lands in the V set
    conn.execute(
        "INSERT INTO media_artifacts (artifact_id, book_id, chapter_id, page_id,"
        " artifact_type, current_revision_id, created_at, updated_at)"
        " VALUES ('art1', 'b1', 'c1', 'p_ok', 'original', 'rev1', ?, ?)", (NOW, NOW))
    conn.execute(
        "INSERT INTO artifact_revisions (artifact_revision_id, artifact_id,"
        " revision_no, managed_path, file_hash, mime_type, size_bytes,"
        " integrity_status, is_pinned, created_at)"
        " VALUES ('rev1', 'art1', 1, 'managed/missing.png', ?, 'image/png', 10,"
        " 'valid', 0, ?)",
        ("a" * 64, NOW))
    conn.commit()
    baseline = capture_pre_v7_baseline(conn)
    assert baseline.v_artifact_page_ids == ("p_ok",)
    assert baseline.v_original_paths == (("p_ok", "managed/missing.png"),)

    class MissingVerifier:
        def verify_readable(self, paths):
            return list(paths)

    with pytest.raises(MigrationError) as excinfo:
        MigrationRunner(
            conn, default_migrations(),
            validate=make_v7_validator(baseline, resource_verifier=MissingVerifier()),
        ).apply_pending()
    assert "SOURCE_MIGRATION_RESOURCE_UNVERIFIED" in str(excinfo.value)
    assert conn.execute(
        "SELECT MAX(schema_version) FROM schema_migrations").fetchone()[0] == 6


def test_resource_verifier_accepts_readable_original() -> None:
    conn = fresh_v6()
    seed_v6_library(conn)
    conn.execute(
        "INSERT INTO media_artifacts (artifact_id, book_id, chapter_id, page_id,"
        " artifact_type, current_revision_id, created_at, updated_at)"
        " VALUES ('art1', 'b1', 'c1', 'p_ok', 'original', 'rev1', ?, ?)", (NOW, NOW))
    conn.execute(
        "INSERT INTO artifact_revisions (artifact_revision_id, artifact_id,"
        " revision_no, managed_path, file_hash, mime_type, size_bytes,"
        " integrity_status, is_pinned, created_at)"
        " VALUES ('rev1', 'art1', 1, 'managed/a.png', ?, 'image/png', 10,"
        " 'valid', 0, ?)",
        ("a" * 64, NOW))
    conn.commit()
    baseline = capture_pre_v7_baseline(conn)

    class OkVerifier:
        def verify_readable(self, paths):
            return []

    MigrationRunner(
        conn, default_migrations(),
        validate=make_v7_validator(baseline, resource_verifier=OkVerifier()),
    ).apply_pending()
    assert conn.execute(
        "SELECT MAX(schema_version) FROM schema_migrations").fetchone()[0] == 8


def test_fresh_database_migrates_with_empty_baseline() -> None:
    """A brand-new database has no pages table at capture time; the empty
    baseline trivially satisfies every frozen assertion."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    baseline = capture_pre_v7_baseline(conn)
    assert baseline.page_rows == ()
    MigrationRunner(
        conn, default_migrations(), validate=make_v7_validator(baseline)
    ).apply_pending()
    assert conn.execute(
        "SELECT MAX(schema_version) FROM schema_migrations").fetchone()[0] == 8

def test_legacy_complete_copy_without_artifact_is_visible_after_v7() -> None:
    """C-15 v1.1 union conservation: the legacy positive-dimension copy set is
    a legitimate post-migration V source even without any artifact row."""
    conn = fresh_v6()
    conn.execute(
        "INSERT INTO books (book_id, title, created_at, updated_at)"
        " VALUES ('b1', 't', ?, ?)", (NOW, NOW),
    )
    conn.execute(
        "INSERT INTO chapters (chapter_id, book_id, title, created_at, updated_at)"
        " VALUES ('c1', 'b1', 'c', ?, ?)", (NOW, NOW),
    )
    conn.execute(
        "INSERT INTO pages (page_id, chapter_id, sort_order, source_hash,"
        " source_size_bytes, width, height, managed_original_ref, created_at, updated_at)"
        " VALUES ('p_copy', 'c1', 0, ?, 1, 10, 10, 'managed/p_copy.png', ?, ?)",
        ("a" * 64, NOW, NOW),
    )
    conn.commit()
    baseline = capture_pre_v7_baseline(conn)
    assert baseline.v_artifact_page_ids == ()
    assert baseline.expected_managed_v_ids == ("p_copy",)

    class OkVerifier:
        def verify_readable(self, paths):
            return []

    MigrationRunner(
        conn, default_migrations(),
        validate=make_v7_validator(baseline, resource_verifier=OkVerifier()),
    ).apply_pending()
    from infrastructure.sqlite.library import SqliteLibraryRepository

    repo = SqliteLibraryRepository(conn)
    result = repo.get_page("p_copy")
    assert result is not None
    assert result.page_id == "p_copy"


def test_validator_requires_resource_verifier_for_non_empty_v() -> None:
    """C-15 v1.1 assertion 5: a non-empty managed V resource set must not skip
    verification via a missing seam."""
    conn = fresh_v6()
    seed_v6_library(conn)
    baseline = capture_pre_v7_baseline(conn)
    assert baseline.v_original_paths
    with pytest.raises(MigrationError, match="SOURCE_MIGRATION_RESOURCE_UNVERIFIED"):
        MigrationRunner(
            conn, default_migrations(), validate=make_v7_validator(baseline)
        ).apply_pending()