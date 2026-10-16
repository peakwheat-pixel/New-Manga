"""P13 AC4 characterization tests; expected to fail on the unmodified base."""

from __future__ import annotations

from pathlib import Path
import sys
from threading import Event, Thread

import pytest

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from application.tasks.service import PipelineService
from application.tasks.store import (
    InMemoryPipelineStore,
    InMemorySnapshotProvider,
    InMemoryTargetCatalog,
)
from application.translation.pipeline.executor import DeterministicStepExecutor
from domain.tasks.models import (
    CommandType,
    LockSnapshot,
    PipelineError,
    PipelineRun,
    PipelineRunStatus,
    PipelineScope,
    PipelineTaskStatus,
    RegionSnapshot,
    ScopeType,
)


def _pipeline(*, store=None, executor=None, provider_bindings=None):
    catalog = InMemoryTargetCatalog()
    catalog.add_page(
        "page-1",
        book_id="book-1",
        chapter_id="chapter-1",
        regions=(RegionSnapshot("region-1", "page-1"),),
    )
    store = store or InMemoryPipelineStore()
    pipeline = PipelineService(
        catalog,
        store=store,
        snapshots=InMemorySnapshotProvider(
            provider_bindings=provider_bindings or {}
        ),
        executor=executor,
    )
    return pipeline, store


def _new_run(pipeline):
    return pipeline.create_run(
        CommandType.TRANSLATE_ALL,
        PipelineScope(ScopeType.CHAPTER, chapter_id="chapter-1"),
    )


def test_pending_pause_is_rejected_without_mutation():
    pipeline, store = _pipeline()
    run = _new_run(pipeline)

    with pytest.raises(PipelineError) as error:
        pipeline.control_run(run.run_id, "pause")

    assert error.value.code == "INVALID_RUN_TRANSITION"
    persisted = store.get(run.run_id)
    assert persisted.status is PipelineRunStatus.PENDING
    assert persisted.pause_requested is False


def test_blocked_stop_reaches_cancelled_terminal_state():
    pipeline, store = _pipeline(provider_bindings={"ocr": {"available": False}})
    run = pipeline.plan_run(_new_run(pipeline).run_id)
    assert run.status is PipelineRunStatus.BLOCKED

    result = pipeline.control_run(run.run_id, "stop")

    assert result.status is PipelineRunStatus.CANCELLED
    assert store.get(run.run_id).status is PipelineRunStatus.CANCELLED
    assert all(task.status is PipelineTaskStatus.CANCELLED for task in run.tasks)


class _FailParentAfterChildStore(InMemoryPipelineStore):
    def put(self, run_id: str, run: PipelineRun) -> None:
        if run.interruption_disposition == "restarted":
            raise OSError("injected parent persistence failure")
        super().put(run_id, run)

    def put_many(self, runs) -> None:
        # The atomic store operation must leave both rows untouched on failure.
        raise OSError("injected atomic acceptance failure")


def test_restart_failure_does_not_leave_child_without_parent_disposition():
    store = _FailParentAfterChildStore()
    pipeline, _ = _pipeline(store=store)
    parent = _new_run(pipeline)
    parent.status = PipelineRunStatus.INTERRUPTED
    store.put(parent.run_id, parent)

    with pytest.raises(OSError):
        pipeline.control_run(parent.run_id, "restart")

    assert store.list_ids() == (parent.run_id,)
    persisted = store.get(parent.run_id)
    assert persisted.status is PipelineRunStatus.INTERRUPTED
    assert persisted.interruption_disposition is None


def test_retry_failed_targets_requires_completed_with_failures():
    pipeline, store = _pipeline()
    run = pipeline.plan_run(_new_run(pipeline).run_id)
    run.tasks[0].status = PipelineTaskStatus.FAILED
    run.status = PipelineRunStatus.FAILED
    store.put(run.run_id, run)
    original_ids = store.list_ids()

    with pytest.raises(PipelineError) as error:
        pipeline.retry_failed_targets(run.run_id)

    assert error.value.code == "INVALID_RUN_TRANSITION"
    assert store.list_ids() == original_ids


