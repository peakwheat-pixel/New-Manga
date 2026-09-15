"""Managed file storage implementing the immutable revision layout.

Layout follows D03 §18 exactly: ``books/{book_id}/chapters/{chapter_id}/``
with the fixed per-type directory set (``original/ masks/ clean/
translated/ thumbnails/ previews/ debug/``) plus the book-level
``exports/`` directory for export artifacts. Paths stored in the database
are relative with forward slashes so they stay portable across drives and
Unicode-safe (D07 §33~36). Publishing uses ``os.replace`` only onto a path
that does not exist yet: committed revisions are immutable and can never be
overwritten (TASK-002 §8.1).
"""

from __future__ import annotations

import os
import uuid
from pathlib import Path

from infrastructure.filesystem.integrity import integrity_of
from ports.repositories.storage import IntegrityInfo

_TEMP_DIR = "temp"

#: Mapping from ``media_artifacts.artifact_type`` (D03 §16.1) onto the fixed
#: directory names of the D03 §18 layout. ``export`` lives on the book level
#: (``books/{book_id}/exports/``) exactly as drawn in D03 §18.
ARTIFACT_TYPE_DIRS: dict[str, str] = {
    "original": "original",
    "thumbnail": "thumbnails",
    "detection_overlay": "previews",
    "mask": "masks",
    "clean": "clean",
    "translated": "translated",
    "render_preview": "previews",
    "export": "exports",
    "debug_ocr": "debug",
    "debug_detection": "debug",
}


class ImmutablePathViolation(RuntimeError):
    """Raised when publishing would overwrite an existing managed file."""


def _sanitize_component(component: str) -> str:
    """Reject path separators in id-like path components (D07 §33~34)."""
    if not component or any(ch in component for ch in "\\/") or component in {".", ".."}:
        raise ValueError(f"unsafe path component: {component!r}")
    return component


class ManagedFileStorage:
    def __init__(self, root: str | Path) -> None:
        self._root = Path(root)
        self._temp_dir = self._root / _TEMP_DIR

    @property
    def root(self) -> Path:
        return self._root

    def ensure_layout(self) -> None:
        self._temp_dir.mkdir(parents=True, exist_ok=True)

    def new_revision_relative_path(
        self, book_id: str, chapter_id: str, artifact_type: str, revision_id: str, suffix: str
    ) -> str:
        """Return the D03 §18 relative path for a new revision.

        Export artifacts use the book-level ``exports/`` directory; every
        other type lives under the chapter in its mapped fixed directory.
        Unknown artifact types are rejected instead of creating ad-hoc
        directories that would fork the managed layout.
        """
        try:
            type_dir = ARTIFACT_TYPE_DIRS[artifact_type]
        except KeyError:
            raise ValueError(f"unknown artifact_type: {artifact_type!r}") from None
        book = _sanitize_component(book_id)
        revision = _sanitize_component(revision_id) + suffix
        if artifact_type == "export":
            return "/".join(["books", book, "exports", revision])
        chapter = _sanitize_component(chapter_id)
        return "/".join(["books", book, "chapters", chapter, type_dir, revision])

    def absolute_path(self, relative_path: str) -> str:
        return str(self._root.joinpath(*relative_path.split("/")))

    def write_temp(self, content: bytes) -> str:
        self.ensure_layout()
        temp_path = self._temp_dir / f"{uuid.uuid4().hex}.tmp"
        with temp_path.open("wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        return str(temp_path)

    def discard_temp(self, temp_handle: str) -> None:
        temp_path = Path(temp_handle)
        if temp_path.exists():
            temp_path.unlink()

    def verify_temp(self, temp_handle: str) -> IntegrityInfo:
        return integrity_of(temp_handle)

    def publish(self, temp_handle: str, relative_path: str) -> None:
        final_path = Path(self.absolute_path(relative_path))
        if final_path.exists():
            raise ImmutablePathViolation(
                f"refusing to overwrite managed revision file: {final_path}"
            )
        final_path.parent.mkdir(parents=True, exist_ok=True)
        # os.replace is atomic within one volume; the existence guard above
        # keeps committed revisions immutable (TASK-002 §8.1).
        os.replace(temp_handle, final_path)
