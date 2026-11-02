"""RC-4 wire-level evidence for list_region_revisions / restore_region_revision.

DSH r1 RC4-01: the frozen contract's verification Gate explicitly requires
"真实 SQLite restore（历史/pin/人工文字/Lock、过期与事务中竞态）".  Existing
coverage only exercised the legacy ``restore_revision`` signature; this file
pins the RC-4 wire surface: DTO shape, typed rejections, the stale
``expected_revision`` zero-write conflict, and the in-transaction race where
two independent Core connections race on the same expected revision and
exactly one restored revision may appear.
"""

from __future__ import annotations

import io
import json
import sys
import threading
from pathlib import Path

from PIL import Image

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from application.importing.images.ports import ImportSource
from bootstrap.core_service import (
    PROTOCOL_MAJOR,
    PROTOCOL_MINOR,
    CoreServiceServer,
    assemble_production_core,
)
from domain.regions.entities import BBox, RegionGeometry

NOW = "2026-01-01T00:00:00.000+00:00"

SUMMARY_FIELDS = {
    "region_revision_id",
    "revision_no",
    "origin",
    "review_state",
    "is_pinned",
    "restored_from_revision_id",
    "created_at",
    "region_type",
    "sfx_policy",
    "is_current",
}


def _rpc(command: str, request_id: str, payload: dict) -> str:
    return json.dumps(
        {
            "protocol": "new-manga.core",
            "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
            "request_id": request_id,
            "command": command,
            "payload": payload,
        }
    )


def _seed_region(core, tmp_path: Path) -> tuple[str, str]:
    """One page with a speech region holding three revisions of history."""
    with core.conn:
        core.conn.execute(
            "INSERT INTO books (book_id,title,created_at,updated_at) VALUES ('book','b',?,?)",
            (NOW, NOW),
        )
        core.conn.execute(
            "INSERT INTO chapters (chapter_id,book_id,title,created_at,updated_at)"
            " VALUES ('chapter','book','c',?,?)",
            (NOW, NOW),
        )
    source_path = tmp_path / "rc4-revision-source.png"
    buffer = io.BytesIO()
    Image.new("RGBA", (200, 140), (30, 60, 200, 255)).save(buffer, format="PNG")
    source_path.write_bytes(buffer.getvalue())
    report = core.importer.import_files(
        "chapter", [ImportSource("source.png", source_path.read_bytes)]
    )
    assert not report.failed and len(report.imported) == 1
    page = core.repository.get_page(report.imported[0].page.page_id)
    assert page is not None
    speech = core.editing.create_region(
        page.page_id,
        RegionGeometry(bbox=BBox(20, 20, 130, 100)),
    )
    core.editing.save_manual_translation(speech.region_id, "FIRST TEXT")
    core.editing.confirm_final(speech.region_id)
    core.editing.save_manual_translation(speech.region_id, "SECOND TEXT")
    return speech.region_id, page.page_id


def _summaries(server, region_id: str) -> dict:
    res, _ = server.dispatch_request(_rpc("list_region_revisions", "r-1", {"region_id": region_id}))
    assert res["error"] is None, res["error"]
    return res["result"]


def _summary_by_no(result: dict, revision_no: int) -> dict:
    return next(r for r in result["revisions"] if r["revision_no"] == revision_no)


def test_list_projects_full_history_in_revision_order(tmp_path) -> None:
    core = assemble_production_core(tmp_path / "data")
    try:
        region_id, _page_id = _seed_region(core, tmp_path)
        server = CoreServiceServer(core)
        data = _summaries(server, region_id)

        assert data["region_id"] == region_id
        # create_region commits revision 1 (user/unreviewed); the two manual
        # saves and the confirm add revisions 2-4.
        assert data["current_revision_no"] == 4
        assert [rev["revision_no"] for rev in data["revisions"]] == [1, 2, 3, 4]
        for rev in data["revisions"]:
            assert set(rev) == SUMMARY_FIELDS, sorted(rev)
        currents = [rev for rev in data["revisions"] if rev["is_current"]]
        assert len(currents) == 1 and currents[0]["revision_no"] == 4
        assert _summary_by_no(data, 3)["review_state"] == "confirmed"
        assert _summary_by_no(data, 2)["review_state"] == "needs_review"
        assert all(rev["origin"] == "user" for rev in data["revisions"])
        assert all(rev["restored_from_revision_id"] is None for rev in data["revisions"])
    finally:
        core.conn.close()


