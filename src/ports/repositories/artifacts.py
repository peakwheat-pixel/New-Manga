"""Artifact persistence port.

Implements the infrastructure subset of the TASK-002 frozen contract
(§2.1 current pointers, §8.1 atomic commit, §10 error codes) for
``MediaArtifact`` / ``ArtifactRevision``. Region/Constraint revisions and
StepResultCandidate persistence belong to later slices and are intentionally
out of scope here.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Protocol


class ArtifactType(str, Enum):
    """Allowed ``media_artifacts.artifact_type`` values (D03 §16.1)."""

    ORIGINAL = "original"
    THUMBNAIL = "thumbnail"
    DETECTION_OVERLAY = "detection_overlay"
    MASK = "mask"
    CLEAN = "clean"
    TRANSLATED = "translated"
    RENDER_PREVIEW = "render_preview"
    EXPORT = "export"
    DEBUG_OCR = "debug_ocr"
    DEBUG_DETECTION = "debug_detection"


@dataclass(frozen=True)
class NewArtifact:
    """Input for creating a ``media_artifacts`` row with no current revision."""

    book_id: str
    chapter_id: str
    page_id: str
    artifact_type: ArtifactType


@dataclass(frozen=True)
class ArtifactRecord:
    artifact_id: str
    book_id: str
    chapter_id: str
    page_id: str
    artifact_type: ArtifactType
    current_revision_id: str | None
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class ArtifactRevisionRecord:
    artifact_revision_id: str
    artifact_id: str
    revision_no: int
    managed_path: str
    file_hash: str
    mime_type: str
    width: int | None
    height: int | None
    size_bytes: int
    integrity_status: str
    is_pinned: bool
    created_at: str


@dataclass(frozen=True)
class PendingArtifactCommit:
    """A prepared artifact result waiting for the atomic compare-and-write.

    ``expected_current_revision_id`` is the caller's view of the artifact's
    current revision (``None`` only when the artifact must still have no
    current revision, i.e. the first version). ``expected_sha256`` lets the
    caller pin the content hash produced by the pipeline step; mismatch fails
    the commit before anything is published.
    """

    artifact_id: str
    content_provider: "ContentProvider"
    mime_type: str
    expected_current_revision_id: str | None
    expected_sha256: str | None = None
    width: int | None = None
    height: int | None = None
    provider_profile_id: str | None = None
    model_name: str | None = None
    options_json: str | None = None
    source_artifact_revision_id: str | None = None
    pipeline_run_id: str | None = None
    step_run_id: str | None = None
    provenance_json: str | None = None
    file_suffix: str = ".bin"


@dataclass(frozen=True)
class ContentProvider:
    """Supplies the raw bytes for a revision.

    The provider is invoked exactly once per commit attempt; failures are
    mapped to ``ARTIFACT_WRITE_FAILED`` and leave no database trace.
    """

    payload: bytes = field(repr=False, default=b"")
    error: BaseException | None = None

    def read(self) -> bytes:
        if self.error is not None:
            raise self.error
        return self.payload


class CommitStatus(str, Enum):
    """Terminal outcomes of ``commit_revision`` (TASK-002 §8.1/§10)."""

    COMMITTED = "committed"
    CONFLICT = "conflict"
    WRITE_FAILED = "write_failed"
    HASH_MISMATCH = "hash_mismatch"
    ARTIFACT_NOT_FOUND = "artifact_not_found"
    DB_FAILED = "db_failed"


@dataclass(frozen=True)
class CommitOutcome:
    status: CommitStatus
    revision: ArtifactRevisionRecord | None = None
    error_code: str | None = None
    detail: str | None = None
    #: Files published to immutable storage but not referenced by the
    #: database after a conflict or DB failure. Orphan cleanup itself is a
    #: later infrastructure slice (TASK-002 §8.1).
    orphan_paths: tuple[str, ...] = ()


class ArtifactRepositoryPort(Protocol):
    """Persistence port for media artifacts and their revisions."""

    def create_artifact(self, artifact: NewArtifact) -> ArtifactRecord:
        """Create an artifact row with no current revision yet."""
        ...

    def get_artifact(self, artifact_id: str) -> ArtifactRecord | None:
        ...

    def get_current_revision(self, artifact_id: str) -> ArtifactRevisionRecord | None:
        ...

    def list_revisions(self, artifact_id: str) -> list[ArtifactRevisionRecord]:
        ...

    def commit_revision(self, commit: PendingArtifactCommit) -> CommitOutcome:
        """Atomically publish bytes and compare-and-write the current pointer."""
        ...
