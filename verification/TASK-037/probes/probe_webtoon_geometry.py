"""Standalone diagnostic probe for the webtoon scroll geometry (TASK-037).

Not part of the test suite — runs the same harness as
test_reader_webtoon_swaps_in_vertical_viewer and prints the live geometry
timeline so the clamp behaviour can be observed with real numbers.
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
        time.sleep(0.02)
    print(f"scroll found: {scroll is not None} after {(time.monotonic()-start)*1000:.0f} ms")

    image = t.find_by_name(root, "readerPage")
    for step in range(40):
        QGuiApplication.processEvents()
        geom = {
            "sc_w": h.safe_number(scroll, "width"),
            "sc_h": h.safe_number(scroll, "height"),
            "sc_cw": h.safe_number(scroll, "contentWidth"),
            "sc_ch": h.safe_number(scroll, "contentHeight"),
            "img_w": h.safe_number(image, "width"),
            "img_h": h.safe_number(image, "height"),
            "img_ph": h.safe_number(image, "paintedHeight"),
            "img_pw": h.safe_number(image, "paintedWidth"),
            "img_implicit": h.safe_number(image, "implicitHeight"),
            "ch_minus_h": h.safe_number(scroll, "contentHeight") - h.safe_number(scroll, "height"),
        }
        print(f"t={step*100:4d}ms {geom}")
        if geom["ch_minus_h"] >= 240:
            print(">>> hold-condition met")
            break
        time.sleep(0.1)

    print("--- set contentY=240 ---")
    scroll.setProperty("contentY", 240.0)
    QGuiApplication.processEvents()
    print("contentY after set:", h.safe_property(scroll, "contentY"))
    for _ in range(20):
        QGuiApplication.processEvents()
        time.sleep(0.05)
    print("contentY settle:", h.safe_property(scroll, "contentY"))
    print("saved:", reading.progress.scroll_offset_y)
    window.close()
print("PROBE DONE")
