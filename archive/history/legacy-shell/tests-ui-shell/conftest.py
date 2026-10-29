"""Fixtures for the ui_shell suite.

ViewModel/QML tests need a QGuiApplication. The default (Windows) platform
is used: the offscreen platform ships no font database and QML Controls
text layout misbehaves without one; Windows is the product boundary.

The Quick render backend is pinned to ``software`` (M2-UI-SHELL-ENV-1):
the default RHI (D3D) backend drops synthesized mouse delivery when the
session's window surface is not interactive (locked/disconnected display),
which made the two QTest.mouseClick regression guards fail nondeterministically
per session. Software rasterization keeps the Windows platform + font
database and makes delivery deterministic; setdefault keeps an explicit
external override working.
"""

from __future__ import annotations

import os

os.environ.setdefault("QT_QUICK_BACKEND", "software")

import helpers  # noqa: E402, F401  (sys.path injection)

import pytest


@pytest.fixture(scope="session")
def qapp():
    from PySide6.QtGui import QGuiApplication

    app = QGuiApplication.instance() or QGuiApplication([])
    yield app
