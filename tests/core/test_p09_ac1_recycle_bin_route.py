"""AC1 (R-007): the recycle bin route must exist on the real dispatcher.

The frontend command name, the Tauri command, the bridge round trip, the Core
dispatcher branch and the service method are five separate links. Before this
task four of them were missing, so the UI called a name nothing answered - and
its fail-soft empty list hid that completely.

These are assembly-level assertions: they drive the production Core the same way
the real process does, rather than checking that a symbol exists.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from bootstrap.core_service import CoreServiceServer, assemble_production_core


def _rpc(server: CoreServiceServer, command: str, payload: object) -> dict:
    response, should_exit = server.dispatch_request(
        json.dumps(
            {
                "protocol": "new-manga.core",
                "version": {"major": 2, "minor": 10},
                "request_id": f"ac1-{command}",
                "command": command,
                "payload": payload,
            }
        )
    )
    assert not should_exit
    return response


def test_recycle_bin_command_is_answered_by_the_production_dispatcher(
    tmp_path: Path,
) -> None:
    core = assemble_production_core(tmp_path / "data")
    try:
        server = CoreServiceServer(core)

        res = _rpc(server, "ListRecycleBinBooks", {})

        assert res["error"] is None, (
            "the production dispatcher does not answer ListRecycleBinBooks; the"
            f" frontend command has no handler: {res['error']}"
        )
        assert res["result"] == []

        # The visible list and the recycle bin are different faces of the same
        # library: a live book appears in ListBooks and NOT here.
        with core.conn:
            core.conn.execute(
                "INSERT INTO books (book_id, title, created_at, updated_at)"
                " VALUES ('live-1', 'Live', 'now', 'now')"
            )
        assert [b["book_id"] for b in _rpc(server, "ListBooks", {})["result"]] == [
            "live-1"
        ]
        assert _rpc(server, "ListRecycleBinBooks", {})["result"] == []

        # Soft-delete it: it must leave the visible face and appear here.
        with core.conn:
            core.conn.execute(
                "UPDATE books SET deleted_at = 'now' WHERE book_id = 'live-1'"
            )
        assert _rpc(server, "ListBooks", {})["result"] == []
        recycle = _rpc(server, "ListRecycleBinBooks", {})["result"]
        assert [b["book_id"] for b in recycle] == ["live-1"], (
            "the recycle bin must be driven by the soft-delete set, not by the"
            " visible list"
        )
        # Same frozen projection shape as ListBooks.
        assert set(recycle[0]) == {
            "book_id",
            "title",
            "original_title",
            "is_favorite",
            "is_archived",
            "page_count",
            "created_at",
            "updated_at",
        }
    finally:
        core.conn.close()
