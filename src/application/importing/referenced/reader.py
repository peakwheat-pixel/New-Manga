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
            try:
                return archive.read(info, pwd=password)
            except (RuntimeError, OSError) as error:
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
        handle = document_raster.open(raw)
        try:
            rendered = handle.render_page(entry.ordinal)
        finally:
            handle.close()
        return rendered.png_bytes, int(rendered.width), int(rendered.height)

    from PIL import Image, ImageOps

    try:
        image = Image.open(io.BytesIO(raw))
        image.load()
    except Exception as error:  # noqa: BLE001 - typed refusal
        raise SourceImportError(
            "SOURCE_FORMAT_UNSUPPORTED", "entry image could not be decoded"
        ) from error
    try:
        image = ImageOps.exif_transpose(image)
        if image.mode not in ("RGB", "RGBA"):
            image = image.convert("RGBA" if "A" in image.getbands() else "RGB")
        width, height = image.size
        output = io.BytesIO()
        image.save(output, format="PNG", optimize=False)
        return output.getvalue(), int(width), int(height)
    finally:
        try:
            image.close()
        except Exception:  # pragma: no cover - closing never raises
            pass
