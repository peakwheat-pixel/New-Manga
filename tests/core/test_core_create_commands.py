"""Core 2.8 CreateBook/CreateChapter wire behavior and failure boundaries."""

from __future__ import annotations

import json
from pathlib import Path
import sys

import pytest

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from bootstrap.core_service import CoreServiceServer, assemble_production_core


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
    minor: int = 8,
    major: int = 2,
) -> dict:
    response, should_exit = server.dispatch_request(json.dumps({
        "protocol": "new-manga.core",
        "version": {"major": major, "minor": minor},
        "request_id": "create-test-request",
        "command": command,
        "payload": payload,
    }))
    assert not should_exit
    return response


def _count(
    server: CoreServiceServer,
    table: str,
    where: str = "",
    parameters: tuple[object, ...] = (),
) -> int:
    return server._core.conn.execute(
        f"SELECT COUNT(*) FROM {table} {where}", parameters
    ).fetchone()[0]


def test_create_book_uses_the_list_books_projection(server: CoreServiceServer) -> None:
    created = _rpc(server, "CreateBook", {"title": " A manga "})

    assert created["error"] is None
    assert created["version"] == {"major": 2, "minor": 8}
    assert set(created["result"]) == {
        "book_id", "title", "original_title", "is_favorite", "is_archived",
        "page_count", "created_at", "updated_at",
    }
    assert created["result"]["title"] == " A manga "
    assert created["result"]["original_title"] == ""
    assert created["result"]["is_favorite"] is False
    assert created["result"]["is_archived"] is False
    assert created["result"]["page_count"] is None
    duplicate = _rpc(server, "CreateBook", {"title": " A manga "})
    assert duplicate["error"] is None
    assert duplicate["result"]["title"] == created["result"]["title"]
    assert duplicate["result"]["book_id"] != created["result"]["book_id"]
    listed = _rpc(server, "ListBooks", {}, minor=3)
    assert listed["error"] is None
    assert listed["result"] == [created["result"], duplicate["result"]]


def test_create_chapter_defaults_and_allows_duplicate_titles_and_numbers(
    server: CoreServiceServer,
) -> None:
    book = _rpc(server, "CreateBook", {"title": "A manga"})["result"]
    first = _rpc(server, "CreateChapter", {
        "book_id": book["book_id"], "title": "Chapter", "chapter_number": "1",
    })
    duplicate = _rpc(server, "CreateChapter", {
        "book_id": book["book_id"], "title": "Chapter", "chapter_number": "1",
    })
    omitted_number = _rpc(server, "CreateChapter", {
        "book_id": book["book_id"], "title": "Extra",
    })

    assert first["error"] is None and duplicate["error"] is None
    assert set(first["result"]) == {"chapter_id", "title", "chapter_number", "sort_order"}
    assert first["result"]["chapter_id"] != duplicate["result"]["chapter_id"]
    assert first["result"]["chapter_number"] == duplicate["result"]["chapter_number"] == "1"
    assert [first["result"]["sort_order"], duplicate["result"]["sort_order"]] == [1, 2]
    assert omitted_number["error"] is None
    assert omitted_number["result"]["chapter_number"] == ""
    assert omitted_number["result"]["sort_order"] == 3


