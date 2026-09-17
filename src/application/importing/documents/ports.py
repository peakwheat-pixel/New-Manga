"""Contracts for the PDF/MOBI document import use case (TASK-023, D02 §8).

A document is one user file that yields *many* managed page images: the
raster adapter turns document pages into PNG bytes, and the use case feeds
each page through the same Managed Copy / duplicate / ordering discipline as
the image import (reuse, not a second pipeline).

Scope note (TASK-023): the approved binding covers **PDF** only (U-2 chose
PDFium via pypdfium2). MOBI has no approved parsing dependency — files that
are not PDFs fail with ``UNSUPPORTED_FORMAT`` (diagnosable) instead of the
use case inventing a parser.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class RenderedDocumentPage:
    """One document page rasterised to PNG, ready for Managed Copy."""

    png: bytes
    width: int
    height: int


class DocumentDecodeError(ValueError):
    """Typed, diagnosable failure for corrupt / encrypted / unreadable input.

    ``reason`` is a stable code for the import report: ``INVALID_DOCUMENT``
    for bytes that cannot be parsed, ``ENCRYPTED`` for password-protected
    documents (no credential is ever guessed).
    """

    def __init__(self, reason: str, detail: str = "") -> None:
        super().__init__(f"{reason}: {detail}" if detail else reason)
        self.reason = reason
        self.detail = detail


class DocumentHandle(Protocol):
    """An opened document: page count plus per-page rasterisation."""

    @property
    def page_count(self) -> int: ...

    def render_page(self, index: int) -> RenderedDocumentPage: ...

    def close(self) -> None: ...


class DocumentRaster(Protocol):
    """Opens document bytes for rasterisation; production binds PDFium."""

    def open(self, data: bytes) -> DocumentHandle: ...
