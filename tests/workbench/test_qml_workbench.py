"""QML workbench end-to-end tests (TASK-013).

Loads ``src/ui/qml/workbench/WorkbenchView.qml`` inside an ApplicationWindow
host with the real WorkbenchViewModel published as the ``workbenchViewModel``
context property — the assembly bootstrap will perform. Asserts the D05
§16 five fixed areas, the D06 §103 button matrix through QML, the
AC-PROGRESS statistic→filter linkage, and the dirty-confirm dialog flow.

Harness notes inherited from tests/ui_shell (PySide6 6.11): runs on the
default Windows platform; delegate items are reached via ListView helpers
or objectName lookups on declared items only.
"""

from __future__ import annotations

import time

import workbench_helpers  # noqa: F401  (sys.path injection)
from workbench_helpers import (
    FakeRegion,
    fail_first_region_step,
    make_pipeline,
    make_vm,
    wait_until,
)

import pytest

from PySide6.QtCore import QObject, QUrl
from PySide6.QtQml import QQmlComponent, QQmlEngine

WORKBENCH_DIR = workbench_helpers.SRC_ROOT / "ui" / "qml" / "workbench"
WORKBENCH_QML = WORKBENCH_DIR / "WorkbenchView.qml"

HOST_QML = """
import QtQuick
import QtQuick.Controls
ApplicationWindow {
    objectName: "testWindow"
    width: 1280
    height: 800
    WorkbenchView { anchors.fill: parent }
}
"""

# Standalone overlay host: the fit rect is driven by width/height alone, so
# the item->normalized half of the coordinate chain can be pinned at any
# display scale without a mouse.
OVERLAY_HOST_QML = """
import QtQuick
Rectangle {
    objectName: "overlayHost"
    width: 600
    height: 600
    RegionOverlay {
        objectName: "standaloneOverlay"
        width: 600
        height: 600
        pageW: 800
        pageH: 1200
    }
}
"""


def find_one(root, object_name):
    listed = root.findChildren(QObject, object_name)
    assert listed, f"expected an item named {object_name!r} in the workbench"
    return listed[0]


def click_button(button):
    meta = button.metaObject()
    index = meta.indexOfMethod("clicked()")
    assert index >= 0, f"clicked() not found on {button.objectName()}"
    meta.method(index).invoke(button)


def js_pair(value):
    """Read a QML ``[number, number]`` return without a production shim.

    A JS array crosses into Python as an opaque QJSValue; JS ``null`` arrives
    as ``None``, which is what the rejection cases assert on.
    """
    if value is None:
        return None
    assert value.isArray(), "expected a JS array from toNormalized()"
    return [value.property(0).toNumber(), value.property(1).toNumber()]


@pytest.fixture()
def qml_only(qapp):
    """Engine without a workbenchViewModel — TASK-012 shell semantics."""
    engine = QQmlEngine(None)
    component = QQmlComponent(engine)
    component.setData(
        HOST_QML.encode(),
        QUrl.fromLocalFile(str(WORKBENCH_DIR / "_TestHost.qml")),
    )
    assert component.isReady(), [e.toString() for e in component.errors()]
    window = component.create()
    assert window is not None
    qapp.processEvents()
    yield window
    window.deleteLater()
    engine.deleteLater()
    qapp.processEvents()


