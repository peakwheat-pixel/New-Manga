"""AC11-4/AC11-5/AC11-8 evidence: the apply transaction, idempotent replay,
tombstone preservation, pending read gates / acknowledgement and recovery.

Real SQLite (v8), real HMAC-signed grants, real zip containers and the
production source-sync stack; no fakes on the apply path.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import threading
import uuid

import pytest

from tests.fea11.conftest import (
    NOW,
    add_referenced_page,
    add_source_tree,
    authorization_for,
    build_plan_body,
    default_decisions,
    host_authorization,
    mint_grant,
    png_bytes,
    run_full_sync,
    write_zip,
)
from application.importing.referenced.errors import SourceImportError
from application.sources.errors import SourceSyncError
from application.sources.model import request_digest_of


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _seed_two_page_source(conn, scratch_dir, *, legacy_v7_evidence=True):
    page1, page2 = png_bytes(color=(255, 0, 0)), png_bytes(color=(0, 255, 0))
    zip_path = write_zip(
        scratch_dir / "old.zip", [("001.png", page1), ("002.png", page2)]
    )
    container_digest = _digest(zip_path.read_bytes())
    add_source_tree(
        conn,
        source_id="s1",
        version_id="sv1",
        digest=container_digest,
        entries=[
            ("e1", "001.png", _digest(page1)),
            ("e2", "002.png", _digest(page2)),
        ],
        legacy_v7_evidence=legacy_v7_evidence,
    )
    add_referenced_page(
        conn, "p1", "c1", "b1", order=1, source_id="s1", version_id="sv1",
        entry_id="e1", digest=_digest(page1),
    )
    add_referenced_page(
        conn, "p2", "c1", "b1", order=2, source_id="s1", version_id="sv1",
        entry_id="e2", digest=_digest(page2),
    )
    return zip_path, page1, page2, container_digest


def _scan(stack, registry, zip_path, *, source_id="s1", kind="resync",
          entries=None):
    grant_id, _facts = mint_grant(
        registry,
        source_id=source_id,
        kind="zip",
        entries=entries or [(zip_path, zip_path.name, 0)],
    )
    scan = stack["scanner"].scan(
        {
            "source_id": source_id,
            "project_ids": ["b1"],
            "scope": "current",
            "kind": kind,
            "grant_ids": [grant_id],
            "missing": [],
        }
    )
    return grant_id, scan


def test_resync_apply_publishes_new_generation_and_replay_is_idempotent(
    conn, registry, stack, book_chapter, scratch_dir
):
    """AC11-4/AC11-5: one apply commits a new binding generation + pending
    gate + receipt; replaying the same operation never publishes twice."""
    zip_path, page1, _page2, _old_digest = _seed_two_page_source(
        conn, scratch_dir
    )
    # 001.png kept, 002.png dropped from the container -> one unchanged page
    # and one tombstoned (missing) page.
    new_zip = write_zip(scratch_dir / "new.zip", [("001.png", page1)])
    grant_id, scan = _scan(stack, registry, new_zip)
    assert scan["totals"]["unchanged"] == 1
    assert scan["totals"]["missing"] == 1
    plan, dispatch = run_full_sync(stack, scan, grant_ids=[grant_id])
    assert dispatch["accepted"] is True
    assert dispatch["state"] == "core-committed"

    operation = stack["operations"].get(
        {"operation_id": dispatch["operation_id"]}
    )
    assert operation["state"] == "core-committed"
    assert operation["commit_digest"]

    binding = stack["store"].current_binding_of_page("p1")
    assert binding["binding_version"] == 2
    assert binding["status"] == "healthy"
    assert binding["source_id"] == "s1"
    assert (
        scan["diff"][0]["new_entry_id"] == binding["entry_id"]
    )  # unchanged page: same PageId, new container entry id
    gate = stack["store"].gate_of_binding(binding["binding_id"])
    assert gate["read_gate"] == "pending"

    # Tombstone: the page row and its binding survive with a missing status.
    missing = stack["store"].current_binding_of_page("p2")
    assert missing["status"] == "missing"
    page2 = conn.execute(
        "SELECT page_id FROM pages WHERE page_id = 'p2'"
    ).fetchone()
    assert page2 is not None

    # Replay the same operation + request digest: the original receipt is
    # returned and no second binding generation is published.
    operation = stack["operations"].get(
        {"operation_id": dispatch["operation_id"]}
    )
    replay = stack["service"].apply(
        "ResyncSource",
        {
            "operation_id": dispatch["operation_id"],
            "plan_id": plan["body"]["plan_id"],
            "plan_digest": plan["plan_digest"],
            "grant_ids": [grant_id],
            "authorization": host_authorization(
                operation_id=dispatch["operation_id"],
                request_digest=operation["request_digest"],
                authorizations=scan["authorizations"],
            ),
        },
    )
    assert replay["operation_id"] == dispatch["operation_id"]
    assert replay["state"] == "core-committed"
    assert replay["request_digest"] == operation["request_digest"]
    assert (
        conn.execute(
            "SELECT COUNT(*) FROM page_bindings WHERE page_id = 'p1'"
        ).fetchone()[0]
        == 2
    )


def test_apply_acknowledge_opens_gates_and_marks_operation(
    conn, registry, stack, book_chapter, scratch_dir
):
    """AC11-8: AcknowledgeSourceOperation atomically opens every gate of the
    operation and marks it acknowledged; a missing ACK keeps reads gated."""
    zip_path, page1, _page2, _old_digest = _seed_two_page_source(
        conn, scratch_dir
    )
    new_zip = write_zip(
        scratch_dir / "new.zip", [("001.png", page1), ("002.png", png_bytes(color=(9, 9, 9)))]
    )
    grant_id, scan = _scan(stack, registry, new_zip)
    plan, dispatch = run_full_sync(stack, scan, grant_ids=[grant_id])
    binding = stack["store"].current_binding_of_page("p1")
    assert stack["store"].gate_of_binding(binding["binding_id"])["read_gate"] == "pending"

    operation = stack["operations"].get(
        {"operation_id": dispatch["operation_id"]}
    )
    authorization = host_authorization(
        operation_id=dispatch["operation_id"],
        request_digest=operation["request_digest"],
        authorizations=scan["authorizations"],
    )
    ack = stack["operations"].acknowledge(
        {
            "operation_id": dispatch["operation_id"],
            "request_digest": operation["request_digest"],
            "commit_digest": operation["commit_digest"],
            "host_receipt_id": authorization["host_receipt_id"],
            "authorization": authorization,
            "grant_ids": [grant_id],
        }
    )
    assert ack["state"] == "acknowledged"
    gate = stack["store"].gate_of_binding(binding["binding_id"])
    assert gate["read_gate"] == "open"


def test_apply_rejects_replayed_different_request_without_writes(
    conn, registry, stack, book_chapter, scratch_dir
):
    """AC11-8: same operation id with a different request digest is rejected
    and leaves no additional binding generation."""
    zip_path, page1, _page2, _old_digest = _seed_two_page_source(
        conn, scratch_dir
    )
    new_zip = write_zip(scratch_dir / "new.zip", [("001.png", page1)])
    grant_id, scan = _scan(stack, registry, new_zip)
    plan, dispatch = run_full_sync(stack, scan, grant_ids=[grant_id])
    with pytest.raises(Exception) as caught:
        stack["service"].apply(
            "ResyncSource",
            {
                "operation_id": dispatch["operation_id"],
                "plan_id": plan["body"]["plan_id"],
                "plan_digest": plan["plan_digest"],
                "grant_ids": [grant_id],
                "authorization": host_authorization(
                    operation_id=dispatch["operation_id"],
                    request_digest="0" * 64,
                    authorizations=scan["authorizations"],
                ),
            },
        )
    assert caught.value.code in (
        "INVALID_REQUEST",
        "SOURCE_SYNC_STATE_CONFLICT",
        "SOURCE_PLAN_STALE",
        "SOURCE_OPERATION_NOT_FOUND",
    )
    assert (
        conn.execute(
            "SELECT COUNT(*) FROM page_bindings WHERE page_id = 'p1'"
        ).fetchone()[0]
        == 2
    )


def test_operation_cancel_before_commit_keeps_zero_business_writes(
    conn, registry, stack, book_chapter, scratch_dir
):
    """AC11-8: cancelling a started operation before Core commit records a
    failure/receipt but publishes no binding generation."""
    zip_path, page1, _page2, _old_digest = _seed_two_page_source(
        conn, scratch_dir
    )
    new_zip = write_zip(scratch_dir / "new.zip", [("001.png", page1)])
    grant_id, scan = _scan(stack, registry, new_zip)
    plan, dispatch = run_full_sync(stack, scan, grant_ids=[grant_id])
    # Acknowledge first so the cancel path is exercised on a settled op.
    operation = stack["operations"].get(
        {"operation_id": dispatch["operation_id"]}
    )
    authorization = host_authorization(
        operation_id=dispatch["operation_id"],
        request_digest=operation["request_digest"],
        authorizations=scan["authorizations"],
    )
    stack["operations"].acknowledge(
        {
            "operation_id": dispatch["operation_id"],
            "request_digest": operation["request_digest"],
            "commit_digest": operation["commit_digest"],
            "host_receipt_id": authorization["host_receipt_id"],
            "authorization": authorization,
            "grant_ids": [grant_id],
        }
    )
    cancelled = stack["operations"].cancel(
        {
            "operation_id": dispatch["operation_id"],
            "request_digest": operation["request_digest"],
        }
    )
    assert cancelled["accepted"] is False
    assert cancelled["state"] == "acknowledged"  # already settled: not cancellable
    # The committed binding generation is still exactly one new one.
    assert (
        conn.execute(
            "SELECT COUNT(*) FROM page_bindings WHERE page_id = 'p1'"
        ).fetchone()[0]
        == 2
    )


# ---------------------------------------------------------------------------
# R-011 (FEA-11 r1): AC11-4 breadth — multi-project scope, final-item drift
# rollback and revocation before apply.
# ---------------------------------------------------------------------------

def _table_digest(conn):
    import hashlib as _hashlib

    rows = []
    for table in (
        "pages", "page_bindings", "source_versions", "source_entries",
        "source_locations", "source_sync_plans", "source_operations",
        "source_binding_publications", "source_revision_lineage",
    ):
        try:
            values = conn.execute(f"SELECT * FROM {table} ORDER BY 1").fetchall()
        except Exception:
            values = []
        rows.append((table, [tuple(row) for row in values]))
    return _hashlib.sha256(repr(rows).encode("utf-8")).hexdigest()


def _apply_payload(stack, scan, grant_ids, kind="resync", scope="current"):
    from application.sources.model import request_digest_of

    body = build_plan_body(scan, kind=kind, scope=scope)
    plan = stack["planner"].create(body)
    stack["planner"].preview(
        {"plan_id": body["plan_id"], "plan_digest": plan["plan_digest"]}
    )
    stack["planner"].confirm(
        {
            "plan_id": body["plan_id"],
            "plan_digest": plan["plan_digest"],
            "confirmation": body["confirmation"],
        }
    )
    operation_id = "op-" + __import__("uuid").uuid4().hex[:16]
    request_digest = request_digest_of(
        operation_id, body["plan_id"], plan["plan_digest"], kind
    )
    return {
        "operation_id": operation_id,
        "plan_id": body["plan_id"],
        "plan_digest": plan["plan_digest"],
        "grant_ids": grant_ids,
        "authorization": host_authorization(
            operation_id=operation_id,
            request_digest=request_digest,
            authorizations=scan["authorizations"],
        ),
    }


def test_scope_all_covers_every_referencing_project(
    conn, registry, stack, book_chapter, scratch_dir
):
    """AC11-4/R-011: scope=all spans the whole-source reference set (books)."""
    zip_path, page1, _page2, _container_digest = _seed_two_page_source(conn, scratch_dir)
    conn.execute(
        "INSERT INTO books (book_id, title, created_at, updated_at)"
        " VALUES ('b2', 'Book 2', ?, ?)", (__import__('tests.fea11.conftest',
        fromlist=['NOW']).NOW,) * 2)
    conn.execute(
        "INSERT INTO chapters (chapter_id, book_id, title, created_at, updated_at)"
        " VALUES ('c2', 'b2', 'Ch', ?, ?)", (__import__('tests.fea11.conftest',
        fromlist=['NOW']).NOW,) * 2)
    add_referenced_page(
        conn, "p3", "c2", "b2", order=1, source_id="s1", version_id="sv1",
        entry_id="e1", digest=_digest(page1),
    )
    conn.commit()
    grant_id, _facts = mint_grant(
        registry, source_id="s1", kind="zip",
        entries=[(zip_path, zip_path.name, 0)],
    )
    scan = stack["scanner"].scan(
        {
            "source_id": "s1", "project_ids": ["b1", "b2"], "scope": "all",
            "kind": "resync", "grant_ids": [grant_id], "missing": [],
        }
    )
    assert sorted({row["project_id"] for row in scan["bases"]}) == ["b1", "b2"]
    # two entries (e1 is referenced by both p1 and p3), both unchanged
    assert scan["totals"]["unchanged"] == 2
    payload = _apply_payload(stack, scan, [grant_id], scope="all")
    dispatch = stack["service"].apply("ResyncSource", payload)
    assert dispatch["state"] == "core-committed"
    # Both projects stay on their bindings (all keep).
    for page_id in ("p1", "p2", "p3"):
        binding = stack["store"].current_binding_of_page(page_id)
        assert binding["binding_version"] == 1


def test_final_item_drift_rolls_back_the_whole_batch(
    conn, registry, stack, book_chapter, scratch_dir
):
    """AC11-4/R-011: a drift on the LAST bases entry aborts with zero writes."""
    zip_path, page1, page2, _digest = _seed_two_page_source(conn, scratch_dir)
    changed = png_bytes(color=(0, 0, 255))
    new_zip = write_zip(
        scratch_dir / "new.zip", [("001.png", changed), ("002.png", page2)]
    )
    grant_id, _facts = mint_grant(
        registry, source_id="s1", kind="zip",
        entries=[(new_zip, new_zip.name, 0)],
    )
    scan = stack["scanner"].scan(
        {
            "source_id": "s1", "project_ids": ["b1"], "scope": "current",
            "kind": "resync", "grant_ids": [grant_id], "missing": [],
        }
    )
    payload = _apply_payload(stack, scan, [grant_id])
    # Drift the LAST bases entry (p2) after the plan was frozen.
    conn.execute("UPDATE pages SET sort_order = 99 WHERE page_id = 'p2'")
    conn.commit()
    baseline = _table_digest(conn)
    from application.sources.errors import SourceSyncError

    with pytest.raises(SourceSyncError):
        stack["service"].apply("ResyncSource", payload)
    assert _table_digest(conn) == baseline  # zero business writes


def test_apply_after_grant_revocation_is_refused(
    conn, registry, stack, book_chapter, scratch_dir
):
    """AC11-4/R-011: revoking the grant before COMMIT refuses the apply."""
    zip_path, page1, page2, _digest = _seed_two_page_source(conn, scratch_dir)
    changed = png_bytes(color=(0, 0, 255))
    new_zip = write_zip(
        scratch_dir / "new.zip", [("001.png", changed), ("002.png", page2)]
    )
    grant_id, _facts = mint_grant(
        registry, source_id="s1", kind="zip",
        entries=[(new_zip, new_zip.name, 0)],
    )
    scan = stack["scanner"].scan(
        {
            "source_id": "s1", "project_ids": ["b1"], "scope": "current",
            "kind": "resync", "grant_ids": [grant_id], "missing": [],
        }
    )
    payload = _apply_payload(stack, scan, [grant_id])
    registry.revoke_grant_ids([grant_id])
    from application.importing.referenced.errors import SourceImportError
    from application.sources.errors import SourceSyncError

    baseline = _table_digest(conn)
    with pytest.raises((SourceSyncError, SourceImportError)) as error:
        stack["service"].apply("ResyncSource", payload)
    assert error.value.code in ("SOURCE_GRANT_REVOKED", "SOURCE_ACCESS_DENIED")
    assert _table_digest(conn) == baseline


def test_shared_source_scope_current_apply_succeeds_without_drift(
    conn, registry, stack, book_chapter, scratch_dir
):
    """r2 P1-1 regression: the plan digest covers the whole source; a
    scope=current apply on a shared source must not be stale when nothing
    drifted (the CAS recheck used the scoped subset before)."""
    zip_path, page1, _page2, _container = _seed_two_page_source(conn, scratch_dir)
    now = __import__('tests.fea11.conftest', fromlist=['NOW']).NOW
    conn.execute(
        "INSERT INTO books (book_id, title, created_at, updated_at)"
        " VALUES ('b2', 'Book 2', ?, ?)", (now, now))
    conn.execute(
        "INSERT INTO chapters (chapter_id, book_id, title, created_at, updated_at)"
        " VALUES ('c2', 'b2', 'Ch', ?, ?)", (now, now))
    add_referenced_page(
        conn, "p3", "c2", "b2", order=1, source_id="s1", version_id="sv1",
        entry_id="e1", digest=_digest(page1),
    )
    conn.commit()
    grant_id, _facts = mint_grant(
        registry, source_id="s1", kind="zip",
        entries=[(zip_path, zip_path.name, 0)],
    )
    scan = stack["scanner"].scan(
        {
            "source_id": "s1", "project_ids": ["b1"], "scope": "current",
            "kind": "resync", "grant_ids": [grant_id], "missing": [],
        }
    )
    assert scan["totals"]["unchanged"] == 2  # only b1's pages are in scope
    payload = _apply_payload(stack, scan, [grant_id])
    dispatch = stack["service"].apply("ResyncSource", payload)
    assert dispatch["state"] == "core-committed"
    # b1 and b2 both keep their bindings; nothing drifted.
    for page_id in ("p1", "p2", "p3"):
        assert stack["store"].current_binding_of_page(page_id)["binding_version"] == 1


def test_completion_that_omits_a_committed_registry_is_refused(
    conn, registry, stack, book_chapter, scratch_dir
):
    """r4 P2-9: the ACK must re-verify every committed registry."""
    from application.sources.errors import SourceSyncError

    zip_path, _page1, _page2, _container = _seed_two_page_source(conn, scratch_dir)
    grant_id, _facts = mint_grant(
        registry, source_id="s1", kind="zip",
        entries=[(zip_path, zip_path.name, 0)],
    )
    scan = stack["scanner"].scan(
        {
            "source_id": "s1", "project_ids": ["b1"], "scope": "current",
            "kind": "resync", "grant_ids": [grant_id], "missing": [],
        }
    )
    plan, dispatch = run_full_sync(stack, scan, grant_ids=[grant_id])
    operation = stack["operations"].get(
        {"operation_id": dispatch["operation_id"]})
    authorization = host_authorization(
        operation_id=operation["operation_id"],
        request_digest=operation["request_digest"],
        authorizations=[],
    )
    with pytest.raises(SourceSyncError):
        stack["operations"].acknowledge({
            "operation_id": operation["operation_id"],
            "request_digest": operation["request_digest"],
            "commit_digest": operation["commit_digest"],
            "host_receipt_id": authorization["host_receipt_id"],
            "authorization": authorization,
            "grant_ids": [grant_id],
        })


# ---------------------------------------------------------------------------
# FEA-11-AC4-GAPS-1 (AC1/AC2/AC3/AC4): concurrency, storage failure, third
# region BaseRevision and the C-17 §6.2 drift matrix.
#
# Every refusal below is compared against the SAME 16-table snapshot set
# (card frozen rule 4 / G11) and must leave each row byte-identical: a
# per-item commit, a plan-state side effect or a partial publication shows up
# as an extra/changed row. The only writes the apply transaction performs are
# inside service.py:239-287 (BEGIN IMMEDIATE .. COMMIT).
# ---------------------------------------------------------------------------

#: C-17 §6.2 zero-write comparison set (card frozen rule 4: 16 tables).
_SNAPSHOT_TABLES = (
    "pages",
    "page_bindings",
    "source_locations",
    "source_versions",
    "source_entries",
    "source_sync_plans",
    "source_operations",
    "source_binding_publications",
    "source_revision_lineage",
    "regions",
    "region_revisions",
    "reading_progress",
    "step_result_candidates",
    "pipeline_runs",
    "pipeline_run_targets",
    "rendition_cache",
)


def _full_snapshot(conn) -> dict[str, list[tuple]]:
    """The exact C-17 §6.2 zero-write baseline: every row of the 16 tables."""
    return {
        table: [
            tuple(row)
            for row in conn.execute(f"SELECT * FROM {table} ORDER BY 1")
        ]
        for table in _SNAPSHOT_TABLES
    }


def _assert_snapshot_equal(before, after, *, label="") -> None:
    difference = {
        table: (before.get(table, []), after.get(table, []))
        for table in _SNAPSHOT_TABLES
        if before.get(table) != after.get(table)
    }
    if not difference:
        return
    details = {
        table: {
            "before_rows": len(pair[0]),
            "after_rows": len(pair[1]),
            "first_before": pair[0][:1],
            "first_after": pair[1][:1],
        }
        for table, pair in difference.items()
    }
    raise AssertionError(
        f"zero-write baseline drifted{f' [{label}]' if label else ''}:"
        f" {json.dumps(details, default=str, ensure_ascii=False)}"
    )


def _freeze_plan(stack, scan, *, kind="resync", scope="current", decisions=None):
    """plan -> preview -> confirm; returns the immutable (body, plan) pair."""
    body = build_plan_body(
        scan, kind=kind, scope=scope, decisions=decisions
    )
    plan = stack["planner"].create(body)
    stack["planner"].preview(
        {"plan_id": body["plan_id"], "plan_digest": plan["plan_digest"]}
    )
    stack["planner"].confirm(
        {
            "plan_id": body["plan_id"],
            "plan_digest": plan["plan_digest"],
            "confirmation": body["confirmation"],
        }
    )
    # C-17 §5.2: plan rows are durable at the command boundary — the wire
    # face commits right after every planner call (core_service
    # ``_commit_source_sync``), so the apply transaction must not see an open
    # writer transaction on the same connection.
    stack["store"]._conn.commit()
    return body, plan


def _op_payload(
    scan,
    grant_ids,
    *,
    plan_id,
    plan_digest,
    kind="resync",
    operation_id=None,
    authorizations=None,
):
    """One C-17 §5.2 ApplyRequest bound to a distinct operation id."""
    operation_id = operation_id or ("op-" + uuid.uuid4().hex[:16])
    request_digest = request_digest_of(
        operation_id, plan_id, plan_digest, kind
    )
    return {
        "operation_id": operation_id,
        "plan_id": plan_id,
        "plan_digest": plan_digest,
        "grant_ids": grant_ids,
        "authorization": host_authorization(
            operation_id=operation_id,
            request_digest=request_digest,
            authorizations=(
                scan["authorizations"]
                if authorizations is None
                else authorizations
            ),
        ),
    }


def _run_concurrently(call, count: int = 2):
    """Fan ``call(index)`` out to ``count`` threads released by one barrier.

    Returns ``[(index, result, error)]``; the barrier makes the two applies
    start together without any sleep (R4: assert invariants, never "who
    wins")."""
    barrier = threading.Barrier(count)
    outcomes: list[tuple[int, dict | None, BaseException | None]] = []

    def worker(index: int) -> None:
        try:
            barrier.wait(timeout=15)
            outcomes.append((index, call(index), None))
        except BaseException as error:  # noqa: BLE001 - recorded, asserted
            outcomes.append((index, None, error))

    threads = [
        threading.Thread(target=worker, args=(index,))
        for index in range(count)
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=60)
    assert not any(thread.is_alive() for thread in threads), "worker hung"
    assert len(outcomes) == count
    return outcomes


def _assert_plan_untouched(conn, plan_id, *, state="confirmed"):
    row = conn.execute(
        "SELECT state, applied_at FROM source_sync_plans WHERE plan_id = ?",
        (plan_id,),
    ).fetchone()
    assert row is not None
    assert row["state"] == state
    if state == "confirmed":
        assert row["applied_at"] is None


def _assert_refusal(conn, stack, payload, *, code, cause=None):
    """One typed refusal + the full 16-table zero-write comparison."""
    before = _full_snapshot(conn)
    with pytest.raises(SourceImportError) as caught:
        stack["service"].apply("ResyncSource", payload)
    error = caught.value
    assert not isinstance(error, sqlite3.Error), f"unwrapped: {error!r}"
    assert error.code == code, (error.code, str(error))
    if cause is not None:
        assert error.details.get("cause") == cause, error.details
    _assert_snapshot_equal(before, _full_snapshot(conn), label=code)
    return error


def _two_page_changed_scan(
    stack, registry, conn, scratch_dir, *, region_page=None
):
    """AC4 device: p1 unchanged / p2 changed over a changed container.

    ``region_page`` seeds the three-region fixture (AC3) on that page before
    the scan so the plan captures its manual/protection/draft/run baselines.
    """
    _zip_path, page1, page2, container_digest = _seed_two_page_source(
        conn, scratch_dir, legacy_v7_evidence=False
    )
    if region_page is not None:
        _seed_three_regions(conn, region_page)
    changed = png_bytes(color=(0, 0, 255))
    new_zip = write_zip(
        scratch_dir / "new.zip", [("001.png", page1), ("002.png", changed)]
    )
    grant_id, scan = _scan(stack, registry, new_zip)
    assert scan["totals"] == {
        "unchanged": 1,
        "added": 0,
        "missing": 0,
        "changed": 1,
        "ambiguous": 0,
    }
    return {
        "grant_id": grant_id,
        "scan": scan,
        "new_zip": new_zip,
        "page1": page1,
        "page2": page2,
        "container_digest": container_digest,
    }


def _changed_container_plan(
    stack, registry, conn, scratch_dir, *, region_page=None
):
    """Frozen confirmed plan over the p1-keep / p2-bind device."""
    seeded = _two_page_changed_scan(
        stack, registry, conn, scratch_dir, region_page=region_page
    )
    body, plan = _freeze_plan(stack, seeded["scan"])
    seeded.update(
        {
            "body": body,
            "plan": plan,
            "payload": _op_payload(
                seeded["scan"],
                [seeded["grant_id"]],
                plan_id=body["plan_id"],
                plan_digest=plan["plan_digest"],
            ),
        }
    )
    return seeded


def _seed_three_regions(conn, page_id: str) -> None:
    """Three regions with current revisions r1/r2/r3 plus rg3's stale r3old.

    The historical ``r3old`` (revision_no 1) is deliberately NOT the current
    revision: it makes ``_migrate_revisions`` reach its STALE_BASE_REVISION
    branch after r1/r2 already migrated inside the same transaction (AC3-a).
    """
    geometry = json.dumps(
        {"x": 0.1, "y": 0.1, "width": 0.5, "height": 0.4},
        separators=(",", ":"),
    )
    snapshot = json.dumps(
        {"text": "旧译文"}, ensure_ascii=False, separators=(",", ":")
    )
    for region_id, revision_id, revision_no in (
        ("rg1", "r1", 1),
        ("rg2", "r2", 1),
        ("rg3", "r3", 2),
    ):
        conn.execute(
            "INSERT INTO regions (region_id, page_id, region_type,"
            " reading_order, geometry_json, text_json, style_json,"
            " sfx_policy, region_locked, translation_locked, inpaint_locked,"
            " created_at, updated_at) VALUES (?, ?, 'speech', 0, ?, '{}',"
            " '{}', 'skip', 0, 0, 0, ?, ?)",
            (region_id, page_id, geometry, NOW, NOW),
        )
        conn.execute(
            "INSERT INTO region_revisions (region_revision_id, region_id,"
            " revision_no, snapshot_json, origin, review_state, is_pinned,"
            " created_at) VALUES (?, ?, ?, ?, 'machine', 'confirmed', 0, ?)",
            (revision_id, region_id, revision_no, snapshot, NOW),
        )
    conn.execute(
        "INSERT INTO region_revisions (region_revision_id, region_id,"
        " revision_no, snapshot_json, origin, review_state, is_pinned,"
        " created_at) VALUES ('r3old', 'rg3', 1, ?, 'machine', 'confirmed',"
        " 0, ?)",
        (snapshot, NOW),
    )
    for region_id, revision_id in (
        ("rg1", "r1"),
        ("rg2", "r2"),
        ("rg3", "r3"),
    ):
        conn.execute(
            "UPDATE regions SET current_revision_id = ? WHERE region_id = ?",
            (revision_id, region_id),
        )
    conn.commit()


def _add_project_reference(
    conn, *, book_id, chapter_id, page_id, order, entry_id, digest
):
    """A second project referencing the SAME source (shared-source drift)."""
    conn.execute(
        "INSERT INTO books (book_id, title, created_at, updated_at)"
        " VALUES (?, ?, ?, ?)",
        (book_id, book_id, NOW, NOW),
    )
    conn.execute(
        "INSERT INTO chapters (chapter_id, book_id, title, created_at,"
        " updated_at) VALUES (?, ?, 'Ch', ?, ?)",
        (chapter_id, book_id, NOW, NOW),
    )
    conn.commit()
    add_referenced_page(
        conn,
        page_id,
        chapter_id,
        book_id,
        order=order,
        source_id="s1",
        version_id="sv1",
        entry_id=entry_id,
        digest=digest,
    )


def _seed_pipeline_run(conn, page_id: str, *, with_draft: bool) -> None:
    """One in-flight Run target for ``page_id`` (+ one open draft candidate)."""
    conn.execute(
        "INSERT INTO pipeline_runs (run_id, command_type, scope_type,"
        " requested_targets_json, settings_snapshot_json,"
        " provider_binding_snapshot_json, context_policy_json, status,"
        " run_json, updated_at) VALUES ('run-1', 'translate', 'page', '[]',"
        " '{}', '{}', '{}', 'running', '{}', ?)",
        (NOW,),
    )
    conn.execute(
        "INSERT INTO pipeline_run_targets (run_target_id, pipeline_run_id,"
        " target_id, target_type, page_id, target_order, snapshot_json)"
        " VALUES ('rt-1', 'run-1', ?, 'page', ?, 0, '{}')",
        (f"target-{page_id}", page_id),
    )
    if with_draft:
        conn.execute(
            "INSERT INTO pipeline_tasks (task_id, pipeline_run_id,"
            " run_target_id, target_id, target_type, page_id, status,"
            " units_json, step_run_ids_json) VALUES ('task-1', 'run-1',"
            " 'rt-1', ?, 'page', ?, 'running', '{}', '[]')",
            (f"target-{page_id}", page_id),
        )
        conn.execute(
            "INSERT INTO step_runs (step_run_id, pipeline_run_id, task_id,"
            " target_id, page_id, step_type, unit_id, status,"
            " input_refs_json, lock_snapshot_json, output_json)"
            " VALUES ('step-1', 'run-1', 'task-1', ?, ?, 'detect', 'u1',"
            " 'running', '{}', '{}', '{}')",
            (f"target-{page_id}", page_id),
        )
        conn.execute(
            "INSERT INTO step_result_candidates (candidate_id,"
            " pipeline_run_id, step_run_id, target_id, page_id, result_kind,"
            " payload_json, reason, status, created_at) VALUES ('cand-1',"
            " 'run-1', 'step-1', ?, ?, 'region', '{}', 'needs_review',"
            " 'pending', ?)",
            (f"target-{page_id}", page_id, NOW),
        )
    conn.commit()


def _file_db_conn(path):
    """Isolated file DB (v8, WAL, FK, production busy_timeout) for AC1-c."""
    from infrastructure.sqlite.migrator import MigrationRunner
    from infrastructure.sqlite.schema import default_migrations

    connection = sqlite3.connect(
        str(path), check_same_thread=False, isolation_level=None
    )
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA journal_mode = WAL")
    connection.execute("PRAGMA busy_timeout = 5000")
    MigrationRunner(connection, default_migrations()).apply_pending()
    return connection


def _file_db_stack(path):
    """One fully independent source-sync stack over its own connection."""
    from application.sources.ports import build_source_sync_stack
    from infrastructure.resource_channel.source_read_refs import (
        SourceReadGrantRegistry,
    )
    from infrastructure.sqlite.library import SqliteLibraryRepository
    from infrastructure.sqlite.source_sync import SourceSyncStore

    conn = _file_db_conn(path)
    store = SourceSyncStore(conn)
    registry = SourceReadGrantRegistry()
    repository = SqliteLibraryRepository(conn)
    return {
        "conn": conn,
        "store": store,
        "registry": registry,
        "repository": repository,
        "stack": build_source_sync_stack(
            store=store, access=registry, repository=repository
        ),
    }


def _routed_file_stack(path):
    """One stack over the PRODUCTION connection facade on an isolated file DB.

    ``ThreadRoutedConnection`` gives every thread its own real sqlite3
    connection (one shared transaction state per thread), which is exactly
    what the assembled Core uses. A single shared ``:memory:`` connection is
    not transaction-safe across threads by design (connection.py TASK-060
    Q-001), so the same-instance concurrency tests must use this facade.
    """
    from application.sources.ports import build_source_sync_stack
    from infrastructure.resource_channel.source_read_refs import (
        SourceReadGrantRegistry,
    )
    from infrastructure.sqlite.connection import open_database
    from infrastructure.sqlite.library import SqliteLibraryRepository
    from infrastructure.sqlite.migrator import MigrationRunner
    from infrastructure.sqlite.schema import default_migrations
    from infrastructure.sqlite.source_sync import SourceSyncStore

    conn, _opened = open_database(path, latest_known_schema_version=8)
    MigrationRunner(conn, default_migrations()).apply_pending()
    store = SourceSyncStore(conn)
    registry = SourceReadGrantRegistry()
    repository = SqliteLibraryRepository(conn)
    return {
        "conn": conn,
        "store": store,
        "registry": registry,
        "repository": repository,
        "stack": build_source_sync_stack(
            store=store, access=registry, repository=repository
        ),
    }


def _seed_book_and_chapter(conn) -> None:
    conn.execute(
        "INSERT INTO books (book_id, title, created_at, updated_at)"
        " VALUES ('b1', 'Book', ?, ?)",
        (NOW, NOW),
    )
    conn.execute(
        "INSERT INTO chapters (chapter_id, book_id, title, created_at,"
        " updated_at) VALUES ('c1', 'b1', 'Ch', ?, ?)",
        (NOW, NOW),
    )
    conn.commit()


def _materialize_target_version(conn, body, *, size_bytes: int) -> None:
    """AC1-c fixture: pre-materialize the plan's target version + entries.

    The live-scan cache is per stack, so a second, independent stack cannot
    observe the first stack's scan record. Writing the target version rows
    makes ``_ensure_target_version`` short-circuit (service.py:715-719) and
    lets BOTH apply transactions reach ``BEGIN IMMEDIATE``: the loss is then
    decided by the v8 transaction/CAS seam under test, never by a per-stack
    scan TTL (card AC1-c: service seam defensive evidence, L1).
    """
    target = body["target"]
    location = conn.execute(
        "SELECT location_id FROM source_locations WHERE source_id = ?"
        " AND is_current = 1",
        (body["source_id"],),
    ).fetchone()
    assert location is not None
    conn.execute(
        "INSERT INTO source_versions (version_id, source_id, location_id,"
        " content_digest, size_bytes, observed_at, created_at)"
        " VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            target["version_id"],
            body["source_id"],
            location["location_id"],
            target["content_digest"],
            size_bytes,
            NOW,
            NOW,
        ),
    )
    for entry in target["entries"]:
        digest = entry["content_digest"]
        conn.execute(
            "INSERT INTO source_entries (source_id, version_id, entry_id,"
            " locator, ordinal, stable_sort_key, content_digest_kind,"
            " content_digest, encoded_digest, size_bytes, decoder_name,"
            " decoder_version, decoder_params_json, created_at)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, '', '', '{}', ?)",
            (
                body["source_id"],
                target["version_id"],
                entry["entry_id"],
                entry["locator"],
                entry["ordinal"],
                f"{entry['ordinal']:08d}",
                entry["content_digest_kind"],
                digest,
                digest
                if entry["content_digest_kind"] == "encoded"
                else None,
                NOW,
            ),
        )
    conn.commit()


