"""End-to-end deterministic contract vectors for TASK-011."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from application.tasks.service import (  # noqa: E402
    PipelineService,
    ResourceLimits,
)
from application.tasks.store import (  # noqa: E402
    InMemoryPipelineStore,
    InMemorySnapshotProvider,
    InMemoryTargetCatalog,
)
from application.translation.context.gate import (  # noqa: E402
    decide_sfx_translation,
)
from application.translation.pipeline.executor import (  # noqa: E402
    DeterministicStepExecutor,
)
from domain.regions.entities import Region, SfxPolicy  # noqa: E402
from domain.tasks.models import (  # noqa: E402
    CommandType,
    LockSnapshot,
    PipelineError,
    PipelineRunStatus,
    PipelineScope,
    PipelineTaskStatus,
    PlanDecision,
    RegionSnapshot,
    ScopeType,
    StageState,
)


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
    """Build one region snapshot with the **production** policy default.

    The default is ``SfxPolicy.SKIP`` — the same value as the entity and the
    SQLite Schema (D03 §7). TASK-035 closed R-02: with the old ``"translate"``
    default no case in this suite ever combined ``speech`` with the policy a
    real, newly created region carries, which is exactly why F-1 stayed
    invisible here.
    """
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
    catalog.add_page(
        "p2",
        book_id="book-1",
        chapter_id="chapter-1",
        page_order=2,
        regions=(region("r3", "p2"),),
    )
    return catalog


def service(
    catalog: InMemoryTargetCatalog | None = None,
    *,
    provider_bindings: dict | None = None,
    executor=None,
    limits: ResourceLimits | None = None,
) -> tuple[PipelineService, InMemoryTargetCatalog, InMemoryPipelineStore]:
    catalog = catalog or catalog_with_pages()
    store = InMemoryPipelineStore()
    snapshots = InMemorySnapshotProvider(
        settings={"model": "test", "temperature": 0},
        provider_bindings=provider_bindings or {},
        constraint_snapshot_ref="constraint-1",
        context_policy={"window": "current"},
    )
    pipeline = PipelineService(
        catalog,
        store=store,
        snapshots=snapshots,
        executor=executor,
        limits=limits,
    )
    return pipeline, catalog, store


def create_and_plan(
    pipeline: PipelineService,
    command: str,
    *,
    scope: PipelineScope | None = None,
    overrides: dict | None = None,
):
    run = pipeline.create_run(
        command,
        scope or PipelineScope(ScopeType.CHAPTER, chapter_id="chapter-1"),
        overrides=overrides,
    )
    pipeline.plan_run(run.run_id)
    return run


def test_create_run_freezes_targets_and_configuration_before_planning() -> None:
    pipeline, catalog, _ = service()
    run = pipeline.create_run(
        CommandType.TRANSLATE_ALL,
        PipelineScope(ScopeType.CHAPTER, chapter_id="chapter-1"),
        overrides={"settings": {"temperature": 0.2}},
    )

    catalog.update_region("r1", current_revisions={"region": "new-rev"})
    assert run.targets[0].snapshot.region_snapshots()[0].current_revisions["region"] == "r1-rev-1"
    assert run.settings_snapshot["temperature"] == 0.2
    with pytest.raises(TypeError):
        run.settings_snapshot["temperature"] = 0.9


def test_planner_reuses_valid_ocr_and_keeps_rerender_strict() -> None:
    pipeline, catalog, _ = service()
    catalog.update_region(
        "r1",
        stage_states={
            "ocr": StageState.COMPLETED,
            "clean": StageState.COMPLETED,
            "render": StageState.COMPLETED,
        },
    )
    translate = create_and_plan(pipeline, "translate_all")
    r1_units = [unit for task in translate.tasks for unit in task.units if unit.region_id == "r1"]
    assert next(unit for unit in r1_units if unit.step_type == "ocr").decision.value == "skip_valid"
    assert any(unit.step_type == "translate" and unit.decision.value == "run" for unit in r1_units)

    rerender = create_and_plan(pipeline, "rerender_all")
    assert {unit.step_type for task in rerender.tasks for unit in task.units} == {"render"}


def test_every_catalog_command_has_a_page_or_region_plan() -> None:
    pipeline, _, _ = service()
    page_commands = {
        "translate_all", "translate_untranslated", "translate_selected",
        "translate_single", "rerender_all", "rerender_selected",
        "rerender_single", "reinpaint_all", "reinpaint_selected",
        "reinpaint_single", "reocr_all", "reocr_selected", "reocr_single",
    }
    for command in page_commands:
        scope = (
            PipelineScope(ScopeType.PAGE, selected_ids=("p1",))
            if command.endswith("single")
            else PipelineScope(ScopeType.CHAPTER, chapter_id="chapter-1")
        )
        run = create_and_plan(pipeline, command, scope=scope)
        assert run.tasks, command

    for command in {
        "ocr_region", "retranslate_region", "retranslate_region_full",
        "reinpaint_region", "rerender_region",
    }:
        run = create_and_plan(
            pipeline,
            command,
            scope=PipelineScope(ScopeType.REGION, selected_ids=("r1",)),
        )
        assert all(task.region_id == "r1" for task in run.tasks), command


def test_stale_and_missing_prerequisites_are_not_silently_reused() -> None:
    catalog = InMemoryTargetCatalog()
    catalog.add_page(
        "p1",
        book_id="b",
        chapter_id="c",
        regions=(
            region(
                "r1",
                "p1",
                stages={"ocr": "completed", "translate": "stale"},
            ),
        ),
    )
    pipeline, _, _ = service(catalog)
    stale_run = create_and_plan(
        pipeline,
        "translate_single",
        scope=PipelineScope(ScopeType.PAGE, selected_ids=("p1",)),
    )
    assert next(unit for task in stale_run.tasks for unit in task.units if unit.step_type == "translate").decision.value == "run"

    catalog.update_region("r1", stage_states={"translate": StageState.STALE})
    missing_ocr = create_and_plan(
        pipeline,
        "retranslate_region",
        scope=PipelineScope(ScopeType.REGION, selected_ids=("r1",)),
    )
    assert any(
        unit.decision.value == "blocked" and unit.reason == "MISSING_REQUIRED_INPUT"
        for task in missing_ocr.tasks
        for unit in task.units
    )


def test_region_full_only_allows_explicit_translation_and_inpaint_override() -> None:
    catalog = InMemoryTargetCatalog()
    catalog.add_page(
        "p1",
        book_id="b",
        chapter_id="c",
        regions=(
            region(
                "r1",
                "p1",
                lock=LockSnapshot(translation_locked=True, inpaint_locked=True),
            ),
        ),
    )
    pipeline, _, _ = service(catalog)
    blocked = create_and_plan(
        pipeline,
        "retranslate_region_full",
        scope=PipelineScope(ScopeType.REGION, selected_ids=("r1",)),
    )
    assert any(unit.decision.value == "skip_lock" for task in blocked.tasks for unit in task.units)

    allowed = create_and_plan(
        pipeline,
        "retranslate_region_full",
        scope=PipelineScope(ScopeType.REGION, selected_ids=("r1",)),
        overrides={"allow_lock_override": True},
    )
    assert all(unit.decision.value == "run" for task in allowed.tasks for unit in task.units)


def test_rerender_without_clean_is_blocked_with_specific_reason() -> None:
    pipeline, _, _ = service()
    run = create_and_plan(
        pipeline,
        "rerender_region",
        scope=PipelineScope(ScopeType.REGION, selected_ids=("r2",)),
    )
    render = next(unit for task in run.tasks for unit in task.units)
    assert render.decision.value == "blocked"
    assert render.reason == "missing_clean_artifact"


def test_planner_marks_lock_sfx_and_provider_decisions_separately() -> None:
    catalog = InMemoryTargetCatalog()
    catalog.add_page(
        "p1",
        book_id="b",
        chapter_id="c",
        regions=(
            region("locked", "p1", lock=LockSnapshot(region_locked=True)),
            region("sfx", "p1", region_type="sfx", sfx_policy="skip"),
        ),
    )
    pipeline, _, _ = service(catalog, provider_bindings={"ocr": {"available": False}})
    run = create_and_plan(
        pipeline,
        "translate_single",
        scope=PipelineScope(ScopeType.PAGE, selected_ids=("p1",)),
    )
    locked = [unit for task in run.tasks for unit in task.units if unit.region_id == "locked"]
    assert {unit.decision.value for unit in locked} == {"skip_lock"}
    sfx_ocr = next(
        unit for task in run.tasks for unit in task.units
        if unit.region_id == "sfx" and unit.step_type == "ocr"
    )
    assert sfx_ocr.decision.value == "blocked"
    assert sfx_ocr.reason == "PROVIDER_UNAVAILABLE"


def test_all_locked_targets_complete_with_100_percent_and_skip_reasons() -> None:
    catalog = InMemoryTargetCatalog()
    catalog.add_page(
        "p1",
        book_id="b",
        chapter_id="c",
        lock=LockSnapshot(page_locked=True),
        regions=(region("r1", "p1"),),
    )
    pipeline, _, _ = service(catalog)
    run = create_and_plan(
        pipeline,
        "translate_single",
        scope=PipelineScope(ScopeType.PAGE, selected_ids=("p1",)),
    )
    assert run.status is PipelineRunStatus.COMPLETED
    progress = pipeline.get_task_progress(run.run_id)
    assert progress.overall_progress == 1.0
    assert progress.skipped_page_count == 1
    assert progress.completed_page_count == 0
    assert progress.skipped_reasons


def test_execute_commits_each_step_and_projects_page_progress() -> None:
    executor = DeterministicStepExecutor()
    pipeline, catalog, _ = service(executor=executor)
    run = create_and_plan(
        pipeline,
        "retranslate_region",
        scope=PipelineScope(ScopeType.REGION, selected_ids=("r1",)),
    )
    result = pipeline.execute_run(run.run_id)
    assert result.status is PipelineRunStatus.COMPLETED
    assert [step.status.value for step in result.step_runs] == ["completed", "completed"]
    assert catalog.current("r1").stage("translate") is StageState.COMPLETED
    progress = pipeline.get_task_progress(run.run_id)
    assert progress.overall_progress == 1.0
    assert progress.completed_page_count == 1


def test_full_region_retranslate_forces_the_complete_dependency_chain() -> None:
    pipeline, _, _ = service()
    run = create_and_plan(
        pipeline,
        "retranslate_region_full",
        scope=PipelineScope(ScopeType.REGION, selected_ids=("r1",)),
    )
    assert [unit.step_type for task in run.tasks for unit in task.units] == [
        "ocr",
        "color",
        "term_extract",
        "translate",
        "segment",
        "mask_refine",
        "inpaint",
        "render",
    ]
    assert all(
        unit.decision.value == "run"
        for task in run.tasks
        for unit in task.units
    )


def test_output_mapping_mismatch_fails_step_without_current_update() -> None:
    executor = DeterministicStepExecutor(output_target_ids=("wrong",))
    pipeline, catalog, _ = service(executor=executor)
    run = create_and_plan(
        pipeline,
        "retranslate_region",
        scope=PipelineScope(ScopeType.REGION, selected_ids=("r1",)),
    )
    result = pipeline.execute_run(run.run_id)
    assert result.status is PipelineRunStatus.COMPLETED_WITH_FAILURES
    assert result.step_runs[0].error_code == "OUTPUT_MAPPING_MISMATCH"
    assert catalog.current("r1").current_revisions["region"] == "r1-rev-1"


def test_step_result_can_only_be_committed_once() -> None:
    executor = DeterministicStepExecutor()
    pipeline, _, _ = service(executor=executor)
    run = create_and_plan(
        pipeline,
        "retranslate_region",
        scope=PipelineScope(ScopeType.REGION, selected_ids=("r1",)),
    )
    step = pipeline.record_step_attempt(run.tasks[0].task_id, "translate")
    result = executor.execute(step, run.tasks[0].units[0], run)
    pipeline.commit_step_result(step.step_run_id, result)
    with pytest.raises(PipelineError) as error:
        pipeline.commit_step_result(step.step_run_id, result)
    assert error.value.code == "INVALID_RUN_TRANSITION"


def test_revision_conflict_creates_candidate_and_preserves_current() -> None:
    executor = DeterministicStepExecutor()
    pipeline, catalog, _ = service(executor=executor)

    original_execute = executor.execute

    def execute_and_mutate(step_run, unit, run):
        if unit.step_type == "translate":
            catalog.update_region("r1", current_revisions={"region": "manual-rev"})
        return original_execute(step_run, unit, run)

    executor.execute = execute_and_mutate
    run = create_and_plan(
        pipeline,
        "retranslate_region",
        scope=PipelineScope(ScopeType.REGION, selected_ids=("r1",)),
    )
    result = pipeline.execute_run(run.run_id)
    assert result.status is PipelineRunStatus.COMPLETED_WITH_FAILURES
    assert result.candidates[0].reason == "INPUT_REVISION_CHANGED"
    assert catalog.current("r1").current_revisions["region"] == "manual-rev"


def test_pause_is_safe_boundary_and_continue_reuses_completed_step() -> None:
    pipeline, _, _ = service()
    executor = DeterministicStepExecutor()
    pipeline._executor = executor
    run = create_and_plan(
        pipeline,
        "retranslate_region",
        scope=PipelineScope(ScopeType.REGION, selected_ids=("r1",)),
    )

    paused_once = {"value": False}

    def pause_after_translate(step_run, unit, running):
        if unit.step_type == "translate" and not paused_once["value"]:
            paused_once["value"] = True
            pipeline.control_run(running.run_id, "pause")

    executor.on_execute = pause_after_translate
    assert pipeline.execute_run(run.run_id).status is PipelineRunStatus.PAUSED
    pipeline.control_run(run.run_id, "continue")
    assert pipeline.execute_run(run.run_id).status is PipelineRunStatus.COMPLETED
    assert [step.step_type for step in run.step_runs].count("translate") == 1


def test_stop_preserves_completed_steps_and_cancels_remaining_work() -> None:
    executor = DeterministicStepExecutor()
    pipeline, _, _ = service(executor=executor)
    stopped = {"value": False}

    def stop_after_first(step_run, unit, running):
        if not stopped["value"]:
            stopped["value"] = True
            pipeline.control_run(running.run_id, "stop")

    executor.on_execute = stop_after_first
    run = create_and_plan(
        pipeline,
        "retranslate_region_full",
        scope=PipelineScope(ScopeType.REGION, selected_ids=("r1",)),
    )
    result = pipeline.execute_run(run.run_id)
    assert result.status is PipelineRunStatus.CANCELLED
    assert result.step_runs[0].status.value == "completed"
    assert all(task.status is not PipelineTaskStatus.PENDING for task in result.tasks)


def test_recover_continue_restart_and_abandon_have_distinct_crash_semantics() -> None:
    pipeline, _, store = service()
    run = create_and_plan(
        pipeline,
        "retranslate_region",
        scope=PipelineScope(ScopeType.REGION, selected_ids=("r1",)),
    )
    run.status = PipelineRunStatus.RUNNING
    run.tasks[0].status = PipelineTaskStatus.RUNNING
    store.put(run.run_id, run)
    assert pipeline.recover_running_runs() == (run.run_id,)
    assert run.status is PipelineRunStatus.INTERRUPTED

    continued = pipeline.control_run(run.run_id, "continue")
    assert continued.status is PipelineRunStatus.PENDING
    restarted = pipeline.create_run(
        "retranslate_region",
        PipelineScope(ScopeType.REGION, selected_ids=("r1",)),
        source_run_id=run.run_id,
        retry_reason="restart_after_interruption",
    )
    run.interruption_disposition = "restarted"
    assert restarted.source_run_id == run.run_id
    assert restarted.retry_reason == "restart_after_interruption"

    abandoned = create_and_plan(
        pipeline,
        "retranslate_region",
        scope=PipelineScope(ScopeType.REGION, selected_ids=("r1",)),
    )
    abandoned.status = PipelineRunStatus.INTERRUPTED
    store.put(abandoned.run_id, abandoned)
    result = pipeline.control_run(abandoned.run_id, "abandon")
    assert result.status is PipelineRunStatus.CANCELLED
    assert abandoned.termination_reason == "abandoned_after_interruption"


def test_failed_page_retry_creates_new_run_without_rewriting_original() -> None:
    executor = DeterministicStepExecutor(fail_on={("r3", "translate"): "PROVIDER_FAILED"})
    pipeline, _, _ = service(executor=executor)
    run = create_and_plan(pipeline, "translate_all")
    result = pipeline.execute_run(run.run_id)
    assert result.status is PipelineRunStatus.COMPLETED_WITH_FAILURES
    retry = pipeline.retry_failed_targets(run.run_id)
    assert retry.source_run_id == run.run_id
    assert retry.retry_reason == "retry_failed_targets"
    assert retry.requested_targets == ("p2",)
    assert run.status is PipelineRunStatus.COMPLETED_WITH_FAILURES


def test_empty_scope_is_rejected_without_creating_a_run() -> None:
    pipeline, _, store = service()
    with pytest.raises(PipelineError) as error:
        pipeline.create_run(
            "translate_all",
            PipelineScope(ScopeType.PAGE_SELECTION),
        )
    assert error.value.code == "EMPTY_TARGET_SELECTION"
    assert store.list_ids() == ()


def test_resource_limit_is_a_run_fatal_error() -> None:
    executor = DeterministicStepExecutor()
    pipeline, _, _ = service(executor=executor, limits=ResourceLimits(max_step_runs=1))
    run = create_and_plan(
        pipeline,
        "retranslate_region",
        scope=PipelineScope(ScopeType.REGION, selected_ids=("r1",)),
    )
    result = pipeline.execute_run(run.run_id)
    assert result.status is PipelineRunStatus.FAILED
    assert result.fatal_error == "RESOURCE_LIMIT_EXCEEDED"


# ---------------------------------------------------------------------------
# TASK-032 / F-1: the SFX Policy Gate is preconditioned on region_type
# ---------------------------------------------------------------------------

#: Every region type except ``sfx`` (D03 §6.2).
NON_SFX_REGION_TYPES = ("speech", "narration", "title", "note", "other")
#: Steps the SFX Policy Gate may suppress (D06 §85).
SFX_GATED_STEPS = ("translate", "segment", "mask_refine", "inpaint", "render")
DOCUMENTED_SFX_POLICIES = ("skip", "manual", "translate")


def plan_region(catalog, command: str, region_id: str):
    """Plan one region-scoped command and return its units keyed by step."""
    pipeline, _, _ = service(catalog)
    run = create_and_plan(
        pipeline,
        command,
        scope=PipelineScope(ScopeType.REGION, selected_ids=(region_id,)),
    )
    units = [unit for task in run.tasks for unit in task.units]
    return units, {unit.step_type: unit for unit in units}


def single_region_catalog(**region_kwargs) -> InMemoryTargetCatalog:
    catalog = InMemoryTargetCatalog()
    catalog.add_page(
        "p1",
        book_id="b",
        chapter_id="c",
        regions=(region("r1", "p1", **region_kwargs),),
    )
    return catalog


@pytest.mark.parametrize("region_type", NON_SFX_REGION_TYPES)
@pytest.mark.parametrize("sfx_policy", DOCUMENTED_SFX_POLICIES)
def test_sfx_policy_never_gates_a_non_sfx_region(region_type: str, sfx_policy: str) -> None:
    """AC ②: for a non-SFX region any policy value leaves planning untouched.

    ``speech`` × ``skip`` is the **real default** combination (entity and
    Schema default) that F-1 was reported against: before the fix every
    ``translate/segment/mask_refine/inpaint/render`` unit of such a region was
    planned as ``SKIP_POLICY("sfx_skip")``.
    """
    units, _ = plan_region(
        single_region_catalog(
            region_type=region_type,
            sfx_policy=sfx_policy,
            stages={"ocr": "completed", "clean": "completed"},
        ),
        "retranslate_region_full",
        "r1",
    )
    assert units, "the full chain must be planned"
    assert {unit.decision for unit in units} == {PlanDecision.RUN}
    assert [unit for unit in units if unit.reason == "sfx_skip"] == []


@pytest.mark.parametrize("sfx_policy", ("skip", "manual"))
def test_sfx_region_policies_suppress_the_automatic_chain(sfx_policy: str) -> None:
    """AC ①: on a real SFX region ``skip``/``manual`` keep SKIP_POLICY('sfx_skip')."""
    _, by_step = plan_region(
        single_region_catalog(
            region_type="sfx", sfx_policy=sfx_policy, stages={"ocr": "completed"}
        ),
        "retranslate_region_full",
        "r1",
    )
    for step_type in SFX_GATED_STEPS:
        assert by_step[step_type].decision is PlanDecision.SKIP_POLICY, step_type
        assert by_step[step_type].reason == "sfx_skip", step_type


def test_sfx_region_translate_policy_enters_the_translation_chain() -> None:
    """AC ① / AC-SFX-002: SFX + ``translate`` runs the normal chain."""
    units, by_step = plan_region(
        single_region_catalog(
            region_type="sfx",
            sfx_policy="translate",
            stages={"ocr": "completed", "clean": "completed"},
        ),
        "retranslate_region_full",
        "r1",
    )
    assert {unit.decision for unit in units} == {PlanDecision.RUN}
    assert by_step["translate"].decision is PlanDecision.RUN
    assert [unit for unit in units if unit.reason == "sfx_skip"] == []


@pytest.mark.parametrize("missing_policy", ("", None))
def test_sfx_region_without_a_policy_falls_back_to_skip(missing_policy) -> None:
    """AC ③: an absent/blank policy on SFX falls back to the documented skip."""
    _, by_step = plan_region(
        single_region_catalog(
            region_type="sfx",
            sfx_policy=missing_policy,
            stages={"ocr": "completed"},
        ),
        "retranslate_region_full",
        "r1",
    )
    for step_type in SFX_GATED_STEPS:
        assert by_step[step_type].decision is PlanDecision.SKIP_POLICY, step_type
        assert by_step[step_type].reason == "sfx_skip", step_type


@pytest.mark.parametrize("region_type", ("speech", "sfx"))
@pytest.mark.parametrize("sfx_policy", DOCUMENTED_SFX_POLICIES)
def test_planner_agrees_with_the_translate_step_gate(region_type: str, sfx_policy: str) -> None:
    """The planner and the Translate Step must not drift apart again (F-1 root cause).

    The reference verdict is the shared rule
    (:func:`application.translation.context.gate.decide_sfx_translation`) that
    the Translate Step already used while the planner had its own copy.
    """
    units, _ = plan_region(
        single_region_catalog(
            region_type=region_type,
            sfx_policy=sfx_policy,
            stages={"ocr": "completed", "clean": "completed"},
        ),
        "retranslate_region_full",
        "r1",
    )
    planned_skip = any(
        unit.step_type == "translate" and unit.decision is PlanDecision.SKIP_POLICY
        for unit in units
    )
    assert planned_skip is decide_sfx_translation(region_type, sfx_policy).skipped


def test_sfx_region_with_an_out_of_contract_policy_fails_loudly() -> None:
    """A policy outside the Schema's three values is rejected, not translated.

    ``SfxPolicy`` permits only ``skip``/``manual``/``translate`` (D03 §7,
    Schema CHECK); the shared gate validates the value, so a corrupt snapshot
    on an SFX region fails at planning instead of silently entering the
    translation chain. The Translate Step already behaved this way.
    """
    with pytest.raises(ValueError):
        plan_region(
            single_region_catalog(
                region_type="sfx",
                sfx_policy="not-a-policy",
                stages={"ocr": "completed"},
            ),
            "retranslate_region_full",
            "r1",
        )


def test_region_defaults_agree_across_entity_snapshot_and_fixture() -> None:
    """TASK-035 (R-02/R-05 guard): the three SFX defaults must not drift apart.

    Entity, snapshot and this suite's fixture all use the production default
    ``SfxPolicy.SKIP`` (D03 §7, matching the Schema default); the old fixture
    value ``"translate"`` is what kept F-1 invisible to this suite.
    """
    assert (
        Region("r-entity", "p1").sfx_policy.value
        == RegionSnapshot("r-snapshot", "p1").sfx_policy
        == region("r-fixture", "p1").sfx_policy
        == SfxPolicy.SKIP.value
    )
