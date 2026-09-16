"""Ports for the reader slice (TASK-015).

The reader consumes page data through :class:`ReaderPageCatalog` so the
application layer never imports infrastructure: the production catalog is
assembled in the composition root (bootstrap) from the SQLite repository
and Managed File Storage, exactly like the workbench's page catalog.

Reading progress persistence is a JSON document store for this slice:
D03 §29 targets SQLite, but the schema/migration set is frozen outside
TASK-015, so the row shape here mirrors the future columns
(``reading_progress``) one-to-one and the port keeps the swap local.
"""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class ReaderPage:
    """One page as the reader sees it (D03 §5, §16, §29).

    ``translated_revision_id`` is the revision the translated file on disk
    was produced from; ``current_translated_revision_id`` is the artifact's
    current pointer. A mismatch means a newer render exists — the shown
    image is stale (D06 §97). An empty ``translated_path`` means the page
    has no translated render at all.
    """

    page_id: str
    filename: str
    original_path: str
    translated_path: str | None = None
    translated_revision_id: str | None = None
    current_translated_revision_id: str | None = None
    text: str = ""

    @property
    def translated_stale(self) -> bool:
        return bool(
            self.translated_path
            and self.translated_revision_id
            and self.current_translated_revision_id
            and self.translated_revision_id != self.current_translated_revision_id
        )


class ReaderPageCatalog(Protocol):
    """Read-only page source for one chapter, in reading order."""

    def list_pages(self, chapter_id: str) -> list[ReaderPage]:
        """Pages sorted by the chapter's reading order; empty if unknown."""
        ...


class ProgressDocumentStore(Protocol):
    """Document store for reading progress rows (JSON file in this slice)."""

    def read(self) -> dict:
        """Return the stored document; ``{}`` when absent/corrupt."""
        ...

    def write(self, state: dict) -> None:
        """Persist the document atomically (temp file + replace)."""
        ...


class JsonProgressDocumentStore:
    """UTF-8 JSON document store with atomic replacement.

    A failed write (disk full, permission error) leaves the previous
    document untouched; the temp file is always cleaned up.
    """

    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)

    def read(self) -> dict:
        try:
            value = json.loads(self._path.read_text(encoding="utf-8"))
        except (FileNotFoundError, ValueError):
            return {}
        return value if isinstance(value, dict) else {}

    def write(self, state: dict) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        fd, temp_name = tempfile.mkstemp(
            prefix=f".{self._path.name}.", suffix=".tmp", dir=self._path.parent
        )
        temp = Path(temp_name)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(state, handle, ensure_ascii=False, indent=2)
            os.replace(temp, self._path)
        except BaseException:
            temp.unlink(missing_ok=True)
            raise