@pytest.fixture()
def workbench(qapp):
    """Engine with a real WorkbenchViewModel + a 4-page chapter."""
    from application.translation.pipeline.executor import DeterministicStepExecutor

    executor = DeterministicStepExecutor(fail_on=fail_first_region_step(("p2", "p4")))
    service, _ = make_pipeline(
        pages=[(f"p{i}", i) for i in range(1, 5)], executor=executor
    )
    vm = make_vm(
        service,
        pages=[
            workbench_helpers.FakePage(f"p{i}", "chapter-1", i, f"{i:03d}.jpg")
            for i in range(1, 5)
        ],
        regions=[FakeRegion("r1", "p1", 0, machine_translation="机器一")],
    )
    engine = QQmlEngine(None)
    engine.rootContext().setContextProperty("workbenchViewModel", vm)
    component = QQmlComponent(engine)
    component.setData(
        HOST_QML.encode(),
        QUrl.fromLocalFile(str(WORKBENCH_DIR / "_TestHost.qml")),
    )
    assert component.isReady(), [e.toString() for e in component.errors()]
    window = component.create()
    assert window is not None
    qapp.processEvents()
    view = window.findChild(QObject, "workbenchView")
    assert view is not None
    harness = type("Harness", (), {})()
    harness.vm = vm
    harness.engine = engine
    harness.window = window
    harness.view = view
    yield harness
    window.deleteLater()
    engine.deleteLater()
    qapp.processEvents()


@pytest.fixture()
def overlay_item(qapp):
    """A RegionOverlay sized from the test, over an 800x1200 page."""
    engine = QQmlEngine(None)
    component = QQmlComponent(engine)
    component.setData(
        OVERLAY_HOST_QML.encode(),
        QUrl.fromLocalFile(str(WORKBENCH_DIR / "_OverlayHost.qml")),
    )
    assert component.isReady(), [e.toString() for e in component.errors()]
    root = component.create()
    assert root is not None
    qapp.processEvents()
    item = root.findChild(QObject, "standaloneOverlay")
    assert item is not None
    yield item
    root.deleteLater()
    engine.deleteLater()
    qapp.processEvents()


# ----------------------------------------------------------------------
# D05 §62 empty state without a viewmodel / context
# ----------------------------------------------------------------------


def test_no_viewmodel_keeps_honest_empty_state(qml_only):
    pick = qml_only.findChild(QObject, "workbenchPickContext")
    assert pick is not None
    assert bool(pick.property("enabled")) is False
    empty = qml_only.findChild(QObject, "workbenchView")
    assert empty is not None


def test_viewmodel_without_context_shows_empty_state(workbench):
    pick = find_one(workbench.view, "workbenchPickContext")
    assert bool(pick.property("enabled")) is False


# ----------------------------------------------------------------------
# five fixed areas + projection display
# ----------------------------------------------------------------------


def test_context_reveals_all_five_fixed_areas(workbench, qapp):
    workbench.vm.setContext("book-1", "chapter-1", "测试书", "第1话")
    qapp.processEvents()

    for name in (
        "workbenchToolbarHost",
        "pageListPanelHost",
        "viewerPanelHost",
        "regionInspectorHost",
        "taskProgressPanelHost",
    ):
        item = find_one(workbench.view, name)
        assert bool(item.property("visible")) is True, name

    list_view = find_one(workbench.view, "pageListView")
    assert int(list_view.property("count")) == 4

    panel = find_one(workbench.view, "taskProgressPanelHost")
    # AC-PROGRESS-001: the panel exists fixed at the bottom even with no run
    assert bool(panel.property("visible")) is True


def test_task_progress_reflects_run_through_qml(workbench, qapp):
    workbench.vm.setContext("book-1", "chapter-1", "书", "章")
    workbench.vm.startTranslateAll()
    assert wait_until(qapp, lambda: workbench.vm.taskProgress["run_status"]
                      == "completed_with_failures", timeout_ms=10000)

    title = find_one(workbench.view, "taskProgressTitle")
    assert title.property("text") == "全部翻译"
    status = find_one(workbench.view, "taskProgressStatus")
    assert status.property("text") == "已完成（有失败）"
    percent = find_one(workbench.view, "taskProgressPercent")
    assert percent.property("text") == "100%"

    # terminal state → all three main controls disabled (D06 §103)
    for name in ("btnPauseRun", "btnStopRun", "btnContinueRun"):
        button = find_one(workbench.view, name)
        assert bool(button.property("enabled")) is False, name
    retry = find_one(workbench.view, "btnRetryFailed")
    assert bool(retry.property("visible")) is True


