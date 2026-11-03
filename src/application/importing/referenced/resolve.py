"""Referenced page -> rendition resolution (C-15 §4.2).

The resolve path for a referenced page must go through the source-read grant
registry (no arbitrary-path fallback) and must publish a decoded/re-encoded
rendition, never the raw user-source bytes. This module implements the
application-side half; bootstrap owns publication into the derived root.
"""

from __future__ import annotations

import hashlib
import json
from importlib import metadata as importlib_metadata

from application.importing.referenced.errors import SourceImportError
from application.importing.referenced.model import ScannedEntry
from application.importing.referenced.reader import render_entry_png

#: Frozen rendition algorithm label for the resolve/preview face (C-15 §4.2).
RENDITION_PARAMS = {"algorithm": "rendition-png/1", "exif_transpose": True}


def _decoder_identity(source_kind: str) -> tuple[str, str]:
    if source_kind == "pdf":
        try:
            version = importlib_metadata.version("pypdfium2")
        except importlib_metadata.PackageNotFoundError:  # pragma: no cover
            version = "unknown"
        return "pdfium", version
    from PIL import __version__ as pillow_version

    return "pillow", pillow_version


def resolve_referenced_rendition(
    page_id: str,
    *,
    repository,
    access,
    image_decoder=None,
    document_raster=None,
) -> dict:
    """Return ``{png, width, height, cache, ...}`` for one referenced page.

    Raises typed :class:`SourceImportError` when the binding is unhealthy, the
    entry is missing, no live grant covers the source, the decode budget is
    exceeded, or the source kind is unsupported. Authorization failures never
    fall back to another path.
    """
    binding = repository.get_page_binding(page_id)
    if not binding or binding.get("status") != "healthy":
        raise SourceImportError(
            "SOURCE_ACCESS_DENIED", "page binding is not healthy"
        )
    entries = repository.list_source_entries(binding["accepted_source_version"])
    row = next(
        (item for item in entries if item["entry_id"] == binding["entry_id"]),
        None,
    )
    if row is None:
        raise SourceImportError(
            "SOURCE_ENTRY_MISSING", "bound source entry is missing"
        )
    entry = ScannedEntry(
        locator=row["locator"],
        ordinal=int(row["ordinal"]),
        size_bytes=int(row["size_bytes"]),
        content_digest=row.get("content_digest"),
        content_digest_kind=row.get("content_digest_kind") or "encoded",
    )
    try:
        grant_id, resolved = access.find_for_source(binding["source_id"])
    except SourceImportError as source_error:
        # Import-time grants are minted before the Core assigns a source id;
        # fall back to the binding's physical identity (same file, same grant
        # root). Still typed/authorized — never an arbitrary path.
        identity_of = getattr(repository, "get_source_identity", None)
        find_for_identity = getattr(access, "find_for_identity", None)
        identity = identity_of(binding["source_id"]) if identity_of else None
        if identity is None or find_for_identity is None:
            raise
        try:
            grant_id, resolved = find_for_identity(
                content_digest=identity["content_digest"],
                volume_serial=int(identity["volume_serial"]),
                file_id=int(identity["file_id"]),
            )
        except SourceImportError:
            raise source_error
    if int(binding.get("authorization_generation") or 0) > int(
        getattr(resolved, "generation", 0)
    ):
        raise SourceImportError(
            "SOURCE_GRANT_REVOKED",
            "binding generation is newer than the live grant",
        )
    png, width, height = render_entry_png(
        resolved,
        entry,
        image_decoder=image_decoder,
        document_raster=document_raster,
    )
    decoder_name, decoder_version = _decoder_identity(resolved.source_kind)
    params_digest = hashlib.sha256(
        json.dumps(
            {"kind": resolved.source_kind, **RENDITION_PARAMS},
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    cache_key = hashlib.sha256(
        "\0".join(
            [
                str(binding["source_id"]),
                str(binding["accepted_source_version"]),
                str(binding["entry_id"]),
                decoder_name,
                decoder_version,
                params_digest,
            ]
        ).encode("utf-8")
    ).hexdigest()
    rendition_kind = "pdf_raster" if resolved.source_kind == "pdf" else (
        "archive_page" if resolved.source_kind in {"zip", "cbz"} else "page_preview"
    )
    return {
        "png": png,
        "width": width,
        "height": height,
        "grant_id": grant_id,
        "source_id": binding["source_id"],
        "version_id": binding["accepted_source_version"],
        "entry_id": binding["entry_id"],
        "verified_digest": binding.get("verified_digest"),
        "cache": {
            "cache_key": cache_key,
            "rendition_kind": rendition_kind,
            "decoder_name": decoder_name,
            "decoder_version": decoder_version,
            "params_digest": params_digest,
            "size_bytes": len(png),
            "content_digest": hashlib.sha256(png).hexdigest(),
        },
    }
