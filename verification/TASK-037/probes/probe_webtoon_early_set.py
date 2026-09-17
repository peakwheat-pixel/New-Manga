"""Probe 2: reproduce the flaky timing — write contentY=240 while
contentHeight is still 0 (image not yet loaded) and trace the timeline.
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

from PySide6.QtGui import QGuiApplication  # noqa: E402
from PySide6.QtQml import QQmlEngine  # noqa: E402
from PySide6.QtQuick import QQuickWindow  # noqa: F401,E402

from ui.viewmodels.reader.viewmodel import ReaderViewModel  # noqa: E402

app = QGuiApplication.instance() or QGuiApplication([])

with tempfile.TemporaryDirectory() as td:
    tmp_path = Path(td)
    pages = t.real_png_pages(tmp_path)
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

    print(f"scroll found at {(time.monotonic()-start)*1000:.0f} ms")
    print("contentHeight at find:", h.safe_property(scroll, "contentHeight"))

    # --- write 240 EARLY (contentHeight may still be 0) ---
    scroll.setProperty("contentY", 240.0)
    print("contentY immediately after early set:", h.safe_property(scroll, "contentY"))

    scroll_obj = scroll
    for step in range(60):
        QGuiApplication.processEvents()
        cy = h.safe_property(scroll_obj, "contentY")
        ch = h.safe_property(scroll_obj, "contentHeight")
        alive = t.find_by_name(root, "readerWebtoonScroll")
        same = alive is scroll_obj
        print(
            f"t={step*100:4d}ms contentY={cy!r} contentHeight={ch!r} "
            f"tree_scroll_is_same={same} saved={reading.progress.scroll_offset_y!r}"
        )
        if reading.progress.scroll_offset_y == 240.0:
            print(">>> saved 240")
            break
        time.sleep(0.1)

    # what does a *fresh* lookup see?
    fresh = t.find_by_name(root, "readerWebtoonScroll")
    print("fresh scroll contentY:", h.safe_property(fresh, "contentY"))
    print("held scroll is fresh:", fresh is scroll_obj)
    window.close()
print("PROBE2 DONE")
