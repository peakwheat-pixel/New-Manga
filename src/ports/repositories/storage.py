"""Managed file storage port (D03 §18, D07 §31~36).

Revision paths follow the D03 §18 managed layout: ``books/{book_id}/
chapters/{chapter_id}/{fixed type directory}/`` with ``original/ masks/
clean/ translated/ thumbnails/ previews/ debug/`` as the fixed directory
set, and book-level ``books/{book_id}/exports/`` for export artifacts.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class IntegrityInfo:
    sha256: str
    size_bytes: int


class ManagedFileStoragePort(Protocol):
    """Immutable, content-addressed storage for artifact revisions.

    Implementations must guarantee that a published revision path is never
    overwritten, that publishing is atomic, and that temporary files never
    reach managed paths (D07 §31).
    """

    def new_revision_relative_path(
        self, book_id: str, chapter_id: str, artifact_type: str, revision_id: str, suffix: str
    ) -> str:
        """Return the canonical relative path (forward slashes) for a revision."""
        ...

    def write_temp(self, content: bytes) -> str:
        """Write bytes to a private temp location and return its handle/path."""
        ...

    def discard_temp(self, temp_handle: str) -> None:
        """Best-effort removal of an unconsumed temp file."""
        ...

    def publish(self, temp_handle: str, relative_path: str) -> None:
        """Atomically move a verified temp file onto its immutable path."""
        ...

    def absolute_path(self, relative_path: str) -> str:
        ...

    def verify_temp(self, temp_handle: str) -> IntegrityInfo:
        """Hash and size a temp file before it is published."""
        ...
