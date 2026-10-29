"""V11R-F0-1 I2/P1-A: batch targets must still be LIVE when the transaction runs.

The r2 review found the batch seam only compared ``current_revision_id``:
soft delete updated by bare ``region_id`` and never checked ``deleted_at``. Two
callers that both passed ``_require_region`` before the first commit could both
merge/split the same sources (the second produced a second result set on
already-deleted sources), and delete/pin could write to a target another
request had just soft-deleted.

The fix (commit_region_batch): every existing target is re-read INSIDE the
transaction and must be ``deleted_at IS NULL`` (else the whole batch rolls back
with TARGET_NOT_FOUND); the soft delete itself is a CONDITIONAL update whose
rowcount must be 1; the pin update additionally requires the region to be live.
These tests drive the real production SQLite assembly (and a second raw
connection for the merge-time race) and assert typed failures with ZERO write.
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
        "chapter", [ImportSource("liveness.png", lambda: payload)]
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


def _live_ids(core, page_id: str) -> set[str]:
    return {region.region_id for region in core.editing.list_regions(page_id)}


def _revision_count(core, region_id: str) -> int:
    return core.conn.execute(
        "SELECT COUNT(*) FROM region_revisions WHERE region_id = ?",
        (region_id,),
    ).fetchone()[0]


def _deleted_at(core, region_id: str):
    return core.conn.execute(
        "SELECT deleted_at FROM regions WHERE region_id = ?", (region_id,)
    ).fetchone()["deleted_at"]


def _is_pinned(core, region_id: str, revision_no: int):
    return core.conn.execute(
        "SELECT is_pinned FROM region_revisions WHERE region_id = ?"
        " AND revision_no = ?",
        (region_id, revision_no),
    ).fetchone()["is_pinned"]


def _assert_liveness_invariant(core) -> None:
    orphan = core.conn.execute(
        "SELECT COUNT(*) FROM regions r LEFT JOIN region_revisions rev"
        " ON rev.region_revision_id = r.current_revision_id"
        " WHERE r.current_revision_id IS NULL"
        " OR rev.region_revision_id IS NULL"
    ).fetchone()[0]
    assert orphan == 0


# ===========================================================================
# Sequential: a target the caller already saw deleted is never written again
# ===========================================================================


def test_merge_of_soft_deleted_source_is_target_not_found_and_zero_write(core):
    page_id = _seed_page(core)
    first = core.editing.create_region(page_id, RegionGeometry(bbox=BBox(0, 0, 50, 40)))
    second = core.editing.create_region(
        page_id, RegionGeometry(bbox=BBox(60, 0, 50, 40))
    )
    core.editing.delete_region(first.region_id)
    live_before = _live_ids(core, page_id)
    second_revisions = _revision_count(core, second.region_id)

    with pytest.raises(RegionNotFound):
        core.editing.merge_regions(page_id, [first.region_id, second.region_id])

    # Zero write: no merged region, the second source is untouched.
    assert _live_ids(core, page_id) == live_before
    assert _revision_count(core, second.region_id) == second_revisions
    _assert_liveness_invariant(core)


def test_split_of_soft_deleted_source_is_target_not_found_and_zero_write(core):
    page_id = _seed_page(core)
    source = core.editing.create_region(
        page_id, RegionGeometry(bbox=BBox(0, 0, 100, 50))
    )
    core.editing.delete_region(source.region_id)
    live_before = _live_ids(core, page_id)

    with pytest.raises(RegionNotFound):
        core.editing.split_region(
            source.region_id,
            [
                RegionGeometry(bbox=BBox(0, 0, 50, 50)),
                RegionGeometry(bbox=BBox(50, 0, 50, 50)),
            ],
        )

    assert _live_ids(core, page_id) == live_before
    assert _revision_count(core, source.region_id) == 1
    _assert_liveness_invariant(core)


def test_delete_of_soft_deleted_region_is_target_not_found_and_zero_write(core):
    page_id = _seed_page(core)
    region = core.editing.create_region(page_id, RECT)
    core.editing.delete_region(region.region_id)
    deleted_at = _deleted_at(core, region.region_id)

    with pytest.raises(RegionNotFound):
        core.editing.delete_region(region.region_id)

    # The second delete never rewrites deleted_at and creates no revision.
    assert _deleted_at(core, region.region_id) == deleted_at
    assert _revision_count(core, region.region_id) == 1


def test_pin_of_soft_deleted_region_is_target_not_found_and_zero_write(core):
    page_id = _seed_page(core)
    region = core.editing.create_region(page_id, RECT)
    core.editing.delete_region(region.region_id)

    with pytest.raises(RegionNotFound):
        core.editing.set_revision_pinned(region.region_id, 1, True)

    assert _is_pinned(core, region.region_id, 1) == 0


# ===========================================================================
# Race: the target is soft-deleted between the service pre-check and the
# transaction (real second SQLite connection, not a mocked committer)
# ===========================================================================


@pytest.fixture()
def raw_conn_factory(core, tmp_path: Path):
    db_path = tmp_path / "data" / "library.db"
    assert db_path.exists(), db_path

    def factory() -> sqlite3.Connection:
        conn = sqlite3.connect(db_path, timeout=5)
        conn.row_factory = sqlite3.Row
        return conn

    return factory


def _soft_delete_from_second_connection(conn: sqlite3.Connection, region_id: str):
    conn.execute(
        "UPDATE regions SET deleted_at = ?, updated_at = ?"
        " WHERE region_id = ? AND deleted_at IS NULL",
        (NOW, NOW, region_id),
    )


def test_batch_rejects_a_target_soft_deleted_between_precheck_and_commit(
    core, raw_conn_factory
):
    """Direct seam probe: the service pre-check has already passed, then a
    second connection soft-deletes the target; the batch must roll back with
    TARGET_NOT_FOUND and leave the caller's write unapplied."""
    page_id = _seed_page(core)
    first = core.editing.create_region(page_id, RegionGeometry(bbox=BBox(0, 0, 50, 40)))
    second = core.editing.create_region(
        page_id, RegionGeometry(bbox=BBox(60, 0, 50, 40))
    )
    expected_ids = {
        first.region_id: first.current_revision_id,
        second.region_id: second.current_revision_id,
    }
    live_before = _live_ids(core, page_id)

    with raw_conn_factory() as side:
        _soft_delete_from_second_connection(side, first.region_id)
        side.commit()

    from application.editing.ports import RegionCommitStatus

    result = core.editing._committer.commit_region_batch(
        soft_delete_region_ids=[
            (second.region_id, expected_ids[second.region_id])
        ],
        expected_current_checks=[(first.region_id, expected_ids[first.region_id])],
    )
    assert result.status is RegionCommitStatus.TARGET_NOT_FOUND
    # Only the second connection's delete happened; the batch wrote nothing.
    assert _deleted_at(core, second.region_id) is None
    assert _live_ids(core, page_id) == live_before - {first.region_id}
    _assert_liveness_invariant(core)