@pytest.mark.parametrize(
    ("command", "payload", "details"),
    [
        ("CreateBook", {}, [{"field": "title", "issue": "required"}]),
        ("CreateBook", {"title": ""}, [{"field": "title", "issue": "blank"}]),
        ("CreateBook", {"title": " \u2003 "}, [{"field": "title", "issue": "blank"}]),
        ("CreateBook", {"title": 7}, [{"field": "title", "issue": "wrong_type"}]),
        (
            "CreateBook", {"path": "private/path", "title": "A"},
            [{"field": "$", "issue": "unknown_field"}],
        ),
        ("CreateBook", [], [{"field": "$", "issue": "wrong_type"}]),
        (
            "CreateChapter", {"book_id": "book", "title": "A", "path": "private/path"},
            [{"field": "$", "issue": "unknown_field"}],
        ),
        ("CreateChapter", {"title": "A"}, [{"field": "book_id", "issue": "required"}]),
        (
            "CreateChapter", {"book_id": "", "title": "A"},
            [{"field": "book_id", "issue": "blank"}],
        ),
        (
            "CreateChapter", {"book_id": 7, "title": "A"},
            [{"field": "book_id", "issue": "wrong_type"}],
        ),
        (
            "CreateChapter", {"book_id": "book", "title": " \u2003 "},
            [{"field": "title", "issue": "blank"}],
        ),
        (
            "CreateChapter", {"book_id": "book", "title": "A", "chapter_number": None},
            [{"field": "chapter_number", "issue": "wrong_type"}],
        ),
    ],
)
def test_invalid_create_payload_fails_closed_without_writes(
    server: CoreServiceServer,
    command: str,
    payload: object,
    details: list[dict[str, str]],
) -> None:
    response = _rpc(server, command, payload)

    assert response["result"] is None
    assert response["error"] == {
        "code": "INVALID_REQUEST",
        "category": "validation",
        "retryable": False,
        "details": details,
    }
    assert _count(server, "books") == 0
    assert _count(server, "chapters") == 0
    assert "private/path" not in json.dumps(response)
    assert "message" not in response["error"]


@pytest.mark.parametrize("deleted", [False, True])
def test_create_chapter_rejects_missing_or_deleted_book(
    server: CoreServiceServer, deleted: bool,
) -> None:
    if deleted:
        book = server._core.library.create_book("Deleted")
        server._core.library.delete_book(book.book_id)
        book_id = book.book_id
    else:
        book_id = "missing-book"

    response = _rpc(server, "CreateChapter", {"book_id": book_id, "title": "Chapter"})

    assert response["result"] is None
    assert response["error"] == {
        "code": "TARGET_NOT_FOUND", "category": "not_found", "retryable": False,
    }
    assert _count(server, "chapters") == 0


@pytest.mark.parametrize(
    ("major", "minor", "code"),
    [(2, 7, "INVALID_REQUEST"), (1, 8, "PROTOCOL_VERSION_UNSUPPORTED")],
)
def test_create_commands_require_protocol_2_8_before_side_effects(
    server: CoreServiceServer, major: int, minor: int, code: str,
) -> None:
    response = _rpc(server, "CreateBook", {"title": "A manga"}, major=major, minor=minor)

    assert response["version"] == {"major": 2, "minor": 8}
    assert response["result"] is None
    assert response["error"] == {
        "code": code, "category": "validation", "retryable": False,
    }
    assert _count(server, "books") == 0


@pytest.mark.parametrize("command", ["CreateBook", "CreateChapter"])
def test_primary_key_write_failure_leaves_no_partial_entity(
    server: CoreServiceServer, monkeypatch: pytest.MonkeyPatch, command: str,
) -> None:
    if command == "CreateBook":
        existing = server._core.library.create_book("Existing")
        collision_id = existing.book_id
        payload = {"title": "Attempt"}
        table = "books"
        where = ""
    else:
        book = server._core.library.create_book("Parent")
        existing = server._core.library.create_chapter(book.book_id, "Existing")
        collision_id = existing.chapter_id
        payload = {"book_id": book.book_id, "title": "Attempt"}
        table = "chapters"
        where = "WHERE book_id = ?"
        parameters = (book.book_id,)
    if command == "CreateBook":
        parameters = ()
    monkeypatch.setattr("application.library.service._new_id", lambda: collision_id)

    response = _rpc(server, command, payload)

    assert response["result"] is None
    assert response["error"] == {
        "code": "LIBRARY_WRITE_FAILED", "category": "internal", "retryable": "unknown",
    }
    assert _count(server, table, where, parameters) == 1
    assert "message" not in response["error"]
