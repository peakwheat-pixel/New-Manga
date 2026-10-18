"""Core 2.10 PermanentlyDeleteBook / PermanentlyDeleteBooks wire behavior and safety boundaries."""

from __future__ import annotations

import json
from pathlib import Path
import sys

import pytest

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from bootstrap.core_service import CoreServiceServer, assemble_production_core
from infrastructure.resource_channel.catalog_store import (
    ResourceCatalogStore,
    initialize_namespace,
)
from infrastructure.resource_channel.render_preview import RenderPreviewPublisher


@pytest.fixture
def server(tmp_path: Path):
    core = assemble_production_core(tmp_path / "data")
    try:
        yield CoreServiceServer(core)
    finally:
        core.conn.close()


def _rpc(
    server: CoreServiceServer,
    command: str,
    payload: object,
    *,
    minor: int = 10,
    major: int = 2,
    request_id: str = "del-test-req",
) -> dict:
    response, should_exit = server.dispatch_request(json.dumps({
        "protocol": "new-manga.core",
        "version": {"major": major, "minor": minor},
        "request_id": request_id,
        "command": command,
        "payload": payload,
    }))
    assert not should_exit
    return response


def _seed_book(server: CoreServiceServer, book_id: str, title: str) -> None:
    with server._core.conn:
        server._core.conn.execute(
            "INSERT INTO books (book_id, title, created_at, updated_at) VALUES (?, ?, 'now', 'now')",
            (book_id, title),
        )


def _seed_chapter_and_page(server: CoreServiceServer, book_id: str, chapter_id: str, page_id: str) -> str:
    storage = server._core.storage
    temp_h = storage.write_temp(b"dummy page bytes")
    rel_path = storage.new_revision_relative_path(book_id, chapter_id, "original", page_id, ".png")
    storage.publish(temp_h, rel_path)
    with server._core.conn:
        server._core.conn.execute(
            "INSERT INTO chapters (chapter_id, book_id, title, created_at, updated_at) VALUES (?, ?, 'Ch', 'now', 'now')",
            (chapter_id, book_id),
        )
        server._core.conn.execute(
            "INSERT INTO pages (page_id, chapter_id, managed_original_ref, created_at, updated_at) VALUES (?, ?, ?, 'now', 'now')",
            (page_id, chapter_id, rel_path),
        )
    return rel_path


# --- PermanentlyDeleteBook (Single) Tests ---

def test_delete_book_version_check(server: CoreServiceServer) -> None:
    _seed_book(server, "b1", "Book 1")
    # wrong minor
    res = _rpc(server, "PermanentlyDeleteBook", {"book_id": "b1", "confirm_permanent_delete": True}, minor=8)
    assert res["error"]["code"] == "INVALID_REQUEST"

    # wrong major
    res = _rpc(server, "PermanentlyDeleteBook", {"book_id": "b1", "confirm_permanent_delete": True}, major=3)
    assert res["error"]["code"] == "PROTOCOL_VERSION_UNSUPPORTED"


def test_delete_book_invalid_request_shape(server: CoreServiceServer) -> None:
    _seed_book(server, "b1", "Book 1")
    # missing confirm
    res = _rpc(server, "PermanentlyDeleteBook", {"book_id": "b1"})
    assert res["error"]["code"] == "INVALID_REQUEST"

    # confirm is false
    res = _rpc(server, "PermanentlyDeleteBook", {"book_id": "b1", "confirm_permanent_delete": False})
    assert res["error"]["code"] == "INVALID_REQUEST"

    # extra fields
    res = _rpc(server, "PermanentlyDeleteBook", {"book_id": "b1", "confirm_permanent_delete": True, "extra": 1})
    assert res["error"]["code"] == "INVALID_REQUEST"


def test_delete_book_not_found(server: CoreServiceServer) -> None:
    res = _rpc(server, "PermanentlyDeleteBook", {"book_id": "nonexistent", "confirm_permanent_delete": True})
    assert res["error"]["code"] == "BOOK_NOT_FOUND"
    assert res["error"]["category"] == "not_found"


def test_delete_book_busy(server: CoreServiceServer) -> None:
    _seed_book(server, "b1", "Book 1")
    # Add a running pipeline run
    with server._core.conn:
        run_json = json.dumps({"scope": {"book_id": "b1"}})
        server._core.conn.execute(
            "INSERT INTO pipeline_runs (run_id, command_type, scope_type, requested_targets_json, settings_snapshot_json, provider_binding_snapshot_json, context_policy_json, status, run_json, updated_at) VALUES ('r1', 'translate', 'book', '[]', '{}', '{}', '{}', 'running', ?, 'now')",
            (run_json,),
        )
    res = _rpc(server, "PermanentlyDeleteBook", {"book_id": "b1", "confirm_permanent_delete": True})
    assert res["error"]["code"] == "BOOK_BUSY"
    assert res["error"]["category"] == "conflict"


