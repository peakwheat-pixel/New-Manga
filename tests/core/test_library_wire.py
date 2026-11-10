"""FEA-14-LIB-1: Core wire face for book/chapter metadata (PREQ LIB P5-P8)."""

from __future__ import annotations

import io
import json
from pathlib import Path
import sys

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from bootstrap.core_service import (  # noqa: E402
    PROTOCOL_MAJOR, PROTOCOL_MINOR, PROTOCOL_NAME, CoreServiceServer, assemble_production_core,
)
from infrastructure.resource_channel.catalog_store import (  # noqa: E402
    ResourceCatalogStore, initialize_namespace,
)
from infrastructure.resource_channel.render_preview import RenderPreviewPublisher  # noqa: E402


def _rpc(server: CoreServiceServer, command: str, payload: dict) -> dict:
    raw = json.dumps({
        "protocol": PROTOCOL_NAME, "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
        "request_id": "lib-wire", "command": command, "payload": payload,
    })
    return server.dispatch_request(raw)[0]


def _server(tmp_path: Path):
    core = assemble_production_core(tmp_path / "data")
    derived_root = tmp_path / "derived"
    catalog_db = tmp_path / "catalog" / "catalog.sqlite"
    derived_root.mkdir(parents=True, exist_ok=True)
    catalog_db.parent.mkdir(parents=True, exist_ok=True)
    initialize_namespace(catalog_db, derived_root)
    server = CoreServiceServer(
        core, stdout=io.StringIO(),
        render_previews=RenderPreviewPublisher(derived_root, ResourceCatalogStore(catalog_db)),
    )
    return core, server


def test_library_metadata_wire_roundtrip(tmp_path):
    core, server = _server(tmp_path)
    book = core.library.create_book("Wire Book")
    updated = _rpc(server, "UpdateBookMetadata", {"book_id": book.book_id, "patch": {"title": "Renamed"}})
    assert updated["error"] is None and updated["result"]["updated"] is True
    assert core.library.get_book(book.book_id).title == "Renamed"

    chapter = core.library.create_chapter(book.book_id, "Ch 1")
    patched = _rpc(server, "UpdateChapterMetadata", {
        "chapter_id": chapter.chapter_id,
        "patch": {"kind": "webtoon", "number": "02", "custom_rank": 5},
    })
    assert patched["error"] is None
    reloaded = core.library.get_chapter(chapter.chapter_id)
    assert reloaded.chapter_type.value == "webtoon"
    assert reloaded.chapter_number == "02" and reloaded.custom_rank == 5


def test_library_wire_reorder_and_create_and_errors(tmp_path):
    core, server = _server(tmp_path)
    book = core.library.create_book("Wire Book")
    first = core.library.create_chapter(book.book_id, "Ch 1")
    second = core.library.create_chapter(book.book_id, "Ch 2")

    reordered = _rpc(server, "ReorderChapters", {
        "book_id": book.book_id, "ordered_ids": [second.chapter_id, first.chapter_id],
    })
    assert reordered["error"] is None and reordered["result"]["updated"] is True
    assert [c.chapter_id for c in core.library.list_chapters(book.book_id)] == [
        second.chapter_id, first.chapter_id,
    ]

    partial = _rpc(server, "ReorderChapters", {"book_id": book.book_id, "ordered_ids": [first.chapter_id]})
    assert partial["error"] is not None and partial["error"]["code"] == "INVALID_REQUEST"

    created = _rpc(server, "CreateChapterWithMetadata", {
        "book_id": book.book_id, "title": "Extra", "kind": "webtoon", "number": "99", "import_order": 9,
    })
    assert created["error"] is None
    assert created["result"]["kind"] == "webtoon"
    assert created["result"]["title"] == "Extra"

    missing = _rpc(server, "UpdateChapterMetadata", {"chapter_id": "nope", "patch": {"notes": "x"}})
    assert missing["error"] is not None and missing["error"]["code"] == "TARGET_NOT_FOUND"
