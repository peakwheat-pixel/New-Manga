"""V11R-F0-1 I3/P2-A: the page region cap is enforced INSIDE the write transaction.

Review r3 (P2-A): the 500-live-region page cap was checked in the service/wire
BEFORE the transaction. Two callers that both counted ``limit - 1`` could both
insert, ending at ``limit + 1``.

The fix passes ``(page_id, limit)`` into ``commit_region_batch``: the live count
is re-read inside the same ``BEGIN IMMEDIATE`` and count >= limit rolls the
batch back with ``REGION_LIMIT_EXCEEDED`` (service -> RegionLimitExceeded,
wire INVALID_REQUEST/validation, zero write).

The concurrency test lowers the limit to 2, starts from 1 live region and lets
both creators pass the pre-check at a barrier before either transaction starts.
"""

from __future__ import annotations

import io
import json
from pathlib import Path
import sys
import threading

import pytest
from PIL import Image

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

import application.editing.service as editing_service  # noqa: E402
from application.editing.errors import RegionLimitExceeded  # noqa: E402
from application.editing.ports import (  # noqa: E402
    RegionCommitStatus,
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
    Region,
    RegionGeometry,
    RegionOrigin,
    RegionRevision,
    ReviewState,
)

NOW = "2026-01-01T00:00:00.000+00:00"
RECT = RegionGeometry(bbox=BBox(10, 10, 60, 40))


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
        "chapter", [ImportSource("create-cap.png", lambda: payload)]
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


def _live_count(core, page_id: str) -> int:
    return len(core.editing.list_regions(page_id))


def test_sequential_create_at_cap_is_rejected_without_write(core, monkeypatch):
    monkeypatch.setattr(editing_service, "MAX_REGIONS_PER_PAGE", 2)
    page_id = _seed_page(core)
    for index in range(2):
        core.editing.create_region(
            page_id, RegionGeometry(bbox=BBox(10 + index * 70, 10, 50, 40))
        )
    revisions_before = core.conn.execute(
        "SELECT COUNT(*) FROM region_revisions"
    ).fetchone()[0]

    with pytest.raises(RegionLimitExceeded):
        core.editing.create_region(page_id, RECT)

    assert _live_count(core, page_id) == 2
    assert core.conn.execute(
        "SELECT COUNT(*) FROM region_revisions"
    ).fetchone()[0] == revisions_before


def test_batch_page_cap_is_the_authority_even_if_the_precheck_passed(core):
    """Direct seam probe: the pre-check counted limit-1, but by the time the
    transaction runs the page is full -> REGION_LIMIT_EXCEEDED, zero write."""
    page_id = _seed_page(core)
    first = core.editing.create_region(page_id, RECT)
    core.editing.create_region(page_id, RegionGeometry(bbox=BBox(100, 10, 50, 40)))

    new_region = Region(
        region_id="racing-region",
        page_id=page_id,
        region_type=first.region_type,
        reading_order=3,
        geometry=RECT,
        sfx_policy=first.sfx_policy,
    )
    revision = RegionRevision(
        region_revision_id="racing-revision",
        region_id="racing-region",
        revision_no=0,
        snapshot=new_region.snapshot_state(),
        origin=RegionOrigin.USER,
        review_state=ReviewState.UNREVIEWED,
    )
    result = core.editing._committer.commit_region_batch(
        new_regions=[(new_region, revision)],
        page_region_limit=(page_id, 2),
    )
    assert result.status is RegionCommitStatus.REGION_LIMIT_EXCEEDED
    assert _live_count(core, page_id) == 2
    assert core.conn.execute(
        "SELECT COUNT(*) FROM regions WHERE region_id = 'racing-region'"
    ).fetchone()[0] == 0


def test_concurrent_creates_at_the_cap_boundary_cannot_overshoot(
    core, monkeypatch
):
    monkeypatch.setattr(editing_service, "MAX_REGIONS_PER_PAGE", 2)
    page_id = _seed_page(core)
    core.editing.create_region(page_id, RECT)  # 1 live region; limit is 2

    barrier = threading.Barrier(2)
    original = type(core.editing)._commit_batch_or_raise

    def gated(self, **batch):
        if batch.get("page_region_limit") is not None:
            barrier.wait(timeout=10)  # both pre-checks passed, no tx started
        return original(self, **batch)

    monkeypatch.setattr(type(core.editing), "_commit_batch_or_raise", gated)

    results: list[RegionLimitExceeded] = []
    created: list = []

    def create(index: int) -> None:
        try:
            created.append(
                core.editing.create_region(
                    page_id,
                    RegionGeometry(bbox=BBox(10 + index * 70, 10, 50, 40)),
                )
            )
        except RegionLimitExceeded as error:
            results.append(error)

    threads = [
        threading.Thread(target=create, args=(index,), daemon=True)
        for index in (1, 2)
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=15)
        assert not thread.is_alive()

    # Exactly one creator wins; the other is a typed limit rejection; the page
    # never exceeds the limit (the pre-I3 code could reach 3 here).
    assert len(created) == 1
    assert len(results) == 1
    assert _live_count(core, page_id) == 2
    orphan = core.conn.execute(
        "SELECT COUNT(*) FROM regions r LEFT JOIN region_revisions rev"
        " ON rev.region_revision_id = r.current_revision_id"
        " WHERE r.current_revision_id IS NULL OR rev.region_revision_id IS NULL"
    ).fetchone()[0]
    assert orphan == 0


def test_wire_create_at_cap_is_invalid_request(core, monkeypatch):
    import bootstrap.core_service as core_service

    page_id = _seed_page(core)
    server = CoreServiceServer(core)
    monkeypatch.setattr(core_service, "MAX_REGIONS_PER_PAGE", 1)
    first = _rpc(server, "create_region", {
        "page_id": page_id, "geometry": {"points": [[0.1, 0.1], [0.3, 0.3]]},
    })
    assert first["error"] is None, first["error"]
    second = _rpc(server, "create_region", {
        "page_id": page_id, "geometry": {"points": [[0.5, 0.5], [0.7, 0.7]]},
    })
    assert second["error"]["code"] == "INVALID_REQUEST"
    assert second["error"]["category"] == "validation"
    assert _live_count(core, page_id) == 1


def _rpc(server, command: str, payload: dict) -> dict:
    line = json.dumps({
        "protocol": "new-manga.core",
        "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
        "request_id": f"i3-cap-{command}",
        "command": command,
        "payload": payload,
    })
    response, exit_flag = server.dispatch_request(line)
    assert not exit_flag
    return response
