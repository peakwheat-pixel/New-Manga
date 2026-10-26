"""SQLite artifact repository implementing the TASK-002 atomic commit.

This repository implements the **artifact current-pointer subset** of the
frozen §8.1 sequence:

    write unique temp file
    → verify (hash/size)
    → atomically move onto the immutable managed path
    → BEGIN IMMEDIATE, re-read the artifact's current revision
    → matches the caller's expectation: insert revision, update pointer
    → mismatch: roll back, keep the old current, report the orphan file

Deliberately NOT part of this slice (registered for later slices, see the
TASK-006 task file): §8.1's Lock re-read (Page/Region Lock tables arrive
with TASK-007/008 and gate planning in TASK-011) and the
``StepResultCandidate`` fallback write (StepRun tables arrive with
TASK-011). Until then a mismatch is reported as a port-level conflict and
no candidate row is created.

Any database failure leaves the previous current unchanged (AC-REV-002,
AC-ART-002); published-but-unreferenced files are returned as orphans for a
later cleanup slice and never overwrite committed revisions.
"""

from __future__ import annotations

import sqlite3
import uuid
from datetime import datetime, timezone

from ports.repositories.artifacts import (
    ArtifactRecord,
    ArtifactRepositoryPort,
    ArtifactRevisionRecord,
    ArtifactType,
    CommitOutcome,
    CommitStatus,
    NewArtifact,
    PendingArtifactCommit,
)
from ports.repositories.storage import ManagedFileStoragePort


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


