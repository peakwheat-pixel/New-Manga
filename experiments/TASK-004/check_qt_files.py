"""TASK-004 Qt asset checker.

Reports which Qt DLLs, platform plugins and QML module directories exist in a
given PySide6 installation root or a PyInstaller onedir distribution.

Usage: python check_qt_files.py <root> [--layout pyside6|onedir]
"""

import json
import os
import sys

QT_CORE_NAMES = ["Qt6Core.dll", "Qt6Gui.dll", "Qt6Qml.dll", "Qt6Quick.dll", "Qt6QuickControls2.dll"]

REQUIRED_PLUGIN_FILES = [
    os.path.join("platforms", "qwindows.dll"),
    os.path.join("platforms", "qoffscreen.dll"),
]

REQUIRED_QML_DIRS = [
    os.path.join("QtQuick"),
    os.path.join("QtQuick", "Controls"),
    os.path.join("QtQuick", "Window"),
]


def find_layout(root: str, layout: str) -> dict:
    if layout == "pyside6":
        dll_dir = os.path.join(root, "PySide6")
        plugins_dir = os.path.join(root, "PySide6", "plugins")
        qml_dir = os.path.join(root, "PySide6", "qml")
    else:
        dll_dir = os.path.join(root, "_internal", "PySide6")
        plugins_dir = os.path.join(root, "_internal", "PySide6", "plugins")
        qml_dir = os.path.join(root, "_internal", "PySide6", "qml")

    def hit(rel: str) -> str:
        return "present" if os.path.exists(os.path.join(root_check, rel)) else "MISSING"

    root_check = dll_dir
    qt_cores = {name: hit(name) for name in QT_CORE_NAMES}
    root_check = plugins_dir
    plugins = {rel.replace("\\", "/"): hit(rel) for rel in REQUIRED_PLUGIN_FILES}
    root_check = qml_dir
    qml_dirs = {rel.replace("\\", "/"): hit(rel) for rel in REQUIRED_QML_DIRS}

    return {
        "root": root,
        "layout": layout,
        "dll_dir_exists": os.path.isdir(dll_dir),
        "qt_core_dlls": qt_cores,
        "plugins": plugins,
        "qml_dirs": qml_dirs,
    }


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: check_qt_files.py <root> [--layout pyside6|onedir]")
        return 64
    root = os.path.abspath(sys.argv[1])
    layout = "pyside6"
    if "--layout" in sys.argv:
        layout = sys.argv[sys.argv.index("--layout") + 1]
    report = find_layout(root, layout)
    missing = [
        key
        for group in ("qt_core_dlls", "plugins", "qml_dirs")
        for key, value in report[group].items()
        if value != "present"
    ]
    report["missing"] = missing
    report["result"] = "PASS" if not missing and report["dll_dir_exists"] else "FAIL"
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["result"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
