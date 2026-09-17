"""QML end-to-end contract tests for the reader/export slice (TASK-015).

Loads the real ReaderView.qml / ExportWindow.qml with the real ViewModels
published exactly the way bootstrap will (context properties), mirroring
tests/ui_shell's harness. Runs on PySide6 with a window-hosted loader;
skips with an explicit reason when PySide6 is missing.
"""

from __future__ import annotations

import pytest
import reading_export_helpers
from reading_export_helpers import (
    make_pages,
    make_reading_service,
    make_service,
    requires_pyside6,
    safe_number,
    safe_property,
    to_export_pages,
)

pytest.importorskip("PySide6", reason="PySide6 not installed in this interpreter")

import time as _time  # noqa: E402

from PySide6.QtCore import QObject, QUrl, Qt  # noqa: E402
from PySide6.QtGui import QGuiApplication  # noqa: E402
from PySide6.QtQml import QQmlComponent, QQmlEngine  # noqa: E402
from PySide6.QtQuick import QQuickWindow  # noqa: F401,E402  (registers item types)
from PySide6.QtTest import QTest  # noqa: E402

from application.export import ExportPage  # noqa: E402
from application.export import ExportPage  # noqa: E402
from application.reading import ReaderPage  # noqa: E402
from ui.viewmodels.export.viewmodel import ExportViewModel  # noqa: E402
from ui.viewmodels.reader.viewmodel import ReaderViewModel  # noqa: E402

pytestmark = pytest.mark.usefixtures("qapp")

SRC_QML = reading_export_helpers.SRC_ROOT / "ui" / "qml"

READER_HOST = """
import QtQuick
import QtQuick.Controls
ApplicationWindow {
    objectName: "testWindow"
    width: 1280
    height: 800
    ReaderView { anchors.fill: parent }
}
"""


class Catalog:
    def __init__(self, pages):
        self.pages = pages

    def list_pages(self, chapter_id):
        return list(self.pages)


def load_host(engine, host_qml, base_dir):
    """Compile+create the host document; returns the created root object.

    PySide6 6.11 keeps ownership of parent-less QML roots with the
    component: letting the local ``QQmlComponent`` be garbage-collected
    deletes the window out from under the test, so the component rides
    along on the created object.
    """
    component = QQmlComponent(engine)
    component.setData(host_qml.encode(), QUrl.fromLocalFile(str(base_dir / "host.qml")))
    if component.isError():
        raise RuntimeError(component.errorString())
    created = component.create()
    assert created is not None, component.errorString()
    created._test_component = component
    if isinstance(created, QQuickWindow):
        created.show()
    QGuiApplication.processEvents()
    return created


def click_button(button):
    """Emit AbstractButton.clicked via QMetaMethod: the QQuickItem wrapper
    is statically typed and has no clicked attribute (see ui_shell)."""
    meta = button.metaObject()
    index = meta.indexOfMethod("clicked()")
    assert index >= 0, "clicked() not found on button"
    meta.method(index).invoke(button)


def find_by_name(root, object_name):
    """Depth-first search over the QObject tree for an objectName."""
    if root.objectName() == object_name:
        return root
    for child in root.findChildren(QObject):
        if child.objectName() == object_name:
            return child
    return None


def pump(window, seconds=2.0, condition=None):
    deadline = _time.monotonic() + seconds
    while _time.monotonic() < deadline:
        QGuiApplication.processEvents()
        if condition is not None and condition():
            return True
        _time.sleep(0.02)
    return condition is not None and condition()


