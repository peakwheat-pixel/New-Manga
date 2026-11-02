"""Region text read projection over the production Core service (V11R-F0-2).

Closes the V11R-F0-1 GAP-2: before this command the IPC had no way to read the
four-level text of an already-edited page, so the Studio Page mode could not
load real text on first paint (only ``list_regions``' minimal five-field DTO and
revision summaries existed).

The single read command ``list_page_region_texts`` returns, in ONE round trip,
every live region of one page with its REAL persisted projection: four-level
text, the three locks, review_state, origin, current revision number/id,
is_pinned of the current revision, all pinned revision numbers and the
normalized geometry. These tests prove the projection is the authoritative
SQLite state (not defaults/placeholders), the page-level 1-command load shape,
the strict optional filter (unknown or cross-page region -> TARGET_NOT_FOUND),
soft-deleted region invisibility, the empty-page/empty-list precedent, and the
typed validation errors -- all on a real production assembly with tmp roots.
"""

from __future__ import annotations

import io
import json
from pathlib import Path
import sys

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

NOW = "2026-01-01T00:00:00.000+00:00"
PAGE_WIDTH = 1000
PAGE_HEIGHT = 1500
RECT = [[0.1, 0.1], [0.4, 0.4]]
RECT_2 = [[0.5, 0.5], [0.8, 0.8]]


class Harness:
    def __init__(self, core) -> None:
        self.core = core
        self.server = CoreServiceServer(core)
        self._request_no = 0
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
        self.page_id = self.import_page((30, 60, 90, 255))

    # -- transport -----------------------------------------------------
    def rpc(self, command: str, payload: dict) -> dict:
        self._request_no += 1
        line = json.dumps({
            "protocol": "new-manga.core",
            "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
            "request_id": f"v11r-region-texts-{self._request_no}",
            "command": command,
            "payload": payload,
        })
        response, exit_flag = self.server.dispatch_request(line)
        assert not exit_flag
        assert response["version"] == {"major": 2, "minor": 3}
        return response

    def import_page(self, color: tuple[int, int, int, int]) -> str:
        buffer = io.BytesIO()
        Image.new("RGBA", (PAGE_WIDTH, PAGE_HEIGHT), color).save(
            buffer, format="PNG"
        )
        payload = buffer.getvalue()
        report = self.core.importer.import_files(
            "chapter",
            [ImportSource(f"source-{self._request_no}.png", lambda: payload)],
        )
        assert not report.failed and len(report.imported) == 1, report
        return report.imported[0].page.page_id

    # -- helpers -------------------------------------------------------
    def create_region(self, page_id: str, points) -> dict:
        response = self.rpc(
            "create_region",
            {"page_id": page_id, "geometry": {"points": points}},
        )
        assert response["error"] is None, response["error"]
        return response["result"]

    def read_texts(self, payload: dict) -> dict:
        response = self.rpc("list_page_region_texts", payload)
        assert response["error"] is None, response["error"]
        return response["result"]

    @staticmethod
    def assert_error(response: dict, code: str, category: str) -> None:
        assert response["result"] is None
        error = response["error"]
        assert error is not None
        assert error["code"] == code
        assert error["category"] == category
        assert error["retryable"] is False


@pytest.fixture()
def core(tmp_path: Path):
    assembled = assemble_production_core(tmp_path / "data")
    try:
        yield assembled
    finally:
        assembled.conn.close()


@pytest.fixture()
def harness(core) -> Harness:
    return Harness(core)


# ===========================================================================
# 1-command page load with the full REAL projection
# ===========================================================================


