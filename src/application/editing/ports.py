"""Region persistence contract consumed by the editing use cases.

Consumer-side protocol (TASK-008 allowance excludes src/ports and
src/infrastructure); the SQLite adapter lands in a later slice. Fakes in
tests exercise the contract, including simulated restarts.
"""

from __future__ import annotations

from dataclasses import dataclass
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

    def commit_region_batch(
        self,
        *,
        new_regions: "Sequence[tuple[Region, RegionRevision]]" = (),
        updated_regions: "Sequence[tuple[Region, RegionRevision, str | None]]" = (),
        soft_delete_region_ids: "Sequence[tuple[str, str | None]]" = (),
        revision_pins: "Sequence[tuple[str, int, bool]]" = (),
        expected_current_checks: "Sequence[tuple[str, str]]" = (),
    ) -> RegionCommitResult:
        """V11R-F0-1 I1: ALL-OR-NOTHING composite write for the Region face.

        One ``BEGIN IMMEDIATE`` transaction performs, in order:

        1. re-read the current pointer of EVERY region named by
           ``soft_delete_region_ids`` / ``updated_regions`` / any
           ``expected_current_checks`` entry and compare it with the caller's
           expected revision id (a mismatch rolls back with
           ``INPUT_REVISION_CHANGED`` and ZERO write);
        2. insert every ``(region, revision)`` of ``new_regions`` together
           with revision_no=1 and the current pointer (a region can never be
           persisted without its first revision/current pointer);
        3. append the next revision of every ``updated_regions`` entry, sync
           the revision-owned region state and move the pointer;
        4. soft-delete every ``soft_delete_region_ids`` region (source rows of
           merge/split) — never hard delete, history stays addressable;
        5. flip ``is_pinned`` for ``revision_pins`` (revision rows are
           immutable; the target revision existence is the caller's
           race-free pre-check because history is append-only);
        6. commit only when every step succeeded; any exception rolls the
           whole transaction back and returns ``DB_FAILED``.

        This is the seam the create/merge/split/reorder/delete/pin use cases
        call so a failure can never leave a partial state (orphan region,
        merged-with-live-sources, half split parts, partially reordered
        reading order, a delete/pin past a changed current pointer).
        """