def test_delete_book_success(server: CoreServiceServer) -> None:
    _seed_book(server, "b1", "Book 1")
    rel_path = _seed_chapter_and_page(server, "b1", "c1", "p1")
    abs_path = Path(server._core.storage.absolute_path(rel_path))
    assert abs_path.is_file()

    # Add pipeline run and export history
    with server._core.conn:
        run_json = json.dumps({"run_id": "r1", "scope": {"book_id": "b1"}})
        server._core.conn.execute(
            "INSERT INTO pipeline_runs (run_id, command_type, scope_type, requested_targets_json, settings_snapshot_json, provider_binding_snapshot_json, context_policy_json, status, run_json, updated_at) VALUES ('r1', 'translate', 'book', '[]', '{}', '{}', '{}', 'completed', ?, 'now')",
            (run_json,),
        )
        server._core.conn.execute(
            "INSERT INTO export_history (export_id, book_id, chapter_id, export_type, scope_snapshot_json, status, created_at) VALUES ('e1', 'b1', 'c1', 'zip', '{\"pages\": [\"p1\"]}', 'completed', 'now')"
        )

    res = _rpc(server, "PermanentlyDeleteBook", {"book_id": "b1", "confirm_permanent_delete": True})
    assert res["error"] is None
    assert res["result"] == {"book_id": "b1", "deleted": True}
    assert res["version"] == {"major": 2, "minor": 10}

    # Verify files removed
    assert not abs_path.is_file()
    assert not (server._core.storage.root / "books" / "b1").exists()

    # Verify DB content deleted
    assert server._core.conn.execute("SELECT COUNT(*) FROM books WHERE book_id = 'b1'").fetchone()[0] == 0
    assert server._core.conn.execute("SELECT COUNT(*) FROM chapters WHERE book_id = 'b1'").fetchone()[0] == 0
    assert server._core.conn.execute("SELECT COUNT(*) FROM pages WHERE chapter_id = 'c1'").fetchone()[0] == 0

    # Verify pipeline history retained with book title snapshot
    pr_row = server._core.conn.execute("SELECT run_json FROM pipeline_runs WHERE run_id = 'r1'").fetchone()
    assert pr_row is not None
    pr_json = json.loads(pr_row[0])
    assert pr_json["book_title"] == "Book 1"

    # Verify export history retained with book title snapshot
    exp_row = server._core.conn.execute("SELECT scope_snapshot_json FROM export_history WHERE export_id = 'e1'").fetchone()
    assert exp_row is not None
    exp_json = json.loads(exp_row[0])
    assert exp_json["book_title"] == "Book 1"


# --- PermanentlyDeleteBooks (Batch) Tests ---

def test_delete_books_validation_guards(server: CoreServiceServer) -> None:
    _seed_book(server, "b1", "Book 1")
    _seed_book(server, "b2", "Book 2")
    _seed_book(server, "b3", "Book 3")

    # Limit exceeded (> 20)
    over_20 = [f"b_{i}" for i in range(21)]
    res = _rpc(server, "PermanentlyDeleteBooks", {
        "book_ids": over_20,
        "confirmed_book_ids": over_20,
        "confirm_count": 21,
        "confirm_permanent_delete": True,
    })
    assert res["error"]["code"] == "BOOK_DELETE_BATCH_LIMIT_EXCEEDED"

    # Duplicate IDs
    dups = ["b1", "b2", "b1"]
    res = _rpc(server, "PermanentlyDeleteBooks", {
        "book_ids": dups,
        "confirmed_book_ids": dups,
        "confirm_count": 3,
        "confirm_permanent_delete": True,
    })
    assert res["error"]["code"] == "DUPLICATE_BOOK_ID"

    # Mismatched confirmation
    res = _rpc(server, "PermanentlyDeleteBooks", {
        "book_ids": ["b1", "b2"],
        "confirmed_book_ids": ["b2", "b1"],
        "confirm_count": 2,
        "confirm_permanent_delete": True,
    })
    assert res["error"]["code"] == "INVALID_REQUEST"

    # Mismatched count
    res = _rpc(server, "PermanentlyDeleteBooks", {
        "book_ids": ["b1", "b2"],
        "confirmed_book_ids": ["b1", "b2"],
        "confirm_count": 1,
        "confirm_permanent_delete": True,
    })
    assert res["error"]["code"] == "INVALID_REQUEST"


