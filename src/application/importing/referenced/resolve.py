"""Referenced page -> rendition resolution (C-15 §4.2).

The resolve path for a referenced page must go through the source-read grant
registry (no arbitrary-path fallback) and must publish a decoded/re-encoded
rendition, never the raw user-source bytes. This module implements the
application-side half; bootstrap owns publication into the derived root.
"""

from __future__ import annotations

from application.importing.referenced.errors import SourceImportError
from application.importing.referenced.model import ScannedEntry
from application.importing.referenced.reader import render_entry_png


def resolve_referenced_rendition(
    page_id: str,
    *,
    repository,
    access,
    image_decoder=None,
    document_raster=None,
) -> dict:
    """Return ``{png, width, height, ...}`` for one referenced page.

    Raises typed :class:`SourceImportError` when the binding is unhealthy, the
    entry is missing, no live grant covers the source, or the source kind is
    unsupported. Authorization failures never fall back to another path.
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
    grant_id, resolved = access.find_for_source(binding["source_id"])
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
    return {
        "png": png,
        "width": width,
        "height": height,
        "grant_id": grant_id,
        "source_id": binding["source_id"],
        "version_id": binding["accepted_source_version"],
        "entry_id": binding["entry_id"],
        "verified_digest": binding.get("verified_digest"),
    }