def test_merge_batch_rolls_back_when_a_source_is_concurrently_deleted(
    core, raw_conn_factory, monkeypatch
):
    """Full merge path: a second connection soft-deletes a source AFTER the
    service pre-check but BEFORE the batch transaction; typed not-found, no
    merged region, no source revision."""
    import threading

    page_id = _seed_page(core)
    first = core.editing.create_region(page_id, RegionGeometry(bbox=BBox(0, 0, 50, 40)))
    second = core.editing.create_region(
        page_id, RegionGeometry(bbox=BBox(60, 0, 50, 40))
    )
    barrier = threading.Barrier(2)
    original = type(core.editing)._commit_batch_or_raise

    def gated(self, **batch):
        barrier.wait(timeout=10)  # both parties at the gate: pre-check passed
        barrier.wait(timeout=10)  # side effect committed
        return original(self, **batch)

    monkeypatch.setattr(
        type(core.editing), "_commit_batch_or_raise", gated
    )

    def side_effect() -> None:
        barrier.wait(timeout=10)
        with raw_conn_factory() as side:
            _soft_delete_from_second_connection(side, first.region_id)
            side.commit()
        barrier.wait(timeout=10)

    worker = threading.Thread(target=side_effect, daemon=True)
    worker.start()
    with pytest.raises(RegionNotFound):
        core.editing.merge_regions(page_id, [first.region_id, second.region_id])
    worker.join(timeout=10)
    assert not worker.is_alive()

    # Zero write from the merge: no merged row, second source still live with
    # only its first revision.
    merged_like = [
        region
        for region in core.conn.execute(
            "SELECT region_id FROM regions WHERE page_id = ?"
            " AND deleted_at IS NULL",
            (page_id,),
        ).fetchall()
    ]
    assert {row["region_id"] for row in merged_like} == {second.region_id}
    assert _revision_count(core, second.region_id) == 1
    _assert_liveness_invariant(core)


# ===========================================================================
# Wire level: typed TARGET_NOT_FOUND, not an internal error, not a conflict
# ===========================================================================


def _rpc(server, command: str, payload: dict) -> dict:
    line = json.dumps({
        "protocol": "new-manga.core",
        "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
        "request_id": f"i2-{command}",
        "command": command,
        "payload": payload,
    })
    response, exit_flag = server.dispatch_request(line)
    assert not exit_flag
    return response


def test_wire_repeated_merge_is_target_not_found_and_zero_write(core):
    page_id = _seed_page(core)
    server = CoreServiceServer(core)
    first = _rpc(server, "create_region", {
        "page_id": page_id, "geometry": {"points": [[0.1, 0.1], [0.3, 0.3]]},
    })["result"]
    second = _rpc(server, "create_region", {
        "page_id": page_id, "geometry": {"points": [[0.5, 0.5], [0.8, 0.8]]},
    })["result"]
    merged = _rpc(server, "merge_regions", {
        "page_id": page_id,
        "region_ids": [first["region_id"], second["region_id"]],
    })
    assert merged["error"] is None, merged["error"]
    merged_id = merged["result"]["region_id"]

    again = _rpc(server, "merge_regions", {
        "page_id": page_id,
        "region_ids": [first["region_id"], second["region_id"]],
    })
    assert again["error"] is not None
    assert again["error"]["code"] == "TARGET_NOT_FOUND"
    assert again["error"]["category"] == "not_found"
    # No second merged region, and the first merged region keeps one revision.
    live = _live_ids(core, page_id)
    assert live == {merged_id}
    assert _revision_count(core, merged_id) == 1
    _assert_liveness_invariant(core)


def test_wire_delete_pin_on_deleted_target_are_typed_not_found(core):
    page_id = _seed_page(core)
    server = CoreServiceServer(core)
    created = _rpc(server, "create_region", {
        "page_id": page_id, "geometry": {"points": [[0.1, 0.1], [0.3, 0.3]]},
    })["result"]
    region_id = created["region_id"]
    deleted = _rpc(server, "delete_region", {"region_id": region_id})
    assert deleted["error"] is None, deleted["error"]

    again = _rpc(server, "delete_region", {"region_id": region_id})
    assert again["error"]["code"] == "TARGET_NOT_FOUND"
    pinned = _rpc(server, "pin_revision", {
        "region_id": region_id, "revision_no": 1, "pinned": True,
    })
    assert pinned["error"]["code"] == "TARGET_NOT_FOUND"
    assert _is_pinned(core, region_id, 1) == 0
