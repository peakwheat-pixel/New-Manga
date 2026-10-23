"""Check result model shared by every layer of the software smoke tool."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import time
from typing import Any, Callable, Mapping, Sequence

PASS = "PASS"
FAIL = "FAIL"
SKIP = "SKIP"
BLOCKED = "BLOCKED"


class SmokeFailure(Exception):
    """A discriminating check failure with a stable machine code."""

    def __init__(
        self, code: str, message: str, detail: Mapping[str, Any] | None = None
    ) -> None:
        self.code = code
        self.message = message
        self.detail: dict[str, Any] = dict(detail or {})
        super().__init__(f"{code}: {message}")


class SmokeSkip(Exception):
    """An explicitly skipped check (for example an opt-in packaging re-verify)."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(f"{code}: {message}")


@dataclass
class RunOptions:
    """Options shared by all layers for one run."""

    run_root: Path
    repack: bool = False

    @property
    def logs_dir(self) -> Path:
        path = self.run_root / "logs"
        path.mkdir(parents=True, exist_ok=True)
        return path


@dataclass(frozen=True)
class CheckSpec:
    id: str
    name: str
    description: str = ""


@dataclass
class CheckResult:
    id: str
    name: str
    status: str = PASS
    code: str | None = None
    message: str = ""
    duration_ms: int = 0
    detail: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "code": self.code,
            "message": self.message,
            "duration_ms": self.duration_ms,
            "detail": self.detail,
        }


@dataclass
class LayerResult:
    id: str
    name: str
    checks: list[CheckResult] = field(default_factory=list)
    duration_ms: int = 0
    skipped: bool = False
    skip_reason: str = ""

    @property
    def status(self) -> str:
        if self.skipped:
            return SKIP
        if any(check.status == FAIL for check in self.checks):
            return FAIL
        if any(check.status == BLOCKED for check in self.checks):
            return BLOCKED
        if self.checks and all(check.status == SKIP for check in self.checks):
            return SKIP
        return PASS

    def to_dict(self) -> dict[str, Any]:
        payload = {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "duration_ms": self.duration_ms,
            "checks": [check.to_dict() for check in self.checks],
        }
        if self.skipped:
            payload["skip_reason"] = self.skip_reason or "显式跳过"
        return payload


def all_blocked(
    specs: Sequence[CheckSpec], code: str, message: str
) -> list[CheckResult]:
    """Mark every check of a layer BLOCKED (fail closed, never PASS)."""

    return [
        CheckResult(
            id=spec.id,
            name=spec.name,
            status=BLOCKED,
            code=code,
            message=message,
        )
        for spec in specs
    ]


def run_checks(
    entries: Sequence[tuple[CheckSpec, Callable[[Any], Mapping[str, Any] | None]]],
    context: Any,
) -> list[CheckResult]:
    """Run checks in order, turning exceptions into typed results.

    A check function returns an optional ``detail`` mapping. ``SmokeFailure``
    means FAIL; ``SmokeSkip`` means SKIP; any other exception is an unexpected
    tool error and is reported as FAIL with a stable code so a crash never
    looks like a pass.
    """

    results: list[CheckResult] = []
    for spec, function in entries:
        started = time.perf_counter()
        try:
            detail = function(context) or {}
            result = CheckResult(
                id=spec.id,
                name=spec.name,
                status=PASS,
                detail=dict(detail),
            )
        except SmokeFailure as error:
            result = CheckResult(
                id=spec.id,
                name=spec.name,
                status=FAIL,
                code=error.code,
                message=error.message,
                detail=error.detail,
            )
        except SmokeSkip as error:
            result = CheckResult(
                id=spec.id,
                name=spec.name,
                status=SKIP,
                code=error.code,
                message=error.message,
            )
        except Exception as error:  # noqa: BLE001 - one check must not kill the run
            result = CheckResult(
                id=spec.id,
                name=spec.name,
                status=FAIL,
                code="UNEXPECTED_CHECK_ERROR",
                message=f"{type(error).__name__}: {error}",
            )
        result.duration_ms = int((time.perf_counter() - started) * 1000)
        results.append(result)
    return results


def overall_status(layers: Sequence[LayerResult]) -> str:
    if any(layer.status == FAIL for layer in layers):
        return FAIL
    if any(layer.status == BLOCKED for layer in layers):
        return BLOCKED
    if layers and all(layer.status == SKIP for layer in layers):
        return SKIP
    return PASS


def exit_code(layers: Sequence[LayerResult]) -> int:
    return 0 if overall_status(layers) in (PASS, SKIP) else 1
