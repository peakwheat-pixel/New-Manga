"""TASK-045 post-hoc review, target 5 (ZCode): the Repeater shadowing claim.

The F-5/R-003 fix comment claims that inside ``Repeater { model: visible ?
model.tiles : [] }`` (the TASK-020 integration spelling, unchanged through
602cca8) the unqualified names resolve to the **Repeater's own properties**,
so ``model.tiles`` was ``undefined`` and *no tile delegate was ever created*;
and that ``visible`` (left unqualified even in 1171bc5) resolved to the
Repeater's own ``visible`` (always true), voiding the guard.

This probe re-plays both spellings side by side in a minimal QML tree:

- legacy:  ``model: visible ? model.tiles : []``   -> expect 0 delegates
- partial: ``model: visible && rv.model ? rv.model.tiles : []`` (1171bc5)
                                                           -> expect 2 delegates
- fixed:   ``model: tilesHost.visible && rv.model ? rv.model.tiles : []``
   (a165aa3)                                               -> expect 2 delegates

Run:
    set PYTHONPATH=<src> && python qml_shadow_probe.py
Exit 0 = the claim reproduces on this Qt build.
"""

from __future__ import annotations

import sys
from pathlib import Path

QML = """
import QtQuick
Rectangle {
    id: root
    width: 100; height: 100
    // stands in for the context property the ViewModel would be
    property var model: [{url: "a"}, {url: "b"}]
    property bool hostVisible: true

    Column {
        Repeater {
            objectName: "legacy"
            // the TASK-020 .. 602cca8 spelling, verbatim
            model: visible ? model.tiles : []
            delegate: Rectangle { width: 10; height: 10; color: "red" }
        }
    }
    Column {
        Repeater {
            objectName: "partial"
            // 1171bc5: model qualified, visible still shadowed
            model: visible && root.model ? root.model : []
            delegate: Rectangle { width: 10; height: 10; color: "green" }
        }
    }
    Column {
        id: tilesHost
        Repeater {
            objectName: "fixed"
            // a165aa3: both names qualified
            model: tilesHost.visible && root.model ? root.model : []
            delegate: Rectangle { width: 10; height: 10; color: "blue" }
        }
    }
}
"""


def find_repeater(root, object_name: str):
    stack = list(root.children())
    while stack:
        current = stack.pop()
        if current.objectName() == object_name:
            return current
        stack.extend(current.children())
    return None


def main() -> int:
    from PySide6.QtCore import QUrl
    from PySide6.QtGui import QGuiApplication
    from PySide6.QtQml import QQmlApplicationEngine

    app = QGuiApplication.instance() or QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    path = Path(__file__).parent / "_qml_shadow_probe.qml"
    path.write_text(QML, encoding="utf-8")
    engine.load(QUrl.fromLocalFile(str(path)))
    if not engine.rootObjects():
        print("FAIL: the probe QML did not load")
        return 1
    root = engine.rootObjects()[0]

    counts = {}
    for name in ("legacy", "partial", "fixed"):
        repeater = find_repeater(root, name)
        counts[name] = repeater.property("count") if repeater is not None else None

    print(f"[shadow] delegate counts: legacy={counts['legacy']} "
          f"partial={counts['partial']} fixed={counts['fixed']}")
    ok = (
        counts["legacy"] == 0
        and counts["partial"] == 2
        and counts["fixed"] == 2
    )
    print(f"[shadow] the 'delegates were never created under the TASK-020 "
          f"spelling' claim reproduces: {'YES' if ok else 'NO'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
