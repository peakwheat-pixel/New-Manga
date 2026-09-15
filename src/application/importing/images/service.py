"""Local image import use case (D04 §8, D07 §37~39).

Per file, in order: duplicate check (source_hash) → decode validation →
Managed Copy → page commit. A file that fails decode or copy never reaches
the sink, so the repository can never hold a page whose managed original is
missing (AC-IMPORT-003). Cancellation stops before starting the next file;
already committed pages stay, unprocessed files are reported as pending.
Source files are only read, never written (D07 §37, AC-IMPORT-002).
"""

from __future__ import annotations

import hashlib
import uuid
from typing import Callable

from application.importing.images.ports import (
    FailedImport,
    ImageDecodeError,
    ImageDecoder,
    ImportPageSink,
    ImportReport,
    ImportSource,
    ImportedPage,
    ManagedCopyStore,
)
from domain.pages.entities import Page


class DuplicatePolicy:
    SKIP = "skip"
    IMPORT_AS_NEW = "import_as_new"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class ImportImagesUseCase:
    def __init__(
        self,
        decoder: ImageDecoder,
        copy_store: ManagedCopyStore,
        sink: ImportPageSink,
    ) -> None:
        self._decoder = decoder
        self._store = copy_store
        self._sink = sink

    def import_files(
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
                failed.append(FailedImport(source.filename, "SOURCE_READ_FAILED", str(error)))
                continue
            source_hash = sha256_bytes(data)

            if source_hash in existing_hashes and duplicate_policy == DuplicatePolicy.SKIP:
                skipped.append(source.filename)
                continue

            try:
                decoded = self._decoder.decode(data)
            except ImageDecodeError as error:
                failed.append(FailedImport(source.filename, "INVALID_IMAGE", str(error)))
                continue

            try:
                managed_ref = self._store.store_original(
                    chapter_id, source.filename, data, source_hash
                )
            except OSError as error:
                failed.append(FailedImport(source.filename, "COPY_FAILED", str(error)))
                continue

            next_order += 1
            page = Page(
                page_id=uuid.uuid4().hex,
                chapter_id=chapter_id,
                source_filename=source.filename,
                source_order=next_order,
                sort_order=next_order,
                source_hash=source_hash,
                source_size_bytes=len(data),
                width=decoded.width,
                height=decoded.height,
                managed_original_ref=managed_ref,
            )
            # Committed strictly after the managed copy exists (AC-IMPORT-003).
            self._sink.add_page(page)
            existing_hashes.add(source_hash)
            imported.append(ImportedPage(source.filename, page))

        return ImportReport(
            chapter_id=chapter_id,
            imported=tuple(imported),
            skipped_duplicates=tuple(skipped),
            failed=tuple(failed),
            pending_after_cancel=tuple(pending),
            cancelled=bool(pending),
        )
