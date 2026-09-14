"""TASK-004 minimal QML smoke experiment.

Starts a real Qt Quick window, keeps it open briefly, then closes it and
reports Qt version, platform plugin and QML load state on stdout as JSON.

Runs both from a development venv and inside a PyInstaller onedir build:
QML assets are located via ``sys._MEIPASS`` when frozen.
"""

import json
import os
import sys

BASE_DIR = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtCore import QLibraryInfo, QTimer, QUrl, qVersion  # noqa: E402
from PySide6.QtGui import QGuiApplication  # noqa: E402
from PySide6.QtQml import QQmlApplicationEngine  # noqa: E402


def collect_info() -> dict:
    plugins_path = QLibraryInfo.path(QLibraryInfo.PluginsPath)
    platform_dll = os.path.join(plugins_path, "platforms", "qwindows.dll")
    return {
        "qt_version": qVersion(),
        "python_version": sys.version.split()[0],
        "platform_name": QGuiApplication.platformName(),
        "plugins_path": plugins_path,
        "qwindows_dll_present": os.path.isfile(platform_dll),
        "qml_imports_path": QLibraryInfo.path(QLibraryInfo.Qml2ImportsPath),
        "frozen": getattr(sys, "frozen", False),
    }


def main() -> int:
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    qml_file = os.path.join(BASE_DIR, "main.qml")
    engine.load(QUrl.fromLocalFile(qml_file))
    info = collect_info()
    info["qml_file"] = qml_file
    if not engine.rootObjects():
        info["result"] = "FAIL"
        info["reason"] = "QML engine produced no root object"
        print(json.dumps(info, ensure_ascii=False))
        return 2
    window = engine.rootObjects()[0]
    info["window_title"] = window.property("title")
    info["window_visible"] = bool(window.property("visible"))

    def finish() -> None:
        window.close()
        info["result"] = "PASS"
        print(json.dumps(info, ensure_ascii=False))
        app.quit()

    QTimer.singleShot(1500, finish)
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
