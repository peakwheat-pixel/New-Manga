"""M2-PAGE-NAV-PROJECTION-1 wire-level evidence for list_chapters /
list_chapter_pages.

Pins the page-navigation read face (contract M2-C1 rev 1.8 §5): the
minimal navigation summary shapes, the ``sort_order`` ascending order
(D03 AC-PAGE-001), the fail-soft EMPTY list for unknown parent ids (the
list_regions P3-4 precedent), the payload validation row, and the
protocol minor bump 5 -> 6.
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


def _seed_core(tmp_path: Path) -> CoreServiceServer:
    """One book, two chapters (reverse-name order, explicit sort_order),
    two pages in the second chapter imported in one call."""
    core = assemble_production_core(tmp_path / "data")
    with core.conn:
        core.conn.execute(
            "INSERT INTO books (book_id,title,created_at,updated_at) VALUES ('book','b',?,?)",
            (NOW, NOW),
        )
        core.conn.execute(
            "INSERT INTO chapters (chapter_id,book_id,title,chapter_number,sort_order,created_at,updated_at)"
            " VALUES ('chapter-2','book','second','2',2,?,?)",
            (NOW, NOW),
        )
        core.conn.execute(
            "INSERT INTO chapters (chapter_id,book_id,title,chapter_number,sort_order,created_at,updated_at)"
            " VALUES ('chapter-1','book','first','1',1,?,?)",
            (NOW, NOW),
        )
    for name, color in (("page-a", (30, 60, 200, 255)), ("page-b", (200, 60, 30, 255))):
        buffer = io.BytesIO()
        Image.new("RGBA", (64, 40), color).save(buffer, format="PNG")
        core.importer.import_files(
            "chapter-2", [ImportSource(f"{name}.png", buffer.getvalue)]
        )
    return core


def test_ping_carries_protocol_minor_6(tmp_path) -> None:
    core = assemble_production_core(tmp_path / "data")
    core.conn.close()
    server = CoreServiceServer(core)
    res, _ = server.dispatch_request(_rpc("core.ping", "p-1", {}))
    assert res["error"] is None
    assert res["result"]["protocol_version"] == {"major": PROTOCOL_MAJOR, "minor": 6}


def test_list_chapters_returns_sorted_projection(tmp_path) -> None:
    core = _seed_core(tmp_path)
    server = CoreServiceServer(core)
    try:
        res, _ = server.dispatch_request(
            _rpc("list_chapters", "r-1", {"book_id": "book"})
        )
        assert res["error"] is None, res["error"]
        rows = res["result"]["chapters"]
        # sorted by the user's sort_order (1 then 2), NOT by insertion/name
        assert [row["chapter_id"] for row in rows] == ["chapter-1", "chapter-2"]
        assert rows[0] == {
            "chapter_id": "chapter-1",
            "title": "first",
            "chapter_number": "1",
            "sort_order": 1,
        }
        # the navigation projection carries no Reader semantics
        assert set(rows[1].keys()) == {"chapter_id", "title", "chapter_number", "sort_order"}
    finally:
        core.conn.close()


def test_list_chapter_pages_returns_sorted_projection(tmp_path) -> None:
    core = _seed_core(tmp_path)
    server = CoreServiceServer(core)
    try:
        res, _ = server.dispatch_request(
            _rpc("list_chapter_pages", "r-1", {"chapter_id": "chapter-2"})
        )
        assert res["error"] is None, res["error"]
        rows = res["result"]["pages"]
        assert [row["source_filename"] for row in rows] == ["page-a.png", "page-b.png"]
        assert rows[0]["sort_order"] < rows[1]["sort_order"]
        # uuid page ids + the navigation summary shape only
        assert set(rows[0].keys()) == {"page_id", "source_filename", "sort_order"}
        assert all(row["page_id"] for row in rows)
    finally:
        core.conn.close()


def test_unknown_parent_ids_return_empty_arrays(tmp_path) -> None:
    # list_regions P3-4 precedent: a missing parent is EMPTY data (soft),
    # not an error -- the navigation UI renders "no entries".
    core = _seed_core(tmp_path)
    server = CoreServiceServer(core)
    try:
        res, _ = server.dispatch_request(
            _rpc("list_chapters", "r-1", {"book_id": "no-such-book"})
        )
        assert res["error"] is None
        assert res["result"] == {"chapters": []}

        res, _ = server.dispatch_request(
            _rpc("list_chapter_pages", "r-2", {"chapter_id": "no-such-chapter"})
        )
        assert res["error"] is None
        assert res["result"] == {"pages": []}
    finally:
        core.conn.close()


def test_validation_rejects_missing_ids(tmp_path) -> None:
    core = _seed_core(tmp_path)
    server = CoreServiceServer(core)
    try:
        for payload in ({}, {"book_id": ""}, {"book_id": 7}):
            res, _ = server.dispatch_request(
                _rpc("list_chapters", "r-1", payload)
            )
            assert res["result"] is None
            assert res["error"]["code"] == "INVALID_REQUEST"
            assert res["error"]["category"] == "validation"

        for payload in ({}, {"chapter_id": ""}, {"chapter_id": None}):
            res, _ = server.dispatch_request(
                _rpc("list_chapter_pages", "r-1", payload)
            )
            assert res["result"] is None
            assert res["error"]["code"] == "INVALID_REQUEST"
            assert res["error"]["category"] == "validation"
    finally:
        core.conn.close()