def test_delete_books_whole_library_protection(server: CoreServiceServer) -> None:
    _seed_book(server, "b1", "Book 1")
    _seed_book(server, "b2", "Book 2")

    # Attempt to delete all books in the library
    res = _rpc(server, "PermanentlyDeleteBooks", {
        "book_ids": ["b1", "b2"],
        "confirmed_book_ids": ["b1", "b2"],
        "confirm_count": 2,
        "confirm_permanent_delete": True,
    })
    assert res["error"]["code"] == "BOOK_DELETE_BATCH_WHOLE_LIBRARY"
    assert res["error"]["category"] == "conflict"
    # Verify no side effects
    assert server._core.conn.execute("SELECT COUNT(*) FROM books").fetchone()[0] == 2


def test_delete_books_preflight_failure(server: CoreServiceServer) -> None:
    _seed_book(server, "b1", "Book 1")
    _seed_book(server, "b2", "Book 2")
    _seed_book(server, "b3", "Book 3")

    # b1 exists, b_missing does not
    res = _rpc(server, "PermanentlyDeleteBooks", {
        "book_ids": ["b1", "b_missing"],
        "confirmed_book_ids": ["b1", "b_missing"],
        "confirm_count": 2,
        "confirm_permanent_delete": True,
    })
    assert res["error"]["code"] == "BOOK_DELETE_BATCH_PREFLIGHT_FAILED"
    assert res["error"]["category"] == "conflict"
    details = res["error"]["details"]
    assert details["phase"] == "preflight"
    assert details["requested_count"] == 2
    assert details["completed_count"] == 0
    assert details["items"] == [
        {"book_id": "b1", "status": "not_started", "error_code": None},
        {"book_id": "b_missing", "status": "not_started", "error_code": "BOOK_NOT_FOUND"},
    ]
    # Zero side effects: b1 still exists!
    assert server._core.conn.execute("SELECT COUNT(*) FROM books WHERE book_id = 'b1'").fetchone()[0] == 1


def test_delete_books_success(server: CoreServiceServer) -> None:
    _seed_book(server, "b1", "Book 1")
    _seed_book(server, "b2", "Book 2")
    _seed_book(server, "b3", "Book 3")  # ensures not whole library
    rel_p1 = _seed_chapter_and_page(server, "b1", "c1", "p1")
    rel_p2 = _seed_chapter_and_page(server, "b2", "c2", "p2")

    res = _rpc(server, "PermanentlyDeleteBooks", {
        "book_ids": ["b1", "b2"],
        "confirmed_book_ids": ["b1", "b2"],
        "confirm_count": 2,
        "confirm_permanent_delete": True,
    })
    assert res["error"] is None
    assert res["result"]["requested_count"] == 2
    assert res["result"]["completed_count"] == 2
    assert res["result"]["items"] == [
        {"book_id": "b1", "status": "deleted", "error_code": None},
        {"book_id": "b2", "status": "deleted", "error_code": None},
    ]

    # Verify both books deleted, b3 remains
    assert [r["book_id"] for r in server._core.conn.execute("SELECT book_id FROM books").fetchall()] == ["b3"]
    assert not Path(server._core.storage.absolute_path(rel_p1)).exists()
    assert not Path(server._core.storage.absolute_path(rel_p2)).exists()


