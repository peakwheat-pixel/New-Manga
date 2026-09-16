"""Fixtures for the ui_shell suite.

ViewModel/QML tests need a QGuiApplication. The default (Windows) platform
is used: the offscreen platform ships no font database and QML Controls
text layout misbehaves without one; Windows is the product boundary.
"""

from __future__ import annotations

import helpers  # noqa: F401  (sys.path injection)

import pytest


@pytest.fixture(scope="session")
def qapp():
    from PySide6.QtGui import QGuiApplication

    app = QGuiApplication.instance() or QGuiApplication([])
    yield app
