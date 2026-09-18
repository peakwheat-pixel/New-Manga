"""Trash use case: page-level soft delete, batch restore and controlled-only
purge (TASK-021 self-contained subset; D03 §32~34, AC-TRASH-001~004).

Invariants:

- soft delete never destroys anything: pages flip ``deleted_at`` in one
  shared timestamp per batch (same batch ⇒ same value), reader/imports hide
  soft-deleted rows through their existing filters;
- restore works **per batch** and only clears ``deleted_at`` — content,
  managed files and order metadata are untouched;
- permanent deletion (``purge_batch``) addresses **controlled data only**:
  the page's managed original **and every generated asset** (artifact
  revisions, F-6) through the injected remover, which refuses paths escaping
  the managed root, plus every database row that references the pages. User
  source files are never inside the managed root, so they are structurally
  unreachable. Rows go first and files afterwards, so the database can never
  point at a file that is already gone (F-2);
- the batch ledger is a JSON manifest next to the managed data, written
  atomically. It is an *index*, not the only source of truth: ``deleted_at``
  is the batch identity in the store, so a missing or corrupt manifest
  degrades to a rebuild instead of disabling restore/purge (F-7; no schema
  change);
- the file sweep list of a purge is persisted as a ``pending_purges``
  manifest entry **before** any destructive step (TASK-053 R-04): a file
  removal failure after the rows are gone leaves a *retryable* pending
  entry instead of an undiscoverable orphan. The entry clears only when
  every file is removed; ``retry_pending_purges()`` retries (file removal
  is idempotent — already-gone files complete silently). Target-less
  pipeline runs are deliberately kept and reclaimed only through
  ``RunLedgerMaintenance.purge_targetless_runs()`` (R-03).
"""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Callable

from application.maintenance.ports import (
    PageTrashStore,
    ControlledFileRemover,
    TrashBatch,
    TrashManifestStore,
)


class _JsonTrashManifest:
    """JSON-file manifest store (one file, one ``batches`` list).

    Writes are atomic: the payload goes to a unique temp file in the same
    directory and is swapped in with ``os.replace``, so a crash mid-write
    leaves the previous manifest untouched rather than a truncated one. Reads
    tolerate a missing, unreadable or corrupt file by reporting no batches —
    the service then rebuilds the list from the store, so a damaged ledger
    never disables the feature (F-7, TASK-044).
    """

    def __init__(self, path: Path) -> None:
        self._path = Path(path)

    def read_manifest(self) -> dict:
        try:
            text = self._path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return {"batches": []}
        try:
            manifest = json.loads(text)
        except json.JSONDecodeError:
            return {"batches": []}
        if not isinstance(manifest, dict) or not isinstance(
            manifest.get("batches"), list
        ):
            return {"batches": []}
        return manifest

    def write_manifest(self, manifest: dict) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(manifest, ensure_ascii=False, indent=2)
        temp_path = self._path.with_name(f".{self._path.name}.tmp-{uuid.uuid4().hex}")
        try:
            with open(temp_path, "w", encoding="utf-8") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_path, self._path)
        except OSError:
            # the previous manifest must survive; never leave the temp behind
            try:
                temp_path.unlink()
            except OSError:
                pass
            raise


def _rebuilt_batch_id(chapter_id: str, deleted_at: str) -> str:
    """Deterministic id for a batch recovered from the store's ``deleted_at``."""
    return f"rebuilt:{chapter_id}:{deleted_at}"


