"""V11R-F0-1 I3/P1: a single-revision write cannot land on a soft-deleted target.

Review r3 (P1): ``commit_region_revision`` re-read only the current pointer and
the locks inside its transaction, never ``deleted_at``. Between the service
pre-check and the commit another connection could soft-delete the region (via
delete/merge/split), and the stale write still inserted a new revision on the
invisible target and reported success.

The fix re-reads ``deleted_at IS NULL`` INSIDE the single-revision transaction
and returns TARGET_NOT_FOUND (service raises typed RegionNotFound, wire
TARGET_NOT_FOUND) with ZERO write.

These tests use an independent sqlite3 connection + a synchronous barrier
placed before ``BEGIN IMMEDIATE`` to create the real interleaving for
save_geometry / save_manual_translation / confirm_final / set_locks (plus one
wire-level save_region_geometry assertion).
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

from application.editing.errors import RegionNotFound  # noqa: E402
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
NEW_GEOMETRY = RegionGeometry(bbox=BBox(20, 20, 50, 30))


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
        "chapter", [ImportSource("single-liveness.png", lambda: payload)]
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


@pytest.fixture()
def db_path(tmp_path: Path) -> Path:
    path = tmp_path / "data" / "library.db"
    assert path.exists(), path
    return path


def _install_commit_gate(core, monkeypatch, barrier: threading.Barrier) -> None:
    """Pause before BEGIN IMMEDIATE of the SINGLE-revision seam: the service
    pre-check already passed, the transaction has not started."""
    committer = core.editing._committer
    original = committer.commit_region_revision

    def gated(region, revision, **kwargs):
        barrier.wait(timeout=10)
        barrier.wait(timeout=10)
        return original(region, revision, **kwargs)

    monkeypatch.setattr(committer, "commit_region_revision", gated)


def _start_side_delete(barrier, db_path, region_id: str):
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


def _revision_count(core, region_id: str) -> int:
    return core.conn.execute(
        "SELECT COUNT(*) FROM region_revisions WHERE region_id = ?",
        (region_id,),
    ).fetchone()[0]


def _deleted_at(core, region_id: str):
    return core.conn.execute(
        "SELECT deleted_at FROM regions WHERE region_id = ?", (region_id,)
    ).fetchone()["deleted_at"]


def _make_region(core, page_id: str):
    return core.editing.create_region(page_id, RECT)


# ===========================================================================
# save_geometry
# ===========================================================================


def test_save_geometry_after_concurrent_delete_is_target_not_found(
    core, db_path, monkeypatch
):
    page_id = _seed_page(core)
    region = _make_region(core, page_id)
    barrier = threading.Barrier(2)
    _install_commit_gate(core, monkeypatch, barrier)

    thread, state = _start_side_delete(barrier, db_path, region.region_id)
    with pytest.raises(RegionNotFound):
        core.editing.save_geometry(
            region.region_id, NEW_GEOMETRY, expected_revision_no=1
        )
    thread.join(timeout=10)
    assert state["error"] is None, state["error"]

    # Only the side delete happened: no new revision, geometry unchanged.
    assert _revision_count(core, region.region_id) == 1
    assert _deleted_at(core, region.region_id) is not None
    row = core.conn.execute(
        "SELECT geometry_json FROM regions WHERE region_id = ?",
        (region.region_id,),
    ).fetchone()
    assert "50" not in str(row["geometry_json"])


# ===========================================================================
# save_manual_translation / confirm_final / set_locks (commit_user path)
# ===========================================================================


def test_save_manual_translation_after_concurrent_delete_is_target_not_found(
    core, db_path, monkeypatch
):
    page_id = _seed_page(core)
    region = _make_region(core, page_id)
    barrier = threading.Barrier(2)
    _install_commit_gate(core, monkeypatch, barrier)

    thread, state = _start_side_delete(barrier, db_path, region.region_id)
    with pytest.raises(RegionNotFound):
        core.editing.save_manual_translation(
            region.region_id, "人工译文", expected_revision_no=1
        )
    thread.join(timeout=10)
    assert state["error"] is None, state["error"]

    assert _revision_count(core, region.region_id) == 1
    stored = core.conn.execute(
        "SELECT text_json FROM regions WHERE region_id = ?",
        (region.region_id,),
    ).fetchone()
    assert "人工译文" not in stored["text_json"]


def test_confirm_final_after_concurrent_delete_is_target_not_found(
    core, db_path, monkeypatch
):
    page_id = _seed_page(core)
    region = _make_region(core, page_id)
    core.editing.save_manual_translation(region.region_id, "人工译文")
    revisions_before = _revision_count(core, region.region_id)
    barrier = threading.Barrier(2)
    _install_commit_gate(core, monkeypatch, barrier)

    thread, state = _start_side_delete(barrier, db_path, region.region_id)
    with pytest.raises(RegionNotFound):
        core.editing.confirm_final(region.region_id, expected_revision_no=2)
    thread.join(timeout=10)
    assert state["error"] is None, state["error"]

    assert _revision_count(core, region.region_id) == revisions_before


def test_set_locks_after_concurrent_delete_is_target_not_found(
    core, db_path, monkeypatch
):
    page_id = _seed_page(core)
    region = _make_region(core, page_id)
    barrier = threading.Barrier(2)
    _install_commit_gate(core, monkeypatch, barrier)

    thread, state = _start_side_delete(barrier, db_path, region.region_id)
    with pytest.raises(RegionNotFound):
        core.editing.set_locks(
            region.region_id, translation_locked=True, expected_revision_no=1
        )
    thread.join(timeout=10)
    assert state["error"] is None, state["error"]

    assert _revision_count(core, region.region_id) == 1
    stored = core.conn.execute(
        "SELECT region_locked, translation_locked, inpaint_locked FROM regions"
        " WHERE region_id = ?",
        (region.region_id,),
    ).fetchone()
    assert tuple(stored) == (0, 0, 0)


# ===========================================================================
# wire: typed TARGET_NOT_FOUND, not internal/conflict
# ===========================================================================


def _rpc(server, command: str, payload: dict) -> dict:
    line = json.dumps({
        "protocol": "new-manga.core",
        "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
        "request_id": f"i3-{command}",
        "command": command,
        "payload": payload,
    })
    response, exit_flag = server.dispatch_request(line)
    assert not exit_flag
    return response


def test_wire_save_region_geometry_after_concurrent_delete_is_target_not_found(
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

    thread, state = _start_side_delete(barrier, db_path, region_id)
    response = _rpc(server, "save_region_geometry", {
        "region_id": region_id,
        "geometry": {"points": [[0.2, 0.2], [0.4, 0.4]]},
        "expected_revision": 1,
    })
    thread.join(timeout=10)
    assert state["error"] is None, state["error"]

    assert response["error"]["code"] == "TARGET_NOT_FOUND"
    assert response["error"]["category"] == "not_found"
    assert _revision_count(core, region_id) == 1
