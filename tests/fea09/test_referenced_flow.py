"""FEA-09 AC-3/AC-5: plan/start/receipt/cancel state machine and counts.

Covers the frozen C-16 §4 scenarios (accepted-cancel, partial cancel with an
unsupported member, mid-run failure, unsupported-only, whole-source skip,
partial already-referenced), the replay matrix, the per-book single-flight
lock, cross-restart SOURCE_OPERATION_NOT_FOUND, natural-key retry without
duplicate pages, plan staleness and the SOURCE_PROJECT_MISMATCH guard.
"""

from __future__ import annotations

import time

import pytest

from support import (
    FakeSourceReadAccess,
    HookDecoder,
    build_pdf_open,
    build_runtime,
    png_bytes,
    write_zip,
)
from application.importing.referenced.errors import SourceImportError
from application.importing.referenced.planner import ReferencedImportPlanner
from application.importing.referenced.runtime import ReferencedImportRuntime
from tests.fea09.zip_fixtures import make_flat_pdf

OP = "op-0000000000000001"
OP2 = "op-0000000000000002"


def _wait_terminal(runtime, operation_id, timeout=20.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
        receipt = runtime.receipt(operation_id)
        if receipt["state"] in {"completed", "cancelled", "failed"}:
            return receipt
        time.sleep(0.01)
    return runtime.receipt(operation_id)


def _plan_and_start(runtime, grant_ids, *, chapter="c1", policy="skip",
                    operation=OP, secret_ref=None):
    planner = runtime._planner
    plan = planner.plan(
        chapter_id=chapter, grants=grant_ids, duplicate_policy=policy
    )
    return runtime.start(
        chapter_id=chapter,
        plan_id=plan["plan_id"],
        plan_digest=plan["plan_digest"],
        grants=grant_ids,
        duplicate_policy=policy,
        operation_id=operation,
        secret_ref=secret_ref,
    )


def _image_grant_(access, tmp_path, name, grant):
    path = tmp_path / name
    path.write_bytes(png_bytes(4, 4))
    access.add_file(grant, "image", path)
    return path


# --------------------------------------------------------------- happy path
def test_import_images_full_flow(tmp_path, repo, book_chapter):
    access = FakeSourceReadAccess()
    _image_grant_(access, tmp_path, "001.png", "g-image-0000000001")
    _image_grant_(access, tmp_path, "002.png", "g-image-0000000002")
    runtime = build_runtime(repo, access)

    plan = runtime._planner.plan(
        chapter_id="c1",
        grants=["g-image-0000000001", "g-image-0000000002"],
        duplicate_policy="skip",
    )
    assert plan["totals"] == {"import": 2, "skip": 0, "unsupported": 0, "failed": 0}

    started = runtime.start(
        chapter_id="c1", plan_id=plan["plan_id"], plan_digest=plan["plan_digest"],
        grants=["g-image-0000000001", "g-image-0000000002"],
        duplicate_policy="skip", operation_id=OP,
    )
    assert started == {
        "operation_id": OP, "accepted": True, "plan_digest": plan["plan_digest"],
    }
    receipt = _wait_terminal(runtime, OP)
    assert receipt["state"] == "completed"
    assert receipt["totals"]["imported_pages"] == 2
    assert receipt["committed_boundary"] == 2

    pages = repo.list_pages("c1")
    assert len(pages) == 2
    for page in pages:
        assert page.source_mode == "referenced"
        assert page.integrity_status == "complete"
        assert page.width == 4 and page.height == 4
        binding = repo.get_page_binding(page.page_id)
        assert binding["status"] == "healthy"
        assert binding["project_id"] == "b1"
    counts = repo._conn.execute(
        "SELECT (SELECT COUNT(*) FROM sources) s,"
        " (SELECT COUNT(*) FROM source_versions) v,"
        " (SELECT COUNT(*) FROM source_entries) e,"
        " (SELECT COUNT(*) FROM page_bindings) b"
    ).fetchone()
    assert (counts["s"], counts["v"], counts["e"], counts["b"]) == (2, 2, 2, 2)


def test_import_zip_occurrences_and_order(tmp_path, repo, book_chapter):
    access = FakeSourceReadAccess()
    members = [
        ("002.png", png_bytes(3, 3, (0, 255, 0))),
        ("001.png", png_bytes(3, 3, (255, 0, 0))),
        ("dup/001.png", png_bytes(3, 3, (255, 0, 0))),
        ("010.png", png_bytes(3, 3, (0, 0, 255))),
    ]
    path = write_zip(tmp_path / "book.zip", members)
    access.add_file("g-zip-0000000000001", "zip", path)
    runtime = build_runtime(repo, access)

    _plan_and_start(runtime, ["g-zip-0000000000001"])
    receipt = _wait_terminal(runtime, OP)
    assert receipt["state"] == "completed"
    assert receipt["totals"]["imported_pages"] == 4

    pages = repo.list_pages("c1")
    # natural order: 001.png, 002.png, 010.png, dup/001.png (AC-2)
    assert [p.source_filename for p in pages] == [
        "001.png", "002.png", "010.png", "001.png",
    ]
    orders = [p.source_order for p in pages]
    assert orders == sorted(orders)
    assert len({p.page_id for p in pages}) == 4
    entries = repo._conn.execute(
        "SELECT locator FROM source_entries ORDER BY ordinal"
    ).fetchall()
    assert [row["locator"] for row in entries] == [
        "001.png", "002.png", "010.png", "dup/001.png",
    ]


def test_import_pdf_pages(tmp_path, repo, book_chapter):
    path = tmp_path / "doc.pdf"
    path.write_bytes(make_flat_pdf(3))
    access = FakeSourceReadAccess()
    access.add_file("g-pdf-00000000000001", "pdf", path)
    runtime = build_runtime(repo, access)

    _plan_and_start(runtime, ["g-pdf-00000000000001"])
    receipt = _wait_terminal(runtime, OP)
    assert receipt["state"] == "completed"
    assert receipt["totals"]["imported_pages"] == 3
    pages = repo.list_pages("c1")
    assert [p.source_filename for p in pages] == ["1", "2", "3"]
    assert all(p.width == 612 and p.height == 792 for p in pages)


def test_import_folder_nested_order(tmp_path, repo, book_chapter):
    access = FakeSourceReadAccess()
    root = tmp_path / "src"
    root.mkdir()
    names = ["1.png", "2.png", "10.png", "100.png", "nested/a.png"]
    paths = []
    for name in names:
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(png_bytes(3, 3))
        paths.append(target)
    access.add_folder("g-folder-0000000001", root, paths)
    runtime = build_runtime(repo, access)

    _plan_and_start(runtime, ["g-folder-0000000001"])
    receipt = _wait_terminal(runtime, OP)
    assert receipt["state"] == "completed"
    assert receipt["totals"]["imported_pages"] == 5
    pages = repo.list_pages("c1")
    assert [p.source_filename for p in pages] == [
        "1.png", "2.png", "10.png", "100.png", "a.png",
    ]


# ------------------------------------------------------ C-16 §4 scenarios
def test_scenario_1_accepted_cancel(tmp_path, repo, book_chapter):
    """accepted 即取消：planned=20，imported=0，pending=20，remaining=20。"""
    path = write_zip(
        tmp_path / "cancel.zip", [(f"{i:03d}.png", png_bytes(2, 2)) for i in range(20)]
    )
    access = FakeSourceReadAccess()
    access.add_file("g-zip-0000000000002", "zip", path)
    runtime = build_runtime(repo, access)
    plan = runtime._planner.plan(
        chapter_id="c1", grants=["g-zip-0000000000002"], duplicate_policy="skip"
    )

    # Hold the worker in `accepted`: cancel before the thread ever runs.
    import application.importing.referenced.runtime as runtime_module

    class _NoThread:
        def __init__(self, *args, **kwargs):
            pass

        def start(self):
            return None

    original_thread = runtime_module.threading.Thread
    runtime_module.threading.Thread = _NoThread
    try:
        started = runtime.start(
            chapter_id="c1", plan_id=plan["plan_id"], plan_digest=plan["plan_digest"],
            grants=["g-zip-0000000000002"], duplicate_policy="skip", operation_id=OP,
        )
        assert started["accepted"] is True
        cancelled = runtime.cancel(OP)
        assert cancelled == {
            "operation_id": OP, "accepted": True, "state": "cancelled",
        }
    finally:
        runtime_module.threading.Thread = original_thread

    receipt = runtime.receipt(OP)
    assert receipt["state"] == "cancelled"
    item = receipt["items"][0]
    assert item["outcome"] == "pending"
    assert item["counts"] == {
        "imported_pages": 0, "skipped_pages": 0, "skipped_sources": 0,
        "failed_sources": 0, "unsupported_entries": 0, "pending_pages": 20,
    }
    assert item["remaining_pages"] == 20
    assert receipt["totals"]["pending_pages"] == 20
    assert repo.list_pages("c1") == []


def test_scenario_2_partial_cancel_with_unsupported(tmp_path, repo, book_chapter):
    """提交 12 页后取消（20 页含 1 unsupported）：pending=7，已提交保留。"""
    members = [(f"{i:03d}.png", png_bytes(2, 2)) for i in range(19)]
    members.insert(0, ("000-note.txt", b"note"))
    path = write_zip(tmp_path / "mixed.zip", members)
    access = FakeSourceReadAccess()
    access.add_file("g-zip-0000000000003", "zip", path)

    runtime_holder = {}

    def hook(call_index, data):
        if call_index == 12:
            runtime_holder["runtime"].cancel(OP)

    decoder = HookDecoder(hook=hook)
    runtime = build_runtime(repo, access, decoder=decoder)
    runtime_holder["runtime"] = runtime

    _plan_and_start(runtime, ["g-zip-0000000000003"])
    receipt = _wait_terminal(runtime, OP)
    assert receipt["state"] == "cancelled"
    item = receipt["items"][0]
    assert item["counts"]["imported_pages"] == 12
    assert item["counts"]["unsupported_entries"] == 1
    assert item["counts"]["pending_pages"] == 7
    assert item["remaining_pages"] == 7
    assert receipt["committed_boundary"] == 12
    assert len(repo.list_pages("c1")) == 12


def test_scenario_3_midrun_failure(tmp_path, repo, book_chapter):
    """提交 12 页后失败：failed_sources=1，已提交不回滚，pending=7。"""
    members = [(f"{i:03d}.png", png_bytes(2, 2)) for i in range(19)]
    members.insert(0, ("000-note.txt", b"note"))
    path = write_zip(tmp_path / "fail.zip", members)
    access = FakeSourceReadAccess()
    access.add_file("g-zip-0000000000004", "zip", path)

    def hook(call_index, data):
        if call_index == 13:
            raise SourceImportError(
                "FILE_IDENTITY_CHANGED", "member identity drifted"
            )

    runtime = build_runtime(repo, access, decoder=HookDecoder(hook=hook))

    _plan_and_start(runtime, ["g-zip-0000000000004"])
    receipt = _wait_terminal(runtime, OP)
    assert receipt["state"] == "failed"
    item = receipt["items"][0]
    assert item["outcome"] == "failed"
    assert item["reason_code"] == "FILE_IDENTITY_CHANGED"
    assert item["counts"]["imported_pages"] == 12
    assert item["counts"]["failed_sources"] == 1
    assert item["counts"]["unsupported_entries"] == 1
    assert item["counts"]["pending_pages"] == 7
    assert item["remaining_pages"] == 7
    assert len(repo.list_pages("c1")) == 12


def test_revocation_halts_at_commit_boundary(tmp_path, repo, book_chapter):
    """RevokeSourceReadGrant 语义：commit 前重验失败 → 中止后续单元。"""
    path = write_zip(
        tmp_path / "rev.zip", [(f"{i:03d}.png", png_bytes(2, 2)) for i in range(10)]
    )
    access = FakeSourceReadAccess()
    access.add_file("g-zip-000000000005", "zip", path)
    runtime = build_runtime(repo, access)

    original_verify = access.verify_before_commit

    def fail_after_five(grant_id):
        original_verify(grant_id)
        if len(access.verify_calls) == 6:
            raise SourceImportError(
                "SOURCE_GRANT_REVOKED", "grant was revoked mid-run"
            )

    access.verify_before_commit = fail_after_five
    _plan_and_start(runtime, ["g-zip-000000000005"])
    receipt = _wait_terminal(runtime, OP)
    assert receipt["state"] == "failed"
    item = receipt["items"][0]
    assert item["reason_code"] == "SOURCE_GRANT_REVOKED"
    assert item["counts"]["imported_pages"] == 5
    assert item["counts"]["pending_pages"] == 5
    assert len(repo.list_pages("c1")) == 5


def test_scenario_4_unsupported_only(tmp_path, repo, book_chapter):
    """unsupported-only（20 页）：planned=20，unsupported=20，completed。"""
    members = [(f"n{i:03d}.txt", b"note") for i in range(20)]
    path = write_zip(tmp_path / "text.zip", members)
    access = FakeSourceReadAccess()
    access.add_file("g-zip-000000000006", "zip", path)
    runtime = build_runtime(repo, access)

    _plan_and_start(runtime, ["g-zip-000000000006"])
    receipt = _wait_terminal(runtime, OP)
    assert receipt["state"] == "completed"
    item = receipt["items"][0]
    assert item["outcome"] == "unsupported"
    assert item["counts"]["unsupported_entries"] == 20
    assert item["counts"]["pending_pages"] == 0
    assert item["remaining_pages"] == 0
    assert repo.list_pages("c1") == []


def test_scenario_5_whole_source_skip(tmp_path, repo, book_chapter):
    """整源已引用跳过：planned=0，skipped_sources=1（skip 政策二次导入）。"""
    path = write_zip(
        tmp_path / "again.zip", [(f"{i:03d}.png", png_bytes(2, 2)) for i in range(6)]
    )
    access = FakeSourceReadAccess()
    access.add_file("g-zip-000000000007", "zip", path)
    runtime = build_runtime(repo, access)

    _plan_and_start(runtime, ["g-zip-000000000007"], operation=OP)
    first = _wait_terminal(runtime, OP)
    assert first["totals"]["imported_pages"] == 6

    _plan_and_start(runtime, ["g-zip-000000000007"], operation=OP2)
    second = _wait_terminal(runtime, OP2)
    assert second["state"] == "completed"
    item = second["items"][0]
    assert item["outcome"] == "skipped"
    assert item["counts"] == {
        "imported_pages": 0, "skipped_pages": 0, "skipped_sources": 1,
        "failed_sources": 0, "unsupported_entries": 0, "pending_pages": 0,
    }
    assert len(repo.list_pages("c1")) == 6


def test_scenario_6_partial_already_referenced(tmp_path, repo, book_chapter):
    """部分已引用：import_as_new 下已绑定 entry 跳过（不可绕过唯一性）。"""
    members = [(f"{i:03d}.png", png_bytes(2, 2)) for i in range(8)]
    path = write_zip(tmp_path / "part.zip", members)
    access = FakeSourceReadAccess()
    access.add_file("g-zip-000000000008", "zip", path)
    runtime = build_runtime(repo, access)

    _plan_and_start(runtime, ["g-zip-000000000008"], operation=OP)
    first = _wait_terminal(runtime, OP)
    assert first["totals"]["imported_pages"] == 8

    # import_as_new cannot bypass project-internal entry uniqueness (C-16 §4)
    _plan_and_start(
        runtime, ["g-zip-000000000008"], policy="import_as_new", operation=OP2
    )
    second = _wait_terminal(runtime, OP2)
    item = second["items"][0]
    assert item["counts"]["skipped_pages"] == 8
    assert item["counts"]["imported_pages"] == 0
    assert item["counts"]["pending_pages"] == 0
    assert item["outcome"] == "skipped"
    assert len(repo.list_pages("c1")) == 8


# --------------------------------------------------------- replay / locks
def test_replay_same_id_same_fingerprint(tmp_path, repo, book_chapter):
    access = FakeSourceReadAccess()
    _image_grant_(access, tmp_path, "r.png", "g-image-0000000001")
    runtime = build_runtime(repo, access)
    plan = runtime._planner.plan(
        chapter_id="c1", grants=["g-image-0000000001"], duplicate_policy="skip"
    )
    started = runtime.start(
        chapter_id="c1", plan_id=plan["plan_id"], plan_digest=plan["plan_digest"],
        grants=["g-image-0000000001"], duplicate_policy="skip", operation_id=OP,
    )
    assert started["accepted"] is True
    replay = runtime.start(
        chapter_id="c1", plan_id=plan["plan_id"], plan_digest=plan["plan_digest"],
        grants=["g-image-0000000001"], duplicate_policy="skip", operation_id=OP,
    )
    assert replay["accepted"] is True
    assert replay["state"] in {"running", "completed"}
    _wait_terminal(runtime, OP)
    final = runtime.start(
        chapter_id="c1", plan_id=plan["plan_id"], plan_digest=plan["plan_digest"],
        grants=["g-image-0000000001"], duplicate_policy="skip", operation_id=OP,
    )
    assert final["state"] == "completed"
    assert repo._conn.execute("SELECT COUNT(*) c FROM pages").fetchone()["c"] == 1


def test_replay_conflicting_fingerprint_rejected(tmp_path, repo, book_chapter):
    access = FakeSourceReadAccess()
    _image_grant_(access, tmp_path, "c.png", "g-image-0000000001")
    _image_grant_(access, tmp_path, "d.png", "g-image-0000000002")
    runtime = build_runtime(repo, access)
    plan = runtime._planner.plan(
        chapter_id="c1", grants=["g-image-0000000001"], duplicate_policy="skip"
    )
    runtime.start(
        chapter_id="c1", plan_id=plan["plan_id"], plan_digest=plan["plan_digest"],
        grants=["g-image-0000000001"], duplicate_policy="skip", operation_id=OP,
    )
    other = runtime._planner.plan(
        chapter_id="c1", grants=["g-image-0000000002"], duplicate_policy="skip"
    )
    with pytest.raises(SourceImportError) as caught:
        runtime.start(
            chapter_id="c1", plan_id=other["plan_id"],
            plan_digest=other["plan_digest"],
            grants=["g-image-0000000002"], duplicate_policy="skip",
            operation_id=OP,
        )
    assert caught.value.code == "SOURCE_OPERATION_CONFLICT"


def test_project_lock_single_flight(tmp_path, repo, book_chapter):
    """同项目同时只允许一个非终态 import → SOURCE_IMPORT_BUSY。"""
    path = write_zip(
        tmp_path / "busy.zip", [(f"{i:03d}.png", png_bytes(2, 2)) for i in range(30)]
    )
    access = FakeSourceReadAccess()
    access.add_file("g-zip-000000000009", "zip", path)
    runtime = build_runtime(repo, access)

    plan = runtime._planner.plan(
        chapter_id="c1", grants=["g-zip-000000000009"], duplicate_policy="skip"
    )
    runtime.start(
        chapter_id="c1", plan_id=plan["plan_id"], plan_digest=plan["plan_digest"],
        grants=["g-zip-000000000009"], duplicate_policy="skip", operation_id=OP,
    )
    plan2 = runtime._planner.plan(
        chapter_id="c1", grants=["g-zip-000000000009"], duplicate_policy="skip"
    )
    with pytest.raises(SourceImportError) as caught:
        runtime.start(
            chapter_id="c1", plan_id=plan2["plan_id"],
            plan_digest=plan2["plan_digest"],
            grants=["g-zip-000000000009"], duplicate_policy="skip",
            operation_id=OP2,
        )
    assert caught.value.code == "SOURCE_IMPORT_BUSY"
    _wait_terminal(runtime, OP, timeout=30.0)
    plan3 = runtime._planner.plan(
        chapter_id="c1", grants=["g-zip-000000000009"], duplicate_policy="skip"
    )
    runtime.start(
        chapter_id="c1", plan_id=plan3["plan_id"], plan_digest=plan3["plan_digest"],
        grants=["g-zip-000000000009"], duplicate_policy="skip", operation_id=OP2,
    )
    receipt = _wait_terminal(runtime, OP2, timeout=30.0)
    assert receipt["totals"]["skipped_sources"] == 1


def test_cancel_after_terminal_rejected(tmp_path, repo, book_chapter):
    access = FakeSourceReadAccess()
    _image_grant_(access, tmp_path, "t.png", "g-image-0000000001")
    runtime = build_runtime(repo, access)
    _plan_and_start(runtime, ["g-image-0000000001"])
    _wait_terminal(runtime, OP)
    cancelled = runtime.cancel(OP)
    assert cancelled == {"operation_id": OP, "accepted": False, "state": "completed"}


def test_cross_restart_operation_not_found(tmp_path, repo, book_chapter):
    """Receipt 是会话内状态：新 runtime 实例（重启语义）→ NOT_FOUND。"""
    access = FakeSourceReadAccess()
    _image_grant_(access, tmp_path, "x.png", "g-image-0000000001")
    runtime = build_runtime(repo, access)
    _plan_and_start(runtime, ["g-image-0000000001"])
    _wait_terminal(runtime, OP)
    restarted = build_runtime(repo, FakeSourceReadAccess())
    with pytest.raises(SourceImportError) as caught:
        restarted.receipt(OP)
    assert caught.value.code == "SOURCE_OPERATION_NOT_FOUND"


def test_natural_key_retry_no_duplicate_pages(tmp_path, repo, book_chapter):
    """重试经自然键判 skipped，不产生重复页（C-16 §4）。"""
    path = write_zip(
        tmp_path / "retry.zip", [(f"{i:03d}.png", png_bytes(2, 2)) for i in range(5)]
    )
    access = FakeSourceReadAccess()
    access.add_file("g-zip-00000000000a", "zip", path)
    runtime = build_runtime(repo, access)
    _plan_and_start(runtime, ["g-zip-00000000000a"], operation=OP)
    _wait_terminal(runtime, OP)
    _plan_and_start(runtime, ["g-zip-00000000000a"], operation=OP2)
    receipt = _wait_terminal(runtime, OP2)
    assert receipt["state"] == "completed"
    assert receipt["totals"]["imported_pages"] == 0
    assert receipt["totals"]["skipped_sources"] == 1
    assert repo._conn.execute("SELECT COUNT(*) c FROM pages").fetchone()["c"] == 5


def test_plan_stale_when_container_changes(tmp_path, repo, book_chapter):
    """确认前源变化：容器 digest 漂移 → strict 重验 typed 失败。"""
    import io
    import zipfile

    path = write_zip(tmp_path / "stale.zip", [("001.png", png_bytes(2, 2))])
    access = FakeSourceReadAccess()
    access.add_file("g-zip-00000000000b", "zip", path)
    runtime = build_runtime(repo, access)
    plan = runtime._planner.plan(
        chapter_id="c1", grants=["g-zip-00000000000b"], duplicate_policy="skip"
    )
    # Same physical file, different content: grant facts no longer match.
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("001.png", png_bytes(2, 2, (7, 7, 7)))
    path.write_bytes(buffer.getvalue())
    runtime.start(
        chapter_id="c1", plan_id=plan["plan_id"], plan_digest=plan["plan_digest"],
        grants=["g-zip-00000000000b"], duplicate_policy="skip", operation_id=OP,
    )
    receipt = _wait_terminal(runtime, OP)
    assert receipt["state"] == "failed"
    assert receipt["items"][0]["reason_code"] == "FILE_IDENTITY_CHANGED"
    assert repo.list_pages("c1") == []


def test_start_rejects_wrong_digest(tmp_path, repo, book_chapter):
    access = FakeSourceReadAccess()
    _image_grant_(access, tmp_path, "w.png", "g-image-0000000001")
    runtime = build_runtime(repo, access)
    plan = runtime._planner.plan(
        chapter_id="c1", grants=["g-image-0000000001"], duplicate_policy="skip"
    )
    with pytest.raises(SourceImportError) as caught:
        runtime.start(
            chapter_id="c1", plan_id=plan["plan_id"], plan_digest="0" * 64,
            grants=["g-image-0000000001"], duplicate_policy="skip",
            operation_id=OP,
        )
    assert caught.value.code == "SOURCE_PLAN_STALE"


def test_project_mismatch_rolls_back_unit(tmp_path, repo, book_chapter):
    """SOURCE_PROJECT_MISMATCH：page→chapter→book 与 project_id 不符 → 回滚。"""
    conn = repo._conn
    conn.execute(
        "INSERT INTO books (book_id, title, created_at, updated_at)"
        " VALUES ('b2', 'Other', '2026-11-03T00:00:00', '2026-11-03T00:00:00')"
    )
    conn.execute(
        "INSERT INTO chapters (chapter_id, book_id, title, created_at, updated_at)"
        " VALUES ('c2', 'b2', 'Ch2', '2026-11-03T00:00:00', '2026-11-03T00:00:00')"
    )
    conn.commit()

    access = FakeSourceReadAccess()
    _image_grant_(access, tmp_path, "mm.png", "g-image-0000000001")

    def wrong_project(chapter_id):
        return "b2"  # chapter c1 belongs to b1 — the binding must be refused

    planner = ReferencedImportPlanner(
        access=access, repository=repo, project_of_chapter=wrong_project,
        pdf_open=build_pdf_open(),
    )
    runtime = ReferencedImportRuntime(
        repository=repo, access=access, planner=planner,
        project_of_chapter=wrong_project, image_decoder=HookDecoder(),
        pdf_open=build_pdf_open(),
    )
    plan = planner.plan(
        chapter_id="c1", grants=["g-image-0000000001"], duplicate_policy="skip"
    )
    runtime.start(
        chapter_id="c1", plan_id=plan["plan_id"], plan_digest=plan["plan_digest"],
        grants=["g-image-0000000001"], duplicate_policy="skip", operation_id=OP,
    )
    receipt = _wait_terminal(runtime, OP)
    assert receipt["state"] == "failed"
    counts = conn.execute(
        "SELECT (SELECT COUNT(*) FROM pages) p,"
        " (SELECT COUNT(*) FROM page_bindings) b,"
        " (SELECT COUNT(*) FROM sources) s"
    ).fetchone()
    assert (counts["p"], counts["b"], counts["s"]) == (0, 0, 0)


def test_disabled_flag_rejects_new_imports(tmp_path, repo, book_chapter):
    """ReferencedImportEnabled=false：拒新导入，已提交数据保持双读。"""
    access = FakeSourceReadAccess()
    _image_grant_(access, tmp_path, "on.png", "g-image-0000000001")
    runtime = build_runtime(repo, access)
    _plan_and_start(runtime, ["g-image-0000000001"])
    _wait_terminal(runtime, OP)
    assert len(repo.list_pages("c1")) == 1

    disabled = build_runtime(repo, access, enabled=lambda: False)
    _image_grant_(access, tmp_path, "off.png", "g-image-0000000002")
    with pytest.raises(SourceImportError) as caught:
        _plan_and_start(disabled, ["g-image-0000000002"], operation=OP2)
    assert caught.value.code == "SOURCE_ACCESS_DENIED"
    assert len(repo.list_pages("c1")) == 1
