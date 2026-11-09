"""FEA-13-RESTORE-4: the merge-restore wire on the production Core.

Covers the application-channel surface: ``backup.restore`` with ``mode``
(``defer`` default behaviour of the merge path, ``overwrite`` unchanged), the
staging/commit marker protocol, and the L-5 exclusive maintenance window that
fails every other write command closed while a merge restore is active.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from bootstrap.core_service import (  # noqa: E402
    PROTOCOL_MAJOR,
    PROTOCOL_MINOR,
    CoreServiceServer,
    assemble_production_core,
)

NOW = "2026-11-09T16:00:00+00:00"


@pytest.fixture()
def core(tmp_path: Path):
    assembled = assemble_production_core(tmp_path / "data")
    try:
        yield assembled
    finally:
        assembled.conn.close()


def _request(
    server: CoreServiceServer, command: str, payload, request_id: str = "req-restore-1"
) -> dict:
    request = {
        "protocol": "new-manga.core",
        "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
        "request_id": request_id,
        "command": command,
        "payload": payload,
    }
    response, _should_exit = server.dispatch_request(json.dumps(request))
    return response


def _result(response: dict) -> dict:
    assert response.get("error") is None, response.get("error")
    return response["result"]


def _create_backup(server) -> str:
    created = _result(_request(server, "backup.create", {}))
    assert created["verified"] is True
    return created["backup_id"]


def _seed_book(conn, title: str, book_id: str = "book-1") -> None:
    with conn:
        conn.execute(
            "INSERT OR IGNORE INTO books (book_id, title, created_at, updated_at)"
            " VALUES (?, ?, ?, ?)",
            (book_id, title, NOW, NOW),
        )


def test_defer_restore_keeps_conflicts_and_writes_the_commit_marker(core):
    server = CoreServiceServer(core)
    _seed_book(core.conn, "BEFORE")
    backup_id = _create_backup(server)
    with core.conn:
        core.conn.execute("UPDATE books SET title = 'AFTER' WHERE book_id = 'book-1'")

    report = _result(
        _request(
            server,
            "backup.restore",
            {"backup_id": backup_id, "confirm_restore": True, "mode": "defer"},
        )
    )

    assert report["mode"] == "defer"
    assert report["failed"] == []
    assert any(item["action"] == "conflict" for item in report["deferred"])
    title = core.conn.execute("SELECT title FROM books WHERE book_id = 'book-1'").fetchone()[0]
    assert title == "AFTER"  # defer never overwrites the live value

    marker = Path(report["staging_root"]).parent / f".restore-{backup_id}.json"
    assert marker.is_file()
    marker_state = json.loads(marker.read_text(encoding="utf-8"))
    assert marker_state["state"] == "committed"


def test_overwrite_mode_keeps_the_legacy_behaviour(core):
    server = CoreServiceServer(core)
    _seed_book(core.conn, "BEFORE")
    backup_id = _create_backup(server)
    with core.conn:
        core.conn.execute("UPDATE books SET title = 'AFTER' WHERE book_id = 'book-1'")

    report = _result(
        _request(
            server,
            "backup.restore",
            {"backup_id": backup_id, "confirm_restore": True},
        )
    )

    assert report["restored_from"] == backup_id
    title = core.conn.execute("SELECT title FROM books WHERE book_id = 'book-1'").fetchone()[0]
    assert title == "BEFORE"


def test_unknown_mode_is_rejected(core):
    server = CoreServiceServer(core)
    backup_id = _create_backup(server)

    response = _request(
        server,
        "backup.restore",
        {"backup_id": backup_id, "confirm_restore": True, "mode": "merge-everything"},
    )

    assert response["error"]["code"] == "INVALID_REQUEST"


def test_write_commands_fail_closed_during_the_maintenance_window(core):
    server = CoreServiceServer(core)
    server._restore_maintenance_active = True
    try:
        response = _request(server, "books.list", {})
        assert response["error"]["code"] == "RESTORE_IN_PROGRESS"
        assert response["error"]["category"] == "conflict"

        # Backup commands stay available (list/create/delete are exempt).
        listed = _result(_request(server, "backup.list", {}, "req-exempt-1"))
        assert isinstance(listed, list)
    finally:
        server._restore_maintenance_active = False


def test_marker_stays_staging_when_the_apply_crashes(core, monkeypatch):
    """AC5: a crash before commit leaves a decidable marker and an intact live DB."""
    from application.maintenance import restore_plan as planner

    server = CoreServiceServer(core)
    _seed_book(core.conn, "BEFORE")
    backup_id = _create_backup(server)
    with core.conn:
        core.conn.execute("UPDATE books SET title = 'AFTER' WHERE book_id = 'book-1'")

    def boom(*_args, **_kwargs):
        raise RuntimeError("simulated crash before commit")

    monkeypatch.setattr(planner, "apply_restore", boom)

    response = _request(
        server,
        "backup.restore",
        {"backup_id": backup_id, "confirm_restore": True, "mode": "defer"},
    )

    assert response["error"] is not None  # the crash is reported, never swallowed
    marker = core.backup._backup_root / f".restore-{backup_id}.json"
    assert marker.is_file()
    assert json.loads(marker.read_text(encoding="utf-8"))["state"] == "staging"
    title = core.conn.execute("SELECT title FROM books WHERE book_id = 'book-1'").fetchone()[0]
    assert title == "AFTER"  # the live database was never touched
    # The maintenance window is released even on failure.
    assert server._restore_maintenance_active is False
