"""WorkbenchViewModel behavior (TASK-013 AC 1~3).

Covers context loading, single/ctrl/shift selection, viewer-vs-pipeline
page separation, command entries executed on the worker thread,
pause/stop/continue with optimistic feedback, failure-filter linkage,
dirty navigation guard, and the 4 Hz progress throttle.
"""

from __future__ import annotations

import time

import workbench_helpers  # noqa: F401  (sys.path injection)
from workbench_helpers import (
    FakeEditor,
    FakeNavigation,
    FakePage,
    FakeRegion,
    FakeRegionWriter,
    fail_first_region_step,
    make_pipeline,
    make_vm,
    pages_list,
    wait_until,
)

import pytest

from application.translation.pipeline.executor import DeterministicStepExecutor
from domain.regions.entities import BBox, RegionGeometry
from domain.tasks.models import ScopeType


def slow_executor(seconds_per_step: float = 0.02) -> DeterministicStepExecutor:
    """Enough total delay that a control request lands mid-run."""

    return DeterministicStepExecutor(
        on_execute=lambda *a: time.sleep(seconds_per_step)
    )


@pytest.fixture()
def qapp_(qapp):
    yield qapp


def completed_vm():
    pages = pages_list(4)
    service, _ = make_pipeline(pages=pages)
    vm = make_vm(
        service,
        pages=[
            FakePage(page_id, "chapter-1", order, f"{order:03d}.jpg")
            for page_id, order in pages
        ],
    )
    vm.setContext("book-1", "chapter-1", "测试书", "第1话")
    return service, vm


# ----------------------------------------------------------------------
# context + selection
# ----------------------------------------------------------------------


def test_context_loads_pages_into_idle_projection(qapp_):
    service, vm = completed_vm()
    assert vm.hasContext is True
    model = vm.pageListModel
    assert model.rowCount() == 4
    progress = vm.taskProgress
    assert progress["run_status"] == "idle"
    assert progress["total_page_count"] == 4
    assert progress["waiting_page_count"] == 4
    assert progress["run_title"] == ""
    assert progress["active"] is False


def test_empty_context_state(qapp_):
    service, _ = make_pipeline()
    vm = make_vm(service)
    assert vm.hasContext is False
    vm.setContext("", "", "", "")
    assert vm.hasContext is False


def test_single_select_opens_viewer_and_keeps_pipeline_focus_separate(qapp_):
    """AC 2: the viewer page and the pipeline focus page are different
    pieces of state (D05 §18.3)."""

    service, vm = completed_vm()
    vm.selectPage("p2")
    assert vm.viewerPageId == "p2"
    # no run yet → no pipeline focus, but the viewer keeps its page
    assert vm.taskProgress["current_page_id"] == ""
    assert vm.viewerPageId == "p2"

    vm.selectPage("p1")
    assert vm.viewerPageId == "p1"


def test_step_page_is_viewmodel_owned_and_clamped(qapp_):
    _, vm = completed_vm()
    vm.selectPage("p2")

    vm.stepPage(1)
    assert vm.viewerPageId == "p3"
    vm.stepPage(99)
    assert vm.viewerPageId == "p4"
    vm.stepPage(-99)
    assert vm.viewerPageId == "p1"


def test_ctrl_and_shift_multi_select(qapp_):
    service, vm = completed_vm()
    vm.togglePageSelected("p1")
    vm.togglePageSelected("p3")
    assert vm.selectedPageIds == ["p1", "p3"]
    assert vm.selectedPageCount == 2

    vm.clearSelection()
    assert vm.selectedPageIds == []

    # shift-select builds a contiguous range from the anchor
    vm.togglePageSelected("p2")
    vm.selectRangeTo("p4")
    assert vm.selectedPageIds == ["p2", "p3", "p4"]


# ----------------------------------------------------------------------
# command entries + worker execution
# ----------------------------------------------------------------------