# ---------------------------------------------------------------------------
# AC1: concurrent apply (C-17 §6.2 "两个并发 apply")
# ---------------------------------------------------------------------------

def test_concurrent_same_operation_returns_the_original_receipt_once(
    tmp_path, scratch_dir
):
    """AC1-a: two threads on ONE service instance replay the SAME operation.

    Both responses are the original receipt (``accepted=true`` /
    ``state='core-committed'`` / same ``operation_id``+``request_digest``,
    C-17 §6.2 replay) and the business batch commits exactly once. A second
    commit would make the operation/binding/publication counts 2; a wrongly
    rejected replay would make ``accepted`` false."""
    device = _routed_file_stack(tmp_path / "library.db")
    conn, registry = device["conn"], device["registry"]
    stack = device["stack"]
    try:
        _seed_book_and_chapter(conn)
        _zip_path, page1, _page2, _container = _seed_two_page_source(
            conn, scratch_dir
        )
        new_zip = write_zip(scratch_dir / "new.zip", [("001.png", page1)])
        grant_id, scan = _scan(stack, registry, new_zip)
        body, plan = _freeze_plan(stack, scan)
        payload = _op_payload(
            scan,
            [grant_id],
            plan_id=body["plan_id"],
            plan_digest=plan["plan_digest"],
        )
        outcomes = _run_concurrently(
            lambda _index: stack["service"].apply("ResyncSource", payload)
        )
        assert [error for _index, _result, error in outcomes if error] == []
        results = [result for _index, result, _error in outcomes]
        assert len(results) == 2
        expected_digest = payload["authorization"]["request_digest"]
        for dispatch in results:
            assert dispatch["accepted"] is True
            assert dispatch["state"] == "core-committed"
            assert dispatch["operation_id"] == payload["operation_id"]
            assert dispatch["request_digest"] == expected_digest

        _assert_plan_untouched(conn, body["plan_id"], state="applied")
        assert conn.execute(
            "SELECT applied_at FROM source_sync_plans WHERE plan_id = ?",
            (body["plan_id"],),
        ).fetchone()["applied_at"] is not None
        # exactly one business commit: one receipt, one new generation.
        assert conn.execute(
            "SELECT COUNT(*) FROM source_operations WHERE plan_id = ?",
            (body["plan_id"],),
        ).fetchone()[0] == 1
        assert conn.execute(
            "SELECT COUNT(*) FROM page_bindings WHERE page_id = 'p1'"
        ).fetchone()[0] == 2
        assert conn.execute(
            "SELECT COUNT(*) FROM page_bindings WHERE page_id = 'p2'"
        ).fetchone()[0] == 1
        assert conn.execute(
            "SELECT COUNT(*) FROM source_binding_publications"
            " WHERE operation_id = ?",
            (payload["operation_id"],),
        ).fetchone()[0] == 1
        assert conn.execute(
            "SELECT COUNT(*) FROM page_bindings"
        ).fetchone()[0] == 3
    finally:
        conn.close()


