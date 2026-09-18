"""Command planner and serial scheduler for TASK-011.

The service is intentionally synchronous.  It supplies the contract's safe
Step boundary and deterministic lifecycle without inventing threads,
database tables, or bootstrap wiring outside this Task's whitelist.
"""

from __future__ import annotations

import uuid
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from application.tasks.store import (
    InMemoryPipelineStore,
    InMemorySnapshotProvider,
    PipelineStore,
    SnapshotProvider,
    TargetCatalog,
)
from application.translation.context.gate import (
    SFX_SKIP_REASON,
    decide_sfx_translation,
)
from application.translation.pipeline.executor import (
    DeterministicStepExecutor,
    StepExecutionError,
    StepExecutor,
)
from domain.regions.entities import RegionType, SfxPolicy
from domain.tasks.models import (
    CommandType,
    ControlResult,
    LockSnapshot,
    PipelineError,
    PipelineRun,
    PipelineRunStatus,
    PipelineScope,
    PipelineTask,
    PipelineTaskStatus,
    PlanDecision,
    PlanUnit,
    RegionSnapshot,
    RunTarget,
    ScopeType,
    StageState,
    StepResult,
    StepResultCandidate,
    StepRun,
    StepRunStatus,
    TargetSnapshot,
    TargetType,
    TERMINAL_TASK_STATUSES,
)


@dataclass(frozen=True)
class ResourceLimits:
    """Serial limits; ``max_parallel_*`` document the enforced invariant."""

    max_parallel_pages: int = 1
    max_parallel_steps: int = 1
    max_step_runs: int = 1000

    def __post_init__(self) -> None:
        if self.max_parallel_pages < 1 or self.max_parallel_steps < 1:
            raise ValueError("parallel resource limits must be positive")
        if self.max_step_runs < 1:
            raise ValueError("max_step_runs must be positive")


@dataclass(frozen=True)
class CommitStepOutcome:
    status: str
    step_run_id: str
    candidate_id: str | None = None
    error_code: str | None = None
    detail: str = ""


_FULL_TRANSLATION = (
    "ocr",
    "color",
    "term_extract",
    "translate",
    "segment",
    "mask_refine",
    "inpaint",
    "render",
)
_TRANSLATION = ("translate", "segment", "mask_refine", "inpaint", "render")
_RERENDER = ("render",)
_REINPAINT = ("segment", "mask_refine", "inpaint")
_REOCR = ("ocr",)
_RETRANSLATE = ("translate", "render")

_COMMAND_STEPS = {
    CommandType.TRANSLATE_ALL: _FULL_TRANSLATION,
    CommandType.TRANSLATE_UNTRANSLATED: _FULL_TRANSLATION,
    CommandType.TRANSLATE_SELECTED: _FULL_TRANSLATION,
    CommandType.TRANSLATE_SINGLE: _FULL_TRANSLATION,
    CommandType.RERENDER_ALL: _RERENDER,
    CommandType.RERENDER_SELECTED: _RERENDER,
    CommandType.RERENDER_SINGLE: _RERENDER,
    CommandType.REINPAINT_ALL: _REINPAINT,
    CommandType.REINPAINT_SELECTED: _REINPAINT,
    CommandType.REINPAINT_SINGLE: _REINPAINT,
    CommandType.REOCR_ALL: _REOCR,
    CommandType.REOCR_SELECTED: _REOCR,
    CommandType.REOCR_SINGLE: _REOCR,
    CommandType.OCR_REGION: _REOCR,
    CommandType.RETRANSLATE_REGION: _RETRANSLATE,
    CommandType.RETRANSLATE_REGION_FULL: _FULL_TRANSLATION,
    CommandType.REINPAINT_REGION: _REINPAINT,
    CommandType.RERENDER_REGION: _RERENDER,
}

_PAGE_COMMANDS = {
    CommandType.TRANSLATE_ALL,
    CommandType.TRANSLATE_UNTRANSLATED,
    CommandType.TRANSLATE_SELECTED,
    CommandType.TRANSLATE_SINGLE,
    CommandType.RERENDER_ALL,
    CommandType.RERENDER_SELECTED,
    CommandType.RERENDER_SINGLE,
    CommandType.REINPAINT_ALL,
    CommandType.REINPAINT_SELECTED,
    CommandType.REINPAINT_SINGLE,
    CommandType.REOCR_ALL,
    CommandType.REOCR_SELECTED,
    CommandType.REOCR_SINGLE,
}
_REGION_COMMANDS = {
    CommandType.OCR_REGION,
    CommandType.RETRANSLATE_REGION,
    CommandType.RETRANSLATE_REGION_FULL,
    CommandType.REINPAINT_REGION,
    CommandType.RERENDER_REGION,
}

