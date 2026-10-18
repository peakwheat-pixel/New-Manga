"""AC4 (N-003): a translated reader preview must be reclaimable by reference.

The reader used to publish translated previews with ``origin=None``, which the
publisher documents as catalog-only - "the copy can never be reclaimed by
reference".  No ``preview_lifecycle`` row was written, so the derived GC never
considered it and the permanent delete could not find it either (cleanup only
knows the deterministic ``page-original-{page_id}`` key, while
``publish()`` mints a fresh uuid4 key every call).  The preview therefore leaked
one permanent artifact per page per translated read.

This test drives the real reader face and asserts the origin row now exists and
binds the page's exact source revision.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from bootstrap.core_service import CoreServiceServer, assemble_production_core
from infrastructure.resource_channel.catalog_store import (
    ResourceCatalogStore,
    initialize_namespace,
)
from infrastructure.resource_channel.render_preview import RenderPreviewPublisher


def _rpc(server: CoreServiceServer, command: str, payload: object) -> dict:
    response, should_exit = server.dispatch_request(
        json.dumps(
            {
                "protocol": "new-manga.core",
                "version": {"major": 2, "minor": 10},
                "request_id": "ac4-translated-preview",
                "command": command,
                "payload": payload,
            }
        )
    )
    assert not should_exit
    return response


_ORIGINAL_BYTES = b"original bytes"
_TRANSLATED_BYTES = b"translated bytes"


def _seed_translated_page(core, storage) -> tuple[str, str]:
    temp_original = storage.write_temp(_ORIGINAL_BYTES)
    rel_original = storage.new_revision_relative_path(
        "b1", "c1", "original", "p1", ".png"
    )
    storage.publish(temp_original, rel_original)

    temp_translated = storage.write_temp(_TRANSLATED_BYTES)
    rel_translated = storage.new_revision_relative_path(
        "b1", "c1", "translated", "p1", ".png"
    )
    storage.publish(temp_translated, rel_translated)
    return rel_original, rel_translated


def test_translated_reader_preview_registers_a_reclaimable_origin(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    core = assemble_production_core(data_root)

    # M2-DERIVED-GC-2 (R4-A1): a file-backed catalog must first bind its own
    # derived root through the frozen narrow initializer; an unbound store is a
    # typed refusal, never an un-leased write channel.
    derived_root = tmp_path / "derived"
    derived_root.mkdir(parents=True, exist_ok=True)
    catalog_db = tmp_path / "catalog" / "catalog.sqlite"
    catalog_db.parent.mkdir(parents=True, exist_ok=True)
    initialize_namespace(catalog_db, derived_root)
    catalog = ResourceCatalogStore(catalog_db)
    try:
        previews = RenderPreviewPublisher(derived_root, catalog)
        server = CoreServiceServer(
            core,
            render_previews=previews,
            producer_root=data_root.resolve(),
        )

        rel_original, rel_translated = _seed_translated_page(core, core.storage)
        with core.conn:
            core.conn.execute(
                "INSERT INTO books (book_id, title, created_at, updated_at)"
                " VALUES ('b1', 'Book 1', 'now', 'now')"
            )
            core.conn.execute(
                "INSERT INTO chapters (chapter_id, book_id, title, created_at, updated_at)"
                " VALUES ('c1', 'b1', 'Ch', 'now', 'now')"
            )
            # pages carries no translated_* columns: the reader projection
            # derives the translated face entirely from the artifact tables.
            core.conn.execute(
                "INSERT INTO pages (page_id, chapter_id, managed_original_ref,"
                " source_filename, source_hash, source_size_bytes, width, height,"
                " created_at, updated_at)"
                " VALUES ('p1', 'c1', ?, 'p1.png', ?, ?, 10, 10, 'now', 'now')",
                (
                    rel_original,
                    hashlib.sha256(_ORIGINAL_BYTES).hexdigest(),
                    len(_ORIGINAL_BYTES),
                ),
            )
            core.conn.execute(
                "INSERT INTO media_artifacts (artifact_id, book_id, chapter_id,"
                " page_id, artifact_type, current_revision_id, created_at, updated_at)"
                " VALUES ('a1', 'b1', 'c1', 'p1', 'translated', 'ar1', 'now', 'now')"
            )
            core.conn.execute(
                "INSERT INTO artifact_revisions (artifact_revision_id, artifact_id,"
                " revision_no, managed_path, file_hash, mime_type, size_bytes,"
                " integrity_status, created_at)"
                " VALUES ('ar1', 'a1', 1, ?, ?, 'image/png', ?, 'valid', 'now')",
                (
                    rel_translated,
                    hashlib.sha256(_TRANSLATED_BYTES).hexdigest(),
                    len(_TRANSLATED_BYTES),
                ),
            )

        res = _rpc(
            server,
            "GetReaderProjection",
            {
                "chapter_id": "c1",
                "mode": "translated",
                "start_position": "beginning",
            },
        )
        assert res["error"] is None, res["error"]

        page_entry = res["result"]["pages"][0]
        translated = page_entry["translated"]["resource_ref"]
        assert translated is not None, "the translated preview was not published"

        key = translated["resource_id"]
        row = catalog.preview_lifecycle_row(key)
        assert row is not None, (
            "AC4: the translated preview was published without an origin, so it"
            " carries no lifecycle row and can never be reclaimed by reference"
        )
        assert row["artifact_id"] == "a1"
        assert row["artifact_revision_id"] == "ar1", (
            "the origin must bind the page's exact source revision"
        )
    finally:
        catalog.close()
        core.conn.close()
