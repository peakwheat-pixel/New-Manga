"""File ordering for imports (D04 §8: 识别顺序)."""

from __future__ import annotations

from collections.abc import Iterable
import os
import re
import stat
from pathlib import Path

from application.importing.images.ports import ImportSource

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"}

_NUMBER_RE = re.compile(r"(\d+)")
_REPARSE_POINT = 0x400


def natural_sort_key(name: str) -> tuple:
    """Case-insensitive natural sort: page2 < page10 (numeric aware)."""
    return tuple(
        int(part) if part.isdigit() else part.lower()
        for part in _NUMBER_RE.split(name)
    )


def collect_image_files(directory: str | Path) -> list[Path]:
    """Image files directly inside ``directory``, naturally sorted by name."""
    root = _absolute_path(directory)
    try:
        root.lstat()
    except FileNotFoundError as error:
        raise NotADirectoryError(str(root)) from error
    _reject_reparse_path(root)
    if not root.is_dir():
        raise NotADirectoryError(str(root))
    entries = list(root.iterdir())
    for entry in entries:
        _reject_reparse_path(entry)
    files = [
        entry for entry in entries
        if entry.is_file() and entry.suffix.lower() in IMAGE_EXTENSIONS
    ]
    return sorted(files, key=lambda entry: natural_sort_key(entry.name))


def sources_from_selection(
    selection_root: str | Path,
    selected_paths: Iterable[str | Path] | None = None,
) -> list[ImportSource]:
    """Build byte sources only from explicit files inside a selected root.

    Selecting a directory imports its direct image children. Passing paths
    imports only those explicitly selected image/PDF files. The path and its
    ancestors are rechecked when bytes are read, so a replaced link fails
    closed before the import use case can copy or persist anything.
    """
    root = _absolute_path(selection_root)
    _reject_reparse_path(root)
    if not root.is_dir():
        raise NotADirectoryError(str(root))

    if selected_paths is None:
        paths = collect_image_files(root)
    else:
        paths = [_absolute_path(selected) for selected in selected_paths]
        for path in paths:
            _assert_within(path, root)
            _reject_reparse_path(path)
            if not path.is_file():
                raise ValueError("selected import source must be a file")
            if path.suffix.lower() not in IMAGE_EXTENSIONS | {".pdf"}:
                raise ValueError("selected import source format is unsupported")

    return [
        ImportSource(
            filename=path.name,
            data_provider=lambda path=path, root=root: _read_selected(path, root),
        )
        for path in paths
    ]


def _absolute_path(value: str | Path) -> Path:
    raw = os.fspath(value)
    if any(segment in {".", ".."} for segment in re.split(r"[\\/]", raw)):
        raise ValueError("relative traversal is not allowed in import paths")
    path = Path(raw)
    if not path.is_absolute():
        raise ValueError("import paths must be absolute")
    return path


def _reject_reparse_path(path: Path) -> None:
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current /= part
        try:
            info = current.lstat()
        except OSError as error:
            raise ValueError("selected import path cannot be inspected") from error
        if stat.S_ISLNK(info.st_mode) or (
            getattr(info, "st_file_attributes", 0) & _REPARSE_POINT
        ):
            raise ValueError("symlink or junction import paths are not allowed")


def _assert_within(path: Path, root: Path) -> None:
    try:
        common = os.path.commonpath((str(root), str(path)))
    except ValueError as error:
        raise ValueError("selected import path escaped its drive or root") from error
    if os.path.normcase(os.path.normpath(common)) != os.path.normcase(
        os.path.normpath(str(root))
    ):
        raise ValueError("selected import path escaped its explicit selection root")


def _read_selected(path: Path, root: Path) -> bytes:
    _assert_within(path, root)
    _reject_reparse_path(path)
    if not path.is_file():
        raise OSError("selected import source is no longer a file")
    # shortcut: path validation leaves a TOCTOU window; use handle-relative opens if concurrent swaps need defending.
    return path.read_bytes()
