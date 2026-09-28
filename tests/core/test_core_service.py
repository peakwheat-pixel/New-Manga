"""Tests for bootstrap.core_service (M2-IPC1 AC1 & AC4).

Exercises both pure-function envelope dispatch and the end-to-end real subprocess
round-trip over stdio JSON-lines.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import time

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

import pytest

from bootstrap.core_service import (
    E_PROTOCOL_VERSION_UNSUPPORTED,
    E_UNKNOWN_COMMAND,
    PROTOCOL_MAJOR,
    PROTOCOL_NAME,
    CoreServiceServer,
    assemble_production_core,
    make_error_envelope,
)
from domain.books.entities import Book, Chapter
from domain.pages.entities import Page
from infrastructure.sqlite.library import SqliteLibraryRepository


def test_make_error_envelope_structure() -> None:
    envelope = make_error_envelope(
        code="TEST_CODE",
        category="validation",
        message="A safe short message",
        retryable=False,
    )
    assert envelope["code"] == "TEST_CODE"
    assert envelope["category"] == "validation"
    assert envelope["message"] == "A safe short message"
    assert envelope["retryable"] is False
    assert "details" not in envelope

    detailed = make_error_envelope(
        code="ERR_DETAILED",
        category="conflict",
        message="msg",
        retryable=True,
        details=[{"field": "foo", "issue": "bar"}],
    )
    assert detailed["details"] == [{"field": "foo", "issue": "bar"}]


def test_dispatch_pure_functions(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    core = assemble_production_core(data_root)
    try:
        server = CoreServiceServer(core)

        # 1. Invalid JSON
        res, exit_flag = server.dispatch_request("not-a-json")
        assert not exit_flag
        assert res["result"] is None
        assert res["error"]["code"] == "INVALID_JSON"

        # 2. Unsupported protocol name
        bad_proto_req = json.dumps({
            "protocol": "other.protocol",
            "version": {"major": 1, "minor": 0},
            "request_id": "req-1",
            "command": "core.ping",
            "payload": {},
        })
        res, exit_flag = server.dispatch_request(bad_proto_req)
        assert not exit_flag
        assert res["request_id"] == "req-1"
        assert res["result"] is None
        assert res["error"]["code"] == E_PROTOCOL_VERSION_UNSUPPORTED

        # 3. Unsupported protocol version (major != 1)
        bad_ver_req = json.dumps({
            "protocol": PROTOCOL_NAME,
            "version": {"major": 2, "minor": 0},
            "request_id": "req-2",
            "command": "core.ping",
            "payload": {},
        })
        res, exit_flag = server.dispatch_request(bad_ver_req)
        assert not exit_flag
        assert res["request_id"] == "req-2"
        assert res["result"] is None
        assert res["error"]["code"] == E_PROTOCOL_VERSION_UNSUPPORTED
        assert res["error"]["category"] == "validation"
        assert res["error"]["retryable"] is False

        # 4. Unknown command
        unknown_cmd_req = json.dumps({
            "protocol": PROTOCOL_NAME,
            "version": {"major": 1, "minor": 0},
            "request_id": "req-3",
            "command": "CreateBook",
            "payload": {},
        })
        res, exit_flag = server.dispatch_request(unknown_cmd_req)
        assert not exit_flag
        assert res["request_id"] == "req-3"
        assert res["result"] is None
        assert res["error"]["code"] == E_UNKNOWN_COMMAND

        # 5. core.ping
        ping_req = json.dumps({
            "protocol": PROTOCOL_NAME,
            "version": {"major": 1, "minor": 0},
            "request_id": "req-4",
            "command": "core.ping",
            "payload": {},
        })
        res, exit_flag = server.dispatch_request(ping_req)
        assert not exit_flag
        assert res["request_id"] == "req-4"
        assert res["error"] is None
        assert res["result"]["status"] == "ready"
        assert res["result"]["protocol_version"] == {"major": 1, "minor": 0}
        assert res["result"]["capabilities"] == ["library.list_books"]

        # 6. ListBooks on empty repository
        list_req = json.dumps({
            "protocol": PROTOCOL_NAME,
            "version": {"major": 1, "minor": 0},
            "request_id": "req-5",
            "command": "ListBooks",
            "payload": {},
        })
        res, exit_flag = server.dispatch_request(list_req)
        assert not exit_flag
        assert res["request_id"] == "req-5"
        assert res["error"] is None
        assert res["result"] == []

        # 7. core.shutdown
        shutdown_req = json.dumps({
            "protocol": PROTOCOL_NAME,
            "version": {"major": 1, "minor": 0},
            "request_id": "req-6",
            "command": "core.shutdown",
            "payload": {},
        })
        res, exit_flag = server.dispatch_request(shutdown_req)
        assert exit_flag is True
        assert res["request_id"] == "req-6"
        assert res["error"] is None
        assert res["result"] == {"status": "stopped"}
    finally:
        core.conn.close()


def test_real_subprocess_e2e_round_trip(tmp_path: Path) -> None:
    """AC4 discriminating test: spawns real subprocess and tests request/response."""
    data_root = tmp_path / "data_e2e"
    data_root.mkdir(parents=True, exist_ok=True)

    repo_root = Path(__file__).resolve().parents[2]
    src_root = repo_root / "src"

    env = os.environ.copy()
    env["NEWMANGA_DATA_ROOT"] = str(data_root)
    env["PYTHONPATH"] = str(src_root)
    env["PYTHONDONTWRITEBYTECODE"] = "1"

    proc = subprocess.Popen(
        [sys.executable, "-m", "bootstrap.core_service"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        env=env,
        cwd=str(repo_root),
    )

    def send_and_recv(cmd_obj: dict) -> dict:
        line = json.dumps(cmd_obj) + "\n"
        proc.stdin.write(line)  # type: ignore[union-attr]
        proc.stdin.flush()  # type: ignore[union-attr]
        resp_line = proc.stdout.readline()  # type: ignore[union-attr]
        return json.loads(resp_line)

    try:
        # 1. ping
        ping_resp = send_and_recv({
            "protocol": PROTOCOL_NAME,
            "version": {"major": 1, "minor": 0},
            "request_id": "p-1",
            "command": "core.ping",
            "payload": {},
        })
        assert ping_resp["request_id"] == "p-1"
        assert ping_resp["error"] is None
        assert ping_resp["result"]["status"] == "ready"
        assert ping_resp["result"]["protocol_version"] == {"major": 1, "minor": 0}
        assert ping_resp["result"]["capabilities"] == ["library.list_books"]

        # 2. ListBooks when empty
        empty_resp = send_and_recv({
            "protocol": PROTOCOL_NAME,
            "version": {"major": 1, "minor": 0},
            "request_id": "l-1",
            "command": "ListBooks",
            "payload": {},
        })
        assert empty_resp["request_id"] == "l-1"
        assert empty_resp["error"] is None
        assert empty_resp["result"] == []

        # 3. Seed 1 book with 1 chapter and 1 page directly into SQLite
        # Database file was created by core_service on startup
        db_path = data_root / "library.db"
        assert db_path.exists()

        import sqlite3
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        repo = SqliteLibraryRepository(conn)

        book = Book(
            book_id="book-test-1",
            title="测试书目",
            original_title="Test Book Original",
            source_language="ja",
            target_language="zh",
            is_favorite=True,
            is_archived=False,
        )
        repo.add_book(book)

        chapter = Chapter(
            chapter_id="chap-test-1",
            book_id="book-test-1",
            title="第1话",
        )
        repo.add_chapter(chapter)

        page = Page(
            page_id="page-test-1",
            chapter_id="chap-test-1",
            source_filename="001.png",
            source_order=1,
            sort_order=1,
            source_hash="sha256-hash-001",
            source_size_bytes=1024,
            width=800,
            height=1200,
            managed_original_ref="books/book-test-1/chapters/chap-test-1/original/001.png",
        )
        repo.add_page(page)
        conn.close()

        # 4. ListBooks after seeding
        seeded_resp = send_and_recv({
            "protocol": PROTOCOL_NAME,
            "version": {"major": 1, "minor": 0},
            "request_id": "l-2",
            "command": "ListBooks",
            "payload": {},
        })
        assert seeded_resp["request_id"] == "l-2"
        assert seeded_resp["error"] is None
        books = seeded_resp["result"]
        assert len(books) == 1

        b0 = books[0]
        assert b0["book_id"] == "book-test-1"
        assert b0["title"] == "测试书目"
        assert b0["original_title"] == "Test Book Original"
        assert b0["is_favorite"] is True
        assert b0["is_archived"] is False
        assert b0["page_count"] == 1
        assert "created_at" in b0
        assert "updated_at" in b0

        # No OS path or DB internal leakage
        assert "managed_original_ref" not in b0
        assert "source_filename" not in b0
        assert str(data_root) not in json.dumps(b0)

        # 5. Unsupported version rejection
        bad_ver_resp = send_and_recv({
            "protocol": PROTOCOL_NAME,
            "version": {"major": 99, "minor": 0},
            "request_id": "v-bad",
            "command": "core.ping",
            "payload": {},
        })
        assert bad_ver_resp["request_id"] == "v-bad"
        assert bad_ver_resp["result"] is None
        assert bad_ver_resp["error"]["code"] == E_PROTOCOL_VERSION_UNSUPPORTED
        assert bad_ver_resp["error"]["category"] == "validation"
        assert bad_ver_resp["error"]["retryable"] is False

        # 6. Unknown command rejection
        unknown_resp = send_and_recv({
            "protocol": PROTOCOL_NAME,
            "version": {"major": 1, "minor": 0},
            "request_id": "u-bad",
            "command": "UnknownOperation",
            "payload": {},
        })
        assert unknown_resp["request_id"] == "u-bad"
        assert unknown_resp["result"] is None
        assert unknown_resp["error"]["code"] == E_UNKNOWN_COMMAND

        # 7. Shutdown and clean exit
        shutdown_resp = send_and_recv({
            "protocol": PROTOCOL_NAME,
            "version": {"major": 1, "minor": 0},
            "request_id": "s-1",
            "command": "core.shutdown",
            "payload": {},
        })
        assert shutdown_resp["request_id"] == "s-1"
        assert shutdown_resp["error"] is None
        assert shutdown_resp["result"] == {"status": "stopped"}

        exit_code = proc.wait(timeout=5)
        assert exit_code == 0
    finally:
        if proc.poll() is None:
            proc.kill()
            proc.wait()
