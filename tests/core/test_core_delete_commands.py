"""FEA-12 CORE: PermanentlyDeleteBook / PermanentlyDeleteBooks wire behavior.

Rewritten for the frozen M2-C1 rev 2.13 confirmation binding (the
``inventory_digest`` / ``inventory_digests`` fields are REQUIRED per §5.11.1a)
and the ADJ-2026-11-05-FEA-12-SCOPE rulings:

* PD-08 (D3): safely splittable shared references no longer block the delete;
  shared physical files survive, out-of-target provenance is detached, and
  only genuinely unsplittable/out-of-target state stays a
  ``BOOK_DELETE_CONFLICT``.
* D1 X1: a book's ``page_bindings`` / ``source_binding_publications`` /
  ``source_revision_lineage`` rows are deleted in the same transaction while
  ``source_sync_plans`` / ``source_operations`` stay; a non-terminal source
  operation is ``BOOK_BUSY`` with zero side effects.
* PD-05/PD-06: explicit ``BEGIN IMMEDIATE`` single transaction; injected
  failure rolls everything back and never starts file cleanup.
* PD-07: ``cleanup_pending`` is explicitly retryable; completed items must
  not be mixed into the retry (``BOOK_NOT_FOUND``).

The "expected behavior change" is registered in doc/tasks/FEA-12-CORE.md:
the old tests sent only ``confirm_permanent_delete`` and expected
"shared references always conflict" — both now contradict the frozen
contracts, so their expectations moved with the ruling, not to make the
implementation pass.
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

from bootstrap.core_service import CoreServiceServer, assemble_production_core
from infrastructure.resource_channel.catalog_store import (
    ResourceCatalogStore,
    initialize_namespace,
)
from infrastructure.resource_channel.render_preview import RenderPreviewPublisher

NOW = "2026-11-05T00:00:00+00:00"
FAKE_DIGEST = "sha256:" + "0" * 64


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


def _preview(server: CoreServiceServer, book_ids: list[str]) -> dict:
    preview = _rpc(
        server, "PreviewPermanentDeleteBooks", {"bookIds": book_ids}, minor=11
    )
    assert preview["error"] is None, preview["error"]
    return preview["result"]


def _single_digest(server: CoreServiceServer, book_id: str) -> str:
    return _preview(server, [book_id])["inventoryDigests"][book_id]


def _batch_digests(server: CoreServiceServer, book_ids: list[str]) -> tuple[str, dict]:
    result = _preview(server, book_ids)
    return result["inventoryDigest"], result["inventoryDigests"]


def _delete_single(server: CoreServiceServer, book_id: str, digest: str) -> dict:
    return _rpc(server, "PermanentlyDeleteBook", {
        "book_id": book_id,
        "confirm_permanent_delete": True,
        "inventory_digest": digest,
    })


def _delete_single_auto(server: CoreServiceServer, book_id: str) -> dict:
    return _delete_single(server, book_id, _single_digest(server, book_id))


def _delete_batch(
    server: CoreServiceServer, book_ids: list[str], digest: str, digests: dict
) -> dict:
    return _rpc(server, "PermanentlyDeleteBooks", {
        "book_ids": book_ids,
        "confirmed_book_ids": book_ids,
        "confirm_count": len(book_ids),
        "confirm_permanent_delete": True,
        "inventory_digest": digest,
        "inventory_digests": digests,
    })


def _delete_batch_auto(server: CoreServiceServer, book_ids: list[str]) -> dict:
    digest, digests = _batch_digests(server, book_ids)
    return _delete_batch(server, book_ids, digest, digests)


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


def _seed_sources_graph(server: CoreServiceServer) -> None:
    """FK-complete v7 source graph (sources→locations→versions→entries)."""
    conn = server._core.conn
    with conn:
        conn.execute(
            "INSERT INTO sources (source_id, source_kind, display_name, created_at, updated_at)"
            " VALUES ('src-1','folder','src',?,?)",
            (NOW, NOW),
        )
        conn.execute(
            "INSERT INTO source_locations (location_id, source_id, registry_id,"
            " authorization_generation, content_digest, volume_serial, file_id, size_bytes,"
            " observed_at, is_current, created_at)"
            " VALUES ('loc-1','src-1','reg-1',1,?,0,0,10,?,1,?)",
            ("b" * 64, NOW, NOW),
        )
        conn.execute(
            "INSERT INTO source_versions (version_id, source_id, location_id, content_digest,"
            " size_bytes, observed_at, created_at)"
            " VALUES ('ver-1','src-1','loc-1',?,10,?,?)",
            ("b" * 64, NOW, NOW),
        )
        conn.execute(
            "INSERT INTO source_entries (source_id, version_id, entry_id, locator, ordinal,"
            " stable_sort_key, content_digest_kind, content_digest, size_bytes, created_at)"
            " VALUES ('src-1','ver-1','entry-1','img/1.png',0,'0','page-identity',?,10,?)",
            ("c" * 64, NOW),
        )


def _seed_plan_and_operation(
    server: CoreServiceServer,
    *,
    operation_id: str = "op-1",
    plan_id: str = "plan-1",
    state: str = "acknowledged",
) -> None:
    """Insert one applied plan + operation (state sets the non-terminal flag)."""
    conn = server._core.conn
    committed_at = NOW if state in ("core-committed", "acknowledged", "recovered") else None
    acknowledged_at = NOW if state in ("acknowledged", "recovered") else None
    error_code = "X" if state == "failed" else None
    with conn:
        conn.execute(
            "INSERT INTO source_sync_plans (plan_id, source_id, kind, state, plan_digest,"
            " body_json, created_at, expires_at, previewed_at, confirmed_at, applied_at)"
            " VALUES (?, 'src-1', 'relink', 'applied', ?, '{}', ?, ?, ?, ?, ?)",
            (plan_id, "d" * 64, NOW, NOW, NOW, NOW, NOW),
        )
        conn.execute(
            "INSERT INTO source_operations (operation_id, plan_id, plan_digest, kind,"
            " request_digest, state, authorization_digest, authorization_json,"
            " host_receipt_id, commit_receipt_json, commit_digest, error_code, retryable,"
            " created_at, updated_at, committed_at, acknowledged_at)"
            " VALUES (?, ?, ?, 'relink', ?, ?, ?, '{}', 'host-1', ?, ?, ?, 0, ?, ?, ?, ?)",
            (
                operation_id,
                plan_id,
                "d" * 64,
                "e" * 64,
                state,
                "f" * 64,
                "{}" if committed_at else None,
                "f" * 64 if committed_at else None,
                error_code,
                NOW,
                NOW,
                committed_at,
                acknowledged_at,
            ),
        )


def _seed_binding_publication_lineage(
    server: CoreServiceServer,
    *,
    book_id: str,
    page_id: str,
    region_id: str,
    revision_id: str,
    binding_id: str = "bind-1",
    operation_id: str = "op-1",
    previous_binding_id: str | None = None,
    relation: str = "added",
    provenance: str = "captured_v7",
    lineage_operation_id: str | None = None,
) -> None:
    conn = server._core.conn
    if previous_binding_id is None and relation != "added":
        raise AssertionError("non-added publications need a previous binding")
    with conn:
        conn.execute(
            "INSERT INTO page_bindings (binding_id, page_id, project_id, binding_version,"
            " source_id, entry_id, accepted_source_version, status,"
            " authorization_generation, authorized_at, verified_digest, created_at, updated_at)"
            " VALUES (?, ?, ?, 1, 'src-1', 'entry-1', 'ver-1', 'healthy', 1, ?, ?, ?, ?)",
            (binding_id, page_id, book_id, NOW, "a" * 64, NOW, NOW),
        )
        conn.execute(
            "INSERT INTO source_binding_publications (binding_id, operation_id,"
            " previous_binding_id, relation, read_gate, opened_at)"
            " VALUES (?, ?, ?, ?, 'open', ?)",
            (binding_id, operation_id, previous_binding_id, relation, NOW),
        )
        conn.execute(
            "INSERT INTO source_revision_lineage (revision_id, region_id, binding_id,"
            " provenance, operation_id, created_at)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            (
                revision_id,
                region_id,
                None if provenance == "legacy_unverified" else binding_id,
                provenance,
                lineage_operation_id,
                NOW,
            ),
        )


def _seed_region(server: CoreServiceServer, *, page_id: str, region_id: str, revision_id: str) -> None:
    conn = server._core.conn
    with conn:
        conn.execute(
            "INSERT INTO regions (region_id, page_id, region_type, geometry_json,"
            " text_json, style_json, created_at, updated_at)"
            " VALUES (?, ?, 'speech', '{}', '{}', '{}', ?, ?)",
            (region_id, page_id, NOW, NOW),
        )
        conn.execute(
            "INSERT INTO region_revisions (region_revision_id, region_id, revision_no,"
            " snapshot_json, origin, review_state, created_at)"
            " VALUES (?, ?, 1, '{}', 'machine', 'unreviewed', ?)",
            (revision_id, region_id, NOW),
        )
        conn.execute(
            "UPDATE regions SET current_revision_id = ? WHERE region_id = ?",
            (revision_id, region_id),
        )


def _table_snapshot(conn) -> dict[str, list[tuple]]:
    """Every user table's rows (rollback comparison helper)."""
    tables = [
        row["name"]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
            " AND name NOT LIKE 'sqlite_%' ORDER BY name"
        ).fetchall()
    ]
    return {
        name: [tuple(row) for row in conn.execute(f'SELECT * FROM "{name}"').fetchall()]
        for name in tables
    }


