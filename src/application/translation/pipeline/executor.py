"""Injected step executors for the TASK-011 scheduler.

The scheduler owns lifecycle and safety; providers own step work.  The
deterministic executor is deliberately boring and dependency-free so the
complete command/error graph can be tested without claiming AI quality.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Set
from typing import Protocol

from domain.tasks.models import PipelineRun, PlanUnit, StepResult, StepRun


class StepExecutionError(RuntimeError):
    def __init__(self, code: str, detail: str = "") -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}" if detail else code)


class StepExecutor(Protocol):
    def execute(
        self, step_run: StepRun, unit: PlanUnit, run: PipelineRun
    ) -> StepResult: ...


class DeterministicStepExecutor:
    """A predictable test executor with injectable failures and callbacks."""

    def __init__(
        self,
        *,
        fail_on: Mapping[tuple[str, str], str] | Set[tuple[str, str]] = (),
        output_target_ids: tuple[str, ...] | None = None,
        on_execute: Callable[[StepRun, PlanUnit, PipelineRun], None] | None = None,
    ) -> None:
        self._fail_on = (
            dict(fail_on) if isinstance(fail_on, Mapping)
            else {key: "STEP_FAILED" for key in fail_on}
        )
        self.output_target_ids = output_target_ids
        self.on_execute = on_execute
        self.calls: list[tuple[str, str]] = []

    def execute(
        self, step_run: StepRun, unit: PlanUnit, run: PipelineRun
    ) -> StepResult:
        self.calls.append((unit.target_id, unit.step_type))
        if self.on_execute is not None:
            self.on_execute(step_run, unit, run)
        failure = self._fail_on.get((unit.target_id, unit.step_type))
        if failure is not None:
            raise StepExecutionError(failure, f"injected failure for {unit.target_id}")
        revision_key = "region" if unit.region_id else "page"
        return StepResult(
            target_id=unit.target_id,
            step_type=unit.step_type,
            outputs={"deterministic": f"{unit.target_id}:{unit.step_type}"},
            output_target_ids=self.output_target_ids or (unit.target_id,),
            revision_updates={revision_key: f"{unit.target_id}:{step_run.step_run_id}"},
        )

