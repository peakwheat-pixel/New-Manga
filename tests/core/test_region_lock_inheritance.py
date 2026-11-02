"""V11R-F0-1 I1/P1-3: merge/split inherit the EFFECTIVE translation locks.

The r1 review found merge dropped an explicitly-set translation lock (only
``manual_edited`` copied the text flag, and the region-level projection was
never set) and split copied the text flag only, so the translation step could
overwrite merged/protected text. The fix inherits the effective lock state
(region OR text) into BOTH projections; these tests prove the lock survives and
the machine translation step degrades to the lock/candidate path.
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


def test_merge_inherits_an_explicit_translation_lock(core) -> None:
    page_id = _seed_page(core)
    first = core.editing.create_region(page_id, RegionGeometry(bbox=BBox(0, 0, 50, 40)))
    second = core.editing.create_region(
        page_id, RegionGeometry(bbox=BBox(60, 0, 50, 40))
    )
    # Explicit user lock on a region that was never manually edited: only the
    # explicit lock command arms this, and it must survive the merge.
    assert first.text.manual_edited is False
    core.editing.set_locks(first.region_id, translation_locked=True)
    assert core.editing.get_region(first.region_id).text.manual_edited is False

    merged, deleted = core.editing.merge_regions(
        page_id, [first.region_id, second.region_id]
    )
    assert set(deleted) == {first.region_id, second.region_id}
    stored = core.editing.get_region(merged.region_id)
    # BOTH projections carry the inherited lock ...
    assert stored.translation_locked is True
    assert stored.text.translation_locked is True
    # ... and the machine translation step can no longer overwrite the merged
    # text (it degrades to the candidate/lock path, never a direct write).
    outcome = core.editing.apply_machine_translation(merged.region_id, "自动译文")
    assert outcome.status.value == "lock_changed"
    stored_text = core.editing.get_region(merged.region_id).text
    assert stored_text.machine_translation == ""


def test_split_inherits_an_explicit_translation_lock(core) -> None:
    page_id = _seed_page(core)
    source = core.editing.create_region(page_id, RegionGeometry(bbox=BBox(0, 0, 100, 50)))
    core.editing.set_locks(source.region_id, translation_locked=True)

    parts = core.editing.split_region(
        source.region_id,
        [
            RegionGeometry(bbox=BBox(0, 0, 50, 50)),
            RegionGeometry(bbox=BBox(50, 0, 50, 50)),
        ],
    )
    assert len(parts) == 2
    for part in parts:
        stored = core.editing.get_region(part.region_id)
        assert stored.translation_locked is True
        assert stored.text.translation_locked is True
        outcome = core.editing.apply_machine_translation(part.region_id, "自动译文")
        assert outcome.status.value == "lock_changed"


def test_merge_inherits_region_and_inpaint_locks(core) -> None:
    page_id = _seed_page(core)
    first = core.editing.create_region(page_id, RegionGeometry(bbox=BBox(0, 0, 50, 40)))
    second = core.editing.create_region(
        page_id, RegionGeometry(bbox=BBox(60, 0, 50, 40))
    )
    core.editing.set_locks(
        second.region_id, region_locked=True, inpaint_locked=True
    )
    merged, _deleted = core.editing.merge_regions(
        page_id, [first.region_id, second.region_id]
    )
    stored = core.editing.get_region(merged.region_id)
    assert stored.region_locked is True
    assert stored.inpaint_locked is True


def _rpc(server, command: str, payload: dict, number: int = 1) -> dict:
    line = json.dumps({
        "protocol": "new-manga.core",
        "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
        "request_id": f"i1-{command}-{number}",
        "command": command,
        "payload": payload,
    })
    response, exit_flag = server.dispatch_request(line)
    assert not exit_flag
    return response


def test_wire_merge_inherits_lock_and_reports_real_state(core) -> None:
    page_id = _seed_page(core)
    server = CoreServiceServer(core)
    first = _rpc(server, "create_region", {
        "page_id": page_id, "geometry": {"points": [[0.1, 0.1], [0.3, 0.3]]},
    })["result"]
    second = _rpc(server, "create_region", {
        "page_id": page_id, "geometry": {"points": [[0.5, 0.5], [0.8, 0.8]]},
    })["result"]
    locked = _rpc(server, "set_region_lock", {
        "region_id": first["region_id"], "translation_locked": True,
    })
    assert locked["error"] is None, locked["error"]

    merged = _rpc(server, "merge_regions", {
        "page_id": page_id,
        "region_ids": [first["region_id"], second["region_id"]],
    })
    assert merged["error"] is None, merged["error"]
    merged_id = merged["result"]["region_id"]

    detail = _rpc(server, "list_page_region_texts", {"page_id": page_id})["result"]
    row = next(item for item in detail["regions"] if item["region_id"] == merged_id)
    assert row["locks"]["translation_locked"] is True
    assert row["text"]["translation_locked"] is True
    _assert_no_orphan_regions(core)