def test_statistic_click_filters_pagelist_through_qml(workbench, qapp):
    """AC-PROGRESS-004: clicking 失败 2 filters the visible tiles."""

    workbench.vm.setContext("book-1", "chapter-1", "书", "章")
    workbench.vm.startTranslateAll()
    assert wait_until(qapp, lambda: workbench.vm.taskProgress["failed_page_count"]
                      == 2, timeout_ms=10000)

    list_view = find_one(workbench.view, "pageListView")
    assert int(list_view.property("count")) == 4
    click_button(find_one(workbench.view, "statFailed"))
    assert int(list_view.property("count")) == 2
    click_button(find_one(workbench.view, "statWaiting"))
    assert int(list_view.property("count")) == 4


# ----------------------------------------------------------------------
# dirty dialog flow through QML
# ----------------------------------------------------------------------


def test_dirty_confirm_dialog_blocks_and_resumes(workbench, qapp):
    workbench.vm.setContext("book-1", "chapter-1", "书", "章")
    workbench.vm.selectPage("p1")
    workbench.vm.selectRegion("r1")
    qapp.processEvents()

    # simulate user typing in the inspector textarea
    editor_input = find_one(workbench.view, "inspectorTranslationInput")
    editor_input.setProperty("text", "人工校正文本")
    assert workbench.vm.hasDirtyEditor is True
    assert bool(find_one(workbench.view, "inspectorDirtyBadge")
                .property("visible")) is True

    # click another page → dialog opens, viewer does not switch yet
    vm_select = workbench.vm
    vm_select.selectPage("p2")
    qapp.processEvents()
    dialog = find_one(workbench.view, "dirtyConfirmDialogHost")
    assert bool(dialog.property("visible")) is True
    assert workbench.vm.viewerPageId == "p1"

    # cancel keeps everything
    click_button(find_one(workbench.view, "dirtyCancel"))
    qapp.processEvents()
    assert bool(dialog.property("visible")) is False
    assert workbench.vm.viewerPageId == "p1"
    assert workbench.vm.inspectorText == "人工校正文本"

    # retry, then discard → viewer moves, edit dropped
    workbench.vm.selectPage("p2")
    click_button(find_one(workbench.view, "dirtyDiscard"))
    qapp.processEvents()
    assert workbench.vm.viewerPageId == "p2"
    assert workbench.vm.hasDirtyEditor is False


def test_toolbar_mode_switch_roundtrip(workbench, qapp):
    workbench.vm.setContext("book-1", "chapter-1", "书", "章")
    workbench.vm.selectPage("p1")
    click_button(find_one(workbench.view, "modeCompare"))
    assert workbench.vm.viewerMode == "compare"
    assert find_one(workbench.view, "viewerModeLabel").property("text") == "对比"
    assert bool(find_one(workbench.view, "viewerComparePane")
                .property("visible")) is True


# ----------------------------------------------------------------------
# TASK-052: the command-error bar (provisional minimal visibility)
# ----------------------------------------------------------------------


def test_command_error_bar_visible_only_when_a_failure_is_held(workbench, qapp):
    """AC ②/④: the bar is a real QML element (objectName-addressable),
    it becomes visible when the VM holds a failure, the copy action runs
    without error, and dismissing it hides the bar again."""
    workbench.vm.setContext("book-1", "chapter-1", "书", "章")
    qapp.processEvents()
    bar = workbench.view.findChild(QObject, "commandErrorBar")
    assert bar is not None
    qapp.processEvents()
    assert bool(bar.property("visible")) is False  # idle: nothing held

    # a real VM failure path (selection guard) feeds the surface
    workbench.vm.startTranslateSelected()
    qapp.processEvents()
    assert bool(bar.property("visible")) is True
    text_item = workbench.view.findChild(QObject, "commandErrorText")
    assert text_item is not None
    assert "未选择任何 Page" in str(text_item.property("text"))
    run_status_before_dismiss = workbench.vm.runStatus

    # copy action runs the clipboard helper without error
    copy_button = workbench.view.findChild(QObject, "commandErrorCopyButton")
    assert copy_button is not None
    click_button(copy_button)

    # dismiss hides the bar and clears the VM state
    close_button = workbench.view.findChild(QObject, "commandErrorCloseButton")
    assert close_button is not None
    source = WORKBENCH_QML.read_text(encoding="utf-8")
    binding = 'Accessible.name: "关闭错误提示"'
    assert binding in source
    assert binding not in source.replace(binding, 'Accessible.name: ""', 1)
    click_button(close_button)
    qapp.processEvents()
    assert workbench.vm.commandErrorText == ""
    assert workbench.vm.runStatus == run_status_before_dismiss
    assert bool(bar.property("visible")) is False