def pump_traced(window, seconds, condition):
    """``pump`` that also reports how much event-loop time was spent.

    TASK-034 AC ③: the registered flaky case fails inside a *bounded* wait, so
    the failure message must say whether the event loop was starved (few
    iterations) or the state simply never changed (many iterations). The wait
    budget and the assertions are unchanged — this only makes the failure
    diagnosable.
    """
    started = _time.monotonic()
    iterations = 0
    ok = False
    deadline = started + seconds
    while _time.monotonic() < deadline:
        QGuiApplication.processEvents()
        iterations += 1
        if condition():
            ok = True
            break
        _time.sleep(0.02)
    if not ok:
        ok = bool(condition())
    elapsed_ms = int((_time.monotonic() - started) * 1000)
    return ok, f"pump({seconds:g}s): iterations={iterations} elapsed_ms={elapsed_ms} ok={ok}"


def object_names(root, limit=25):
    """Collected ``objectName`` values, for failure diagnostics only."""
    if root is None:
        return []
    try:
        children = root.findChildren(QObject)
    except RuntimeError as error:  # pragma: no cover - deleted C++ object
        return [f"<unavailable: {error}>"]
    names = [child.objectName() for child in children if child.objectName()]
    return sorted(set(names))[:limit]


def webtoon_save_diagnostics(root, scroll, reading) -> str:
    """State trace for the webtoon scroll-save assertion."""
    content_y = safe_property(scroll, "contentY")
    image = find_by_name(root, "readerPage")
    status = safe_property(image, "status")
    return (
        f"scroll_contentY={content_y!r}"
        f" saved_scroll_offset_y={reading.progress.scroll_offset_y!r}"
        f" image_status={status!r}"
        f" object_names={object_names(root)}"
    )


@pytest.fixture()
def engine():
    qml_engine = QQmlEngine()
    yield qml_engine
    qml_engine.deleteLater()


def real_png_pages(tmp_path, count=3, page_height=60):
    """真 PNG 页面：QML Image 解码器必须能加载，webtoon 才有 contentHeight。

    ``page_height=1000``（``reader_stack_webtoon``） produces a page whose
    contentHeight can actually hold the 240 px scroll offset the webtoon
    contract test writes; the default 40x60 page tops out at contentHeight=60,
    which cannot scroll at all (see verification/TASK-037/clamp-race-probe.md).
    """
    from PySide6.QtGui import QColor, QImage

    rows = []
    for index in range(count):
        path = tmp_path / f"page_{index}.png"
        image = QImage(40, page_height, QImage.Format.Format_RGB32)
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


@pytest.fixture()
def reader_stack(tmp_path):
    pages = real_png_pages(tmp_path)
    reading = make_reading_service(tmp_path)
    export_service = make_service(tmp_path)
    vm = ReaderViewModel(reading, Catalog(pages), export_service=export_service)
    return vm, reading, pages


@pytest.fixture()
def reader_stack_webtoon(tmp_path):
    """reader_stack with tall (40x1000) pages so the webtoon Flickable's
    contentHeight (the page's natural height) can actually hold the 240 px
    scroll offset the save/restore contract test writes — with the 40x60
    default the content never becomes scrollable and the write races the
    StopAtBounds extent fixup (verification/TASK-037/clamp-race-probe.md).
    """
    pages = real_png_pages(tmp_path, page_height=1000)
    reading = make_reading_service(tmp_path)
    export_service = make_service(tmp_path)
    vm = ReaderViewModel(reading, Catalog(pages), export_service=export_service)
    return vm, reading, pages


class _EmptyCatalog:
    """ReaderPageCatalog double: an openable chapter that has no pages yet."""

    def list_pages(self, chapter_id):
        return []