def test_list_unknown_region_is_typed_target_not_found(tmp_path) -> None:
    core = assemble_production_core(tmp_path / "data")
    try:
        server = CoreServiceServer(core)
        res, should_exit = server.dispatch_request(
            _rpc("list_region_revisions", "r-2", {"region_id": "no-such-region"})
        )
        assert should_exit is False
        assert res["result"] is None
        assert res["error"]["code"] == "TARGET_NOT_FOUND"
        assert res["error"]["category"] == "not_found"
        assert res["error"]["retryable"] is False
    finally:
        core.conn.close()


def test_restore_creates_new_restored_revision_and_preserves_history(tmp_path) -> None:
    core = assemble_production_core(tmp_path / "data")
    try:
        region_id, page_id = _seed_region(core, tmp_path)
        core.editing.set_revision_pinned(region_id, 3, True)
        server = CoreServiceServer(core)
        before = _summaries(server, region_id)
        source_summary = _summary_by_no(before, 3)

        res, _ = server.dispatch_request(
            _rpc(
                "restore_region_revision",
                "r-3",
                {"region_id": region_id, "revision_no": 3, "expected_revision": 4},
            )
        )
        assert res["error"] is None, res["error"]
        assert res["result"] == {
            "region_id": region_id,
            "revision_no": 5,
            "region_type": source_summary["region_type"],
            "sfx_policy": source_summary["sfx_policy"],
        }

        after = _summaries(server, region_id)
        assert after["current_revision_no"] == 5
        assert len(after["revisions"]) == len(before["revisions"]) + 1
        restored = _summary_by_no(after, 5)
        assert restored["origin"] == "restored"
        assert restored["review_state"] == "needs_review"
        assert restored["is_pinned"] is False
        assert restored["restored_from_revision_id"] == source_summary["region_revision_id"]
        assert restored["is_current"] is True
        assert restored["region_type"] == source_summary["region_type"]
        assert restored["sfx_policy"] == source_summary["sfx_policy"]
        # The source revision, its pin, and the untouched history all survive.
        assert _summary_by_no(after, 3)["is_pinned"] is True
        for rev in before["revisions"]:
            kept = _summary_by_no(after, rev["revision_no"])
            assert kept["region_revision_id"] == rev["region_revision_id"]
            assert kept["origin"] == rev["origin"]
            assert kept["review_state"] == rev["review_state"]
        # No pointer move: the source revision is NOT current after restore.
        assert _summary_by_no(after, 3)["is_current"] is False

        region = next(r for r in core.editing.list_regions(page_id) if r.region_id == region_id)
        # Revision 3 is the confirmed save: the manual final comes back and
        # the save's automatic translation lock rides along in the snapshot.
        assert region.text.final_translation == "FIRST TEXT"
        assert region.text.translation_locked is True
    finally:
        core.conn.close()


def test_restore_stale_expected_revision_conflicts_with_zero_writes(tmp_path) -> None:
    core = assemble_production_core(tmp_path / "data")
    try:
        region_id, _page_id = _seed_region(core, tmp_path)
        server = CoreServiceServer(core)
        stale = _summaries(server, region_id)["current_revision_no"]

        core.editing.save_manual_translation(region_id, "THIRD TEXT")

        res, should_exit = server.dispatch_request(
            _rpc(
                "restore_region_revision",
                "r-4",
                {"region_id": region_id, "revision_no": 1, "expected_revision": stale},
            )
        )
        assert should_exit is False
        assert res["result"] is None
        assert res["error"]["code"] == "INPUT_REVISION_CHANGED"
        assert res["error"]["category"] == "conflict"
        assert res["error"]["retryable"] is False
        assert res["error"]["message"] == "region revision changed since it was read"

        after = _summaries(server, region_id)
        assert after["current_revision_no"] == stale + 1
        assert len(after["revisions"]) == 5
        assert all(rev["origin"] != "restored" for rev in after["revisions"])
    finally:
        core.conn.close()