# ----------------------------------------------------------------------
# T1.1.2: region drawing overlay
# ----------------------------------------------------------------------


def test_region_overlay_mounts_and_follows_viewer_mode(workbench, qapp):
    # Load/visibility only, by design: synthetic mouse drags are exactly the
    # flakiness this repo already documents, so the interaction is covered by
    # the viewmodel tests and the conversion by test_region_canvas.py.
    workbench.vm.setContext("book-1", "chapter-1", "测试书", "第1话")
    workbench.vm.selectPage("p1")
    qapp.processEvents()

    overlay = find_one(workbench.view, "viewerRegionOverlay")
    assert bool(overlay.property("visible")) is True
    assert overlay.property("drawingMode") == "rect"

    workbench.vm.setViewerMode("translated")
    qapp.processEvents()
    assert bool(overlay.property("visible")) is False

    workbench.vm.setViewerMode("original")
    qapp.processEvents()
    assert bool(overlay.property("visible")) is True


def test_overlay_scales_by_the_viewmodel_extent_not_the_image(workbench, qapp):
    # The fixture's FakePages carry no width/height, so the viewmodel reports
    # 0x0: scale must stay 0 and input disabled, rather than the overlay
    # silently borrowing Image.sourceSize and drifting from the converter.
    workbench.vm.setContext("book-1", "chapter-1", "测试书", "第1话")
    workbench.vm.selectPage("p1")
    qapp.processEvents()
    overlay = find_one(workbench.view, "viewerRegionOverlay")
    assert float(overlay.property("scale")) == 0.0
    input_area = overlay.findChild(QObject, "regionOverlayInput")
    assert input_area is not None
    assert bool(input_area.property("enabled")) is False


def test_overlay_tool_buttons_switch_the_drawing_mode(workbench, qapp):
    # Polygon creation is unreachable without a mode switch, so the control
    # belongs to this slice instead of being deferred to later polish.
    workbench.vm.setContext("book-1", "chapter-1", "测试书", "第1话")
    workbench.vm.selectPage("p1")
    workbench.vm._pages["p1"].update(width=800, height=1200)
    workbench.vm.viewerChanged.emit()
    qapp.processEvents()

    overlay = find_one(workbench.view, "viewerRegionOverlay")
    assert overlay.property("drawingMode") == "rect"
    assert bool(find_one(overlay, "regionToolRect").property("enabled")) is True
    assert bool(find_one(overlay, "regionToolPolygon").property("enabled")) is True

    click_button(find_one(overlay, "regionToolPolygon"))
    assert overlay.property("drawingMode") == "polygon"

    click_button(find_one(overlay, "regionToolRect"))
    assert overlay.property("drawingMode") == "rect"


# ----------------------------------------------------------------------
# T1.1.2: the item -> normalized half of the coordinate chain
# ----------------------------------------------------------------------


def test_overlay_reproduces_the_documented_worked_example(overlay_item):
    # doc/tasks/TASK-013.md: page 800x1200 in a 600x600 pane gives scale 0.5
    # and a fit rect spanning item x 100..500. A drag from (150,100) to
    # (350,400) must normalize to the pair documented to become
    # bbox [100, 200, 400, 600] on the page.
    from ui.viewmodels.workbench.region_canvas import normalized_to_page_geometry

    assert float(overlay_item.property("scale")) == 0.5
    assert float(overlay_item.property("offsetX")) == 100
    assert float(overlay_item.property("offsetY")) == 0

    corner_a = js_pair(overlay_item.toNormalized(150, 100))
    corner_b = js_pair(overlay_item.toNormalized(350, 400))
    assert corner_a == [0.125, 1 / 6]
    assert corner_b == [0.625, 2 / 3]

    geometry = normalized_to_page_geometry([corner_a, corner_b], 800, 1200)
    assert geometry.bbox.as_tuple() == (100, 200, 400, 600)


