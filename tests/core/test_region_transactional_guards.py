"""V11R-F0-1 I1/P2-4: delete and pin guards run in the SAME transaction.

The r1 review found the current-pointer check and the soft-delete / is_pinned
write were two separate steps, so a pipeline write in between could let a stale
request succeed. The fix places the comparison and the write inside one
``BEGIN IMMEDIATE`` batch; these tests simulate the concurrent pointer move and
assert zero write on either path.
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


def test_delete_guard_and_soft_delete_are_one_transaction(core) -> None:
    page_id = _seed_page(core)
    region = core.editing.create_region(page_id, RECT)
    stale_current_id = region.current_revision_id
    _advance_current_revision(core, region)

    result = _repo(core).commit_region_batch(
        soft_delete_region_ids=[(region.region_id, stale_current_id)]
    )
    assert result.status is RegionCommitStatus.INPUT_REVISION_CHANGED
    row = core.conn.execute(
        "SELECT deleted_at FROM regions WHERE region_id = ?", (region.region_id,)
    ).fetchone()
    assert row["deleted_at"] is None


def test_pin_guard_and_flag_update_are_one_transaction(core) -> None:
    page_id = _seed_page(core)
    region = core.editing.create_region(page_id, RECT)
    stale_current_id = region.current_revision_id
    _advance_current_revision(core, region)

    result = _repo(core).commit_region_batch(
        revision_pins=[(region.region_id, 1, True)],
        expected_current_checks=[(region.region_id, stale_current_id)],
    )
    assert result.status is RegionCommitStatus.INPUT_REVISION_CHANGED
    row = core.conn.execute(
        "SELECT is_pinned FROM region_revisions WHERE region_id = ?"
        " AND revision_no = 1",
        (region.region_id,),
    ).fetchone()
    assert row["is_pinned"] == 0


