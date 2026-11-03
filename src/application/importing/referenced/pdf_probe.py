"""PDF container probing for referenced imports (page count + page sizes).

A light pypdfium2 wrapper separate from the managed-import rasteriser: the
referenced pipeline stores identity (pdf-page/1) and page dimensions, it
never rasterises at import time — rendering happens through the rendition
cache on read. Password handling follows C-16 §3: an empty-password open of
an encrypted document is a typed ``SOURCE_PASSWORD_REQUIRED``; a wrong
password is ``SOURCE_PASSWORD_INVALID``.
"""

from __future__ import annotations

from application.importing.referenced.errors import SourceImportError


class _PdfProbeHandle:
    def __init__(self, document) -> None:
        self._document = document

    @property
    def page_count(self) -> int:
        return len(self._document)

    def page_size(self, index: int) -> tuple[float, float]:
        try:
            page = self._document[index]
            width, height = page.get_size()
        except Exception as error:  # noqa: BLE001 - pdfium-level typed refusal
            raise SourceImportError(
                "SOURCE_FORMAT_UNSUPPORTED", "pdf page could not be inspected"
            ) from error
        if width <= 0 or height <= 0:
            raise SourceImportError(
                "SOURCE_FORMAT_UNSUPPORTED", "pdf page has no usable size"
            )
        return width, height

    def close(self) -> None:
        try:
            self._document.close()
        except Exception:  # pragma: no cover - closing must never raise
            pass


class PdfiumSourceInspector:
    """``pdf_open(data, password)`` implementation backed by pypdfium2."""

    def open(self, data: bytes, password: bytes | None):
        try:
            import pypdfium2 as pdfium
        except (ImportError, OSError) as error:
            raise SourceImportError(
                "CORE_CAPABILITY_MISSING",
                "the pypdfium2 binding required for PDF sources is unavailable",
            ) from error
        try:
            document = pdfium.PdfDocument(data, password=password)
        except Exception as error:  # noqa: BLE001 - classify every open failure
            message = str(error).lower()
            if "password" in message:
                if password is None:
                    raise SourceImportError(
                        "SOURCE_PASSWORD_REQUIRED",
                        "the pdf source requires a password",
                    ) from error
                raise SourceImportError(
                    "SOURCE_PASSWORD_INVALID", "the pdf password was rejected"
                ) from error
            raise SourceImportError(
                "SOURCE_FORMAT_UNSUPPORTED", "the pdf source could not be opened"
            ) from error
        return _PdfProbeHandle(document)