# --- Version / shape / confirmation binding ---------------------------


def test_delete_book_version_check(server: CoreServiceServer) -> None:
    _seed_book(server, "b1", "Book 1")
    digest = _single_digest(server, "b1")
    res = _rpc(server, "PermanentlyDeleteBook", {
        "book_id": "b1", "confirm_permanent_delete": True, "inventory_digest": digest,
    }, minor=8)
    assert res["error"]["code"] == "INVALID_REQUEST"
    res = _rpc(server, "PermanentlyDeleteBook", {
        "book_id": "b1", "confirm_permanent_delete": True, "inventory_digest": digest,
    }, major=3)
    assert res["error"]["code"] == "PROTOCOL_VERSION_UNSUPPORTED"


def test_delete_book_requires_well_formed_preview_digest(server: CoreServiceServer) -> None:
    """§5.11.1a: the digest is a required, validated closed-shape field.

    A missing/format-bad digest is INVALID_REQUEST *before* any preflight, and
    an old Host that does not send it must fail closed (no soft-delete
    fallback, no side effect).
    """
    _seed_book(server, "b1", "Book 1")
    res = _rpc(server, "PermanentlyDeleteBook", {
        "book_id": "b1", "confirm_permanent_delete": True,
    })
    assert res["error"]["code"] == "INVALID_REQUEST"
    res = _rpc(server, "PermanentlyDeleteBook", {
        "book_id": "b1", "confirm_permanent_delete": True,
        "inventory_digest": "sha256:not-a-digest",
    })
    assert res["error"]["code"] == "INVALID_REQUEST"
    assert server._core.conn.execute(
        "SELECT COUNT(*) FROM books WHERE book_id = 'b1'"
    ).fetchone()[0] == 1


def test_delete_book_invalid_request_shape(server: CoreServiceServer) -> None:
    _seed_book(server, "b1", "Book 1")
    digest = FAKE_DIGEST
    res = _rpc(server, "PermanentlyDeleteBook", {"book_id": "b1"})
    assert res["error"]["code"] == "INVALID_REQUEST"
    res = _rpc(server, "PermanentlyDeleteBook", {
        "book_id": "b1", "confirm_permanent_delete": False, "inventory_digest": digest,
    })
    assert res["error"]["code"] == "INVALID_REQUEST"
    res = _rpc(server, "PermanentlyDeleteBook", {
        "book_id": "b1", "confirm_permanent_delete": True,
        "inventory_digest": digest, "extra": 1,
    })
    assert res["error"]["code"] == "INVALID_REQUEST"
    # §5.11.1: the single command must keep rejecting the batch array shape.
    res = _rpc(server, "PermanentlyDeleteBook", {
        "book_ids": ["b1"], "confirmed_book_ids": ["b1"], "confirm_count": 1,
        "confirm_permanent_delete": True, "inventory_digest": digest,
    })
    assert res["error"]["code"] == "INVALID_REQUEST"


def test_delete_book_stale_preview_after_protection_change(
    server: CoreServiceServer,
) -> None:
    """PD-04: any protection change between preview and confirmation rejects.

    The old digest no longer matches the recomputed inventory; a fresh preview
    then binds the new state and the delete succeeds.
    """
    _seed_book(server, "b1", "Book 1")
    rel_path = _seed_chapter_and_page(server, "b1", "c1", "p1")
    _seed_region(server, page_id="p1", region_id="rg1", revision_id="rr1")
    digest = _single_digest(server, "b1")

    with server._core.conn:
        server._core.conn.execute(
            "UPDATE regions SET region_locked = 1 WHERE region_id = 'rg1'"
        )
    res = _delete_single(server, "b1", digest)
    assert res["error"]["code"] == "BOOK_DELETE_STALE_PREVIEW"
    assert res["error"]["category"] == "conflict"
    assert server._core.conn.execute(
        "SELECT COUNT(*) FROM books WHERE book_id = 'b1'"
    ).fetchone()[0] == 1
    assert Path(server._core.storage.absolute_path(rel_path)).is_file()

    digest = _single_digest(server, "b1")
    res = _delete_single(server, "b1", digest)
    assert res["error"] is None
    assert res["result"] == {"book_id": "b1", "deleted": True}


