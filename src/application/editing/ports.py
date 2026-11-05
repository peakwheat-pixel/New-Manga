"""Region persistence contract consumed by the editing use cases.

Consumer-side protocol (TASK-008 allowance excludes src/ports and
src/infrastructure); the SQLite adapter lands in a later slice. Fakes in
tests exercise the contract, including simulated restarts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Protocol, Sequence

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

    def revision_by_id(self, revision_id: str) -> RegionRevision | None: ...


class RegionCommitStatus(str, Enum):
    """Outcome of the atomic ``commit_region_revision`` seam (TASK-028 §4.2,
    mapping onto the TASK-002 §10 failure family)."""

    APPLIED = "applied"
    INPUT_REVISION_CHANGED = "input_revision_changed"
    LOCK_CHANGED = "lock_changed"
    TARGET_NOT_FOUND = "target_not_found"
    REGION_LIMIT_EXCEEDED = "region_limit_exceeded"
    STALE_BASE_REVISION = "stale_base_revision"
    DB_FAILED = "db_failed"


@dataclass(frozen=True)
class RegionCommitResult:
    status: RegionCommitStatus
    revision_no: int | None = None
    detail: str = ""
    revision_ids: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class RegionProtectionGuard:
    """Base pointer and protection digest rechecked inside BEGIN IMMEDIATE."""

    region_id: str
    base_revision_id: str
    protection_digest: str


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

    def commit_region_batch(
        self,
        *,
        new_regions: "Sequence[tuple[Region, RegionRevision]]" = (),
        updated_regions: "Sequence[tuple[Region, RegionRevision, str | None]]" = (),
        soft_delete_region_ids: "Sequence[tuple[str, str | None]]" = (),
        revision_pins: "Sequence[tuple[str, int, bool]]" = (),
        expected_current_checks: "Sequence[tuple[str, str]]" = (),
        page_region_limit: tuple[str, int] | None = None,
    ) -> RegionCommitResult:
        """Existing composite write contract; its signature stays stable."""
        ...

    def commit_region_batch_guarded(
        self,
        *,
        updated_regions: "Sequence[tuple[Region, RegionRevision, str | None]]",
        protection_guards: "Sequence[RegionProtectionGuard]",
    ) -> RegionCommitResult: ...

@dataclass(frozen=True, slots=True)
class RevisionLineage:
    """FEA-11-LINEAGE-1 AC1: native lineage committed with a region revision
    (C-17 §7.1). ``binding_id`` is the source binding the revision was captured
    against; ``provenance`` is the frozen lineage value."""

    binding_id: str | None
    provenance: str
    from_revision_id: str | None = None
    operation_id: str | None = None