class TrashService:
    """Page-level trash with batch restore and controlled-only purge."""

    def __init__(
        self,
        pages: PageTrashStore,
        remover: ControlledFileRemover,
        manifest: TrashManifestStore,
        *,
        id_factory: Callable[[], str] | None = None,
    ) -> None:
        self._pages = pages
        self._remover = remover
        self._manifest = manifest
        self._id_factory = id_factory or (lambda: uuid.uuid4().hex[:16])

    def soft_delete_pages(
        self, chapter_id: str, page_ids: tuple[str, ...] | list[str]
    ) -> TrashBatch:
        """Soft-delete the pages as one batch; the batch is recorded in the
        manifest. Raises when none of the pages was still live."""
        ids = tuple(page_ids)
        if not ids:
            raise ValueError("no pages given")
        batch_id = self._id_factory()
        # microsecond precision + collision guard: the deleted_at value *is*
        # the batch identity in the store, so two batches must never share it
        # (same-millisecond deletes would otherwise merge).
        existing = {batch.deleted_at for batch in self.list_batches()}
        deleted_at = datetime.now(timezone.utc).isoformat(timespec="microseconds")
        stamp = datetime.fromisoformat(deleted_at)
        while deleted_at in existing:
            stamp += timedelta(microseconds=1)
            deleted_at = stamp.isoformat(timespec="microseconds")
        self._pages.soft_delete_pages(ids, deleted_at)
        # R-001 (Review a9b4141): the store may skip ids that are already in
        # an *earlier* batch (its UPDATE only touches live rows). Record only
        # the ids this batch actually soft-deleted — otherwise restore/purge
        # of this batch would reach into another batch's pages.
        actually_deleted = tuple(
            page.page_id
            for page in self._pages.get_pages_by_ids(list(ids))
            if page.deleted_at == deleted_at
        )
        if not actually_deleted:
            raise ValueError("no live page matched the given ids")
        batch = TrashBatch(
            batch_id=batch_id,
            chapter_id=chapter_id,
            deleted_at=deleted_at,
            page_ids=actually_deleted,
        )
        manifest = self._manifest.read_manifest()
        manifest.setdefault("batches", []).append(
            {
                "batch_id": batch.batch_id,
                "chapter_id": batch.chapter_id,
                "deleted_at": batch.deleted_at,
                "page_ids": list(batch.page_ids),
            }
        )
        self._manifest.write_manifest(manifest)
        return batch

    def list_batches(self) -> list[TrashBatch]:
        """Ledger batches plus any batch rebuilt from the store.

        A soft-delete group that the manifest does not know about (lost,
        truncated or corrupt ledger) is reported with a deterministic
        ``rebuilt:…`` id, so restore and purge keep working (F-7, TASK-044).
        """
        batches = self._manifest_batches()
        known = {(batch.chapter_id, batch.deleted_at) for batch in batches}
        rebuilt = [
            TrashBatch(
                batch_id=_rebuilt_batch_id(chapter_id, deleted_at),
                chapter_id=chapter_id,
                deleted_at=deleted_at,
                page_ids=page_ids,
            )
            for chapter_id, deleted_at, page_ids in self._pages.list_trashed_page_groups()
            if (chapter_id, deleted_at) not in known
        ]
        return batches + rebuilt

    def restore_batch(self, batch_id: str) -> int:
        """Restore every page of the batch (同 batch 恢复); the batch record
        is removed once all its pages are live again."""
        batch, _remaining = self._take_batch(batch_id)
        restored = self._pages.restore_pages(batch.page_ids)
        self._drop_batch(batch_id)
        return restored

    def purge_batch(self, batch_id: str) -> None:
        """Permanently delete the batch: rows first, then the managed files.

        The database rows go in **one transaction** and only after that
        succeeds are the files removed — the managed original plus every
        generated asset of those pages (F-6). A file that cannot be removed
        (including any path escaping the managed root, which the remover
        refuses) raises, leaving a diagnosable orphan file rather than a row
        pointing at something that is already gone. User source files are
        outside the managed root and structurally unreachable.

        Before any row is deleted the file list is persisted into the
        manifest as a **pending purge** entry (TASK-053 R-04): if file
        removal fails, the batch record is already gone, so without the
        pending entry the orphan could never be rediscovered. The entry is
        cleared only after every file was removed (or was already gone);
        :meth:`retry_pending_purges` retries failed entries.
        """
        batch, _remaining = self._take_batch(batch_id)
        pages = self._pages.get_pages_by_ids(list(batch.page_ids))
        targets: list[str] = [
            page.managed_original_ref
            for page in pages
            if page.managed_original_ref
        ]
        targets.extend(self._pages.list_generated_asset_paths(list(batch.page_ids)))
        unique_targets = list(dict.fromkeys(targets))
        self._record_pending_purge(batch_id, unique_targets)
        self._pages.purge_pages(list(batch.page_ids))
        self._drop_batch(batch_id)
        self._remove_pending_targets(batch_id, unique_targets)

    def retry_pending_purges(self) -> int:
        """Retry every pending purge entry left by failed :meth:`purge_batch`
        runs (TASK-053 R-04). File removal is idempotent — an entry whose
        files are already gone completes silently. Each entry is cleared
        only when all of its files are removable; the first failure raises
        and leaves the remaining entries in place for another retry.
        Returns the number of entries cleared."""
        cleared = 0
        for batch_id, targets in self._pending_purges():
            self._remove_pending_targets(batch_id, targets)
            cleared += 1
        return cleared

    def pending_purge_count(self) -> int:
        """Diagnosable view: how many purge batches are awaiting file
        cleanup (R-04 makes this number reachability-recoverable)."""
        return len(self._pending_purges())

    # ------------------------------------------------------------------

    def _manifest_batches(self) -> list[TrashBatch]:
        manifest = self._manifest.read_manifest()
        return [
            TrashBatch(
                batch_id=item["batch_id"],
                chapter_id=item["chapter_id"],
                deleted_at=item["deleted_at"],
                page_ids=tuple(item["page_ids"]),
            )
            for item in manifest.get("batches", [])
        ]

    def _take_batch(self, batch_id: str) -> tuple[TrashBatch, list[dict]]:
        manifest = self._manifest.read_manifest()
        items = manifest.get("batches", [])
        for item in items:
            if item["batch_id"] == batch_id:
                batch = TrashBatch(
                    batch_id=item["batch_id"],
                    chapter_id=item["chapter_id"],
                    deleted_at=item["deleted_at"],
                    page_ids=tuple(item["page_ids"]),
                )
                remaining = [item for item in items if item["batch_id"] != batch_id]
                return batch, remaining
        # not in the ledger: possibly a batch rebuilt from the store
        for batch in self.list_batches():
            if batch.batch_id == batch_id:
                return batch, list(items)
        raise KeyError(f"unknown trash batch: {batch_id!r}")

    def _drop_batch(self, batch_id: str) -> None:
        manifest = self._manifest.read_manifest()
        manifest["batches"] = [
            item for item in manifest.get("batches", []) if item["batch_id"] != batch_id
        ]
        self._manifest.write_manifest(manifest)

    # -- pending purges (TASK-053 R-04) -----------------------------------

    def _record_pending_purge(self, batch_id: str, targets: list[str]) -> None:
        """Persist the file sweep list *before* any destructive step so a
        partial file failure can always be retried."""
        manifest = self._manifest.read_manifest()
        pending = [p for p in manifest.get("pending_purges", []) if p["batch_id"] != batch_id]
        pending.append({"batch_id": batch_id, "targets": list(targets)})
        manifest["pending_purges"] = pending
        self._manifest.write_manifest(manifest)

    def _pending_purges(self) -> list[tuple[str, list[str]]]:
        manifest = self._manifest.read_manifest()
        return [
            (item["batch_id"], list(item["targets"]))
            for item in manifest.get("pending_purges", [])
        ]

    def _remove_pending_targets(self, batch_id: str, targets: list[str]) -> None:
        """Remove every file of one pending entry, then clear the entry.
        A remover failure raises *before* the entry is cleared, so the
        orphan stays discoverable and retryable."""
        for relative_path in targets:
            self._remover.remove_managed(relative_path)
        manifest = self._manifest.read_manifest()
        manifest["pending_purges"] = [
            item
            for item in manifest.get("pending_purges", [])
            if item["batch_id"] != batch_id
        ]
        self._manifest.write_manifest(manifest)