@requires_pyside6
def test_reader_loads_with_injected_viewmodel_shows_empty_state(engine, tmp_path):
    """TASK-038 AC ①（前提变化的等价更新，非放宽）：生产装配
    （bootstrap.assemble_engine）自本切片起注入 readerViewModel——原用例
    "生产装配尚未注入 readerViewModel：页面必须可加载且显示空状态"的前提
    已不存在。本用例改为断言注入后的行为：以生产同型的方式注入一个尚未
    打开章节的 ViewModel（production assembly 走 _ManagedReaderCatalog；
    此处用无页面 catalog 等价），页面必须可加载、空态照常显示、注入的 VM
    被页面消费（hasChapter=False）。"""
    reading = make_reading_service(tmp_path)
    vm = ReaderViewModel(reading, _EmptyCatalog(), export_service=make_service(tmp_path))
    engine.rootContext().setContextProperty("readerViewModel", vm)
    window = load_host(engine, READER_HOST, SRC_QML / "reader")
    try:
        root = find_by_name(window, "readerView")
        assert root is not None
        empty = find_by_name(root, "readerEmptyState")
        assert empty is not None and bool(empty.property("visible"))
        assert find_by_name(root, "readerToolbar") is not None
        assert vm.hasChapter is False
    finally:
        window.close()


@requires_pyside6
def test_reader_shows_chapter_and_paging(engine, reader_stack):
    vm, reading, pages = reader_stack
    engine.rootContext().setContextProperty("readerViewModel", vm)
    window = load_host(engine, READER_HOST, SRC_QML / "reader")
    try:
        root = find_by_name(window, "readerView")
        vm.openChapter("b", "c", "第1话", "paged", "rtl")
        QGuiApplication.processEvents()
        title = find_by_name(root, "readerChapterTitle")
        assert title.property("text") == "第1话"
        progress = find_by_name(root, "readerProgress")
        assert "1 / 3" in progress.property("text")
        next_button = find_by_name(root, "readerNextPage")
        assert next_button.property("enabled")
        click_button(next_button)
        QGuiApplication.processEvents()
        assert vm.pageNumber == 2
        assert not find_by_name(root, "readerEmptyState").property("visible")
    finally:
        window.close()


@requires_pyside6
def test_reader_rtl_ltr_key_order(engine, reader_stack):
    """RTL 章节：Left 键前进（右→左阅读），Right 键后退 (D05 §39/AC-READ-003/004)。"""
    vm, reading, pages = reader_stack
    engine.rootContext().setContextProperty("readerViewModel", vm)
    window = load_host(engine, READER_HOST, SRC_QML / "reader")
    try:
        root = find_by_name(window, "readerView")
        vm.openChapter("b", "c", "第1话", "paged", "rtl")
        root.forceActiveFocus()
        QGuiApplication.processEvents()
        QTest.keyClick(window, Qt.Key_Left)
        assert vm.pageNumber == 2, "RTL: physical Left advances"
        QTest.keyClick(window, Qt.Key_Right)
        assert vm.pageNumber == 1, "RTL: physical Right goes back"

        vm.openChapter("b", "c", "第1话", "paged", "ltr")
        QTest.keyClick(window, Qt.Key_Right)
        assert vm.pageNumber == 2, "LTR: physical Right advances"
        QTest.keyClick(window, Qt.Key_Left)
        assert vm.pageNumber == 1, "LTR: physical Left goes back"
    finally:
        window.close()


