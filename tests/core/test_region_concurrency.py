"""V11R-F0-1 I2/P1-B: REAL interleavings (independent SQLite connection + barrier).

The r1/I1 tests only provoked conflicts in the service pre-check or called the
committer directly, so they never proved the batch transaction re-reads state
that moved after the pre-check. These tests install a synchronous barrier
INSIDE ``_commit_batch_or_raise`` (i.e. after the service pre-check, before
``BEGIN IMMEDIATE``) and let a SEPARATE sqlite3 connection advance the current
pointer or soft-delete a target in that window:

- stale pointer -> INPUT_REVISION_CHANGED with ZERO write;
- soft-deleted target -> TARGET_NOT_FOUND with ZERO write;
- multi-region reorder where BOTH expectations expire in one side transaction;
- delete / pin guards vs. an advanced pointer;
- two real merge callers that both pass the pre-check (only one can commit);
- concurrent writers serialize without orphans (bounded stress).

Every assertion reads the database through yet another fresh connection / the
Core facade, never through mocked state.
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
    RegionNotFound,
    RegionRevisionChanged,
)
from application.importing.images.ports import ImportSource  # noqa: E402
from bootstrap.core_service import assemble_production_core  # noqa: E402
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
        "chapter", [ImportSource("concurrency.png", lambda: payload)]
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
def db_path(tmp_path: Path, core) -> Path:
    path = tmp_path / "data" / "library.db"
    assert path.exists(), path
    return path


def _side_connection(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, timeout=5)
    conn.row_factory = sqlite3.Row
    return conn


def _install_gate(monkeypatch, core, barrier: threading.Barrier, waits: int = 2) -> None:
    """Pause INSIDE _commit_batch_or_raise: the service pre-check already
    passed, the transaction has NOT begun. ``waits=2`` = wait for the side
    effect thread (barrier round 1) and for it to commit (round 2)."""
    original = type(core.editing)._commit_batch_or_raise

    def gated(self, **batch):
        barrier.wait(timeout=10)
        if waits > 1:
            barrier.wait(timeout=10)
        return original(self, **batch)

    monkeypatch.setattr(type(core.editing), "_commit_batch_or_raise", gated)


def _start_side_effect(barrier, action):
    """Run ``action`` on a separate OS thread between the two barrier rounds;
    the action opens its OWN sqlite connection (never the Core facade)."""
    state: dict[str, BaseException | None] = {"error": None}

    def worker() -> None:
        try:
            barrier.wait(timeout=10)
            action()
        except BaseException as error:  # noqa: BLE001 - surfaced to the test
            state["error"] = error
        finally:
            try:
                barrier.wait(timeout=10)
            except threading.BrokenBarrierError:
                pass

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
    return thread, state


def _advance_current_revision(conn: sqlite3.Connection, region_id: str, next_no: int = 2) -> None:
    """Append a real revision row and move the pointer (a pipeline write)."""
    row = conn.execute(
        "SELECT snapshot_json FROM region_revisions WHERE region_id = ?"
        " ORDER BY revision_no DESC LIMIT 1",
        (region_id,),
    ).fetchone()
    assert row is not None
    new_id = f"side-{region_id}-{next_no}"
    conn.execute(
        "INSERT INTO region_revisions (region_revision_id, region_id, revision_no,"
        " snapshot_json, origin, review_state, is_pinned, source_run_id,"
        " source_step_run_id, restored_from_revision_id, created_at)"
        " VALUES (?, ?, ?, ?, 'machine', 'needs_review', 0, NULL, NULL, NULL, ?)",
        (new_id, region_id, next_no, row["snapshot_json"], NOW),
    )
    conn.execute(
        "UPDATE regions SET current_revision_id = ?, updated_at = ?"
        " WHERE region_id = ?",
        (new_id, NOW, region_id),
    )


def _soft_delete(conn: sqlite3.Connection, region_id: str) -> None:
    conn.execute(
        "UPDATE regions SET deleted_at = ?, updated_at = ?"
        " WHERE region_id = ? AND deleted_at IS NULL",
        (NOW, NOW, region_id),
    )


def _revision_count(core, region_id: str) -> int:
    return core.conn.execute(
        "SELECT COUNT(*) FROM region_revisions WHERE region_id = ?",
        (region_id,),
    ).fetchone()[0]


def _live_ids(core, page_id: str) -> set[str]:
    return {region.region_id for region in core.editing.list_regions(page_id)}


def _assert_clean(core) -> None:
    orphan = core.conn.execute(
        "SELECT COUNT(*) FROM regions r LEFT JOIN region_revisions rev"
        " ON rev.region_revision_id = r.current_revision_id"
        " WHERE r.current_revision_id IS NULL"
        " OR rev.region_revision_id IS NULL"
    ).fetchone()[0]
    assert orphan == 0


def _make_regions(core, page_id: str, count: int):
    return [
        core.editing.create_region(
            page_id,
            RegionGeometry(bbox=BBox(10 + index * 60, 10, 50, 40)),
        )
        for index in range(count)
    ]


# ===========================================================================
# One stale expectation, advanced by an independent connection
# ===========================================================================


def test_merge_stale_pointer_after_precheck_is_zero_write(
    core, db_path, monkeypatch
):
    page_id = _seed_page(core)
    first, second = _make_regions(core, page_id, 2)
    barrier = threading.Barrier(2)
    _install_gate(monkeypatch, core, barrier)

    def side() -> None:
        conn = _side_connection(db_path)
        try:
            with conn:
                _advance_current_revision(conn, second.region_id, 2)
        finally:
            conn.close()

    thread, state = _start_side_effect(barrier, side)
    with pytest.raises(RegionRevisionChanged):
        core.editing.merge_regions(
            page_id,
            [first.region_id, second.region_id],
            expected_revisions={first.region_id: 1, second.region_id: 1},
        )
    thread.join(timeout=10)
    assert state["error"] is None, state["error"]

    # Zero write: no merged region, second source keeps exactly the two
    # revisions (its own + the concurrent one), first source untouched.
    assert _live_ids(core, page_id) == {first.region_id, second.region_id}
    assert _revision_count(core, first.region_id) == 1
    assert _revision_count(core, second.region_id) == 2
    _assert_clean(core)


def test_reorder_two_expired_regions_in_one_side_transaction_is_zero_write(
    core, db_path, monkeypatch
):
    page_id = _seed_page(core)
    first, second, third = _make_regions(core, page_id, 3)
    barrier = threading.Barrier(2)
    _install_gate(monkeypatch, core, barrier)

    def side() -> None:
        conn = _side_connection(db_path)
        try:
            with conn:
                _advance_current_revision(conn, second.region_id, 2)
                _advance_current_revision(conn, third.region_id, 2)
        finally:
            conn.close()

    thread, state = _start_side_effect(barrier, side)
    with pytest.raises(RegionRevisionChanged):
        core.editing.reorder_regions(
            page_id,
            [third.region_id, second.region_id, first.region_id],
            expected_revisions={
                first.region_id: 1,
                second.region_id: 1,
                third.region_id: 1,
            },
        )
    thread.join(timeout=10)
    assert state["error"] is None, state["error"]

    # Zero write: the whole reorder is rolled back (no reading_order change,
    # no revision appended to the first region).
    orders = {
        region.region_id: region.reading_order
        for region in core.editing.list_regions(page_id)
    }
    assert orders == {
        first.region_id: 1,
        second.region_id: 2,
        third.region_id: 3,
    }
    assert _revision_count(core, first.region_id) == 1
    _assert_clean(core)


def test_split_target_concurrently_deleted_after_precheck_is_not_found(
    core, db_path, monkeypatch
):
    page_id = _seed_page(core)
    source = _make_regions(core, page_id, 1)[0]
    barrier = threading.Barrier(2)
    _install_gate(monkeypatch, core, barrier)

    def side() -> None:
        conn = _side_connection(db_path)
        try:
            with conn:
                _soft_delete(conn, source.region_id)
        finally:
            conn.close()

    thread, state = _start_side_effect(barrier, side)
    with pytest.raises(RegionNotFound):
        core.editing.split_region(
            source.region_id,
            [
                RegionGeometry(bbox=BBox(0, 0, 50, 50)),
                RegionGeometry(bbox=BBox(50, 0, 50, 50)),
            ],
        )
    thread.join(timeout=10)
    assert state["error"] is None, state["error"]

    # Only the side delete exists: no part rows, no source revision.
    assert _live_ids(core, page_id) == set()
    assert _revision_count(core, source.region_id) == 1
    _assert_clean(core)


def test_delete_guard_vs_advanced_pointer_is_zero_write(
    core, db_path, monkeypatch
):
    page_id = _seed_page(core)
    region = _make_regions(core, page_id, 1)[0]
    barrier = threading.Barrier(2)
    _install_gate(monkeypatch, core, barrier)

    def side() -> None:
        conn = _side_connection(db_path)
        try:
            with conn:
                _advance_current_revision(conn, region.region_id, 2)
        finally:
            conn.close()

    thread, state = _start_side_effect(barrier, side)
    with pytest.raises(RegionRevisionChanged):
        core.editing.delete_region(region.region_id, expected_revision_no=1)
    thread.join(timeout=10)
    assert state["error"] is None, state["error"]

    row = core.conn.execute(
        "SELECT deleted_at FROM regions WHERE region_id = ?",
        (region.region_id,),
    ).fetchone()
    assert row["deleted_at"] is None
    assert _revision_count(core, region.region_id) == 2
    _assert_clean(core)


def test_pin_guard_vs_advanced_pointer_is_zero_write(
    core, db_path, monkeypatch
):
    page_id = _seed_page(core)
    region = _make_regions(core, page_id, 1)[0]
    barrier = threading.Barrier(2)
    _install_gate(monkeypatch, core, barrier)

    def side() -> None:
        conn = _side_connection(db_path)
        try:
            with conn:
                _advance_current_revision(conn, region.region_id, 2)
        finally:
            conn.close()

    thread, state = _start_side_effect(barrier, side)
    with pytest.raises(RegionRevisionChanged):
        core.editing.set_revision_pinned(
            region.region_id, 1, True, expected_revision_no=1
        )
    thread.join(timeout=10)
    assert state["error"] is None, state["error"]

    pinned = core.conn.execute(
        "SELECT is_pinned FROM region_revisions WHERE region_id = ?"
        " AND revision_no = 1",
        (region.region_id,),
    ).fetchone()["is_pinned"]
    assert pinned == 0
    _assert_clean(core)


# ===========================================================================
# Two REAL callers: both pass the pre-check, only one can commit
# ===========================================================================


def test_two_merge_callers_only_one_wins(core, monkeypatch):
    page_id = _seed_page(core)
    first, second = _make_regions(core, page_id, 2)
    barrier = threading.Barrier(2)
    # Both callers pause once at the gate: both pre-checks have passed.
    _install_gate(monkeypatch, core, barrier, waits=1)

    results: list[tuple] = []
    errors: list[BaseException] = []

    def call_merge() -> None:
        try:
            results.append(
                core.editing.merge_regions(
                    page_id, [first.region_id, second.region_id]
                )
            )
        except BaseException as error:  # noqa: BLE001 - classified below
            errors.append(error)

    threads = [
        threading.Thread(target=call_merge, daemon=True) for _ in range(2)
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=15)
        assert not thread.is_alive()

    assert len(results) + len(errors) == 2
    assert len(results) == 1, (results, errors)
    assert len(errors) == 1 and isinstance(errors[0], RegionNotFound), errors

    # Exactly one merged region; both sources soft-deleted by exactly one
    # caller (the loser wrote nothing, so no duplicate result set exists).
    live = _live_ids(core, page_id)
    assert len(live) == 1
    merged_id = next(iter(live))
    assert _revision_count(core, merged_id) == 1
    assert _revision_count(core, first.region_id) == 1
    assert _revision_count(core, second.region_id) == 1
    _assert_clean(core)


# ===========================================================================
# Bounded stress: concurrent writers serialize, never orphan a region
# ===========================================================================


def test_concurrent_writers_serialize_without_orphans(core):
    page_id = _seed_page(core)
    per_thread = 5
    errors: list[BaseException] = []

    def create_batch(worker: int) -> None:
        for index in range(per_thread):
            try:
                core.editing.create_region(
                    page_id,
                    RegionGeometry(
                        bbox=BBox(10 + worker * 100 + index, 10, 40, 30)
                    ),
                )
            except BaseException as error:  # noqa: BLE001
                errors.append(error)
                return

    threads = [
        threading.Thread(target=create_batch, args=(worker,), daemon=True)
        for worker in range(2)
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=30)
        assert not thread.is_alive()

    assert errors == []
    regions = core.editing.list_regions(page_id)
    assert len(regions) == 2 * per_thread
    assert len({region.region_id for region in regions}) == 2 * per_thread
    assert all(region.current_revision_id for region in regions)
    _assert_clean(core)