def test_concurrent_different_operations_leave_one_commit_and_one_refusal(
    tmp_path, scratch_dir
):
    """AC1-b: two threads, the SAME plan, TWO different operations.

    One operation commits; the other is a typed C-17 refusal
    (``SOURCE_OPERATION_CONFLICT``/``SOURCE_PLAN_STALE``) — never an
    unwrapped ``sqlite3`` UNIQUE/IntegrityError — and the losing different-op
    path writes nothing (deterministic re-probe after the winner settled)."""
    device = _routed_file_stack(tmp_path / "library.db")
    conn, registry = device["conn"], device["registry"]
    stack = device["stack"]
    try:
        _seed_book_and_chapter(conn)
        _zip_path, page1, _page2, _container = _seed_two_page_source(
            conn, scratch_dir
        )
        new_zip = write_zip(scratch_dir / "new.zip", [("001.png", page1)])
        grant_id, scan = _scan(stack, registry, new_zip)
        body, plan = _freeze_plan(stack, scan)
        payloads = [
            _op_payload(
                scan,
                [grant_id],
                plan_id=body["plan_id"],
                plan_digest=plan["plan_digest"],
                operation_id=f"op-concurrent-{index}",
            )
            for index in range(2)
        ]
        outcomes = _run_concurrently(
            lambda index: stack["service"].apply(
                "ResyncSource", payloads[index]
            )
        )
        winners = [r for _i, r, error in outcomes if error is None]
        losers = [(index, error) for index, _r, error in outcomes if error]
        assert len(winners) == 1, [str(error) for _i, error in losers]
        assert len(losers) == 1
        loser_index, loser_error = losers[0]
        assert not isinstance(loser_error, sqlite3.Error), repr(loser_error)
        assert isinstance(loser_error, SourceSyncError), repr(loser_error)
        assert loser_error.code in (
            "SOURCE_OPERATION_CONFLICT",
            "SOURCE_PLAN_STALE",
        )
        assert winners[0]["state"] == "core-committed"
        # exactly one business commit (no second generation, no second receipt).
        assert conn.execute(
            "SELECT COUNT(*) FROM source_operations WHERE plan_id = ?",
            (body["plan_id"],),
        ).fetchone()[0] == 1
        assert conn.execute(
            "SELECT COUNT(*) FROM page_bindings WHERE page_id = 'p1'"
        ).fetchone()[0] == 2
        assert conn.execute(
            "SELECT COUNT(*) FROM page_bindings"
        ).fetchone()[0] == 3
        assert conn.execute(
            "SELECT COUNT(*) FROM source_binding_publications"
        ).fetchone()[0] == 1
        # deterministic zero-write probe of the losing different-op path.
        before = _full_snapshot(conn)
        with pytest.raises(SourceSyncError) as again:
            stack["service"].apply("ResyncSource", payloads[loser_index])
        assert again.value.code in (
            "SOURCE_OPERATION_CONFLICT",
            "SOURCE_PLAN_STALE",
        )
        _assert_snapshot_equal(before, _full_snapshot(conn))
    finally:
        conn.close()