def test_delete_book_busy_with_active_tasks_and_exports(server: CoreServiceServer) -> None:
    _seed_book(server, "b1", "Book 1")
    _seed_book(server, "b2", "Book 2")
    _seed_chapter_and_page(server, "b1", "c1", "p1")

    # 1. Active pipeline_tasks
    with server._core.conn:
        server._core.conn.execute(
            "INSERT INTO pipeline_runs (run_id, command_type, scope_type, requested_targets_json, settings_snapshot_json, provider_binding_snapshot_json, context_policy_json, status, run_json, updated_at) "
            "VALUES ('r_task', 'translate', 'book', '[]', '{}', '{}', '{}', 'completed', '{}', 'now')"
        )
        server._core.conn.execute(
            "INSERT INTO pipeline_run_targets (run_target_id, pipeline_run_id, target_id, target_type, target_order, page_id, snapshot_json) "
            "VALUES ('rt1', 'r_task', 'p1', 'page', 0, 'p1', '{}')"
        )
        server._core.conn.execute(
            "INSERT INTO pipeline_tasks (task_id, pipeline_run_id, run_target_id, target_id, target_type, page_id, status, units_json, step_run_ids_json) "
            "VALUES ('t1', 'r_task', 'rt1', 'p1', 'page', 'p1', 'running', '[]', '[]')"
        )
    res = _rpc(server, "PermanentlyDeleteBook", {"book_id": "b1", "confirm_permanent_delete": True})
    assert res["error"]["code"] == "BOOK_BUSY"
    # Zero side effects
    assert server._core.conn.execute("SELECT COUNT(*) FROM books WHERE book_id = 'b1'").fetchone()[0] == 1

    # Clear active task, test active export via export_runtime.has_active_exports_for_book
    with server._core.conn:
        server._core.conn.execute("UPDATE pipeline_tasks SET status = 'completed' WHERE task_id = 't1'")

    class DummyExports:
        def has_active_exports_for_book(self, bid: str) -> bool:
            return bid == "b1"

    server._exports = DummyExports()
    res = _rpc(server, "PermanentlyDeleteBook", {"book_id": "b1", "confirm_permanent_delete": True})
    assert res["error"]["code"] == "BOOK_BUSY"
    server._exports = None


def test_delete_book_conflict_with_shared_managed_or_cross_project(server: CoreServiceServer) -> None:
    _seed_book(server, "b1", "Book 1")
    _seed_book(server, "b2", "Book 2")
    rel_p1 = _seed_chapter_and_page(server, "b1", "c1", "p1")

    # Scenario a: Shared managed copy in pages table
    with server._core.conn:
        server._core.conn.execute(
            "INSERT INTO chapters (chapter_id, book_id, title, created_at, updated_at) VALUES ('c2', 'b2', 'Ch2', 'now', 'now')"
        )
        server._core.conn.execute(
            "INSERT INTO pages (page_id, chapter_id, managed_original_ref, created_at, updated_at) VALUES ('p2', 'c2', ?, 'now', 'now')",
            (rel_p1,),
        )
    res = _rpc(server, "PermanentlyDeleteBook", {"book_id": "b1", "confirm_permanent_delete": True})
    assert res["error"]["code"] == "BOOK_DELETE_CONFLICT"
    assert server._core.conn.execute("SELECT COUNT(*) FROM books WHERE book_id = 'b1'").fetchone()[0] == 1
    assert Path(server._core.storage.absolute_path(rel_p1)).exists()

    # Clear shared page, test Scenario b: Shared artifact_revisions managed_path
    with server._core.conn:
        server._core.conn.execute("DELETE FROM pages WHERE page_id = 'p2'")
        server._core.conn.execute(
            "INSERT INTO media_artifacts (artifact_id, book_id, chapter_id, page_id, artifact_type, created_at, updated_at) "
            "VALUES ('ma1', 'b1', 'c1', 'p1', 'original', 'now', 'now')"
        )
        server._core.conn.execute(
            "INSERT INTO artifact_revisions (artifact_revision_id, artifact_id, revision_no, managed_path, file_hash, mime_type, size_bytes, created_at) "
            "VALUES ('rev1', 'ma1', 1, 'shared/path.png', 'hash1', 'image/png', 100, 'now')"
        )
        server._core.conn.execute(
            "INSERT INTO pages (page_id, chapter_id, source_order, sort_order, created_at, updated_at) "
            "VALUES ('p2_ext', 'c2', 1, 1, 'now', 'now')"
        )
        server._core.conn.execute(
            "INSERT INTO media_artifacts (artifact_id, book_id, chapter_id, page_id, artifact_type, created_at, updated_at) "
            "VALUES ('ma2', 'b2', 'c2', 'p2_ext', 'original', 'now', 'now')"
        )
        server._core.conn.execute(
            "INSERT INTO artifact_revisions (artifact_revision_id, artifact_id, revision_no, managed_path, file_hash, mime_type, size_bytes, created_at) "
            "VALUES ('rev2', 'ma2', 1, 'shared/path.png', 'hash2', 'image/png', 100, 'now')"
        )
    res = _rpc(server, "PermanentlyDeleteBook", {"book_id": "b1", "confirm_permanent_delete": True})
    assert res["error"]["code"] == "BOOK_DELETE_CONFLICT"

    # Clear shared path, test Scenario c: Cross-project source_artifact_revision_id
    with server._core.conn:
        server._core.conn.execute("UPDATE artifact_revisions SET managed_path = 'rev2/path.png' WHERE artifact_revision_id = 'rev2'")
        server._core.conn.execute(
            "UPDATE artifact_revisions SET source_artifact_revision_id = 'rev1' WHERE artifact_revision_id = 'rev2'"
        )
    res = _rpc(server, "PermanentlyDeleteBook", {"book_id": "b1", "confirm_permanent_delete": True})
    assert res["error"]["code"] == "BOOK_DELETE_CONFLICT"


