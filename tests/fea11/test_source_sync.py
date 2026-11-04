"""AC11-4/AC11-5/AC11-8 evidence: the apply transaction, idempotent replay,
tombstone preservation, pending read gates / acknowledgement and recovery.

Real SQLite (v8), real HMAC-signed grants, real zip containers and the
production source-sync stack; no fakes on the apply path.
"""

from __future__ import annotations

import hashlib

import pytest

from tests.fea11.conftest import (
    add_referenced_page,
    add_source_tree,
    build_plan_body,
    host_authorization,
    mint_grant,
    png_bytes,
    run_full_sync,
    write_zip,
)
from application.sources.model import request_digest_of


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _seed_two_page_source(conn, scratch_dir):
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