def test_delete_book_not_found(server: CoreServiceServer) -> None:
    preview = _rpc(server, "PreviewPermanentDeleteBooks", {"bookIds": ["nonexistent"]}, minor=11)
    assert preview["error"]["code"] == "BOOK_NOT_FOUND"
    res = _delete_single(server, "nonexistent", FAKE_DIGEST)
    assert res["error"]["code"] == "BOOK_NOT_FOUND"
    assert res["error"]["category"] == "not_found"


# --- Busy / active operations ----------------------------------------


def test_delete_book_busy(server: CoreServiceServer) -> None:
    _seed_book(server, "b1", "Book 1")
    with server._core.conn:
        run_json = json.dumps({"scope": {"book_id": "b1"}})
        server._core.conn.execute(
            "INSERT INTO pipeline_runs (run_id, command_type, scope_type, requested_targets_json, settings_snapshot_json, provider_binding_snapshot_json, context_policy_json, status, run_json, updated_at) VALUES ('r1', 'translate', 'book', '[]', '{}', '{}', '{}', 'running', ?, 'now')",
            (run_json,),
        )
    result = _preview(server, ["b1"])
    assert result["items"][0]["protection"]["activeRunIds"] == ["r1"]
    digest = result["inventoryDigests"]["b1"]
    res = _delete_single(server, "b1", digest)
    assert res["error"]["code"] == "BOOK_BUSY"
    assert res["error"]["category"] == "conflict"
    assert server._core.conn.execute(
        "SELECT COUNT(*) FROM books WHERE book_id = 'b1'"
    ).fetchone()[0] == 1


def test_delete_book_busy_with_active_tasks_and_exports(server: CoreServiceServer) -> None:
    _seed_book(server, "b1", "Book 1")
    _seed_book(server, "b2", "Book 2")
    _seed_chapter_and_page(server, "b1", "c1", "p1")

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
    res = _delete_single(server, "b1", _single_digest(server, "b1"))
    assert res["error"]["code"] == "BOOK_DELETE_STALE_PREVIEW" or res["error"]["code"] == "BOOK_BUSY"
    # The preview above already saw the running task: confirm must be BOOK_BUSY.
    assert res["error"]["code"] == "BOOK_BUSY"
    assert server._core.conn.execute("SELECT COUNT(*) FROM books WHERE book_id = 'b1'").fetchone()[0] == 1

    with server._core.conn:
        server._core.conn.execute("UPDATE pipeline_tasks SET status = 'completed' WHERE task_id = 't1'")

    class DummyExports:
        def has_active_exports_for_book(self, bid: str) -> bool:
            return bid == "b1"

    server._exports = DummyExports()
    res = _delete_single(server, "b1", _single_digest(server, "b1"))
    assert res["error"]["code"] == "BOOK_BUSY"
    server._exports = None


def test_delete_book_nonterminal_source_operation_busy(
    server: CoreServiceServer,
) -> None:
    """D1 X1: a non-terminal source operation on the book's C-17 subgraph is
    BOOK_BUSY with zero side effects (plans/operations are kept, not deleted)."""
    _seed_book(server, "b1", "Book 1")
    _seed_chapter_and_page(server, "b1", "c1", "p1")
    _seed_region(server, page_id="p1", region_id="rg1", revision_id="rr1")
    _seed_sources_graph(server)
    _seed_plan_and_operation(server, state="core-committed")
    _seed_binding_publication_lineage(
        server, book_id="b1", page_id="p1", region_id="rg1", revision_id="rr1"
    )
    result = _preview(server, ["b1"])
    digest = result["inventoryDigests"]["b1"]
    res = _delete_single(server, "b1", digest)
    assert res["error"]["code"] == "BOOK_BUSY"
    assert server._core.conn.execute(
        "SELECT COUNT(*) FROM source_operations WHERE operation_id = 'op-1'"
    ).fetchone()[0] == 1
    assert server._core.conn.execute(
        "SELECT COUNT(*) FROM page_bindings WHERE binding_id = 'bind-1'"
    ).fetchone()[0] == 1
    assert server._core.conn.execute(
        "SELECT COUNT(*) FROM books WHERE book_id = 'b1'"
    ).fetchone()[0] == 1


# --- Success path ----------------------------------------------------


def test_delete_book_success(server: CoreServiceServer) -> None:
    _seed_book(server, "b1", "Book 1")
    rel_path = _seed_chapter_and_page(server, "b1", "c1", "p1")
    abs_path = Path(server._core.storage.absolute_path(rel_path))
    assert abs_path.is_file()

    with server._core.conn:
        run_json = json.dumps({"run_id": "r1", "scope": {"book_id": "b1"}})
        server._core.conn.execute(
            "INSERT INTO pipeline_runs (run_id, command_type, scope_type, requested_targets_json, settings_snapshot_json, provider_binding_snapshot_json, context_policy_json, status, run_json, updated_at) VALUES ('r1', 'translate', 'book', '[]', '{}', '{}', '{}', 'completed', ?, 'now')",
            (run_json,),
        )
        server._core.conn.execute(
            "INSERT INTO export_history (export_id, book_id, chapter_id, export_type, scope_snapshot_json, status, created_at) VALUES ('e1', 'b1', 'c1', 'zip', '{\"pages\": [\"p1\"]}', 'completed', 'now')"
        )

    res = _delete_single_auto(server, "b1")
    assert res["error"] is None
    assert res["result"] == {"book_id": "b1", "deleted": True}
    assert res["version"] == {"major": 2, "minor": 10}

    assert not abs_path.is_file()
    assert not (server._core.storage.root / "books" / "b1").exists()
    assert server._core.conn.execute("SELECT COUNT(*) FROM books WHERE book_id = 'b1'").fetchone()[0] == 0
    assert server._core.conn.execute("SELECT COUNT(*) FROM chapters WHERE book_id = 'b1'").fetchone()[0] == 0
    assert server._core.conn.execute("SELECT COUNT(*) FROM pages WHERE chapter_id = 'c1'").fetchone()[0] == 0
    pr_row = server._core.conn.execute("SELECT run_json FROM pipeline_runs WHERE run_id = 'r1'").fetchone()
    assert pr_row is not None
    assert json.loads(pr_row[0])["book_title"] == "Book 1"
    exp_row = server._core.conn.execute("SELECT scope_snapshot_json FROM export_history WHERE export_id = 'e1'").fetchone()
    assert exp_row is not None
    assert json.loads(exp_row[0])["book_title"] == "Book 1"


