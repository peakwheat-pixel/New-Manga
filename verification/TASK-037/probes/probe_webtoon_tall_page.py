"""Probe 3: verify that a tall page (40x1000) makes contentHeight large
enough that contentY=240 lands inside the StopAtBounds extent and stays.
"""

import sys
import tempfile
import time
from pathlib import Path

TESTS_DIR = Path(r"G:/CODEX/New Manga.worktrees/TASK-037-zcode/tests/reading_export")
SRC_DIR = Path(r"G:/CODEX/New Manga.worktrees/TASK-037-zcode/src")
sys.path.insert(0, str(TESTS_DIR))
sys.path.insert(0, str(SRC_DIR))

import reading_export_helpers as h  # noqa: E402
import test_qml_contract as t  # noqa: E402

from PySide6.QtCore import Qt  # noqa: E402
from PySide6.QtGui import QColor, QGuiApplication, QImage  # noqa: E402
from PySide6.QtQml import QQmlEngine  # noqa: E402
from PySide6.QtQuick import QQuickWindow  # noqa: F401,E402

from application.reading import ReaderPage  # noqa: E402
from ui.viewmodels.reader.viewmodel import ReaderViewModel  # noqa: E402

app = QGuiApplication.instance() or QGuiApplication([])


def tall_pages(tmp_path, count=3, width=40, height=1000):
    rows = []
    for index in range(count):
        path = tmp_path / f"page_{index}.png"
        image = QImage(width, height, QImage.Format.Format_RGB32)
        image.fill(QColor(120 + index * 30, 40, 40))
        assert image.save(str(path))
        rows.append(
            ReaderPage(
                page_id=f"p{index}",
                filename=path.name,
                original_path=str(path),
                text=f"第 {index} 页",
            )
        )
    return rows


with tempfile.TemporaryDirectory() as td:
    tmp_path = Path(td)
    pages = tall_pages(tmp_path)
    reading = h.make_reading_service(tmp_path)
    export_service = h.make_service(tmp_path)
    vm = ReaderViewModel(reading, t.Catalog(pages), export_service=export_service)

    engine = QQmlEngine()
    engine.rootContext().setContextProperty("readerViewModel", vm)
    window = t.load_host(engine, t.READER_HOST, t.SRC_QML / "reader")
    root = t.find_by_name(window, "readerView")
    vm.openChapter("b", "c", "条漫", "webtoon", "vertical")

    start = time.monotonic()
    scroll = None
    while time.monotonic() - start < 5:
        QGuiApplication.processEvents()
        scroll = t.find_by_name(root, "readerWebtoonScroll")
        if scroll is not None:
            break
        time.sleep(0.01)

    # wait for contentHeight > 0 like the test does, then trace
    start2 = time.monotonic()
    while time.monotonic() - start2 < 5:
        QGuiApplication.processEvents()
        if h.safe_number(scroll, "contentHeight") > 0:
            break
        time.sleep(0.02)
    print(f"contentHeight>0 at +{(time.monotonic()-start2)*1000:.0f} ms")

    scroll.setProperty("contentY", 240.0)
    for step in range(30):
        QGuiApplication.processEvents()
        cy = h.safe_property(scroll, "contentY")
        ch = h.safe_property(scroll, "contentHeight")
        print(f"t={step*100:4d}ms contentY={cy!r} contentHeight={ch!r} saved={reading.progress.scroll_offset_y!r}")
        if step == 8:
            print("--- re-set contentY=240 (post-batch) ---")
        time.sleep(0.1)
        if reading.progress.scroll_offset_y == 240.0 and step > 8:
            print(">>> saved 240 and stable")
            break
    window.close()
print("PROBE3 DONE")
