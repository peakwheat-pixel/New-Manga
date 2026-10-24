"""Hash and size helpers for managed files (D03 §17.4, D07 §31~32)."""

from __future__ import annotations

import hashlib
from pathlib import Path

from ports.repositories.storage import IntegrityInfo

_READ_CHUNK = 1024 * 1024


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(_READ_CHUNK), b""):
            digest.update(chunk)
    return digest.hexdigest()


def integrity_of(path: str | Path) -> IntegrityInfo:
    resolved = Path(path)
    return IntegrityInfo(sha256=sha256_file(resolved), size_bytes=resolved.stat().st_size)
