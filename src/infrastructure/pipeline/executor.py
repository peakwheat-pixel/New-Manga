"""Explicit production provider dispatch for PipelineService."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from application.translation.pipeline.executor import StepExecutionError, StepExecutor
from domain.tasks.models import PipelineRun, PlanUnit, StepResult, StepRun

StepHandler = Callable[[StepRun, PlanUnit, PipelineRun], StepResult]


class ProductionStepExecutor(StepExecutor):
    """Dispatch to registered production handlers without fake output.

    The registry is deliberately explicit: an absent handler is a provider
    availability error, never a successful deterministic placeholder.
    """

    def __init__(self, handlers: Mapping[str, StepHandler] | None = None) -> None:
        self._handlers = dict(handlers or {})

    def execute(
        self, step_run: StepRun, unit: PlanUnit, run: PipelineRun
    ) -> StepResult:
        binding: Any = run.provider_binding_snapshot.get(unit.step_type)
        handler = self._resolve(unit.step_type, binding)
        if handler is None:
            raise StepExecutionError(
                "PROVIDER_UNAVAILABLE",
                f"no production handler for step={unit.step_type!r} binding={binding!r}",
            )
        try:
            result = handler(step_run, unit, run)
        except StepExecutionError:
            raise
        except Exception as error:
            raise StepExecutionError("PROVIDER_FAILED", str(error)) from error
        if not isinstance(result, StepResult):
            raise StepExecutionError("INVALID_PROVIDER_OUTPUT", "handler did not return StepResult")
        return result

    def _resolve(self, step_type: str, binding: Any) -> StepHandler | None:
        handler = self._handlers.get(step_type)
        if handler is not None:
            return handler
        if isinstance(binding, Mapping):
            for key in ("provider_id", "provider_profile_id", "id"):
                provider_id = binding.get(key)
                if isinstance(provider_id, str) and provider_id in self._handlers:
                    return self._handlers[provider_id]
        if isinstance(binding, str):
            return self._handlers.get(binding)
        return None
