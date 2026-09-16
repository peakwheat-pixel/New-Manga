"""Pure command-scheduling records (TASK-002 §1/§5, TASK-011).

The module deliberately contains no persistence, Qt, network, or provider
imports.  A run owns immutable target and configuration snapshots; mutable
execution state is kept separately by the application store.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping


def _freeze(value: Any) -> Any:
    """Recursively freeze JSON-like values used by run snapshots."""

    if isinstance(value, Mapping):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, tuple):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, set):
        return frozenset(_freeze(item) for item in value)
    return value


def _clone(value: Any) -> Any:
    """Copy JSON-like values without asking deepcopy to pickle mappingproxy."""

    if isinstance(value, Mapping):
        return {key: _clone(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_clone(item) for item in value]
    if isinstance(value, tuple):
        return tuple(_clone(item) for item in value)
    if isinstance(value, set):
        return {_clone(item) for item in value}
    return deepcopy(value)


def freeze_snapshot(value: Mapping[str, Any] | None) -> Mapping[str, Any]:
    """Return a recursively immutable copy of a snapshot mapping."""

    return _freeze(_clone(dict(value or {})))


class ScopeType(str, Enum):
    BOOK = "book"
    CHAPTER = "chapter"
    PAGE_SELECTION = "page_selection"
    PAGE = "page"
    REGION = "region"


class TargetType(str, Enum):
    PAGE = "page"
    REGION = "region"


class CommandType(str, Enum):
    TRANSLATE_ALL = "translate_all"
    TRANSLATE_UNTRANSLATED = "translate_untranslated"
    TRANSLATE_SELECTED = "translate_selected"
    TRANSLATE_SINGLE = "translate_single"
    RERENDER_ALL = "rerender_all"
    RERENDER_SELECTED = "rerender_selected"
    RERENDER_SINGLE = "rerender_single"
    REINPAINT_ALL = "reinpaint_all"
    REINPAINT_SELECTED = "reinpaint_selected"
    REINPAINT_SINGLE = "reinpaint_single"
    REOCR_ALL = "reocr_all"
    REOCR_SELECTED = "reocr_selected"
    REOCR_SINGLE = "reocr_single"
    OCR_REGION = "ocr_region"
    RETRANSLATE_REGION = "retranslate_region"
    RETRANSLATE_REGION_FULL = "retranslate_region_full"
    REINPAINT_REGION = "reinpaint_region"
    RERENDER_REGION = "rerender_region"


COMMAND_CATALOG = tuple(command.value for command in CommandType)


class PipelineRunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    COMPLETED_WITH_FAILURES = "completed_with_failures"
    FAILED = "failed"
    CANCELLED = "cancelled"
    INTERRUPTED = "interrupted"


class PipelineTaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"
    INTERRUPTED = "interrupted"


class StepRunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    INTERRUPTED = "interrupted"


class PlanDecision(str, Enum):
    RUN = "run"
    SKIP_VALID = "skip_valid"
    SKIP_LOCK = "skip_lock"
    SKIP_POLICY = "skip_policy"
    BLOCKED = "blocked"

    @property
    def is_terminal(self) -> bool:
        return self is not PlanDecision.RUN and self is not PlanDecision.BLOCKED


class StageState(str, Enum):
    NOT_STARTED = "not_started"
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    STALE = "stale"
    FAILED = "failed"
    SKIPPED = "skipped"
    INTERRUPTED = "interrupted"
    CANCELLED = "cancelled"

    @property
    def is_valid(self) -> bool:
        return self is StageState.COMPLETED


class PipelineError(ValueError):
    """A contract error with a stable TASK-002 error code."""

    def __init__(self, code: str, detail: str = "") -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}" if detail else code)


@dataclass(frozen=True)
class PipelineScope:
    scope_type: ScopeType | str
    selected_ids: tuple[str, ...] = ()
    book_id: str | None = None
    chapter_id: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "scope_type", ScopeType(self.scope_type))
        object.__setattr__(self, "selected_ids", tuple(self.selected_ids))


@dataclass(frozen=True)
class LockSnapshot:
    page_locked: bool = False
    region_locked: bool = False
    translation_locked: bool = False
    inpaint_locked: bool = False


@dataclass(frozen=True)
class RegionSnapshot:
    region_id: str
    page_id: str
    region_type: str = "speech"
    sfx_policy: str = "translate"
    lock: LockSnapshot = field(default_factory=LockSnapshot)
    manual_edited: bool = False
    final_confirmed: bool = False
    current_revisions: Mapping[str, str | None] = field(default_factory=dict)
    stage_states: Mapping[str, StageState | str] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.region_id or not self.page_id:
            raise ValueError("region snapshot requires region_id and page_id")
        object.__setattr__(self, "lock", self.lock if isinstance(self.lock, LockSnapshot) else LockSnapshot(**self.lock))
        object.__setattr__(
            self,
            "current_revisions",
            MappingProxyType(dict(_clone(dict(self.current_revisions)))),
        )
        object.__setattr__(
            self,
            "stage_states",
            MappingProxyType(
                {key: StageState(value) for key, value in self.stage_states.items()}
            ),
        )
        object.__setattr__(self, "metadata", freeze_snapshot(self.metadata))

    def stage(self, step_type: str) -> StageState:
        return self.stage_states.get(step_type, StageState.NOT_STARTED)


@dataclass(frozen=True)
class TargetSnapshot:
    """A current target view captured before a Run becomes pending."""

    target_id: str
    page_id: str
    target_type: TargetType | str
    page_order: int = 0
    book_id: str | None = None
    chapter_id: str | None = None
    region_id: str | None = None
    lock: LockSnapshot = field(default_factory=LockSnapshot)
    manual_edited: bool = False
    final_confirmed: bool = False
    current_revisions: Mapping[str, str | None] = field(default_factory=dict)
    stage_states: Mapping[str, StageState | str] = field(default_factory=dict)
    regions: tuple[RegionSnapshot, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)
    deleted: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "target_type", TargetType(self.target_type))
        if not self.target_id or not self.page_id:
            raise ValueError("target snapshot requires target_id and page_id")
        if self.target_type is TargetType.REGION and not self.region_id:
            raise ValueError("region target requires region_id")
        object.__setattr__(self, "lock", self.lock if isinstance(self.lock, LockSnapshot) else LockSnapshot(**self.lock))
        object.__setattr__(
            self,
            "current_revisions",
            MappingProxyType(dict(_clone(dict(self.current_revisions)))),
        )
        object.__setattr__(
            self,
            "stage_states",
            MappingProxyType(
                {key: StageState(value) for key, value in self.stage_states.items()}
            ),
        )
        object.__setattr__(self, "regions", tuple(self.regions))
        object.__setattr__(self, "metadata", freeze_snapshot(self.metadata))

    def stage(self, step_type: str) -> StageState:
        return self.stage_states.get(step_type, StageState.NOT_STARTED)

    def region_snapshots(self) -> tuple[RegionSnapshot, ...]:
        if self.target_type is TargetType.REGION:
            return tuple(
                region
                for region in self.regions
                if region.region_id == self.region_id
            ) or (
                RegionSnapshot(
                    region_id=self.region_id or self.target_id,
                    page_id=self.page_id,
                    lock=self.lock,
                    manual_edited=self.manual_edited,
                    final_confirmed=self.final_confirmed,
                    current_revisions=self.current_revisions,
                    stage_states=self.stage_states,
                    metadata=self.metadata,
                ),
            )
        return self.regions


@dataclass(frozen=True)
class RunTarget:
    run_target_id: str
    target_id: str
    target_type: TargetType
    page_id: str
    region_id: str | None
    target_order: int
    snapshot: TargetSnapshot


@dataclass(frozen=True)
class PlanUnit:
    unit_id: str
    task_id: str
    target_id: str
    page_id: str
    region_id: str | None
    step_type: str
    decision: PlanDecision
    reason: str | None = None
    expected_revisions: Mapping[str, str | None] = field(default_factory=dict)
    expected_lock: LockSnapshot = field(default_factory=LockSnapshot)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "expected_revisions",
            MappingProxyType(dict(self.expected_revisions)),
        )


@dataclass
class PipelineTask:
    task_id: str
    run_target_id: str
    target_id: str
    target_type: TargetType
    page_id: str
    region_id: str | None
    status: PipelineTaskStatus = PipelineTaskStatus.PENDING
    units: tuple[PlanUnit, ...] = ()
    step_run_ids: list[str] = field(default_factory=list)
    error_code: str | None = None
    error_detail: str | None = None


@dataclass
class StepRun:
    step_run_id: str
    task_id: str
    target_id: str
    page_id: str
    region_id: str | None
    step_type: str
    unit_id: str = ""
    status: StepRunStatus = StepRunStatus.PENDING
    input_refs: Mapping[str, str | None] = field(default_factory=dict)
    lock_snapshot: LockSnapshot = field(default_factory=LockSnapshot)
    retry_no: int = 0
    error_code: str | None = None
    error_detail: str | None = None
    output: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class StepResult:
    """Deterministic executor output; keys identify primary write targets."""

    target_id: str
    step_type: str
    outputs: Mapping[str, Any] = field(default_factory=dict)
    output_target_ids: tuple[str, ...] = ()
    revision_updates: Mapping[str, str] = field(default_factory=dict)
    next_stage_states: Mapping[str, StageState | str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "output_target_ids", tuple(self.output_target_ids))
        object.__setattr__(self, "outputs", freeze_snapshot(self.outputs))
        object.__setattr__(self, "revision_updates", MappingProxyType(dict(self.revision_updates)))
        object.__setattr__(
            self,
            "next_stage_states",
            MappingProxyType(
                {key: StageState(value) for key, value in self.next_stage_states.items()}
            ),
        )


@dataclass(frozen=True)
class StepResultCandidate:
    candidate_id: str
    step_run_id: str
    target_id: str
    page_id: str
    region_id: str | None
    result_kind: str
    base_revision_id: str | None
    payload: Mapping[str, Any]
    reason: str
    status: str = "pending"

    def __post_init__(self) -> None:
        object.__setattr__(self, "payload", freeze_snapshot(self.payload))


@dataclass
class PipelineRun:
    run_id: str
    command_type: CommandType
    scope: PipelineScope
    requested_targets: tuple[str, ...]
    targets: tuple[RunTarget, ...]
    settings_snapshot: Mapping[str, Any]
    provider_binding_snapshot: Mapping[str, Any]
    constraint_snapshot_ref: str | None
    context_policy: Mapping[str, Any]
    status: PipelineRunStatus = PipelineRunStatus.PENDING
    tasks: list[PipelineTask] = field(default_factory=list)
    step_runs: list[StepRun] = field(default_factory=list)
    candidates: list[StepResultCandidate] = field(default_factory=list)
    planned_step_units: int = 0
    terminal_step_units: int = 0
    terminal_unit_ids: set[str] = field(default_factory=set)
    pause_requested: bool = False
    cancel_requested: bool = False
    source_run_id: str | None = None
    retry_reason: str | None = None
    interruption_disposition: str | None = None
    termination_reason: str | None = None
    fatal_error: str | None = None

    def __post_init__(self) -> None:
        self.requested_targets = tuple(self.requested_targets)
        self.settings_snapshot = freeze_snapshot(self.settings_snapshot)
        self.provider_binding_snapshot = freeze_snapshot(self.provider_binding_snapshot)
        self.context_policy = freeze_snapshot(self.context_policy)


@dataclass(frozen=True)
class TaskProgressSnapshot:
    run_id: str
    run_status: PipelineRunStatus
    overall_progress: float
    planned_step_units: int
    terminal_step_units: int
    total_page_count: int
    completed_page_count: int
    failed_page_count: int
    skipped_page_count: int
    blocked_page_count: int
    waiting_page_count: int
    processing_page_count: int
    skipped_reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class ControlResult:
    run_id: str
    status: PipelineRunStatus
    new_run_id: str | None = None


TERMINAL_TASK_STATUSES = frozenset(
    {
        PipelineTaskStatus.COMPLETED,
        PipelineTaskStatus.FAILED,
        PipelineTaskStatus.SKIPPED,
        PipelineTaskStatus.CANCELLED,
    }
)

TERMINAL_STEP_STATUSES = frozenset(
    {
        StepRunStatus.COMPLETED,
        StepRunStatus.FAILED,
        StepRunStatus.CANCELLED,
    }
)
