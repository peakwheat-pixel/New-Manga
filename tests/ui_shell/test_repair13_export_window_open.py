"""REPAIR-13 F-13-2 regression guard: the reader's export window must open.

The local-machine GUI run against package build 6 hit a pre-existing defect:
clicking 导出… in the Reader never showed the ExportWindow — stderr repeated
``ReaderView.qml:62: ReferenceError: open is not defined`` because the
inline component that instantiates ``ExportWindow`` (a *Window* root, not a
Popup) called ``open()``, which only exists on Popup/Dialog. The window was
created but never shown, silently killing the real-UI export path (AC4).

This test loads the real ReaderView.qml with a stub ``readerViewModel``
context property whose ``openExporter()`` returns a ready stub controller —
the same publication contract bootstrap uses — and guards:

- invoking the export button raises no QML ReferenceError (message-handler
  probe, discriminating: the pre-repair delegate fails it),
- an ``exportWindow`` instance is created AND is visible (discriminating:
  pre-repair the window existed with ``visible == false``).
"""

from __future__ import annotations

import helpers  # noqa: F401  (sys.path injection; SRC_ROOT below)

import pytest

from PySide6.QtCore import Property, QObject, QUrl, Slot, qInstallMessageHandler
from PySide6.QtQml import QQmlComponent, QQmlEngine
from PySide6.QtQuick import QQuickWindow
from PySide6.QtTest import QTest

pytestmark = pytest.mark.usefixtures("qapp")

SRC_QML = helpers.SRC_ROOT / "ui" / "qml" / "reader" / "ReaderView.qml"

HOST_QML = """
import QtQuick
import QtQuick.Controls
ApplicationWindow {
    objectName: "testWindow"
    visible: true
    width: 1280
    height: 800
    ReaderView { anchors.fill: parent }
}
"""


class StubBookSummary(QObject):
    @Property(bool, constant=True)
    def has_progress(self):
        return False

    @Property(str, constant=True)
    def last_read_at(self):
        return ""


class StubExportController(QObject):
    """Just enough surface for ExportWindow's bindings on load."""

    def __init__(self):
        super().__init__()
        self._mode = "original"
        self._output_path = r"C:\default\export.zip"
        self.set_output_calls: list[str] = []
        self.start_calls = 0

    @Property(int, constant=True)
    def pageCount(self):
        return 2

    @Property(str, constant=True)
    def scopeSummary(self):
        return "全部页面 · 2 页"

    @Property(str, constant=True)
    def staleWarningText(self):
        return ""

    @Property(bool, constant=True)
    def staleWarningVisible(self):
        return False

    @Property(str, constant=True)
    def statusMessage(self):
        return ""

    @Property(str, constant=True)
    def mode(self):
        return self._mode

    @Property(str, constant=True)
    def format(self):
        return "zip"

    @Property("QVariantList", constant=True)
    def formats(self):
        return [{"value": "zip", "label": "ZIP (.zip)"}]

    @Property(str, constant=True)
    def outputPath(self):
        return self._output_path

    @Property(str, constant=True)
    def overwritePolicy(self):
        return "overwrite"

    @Property(str, constant=True)
    def stalePolicy(self):
        return "abort"

    @Property(bool, constant=True)
    def running(self):
        return False

    @Property("QVariantList", constant=True)
    def history(self):
        return []

    @Slot(str)
    def setOutputPath(self, path):
        self._output_path = path
        self.set_output_calls.append(path)

    @Slot()
    def startExport(self):
        self.start_calls += 1

    @Slot()
    def refreshStaleWarning(self):
        pass


class StubReaderViewModel(QObject):
    def __init__(self):
        super().__init__()
        self._summary = StubBookSummary()
        self._export_controller = StubExportController()

    @Property(bool, constant=True)
    def hasChapter(self):
        return True

    @Property(str, constant=True)
    def chapterType(self):
        return "paged"

    @Property(str, constant=True)
    def direction(self):
        return "ltr"

    @Property(int, constant=True)
    def pageNumber(self):
        return 1

    @Property(int, constant=True)
    def pageCount(self):
        return 2

    @Property(float, constant=True)
    def progressPercent(self):
        return 50.0

    @Property(str, constant=True)
    def mode(self):
        return "original"

    @Property(str, constant=True)
    def chapterTitle(self):
        return "守卫章节"

    @Property(bool, constant=True)
    def canGoPrevious(self):
        return False

    @Property(bool, constant=True)
    def canGoNext(self):
        return True

    @Property(float, constant=True)
    def totalReadSeconds(self):
        return 0.0

    @Property(str, constant=True)
    def sourcePath(self):
        return ""

    @Property(str, constant=True)
    def statusMessage(self):
        return ""

    @Property(QObject, constant=True)
    def bookSummary(self):
        return self._summary

    @Property(QObject, constant=True)
    def exportController(self):
        return self._export_controller

    @Slot(result="QVariant")
    def openExporter(self):
        return self._export_controller


