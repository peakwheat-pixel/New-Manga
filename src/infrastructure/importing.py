"""Production adapters for local image import (D04 §8, D07 §37~39)."""

from __future__ import annotations

import os
import re
import shutil
import struct
import tempfile
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

# R-001 (TASK-041 review): page images are exactly ``image%05d.<ext>`` in
# ``mobi7/Images/``. The fullmatch keeps the extractor's other outputs out —
# ``cover%05d.*`` (a cover, not a page) and ``HDimage%05d.*`` (HD duplicates
# under ``HDImages/``) both end in "...image%05d.<ext>" but do not fullmatch.
_PAGE_IMAGE_RE = re.compile(
    r"image(\d{5})\.(?:bmp|gif|jpe?g|png)", re.IGNORECASE
)


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
    ``INVALID_DOCUMENT`` otherwise). An unusable binding (not installed, or
    its native library cannot load) is ``MISSING_DEPENDENCY``, never a bare
    ``ImportError`` escaping the adapter (F-9, TASK-043).
    """

    def __init__(self, scale: float = 2.0) -> None:
        self.scale = float(scale)

    def open(self, data: bytes):
        from application.importing.documents.ports import DocumentDecodeError

        try:
            import pypdfium2 as pdfium
        except (ImportError, OSError) as error:
            # F-9 (TASK-043): the binding is imported inside the guarded
            # region so a missing/unloadable PDFium is a diagnosable typed
            # failure instead of an exception escaping mid-import.
            raise DocumentDecodeError(
                "MISSING_DEPENDENCY",
                "the pypdfium2 binding required for PDF import is unavailable: "
                f"{error}",
            ) from error

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
            # pdfium hands back BGRA byte order. Format_ARGB32 is the
            # little-endian name for exactly that in-memory layout
            # (0xAARRGGBB words read as B,G,R,A), so the two agree.
            qformat = QImage.Format.Format_ARGB32
        elif mode == "BGR":
            # F-1 (TASK-043): pdfium hands back BGR byte order, so the buffer
            # must be read as BGR — Format_RGB888 swapped red and blue on
            # every page (and the wrong pixels were persisted to the Managed
            # Copy and hashed into source_hash).
            qformat = QImage.Format.Format_BGR888
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


class MobiDocumentRaster:
    """Extract embedded page images from KF7 picture MOBI (TASK-041).

    Scope (user-approved; narrowed per review R-002): **KF7 picture MOBI
    only** — comic MOBI files in the classic format are one embedded image
    per page, published as managed pages through the shared document-import
    discipline. Deliberately out of scope, typed fail-closed:

    - reflowable text-only MOBI (no page images): ``INVALID_DOCUMENT`` with
      a scope note (rendering HTML would need an engine the approved
      dependency set does not include);
    - KF8/AZW3 containers (dual-format or KF8-only): ``INVALID_DOCUMENT`` —
      **BLOCKED** pending a dedicated slice that verifies the KF8 tree on
      real samples; the ``mobi7/`` tree of a dual-format container is an
      unverified down-conversion, so it is not trusted either.

    Page semantics (R-001): the extractor's temp tree is **not** trusted as
    a page list. Besides ``mobi7/Images/image%05d.<ext>`` (page images,
    named after their container record number) it may contain
    ``cover%05d.*`` (a cover, not a page), ``HDimage%05d.*`` (HD duplicates
    under ``HDImages/``) and a mirrored ``mobi8/`` tree. Only the KF7 page
    images are collected, ordered by the record number in the name — cover
    and HD resources never become pages.

    The ``mobi`` binding (mobi==0.4.1, an embedded KindleUnpack) sits
    strictly behind this adapter — application code never imports it — so a
    dead upstream is swapped here and nowhere else. DRM-protected containers
    (``crypto_type != 0`` in the PalmDoc header) are rejected as
    ``ENCRYPTED`` before any parsing; truncation and parse failures surface
    as ``INVALID_DOCUMENT``; a page whose image bytes Qt cannot decode fails
    that page (F-3 accounting); an unusable binding is
    ``MISSING_DEPENDENCY`` (F-9 caliber, same as the PDF path).
    """

    def open(self, data: bytes):
        from application.importing.documents.ports import DocumentDecodeError

        try:
            import mobi  # adapter-local: never leaks past this file
        except (ImportError, OSError) as error:
            raise DocumentDecodeError(
                "MISSING_DEPENDENCY",
                "the mobi binding required for MOBI import is unavailable: "
                f"{error}",
            ) from error

        crypto_type = _pdb_crypto_type(data)
        if crypto_type is not None and crypto_type != 0:
            raise DocumentDecodeError(
                "ENCRYPTED",
                "the MOBI is DRM-protected; protected files are never opened",
            )

        temp_source: str | None = None
        try:
            descriptor, temp_source = tempfile.mkstemp(suffix=".mobi")
            with os.fdopen(descriptor, "wb") as handle:
                handle.write(data)
            tempdir, _html = mobi.extract(temp_source)
        except DocumentDecodeError:
            raise
        except Exception as error:
            raise DocumentDecodeError(
                "INVALID_DOCUMENT",
                f"the MOBI container could not be parsed: {error}",
            ) from error
        finally:
            if temp_source is not None:
                try:
                    os.unlink(temp_source)
                except OSError:  # pragma: no cover - temp file best effort
                    pass

        root = Path(tempdir)
        if (root / "mobi8").is_dir():
            # KF8/AZW3 container (dual-format or KF8-only): fail closed
            # instead of trusting an unverified down-converted KF7 tree
            # (review R-001/R-002; see the class docstring for the BLOCKED
            # registration).
            shutil.rmtree(tempdir, ignore_errors=True)
            raise DocumentDecodeError(
                "INVALID_DOCUMENT",
                "KF8/AZW3 MOBI containers are not supported yet: only KF7 "
                "picture MOBI is verified (support is BLOCKED pending a "
                "dedicated slice)",
            )

        page_dir = root / "mobi7" / "Images"
        images: list[tuple[int, Path]] = []
        if page_dir.is_dir():
            for path in page_dir.iterdir():
                match = _PAGE_IMAGE_RE.fullmatch(path.name)
                if match is not None and path.is_file():
                    images.append((int(match.group(1)), path))
        images.sort(key=lambda entry: entry[0])
        if not images:
            shutil.rmtree(tempdir, ignore_errors=True)
            raise DocumentDecodeError(
                "INVALID_DOCUMENT",
                "text-only MOBI: no KF7 page images (mobi7/Images/"
                "image%05d.*); reflowable rendering is out of the approved "
                "scope",
            )
        return _MobiDocumentHandle(tempdir, [path for _record, path in images])


class _MobiDocumentHandle:
    """Extracted picture-MOBI: one image file per page, record order."""

    def __init__(self, tempdir: str, images: list[Path]) -> None:
        self._tempdir = tempdir
        self._images = images

    @property
    def page_count(self) -> int:
        return len(self._images)

    def render_page(self, index: int):
        from application.importing.documents.ports import (
            DocumentDecodeError,
            RenderedDocumentPage,
        )

        from PySide6.QtCore import QBuffer, QIODevice
        from PySide6.QtGui import QImage

        path = self._images[index]
        try:
            raw = path.read_bytes()
        except OSError as error:
            raise DocumentDecodeError(
                "INVALID_DOCUMENT", f"page image could not be read: {error}"
            ) from error
        image = QImage()
        if not image.loadFromData(raw):
            raise DocumentDecodeError(
                "INVALID_DOCUMENT",
                f"page image {path.name} could not be decoded by Qt",
            )
        buffer = QBuffer()
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        if not image.save(buffer, "PNG"):
            raise DocumentDecodeError(
                "INVALID_DOCUMENT",
                f"page image {path.name} could not be encoded as PNG",
            )
        return RenderedDocumentPage(bytes(buffer.data()), image.width(), image.height())

    def close(self) -> None:
        # The extractor leaves its temp tree behind; ownership of cleanup is
        # here so every exit path (success, page failure, cancellation)
        # releases it.
        shutil.rmtree(self._tempdir, ignore_errors=True)


def _pdb_crypto_type(data: bytes) -> int | None:
    """``crypto_type`` of the PalmDoc header (record 0), or ``None`` when
    the container is too short to have one (the extractor reports that)."""
    if len(data) < 78:
        return None
    record_count = struct.unpack_from(">H", data, 76)[0]
    if record_count == 0:
        return None
    record0_offset = struct.unpack_from(">I", data, 78)[0]
    crypto_offset = record0_offset + 0x0C
    if len(data) < crypto_offset + 2:
        return None
    return struct.unpack_from(">H", data, crypto_offset)[0]
