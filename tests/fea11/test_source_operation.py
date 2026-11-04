"""AC11-8 evidence: durable operation state survives restarts, recovery opens
the pending gates, and receipts cannot be forged.

The store is the durable truth: a fresh stack over the same connection sees
the same operation/commit_digest; only an ACK/recovery with the exact durable
commit digest may open the read gates.
"""

from __future__ import annotations

import hashlib

import pytest

from tests.fea11.conftest import (
    add_referenced_page,
    add_source_tree,
    host_authorization,
    mint_grant,
    png_bytes,
    run_full_sync,
    write_zip,
)


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _seed(conn, scratch_dir):
    page1, page2 = png_bytes(color=(255, 0, 0)), png_bytes(color=(0, 255, 0))
    zip_path = write_zip(
        scratch_dir / "old.zip", [("001.png", page1), ("002.png", page2)]
    )
    digest = _digest(zip_path.read_bytes())
    add_source_tree(
        conn, source_id="s1", version_id="sv1", digest=digest,
        entries=[("e1", "001.png", _digest(page1)),
                 ("e2", "002.png", _digest(page2))],
    )
    add_referenced_page(
        conn, "p1", "c1", "b1", order=1, source_id="s1", version_id="sv1",
        entry_id="e1", digest=_digest(page1),
    )
    add_referenced_page(
        conn, "p2", "c1", "b1", order=2, source_id="s1", version_id="sv1",
        entry_id="e2", digest=_digest(page2),
    )
    return zip_path, page1


def _apply_one_sync(stack, registry, conn, scratch_dir):
    zip_path, page1 = _seed(conn, scratch_dir)
    new_zip = write_zip(scratch_dir / "new.zip", [("001.png", page1)])
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
    plan, dispatch = run_full_sync(stack, scan, grant_ids=[grant_id])
    operation = stack["operations"].get(
        {"operation_id": dispatch["operation_id"]}
    )
    return grant_id, scan, plan, dispatch, operation


def _completion(stack, registry, grant_id, scan, operation, digest=None):
    authorization = host_authorization(
        operation_id=operation["operation_id"],
        request_digest=operation["request_digest"],
        authorizations=scan["authorizations"],
    )
    return {
        "operation_id": operation["operation_id"],
        "request_digest": operation["request_digest"],
        "commit_digest": digest or operation["commit_digest"],
        "host_receipt_id": authorization["host_receipt_id"],
        "authorization": authorization,
        "grant_ids": [grant_id],
    }


def test_operation_survives_a_fresh_stack_over_the_same_store(
    conn, registry, stack, book_chapter, scratch_dir
):
    """AC11-8: the operation/commit receipt is durable, not in-memory."""
    grant_id, scan, plan, dispatch, operation = _apply_one_sync(
        stack, registry, conn, scratch_dir
    )
    assert operation["state"] == "core-committed"
    commit_digest = operation["commit_digest"]
    assert commit_digest

    from application.sources.ports import build_source_sync_stack
    from infrastructure.sqlite.library import SqliteLibraryRepository

    fresh = build_source_sync_stack(
        store=stack["store"],
        access=registry,
        repository=SqliteLibraryRepository(conn),
    )
    again = fresh["operations"].get({"operation_id": dispatch["operation_id"]})
    assert again["state"] == "core-committed"
    assert again["commit_digest"] == commit_digest


def test_recovery_opens_gates_and_is_idempotent(
    conn, registry, stack, book_chapter, scratch_dir
):
    """AC11-8: recovery (without a Host ACK) opens the gates atomically; a
    second recovery returns the same receipt without publishing again."""
    grant_id, scan, plan, dispatch, operation = _apply_one_sync(
        stack, registry, conn, scratch_dir
    )
    binding = stack["store"].current_binding_of_page("p1")
    assert (
        stack["store"].gate_of_binding(binding["binding_id"])["read_gate"]
        == "pending"
    )
    payload = _completion(stack, registry, grant_id, scan, operation)
    recovered = stack["operations"].recover(payload)
    assert recovered["state"] == "recovered"
    assert (
        stack["store"].gate_of_binding(binding["binding_id"])["read_gate"]
        == "open"
    )
    replay = stack["operations"].recover(payload)
    assert replay["state"] == "recovered"
    assert (
        conn.execute(
            "SELECT COUNT(*) FROM page_bindings WHERE page_id = 'p1'"
        ).fetchone()[0]
        == 2
    )


def test_acknowledge_rejects_forged_commit_digest(
    conn, registry, stack, book_chapter, scratch_dir
):
    """AC11-8: only the exact durable commit digest may open the gates."""
    grant_id, scan, plan, dispatch, operation = _apply_one_sync(
        stack, registry, conn, scratch_dir
    )
    binding = stack["store"].current_binding_of_page("p1")
    payload = _completion(
        stack, registry, grant_id, scan, operation, digest="0" * 64
    )
    with pytest.raises(Exception) as caught:
        stack["operations"].acknowledge(payload)
    assert caught.value.code == "INVALID_REQUEST"
    assert (
        stack["store"].gate_of_binding(binding["binding_id"])["read_gate"]
        == "pending"
    )
    assert (
        conn.execute(
            "SELECT COUNT(*) FROM source_binding_publications"
            " WHERE read_gate = 'open'"
        ).fetchone()[0]
        == 0
    )


def test_unknown_operation_is_a_typed_error(
    conn, registry, stack, book_chapter, scratch_dir
):
    """AC11-8: querying/acknowledging an unknown operation fails typed."""
    with pytest.raises(Exception) as caught:
        stack["operations"].get({"operation_id": "op-does-not-exist"})
    assert caught.value.code in (
        "SOURCE_OPERATION_NOT_FOUND", "SOURCE_SYNC_STATE_CONFLICT",
    )