def test_delete_book_v7_v8_fk_probe_case_succeeds(server: CoreServiceServer) -> None:
    """AC9 / D1 X1 + the recorded probe failure: a book carrying a v7
    ``page_bindings`` row and v8 ``source_binding_publications`` /
    ``source_revision_lineage`` rows used to roll back with
    ``IntegrityError: FOREIGN KEY constraint failed``.  It must now commit in
    one transaction, leave ``foreign_key_check`` empty and keep the
    plan/operation audit rows."""
    _seed_book(server, "b1", "Book 1")
    rel_path = _seed_chapter_and_page(server, "b1", "c1", "p1")
    _seed_region(server, page_id="p1", region_id="rg1", revision_id="rr1")
    _seed_sources_graph(server)
    _seed_plan_and_operation(server, state="acknowledged")
    _seed_binding_publication_lineage(
        server, book_id="b1", page_id="p1", region_id="rg1", revision_id="rr1"
    )
    assert [tuple(r) for r in server._core.conn.execute("PRAGMA foreign_key_check")] == []

    res = _delete_single_auto(server, "b1")
    assert res["error"] is None, res["error"]
    assert res["result"] == {"book_id": "b1", "deleted": True}
    assert not Path(server._core.storage.absolute_path(rel_path)).exists()
    assert server._core.conn.execute("SELECT COUNT(*) FROM page_bindings").fetchone()[0] == 0
    assert server._core.conn.execute("SELECT COUNT(*) FROM source_binding_publications").fetchone()[0] == 0
    assert server._core.conn.execute("SELECT COUNT(*) FROM source_revision_lineage").fetchone()[0] == 0
    assert server._core.conn.execute("SELECT COUNT(*) FROM source_sync_plans").fetchone()[0] == 1
    assert server._core.conn.execute("SELECT COUNT(*) FROM source_operations").fetchone()[0] == 1
    assert [tuple(r) for r in server._core.conn.execute("PRAGMA foreign_key_check")] == []


# --- Batch validation / preflight -----------------------------------


def test_delete_books_validation_guards(server: CoreServiceServer) -> None:
    _seed_book(server, "b1", "Book 1")
    _seed_book(server, "b2", "Book 2")
    _seed_book(server, "b3", "Book 3")

    def dataset(ids: list[str], digests: dict | None = None) -> dict:
        return {
            "book_ids": ids,
            "confirmed_book_ids": ids,
            "confirm_count": len(ids),
            "confirm_permanent_delete": True,
            "inventory_digest": FAKE_DIGEST,
            "inventory_digests": digests if digests is not None else {bid: FAKE_DIGEST for bid in ids},
        }

    over_20 = [f"b_{i}" for i in range(21)]
    res = _rpc(server, "PermanentlyDeleteBooks", dataset(over_20))
    assert res["error"]["code"] == "BOOK_DELETE_BATCH_LIMIT_EXCEEDED"

    dups = ["b1", "b2", "b1"]
    res = _rpc(server, "PermanentlyDeleteBooks", dataset(dups))
    assert res["error"]["code"] == "DUPLICATE_BOOK_ID"

    data = dataset(["b1", "b2"])
    data["confirmed_book_ids"] = ["b2", "b1"]
    res = _rpc(server, "PermanentlyDeleteBooks", data)
    assert res["error"]["code"] == "INVALID_REQUEST"

    data = dataset(["b1", "b2"])
    data["confirm_count"] = 1
    res = _rpc(server, "PermanentlyDeleteBooks", data)
    assert res["error"]["code"] == "INVALID_REQUEST"

    # Closed shape: digest map missing / not an object / bad value => INVALID.
    data = dataset(["b1", "b2"])
    data.pop("inventory_digests")
    res = _rpc(server, "PermanentlyDeleteBooks", data)
    assert res["error"]["code"] == "INVALID_REQUEST"
    data = dataset(["b1", "b2"])
    data["inventory_digests"] = {"b1": "nope", "b2": FAKE_DIGEST}
    res = _rpc(server, "PermanentlyDeleteBooks", data)
    assert res["error"]["code"] == "INVALID_REQUEST"


def test_delete_books_whole_library_protection(server: CoreServiceServer) -> None:
    _seed_book(server, "b1", "Book 1")
    _seed_book(server, "b2", "Book 2")
    _seed_book(server, "b3", "Book 3")
    res = _delete_batch_auto(server, ["b1", "b2", "b3"])
    assert res["error"]["code"] == "BOOK_DELETE_BATCH_WHOLE_LIBRARY"
    assert res["error"]["category"] == "conflict"
    assert server._core.conn.execute("SELECT COUNT(*) FROM books").fetchone()[0] == 3


def test_delete_books_preflight_failure(server: CoreServiceServer) -> None:
    _seed_book(server, "b1", "Book 1")
    _seed_book(server, "b2", "Book 2")
    _seed_book(server, "b3", "Book 3")
    res = _rpc(server, "PermanentlyDeleteBooks", {
        "book_ids": ["b1", "b_missing"],
        "confirmed_book_ids": ["b1", "b_missing"],
        "confirm_count": 2,
        "confirm_permanent_delete": True,
        "inventory_digest": FAKE_DIGEST,
        "inventory_digests": {"b1": FAKE_DIGEST, "b_missing": FAKE_DIGEST},
    })
    assert res["error"]["code"] == "BOOK_DELETE_BATCH_PREFLIGHT_FAILED"
    details = res["error"]["details"]
    assert details["phase"] == "preflight"
    assert details["requested_count"] == 2
    assert details["completed_count"] == 0
    assert details["items"] == [
        {"book_id": "b1", "status": "not_started", "error_code": None},
        {"book_id": "b_missing", "status": "not_started", "error_code": "BOOK_NOT_FOUND"},
    ]
    assert server._core.conn.execute("SELECT COUNT(*) FROM books WHERE book_id = 'b1'").fetchone()[0] == 1


