"""Import PDF pages through the shared Managed Copy and Page commit path."""

from __future__ import annotations

import hashlib
import uuid
from pathlib import Path
from typing import Callable

from application.importing.documents.ports import DocumentDecodeError, DocumentRaster
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
REASON_UNSUPPORTED_FORMAT = "UNSUPPORTED_FORMAT"
REASON_COPY_FAILED = "COPY_FAILED"
REASON_SOURCE_READ_FAILED = "SOURCE_READ_FAILED"


def _is_pdf(data: bytes) -> bool:
    return data.startswith(_PDF_MAGIC)


def _page_name(source_filename: str, page_no: int) -> str:
    """Managed-copy display name for one document page (1-based, stable)."""
    stem = Path(source_filename).stem or "document"
    return f"{stem}-page-{page_no:04d}.png"


def _pending_pages(source_filename: str, first_page: int, page_count: int) -> list[str]:
    """Pending labels for every page in the 1-based inclusive interval."""
    return [
        f"{source_filename} (page {page_no}+)"
        for page_no in range(first_page, page_count + 1)
    ]


class ImportDocumentsUseCase:
    """Import only PDF files as managed page images."""

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
        was_cancelled = False

        for source in sources:
            if is_cancelled():
                pending.append(source.filename)
                was_cancelled = True
                continue
            try:
                data = source.read()
            except OSError as error:
                failed.append(
                    FailedImport(source.filename, REASON_SOURCE_READ_FAILED, str(error))
                )
                continue

            if not _is_pdf(data):
                failed.append(
                    FailedImport(
                        source.filename,
                        REASON_UNSUPPORTED_FORMAT,
                        "only PDF document import is supported",
                    )
                )
                continue

            try:
                handle = self._raster.open(data)
            except DocumentDecodeError as error:
                failed.append(FailedImport(source.filename, error.reason, error.detail))
                continue

            # shortcut: buffer all pages for preflight; spool to Managed temp if large PDFs exceed memory.
            rendered_pages = []
            page_count = 0
            failed_page: int | None = None
            decode_error: DocumentDecodeError | None = None
            cancelled_during_preflight = False
            try:
                page_count = handle.page_count
                if page_count <= 0:
                    decode_error = DocumentDecodeError(
                        REASON_INVALID_DOCUMENT, "document contains no pages"
                    )
                for page_no in range(1, page_count + 1):
                    if is_cancelled():
                        cancelled_during_preflight = True
                        was_cancelled = True
                        break
                    try:
                        rendered = handle.render_page(page_no - 1)
                    except DocumentDecodeError as error:
                        failed_page = page_no
                        decode_error = error
                        break
                    if rendered.width <= 0 or rendered.height <= 0 or not rendered.png:
                        failed_page = page_no
                        decode_error = DocumentDecodeError(
                            REASON_INVALID_DOCUMENT,
                            f"page {page_no} rendered without valid pixels",
                        )
                        break
                    rendered_pages.append((page_no, rendered))
            except DocumentDecodeError as error:
                decode_error = error
            finally:
                handle.close()

            if decode_error is not None:
                failed.append(
                    FailedImport(source.filename, decode_error.reason, decode_error.detail)
                )
                if failed_page is not None:
                    pending.extend(_pending_pages(source.filename, 1, failed_page - 1))
                    pending.extend(
                        _pending_pages(source.filename, failed_page + 1, page_count)
                    )
                continue
            if cancelled_during_preflight:
                pending.extend(_pending_pages(source.filename, 1, page_count))
                continue

            file_page_failures = 0
            file_pages_imported = 0
            cancelled_during_commit = False
            for page_no, rendered in rendered_pages:
                if is_cancelled():
                    pending.extend(_pending_pages(source.filename, page_no, page_count))
                    cancelled_during_commit = True
                    was_cancelled = True
                    break
                page_hash = hashlib.sha256(rendered.png).hexdigest()
                if (
                    page_hash in existing_hashes
                    and duplicate_policy == DuplicatePolicy.SKIP
                ):
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
                    file_page_failures += 1
                    pending.extend(_pending_pages(source.filename, page_no + 1, page_count))
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
                # Managed Original is published before the SQLite Page row.
                self._sink.add_page(page)
                existing_hashes.add(page_hash)
                file_pages_imported += 1
                imported.append(ImportedPage(_page_name(source.filename, page_no), page))

            if cancelled_during_commit:
                continue
            if file_pages_imported == 0 and file_page_failures == 0 and page_count > 0:
                skipped.append(source.filename)

        return ImportReport(
            chapter_id=chapter_id,
            imported=tuple(imported),
            skipped_duplicates=tuple(skipped),
            failed=tuple(failed),
            pending=tuple(pending),
            cancelled=was_cancelled,
        )