def test_translate_all_runs_to_completed_on_worker(qapp_):
    service, vm = completed_vm()
    finished = []
    vm.runFinished.connect(lambda run_id, status: finished.append(status))
    vm.startTranslateAll()

    assert wait_until(qapp_, lambda: bool(finished), timeout_ms=10000)
    assert finished == ["completed"]
    progress = vm.taskProgress
    assert progress["run_status"] == "completed"
    assert progress["completed_page_count"] == 4
    assert progress["progress_percent"] == 100
    assert progress["active"] is False  # controller released after finish


def test_command_scope_uses_selection(qapp_):
    service, vm = completed_vm()
    vm.togglePageSelected("p2")
    vm.togglePageSelected("p3")
    vm.startTranslateSelected()

    assert wait_until(qapp_, lambda: vm.taskProgress["run_status"] == "completed")
    # scope carried the two selected pages
    run = vm._run
    assert run.scope.scope_type.value == "page_selection"
    assert sorted(run.scope.selected_ids) == ["p2", "p3"]


def test_translate_selected_without_selection_errors(qapp_):
    service, vm = completed_vm()
    errors = []
    vm.commandError.connect(errors.append)
    vm.startTranslateSelected()
    assert errors == ["未选择任何 Page"]


def test_region_command_requires_region(qapp_):
    service, vm = completed_vm()
    errors = []
    vm.commandError.connect(errors.append)
    vm.startRegionCommand("ocr_region")
    assert errors == ["未选择 Region"]


# ----------------------------------------------------------------------
# pause / stop / continue (AC 3)
# ----------------------------------------------------------------------


def test_pause_shows_optimistic_feedback_immediately(qapp_):
    """AC-PAUSE-001: ≤200 ms “正在暂停” — the viewmodel flips the flag
    synchronously on click, long before the executor boundary."""

    service, _ = make_pipeline(
        pages=[(f"p{i}", i) for i in range(1, 9)], executor=slow_executor()
    )
    vm = make_vm(service)
    vm.setContext("book-1", "chapter-1", "书", "章")
    vm.startTranslateAll()

    started = time.monotonic()
    vm.pauseRun()
    elapsed_ms = (time.monotonic() - started) * 1000

    assert elapsed_ms <= 200
    assert vm.taskProgress["pausing"] is True
    assert vm.taskProgress["can_pause"] is False  # 暂停中不可重复暂停

    assert wait_until(
        qapp_, lambda: vm.taskProgress["run_status"] == "paused", timeout_ms=15000
    )
    assert vm.taskProgress["pausing"] is False
    assert vm.taskProgress["can_continue"] is True

    vm.continueRun()
    assert wait_until(
        qapp_, lambda: vm.taskProgress["run_status"] == "completed", timeout_ms=15000
    )


def test_stop_cancels_running_job(qapp_):
    """AC-STOP-001/002: stop keeps committed pages, cancels the rest."""

    service, _ = make_pipeline(
        pages=[(f"p{i}", i) for i in range(1, 13)], executor=slow_executor()
    )
    vm = make_vm(service)
    vm.setContext("book-1", "chapter-1", "书", "章")
    vm.startTranslateAll()
    assert wait_until(qapp_, lambda: vm.taskProgress["active"] is True)
    # let at least one page commit so AC-STOP-001 “已有页完成仍保留” holds
    assert wait_until(
        qapp_, lambda: vm.taskProgress["completed_page_count"] >= 1,
        timeout_ms=15000,
    )

    vm.stopRun()
    assert wait_until(
        qapp_, lambda: vm.taskProgress["run_status"] == "cancelled", timeout_ms=15000
    )
    progress = vm.taskProgress
    assert progress["completed_page_count"] >= 1  # committed pages remain
    assert progress["can_stop"] is False