@pytest.mark.parametrize(
    "status",
    [
        PipelineRunStatus.PENDING,
        PipelineRunStatus.RUNNING,
        PipelineRunStatus.PAUSED,
        PipelineRunStatus.BLOCKED,
        PipelineRunStatus.INTERRUPTED,
        PipelineRunStatus.COMPLETED,
        PipelineRunStatus.FAILED,
        PipelineRunStatus.CANCELLED,
    ],
)
def test_retry_failed_targets_rejects_every_status_except_completed_with_failures(status):
    pipeline, store = _pipeline()
    run = _new_run(pipeline)
    run.status = status
    run.tasks = []
    store.put(run.run_id, run)

    with pytest.raises(PipelineError) as error:
        pipeline.retry_failed_targets(run.run_id)

    assert error.value.code == "INVALID_RUN_TRANSITION"
    assert store.list_ids() == (run.run_id,)
    assert store.get(run.run_id).status is status


def test_scheduler_start_rejects_every_non_pending_status():
    for status in (
        PipelineRunStatus.RUNNING,
        PipelineRunStatus.PAUSED,
        PipelineRunStatus.BLOCKED,
        PipelineRunStatus.INTERRUPTED,
        PipelineRunStatus.COMPLETED,
        PipelineRunStatus.COMPLETED_WITH_FAILURES,
        PipelineRunStatus.FAILED,
        PipelineRunStatus.CANCELLED,
    ):
        pipeline, store = _pipeline()
        run = _new_run(pipeline)
        run.status = status
        store.put(run.run_id, run)

        with pytest.raises(PipelineError) as error:
            pipeline.execute_run(run.run_id)

        assert error.value.code == "INVALID_RUN_TRANSITION"
        assert store.get(run.run_id).status is status


def test_scheduler_start_on_preplanned_all_skipped_run_is_a_terminal_noop():
    catalog = InMemoryTargetCatalog()
    catalog.add_page(
        "page-1",
        book_id="book-1",
        chapter_id="chapter-1",
        lock=LockSnapshot(page_locked=True),
        regions=(RegionSnapshot("region-1", "page-1"),),
    )
    pipeline = PipelineService(catalog)
    run = pipeline.create_run(
        CommandType.OCR_REGION,
        PipelineScope(ScopeType.REGION, selected_ids=("region-1",)),
    )
    run = pipeline.plan_run(run.run_id)
    assert run.status is PipelineRunStatus.COMPLETED
    assert run.tasks[0].status is PipelineTaskStatus.SKIPPED

    finished = pipeline.execute_run(run.run_id)

    assert finished is run
    assert run.status is PipelineRunStatus.COMPLETED


@pytest.mark.parametrize(
    ("status", "disposition", "action"),
    [
        (PipelineRunStatus.PENDING, None, "continue"),
        (PipelineRunStatus.PENDING, None, "restart"),
        (PipelineRunStatus.PENDING, None, "abandon"),
        (PipelineRunStatus.RUNNING, None, "continue"),
        (PipelineRunStatus.RUNNING, None, "restart"),
        (PipelineRunStatus.RUNNING, None, "abandon"),
        (PipelineRunStatus.PAUSED, None, "pause"),
        (PipelineRunStatus.PAUSED, None, "restart"),
        (PipelineRunStatus.PAUSED, None, "abandon"),
        (PipelineRunStatus.BLOCKED, None, "pause"),
        (PipelineRunStatus.BLOCKED, None, "continue"),
        (PipelineRunStatus.BLOCKED, None, "restart"),
        (PipelineRunStatus.BLOCKED, None, "abandon"),
        (PipelineRunStatus.INTERRUPTED, None, "pause"),
        (PipelineRunStatus.INTERRUPTED, None, "stop"),
        (PipelineRunStatus.INTERRUPTED, "restarted", "continue"),
        (PipelineRunStatus.INTERRUPTED, "restarted", "restart"),
        (PipelineRunStatus.INTERRUPTED, "restarted", "abandon"),
        *[
            (status, None, action)
            for status in (
                PipelineRunStatus.COMPLETED,
                PipelineRunStatus.COMPLETED_WITH_FAILURES,
                PipelineRunStatus.FAILED,
                PipelineRunStatus.CANCELLED,
            )
            for action in ("pause", "continue", "stop", "restart", "abandon")
        ],
    ],
)
def test_illegal_control_matrix_rejects_without_side_effects(status, disposition, action):
    pipeline, store = _pipeline()
    run = _new_run(pipeline)
    run.status = status
    run.interruption_disposition = disposition
    store.put(run.run_id, run)
    before_ids = store.list_ids()
    before_flags = (run.pause_requested, run.cancel_requested, run.termination_reason)

    with pytest.raises(PipelineError) as error:
        pipeline.control_run(run.run_id, action)

    assert error.value.code == "INVALID_RUN_TRANSITION"
    assert store.list_ids() == before_ids
    persisted = store.get(run.run_id)
    assert persisted.status is status
    assert (persisted.pause_requested, persisted.cancel_requested, persisted.termination_reason) == before_flags