class SqliteArtifactRepository(ArtifactRepositoryPort):
    def __init__(
        self, conn: sqlite3.Connection, storage: ManagedFileStoragePort
    ) -> None:
        self._conn = conn
        self._storage = storage

    # ------------------------------------------------------------------
    # artifact lifecycle
    # ------------------------------------------------------------------

    def create_artifact(self, artifact: NewArtifact) -> ArtifactRecord:
        artifact_id = uuid.uuid4().hex
        now = _utc_now()
        with self._conn:
            self._conn.execute(
                "INSERT INTO media_artifacts (artifact_id, book_id, chapter_id, page_id,"
                " artifact_type, current_revision_id, created_at, updated_at)"
                " VALUES (?, ?, ?, ?, ?, NULL, ?, ?)",
                (
                    artifact_id,
                    artifact.book_id,
                    artifact.chapter_id,
                    artifact.page_id,
                    artifact.artifact_type.value,
                    now,
                    now,
                ),
            )
        record = self.get_artifact(artifact_id)
        assert record is not None  # freshly inserted in the same connection
        return record

    def get_artifact(self, artifact_id: str) -> ArtifactRecord | None:
        row = self._conn.execute(
            "SELECT artifact_id, book_id, chapter_id, page_id, artifact_type,"
            " current_revision_id, created_at, updated_at"
            " FROM media_artifacts WHERE artifact_id = ?",
            (artifact_id,),
        ).fetchone()
        if row is None:
            return None
        return ArtifactRecord(
            artifact_id=row["artifact_id"],
            book_id=row["book_id"],
            chapter_id=row["chapter_id"],
            page_id=row["page_id"],
            artifact_type=ArtifactType(row["artifact_type"]),
            current_revision_id=row["current_revision_id"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def get_current_revision(self, artifact_id: str) -> ArtifactRevisionRecord | None:
        row = self._conn.execute(
            "SELECT r.* FROM media_artifacts a"
            " JOIN artifact_revisions r ON r.artifact_revision_id = a.current_revision_id"
            " WHERE a.artifact_id = ?",
            (artifact_id,),
        ).fetchone()
        return self._revision_from_row(row) if row else None

    def list_revisions(self, artifact_id: str) -> list[ArtifactRevisionRecord]:
        rows = self._conn.execute(
            "SELECT * FROM artifact_revisions WHERE artifact_id = ? ORDER BY revision_no",
            (artifact_id,),
        ).fetchall()
        return [self._revision_from_row(row) for row in rows]

    # ------------------------------------------------------------------
    # atomic commit (TASK-002 §8.1)
    # ------------------------------------------------------------------

    def commit_revision(self, commit: PendingArtifactCommit) -> CommitOutcome:
        artifact = self.get_artifact(commit.artifact_id)
        if artifact is None:
            # Frozen §10 code; no contract-external error codes are used.
            return CommitOutcome(
                CommitStatus.TARGET_NOT_FOUND, error_code="TARGET_NOT_FOUND"
            )

        # 1. write the unique temp file.
        try:
            temp_handle = self._storage.write_temp(commit.content_provider.read())
        except BaseException as error:  # provider or OS failure, no DB trace
            return CommitOutcome(
                CommitStatus.WRITE_FAILED,
                error_code="ARTIFACT_WRITE_FAILED",
                detail=str(error),
            )

        try:
            # 2. verify the temp content before it becomes official.
            integrity = self._storage.verify_temp(temp_handle)
            if (
                commit.expected_sha256 is not None
                and integrity.sha256 != commit.expected_sha256
            ):
                self._storage.discard_temp(temp_handle)
                return CommitOutcome(
                    CommitStatus.HASH_MISMATCH,
                    error_code="ARTIFACT_HASH_MISMATCH",
                    detail="temp file hash differs from the declared content hash",
                )

            # 3. publish onto the immutable managed path.
            revision_id = uuid.uuid4().hex
            relative_path = self._storage.new_revision_relative_path(
                artifact.book_id,
                artifact.chapter_id,
                artifact.artifact_type.value,
                revision_id,
                commit.file_suffix,
            )
            self._storage.publish(temp_handle, relative_path)
        except OSError as error:
            self._safe_discard(temp_handle)
            return CommitOutcome(
                CommitStatus.WRITE_FAILED,
                error_code="ARTIFACT_WRITE_FAILED",
                detail=str(error),
            )

        # 4. short immediate transaction: re-read, compare, write.
        try:
            return self._commit_in_transaction(commit, artifact.artifact_id, relative_path, integrity)
        except sqlite3.Error as error:
            self._conn.rollback()
            return CommitOutcome(
                CommitStatus.DB_FAILED,
                error_code="COMMIT_CONFLICT",
                detail=str(error),
                orphan_paths=(relative_path,),
            )

    # ------------------------------------------------------------------
    # internals
    # ------------------------------------------------------------------

    def _commit_in_transaction(
        self,
        commit: PendingArtifactCommit,
        artifact_id: str,
        relative_path: str,
        integrity,
    ) -> CommitOutcome:
        conn = self._conn
        # TASK-060 Q-002: same as regions.commit_region_revision — the
        # BEGIN belongs inside the try; failure raises sqlite3.Error which
        # the caller already maps to the typed DB_FAILED outcome.
        try:
            conn.execute("BEGIN IMMEDIATE")
            current = conn.execute(
                "SELECT current_revision_id FROM media_artifacts WHERE artifact_id = ?",
                (artifact_id,),
            ).fetchone()
            actual_current = current["current_revision_id"] if current else None
            if actual_current != commit.expected_current_revision_id:
                conn.rollback()
                return CommitOutcome(
                    CommitStatus.CONFLICT,
                    error_code="INPUT_REVISION_CHANGED",
                    detail=(
                        f"expected current {commit.expected_current_revision_id!r}, "
                        f"database current {actual_current!r}"
                    ),
                    orphan_paths=(relative_path,),
                )

            row = conn.execute(
                "SELECT COALESCE(MAX(revision_no), 0) + 1 AS next_no"
                " FROM artifact_revisions WHERE artifact_id = ?",
                (artifact_id,),
            ).fetchone()
            revision_no = int(row["next_no"])
            now = _utc_now()
            conn.execute(
                "INSERT INTO artifact_revisions (artifact_revision_id, artifact_id,"
                " revision_no, managed_path, file_hash, mime_type, width, height,"
                " size_bytes, integrity_status, last_verified_at, provider_profile_id,"
                " model_name, options_json, source_artifact_revision_id, pipeline_run_id,"
                " step_run_id, provenance_json, is_pinned, created_at)"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'valid', ?, ?, ?, ?, ?, ?, ?, ?, 0, ?)",
                (
                    uuid.uuid4().hex,
                    artifact_id,
                    revision_no,
                    relative_path,
                    integrity.sha256,
                    commit.mime_type,
                    commit.width,
                    commit.height,
                    integrity.size_bytes,
                    now,
                    commit.provider_profile_id,
                    commit.model_name,
                    commit.options_json,
                    commit.source_artifact_revision_id,
                    commit.pipeline_run_id,
                    commit.step_run_id,
                    commit.provenance_json,
                    now,
                ),
            )
            new_revision_id = conn.execute(
                "SELECT artifact_revision_id FROM artifact_revisions"
                " WHERE artifact_id = ? AND revision_no = ?",
                (artifact_id, revision_no),
            ).fetchone()["artifact_revision_id"]
            conn.execute(
                "UPDATE media_artifacts SET current_revision_id = ?, updated_at = ?"
                " WHERE artifact_id = ?",
                (new_revision_id, now, artifact_id),
            )
            conn.commit()
        except sqlite3.Error:
            conn.rollback()
            raise

        revision = conn.execute(
            "SELECT * FROM artifact_revisions WHERE artifact_revision_id = ?",
            (new_revision_id,),
        ).fetchone()
        return CommitOutcome(
            CommitStatus.COMMITTED, revision=self._revision_from_row(revision)
        )

    def _safe_discard(self, temp_handle: str) -> None:
        try:
            self._storage.discard_temp(temp_handle)
        except OSError:
            pass

    def _revision_from_row(self, row: sqlite3.Row) -> ArtifactRevisionRecord:
        return ArtifactRevisionRecord(
            artifact_revision_id=row["artifact_revision_id"],
            artifact_id=row["artifact_id"],
            revision_no=int(row["revision_no"]),
            managed_path=row["managed_path"],
            file_hash=row["file_hash"],
            mime_type=row["mime_type"],
            width=row["width"],
            height=row["height"],
            size_bytes=int(row["size_bytes"]),
            integrity_status=row["integrity_status"],
            is_pinned=bool(row["is_pinned"]),
            created_at=row["created_at"],
        )
