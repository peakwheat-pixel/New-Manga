"""Durable atomic snapshots for active and completed P16 export jobs."""

from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile
import threading


class JsonExportJobStore:
    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)
        self._lock = threading.Lock()

    def read(self) -> list[dict]:
        with self._lock:
            try:
                value = json.loads(self._path.read_text(encoding="utf-8"))
            except (FileNotFoundError, ValueError):
                return []
            return value if isinstance(value, list) else []

    def write(self, jobs: list[dict]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._lock:
            fd, name = tempfile.mkstemp(prefix=f".{self._path.name}.", suffix=".tmp", dir=self._path.parent)
            temp = Path(name)
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as handle:
                    json.dump(jobs, handle, ensure_ascii=False, separators=(",", ":"))
                    handle.flush()
                    os.fsync(handle.fileno())
                os.replace(temp, self._path)
            except BaseException:
                temp.unlink(missing_ok=True)
                raise