@pytest.mark.parametrize(
    "status",
    [
        PipelineRunStatus.PENDING,
        PipelineRunStatus.RUNNING,
        PipelineRunStatus.PAUSED,
        PipelineRunStatus.INTERRUPTED,
        PipelineRunStatus.COMPLETED,
        PipelineRunStatus.COMPLETED_WITH_FAILURES,
        PipelineRunStatus.FAILED,
        PipelineRunStatus.CANCELLED,
    ],
)
def test_resume_blocked_rejects_non_blocked_run_without_mutation(status):
    pipeline, store = _pipeline()
    run = _new_run(pipeline)
    run.status = status
    store.put(run.run_id, run)

    with pytest.raises(PipelineError) as error:
        pipeline.resume_blocked_run(run.run_id)

    assert error.value.code == "INVALID_RUN_TRANSITION"
    assert store.get(run.run_id).status is status


def test_blocked_run_replans_only_after_resume_blocked_operation():
    pipeline, store = _pipeline(provider_bindings={"ocr": {"available": False}})
    run = pipeline.plan_run(_new_run(pipeline).run_id)
    assert run.status is PipelineRunStatus.BLOCKED

    pipeline.resume_blocked_run(run.run_id)

    assert store.get(run.run_id).status is PipelineRunStatus.BLOCKED


def test_abandon_interruptions_cancels_only_the_original_run():
    pipeline, store = _pipeline()
    run = _new_run(pipeline)
    run.status = PipelineRunStatus.INTERRUPTED
    store.put(run.run_id, run)

    result = pipeline.control_run(run.run_id, "abandon")

    assert result.run_id == run.run_id
    assert result.new_run_id is None
    assert result.status is PipelineRunStatus.CANCELLED
    assert store.list_ids() == (run.run_id,)
    assert store.get(run.run_id).termination_reason == "abandoned_after_interruption"


def test_pipeline_service_rejects_a_second_scheduler_owner():
    pipeline, _ = _pipeline()
    run = _new_run(pipeline)
    entered = Event()
    release = Event()
    result = []
    original = pipeline._execute_run_owned

    def hold_owner(run_id):
        entered.set()
        assert release.wait(timeout=2)
        return original(run_id)

    pipeline._execute_run_owned = hold_owner
    worker = Thread(target=lambda: result.append(pipeline.execute_run(run.run_id)))
    worker.start()
    try:
        assert entered.wait(timeout=2)
        with pytest.raises(PipelineError) as error:
            pipeline.execute_run(run.run_id)
        assert error.value.code == "INVALID_RUN_TRANSITION"
    finally:
        release.set()
        worker.join(timeout=2)
        pipeline._execute_run_owned = original
    assert not worker.is_alive()
    assert result and result[0].status is PipelineRunStatus.COMPLETED
