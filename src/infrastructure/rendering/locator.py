"""SQLite read-only locator for a page's current artifact of a type.

The frozen ``ArtifactRepositoryPort`` (outside this slice's paths) has no
page-level query; rendering needs "the page's current Clean / Translated
artifact", so this small read adapter answers exactly that without
touching the shared port file.
"""

from __future__ import annotations

import sqlite3

from ports.repositories.artifacts import (
    ArtifactRecord,
    ArtifactRevisionRecord,
    ArtifactType,
)


class SqlitePageArtifactLocator:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def locate_current(
        self, page_id: str, artifact_type: ArtifactType
    ) -> tuple[ArtifactRecord, ArtifactRevisionRecord] | None:
        row = self._conn.execute(
            "SELECT a.artifact_id, a.book_id, a.chapter_id, a.page_id,"
            " a.artifact_type, a.current_revision_id, a.created_at, a.updated_at"
            " FROM media_artifacts a"
            " WHERE a.page_id = ? AND a.artifact_type = ?"
            " ORDER BY a.created_at LIMIT 1",
            (page_id, artifact_type.value),
        ).fetchone()
        if row is None:
            return None
        record = ArtifactRecord(
            artifact_id=row["artifact_id"],
            book_id=row["book_id"],
            chapter_id=row["chapter_id"],
            page_id=row["page_id"],
            artifact_type=ArtifactType(row["artifact_type"]),
            current_revision_id=row["current_revision_id"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
        if record.current_revision_id is None:
            return None
        revision_row = self._conn.execute(
            "SELECT * FROM artifact_revisions"
            " WHERE artifact_revision_id = ?",
            (record.current_revision_id,),
        ).fetchone()
        if revision_row is None:
            return None
        revision = ArtifactRevisionRecord(
            artifact_revision_id=revision_row["artifact_revision_id"],
            artifact_id=revision_row["artifact_id"],
            revision_no=int(revision_row["revision_no"]),
            managed_path=revision_row["managed_path"],
            file_hash=revision_row["file_hash"],
            mime_type=revision_row["mime_type"],
            width=revision_row["width"],
            height=revision_row["height"],
            size_bytes=int(revision_row["size_bytes"]),
            integrity_status=revision_row["integrity_status"],
            is_pinned=bool(revision_row["is_pinned"]),
            created_at=revision_row["created_at"],
        )
        return record, revision
