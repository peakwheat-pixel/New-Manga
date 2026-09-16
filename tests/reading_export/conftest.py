"""Fixtures for the reading_export suite.

Qt-dependent tests skip with an explicit reason when PySide6 is missing
(the 3.14 interpreter on this machine has no PySide6; the project venvs
do). Pure service tests run everywhere.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# This directory first, then src (same convention as tests/ui_shell).
THIS_DIR = Path(__file__).resolve().parent
for _entry in (str(THIS_DIR), str(THIS_DIR.parents[1] / "src")):
    if _entry not in sys.path:
        sys.path.insert(0, _entry)


def _pyside6_available() -> bool:
    import importlib.util

    return importlib.util.find_spec("PySide6") is not None


requires_pyside6 = pytest.mark.skipif(
    not _pyside6_available(), reason="PySide6 not installed in this interpreter"
)


@pytest.fixture(scope="session")
def qapp():
    if not _pyside6_available():  # pragma: no cover - guarded by skipif
        pytest.skip("PySide6 not installed")
    from PySide6.QtGui import QGuiApplication

    app = QGuiApplication.instance() or QGuiApplication([])
    yield app
