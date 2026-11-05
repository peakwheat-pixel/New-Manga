"""Contracts for the maintenance/trash use case (TASK-021 subset + FEA-12).

The subset covers page-level soft delete, batch restore and controlled-only
purge. Files addressed through :class:`ControlledFileRemover` live inside the
managed root; **user source files are never inside it**, so a purge can
never reach them — the type boundary is the AC guarantee.

FEA-12 (C-09 SC-B04a / ADJ-001 PD-10): the same :class:`ProtectionPolicy`
verdict decides the three delete paths (application trash soft delete,
automatic cleanup, explicit permanent delete).  The policy is a pure
application-layer function over plain facts — it imports no infrastructure and
writes nothing; each path supplies the facts it can observe and adapts the
verdict to its own typed surface.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Protocol

from domain.pages.entities import Page


@dataclass(frozen=True)
class TrashBatch:
    """One soft-delete batch: the unit of restore and of permanent deletion."""

    batch_id: str
    chapter_id: str
    deleted_at: str
    page_ids: tuple[str, ...]


class PageTrashStore(Protocol):
    """The repository slice the trash use case needs (consumer-side)."""

    def get_pages_by_ids(self, page_ids) -> list[Page]: ...

    def soft_delete_pages(self, page_ids, deleted_at: str) -> int: ...

    def restore_pages(self, page_ids) -> int: ...

    def purge_pages(self, page_ids) -> None:
        """Hard-delete the pages in **one transaction**, together with every
        row that references them (the caller handles managed files).

        Implementations must delete the whole foreign-key closure — a page with
        artifact or pipeline rows included — in child-before-parent order, with
        foreign-key enforcement left on (F-2, TASK-044).
        """
        ...

    def list_generated_asset_paths(self, page_ids) -> list[str]:
        """Managed paths of every **generated asset** belonging to these pages
        (artifact revisions), for the permanent-delete file sweep (F-6)."""
        ...

    def list_live_managed_refs(self, refs) -> set[str]:
        """Which of the given managed paths are still referenced by a **live
        page row** (soft-deleted counts as live — the row exists).

        TASK-060 Q-007 ③: row-liveness guard for pending purge retries —
        a pending entry whose targets a live row still references must
        never be swept, even when the batch identity is unrecoverable
        (lost ledger) and cannot be matched by id.
        """
        ...

    def list_trashed_page_groups(self) -> list[tuple[str, str, tuple[str, ...]]]:
        """``(chapter_id, deleted_at, page_ids)`` for each soft-deleted group.

        ``deleted_at`` is the batch identity in the store, which makes the
        batch list derivable from the database when the JSON ledger is missing
        or corrupt (F-7).
        """
        ...


class ControlledFileRemover(Protocol):
    """Removes one **managed (controlled)** file; must refuse paths escaping
    the managed root (production: ``ManagedFileStorage.remove_managed``)."""

    def remove_managed(self, relative_path: str) -> None: ...


class TrashManifestStore(Protocol):
    """Persists batch records next to the controlled data."""

    def read_manifest(self) -> dict: ...

    def write_manifest(self, manifest: dict) -> None: ...


class RunLedgerMaintenance(Protocol):
    """Maintenance seam for the persisted pipeline-run ledger (TASK-053
    R-03: runs are deliberately **kept** after every target page is
    purged — a run spans pages, so cascading it away would destroy
    audit history other pages still share. Target-less runs stay
    visible and reclaimable through this port instead of being
    silently dropped by page deletion."""

    def count_targetless_runs(self) -> int:
        """Number of persisted runs whose every target row is gone."""
        ...

    def purge_targetless_runs(self) -> int:
        """Delete every non-active target-less run; returns the count
        removed. Active runs (running/paused) are always kept: they may
        still be referenced by the recovery path even with no tasks."""
        ...


# ----------------------------------------------------------------------
# FEA-12 / C-09 SC-B04a: one ProtectionPolicy for the three delete paths
# ----------------------------------------------------------------------


class ProtectionScope(str, Enum):
    """The three delete paths that must share one protection verdict.

    ADJ-001 §3 forbids conflating them: the same protection facts have a
    different consequence per path (soft delete never blocks, automatic
    cleanup refuses to destroy human work, explicit permanent delete
    *discloses* and requires the dedicated confirmation instead of
    blocking).
    """

    SOFT_DELETE = "soft_delete"
    AUTO_CLEANUP = "auto_cleanup"
    PERMANENT_DELETE = "permanent_delete"


#: Stable, path-free reason codes for a blocked verdict.  They are the only
#: reason vocabulary the policy emits (host projections must never forward
#: free text).
PROTECTION_REASON_LOCK = "PROTECTED_LOCK"
PROTECTION_REASON_MANUAL = "PROTECTED_MANUAL_EDIT"
PROTECTION_REASON_REVISION = "PROTECTED_REVISION"
PROTECTION_REASON_DRAFT = "PROTECTED_ACTIVE_DRAFT"
PROTECTION_REASON_BUSY = "BOOK_BUSY"
PROTECTION_REASON_SHARED_UNSAFE = "BOOK_DELETE_CONFLICT"


@dataclass(frozen=True)
class ProtectionFacts:
    """The observable protection inventory of one target scope.

    Amounts are counts, never paths or book text: the policy is a decision
    function, the PD-01 disclosure detail is built by the preview face from
    its own authoritative Core computation.
    """

    lock_count: int = 0
    manual_region_count: int = 0
    current_revision_count: int = 0
    pinned_revision_count: int = 0
    draft_page_count: int = 0
    active_run_count: int = 0
    active_export_count: int = 0
    #: Shared references that cannot be split safely (out-of-target rows that
    #: a delete would have to corrupt instead of detach).  PD-08: only these
    #: are a conflict; safely splittable sharing is *not* a block.
    unsafe_shared_ref_count: int = 0


@dataclass(frozen=True)
class ProtectionVerdict:
    """``{blocked, reasons[]}`` — the shared shape of every delete path."""

    scope: ProtectionScope
    blocked: bool
    reasons: tuple[str, ...] = ()

    @property
    def disclosure_required(self) -> bool:
        """PD-01/PD-02: the permanent-delete path must disclose and require
        the dedicated confirmation whenever protected content is destroyed.

        This is *not* a block: ADJ-001 PD-01 explicitly keeps disclosure
        non-blocking (a book with locks/manual edits must stay deletable
        after the dedicated confirmation).
        """
        return self.scope is ProtectionScope.PERMANENT_DELETE and bool(self.reasons)


class ProtectionPolicy:
    """The single protection judgement shared by A/B/C (C-09 SC-B04a).

    ``ProtectionPolicy.evaluate(scope, facts) -> {blocked, reasons[]}``.
    No path implements its own rule table; callers only translate the
    verdict into their own typed surface.
    """

    @staticmethod
    def evaluate(
        scope: ProtectionScope
        | str, facts: ProtectionFacts
    ) -> ProtectionVerdict:
        scope = ProtectionScope(scope)
        if scope is ProtectionScope.SOFT_DELETE:
            # ADJ-001 §3 A: soft delete preserves every protection datum; it
            # must never unlock, unpin or rewrite anything, and therefore no
            # protection fact blocks it.
            return ProtectionVerdict(scope, blocked=False)
        if scope is ProtectionScope.AUTO_CLEANUP:
            # C-09 SC-B04a: automatic cleanup never destroys human work or
            # recoverable revisions; it refuses instead of silently
            # unlocking.  Drafts are protected here too (they are the
            # in-flight human edits).
            reasons: list[str] = []
            if facts.lock_count > 0:
                reasons.append(PROTECTION_REASON_LOCK)
            if facts.manual_region_count > 0:
                reasons.append(PROTECTION_REASON_MANUAL)
            if facts.current_revision_count > 0 or facts.pinned_revision_count > 0:
                reasons.append(PROTECTION_REASON_REVISION)
            if facts.draft_page_count > 0:
                reasons.append(PROTECTION_REASON_DRAFT)
            return ProtectionVerdict(scope, blocked=bool(reasons), reasons=tuple(reasons))
        # Explicit permanent delete (C flow): disclosure is non-blocking, the
        # only hard blocker is an active operation (ADJ-001 PD-01 /
        # M2-C1 §5.11.3 BOOK_BUSY), plus genuinely unsplittable shared state
        # (PD-08 fail-closed).
        reasons = []
        if (
            facts.active_run_count > 0
            or facts.active_export_count > 0
        ):
            reasons.append(PROTECTION_REASON_BUSY)
        if facts.unsafe_shared_ref_count > 0:
            reasons.append(PROTECTION_REASON_SHARED_UNSAFE)
        if facts.lock_count > 0:
            reasons.append(PROTECTION_REASON_LOCK)
        if facts.manual_region_count > 0:
            reasons.append(PROTECTION_REASON_MANUAL)
        if facts.current_revision_count > 0 or facts.pinned_revision_count > 0:
            reasons.append(PROTECTION_REASON_REVISION)
        if facts.draft_page_count > 0:
            reasons.append(PROTECTION_REASON_DRAFT)
        blocked_reasons = tuple(
            reason
            for reason in reasons
            if reason in (PROTECTION_REASON_BUSY, PROTECTION_REASON_SHARED_UNSAFE)
        )
        return ProtectionVerdict(scope, blocked=bool(blocked_reasons), reasons=reasons)
