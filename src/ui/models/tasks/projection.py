"""Single task progress projection for the workbench (TASK-013).

D06 §74~79 / §102~103 and D05 §18/§31/§32 in one place:

- one ``TaskProjection`` is built from the authoritative ``PipelineRun``;
- PageList rows and TaskProgressPanel fields both read that projection, so
  the panel can never say "completed" while the list says "running"
  (AC-PROGRESS-007, D06 不变量 11);
- page classification reuses the exact precedence the scheduler's own
  ``get_task_progress`` uses: failed > processing > blocked > completed >
  skipped > waiting (D06 §74);
- percentages use terminal/planned step units, never completed/total pages
  (D06 §75);
- button enablement follows D06 §103 / D05 §32 per run status.

Pure data + construction only: no Qt imports, so tests can assert on it
directly and the Qt model layer adapts it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Sequence

from domain.tasks.models import (
    CommandType,
    PipelineRun,
    PipelineRunStatus,
    PipelineTaskStatus,
    PlanDecision,
    StepRunStatus,
)

# Page-level status vocabulary shown on Page tiles (AC-PAGE-003) and in the
# TaskProgressPanel counts (AC-PROGRESS-002). "locked" is an overlay flag on
# a tile (is_locked role), never a replacement for the run classification.
STATUS_WAITING = "waiting"
STATUS_PROCESSING = "processing"
STATUS_COMPLETED = "completed"
STATUS_FAILED = "failed"
STATUS_SKIPPED = "skipped"
STATUS_BLOCKED = "blocked"

_COMMAND_LABELS = {
    CommandType.TRANSLATE_ALL: "全部翻译",
    CommandType.TRANSLATE_UNTRANSLATED: "全部翻译（跳过已翻译）",
    CommandType.TRANSLATE_SELECTED: "翻译所选",
    CommandType.TRANSLATE_SINGLE: "翻译单页",
    CommandType.RERENDER_ALL: "重新渲染（全部）",
    CommandType.RERENDER_SELECTED: "重新渲染（所选）",
    CommandType.RERENDER_SINGLE: "重新渲染（单页）",
    CommandType.REINPAINT_ALL: "重新修复（全部）",
    CommandType.REINPAINT_SELECTED: "重新修复（所选）",
    CommandType.REINPAINT_SINGLE: "重新修复（单页）",
    CommandType.REOCR_ALL: "重新 OCR（全部）",
    CommandType.REOCR_SELECTED: "重新 OCR（所选）",
    CommandType.REOCR_SINGLE: "重新 OCR（单页）",
    CommandType.OCR_REGION: "OCR Region",
    CommandType.RETRANSLATE_REGION: "重新翻译 Region",
    CommandType.RETRANSLATE_REGION_FULL: "Region 重全翻译",
    CommandType.REINPAINT_REGION: "重新修复 Region",
    CommandType.RERENDER_REGION: "重新渲染 Region",
}

_STEP_LABELS = {
    "detect": "检测",
    "ocr": "OCR",
    "color": "配色",
    "term_extract": "术语",
    "translate": "翻译",
    "segment": "分割",
    "mask_refine": "掩膜",
    "inpaint": "修复",
    "render": "渲染",
}

_STEP_ORDER = tuple(_STEP_LABELS)


@dataclass(frozen=True)
class PageProjectionRow:
    """One Page tile row; status comes from the run, never from the tile."""

    page_id: str
    page_order: int
    filename: str
    status: str
    is_locked: bool = False
    is_pipeline_current: bool = False
    error_code: str | None = None


@dataclass(frozen=True)
class TaskProjection:
    run_id: str
    run_status: str
    run_title: str
    overall_progress: float  # 0.0..1.0, terminal/planned step units (D06 §75)
    current_page_id: str | None
    current_step_type: str
    step_flow: tuple[tuple[str, str, str], ...] = ()  # (type, label, state)
    rows: tuple[PageProjectionRow, ...] = ()
    total_page_count: int = 0
    completed_page_count: int = 0
    failed_page_count: int = 0
    skipped_page_count: int = 0
    blocked_page_count: int = 0
    waiting_page_count: int = 0
    processing_page_count: int = 0
    blocked_reasons: tuple[str, ...] = ()
    can_pause: bool = False
    can_stop: bool = False
    can_continue: bool = False
    can_restart: bool = False
    can_abandon: bool = False
    can_retry_failed: bool = False
    extra: Mapping[str, str] = field(default_factory=dict)

    @property
    def progress_percent(self) -> int:
        return round(self.overall_progress * 100)

    @property
    def has_failures(self) -> bool:
        return self.failed_page_count > 0

    @property
    def is_terminal(self) -> bool:
        return self.run_status in _TERMINAL_STATUSES


_TERMINAL_STATUSES = frozenset(
    status.value
    for status in (
        PipelineRunStatus.COMPLETED,
        PipelineRunStatus.COMPLETED_WITH_FAILURES,
        PipelineRunStatus.FAILED,
        PipelineRunStatus.CANCELLED,
    )
)


def command_label(command: CommandType | str) -> str:
    return _COMMAND_LABELS.get(CommandType(command), str(command))


def step_label(step_type: str) -> str:
    return _STEP_LABELS.get(step_type, step_type)


def run_title(run: PipelineRun) -> str:
    """“第 12 话 · 全部翻译（跳过已翻译）”-style title (D05 §31.2)."""

    return command_label(run.command_type)


def build_projection(
    run: PipelineRun,
    page_meta: Mapping[str, tuple[int, str, bool]] | None = None,
) -> TaskProjection:
    """Project one run onto page rows + panel fields.

    ``page_meta`` maps page_id → (page_order, filename, locked) and comes
    from the chapter page catalog; targets missing from it fall back to run
    ordering so projection never crashes on partial catalogs.
    """

    meta = dict(page_meta or {})
    ordered_tasks = sorted(
        run.tasks,
        key=lambda task: int(task.task_id.rsplit(":", 1)[-1] or 0),
    )
    # pages missing from the catalog fall back to 1-based run target order
    # so the projection never crashes on partial metadata (D06 §74 view)
    fallback_order = {
        task.page_id: index + 1 for index, task in enumerate(ordered_tasks)
    }

    by_page: dict[str, list] = {}
    for task in ordered_tasks:
        by_page.setdefault(task.page_id, []).append(task)

    current_page_id, current_step_type = _primary_focus(ordered_tasks, run)

    rows: list[PageProjectionRow] = []
    counts = {key: 0 for key in (
        STATUS_COMPLETED, STATUS_FAILED, STATUS_SKIPPED,
        STATUS_BLOCKED, STATUS_WAITING, STATUS_PROCESSING,
    )}
    for page_id, tasks in by_page.items():
        order, filename, locked = meta.get(
            page_id, (fallback_order.get(page_id, 0), page_id, False)
        )
        status, error_code = _classify_page(tasks)
        counts[status] += 1
        rows.append(
            PageProjectionRow(
                page_id=page_id,
                page_order=order,
                filename=filename,
                status=status,
                is_locked=locked,
                is_pipeline_current=page_id == current_page_id,
                error_code=error_code,
            )
        )
    rows.sort(key=lambda row: (row.page_order, row.page_id))

    reasons: list[str] = []
    for task in ordered_tasks:
        if task.status is PipelineTaskStatus.BLOCKED and task.error_code:
            if task.error_code not in reasons:
                reasons.append(task.error_code)

    return TaskProjection(
        run_id=run.run_id,
        run_status=run.status.value,
        run_title=f"{run_title(run)}",
        overall_progress=(
            run.terminal_step_units / run.planned_step_units
            if run.planned_step_units
            else 0.0
        ),
        current_page_id=current_page_id,
        current_step_type=current_step_type,
        step_flow=_step_flow(run),
        rows=tuple(rows),
        total_page_count=len(rows),
        completed_page_count=counts[STATUS_COMPLETED],
        failed_page_count=counts[STATUS_FAILED],
        skipped_page_count=counts[STATUS_SKIPPED],
        blocked_page_count=counts[STATUS_BLOCKED],
        waiting_page_count=counts[STATUS_WAITING],
        processing_page_count=counts[STATUS_PROCESSING],
        blocked_reasons=tuple(reasons),
        **_button_enablement(run.status, counts[STATUS_FAILED] > 0),
    )


def _classify_page(tasks: Sequence) -> tuple[str, str | None]:
    """Same precedence as PipelineService.get_task_progress (D06 §74)."""

    statuses = {task.status for task in tasks}
    if PipelineTaskStatus.FAILED in statuses:
        failed = next(task for task in tasks if task.status is PipelineTaskStatus.FAILED)
        return STATUS_FAILED, failed.error_code
    if PipelineTaskStatus.RUNNING in statuses:
        return STATUS_PROCESSING, None
    if PipelineTaskStatus.BLOCKED in statuses:
        blocked = next(task for task in tasks if task.status is PipelineTaskStatus.BLOCKED)
        return STATUS_BLOCKED, blocked.error_code
    if statuses and statuses <= {PipelineTaskStatus.COMPLETED}:
        return STATUS_COMPLETED, None
    if statuses and statuses <= {PipelineTaskStatus.SKIPPED}:
        return STATUS_SKIPPED, None
    return STATUS_WAITING, None


def _primary_focus(tasks: Sequence, run: PipelineRun) -> tuple[str | None, str]:
    """D06 §77/§78: first running task by target order shows the primary
    focus page and its running step; when nothing runs (paused, terminal)
    the most recent step run keeps the last focus visible."""

    for task in tasks:
        if task.status is PipelineTaskStatus.RUNNING:
            running_step = next(
                (
                    step.step_type
                    for step in reversed(run.step_runs)
                    if step.task_id == task.task_id
                    and step.status is StepRunStatus.RUNNING
                ),
                "",
            )
            return task.page_id, running_step
    if run.step_runs:
        return run.step_runs[-1].page_id, ""
    return None, ""


def _step_flow(run: PipelineRun) -> tuple[tuple[str, str, str], ...]:
    """Per-step aggregate state for the D05 §31.2 flow strip.

    The command's step sequence is read off the first planned task's units
    (every task plans the full command sequence in order).
    """

    command_steps: tuple[str, ...] = tuple(
        unit.step_type for unit in run.tasks[0].units
    ) if run.tasks else ()
    flow: list[tuple[str, str, str]] = []
    for step_type in command_steps:
        units = [
            unit
            for task in run.tasks
            for unit in task.units
            if unit.step_type == step_type
        ]
        step_runs = [step for step in run.step_runs if step.step_type == step_type]
        flow.append((step_type, step_label(step_type), _flow_state(units, step_runs)))
    return tuple(flow)


def _flow_state(units: Sequence, step_runs: Sequence) -> str:
    if any(step.status is StepRunStatus.FAILED for step in step_runs):
        return "failed"
    if any(step.status is StepRunStatus.RUNNING for step in step_runs):
        return "running"
    if not units:
        return "pending"
    if all(unit.decision.is_terminal for unit in units):
        if all(
            unit.decision in {PlanDecision.SKIP_LOCK, PlanDecision.SKIP_POLICY}
            for unit in units
        ):
            return "skipped"
        return "completed"
    return "pending"


def _button_enablement(status: PipelineRunStatus, has_failures: bool) -> dict:
    """D06 §103 / D05 §32 button matrix, including stop-from-blocked."""

    running = {PipelineRunStatus.PENDING, PipelineRunStatus.RUNNING}
    if status in running:
        return dict(can_pause=True, can_stop=True)
    if status is PipelineRunStatus.PAUSED:
        return dict(can_stop=True, can_continue=True)
    if status is PipelineRunStatus.BLOCKED:
        return dict(can_stop=True)
    if status is PipelineRunStatus.INTERRUPTED:
        return dict(can_continue=True, can_restart=True, can_abandon=True)
    enabled: dict = {}
    if status is PipelineRunStatus.COMPLETED_WITH_FAILURES and has_failures:
        enabled["can_retry_failed"] = True
    return enabled
