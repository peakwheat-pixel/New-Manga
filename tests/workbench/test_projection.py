"""TaskProjection unit vectors (TASK-013, D06 §74~79/§102~103).

The projection is the single source PageList and TaskProgressPanel both
read (AC-PROGRESS-007); these tests pin the classification precedence
against the scheduler's own ``get_task_progress`` so the two can never
drift.
"""

from __future__ import annotations

import workbench_helpers  # noqa: F401  (sys.path injection)
from workbench_helpers import fail_first_region_step, make_pipeline

from application.translation.pipeline.executor import DeterministicStepExecutor
from domain.tasks.models import (
    PipelineRunStatus,
    PipelineScope,
    PipelineTaskStatus,
    ScopeType,
    StepRun,
    StepRunStatus,
)
from ui.models.tasks.projection import (
    STATUS_FAILED,
    STATUS_WAITING,
    build_projection,
)


def run_of(service, catalog_pages=None, command="translate_all", **kwargs):
    run = service.create_run(
        command, PipelineScope(ScopeType.CHAPTER, chapter_id="chapter-1"), **kwargs
    )
    service.plan_run(run.run_id)
    return run


def test_pending_run_all_waiting_and_pause_stop_enabled():
    service, _ = make_pipeline(pages=[("p1", 1), ("p2", 2)])
    run = run_of(service)
    projection = build_projection(run)

    assert projection.run_status == "pending"
    assert projection.total_page_count == 2
    assert projection.waiting_page_count == 2
    assert projection.completed_page_count == 0
    # D06 §103 Running/Pending: pause + stop, no continue.
    assert projection.can_pause is True
    assert projection.can_stop is True
    assert projection.can_continue is False
    # D06 §75: nothing terminal yet.
    assert projection.overall_progress == 0.0
    assert projection.progress_percent == 0


def test_counts_match_scheduler_projection():
    """D06 §79/AC-PROGRESS-007: same run, same numbers, one projection."""

    service, _ = make_pipeline(pages=[("p1", 1), ("p2", 2)])
    run = run_of(service)
    service.execute_run(run.run_id)
    projection = build_projection(run)
    official = service.get_task_progress(run.run_id)

    assert projection.completed_page_count == official.completed_page_count
    assert projection.failed_page_count == official.failed_page_count
    assert projection.skipped_page_count == official.skipped_page_count
    assert projection.blocked_page_count == official.blocked_page_count
    assert projection.waiting_page_count == official.waiting_page_count
    assert projection.processing_page_count == official.processing_page_count
    assert projection.total_page_count == official.total_page_count


def test_completed_run_counts_and_progress():
    service, _ = make_pipeline(pages=[("p1", 1), ("p2", 2)])
    run = run_of(service)
    service.execute_run(run.run_id)

    projection = build_projection(run)
    assert projection.run_status == "completed"
    assert projection.completed_page_count == 2
    assert projection.overall_progress == 1.0
    assert projection.progress_percent == 100
    assert projection.can_pause is False
    assert projection.can_stop is False
    assert projection.can_continue is False


def test_completed_with_failures_is_not_total_failure():
    """AC-PROGRESS-006: 38 success + 2 failure → completed（有失败）, with
    retry-failed available; the 38 good pages are not a failed run."""

    executor = DeterministicStepExecutor(
        fail_on=fail_first_region_step(("p39", "p40"))
    )
    service, _ = make_pipeline(
        pages=[(f"p{i}", i) for i in range(1, 41)], executor=executor
    )
    run = run_of(service)
    service.execute_run(run.run_id)

    projection = build_projection(run)
    assert projection.run_status == "completed_with_failures"
    assert projection.completed_page_count == 38
    assert projection.failed_page_count == 2
    assert projection.can_retry_failed is True
    assert projection.can_stop is False
    # failed > everything: the two failing pages are "failed", not waiting
    failed_rows = [row for row in projection.rows if row.status == STATUS_FAILED]
    assert [row.page_id for row in failed_rows] == ["p39", "p40"]