def test_run_badge_and_terminal_refresh(qapp_):
    """D05 §3.1 badge follows the run; terminal state refreshes at once."""

    navigation = FakeNavigation()
    service, _ = make_pipeline(pages=[("p1", 1), ("p2", 2)])
    vm = make_vm(service, navigation=navigation)
    vm.setContext("book-1", "chapter-1", "书", "章")

    vm.startTranslateAll()
    assert wait_until(
        qapp_, lambda: vm.taskProgress["run_status"] == "completed"
    )
    # the badge returned to idle once the run left “running”
    assert navigation.activity == (False, "")


# ----------------------------------------------------------------------
# failure linkage (AC-PROGRESS-004/006)
# ----------------------------------------------------------------------


def test_failure_statistic_filters_pagelist(qapp_):
    executor = DeterministicStepExecutor(fail_on=fail_first_region_step(("p2", "p4")))
    service, _ = make_pipeline(
        pages=[(f"p{i}", i) for i in range(1, 5)], executor=executor
    )
    vm = make_vm(service)
    vm.setContext("book-1", "chapter-1", "书", "章")

    vm.startTranslateAll()
    assert wait_until(
        qapp_, lambda: vm.taskProgress["run_status"] == "completed_with_failures",
        timeout_ms=10000,
    )
    progress = vm.taskProgress
    assert progress["failed_page_count"] == 2
    assert progress["completed_page_count"] == 2
    assert progress["can_retry_failed"] is True

    vm.filterByStatus("failed")
    assert vm.pageListModel.rowCount() == 2
    vm.clearPageFilter()
    assert vm.pageListModel.rowCount() == 4


def test_retry_failed_pages_creates_and_finishes_new_run(qapp_):
    executor = DeterministicStepExecutor(fail_on=fail_first_region_step(("p2",)))
    service, _ = make_pipeline(
        pages=[(f"p{i}", i) for i in range(1, 4)], executor=executor
    )
    vm = make_vm(service)
    vm.setContext("book-1", "chapter-1", "书", "章")

    vm.startTranslateAll()
    assert wait_until(qapp_, lambda: vm.taskProgress["can_retry_failed"] is True)
    first_run_id = vm.taskProgress["run_id"]

    vm.retryFailedPages()
    assert wait_until(
        qapp_,
        lambda: vm.taskProgress["run_status"] == "completed_with_failures"
        and vm.taskProgress["active"] is False,
    )
    # a fresh run targeting only the failed page went through the cycle
    assert vm.taskProgress["run_id"] != first_run_id
    assert vm.taskProgress["failed_page_count"] == 1
    assert vm.taskProgress["total_page_count"] == 1


# ----------------------------------------------------------------------
# inspector + dirty guard (D05 §55)
# ----------------------------------------------------------------------


def regioned_vm():
    service, _ = make_pipeline(pages=[("p1", 1), ("p2", 2)])
    regions = [
        FakeRegion("r1", "p1", reading_order=0, machine_translation="机器译文一"),
        FakeRegion("r2", "p1", reading_order=1, final_translation="终稿二"),
        FakeRegion("r3", "p2", reading_order=0),
    ]
    editor = FakeEditor()
    vm = make_vm(service, regions=regions, editor=editor)
    vm.setContext("book-1", "chapter-1", "书", "章")
    return vm, editor


def test_inspector_lists_regions_and_selects(qapp_):
    vm, _editor = regioned_vm()
    vm.selectPage("p1")
    regions = vm.inspectorRegions
    assert [region["region_id"] for region in regions] == ["r1", "r2"]
    assert regions[0]["translation"] == "机器译文一"
    assert regions[1]["translation"] == "终稿二"  # final beats machine

    vm.selectRegion("r1")
    assert vm.inspectorRegionId == "r1"
    assert vm.inspectorText == "机器译文一"
    assert vm.hasDirtyEditor is False


def test_dirty_flow_save_and_discard(qapp_):
    vm, editor = regioned_vm()
    vm.selectPage("p1")
    vm.selectRegion("r1")
    vm.setInspectorText("人工校正")
    assert vm.hasDirtyEditor is True

    vm.saveInspector()
    assert editor.saved == [("r1", "人工校正")]
    assert vm.hasDirtyEditor is False

    vm.setInspectorText("再改")
    vm.discardInspector()
    assert vm.inspectorText == "人工校正"
    assert vm.hasDirtyEditor is False
    assert editor.saved == [("r1", "人工校正")]


