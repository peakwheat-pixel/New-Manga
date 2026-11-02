"""Ports for the export slice (TASK-015; D06 §96).

``PdfComposer`` keeps PDF encoding pluggable: the application layer never
hard-depends on a GUI toolkit at import time. The production composer
(``pdf_qt.QtImagePdfComposer``) decodes with Qt lazily; tests inject a
deterministic stub.

Export history persistence mirrors the D03 §31 ``ExportHistory`` columns
one-to-one in a JSON document store — SQLite is the frozen target shape,
but the schema/migration set is outside this task's allowed paths, so the
port keeps the later adapter swap local.
"""

from __future__ import annotations

import json
import os
import tempfile
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


class PdfComposer(Protocol):
    """Encodes one PDF from decoded page images, in scope order."""

    def compose(self, images: Sequence[bytes]) -> bytes:
        """Return PDF bytes; raise on any page that cannot be encoded."""
        ...


class HistoryDocumentStore(Protocol):
    """Document store for export history rows (JSON file in this slice)."""

    def read(self) -> list[dict]:
        """Return the stored record list; ``[]`` when absent/corrupt."""
        ...

    def write(self, records: list[dict]) -> None:
        """Persist the record list atomically (temp file + replace)."""
        ...


class JsonHistoryDocumentStore:
    """UTF-8 JSON list store with atomic replacement.

    A failed write leaves the previous document untouched and the temp
    file cleaned up.
    """

    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)

    def read(self) -> list[dict]:
        try:
            value = json.loads(self._path.read_text(encoding="utf-8"))
        except (FileNotFoundError, ValueError):
            return []
        return value if isinstance(value, list) else []

    def write(self, records: list[dict]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        fd, temp_name = tempfile.mkstemp(
            prefix=f".{self._path.name}.", suffix=".tmp", dir=self._path.parent
        )
        temp = Path(temp_name)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(records, handle, ensure_ascii=False, indent=2)
            os.replace(temp, self._path)
        except BaseException:
            temp.unlink(missing_ok=True)
            raise


def file_bytes_provider(path: str | Path) -> Callable[[], bytes]:
    """Provider reading an image file lazily at export time."""
    resolved = Path(path)

    def _read() -> bytes:
        return resolved.read_bytes()

    return _read
