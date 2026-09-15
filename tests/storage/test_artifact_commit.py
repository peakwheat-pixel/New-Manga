"""Artifact atomic commit tests: TASK-002 §8.1, AC-ART-001/002/003,
AC-REV-001/002 and the task failure matrix (write failure, crash before DB
commit, transaction failure, duplicate commit, illegal FK, cross-artifact
current reference)."""

from __future__ import annotations

import sqlite3

import pytest

from infrastructure.filesystem.managed_storage import ManagedFileStorage
from infrastructure.sqlite.artifacts import SqliteArtifactRepository
from ports.repositories.artifacts import (
    ArtifactType,
    CommitStatus,
    ContentProvider,
    NewArtifact,
    PendingArtifactCommit,
)


def _sha256(content: bytes) -> str:
    import hashlib

    return hashlib.sha256(content).hexdigest()


class FlakyCommitConnection:
    """Proxy that fails exactly one ``commit()`` to simulate a crash after
    the artifact file was published but before the DB transaction commits
    (AC-ART-002)."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn
        self.fail_next_commit = True

    def commit(self):
        if self.fail_next_commit:
            self.fail_next_commit = False
            raise sqlite3.OperationalError("injected crash before metadata commit")
        return self._conn.commit()

    def rollback(self):
        return self._conn.rollback()

    def execute(self, *args, **kwargs):
        return self._conn.execute(*args, **kwargs)

    def __enter__(self):
        self._conn.__enter__()
        return self

    def __exit__(self, *args):
        return self._conn.__exit__(*args)


def test_successful_commit_creates_revision_and_moves_current(
    repo, artifact_id, storage_root, make_commit
):
    first_bytes = b"render-v1"
    outcome = repo.commit_revision(
        make_commit(artifact_id, first_bytes, expected_current=None)
    )
    assert outcome.status is CommitStatus.COMMITTED
    assert outcome.revision.revision_no == 1

    current = repo.get_current_revision(artifact_id)
    assert current.artifact_revision_id == outcome.revision.artifact_revision_id
    published = storage_root / outcome.revision.managed_path.replace("/", "/")
    assert published.is_file()
    assert published.read_bytes() == first_bytes

    # AC-REV-001: a successful rerun keeps the old revision and re-points current.
    second_bytes = b"render-v2"
    second = repo.commit_revision(
        make_commit(artifact_id, second_bytes, expected_current=current.artifact_revision_id)
    )
    assert second.status is CommitStatus.COMMITTED
    assert second.revision.revision_no == 2
    revisions = repo.list_revisions(artifact_id)
    assert [r.revision_no for r in revisions] == [1, 2]
    assert repo.get_current_revision(artifact_id).artifact_revision_id == (
        second.revision.artifact_revision_id
    )
    assert (storage_root / revisions[0].managed_path).is_file()


def test_current_file_hash_is_verifiable(repo, artifact_id, storage_root, make_commit):
    # AC-ART-003: the current artifact carries a verifiable hash.
    content = b"\x89PNG-hash-me"
    outcome = repo.commit_revision(
        make_commit(artifact_id, content, expected_current=None)
    )
    current = repo.get_current_revision(artifact_id)
    on_disk = (storage_root / current.managed_path).read_bytes()
    assert current.file_hash == _sha256(on_disk) == _sha256(content)
    assert current.size_bytes == len(content)


def test_crash_before_metadata_commit_keeps_old_current(
    repo, db_conn, storage_root, artifact_id, make_commit
):
    first = repo.commit_revision(make_commit(artifact_id, b"v1", expected_current=None))
    assert first.status is CommitStatus.COMMITTED

    flaky = FlakyCommitConnection(db_conn)
    guarded = SqliteArtifactRepository(flaky, ManagedFileStorage(storage_root))
    outcome = guarded.commit_revision(
        make_commit(artifact_id, b"v2-orphan", expected_current=first.revision.artifact_revision_id)
    )

    assert outcome.status is CommitStatus.DB_FAILED
    assert outcome.error_code == "COMMIT_CONFLICT"
    # AC-ART-002: old current unchanged, no new revision rows.
    assert repo.get_current_revision(artifact_id).artifact_revision_id == (
        first.revision.artifact_revision_id
    )
    count = db_conn.execute(
        "SELECT COUNT(*) AS n FROM artifact_revisions WHERE artifact_id = ?", (artifact_id,)
    ).fetchone()["n"]
    assert count == 1
    # The published file exists but the database never references it.
    orphan = storage_root / outcome.orphan_paths[0]
    assert orphan.is_file()
    referenced = db_conn.execute(
        "SELECT COUNT(*) AS n FROM artifact_revisions WHERE managed_path = ?",
        (outcome.orphan_paths[0],),
    ).fetchone()["n"]
    assert referenced == 0
    assert db_conn.execute("PRAGMA integrity_check").fetchone()[0] == "ok"


def test_stale_expected_current_conflicts_without_touching_state(
    repo, artifact_id, storage_root, make_commit
):
    v1 = repo.commit_revision(make_commit(artifact_id, b"v1", expected_current=None))
    repo.commit_revision(
        make_commit(artifact_id, b"v2", expected_current=v1.revision.artifact_revision_id)
    )
    outcome = repo.commit_revision(
        make_commit(artifact_id, b"v3-late", expected_current=v1.revision.artifact_revision_id)
    )
    assert outcome.status is CommitStatus.CONFLICT
    assert outcome.error_code == "INPUT_REVISION_CHANGED"
    assert repo.get_current_revision(artifact_id).revision_no == 2
    assert len(repo.list_revisions(artifact_id)) == 2
    assert (storage_root / outcome.orphan_paths[0]).is_file()
    assert outcome.orphan_paths[0] not in [
        r.managed_path for r in repo.list_revisions(artifact_id)
    ]


def test_first_commit_requires_missing_current(repo, artifact_id, make_commit):
    repo.commit_revision(make_commit(artifact_id, b"v1", expected_current=None))
    stale_first = repo.commit_revision(
        make_commit(artifact_id, b"again", expected_current=None)
    )
    assert stale_first.status is CommitStatus.CONFLICT


def test_write_failure_leaves_no_trace(repo, db_conn, artifact_id, make_commit):
    outcome = repo.commit_revision(
        PendingArtifactCommit(
            artifact_id=artifact_id,
            content_provider=ContentProvider(error=OSError("disk blown")),
            mime_type="image/png",
            expected_current_revision_id=None,
        )
    )
    assert outcome.status is CommitStatus.WRITE_FAILED
    assert outcome.error_code == "ARTIFACT_WRITE_FAILED"
    assert repo.get_artifact(artifact_id).current_revision_id is None
    assert (
        db_conn.execute("SELECT COUNT(*) AS n FROM artifact_revisions").fetchone()["n"] == 0
    )


def test_declared_hash_mismatch_rejects_before_publish(repo, artifact_id, make_commit):
    outcome = repo.commit_revision(
        make_commit(artifact_id, b"real-bytes", expected_current=None,
                    expected_sha256=_sha256(b"different-bytes"))
    )
    assert outcome.status is CommitStatus.HASH_MISMATCH
    assert outcome.error_code == "ARTIFACT_HASH_MISMATCH"
    assert repo.get_artifact(artifact_id).current_revision_id is None
    assert outcome.orphan_paths == ()


def test_duplicate_revision_no_is_rejected(repo, db_conn, artifact_id, make_commit):
    committed = repo.commit_revision(make_commit(artifact_id, b"v1", expected_current=None))
    assert committed.status is CommitStatus.COMMITTED
    with pytest.raises(sqlite3.IntegrityError):
        with db_conn:
            db_conn.execute(
                "INSERT INTO artifact_revisions (artifact_revision_id, artifact_id,"
                " revision_no, managed_path, file_hash, mime_type, size_bytes, created_at)"
                " VALUES (?, ?, ?, 'dup.png', 'h', 'image/png', 1, '2026-01-01')",
                ("dup" + "0" * 26, artifact_id, committed.revision.revision_no),
            )


def test_cross_artifact_current_pointer_is_rejected(
    repo, db_conn, seeded_page, artifact_id, make_commit
):
    other_id = repo.create_artifact(
        NewArtifact(
            book_id=seeded_page["book_id"],
            chapter_id=seeded_page["chapter_id"],
            page_id=seeded_page["page_id"],
            artifact_type=ArtifactType.CLEAN,
        )
    ).artifact_id
    committed = repo.commit_revision(make_commit(other_id, b"clean", expected_current=None))
    with pytest.raises(sqlite3.IntegrityError):
        with db_conn:
            db_conn.execute(
                "UPDATE media_artifacts SET current_revision_id = ? WHERE artifact_id = ?",
                (committed.revision.artifact_revision_id, artifact_id),
            )


def test_commit_to_unknown_artifact_is_rejected(make_commit):
    from infrastructure.filesystem.managed_storage import ManagedFileStorage
    from infrastructure.sqlite.connection import open_database
    from infrastructure.sqlite.migrator import MigrationRunner
    from infrastructure.sqlite.schema import default_migrations

    # Standalone mini-environment: no artifact rows at all.
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        conn, _ = open_database(root / "app.db", latest_known_schema_version=1)
        MigrationRunner(conn, default_migrations()).apply_pending()
        repository = SqliteArtifactRepository(conn, ManagedFileStorage(root / "storage"))
        outcome = repository.commit_revision(
            make_commit("missing-artifact", b"x", expected_current=None)
        )
        assert outcome.status is CommitStatus.ARTIFACT_NOT_FOUND
        conn.close()


def test_temp_directory_is_clean_after_success(repo, storage_root, artifact_id, make_commit):
    repo.commit_revision(make_commit(artifact_id, b"clean-exit", expected_current=None))
    temp_dir = storage_root / "temp"
    assert list(temp_dir.iterdir()) == []