def test_delete_books_batch_allows_internal_shared_managed_but_rejects_external(server: CoreServiceServer) -> None:
    _seed_book(server, "b1", "Book 1")
    _seed_book(server, "b2", "Book 2")
    _seed_book(server, "b3", "Book 3")
    rel_p1 = _seed_chapter_and_page(server, "b1", "c1", "p1")

    # b1 and b2 share rel_p1
    with server._core.conn:
        server._core.conn.execute(
            "INSERT INTO chapters (chapter_id, book_id, title, created_at, updated_at) VALUES ('c2', 'b2', 'Ch2', 'now', 'now')"
        )
        server._core.conn.execute(
            "INSERT INTO pages (page_id, chapter_id, managed_original_ref, created_at, updated_at) VALUES ('p2', 'c2', ?, 'now', 'now')",
            (rel_p1,),
        )

    # Deleting b1 alone fails with conflict
    res_single = _rpc(server, "PermanentlyDeleteBook", {"book_id": "b1", "confirm_permanent_delete": True})
    assert res_single["error"]["code"] == "BOOK_DELETE_CONFLICT"

    # Deleting [b1, b2] together succeeds because neither is external to the batch!
    res_batch = _rpc(server, "PermanentlyDeleteBooks", {
        "book_ids": ["b1", "b2"],
        "confirmed_book_ids": ["b1", "b2"],
        "confirm_count": 2,
        "confirm_permanent_delete": True,
    })
    assert res_batch["error"] is None
    assert res_batch["result"]["completed_count"] == 2


def test_delete_book_cleans_derived_files_and_catalog(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    core = assemble_production_core(data_dir)
    catalog_db = tmp_path / "derived" / "catalog.db"
    catalog_db.parent.mkdir(parents=True, exist_ok=True)
    derived_root = tmp_path / "derived"
    derived_root.mkdir(parents=True, exist_ok=True)
    initialize_namespace(catalog_db, derived_root)
    catalog = ResourceCatalogStore(catalog_db)
    publisher = RenderPreviewPublisher(derived_root, catalog)
    server = CoreServiceServer(core, render_previews=publisher)

    try:
        _seed_book(server, "b1", "Book 1")
        rel_p1 = _seed_chapter_and_page(server, "b1", "c1", "p1")
        abs_p1 = Path(server._core.storage.absolute_path(rel_p1))

        # Publish a derived preview
        publisher.publish_original(abs_p1, "page-original-p1", ".png")
        entry = catalog.lookup("page-original-p1")
        assert entry is not None
        derived_file = derived_root / entry.rel_path
        assert derived_file.is_file()

        # Permanently delete Book 1
        res = _rpc(server, "PermanentlyDeleteBook", {"book_id": "b1", "confirm_permanent_delete": True})
        assert res["error"] is None

        # Verify derived file removed and catalog entry removed
        assert not derived_file.exists()
        assert catalog.lookup("page-original-p1") is None
    finally:
        catalog.close()
        core.conn.close()


def test_delete_books_whole_library_exact_match_vs_not_found(server: CoreServiceServer) -> None:
    _seed_book(server, "b1", "Book 1")
    _seed_book(server, "b2", "Book 2")

    # Requesting ["b1", "b2", "b_missing"]
    # Total books in DB: 2. Request count: 3.
    # set(book_ids) != all_book_ids, so is_whole_library is False.
    # Preflight should detect b_missing and return BOOK_DELETE_BATCH_PREFLIGHT_FAILED with BOOK_NOT_FOUND.
    res = _rpc(server, "PermanentlyDeleteBooks", {
        "book_ids": ["b1", "b2", "b_missing"],
        "confirmed_book_ids": ["b1", "b2", "b_missing"],
        "confirm_count": 3,
        "confirm_permanent_delete": True,
    })
    assert res["error"]["code"] == "BOOK_DELETE_BATCH_PREFLIGHT_FAILED"
    items = res["error"]["details"]["items"]
    missing_item = next(it for it in items if it["book_id"] == "b_missing")
    assert missing_item["error_code"] == "BOOK_NOT_FOUND"
