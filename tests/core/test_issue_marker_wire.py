"""FEA-14-EDIT-1: Core wire face for issue markers (PREQ EDIT P16-P20)."""

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
from domain.books.entities import Book, Chapter  # noqa: E402
from domain.pages.entities import Page  # noqa: E402
from infrastructure.resource_channel.catalog_store import (  # noqa: E402
    ResourceCatalogStore, initialize_namespace,
)
from infrastructure.resource_channel.render_preview import RenderPreviewPublisher  # noqa: E402


def _rpc(server: CoreServiceServer, command: str, payload: dict) -> dict:
    raw = json.dumps({
        "protocol": PROTOCOL_NAME, "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
        "request_id": "edit-wire", "command": command, "payload": payload,
    })
    return server.dispatch_request(raw)[0]


def _server(tmp_path: Path):
    core = assemble_production_core(tmp_path / "data")
    derived_root = tmp_path / "derived"
    catalog_db = tmp_path / "catalog" / "catalog.sqlite"
    derived_root.mkdir(parents=True, exist_ok=True)
    catalog_db.parent.mkdir(parents=True, exist_ok=True)
    initialize_namespace(catalog_db, derived_root)
    server = CoreServiceServer(
        core, stdout=io.StringIO(),
        render_previews=RenderPreviewPublisher(derived_root, ResourceCatalogStore(catalog_db)),
    )
    return core, server


def _seed(core) -> None:
    core.repository.add_book(Book(book_id="book-1", title="Marker Book"))
    core.repository.add_chapter(Chapter(chapter_id="chapter-1", book_id="book-1", title="Ch 1"))
    core.repository.add_page(Page(
        page_id="page-1",
        chapter_id="chapter-1",
        source_filename="1.png",
        source_order=1,
        sort_order=1,
        source_hash="hash-1",
        source_size_bytes=1,
        width=10,
        height=10,
        managed_original_ref="books/book-1/chapters/chapter-1/1.png",
    ))


def test_issue_marker_wire_roundtrip(tmp_path):
    core, server = _server(tmp_path)
    _seed(core)

    empty = _rpc(server, "ListIssueMarkers", {"book_id": "book-1"})
    assert empty["error"] is None and empty["result"] == {"markers": []}

    created = _rpc(server, "CreateIssueMarker", {
        "book_id": "book-1", "chapter_id": "chapter-1", "page_id": "page-1",
        "kind": "translation-check", "note": "review this bubble",
    })
    assert created["error"] is None, created["error"]
    marker_id = created["result"]["marker_id"]
    assert isinstance(marker_id, str) and marker_id

    positioned = _rpc(server, "CreateIssueMarker", {
        "book_id": "book-1", "chapter_id": "chapter-1", "page_id": "page-1",
        "kind": "sfx", "position": {"x": 0.25, "y": 0.75},
    })
    assert positioned["error"] is None, positioned["error"]
    positioned_id = positioned["result"]["marker_id"]

    listed = _rpc(server, "ListIssueMarkers", {"book_id": "book-1"})
    assert listed["error"] is None
    markers = listed["result"]["markers"]
    # P16 ordering is stable: created_at then marker_id (same-millisecond creates
    # can therefore order either way, so compare as a set + the declared key).
    assert {marker["marker_id"] for marker in markers} == {marker_id, positioned_id}
    assert markers == sorted(markers, key=lambda marker: (marker["created_at"], marker["marker_id"]))
    by_id = {marker["marker_id"]: marker for marker in markers}
    markers = [by_id[marker_id], by_id[positioned_id]]
    # PREQ §8 P16 shape: position only on point markers, note always present.
    assert set(markers[0]) == {
        "marker_id", "chapter_id", "page_id", "kind", "note", "state", "created_at",
    }
    assert markers[0]["state"] == "open" and markers[0]["note"] == "review this bubble"
    assert set(markers[1]) == {
        "marker_id", "chapter_id", "page_id", "position", "kind", "note", "state", "created_at",
    }
    assert markers[1]["position"] == {"x": 0.25, "y": 0.75}

    resolved = _rpc(server, "ResolveIssueMarker", {"marker_id": marker_id})
    assert resolved["error"] is None and resolved["result"] == {"resolved": True}
    open_ids = {
        marker["marker_id"]
        for marker in _rpc(server, "ListIssueMarkers", {"book_id": "book-1"})["result"]["markers"]
    }
    assert open_ids == {positioned_id}
    resolved_list = _rpc(server, "ListIssueMarkers", {"book_id": "book-1", "state": "resolved"})
    assert [m["marker_id"] for m in resolved_list["result"]["markers"]] == [marker_id]
    assert "resolved_at" in resolved_list["result"]["markers"][0]

    reopened = _rpc(server, "ReopenIssueMarker", {"marker_id": marker_id})
    assert reopened["error"] is None and reopened["result"] == {"reopened": True}
    deleted = _rpc(server, "DeleteIssueMarker", {"marker_id": positioned_id})
    assert deleted["error"] is None and deleted["result"] == {"deleted": True}
    remaining = _rpc(server, "ListIssueMarkers", {"book_id": "book-1"})["result"]["markers"]
    assert [marker["marker_id"] for marker in remaining] == [marker_id]


def test_issue_marker_wire_errors_are_typed(tmp_path):
    core, server = _server(tmp_path)
    _seed(core)

    missing_book = _rpc(server, "ListIssueMarkers", {"book_id": "nope"})
    assert missing_book["error"] is not None
    assert missing_book["error"]["code"] == "TARGET_NOT_FOUND"
    assert missing_book["error"]["category"] == "not_found"

    bad_state = _rpc(server, "ListIssueMarkers", {"book_id": "book-1", "state": "deleted"})
    assert bad_state["error"]["code"] == "INVALID_REQUEST"

    for bad_position in ({"x": 2.0, "y": 0.5}, {"x": 0.5}, {"x": 0.5, "y": 0.5, "z": 0.0}, "0.5,0.5"):
        response = _rpc(server, "CreateIssueMarker", {
            "book_id": "book-1", "chapter_id": "chapter-1", "page_id": "page-1",
            "kind": "kind", "position": bad_position,
        })
        assert response["error"] is not None, bad_position
        assert response["error"]["code"] == "INVALID_REQUEST", (bad_position, response["error"])

    missing_page = _rpc(server, "CreateIssueMarker", {
        "book_id": "book-1", "chapter_id": "chapter-1", "page_id": "nope", "kind": "kind",
    })
    assert missing_page["error"]["code"] == "TARGET_NOT_FOUND"

    unknown_field = _rpc(server, "ListIssueMarkers", {"book_id": "book-1", "extra": 1})
    assert unknown_field["error"]["code"] == "INVALID_REQUEST"

    for command in ("ResolveIssueMarker", "ReopenIssueMarker", "DeleteIssueMarker"):
        response = _rpc(server, command, {"marker_id": "nope"})
        assert response["error"] is not None, command
        assert response["error"]["code"] == "TARGET_NOT_FOUND", (command, response["error"])
