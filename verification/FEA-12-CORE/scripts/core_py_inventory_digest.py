"""FEA-12-CORE (shard A) evidence probe: deletion-preview inventory digest.

ADR: C-04b §2.1 / M2-C1 §5.13 freeze the canonical digest form; this probe
*materialises the implementation's golden vector*: it builds a fully isolated
Core (workspace temp root, real v1..v8 migrations), calls the real wire preview
command, and compares the Core-computed digest with an independent
recomputation from the frozen canonical rule.

No real user data, no fixed drive path, no roaming/local app-data variable and
no recycle-bin API is involved; every path is derived from this file's
location and removed afterwards.

Run: python verification/FEA-12-CORE/scripts/core_py_inventory_digest.py
"""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
WORKSPACE = REPO.parent / (REPO.name + ".workspace")
WORK_ROOT = WORKSPACE / "temp" / "FEA-12-CORE" / "evidence-digest"
EVIDENCE = REPO / "verification" / "FEA-12-CORE" / "evidence" / "core-py-inventory-digest-golden.json"

sys.path.insert(0, str(REPO / "src"))

from bootstrap.core_service import CoreServiceServer, assemble_production_core  # noqa: E402
from infrastructure.resource_channel.catalog_store import (  # noqa: E402
    ResourceCatalogStore,
    initialize_namespace,
)
from infrastructure.resource_channel.render_preview import RenderPreviewPublisher  # noqa: E402

NOW = "2026-11-05T00:00:00+00:00"
PREFIX = "sha256:"
#: r1 R-001: derived preview bytes counted into deletedFiles/deletedBytes.
DERIVED_BYTES = b"derived-golden"
DERIVED_REL_PATH = "previews/derived-golden.png"


def _canonical_payload(book_id: str, item: dict) -> dict:
    """The frozen C-04b §2.1 canonical object (keys are sorted at dump time)."""
    return {
        "bookId": book_id,
        "lockCount": item["protection"]["lockCount"],
        "currentRevisionId": item["protection"]["currentRevisionId"],
        "pinnedRevisionIds": sorted(item["protection"]["pinnedRevisionIds"]),
        "activeRunIds": sorted(item["protection"]["activeRunIds"]),
        "draftPageCount": item["protection"]["draftPageCount"],
        "manualRegionCount": item["protection"]["manualRegionCount"],
        "chapters": item["contentSummary"]["chapters"],
        "pages": item["contentSummary"]["pages"],
        "artifacts": item["contentSummary"]["artifacts"],
        "deletedFiles": item["contentSummary"]["deletedFiles"],
        "deletedBytes": item["contentSummary"]["deletedBytes"],
        "sharedFileRefs": [
            {
                "fileId": ref["fileId"],
                "otherProjectCount": ref["otherProjectCount"],
            }
            for ref in sorted(item["sharedFileRefs"], key=lambda ref: ref["fileId"])
        ],
    }


def _digest(payload: dict) -> str:
    canonical = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )
    return PREFIX + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _collection_digest(book_ids: list[str], digests: dict[str, str]) -> str:
    joined = "".join(digests[book_id][len(PREFIX):].lower() for book_id in book_ids)
    return PREFIX + hashlib.sha256(joined.encode("ascii")).hexdigest()


