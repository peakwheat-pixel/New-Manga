"""FEA-09 AC-3: the same physical source shared by two projects.

C-16 §4: two projects may reference the same source; pages/bindings stay
project-scoped while the source identity is shared (no duplicate source row
for one physical file).
"""

from __future__ import annotations

import time

from support import FakeSourceReadAccess, build_runtime, png_bytes

NOW = "2026-11-03T00:00:00.000+00:00"
OP1 = "op-0000000000000020"
OP2 = "op-0000000000000021"


def _wait_terminal(runtime, operation_id, timeout=10.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
        receipt = runtime.receipt(operation_id)
        if receipt["state"] in {"completed", "cancelled", "failed"}:
            return receipt
        time.sleep(0.01)
    return runtime.receipt(operation_id)


def _add_second_project(repo):
    with repo._conn:
        repo._conn.execute(
            "INSERT INTO books (book_id,title,created_at,updated_at)"
            " VALUES ('b2','Second',?,?)",
            (NOW, NOW),
        )
        repo._conn.execute(
            "INSERT INTO chapters (chapter_id,book_id,title,created_at,updated_at)"
            " VALUES ('c2','b2','Ch2',?,?)",
            (NOW, NOW),
        )


def _import_into(runtime, repo, grant, chapter, operation):
    plan = runtime._planner.plan(
        chapter_id=chapter, grants=[grant], duplicate_policy="skip"
    )
    runtime.start(
        chapter_id=chapter,
        plan_id=plan["plan_id"],
        plan_digest=plan["plan_digest"],
        grants=[grant],
        duplicate_policy="skip",
        operation_id=operation,
    )
    receipt = _wait_terminal(runtime, operation)
    assert receipt["state"] == "completed", receipt


def test_same_source_shared_across_projects(tmp_path, repo, book_chapter):
    _add_second_project(repo)
    access = FakeSourceReadAccess()
    path = tmp_path / "shared.png"
    path.write_bytes(png_bytes(5, 5))
    access.add_file("g-image-0000000021", "image", path)
    access.add_file("g-image-0000000022", "image", path)
    runtime = build_runtime(repo, access)

    _import_into(runtime, repo, "g-image-0000000021", "c1", OP1)
    _import_into(runtime, repo, "g-image-0000000022", "c2", OP2)

    pages1 = repo.list_pages("c1")
    pages2 = repo.list_pages("c2")
    assert len(pages1) == 1 and len(pages2) == 1
    assert pages1[0].page_id != pages2[0].page_id
    first = repo.get_page_binding(pages1[0].page_id)
    second = repo.get_page_binding(pages2[0].page_id)
    assert first["project_id"] == "b1"
    assert second["project_id"] == "b2"
    # One physical file is one source identity, shared by both bindings.
    assert first["source_id"] == second["source_id"]
    count = repo._conn.execute("SELECT COUNT(*) FROM sources").fetchone()[0]
    assert count == 1