def _make_harness(qapp):
    engine = QQmlEngine(None)
    model = StubReaderViewModel()
    engine.rootContext().setContextProperty("readerViewModel", model)
    component = QQmlComponent(engine)
    component.setData(
        HOST_QML.encode(),
        QUrl.fromLocalFile(str(SRC_QML.parent / "_TestHost.qml")),
    )
    if not component.isReady():
        raise AssertionError(
            f"host failed to load: {[e.toString() for e in component.errors()]}"
        )
    window = component.create()
    assert window is not None
    qapp.processEvents()
    root = window.findChild(QObject, "readerView")
    assert root is not None
    # Keep the component alive: once Python GC reclaims it, PySide6 tears
    # down the object it created (host window included) mid-test.
    return engine, window, root, model, component


def _invoke_export_button(root):
    button = root.findChild(QObject, "readerExportButton")
    assert button is not None, "readerExportButton missing"
    meta = button.metaObject()
    index = meta.indexOfMethod("clicked()")
    assert index >= 0, "clicked() not found on button"
    meta.method(index).invoke(button)


def test_export_button_opens_visible_window_without_referenceerror(qapp):
    engine, window, root, model, _component = _make_harness(qapp)
    messages: list[str] = []

    def capture(mode, context, message):
        messages.append(message)

    try:
        qInstallMessageHandler(capture)
        _invoke_export_button(root)
        QTest.qWait(200)
    finally:
        qInstallMessageHandler(None)
        try:
            window.deleteLater()
            engine.deleteLater()
            qapp.processEvents()
        except RuntimeError:
            pass  # QML may already have destroyed the host window

    errors = [m for m in messages if "ReferenceError" in m]
    assert not errors, (
        f"QML ReferenceError on the export path (F-13-2): {errors}"
    )

    windows = root.findChildren(QQuickWindow, "exportWindow")
    assert windows, "export window component was not instantiated"
    assert windows[0].isVisible(), (
        "ExportWindow was created but never shown — the F-13-2 "
        "open()-on-Window defect is back"
    )


def test_export_run_button_passes_path_and_starts(qapp):
    """F-13-4 guard: the export window's 导出 button must reach the
    controller. The onClicked handler reads ``exportOutputPath.text``, but
    the output TextField historically had only an objectName and no id, so
    the handler's first line threw ``ReferenceError: exportOutputPath is
    not defined`` and ``startExport()`` was never reached — the real-UI
    export silently did nothing (local GUI run against build 7)."""
    engine, window, root, model, _component = _make_harness(qapp)
    messages: list[str] = []

    def capture(mode, context, message):
        messages.append(message)

    try:
        qInstallMessageHandler(capture)
        _invoke_export_button(root)
        QTest.qWait(100)
        export_window = root.findChildren(QQuickWindow, "exportWindow")[0]

        path_field = export_window.findChild(QObject, "exportOutputPath")
        assert path_field is not None, "exportOutputPath text field missing"
        path_field.setProperty("text", r"G:\verify\out\two-pages.zip")

        run_button = export_window.findChild(QObject, "exportRunButton")
        assert run_button is not None, "exportRunButton missing"
        meta = run_button.metaObject()
        index = meta.indexOfMethod("clicked()")
        meta.method(index).invoke(run_button)
        QTest.qWait(100)
    finally:
        qInstallMessageHandler(None)
        try:
            window.deleteLater()
            engine.deleteLater()
            qapp.processEvents()
        except RuntimeError:
            pass  # QML may already have destroyed the host window

    errors = [m for m in messages if "ReferenceError" in m]
    assert not errors, (
        f"QML ReferenceError on the export-run path (F-13-4): {errors}"
    )
    controller = model._export_controller
    assert controller.start_calls == 1, (
        f"startExport was not reached (F-13-4): calls={controller.start_calls}"
    )
    assert r"G:\verify\out\two-pages.zip" in controller.set_output_calls, (
        "the typed output path never reached setOutputPath"
    )