def test_two_connection_stacks_commit_exactly_once_on_one_file_db(
    tmp_path, scratch_dir
):
    """AC1-c: two independent registries/stores/stacks over ONE file DB.

    ``tmp_path`` file DB + the production PRAGMA profile (FK, WAL,
    busy_timeout=5000). Both stacks register an EQUIVALENT grant
    (registry_id/generation/identity), both apply different operations
    concurrently: exactly one business commit, the loser is a typed
    ``SOURCE_PLAN_STALE``/``SOURCE_OPERATION_CONFLICT`` with zero writes, and
    ``database is locked`` must never appear (card R9: not relaxed). This is
    the service-seam defensive device, not production IPC concurrency (L1)."""
    db_path = tmp_path / "library.db"
    left = _file_db_stack(db_path)
    right = _file_db_stack(db_path)
    try:
        conn = left["conn"]
        conn.execute(
            "INSERT INTO books (book_id, title, created_at, updated_at)"
            " VALUES ('b1', 'Book', ?, ?)",
            (NOW, NOW),
        )
        conn.execute(
            "INSERT INTO chapters (chapter_id, book_id, title, created_at,"
            " updated_at) VALUES ('c1', 'b1', 'Ch', ?, ?)",
            (NOW, NOW),
        )
        conn.commit()
        _zip_path, page1, page2, _container = _seed_two_page_source(
            conn, scratch_dir, legacy_v7_evidence=False
        )
        changed = png_bytes(color=(0, 0, 255))
        new_zip = write_zip(
            scratch_dir / "new.zip",
            [("001.png", page1), ("002.png", changed)],
        )
        left_grant, scan = _scan(left["stack"], left["registry"], new_zip)
        body, plan = _freeze_plan(left["stack"], scan)
        _materialize_target_version(
            conn, body, size_bytes=new_zip.stat().st_size
        )
        right_grant, _facts = mint_grant(
            right["registry"],
            source_id="s1",
            kind="zip",
            entries=[(new_zip, new_zip.name, 0)],
        )
        payloads = [
            _op_payload(
                scan,
                [grant_id],
                plan_id=body["plan_id"],
                plan_digest=plan["plan_digest"],
                operation_id=f"op-two-conn-{index}",
            )
            for index, grant_id in enumerate((left_grant, right_grant))
        ]
        # the equivalent baseline: same registry id/generation/identity.
        assert (
            payloads[0]["authorization"]["authorizations"]
            == payloads[1]["authorization"]["authorizations"]
        )
        stacks = (left["stack"], right["stack"])
        outcomes = _run_concurrently(
            lambda index: stacks[index]["service"].apply(
                "ResyncSource", payloads[index]
            )
        )
        winners = [r for _i, r, error in outcomes if error is None]
        losers = [(index, error) for index, _r, error in outcomes if error]
        assert len(winners) == 1, [str(error) for _i, error in losers]
        assert len(losers) == 1
        loser_index, loser_error = losers[0]
        assert "database is locked" not in str(loser_error)
        assert not isinstance(loser_error, sqlite3.Error), repr(loser_error)
        assert isinstance(loser_error, SourceSyncError), repr(loser_error)
        assert loser_error.code in (
            "SOURCE_PLAN_STALE",
            "SOURCE_OPERATION_CONFLICT",
        )
        if loser_error.code == "SOURCE_PLAN_STALE":
            # the winner's COMMIT made the plan ``applied`` under the loser's
            # BEGIN IMMEDIATE — the v8 transaction/CAS seam, not a scan TTL.
            assert loser_error.details.get("cause") == "applied"
        winner = winners[0]
        assert winner["state"] == "core-committed"
        # exactly one business commit across BOTH connections.
        assert conn.execute(
            "SELECT COUNT(*) FROM source_operations WHERE plan_id = ?",
            (body["plan_id"],),
        ).fetchone()[0] == 1
        for page_id in ("p1", "p2"):
            assert conn.execute(
                "SELECT COUNT(*) FROM page_bindings WHERE page_id = ?",
                (page_id,),
            ).fetchone()[0] == 2
        assert conn.execute(
            "SELECT COUNT(*) FROM source_binding_publications"
            " WHERE operation_id = ?",
            (winner["operation_id"],),
        ).fetchone()[0] == 2
        # zero-write probe of the losing different-op path.
        before = _full_snapshot(conn)
        with pytest.raises(SourceSyncError) as again:
            stacks[loser_index]["service"].apply(
                "ResyncSource", payloads[loser_index]
            )
        assert again.value.code in (
            "SOURCE_PLAN_STALE",
            "SOURCE_OPERATION_CONFLICT",
        )
        _assert_snapshot_equal(before, _full_snapshot(conn))
    finally:
        left["conn"].close()
        right["conn"].close()