def test_restore_validates_positive_integers(tmp_path) -> None:
    core = assemble_production_core(tmp_path / "data")
    try:
        region_id, _page_id = _seed_region(core, tmp_path)
        server = CoreServiceServer(core)
        for payload in (
            {"region_id": region_id, "revision_no": 0, "expected_revision": 1},
            {"region_id": region_id, "revision_no": 1, "expected_revision": 0},
            {"region_id": region_id, "revision_no": "1", "expected_revision": 1},
            {"region_id": region_id, "revision_no": 1.5, "expected_revision": 1},
            {"region_id": region_id, "revision_no": True, "expected_revision": 1},
            {"region_id": region_id, "revision_no": 1},
            {"revision_no": 1, "expected_revision": 1},
        ):
            res, _ = server.dispatch_request(_rpc("restore_region_revision", "r-5", payload))
            assert res["result"] is None, payload
            assert res["error"]["code"] == "INVALID_REQUEST", payload
            assert res["error"]["category"] == "validation", payload
    finally:
        core.conn.close()


def test_restore_unknown_region_or_revision_is_typed_target_not_found(tmp_path) -> None:
    core = assemble_production_core(tmp_path / "data")
    try:
        region_id, _page_id = _seed_region(core, tmp_path)
        server = CoreServiceServer(core)
        for payload in (
            {"region_id": "no-such-region", "revision_no": 1, "expected_revision": 1},
            # A valid expected guard comes first (TOCTOU-safe), so the unknown
            # source revision is only reachable with a CURRENT expected number.
            {"region_id": region_id, "revision_no": 99, "expected_revision": 4},
        ):
            res, _ = server.dispatch_request(_rpc("restore_region_revision", "r-6", payload))
            assert res["result"] is None, payload
            assert res["error"]["code"] == "TARGET_NOT_FOUND", payload
            assert res["error"]["category"] == "not_found", payload
    finally:
        core.conn.close()


def test_restore_race_on_same_expected_revision_exactly_one_applies(tmp_path) -> None:
    """Two independent Core connections, one shared SQLite file.

    Both threads dispatch the wire restore with the SAME expected_revision.
    The BEGIN IMMEDIATE seam serializes them: exactly one applied, the loser
    conflicts with zero writes, and the file ends with exactly one extra
    restored revision.
    """
    data_root = tmp_path / "data"
    core = assemble_production_core(data_root)
    try:
        region_id, _page_id = _seed_region(core, tmp_path)
        expected = core.editing.list_revision_summaries(region_id)["current_revision_no"]
        payload = {"region_id": region_id, "revision_no": 1, "expected_revision": expected}
    finally:
        core.conn.close()

    results: list[dict] = []
    barrier = threading.Barrier(2)

    def _racer() -> None:
        racer_core = assemble_production_core(data_root)
        try:
            racer_server = CoreServiceServer(racer_core)
            barrier.wait(timeout=10)
            res, _ = racer_server.dispatch_request(_rpc("restore_region_revision", "race", payload))
            results.append(res)
        finally:
            racer_core.conn.close()

    threads = [threading.Thread(target=_racer) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=30)

    assert len(results) == 2
    applied = [res for res in results if res["error"] is None]
    conflicted = [res for res in results if res["error"] is not None]
    assert len(applied) == 1, results
    assert len(conflicted) == 1
    assert conflicted[0]["error"]["code"] == "INPUT_REVISION_CHANGED"
    assert applied[0]["result"]["revision_no"] == expected + 1

    witness = assemble_production_core(data_root)
    try:
        data = witness.editing.list_revision_summaries(region_id)
        assert data["current_revision_no"] == expected + 1
        restored = [rev for rev in data["revisions"] if rev["origin"] == "restored"]
        assert len(restored) == 1
        assert restored[0]["revision_no"] == expected + 1
        assert restored[0]["restored_from_revision_id"] is not None
    finally:
        witness.conn.close()
