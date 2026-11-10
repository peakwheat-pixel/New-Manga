"""FEA-14-READ-1: Core wire face for preferences/bookmarks/whole-book progress (P9-P15)."""

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
        "request_id": "read-wire", "command": command, "payload": payload,
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


def test_preferences_wire_defaults_and_save(tmp_path):
    server = _server(tmp_path)
    response = _rpc(server, "GetReadingPreferences", {"book_id": "b1"})
    assert response["error"] is None
    assert response["result"]["is_default"] is True
    assert response["result"]["mode"] == "original"

    saved = _rpc(server, "SaveReadingPreferences", {
        "book_id": "b1",
        "prefs": {"mode": "translated", "direction": "rtl", "zoom": 1.5, "double_page": True, "layout": "double"},
    })
    assert saved["error"] is None and saved["result"]["saved"] is True
    assert saved["result"]["mode"] == "translated" and saved["result"]["double_page"] is True

    again = _rpc(server, "GetReadingPreferences", {"book_id": "b1"})
    assert again["result"]["zoom"] == 1.5 and again["result"]["direction"] == "rtl"

    invalid = _rpc(server, "SaveReadingPreferences", {"book_id": "b1", "prefs": {"mode": "bogus"}})
    assert invalid["error"] is not None and invalid["error"]["code"] == "INVALID_REQUEST"


def test_bookmarks_wire_create_list_delete(tmp_path):
    server = _server(tmp_path)
    created = _rpc(server, "CreateBookmark", {
        "book_id": "b1", "chapter_id": "c1", "page_id": "p1", "side": "left", "note": "keep",
    })
    assert created["error"] is None
    bookmark_id = created["result"]["bookmark_id"]
    assert bookmark_id

    listed = _rpc(server, "ListBookmarks", {"book_id": "b1"})
    assert listed["error"] is None
    assert [item["bookmark_id"] for item in listed["result"]["bookmarks"]] == [bookmark_id]
    assert listed["result"]["bookmarks"][0]["side"] == "left"

    deleted = _rpc(server, "DeleteBookmark", {"bookmark_id": bookmark_id})
    assert deleted["result"]["deleted"] is True
    again = _rpc(server, "DeleteBookmark", {"bookmark_id": bookmark_id})
    assert again["result"]["deleted"] is False
    assert _rpc(server, "ListBookmarks", {"book_id": "b1"})["result"]["bookmarks"] == []


def test_book_progress_and_reset_require_confirm(tmp_path):
    server = _server(tmp_path)
    progress = _rpc(server, "GetBookReadingProgress", {"book_id": "b1"})
    assert progress["error"] is None
    assert progress["result"]["total_pages"] == 0
    assert progress["result"]["finished"] is False

    missing_confirm = _rpc(server, "ResetReadingProgress", {"book_id": "b1"})
    assert missing_confirm["error"] is not None
    assert missing_confirm["error"]["code"] == "INVALID_REQUEST"

    reset = _rpc(server, "ResetReadingProgress", {"book_id": "b1", "confirm": True})
    assert reset["error"] is None
    assert reset["result"]["reset"] == 0

    invalid = _rpc(server, "GetReadingPreferences", {"book_id": ""})
    assert invalid["error"] is not None and invalid["error"]["code"] == "INVALID_REQUEST"


def test_book_progress_wire_is_page_based(tmp_path):
    server = _server(tmp_path)
    import sqlite3 as _sqlite
    conn = _sqlite.connect(tmp_path / "data" / "library.db")
    conn.execute(
        "INSERT INTO books (book_id, title, created_at, updated_at)"
        " VALUES ('bp', 'Book', '2026-01-01', '2026-01-01')"
    )
    conn.execute(
        "INSERT INTO chapters (chapter_id, book_id, title, chapter_type, sort_order, created_at, updated_at)"
        " VALUES ('bp-c1', 'bp', 'Ch 1', 'paged', 1, '2026-01-01', '2026-01-01')"
    )
    for index in (1, 2):
        conn.execute(
            "INSERT INTO pages (page_id, chapter_id, sort_order, created_at, updated_at)"
            " VALUES (?, 'bp-c1', ?, '2026-01-01', '2026-01-01')",
            (f"bp-p{index}", index),
        )
    conn.execute(
        "INSERT INTO reading_progress (progress_id, book_id, chapter_id, mode,"
        " last_page_id, scroll_offset_x, scroll_offset_y, progress_percent, updated_at)"
        " VALUES ('bp-r1', 'bp', 'bp-c1', 'original', 'bp-p1', 0.0, 0.0, 50.0, '2026-01-01')"
    )
    conn.commit()
    response = _rpc(server, "GetBookReadingProgress", {"book_id": "bp"})
    assert response["error"] is None
    assert response["result"]["total_pages"] == 2
    assert response["result"]["read_pages"] == 1
    assert response["result"]["percent"] == 50.0
    assert response["result"]["finished"] is False


def test_save_preferences_wire_is_partial_presence_based(tmp_path):
    server = _server(tmp_path)
    first = _rpc(server, "SaveReadingPreferences", {
        "book_id": "bw", "prefs": {"mode": "translated", "direction": "rtl", "zoom": 2.0, "layout": "double"},
    })
    assert first["error"] is None
    second = _rpc(server, "SaveReadingPreferences", {"book_id": "bw", "prefs": {"zoom": 1.25}})
    assert second["error"] is None
    read = _rpc(server, "GetReadingPreferences", {"book_id": "bw"})
    result = read["result"]
    assert result["zoom"] == 1.25
    assert result["mode"] == "translated" and result["direction"] == "rtl" and result["layout"] == "double"
    # Explicit defaults must reset (presence, not value-equality heuristic).
    reset = _rpc(server, "SaveReadingPreferences", {
        "book_id": "bw", "prefs": {"mode": "original", "direction": "ltr", "zoom": 1.0, "double_page": False, "layout": "single"},
    })
    assert reset["error"] is None
    again = _rpc(server, "GetReadingPreferences", {"book_id": "bw"})["result"]
    assert again["mode"] == "original" and again["direction"] == "ltr" and again["zoom"] == 1.0
