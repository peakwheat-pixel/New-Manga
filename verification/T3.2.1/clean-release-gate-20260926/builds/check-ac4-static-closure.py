# -*- coding: utf-8 -*-
"""AC4 static resource-closure check for Build 2 dist (read-only)."""
import json
import os

DIST = r"G:\CODEX\New Manga.artifacts\T3.2.1-clean-release-gate-20260926\build2\dist\NewManga"
INT = os.path.join(DIST, "_internal")

def must(rel):
    p = os.path.join(DIST, rel.replace("/", os.sep))
    if not os.path.exists(p):
        p2 = os.path.join(INT, rel.replace("/", os.sep))
        if os.path.exists(p2):
            return ("_internal/" + rel, "OK", os.path.getsize(p2))
        return (rel, "MISSING", None)
    return (rel, "OK", os.path.getsize(p))

checks = [
    # production QML entry + four top-level pages
    "ui/qml/Main.qml",
    "ui/qml/bookshelf/BookshelfView.qml",
    "ui/qml/workbench/WorkbenchView.qml",
    "ui/qml/reader/ReaderView.qml",
    "ui/qml/settings/SettingsView.qml",
    "ui/qml/shell",
    "ui/qml/theme",
    # Qt platform plugin
    "PySide6/plugins/platforms/qwindows.dll",
    # core Qt DLLs
    "PySide6/Qt6Core.dll", "PySide6/Qt6Gui.dll", "PySide6/Qt6Qml.dll",
    "PySide6/Qt6Quick.dll", "PySide6/Qt6QuickControls2.dll",
    "PySide6/Qt6Widgets.dll",
    # python runtime
    "python312.dll",
]
results = [must(c) for c in checks]

# QML module dirs shipped by PySide6
qml_mods = sorted(os.listdir(os.path.join(INT, "PySide6", "qml"))) if os.path.isdir(os.path.join(INT, "PySide6", "qml")) else []
plugins = sorted(os.listdir(os.path.join(INT, "PySide6", "plugins", "platforms"))) if os.path.isdir(os.path.join(INT, "PySide6", "plugins", "platforms")) else []
imageformats = sorted(os.listdir(os.path.join(INT, "PySide6", "plugins", "imageformats"))) if os.path.isdir(os.path.join(INT, "PySide6", "plugins", "imageformats")) else []

missing = [r for r in results if r[1] == "MISSING"]
print(json.dumps({
    "checked": [{"path": r[0], "state": r[1], "bytes": r[2]} for r in results],
    "missing_count": len(missing),
    "qml_modules": qml_mods,
    "platform_plugins": plugins,
    "imageformat_plugins": imageformats,
}, ensure_ascii=False, indent=1))
