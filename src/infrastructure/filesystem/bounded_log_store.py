"""Bounded, rotating diagnostics log store (TASK-055 AC 2).

Retention contract: at most ``max_files`` files under ``root``, each at
most ``max_bytes_per_file``; appending never grows the store beyond that
bound. File names carry microsecond timestamps so concurrent appenders
cannot collide on a name, and a lock serialises rotation decisions
within one process. Layout lives under the data root managed by the
assembler — never inside a user source tree.
"""

from __future__ import annotations

import threading
from pathlib import Path

_FILE_PREFIX = "diag-"
_FILE_SUFFIX = ".log"


def _stamp_of(timestamp: str) -> str:
    """File-name-safe stamp: keep the fixed-width date/time digits (and
    the fractional part) so names sort by creation time."""
    return timestamp.replace("-", "").replace(":", "").replace(" ", "T")


class BoundedLogStore:
    def __init__(
        self,
        root: Path,
        *,
        max_files: int = 5,
        max_bytes_per_file: int = 512_000,
    ) -> None:
        if max_files < 1:
            raise ValueError("max_files must be >= 1")
        if max_bytes_per_file < 1:
            raise ValueError("max_bytes_per_file must be >= 1")
        self._root = Path(root)
        self._max_files = max_files
        self._max_bytes_per_file = max_bytes_per_file
        self._lock = threading.Lock()

    @property
    def root(self) -> Path:
        return self._root

    def append(self, line: str, *, timestamp: str) -> None:
        """Append one entry; rotate first when the current file is full,
        then prune the oldest files until the file-count bound holds."""
        with self._lock:
            self._root.mkdir(parents=True, exist_ok=True)
            entry = line if line.endswith("\n") else line + "\n"
            incoming = len(entry.encode("utf-8"))
            current = self._current_file()
            # Rotate *before* writing when the entry would push the current
            # file past the per-file cap, so the "each file at most
            # max_bytes_per_file" invariant holds after every append (a
            # single entry larger than the cap goes to a fresh file and may
            # exceed it on its own; the file-count bound still holds).
            if (
                current is None
                or current.stat().st_size + incoming > self._max_bytes_per_file
            ):
                current = self._open_new_file(timestamp)
            with current.open("a", encoding="utf-8") as handle:
                handle.write(entry)
            self._prune()

    def write(self, line: str, *, timestamp: str) -> Path:
        """Write one standalone bounded entry to a fresh file."""
        with self._lock:
            self._root.mkdir(parents=True, exist_ok=True)
            entry = line if line.endswith("\n") else line + "\n"
            path = self._open_new_file(timestamp)
            with path.open("w", encoding="utf-8") as handle:
                handle.write(entry)
            self._prune()
            return path

    def files(self) -> tuple[Path, ...]:
        """Existing log files, oldest first."""
        with self._lock:
            return self._files_snapshot()

    def total_bytes(self) -> int:
        with self._lock:
            return sum(path.stat().st_size for path in self._files_snapshot())

    # -- internals (caller holds the lock) ---------------------------------

    def _files_snapshot(self) -> tuple[Path, ...]:
        if not self._root.exists():
            return ()
        return tuple(sorted(self._root.glob(f"{_FILE_PREFIX}*{_FILE_SUFFIX}")))

    def _current_file(self) -> Path | None:
        files = self._files_snapshot()
        return files[-1] if files else None

    def _open_new_file(self, timestamp: str) -> Path:
        stamp = _stamp_of(timestamp)
        prefix = f"{_FILE_PREFIX}{stamp}-"
        # Continue *after* the highest existing sequence for this stamp:
        # pruning may have freed low sequence numbers, and reusing them
        # would break "name order == creation order".
        seq = max(
            (int(path.stem.rsplit("-", 1)[-1]) for path in self._files_snapshot()
             if path.stem.startswith(prefix)),
            default=-1,
        ) + 1
        path = self._root / f"{prefix}{seq:04d}{_FILE_SUFFIX}"
        path.touch()
        return path

    def _prune(self) -> None:
        files = self._files_snapshot()
        excess = len(files) - self._max_files
        for path in files[:max(0, excess)]:
            path.unlink()