def test_delete_books_two_level_digest_binding(server: CoreServiceServer) -> None:
    """PD-02/PD-04: the collection digest binds the ordered id set, the map
    binds each book.  A reorder / wrong map / wrong collection digest must be
    ``BOOK_DELETE_STALE_PREVIEW`` with zero side effects."""
    _seed_book(server, "b1", "Book 1")
    _seed_book(server, "b2", "Book 2")
    _seed_book(server, "b3", "Book 3")
    collection, digests = _batch_digests(server, ["b1", "b2"])

    # Same collection/order but a wrong per-book digest => stale.
    res = _delete_batch(server, ["b1", "b2"], collection, {"b1": FAKE_DIGEST, "b2": digests["b2"]})
    assert res["error"]["code"] == "BOOK_DELETE_STALE_PREVIEW"
    items = res["error"]["details"]["items"]
    assert next(it for it in items if it["book_id"] == "b1")["error_code"] == "BOOK_DELETE_STALE_PREVIEW"
    assert next(it for it in items if it["book_id"] == "b2")["error_code"] is None
    assert server._core.conn.execute("SELECT COUNT(*) FROM books").fetchone()[0] == 3

    # Reordered confirmation changes the bound sequence => collection mismatch.
    res = _rpc(server, "PermanentlyDeleteBooks", {
        "book_ids": ["b2", "b1"],
        "confirmed_book_ids": ["b2", "b1"],
        "confirm_count": 2,
        "confirm_permanent_delete": True,
        "inventory_digest": collection,
        "inventory_digests": {"b2": digests["b2"], "b1": digests["b1"]},
    })
    assert res["error"]["code"] == "BOOK_DELETE_STALE_PREVIEW"
    assert server._core.conn.execute("SELECT COUNT(*) FROM books").fetchone()[0] == 3

    # Key-set mismatch between the map and book_ids => stale, zero side effect.
    res = _delete_batch(server, ["b1", "b2"], collection, {"b1": digests["b1"]})
    assert res["error"]["code"] == "BOOK_DELETE_STALE_PREVIEW"

    res = _delete_batch(server, ["b1", "b2"], collection, digests)
    assert res["error"] is None
    assert res["result"]["requested_count"] == 2
    assert res["result"]["completed_count"] == 2


def test_delete_books_success(server: CoreServiceServer) -> None:
    _seed_book(server, "b1", "Book 1")
    _seed_book(server, "b2", "Book 2")
    _seed_book(server, "b3", "Book 3")
    rel_p1 = _seed_chapter_and_page(server, "b1", "c1", "p1")
    rel_p2 = _seed_chapter_and_page(server, "b2", "c2", "p2")

    res = _delete_batch_auto(server, ["b1", "b2"])
    assert res["error"] is None
    assert res["result"]["requested_count"] == 2
    assert res["result"]["completed_count"] == 2
    assert res["result"]["items"] == [
        {"book_id": "b1", "status": "deleted", "error_code": None},
        {"book_id": "b2", "status": "deleted", "error_code": None},
    ]
    assert [r["book_id"] for r in server._core.conn.execute("SELECT book_id FROM books").fetchall()] == ["b3"]
    assert not Path(server._core.storage.absolute_path(rel_p1)).exists()
    assert not Path(server._core.storage.absolute_path(rel_p2)).exists()


# --- PD-08 shared references ----------------------------------------


def test_delete_book_pd08_shared_managed_split_succeeds(server: CoreServiceServer) -> None:
    """D3/PD-08: a shared managed original is *safely splittable*.

    Deleting b1 removes only b1's rows; the shared physical file and b2's
    binding row survive, and ``foreign_key_check`` stays empty.
    """
    _seed_book(server, "b1", "Book 1")
    _seed_book(server, "b2", "Book 2")
    rel_p1 = _seed_chapter_and_page(server, "b1", "c1", "p1")
    with server._core.conn:
        server._core.conn.execute(
            "INSERT INTO chapters (chapter_id, book_id, title, created_at, updated_at) VALUES ('c2', 'b2', 'Ch2', 'now', 'now')"
        )
        server._core.conn.execute(
            "INSERT INTO pages (page_id, chapter_id, managed_original_ref, created_at, updated_at) VALUES ('p2', 'c2', ?, 'now', 'now')",
            (rel_p1,),
        )
    result = _preview(server, ["b1"])
    item = result["items"][0]
    assert item["contentSummary"]["deletedFiles"] == 0, item["contentSummary"]
    assert item["sharedFileRefs"], item["sharedFileRefs"]
    ref = item["sharedFileRefs"][0]
    assert ref["fileId"].startswith("managed:")
    assert "books/" not in json.dumps(result)
    assert ref["otherProjectCount"] == 1

    res = _delete_single(server, "b1", result["inventoryDigests"]["b1"])
    assert res["error"] is None, res["error"]
    assert server._core.conn.execute("SELECT COUNT(*) FROM books WHERE book_id = 'b1'").fetchone()[0] == 0
    assert server._core.conn.execute("SELECT COUNT(*) FROM books WHERE book_id = 'b2'").fetchone()[0] == 1
    assert server._core.conn.execute("SELECT COUNT(*) FROM pages WHERE page_id = 'p2'").fetchone()[0] == 1
    assert Path(server._core.storage.absolute_path(rel_p1)).is_file(), "shared file was deleted"
    assert [tuple(r) for r in server._core.conn.execute("PRAGMA foreign_key_check")] == []


def test_delete_book_pd08_shared_artifact_split_succeeds(
    server: CoreServiceServer,
) -> None:
    """D3/PD-08: a shared artifact ``managed_path`` splits the same way — the
    other project's artifact row and the shared file survive."""
    _seed_book(server, "b1", "Book 1")
    _seed_book(server, "b2", "Book 2")
    _seed_chapter_and_page(server, "b1", "c1", "p1")
    with server._core.conn:
        server._core.conn.execute(
            "INSERT INTO chapters (chapter_id, book_id, title, created_at, updated_at) VALUES ('c2', 'b2', 'Ch2', 'now', 'now')"
        )
        server._core.conn.execute(
            "INSERT INTO pages (page_id, chapter_id, source_order, sort_order, created_at, updated_at) VALUES ('p2', 'c2', 1, 1, 'now', 'now')"
        )
        for artifact_id, book_id, chapter_id, page_id in (
            ("ma1", "b1", "c1", "p1"),
            ("ma2", "b2", "c2", "p2"),
        ):
            server._core.conn.execute(
                "INSERT INTO media_artifacts (artifact_id, book_id, chapter_id, page_id, artifact_type, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, 'original', 'now', 'now')",
                (artifact_id, book_id, chapter_id, page_id),
            )
        for revision_id, artifact_id in (("rev1", "ma1"), ("rev2", "ma2")):
            server._core.conn.execute(
                "INSERT INTO artifact_revisions (artifact_revision_id, artifact_id, revision_no, managed_path, file_hash, mime_type, size_bytes, created_at) "
                "VALUES (?, ?, 1, 'shared/path.png', 'hash1', 'image/png', 100, 'now')",
                (revision_id, artifact_id),
            )
    storage_root = Path(server._core.storage.root)
    shared_file = storage_root / "shared" / "path.png"
    shared_file.parent.mkdir(parents=True, exist_ok=True)
    shared_file.write_bytes(b"SHARED BYTES")

    result = _preview(server, ["b1"])
    item = result["items"][0]
    # b1's own page original is still its own file; the *shared* artifact
    # path is excluded from the sweep list and never counted.
    assert item["contentSummary"]["deletedFiles"] == 1, item["contentSummary"]
    assert any(
        ref["fileId"].startswith("managed:") for ref in item["sharedFileRefs"]
    ), item["sharedFileRefs"]
    res = _delete_single(server, "b1", result["inventoryDigests"]["b1"])
    assert res["error"] is None, res["error"]
    assert server._core.conn.execute("SELECT COUNT(*) FROM artifact_revisions WHERE artifact_revision_id = 'rev2'").fetchone()[0] == 1
    assert shared_file.read_bytes() == b"SHARED BYTES"
    assert [tuple(r) for r in server._core.conn.execute("PRAGMA foreign_key_check")] == []