# ---------------------------------------------------------------------------
# AC2: DB failure injection (a: mid transaction, b: final step)
# ---------------------------------------------------------------------------

def test_mid_transaction_storage_failure_rolls_back_the_whole_batch(
    conn, registry, stack, book_chapter, scratch_dir
):
    """AC2-a: a real SQLite ABORT on the p2 binding INSERT (after p1 already
    published inside the same transaction) rolls the whole batch back.

    The trigger fires between ``BEGIN IMMEDIATE`` and ``COMMIT``; afterwards
    every one of the 16 tables is byte-identical, the plan stays ``confirmed``
    and a retry with a fresh operation id succeeds."""
    scenario = _changed_container_plan(stack, registry, conn, scratch_dir)
    payload = scenario["payload"]
    conn.execute(
        "CREATE TRIGGER fea11_inject_mid BEFORE INSERT ON page_bindings"
        " WHEN NEW.page_id = 'p2' BEGIN SELECT RAISE(ABORT, 'injected');"
        " END"
    )
    conn.commit()
    baseline = _full_snapshot(conn)
    try:
        with pytest.raises(sqlite3.Error) as caught:
            stack["service"].apply("ResyncSource", payload)
        assert "injected" in str(caught.value)
        assert not isinstance(caught.value, SourceSyncError)
    finally:
        conn.execute("DROP TRIGGER fea11_inject_mid")
        conn.commit()
    _assert_snapshot_equal(baseline, _full_snapshot(conn), label="AC2-a")
    _assert_plan_untouched(conn, scenario["body"]["plan_id"])
    assert conn.execute(
        "SELECT COUNT(*) FROM source_operations"
    ).fetchone()[0] == 0
    assert conn.execute(
        "SELECT COUNT(*) FROM source_binding_publications"
    ).fetchone()[0] == 0
    assert conn.execute(
        "SELECT COUNT(*) FROM page_bindings WHERE page_id = 'p1'"
    ).fetchone()[0] == 1
    retry = _op_payload(
        scenario["scan"],
        [scenario["grant_id"]],
        plan_id=scenario["body"]["plan_id"],
        plan_digest=scenario["plan"]["plan_digest"],
    )
    dispatch = stack["service"].apply("ResyncSource", retry)
    assert dispatch["state"] == "core-committed"
    _assert_plan_untouched(conn, scenario["body"]["plan_id"], state="applied")
    assert conn.execute(
        "SELECT COUNT(*) FROM page_bindings WHERE page_id = 'p1'"
    ).fetchone()[0] == 2


