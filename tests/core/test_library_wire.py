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


def test_library_wire_missing_book_is_typed_and_tags_replace(tmp_path):
    core, server = _server(tmp_path)
    for command, payload in (
        ("UpdateBookMetadata", {"book_id": "nope", "patch": {"title": "x"}}),
        ("ReorderChapters", {"book_id": "nope", "ordered_ids": ["c"]}),
        ("CreateChapterWithMetadata", {"book_id": "nope", "title": "x"}),
    ):
        response = _rpc(server, command, payload)
        assert response["error"] is not None, command
        assert response["error"]["code"] == "TARGET_NOT_FOUND", (command, response["error"])

    book = core.library.create_book("Tags Book")
    first = core.library.create_tag("t1")
    second = core.library.create_tag("t2")
    updated = _rpc(server, "UpdateBookMetadata", {
        "book_id": book.book_id, "patch": {"tags": [first.tag_id]},
    })
    assert updated["error"] is None
    assert [tag.tag_id for tag in core.library.tags_of_book(book.book_id)] == [first.tag_id]
    replaced = _rpc(server, "UpdateBookMetadata", {
        "book_id": book.book_id, "patch": {"tags": [second.tag_id]},
    })
    assert replaced["error"] is None
    assert [tag.tag_id for tag in core.library.tags_of_book(book.book_id)] == [second.tag_id]
    # R-02 (r2): unknown tag ids are typed and must not half-write text fields.
    half = core.library.create_book("HalfWrite")
    unknown_tag = _rpc(server, "UpdateBookMetadata", {
        "book_id": half.book_id, "patch": {"title": "HalfWrite!", "tags": ["missing-tag"]},
    })
    assert unknown_tag["error"] is not None
    assert unknown_tag["error"]["code"] == "TARGET_NOT_FOUND", unknown_tag["error"]
    assert core.library.get_book(half.book_id).title == "HalfWrite"
    # R-05 (r2): P5 text values are strings; no silent coercion.
    non_string = _rpc(server, "UpdateBookMetadata", {
        "book_id": half.book_id, "patch": {"title": 5},
    })
    assert non_string["error"] is not None
    assert non_string["error"]["code"] == "INVALID_REQUEST", non_string["error"]


def test_library_wire_empty_book_reorder_and_strict_types(tmp_path):
    core, server = _server(tmp_path)
    empty = core.library.create_book("Empty Book")
    # R-13: an empty ordered_ids list is the only encoding of "reorder empty book".
    noop = _rpc(server, "ReorderChapters", {"book_id": empty.book_id, "ordered_ids": []})
    assert noop["error"] is None and noop["result"]["updated"] is True
    created = _rpc(server, "CreateChapterWithMetadata", {"book_id": empty.book_id, "title": "Ch"})
    assert created["error"] is None
    assert created["result"]["sort_order"] == 1
    not_covered = _rpc(server, "ReorderChapters", {"book_id": empty.book_id, "ordered_ids": []})
    assert not_covered["error"] is not None and not_covered["error"]["code"] == "INVALID_REQUEST"
    # R-13: bool/float import_order must not slip through isinstance(int).
    for bad in (True, 1.0, "1"):
        response = _rpc(server, "CreateChapterWithMetadata", {
            "book_id": empty.book_id, "title": "x", "import_order": bad,
        })
        assert response["error"] is not None, bad
        assert response["error"]["code"] == "INVALID_REQUEST", (bad, response["error"])
    # P3 (r2): P7 text fields are strings only (same rule as P5).
    p7_book = core.library.create_book("P7 Book")
    p7_chapter = core.library.create_chapter(p7_book.book_id, "C")
    for key in ("kind", "number", "title", "subtitle", "notes"):
        non_string = _rpc(server, "UpdateChapterMetadata", {
            "chapter_id": p7_chapter.chapter_id, "patch": {key: 5},
        })
        assert non_string["error"] is not None, key
        assert non_string["error"]["code"] == "INVALID_REQUEST", (key, non_string["error"])


# MAINT-2-C1-BATCH-1 AC6 (C1-6 / L-L1-4, LIB-1 r3 R3-001): SQLite INTEGER is signed
# 64-bit. Out-of-range values used to reach sqlite3 and surface as `UNKNOWN/internal`;
# P8 additionally left a half-created chapter behind. The guards must be TYPED
# (`INVALID_REQUEST`/validation) and ATOMIC (no row written).
SQLITE_MAX = 2**63 - 1


def test_chapter_metadata_rejects_64_bit_overflow_as_typed_and_atomic(tmp_path):
    core, server = _server(tmp_path)
    book = core.library.create_book("Bounds Book")
    chapter = core.library.create_chapter(book.book_id, "C1")

    # P7 (custom_rank): out of range -> typed validation error, stored value untouched.
    overflow_rank = _rpc(server, "UpdateChapterMetadata", {
        "chapter_id": chapter.chapter_id, "patch": {"custom_rank": SQLITE_MAX + 1},
    })
    assert overflow_rank["error"] is not None
    assert overflow_rank["error"]["code"] == "INVALID_REQUEST", overflow_rank["error"]
    assert overflow_rank["error"]["category"] == "validation", overflow_rank["error"]
    assert core.library.get_chapter(chapter.chapter_id).custom_rank is None

    # The representable ceiling itself is still accepted (no over-rejection).
    at_ceiling = _rpc(server, "UpdateChapterMetadata", {
        "chapter_id": chapter.chapter_id, "patch": {"custom_rank": SQLITE_MAX},
    })
    assert at_ceiling["error"] is None, at_ceiling["error"]
    assert core.library.get_chapter(chapter.chapter_id).custom_rank == SQLITE_MAX

    # P8 (import_order): out of range -> typed error AND no chapter row left behind.
    before = len(core.library.list_chapters(book.book_id))
    overflow_order = _rpc(server, "CreateChapterWithMetadata", {
        "book_id": book.book_id, "title": "Overflow", "import_order": SQLITE_MAX + 1,
    })
    assert overflow_order["error"] is not None
    assert overflow_order["error"]["code"] == "INVALID_REQUEST", overflow_order["error"]
    assert len(core.library.list_chapters(book.book_id)) == before, "partial chapter row was written"

    # R3-001 cascade: the top of the import range is accepted, but the NEXT append must be a
    # typed failure instead of an UNKNOWN/internal that poisons the book forever.
    accepted = _rpc(server, "CreateChapterWithMetadata", {
        "book_id": book.book_id, "title": "Ceiling", "import_order": SQLITE_MAX - 1,
    })
    assert accepted["error"] is None, accepted["error"]
    before = len(core.library.list_chapters(book.book_id))
    poisoned = _rpc(server, "CreateChapterWithMetadata", {"book_id": book.book_id, "title": "Next"})
    assert poisoned["error"] is not None
    assert poisoned["error"]["code"] == "INVALID_REQUEST", poisoned["error"]
    assert poisoned["error"]["code"] != "UNKNOWN"
    assert len(core.library.list_chapters(book.book_id)) == before