def test_delete_book_pd08_cross_project_provenance_detached(
    server: CoreServiceServer,
) -> None:
    """D3/PD-08: an out-of-target revision deriving from a target revision is
    safely splittable — the pointer is detached on the surviving row (the
    page-level purge precedent), the source row/file is preserved."""
    _seed_book(server, "b1", "Book 1")
    _seed_book(server, "b2", "Book 2")
    _seed_chapter_and_page(server, "b1", "c1", "p1")
    with server._core.conn:
        server._core.conn.execute(
            "INSERT INTO chapters (chapter_id, book_id, title, created_at, updated_at) VALUES ('c2', 'b2', 'Ch2', 'now', 'now')"
        )
        server._core.conn.execute(
            "INSERT INTO pages (page_id, chapter_id, source_order, sort_order, created_at, updated_at) VALUES ('p2', 'c2', 1, 1, 'now', 'now')"
        )
        server._core.conn.execute(
            "INSERT INTO media_artifacts (artifact_id, book_id, chapter_id, page_id, artifact_type, created_at, updated_at) "
            "VALUES ('ma1', 'b1', 'c1', 'p1', 'original', 'now', 'now')"
        )
        server._core.conn.execute(
            "INSERT INTO media_artifacts (artifact_id, book_id, chapter_id, page_id, artifact_type, created_at, updated_at) "
            "VALUES ('ma2', 'b2', 'c2', 'p2', 'original', 'now', 'now')"
        )
        server._core.conn.execute(
            "INSERT INTO artifact_revisions (artifact_revision_id, artifact_id, revision_no, managed_path, file_hash, mime_type, size_bytes, created_at) "
            "VALUES ('rev1', 'ma1', 1, 'b1/path.png', 'hash1', 'image/png', 100, 'now')"
        )
        server._core.conn.execute(
            "INSERT INTO artifact_revisions (artifact_revision_id, artifact_id, revision_no, managed_path, file_hash, mime_type, size_bytes, source_artifact_revision_id, created_at) "
            "VALUES ('rev2', 'ma2', 1, 'b2/path.png', 'hash2', 'image/png', 100, 'rev1', 'now')"
        )
    storage_root = Path(server._core.storage.root)
    derived_file = storage_root / "b2" / "path.png"
    derived_file.parent.mkdir(parents=True, exist_ok=True)
    derived_file.write_bytes(b"B2 BYTES")

    res = _delete_single_auto(server, "b1")
    assert res["error"] is None, res["error"]
    row = server._core.conn.execute(
        "SELECT source_artifact_revision_id FROM artifact_revisions WHERE artifact_revision_id = 'rev2'"
    ).fetchone()
    assert row is not None and row["source_artifact_revision_id"] is None
    assert derived_file.read_bytes() == b"B2 BYTES"
    assert [tuple(r) for r in server._core.conn.execute("PRAGMA foreign_key_check")] == []


def test_delete_book_unsafe_source_reference_conflict(server: CoreServiceServer) -> None:
    """PD-08 fail-closed half: an out-of-target publication whose previous
    binding is the book's cannot be detached (schema CHECK keeps
    ``previous_binding_id`` non-null for non-'added' relations), so the delete
    is ``BOOK_DELETE_CONFLICT`` with zero side effects."""
    _seed_book(server, "b1", "Book 1")
    _seed_book(server, "b2", "Book 2")
    _seed_chapter_and_page(server, "b1", "c1", "p1")
    _seed_chapter_and_page(server, "b2", "c2", "p2")
    _seed_region(server, page_id="p1", region_id="rg1", revision_id="rr1")
    _seed_sources_graph(server)
    _seed_plan_and_operation(server, state="acknowledged")
    _seed_binding_publication_lineage(
        server, book_id="b1", page_id="p1", region_id="rg1", revision_id="rr1"
    )
    # b1's binding is the older chain link; b2's publication points at it.
    with server._core.conn:
        server._core.conn.execute(
            "INSERT INTO page_bindings (binding_id, page_id, project_id, binding_version,"
            " source_id, entry_id, accepted_source_version, status,"
            " authorization_generation, authorized_at, verified_digest, created_at, updated_at)"
            " VALUES ('bind-2', 'p2', 'b2', 1, 'src-1', 'entry-1', 'ver-1', 'healthy', 1, ?, ?, ?, ?)",
            (NOW, "a" * 64, NOW, NOW),
        )
        server._core.conn.execute(
            "INSERT INTO source_binding_publications (binding_id, operation_id,"
            " previous_binding_id, relation, read_gate, opened_at)"
            " VALUES ('bind-2', 'op-1', 'bind-1', 'same_content', 'open', ?)",
            (NOW,),
        )
    result = _preview(server, ["b1"])
    # The shared *source entry* is safely splittable and disclosed; it is not
    # the reason the delete fails — the undetachable publication is.
    assert any(
        ref["fileId"] == "entry-1" for ref in result["items"][0]["sharedFileRefs"]
    )
    res = _delete_single(server, "b1", result["inventoryDigests"]["b1"])
    assert res["error"]["code"] == "BOOK_DELETE_CONFLICT"
    assert server._core.conn.execute("SELECT COUNT(*) FROM books WHERE book_id = 'b1'").fetchone()[0] == 1
    assert server._core.conn.execute("SELECT COUNT(*) FROM page_bindings").fetchone()[0] == 2


def test_delete_books_batch_internal_shared_managed_cleaned_once(
    server: CoreServiceServer,
) -> None:
    """PD-08 batch: shared files *inside* the batch are not an external
    reference — the batch deletes both rows and cleans the file once."""
    _seed_book(server, "b1", "Book 1")
    _seed_book(server, "b2", "Book 2")
    _seed_book(server, "b3", "Book 3")
    rel_p1 = _seed_chapter_and_page(server, "b1", "c1", "p1")
    with server._core.conn:
        server._core.conn.execute(
            "INSERT INTO chapters (chapter_id, book_id, title, created_at, updated_at) VALUES ('c2', 'b2', 'Ch2', 'now', 'now')"
        )
        server._core.conn.execute(
            "INSERT INTO pages (page_id, chapter_id, managed_original_ref, created_at, updated_at) VALUES ('p2', 'c2', ?, 'now', 'now')",
            (rel_p1,),
        )
    res = _delete_batch_auto(server, ["b1", "b2"])
    assert res["error"] is None, res["error"]
    assert res["result"]["completed_count"] == 2
    assert not Path(server._core.storage.absolute_path(rel_p1)).exists()
    assert [tuple(r) for r in server._core.conn.execute("PRAGMA foreign_key_check")] == []


