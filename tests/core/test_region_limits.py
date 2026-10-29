"""V11R-F0-1 I2/P2-E: bounded write inputs + concurrent-writer stress.

Every composite Region write runs inside ONE ``BEGIN IMMEDIATE`` transaction
with a 5 s busy timeout. Unbounded inputs (a 10k-vertex polygon, a thousand
split parts, a reorder list over the whole page) would hold the SQLite write
lock long enough to starve every other writer (BUSY), so the contract freezes
hard limits and rejects them fail-closed BEFORE any persistence:

    MAX_REGIONS_PER_PAGE = 500   (create / reorder list)
    MAX_REGION_IDS_PER_BATCH = 64 (merge)
    MAX_SPLIT_PARTS = 64
    MAX_GEOMETRY_POINTS = 512

The last test holds a real write lock on an independent connection and proves
a normal region write waits (bounded) instead of failing spuriously.
"""

from __future__ import annotations

import io
import json
from pathlib import Path
import sqlite3
import sys
import threading

import pytest
from PIL import Image

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from application.importing.images.ports import ImportSource  # noqa: E402
from bootstrap.core_service import (  # noqa: E402
    PROTOCOL_MAJOR,
    PROTOCOL_MINOR,
    CoreServiceServer,
    assemble_production_core,
)
from domain.regions.entities import BBox, RegionGeometry  # noqa: E402

NOW = "2026-01-01T00:00:00.000+00:00"


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
        "chapter", [ImportSource("limits.png", lambda: payload)]
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
        "request_id": f"i2-limits-{command}",
        "command": command,
        "payload": payload,
    })
    response, exit_flag = server.dispatch_request(line)
    assert not exit_flag
    return response


def _square(index: int) -> list[list[float]]:
    return [[0.1, 0.1], [0.9, 0.1], [0.9, 0.9]]


def _revision_count(core) -> int:
    return core.conn.execute(
        "SELECT COUNT(*) FROM region_revisions"
    ).fetchone()[0]


def _region_count(core) -> int:
    return core.conn.execute("SELECT COUNT(*) FROM regions").fetchone()[0]


def test_oversized_split_is_rejected_before_any_write(core):
    from application.editing.region_canvas import MAX_SPLIT_PARTS

    page_id = _seed_page(core)
    server = CoreServiceServer(core)
    source = _rpc(server, "create_region", {
        "page_id": page_id, "geometry": {"points": _square(0)},
    })["result"]
    revisions_before = _revision_count(core)
    regions_before = _region_count(core)
    parts = [_square(index) for index in range(MAX_SPLIT_PARTS + 1)]

    response = _rpc(server, "split_region", {
        "region_id": source["region_id"], "parts": parts,
    })
    assert response["error"]["code"] == "INVALID_REQUEST"
    assert response["error"]["category"] == "validation"
    assert _revision_count(core) == revisions_before
    assert _region_count(core) == regions_before
    # The source stays live: nothing was written.
    assert source["region_id"] in {
        region.region_id for region in core.editing.list_regions(page_id)
    }


def test_oversized_merge_is_rejected_before_any_write(core):
    from application.editing.region_canvas import MAX_REGION_IDS_PER_BATCH

    page_id = _seed_page(core)
    server = CoreServiceServer(core)
    source = _rpc(server, "create_region", {
        "page_id": page_id, "geometry": {"points": _square(0)},
    })["result"]
    revisions_before = _revision_count(core)
    ids = [f"nonexistent-{index}" for index in range(MAX_REGION_IDS_PER_BATCH + 1)]

    response = _rpc(server, "merge_regions", {
        "page_id": page_id, "region_ids": ids,
    })
    assert response["error"]["code"] == "INVALID_REQUEST"
    assert _revision_count(core) == revisions_before
    assert source["region_id"] in {
        region.region_id for region in core.editing.list_regions(page_id)
    }


def test_oversized_reorder_is_rejected_before_any_write(core):
    from application.editing.region_canvas import MAX_REGIONS_PER_PAGE

    page_id = _seed_page(core)
    server = CoreServiceServer(core)
    source = _rpc(server, "create_region", {
        "page_id": page_id, "geometry": {"points": _square(0)},
    })["result"]
    revisions_before = _revision_count(core)
    ids = [f"nonexistent-{index}" for index in range(MAX_REGIONS_PER_PAGE + 1)]

    response = _rpc(server, "reorder_regions", {
        "page_id": page_id, "ordered_region_ids": ids,
    })
    assert response["error"]["code"] == "INVALID_REQUEST"
    assert _revision_count(core) == revisions_before
    assert source["region_id"] in {
        region.region_id for region in core.editing.list_regions(page_id)
    }


