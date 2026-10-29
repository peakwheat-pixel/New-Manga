"""Region persistence contract consumed by the editing use cases.

Consumer-side protocol (TASK-008 allowance excludes src/ports and
src/infrastructure); the SQLite adapter lands in a later slice. Fakes in
tests exercise the contract, including simulated restarts.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Protocol

from domain.regions.entities import Region, RegionRevision


class RegionRepository(Protocol):
    def add_region(self, region: Region) -> None: ...

    def get_region(self, region_id: str) -> Region | None: ...

    def list_regions(self, page_id: str) -> list[Region]: ...

    def update_region(self, region: Region) -> None: ...

    def soft_delete_region(self, region_id: str) -> None: ...

    def add_revision(self, revision: RegionRevision) -> None: ...

    def list_revisions(self, region_id: str) -> list[RegionRevision]: ...

    def get_revision(
        self, region_id: str, revision_no: int
    ) -> RegionRevision | None: ...


class RegionCommitStatus(str, Enum):
    """Outcome of the atomic ``commit_region_revision`` seam (TASK-028 §4.2,
    mapping onto the TASK-002 §10 failure family)."""

    APPLIED = "applied"
    INPUT_REVISION_CHANGED = "input_revision_changed"
    LOCK_CHANGED = "lock_changed"
    DB_FAILED = "db_failed"


@dataclass(frozen=True)
class RegionCommitResult:
    status: RegionCommitStatus
    revision_no: int | None = None
    detail: str = ""


@dataclass(frozen=True)
class RegionLockSnapshot:
    """Automatic writes may carry the locks observed when the step started;
    the commit re-reads and compares them inside its transaction (D06 §89)."""

    region_locked: bool
    translation_locked: bool
    inpaint_locked: bool


class RegionRevisionCommitter(Protocol):
    """Atomic "region state + revision + current pointer" seam (TASK-028
    §4.2). Implementations must run inside one ``BEGIN IMMEDIATE``:
    re-read current, compare expected id and lock snapshot, insert the
    revision, sync the revision-owned region state, update the pointer —
    rolling everything back on mismatch or database failure.
    """

    def commit_region_revision(
        self,
        region: Region,
        revision: RegionRevision,
        *,
        expected_current_revision_id: str | None = None,
        lock_snapshot: RegionLockSnapshot | None = None,
    ) -> RegionCommitResult: ...