@requires_pyside6
def test_reader_webtoon_swaps_in_vertical_viewer(engine, reader_stack_webtoon):
    vm, reading, pages = reader_stack_webtoon
    engine.rootContext().setContextProperty("readerViewModel", vm)
    window = load_host(engine, READER_HOST, SRC_QML / "reader")
    try:
        root = find_by_name(window, "readerView")
        vm.openChapter("b", "c", "条漫", "webtoon", "vertical")
        # TASK-034 AC ③: the swap is created by the QML after `openChapter`;
        # wait for it under a bound instead of assuming one processEvents()
        # delivered it (the assertion is unchanged, the failure now carries a
        # trace).
        swapped, trace = pump_traced(
            window, 5.0, lambda: find_by_name(root, "readerWebtoonScroll") is not None
        )
        scroll = find_by_name(root, "readerWebtoonScroll")
        assert swapped and scroll is not None, (
            "webtoon chapter swaps in the vertical Flickable — "
            f"{trace} {webtoon_save_diagnostics(root, scroll, reading)}"
        )
        # the page image loads asynchronously; contentHeight must exist
        # before contentY can be set past the clamp
        height_ok, height_trace = pump_traced(
            window, 5.0, lambda: safe_number(scroll, "contentHeight") > 0
        )
        assert height_ok, (
            "webtoon image never produced a scrollable height — "
            f"{height_trace} {webtoon_save_diagnostics(root, scroll, reading)}"
        )
        scroll.setProperty("contentY", 240.0)
        # The scroll offset must land and stay: with content that can hold a
        # 240 px offset the StopAtBounds extent has nothing to clamp back
        # (historically a 40x60 page capped contentHeight at 60 and the
        # extent fixup rewrote the write to -0.0, persisting 0 — see
        # verification/TASK-037/clamp-race-probe.md). This assertion turns
        # that race into an immediate, diagnosable failure (TASK-037 AC ①).
        landed = safe_number(scroll, "contentY")
        assert landed == 240.0, (
            "contentY write must land inside the scrollable extent — "
            f"contentY={landed!r} {webtoon_save_diagnostics(root, scroll, reading)}"
        )
        # the throttled save timer fires after ~500 ms
        saved_ok, saved_trace = pump_traced(
            window, 2.0, lambda: reading.progress.scroll_offset_y == 240.0
        )
        assert saved_ok, (
            "scroll_offset_y is saved through the service — "
            f"{saved_trace} {webtoon_save_diagnostics(root, scroll, reading)}"
        )

        # R-003: reopening restores the offset only once the image has
        # content height (never clamped to 0 by the empty Flickable)
        vm.openChapter("b", "c", "条漫", "webtoon", "vertical", True)
        scroll2 = None
        deadline = _time.monotonic() + 5
        reopen_iterations = 0
        while _time.monotonic() < deadline:
            QGuiApplication.processEvents()
            reopen_iterations += 1
            scroll2 = find_by_name(root, "readerWebtoonScroll")
            if scroll2 is not None and safe_number(scroll2, "contentHeight") > 0:
                break
            _time.sleep(0.05)
        assert scroll2 is not None, (
            "reopened webtoon viewer —"
            f" reopen_iterations={reopen_iterations}"
            f" {webtoon_save_diagnostics(root, scroll2, reading)}"
        )
        restored_ok, restored_trace = pump_traced(
            window, 5.0, lambda: safe_property(scroll2, "contentY") == 240.0
        )
        assert restored_ok, (
            "saved offset restored after image load,"
            f" got {safe_property(scroll2, 'contentY')!r} —"
            f" {restored_trace} {webtoon_save_diagnostics(root, scroll2, reading)}"
        )
    finally:
        window.close()


@requires_pyside6
def test_reader_mode_buttons_highlight_current(engine, reader_stack):
    vm, reading, pages = reader_stack
    engine.rootContext().setContextProperty("readerViewModel", vm)
    window = load_host(engine, READER_HOST, SRC_QML / "reader")
    try:
        root = find_by_name(window, "readerView")
        vm.openChapter("b", "c", "第1话", "paged", "rtl")
        QGuiApplication.processEvents()
        original = find_by_name(root, "readerModeOriginal")
        translated = find_by_name(root, "readerModeTranslated")
        assert original.property("highlighted") and not translated.property("highlighted")
        click_button(translated)
        QGuiApplication.processEvents()
        assert vm.mode == "translated"
        assert translated.property("highlighted") and not original.property("highlighted")
    finally:
        window.close()


def make_export_vm(tmp_path, pages):
    providers = to_export_pages(pages)
    return ExportViewModel(
        make_service(tmp_path),
        lambda: list(providers),
        book_id="b",
        chapter_id="c",
        output_dir=str(tmp_path / "out"),
    )


