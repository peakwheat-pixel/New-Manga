"""Versioned schema definitions for TASK-006's first storage slice.

Only tables this slice actually uses are created (D03: books/chapters/pages
as the minimal FK chain for artifacts, the artifact revision tables, and the
infrastructure metadata tables). Everything else arrives through later
versioned migrations (TASK-007/008/011...).

The v1 DDL encodes the TASK-002 §2.1 frozen invariant "the current pointer
must reference a revision of the same artifact" as a composite foreign key
``media_artifacts(current_revision_id, artifact_id) →
artifact_revisions(artifact_revision_id, artifact_id)``. It is DEFERRABLE so
the first revision insert and the pointer update can happen in one
transaction.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

SCHEMA_VERSION_V1 = 1

MIGRATION_V1_NAME = "v1__storage_base"

MIGRATION_V1_SQL = """
CREATE TABLE books (
    book_id TEXT PRIMARY KEY CHECK (length(book_id) > 0),
    title TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    deleted_at TEXT
);

CREATE TABLE chapters (
    chapter_id TEXT PRIMARY KEY CHECK (length(chapter_id) > 0),
    book_id TEXT NOT NULL REFERENCES books(book_id),
    title TEXT NOT NULL,
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    deleted_at TEXT
);
CREATE INDEX idx_chapters_book_id ON chapters(book_id);

CREATE TABLE pages (
    page_id TEXT PRIMARY KEY CHECK (length(page_id) > 0),
    chapter_id TEXT NOT NULL REFERENCES chapters(chapter_id),
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    deleted_at TEXT
);
CREATE INDEX idx_pages_chapter_sort ON pages(chapter_id, sort_order);

CREATE TABLE media_artifacts (
    artifact_id TEXT PRIMARY KEY CHECK (length(artifact_id) > 0),
    book_id TEXT NOT NULL REFERENCES books(book_id),
    chapter_id TEXT NOT NULL REFERENCES chapters(chapter_id),
    page_id TEXT NOT NULL REFERENCES pages(page_id),
    artifact_type TEXT NOT NULL CHECK (artifact_type IN (
        'original', 'thumbnail', 'detection_overlay', 'mask', 'clean',
        'translated', 'render_preview', 'export', 'debug_ocr', 'debug_detection')),
    current_revision_id TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (page_id) REFERENCES pages(page_id),
    FOREIGN KEY (current_revision_id, artifact_id) REFERENCES
        artifact_revisions(artifact_revision_id, artifact_id) DEFERRABLE INITIALLY DEFERRED
);
CREATE INDEX idx_media_artifacts_page ON media_artifacts(page_id, artifact_type);

CREATE TABLE artifact_revisions (
    artifact_revision_id TEXT PRIMARY KEY CHECK (length(artifact_revision_id) > 0),
    artifact_id TEXT NOT NULL REFERENCES media_artifacts(artifact_id),
    revision_no INTEGER NOT NULL CHECK (revision_no >= 1),
    managed_path TEXT NOT NULL,
    file_hash TEXT NOT NULL,
    mime_type TEXT NOT NULL,
    width INTEGER,
    height INTEGER,
    size_bytes INTEGER NOT NULL CHECK (size_bytes >= 0),
    integrity_status TEXT NOT NULL DEFAULT 'valid'
        CHECK (integrity_status IN ('unknown', 'valid', 'missing', 'corrupted')),
    last_verified_at TEXT,
    provider_profile_id TEXT,
    model_name TEXT,
    options_json TEXT,
    source_artifact_revision_id TEXT REFERENCES artifact_revisions(artifact_revision_id),
    pipeline_run_id TEXT,
    step_run_id TEXT,
    provenance_json TEXT,
    is_pinned INTEGER NOT NULL DEFAULT 0 CHECK (is_pinned IN (0, 1)),
    created_at TEXT NOT NULL,
    UNIQUE (artifact_id, revision_no),
    UNIQUE (artifact_revision_id, artifact_id)
);
CREATE INDEX idx_artifact_revisions_artifact ON artifact_revisions(artifact_id, revision_no);

CREATE TABLE schema_migrations (
    schema_version INTEGER PRIMARY KEY,
    migration_name TEXT NOT NULL,
    applied_at TEXT NOT NULL,
    checksum TEXT NOT NULL
);

CREATE TABLE application_metadata (
    metadata_key TEXT PRIMARY KEY,
    value_json TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE backup_records (
    backup_id TEXT PRIMARY KEY CHECK (length(backup_id) > 0),
    backup_type TEXT NOT NULL
        CHECK (backup_type IN ('automatic', 'manual', 'pre_migration', 'pre_restore')),
    managed_path TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('pending', 'completed', 'failed')),
    app_version TEXT,
    schema_version INTEGER,
    database_hash TEXT,
    size_bytes INTEGER,
    created_at TEXT NOT NULL,
    completed_at TEXT,
    source_reason TEXT
);
"""


@dataclass(frozen=True)
class Migration:
    schema_version: int
    migration_name: str
    sql: str

    @property
    def checksum(self) -> str:
        return hashlib.sha256(self.sql.encode("utf-8")).hexdigest()


def default_migrations() -> tuple[Migration, ...]:
    return (Migration(SCHEMA_VERSION_V1, MIGRATION_V1_NAME, MIGRATION_V1_SQL),)
