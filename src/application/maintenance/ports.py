"""Contracts for the maintenance/trash use case (TASK-021 subset).

The subset covers page-level soft delete, batch restore and controlled-only
purge. Files addressed through :class:`ControlledFileRemover` live inside the
managed root; **user source files are never inside it**, so a purge can
never reach them — the type boundary is the AC guarantee.
"""

from __future__ import annotations

from dataclasses import dataclass
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
