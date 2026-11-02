"""Production adapters for local image import (D04 §8, D07 §37~39)."""

from __future__ import annotations

import io
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

#: M2-PAGE-RESOURCE-RESOLVE-1 (DSH r1 PR-06): the page-resolve wire gate in
#: bootstrap.core_service admits exactly the suffixes this decode face can
#: decode -- derived from _MIME_TYPES so the two can never drift (a legally
#: imported .tif/.heic page must not fail closed as an unsupported format).
SUPPORTED_IMAGE_SUFFIXES = frozenset(f".{ext}" for ext in _MIME_TYPES)

# R-001 (TASK-041 review): page images are exactly ``image%05d.<ext>`` in
# ``mobi7/Images/``. The fullmatch keeps the extractor's other outputs out —
# ``cover%05d.*`` (a cover, not a page) and ``HDimage%05d.*`` (HD duplicates
# under ``HDImages/``) both end in "...image%05d.<ext>" but do not fullmatch.
_PAGE_IMAGE_RE = re.compile(
    r"image(\d{5})\.(?:bmp|gif|jpe?g|png)", re.IGNORECASE
)

# M2-IMPORT-ALLOC-LIMIT (TA3-B2 F2): Qt caps decoded images at a built-in
# 256 MiB allocation limit (Qt 6.5+). Webtoon long-strips in the product
# domain exceed it and were rejected at import (K07 690x131289 decodes to
# ~345.6 MiB; K09/K10 ~264.5/265.0 MiB), so the decoder asserts its own,
# documented ceiling before every read. The value is 2047 MiB because:
#   - Domain anchor (r1 R6): the largest *measured* webtoon page decodes to
#     ~345.6 MiB, so 2047 keeps a ~5.9x margin over observed reality; even
#     an unmeasured extrapolation (690 x ~350k px x 4 B ~ 921 MiB — the
#     ~350k-px figure has no measured source in the domain, it is a
#     hypothetical upper tail) still leaves ~2.2x margin.
#   - NOT 0: the point is a bounded fail-closed ceiling, anchored on the
#     measured domain above — ``setAllocationLimit(0)`` disables the check
#     entirely, so a corrupt/declared-huge header could OOM the process
#     (AC1 rationale, M2-IMPORT-ALLOC-LIMIT).
#   - 2047 is inside Qt's ``int`` megabyte parameter and keeps any single
#     decode well below realistic 64-bit desktop memory budgets.
#   - Qt checks the bound *before* allocating, so the limit is an upper
#     bound on one decode, never a preallocation.
# The static setter is process-global; re-asserting it per decode is
# idempotent and cheap, and keeps the bound correct even if unrelated code
# mutates the global later. Import runs on the application thread today;
# worst case under concurrency is two idempotent writes of the same value.
_ALLOCATION_LIMIT_MIB = 2047

# r1 R4 (M2-TA3-B2): a per-file failure detail must stay diagnosable but
# bounded — it surfaces in reports, UI and logs.
_ERROR_DETAIL_MAX_CHARS = 300


def _bounded_detail(text: str) -> str:
    """Bounded per-file decode failure detail (r1 R4/R8 contract)."""
    detail = (text or "").strip()
    if not detail:
        detail = "bytes are not a decodable image"
    if len(detail) > _ERROR_DETAIL_MAX_CHARS:
        detail = detail[:_ERROR_DETAIL_MAX_CHARS] + "..."
    return detail


def _decode_ceiling_mib(width: int, height: int) -> float:
    """Decoded RGBA footprint of a DECLARED image size, in MiB.

    The ceiling is evaluated against the header dimensions before any pixel
    buffer is materialised — the same fail-closed ordering the replaced Qt
    reader used (M2-IMPORT-ALLOC-LIMIT): a corrupt/declared-huge header can
    never be the reason a Core process OOMs.
    """
    return (int(width) * int(height) * 4) / float(1024 * 1024)


