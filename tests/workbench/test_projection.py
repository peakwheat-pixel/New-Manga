"""TaskProjection unit vectors (TASK-013, D06 §74~79/§102~103).

The projection is the single source PageList and TaskProgressPanel both
read (AC-PROGRESS-007); these tests pin the classification precedence
against the scheduler's own ``get_task_progress`` so the two can never
drift.
"""

from __future__ import annotations

import workbench_helpers  # noqa: F401  (sys.path injection)
from workbench_helpers import fail_first_region_step, make_pipeline
import pytest

from application.translation.pipeline.executor import DeterministicStepExecutor
from domain.tasks.models import (
    PipelineRunStatus,
    PipelineScope,
    PipelineTaskStatus,
    ScopeType,
    StepRun,
    StepRunStatus,
)
from application.tasks.projection import (
    STATUS_FAILED,
    STATUS_WAITING,
    _button_enablement,
    build_projection,
)


def run_of(service, catalog_pages=None, command="translate_all", **kwargs):
    run = service.create_run(
        command, PipelineScope(ScopeType.CHAPTER, chapter_id="chapter-1"), **kwargs
    )
    service.plan_run(run.run_id)
    return run


def test_pending_run_all_waiting_and_stop_enabled_only():
    """Pending may be stopped but NOT paused (P11 §4.5).

    The name changed from ``..._pause_stop_enabled`` because that said the
    opposite of the contract. It was written when PENDING and RUNNING shared one
    arm of ``_button_enablement``; P13 split them and P11 §4.5 then froze
    Pending as "scheduler start, stop" with pause explicitly rejected, because a
    run that has not started has nothing to pause at - the useful action is to
    cancel it before it begins.

    The rename is deliberate rather than cosmetic: a test whose name asserts a
    behaviour the contract forbids will keep inviting the old expectation back.
    """
    service, _ = make_pipeline(pages=[("p1", 1), ("p2", 2)])
    run = run_of(service)
    projection = build_projection(run)

    assert projection.run_status == "pending"
    assert projection.total_page_count == 2
    assert projection.waiting_page_count == 2
    assert projection.completed_page_count == 0
    # P11 §4.5: Pending allows scheduler start and stop; pause is in the
    # illegal-transition list.
    assert projection.can_pause is False
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


#: The button matrix exactly as P11 §4.5 freezes it. "仅允许" is the only
#: column that matters here: any action not listed for a state must be rejected,
#: and the projection is what the UI reads.
#:
#: Kept as a table so a future disagreement shows up as one bad row naming its
#: state, instead of a tuple that has to be decoded.
P11_BUTTON_MATRIX = {
    # status: (can_pause, can_stop, can_continue, can_restart, can_abandon)
    PipelineRunStatus.PENDING: (False, True, False, False, False),
    PipelineRunStatus.RUNNING: (True, True, False, False, False),
    PipelineRunStatus.PAUSED: (False, True, True, False, False),
    PipelineRunStatus.BLOCKED: (False, True, False, False, False),
    # Interrupted with no disposition may be continued, restarted or abandoned.
    PipelineRunStatus.INTERRUPTED: (False, False, True, True, True),
    PipelineRunStatus.COMPLETED: (False, False, False, False, False),
    PipelineRunStatus.COMPLETED_WITH_FAILURES: (False, False, False, False, False),
    PipelineRunStatus.FAILED: (False, False, False, False, False),
    PipelineRunStatus.CANCELLED: (False, False, False, False, False),
}


def test_button_matrix_matches_p11_4_5_for_every_status():
    """Every status, not just the two the old version sampled.

    The previous body checked pending and completed and called itself 'all
    statuses'. Pending was wrong, and seven other states were never looked at -
    including RUNNING, which is the one the pause button exists for.
    """
    for status, expected in P11_BUTTON_MATRIX.items():
        enabled = _button_enablement(status, has_failures=False)
        actual = (
            enabled.get("can_pause") is True,
            enabled.get("can_stop") is True,
            enabled.get("can_continue") is True,
            enabled.get("can_restart") is True,
            enabled.get("can_abandon") is True,
        )
        assert actual == expected, (
            "%s: expected (pause, stop, continue, restart, abandon) = %r, got %r "
            "from %r" % (status.name, expected, actual, enabled)
        )


def test_interrupted_with_a_disposition_offers_nothing():
    """P11 §4.5: an Interrupted run that was already disposed of accepts nothing."""
    for disposition in ("restarted", "abandoned"):
        enabled = _button_enablement(
            PipelineRunStatus.INTERRUPTED, has_failures=False,
            interruption_disposition=disposition)
        assert enabled == {}, (
            "disposition %r still offered %r" % (disposition, enabled)
        )


def test_retry_is_offered_only_for_failures_that_exist():
    """completed_with_failures is retryable only when it actually has failures."""
    assert _button_enablement(
        PipelineRunStatus.COMPLETED_WITH_FAILURES, has_failures=False) == {}
    assert _button_enablement(
        PipelineRunStatus.COMPLETED_WITH_FAILURES, has_failures=True
    ) == {"can_retry_failed": True}


def test_button_matrix_all_statuses():
    """The lifecycle through build_projection, end to end."""

    service, _ = make_pipeline(pages=[("p1", 1)])

    run = run_of(service)
    projection = build_projection(run)
    # P11 §4.5: pending stops, cannot pause.
    assert (projection.can_pause, projection.can_stop, projection.can_continue) == (
        False, True, False,
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


def test_backward_compatibility_reexports():
    """Verify legacy ui.models.tasks.projection acts as a seamless shim (M2-I2).

    Note: ui.models.tasks package __init__ imports page_list_model (PySide6),
    so importing via module name requires PySide6 in legacy UI tree.
    """
    try:
        import PySide6  # noqa: F401
    except ImportError:
        pytest.skip("PySide6 not installed; legacy UI package __init__ requires Qt")

    import application.tasks.projection as app_proj
    import ui.models.tasks.projection as ui_proj

    assert ui_proj.build_projection is app_proj.build_projection
    assert ui_proj.TaskProjection is app_proj.TaskProjection
    assert ui_proj.PageProjectionRow is app_proj.PageProjectionRow
    assert ui_proj.command_label is app_proj.command_label
    assert ui_proj.run_title is app_proj.run_title
    assert ui_proj.step_label is app_proj.step_label
    assert ui_proj.STATUS_WAITING is app_proj.STATUS_WAITING
    assert ui_proj.STATUS_FAILED is app_proj.STATUS_FAILED
