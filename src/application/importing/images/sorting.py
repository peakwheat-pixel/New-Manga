"""File ordering for imports (D04 §8: 识别顺序)."""

from __future__ import annotations

import re
from pathlib import Path

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"}

_NUMBER_RE = re.compile(r"(\d+)")


def natural_sort_key(name: str) -> tuple:
    """Case-insensitive natural sort: page2 < page10 (numeric aware)."""
    return tuple(
        int(part) if part.isdigit() else part.lower()
        for part in _NUMBER_RE.split(name)
    )


def collect_image_files(directory: str | Path) -> list[Path]:
    """Image files directly inside ``directory``, naturally sorted by name."""
    root = Path(directory)
    if not root.is_dir():
        raise NotADirectoryError(str(root))
    files = [
        entry
        for entry in root.iterdir()
        if entry.is_file() and entry.suffix.lower() in IMAGE_EXTENSIONS
    ]
    return sorted(files, key=lambda entry: natural_sort_key(entry.name))
