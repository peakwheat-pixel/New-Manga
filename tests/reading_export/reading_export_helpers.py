"""Shared helpers for the reading_export suite (TASK-015).

Same convention as tests/workbench/workbench_helpers: the suite-specific
name avoids the cross-suite ``helpers`` module clash seen in TASK-014;
tests import ``reading_export_helpers`` directly and the module puts this
directory and ``src`` on sys.path.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

THIS_DIR = Path(__file__).resolve().parent
SRC_ROOT = THIS_DIR.parents[1] / "src"
for entry in (str(THIS_DIR), str(SRC_ROOT)):
    if entry not in sys.path:
        sys.path.insert(0, entry)


def _pyside6_available() -> bool:
    """True when the active interpreter can import PySide6 (no import side effect)."""
    return importlib.util.find_spec("PySide6") is not None


#: Skip marker for Qt-dependent tests.
#:
#: It lives here — in the **uniquely named** helper module — and is imported
#: explicitly (TASK-034 R-01). It used to be reached through a bare
#: ``from conftest import requires_pyside6``, which resolved to another
#: directory's ``conftest`` whenever ``tests/reading_export`` was collected
#: after a suite that has its own ``conftest.py``
#: (``pytest tests/reading_export tests/editing`` → 2 collection errors).
requires_pyside6 = pytest.mark.skipif(
    not _pyside6_available(), reason="PySide6 not installed in this interpreter"
)

from application.export import (  # noqa: E402
    ExportPage,
    JsonHistoryDocumentStore,
    file_bytes_provider,
)
from application.reading import (  # noqa: E402
    JsonProgressDocumentStore,
    ReaderPage,
)


def make_pages(tmp_path: Path, count: int = 3, translated: bool = False):
    """Write `count` tiny PNG-ish files and return matching ReaderPages.

    ``translated=True`` gives every page a distinct translated file whose
    revision is current, so translated reading/export paths have data.
    """
    originals, rows = [], []
    for index in range(count):
        original = tmp_path / f"page_{index:02d}_第{index}页.png"
        original.parent.mkdir(parents=True, exist_ok=True)
        original.write_bytes(f"PNG-orig-{index}".encode())
        row = ReaderPage(
            page_id=f"p{index}",
            filename=original.name,
            original_path=str(original),
        )
        if translated:
            translated_path = tmp_path / f"page_{index:02d}_translated.png"
            translated_path.write_bytes(f"PNG-trans-{index}".encode())
            row = ReaderPage(
                page_id=row.page_id,
                filename=row.filename,
                original_path=row.original_path,
                translated_path=str(translated_path),
                translated_revision_id=f"rev-{index}",
                current_translated_revision_id=f"rev-{index}",
                text=f"第 {index} 页译文",
            )
        originals.append(row)
    return originals


def to_export_pages(reader_pages):
    """ReaderPage rows → ExportPage rows (same seam the ViewModel uses)."""
    return [
        ExportPage(
            page_id=page.page_id,
            filename=page.filename,
            source_provider=file_bytes_provider(page.original_path),
            translated_provider=(
                file_bytes_provider(page.translated_path)
                if page.translated_path
                else None
            ),
            translated_revision_id=page.translated_revision_id,
            current_translated_revision_id=page.current_translated_revision_id,
            text=page.text,
        )
        for page in reader_pages
    ]


def make_service(tmp_path):
    from application.export import ExportService

    return ExportService(
        JsonHistoryDocumentStore(tmp_path / "export_history.json")
    )


def make_reading_service(tmp_path):
    from application.reading import ReadingService

    return ReadingService(JsonProgressDocumentStore(tmp_path / "progress.json"))


def safe_property(obj, name):
    """Read a QML property, tolerating a deleted C++ object.

    Diagnostics must never replace the failure they describe: during a real
    reproduction of the registered webtoon flaky the QML ``Image``/``Flickable``
    can already be gone, and a bare ``obj.property(...)`` would raise
    ``RuntimeError: Internal C++ object already deleted`` instead of letting the
    underlying ``AssertionError`` surface (observed 2026-09-17, TASK-036).
    Moved here from test_qml_contract (TASK-037) so the placeholder contract
    is unit-testable without Qt.
    """
    if obj is None:
        return None
    try:
        return obj.property(name)
    except RuntimeError as error:  # pragma: no cover - deleted C++ object
        return f"<unavailable: {error}>"


def safe_number(obj, name, default=0.0):
    """Read a QML property as a number for numeric wait conditions.

    ``safe_property`` deliberately returns a *string* placeholder — right for
    diagnostics, wrong for comparisons: ``(safe_property(x, "contentHeight")
    or 0) > 0`` evaluates ``str > int`` and raises ``TypeError``, replacing
    the real assertion failure with a crash (TASK-036 R-01). Numeric wait
    conditions use this helper instead: a missing object or a non-numeric
    value falls back to ``default``, so the comparison stays numeric, the
    bounded wait keeps waiting, and the eventual assertion still reports
    through ``safe_property`` diagnostics — never masking a real failure.
    """
    if obj is None:
        return default
    try:
        value = obj.property(name)
    except RuntimeError:  # pragma: no cover - deleted C++ object
        return default
    if isinstance(value, (int, float)):
        return value
    return default
