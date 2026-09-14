from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path
import sys

from PySide6.QtCore import QTimer, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine


QML_PATH = Path(__file__).resolve().parents[1] / "ui" / "qml" / "Main.qml"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke-test", action="store_true")
    options = parser.parse_args(argv)

    application = QGuiApplication([sys.argv[0]])
    engine = QQmlApplicationEngine()
    engine.load(QUrl.fromLocalFile(str(QML_PATH)))
    if not engine.rootObjects():
        print(f"Failed to load QML: {QML_PATH}", file=sys.stderr)
        return 1

    if options.smoke_test:
        QTimer.singleShot(0, application.quit)
    return application.exec()


if __name__ == "__main__":
    raise SystemExit(main())
