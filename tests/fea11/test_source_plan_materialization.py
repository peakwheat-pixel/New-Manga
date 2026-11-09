"""C-17 v1.2 (FEA-11-HOST-AUTH-3): read-only plan materialization projection."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from application.sources.errors import SourceSyncError  # noqa: E402
from application.sources.materialization import FORMAT, materialize  # noqa: E402

DIGEST = "a" * 64


class _FakeStore:
    """Read-tracking fake: the projection must ONLY ever call ``get_plan`` (M3)."""

    def __init__(self, rows: dict[str, dict]) -> None:
        self._rows = rows
        self.writes: list[str] = []

    def get_plan(self, plan_id: str):
        return self._rows.get(plan_id)

    # Every plausible write the projection must never perform.
    def mark_previewed(self, *_args, **_kwargs):
        self.writes.append("mark_previewed")

    def mark_confirmed(self, *_args, **_kwargs):
        self.writes.append("mark_confirmed")

    def mark_applied(self, *_args, **_kwargs):
        self.writes.append("mark_applied")

    def insert_receipt(self, *_args, **_kwargs):
        self.writes.append("insert_receipt")


def _row(*, state: str = "applied", digest: str = DIGEST, body: dict | None = None) -> dict:
    default_body = {
        "kind": "relink",
        "source_id": "src-0123456789abcdef",
        "reference_set_digest": "b" * 64,
        "target": {
            "status": "ok",
            "version_id": "ver-001",
            "content_digest": "c" * 64,
            "entries": [
                {"entry_id": "e-2", "locator": "2.png", "ordinal": 2, "content_digest_kind": "encoded", "content_digest": "d" * 64},
                {"entry_id": "e-1", "locator": "1.png", "ordinal": 1, "content_digest_kind": "encoded", "content_digest": "e" * 64},
            ],
        },
    }
    return {
        "plan_id": "plan-1",
        "source_id": "src-0123456789abcdef",
        "kind": "relink",
        "state": state,
        "plan_digest": digest,
        "body_json": json.dumps(body if body is not None else default_body),
        "expires_at": "2026-11-09T12:00:00+00:00",
    }


def _call(payload, rows=None):
    store = _FakeStore(rows if rows is not None else {"plan-1": _row()})
    return materialize(store, payload)


def test_projection_returns_the_persisted_subset_with_sorted_entries():
    result = _call({"plan_id": "plan-1", "plan_digest": DIGEST})

    assert result["format"] == FORMAT
    assert result["plan_id"] == "plan-1"
    assert result["kind"] == "relink"
    assert result["version_id"] == "ver-001"
    assert [entry["ordinal"] for entry in result["entries"]] == [1, 2]
    assert result["state"] == "applied"
    assert result["expires_at"]

    # M3 judgement: the projection performs ZERO writes on the store.
    store = _FakeStore({"plan-1": _row()})
    materialize(store, {"plan_id": "plan-1", "plan_digest": DIGEST})
    assert store.writes == []


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"plan_id": "plan-1"},
        {"plan_digest": DIGEST},
        {"plan_id": "plan-1", "plan_digest": DIGEST, "extra": 1},
        {"plan_id": 1, "plan_digest": DIGEST},
        {"plan_id": "plan-1", "plan_digest": "short"},
        {"plan_id": "plan-1", "plan_digest": "G" * 64},
    ],
)
def test_closed_shape_and_type_negatives(payload):
    with pytest.raises(SourceSyncError) as caught:
        _call(payload)
    assert caught.value.code == "INVALID_REQUEST"


def test_unknown_plan_is_not_found():
    with pytest.raises(SourceSyncError) as caught:
        _call({"plan_id": "missing", "plan_digest": DIGEST}, rows={})
    assert caught.value.code == "SOURCE_PLAN_NOT_FOUND"
    assert caught.value.category == "not_found"
    assert caught.value.retryable is False


def test_digest_mismatch_is_stale():
    with pytest.raises(SourceSyncError) as caught:
        _call({"plan_id": "plan-1", "plan_digest": "f" * 64})
    assert caught.value.code == "SOURCE_PLAN_STALE"
    assert caught.value.retryable is True


def test_unreadable_body_is_unavailable():
    broken = _row()
    broken["body_json"] = "{not-json"
    with pytest.raises(SourceSyncError) as caught:
        _call({"plan_id": "plan-1", "plan_digest": DIGEST}, rows={"plan-1": broken})
    assert caught.value.code == "SOURCE_PLAN_UNAVAILABLE"


def test_missing_target_has_null_version_and_no_entries():
    body = {
        "kind": "relink",
        "source_id": "src-0123456789abcdef",
        "reference_set_digest": "b" * 64,
        "target": {"status": "missing", "entries": [{"entry_id": "e-1", "ordinal": 1}]},
    }
    result = _call({"plan_id": "plan-1", "plan_digest": DIGEST}, rows={"plan-1": _row(body=body)})

    assert result["version_id"] is None
    assert result["content_digest"] is None
    assert result["entries"] == []


def test_duplicate_ordinals_are_unavailable():
    body = {
        "kind": "relink",
        "source_id": "src-0123456789abcdef",
        "reference_set_digest": "b" * 64,
        "target": {
            "status": "ok",
            "version_id": "ver-001",
            "content_digest": "c" * 64,
            "entries": [
                {"entry_id": "e-1", "locator": "1.png", "ordinal": 1},
                {"entry_id": "e-2", "locator": "2.png", "ordinal": 1},
            ],
        },
    }
    with pytest.raises(SourceSyncError) as caught:
        _call({"plan_id": "plan-1", "plan_digest": DIGEST}, rows={"plan-1": _row(body=body)})
    assert caught.value.code == "SOURCE_PLAN_UNAVAILABLE"


def test_entry_budget_is_enforced_without_truncation():
    entries = [
        {"entry_id": f"e-{index}", "locator": f"{index}.png", "ordinal": index}
        for index in range(10001)
    ]
    body = {
        "kind": "relink",
        "source_id": "src-0123456789abcdef",
        "reference_set_digest": "b" * 64,
        "target": {
            "status": "ok",
            "version_id": "ver-001",
            "content_digest": "c" * 64,
            "entries": entries,
        },
    }
    with pytest.raises(SourceSyncError) as caught:
        _call({"plan_id": "plan-1", "plan_digest": DIGEST}, rows={"plan-1": _row(body=body)})
    assert caught.value.code == "SOURCE_BUDGET_EXCEEDED"