def test_oversized_geometry_is_rejected_before_any_write(core):
    from application.editing.region_canvas import MAX_GEOMETRY_POINTS

    page_id = _seed_page(core)
    server = CoreServiceServer(core)
    source = _rpc(server, "create_region", {
        "page_id": page_id, "geometry": {"points": _square(0)},
    })["result"]
    revisions_before = _revision_count(core)
    points = [
        [0.1 + (index % 10) * 0.01, 0.1 + (index // 10) * 0.01]
        for index in range(MAX_GEOMETRY_POINTS + 1)
    ]

    response = _rpc(server, "create_region", {
        "page_id": page_id, "geometry": {"points": points},
    })
    assert response["error"]["code"] == "INVALID_REQUEST"
    assert _revision_count(core) == revisions_before

    # Same limit on an existing region's geometry edit.
    response = _rpc(server, "save_region_geometry", {
        "region_id": source["region_id"], "geometry": {"points": points},
    })
    assert response["error"]["code"] == "INVALID_REQUEST"
    assert _revision_count(core) == revisions_before


def test_page_region_cap_is_enforced_at_the_wire_and_service(
    core, monkeypatch
):
    import bootstrap.core_service as core_service
    import application.editing.service as editing_service

    page_id = _seed_page(core)
    server = CoreServiceServer(core)
    monkeypatch.setattr(core_service, "MAX_REGIONS_PER_PAGE", 2)
    monkeypatch.setattr(editing_service, "MAX_REGIONS_PER_PAGE", 2)

    assert _rpc(server, "create_region", {
        "page_id": page_id, "geometry": {"points": _square(0)},
    })["error"] is None
    assert _rpc(server, "create_region", {
        "page_id": page_id, "geometry": {"points": _square(1)},
    })["error"] is None
    third = _rpc(server, "create_region", {
        "page_id": page_id, "geometry": {"points": _square(2)},
    })
    assert third["error"]["code"] == "INVALID_REQUEST"
    assert len(core.editing.list_regions(page_id)) == 2

    with pytest.raises(ValueError):
        core.editing.create_region(
            page_id, RegionGeometry(bbox=BBox(10, 10, 20, 20))
        )


def test_normal_write_waits_for_a_short_concurrent_writer_lock(core, tmp_path):
    """The 5 s busy timeout is what makes the bounded limits meaningful: a
    normal region write waits for a short-lived independent writer instead of
    failing; no corruption, no orphan."""
    page_id = _seed_page(core)
    db_path = tmp_path / "data" / "library.db"
    holder_ready = threading.Event()
    release = threading.Event()
    holder_error: list[BaseException] = []

    def hold_write_lock() -> None:
        try:
            conn = sqlite3.connect(db_path, timeout=5)
            conn.isolation_level = None
            try:
                conn.execute("BEGIN IMMEDIATE")
                holder_ready.set()
                release.wait(timeout=10)
                conn.execute("ROLLBACK")
            finally:
                conn.close()
        except BaseException as error:  # noqa: BLE001
            holder_error.append(error)
            holder_ready.set()

    holder = threading.Thread(target=hold_write_lock, daemon=True)
    holder.start()
    assert holder_ready.wait(timeout=10)
    threading.Timer(0.2, release.set).start()

    region = core.editing.create_region(
        page_id, RegionGeometry(bbox=BBox(10, 10, 30, 20))
    )
    holder.join(timeout=10)
    assert holder_error == []
    assert region.current_revision_id is not None
    assert {
        item.region_id for item in core.editing.list_regions(page_id)
    } == {region.region_id}
    orphan = core.conn.execute(
        "SELECT COUNT(*) FROM regions r LEFT JOIN region_revisions rev"
        " ON rev.region_revision_id = r.current_revision_id"
        " WHERE r.current_revision_id IS NULL OR rev.region_revision_id IS NULL"
    ).fetchone()[0]
    assert orphan == 0
