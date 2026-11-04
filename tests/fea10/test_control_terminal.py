"""FEA-10 AC6 (DSH ADJ 2026-11-04 §2.4): control-request persistence vs state
change, UI-not-before-Core status, terminal-state invariants and same-source
readback across a Core restart — all on the existing RunMonitor/RunStateStore
projection (no second source of truth)."""
from __future__ import annotations

from pathlib import Path

from tests.core.test_fea00a_pipeline_seam import _new_workspace
from tests.fea10.test_prepared_run import workspace

from domain.tasks.models import (
    PipelineRunStatus,
    PipelineScope,
    PipelineTaskStatus,
    ScopeType,
)


def _projection(core, run_id):
    from application.tasks.projection import build_projection

    return build_projection(core.pipeline.get_run_snapshot(run_id, fresh=True))


def _plan_and_mark_running(core, region):
    pipeline = core.pipeline
    run = pipeline.create_run(
        'ocr_region', PipelineScope(ScopeType.REGION, selected_ids=(region,))
    )
    pipeline.plan_run(run.run_id)
    run.status = PipelineRunStatus.RUNNING
    pipeline._persist(run)
    return run


def _db_root(core) -> Path:
    return Path(core.conn.execute('PRAGMA database_list').fetchall()[0][2]).parent


def test_pause_request_persists_without_status_change_and_ui_waits_for_core():
    core, _, region = _new_workspace(workspace('control-pause-pending'))
    try:
        run = _plan_and_mark_running(core, region)
        result = core.pipeline.control_run(run.run_id, 'pause')
        # The request is durable, but it is NOT a status change.
        assert result.status is PipelineRunStatus.RUNNING
        fresh = core.pipeline.get_run_snapshot(run.run_id, fresh=True)
        assert fresh.status is PipelineRunStatus.RUNNING
        assert fresh.pause_requested is True
        # UI projection is fed by the Core-persisted status only: still running.
        assert _projection(core, run.run_id).run_status == 'running'
        # The scheduler honours the request at the next unit boundary.
        core.pipeline._resumed_runs.add(run.run_id)
        core.pipeline.execute_run(run.run_id)
        fresh = core.pipeline.get_run_snapshot(run.run_id, fresh=True)
        assert fresh.status is PipelineRunStatus.PAUSED
        assert _projection(core, run.run_id).run_status == 'paused'
    finally:
        core.conn.close()


def test_stop_request_on_running_run_stays_pending_until_scheduler():
    core, _, region = _new_workspace(workspace('control-stop-pending'))
    try:
        run = _plan_and_mark_running(core, region)
        result = core.pipeline.control_run(run.run_id, 'stop')
        assert result.status is PipelineRunStatus.RUNNING
        fresh = core.pipeline.get_run_snapshot(run.run_id, fresh=True)
        assert fresh.status is PipelineRunStatus.RUNNING
        assert fresh.cancel_requested is True
        assert _projection(core, run.run_id).run_status == 'running'
        core.pipeline._resumed_runs.add(run.run_id)
        core.pipeline.execute_run(run.run_id)
        fresh = core.pipeline.get_run_snapshot(run.run_id, fresh=True)
        assert fresh.status is PipelineRunStatus.CANCELLED
        assert _projection(core, run.run_id).run_status == 'cancelled'
    finally:
        core.conn.close()


def _terminal_invariants(projection, *, failed=0, blocked=0):
    assert projection.processing_page_count == 0
    assert projection.waiting_page_count == 0
    assert projection.failed_page_count == failed
    assert projection.blocked_page_count == blocked
    return projection


def test_terminal_states_share_invariants_with_per_state_predicates():
    core, page, region = _new_workspace(workspace('terminal-invariants'))
    try:
        pipeline = core.pipeline
        # completed: a fully successful run.
        done = _plan_and_mark_running(core, region)
        pipeline._resumed_runs.add(done.run_id)
        pipeline.execute_run(done.run_id)
        assert done.status is PipelineRunStatus.COMPLETED
        projection = _terminal_invariants(_projection(core, done.run_id), failed=0, blocked=0)
        assert projection.is_terminal is True

        # completed_with_failures: at least one failed page, nothing blocked/waiting.
        parent = pipeline.create_run(
            'reocr_single', PipelineScope(ScopeType.PAGE, selected_ids=(page,))
        )
        pipeline.plan_run(parent.run_id)
        parent.status = PipelineRunStatus.COMPLETED_WITH_FAILURES
        parent.tasks[0].status = PipelineTaskStatus.FAILED
        parent.tasks[0].error_code = 'PROVIDER_FAILED'
        pipeline._persist(parent)
        projection = _terminal_invariants(_projection(core, parent.run_id), failed=1, blocked=0)
        assert projection.is_terminal is True

        # cancelled: stop before any work; pending pages fold to skipped.
        pending = pipeline.create_run(
            'reocr_single', PipelineScope(ScopeType.PAGE, selected_ids=(page,))
        )
        pipeline.plan_run(pending.run_id)
        result = pipeline.control_run(pending.run_id, 'stop')
        assert result.status is PipelineRunStatus.CANCELLED
        projection = _terminal_invariants(_projection(core, pending.run_id), failed=0, blocked=0)
        assert projection.is_terminal is True

        # failed: failure page present under the failed run status.
        parent.status = PipelineRunStatus.FAILED
        pipeline._persist(parent)
        projection = _terminal_invariants(_projection(core, parent.run_id), failed=1, blocked=0)
        assert projection.is_terminal is True

        # Illegal projection (a claimed terminal run with a waiting page) must
        # not pass as terminal: the invariant is the guard, not the label.
        parent.tasks[0].status = PipelineTaskStatus.PENDING
        parent.status = PipelineRunStatus.COMPLETED
        pipeline._persist(parent)
        projection = _projection(core, parent.run_id)
        assert projection.waiting_page_count == 1
        assert projection.is_terminal is False
    finally:
        core.conn.close()


def test_control_and_terminal_state_survive_core_restart_same_source():
    core, _, region = _new_workspace(workspace('control-restart-readback'))
    run = _plan_and_mark_running(core, region)
    core.pipeline.control_run(run.run_id, 'pause')
    core.pipeline._resumed_runs.add(run.run_id)
    core.pipeline.execute_run(run.run_id)
    assert core.pipeline.get_run_snapshot(run.run_id, fresh=True).status is PipelineRunStatus.PAUSED
    db_root = _db_root(core)
    core.conn.close()
    # Reopen the same DataRoot/DB with a fresh Core (process-restart analogue).
    from tests.core.test_fea00a_pipeline_seam import _assemble
    reopened = _assemble(db_root)
    try:
        fresh = reopened.pipeline.get_run_snapshot(run.run_id, fresh=True)
        assert fresh.status is PipelineRunStatus.PAUSED
        # The honoured request bit stays durable; only `continue` clears it.
        assert fresh.pause_requested is True
        assert _projection(reopened, run.run_id).run_status == 'paused'
    finally:
        reopened.conn.close()
