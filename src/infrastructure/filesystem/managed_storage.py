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
import stat
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


def _is_reparse_point(st: os.stat_result) -> bool:
    """Junction/symlink detection that works on both Windows and POSIX."""
    attributes = getattr(st, "st_file_attributes", 0)
    if attributes:
        return bool(attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)
    return stat.S_ISLNK(st.st_mode)


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

    def remove_managed(self, relative_path: str) -> None:
        """Delete one managed (controlled) file (TASK-021 trash subset).

        Refuses anything that does not resolve to a plain file *inside* the
        managed root reached without crossing a reparse point — permanent
        deletion can only ever reach controlled copies, never anything
        outside (and user source files are never inside the managed root at
        all).  The guards, in order:

        - **lexical** (TASK-060 R-001 / TASK-061 R-011): the raw ``/``-split
          segments must not contain ``..``, ``.`` or empty components.  The
          segments come from the raw string, *not* ``PurePosixPath.parts``,
          which silently drops ``.`` and empty components (the dead
          ``"." in parts`` condition this slice removes);
        - **containment** (TASK-021): the fully resolved path must stay
          inside the resolved root;
        - **reparse walk** (TASK-061 R-010): every existing directory along
          the *unresolved* walk must be a plain directory.  A root-internal
          junction or symlink resolves back inside the root, so containment
          alone would let a tampered reference reach a sibling chapter's
          protected original through a link.
        """
        absolute = Path(self.absolute_path(relative_path)).resolve()
        root = self._root.resolve()
        try:
            absolute.relative_to(root)
        except ValueError as error:
            raise ImmutablePathViolation(
                f"refusing to remove {absolute}: escapes the managed root {root}"
            ) from error
        segments = relative_path.replace("\\", "/").split("/")
        if (
            ".." in segments
            or "." in segments
            or Path(relative_path).is_absolute()
            or any(segment == "" for segment in segments[1:])
        ):
            raise ImmutablePathViolation(
                f"refusing to remove {relative_path!r}:"
                " path components may not traverse"
            )
        # TASK-061 R-010: walk the *unresolved* path and reject any link.
        probe = self._root
        for segment in segments:
            probe = probe / segment
            try:
                probe_stat = probe.lstat()
            except OSError:
                break  # nothing there to traverse through
            if _is_reparse_point(probe_stat):
                raise ImmutablePathViolation(
                    f"refusing to remove {relative_path!r}:"
                    f" path crosses a junction/symlink at {probe}"
                )
        if absolute.is_file():
            absolute.unlink()
