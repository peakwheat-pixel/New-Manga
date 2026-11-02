"""V11R-F0-1 I1/P1-1: create / merge / split are ALL-OR-NOTHING.

The r1 review found the composite writes were multi-step (row insert, revision
seam, per-source soft deletes), so a mid-way failure could leave an orphan
region without a current revision, a merged region next to live sources, or a
live source next to half the split parts. The fix routes them through ONE
``BEGIN IMMEDIATE`` batch transaction; these tests inject failures at the
row-writer seams on the REAL production SQLite assembly and assert zero write
plus the TASK-002 §2.1 no-orphan invariant.
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

from application.editing.errors import RegionRevisionChanged  # noqa: E402
from application.editing.ports import (  # noqa: E402
    RegionCommitStatus,
    RegionLockSnapshot,  # noqa: F401  (documents the seam contract)
)
from application.importing.images.ports import ImportSource  # noqa: E402
from bootstrap.core_service import (  # noqa: E402
    PROTOCOL_MAJOR,
    PROTOCOL_MINOR,
    CoreServiceServer,
    assemble_production_core,
)
from domain.regions.entities import (  # noqa: E402
    BBox,
    RegionGeometry,
    RegionOrigin,
    RegionRevision,
    ReviewState,
)

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
        "chapter", [ImportSource("atomicity.png", lambda: payload)]
    )
    assert not report.failed and len(report.imported) == 1, report
    return report.imported[0].page.page_id


def _repo(core):
    """The production committer is the SQLite repository itself."""
    return core.editing._committer


def _assert_no_orphan_regions(core) -> None:
    """TASK-002 §2.1 invariant: a region row always has a resolvable current
    revision + first revision (no orphan can survive a failed batch)."""
    orphan_rows = core.conn.execute(
        "SELECT COUNT(*) FROM regions r"
        " LEFT JOIN region_revisions rev"
        " ON rev.region_revision_id = r.current_revision_id"
        " WHERE r.current_revision_id IS NULL"
        " OR rev.region_revision_id IS NULL"
    ).fetchone()[0]
    assert orphan_rows == 0

    revisionless = core.conn.execute(
        "SELECT COUNT(*) FROM regions r WHERE NOT EXISTS"
        " (SELECT 1 FROM region_revisions rev WHERE rev.region_id = r.region_id)"
    ).fetchone()[0]
    assert revisionless == 0


def _revision_count(core, region_id: str) -> int:
    return core.conn.execute(
        "SELECT COUNT(*) FROM region_revisions WHERE region_id = ?",
        (region_id,),
    ).fetchone()[0]


def _live_region_ids(core, page_id: str) -> set[str]:
    rows = core.conn.execute(
        "SELECT region_id FROM regions WHERE page_id = ? AND deleted_at IS NULL",
        (page_id,),
    ).fetchall()
    return {row["region_id"] for row in rows}


def _advance_current_revision(core, region) -> None:
    """Simulate a concurrent pipeline write: append a real revision row and
    move the current pointer, so the region's observed revision becomes stale
    while every FK/immutability invariant stays satisfied."""
    next_no = core.conn.execute(
        "SELECT COALESCE(MAX(revision_no), 0) + 1 FROM region_revisions"
        " WHERE region_id = ?",
        (region.region_id,),
    ).fetchone()[0]
    concurrent_id = f"concurrent-{region.region_id}-{next_no}"
    with core.conn:
        core.conn.execute(
            "INSERT INTO region_revisions (region_revision_id, region_id,"
            " revision_no, snapshot_json, origin, review_state, is_pinned,"
            " created_at) VALUES (?, ?, ?, ?, 'machine', 'needs_review', 0, ?)",
            (
                concurrent_id,
                region.region_id,
                next_no,
                json.dumps(region.snapshot_state()),
                NOW,
            ),
        )
        core.conn.execute(
            "UPDATE regions SET current_revision_id = ? WHERE region_id = ?",
            (concurrent_id, region.region_id),
        )


@pytest.fixture()
def core(tmp_path: Path):
    assembled = assemble_production_core(tmp_path / "data")
    try:
        yield assembled
    finally:
        assembled.conn.close()


# ===========================================================================
# P1-1: composite writes are all-or-nothing
# ===========================================================================


def test_create_rolls_back_when_the_first_revision_insert_fails(
    core, monkeypatch
) -> None:
    page_id = _seed_page(core)
    repo = _repo(core)

    def exploded(revision):
        raise sqlite3.OperationalError("injected first-revision failure")

    monkeypatch.setattr(repo, "_insert_revision", exploded)
    with pytest.raises(RuntimeError):
        core.editing.create_region(page_id, RECT)

    # The region row must not exist at all (no orphan without a revision).
    rows = core.conn.execute(
        "SELECT COUNT(*) FROM regions WHERE page_id = ?", (page_id,)
    ).fetchone()[0]
    assert rows == 0
    _assert_no_orphan_regions(core)


def test_merge_rolls_back_and_keeps_sources_live_when_source_delete_fails(
    core, monkeypatch
) -> None:
    page_id = _seed_page(core)
    first = core.editing.create_region(page_id, RegionGeometry(bbox=BBox(0, 0, 50, 40)))
    second = core.editing.create_region(
        page_id, RegionGeometry(bbox=BBox(30, 10, 60, 50))
    )
    repo = _repo(core)
    sources_before = _live_region_ids(core, page_id)

    def exploded(conn, region_id, deleted_at):
        raise sqlite3.OperationalError("injected source soft-delete failure")

    monkeypatch.setattr(repo, "_soft_delete_row", exploded)
    with pytest.raises(RuntimeError):
        core.editing.merge_regions(page_id, [first.region_id, second.region_id])

    # Zero write: the merged region never appears and both sources stay live.
    assert _live_region_ids(core, page_id) == sources_before
    assert _revision_count(core, first.region_id) == 1
    assert _revision_count(core, second.region_id) == 1
    _assert_no_orphan_regions(core)


def test_split_rolls_back_when_a_later_part_fails(core, monkeypatch) -> None:
    page_id = _seed_page(core)
    source = core.editing.create_region(page_id, RegionGeometry(bbox=BBox(0, 0, 100, 50)))
    repo = _repo(core)
    original_insert = repo._insert_revision
    calls = {"count": 0}

    def flaky(revision):
        calls["count"] += 1
        if calls["count"] == 2:
            raise sqlite3.OperationalError("injected second-part failure")
        original_insert(revision)

    monkeypatch.setattr(repo, "_insert_revision", flaky)
    with pytest.raises(RuntimeError):
        core.editing.split_region(
            source.region_id,
            [
                RegionGeometry(bbox=BBox(0, 0, 50, 50)),
                RegionGeometry(bbox=BBox(50, 0, 50, 50)),
            ],
        )

    # Zero write: the source stays live and no part row survives.
    assert _live_region_ids(core, page_id) == {source.region_id}
    assert _revision_count(core, source.region_id) == 1
    _assert_no_orphan_regions(core)


def test_successful_composite_writes_leave_the_invariant_intact(core) -> None:
    page_id = _seed_page(core)
    first = core.editing.create_region(page_id, RegionGeometry(bbox=BBox(0, 0, 50, 40)))
    second = core.editing.create_region(
        page_id, RegionGeometry(bbox=BBox(30, 10, 60, 50))
    )
    merged, deleted = core.editing.merge_regions(
        page_id, [first.region_id, second.region_id]
    )
    assert merged.current_revision_id is not None
    assert _revision_count(core, merged.region_id) == 1
    assert set(deleted) == {first.region_id, second.region_id}
    _assert_no_orphan_regions(core)