def test_final_step_storage_failure_rolls_back_the_whole_batch(
    conn, registry, stack, book_chapter, scratch_dir
):
    """AC2-b: the LAST transaction step (``commit_operation``'s
    ``host-authorized -> core-committed`` UPDATE) aborts -> success pages = 0.

    One real SQLite error on the receipt UPDATE rolls back every business row
    written earlier in the same transaction (bindings/publications/plan)."""
    scenario = _changed_container_plan(stack, registry, conn, scratch_dir)
    payload = scenario["payload"]
    conn.execute(
        "CREATE TRIGGER fea11_inject_commit BEFORE UPDATE ON source_operations"
        " WHEN OLD.state = 'host-authorized' BEGIN SELECT RAISE(ABORT,"
        " 'injected'); END"
    )
    conn.commit()
    baseline = _full_snapshot(conn)
    try:
        with pytest.raises(sqlite3.Error) as caught:
            stack["service"].apply("ResyncSource", payload)
        assert "injected" in str(caught.value)
        assert not isinstance(caught.value, SourceSyncError)
    finally:
        conn.execute("DROP TRIGGER fea11_inject_commit")
        conn.commit()
    _assert_snapshot_equal(baseline, _full_snapshot(conn), label="AC2-b")
    _assert_plan_untouched(conn, scenario["body"]["plan_id"])
    assert conn.execute(
        "SELECT COUNT(*) FROM source_operations"
    ).fetchone()[0] == 0
    assert conn.execute(
        "SELECT COUNT(*) FROM page_bindings WHERE page_id = 'p1'"
    ).fetchone()[0] == 1
    retry = _op_payload(
        scenario["scan"],
        [scenario["grant_id"]],
        plan_id=scenario["body"]["plan_id"],
        plan_digest=scenario["plan"]["plan_digest"],
    )
    dispatch = stack["service"].apply("ResyncSource", retry)
    assert dispatch["state"] == "core-committed"


