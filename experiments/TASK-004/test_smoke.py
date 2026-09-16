"""TASK-004 pytest smoke suite.

Validates that PySide6 imports, reports a consistent Qt version, and that a
QML engine can load the minimal QML file using the offscreen platform
plugin (no desktop session required). The QML check runs in a child process
because Qt binds the platform plugin to the process-level application.
"""

import json
import os
import subprocess
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
def test_qml_engine_loads_min_qml(platform_name: str) -> None:
    env = os.environ.copy()
    env["QT_QPA_PLATFORM"] = platform_name
    completed = subprocess.run(
        [sys.executable, os.path.join(HERE, "qml_min", "main.py")],
        cwd=HERE,
        env=env,
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    info = json.loads(completed.stdout.strip().splitlines()[-1])
    assert info["result"] == "PASS", completed.stdout + completed.stderr
    assert info["window_title"] == "TASK-004 QML Smoke"
