"""FEA-12 CORE: unified ProtectionPolicy (AC10) + isolation/meta AC12.

C-09 SC-B04a requires the three delete paths to share ONE judgement function:
soft delete preserves everything, automatic cleanup refuses protected content,
and explicit permanent delete discloses instead of blocking (the only hard
blockers are active operations and genuinely unsplittable shared state).
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import pytest

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from application.library.service import is_inventory_digest  # noqa: E402
from application.maintenance.cleanup import is_safe_relative_path  # noqa: E402
from application.maintenance.ports import (  # noqa: E402
    PROTECTION_REASON_BUSY,
    PROTECTION_REASON_DRAFT,
    PROTECTION_REASON_LOCK,
    PROTECTION_REASON_MANUAL,
    PROTECTION_REASON_REVISION,
    PROTECTION_REASON_SHARED_UNSAFE,
    ProtectionFacts,
    ProtectionPolicy,
    ProtectionScope,
)
from bootstrap.core_service import CoreServiceServer, assemble_production_core  # noqa: E402

NOW = "2026-11-05T00:00:00+00:00"

#: Names of real Windows recycle-bin / shell deletion entry points that this
#: release must not call anywhere (D flow is OUT of scope; zero OS APIs).
FORBIDDEN_RECYCLE_API_TOKENS = (
    "SHFileOperation",
    "IFileOperation",
    "Shell32",
    "Microsoft.VisualBasic",
    "Windows.Storage",
    "SendToRecycleBin",
    "FOF_ALLOWUNDO",
)


def _rpc(server: CoreServiceServer, command: str, payload: object, *, minor: int) -> dict:
    response, should_exit = server.dispatch_request(json.dumps({
        "protocol": "new-manga.core",
        "version": {"major": 2, "minor": minor},
        "request_id": "fea12-protection-req",
        "command": command,
        "payload": payload,
    }))
    assert not should_exit
    return response


# --- Policy unit matrix (same function for A/B/C) ---------------------


def test_soft_delete_is_never_blocked_by_protection() -> None:
    facts = ProtectionFacts(
        lock_count=3,
        manual_region_count=2,
        current_revision_count=1,
        pinned_revision_count=1,
        draft_page_count=1,
        active_run_count=1,
        active_export_count=1,
        unsafe_shared_ref_count=1,
    )
    verdict = ProtectionPolicy.evaluate(ProtectionScope.SOFT_DELETE, facts)
    assert verdict.blocked is False
    assert verdict.reasons == ()
    assert verdict.disclosure_required is False


def test_auto_cleanup_refuses_protected_facts() -> None:
    """ADJ-001 §3 B: automatic cleanup never destroys human work → refuse."""
    locked = ProtectionPolicy.evaluate(
        ProtectionScope.AUTO_CLEANUP, ProtectionFacts(lock_count=1)
    )
    assert locked.blocked is True
    assert PROTECTION_REASON_LOCK in locked.reasons

    manual = ProtectionPolicy.evaluate(
        ProtectionScope.AUTO_CLEANUP, ProtectionFacts(manual_region_count=1)
    )
    assert manual.blocked is True
    assert PROTECTION_REASON_MANUAL in manual.reasons

    revision = ProtectionPolicy.evaluate(
        ProtectionScope.AUTO_CLEANUP, ProtectionFacts(current_revision_count=1)
    )
    assert revision.blocked is True
    assert PROTECTION_REASON_REVISION in revision.reasons

    draft = ProtectionPolicy.evaluate(
        ProtectionScope.AUTO_CLEANUP, ProtectionFacts(draft_page_count=1)
    )
    assert draft.blocked is True
    assert PROTECTION_REASON_DRAFT in draft.reasons


def test_permanent_delete_discloses_but_does_not_block() -> None:
    """ADJ-001 PD-01: protected content is *disclosed*, never a refusal —
    otherwise a book with manual edits could never be deleted."""
    facts = ProtectionFacts(
        lock_count=2,
        manual_region_count=2,
        current_revision_count=1,
        pinned_revision_count=1,
        draft_page_count=1,
    )
    verdict = ProtectionPolicy.evaluate(ProtectionScope.PERMANENT_DELETE, facts)
    assert verdict.blocked is False
    assert verdict.disclosure_required is True
    for reason in (
        PROTECTION_REASON_LOCK,
        PROTECTION_REASON_MANUAL,
        PROTECTION_REASON_REVISION,
        PROTECTION_REASON_DRAFT,
    ):
        assert reason in verdict.reasons


def test_permanent_delete_blocks_active_operations_and_unsafe_shared() -> None:
    busy = ProtectionPolicy.evaluate(
        ProtectionScope.PERMANENT_DELETE, ProtectionFacts(active_run_count=1)
    )
    assert busy.blocked is True
    assert PROTECTION_REASON_BUSY in busy.reasons
    export_busy = ProtectionPolicy.evaluate(
        ProtectionScope.PERMANENT_DELETE, ProtectionFacts(active_export_count=1)
    )
    assert export_busy.blocked is True
    unsafe = ProtectionPolicy.evaluate(
        ProtectionScope.PERMANENT_DELETE, ProtectionFacts(unsafe_shared_ref_count=1)
    )
    assert unsafe.blocked is True
    assert PROTECTION_REASON_SHARED_UNSAFE in unsafe.reasons


def test_policy_verdict_is_stable_for_the_same_scope() -> None:
    facts = ProtectionFacts(lock_count=1, manual_region_count=1, draft_page_count=1)
    first = ProtectionPolicy.evaluate(ProtectionScope.AUTO_CLEANUP, facts)
    second = ProtectionPolicy.evaluate(ProtectionScope.AUTO_CLEANUP, facts)
    assert first == second


def test_cache_cleanup_predicate_never_admits_business_paths() -> None:
    """AC10 regression: the cache cleanup face keeps its never-clean
    predicate — locks/manual data/current+pinned revisions live outside
    ``cache/`` so it structurally cannot hit a protected object."""
    for path in (
        "books/book-1/chapters/c1/original/p1.png",
        "books/book-1/regions/rev-1.json",
        "book-1/path.png",
        "trash-manifest.json",
    ):
        assert is_safe_relative_path(path) is False, path
    assert is_safe_relative_path("cache/webtoon-tiles/tile-1.png") is True
    # A dot-dot escape is refused even under the safe prefix.
    assert is_safe_relative_path("cache/../books/book-1/secret.png") is False


# --- Wire-level A/C consistency on a protected book -------------------


@pytest.fixture
def server(tmp_path: Path):
    core = assemble_production_core(tmp_path / "data")
    try:
        yield CoreServiceServer(core)
    finally:
        core.conn.close()


def _seed_locked_draft_book(server: CoreServiceServer) -> str:
    core = server._core
    conn = core.conn
    rel_path = "books/b1/p1.png"
    target = Path(core.storage.root) / rel_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(b"PROTECTED")
    with conn:
        conn.execute(
            "INSERT INTO books (book_id, title, created_at, updated_at)"
            " VALUES ('b1', 'Protected', ?, ?)",
            (NOW, NOW),
        )
        conn.execute(
            "INSERT INTO chapters (chapter_id, book_id, title, created_at, updated_at)"
            " VALUES ('c1', 'b1', 'Ch', ?, ?)",
            (NOW, NOW),
        )
        conn.execute(
            "INSERT INTO pages (page_id, chapter_id, managed_original_ref,"
            " created_at, updated_at) VALUES ('p1', 'c1', ?, ?, ?)",
            (rel_path, NOW, NOW),
        )
        conn.execute(
            "INSERT INTO regions (region_id, page_id, region_type, geometry_json,"
            " text_json, style_json, region_locked, created_at, updated_at)"
            " VALUES ('rg1', 'p1', 'speech', '{}',"
            " '{\"manual_edited\": true, \"translation_locked\": true}',"
            " '{}', 1, ?, ?)",
            (NOW, NOW),
        )
        conn.execute(
            "INSERT INTO region_revisions (region_revision_id, region_id,"
            " revision_no, snapshot_json, origin, review_state, is_pinned,"
            " created_at) VALUES ('rr1', 'rg1', 1, '{}', 'user', 'confirmed', 1, ?)",
            (NOW,),
        )
        conn.execute(
            "UPDATE regions SET current_revision_id = 'rr1' WHERE region_id = 'rg1'"
        )
    core.drafts.open_draft(
        "session-1", "p1", "rg1", base_revision_id="rr1", page_binding_version=0
    )
    return rel_path


def test_a_flow_passes_while_c_flow_discloses_on_the_same_book(
    server: CoreServiceServer,
) -> None:
    """AC10: 有锁 + 有草稿 —— 软删通过；彻底删除先披露后可执行."""
    _seed_locked_draft_book(server)
    moved = _rpc(
        server,
        "MoveToTrash",
        {"entries": [{"book_id": "b1"}], "idempotency_key": "k1"},
        minor=13,
    )
    assert moved["error"] is None, moved["error"]
    assert moved["result"]["moved"] == [{"book_id": "b1"}]
    restored = _rpc(
        server,
        "RestoreFromTrash",
        {"entries": [{"book_id": "b1"}], "idempotency_key": "k2"},
        minor=13,
    )
    assert restored["error"] is None
    assert restored["result"]["restored"] == [{"book_id": "b1"}]

    preview = _rpc(server, "PreviewPermanentDeleteBooks", {"bookIds": ["b1"]}, minor=11)
    assert preview["error"] is None, preview["error"]
    item = preview["result"]["items"][0]
    assert item["protection"]["lockCount"] == 1
    assert item["protection"]["manualRegionCount"] == 1
    assert item["protection"]["draftPageCount"] == 1
    assert item["protection"]["pinnedRevisionIds"] == ["rr1"]
    digest = preview["result"]["inventoryDigests"]["b1"]
    deleted = _rpc(
        server,
        "PermanentlyDeleteBook",
        {
            "book_id": "b1",
            "confirm_permanent_delete": True,
            "inventory_digest": digest,
        },
        minor=10,
    )
    assert deleted["error"] is None, deleted["error"]
    # 披露 ≠ 阻断: the protected rows are gone after the dedicated confirmation.
    assert server._core.conn.execute("SELECT COUNT(*) FROM regions").fetchone()[0] == 0
    assert server._core.conn.execute("SELECT COUNT(*) FROM region_revisions").fetchone()[0] == 0
    assert server._core.conn.execute("SELECT COUNT(*) FROM books").fetchone()[0] == 0


def test_permanent_delete_blocks_nonterminal_run_while_soft_delete_passes(
    server: CoreServiceServer,
) -> None:
    """AC10: 非终态 Run 彻底删除 BOOK_BUSY；同一本书软删通过."""
    _seed_locked_draft_book(server)
    with server._core.conn:
        server._core.conn.execute(
            "INSERT INTO pipeline_runs (run_id, command_type, scope_type,"
            " requested_targets_json, settings_snapshot_json,"
            " provider_binding_snapshot_json, context_policy_json, status,"
            " run_json, updated_at)"
            " VALUES ('run-active', 'translate', 'book', '[]', '{}', '{}',"
            " '{}', 'running', ?, ?)",
            (json.dumps({"scope": {"book_id": "b1"}}), NOW),
        )
    moved = _rpc(
        server,
        "MoveToTrash",
        {"entries": [{"book_id": "b1"}], "idempotency_key": "k1"},
        minor=13,
    )
    assert moved["error"] is None
    assert _rpc(
        server,
        "RestoreFromTrash",
        {"entries": [{"book_id": "b1"}], "idempotency_key": "k2"},
        minor=13,
    )["error"] is None
    preview = _rpc(server, "PreviewPermanentDeleteBooks", {"bookIds": ["b1"]}, minor=11)
    assert preview["result"]["items"][0]["protection"]["activeRunIds"] == ["run-active"]
    blocked = _rpc(
        server,
        "PermanentlyDeleteBook",
        {
            "book_id": "b1",
            "confirm_permanent_delete": True,
            "inventory_digest": preview["result"]["inventoryDigests"]["b1"],
        },
        minor=10,
    )
    assert blocked["error"]["code"] == "BOOK_BUSY"
    assert server._core.conn.execute("SELECT COUNT(*) FROM books").fetchone()[0] == 1


# --- AC12 isolation / no OS recycle-bin APIs -------------------------


def _tree_fingerprint(root: Path) -> dict[str, str]:
    return {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def test_delete_flows_are_isolated_to_the_tmp_data_root(
    server: CoreServiceServer, tmp_path: Path
) -> None:
    core = server._core
    data_root = Path(core.data_root)
    assert data_root.is_relative_to(tmp_path)
    sentinel = tmp_path / "outside-root"
    (sentinel / "user-sources").mkdir(parents=True)
    (sentinel / "user-sources" / "original.png").write_bytes(b"USER SOURCE")
    (sentinel / "notes.txt").write_text("keep me", encoding="utf-8")
    before = _tree_fingerprint(sentinel)

    book = core.library.create_book(title="Isolated")
    _rpc(
        server,
        "MoveToTrash",
        {"entries": [{"book_id": book.book_id}], "idempotency_key": "k1"},
        minor=13,
    )
    _rpc(
        server,
        "RestoreFromTrash",
        {"entries": [{"book_id": book.book_id}], "idempotency_key": "k2"},
        minor=13,
    )
    _rpc(server, "ListTrash", {}, minor=13)
    preview = _rpc(
        server, "PreviewPermanentDeleteBooks", {"bookIds": [book.book_id]}, minor=11
    )
    assert preview["error"] is None
    _rpc(
        server,
        "PermanentlyDeleteBook",
        {
            "book_id": book.book_id,
            "confirm_permanent_delete": True,
            "inventory_digest": preview["result"]["inventoryDigests"][book.book_id],
        },
        minor=10,
    )
    assert _tree_fingerprint(sentinel) == before
    # The released digest helper is available to fixtures for recomputation.
    assert is_inventory_digest(preview["result"]["inventoryDigests"][book.book_id])


def test_delete_stack_calls_no_windows_recycle_bin_api() -> None:
    """D flow (real Windows recycle bin) is OUT of scope: the delete stack must
    contain zero real recycle/shell deletion API references."""
    checked = 0
    for path in sorted((SRC_ROOT).rglob("*.py")):
        text = path.read_text(encoding="utf-8", errors="ignore")
        checked += 1
        for token in FORBIDDEN_RECYCLE_API_TOKENS:
            assert token not in text, f"{token} referenced in {path}"
    assert checked > 100, "the static scan walked an implausibly small tree"


def test_delete_modules_use_no_real_user_data_roots() -> None:
    """AC12: the FEA-12 implementation modules contain no real roaming/
    local app-data or user-profile path expansion — every root is injected."""
    app_data = "APP" + "DATA"
    local_app_data = "LOCAL" + app_data
    modules = (
        SRC_ROOT / "application" / "library" / "service.py",
        SRC_ROOT / "application" / "maintenance" / "ports.py",
        SRC_ROOT / "infrastructure" / "sqlite" / "library.py",
        SRC_ROOT / "domain" / "books" / "entities.py",
    )
    for module in modules:
        text = module.read_text(encoding="utf-8")
        for token in (
            app_data,
            local_app_data,
            "expanduser",
            "os.environ",
            "getenv(",
        ):
            assert token not in text, f"{token} in {module}"