def test_dirty_navigation_guard_intercepts_page_switch(qapp_):
    """AC 3: Dirty 导航不丢编辑 — the switch waits for save/discard/cancel."""

    vm, editor = regioned_vm()
    confirms = []
    vm.inspectorDirtyConfirmRequested.connect(
        lambda target: confirms.append(target)
    )
    vm.selectPage("p1")
    vm.selectRegion("r1")
    vm.setInspectorText("未保存的修改")

    vm.selectPage("p2")
    assert confirms, "dirty switch must raise the confirm"
    assert vm.viewerPageId == "p1"  # not switched yet

    vm.resolveDirtyConfirm("cancel")
    assert vm.viewerPageId == "p1"
    assert vm.inspectorText == "未保存的修改"

    vm.selectPage("p2")  # guard re-arms
    vm.resolveDirtyConfirm("save")
    assert editor.saved[-1] == ("r1", "未保存的修改")
    assert vm.viewerPageId == "p2"
    assert vm.hasDirtyEditor is False


def test_dirty_navigation_discard_switches(qapp_):
    vm, editor = regioned_vm()
    vm.selectPage("p1")
    vm.selectRegion("r1")
    vm.setInspectorText("丢弃我")
    vm.selectPage("p2")
    vm.resolveDirtyConfirm("discard")
    assert vm.viewerPageId == "p2"
    assert editor.saved == []
    assert vm.hasDirtyEditor is False


# ----------------------------------------------------------------------
# throttle (AC-NFR-UI-002)
# ----------------------------------------------------------------------


def test_progress_throttle_constant_is_about_4hz():
    from ui.viewmodels.workbench.viewmodel import PROGRESS_REFRESH_MS

    assert 200 <= PROGRESS_REFRESH_MS <= 300, "AC-NFR-UI-002 targets ~4 Hz"


def test_refresh_timer_merges_updates(qapp_):
    """While a run is active the timer drives ~4 Hz refreshes; manual
    refreshProgress (key events) applies immediately."""

    service, _ = make_pipeline(
        pages=[(f"p{i}", i) for i in range(1, 7)], executor=slow_executor(0.05)
    )
    vm = make_vm(service)
    vm.setContext("book-1", "chapter-1", "书", "章")

    ticks = []
    vm.taskProgressChanged.connect(lambda: ticks.append(time.monotonic()))

    vm.startTranslateAll()
    assert wait_until(qapp_, lambda: vm.taskProgress["active"] is True)

    # ~1s window with a 250 ms timer → at most ~6 ticks, never one per step
    time.sleep(1.0)
    qapp_.processEvents()
    in_window = [tick for tick in ticks if tick >= ticks[0]]
    assert len(in_window) <= 8, f"throttle violated: {len(in_window)} refreshes/s"

    vm.shutdown()


def test_manual_refresh_applies_projection_immediately(qapp_):
    service, _ = make_pipeline(pages=[("p1", 1), ("p2", 2)])
    vm = make_vm(service)
    vm.setContext("book-1", "chapter-1", "书", "章")
    run = service.create_run("translate_all", ScopeType.CHAPTER, chapter_id="chapter-1")
    service.plan_run(run.run_id)
    # inject the run without the controller to observe pure refresh path
    vm._run = run
    vm.refreshProgress()
    assert vm.taskProgress["run_status"] == "pending"
    assert vm.taskProgress["total_page_count"] == 2


# ----------------------------------------------------------------------
# viewer modes / images
# ----------------------------------------------------------------------


