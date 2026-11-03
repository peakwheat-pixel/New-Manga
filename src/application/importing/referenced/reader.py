"""Referenced-source entry reader and rendition renderer.

Reads one entry's bytes through the injected strict-read port, then produces a
re-encoded PNG rendition (never the raw user-source bytes, C-15 §4.2). The
application layer stays free of infrastructure imports; the strict lease and
decode adapters are injected by bootstrap.
"""

from __future__ import annotations

import io
import zipfile

from application.importing.referenced.errors import SourceImportError
from application.importing.referenced.scanner import (
    ordered_archive_members,
    read_verified_bytes,
)


def _open_archive(data: bytes) -> zipfile.ZipFile:
    try:
        return zipfile.ZipFile(io.BytesIO(data))
    except Exception as error:  # noqa: BLE001 - container-level typed refusal
        raise SourceImportError(
            "SOURCE_FORMAT_UNSUPPORTED", "archive container is invalid"
        ) from error


def _folder_rel(path: str, root: str) -> str:
    import os

    rel = os.path.relpath(os.path.abspath(path), os.path.abspath(root))
    return rel.replace(os.sep, "/")


def _check_decode_budget(resolved, width: int, height: int) -> None:
    max_decode = int(getattr(resolved.budget, "max_decode_bytes", 0) or 0)
    if max_decode and width * height * 4 > max_decode:
        raise SourceImportError(
            "SOURCE_BUDGET_EXCEEDED", "rendition decode budget exceeded"
        )


def check_decode_budget(resolved, width: int, height: int) -> None:
    """R1-I007: refuse a decode/render before allocating the pixel buffer."""
    _check_decode_budget(resolved, width, height)


def read_entry_bytes(resolved, entry, password: bytes | None = None) -> bytes:
    """Read exactly one entry's bytes (container/member/folder/PDF page)."""
    if resolved.source_kind == "image":
        return read_verified_bytes(
            resolved.container_path,
            resolved.container_facts,
            max_bytes=resolved.budget.max_bytes,
        )
    if resolved.source_kind in {"zip", "cbz"}:
        data = read_verified_bytes(
            resolved.container_path,
            resolved.container_facts,
            max_bytes=resolved.budget.max_bytes,
        )
        archive = _open_archive(data)
        with archive:
            ordered = ordered_archive_members(archive)
            if entry.ordinal >= len(ordered):
                raise SourceImportError(
                    "SOURCE_ENTRY_MISSING", "archive member is missing"
                )
            info = ordered[entry.ordinal]
            # R1-I007 P2: bound the *decompressed* member size before
            # ``archive.read`` allocates it (the container byte budget does not
            # cap a zip bomb's expansion).
            max_decode = int(getattr(resolved.budget, "max_decode_bytes", 0) or 0)
            if max_decode and int(info.file_size) > max_decode:
                raise SourceImportError(
                    "SOURCE_BUDGET_EXCEEDED",
                    "archive member exceeds the decode budget",
                )
            # C-16 v1.1 §3.1: an encrypted member without the fresh Secret-G
            # is a password-required refusal, not a wrong-password attempt.
            if (info.flag_bits & 0x1) and password is None:
                raise SourceImportError(
                    "SOURCE_PASSWORD_REQUIRED",
                    "encrypted archive member requires a password",
                )
            try:
                return archive.read(info, pwd=password)
            except (RuntimeError, OSError) as error:
                if password is None:
                    raise SourceImportError(
                        "SOURCE_PASSWORD_REQUIRED",
                        "encrypted archive member requires a password",
                    ) from error
                raise SourceImportError(
                    "SOURCE_PASSWORD_INVALID", "archive member could not be read"
                ) from error
    if resolved.source_kind == "folder":
        for path, facts in resolved.folder_entries:
            if _folder_rel(path, resolved.folder_root) == entry.locator:
                return read_verified_bytes(
                    path, facts, max_bytes=resolved.budget.max_bytes
                )
        raise SourceImportError("SOURCE_ENTRY_MISSING", "folder member is missing")
    if resolved.source_kind == "pdf":
        return read_verified_bytes(
            resolved.container_path,
            resolved.container_facts,
            max_bytes=resolved.budget.max_bytes,
        )
    raise SourceImportError(
        "SOURCE_FORMAT_UNSUPPORTED", "source kind is not supported"
    )


def render_entry_png(
    resolved,
    entry,
    *,
    image_decoder=None,
    document_raster=None,
    password: bytes | None = None,
) -> tuple[bytes, int, int]:
    """Render one entry as a re-encoded PNG rendition (not raw source bytes)."""
    raw = read_entry_bytes(resolved, entry, password)
    if resolved.source_kind == "pdf":
        if document_raster is None:
            raise SourceImportError(
                "SOURCE_FORMAT_UNSUPPORTED", "PDF rendition raster is unavailable"
            )
        from application.importing.documents.ports import DocumentDecodeError

        try:
            # C-16 v1.1 §3.1: the one-shot Secret-G password is handed to the
            # raster seam; an encrypted PDF without it is REQUIRED, a rejected
            # password is INVALID (never a silent plain decode attempt).
            handle = document_raster.open(raw, password=password)
        except DocumentDecodeError as error:
            if error.reason == "ENCRYPTED":
                raise SourceImportError(
                    "SOURCE_PASSWORD_REQUIRED" if password is None
                    else "SOURCE_PASSWORD_INVALID",
                    "the PDF is password-protected",
                ) from error
            raise SourceImportError(
                "SOURCE_FORMAT_UNSUPPORTED", "PDF rendition raster failed"
            ) from error
        try:
            # R1-I007: page dimensions are known before rasterizing.
            page_width, page_height = handle.page_size(entry.ordinal)
            _check_decode_budget(resolved, int(page_width), int(page_height))
            rendered = handle.render_page(entry.ordinal)
        finally:
            handle.close()
        _check_decode_budget(resolved, int(rendered.width), int(rendered.height))
        return rendered.png, int(rendered.width), int(rendered.height)

    from PIL import Image, ImageOps

    try:
        # R1-I007: header-only open first; the pixel buffer is only allocated
        # after the decode budget admitted the declared dimensions.
        image = Image.open(io.BytesIO(raw))
        _check_decode_budget(resolved, int(image.size[0]), int(image.size[1]))
        image.load()
    except SourceImportError:
        raise
    except Exception as error:  # noqa: BLE001 - typed refusal
        raise SourceImportError(
            "SOURCE_FORMAT_UNSUPPORTED", "entry image could not be decoded"
        ) from error
    try:
        image = ImageOps.exif_transpose(image)
        if image.mode not in ("RGB", "RGBA"):
            image = image.convert("RGBA" if "A" in image.getbands() else "RGB")
        width, height = image.size
        _check_decode_budget(resolved, int(width), int(height))
        output = io.BytesIO()
        image.save(output, format="PNG", optimize=False)
        return output.getvalue(), int(width), int(height)
    finally:
        try:
            image.close()
        except Exception:  # pragma: no cover - closing never raises
            pass
