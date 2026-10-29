"""V11R-F0-1 I2/P2-D: a DB fault must not masquerade as an optimistic conflict.

The r2 review found ``_guard_status_of`` mapped every non-applied commit status
to ``INPUT_REVISION_CHANGED`` (except LOCK_CHANGED). A ``busy``/IO failure
therefore surfaced on the wire as a conflict ("refresh and retry") instead of
UNKNOWN/internal with a fixed safe phrase.

The fix keeps ``GuardStatus.DB_FAILED`` as its own status; the wire-level
region write branch maps it to ``UNKNOWN`` / category ``internal`` /
message "Region write failed" (no raw SQLite text, no path), with zero write.
"""

from __future__ import annotations

import io
import json
from pathlib import Path
import sqlite3
import sys

import pytest
from PIL import Image

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from application.editing.errors import GuardStatus  # noqa: E402
from application.importing.images.ports import ImportSource  # noqa: E402
from bootstrap.core_service import (  # noqa: E402
    PROTOCOL_MAJOR,
    PROTOCOL_MINOR,
    CoreServiceServer,
    assemble_production_core,
)
from domain.regions.entities import BBox, RegionGeometry  # noqa: E402

NOW = "2026-01-01T00:00:00.000+00:00"
RECT = RegionGeometry(bbox=BBox(10, 10, 100, 60))


def _seed_page(core) -> str:
    with core.conn:
        core.conn.execute(
            "INSERT INTO books (book_id,title,created_at,updated_at)"
            " VALUES ('book','b',?,?)",
            (NOW, NOW),
        )
        core.conn.execute(
            "INSERT INTO chapters (chapter_id,book_id,title,created_at,updated_at)"
            " VALUES ('chapter','book','c',?,?)",
            (NOW, NOW),
        )
    buffer = io.BytesIO()
    Image.new("RGBA", (400, 600), (40, 80, 120, 255)).save(buffer, format="PNG")
    payload = buffer.getvalue()
    report = core.importer.import_files(
        "chapter", [ImportSource("dbfail.png", lambda: payload)]
    )
    assert not report.failed and len(report.imported) == 1, report
    return report.imported[0].page.page_id


@pytest.fixture()
def core(tmp_path: Path):
    assembled = assemble_production_core(tmp_path / "data")
    try:
        yield assembled
    finally:
        assembled.conn.close()


def _rpc(server, command: str, payload: dict) -> dict:
    line = json.dumps({
        "protocol": "new-manga.core",
        "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
        "request_id": f"i2-db-{command}",
        "command": command,
        "payload": payload,
    })
    response, exit_flag = server.dispatch_request(line)
    assert not exit_flag
    return response


def _revision_count(core, region_id: str) -> int:
    return core.conn.execute(
        "SELECT COUNT(*) FROM region_revisions WHERE region_id = ?",
        (region_id,),
    ).fetchone()[0]


def _inject_busy(repo):
    def explode(_revision):
        raise sqlite3.OperationalError("database is locked")

    repo._insert_revision = explode  # instance-level fault injection seam


def test_save_geometry_db_failure_keeps_its_own_status(core):
    page_id = _seed_page(core)
    region = core.editing.create_region(page_id, RECT)
    _inject_busy(core.editing._committer)

    outcome = core.editing.save_geometry(
        region.region_id, RegionGeometry(bbox=BBox(20, 20, 50, 30))
    )

    assert outcome.status is GuardStatus.DB_FAILED
    assert outcome.status is not GuardStatus.INPUT_REVISION_CHANGED
    # Zero write: the revision count and persisted geometry are unchanged.
    assert _revision_count(core, region.region_id) == 1
    stored = core.editing.get_region(region.region_id)
    assert stored.geometry.bbox == RECT.bbox


def test_wire_save_geometry_db_failure_is_unknown_not_conflict(core):
    page_id = _seed_page(core)
    server = CoreServiceServer(core)
    region = _rpc(server, "create_region", {
        "page_id": page_id, "geometry": {"points": [[0.1, 0.1], [0.3, 0.3]]},
    })["result"]
    revisions_before = _revision_count(core, region["region_id"])
    _inject_busy(core.editing._committer)

    response = _rpc(server, "save_region_geometry", {
        "region_id": region["region_id"],
        "geometry": {"points": [[0.2, 0.2], [0.4, 0.4]]},
    })

    error = response["error"]
    assert error is not None
    assert error["code"] == "UNKNOWN"
    assert error["category"] == "internal"
    assert error["message"] == "Region write failed"
    assert error["retryable"] is False
    # No raw SQLite text / path on the wire.
    assert "locked" not in error["message"].lower()
    assert "sqlite" not in error["message"].lower()
    assert _revision_count(core, region["region_id"]) == revisions_before


def test_wire_create_region_db_failure_is_unknown_with_no_orphan(core):
    page_id = _seed_page(core)
    server = CoreServiceServer(core)
    _inject_busy(core.editing._committer)

    response = _rpc(server, "create_region", {
        "page_id": page_id, "geometry": {"points": [[0.1, 0.1], [0.3, 0.3]]},
    })
    assert response["error"]["code"] == "UNKNOWN"
    # The batch rolled back: no orphan region row and no revision.
    assert core.conn.execute(
        "SELECT COUNT(*) FROM regions WHERE page_id = ?", (page_id,)
    ).fetchone()[0] == 0
    assert core.conn.execute(
        "SELECT COUNT(*) FROM region_revisions"
    ).fetchone()[0] == 0


def test_set_region_type_db_failure_stays_internal(core):
    page_id = _seed_page(core)
    server = CoreServiceServer(core)
    region = _rpc(server, "create_region", {
        "page_id": page_id, "geometry": {"points": [[0.1, 0.1], [0.3, 0.3]]},
    })["result"]
    _inject_busy(core.editing._committer)

    response = _rpc(server, "set_region_type", {
        "region_id": region["region_id"], "new_region_type": "narration",
    })
    assert response["error"]["code"] == "UNKNOWN"
    assert response["error"]["category"] == "internal"
