"""FEA-14-FONT-1: Core wire face for the font library (PREQ P1-P4)."""

from __future__ import annotations

import io
import json
from pathlib import Path
import sys

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from bootstrap.core_service import (  # noqa: E402
    PROTOCOL_MAJOR, PROTOCOL_MINOR, PROTOCOL_NAME, CoreServiceServer, assemble_production_core,
)
from infrastructure.resource_channel.catalog_store import (  # noqa: E402
    ResourceCatalogStore, initialize_namespace,
)
from infrastructure.resource_channel.render_preview import RenderPreviewPublisher  # noqa: E402


def _rpc(server: CoreServiceServer, command: str, payload: dict) -> dict:
    raw = json.dumps({
        "protocol": PROTOCOL_NAME, "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
        "request_id": "font-wire", "command": command, "payload": payload,
    })
    return server.dispatch_request(raw)[0]


def _server(tmp_path: Path) -> CoreServiceServer:
    core = assemble_production_core(tmp_path / "data")
    derived_root = tmp_path / "derived"
    catalog_db = tmp_path / "catalog" / "catalog.sqlite"
    derived_root.mkdir(parents=True, exist_ok=True)
    catalog_db.parent.mkdir(parents=True, exist_ok=True)
    initialize_namespace(catalog_db, derived_root)
    return CoreServiceServer(
        core, stdout=io.StringIO(),
        render_previews=RenderPreviewPublisher(derived_root, ResourceCatalogStore(catalog_db)),
    )


def _font(tmp_path: Path) -> Path:
    path = tmp_path / "WireFont-Bold.ttf"
    path.write_bytes(b"\x00\x01\x00\x00" + b"FONT" * 8)
    return path


def test_font_wire_import_list_delete(tmp_path):
    server = _server(tmp_path)
    empty = _rpc(server, "ListFontAssets", {})
    assert empty["error"] is None
    assert empty["result"]["assets"] == []

    imported = _rpc(server, "ImportFontAsset", {"source_path": str(_font(tmp_path)), "license_note": "ofl"})
    assert imported["error"] is None
    asset_id = imported["result"]["asset_id"]
    assert imported["result"]["family"] == "WireFont"

    listed = _rpc(server, "ListFontAssets", {})
    assert [item["asset_id"] for item in listed["result"]["assets"]] == [asset_id]

    deleted = _rpc(server, "DeleteFontAsset", {"asset_id": asset_id})
    assert deleted["result"]["deleted"] is True
    # R1-002: deleting an unknown/already-deleted asset is a typed error.
    again = _rpc(server, "DeleteFontAsset", {"asset_id": asset_id})
    assert again["error"] is not None and again["error"]["code"] == "FONT_NOT_FOUND"


def test_font_wire_refresh_and_invalid_payloads(tmp_path):
    server = _server(tmp_path)
    imported = _rpc(server, "ImportFontAsset", {"source_path": str(_font(tmp_path))})
    assert imported["error"] is None
    refreshed = _rpc(server, "RefreshFontAssets", {})
    assert refreshed["error"] is None
    assert refreshed["result"]["available"] >= 1
    assert refreshed["result"]["failed"] == []

    invalid = _rpc(server, "ImportFontAsset", {})
    assert invalid["error"] is not None and invalid["error"]["code"] == "INVALID_REQUEST"
    missing = _rpc(server, "ImportFontAsset", {"source_path": str(tmp_path / "nope.ttf")})
    assert missing["error"] is not None and missing["error"]["code"] == "FONT_SOURCE_INVALID"


# MAINT-2-C1-BATCH-1 AC2 (C1-2 / L-F1-2): the STORAGE layer already pins
# FONT_DELETE_FAILED (tests/storage/test_fonts.py::test_delete_reports_typed_failure_when_managed_copy_is_stuck);
# the WIRE layer did not, so a regression in the error mapping would only surface in production.
# This test drives the real command handler end to end: a stuck managed copy must come back as the
# typed FONT_DELETE_FAILED (not a generic failure), and the row must stay active so the delete can
# be retried -- then the retry must succeed.
def test_font_wire_delete_failure_is_typed_and_retryable(tmp_path):
    server = _server(tmp_path)
    imported = _rpc(server, "ImportFontAsset", {"source_path": str(_font(tmp_path))})
    assert imported["error"] is None, imported["error"]
    asset_id = imported["result"]["asset_id"]

    managed_root = tmp_path / "data" / "fonts"
    managed_files = list(managed_root.iterdir())
    assert len(managed_files) == 1, managed_files
    managed = managed_files[0]

    # R2-002: a read-only managed copy cannot be removed on Windows.
    managed.chmod(0o444)
    try:
        failed = _rpc(server, "DeleteFontAsset", {"asset_id": asset_id})
        assert failed["error"] is not None, "stuck managed copy must not report success"
        assert failed["error"]["code"] == "FONT_DELETE_FAILED", failed["error"]
        # Existing projection (core_service.handle_delete_font_asset): only FONT_NOT_FOUND maps
        # to not_found; an IO failure such as a stuck copy is `internal` (it is not a bad input).
        assert failed["error"]["category"] == "internal", failed["error"]
        # R3-001: the row stays active so the delete can be retried.
        still_there = _rpc(server, "ListFontAssets", {})
        assert [item["asset_id"] for item in still_there["result"]["assets"]] == [asset_id]
    finally:
        managed.chmod(0o666)

    retried = _rpc(server, "DeleteFontAsset", {"asset_id": asset_id})
    assert retried["error"] is None, retried["error"]
    assert retried["result"]["deleted"] is True
    assert _rpc(server, "ListFontAssets", {})["result"]["assets"] == []