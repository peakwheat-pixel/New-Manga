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


def find_one(root, object_name):
    listed = root.findChildren(QObject, object_name)
    assert listed, f"expected an item named {object_name!r} in the workbench"
    return listed[0]


def click_button(button):
    meta = button.metaObject()
    index = meta.indexOfMethod("clicked()")
    assert index >= 0, f"clicked() not found on {button.objectName()}"
    meta.method(index).invoke(button)


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