def test_one_command_returns_every_region_with_its_real_text(harness, core) -> None:
    first = harness.create_region(harness.page_id, RECT)
    second = harness.create_region(harness.page_id, RECT_2)

    # Real edit history on the first region: OCR -> machine translation ->
    # manual translation -> final confirmation.
    core.editing.apply_ocr_result(first["region_id"], "原文テキスト")
    core.editing.apply_machine_translation(first["region_id"], "机翻译文")
    core.editing.save_manual_translation(first["region_id"], "人工译文")
    core.editing.confirm_final(first["region_id"])

    result = harness.read_texts({"page_id": harness.page_id})

    assert result["page_id"] == harness.page_id
    assert result["page_size"] == {"width": PAGE_WIDTH, "height": PAGE_HEIGHT}
    assert [row["region_id"] for row in result["regions"]] == [
        first["region_id"], second["region_id"],
    ]
    rows = {row["region_id"]: row for row in result["regions"]}

    # -- the projection equals the authoritative persisted state ---------
    for region_id, row in rows.items():
        region = core.editing.get_region(region_id)
        current = core.editing.current_revision(region_id)
        assert row["text"] == current.snapshot["text"], region_id
        assert row["text"] == {
            "ocr_text": region.text.ocr_text,
            "machine_translation": region.text.machine_translation,
            "edited_translation": region.text.edited_translation,
            "final_translation": region.text.final_translation,
            "final_source": region.text.final_source,
            "edited_confirmed": region.text.edited_confirmed,
            "manual_edited": region.text.manual_edited,
            "translation_locked": region.text.translation_locked,
        }
        assert row["locks"] == {
            "region_locked": region.region_locked,
            "translation_locked": region.translation_locked,
            "inpaint_locked": region.inpaint_locked,
        }
        assert row["review_state"] == current.review_state.value
        assert row["origin"] == current.origin.value
        assert row["revision_no"] == current.revision_no
        assert row["current_revision_id"] == region.current_revision_id
        assert row["is_pinned"] == current.is_pinned
        assert row["region_type"] == region.region_type.value
        assert row["sfx_policy"] == region.sfx_policy.value
        assert row["reading_order"] == region.reading_order
        assert row["page_id"] == region.page_id

    # First region: the confirmed manual text is final (real four-track value).
    first_row = rows[first["region_id"]]
    assert first_row["text"]["ocr_text"] == "原文テキスト"
    assert first_row["text"]["machine_translation"] == "机翻译文"
    assert first_row["text"]["edited_translation"] == "人工译文"
    assert first_row["text"]["final_translation"] == "人工译文"
    assert first_row["text"]["final_source"] == "edited"
    assert first_row["text"]["edited_confirmed"] is True
    assert first_row["text"]["manual_edited"] is True
    assert first_row["text"]["translation_locked"] is True
    assert first_row["review_state"] == "confirmed"
    assert first_row["origin"] == "user"

    # Second region was never edited: the REAL empty values, not placeholders.
    second_row = rows[second["region_id"]]
    assert second_row["text"]["ocr_text"] == ""
    assert second_row["text"]["machine_translation"] == ""
    assert second_row["text"]["edited_translation"] == ""
    assert second_row["text"]["final_translation"] == ""
    assert second_row["text"]["final_source"] == "none"
    assert second_row["text"]["edited_confirmed"] is False
    assert second_row["text"]["manual_edited"] is False
    assert second_row["review_state"] == "unreviewed"


def test_geometry_matches_the_list_regions_read_face(harness) -> None:
    created = harness.create_region(harness.page_id, [[0.2, 0.1], [0.4, 0.3]])
    detail = harness.read_texts({"page_id": harness.page_id})["regions"][0]
    listed = harness.rpc("list_regions", {"page_id": harness.page_id})
    list_row = listed["result"]["regions"][0]
    assert detail["region_id"] == created["region_id"] == list_row["region_id"]
    assert detail["geometry"] == list_row["geometry"]
    assert detail["geometry"]["bbox"] == pytest.approx([0.2, 0.1, 0.2, 0.2])


def test_locks_and_pin_are_real_projections(harness, core) -> None:
    created = harness.create_region(harness.page_id, RECT)
    region_id = created["region_id"]

    # Explicit lock command: both translation projections are synced.
    locked = harness.rpc(
        "set_region_lock",
        {"region_id": region_id, "region_locked": True,
         "translation_locked": True, "inpaint_locked": True},
    )
    assert locked["error"] is None, locked["error"]
    # Pin the FIRST revision (current is now revision 2).
    pinned = harness.rpc(
        "pin_revision",
        {"region_id": region_id, "revision_no": 1, "pinned": True},
    )
    assert pinned["error"] is None, pinned["error"]

    row = harness.read_texts({"page_id": harness.page_id})["regions"][0]
    assert row["locks"] == {
        "region_locked": True,
        "translation_locked": True,
        "inpaint_locked": True,
    }
    assert row["is_pinned"] is False  # current revision (2) is not the pinned one
    assert row["pinned_revision_nos"] == [1]
    assert row["revision_no"] == 2
    # Pin never rewrites history nor the current pointer.
    current = core.editing.current_revision(region_id)
    assert current.revision_no == 2
    assert current.is_pinned is False


