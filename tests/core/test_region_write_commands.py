"""Region write face over the production Core service (V11R-F0-1).

Audit §5.1 F-01: the Studio Page edit main path (create / delete / geometry /
merge / split / reorder / manual translation / confirm final / locks / pin) had
no IPC channel; only ``set_region_type`` / ``list_regions`` /
``list_region_revisions`` / ``restore_region_revision`` / ``renderer_page``
existed. This module pins the ten new stdio JSON-lines commands end to end on a
REAL production assembly (temp data root, no hardcoded absolute paths):

- success: the post-write effective state is projected from the same
  authoritative objects the write path updated;
- optimistic lock: a stale ``expected_revision`` / ``expected_revisions`` is
  the existing INPUT_REVISION_CHANGED/conflict literal with ZERO write;
- invalid parameters: typed INVALID_REQUEST/validation BEFORE any
  persistence (fail-closed write-side validation);
- not found: TARGET_NOT_FOUND/not_found (region, page or revision);
- data safety: current/pinned revisions survive, soft delete hides a region
  without touching its history, a lock change is a revision and survives a
  Core restart, and the wire geometry is the normalized shape owned by
  ``application/editing/region_canvas.py``.

The commands ride envelope minor 3 (the frozen Region family minor) -- zero
protocol bump, pinned by the assertions below.
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
PARTS = [[[0.1, 0.1], [0.25, 0.4]], [[0.25, 0.1], [0.4, 0.4]]]


class Harness:
    """A production assembly plus a dispatch helper (no HTTP, no Qt)."""

    def __init__(self, core) -> None:
        self.core = core
        self.server = CoreServiceServer(core)
        self._request_no = 0
        self.page_id = self._seed_page()

    # -- transport -----------------------------------------------------
    def rpc(self, command: str, payload: dict) -> dict:
        self._request_no += 1
        line = json.dumps({
            "protocol": "new-manga.core",
            "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
            "request_id": f"v11r-region-write-{self._request_no}",
            "command": command,
            "payload": payload,
        })
        response, exit_flag = self.server.dispatch_request(line)
        assert not exit_flag
        assert response["protocol"] == "new-manga.core"
        # Zero protocol bump: every added command answers at the frozen
        # Region family minor (3).
        assert response["version"] == {"major": 2, "minor": 3}
        return response

    @staticmethod
    def assert_error(response: dict, code: str, category: str) -> None:
        assert response["result"] is None
        error = response["error"]
        assert error is not None
        assert error["code"] == code
        assert error["category"] == category
        assert error["retryable"] is False

    # -- fixtures ------------------------------------------------------
    def _seed_page(self) -> str:
        with self.core.conn:
            self.core.conn.execute(
                "INSERT INTO books (book_id,title,created_at,updated_at)"
                " VALUES ('book','b',?,?)",
                (NOW, NOW),
            )
            self.core.conn.execute(
                "INSERT INTO chapters (chapter_id,book_id,title,created_at,updated_at)"
                " VALUES ('chapter','book','c',?,?)",
                (NOW, NOW),
            )
        buffer = io.BytesIO()
        Image.new("RGBA", (PAGE_WIDTH, PAGE_HEIGHT), (20, 40, 80, 255)).save(
            buffer, format="PNG"
        )
        payload = buffer.getvalue()
        report = self.core.importer.import_files(
            "chapter", [ImportSource("source.png", lambda: payload)]
        )
        assert not report.failed and len(report.imported) == 1, report
        return report.imported[0].page.page_id

    # -- helpers -------------------------------------------------------
    def create(self, points=None, **extra) -> dict:
        payload = {"page_id": self.page_id, "geometry": {"points": points or RECT}}
        payload.update(extra)
        response = self.rpc("create_region", payload)
        assert response["error"] is None, response["error"]
        return response["result"]

    def revision_count(self, region_id: str) -> int:
        response = self.rpc("list_region_revisions", {"region_id": region_id})
        assert response["error"] is None, response["error"]
        return len(response["result"]["revisions"])

    def current_revision_no(self, region_id: str) -> int:
        response = self.rpc("list_region_revisions", {"region_id": region_id})
        assert response["error"] is None, response["error"]
        return response["result"]["current_revision_no"]

    def region_ids(self) -> list[str]:
        response = self.rpc("list_regions", {"page_id": self.page_id})
        assert response["error"] is None, response["error"]
        return [row["region_id"] for row in response["result"]["regions"]]

    def stored_revision_numbers(self, region_id: str) -> list[int]:
        """History stays addressable behind a soft delete, so read the
        immutable rows directly (the read command hides soft-deleted
        regions, matching the frozen list semantics)."""
        rows = self.core.conn.execute(
            "SELECT revision_no FROM region_revisions WHERE region_id = ?"
            " ORDER BY revision_no",
            (region_id,),
        ).fetchall()
        return [row["revision_no"] for row in rows]


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
# create_region
# ===========================================================================


def test_create_region_returns_effective_state_and_first_revision(harness) -> None:
    result = harness.create()
    assert result["region_type"] == "speech"
    assert result["sfx_policy"] == "skip"
    assert result["reading_order"] == 1
    assert result["revision_no"] == 1
    assert harness.revision_count(result["region_id"]) == 1
    # Geometry is normalized on the wire and persisted as page pixels: the
    # existing list_regions read face projects the same normalized shape back.
    read = harness.rpc("list_regions", {"page_id": harness.page_id})
    row = read["result"]["regions"][0]
    assert row["geometry"]["bbox"] == pytest.approx([0.1, 0.1, 0.3, 0.3])
    assert row["geometry"]["polygon"] == [
        [0.1, 0.1], [0.4, 0.1], [0.4, 0.4], [0.1, 0.4],
    ]


def test_create_region_appends_reading_order_and_accepts_explicit_order(
    harness,
) -> None:
    first = harness.create(RECT)
    second = harness.create(RECT_2)
    assert (first["reading_order"], second["reading_order"]) == (1, 2)
    explicit = harness.create(
        [[0.0, 0.6], [0.2, 0.8]], reading_order=7
    )
    assert explicit["reading_order"] == 7


def test_create_region_applies_the_shared_ev8_sfx_rule(harness) -> None:
    harness.rpc(
        "settings.update_section",
        {"section": "sfx", "values": {"policy": "translate"}},
    )
    plain = harness.create(RECT)
    assert plain["sfx_policy"] == "skip"  # policy never leaks to non-SFX
    sfx = harness.create(RECT_2, region_type="sfx")
    assert sfx["sfx_policy"] == "translate"


def test_create_region_rejects_invalid_parameters(harness) -> None:
    cases = [
        {},
        {"page_id": ""},
        {"page_id": harness.page_id},
        {"page_id": harness.page_id, "geometry": {}},
        {"page_id": harness.page_id, "geometry": {"points": [[0.1, 0.1]]}},
        {"page_id": harness.page_id, "geometry": {"points": [[0.1, 0.1], [1.2, 0.4]]}},
        {"page_id": harness.page_id, "geometry": {"points": [[0.1, 0.1], [0.4, True]]}},
        {"page_id": harness.page_id, "geometry": {"points": [[0.1, 0.1], [0.4, 0.4]]},
         "region_type": "bubble"},
        {"page_id": harness.page_id, "geometry": {"points": [[0.1, 0.1], [0.4, 0.4]]},
         "reading_order": 0},
        {"page_id": "unknown-page", "geometry": {"points": RECT}},
    ]
    for payload in cases:
        response = harness.rpc("create_region", payload)
        if payload.get("page_id") == "unknown-page":
            harness.assert_error(response, "TARGET_NOT_FOUND", "not_found")
        else:
            harness.assert_error(response, "INVALID_REQUEST", "validation")
    # zero write: no region appears for the page
    assert harness.region_ids() == []


def test_create_region_rejects_degenerate_geometry(harness) -> None:
    response = harness.rpc(
        "create_region",
        {"page_id": harness.page_id,
         "geometry": {"points": [[0.2, 0.2], [0.2, 0.2]]}},
    )
    harness.assert_error(response, "INVALID_REQUEST", "validation")
    assert "DEGENERATE_GEOMETRY" in response["error"]["message"]


# ===========================================================================
# delete_region
# ===========================================================================


def test_delete_region_soft_deletes_without_touching_history(harness) -> None:
    created = harness.create()
    region_id = created["region_id"]
    before = harness.revision_count(region_id)

    response = harness.rpc("delete_region", {"region_id": region_id})
    assert response["error"] is None, response["error"]
    assert response["result"] == {"region_id": region_id, "deleted": True}

    assert harness.region_ids() == []
    # History + current pointer stay addressable (soft delete only).
    assert harness.stored_revision_numbers(region_id) == list(range(1, before + 1))
    stored = harness.core.conn.execute(
        "SELECT current_revision_id FROM regions WHERE region_id = ?",
        (region_id,),
    ).fetchone()
    assert stored["current_revision_id"] is not None


def test_delete_region_is_not_idempotent_but_safe(harness) -> None:
    created = harness.create()
    assert harness.rpc("delete_region", {"region_id": created["region_id"]})[
        "error"
    ] is None
    second = harness.rpc("delete_region", {"region_id": created["region_id"]})
    harness.assert_error(second, "TARGET_NOT_FOUND", "not_found")


def test_delete_region_rejects_stale_expectation_and_bad_parameters(harness) -> None:
    created = harness.create()
    region_id = created["region_id"]
    stale = harness.rpc(
        "delete_region", {"region_id": region_id, "expected_revision": 99}
    )
    harness.assert_error(stale, "INPUT_REVISION_CHANGED", "conflict")
    assert harness.region_ids() == [region_id]  # zero write

    harness.assert_error(
        harness.rpc("delete_region", {}), "INVALID_REQUEST", "validation"
    )
    harness.assert_error(
        harness.rpc("delete_region", {"region_id": region_id,
                                      "expected_revision": "1"}),
        "INVALID_REQUEST",
        "validation",
    )
    harness.assert_error(
        harness.rpc("delete_region", {"region_id": "missing"}),
        "TARGET_NOT_FOUND",
        "not_found",
    )


# ===========================================================================
# save_region_geometry
# ===========================================================================


def test_save_region_geometry_creates_one_user_revision(harness) -> None:
    created = harness.create()
    response = harness.rpc(
        "save_region_geometry",
        {
            "region_id": created["region_id"],
            "geometry": {"points": [[0.2, 0.2], [0.5, 0.5]]},
            "expected_revision": created["revision_no"],
        },
    )
    assert response["error"] is None, response["error"]
    result = response["result"]
    assert result["revision_no"] == created["revision_no"] + 1
    assert result["geometry"]["bbox"] == pytest.approx([0.2, 0.2, 0.3, 0.3])
    assert harness.current_revision_no(created["region_id"]) == result["revision_no"]


def test_save_region_geometry_conflict_has_zero_write(harness) -> None:
    created = harness.create()
    harness.rpc(
        "save_region_geometry",
        {"region_id": created["region_id"],
         "geometry": {"points": [[0.2, 0.2], [0.5, 0.5]]}},
    )
    current = harness.current_revision_no(created["region_id"])
    stale = harness.rpc(
        "save_region_geometry",
        {"region_id": created["region_id"],
         "geometry": {"points": [[0.3, 0.3], [0.6, 0.6]]},
         "expected_revision": created["revision_no"]},
    )
    harness.assert_error(stale, "INPUT_REVISION_CHANGED", "conflict")
    assert harness.current_revision_no(created["region_id"]) == current
    read = harness.rpc("list_regions", {"page_id": harness.page_id})
    assert read["result"]["regions"][0]["geometry"]["bbox"] == pytest.approx(
        [0.2, 0.2, 0.3, 0.3]
    )


def test_save_region_geometry_rejects_invalid_parameters(harness) -> None:
    created = harness.create()
    cases = [
        {},
        {"region_id": created["region_id"]},
        {"region_id": created["region_id"], "geometry": {"points": [[0.2, 0.2]]}},
        {"region_id": created["region_id"],
         "geometry": {"points": [[0.2, 0.2], [0.5, 0.5]]},
         "expected_revision": 0},
    ]
    for payload in cases:
        harness.assert_error(
            harness.rpc("save_region_geometry", payload),
            "INVALID_REQUEST",
            "validation",
        )
    harness.assert_error(
        harness.rpc(
            "save_region_geometry",
            {"region_id": "missing", "geometry": {"points": RECT}},
        ),
        "TARGET_NOT_FOUND",
        "not_found",
    )


# ===========================================================================
# merge_regions
# ===========================================================================


def test_merge_regions_soft_deletes_sources_and_starts_new_history(harness) -> None:
    first = harness.create()
    second = harness.create(RECT_2)
    response = harness.rpc(
        "merge_regions",
        {"page_id": harness.page_id,
         "region_ids": [first["region_id"], second["region_id"]]},
    )
    assert response["error"] is None, response["error"]
    result = response["result"]
    assert sorted(result["deleted_region_ids"]) == sorted(
        [first["region_id"], second["region_id"]]
    )
    assert result["revision_no"] == 1  # merged region starts its own history
    assert harness.region_ids() == [result["region_id"]]
    # Source history is preserved behind the soft delete.
    assert harness.stored_revision_numbers(first["region_id"]) == [1]


def test_merge_regions_rejects_stale_source_expectation(harness) -> None:
    first = harness.create()
    second = harness.create(RECT_2)
    current = harness.current_revision_no(first["region_id"])
    response = harness.rpc(
        "merge_regions",
        {
            "page_id": harness.page_id,
            "region_ids": [first["region_id"], second["region_id"]],
            "expected_revisions": {
                first["region_id"]: current + 5,
                second["region_id"]: second["revision_no"],
            },
        },
    )
    harness.assert_error(response, "INPUT_REVISION_CHANGED", "conflict")
    # zero write: both regions are still live with unchanged history
    assert sorted(harness.region_ids()) == sorted(
        [first["region_id"], second["region_id"]]
    )
    assert harness.current_revision_no(first["region_id"]) == current


def test_merge_regions_requires_full_expectation_coverage(harness) -> None:
    first = harness.create()
    second = harness.create(RECT_2)
    response = harness.rpc(
        "merge_regions",
        {
            "page_id": harness.page_id,
            "region_ids": [first["region_id"], second["region_id"]],
            "expected_revisions": {first["region_id"]: 1},
        },
    )
    harness.assert_error(response, "INVALID_REQUEST", "validation")


def test_merge_regions_rejects_invalid_parameters(harness) -> None:
    first = harness.create()
    cases = [
        {},
        {"page_id": harness.page_id},
        {"page_id": harness.page_id, "region_ids": [first["region_id"]]},
        {"page_id": harness.page_id,
         "region_ids": [first["region_id"], first["region_id"]]},
        {"page_id": harness.page_id,
         "region_ids": [first["region_id"], "missing"]},
        {"page_id": harness.page_id,
         "region_ids": [first["region_id"], ""]},
        {"page_id": harness.page_id,
         "region_ids": [first["region_id"], 5]},
    ]
    for payload in cases:
        response = harness.rpc("merge_regions", payload)
        if payload.get("region_ids") and any(
            item == "missing" for item in payload["region_ids"]
        ):
            harness.assert_error(response, "TARGET_NOT_FOUND", "not_found")
        else:
            harness.assert_error(response, "INVALID_REQUEST", "validation")
    harness.assert_error(
        harness.rpc(
            "merge_regions",
            {"page_id": "unknown-page", "region_ids": [first["region_id"], "x"]},
        ),
        "TARGET_NOT_FOUND",
        "not_found",
    )


# ===========================================================================
# split_region
# ===========================================================================


def test_split_region_creates_parts_and_soft_deletes_source(harness) -> None:
    created = harness.create([[0.1, 0.1], [0.4, 0.4]])
    response = harness.rpc(
        "split_region",
        {"region_id": created["region_id"], "parts": PARTS},
    )
    assert response["error"] is None, response["error"]
    result = response["result"]
    assert result["source_region_id"] == created["region_id"]
    assert result["source_deleted"] is True
    assert len(result["regions"]) == 2
    assert [part["revision_no"] for part in result["regions"]] == [1, 1]
    assert [part["reading_order"] for part in result["regions"]] == [1, 2]
    assert harness.region_ids() == [part["region_id"] for part in result["regions"]]


def test_split_region_rejects_stale_expectation_and_invalid_parameters(
    harness,
) -> None:
    created = harness.create([[0.1, 0.1], [0.4, 0.4]])
    stale = harness.rpc(
        "split_region",
        {"region_id": created["region_id"], "parts": PARTS,
         "expected_revision": 42},
    )
    harness.assert_error(stale, "INPUT_REVISION_CHANGED", "conflict")
    assert harness.region_ids() == [created["region_id"]]

    for payload in (
        {},
        {"region_id": created["region_id"]},
        {"region_id": created["region_id"], "parts": [PARTS[0]]},
        {"region_id": created["region_id"], "parts": [[[0.1, 0.1]], PARTS[1]]},
        {"region_id": created["region_id"], "parts": PARTS,
         "expected_revision": -1},
    ):
        harness.assert_error(
            harness.rpc("split_region", payload), "INVALID_REQUEST", "validation"
        )
    harness.assert_error(
        harness.rpc("split_region", {"region_id": "missing", "parts": PARTS}),
        "TARGET_NOT_FOUND",
        "not_found",
    )


# ===========================================================================
# reorder_regions
# ===========================================================================


def test_reorder_regions_persists_manual_order_with_user_revisions(harness) -> None:
    first = harness.create(RECT)
    second = harness.create(RECT_2)
    response = harness.rpc(
        "reorder_regions",
        {"page_id": harness.page_id,
         "ordered_region_ids": [second["region_id"], first["region_id"]]},
    )
    assert response["error"] is None, response["error"]
    result = response["result"]
    assert [row["region_id"] for row in result["regions"]] == [
        second["region_id"], first["region_id"],
    ]
    assert [row["reading_order"] for row in result["regions"]] == [1, 2]
    # reading_order is revision-owned: both changed regions got a new revision.
    assert [row["revision_no"] for row in result["regions"]] == [2, 2]

    # Repeating the same order is effect-idempotent: no further revisions.
    again = harness.rpc(
        "reorder_regions",
        {"page_id": harness.page_id,
         "ordered_region_ids": [second["region_id"], first["region_id"]]},
    )
    assert again["error"] is None, again["error"]
    assert [row["revision_no"] for row in again["result"]["regions"]] == [2, 2]


def test_reorder_regions_rejects_partial_order_and_stale_expectations(
    harness,
) -> None:
    first = harness.create(RECT)
    second = harness.create(RECT_2)

    partial = harness.rpc(
        "reorder_regions",
        {"page_id": harness.page_id,
         "ordered_region_ids": [second["region_id"]]},
    )
    harness.assert_error(partial, "INVALID_REQUEST", "validation")

    stale = harness.rpc(
        "reorder_regions",
        {
            "page_id": harness.page_id,
            "ordered_region_ids": [second["region_id"], first["region_id"]],
            "expected_revisions": {
                second["region_id"]: 9,
                first["region_id"]: first["revision_no"],
            },
        },
    )
    harness.assert_error(stale, "INPUT_REVISION_CHANGED", "conflict")
    read = harness.rpc("list_regions", {"page_id": harness.page_id})
    # The frozen read DTO carries no reading_order field; the row ORDER is the
    # reading order and revision_no is the current pointer.
    assert [row["region_id"] for row in read["result"]["regions"]] == [
        first["region_id"], second["region_id"],
    ]
    assert [row["revision_no"] for row in read["result"]["regions"]] == [1, 1]

    harness.assert_error(
        harness.rpc("reorder_regions", {"page_id": harness.page_id,
                                        "ordered_region_ids": []}),
        "INVALID_REQUEST",
        "validation",
    )
    harness.assert_error(
        harness.rpc("reorder_regions", {"page_id": "unknown-page",
                                        "ordered_region_ids": [first["region_id"]]}),
        "TARGET_NOT_FOUND",
        "not_found",
    )


# ===========================================================================
# save_manual_translation
# ===========================================================================


def test_save_manual_translation_arms_protection(harness) -> None:
    created = harness.create()
    response = harness.rpc(
        "save_manual_translation",
        {"region_id": created["region_id"], "edited_translation": "人工译文"},
    )
    assert response["error"] is None, response["error"]
    result = response["result"]
    assert result["revision_no"] == created["revision_no"] + 1
    assert result["review_state"] == "needs_review"
    text = result["text"]
    assert text["edited_translation"] == "人工译文"
    assert text["manual_edited"] is True
    assert text["translation_locked"] is True
    assert text["edited_confirmed"] is False
    # A manual save without explicit confirmation never becomes final.
    assert text["final_source"] == "none"


def test_save_manual_translation_conflict_and_invalid_parameters(harness) -> None:
    created = harness.create()
    stale = harness.rpc(
        "save_manual_translation",
        {"region_id": created["region_id"], "edited_translation": "x",
         "expected_revision": 7},
    )
    harness.assert_error(stale, "INPUT_REVISION_CHANGED", "conflict")
    assert harness.current_revision_no(created["region_id"]) == 1

    for payload in (
        {},
        {"region_id": created["region_id"]},
        {"region_id": created["region_id"], "edited_translation": 5},
        {"region_id": created["region_id"], "edited_translation": "x",
         "expected_revision": True},
    ):
        harness.assert_error(
            harness.rpc("save_manual_translation", payload),
            "INVALID_REQUEST",
            "validation",
        )
    harness.assert_error(
        harness.rpc(
            "save_manual_translation",
            {"region_id": "missing", "edited_translation": "x"},
        ),
        "TARGET_NOT_FOUND",
        "not_found",
    )


# ===========================================================================
# confirm_region_final
# ===========================================================================


def test_confirm_region_final_promotes_confirmed_manual_text(harness) -> None:
    created = harness.create()
    harness.rpc(
        "save_manual_translation",
        {"region_id": created["region_id"], "edited_translation": "终稿"},
    )
    response = harness.rpc(
        "confirm_region_final", {"region_id": created["region_id"]}
    )
    assert response["error"] is None, response["error"]
    result = response["result"]
    assert result["review_state"] == "confirmed"
    assert result["text"]["edited_confirmed"] is True
    assert result["text"]["final_translation"] == "终稿"
    assert result["text"]["final_source"] == "edited"


def test_confirm_region_final_without_manual_text_only_locks_review_state(
    harness,
) -> None:
    created = harness.create()
    response = harness.rpc(
        "confirm_region_final", {"region_id": created["region_id"]}
    )
    assert response["error"] is None, response["error"]
    assert response["result"]["review_state"] == "confirmed"
    assert response["result"]["text"]["final_source"] == "none"


def test_confirm_region_final_conflict_and_invalid_parameters(harness) -> None:
    created = harness.create()
    stale = harness.rpc(
        "confirm_region_final",
        {"region_id": created["region_id"], "expected_revision": 3},
    )
    harness.assert_error(stale, "INPUT_REVISION_CHANGED", "conflict")
    harness.assert_error(
        harness.rpc("confirm_region_final", {}),
        "INVALID_REQUEST",
        "validation",
    )
    harness.assert_error(
        harness.rpc("confirm_region_final", {"region_id": "missing"}),
        "TARGET_NOT_FOUND",
        "not_found",
    )


# ===========================================================================
# set_region_lock
# ===========================================================================


def test_set_region_lock_creates_revision_and_persists_both_projections(
    harness,
) -> None:
    created = harness.create()
    response = harness.rpc(
        "set_region_lock",
        {"region_id": created["region_id"], "translation_locked": True,
         "region_locked": True},
    )
    assert response["error"] is None, response["error"]
    result = response["result"]
    assert result["revision_no"] == created["revision_no"] + 1
    assert result["review_state"] == "unreviewed"
    assert result["region_locked"] is True
    assert result["translation_locked"] is True
    assert result["inpaint_locked"] is False

    # The lock lives in the revision snapshot AND in both persisted lock
    # projections (text flag + region column the pipeline lock reads).
    history = harness.rpc(
        "list_region_revisions", {"region_id": created["region_id"]}
    )
    latest = history["result"]["revisions"][-1]
    assert latest["revision_no"] == result["revision_no"]
    stored = harness.core.editing.get_region(created["region_id"])
    assert stored.region_locked is True
    assert stored.translation_locked is True
    assert stored.text.translation_locked is True

    unlocked = harness.rpc(
        "set_region_lock",
        {"region_id": created["region_id"], "translation_locked": False},
    )
    assert unlocked["error"] is None, unlocked["error"]
    stored = harness.core.editing.get_region(created["region_id"])
    assert stored.translation_locked is False
    assert stored.text.translation_locked is False
    assert stored.region_locked is True  # untouched


def test_set_region_lock_rejects_invalid_parameters(harness) -> None:
    created = harness.create()
    for payload in (
        {},
        {"region_id": created["region_id"]},
        {"region_id": created["region_id"], "region_locked": "yes"},
        {"region_id": created["region_id"], "translation_locked": 1},
        {"region_id": created["region_id"], "inpaint_locked": None},
    ):
        harness.assert_error(
            harness.rpc("set_region_lock", payload), "INVALID_REQUEST", "validation"
        )
    harness.assert_error(
        harness.rpc("set_region_lock", {"region_id": "missing",
                                        "region_locked": True}),
        "TARGET_NOT_FOUND",
        "not_found",
    )


def test_set_region_lock_conflict_has_zero_write(harness) -> None:
    created = harness.create()
    stale = harness.rpc(
        "set_region_lock",
        {"region_id": created["region_id"], "inpaint_locked": True,
         "expected_revision": 11},
    )
    harness.assert_error(stale, "INPUT_REVISION_CHANGED", "conflict")
    assert harness.current_revision_no(created["region_id"]) == 1
    stored = harness.core.editing.get_region(created["region_id"])
    assert stored.inpaint_locked is False


# ===========================================================================
# pin_revision
# ===========================================================================


def test_pin_revision_flips_only_the_immutable_flag(harness) -> None:
    created = harness.create()
    history = harness.rpc(
        "list_region_revisions", {"region_id": created["region_id"]}
    )
    first = history["result"]["revisions"][0]
    response = harness.rpc(
        "pin_revision",
        {"region_id": created["region_id"], "revision_no": first["revision_no"],
         "pinned": True},
    )
    assert response["error"] is None, response["error"]
    assert response["result"]["is_pinned"] is True
    assert response["result"]["current_revision_no"] == created["revision_no"]

    history = harness.rpc(
        "list_region_revisions", {"region_id": created["region_id"]}
    )
    pinned = [rev for rev in history["result"]["revisions"] if rev["is_pinned"]]
    assert [rev["revision_no"] for rev in pinned] == [first["revision_no"]]
    # Pin never creates a revision.
    assert len(history["result"]["revisions"]) == 1
    assert history["result"]["current_revision_no"] == created["revision_no"]

    unpinned = harness.rpc(
        "pin_revision",
        {"region_id": created["region_id"], "revision_no": first["revision_no"],
         "pinned": False},
    )
    assert unpinned["error"] is None, unpinned["error"]
    assert unpinned["result"]["is_pinned"] is False


def test_pin_revision_rejects_invalid_parameters(harness) -> None:
    created = harness.create()
    for payload in (
        {},
        {"region_id": created["region_id"]},
        {"region_id": created["region_id"], "revision_no": 0, "pinned": True},
        {"region_id": created["region_id"], "revision_no": "1", "pinned": True},
        {"region_id": created["region_id"], "revision_no": 1},
        {"region_id": created["region_id"], "revision_no": 1, "pinned": "yes"},
        {"region_id": created["region_id"], "revision_no": 1, "pinned": True,
         "expected_revision": 0},
    ):
        harness.assert_error(
            harness.rpc("pin_revision", payload), "INVALID_REQUEST", "validation"
        )
    harness.assert_error(
        harness.rpc(
            "pin_revision",
            {"region_id": created["region_id"], "revision_no": 99,
             "pinned": True},
        ),
        "TARGET_NOT_FOUND",
        "not_found",
    )
    harness.assert_error(
        harness.rpc(
            "pin_revision",
            {"region_id": "missing", "revision_no": 1, "pinned": True},
        ),
        "TARGET_NOT_FOUND",
        "not_found",
    )
    stale = harness.rpc(
        "pin_revision",
        {"region_id": created["region_id"], "revision_no": 1, "pinned": True,
         "expected_revision": 4},
    )
    harness.assert_error(stale, "INPUT_REVISION_CHANGED", "conflict")


# ===========================================================================
# cross-cutting data safety
# ===========================================================================


def test_lock_and_geometry_survive_a_core_restart(tmp_path: Path) -> None:
    data_root = tmp_path / "restart-data"
    first_core = assemble_production_core(data_root)
    try:
        harness = Harness(first_core)
        created = harness.create()
        region_id = created["region_id"]
        harness.rpc(
            "save_region_geometry",
            {"region_id": region_id,
             "geometry": {"points": [[0.2, 0.2], [0.5, 0.5]]}},
        )
        harness.rpc(
            "set_region_lock",
            {"region_id": region_id, "region_locked": True,
             "translation_locked": True, "inpaint_locked": True},
        )
        harness.rpc(
            "pin_revision",
            {"region_id": region_id, "revision_no": 1, "pinned": True},
        )
        expected_current = harness.current_revision_no(region_id)
        # create(1) + geometry(2) + lock(3); pin creates none.
        assert expected_current == 3
    finally:
        first_core.conn.close()

    # Simulated restart: a fresh production assembly over the same data root.
    restarted = assemble_production_core(data_root)
    try:
        region = restarted.editing.get_region(region_id)
        assert region.region_locked is True
        assert region.translation_locked is True
        assert region.inpaint_locked is True
        assert region.text.translation_locked is True
        assert region.geometry.bbox.as_tuple() == (200, 300, 300, 450)
        revisions = restarted.editing.list_revision_summaries(region_id)
        assert revisions["current_revision_no"] == expected_current
        pinned = [rev for rev in revisions["revisions"] if rev["is_pinned"]]
        assert [rev["revision_no"] for rev in pinned] == [1]
    finally:
        restarted.conn.close()


def test_new_commands_are_additive_and_unknown_commands_still_fail() -> None:
    """Zero protocol bump: the ten commands are dispatched in the same
    envelope as the frozen Region family; an unknown command keeps the
    historical UNKNOWN_COMMAND rejection."""
    from bootstrap import core_service as module

    assert module.PROTOCOL_MINOR == 3
    assert module._REGION_WRITE_COMMANDS == {
        "create_region", "delete_region", "save_region_geometry",
        "merge_regions", "split_region", "reorder_regions",
        "save_manual_translation", "confirm_region_final",
        "set_region_lock", "pin_revision",
    }
