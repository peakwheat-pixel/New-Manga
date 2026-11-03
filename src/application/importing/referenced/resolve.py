"""Referenced page -> rendition resolution (C-15 §4.2).

The resolve path for a referenced page must go through the source-read grant
registry (no arbitrary-path fallback) and must publish a decoded/re-encoded
rendition, never the raw user-source bytes. This module implements the
application-side half; bootstrap owns publication into the derived root.

R1-I008 splits authorization/metadata preparation from the decode so the
bootstrap can drive the constrained ``RenditionCache`` (budget/LRU/active
references/crash recovery) before any pixel buffer is allocated.
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


def _rendition_kind(source_kind: str) -> str:
    if source_kind == "pdf":
        return "pdf_raster"
    if source_kind in {"zip", "cbz"}:
        return "archive_page"
    return "page_preview"


def prepare_referenced_rendition(page_id: str, *, repository, access) -> dict:
    """Authorize one referenced page and derive its cache identity (no decode).

    Raises typed :class:`SourceImportError` when the binding is unhealthy, the
    entry is missing, no live grant covers the source, or the source kind is
    unsupported. Authorization failures never fall back to another path.
    """
    binding = repository.get_page_binding(page_id)
    if not binding or binding.get("status") != "healthy":
        raise SourceImportError("SOURCE_ACCESS_DENIED", "page binding is not healthy")
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
    # R1-I002: the read face only honors a grant that imported exactly this
    # (source, accepted version, entry). No path/identity fallback.
    find_bound = getattr(access, "find_bound_for_source", None)
    if find_bound is not None:
        grant_id, resolved = find_bound(
            binding["source_id"],
            binding["accepted_source_version"],
            binding["entry_id"],
        )
    else:
        grant_id, resolved = access.find_for_source(binding["source_id"])
    if int(binding.get("authorization_generation") or 0) > int(
        getattr(resolved, "generation", 0)
    ):
        raise SourceImportError(
            "SOURCE_GRANT_REVOKED",
            "binding generation is newer than the live grant",
        )

    width = int(row.get("width") or 0)
    height = int(row.get("height") or 0)
    if width <= 0 or height <= 0:
        page = repository.get_page(page_id)
        if page is None:
            raise SourceImportError(
                "SOURCE_ENTRY_MISSING", "referenced page dimensions are missing"
            )
        width, height = int(page.width), int(page.height)

    decoder_name, decoder_version = _decoder_identity(resolved.source_kind)
    params = {"kind": resolved.source_kind, **RENDITION_PARAMS}
    params_digest = hashlib.sha256(
        json.dumps(params, sort_keys=True, separators=(",", ":")).encode("utf-8")
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
    return {
        "binding": binding,
        "entry": entry,
        "resolved": resolved,
        "grant_id": grant_id,
        "source_id": binding["source_id"],
        "version_id": binding["accepted_source_version"],
        "entry_id": binding["entry_id"],
        "verified_digest": binding.get("verified_digest"),
        "width": width,
        "height": height,
        "max_decode_bytes": int(
            getattr(resolved.budget, "max_decode_bytes", 0) or 0
        ),
        "decoder_name": decoder_name,
        "decoder_version": decoder_version,
        "params": params,
        "params_digest": params_digest,
        "cache_key": cache_key,
        "rendition_kind": _rendition_kind(resolved.source_kind),
    }


def render_prepared_rendition(
    prepared: dict,
    *,
    image_decoder=None,
    document_raster=None,
    password: bytes | None = None,
) -> tuple[bytes, int, int]:
    """Decode/re-encode the prepared entry as a PNG rendition."""
    return render_entry_png(
        prepared["resolved"],
        prepared["entry"],
        image_decoder=image_decoder,
        document_raster=document_raster,
        password=password,
    )


def resolve_referenced_rendition(
    page_id: str,
    *,
    repository,
    access,
    image_decoder=None,
    document_raster=None,
) -> dict:
    """Return ``{png, width, height, cache, ...}`` for one referenced page.

    Compatibility composition (prepare + unconditional decode); the bootstrap
    read face uses :func:`prepare_referenced_rendition` with the cache.
    """
    prepared = prepare_referenced_rendition(
        page_id, repository=repository, access=access
    )
    png, width, height = render_prepared_rendition(
        prepared,
        image_decoder=image_decoder,
        document_raster=document_raster,
    )
    return {
        "png": png,
        "width": width,
        "height": height,
        "grant_id": prepared["grant_id"],
        "source_id": prepared["source_id"],
        "version_id": prepared["version_id"],
        "entry_id": prepared["entry_id"],
        "verified_digest": prepared["verified_digest"],
        "cache": {
            "cache_key": prepared["cache_key"],
            "rendition_kind": prepared["rendition_kind"],
            "decoder_name": prepared["decoder_name"],
            "decoder_version": prepared["decoder_version"],
            "params_digest": prepared["params_digest"],
            "size_bytes": len(png),
            "content_digest": hashlib.sha256(png).hexdigest(),
        },
    }
