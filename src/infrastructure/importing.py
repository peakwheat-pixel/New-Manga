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