#: Pillow ``Image.format`` -> the MIME type the import surface reports.
#: CORE-SLIM-1: Pillow replaced the Qt image plugins; the frozen product
#: surface (``SUPPORTED_IMAGE_SUFFIXES``) is unchanged. AVIF is a capability
#: the Qt plugin set did NOT have in the shipped closure; HEIC/HEIF stay
#: unsupported in both (Pillow needs pillow-heif, not a dependency), so no
#: decode capability is lost.
_MIME_BY_IMAGE_FORMAT = {
    "AVIF": "image/avif",
    "BMP": "image/bmp",
    "GIF": "image/gif",
    "JPEG": "image/jpeg",
    "PNG": "image/png",
    "TIFF": "image/tiff",
    "WEBP": "image/webp",
}


class PillowImageDecoder:
    """Decode image bytes with Pillow (CORE-SLIM-1: the Core ships no Qt).

    Replacement for the former ``QtImageDecoder``. The documented decode
    allocation ceiling (``_ALLOCATION_LIMIT_MIB``) is enforced against the
    DECLARED dimensions before any pixel buffer is allocated, so webtoon
    long-strips in the product domain decode while oversized/corrupt headers
    stay fail-closed with a bounded typed detail (M2-IMPORT-ALLOC-LIMIT
    behaviour, unchanged).

    Multi-frame payloads (animated GIF/WebP, multi-page TIFF) are accepted and
    reported by their first frame's dimensions — exactly what the replaced
    reader returned to the import surface; the original bytes are stored
    verbatim by the Managed Copy, so no animation data is dropped.

    Pillow's own decompression-bomb heuristic is disabled for the duration of
    one decode (it would otherwise refuse the measured 90.6 Mpx webtoon page
    the 2047 MiB product ceiling deliberately admits); the product ceiling is
    the only bound, exactly as the process-global Qt allocation limit was
    before.
    """

    def decode(self, data: bytes) -> DecodedImage:
        from PIL import Image

        previous_bomb_limit = Image.MAX_IMAGE_PIXELS
        Image.MAX_IMAGE_PIXELS = None  # the product ceiling below is the bound
        try:
            image = Image.open(io.BytesIO(data))
            try:
                width, height = image.size
                decoded_mib = _decode_ceiling_mib(width, height)
                if decoded_mib > _ALLOCATION_LIMIT_MIB:
                    raise ImageDecodeError(
                        _bounded_detail(
                            f"image declares {width}x{height} = "
                            f"{decoded_mib:.1f} MiB decoded, above the "
                            f"{_ALLOCATION_LIMIT_MIB} MiB decode ceiling"
                        )
                    )
                image.load()
                format_name = (image.format or "").upper()
            finally:
                image.close()
        except ImageDecodeError:
            raise
        except Exception as error:  # noqa: BLE001 - every decode failure is typed
            raise ImageDecodeError(_bounded_detail(str(error))) from error
        finally:
            Image.MAX_IMAGE_PIXELS = previous_bomb_limit

        return DecodedImage(
            width=width,
            height=height,
            mime_type=_MIME_BY_IMAGE_FORMAT.get(format_name, _UNKNOWN_MIME_TYPE),
        )


#: CORE-SLIM-1 legacy compatibility shim: the evidence-frozen legacy Qt shell
#: modules (``bootstrap.app``, ``bootstrap.acceptance_bridge``) import the old
#: class name. They are NOT part of the shipped Core closure, and the alias
#: keeps their imports working without reintroducing Qt.
QtImageDecoder = PillowImageDecoder


def _encode_pdf_bitmap_png(raw: bytes, width: int, height: int, mode: str) -> bytes:
    """Encode a pdfium bitmap buffer as PNG bytes (CORE-SLIM-1: Pillow, no Qt).

    The buffer byte order is pdfium's, not Qt's: ``BGRA`` is read as ``BGRA``
    and ``BGR`` as ``BGR``, preserving the red/blue assignment the frozen F-1
    (TASK-043) fix established. Any other mode is a typed refusal by the
    caller; a truncated buffer raises ``ValueError``.
    """
    from PIL import Image

    bytes_per_line = width * (4 if mode == "BGRA" else 3)
    if len(raw) < bytes_per_line * height:
        raise ValueError("truncated bitmap buffer")
    image = (
        Image.frombuffer("RGBA", (width, height), raw, "raw", "BGRA", 0, 1)
        if mode == "BGRA"
        else Image.frombuffer("RGB", (width, height), raw, "raw", "BGR", 0, 1)
    )
    out = io.BytesIO()
    image.save(out, format="PNG")
    return out.getvalue()