@requires_pyside6
def test_export_window_exposes_all_controls(engine, tmp_path):
    """D05 §51 字段与按钮 + D03 §31 历史动作。"""
    vm = make_export_vm(tmp_path, make_pages(tmp_path, count=2, translated=True))
    engine.rootContext().setContextProperty("exportViewModel", vm)
    component = QQmlComponent(engine, QUrl.fromLocalFile(str(SRC_QML / "windows" / "ExportWindow.qml")))
    assert not component.isError(), component.errorString()
    window = component.create()
    assert isinstance(window, QQuickWindow)
    window._test_component = component  # keep the owner alive (see load_host)
    try:
        # QQuickWindow content items are not parented to contentItem()
        # on the QObject tree — search from the window itself.
        assert find_by_name(window, "exportScope") is not None
        fmt = find_by_name(window, "exportFormat")
        assert fmt is not None and fmt.property("count") == 5, "五格式：单图/ZIP/CBZ/PDF/文本"
        assert find_by_name(window, "exportOverwritePolicy") is not None
        assert find_by_name(window, "exportStalePolicy") is not None
        assert find_by_name(window, "exportRunButton") is not None
        assert find_by_name(window, "exportCancelButton") is not None
        assert find_by_name(window, "exportOpenFolderButton") is not None
        assert find_by_name(window, "exportRepeatButton") is not None
        assert "2 页" in find_by_name(window, "exportScope").property("text")
    finally:
        window.close()


@requires_pyside6
def test_export_window_run_button_completes_export(engine, tmp_path):
    vm = make_export_vm(tmp_path, make_pages(tmp_path, count=2, translated=True))
    engine.rootContext().setContextProperty("exportViewModel", vm)
    component = QQmlComponent(engine, QUrl.fromLocalFile(str(SRC_QML / "windows" / "ExportWindow.qml")))
    window = component.create()
    window._test_component = component  # keep the owner alive (see load_host)
    try:
        run = find_by_name(window, "exportRunButton")
        status = find_by_name(window, "exportStatus")
        path_field = find_by_name(window, "exportOutputPath")
        assert run.property("enabled"), "export button must be enabled with pages"
        # Simulate the run button's onClicked exactly (PySide6 6.11 cannot
        # invoke the clicked() signal through QMetaMethod on this tree):
        # commit the field's path, start the export.
        vm.setOutputPath(path_field.property("text"))
        vm.startExport()
        assert pump(window, 5.0, lambda: not vm.running)
        QGuiApplication.processEvents()
        # the Connections→syncFromController binding must surface the result
        assert "导出完成" in status.property("text")
        assert (tmp_path / "out" / "c.zip").exists()
    finally:
        window.close()


@requires_pyside6
def test_export_window_stale_banner_surfaces(engine, tmp_path):
    """D06 §97：stale/缺译时窗口必须显示提示而不是静默导出。"""
    pages = make_pages(tmp_path, count=2, translated=True)
    providers = to_export_pages(pages)
    providers[0] = ExportPage(
        page_id="p0",
        filename=providers[0].filename,
        source_provider=providers[0].source_provider,
        translated_provider=providers[0].translated_provider,
        translated_revision_id="old",
        current_translated_revision_id="new",
    )
    providers[1] = ExportPage(
        page_id="p1",
        filename=providers[1].filename,
        source_provider=providers[1].source_provider,
        translated_provider=None,
    )
    vm = ExportViewModel(
        make_service(tmp_path),
        lambda: list(providers),
        book_id="b",
        chapter_id="c",
        output_dir=str(tmp_path / "out"),
    )
    engine.rootContext().setContextProperty("exportViewModel", vm)
    component = QQmlComponent(engine, QUrl.fromLocalFile(str(SRC_QML / "windows" / "ExportWindow.qml")))
    window = component.create()
    window._test_component = component  # keep the owner alive (see load_host)
    try:
        banner = find_by_name(window, "exportStaleBanner")
        assert banner.property("visible") and banner.property("text") != ""
        assert "不是最新渲染" in banner.property("text")
    finally:
        window.close()
