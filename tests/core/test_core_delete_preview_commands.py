"""FEA-12 CORE: read-only deletion preview (M2-C1 §5.13) — AC4/AC5/AC7.

The preview is the Core-authoritative PD-01 disclosure: it must be strictly
read-only (PD-03), report the frozen ``DeletePreviewItem`` shape with the three
mandatory PD-01 fields, compute the canonical inventory digest (C-04b §2.1)
and never leak paths, plaintext or exception stacks.
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

from application.library.service import (  # noqa: E402
    canonical_inventory_payload,
    collection_inventory_digest,
)
from bootstrap.core_service import CoreServiceServer, assemble_production_core  # noqa: E402

NOW = "2026-11-05T00:00:00+00:00"
SERVER = "server"


@pytest.fixture
def server(tmp_path: Path):
    core = assemble_production_core(tmp_path / "data")
    try:
        yield CoreServiceServer(core)
    finally:
        core.conn.close()


def _rpc(
    server: CoreServiceServer, command: str, payload: object, *, minor: int = 11, major: int = 2
) -> dict:
    response, should_exit = server.dispatch_request(json.dumps({
        "protocol": "new-manga.core",
        "version": {"major": major, "minor": minor},
        "request_id": "preview-test-req",
        "command": command,
        "payload": payload,
    }))
    assert not should_exit
    return response


def _preview(server: CoreServiceServer, book_ids: list[str]) -> dict:
    response = _rpc(server, "PreviewPermanentDeleteBooks", {"bookIds": book_ids})
    assert response["error"] is None, response["error"]
    return response["result"]


def _seed_book(server: CoreServiceServer, book_id: str, title: str = "Book") -> None:
    with server._core.conn:
        server._core.conn.execute(
            "INSERT INTO books (book_id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (book_id, title, NOW, NOW),
        )


def _seed_page_with_region(
    server: CoreServiceServer,
    *,
    book_id: str,
    chapter_id: str,
    page_id: str,
    region_id: str,
    revision_id: str,
    text_json: str = "{}",
    region_locked: int = 0,
    translation_locked: int = 0,
    inpaint_locked: int = 0,
    managed_bytes: bytes = b"original-bytes",
) -> str:
    storage = server._core.storage
    rel_path = f"books/{book_id}/chapters/{chapter_id}/original/{page_id}.png"
    target = Path(storage.root) / rel_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(managed_bytes)
    conn = server._core.conn
    with conn:
        conn.execute(
            "INSERT INTO chapters (chapter_id, book_id, title, created_at, updated_at)"
            " VALUES (?, ?, 'Ch', ?, ?)",
            (chapter_id, book_id, NOW, NOW),
        )
        conn.execute(
            "INSERT INTO pages (page_id, chapter_id, managed_original_ref, created_at, updated_at)"
            " VALUES (?, ?, ?, ?, ?)",
            (page_id, chapter_id, rel_path, NOW, NOW),
        )
        conn.execute(
            "INSERT INTO regions (region_id, page_id, region_type, geometry_json,"
            " text_json, style_json, region_locked, translation_locked,"
            " inpaint_locked, created_at, updated_at)"
            " VALUES (?, ?, 'speech', '{}', ?, '{}', ?, ?, ?, ?, ?)",
            (region_id, page_id, text_json, region_locked, translation_locked,
             inpaint_locked, NOW, NOW),
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
    return rel_path


def _table_rows(conn) -> dict[str, list[tuple]]:
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


def _tree_fingerprint(root: Path) -> dict[str, tuple]:
    fingerprint = {}
    for path in sorted(root.rglob("*")):
        if path.is_file():
            stat = path.stat()
            fingerprint[str(path.relative_to(root))] = (
                hashlib.sha256(path.read_bytes()).hexdigest(),
                stat.st_mtime_ns,
            )
    return fingerprint


# --- Shape / validation ----------------------------------------------


def test_preview_closed_shape_and_validation(server: CoreServiceServer) -> None:
    _seed_book(server, "b1")
    for payload in (
        {},
        {"bookIds": []},
        {"bookIds": ["b1"], "extra": 1},
        {"bookIds": [1]},
        {"bookIds": [""]},
        {"bookIds": ["b1", "b1"]},
        {"bookIds": [f"b{i}" for i in range(21)]},
        {"book_ids": ["b1"]},
    ):
        response = _rpc(server, "PreviewPermanentDeleteBooks", payload)
        assert response["error"]["code"] == "INVALID_REQUEST", payload
        assert response["error"]["category"] == "validation"
    response = _rpc(server, "PreviewPermanentDeleteBooks", {"bookIds": ["missing"]})
    assert response["error"]["code"] == "BOOK_NOT_FOUND"
    assert response["error"]["retryable"] is False


def test_preview_version_wire(server: CoreServiceServer) -> None:
    _seed_book(server, "b1")
    response = _rpc(server, "PreviewPermanentDeleteBooks", {"bookIds": ["b1"]})
    assert response["version"] == {"major": 2, "minor": 11}
    response = _rpc(server, "PreviewPermanentDeleteBooks", {"bookIds": ["b1"]}, minor=10)
    assert response["error"]["code"] == "INVALID_REQUEST"
    response = _rpc(server, "PreviewPermanentDeleteBooks", {"bookIds": ["b1"]}, minor=13)
    assert response["error"]["code"] == "INVALID_REQUEST"
    response = _rpc(server, "PreviewPermanentDeleteBooks", {"bookIds": ["b1"]}, major=3)
    assert response["error"]["code"] == "PROTOCOL_VERSION_UNSUPPORTED"


# --- PD-01 disclosure --------------------------------------------------


def test_preview_reports_full_pd01_disclosure(server: CoreServiceServer) -> None:
    """AC4/AC7: lock union, manual edits, current/pinned revisions, draft
    pages, content counts and the file summary are all authoritative."""
    core = server._core
    _seed_book(server, "b1", "Disclosed")
    rel_a = _seed_page_with_region(
        server, book_id="b1", chapter_id="c1", page_id="p1", region_id="rg1",
        revision_id="rr1", region_locked=1,
        text_json='{"translation_locked": true, "manual_edited": true}',
        managed_bytes=b"a" * 10,
    )
    # Second region only locks through text_json (double-projection union).
    with core.conn:
        core.conn.execute(
            "INSERT INTO regions (region_id, page_id, region_type, geometry_json,"
            " text_json, style_json, created_at, updated_at)"
            " VALUES ('rg2', 'p1', 'speech', '{}', ?, '{}', ?, ?)",
            ('{"translation_locked": true}', NOW, NOW),
        )
        core.conn.execute(
            "INSERT INTO region_revisions (region_revision_id, region_id, revision_no,"
            " snapshot_json, origin, review_state, is_pinned, created_at)"
            " VALUES ('rr2', 'rg2', 1, '{}', 'user', 'confirmed', 1, ?)",
            (NOW,),
        )
        core.conn.execute(
            "UPDATE regions SET current_revision_id = 'rr2' WHERE region_id = 'rg2'"
        )
        # A pinned artifact revision is protected content too.
        core.conn.execute(
            "INSERT INTO media_artifacts (artifact_id, book_id, chapter_id, page_id,"
            " artifact_type, created_at, updated_at)"
            " VALUES ('ma1', 'b1', 'c1', 'p1', 'translated', ?, ?)",
            (NOW, NOW),
        )
        artifact_rel = "b1/artifacts/translated.png"
        core.conn.execute(
            "INSERT INTO artifact_revisions (artifact_revision_id, artifact_id,"
            " revision_no, managed_path, file_hash, mime_type, size_bytes, is_pinned,"
            " created_at) VALUES ('ar1', 'ma1', 1, ?, ?, 'image/png', 7, 1, ?)",
            (artifact_rel, "9" * 64, NOW),
        )
    artifact_file = Path(core.storage.root) / artifact_rel
    artifact_file.parent.mkdir(parents=True, exist_ok=True)
    artifact_file.write_bytes(b"artifac")
    # reading progress + an active C-13 draft over the page.
    with core.conn:
        core.conn.execute(
            "INSERT INTO reading_progress (progress_id, book_id, chapter_id, mode,"
            " last_page_id, progress_percent, updated_at)"
            " VALUES ('prog1', 'b1', 'c1', 'original', 'p1', 0.5, ?)",
            (NOW,),
        )
    core.drafts.open_draft(
        "session-1", "p1", "rg1", base_revision_id="rr1", page_binding_version=0
    )

    item = _preview(server, ["b1"])["items"][0]
    assert item["bookId"] == "b1"
    assert item["title"] == "Disclosed"
    protection = item["protection"]
    assert protection["lockCount"] == 2  # rg1 flag + rg2 text_json union
    assert protection["manualRegionCount"] == 1
    assert protection["currentRevisionId"] in {"rr1", "rr2"}
    assert protection["pinnedRevisionIds"] == ["ar1", "rr2"]
    assert protection["activeRunIds"] == []
    assert protection["draftPageCount"] == 1
    content = item["contentSummary"]
    assert content["chapters"] == 1
    assert content["pages"] == 1
    assert content["artifacts"] == 1
    # One page original (10 bytes) + one artifact file (7 bytes).
    assert content["deletedFiles"] == 2
    assert content["deletedBytes"] == 17
    assert item["sharedFileRefs"] == []


def test_preview_current_revision_uses_lineage_visibility(
    server: CoreServiceServer,
) -> None:
    """Lead ruling: the disclosure follows the released FEA-11 read semantics —
    a region hidden by a ``changed`` publication edge is not "visible", so it
    cannot become the reported current revision."""
    core = server._core
    _seed_book(server, "b1")
    _seed_page_with_region(
        server, book_id="b1", chapter_id="c1", page_id="p1", region_id="rg1",
        revision_id="rr1",
    )
    # FK-complete source graph for a v7 binding chain.
    with core.conn:
        core.conn.execute(
            "INSERT INTO sources (source_id, source_kind, display_name, created_at, updated_at)"
            " VALUES ('src-1','folder','src',?,?)", (NOW, NOW))
        core.conn.execute(
            "INSERT INTO source_locations (location_id, source_id, registry_id,"
            " authorization_generation, content_digest, volume_serial, file_id,"
            " size_bytes, observed_at, is_current, created_at)"
            " VALUES ('loc-1','src-1','reg-1',1,?,0,0,10,?,1,?)",
            ("b" * 64, NOW, NOW))
        core.conn.execute(
            "INSERT INTO source_versions (version_id, source_id, location_id,"
            " content_digest, size_bytes, observed_at, created_at)"
            " VALUES ('ver-1','src-1','loc-1',?,10,?,?)", ("b" * 64, NOW, NOW))
        core.conn.execute(
            "INSERT INTO source_entries (source_id, version_id, entry_id, locator,"
            " ordinal, stable_sort_key, content_digest_kind, content_digest,"
            " size_bytes, created_at)"
            " VALUES ('src-1','ver-1','entry-1','img/1.png',0,'0','page-identity',?,10,?)",
            ("c" * 64, NOW))
        core.conn.execute(
            "INSERT INTO source_sync_plans (plan_id, source_id, kind, state,"
            " plan_digest, body_json, created_at, expires_at, previewed_at,"
            " confirmed_at, applied_at)"
            " VALUES ('plan-1','src-1','relink','applied',?, '{}', ?, ?, ?, ?, ?)",
            ("d" * 64, NOW, NOW, NOW, NOW, NOW))
        core.conn.execute(
            "INSERT INTO source_operations (operation_id, plan_id, plan_digest, kind,"
            " request_digest, state, authorization_digest, authorization_json,"
            " host_receipt_id, commit_receipt_json, commit_digest, retryable,"
            " created_at, updated_at, committed_at, acknowledged_at)"
            " VALUES ('op-1','plan-1',?, 'relink', ?, 'acknowledged', ?, '{}',"
            " 'host-1', '{}', ?, 0, ?, ?, ?, ?)",
            ("d" * 64, "e" * 64, "f" * 64, "f" * 64, NOW, NOW, NOW, NOW))
        for binding_id, status in (("bind-old", "superseded"), ("bind-new", "healthy")):
            core.conn.execute(
                "INSERT INTO page_bindings (binding_id, page_id, project_id,"
                " binding_version, source_id, entry_id, accepted_source_version,"
                " status, authorization_generation, authorized_at, verified_digest,"
                " created_at, updated_at)"
                " VALUES (?, 'p1', 'b1', ?, 'src-1', 'entry-1', 'ver-1', ?, 1, ?, ?, ?, ?)",
                (binding_id, 1 if binding_id == "bind-old" else 2, status, NOW,
                 "a" * 64, NOW, NOW))
        core.conn.execute(
            "INSERT INTO source_binding_publications (binding_id, operation_id,"
            " previous_binding_id, relation, read_gate, opened_at)"
            " VALUES ('bind-new', 'op-1', 'bind-old', 'changed', 'open', ?)",
            (NOW,))
        core.conn.execute(
            "INSERT INTO source_revision_lineage (revision_id, region_id, binding_id,"
            " provenance, created_at)"
            " VALUES ('rr1', 'rg1', 'bind-old', 'captured_v7', ?)",
            (NOW,),
        )
    item = _preview(server, ["b1"])["items"][0]
    assert item["protection"]["currentRevisionId"] is None


# --- Read-only guarantee (PD-03) --------------------------------------


def test_preview_is_read_only(server: CoreServiceServer) -> None:
    core = server._core
    _seed_book(server, "b1")
    _seed_page_with_region(
        server, book_id="b1", chapter_id="c1", page_id="p1", region_id="rg1",
        revision_id="rr1", managed_bytes=b"read-only-bytes",
    )
    before_rows = _table_rows(core.conn)
    before_tree = _tree_fingerprint(Path(core.storage.root))
    before_mtime = (Path(core.data_root) / "library.db").stat().st_mtime_ns

    _preview(server, ["b1"])

    assert _table_rows(core.conn) == before_rows
    assert _tree_fingerprint(Path(core.storage.root)) == before_tree
    assert (Path(core.data_root) / "library.db").stat().st_mtime_ns == before_mtime


def test_preview_has_no_paths_plaintext_or_stacks(server: CoreServiceServer) -> None:
    core = server._core
    _seed_book(server, "b1", "Secret Title Is Allowed")
    rel_path = _seed_page_with_region(
        server, book_id="b1", chapter_id="c1", page_id="p1", region_id="rg1",
        revision_id="rr1",
    )
    payload = json.dumps(_preview(server, ["b1"]), ensure_ascii=False)
    assert "books/" not in payload
    assert rel_path not in payload
    assert str(core.storage.root) not in payload
    assert "Traceback" not in payload
    assert "sqlite" not in payload.lower()
    assert "Secret Title Is Allowed" in payload  # display-only title is allowed


# --- Digest (C-04b §2.1 golden vector) --------------------------------


def _expected_digest(item: dict) -> str:
    canonical = canonical_inventory_payload({
        "book_id": item["bookId"],
        "lock_count": item["protection"]["lockCount"],
        "current_revision_id": item["protection"]["currentRevisionId"],
        "pinned_revision_ids": item["protection"]["pinnedRevisionIds"],
        "active_run_ids": item["protection"]["activeRunIds"],
        "draft_page_count": item["protection"]["draftPageCount"],
        "manual_region_count": item["protection"]["manualRegionCount"],
        "chapters": item["contentSummary"]["chapters"],
        "pages": item["contentSummary"]["pages"],
        "artifacts": item["contentSummary"]["artifacts"],
        "deleted_files": item["contentSummary"]["deletedFiles"],
        "deleted_bytes": item["contentSummary"]["deletedBytes"],
        "shared_file_refs": item["sharedFileRefs"],
    })
    return "sha256:" + hashlib.sha256(
        json.dumps(
            canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")
    ).hexdigest()


def test_preview_digest_golden_vector_and_title_independence(
    server: CoreServiceServer,
) -> None:
    core = server._core
    _seed_book(server, "b1", "Original Title")
    _seed_page_with_region(
        server, book_id="b1", chapter_id="c1", page_id="p1", region_id="rg1",
        revision_id="rr1", managed_bytes=b"golden",
    )
    result = _preview(server, ["b1"])
    item = result["items"][0]
    expected = _expected_digest(item)
    assert result["inventoryDigests"]["b1"] == expected
    # Collection digest = sha256 of the concatenated per-book hex, in order.
    assert result["inventoryDigest"] == collection_inventory_digest(
        ["b1"], {"b1": expected}
    )
    # ``title`` is display-only (C-04b §2.1): renaming must not invalidate it.
    with core.conn:
        core.conn.execute("UPDATE books SET title = 'Renamed' WHERE book_id = 'b1'")
    renamed = _preview(server, ["b1"])
    assert renamed["inventoryDigests"]["b1"] == expected
    assert renamed["items"][0]["title"] == "Renamed"


def test_preview_collection_digest_binds_request_order(
    server: CoreServiceServer,
) -> None:
    _seed_book(server, "b1")
    _seed_book(server, "b2")
    first = _preview(server, ["b1", "b2"])
    second = _preview(server, ["b2", "b1"])
    assert first["inventoryDigests"] == second["inventoryDigests"]
    assert first["inventoryDigest"] != second["inventoryDigest"]
    assert first["inventoryDigest"] == collection_inventory_digest(
        ["b1", "b2"], first["inventoryDigests"]
    )
    assert second["inventoryDigest"] == collection_inventory_digest(
        ["b2", "b1"], second["inventoryDigests"]
    )


# --- Unavailable / zero side effects ---------------------------------


def test_preview_inventory_unavailable_is_typed(server: CoreServiceServer, monkeypatch) -> None:
    _seed_book(server, "b1")

    def explode(*args, **kwargs):
        raise RuntimeError("injected inventory failure")

    monkeypatch.setattr(server._core.repository, "book_delete_inventory", explode)
    response = _rpc(server, "PreviewPermanentDeleteBooks", {"bookIds": ["b1"]})
    assert response["error"] == {
        "code": "BOOK_DELETE_PROTECTION_INVENTORY_UNAVAILABLE",
        "category": "unavailable",
        "retryable": True,
    }
    assert server._core.conn.execute("SELECT COUNT(*) FROM books").fetchone()[0] == 1
