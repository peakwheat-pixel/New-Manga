"""Fixtures for the reading_export suite.

Qt-dependent tests skip with an explicit reason when PySide6 is missing
(the 3.14 interpreter on this machine has no PySide6; the project venvs
do). Pure service tests run everywhere.

``requires_pyside6`` and the availability probe live in
:mod:`reading_export_helpers` and are imported explicitly (TASK-034 R-01), so
no test module depends on the bare ``conftest`` module name — that name
resolves to another directory's conftest when this suite is collected after a
suite that has its own ``conftest.py``.
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

from reading_export_helpers import _pyside6_available  # noqa: E402


@pytest.fixture(scope="session")
def qapp():
    if not _pyside6_available():  # pragma: no cover - guarded by skipif
        pytest.skip("PySide6 not installed")
    from PySide6.QtGui import QGuiApplication

    app = QGuiApplication.instance() or QGuiApplication([])
    yield app
