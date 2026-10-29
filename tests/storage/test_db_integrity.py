"""Database-level integrity tests: PRAGMA profile (AC-DB-001/002),
foreign-key enforcement, deferred composite FK for the current pointer, and
short-transaction rollback consistency."""

from __future__ import annotations

import sqlite3

import pytest

from ports.repositories.artifacts import CommitStatus


def test_pragma_profile_matches_d07(db_conn):
    assert db_conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1
    assert db_conn.execute("PRAGMA journal_mode").fetchone()[0] == "wal"
    assert db_conn.execute("PRAGMA busy_timeout").fetchone()[0] == 5000


def test_illegal_foreign_key_write_is_rejected(db_conn):
    with pytest.raises(sqlite3.IntegrityError):
        with db_conn:
            db_conn.execute(
                "INSERT INTO books (book_id, title, created_at, updated_at)"
                " VALUES ('b1', 'ok', '2026-01-01T00:00:00Z', '2026-01-01T00:00:00Z')"
            )
            db_conn.execute(
                "INSERT INTO chapters (chapter_id, book_id, title, created_at, updated_at)"
                " VALUES ('c1', 'missing-book', 'x', '2026-01-01T00:00:00Z',"
                " '2026-01-01T00:00:00Z')"
            )


def test_artifact_type_enum_is_enforced(db_conn, seeded_page):
    with pytest.raises(sqlite3.IntegrityError):
        with db_conn:
            db_conn.execute(
                "INSERT INTO media_artifacts (artifact_id, book_id, chapter_id, page_id,"
                " artifact_type, created_at, updated_at)"
                " VALUES ('a1', ?, ?, ?, 'sticker', '2026-01-01T00:00:00Z',"
                " '2026-01-01T00:00:00Z')",
                (
                    seeded_page["book_id"],
                    seeded_page["chapter_id"],
                    seeded_page["page_id"],
                ),
            )


def test_rollback_after_failed_commit_keeps_database_consistent(
    repo, db_conn, storage_root, artifact_id, make_commit
):
    good = repo.commit_revision(make_commit(artifact_id, b"good", expected_current=None))
    repo.commit_revision(
        make_commit(artifact_id, b"conflict", expected_current=None)
    )  # conflict → rollback, orphan file only

    counts = db_conn.execute(
        "SELECT (SELECT COUNT(*) FROM artifact_revisions) AS revisions,"
        " (SELECT COUNT(*) FROM media_artifacts WHERE current_revision_id IS NULL) AS nulls"
    ).fetchone()
    assert counts["revisions"] == 1
    assert repo.get_current_revision(artifact_id).artifact_revision_id == (
        good.revision.artifact_revision_id
    )
    assert db_conn.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    assert db_conn.execute("PRAGMA foreign_key_check").fetchall() == []


def test_deferred_current_fk_holds_inside_transaction(db_conn, seeded_page):
    """Inserting artifact + revision + pointer in ONE transaction satisfies
    the deferrable composite FK, mirroring the repository commit order."""
    now = "2026-01-01T00:00:00.000+00:00"
    with db_conn:
        db_conn.execute(
            "INSERT INTO media_artifacts (artifact_id, book_id, chapter_id, page_id,"
            " artifact_type, created_at, updated_at) VALUES ('a-ok', ?, ?, ?, 'original', ?, ?)",
            (
                seeded_page["book_id"],
                seeded_page["chapter_id"],
                seeded_page["page_id"],
                now,
                now,
            ),
        )
        db_conn.execute(
            "INSERT INTO artifact_revisions (artifact_revision_id, artifact_id, revision_no,"
            " managed_path, file_hash, mime_type, size_bytes, created_at)"
            " VALUES ('r-ok', 'a-ok', 1, 'b/c/original/r.png', 'h', 'image/png', 3, ?)",
            (now,),
        )
        db_conn.execute(
            "UPDATE media_artifacts SET current_revision_id = 'r-ok' WHERE artifact_id = 'a-ok'"
        )
    assert db_conn.execute("PRAGMA foreign_key_check").fetchall() == []


def test_established_current_cannot_be_cleared_to_null(
    repo, db_conn, artifact_id, make_commit
):
    """R-106: TASK-002 §2.1 forbids changing an established current pointer;
    the composite deferred FK cannot see the NULL direction, so a DB trigger
    (not an application-layer guard) rejects clearing it."""
    committed = repo.commit_revision(make_commit(artifact_id, b"v1", expected_current=None))
    assert committed.status is CommitStatus.COMMITTED
    assert repo.get_current_revision(artifact_id) is not None

    with pytest.raises(sqlite3.IntegrityError):
        with db_conn:
            db_conn.execute(
                "UPDATE media_artifacts SET current_revision_id = NULL WHERE artifact_id = ?",
                (artifact_id,),
            )

    # State untouched after the rejected attempt.
    assert repo.get_current_revision(artifact_id).artifact_revision_id == (
        committed.revision.artifact_revision_id
    )
    assert db_conn.execute("PRAGMA integrity_check").fetchone()[0] == "ok"


def test_first_version_null_current_still_legal(db_conn, seeded_page):
    """The NULL direction stays open before any revision exists (§2.1:
    'empty only means no usable version yet')."""
    now = "2026-01-01T00:00:00.000+00:00"
    with db_conn:
        db_conn.execute(
            "INSERT INTO media_artifacts (artifact_id, book_id, chapter_id, page_id,"
            " artifact_type, created_at, updated_at) VALUES ('a-null', ?, ?, ?, 'mask', ?, ?)",
            (
                seeded_page["book_id"],
                seeded_page["chapter_id"],
                seeded_page["page_id"],
                now,
                now,
            ),
        )
        db_conn.execute(
            "UPDATE media_artifacts SET current_revision_id = NULL WHERE artifact_id = 'a-null'"
        )
    row = db_conn.execute(
        "SELECT current_revision_id FROM media_artifacts WHERE artifact_id = 'a-null'"
    ).fetchone()
    assert row["current_revision_id"] is None
