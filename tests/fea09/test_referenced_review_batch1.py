"""FEA-09 implementation-review r1 batch-1 regressions.

R1-I007 (decode budget before allocation), R1-I009 (plan bound to project /
duplicate policy).
"""

from __future__ import annotations

import pytest

import time

from application.importing.referenced.errors import SourceImportError
from application.importing.referenced.model import SourceReadBudget
from support import FakeSourceReadAccess, HookDecoder, build_runtime, png_bytes

OP = "op-0000000000000030"


def _wait_terminal(runtime, operation_id, timeout=10.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
        receipt = runtime.receipt(operation_id)
        if receipt["state"] in {"completed", "cancelled", "failed"}:
            return receipt
        time.sleep(0.01)
    return runtime.receipt(operation_id)


def _image_grant(access, tmp_path, name, grant_id, *, budget=None):
    path = tmp_path / name
    path.write_bytes(png_bytes(8, 8))
    access.add_file(grant_id, "image", path, budget=budget)


def test_probe_decode_budget_refuses_before_decoder(tmp_path, repo, book_chapter):
    """R1-I007: a tiny decode budget fails before the decoder is called."""
    access = FakeSourceReadAccess()
    budget = SourceReadBudget(
        max_bytes=1024 * 1024, max_decode_bytes=4, max_entries=10
    )
    _image_grant(access, tmp_path, "big.png", "g-image-0000000001", budget=budget)
    decoder = HookDecoder()
    runtime = build_runtime(repo, access, decoder=decoder)
    plan = runtime._planner.plan(
        chapter_id="c1", grants=["g-image-0000000001"], duplicate_policy="skip"
    )
    runtime.start(
        chapter_id="c1", plan_id=plan["plan_id"], plan_digest=plan["plan_digest"],
        grants=["g-image-0000000001"], duplicate_policy="skip", operation_id=OP,
    )
    receipt = _wait_terminal(runtime, OP)
    # A per-entry budget refusal is an unsupported entry (C-16 §4 ④), and it
    # must be decided before the decoder allocates the pixel buffer.
    assert receipt["state"] == "completed"
    assert receipt["items"][0]["outcome"] == "unsupported"
    assert receipt["items"][0]["counts"]["unsupported_entries"] == 1
    assert decoder.calls == []
    assert repo.list_pages("c1") == []


def test_plan_is_bound_to_project_and_duplicate_policy(tmp_path, repo, book_chapter):
    """R1-I009: a plan taken with another policy is stale, not accepted."""
    access = FakeSourceReadAccess()
    _image_grant(access, tmp_path, "p.png", "g-image-0000000001")
    runtime = build_runtime(repo, access)
    plan = runtime._planner.plan(
        chapter_id="c1", grants=["g-image-0000000001"], duplicate_policy="skip"
    )
    try:
        runtime.start(
            chapter_id="c1", plan_id=plan["plan_id"],
            plan_digest=plan["plan_digest"], grants=["g-image-0000000001"],
            duplicate_policy="import_as_new", operation_id=OP,
        )
    except SourceImportError as error:
        assert error.code == "SOURCE_PLAN_STALE"
    else:  # pragma: no cover - the planner must bind the policy
        raise AssertionError("start accepted a plan from another policy")


def test_stale_plan_when_chapter_moves_to_another_book(tmp_path, repo, book_chapter):
    """R1-I009 P2-b: a plan is bound to the chapter's book, not just the policy."""
    access = FakeSourceReadAccess()
    _image_grant(access, tmp_path, "p.png", "g-image-0000000001")
    runtime = build_runtime(repo, access)
    plan = runtime._planner.plan(
        chapter_id="c1", grants=["g-image-0000000001"], duplicate_policy="skip"
    )
    repo._conn.execute(
        "INSERT INTO books (book_id, title, created_at, updated_at)"
        " VALUES ('book-2', 'other', '2026-11-01T00:00:00.000+00:00',"
        " '2026-11-01T00:00:00.000+00:00')"
    )
    repo._conn.execute(
        "UPDATE chapters SET book_id = 'book-2' WHERE chapter_id = 'c1'"
    )
    repo._conn.commit()
    with pytest.raises(SourceImportError) as caught:
        runtime.start(
            chapter_id="c1", plan_id=plan["plan_id"],
            plan_digest=plan["plan_digest"],
            grants=["g-image-0000000001"], duplicate_policy="skip",
            operation_id=OP,
        )
    assert caught.value.code == "SOURCE_PLAN_STALE"