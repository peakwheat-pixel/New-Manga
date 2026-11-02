"""V11R-F0-1 I4: restore must respect the vertex bound and map not-found.

Review r4 kept two P2 items on ``restore_revision_with_number``:

- P2-B: restore feeds a stored history snapshot straight into the revision
  seam, so an oversized historical geometry (created before the vertex bound,
  or hand-edited storage) bypasses ``MAX_GEOMETRY_POINTS``.
- P2 (new): the commit seam's ``TARGET_NOT_FOUND`` was not mapped; a restore
  racing a concurrent soft delete fell into ``RuntimeError`` (wire UNKNOWN)
  instead of typed not-found.

Fix: ``assert_geometry_within_limits(staged.geometry)`` on the restored
snapshot BEFORE the seam (typed RegionLimitExceeded, wire INVALID_REQUEST) and
an explicit ``TARGET_NOT_FOUND -> RegionNotFound`` mapping (wire
TARGET_NOT_FOUND, zero write).
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

from application.editing.errors import (  # noqa: E402
    RegionLimitExceeded,
    RegionNotFound,
)
from application.editing.region_canvas import MAX_GEOMETRY_POINTS  # noqa: E402
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
        "chapter", [ImportSource("restore-limits.png", lambda: payload)]
    )
    assert not report.failed and len(report.imported) == 1, report
    return report.imported[0].page.page_id


def _make_region(core, page_id: str):
    return core.editing.create_region(page_id, RECT)


def _revision_count(core, region_id: str) -> int:
    return core.conn.execute(
        "SELECT COUNT(*) FROM region_revisions WHERE region_id = ?",
        (region_id,),
    ).fetchone()[0]


@pytest.fixture()
def db_path(tmp_path: Path) -> Path:
    path = tmp_path / "data" / "library.db"
    assert path.exists(), path
    return path


def _install_commit_gate(core, monkeypatch, barrier: threading.Barrier) -> None:
    committer = core.editing._committer
    original = committer.commit_region_revision

    def gated(region, revision, **kwargs):
        barrier.wait(timeout=10)
        barrier.wait(timeout=10)
        return original(region, revision, **kwargs)

    monkeypatch.setattr(committer, "commit_region_revision", gated)


def _start_side_soft_delete(barrier, db_path: Path, region_id: str):
    state: dict[str, BaseException | None] = {"error": None}

    def worker() -> None:
        try:
            barrier.wait(timeout=10)
            conn = sqlite3.connect(db_path, timeout=5)
            try:
                with conn:
                    conn.execute(
                        "UPDATE regions SET deleted_at = ?, updated_at = ?"
                        " WHERE region_id = ? AND deleted_at IS NULL",
                        (NOW, NOW, region_id),
                    )
            finally:
                conn.close()
        except BaseException as error:  # noqa: BLE001
            state["error"] = error
        finally:
            try:
                barrier.wait(timeout=10)
            except threading.BrokenBarrierError:
                pass

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
    return thread, state


def _rpc(server, command: str, payload: dict) -> dict:
    line = json.dumps({
        "protocol": "new-manga.core",
        "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
        "request_id": f"i4-{command}",
        "command": command,
        "payload": payload,
    })
    response, exit_flag = server.dispatch_request(line)
    assert not exit_flag
    return response


# ===========================================================================
# P2-B: oversized historical snapshot geometry is rejected before persistence
# ===========================================================================


@pytest.fixture()
def core(tmp_path: Path):
    assembled = assemble_production_core(tmp_path / "data")
    try:
        yield assembled
    finally:
        assembled.conn.close()


def test_restore_after_concurrent_soft_delete_is_typed_not_found_zero_write(
    core, db_path, monkeypatch
):
    page_id = _seed_page(core)
    region = _make_region(core, page_id)
    barrier = threading.Barrier(2)
    _install_commit_gate(core, monkeypatch, barrier)

    thread, state = _start_side_soft_delete(barrier, db_path, region.region_id)
    with pytest.raises(RegionNotFound):
        core.editing.restore_revision_with_number(
            region.region_id, 1, expected_revision_no=1
        )
    thread.join(timeout=10)
    assert state["error"] is None, state["error"]

    assert _revision_count(core, region.region_id) == 1
    row = core.conn.execute(
        "SELECT deleted_at FROM regions WHERE region_id = ?",
        (region.region_id,),
    ).fetchone()
    assert row["deleted_at"] is not None  # only the side delete happened


def test_wire_restore_after_concurrent_soft_delete_is_target_not_found(
    core, db_path, monkeypatch
):
    page_id = _seed_page(core)
    server = CoreServiceServer(core)
    created = _rpc(server, "create_region", {
        "page_id": page_id, "geometry": {"points": [[0.1, 0.1], [0.3, 0.3]]},
    })["result"]
    region_id = created["region_id"]
    barrier = threading.Barrier(2)
    _install_commit_gate(core, monkeypatch, barrier)

    thread, state = _start_side_soft_delete(barrier, db_path, region_id)
    response = _rpc(server, "restore_region_revision", {
        "region_id": region_id,
        "revision_no": 1,
        "expected_revision": 1,
    })
    thread.join(timeout=10)
    assert state["error"] is None, state["error"]

    assert response["error"]["code"] == "TARGET_NOT_FOUND"
    assert response["error"]["category"] == "not_found"
    assert _revision_count(core, region_id) == 1