def test_viewer_mode_switch_and_image_url(qapp_):
    from pathlib import Path

    original = Path(workbench_helpers.SRC_ROOT) / "x.png"
    service, _ = make_pipeline(pages=[("p1", 1)])
    vm = make_vm(
        service,
        pages=[FakePage("p1", "chapter-1", 1, "001.jpg",
                        managed_original_ref=str(original))],
    )
    vm.setContext("book-1", "chapter-1", "书", "章")
    vm.selectPage("p1")

    assert vm.viewerMode == "original"
    assert vm.viewerImageUrl == original.as_uri()

    vm.setViewerMode("compare")
    assert vm.viewerMode == "compare"
    assert vm.viewerImageUrlFor("translated") == ""  # no artifact in slice

    try:
        vm.setViewerMode("bogus")
    except ValueError:
        pass
    else:
        raise AssertionError("unknown mode must raise")


# ----------------------------------------------------------------------
# T1.1.2: page extent and region geometry reach the view
# ----------------------------------------------------------------------


def test_page_pixel_extent_is_exposed_for_the_overlay(qapp_):
    # The QML overlay must scale with the SAME constants the converter uses,
    # otherwise a box can be drawn at A while the click resolves at B.
    service, _ = make_pipeline(pages=[("p1", 1)])
    vm = make_vm(
        service,
        pages=[FakePage("p1", "chapter-1", 1, "001.jpg", width=800, height=1200)],
    )
    vm.setContext("book-1", "chapter-1", "测试书", "第1话")
    vm.selectPage("p1")
    assert vm.viewerPageWidth == 800
    assert vm.viewerPageHeight == 1200


def test_page_extent_defaults_to_zero_without_dimensions(qapp_):
    service, _ = make_pipeline(pages=[("p1", 1)])
    vm = make_vm(service, pages=[FakePage("p1", "chapter-1", 1, "001.jpg")])
    vm.setContext("book-1", "chapter-1", "测试书", "第1话")
    vm.selectPage("p1")
    assert (vm.viewerPageWidth, vm.viewerPageHeight) == (0, 0)


def test_no_current_page_reports_zero_extent(qapp_):
    _, vm = completed_vm()
    assert vm.viewerPageWidth == 0
    assert vm.viewerPageHeight == 0


def test_inspector_rows_carry_geometry_for_the_overlay(qapp_):
    service, _ = make_pipeline(pages=[("p1", 1)])
    region = FakeRegion("r1", "p1")
    region.geometry = RegionGeometry(bbox=BBox(100, 200, 400, 600))
    vm = make_vm(
        service,
        pages=[FakePage("p1", "chapter-1", 1, "001.jpg", width=800, height=1200)],
        regions=[region],
    )
    vm.setContext("book-1", "chapter-1", "测试书", "第1话")
    vm.selectPage("p1")
    rows = vm.get_inspector_regions()
    assert rows[0]["geometry"] == {"bbox": [100, 200, 400, 600], "polygon": []}


def test_inspector_row_geometry_is_none_when_the_region_has_none(qapp_):
    # A catalog double (or a legacy row) without geometry must read as absent
    # so the overlay skips it, not as a box collapsed onto the origin.
    service, _ = make_pipeline(pages=[("p1", 1)])
    vm = make_vm(service, pages=[FakePage("p1", "chapter-1", 1, "001.jpg",
                                          width=800, height=1200)],
                 regions=[FakeRegion("r1", "p1")])
    vm.setContext("book-1", "chapter-1", "测试书", "第1话")
    vm.selectPage("p1")
    assert vm.get_inspector_regions()[0]["geometry"] is None


# ----------------------------------------------------------------------
# T1.1.2: rectangle creation
# ----------------------------------------------------------------------


def region_vm(editor=None, creator=None, deleter=None):
    service, _ = make_pipeline(pages=[("p1", 1)])
    vm = make_vm(
        service,
        pages=[FakePage("p1", "chapter-1", 1, "001.jpg", width=800, height=1200)],
        creator=creator,
        deleter=deleter,
        editor=editor,
    )
    vm.setContext("book-1", "chapter-1", "测试书", "第1话")
    vm.selectPage("p1")
    return vm


