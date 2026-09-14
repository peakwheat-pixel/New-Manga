"""TASK-004 pytest smoke suite.

Validates that PySide6 imports, reports a consistent Qt version, and that a
QML engine can load the minimal QML file using the offscreen platform
plugin (no desktop session required). The real-window startup is covered by
qml_min/main.py outside pytest.
"""

import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))


def test_import_pyside6() -> None:
    from PySide6.QtCore import qVersion

    assert qVersion(), "qVersion() returned empty"


def test_qt_core_basics() -> None:
    from PySide6.QtCore import QLibraryInfo, QSysInfo

    assert QLibraryInfo.path(QLibraryInfo.PluginsPath), "plugins path empty"
    assert QSysInfo.currentCpuArchitecture() == "x86_64"


@pytest.mark.parametrize("platform_name", ["offscreen"])
def test_qml_engine_loads_min_qml(platform_name: str, monkeypatch: pytest.MonkeyPatch) -> None:
    from PySide6.QtCore import QUrl
    from PySide6.QtGui import QGuiApplication
    from PySide6.QtQml import QQmlApplicationEngine

    monkeypatch.setenv("QT_QPA_PLATFORM", platform_name)
    app = QGuiApplication.instance() or QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    engine.load(QUrl.fromLocalFile(os.path.join(HERE, "qml_min", "main.qml")))
    try:
        assert engine.rootObjects(), "QML engine produced no root object"
        window = engine.rootObjects()[0]
        assert window.property("title") == "TASK-004 QML Smoke"
    finally:
        engine.deleteLater()
    app.processEvents()