def test_button_matrix_all_statuses():
    """D06 §103 / D05 §32 across the run lifecycle."""

    service, _ = make_pipeline(pages=[("p1", 1)])

    run = run_of(service)
    projection = build_projection(run)
    assert (projection.can_pause, projection.can_stop, projection.can_continue) == (
        True, True, False,
    )

    service.execute_run(run.run_id)  # 1 page completes immediately
    projection = build_projection(run)
    assert projection.run_status == "completed"
    assert (projection.can_pause, projection.can_stop, projection.can_continue) == (
        False, False, False,
    )


def test_paused_buttons():
    service, _ = make_pipeline(
        pages=[(f"p{i}", i) for i in range(1, 5)],
        executor=DeterministicStepExecutor(on_execute=lambda *a: None),
    )
    run = run_of(service)
    run.status = PipelineRunStatus.RUNNING
    run.pause_requested = True
    # simulate the executor returning early on the pause boundary
    run.status = PipelineRunStatus.PAUSED
    projection = build_projection(run)
    assert projection.can_pause is False
    assert projection.can_stop is True
    assert projection.can_continue is True


def test_blocked_run_reasons_and_buttons():
    service, _ = make_pipeline(pages=[("p1", 1)])
    run = run_of(service)
    task = run.tasks[0]
    task.status = PipelineTaskStatus.BLOCKED
    task.error_code = "MISSING_REQUIRED_INPUT"
    run.status = PipelineRunStatus.BLOCKED

    projection = build_projection(run)
    assert projection.run_status == "blocked"
    assert projection.blocked_page_count == 1
    assert projection.blocked_reasons == ("MISSING_REQUIRED_INPUT",)
    # D05 §32 Blocked: stop enabled, pause/continue disabled.
    assert projection.can_stop is True
    assert projection.can_pause is False
    assert projection.can_continue is False


def test_interrupted_buttons():
    service, _ = make_pipeline(pages=[("p1", 1)])
    run = run_of(service)
    run.status = PipelineRunStatus.INTERRUPTED

    projection = build_projection(run)
    assert projection.can_continue is True
    assert projection.can_restart is True
    assert projection.can_abandon is True
    assert projection.can_pause is False
    assert projection.can_stop is False


def test_cancelled_buttons():
    service, _ = make_pipeline(pages=[("p1", 1)])
    run = run_of(service)
    run.status = PipelineRunStatus.CANCELLED

    projection = build_projection(run)
    assert all(
        not getattr(projection, flag)
        for flag in ("can_pause", "can_stop", "can_continue")
    )


def test_locked_overlay_does_not_change_run_status():
    """AC-PAGE-003: 已锁定 is a tile overlay on top of the run status."""

    service, _ = make_pipeline(pages=[("p1", 1), ("p2", 2)])
    run = run_of(service)
    projection = build_projection(
        run,
        page_meta={"p1": (1, "001.jpg", True), "p2": (2, "002.jpg", False)},
    )
    p1 = next(row for row in projection.rows if row.page_id == "p1")
    p2 = next(row for row in projection.rows if row.page_id == "p2")
    assert p1.is_locked is True and p1.status == STATUS_WAITING
    assert p2.is_locked is False


def test_primary_focus_and_step_flow():
    """D06 §77/§78: focus = first running task; flow strip per step."""

    service, _ = make_pipeline(pages=[("p1", 1), ("p2", 2)])
    run = run_of(service)
    run.status = PipelineRunStatus.RUNNING
    run.tasks[0].status = PipelineTaskStatus.RUNNING
    run.tasks[1].status = PipelineTaskStatus.PENDING
    step = StepRun(
        step_run_id="s1", task_id=run.tasks[0].task_id, target_id="p1",
        page_id="p1", region_id=None, step_type="ocr",
        status=StepRunStatus.RUNNING,
    )
    run.step_runs.append(step)

    projection = build_projection(run)
    assert projection.current_page_id == "p1"
    assert projection.current_step_type == "ocr"
    flow = dict((step_type, state) for step_type, _label, state in projection.step_flow)
    assert flow["ocr"] == "running"
    assert flow["render"] == "pending"
    labels = dict((step_type, label) for step_type, label, _state in projection.step_flow)
    assert labels["ocr"] == "OCR"


def test_run_title_uses_command_label():
    service, _ = make_pipeline(pages=[("p1", 1)])
    run = run_of(service, command="translate_untranslated")
    projection = build_projection(run)
    assert projection.run_title == "全部翻译（跳过已翻译）"
