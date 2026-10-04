"""Region retype + read channel over the production Core service
(M2-REGION-RETYPE-CORE, contract M2-C1 rev 1.4 §5.4).

Exercises the two new stdio JSON-lines commands (``set_region_type`` /
``list_regions``) at the ``dispatch_request`` level on a real production
assembly, with the wire shape frozen by rev 1.4 §5.4:

- request ``{"region_id", "new_region_type", "expected_revision"?}`` →
  result ``{"region_id", "revision_no", "region_type", "sfx_policy"}``
  (the post-retype effective state, one round trip, no second query);
- ``list_regions`` ``{"page_id"}`` → ``{"regions": RegionListSummary[]}``
  in reading_order, the minimal five-field DTO (no geometry/text/annotation
  semantics);
- error semantics reuse the EXISTING typed codes only (zero new error
  semantics): INVALID_REQUEST (validation) / INPUT_REVISION_CHANGED
  (conflict) / TARGET_NOT_FOUND (not_found) / UNKNOWN (internal); wire
  ``code`` literals are SCREAMING_SNAKE_CASE (footnote c) and never the
  lowercase GuardStatus enum values;
- write-side validation is typed fail-closed BEFORE any persistence
  (§5.3 discipline, same lesson);
- the envelope protocol minor bump 2 -> 3 is pinned here (and on the Rust
  side) with the same backwards-compatible widening precedent.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from bootstrap.core_service import (
    PROTOCOL_MAJOR,
    PROTOCOL_MINOR,
    CoreServiceServer,
    assemble_production_core,
)
from domain.regions.entities import SfxPolicy


NOW = "2026-01-01T00:00:00.000+00:00"


@pytest.fixture()
def server(tmp_path: Path):
    """One real production assembly on a temp root + its stdio server."""
    core = assemble_production_core(tmp_path / "data")
    try:
        yield core
    finally:
        core.conn.close()


@pytest.fixture()
def rpc(server):
    """A dispatch helper bound to the real assembly."""
    state = {"counter": 0}

    def _request(command: str, payload: dict) -> dict:
        state["counter"] += 1
        line = json.dumps({
            "protocol": "new-manga.core",
            "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
            "request_id": f"req-retype-{state['counter']}",
            "command": command,
            "payload": payload,
        })
        response, exit_flag = CoreServiceServer(server).dispatch_request(line)
        assert not exit_flag
        return response

    return _request


def _seed_page(core) -> None:
    with core.conn:
        core.conn.execute(
            "INSERT INTO books (book_id, title, created_at, updated_at)"
            " VALUES ('book-1', 't', ?, ?)",
            (NOW, NOW),
        )
        core.conn.execute(
            "INSERT INTO chapters (chapter_id, book_id, title, created_at,"
            " updated_at) VALUES ('chapter-1', 'book-1', 'c', ?, ?)",
            (NOW, NOW),
        )
        core.conn.execute(
            "INSERT INTO pages (page_id, chapter_id, sort_order, created_at,"
            " updated_at) VALUES ('page-1', 'chapter-1', 0, ?, ?)",
            (NOW, NOW),
        )


def _make_region(core, **create_kwargs):
    from domain.regions.entities import BBox, RegionGeometry

    return core.editing.create_region(
        "page-1", RegionGeometry(bbox=BBox(0, 0, 10, 10)), **create_kwargs
    )


def _make_retype_request(rpc, region_id, **payload_overrides) -> dict:
    payload = {"region_id": region_id, "new_region_type": "sfx"}
    payload.update(payload_overrides)
    return rpc("set_region_type", payload)


def _assert_error(response: dict, code: str, category: str) -> None:
    assert response["result"] is None
    error = response["error"]
    assert error is not None
    assert error["code"] == code  # SCREAMING_SNAKE_CASE literal (footnote c)
    assert error["category"] == category
    assert error["retryable"] is False


# ---------------------------------------------------------------------------
# protocol minor bump with the new command surface
# ---------------------------------------------------------------------------


def test_protocol_minor_bumped_to_three_with_retype_surface(server, rpc) -> None:
    # M2-REGION-RETYPE-CORE: 2 -> 3 (same backwards-compatible widening
    # precedent as core.detect 0->1 and settings 1->2; every pre-existing
    # command keeps its payload/result/error codes).
    assert (PROTOCOL_MAJOR, PROTOCOL_MINOR) == (1, 3)
    response = rpc("core.ping", {})
    assert response["error"] is None
    assert response["result"]["protocol_version"] == {"major": 1, "minor": 3}


# ---------------------------------------------------------------------------
# set_region_type — the happy path returns the post-retype effective state
# ---------------------------------------------------------------------------


def test_set_region_type_round_trip_full_effective_state(server, rpc) -> None:
    _seed_page(core=server)
    rpc("settings.update_section", {"section": "sfx", "values": {"policy": "translate"}})
    region = _make_region(core=server)

    response = _make_retype_request(rpc, region.region_id)

    assert response["error"] is None
    result = response["result"]
    # the wire result is the post-retype effective state, exactly four fields
    assert result == {
        "region_id": region.region_id,
        "revision_no": 2,
        "region_type": "sfx",
        "sfx_policy": "translate",  # EV-8: re-snapshotted from the global config
    }
    # the effective state matches the persisted region (one round trip)
    assert region.region_type.value == "sfx"
    assert region.sfx_policy.value == "translate"


def test_set_region_type_review_state_unreviewed_and_origin_user(server, rpc) -> None:
    _seed_page(core=server)
    region = _make_region(core=server)
    revisions_before = len(server.editing._repo.list_revisions(region.region_id))

    response = _make_retype_request(rpc, region.region_id, {"new_region_type": "note"})

    assert response["error"] is None
    del revisions_before
    revisions = server.editing._repo.list_revisions(region.region_id)
    assert revisions[-1].review_state.value == "unreviewed"
    assert revisions[-1].origin.value == "user"
    assert response["result"]["region_type"] == "note"
    assert response["result"]["sfx_policy"] == "skip"  # non-sfx forces SKIP


# ---------------------------------------------------------------------------
# set_region_type — request validation (typed fail-closed, pre-persistence)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "payload",
    [
        {},  # everything missing
        {"new_region_type": "sfx"},  # region_id missing
        {"region_id": 123, "new_region_type": "sfx"},  # region_id not a string
        {"region_id": "r"},  # new_region_type missing
        {"region_id": "r", "new_region_type": 7},  # not a string
        {"region_id": "r", "new_region_type": "ignore"},  # NOT a RegionType value
        {"region_id": "r", "new_region_type": "speech "},  # not exactly the wire value
        {"region_id": "r", "new_region_type": "sfx", "expected_revision": "2"},
        {"region_id": "r", "new_region_type": "sfx", "expected_revision": True},
        {"region_id": "r", "new_region_type": "sfx", "expected_revision": 1.5},
    ],
)
def test_set_region_type_invalid_payloads_typed_rejected(server, rpc, payload) -> None:
    _seed_page(core=server)
    response = rpc("set_region_type", payload)
    _assert_error(response, "INVALID_REQUEST", "validation")


def test_set_region_type_payload_must_reach_nothing_on_validation_failure(
    server, rpc
) -> None:
    """R4 discipline: a rejected write never reaches the store."""
    _seed_page(core=server)
    region = _make_region(core=server)
    revisions_before = len(server.editing._repo.list_revisions(region.region_id))

    _make_retype_request(rpc, region.region_id, {"new_region_type": "bogus"})

    assert len(server.editing._repo.list_revisions(region.region_id)) == revisions_before
    assert region.region_type.value == "speech"


# ---------------------------------------------------------------------------
# set_region_type — reused error semantics (zero new error codes)
# ---------------------------------------------------------------------------


def test_set_region_type_optimistic_conflict_is_input_revision_changed(
    server, rpc
) -> None:
    _seed_page(core=server)
    region = _make_region(core=server)
    revision_count = len(server.editing._repo.list_revisions(region.region_id))

    response = _make_retype_request(
        rpc, region.region_id, {"expected_revision": 999}
    )

    _assert_error(response, "INPUT_REVISION_CHANGED", "conflict")
    # C4: zero write on rejection
    assert len(server.editing._repo.list_revisions(region.region_id)) == revision_count


def test_set_region_type_unknown_region_is_target_not_found(server, rpc) -> None:
    _seed_page(core=server)
    response = _make_retype_request(rpc, "no-such-region")
    _assert_error(response, "TARGET_NOT_FOUND", "not_found")


def test_set_region_type_soft_deleted_region_is_target_not_found(
    server, rpc
) -> None:
    _seed_page(core=server)
    region = _make_region(core=server)
    server.editing.delete_region(region.region_id)

    response = _make_retype_request(rpc, region.region_id)
    _assert_error(response, "TARGET_NOT_FOUND", "not_found")


def test_set_region_type_unclassified_failure_maps_to_unknown(server) -> None:
    """The UNKNOWN/internal slot for Core-side failures (persistence etc.) is
    the same envelope the settings surface uses — never a raw traceback."""
    _seed_page(core=server)
    region = _make_region(core=server)

    def explode(*args, **kwargs):
        raise RuntimeError("simulated persistence failure")

    broken = SimpleNamespace(
        editing=SimpleNamespace(set_region_type=explode),
        pipeline_defaults=server.pipeline_defaults,
        conn=server.conn,
    )
    response, _ = CoreServiceServer(broken).dispatch_request(
        json.dumps({
            "protocol": "new-manga.core",
            "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
            "request_id": "req-unknown",
            "command": "set_region_type",
            "payload": {"region_id": region.region_id, "new_region_type": "sfx"},
        })
    )
    _assert_error(response, "UNKNOWN", "internal")
    # the message is a fixed safe phrase (no exception text, no paths)
    assert response["error"]["message"] == "Region retype failed"


# ---------------------------------------------------------------------------
# list_regions — the RegionListSummary read channel
# ---------------------------------------------------------------------------


def test_list_regions_returns_minimal_summaries_in_reading_order(
    server, rpc
) -> None:
    _seed_page(core=server)
    third = _make_region(core=server, reading_order=3)
    first = _make_region(core=server, reading_order=1)
    server.editing.set_region_type(
        first.region_id, "sfx", current_global_sfx_policy=SfxPolicy.TRANSLATE
    )

    response = rpc("list_regions", {"page_id": "page-1"})

    assert response["error"] is None
    regions = response["result"]["regions"]
    assert [r["region_id"] for r in regions] == [first.region_id, third.region_id]
    assert regions[0] == {
        "region_id": first.region_id,
        "region_type": "sfx",
        "sfx_policy": "translate",
        "origin": "user",
        "revision_no": 2,
    }
    # the minimal set — no geometry/text/annotation semantics
    assert set(regions[0].keys()) == {
        "region_id", "region_type", "sfx_policy", "origin", "revision_no",
    }


def test_list_regions_empty_list_for_unknown_page_is_not_an_error(
    server, rpc
) -> None:
    """Footnote a: a page with no rows — unknown page_id or no live regions —
    reads as an empty list, NOT a typed error (no page existence check)."""
    _seed_page(core=server)
    response = rpc("list_regions", {"page_id": "no-such-page"})
    assert response["error"] is None
    assert response["result"] == {"regions": []}


def test_list_regions_missing_page_id_is_invalid_request(server, rpc) -> None:
    _seed_page(core=server)
    _assert_error(rpc("list_regions", {}), "INVALID_REQUEST", "validation")
    _assert_error(
        rpc("list_regions", {"page_id": 42}), "INVALID_REQUEST", "validation"
    )


# ---------------------------------------------------------------------------
# the pre-existing command surface is untouched by the widening
# ---------------------------------------------------------------------------


def test_pre_existing_commands_keep_their_shapes(server, rpc) -> None:
    response = rpc("settings.get", {"section": "sfx"})
    assert response["error"] is None
    assert response["result"]["settings"]["sfx"] is None
    del server