def test_create_rectangle_writes_page_pixels(qapp_):
    writer = FakeRegionWriter()
    vm = region_vm(creator=writer)
    vm.createRectangle(0.125, 0.16666666666666666, 0.625, 0.6666666666666666)
    assert writer.created == [
        ("p1", RegionGeometry(bbox=BBox(100, 200, 400, 600),
                              polygon=((100, 200), (500, 200),
                                       (500, 800), (100, 800))))
    ]


def test_create_rectangle_selects_the_new_region(qapp_):
    vm = region_vm(creator=FakeRegionWriter())
    vm.createRectangle(0.1, 0.1, 0.5, 0.5)
    assert vm.inspectorRegionId == "r-created-1"


def test_degenerate_drag_never_reaches_the_writer(qapp_):
    # Discriminating: proves validation runs BEFORE any write. Dropping the
    # RegionCanvasError handling would let BBox's ValueError escape.
    writer = FakeRegionWriter()
    vm = region_vm(creator=writer)
    errors = []
    vm.commandError.connect(errors.append)
    vm.createRectangle(0.3, 0.1, 0.3, 0.8)
    assert writer.created == []
    assert len(errors) == 1
    assert "no area" in errors[0]


def test_missing_page_extent_is_a_typed_error(qapp_):
    # A page row without dimensions must fail loudly, not silently collapse
    # the box onto the origin: the writer is never reached.
    writer = FakeRegionWriter()
    service, _ = make_pipeline(pages=[("p1", 1)])
    vm = make_vm(
        service,
        pages=[FakePage("p1", "chapter-1", 1, "001.jpg")],
        creator=writer,
    )
    vm.setContext("book-1", "chapter-1", "测试书", "第1话")
    vm.selectPage("p1")
    errors = []
    vm.commandError.connect(errors.append)
    vm.createRectangle(0.1, 0.1, 0.5, 0.5)
    assert writer.created == []
    assert len(errors) == 1
    assert "no usable pixel extent" in errors[0]
    # the machine-readable code rides on the typed error surface
    assert "PAGE_SIZE_UNAVAILABLE" in vm.commandErrorText
    assert vm.inspectorRegionId == ""


def test_unbound_creator_is_typed_and_does_not_raise(qapp_):
    vm = region_vm()
    errors = []
    vm.commandError.connect(errors.append)
    vm.createRectangle(0.1, 0.1, 0.5, 0.5)   # must not raise into QML
    assert errors == ["no region creator bound"]


def test_no_page_selected_is_typed(qapp_):
    service, _ = make_pipeline(pages=[("p1", 1)])
    vm = make_vm(service, pages=[], creator=FakeRegionWriter())
    vm.setContext("book-1", "chapter-1", "测试书", "第1话")
    errors = []
    vm.commandError.connect(errors.append)
    vm.createRectangle(0.1, 0.1, 0.5, 0.5)
    assert errors == ["no page selected"]


def test_dirty_editor_is_not_discarded_by_a_new_region(qapp_):
    # _navigate would open the save/discard dialog; bypassing it blindly would
    # throw away typed text. So with a dirty inspector the list refreshes but
    # the selection is left alone.
    writer = FakeRegionWriter()
    vm = region_vm(creator=writer)
    vm.selectRegion("r1")
    vm.setInspectorText("未保存的台词")
    assert vm.hasDirtyEditor is True
    vm.createRectangle(0.1, 0.1, 0.5, 0.5)
    assert writer.created and vm.inspectorRegionId == "r1"


def test_clean_editor_refreshes_the_region_list(qapp_):
    # The other branch: with nothing at risk the new region becomes selected,
    # so the Inspector shows it without a reload.
    emitted = []
    vm = region_vm(creator=FakeRegionWriter())
    vm.inspectorChanged.connect(lambda: emitted.append(1))
    vm.createRectangle(0.1, 0.1, 0.5, 0.5)
    assert vm.inspectorRegionId == "r-created-1"
    assert emitted