#: Steps the SFX Policy Gate may suppress (D06 §85).
_SFX_GATED_STEPS = frozenset(
    {"translate", "segment", "mask_refine", "inpaint", "render"}
)

#: D06 §85 / D08 AC-SFX-001: only ``region_type = sfx`` is gated by the policy.
_SFX_REGION_TYPE = RegionType.SFX.value


def _effective_sfx_policy(region: RegionSnapshot) -> str:
    """SFX policy with the documented default applied (TASK-032 AC ③).

    An absent or blank ``sfx_policy`` falls back to ``skip`` (D03 §7) — the very
    value the entity and the SQLite Schema use — so a snapshot written before
    the field existed can never silently turn an SFX region into a translated
    one.
    """
    policy = str(region.sfx_policy or "").strip()
    return policy or SfxPolicy.SKIP.value


def _sfx_gate_suppresses(region: RegionSnapshot) -> bool:
    """True when the SFX Policy Gate suppresses the automatic steps.

    Two things are deliberate here (TASK-032 / F-1):

    - **the region type is a precondition**: a region that is not
      ``region_type = sfx`` is never gated by this policy, whatever its
      ``sfx_policy`` says (D06 §85, D08 AC-SFX-001, AC ②);
    - **the policy rule is not re-implemented**: it is delegated to
      :func:`~application.translation.context.gate.decide_sfx_translation`,
      the same function the Translate Step uses, so the planner and the
      execution layer cannot drift apart again — that drift was the root cause
      of F-1.
    """
    if region.region_type != _SFX_REGION_TYPE:
        return False
    return decide_sfx_translation(
        region.region_type, _effective_sfx_policy(region)
    ).skipped


def _new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex}"


