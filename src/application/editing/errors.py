"""Editing use-case failures and guarded-write outcomes (TASK-002 §10)."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class RegionNotFound(Exception):
    def __init__(self, region_id: str) -> None:
        super().__init__(f"region not found: {region_id}")
        self.region_id = region_id


class GuardStatus(str, Enum):
    """Outcome of a guarded (optimistic) automatic write, D06 §90."""

    APPLIED = "applied"
    INPUT_REVISION_CHANGED = "input_revision_changed"
    LOCK_CHANGED = "lock_changed"


@dataclass(frozen=True)
class GuardedWriteOutcome:
    """Result of an automatic (machine-origin) write attempt.

    On conflict the current pointer is untouched and the payload is reported
    back so the pipeline layer can persist a StepResultCandidate (the
    candidate table itself belongs to TASK-011).
    """

    status: GuardStatus
    revision_no: int | None = None
    retranslate_hint: bool = False
    detail: str = ""
    conflicts: tuple[str, ...] = field(default=())