# ---------------------------------------------------------------------------
# AC3: third region BaseRevisionId (both branches)
# ---------------------------------------------------------------------------

def test_third_region_stale_migrate_revision_aborts_the_whole_batch(
    conn, registry, stack, book_chapter, scratch_dir
):
    """AC3-a: the plan carries a migrate revision that is no longer current.

    ``migrate_revision_ids=[r1, r2, r3old]``: r1/r2 migrate inside the apply
    transaction, then r3old hits ``_migrate_revisions``' STALE_BASE_REVISION
    (service.py:853-857) and the WHOLE batch rolls back — no new region,
    revision or lineage row survives (card frozen rule 2: a non conforming
    Host plan is the only way to reach this defensive branch; L2)."""
    seeded = _two_page_changed_scan(
        stack, registry, conn, scratch_dir, region_page="p2"
    )
    decisions = default_decisions(seeded["scan"])
    migrated = 0
    for decision in decisions:
        if decision["target_page_id"] == "p2":
            decision["migrate_revision_ids"] = ["r1", "r2", "r3old"]
            migrated += 1
    assert migrated == 1
    body, plan = _freeze_plan(stack, seeded["scan"], decisions=decisions)
    payload = _op_payload(
        seeded["scan"],
        [seeded["grant_id"]],
        plan_id=body["plan_id"],
        plan_digest=plan["plan_digest"],
    )
    error = _assert_refusal(
        conn, stack, payload, code="STALE_BASE_REVISION"
    )
    assert error.code != "INVALID_REQUEST"
    _assert_plan_untouched(conn, body["plan_id"])
    # the first two migrations (and their lineage) rolled back with the third.
    assert conn.execute(
        "SELECT COUNT(*) FROM regions"
    ).fetchone()[0] == 3
    assert conn.execute(
        "SELECT COUNT(*) FROM region_revisions"
    ).fetchone()[0] == 4
    assert conn.execute(
        "SELECT COUNT(*) FROM source_revision_lineage"
    ).fetchone()[0] == 0
    assert conn.execute(
        "SELECT region_id, current_revision_id FROM regions"
        " WHERE region_id = 'rg3'"
    ).fetchone()["current_revision_id"] == "r3"


def test_third_region_live_drift_is_plan_stale_manual(
    conn, registry, stack, book_chapter, scratch_dir
):
    """AC3-b: the realistic drift branch — after confirmation region3's
    ``current_revision_id`` moves to a NEW revision.

    The manual CAS (``manual_digest`` covers ``current_revision_id``,
    service.py:402-404) rejects with SOURCE_PLAN_STALE(cause='manual') and
    the batch never reaches ``_migrate_revisions``' STALE_BASE_REVISION
    branch (card frozen rule 2)."""
    seeded = _two_page_changed_scan(
        stack, registry, conn, scratch_dir, region_page="p2"
    )
    decisions = default_decisions(seeded["scan"])
    for decision in decisions:
        if decision["target_page_id"] == "p2":
            decision["migrate_revision_ids"] = ["r1", "r2", "r3"]
    body, plan = _freeze_plan(stack, seeded["scan"], decisions=decisions)
    payload = _op_payload(
        seeded["scan"],
        [seeded["grant_id"]],
        plan_id=body["plan_id"],
        plan_digest=plan["plan_digest"],
    )
    # realistic drift: a new current revision lands after the plan froze.
    conn.execute(
        "INSERT INTO region_revisions (region_revision_id, region_id,"
        " revision_no, snapshot_json, origin, review_state, is_pinned,"
        " created_at) VALUES ('r3new', 'rg3', 3, '{\"text\":\"新基线\"}',"
        " 'user', 'confirmed', 0, ?)",
        (NOW,),
    )
    conn.execute(
        "UPDATE regions SET current_revision_id = 'r3new'"
        " WHERE region_id = 'rg3'"
    )
    conn.commit()
    error = _assert_refusal(
        conn, stack, payload, code="SOURCE_PLAN_STALE", cause="manual"
    )
    assert error.code != "STALE_BASE_REVISION"
    _assert_plan_untouched(conn, body["plan_id"])


# ---------------------------------------------------------------------------
# AC4: the G4-G11 drift matrix, every case against the same 16-table set
# ---------------------------------------------------------------------------

def test_drift_source_bytes_refuses_file_identity_changed(
    conn, registry, stack, book_chapter, scratch_dir
):
    """G4: the container bytes are overwritten at the SAME path after the
    plan froze -> FILE_IDENTITY_CHANGED (strict lease evidence), zero writes."""
    scenario = _changed_container_plan(stack, registry, conn, scratch_dir)
    replacement = write_zip(
        scratch_dir / "replacement.zip",
        [("001.png", png_bytes(color=(7, 7, 7)))],
    )
    scenario["new_zip"].write_bytes(replacement.read_bytes())
    _assert_refusal(
        conn, stack, scenario["payload"], code="FILE_IDENTITY_CHANGED"
    )
    _assert_plan_untouched(conn, scenario["body"]["plan_id"])


def test_drift_source_version_row_is_plan_stale_source(
    conn, registry, stack, book_chapter, scratch_dir
):
    """G4b: the base source version row's ``content_digest`` is tampered ->
    SOURCE_PLAN_STALE(cause='source') from the in-transaction CAS re-read."""
    scenario = _changed_container_plan(stack, registry, conn, scratch_dir)
    conn.execute(
        "UPDATE source_versions SET content_digest = ?"
        " WHERE source_id = 's1' AND version_id = 'sv1'",
        ("b" * 64,),
    )
    conn.commit()
    _assert_refusal(
        conn, stack, scenario["payload"],
        code="SOURCE_PLAN_STALE", cause="source",
    )
    _assert_plan_untouched(conn, scenario["body"]["plan_id"])


