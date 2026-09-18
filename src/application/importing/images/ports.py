"""Contracts consumed by the image import use case (D04 §8, D07 §37~39)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Protocol

from domain.pages.entities import Page


@dataclass(frozen=True)
class DecodedImage:
    """Result of a successful decode validation."""

    width: int
    height: int
    mime_type: str


class ImageDecodeError(ValueError):
    """Raised when image bytes cannot be decoded (AC-IMPORT corrupt files)."""


class ImageDecoder(Protocol):
    """Decode validation port; the production adapter is bound at assembly.

    Implementations must raise :class:`ImageDecodeError` for bytes that are
    not a decodable image. Keeping this outside the application layer avoids
    binding use cases to any imaging stack.
    """

    def decode(self, data: bytes) -> DecodedImage: ...


class ManagedCopyStore(Protocol):
    """Copies source bytes into managed storage and returns a reference.

    Implementations must copy verbatim (Managed Copy), never touch the
    source file, and raise on failure. A page is only committed after this
    succeeds (D07 §38, AC-IMPORT-003).
    """

    def store_original(
        self, chapter_id: str, source_filename: str, data: bytes, source_hash: str
    ) -> str: ...


class ImportPageSink(Protocol):
    """Persistence boundary for imported pages.

    Soft-deleted pages keep their ``source_order`` slot but no longer block
    re-import: ``max_source_order`` still counts them (so a later restore can
    never collide with a page imported in the meantime), while
    ``existing_source_hashes`` returns live pages only (F-10, TASK-044). Only
    ``PageRepository`` reads hide soft-deleted pages; recycle/restore views are
    a later slice.
    """

    def existing_source_hashes(self, chapter_id: str) -> set[str]: ...

    def max_source_order(self, chapter_id: str) -> int: ...

    def add_page(self, page: Page) -> None: ...


@dataclass(frozen=True)
class ImportSource:
    """One candidate file offered to the import use case."""

    filename: str
    data_provider: Callable[[], bytes]

    def read(self) -> bytes:
        return self.data_provider()


@dataclass(frozen=True)
class ImportedPage:
    filename: str
    page: Page


@dataclass(frozen=True)
class FailedImport:
    filename: str
    reason: str
    detail: str = ""


@dataclass(frozen=True)
class ImportReport:
    """Per-file outcome; a failed or skipped file never yields a Page."""

    chapter_id: str
    imported: tuple[ImportedPage, ...] = ()
    skipped_duplicates: tuple[str, ...] = ()
    failed: tuple[FailedImport, ...] = ()
    pending_after_cancel: tuple[str, ...] = ()
    cancelled: bool = False