class PipelineService:
    def __init__(
        self,
        catalog: TargetCatalog,
        *,
        store: PipelineStore | None = None,
        snapshots: SnapshotProvider | None = None,
        executor: StepExecutor | None = None,
        limits: ResourceLimits | None = None,
        clean_probe: Callable[[str], bool] | None = None,
    ) -> None:
        self._catalog = catalog
        self._store = store or InMemoryPipelineStore()
        self._snapshots = snapshots or InMemorySnapshotProvider()
        self._executor = executor or DeterministicStepExecutor()
        self._limits = limits or ResourceLimits()
        # TASK-039: optional artifact probe (page_id -> current Clean exists?).
        # ``None`` (every pre-existing construction) keeps the inherited
        # stage-based judgement byte-for-byte.
        self._clean_probe = clean_probe

    # ------------------------------------------------------------------
    # TASK-002 §9: create and plan
    # ------------------------------------------------------------------

    def create_run(
        self,
        command_type: CommandType | str,
        scope: PipelineScope | ScopeType | str,
        selected_ids: Sequence[str] = (),
        *,
        book_id: str | None = None,
        chapter_id: str | None = None,
        overrides: Mapping[str, Any] | None = None,
        source_run_id: str | None = None,
        retry_reason: str | None = None,
    ) -> PipelineRun:
        command = CommandType(command_type)
        if isinstance(scope, PipelineScope):
            actual_scope = scope
        else:
            actual_scope = PipelineScope(
                scope,
                selected_ids=tuple(selected_ids),
                book_id=book_id,
                chapter_id=chapter_id,
            )
        self._validate_command_scope(command, actual_scope)
        raw_targets = self._catalog.expand(actual_scope)
        run_id = _new_id("run")
        frozen = self._snapshots.freeze(run_id, overrides=overrides)
        requested = actual_scope.selected_ids
        if not requested:
            requested = tuple(
                item for item in (actual_scope.book_id, actual_scope.chapter_id) if item
            )
        targets = tuple(
            RunTarget(
                run_target_id=f"{run_id}:target:{index}",
                target_id=snapshot.target_id,
                target_type=snapshot.target_type,
                page_id=snapshot.page_id,
                region_id=snapshot.region_id,
                target_order=index,
                snapshot=snapshot,
            )
            for index, snapshot in enumerate(raw_targets)
        )
        run = PipelineRun(
            run_id=run_id,
            command_type=command,
            scope=actual_scope,
            requested_targets=requested,
            targets=targets,
            settings_snapshot=frozen.settings,
            provider_binding_snapshot=frozen.provider_bindings,
            constraint_snapshot_ref=frozen.constraint_snapshot_ref,
            context_policy=frozen.context_policy,
            source_run_id=source_run_id,
            retry_reason=retry_reason,
        )
        self._persist(run)
        return run

    def plan_run(self, run_id: str, *, mode: str = "initial") -> PipelineRun:
        run = self._require_run(run_id)
        if mode not in {"initial", "resume_blocked", "continue"}:
            raise PipelineError("INVALID_RUN_TRANSITION", f"unknown plan mode {mode}")
        if mode == "initial" and run.status not in {
            PipelineRunStatus.PENDING,
            PipelineRunStatus.PAUSED,
        }:
            raise PipelineError("INVALID_RUN_TRANSITION", "run is not pending")
        if mode == "resume_blocked" and run.status is not PipelineRunStatus.BLOCKED:
            raise PipelineError("INVALID_RUN_TRANSITION", "run is not blocked")
        if mode == "continue" and run.status is not PipelineRunStatus.INTERRUPTED:
            raise PipelineError("INVALID_RUN_TRANSITION", "run is not interrupted")

        tasks: list[PipelineTask] = []
        terminal_ids: set[str] = set()
        for run_target in run.targets:
            view = (
                self._catalog.current(run_target.target_id)
                if mode in {"resume_blocked", "continue"}
                else run_target.snapshot
            )
            task = PipelineTask(
                task_id=f"{run.run_id}:task:{run_target.target_order}",
                run_target_id=run_target.run_target_id,
                target_id=run_target.target_id,
                target_type=run_target.target_type,
                page_id=run_target.page_id,
                region_id=run_target.region_id,
            )
            units = self._plan_target(run, task, view)
            task.units = tuple(units)
            task.status = self._planned_task_status(units)
            terminal_ids.update(unit.unit_id for unit in units if unit.decision.is_terminal)
            tasks.append(task)

        run.tasks = tasks
        run.planned_step_units = sum(len(task.units) for task in tasks)
        run.terminal_unit_ids = terminal_ids
        run.terminal_step_units = len(terminal_ids)
        run.step_runs = [] if mode == "initial" else run.step_runs
        self._set_planned_run_status(run)
        self._persist(run)
        return run

    # ------------------------------------------------------------------
    # planner internals
    # ------------------------------------------------------------------

    def _plan_target(
        self,
        run: PipelineRun,
        task: PipelineTask,
        target: TargetSnapshot,
    ) -> list[PlanUnit]:
        units: list[PlanUnit] = []
        region_views = target.region_snapshots()
        if target.target_type is TargetType.PAGE and not target.regions:
            region_views = ()
        if not region_views:
            units.extend(self._plan_region(run, task, target, None))
        else:
            for region in region_views:
                units.extend(self._plan_region(run, task, target, region))
        return units

    def _plan_region(
        self,
        run: PipelineRun,
        task: PipelineTask,
        target: TargetSnapshot,
        region: RegionSnapshot | None,
    ) -> list[PlanUnit]:
        steps = _COMMAND_STEPS[run.command_type]
        forced = self._forced_steps(run.command_type)
        target_id = region.region_id if region is not None else target.page_id
        current_revisions = (
            dict(region.current_revisions) if region is not None
            else dict(target.current_revisions)
        )
        lock = self._effective_lock(target, region)
        stage_states = (
            dict(region.stage_states) if region is not None
            else dict(target.stage_states)
        )
        decisions: dict[str, PlanDecision] = {}
        reasons: dict[str, str | None] = {}
        units: list[PlanUnit] = []
        for step_type in steps:
            decision, reason = self._decide_step(
                run,
                target,
                region,
                step_type,
                stage_states,
                decisions,
                reasons,
                forced,
            )
            unit = PlanUnit(
                unit_id=f"{task.task_id}:{target_id}:{step_type}",
                task_id=task.task_id,
                target_id=target_id,
                page_id=target.page_id,
                region_id=region.region_id if region is not None else None,
                step_type=step_type,
                decision=decision,
                reason=reason,
                expected_revisions=current_revisions,
                expected_lock=lock,
            )
            units.append(unit)
            decisions[step_type] = decision
            reasons[step_type] = reason
        return units

    def _decide_step(
        self,
        run: PipelineRun,
        target: TargetSnapshot,
        region: RegionSnapshot | None,
        step_type: str,
        stages: Mapping[str, StageState],
        previous: Mapping[str, PlanDecision],
        previous_reasons: Mapping[str, str | None],
        forced: frozenset[str],
    ) -> tuple[PlanDecision, str | None]:
        lock = self._effective_lock(target, region)
        allow_override = bool(run.settings_snapshot.get("allow_lock_override", False))

        if lock.page_locked or lock.region_locked:
            return PlanDecision.SKIP_LOCK, "page_or_region_locked"

        if (
            region is not None
            and step_type in _SFX_GATED_STEPS
            and _sfx_gate_suppresses(region)
        ):
            return PlanDecision.SKIP_POLICY, SFX_SKIP_REASON

        if step_type == "translate" and not allow_override:
            if lock.translation_locked:
                return PlanDecision.SKIP_LOCK, "translation_locked"
            if region is not None and (region.manual_edited or region.final_confirmed):
                return PlanDecision.SKIP_LOCK, "manual_translation_protected"
        if step_type in {"segment", "mask_refine", "inpaint"} and not allow_override:
            if lock.inpaint_locked:
                return PlanDecision.SKIP_LOCK, "inpaint_locked"

        if step_type not in forced and stages.get(step_type, StageState.NOT_STARTED).is_valid:
            return PlanDecision.SKIP_VALID, "stage_completed"

        for prior_step, prior_decision in previous.items():
            if prior_decision is PlanDecision.BLOCKED:
                return PlanDecision.BLOCKED, previous_reasons.get(prior_step) or "MISSING_REQUIRED_INPUT"
            if prior_decision in {PlanDecision.SKIP_POLICY, PlanDecision.SKIP_LOCK} and step_type in {
                "segment",
                "mask_refine",
                "inpaint",
                "render",
            }:
                return prior_decision, previous_reasons.get(prior_step)

        if not self._required_input_available(step_type, stages, previous):
            return PlanDecision.BLOCKED, "MISSING_REQUIRED_INPUT"
        if step_type == "render" and not self._clean_available(
            target.page_id, stages, previous
        ):
            return PlanDecision.BLOCKED, "missing_clean_artifact"
        if not self._provider_available(run, step_type):
            return PlanDecision.BLOCKED, "PROVIDER_UNAVAILABLE"
        return PlanDecision.RUN, None

    @staticmethod
    def _required_input_available(
        step_type: str,
        stages: Mapping[str, StageState],
        previous: Mapping[str, PlanDecision],
    ) -> bool:
        requirements = {
            "color": "ocr",
            "term_extract": "ocr",
            "translate": "ocr",
            "segment": "ocr",
            "mask_refine": "segment",
            "inpaint": "mask_refine",
        }
        required = requirements.get(step_type)
        if required is None:
            if step_type == "render":
                return True
            return True
        return stages.get(required, StageState.NOT_STARTED).is_valid or previous.get(required) is PlanDecision.RUN

    def _clean_available(
        self,
        page_id: str,
        stages: Mapping[str, StageState],
        previous: Mapping[str, PlanDecision],
    ) -> bool:
        """TASK-039 (TASK-033 R-001, P2): Clean availability is a question
        about the *artifact*, not about a stage nobody writes.

        Root cause (AC 1): the inherited judge read ``stages["clean"]`` — but
        no step ever writes a ``clean`` **stage** (inpaint completes the
        ``inpaint`` stage and commits the Clean artifact pointer inside the
        handler, outside ``revision_updates``), so for real data the check was
        always false and render-only commands (``RERENDER_*``) stayed
        planning-``BLOCKED(missing_clean_artifact)`` across runs even with a
        current Clean revision on disk. Existing unit tests only passed
        because they hand-wrote a ``clean`` stage into their fixtures.

        The judge keeps both historical inputs — same-run ``inpaint is RUN``
        and a valid ``clean`` stage (for any future writer) — and adds an
        optional artifact probe (TASK-039 AC 2 landed the optional parameter;
        its production injection at assembly is wired by TASK-040).
        ``probe is None`` (every pre-existing construction) preserves the old
        decision exactly;
        the probe can only turn a would-be BLOCKED into RUN when a current
        Clean artifact really exists — it never blocks something the old
        judge allowed (AC 3).
        """
        if previous.get("inpaint") is PlanDecision.RUN:
            return True
        if stages.get("clean", StageState.NOT_STARTED).is_valid:
            return True
        probe = self._clean_probe
        return probe is not None and bool(probe(page_id))

    @staticmethod
    def _effective_lock(
        target: TargetSnapshot, region: RegionSnapshot | None
    ) -> LockSnapshot:
        if region is None:
            return target.lock
        return LockSnapshot(
            page_locked=target.lock.page_locked,
            region_locked=region.lock.region_locked,
            translation_locked=region.lock.translation_locked,
            inpaint_locked=region.lock.inpaint_locked,
        )

    @staticmethod
    def _forced_steps(command: CommandType) -> frozenset[str]:
        if command in {CommandType.RERENDER_ALL, CommandType.RERENDER_SELECTED, CommandType.RERENDER_SINGLE, CommandType.RERENDER_REGION}:
            return frozenset({"render"})
        if command in {CommandType.REOCR_ALL, CommandType.REOCR_SELECTED, CommandType.REOCR_SINGLE, CommandType.OCR_REGION}:
            return frozenset({"ocr"})
        if command in {CommandType.RETRANSLATE_REGION, CommandType.RETRANSLATE_REGION_FULL}:
            return frozenset(_FULL_TRANSLATION if command is CommandType.RETRANSLATE_REGION_FULL else {"translate", "render"})
        if command in {CommandType.REINPAINT_ALL, CommandType.REINPAINT_SELECTED, CommandType.REINPAINT_SINGLE, CommandType.REINPAINT_REGION}:
            return frozenset({"inpaint"})
        return frozenset()

    @staticmethod
    def _provider_available(run: PipelineRun, step_type: str) -> bool:
        binding = run.provider_binding_snapshot.get(step_type)
        if binding is None:
            return True
        if isinstance(binding, Mapping):
            if binding.get("available") is False or binding.get("enabled") is False:
                return False
        return binding is not False

    @staticmethod
    def _planned_task_status(units: Sequence[PlanUnit]) -> PipelineTaskStatus:
        if not units:
            return PipelineTaskStatus.SKIPPED
        decisions = {unit.decision for unit in units}
        if PlanDecision.RUN in decisions:
            return PipelineTaskStatus.PENDING
        if PlanDecision.BLOCKED in decisions:
            return PipelineTaskStatus.BLOCKED
        return PipelineTaskStatus.SKIPPED

    @staticmethod
    def _set_planned_run_status(run: PipelineRun) -> None:
        statuses = {task.status for task in run.tasks}
        if PipelineTaskStatus.BLOCKED in statuses:
            run.status = PipelineRunStatus.BLOCKED
        elif PipelineTaskStatus.PENDING in statuses:
            run.status = PipelineRunStatus.PENDING
        else:
            run.status = PipelineRunStatus.COMPLETED

    @staticmethod
    def _validate_command_scope(command: CommandType, scope: PipelineScope) -> None:
        if command in _REGION_COMMANDS and scope.scope_type is not ScopeType.REGION:
            raise PipelineError("TARGET_NOT_FOUND", "region command requires region scope")
        if command in _PAGE_COMMANDS and scope.scope_type is ScopeType.REGION:
            raise PipelineError("TARGET_NOT_FOUND", "page command requires page scope")

    # ------------------------------------------------------------------
    # TASK-002 §9: Step attempts and commits
    # ------------------------------------------------------------------

    def record_step_attempt(
        self,
        task_id: str,
        step_type: str,
        *,
        retry_no: int = 0,
    ) -> StepRun:
        run, task = self._find_task(task_id)
        unit = next(
            (unit for unit in task.units if unit.step_type == step_type and unit.decision is PlanDecision.RUN),
            None,
        )
        if unit is None:
            raise PipelineError("MISSING_REQUIRED_INPUT", f"no runnable {step_type} unit")
        return self._record_step_attempt(run, task, unit, retry_no=retry_no)

    def _record_step_attempt(
        self,
        run: PipelineRun,
        task: PipelineTask,
        unit: PlanUnit,
        *,
        retry_no: int = 0,
    ) -> StepRun:
        current = self._catalog.current(unit.target_id)
        input_refs = dict(current.current_revisions)
        lock = current.lock
        step_run = StepRun(
            step_run_id=_new_id("step"),
            task_id=task.task_id,
            target_id=unit.target_id,
            page_id=unit.page_id,
            region_id=unit.region_id,
            step_type=unit.step_type,
            unit_id=unit.unit_id,
            status=StepRunStatus.RUNNING,
            input_refs=input_refs,
            lock_snapshot=lock,
            retry_no=retry_no,
        )
        run.step_runs.append(step_run)
        task.step_run_ids.append(step_run.step_run_id)
        task.status = PipelineTaskStatus.RUNNING
        self._persist(run)
        return step_run

    def commit_step_result(
        self,
        step_run_id: str,
        result: StepResult,
    ) -> CommitStepOutcome:
        run, step_run, task, unit = self._find_step(step_run_id)
        if step_run.status is not StepRunStatus.RUNNING:
            raise PipelineError("INVALID_RUN_TRANSITION", "StepRun is no longer running")
        expected_targets = {unit.target_id}
        output_targets = set(result.output_target_ids or (result.target_id,))
        if result.target_id != unit.target_id or result.step_type != unit.step_type or output_targets != expected_targets:
            return self._fail_mapping(run, task, step_run, unit)

        outcome = self._catalog.commit_step(
            target_id=unit.target_id,
            expected_revisions=step_run.input_refs,
            expected_lock=step_run.lock_snapshot,
            stage_updates=result.next_stage_states or {unit.step_type: StageState.COMPLETED},
            revision_updates=result.revision_updates,
        )
        if outcome.status == "applied":
            step_run.status = StepRunStatus.COMPLETED
            step_run.output = result.outputs
            self._mark_terminal(run, unit.unit_id)
            self._persist(run)
            return CommitStepOutcome("committed", step_run.step_run_id)

        if outcome.status in {"input_revision_changed", "lock_changed"}:
            code = "INPUT_REVISION_CHANGED" if outcome.status == "input_revision_changed" else "LOCK_CHANGED"
            step_run.status = StepRunStatus.FAILED
            step_run.error_code = code
            step_run.error_detail = outcome.detail
            candidate = StepResultCandidate(
                candidate_id=_new_id("candidate"),
                step_run_id=step_run.step_run_id,
                target_id=unit.target_id,
                page_id=unit.page_id,
                region_id=unit.region_id,
                result_kind="region" if unit.region_id else "page",
                base_revision_id=next(iter(step_run.input_refs.values()), None),
                payload=result.outputs,
                reason=code,
            )
            run.candidates.append(candidate)
            task.status = PipelineTaskStatus.FAILED
            task.error_code = code
            task.error_detail = outcome.detail
            self._mark_terminal(run, unit.unit_id)
            self._persist(run)
            return CommitStepOutcome("candidate", step_run.step_run_id, candidate.candidate_id, code, outcome.detail)

        code = "DB_FAILED" if outcome.status == "db_failed" else "TARGET_NOT_FOUND"
        return self._fail_step(run, task, step_run, unit, code, outcome.detail)

    def _fail_mapping(
        self,
        run: PipelineRun,
        task: PipelineTask,
        step_run: StepRun,
        unit: PlanUnit,
    ) -> CommitStepOutcome:
        step_run.status = StepRunStatus.FAILED
        step_run.error_code = "OUTPUT_MAPPING_MISMATCH"
        task.status = PipelineTaskStatus.FAILED
        task.error_code = step_run.error_code
        self._mark_terminal(run, unit.unit_id)
        self._persist(run)
        return CommitStepOutcome(
            "failed", step_run.step_run_id, error_code=step_run.error_code
        )

    def _fail_step(
        self,
        run: PipelineRun,
        task: PipelineTask,
        step_run: StepRun,
        unit: PlanUnit,
        code: str,
        detail: str = "",
    ) -> CommitStepOutcome:
        step_run.status = StepRunStatus.FAILED
        step_run.error_code = code
        step_run.error_detail = detail
        task.status = PipelineTaskStatus.FAILED
        task.error_code = code
        task.error_detail = detail
        self._mark_terminal(run, unit.unit_id)
        self._persist(run)
        return CommitStepOutcome("failed", step_run.step_run_id, error_code=code, detail=detail)

    @staticmethod
    def _mark_terminal(run: PipelineRun, unit_id: str) -> None:
        if unit_id not in run.terminal_unit_ids:
            run.terminal_unit_ids.add(unit_id)
            run.terminal_step_units += 1

    # ------------------------------------------------------------------
    # serial scheduler and controls
    # ------------------------------------------------------------------

    def execute_run(self, run_id: str) -> PipelineRun:
        run = self._require_run(run_id)
        if not run.tasks:
            self.plan_run(run_id)
        if run.status in {
            PipelineRunStatus.BLOCKED,
            PipelineRunStatus.PAUSED,
            PipelineRunStatus.CANCELLED,
            PipelineRunStatus.FAILED,
            PipelineRunStatus.COMPLETED,
            PipelineRunStatus.COMPLETED_WITH_FAILURES,
            PipelineRunStatus.INTERRUPTED,
        }:
            return run
        run.status = PipelineRunStatus.RUNNING
        self._persist(run)
        for task in run.tasks:
            if task.status in TERMINAL_TASK_STATUSES:
                continue
            if task.status is PipelineTaskStatus.BLOCKED:
                continue
            task_failed = False
            for unit in task.units:
                if unit.unit_id in run.terminal_unit_ids:
                    continue
                if unit.decision is PlanDecision.SKIP_VALID or unit.decision is PlanDecision.SKIP_LOCK or unit.decision is PlanDecision.SKIP_POLICY:
                    continue
                if unit.decision is PlanDecision.BLOCKED:
                    task.status = PipelineTaskStatus.BLOCKED
                    task.error_code = unit.reason or "MISSING_REQUIRED_INPUT"
                    break
                if run.cancel_requested:
                    self._cancel_remaining(run, task, unit)
                    break
                if run.pause_requested:
                    task.status = PipelineTaskStatus.PENDING
                    run.status = PipelineRunStatus.PAUSED
                    self._persist(run)
                    return run
                if len(run.step_runs) >= self._limits.max_step_runs:
                    run.fatal_error = "RESOURCE_LIMIT_EXCEEDED"
                    run.status = PipelineRunStatus.FAILED
                    self._cancel_remaining(run, task, unit)
                    self._persist(run)
                    return run

                step_run = self._record_step_attempt(run, task, unit)
                try:
                    result = self._executor.execute(step_run, unit, run)
                except StepExecutionError as error:
                    self._fail_step(run, task, step_run, unit, error.code, error.detail)
                    task_failed = True
                except Exception as error:  # provider failures become task failures
                    self._fail_step(run, task, step_run, unit, "STEP_FAILED", str(error))
                    task_failed = True
                else:
                    committed = self.commit_step_result(step_run.step_run_id, result)
                    if committed.status != "committed":
                        task_failed = True

                if task_failed:
                    self._cancel_remaining(run, task, unit)
                    break
                if run.cancel_requested:
                    self._cancel_remaining(run, task, unit)
                    break
                if run.pause_requested:
                    task.status = PipelineTaskStatus.PENDING
                    run.status = PipelineRunStatus.PAUSED
                    self._persist(run)
                    return run

            if run.cancel_requested:
                task.status = PipelineTaskStatus.CANCELLED
                self._cancel_remaining(run, task, None)
                self._cancel_pending_tasks(run)
                run.status = PipelineRunStatus.CANCELLED
                self._persist(run)
                return run
            if task_failed or task.status is PipelineTaskStatus.FAILED:
                task.status = PipelineTaskStatus.FAILED
            elif task.status is PipelineTaskStatus.RUNNING:
                task.status = PipelineTaskStatus.COMPLETED

        self._aggregate_run(run)
        self._persist(run)
        return run

    def control_run(self, run_id: str, action: str) -> ControlResult:
        run = self._require_run(run_id)
        if action == "pause":
            if run.status not in {PipelineRunStatus.PENDING, PipelineRunStatus.RUNNING}:
                raise PipelineError("INVALID_RUN_TRANSITION", "pause requires pending or running")
            run.pause_requested = True
            if run.status is PipelineRunStatus.PENDING:
                run.status = PipelineRunStatus.PAUSED
            self._persist(run)
            return ControlResult(run.run_id, run.status)

        if action == "stop":
            if run.status in {PipelineRunStatus.COMPLETED, PipelineRunStatus.COMPLETED_WITH_FAILURES, PipelineRunStatus.FAILED, PipelineRunStatus.CANCELLED}:
                raise PipelineError("INVALID_RUN_TRANSITION", "run is already terminal")
            run.cancel_requested = True
            if run.status in {PipelineRunStatus.PENDING, PipelineRunStatus.PAUSED}:
                self._cancel_pending_tasks(run)
                run.status = PipelineRunStatus.CANCELLED
            self._persist(run)
            return ControlResult(run.run_id, run.status)

        if action == "continue":
            if run.status is PipelineRunStatus.PAUSED:
                run.pause_requested = False
                run.status = PipelineRunStatus.PENDING
                self._persist(run)
                return ControlResult(run.run_id, run.status)
            if run.status is PipelineRunStatus.INTERRUPTED:
                run.cancel_requested = False
                run.pause_requested = False
                self.plan_run(run_id, mode="continue")
                return ControlResult(run.run_id, run.status)
            raise PipelineError("INVALID_RUN_TRANSITION", "continue requires paused or interrupted")

        if action == "restart":
            if run.status is not PipelineRunStatus.INTERRUPTED:
                raise PipelineError("RUN_NOT_INTERRUPTED", run.run_id)
            fresh = self.create_run(
                run.command_type,
                run.scope,
                source_run_id=run.run_id,
                retry_reason="restart_after_interruption",
            )
            run.interruption_disposition = "restarted"
            self._persist(run)
            return ControlResult(run.run_id, run.status, fresh.run_id)

        if action == "abandon":
            if run.status is not PipelineRunStatus.INTERRUPTED:
                raise PipelineError("RUN_NOT_INTERRUPTED", run.run_id)
            run.status = PipelineRunStatus.CANCELLED
            run.termination_reason = "abandoned_after_interruption"
            self._persist(run)
            return ControlResult(run.run_id, run.status)

        raise PipelineError("INVALID_RUN_TRANSITION", f"unknown control action {action}")

    def recover_running_runs(self) -> tuple[str, ...]:
        recovered: list[str] = []
        for run_id in self._store.list_ids():
            run = self._store.get(run_id)
            if run is None or run.status is not PipelineRunStatus.RUNNING:
                continue
            run.status = PipelineRunStatus.INTERRUPTED
            for task in run.tasks:
                if task.status is PipelineTaskStatus.RUNNING:
                    task.status = PipelineTaskStatus.INTERRUPTED
            for step in run.step_runs:
                if step.status is StepRunStatus.RUNNING:
                    step.status = StepRunStatus.INTERRUPTED
            self._persist(run)
            recovered.append(run_id)
        return tuple(recovered)

    def retry_failed_targets(self, run_id: str) -> PipelineRun:
        run = self._require_run(run_id)
        failed_pages = tuple(
            dict.fromkeys(
                task.page_id
                for task in run.tasks
                if task.status is PipelineTaskStatus.FAILED and task.target_type is TargetType.PAGE
            )
        )
        if not failed_pages:
            raise PipelineError("TARGET_NOT_FOUND", "run has no failed page targets")
        return self.create_run(
            run.command_type,
            PipelineScope(ScopeType.PAGE_SELECTION, selected_ids=failed_pages),
            source_run_id=run.run_id,
            retry_reason="retry_failed_targets",
        )

    def _cancel_remaining(
        self, run: PipelineRun, task: PipelineTask, current: PlanUnit | None
    ) -> None:
        after_current = current is None
        for unit in task.units:
            if current is not None and unit.unit_id == current.unit_id:
                after_current = True
                continue
            if not after_current or unit.decision is not PlanDecision.RUN:
                continue
            self._mark_terminal(run, unit.unit_id)

    def _cancel_pending_tasks(self, run: PipelineRun) -> None:
        for task in run.tasks:
            if task.status not in TERMINAL_TASK_STATUSES:
                task.status = PipelineTaskStatus.CANCELLED
                self._cancel_remaining(run, task, None)

    def _aggregate_run(self, run: PipelineRun) -> None:
        if run.fatal_error:
            run.status = PipelineRunStatus.FAILED
            return
        if run.cancel_requested:
            run.status = PipelineRunStatus.CANCELLED
            return
        statuses = {task.status for task in run.tasks}
        if PipelineTaskStatus.BLOCKED in statuses:
            run.status = PipelineRunStatus.BLOCKED
        elif PipelineTaskStatus.FAILED in statuses:
            run.status = PipelineRunStatus.COMPLETED_WITH_FAILURES
        elif statuses - TERMINAL_TASK_STATUSES:
            run.status = PipelineRunStatus.RUNNING
        else:
            run.status = PipelineRunStatus.COMPLETED

    # ------------------------------------------------------------------
    # progress / lookup
    # ------------------------------------------------------------------

    def get_task_progress(self, run_id: str):
        run = self._require_run(run_id)
        from domain.tasks.models import TaskProgressSnapshot

        pages: dict[str, list[PipelineTask]] = {}
        for task in run.tasks:
            pages.setdefault(task.page_id, []).append(task)
        counts = {key: 0 for key in ("completed", "failed", "skipped", "blocked", "waiting", "processing")}
        for tasks in pages.values():
            statuses = {task.status for task in tasks}
            if PipelineTaskStatus.FAILED in statuses:
                key = "failed"
            elif PipelineTaskStatus.RUNNING in statuses:
                key = "processing"
            elif PipelineTaskStatus.BLOCKED in statuses:
                key = "blocked"
            elif statuses and statuses <= {PipelineTaskStatus.COMPLETED}:
                key = "completed"
            elif statuses and statuses <= {PipelineTaskStatus.SKIPPED}:
                key = "skipped"
            else:
                key = "waiting"
            counts[key] += 1
        reasons = tuple(
            dict.fromkeys(
                unit.reason
                for task in run.tasks
                for unit in task.units
                if unit.decision.is_terminal and unit.reason
            )
        )
        progress = (
            run.terminal_step_units / run.planned_step_units
            if run.planned_step_units
            else 0.0
        )
        return TaskProgressSnapshot(
            run_id=run.run_id,
            run_status=run.status,
            overall_progress=progress,
            planned_step_units=run.planned_step_units,
            terminal_step_units=run.terminal_step_units,
            total_page_count=len(pages),
            completed_page_count=counts["completed"],
            failed_page_count=counts["failed"],
            skipped_page_count=counts["skipped"],
            blocked_page_count=counts["blocked"],
            waiting_page_count=counts["waiting"],
            processing_page_count=counts["processing"],
            skipped_reasons=reasons,
        )

    def _require_run(self, run_id: str) -> PipelineRun:
        run = self._store.get(run_id)
        if run is None:
            raise PipelineError("TARGET_NOT_FOUND", f"run {run_id} not found")
        return run

    def _persist(self, run: PipelineRun) -> None:
        """Persist every lifecycle boundary for durable stores."""
        self._store.put(run.run_id, run)

    def _find_task(self, task_id: str) -> tuple[PipelineRun, PipelineTask]:
        for run_id in self._store.list_ids():
            run = self._store.get(run_id)
            if run is None:
                continue
            for task in run.tasks:
                if task.task_id == task_id:
                    return run, task
        raise PipelineError("TARGET_NOT_FOUND", f"task {task_id} not found")

    def _find_step(self, step_run_id: str) -> tuple[PipelineRun, StepRun, PipelineTask, PlanUnit]:
        for run_id in self._store.list_ids():
            run = self._store.get(run_id)
            if run is None:
                continue
            for step in run.step_runs:
                if step.step_run_id != step_run_id:
                    continue
                task = next(task for task in run.tasks if task.task_id == step.task_id)
                unit = next(unit for unit in task.units if unit.unit_id == step.unit_id)
                return run, step, task, unit
        raise PipelineError("TARGET_NOT_FOUND", f"step {step_run_id} not found")
