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


@pytest.mark.parametrize("field", ["kind", "source_id", "reference_set_digest"])
def test_missing_required_body_field_is_unavailable(field):
    """R-r1-03: a contract-required body field missing -> SOURCE_PLAN_UNAVAILABLE.

    The projection must never emit a silent ``None`` for a required field.
    """
    body = {
        "kind": "relink",
        "source_id": "src-0123456789abcdef",
        "reference_set_digest": "b" * 64,
        "target": {
            "status": "ok",
            "version_id": "ver-001",
            "content_digest": "c" * 64,
            "entries": [],
        },
    }
    body.pop(field)
    with pytest.raises(SourceSyncError) as caught:
        _call({"plan_id": "plan-1", "plan_digest": DIGEST}, rows={"plan-1": _row(body=body)})
    assert caught.value.code == "SOURCE_PLAN_UNAVAILABLE"


def test_expired_applied_plan_is_still_projected():
    """R-r1-03: ACK/recovery is not gated by the plan TTL once applied (C-17 :270)."""
    row = _row(state="applied")
    row["expires_at"] = "2020-01-01T00:00:00+00:00"
    result = _call({"plan_id": "plan-1", "plan_digest": DIGEST}, rows={"plan-1": row})
    assert result["state"] == "applied"
    assert result["expires_at"] == "2020-01-01T00:00:00+00:00"


def test_projection_carries_no_absolute_path_or_secret():
    """R-r1-03: the response never leaks an absolute path / secret_ref / signing key."""
    result = _call({"plan_id": "plan-1", "plan_digest": DIGEST})
    text = json.dumps(result)
    assert "source-v" not in text or ":\\" not in text
    for forbidden in ("secret_ref", "signing_key", "signature"):
        assert forbidden not in text
    assert "\\" not in text


def _real_store(tmp_path):
    """A REAL SQLite store over the migrated schema (R-r1-09: no fake store)."""
    from infrastructure.sqlite.connection import open_database
    from infrastructure.sqlite.migrator import MigrationRunner
    from infrastructure.sqlite.schema import default_migrations
    from infrastructure.sqlite.source_sync import SourceSyncStore

    db_path = tmp_path / "library.db"
    conn, _opened = open_database(
        db_path,
        latest_known_schema_version=max(m.schema_version for m in default_migrations()),
    )
    MigrationRunner(conn, default_migrations()).apply_pending()
    with conn:
        conn.execute(
            "INSERT OR IGNORE INTO sources (source_id, source_kind, display_name,"
            " created_at, updated_at) VALUES (?, 'zip', 'seed', ?, ?)",
            ("src-0123456789abcdef", "2026-11-09T00:00:00+00:00", "2026-11-09T00:00:00+00:00"),
        )
    return conn, SourceSyncStore(conn)


def _table_fingerprints(conn) -> dict[str, str]:
    import hashlib

    tables = [
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )
    ]
    fingerprints: dict[str, str] = {}
    for table in tables:
        rows = [tuple(row) for row in conn.execute(f"SELECT * FROM {table}")]
        payload = json.dumps(rows, ensure_ascii=False, default=str)
        fingerprints[table] = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return fingerprints


def test_projection_writes_nothing_to_a_real_sqlite_store(tmp_path):
    """R-r1-09: every table fingerprint is identical before and after the projection."""
    import hashlib

    conn, store = _real_store(tmp_path)
    body = json.dumps(
        {
            "kind": "relink",
            "source_id": "src-0123456789abcdef",
            "reference_set_digest": "b" * 64,
            "target": {
                "status": "ok",
                "version_id": "ver-001",
                "content_digest": "c" * 64,
                "entries": [],
            },
        }
    )
    store.insert_plan(
        plan_id="plan-1",
        source_id="src-0123456789abcdef",
        kind="relink",
        plan_digest=DIGEST,
        body_json=body,
        created_at="2026-11-09T00:00:00+00:00",
        expires_at="2026-11-09T01:00:00+00:00",
    )
    before = _table_fingerprints(conn)

    result = materialize(store, {"plan_id": "plan-1", "plan_digest": DIGEST})

    assert result["plan_id"] == "plan-1"
    assert _table_fingerprints(conn) == before
    # The connection itself still sees the same row (no rollback/transaction leftover).
    assert store.get_plan("plan-1")["state"] in {"draft", "previewed", "confirmed", "applied", "stale"}


def test_body_budget_over_eight_mebibytes_is_typed(tmp_path):
    """R-r1-09: a >8MiB projection is SOURCE_BUDGET_EXCEEDED (never truncated)."""
    conn, store = _real_store(tmp_path)
    big_entries = [
        {"entry_id": f"e-{index}", "locator": "x" * 1100, "ordinal": index}
        for index in range(9000)
    ]
    body = json.dumps(
        {
            "kind": "relink",
            "source_id": "src-0123456789abcdef",
            "reference_set_digest": "b" * 64,
            "target": {
                "status": "ok",
                "version_id": "ver-001",
                "content_digest": "c" * 64,
                "entries": big_entries,
            },
        }
    )
    assert len(body.encode("utf-8")) > 8 * 1024 * 1024
    store.insert_plan(
        plan_id="plan-big",
        source_id="src-0123456789abcdef",
        kind="relink",
        plan_digest=DIGEST,
        body_json=body,
        created_at="2026-11-09T00:00:00+00:00",
        expires_at="2026-11-09T01:00:00+00:00",
    )

    with pytest.raises(SourceSyncError) as caught:
        materialize(store, {"plan_id": "plan-big", "plan_digest": DIGEST})
    assert caught.value.code == "SOURCE_BUDGET_EXCEEDED"
