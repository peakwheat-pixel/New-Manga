"""FEA-12 CORE: A flow recycle-bin commands (M2-C1 §5.14) — AC1/AC2/AC3.

Semantics under test (ADJ-001 §3 A, C-09 SC-B04/SC-B06):

* soft delete / restore only flip ``books.deleted_at`` — content, protection
  (locks/current/pinned), reading progress, manual edits and source bindings
  are preserved verbatim;
* both faces are per-item atomic: one item's failure is reported per item and
  never rolls back or aborts the others;
* ``ListTrash`` is the additive entry face while ``ListRecycleBinBooks``
  keeps its frozen projection (including the ``page_count`` None channel);
* ``PurgeTrash`` stays unimplemented and fails closed (no sneak delete).
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

from bootstrap.core_service import CoreServiceServer, assemble_production_core  # noqa: E402
from domain.books.entities import Book  # noqa: E402

NOW = "2026-11-05T00:00:00+00:00"


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
    minor: int = 13,
    major: int = 2,
) -> dict:
    response, should_exit = server.dispatch_request(json.dumps({
        "protocol": "new-manga.core",
        "version": {"major": major, "minor": minor},
        "request_id": "trash-test-req",
        "command": command,
        "payload": payload,
    }))
    assert not should_exit
    return response


def _trash_payload(book_ids: list[str], key: str = "idem-1") -> dict:
    return {
        "entries": [{"book_id": book_id} for book_id in book_ids],
        "idempotency_key": key,
    }


def _seed_book(server: CoreServiceServer, book_id: str, title: str = "Book") -> None:
    with server._core.conn:
        server._core.conn.execute(
            "INSERT INTO books (book_id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (book_id, title, NOW, NOW),
        )


def _seed_protected_content(server: CoreServiceServer, book_id: str) -> dict:
    """A book with locks, current/pinned revisions, manual edit, progress and a
    v7 binding — everything A flow must leave untouched."""
    core = server._core
    rel_path = f"books/{book_id}/original/p1.png"
    target = Path(core.storage.root) / rel_path
    target.parent.mkdir(parents=True, exist_ok=True)
    protected_payload = b"PROTECTED-MANAGED-BYTES"
    target.write_bytes(protected_payload)
    conn = core.conn
    with conn:
        conn.execute(
            "INSERT INTO chapters (chapter_id, book_id, title, created_at, updated_at)"
            " VALUES ('c-1', ?, 'Ch', ?, ?)",
            (book_id, NOW, NOW),
        )
        conn.execute(
            "INSERT INTO pages (page_id, chapter_id, managed_original_ref, created_at, updated_at)"
            " VALUES ('p-1', 'c-1', ?, ?, ?)",
            (rel_path, NOW, NOW),
        )
        conn.execute(
            "INSERT INTO regions (region_id, page_id, region_type, geometry_json,"
            " text_json, style_json, region_locked, created_at, updated_at)"
            " VALUES ('rg-1', 'p-1', 'speech', '{}',"
            " '{\"manual_edited\": true, \"translation_locked\": true}', '{}', 1, ?, ?)",
            (NOW, NOW),
        )
        conn.execute(
            "INSERT INTO region_revisions (region_revision_id, region_id, revision_no,"
            " snapshot_json, origin, review_state, is_pinned, created_at)"
            " VALUES ('rr-1', 'rg-1', 1, '{}', 'user', 'confirmed', 1, ?)",
            (NOW,),
        )
        conn.execute(
            "UPDATE regions SET current_revision_id = 'rr-1' WHERE region_id = 'rg-1'"
        )
        conn.execute(
            "INSERT INTO reading_progress (progress_id, book_id, chapter_id, mode,"
            " last_page_id, progress_percent, updated_at)"
            " VALUES ('prog-1', ?, 'c-1', 'original', 'p-1', 0.42, ?)",
            (book_id, NOW),
        )
        # v7 source graph + binding on this page (A flow must not touch it).
        conn.execute(
            "INSERT INTO sources (source_id, source_kind, display_name, created_at, updated_at)"
            " VALUES ('src-1','folder','src',?,?)", (NOW, NOW))
        conn.execute(
            "INSERT INTO source_locations (location_id, source_id, registry_id,"
            " authorization_generation, content_digest, volume_serial, file_id,"
            " size_bytes, observed_at, is_current, created_at)"
            " VALUES ('loc-1','src-1','reg-1',1,?,0,0,10,?,1,?)",
            ("b" * 64, NOW, NOW))
        conn.execute(
            "INSERT INTO source_versions (version_id, source_id, location_id,"
            " content_digest, size_bytes, observed_at, created_at)"
            " VALUES ('ver-1','src-1','loc-1',?,10,?,?)", ("b" * 64, NOW, NOW))
        conn.execute(
            "INSERT INTO source_entries (source_id, version_id, entry_id, locator,"
            " ordinal, stable_sort_key, content_digest_kind, content_digest,"
            " size_bytes, created_at)"
            " VALUES ('src-1','ver-1','entry-1','img/1.png',0,'0','page-identity',?,10,?)",
            ("c" * 64, NOW))
        conn.execute(
            "INSERT INTO page_bindings (binding_id, page_id, project_id, binding_version,"
            " source_id, entry_id, accepted_source_version, status,"
            " authorization_generation, authorized_at, verified_digest, created_at, updated_at)"
            " VALUES ('bind-1', 'p-1', ?, 1, 'src-1', 'entry-1', 'ver-1', 'healthy', 1, ?, ?, ?, ?)",
            (book_id, NOW, "a" * 64, NOW, NOW),
        )
    return {
        "rel_path": rel_path,
        "payload_sha256": hashlib.sha256(protected_payload).hexdigest(),
    }


def _book_row(server: CoreServiceServer, book_id: str) -> dict:
    row = server._core.conn.execute(
        "SELECT * FROM books WHERE book_id = ?", (book_id,)
    ).fetchone()
    return dict(row)


def _shots(server: CoreServiceServer) -> dict[str, list[tuple]]:
    """All tables except ``books`` (whose deleted_at/updated_at may change)."""
    tables = [
        row["name"]
        for row in server._core.conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
            " AND name NOT LIKE 'sqlite_%' AND name != 'books' ORDER BY name"
        ).fetchall()
    ]
    return {
        name: [
            tuple(row)
            for row in server._core.conn.execute(f'SELECT * FROM "{name}"').fetchall()
        ]
        for name in tables
    }


# --- MoveToTrash ------------------------------------------------------


def test_move_to_trash_only_flips_deleted_at(server: CoreServiceServer) -> None:
    """AC1: the shelf loses the book, the bin gains it, and every other row
    (content/protection/current/pin/progress/binding) is byte-identical."""
    _seed_book(server, "b1", "Protected Book")
    protected = _seed_protected_content(server, "b1")
    before_book = _book_row(server, "b1")
    before_other = _shots(server)

    response = _rpc(server, "MoveToTrash", _trash_payload(["b1"]))
    assert response["error"] is None, response["error"]
    assert response["result"] == {"moved": [{"book_id": "b1"}], "skipped": []}
    assert response["version"] == {"major": 2, "minor": 13}

    assert "b1" not in [book.book_id for book in server._core.library.list_books()]
    assert "b1" in [book.book_id for book in server._core.library.list_recycle_bin_books()]
    after_book = _book_row(server, "b1")
    assert after_book["deleted_at"] is not None
    for field in before_book:
        if field in ("deleted_at", "updated_at"):
            continue
        assert after_book[field] == before_book[field], field
    assert _shots(server) == before_other
    managed = Path(server._core.storage.absolute_path(protected["rel_path"]))
    assert hashlib.sha256(managed.read_bytes()).hexdigest() == protected["payload_sha256"]


def test_move_to_trash_is_per_item_atomic(server: CoreServiceServer) -> None:
    """AC1 / C-09: one missing entry is a per-item skip; the rest still move."""
    _seed_book(server, "b1", "One")
    _seed_book(server, "b2", "Two")
    response = _rpc(
        server, "MoveToTrash", _trash_payload(["b1", "missing", "b2"])
    )
    assert response["error"] is None
    assert response["result"]["moved"] == [{"book_id": "b1"}, {"book_id": "b2"}]
    assert response["result"]["skipped"] == [
        {"ref": {"book_id": "missing"}, "reason": "TRASH_ENTRY_NOT_FOUND"}
    ]
    assert server._core.conn.execute(
        "SELECT COUNT(*) FROM books WHERE deleted_at IS NOT NULL"
    ).fetchone()[0] == 2


def test_move_to_trash_replay_is_idempotent(server: CoreServiceServer) -> None:
    _seed_book(server, "b1")
    first = _rpc(server, "MoveToTrash", _trash_payload(["b1"], "same-key"))
    assert first["error"] is None
    second = _rpc(server, "MoveToTrash", _trash_payload(["b1"], "same-key"))
    assert second["error"] is None
    assert second["result"] == {
        "moved": [],
        "skipped": [{"ref": {"book_id": "b1"}, "reason": "TRASH_ENTRY_NOT_FOUND"}],
    }
    # The original soft-delete timestamp was not rewritten by the replay.
    assert _book_row(server, "b1")["deleted_at"] is not None


def test_move_to_trash_closed_shape_and_errors(server: CoreServiceServer) -> None:
    _seed_book(server, "b1")
    for payload in (
        {},
        {"entries": [{"book_id": "b1"}]},
        {"entries": [], "idempotency_key": "k"},
        {"entries": [{"book_id": "b1"}], "idempotency_key": ""},
        {"entries": [{"book_id": "b1"}], "idempotency_key": 5},
        {"entries": [{"book_id": "b1", "extra": 1}], "idempotency_key": "k"},
        {"entries": [{"book_id": ""}], "idempotency_key": "k"},
        {"entries": [{"book_id": "b1"}, {"book_id": "b1"}], "idempotency_key": "k"},
        {"entries": [{"book_id": "b1"}], "idempotency_key": "k", "extra": 1},
    ):
        response = _rpc(server, "MoveToTrash", payload)
        assert response["error"]["code"] == "INVALID_REQUEST", payload
    assert _book_row(server, "b1")["deleted_at"] is None


# --- RestoreFromTrash ------------------------------------------------


def test_restore_from_trash_restores_every_field(server: CoreServiceServer) -> None:
    """AC2: after restore the book is back on the shelf and every protected
    field equals the pre-delete row — no silent unlock / current rewrite."""
    _seed_book(server, "b1", "Protected Book")
    protected = _seed_protected_content(server, "b1")
    before_book = _book_row(server, "b1")
    before_other = _shots(server)

    assert _rpc(server, "MoveToTrash", _trash_payload(["b1"]))["error"] is None
    response = _rpc(server, "RestoreFromTrash", _trash_payload(["b1"], "restore-1"))
    assert response["error"] is None, response["error"]
    assert response["result"] == {"restored": [{"book_id": "b1"}], "conflicts": []}
    assert "b1" in [book.book_id for book in server._core.library.list_books()]
    assert "b1" not in [book.book_id for book in server._core.library.list_recycle_bin_books()]

    after_book = _book_row(server, "b1")
    assert after_book["deleted_at"] is None
    for field in before_book:
        if field in ("deleted_at", "updated_at"):
            continue
        assert after_book[field] == before_book[field], field
    assert _shots(server) == before_other
    managed = Path(server._core.storage.absolute_path(protected["rel_path"]))
    assert hashlib.sha256(managed.read_bytes()).hexdigest() == protected["payload_sha256"]


def test_restore_from_trash_conflicts_are_per_item(server: CoreServiceServer) -> None:
    _seed_book(server, "b1")
    _seed_book(server, "b2")
    assert _rpc(server, "MoveToTrash", _trash_payload(["b1", "b2"]))["error"] is None
    response = _rpc(
        server, "RestoreFromTrash", _trash_payload(["b1", "missing", "b2"], "restore-2")
    )
    assert response["error"] is None
    assert response["result"]["restored"] == [{"book_id": "b1"}, {"book_id": "b2"}]
    assert response["result"]["conflicts"] == [
        {"ref": {"book_id": "missing"}, "reason": "TRASH_ENTRY_NOT_FOUND"}
    ]


def test_restore_of_a_live_book_is_a_conflict_not_a_batch_failure(
    server: CoreServiceServer,
) -> None:
    _seed_book(server, "b1")
    response = _rpc(server, "RestoreFromTrash", _trash_payload(["b1"]))
    assert response["error"] is None
    assert response["result"]["restored"] == []
    assert response["result"]["conflicts"] == [
        {"ref": {"book_id": "b1"}, "reason": "TRASH_ENTRY_NOT_FOUND"}
    ]


# --- ListTrash -------------------------------------------------------


def test_list_trash_empty_entries_and_shape(server: CoreServiceServer) -> None:
    """AC3: an empty bin is ``items: []`` — never an error."""
    response = _rpc(server, "ListTrash", {})
    assert response["error"] is None
    assert response["result"] == {"items": []}

    _seed_book(server, "b1", "Trashed Title")
    assert _rpc(server, "MoveToTrash", _trash_payload(["b1"]))["error"] is None
    items = _rpc(server, "ListTrash", {})["result"]["items"]
    assert len(items) == 1
    assert set(items[0]) == {"bookId", "title", "deletedAt"}
    assert items[0]["bookId"] == "b1"
    assert items[0]["title"] == "Trashed Title"
    assert isinstance(items[0]["deletedAt"], str)


def test_list_trash_pagination(server: CoreServiceServer) -> None:
    for index in range(3):
        _seed_book(server, f"b{index}", f"Book {index}")
        assert _rpc(
            server, "MoveToTrash", _trash_payload([f"b{index}"], f"k{index}")
        )["error"] is None
    first = _rpc(server, "ListTrash", {"limit": 2})
    assert first["error"] is None
    assert len(first["result"]["items"]) == 2
    cursor = first["result"]["nextCursor"]
    assert isinstance(cursor, str)
    second = _rpc(server, "ListTrash", {"limit": 2, "cursor": cursor})
    assert second["error"] is None
    assert len(second["result"]["items"]) == 1
    assert "nextCursor" not in second["result"]
    ids = [item["bookId"] for item in first["result"]["items"]]
    ids += [item["bookId"] for item in second["result"]["items"]]
    assert sorted(ids) == ["b0", "b1", "b2"]


def test_list_trash_validation(server: CoreServiceServer) -> None:
    for payload in (
        {"cursor": "not-a-cursor"},
        {"cursor": ""},
        {"limit": 0},
        {"limit": 201},
        {"limit": "2"},
        {"extra": 1},
    ):
        response = _rpc(server, "ListTrash", payload)
        assert response["error"]["code"] == "INVALID_REQUEST", payload


def test_list_recycle_bin_books_keeps_frozen_projection(server: CoreServiceServer) -> None:
    """AC3: the frozen 2.11 face is unchanged — empty array, no error, and the
    ``page_count`` None channel stays ``None`` instead of a plausible 0."""
    response = _rpc(server, "ListRecycleBinBooks", {}, minor=3)
    assert response["error"] is None
    assert response["result"] == []

    book = server._core.library.create_book(title="No Pages Yet")
    server._core.library.delete_book(book.book_id)
    response = _rpc(server, "ListRecycleBinBooks", {}, minor=3)
    assert response["error"] is None
    assert len(response["result"]) == 1
    summary = response["result"][0]
    assert summary["book_id"] == book.book_id
    assert summary["page_count"] is None
    assert set(summary) == {
        "book_id", "title", "original_title", "is_favorite", "is_archived",
        "page_count", "created_at", "updated_at",
    }


# --- Version / PurgeTrash --------------------------------------------


def test_trash_commands_wire_minor(server: CoreServiceServer) -> None:
    _seed_book(server, "b1")
    for command in ("MoveToTrash", "RestoreFromTrash", "ListTrash", "PurgeTrash"):
        response = _rpc(server, command, {}, minor=12)
        assert response["error"]["code"] == "INVALID_REQUEST", command
        response = _rpc(server, command, {}, major=3)
        assert response["error"]["code"] == "PROTOCOL_VERSION_UNSUPPORTED", command


def test_purge_trash_is_typed_unsupported_with_zero_side_effects(
    server: CoreServiceServer,
) -> None:
    """M2-C1 §5.14: ``PurgeTrash`` is registered but NOT implemented in this
    release; it must fail closed (UNKNOWN_COMMAND) and never perform the
    delete or accept an implicit confirmation."""
    _seed_book(server, "b1")
    assert _rpc(server, "MoveToTrash", _trash_payload(["b1"]))["error"] is None
    response = _rpc(server, "PurgeTrash", {
        "entries": [{"book_id": "b1"}],
        "confirm": True,
        "idempotency_key": "purge-1",
    })
    assert response["error"]["code"] == "UNKNOWN_COMMAND"
    assert response["error"]["category"] == "validation"
    assert response["error"]["retryable"] is False
    assert _book_row(server, "b1")["deleted_at"] is not None
    assert server._core.conn.execute(
        "SELECT COUNT(*) FROM books WHERE book_id = 'b1'"
    ).fetchone()[0] == 1


def test_core_ping_advertises_fea12_capabilities(server: CoreServiceServer) -> None:
    """AC11 (Python side): the three frozen capability names are advertised so
    the Host can probe instead of discovering absence with UNKNOWN_COMMAND."""
    response = _rpc(server, "core.ping", {}, minor=3)
    capabilities = response["result"]["capabilities"]
    for name in (
        "library.delete.preview/1",
        "library.trash.read/1",
        "library.trash.write/1",
    ):
        assert name in capabilities


# --- r1 R-007: Book.restore is the single domain authority ---------------


def test_book_restore_domain_helper_clears_only_the_marker() -> None:
    """R-007: ``Book.restore`` only clears ``deleted_at`` + bumps
    ``updated_at``; the SQLite adapter now reapplies these values through the
    same ``deleted_at IS NOT NULL`` guard, so A flow is genuinely wired to the
    domain rule instead of duplicating it as raw SQL."""
    book = Book(
        book_id="b-domain",
        title="Domain",
        author="Author",
        notes="notes",
        source_url="https://example.invalid/book",
    )
    book.soft_delete()
    # Pin a distinguishable old timestamp so the bump is observable (the
    # millisecond clock could otherwise return the same instant).
    book.updated_at = "2000-01-01T00:00:00.000+00:00"
    before = {
        field: getattr(book, field)
        for field in (
            "book_id", "title", "author", "publisher", "series_title",
            "description", "source_language", "target_language", "source_url",
            "notes", "default_chapter_type", "default_reading_direction",
            "is_favorite", "is_archived", "last_opened_at", "created_at",
        )
    }
    assert book.deleted is True
    book.restore()
    assert book.deleted_at is None
    assert book.deleted is False
    assert book.updated_at != "2000-01-01T00:00:00.000+00:00"
    for field, value in before.items():
        assert getattr(book, field) == value, field
