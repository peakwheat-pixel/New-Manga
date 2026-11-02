"""Fixtures for the rendering suite.

Qt text layout needs a real platform font database; the offscreen
platform ships no fonts at all, so tests run on the default (Windows)
platform — which is exactly the product boundary. A session-scoped
QGuiApplication is created once for the whole suite.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))


@pytest.fixture(scope="session")
def qapp():
    from PySide6.QtGui import QGuiApplication

    app = QGuiApplication.instance() or QGuiApplication([])
    yield app