def test_manual_save_arms_text_lock_but_not_the_region_lock_column(
    harness, core
) -> None:
    """GAP-3 reality preserved: the manual save writes the text-level manual
    protection flag only; the explicit lock command is what syncs both
    projections. This read face projects both raw values, so the UI can show
    the authoritative manual-protection flag without inventing state."""
    created = harness.create_region(harness.page_id, RECT)
    core.editing.save_manual_translation(created["region_id"], "人工译文")
    row = harness.read_texts({"page_id": harness.page_id})["regions"][0]
    assert row["text"]["translation_locked"] is True
    assert row["locks"]["translation_locked"] is False


# ===========================================================================
# page / empty / deleted semantics
# ===========================================================================


def test_soft_deleted_region_is_not_projected(harness) -> None:
    kept = harness.create_region(harness.page_id, RECT)
    removed = harness.create_region(harness.page_id, RECT_2)
    deleted = harness.rpc(
        "delete_region", {"region_id": removed["region_id"]}
    )
    assert deleted["error"] is None, deleted["error"]

    result = harness.read_texts({"page_id": harness.page_id})
    assert [row["region_id"] for row in result["regions"]] == [
        kept["region_id"],
    ]


def test_page_without_regions_is_an_empty_list_not_an_error(harness) -> None:
    result = harness.read_texts({"page_id": harness.page_id})
    assert result == {
        "page_id": harness.page_id,
        "page_size": {"width": PAGE_WIDTH, "height": PAGE_HEIGHT},
        "regions": [],
    }


def test_unknown_page_reads_empty_data_not_an_error(harness) -> None:
    result = harness.read_texts({"page_id": "unknown-page"})
    assert result == {
        "page_id": "unknown-page",
        "page_size": None,
        "regions": [],
    }


# ===========================================================================
# optional strict region_ids filter (covers unknown + cross-page ids)
# ===========================================================================


def test_region_ids_filter_projects_only_the_requested_live_regions(
    harness,
) -> None:
    first = harness.create_region(harness.page_id, RECT)
    second = harness.create_region(harness.page_id, RECT_2)
    result = harness.read_texts({
        "page_id": harness.page_id,
        "region_ids": [second["region_id"]],
    })
    assert [row["region_id"] for row in result["regions"]] == [
        second["region_id"],
    ]
    # Reading order is preserved, not the request order.
    both = harness.read_texts({
        "page_id": harness.page_id,
        "region_ids": [second["region_id"], first["region_id"]],
    })
    assert [row["region_id"] for row in both["regions"]] == [
        first["region_id"], second["region_id"],
    ]


def test_region_ids_filter_rejects_unknown_and_cross_page_ids(harness) -> None:
    created = harness.create_region(harness.page_id, RECT)
    unknown = harness.rpc(
        "list_page_region_texts",
        {"page_id": harness.page_id, "region_ids": ["missing-region"]},
    )
    harness.assert_error(unknown, "TARGET_NOT_FOUND", "not_found")

    other_page = harness.import_page((120, 20, 160, 255))
    other_region = harness.create_region(other_page, RECT)
    cross_page = harness.rpc(
        "list_page_region_texts",
        {"page_id": harness.page_id,
         "region_ids": [created["region_id"], other_region["region_id"]]},
    )
    harness.assert_error(cross_page, "TARGET_NOT_FOUND", "not_found")

    # The other page still reads its own region normally.
    own = harness.read_texts({"page_id": other_page})
    assert [row["region_id"] for row in own["regions"]] == [
        other_region["region_id"],
    ]


# ===========================================================================
# typed validation
# ===========================================================================


def test_invalid_payloads_are_typed_validation_errors(harness) -> None:
    for payload in (
        {},
        {"page_id": ""},
        {"page_id": 5},
        {"page_id": harness.page_id, "region_ids": []},
        {"page_id": harness.page_id, "region_ids": "r1"},
        {"page_id": harness.page_id, "region_ids": [""]},
        {"page_id": harness.page_id, "region_ids": [5]},
        {"page_id": harness.page_id, "region_ids": ["r1", "r1"]},
    ):
        harness.assert_error(
            harness.rpc("list_page_region_texts", payload),
            "INVALID_REQUEST",
            "validation",
        )
    # zero write: a rejected read never creates/photocopies region rows
    assert harness.read_texts({"page_id": harness.page_id})["regions"] == []


def test_command_stays_on_the_region_family_minor_and_unknown_commands_fail(
    harness,
) -> None:
    from bootstrap import core_service as module

    assert module.PROTOCOL_MINOR == 3
    unknown = harness.rpc("list_page_region_textz", {"page_id": harness.page_id})
    harness.assert_error(unknown, "UNKNOWN_COMMAND", "validation")