# --- Transaction boundary (PD-05/PD-06) ------------------------------


def test_delete_book_uses_explicit_begin_immediate(
    server: CoreServiceServer, monkeypatch,
) -> None:
    """PD-05: the DB phase is one explicit ``BEGIN IMMEDIATE`` transaction."""
    _seed_book(server, "b1", "Book 1")
    _seed_chapter_and_page(server, "b1", "c1", "p1")
    executed: list[str] = []
    real_execute = server._core.conn.execute

    def recording_execute(sql, parameters=()):
        executed.append(sql)
        return real_execute(sql, parameters)

    monkeypatch.setattr(server._core.conn, "execute", recording_execute)
    res = _delete_single_auto(server, "b1")
    assert res["error"] is None, res["error"]
    assert any(statement.strip().upper().startswith("BEGIN IMMEDIATE") for statement in executed)
    assert not server._core.conn.in_transaction


def test_delete_book_transaction_rollback_on_injected_failure(
    server: CoreServiceServer, monkeypatch,
) -> None:
    """PD-06: a failure after the in-transaction deletions have started rolls
    every row back, keeps the files, writes no manifest and never starts the
    file cleanup phase."""
    _seed_book(server, "b1", "Book 1")
    rel_path = _seed_chapter_and_page(server, "b1", "c1", "p1")
    _seed_region(server, page_id="p1", region_id="rg1", revision_id="rr1")
    _seed_sources_graph(server)
    _seed_plan_and_operation(server, state="acknowledged")
    _seed_binding_publication_lineage(
        server, book_id="b1", page_id="p1", region_id="rg1", revision_id="rr1"
    )
    before = _table_snapshot(server._core.conn)
    managed_file = Path(server._core.storage.absolute_path(rel_path))
    managed_bytes = managed_file.read_bytes()

    digest = _single_digest(server, "b1")
    real_execute = server._core.conn.execute

    def failing_execute(sql, parameters=()):
        if sql.strip().upper().startswith("DELETE FROM BOOKS"):
            raise RuntimeError("injected failure before the last DELETE")
        return real_execute(sql, parameters)

    monkeypatch.setattr(server._core.conn, "execute", failing_execute)
    res = _delete_single(server, "b1", digest)
    monkeypatch.setattr(server._core.conn, "execute", real_execute)
    assert res["error"]["code"] == "BOOK_DELETE_FAILED"
    assert res["error"]["category"] == "internal"

    after = _table_snapshot(server._core.conn)
    assert after == before, "the failed transaction left row changes behind"
    assert managed_file.read_bytes() == managed_bytes
    assert server._core.repository.get_cleanup_manifest_data("b1") is None
    assert [tuple(r) for r in server._core.conn.execute("PRAGMA foreign_key_check")] == []
    assert server._core.conn.execute("SELECT COUNT(*) FROM books WHERE book_id = 'b1'").fetchone()[0] == 1


# --- Cleanup: pending, retry (PD-07) ---------------------------------


def test_delete_book_cleanup_pending_retry_cleans_derived_and_manifest(
    tmp_path: Path,
) -> None:
    data_dir = tmp_path / "data_retry"
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
        rel_path = _seed_chapter_and_page(server, "b1", "c1", "p1")
        abs_path = Path(server._core.storage.absolute_path(rel_path))
        publisher.publish_original(abs_path, "page-original-p1", ".png")
        entry = catalog.lookup("page-original-p1")
        assert entry is not None
        derived_file = derived_root / entry.rel_path
        assert derived_file.is_file()

        digest = _single_digest(server, "b1")
        original_lookup = catalog.lookup

        def faulty_lookup(res_id: str):
            raise RuntimeError("Injected catalog lookup failure")

        catalog.lookup = faulty_lookup
        res1 = _delete_single(server, "b1", digest)
        assert res1["error"]["code"] == "BOOK_DELETE_CLEANUP_PENDING"
        assert core.conn.execute("SELECT 1 FROM books WHERE book_id = 'b1'").fetchone() is None
        manifest_data = core.repository.get_cleanup_manifest_data("b1")
        assert manifest_data is not None
        assert "p1" in manifest_data["page_ids"]
        assert derived_file.is_file()

        catalog.lookup = original_lookup
        res2 = _delete_single(server, "b1", digest)
        assert res2["error"] is None
        assert res2["result"]["deleted"] is True
        assert not derived_file.exists()
        assert catalog.lookup("page-original-p1") is None
        assert core.repository.get_cleanup_manifest_data("b1") is None
    finally:
        catalog.close()
        core.conn.close()


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
        publisher.publish_original(abs_p1, "page-original-p1", ".png")
        entry = catalog.lookup("page-original-p1")
        assert entry is not None
        derived_file = derived_root / entry.rel_path
        assert derived_file.is_file()

        res = _delete_single_auto(server, "b1")
        assert res["error"] is None
        assert not derived_file.exists()
        assert catalog.lookup("page-original-p1") is None
    finally:
        catalog.close()
        core.conn.close()


# --- Retained history / detach ---------------------------------------


def test_delete_books_whole_library_exact_match_vs_not_found(server: CoreServiceServer) -> None:
    _seed_book(server, "b1", "Book 1")
    _seed_book(server, "b2", "Book 2")
    res = _rpc(server, "PermanentlyDeleteBooks", {
        "book_ids": ["b1", "b2", "b_missing"],
        "confirmed_book_ids": ["b1", "b2", "b_missing"],
        "confirm_count": 3,
        "confirm_permanent_delete": True,
        "inventory_digest": FAKE_DIGEST,
        "inventory_digests": {"b1": FAKE_DIGEST, "b2": FAKE_DIGEST, "b_missing": FAKE_DIGEST},
    })
    assert res["error"]["code"] == "BOOK_DELETE_BATCH_PREFLIGHT_FAILED"
    items = res["error"]["details"]["items"]
    missing_item = next(it for it in items if it["book_id"] == "b_missing")
    assert missing_item["error_code"] == "BOOK_NOT_FOUND"


