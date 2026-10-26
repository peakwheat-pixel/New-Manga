"""Fixtures for the workbench suite.

ViewModel/QML tests need a QGuiApplication on the default Windows platform
(same rationale as tests/ui_shell: the offscreen platform ships no font
database; Windows is the product boundary).
"""

from __future__ import annotations

import workbench_helpers  # noqa: F401  (sys.path injection)

import pytest


@pytest.fixture(scope="session")
def qapp():
    from PySide6.QtGui import QGuiApplication

    app = QGuiApplication.instance() or QGuiApplication([])
    yield app