def test_page_pixels_survive_the_round_trip_at_every_display_scale(overlay_item):
    # The acceptance list requires the mapping be proven by test rather than
    # judged by eye: a page location taken out to item coordinates through the
    # fit rect has to come back as the same canonical pixel at any viewport,
    # including the two extreme sides of letterboxing.
    from ui.viewmodels.workbench.region_canvas import normalized_to_page_geometry

    page_w, page_h = 800, 1200
    rectangles = [
        ((100, 200), (500, 800)),
        ((0, 0), (799, 1199)),
        ((400, 600), (799, 1199)),
    ]
    viewports = [
        (600, 600),    # fit to window
        (800, 1200),   # 1:1
        (1600, 2400),  # magnified past the page
        (400, 600),    # reduced to half
        (1000, 600),   # wide pane: bands left and right
        (600, 1400),   # tall pane: bands top and bottom
    ]
    for width, height in viewports:
        overlay_item.setProperty("width", width)
        overlay_item.setProperty("height", height)
        scale = float(overlay_item.property("scale"))
        offset_x = float(overlay_item.property("offsetX"))
        offset_y = float(overlay_item.property("offsetY"))
        assert scale == pytest.approx(min(width / page_w, height / page_h))
        for (ax, ay), (bx, by) in rectangles:
            corner_a = js_pair(overlay_item.toNormalized(
                ax * scale + offset_x, ay * scale + offset_y
            ))
            corner_b = js_pair(overlay_item.toNormalized(
                bx * scale + offset_x, by * scale + offset_y
            ))
            assert corner_a is not None and corner_b is not None
            geometry = normalized_to_page_geometry(
                [corner_a, corner_b], page_w, page_h
            )
            expected = (min(ax, bx), min(ay, by), abs(bx - ax), abs(by - ay))
            assert geometry.bbox.as_tuple() == expected, (width, height, expected)


def test_overlay_refuses_a_stroke_started_in_the_letterbox_band(overlay_item):
    # Clamping a band start to the page edge would persist a box hugging the
    # page that nobody drew. Refusal is the only honest answer, and the band
    # exists solely in viewport space, so this is the one place that can know.
    assert float(overlay_item.property("offsetX")) == 100
    assert overlay_item.toNormalized(5, 300) is None
    assert overlay_item.toNormalized(595, 300) is None
    assert js_pair(overlay_item.toNormalized(100, 0)) == [0.0, 0.0]
    assert js_pair(overlay_item.toNormalized(500, 600)) == [1.0, 1.0]


def test_overlay_without_a_page_extent_maps_nothing(overlay_item):
    # No extent must mean no input, not a division that yields a stray value.
    overlay_item.setProperty("pageW", 0)
    assert float(overlay_item.property("scale")) == 0.0
    assert overlay_item.toNormalized(150, 100) is None


def test_workbench_panel_geometry_comes_from_the_f_tokens(workbench, qapp):
    # T2.1.1 binds the workbench areas to tb-h / insp-w / prog-h. The numbers
    # here are the accepted geometry, so a re-pasted literal is a regression
    # against the design rather than a style preference.
    workbench.vm.setContext("book-1", "chapter-1", "书", "章")
    qapp.processEvents()
    for name, prop, expected in (
        ("workbenchToolbarHost", "implicitHeight", 52),
        ("regionInspectorHost", "implicitWidth", 288),
        ("taskProgressPanelHost", "implicitHeight", 150),
    ):
        panel = find_one(workbench.view, name)
        assert int(panel.property(prop)) == expected, f"{name}.{prop}"