def _seed(core, storage_root: Path) -> None:
    conn = core.conn

    def add_book(book_id: str, title: str) -> None:
        conn.execute(
            "INSERT INTO books (book_id, title, created_at, updated_at)"
            " VALUES (?, ?, ?, ?)",
            (book_id, title, NOW, NOW),
        )

    def add_page(book_id: str, chapter_id: str, page_id: str, payload: bytes) -> str:
        relative = f"books/{book_id}/chapters/{chapter_id}/original/{page_id}.png"
        target = storage_root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)
        conn.execute(
            "INSERT INTO chapters (chapter_id, book_id, title, created_at, updated_at)"
            " VALUES (?, ?, 'Ch', ?, ?)",
            (chapter_id, book_id, NOW, NOW),
        )
        conn.execute(
            "INSERT INTO pages (page_id, chapter_id, managed_original_ref,"
            " created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (page_id, chapter_id, relative, NOW, NOW),
        )
        return relative

    with conn:
        add_book("book-golden", "Golden Book")
        add_book("book-empty", "Empty Book")
        add_page("book-golden", "chapter-golden", "page-golden", b"golden-page-bytes")
        conn.execute(
            "INSERT INTO regions (region_id, page_id, region_type, geometry_json,"
            " text_json, style_json, created_at, updated_at)"
            " VALUES ('region-golden', 'page-golden', 'speech', '{}',"
            " '{\"manual_edited\": true, \"translation_locked\": true}',"
            " '{}', ?, ?)",
            (NOW, NOW),
        )
        conn.execute(
            "INSERT INTO region_revisions (region_revision_id, region_id,"
            " revision_no, snapshot_json, origin, review_state, is_pinned,"
            " created_at) VALUES ('rev-golden', 'region-golden', 1, '{}',"
            " 'user', 'confirmed', 1, ?)",
            (NOW,),
        )
        conn.execute(
            "UPDATE regions SET current_revision_id = 'rev-golden'"
            " WHERE region_id = 'region-golden'"
        )
        conn.execute(
            "INSERT INTO media_artifacts (artifact_id, book_id, chapter_id,"
            " page_id, artifact_type, created_at, updated_at)"
            " VALUES ('artifact-golden', 'book-golden', 'chapter-golden',"
            " 'page-golden', 'translated', ?, ?)",
            (NOW, NOW),
        )
        artifact_relative = "books/book-golden/artifacts/translated.png"
        artifact_file = storage_root / artifact_relative
        artifact_file.parent.mkdir(parents=True, exist_ok=True)
        artifact_file.write_bytes(b"golden-artifact")
        conn.execute(
            "INSERT INTO artifact_revisions (artifact_revision_id, artifact_id,"
            " revision_no, managed_path, file_hash, mime_type, size_bytes,"
            " is_pinned, created_at)"
            " VALUES ('artifact-rev-golden', 'artifact-golden', 1, ?, ?,"
            " 'image/png', 15, 1, ?)",
            (artifact_relative, hashlib.sha256(b"golden-artifact").hexdigest(), NOW),
        )
    core.drafts.open_draft(
        "golden-session", "page-golden", "region-golden",
        base_revision_id="rev-golden", page_binding_version=0,
    )


def _preview(server: CoreServiceServer, book_ids: list[str]) -> dict:
    raw, should_exit = server.dispatch_request(json.dumps({
        "protocol": "new-manga.core",
        "version": {"major": 2, "minor": 11},
        "request_id": "fea12-core-golden",
        "command": "PreviewPermanentDeleteBooks",
        "payload": {"bookIds": book_ids},
    }))
    assert not should_exit
    assert raw["error"] is None, raw["error"]
    return raw["result"]