#: r1 R7 (M2-IMPORT-ALLOC-LIMIT): MOBI page images are untrusted input and
#: keep the original tightened 256 MiB fail-closed bound (the webtoon path's
#: 2047 MiB ceiling must not leak into this decode face).
_MOBI_PAGE_ALLOCATION_LIMIT_MIB = 256


class _MobiPageDecodeError(RuntimeError):
    """One MOBI page image could not be decoded (typed at the adapter)."""


def _decode_mobi_page_png(raw: bytes) -> tuple[bytes, int, int]:
    """Decode one embedded MOBI page image to PNG bytes (CORE-SLIM-1: Pillow)."""
    from PIL import Image

    previous_bomb_limit = Image.MAX_IMAGE_PIXELS
    Image.MAX_IMAGE_PIXELS = None  # the explicit ceiling below is the bound
    try:
        image = Image.open(io.BytesIO(raw))
        try:
            width, height = image.size
            decoded_mib = _decode_ceiling_mib(width, height)
            if decoded_mib > _MOBI_PAGE_ALLOCATION_LIMIT_MIB:
                raise _MobiPageDecodeError(
                    f"{decoded_mib:.1f} MiB decoded is above the "
                    f"{_MOBI_PAGE_ALLOCATION_LIMIT_MIB} MiB page ceiling"
                )
            image.load()
            if image.mode not in ("RGB", "RGBA", "L", "LA"):
                image = image.convert("RGB")
            out = io.BytesIO()
            image.save(out, format="PNG")
            return out.getvalue(), width, height
        finally:
            image.close()
    except _MobiPageDecodeError:
        raise
    except Exception as error:  # noqa: BLE001 - typed page refusal
        raise _MobiPageDecodeError(str(error)) from error
    finally:
        Image.MAX_IMAGE_PIXELS = previous_bomb_limit


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

        try:
            page = self._document[index]
            bitmap = page.render(scale=self.scale)
            width, height = bitmap.width, bitmap.height
            raw = bytes(bitmap.buffer)
        except Exception as error:  # pdfium-level failure on this page
            raise DocumentDecodeError("INVALID_DOCUMENT", str(error)) from error
        mode = str(bitmap.mode)
        if mode not in ("BGRA", "BGR"):
            # F-1 (TASK-043) background: pdfium hands back BGRA (alpha) or BGR
            # byte order; both must be read in PDFIUM's order — reading BGR as
            # RGB swapped red and blue on every page (and the wrong pixels were
            # persisted to the Managed Copy and hashed into source_hash).
            raise DocumentDecodeError(
                "INVALID_DOCUMENT", f"unexpected pdfium bitmap mode {mode!r}"
            )
        bytes_per_line = width * (4 if mode == "BGRA" else 3)
        if len(raw) < bytes_per_line * height:
            raise DocumentDecodeError(
                "INVALID_DOCUMENT", "pdfium bitmap buffer is truncated"
            )
        try:
            # CORE-SLIM-1: Pillow replaces the QImage -> PNG bridge.
            png = _encode_pdf_bitmap_png(raw, width, height, mode)
        except Exception as error:  # noqa: BLE001 - typed refusal, never a crash
            raise DocumentDecodeError(
                "INVALID_DOCUMENT", "rasterised page could not be encoded as PNG"
            ) from error
        return RenderedDocumentPage(png, width, height)

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

        path = self._images[index]
        try:
            raw = path.read_bytes()
        except OSError as error:
            raise DocumentDecodeError(
                "INVALID_DOCUMENT", f"page image could not be read: {error}"
            ) from error
        # r1 R7 (M2-IMPORT-ALLOC-LIMIT): the webtoon path widens the decode
        # ceiling to 2047 MiB; MOBI embedded page images are untrusted input,
        # so this path keeps the original 256 MiB fail-closed bound of its own
        # (CORE-SLIM-1: enforced against the declared size, before pixels are
        # materialised, instead of through Qt's process-global limit).
        try:
            png, width, height = _decode_mobi_page_png(raw)
        except _MobiPageDecodeError as error:
            raise DocumentDecodeError(
                "INVALID_DOCUMENT",
                f"page image {path.name} could not be decoded ({error})",
            ) from error
        return RenderedDocumentPage(png, width, height)

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
