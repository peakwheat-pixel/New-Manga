"""C2/C3 two-layer coverage ② — pipeline candidate persistence after a
human retype (M2-REGION-RETYPE-CORE, contract M2-C1 rev 1.4 §5.4).

The service-guard layer (the ``GuardStatus`` return of
``apply_machine_translation``) is covered in
``tests/editing/test_region_retype.py``. This file pins the OTHER layer the
T5a review required (P3-6): when a machine write loses the race against a
human retype — the region revision moved forward, or the human locked the
region mid-flight — the pipeline persists the machine payload as a
``StepResultCandidate`` (application/tasks/service.py commit_step_result)
and never overwrites the retyped region. The candidate is kept for review;
nothing is auto-retried over the user's decision.
"""

from __future__ import annotations

import sys
from pathlib import Path

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
from domain.regions.entities import SfxPolicy
from domain.tasks.models import (
    CommandType,
    LockSnapshot,
    PipelineRunStatus,
    PipelineScope,
    RegionSnapshot,
    ScopeType,
    StageState,
)


# ---------------------------------------------------------------------------
# local helpers (the same production-shaped fixtures test_pipeline.py uses)
# ---------------------------------------------------------------------------


def region(
    region_id: str,
    page_id: str,
    *,
    stages: dict[str, str] | None = None,
    revisions: dict[str, str | None] | None = None,
    lock: LockSnapshot | None = None,
    region_type: str = "speech",
    sfx_policy: str = SfxPolicy.SKIP.value,
) -> RegionSnapshot:
    return RegionSnapshot(
        region_id,
        page_id,
        region_type=region_type,
        sfx_policy=sfx_policy,
        lock=lock or LockSnapshot(),
        current_revisions=revisions or {"region": f"{region_id}-rev-1"},
        stage_states=stages or {},
    )


def catalog_with_pages() -> InMemoryTargetCatalog:
    catalog = InMemoryTargetCatalog()
    catalog.add_page(
        "p1",
        book_id="book-1",
        chapter_id="chapter-1",
        page_order=1,
        regions=(
            region("r1", "p1", stages={"ocr": "completed", "clean": "completed"}),
            region("r2", "p1"),
        ),
    )
    return catalog


def service(executor=None):
    catalog = catalog_with_pages()
    store = InMemoryPipelineStore()
    snapshots = InMemorySnapshotProvider(
        settings={"model": "test", "temperature": 0},
        provider_bindings={},
        constraint_snapshot_ref="constraint-1",
        context_policy={"window": "current"},
    )
    pipeline = PipelineService(catalog, store=store, snapshots=snapshots, executor=executor)
    return pipeline, catalog, store


def create_and_plan(
    pipeline: PipelineService,
    command: str,
    *,
    scope: PipelineScope | None = None,
):
    run = pipeline.create_run(
        command,
        scope or PipelineScope(ScopeType.REGION, selected_ids=("r1",)),
    )
    pipeline.plan_run(run.run_id)
    return run


# ---------------------------------------------------------------------------
# C2 ② — the retype moved the region revision under the machine write:
# fail-closed, payload persisted as a candidate, current NOT overwritten.
# ---------------------------------------------------------------------------


def test_retype_revision_move_persists_input_revision_changed_candidate() -> None:
    def retype_lands_during_execution(step_run, unit, run):
        # the human retype commits while the machine step is executing; its
        # pipeline-visible effect is the region revision moving forward
        if unit.step_type == "translate":
            catalog.update_region("r1", current_revisions={"region": "user-retype-rev"})

    executor = DeterministicStepExecutor(on_execute=retype_lands_during_execution)
    pipeline, catalog, _ = service(executor=executor)
    run = create_and_plan(pipeline, "retranslate_region")

    result = pipeline.execute_run(run.run_id)

    assert result.status is PipelineRunStatus.COMPLETED_WITH_FAILURES
    assert len(run.candidates) == 1
    candidate = run.candidates[0]
    assert candidate.reason == "INPUT_REVISION_CHANGED"
    assert candidate.region_id == "r1"
    # the machine payload is PERSISTED for review, not dropped
    assert candidate.payload == {"deterministic": "r1:translate"}
    # fail-closed: the retyped (current) revision was never overwritten
    assert catalog.current("r1").current_revisions["region"] == "user-retype-rev"


# ---------------------------------------------------------------------------
# C3 ② — the human retype+lock appears mid-flight: LOCK_CHANGED candidate,
# and only an explicit rerun after the lock is released consumes the retyped
# decision.
# ---------------------------------------------------------------------------


def test_lock_mid_flight_persists_lock_changed_candidate() -> None:
    def user_locks_during_execution(step_run, unit, run):
        if unit.step_type == "translate":
            catalog.update_region("r1", lock=LockSnapshot(translation_locked=True))

    executor = DeterministicStepExecutor(on_execute=user_locks_during_execution)
    pipeline, catalog, _ = service(executor=executor)
    run = create_and_plan(pipeline, "retranslate_region")

    result = pipeline.execute_run(run.run_id)

    assert result.status is PipelineRunStatus.COMPLETED_WITH_FAILURES
    assert len(run.candidates) == 1
    candidate = run.candidates[0]
    assert candidate.reason == "LOCK_CHANGED"
    assert candidate.payload == {"deterministic": "r1:translate"}
    assert catalog.current("r1").current_revisions["region"] == "r1-rev-1"
    # the machine write did not unlock or otherwise touch the human lock
    assert catalog.current("r1").lock.translation_locked is True


def test_after_lock_release_only_an_explicit_rerun_consumes_the_retype() -> None:
    def user_locks_during_execution(step_run, unit, run):
        if unit.step_type == "translate":
            catalog.update_region("r1", lock=LockSnapshot(translation_locked=True))

    executor = DeterministicStepExecutor(on_execute=user_locks_during_execution)
    pipeline, catalog, _ = service(executor=executor)
    run = create_and_plan(pipeline, "retranslate_region")
    pipeline.execute_run(run.run_id)

    # the candidate is NOT auto-retried: the region stays locked with the
    # machine payload parked in the candidate list
    assert catalog.current("r1").current_revisions["region"] == "r1-rev-1"

    # the user releases the lock and explicitly reruns the failed target
    catalog.update_region("r1", lock=LockSnapshot())
    catalog.update_region("r1", current_revisions={"region": "user-retype-rev"})
    retry = pipeline.retry_failed_targets(run.run_id)
    retry_result = pipeline.execute_run(retry.run_id)

    assert retry_result.status is PipelineRunStatus.COMPLETED
    # the rerun consumed the RETYPED state (the revision the user left)
    assert catalog.current("r1").current_revisions["region"] != "r1-rev-1"
    assert retry_result.step_runs[-1].status.name == "COMPLETED"
