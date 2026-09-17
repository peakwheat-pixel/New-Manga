"""PDF/MOBI document import use case (TASK-023; D01 §2, D02 §8, D04 §8).

One document file becomes many managed pages through the **same discipline**
as the image import (reuse, no second pipeline — TASK-023 AC 1): duplicate
check → document decode (typed diagnosis) → per-page rasterisation →
Managed Copy per page → page commit strictly after the copy exists. Page
order follows document page order (source_order/sort_order append after the
chapter's current pages, D02 §8.4); per-page source hashes participate in
the same duplicate bookkeeping as image pages.

Failure / cancellation semantics mirror ``ImportImagesUseCase`` (AC 2): a
page that fails decode or copy never reaches the sink; cancellation stops
before starting the next page; already committed pages stay and the
remainder is reported as pending. Corrupt, encrypted and unsupported files
fail with typed reasons and never break previously imported data.

MOBI: no parsing dependency is approved, so non-PDF payloads fail with
``UNSUPPORTED_FORMAT`` — diagnosable, never silently ignored, never parsed
by an invented reader (AC 2; MOBI rasterisation stays BLOCKED until a
dependency is approved).
"""

from __future__ import annotations

import hashlib
import uuid
from pathlib import Path
from typing import Callable

from application.importing.documents.ports import (
    DocumentDecodeError,
    DocumentRaster,
)
from application.importing.images.ports import (
    FailedImport,
    ImportPageSink,
    ImportReport,
    ImportSource,
    ImportedPage,
    ManagedCopyStore,
)
from application.importing.images.service import DuplicatePolicy
from domain.pages.entities import Page

_PDF_MAGIC = b"%PDF-"

REASON_INVALID_DOCUMENT = "INVALID_DOCUMENT"
REASON_ENCRYPTED = "ENCRYPTED"
REASON_UNSUPPORTED_FORMAT = "UNSUPPORTED_FORMAT"
REASON_COPY_FAILED = "COPY_FAILED"
REASON_SOURCE_READ_FAILED = "SOURCE_READ_FAILED"


def _is_pdf(data: bytes) -> bool:
    return data[: len(_PDF_MAGIC)] == _PDF_MAGIC


def _page_name(source_filename: str, page_no: int) -> str:
    """Managed-copy display name for one document page (1-based, stable)."""
    stem = Path(source_filename).stem or "document"
    return f"{stem}-page-{page_no:04d}.png"


class ImportDocumentsUseCase:
    """Import document files as managed page images (TASK-023 AC 1/2)."""

    def __init__(
        self,
        raster: DocumentRaster,
        copy_store: ManagedCopyStore,
        sink: ImportPageSink,
    ) -> None:
        self._raster = raster
        self._store = copy_store
        self._sink = sink

    def import_documents(
        self,
        chapter_id: str,
        sources: list[ImportSource],
        *,
        duplicate_policy: str = DuplicatePolicy.SKIP,
        cancelled: Callable[[], bool] | None = None,
    ) -> ImportReport:
        if duplicate_policy not in (DuplicatePolicy.SKIP, DuplicatePolicy.IMPORT_AS_NEW):
            raise ValueError(f"unknown duplicate policy: {duplicate_policy}")
        is_cancelled = cancelled or (lambda: False)
        existing_hashes = self._sink.existing_source_hashes(chapter_id)
        next_order = self._sink.max_source_order(chapter_id)

        imported: list[ImportedPage] = []
        skipped: list[str] = []
        failed: list[FailedImport] = []
        pending: list[str] = []

        for source in sources:
            if is_cancelled():
                pending.append(source.filename)
                continue
            try:
                data = source.read()
            except OSError as error:
                failed.append(
                    FailedImport(source.filename, REASON_SOURCE_READ_FAILED, str(error))
                )
                continue

            document_hash = hashlib.sha256(data).hexdigest()
            del document_hash  # page hashes below are the durable dedup domain

            if not _is_pdf(data):
                # MOBI and every other non-PDF payload: diagnosable, no
                # invented parser (see module docstring).
                failed.append(
                    FailedImport(
                        source.filename,
                        REASON_UNSUPPORTED_FORMAT,
                        "only PDF is supported by the approved binding "
                        "(MOBI rasterisation is BLOCKED, TASK-023)",
                    )
                )
                continue

            try:
                handle = self._raster.open(data)
            except DocumentDecodeError as error:
                failed.append(FailedImport(source.filename, error.reason, error.detail))
                continue

            cancelled_during_pages = False
            file_page_failures = 0
            file_pages_imported = 0
            file_pages_skipped = 0
            try:
                for page_no in range(1, handle.page_count + 1):
                    if is_cancelled():
                        pending.append(f"{source.filename} (page {page_no}+)")
                        cancelled_during_pages = True
                        break
                    try:
                        rendered = handle.render_page(page_no - 1)
                    except DocumentDecodeError as error:
                        failed.append(
                            FailedImport(source.filename, error.reason, error.detail)
                        )
                        file_page_failures += 1
                        break
                    page_hash = hashlib.sha256(rendered.png).hexdigest()
                    if (
                        page_hash in existing_hashes
                        and duplicate_policy == DuplicatePolicy.SKIP
                    ):
                        file_pages_skipped += 1
                        continue
                    try:
                        managed_ref = self._store.store_original(
                            chapter_id,
                            _page_name(source.filename, page_no),
                            rendered.png,
                            page_hash,
                        )
                    except OSError as error:
                        failed.append(
                            FailedImport(source.filename, REASON_COPY_FAILED, str(error))
                        )
                        break
                    next_order += 1
                    page = Page(
                        page_id=uuid.uuid4().hex,
                        chapter_id=chapter_id,
                        source_filename=source.filename,
                        source_order=next_order,
                        sort_order=next_order,
                        source_hash=page_hash,
                        source_size_bytes=len(rendered.png),
                        width=rendered.width,
                        height=rendered.height,
                        managed_original_ref=managed_ref,
                    )
                    # Committed strictly after the managed copy exists.
                    self._sink.add_page(page)
                    existing_hashes.add(page_hash)
                    file_pages_imported += 1
                    imported.append(
                        ImportedPage(_page_name(source.filename, page_no), page)
                    )
            finally:
                handle.close()

            if cancelled_during_pages:
                continue
            if file_pages_imported == 0 and file_page_failures == 0:
                # every page already existed: the document is a duplicate
                skipped.append(source.filename)

        return ImportReport(
            chapter_id=chapter_id,
            imported=tuple(imported),
            skipped_duplicates=tuple(skipped),
            failed=tuple(failed),
            pending_after_cancel=tuple(pending),
            cancelled=bool(pending),
        )
