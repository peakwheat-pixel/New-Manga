"""Trash use case: page-level soft delete, batch restore and controlled-only
purge (TASK-021 self-contained subset; D03 §32~34, AC-TRASH-001~004).

Invariants:

- soft delete never destroys anything: pages flip ``deleted_at`` in one
  shared timestamp per batch (same batch ⇒ same value), reader/imports hide
  soft-deleted rows through their existing filters;
- restore works **per batch** and only clears ``deleted_at`` — content,
  managed files and order metadata are untouched;
- permanent deletion (``purge_batch``) addresses **controlled data only**:
  managed page files (through the injected remover, which refuses paths
  escaping the managed root) and the page/region rows. User source files are
  never inside the managed root, so they are structurally unreachable;
- the batch ledger is a JSON manifest next to the managed data (rebuildable
  bookkeeping, no schema change).
"""

from __future__ import annotations

import json
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
    """JSON-file manifest store (one file, one ``batches`` list)."""

    def __init__(self, path: Path) -> None:
        self._path = Path(path)

    def read_manifest(self) -> dict:
        if not self._path.is_file():
            return {"batches": []}
        return json.loads(self._path.read_text(encoding="utf-8"))

    def write_manifest(self, manifest: dict) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
        )


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

    def restore_batch(self, batch_id: str) -> int:
        """Restore every page of the batch (同 batch 恢复); the batch record
        is removed once all its pages are live again."""
        batch, _remaining = self._take_batch(batch_id)
        restored = self._pages.restore_pages(batch.page_ids)
        self._drop_batch(batch_id)
        return restored

    def purge_batch(self, batch_id: str) -> None:
        """Permanently delete the batch: managed page files first (controlled
        copies only), then the rows. User source files are outside the
        managed root and structurally unreachable."""
        batch, _remaining = self._take_batch(batch_id)
        pages = self._pages.get_pages_by_ids(list(batch.page_ids))
        for page in pages:
            if page.managed_original_ref:
                self._remover.remove_managed(page.managed_original_ref)
        self._pages.purge_pages(list(batch.page_ids))
        self._drop_batch(batch_id)

    # ------------------------------------------------------------------

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
        raise KeyError(f"unknown trash batch: {batch_id!r}")

    def _drop_batch(self, batch_id: str) -> None:
        manifest = self._manifest.read_manifest()
        manifest["batches"] = [
            item for item in manifest.get("batches", []) if item["batch_id"] != batch_id
        ]
        self._manifest.write_manifest(manifest)