def test_delete_book_fail_closed_on_export_runtime_exception(server: CoreServiceServer) -> None:
    _seed_book(server, "b1", "Book 1")
    _seed_chapter_and_page(server, "b1", "c1", "p1")

    class FaultyExportRuntime:
        def has_active_exports_for_book(self, book_id: str) -> bool:
            raise RuntimeError("Injected export runtime failure")

    all_ok, items = server._core.repository.preflight_permanent_delete(
        ["b1"], storage=server._core.storage, export_runtime=FaultyExportRuntime()
    )
    assert not all_ok
    assert items[0]["book_id"] == "b1"
    assert items[0]["error_code"] == "BOOK_BUSY"
    row = server._core.conn.execute("SELECT book_id FROM books WHERE book_id = 'b1'").fetchone()
    assert row is not None


def test_delete_book_output_refs_cleared_and_stage_states_retained(server: CoreServiceServer) -> None:
    conn = server._core.conn
    _seed_book(server, "b1", "Book 1")
    _seed_chapter_and_page(server, "b1", "c1", "p1")

    with conn:
        conn.execute(
            "INSERT INTO pipeline_runs (run_id, command_type, scope_type, requested_targets_json, settings_snapshot_json, provider_binding_snapshot_json, context_policy_json, status, run_json, updated_at)"
            " VALUES ('run1', 'translate', 'page', '[]', '{}', '{}', '{}', 'completed', ?, 'now')",
            (
                '{"scope": {"book_id": "b1", "page_ids": ["p1"]},'
                ' "targets": [{"target_id": "p1", "page_id": "p1", "region_id": "rg1"}],'
                ' "task": {"task_id": "t1", "run_target_id": "rt1"},'
                ' "steps": [{"step_run_id": "sr1", "page_id": "p1"}],'
                ' "book_title": "Book 1",'
                ' "status": "completed"}',
            ),
        )
        conn.execute(
            "INSERT INTO pipeline_run_targets (run_target_id, pipeline_run_id, target_id, target_type, page_id, target_order, snapshot_json)"
            " VALUES ('rt1', 'run1', 'p1', 'page', 'p1', 0, '{}')"
        )
        conn.execute(
            "INSERT INTO pipeline_tasks (task_id, pipeline_run_id, run_target_id, target_id, target_type, page_id, status, units_json, step_run_ids_json)"
            " VALUES ('t1', 'run1', 'rt1', 'p1', 'page', 'p1', 'completed', '[]', '[\"sr1\"]')"
        )
        conn.execute(
            "INSERT INTO step_runs (step_run_id, pipeline_run_id, task_id, target_id, page_id, step_type, unit_id, status, input_refs_json, lock_snapshot_json, output_json)"
            " VALUES ('sr1', 'run1', 't1', 'p1', 'p1', 'step1', 'u1', 'completed', '[]', '{}', '{\"data\": 1}')"
        )
        conn.execute(
            "INSERT INTO step_run_output_refs (step_run_id, output_order, ref_key, value_json)"
            " VALUES ('sr1', 0, 'mask', '{\"locator\": \"media://b1/mask.png\"}')"
        )
        conn.execute(
            "INSERT INTO pipeline_stage_states (target_type, target_id, stage, status, updated_at)"
            " VALUES ('page', 'p1', 'detection', 'completed', 'now')"
        )

    res = _delete_single_auto(server, "b1")
    assert res["error"] is None

    ref_row = conn.execute("SELECT value_json FROM step_run_output_refs WHERE step_run_id = 'sr1'").fetchone()
    assert ref_row is not None
    assert ref_row["value_json"] == "{}"

    stage_rows = conn.execute(
        "SELECT target_id, status FROM pipeline_stage_states"
        " WHERE target_type = 'page' AND stage = 'detection'"
    ).fetchall()
    assert len(stage_rows) == 1, "the stage-state history row was not retained"
    assert stage_rows[0]["status"] == "completed"
    assert stage_rows[0]["target_id"] != "p1"
    assert stage_rows[0]["target_id"].startswith("detached:")

    run_json = json.loads(
        conn.execute("SELECT run_json FROM pipeline_runs WHERE run_id = 'run1'").fetchone()["run_json"]
    )
    locator_keys = {
        "book_id", "chapter_id", "page_id", "page_ids", "ordered_page_ids",
        "last_page_id", "region_id", "region_ids", "target_id", "target_ids",
        "run_target_id", "run_target_ids", "task_id", "task_ids",
        "step_run_id", "step_run_ids",
    }

    def _locators_in(node: object) -> set[str]:
        found: set[str] = set()
        if isinstance(node, dict):
            for key, item in node.items():
                if key in locator_keys:
                    found.add(key)
                found |= _locators_in(item)
        elif isinstance(node, list):
            for item in node:
                found |= _locators_in(item)
        return found

    assert _locators_in(run_json) == set()
    assert run_json.get("book_title") == "Book 1"
    assert run_json.get("status") == "completed"
    assert conn.execute("SELECT 1 FROM books WHERE book_id = 'b1'").fetchone() is None


def test_delete_book_with_multi_target_run_detaches_without_collision(
    server: CoreServiceServer,
) -> None:
    """AC2 / N-001: a run with two targets must not roll the delete back."""
    _seed_book(server, "b1", "Book 1")
    _seed_chapter_and_page(server, "b1", "c1", "p1")
    _seed_chapter_and_page(server, "b1", "c2", "p2")

    with server._core.conn:
        server._core.conn.execute(
            "INSERT INTO pipeline_runs (run_id, command_type, scope_type,"
            " requested_targets_json, settings_snapshot_json,"
            " provider_binding_snapshot_json, context_policy_json, status,"
            " run_json, updated_at)"
            " VALUES ('r_multi', 'translate', 'book', '[]', '{}', '{}', '{}',"
            " 'completed', '{}', 'now')"
        )
        server._core.conn.execute(
            "INSERT INTO pipeline_run_targets (run_target_id, pipeline_run_id,"
            " target_id, target_type, target_order, page_id, snapshot_json)"
            " VALUES ('rt1', 'r_multi', 'p1', 'page', 0, 'p1', '{}')"
        )
        server._core.conn.execute(
            "INSERT INTO pipeline_run_targets (run_target_id, pipeline_run_id,"
            " target_id, target_type, target_order, page_id, snapshot_json)"
            " VALUES ('rt2', 'r_multi', 'p2', 'page', 1, 'p2', '{}')"
        )

    res = _delete_single_auto(server, "b1")
    assert res["error"] is None, res["error"]
    assert res["result"] == {"book_id": "b1", "deleted": True}
    detached = sorted(
        row[0]
        for row in server._core.conn.execute(
            "SELECT target_id FROM pipeline_run_targets WHERE pipeline_run_id = 'r_multi'"
        ).fetchall()
    )
    assert detached == ["detached:rt1", "detached:rt2"]
    assert server._core.conn.execute(
        "SELECT COUNT(*) FROM books WHERE book_id = 'b1'"
    ).fetchone()[0] == 0
