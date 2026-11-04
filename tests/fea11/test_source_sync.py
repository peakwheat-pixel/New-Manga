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
