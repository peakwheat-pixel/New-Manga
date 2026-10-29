"""Editing use-case failures and guarded-write outcomes (TASK-002 §10)."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class RegionNotFound(Exception):
    def __init__(self, region_id: str) -> None:
        super().__init__(f"region not found: {region_id}")
        self.region_id = region_id


class RegionRevisionNotFound(Exception):
    """A requested immutable revision does not belong to the live region."""


class RegionRevisionChanged(Exception):
    """The current revision moved since the caller read it."""


class RegionLimitExceeded(ValueError):
    """A bounded Region write input exceeded its contract limit (I3/P2-A/B).

    Subclasses ``ValueError`` so existing application callers keep their
    failure family; the wire layer maps it to INVALID_REQUEST/validation
    (never to a conflict or an internal error).
    """


class GuardStatus(str, Enum):
    """Outcome of a guarded (optimistic) automatic write, D06 §90.

    ``DB_FAILED`` (I2/P2-D) is deliberately its own status: a persistence
    fault must never masquerade as an optimistic conflict, otherwise the wire
    reports INPUT_REVISION_CHANGED (and callers may "refresh and retry") for a
    database/busy failure. Consumers map it to UNKNOWN/internal with a fixed
    safe phrase.
    """

    APPLIED = "applied"
    INPUT_REVISION_CHANGED = "input_revision_changed"
    LOCK_CHANGED = "lock_changed"
    DB_FAILED = "db_failed"


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
