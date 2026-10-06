"""M2-PAGE-RESOURCE-RESOLVE-1 wire-level evidence for resolve_page_resource.

Pins the page -> resource catalog-key face: deterministic idempotent key
(``page-original-{page_id}``), byte-for-byte publication of the immutable
managed original into the derived read-only root, the PAGE_NOT_FOUND
fail-closed rows (unknown page, page without a managed original), the
validation row, and the protocol minor bump 4 -> 5.
"""

from __future__ import annotations

import io
import json
import sys
from pathlib import Path

from PIL import Image

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from application.importing.images.ports import ImportSource
from bootstrap.core_service import (
    PROTOCOL_MAJOR,
    PROTOCOL_MINOR,
    CoreServiceServer,
    assemble_production_core,
)
from infrastructure.resource_channel.catalog_store import ResourceCatalogStore
from infrastructure.resource_channel.render_preview import RenderPreviewPublisher

NOW = "2026-01-01T00:00:00.000+00:00"


def _rpc(command: str, request_id: str, payload: dict) -> str:
    return json.dumps(
        {
            "protocol": "new-manga.core",
            "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
            "request_id": request_id,
            "command": command,
            "payload": payload,
        }
    )


def _seed_page(tmp_path: Path, *, suffix: str = ".png"):
    """One book/chapter/page imported through the real Managed Copy face."""
    core = assemble_production_core(tmp_path / "data")
    with core.conn:
        core.conn.execute(
            "INSERT INTO books (book_id,title,created_at,updated_at) VALUES ('book','b',?,?)",
            (NOW, NOW),
        )
        core.conn.execute(
            "INSERT INTO chapters (chapter_id,book_id,title,created_at,updated_at)"
            " VALUES ('chapter','book','c',?,?)",
            (NOW, NOW),
        )
    source_path = tmp_path / f"page-resolve-source{suffix}"
    buffer = io.BytesIO()
    Image.new("RGBA", (64, 40), (30, 60, 200, 255)).save(buffer, format="PNG")
    source_path.write_bytes(buffer.getvalue())
    report = core.importer.import_files(
        "chapter", [ImportSource(f"source{suffix}", source_path.read_bytes)]
    )
    assert not report.failed and len(report.imported) == 1
    page = core.repository.get_page(report.imported[0].page.page_id)
    assert page is not None and page.managed_original_ref
    return core, page.page_id, source_path.read_bytes()


def _server(core, tmp_path: Path) -> CoreServiceServer:
    catalog_db = tmp_path / "catalog" / "catalog.sqlite"
    catalog_db.parent.mkdir(parents=True, exist_ok=True)
    catalog = ResourceCatalogStore(catalog_db)
    return CoreServiceServer(
        core,
        render_previews=RenderPreviewPublisher(tmp_path / "derived", catalog),
    )


def test_ping_carries_protocol_minor_5(tmp_path) -> None:
    core = assemble_production_core(tmp_path / "data")
    core.conn.close()
    server = CoreServiceServer(core)
    res, _ = server.dispatch_request(_rpc("core.ping", "p-1", {}))
    assert res["error"] is None
    assert res["result"]["protocol_version"] == {"major": PROTOCOL_MAJOR, "minor": 5}


def test_first_resolve_publishes_and_later_resolves_are_idempotent(tmp_path) -> None:
    core, page_id, source_bytes = _seed_page(tmp_path)
    server = _server(core, tmp_path)
    try:
        res, _ = server.dispatch_request(
            _rpc("resolve_page_resource", "r-1", {"page_id": page_id})
        )
        assert res["error"] is None, res["error"]
        first = res["result"]
        assert first == {
            "resource_id": f"page-original-{page_id}",
            "revision": "original",
        }

        res, _ = server.dispatch_request(
            _rpc("resolve_page_resource", "r-2", {"page_id": page_id})
        )
        assert res["error"] is None, res["error"]
        assert res["result"] == first, "idempotent key must not drift"

        # The published artifact is byte-for-byte the managed original and
        # the catalog row is servable (derived-read-only scope, F-03 gate).
        published = tmp_path / "derived" / "pages" / f"{first['resource_id']}.png"
        assert published.is_file()
        assert published.read_bytes() == source_bytes
        catalog = ResourceCatalogStore(tmp_path / "catalog" / "catalog.sqlite")
        try:
            entry = catalog.lookup(first["resource_id"])
            assert entry is not None
            assert entry.scope_class == "derived-read-only"
            assert entry.rel_path == f"pages/{first['resource_id']}.png"
        finally:
            catalog.close()
    finally:
        core.conn.close()


def test_unknown_page_fails_closed_page_not_found(tmp_path) -> None:
    core, _page_id, _bytes = _seed_page(tmp_path)
    server = _server(core, tmp_path)
    try:
        res, _ = server.dispatch_request(
            _rpc("resolve_page_resource", "r-1", {"page_id": "no-such-page"})
        )
        assert res["result"] is None
        assert res["error"]["code"] == "PAGE_NOT_FOUND"
        assert res["error"]["category"] == "not_found"
        assert res["error"]["retryable"] is False
    finally:
        core.conn.close()


def test_validation_rejects_missing_page_id(tmp_path) -> None:
    core, _page_id, _bytes = _seed_page(tmp_path)
    server = _server(core, tmp_path)
    try:
        for payload in ({}, {"page_id": ""}, {"page_id": 7}):
            res, _ = server.dispatch_request(
                _rpc("resolve_page_resource", "r-1", payload)
            )
            assert res["result"] is None
            assert res["error"]["code"] == "INVALID_REQUEST"
            assert res["error"]["category"] == "validation"
    finally:
        core.conn.close()