def main() -> int:
    shutil.rmtree(WORK_ROOT, ignore_errors=True)
    WORK_ROOT.mkdir(parents=True, exist_ok=True)
    core = assemble_production_core(WORK_ROOT / "data")
    # r1 R-001: a real derived-preview publisher so the disclosure must count
    # the catalog preview / page-original files the cleanup removes.
    derived_root = WORK_ROOT / "derived"
    derived_root.mkdir(parents=True, exist_ok=True)
    catalog_db = WORK_ROOT / "catalog" / "catalog.db"
    catalog_db.parent.mkdir(parents=True, exist_ok=True)
    initialize_namespace(catalog_db, derived_root)
    catalog = ResourceCatalogStore(catalog_db)
    publisher = RenderPreviewPublisher(derived_root, catalog)
    server = CoreServiceServer(core, render_previews=publisher)
    storage_root = Path(core.storage.root)
    evidence: dict = {
        "capability": "library.delete.preview/1",
        "command": "PreviewPermanentDeleteBooks",
        "contract": "doc/plan/FEA-C04b_DELETE_PROTOCOL_DRAFT.md §2.1; M2-C1 §5.13",
        "canonical_form": (
            "json.dumps(payload, sort_keys=True, separators=(',', ':'),"
            " ensure_ascii=False); sha256 hex lowercase; collection ="
            " sha256(concat(per-book hex, request order))"
        ),
        "vectors": [],
        "all_match": True,
    }
    try:
        _seed(core, storage_root)
        # r1 R-001: one existing derived page-original preview file that the
        # cleanup phase removes and the PD-01 disclosure must therefore count.
        derived_file = derived_root / DERIVED_REL_PATH
        derived_file.parent.mkdir(parents=True, exist_ok=True)
        derived_file.write_bytes(DERIVED_BYTES)
        catalog.upsert(
            "page-original-page-golden", "derived-read-only", DERIVED_REL_PATH
        )
        single = _preview(server, ["book-golden"])
        single_item = single["items"][0]
        expected_single = _digest(_canonical_payload("book-golden", single_item))
        evidence["derived_disclosure"] = {
            "derived_rel_path_kind": "catalog preview/page-original under derived root",
            "derived_bytes": len(DERIVED_BYTES),
            "preview_deletedFiles": single_item["contentSummary"]["deletedFiles"],
            "preview_deletedBytes": single_item["contentSummary"]["deletedBytes"],
            "expected_deletedFiles": 3,  # page original + artifact path + derived preview
            "expected_deletedBytes": (
                len(b"golden-page-bytes")
                + len(b"golden-artifact")
                + len(DERIVED_BYTES)
            ),
        }
        evidence["all_match"] &= (
            single_item["contentSummary"]["deletedFiles"]
            == evidence["derived_disclosure"]["expected_deletedFiles"]
            and single_item["contentSummary"]["deletedBytes"]
            == evidence["derived_disclosure"]["expected_deletedBytes"]
        )
        evidence["vectors"].append({
            "name": "single-book-full-protection",
            "request": {"bookIds": ["book-golden"]},
            "preview_item": single_item,
            "canonical_payload": _canonical_payload("book-golden", single_item),
            "expected_inventoryDigest": expected_single,
            "actual_inventoryDigest": single["inventoryDigests"]["book-golden"],
            "match": expected_single == single["inventoryDigests"]["book-golden"],
        })
        evidence["all_match"] &= (
            expected_single == single["inventoryDigests"]["book-golden"]
        )

        ordered = _preview(server, ["book-golden", "book-empty"])
        per_book = {}
        for item in ordered["items"]:
            per_book[item["bookId"]] = _digest(
                _canonical_payload(item["bookId"], item)
            )
        expected_collection = _collection_digest(
            ["book-golden", "book-empty"], per_book
        )
        evidence["vectors"].append({
            "name": "ordered-collection-two-books",
            "request": {"bookIds": ["book-golden", "book-empty"]},
            "expected_inventoryDigests": per_book,
            "actual_inventoryDigests": ordered["inventoryDigests"],
            "expected_inventoryDigest": expected_collection,
            "actual_inventoryDigest": ordered["inventoryDigest"],
            "match": (
                expected_collection == ordered["inventoryDigest"]
                and per_book == ordered["inventoryDigests"]
            ),
        })
        evidence["all_match"] &= (
            expected_collection == ordered["inventoryDigest"]
            and per_book == ordered["inventoryDigests"]
        )

        # Reordering the request must change the collection digest only.
        reordered = _preview(server, ["book-empty", "book-golden"])
        evidence["order_sensitivity"] = {
            "forward": ordered["inventoryDigest"],
            "reordered": reordered["inventoryDigest"],
            "per_book_digests_stable": (
                per_book == reordered["inventoryDigests"]
            ),
            "collection_differs": (
                ordered["inventoryDigest"] != reordered["inventoryDigest"]
            ),
        }
        evidence["all_match"] &= (
            per_book == reordered["inventoryDigests"]
            and ordered["inventoryDigest"] != reordered["inventoryDigest"]
        )
        evidence["computedAt"] = ordered["computedAt"]
    finally:
        catalog.close()
        core.conn.close()
        shutil.rmtree(WORK_ROOT, ignore_errors=True)

    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps({"all_match": evidence["all_match"], "evidence": str(EVIDENCE)}))
    return 0 if evidence["all_match"] else 1


if __name__ == "__main__":
    sys.exit(main())
