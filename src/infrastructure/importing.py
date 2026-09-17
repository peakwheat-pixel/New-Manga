"""Production adapters for local image import (D04 §8, D07 §37~39)."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from uuid import uuid4

from application.importing.images.ports import DecodedImage, ImageDecodeError
from ports.repositories.storage import ManagedFileStoragePort


_MIME_TYPES = {
    "avif": "image/avif",
    "bmp": "image/bmp",
    "gif": "image/gif",
    "heic": "image/heic",
    "heif": "image/heif",
    "jpeg": "image/jpeg",
    "jpg": "image/jpeg",
    "png": "image/png",
    "tif": "image/tiff",
    "tiff": "image/tiff",
    "webp": "image/webp",
}
_UNKNOWN_MIME_TYPE = "application/octet-stream"


class QtImageDecoder:
    """Decode image bytes with the Qt image plugins available to the app."""

    def decode(self, data: bytes) -> DecodedImage:
        from PySide6.QtCore import QByteArray, QBuffer, QIODevice
        from PySide6.QtGui import QImageReader

        buffer = QBuffer()
        buffer.setData(QByteArray(data))
        if not buffer.open(QIODevice.OpenModeFlag.ReadOnly):
            raise ImageDecodeError("image buffer could not be opened")

        reader = QImageReader(buffer)
        format_name = bytes(reader.format()).decode("ascii", errors="ignore").lower()
        image = reader.read()
        if image.isNull():
            detail = reader.errorString() or "bytes are not a decodable image"
            raise ImageDecodeError(detail)

        return DecodedImage(
            width=image.width(),
            height=image.height(),
            mime_type=_MIME_TYPES.get(format_name, _UNKNOWN_MIME_TYPE),
        )


class ManagedCopyStoreAdapter:
    """Publish immutable original bytes through :class:`ManagedFileStorage`.

    The application port receives only a chapter id.  Assembly supplies the
    chapter-to-book lookup so this adapter can preserve the D03 book-level
    storage layout without changing the application contract.
    """

    def __init__(
        self,
        storage: ManagedFileStoragePort,
        book_id_for_chapter: Callable[[str], str],
    ) -> None:
        self._storage = storage
        self._book_id_for_chapter = book_id_for_chapter

    def store_original(
        self, chapter_id: str, source_filename: str, data: bytes, source_hash: str
    ) -> str:
        if (
            not isinstance(source_filename, str)
            or not source_filename
            or source_filename in {".", ".."}
            or any(separator in source_filename for separator in ("/", "\\"))
        ):
            raise ValueError("source filename must be a single path component")

        book_id = self._book_id_for_chapter(chapter_id)
        suffix = Path(source_filename).suffix
        temp_handle = self._storage.write_temp(data)
        try:
            integrity = self._storage.verify_temp(temp_handle)
            if integrity.sha256 != source_hash:
                raise OSError("managed copy source hash does not match")

            relative_path = self._storage.new_revision_relative_path(
                book_id,
                chapter_id,
                "original",
                uuid4().hex,
                suffix,
            )
            self._storage.publish(temp_handle, relative_path)
            temp_handle = None
            return relative_path
        finally:
            if temp_handle is not None:
                self._storage.discard_temp(temp_handle)


class PdfiumDocumentRaster:
    """Rasterise PDF pages via pypdfium2 (TASK-023; U-2 approved PDFium).

    Scope: **PDF only**. MOBI is not a PDFium capability and is deliberately
    not implemented here — the use case reports non-PDF payloads as
    ``UNSUPPORTED_FORMAT`` instead of this adapter guessing a parser.

    Render scale is an implementation default (2.0 ≈ 144 DPI), not a frozen
    contract; pages are encoded to PNG through the same Qt stack as the
    image decoder. PDFium errors surface as
    :class:`~application.importing.documents.ports.DocumentDecodeError`
    (``ENCRYPTED`` for password-protected files — never guessed — and
    ``INVALID_DOCUMENT`` otherwise).
    """

    def __init__(self, scale: float = 2.0) -> None:
        self.scale = float(scale)

    def open(self, data: bytes):
        from application.importing.documents.ports import DocumentDecodeError

        import pypdfium2 as pdfium

        try:
            document = pdfium.PdfDocument(data)
        except pdfium.PdfiumError as error:
            message = str(error)
            if "password" in message.lower():
                raise DocumentDecodeError(
                    "ENCRYPTED", "the PDF is password-protected"
                ) from error
            raise DocumentDecodeError("INVALID_DOCUMENT", message) from error
        return _PdfiumDocumentHandle(document, self.scale)


class _PdfiumDocumentHandle:
    def __init__(self, document, scale: float) -> None:
        self._document = document
        self.scale = scale

    @property
    def page_count(self) -> int:
        return len(self._document)

    def render_page(self, index: int):
        from application.importing.documents.ports import (
            DocumentDecodeError,
            RenderedDocumentPage,
        )

        from PySide6.QtCore import QBuffer, QIODevice
        from PySide6.QtGui import QImage

        try:
            page = self._document[index]
            bitmap = page.render(scale=self.scale)
            width, height = bitmap.width, bitmap.height
            raw = bytes(bitmap.buffer)
        except Exception as error:  # pdfium-level failure on this page
            raise DocumentDecodeError("INVALID_DOCUMENT", str(error)) from error
        mode = str(bitmap.mode)
        if mode == "BGRA":
            qformat = QImage.Format.Format_ARGB32
        elif mode == "BGR":
            qformat = QImage.Format.Format_RGB888
        else:
            raise DocumentDecodeError(
                "INVALID_DOCUMENT", f"unexpected pdfium bitmap mode {mode!r}"
            )
        bytes_per_line = width * (4 if mode == "BGRA" else 3)
        if len(raw) < bytes_per_line * height:
            raise DocumentDecodeError(
                "INVALID_DOCUMENT", "pdfium bitmap buffer is truncated"
            )
        image = QImage(raw, width, height, bytes_per_line, qformat)
        if image.isNull():
            raise DocumentDecodeError(
                "INVALID_DOCUMENT", "rasterised page could not be decoded by Qt"
            )
        buffer = QBuffer()
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        if not image.save(buffer, "PNG"):
            raise DocumentDecodeError(
                "INVALID_DOCUMENT", "rasterised page could not be encoded as PNG"
            )
        return RenderedDocumentPage(bytes(buffer.data()), width, height)

    def close(self) -> None:
        try:
            self._document.close()
        except Exception:  # pragma: no cover - closing must never raise
            pass