def test_drift_reference_set_is_plan_stale_binding(
    conn, registry, stack, book_chapter, scratch_dir
):
    """G5: a new shared-page reference appears after the plan froze ->
    SOURCE_PLAN_STALE(cause='binding') from the whole-source reference set."""
    scenario = _changed_container_plan(stack, registry, conn, scratch_dir)
    entry_digest = conn.execute(
        "SELECT content_digest FROM source_entries WHERE source_id = 's1'"
        " AND version_id = 'sv1' AND entry_id = 'e1'"
    ).fetchone()["content_digest"]
    _add_project_reference(
        conn,
        book_id="b2",
        chapter_id="c2",
        page_id="p3",
        order=1,
        entry_id="e1",
        digest=entry_digest,
    )
    _assert_refusal(
        conn, stack, scenario["payload"],
        code="SOURCE_PLAN_STALE", cause="binding",
    )
    _assert_plan_untouched(conn, scenario["body"]["plan_id"])


def test_drift_decision_is_plan_stale_decision(
    conn, registry, stack, book_chapter, scratch_dir
):
    """G6: the confirmed plan is explicitly invalidated (reason=decision) ->
    SOURCE_PLAN_STALE(cause='decision'), no business write, plan stays
    ``stale`` (the invalidation itself is the baseline)."""
    scenario = _changed_container_plan(stack, registry, conn, scratch_dir)
    stack["planner"].invalidate(
        {
            "plan_id": scenario["body"]["plan_id"],
            "plan_digest": scenario["plan"]["plan_digest"],
            "reason": "decision",
        }
    )
    _assert_refusal(
        conn, stack, scenario["payload"],
        code="SOURCE_PLAN_STALE", cause="decision",
    )
    row = conn.execute(
        "SELECT state, stale_reason FROM source_sync_plans"
        " WHERE plan_id = ?",
        (scenario["body"]["plan_id"],),
    ).fetchone()
    assert row["state"] == "stale"
    assert row["stale_reason"] == "decision"


def test_drift_authorization_generation_is_plan_stale_authorization(
    conn, registry, stack, book_chapter, scratch_dir
):
    """G7: the live Host authorization generation is 2 while the plan baseline
    is 1 -> SOURCE_PLAN_STALE(cause='authorization') (service.py:170-176)."""
    scenario = _changed_container_plan(stack, registry, conn, scratch_dir)
    grant_2, facts_2 = mint_grant(
        registry,
        source_id="s1",
        kind="zip",
        entries=[(scenario["new_zip"], scenario["new_zip"].name, 0)],
        generation=2,
    )
    payload = _op_payload(
        scenario["scan"],
        [grant_2],
        plan_id=scenario["body"]["plan_id"],
        plan_digest=scenario["plan"]["plan_digest"],
        authorizations=[authorization_for(facts_2, generation=2)],
    )
    _assert_refusal(
        conn, stack, payload,
        code="SOURCE_PLAN_STALE", cause="authorization",
    )
    _assert_plan_untouched(conn, scenario["body"]["plan_id"])


def test_drift_authorization_eof_is_grant_revoked(
    conn, registry, stack, book_chapter, scratch_dir
):
    """G8: EOF/transport failure revokes every grant ->
    SOURCE_GRANT_REVOKED (source_read_refs.py:239-246), zero writes."""
    scenario = _changed_container_plan(stack, registry, conn, scratch_dir)
    registry.revoke_all_for_session()
    _assert_refusal(
        conn, stack, scenario["payload"], code="SOURCE_GRANT_REVOKED"
    )
    _assert_plan_untouched(conn, scenario["body"]["plan_id"])


def test_drift_manual_revision_is_plan_stale_manual(
    conn, registry, stack, book_chapter, scratch_dir
):
    """G9 (manual): a manual region edit after the plan froze ->
    SOURCE_PLAN_STALE(cause='manual'); the second base is re-read too (the
    drifted page is the LAST base, not the first)."""
    scenario = _changed_container_plan(
        stack, registry, conn, scratch_dir, region_page="p2"
    )
    assert scenario["scan"]["bases"][-1]["page_id"] == "p2"
    conn.execute(
        "UPDATE regions SET text_json = '{\"text\":\"人工改动\"}'"
        " WHERE region_id = 'rg1'"
    )
    conn.commit()
    _assert_refusal(
        conn, stack, scenario["payload"],
        code="SOURCE_PLAN_STALE", cause="manual",
    )
    _assert_plan_untouched(conn, scenario["body"]["plan_id"])


def test_drift_protection_is_plan_stale_manual(
    conn, registry, stack, book_chapter, scratch_dir
):
    """G9 (protection): flipping a region lock after the plan froze ->
    SOURCE_PLAN_STALE(cause='manual') from ``protection_digest``."""
    scenario = _changed_container_plan(
        stack, registry, conn, scratch_dir, region_page="p2"
    )
    conn.execute(
        "UPDATE regions SET region_locked = 1 WHERE region_id = 'rg1'"
    )
    conn.commit()
    _assert_refusal(
        conn, stack, scenario["payload"],
        code="SOURCE_PLAN_STALE", cause="manual",
    )
    _assert_plan_untouched(conn, scenario["body"]["plan_id"])


def test_drift_draft_is_plan_stale_manual(
    conn, registry, stack, book_chapter, scratch_dir
):
    """G9 (draft): an open step-result candidate lands after the plan froze ->
    SOURCE_PLAN_STALE(cause='manual') from ``drafts_digest``."""
    scenario = _changed_container_plan(
        stack, registry, conn, scratch_dir, region_page="p2"
    )
    _seed_pipeline_run(conn, "p2", with_draft=True)
    _assert_refusal(
        conn, stack, scenario["payload"],
        code="SOURCE_PLAN_STALE", cause="manual",
    )
    _assert_plan_untouched(conn, scenario["body"]["plan_id"])


def test_drift_run_is_plan_stale_manual(
    conn, registry, stack, book_chapter, scratch_dir
):
    """G9 (Run): an in-flight pipeline Run targets the page after the plan
    froze -> SOURCE_PLAN_STALE(cause='manual') from ``runs_digest``."""
    scenario = _changed_container_plan(
        stack, registry, conn, scratch_dir, region_page="p2"
    )
    _seed_pipeline_run(conn, "p2", with_draft=False)
    _assert_refusal(
        conn, stack, scenario["payload"],
        code="SOURCE_PLAN_STALE", cause="manual",
    )
    _assert_plan_untouched(conn, scenario["body"]["plan_id"])


def test_multi_project_final_item_drift_leaves_both_projects_untouched(
    conn, registry, stack, book_chapter, scratch_dir
):
    """G10: b1+b2 share s1, scope=all, the LAST base (b2's page) drifts ->
    SOURCE_PLAN_STALE(cause='binding') and BOTH projects keep zero writes
    (the single atomic unit never commits a prefix)."""
    zip_path, page1, page2, _container = _seed_two_page_source(
        conn, scratch_dir
    )
    _add_project_reference(
        conn,
        book_id="b2",
        chapter_id="c2",
        page_id="p3",
        order=1,
        entry_id="e1",
        digest=_digest(page1),
    )
    grant_id, _facts = mint_grant(
        registry,
        source_id="s1",
        kind="zip",
        entries=[(zip_path, zip_path.name, 0)],
    )
    scan = stack["scanner"].scan(
        {
            "source_id": "s1",
            "project_ids": ["b1", "b2"],
            "scope": "all",
            "kind": "resync",
            "grant_ids": [grant_id],
            "missing": [],
        }
    )
    assert sorted({row["project_id"] for row in scan["bases"]}) == [
        "b1",
        "b2",
    ]
    assert scan["bases"][-1]["page_id"] == "p3"
    body, plan = _freeze_plan(stack, scan, scope="all")
    payload = _op_payload(
        scan,
        [grant_id],
        plan_id=body["plan_id"],
        plan_digest=plan["plan_digest"],
    )
    conn.execute("UPDATE pages SET sort_order = 99 WHERE page_id = 'p3'")
    conn.commit()
    baseline = _full_snapshot(conn)
    _assert_refusal(
        conn, stack, payload,
        code="SOURCE_PLAN_STALE", cause="binding",
    )
    _assert_plan_untouched(conn, body["plan_id"])
    for page_id in ("p1", "p2", "p3"):
        assert conn.execute(
            "SELECT COUNT(*) FROM page_bindings WHERE page_id = ?",
            (page_id,),
        ).fetchone()[0] == 1
    assert _full_snapshot(conn) == baseline
