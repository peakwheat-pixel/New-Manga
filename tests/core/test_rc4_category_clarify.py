"""M2-CATEGORY-CLARIFY-1: MISSING_REQUIRED_INPUT envelope category.

Pins the RC4-10 clarification on the wire envelope: a rerender blocked by
a missing required input is an AVAILABILITY failure (data not there,
``category="unavailable"`` per the §8 taxonomy), not a "target does not
exist" one (``not_found`` stays reserved for TARGET_NOT_FOUND). Neither
contract ever froze this category value (RC-4 r1 RC4-10, taxonomy
Proposal), so this is a clarification, not a revision.
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
from domain.regions.entities import BBox, RegionGeometry

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


def _seed_page_with_region(tmp_path: Path):
    """One imported page carrying a region but NO clean artifact -- the
    exact MISSING_REQUIRED_INPUT shape (rendering service blocks with
    ``missing_clean_artifact``)."""
    core = assemble_production_core(tmp_path / "data")
    with core.conn:
        core.conn.execute(
            "INSERT INTO books (book_id,title,created_at,updated_at) VALUES ('book','b',?,?)",
            (NOW, NOW),
        )
        core.conn.execute(
            "INSERT INTO chapters (chapter_id,book_id,title,chapter_number,sort_order,created_at,updated_at)"
            " VALUES ('chapter-1','book','first','1',1,?,?)",
            (NOW, NOW),
        )
    buffer = io.BytesIO()
    Image.new("RGBA", (64, 40), (30, 60, 200, 255)).save(buffer, format="PNG")
    report = core.importer.import_files(
        "chapter-1", [ImportSource("page-a.png", buffer.getvalue)]
    )
    assert not report.failed and len(report.imported) == 1
    page_id = report.imported[0].page.page_id
    region = core.editing.create_region(
        page_id, RegionGeometry(bbox=BBox(10, 10, 40, 20))
    )
    return core, page_id, region.region_id


def test_missing_required_input_carries_unavailable_category(tmp_path) -> None:
    core, page_id, _region_id = _seed_page_with_region(tmp_path)
    server = CoreServiceServer(core)
    try:
        res, _ = server.dispatch_request(
            _rpc("rerender_page", "r-1", {"page_id": page_id})
        )
        assert res["result"] is None, res
        error = res["error"]
        assert error is not None, res
        assert error["code"] == "MISSING_REQUIRED_INPUT"
        # the clarification itself: availability, not existence
        assert error["category"] == "unavailable"
        assert error["message"] == "required render input is missing"
    finally:
        core.conn.close()


def test_target_not_found_keeps_not_found_category(tmp_path) -> None:
    core = assemble_production_core(tmp_path / "data")
    server = CoreServiceServer(core)
    try:
        res, _ = server.dispatch_request(
            _rpc("rerender_page", "r-2", {"page_id": "no-such-page"})
        )
        error = res["error"]
        assert error is not None, res
        # the mapping split must not disturb the genuine not-found row
        assert error["code"] == "TARGET_NOT_FOUND"
        assert error["category"] == "not_found"
    finally:
        core.conn.close()
