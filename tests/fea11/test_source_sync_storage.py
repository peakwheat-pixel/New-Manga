"""AC2-c (FEA-11-AC4-GAPS-1): the storage-failure projection at the wire.

The failure is injected INSIDE the apply transaction — a real SQLite trigger
on ``page_bindings``, i.e. between ``BEGIN IMMEDIATE`` and ``COMMIT``
(service.py:239-287) — and observed through the REAL host-control dispatch of
the fully assembled production Core. The frozen C-17 §8 projection must be
``SOURCE_SYNC_STORAGE_FAILED`` (``internal`` / ``retryable=true``), must never
echo the injected exception text, and the whole batch must roll back with zero
business writes.

A post-commit ``_bind_operation_grant`` failure is NOT used as rollback
evidence (card limitation L3); the trigger fires strictly inside the
transaction, and the direct service probe below proves it.
"""

from __future__ import annotations

import base64
import io
import json
import sqlite3

import pytest

from tests.fea11.conftest import (
    png_bytes,
    write_zip,
)
from tests.fea11.test_source_sync import (
    _assert_snapshot_equal,
    _freeze_plan,
    _full_snapshot,
    _op_payload,
    _scan,
    _seed_book_and_chapter,
    _seed_two_page_source,
)

from bootstrap.core_service import (
    PROTOCOL_MAJOR,
    PROTOCOL_MINOR,
    CoreServiceServer,
    assemble_production_core,
)

HOST_SESSION_ID = "host-session-ac2c"
HOST_CREDENTIAL = base64.urlsafe_b64encode(bytes(range(32))).decode().rstrip("=")


def _wire(command: str, payload: dict) -> dict:
    return {
        "protocol": "new-manga.core",
        "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
        "request_id": "req-" + command.lower(),
        "channel": "host-control",
        "command": command,
        "payload": payload,
    }


def _open_host_session(server: CoreServiceServer) -> str:
    response, should_exit = server.dispatch_request(
        json.dumps(
            {
                "protocol": "new-manga.core",
                "version": {
                    "major": PROTOCOL_MAJOR,
                    "minor": PROTOCOL_MINOR,
                },
                "request_id": "open-host-session",
                "channel": "host-control",
                "command": "OpenHostSession",
                "payload": {
                    "host_session_id": HOST_SESSION_ID,
                    "host_session_credential": HOST_CREDENTIAL,
                },
            }
        )
    )
    assert not should_exit
    assert response["error"] is None
    return response["result"]["core_session_id"]


def _host_control(
    server: CoreServiceServer,
    core_session_id: str,
    command: str,
    payload: dict,
    *,
    request_id: str,
) -> dict:
    request = _wire(command, payload)
    request.update(
        {
            "request_id": request_id,
            "core_session_id": core_session_id,
            "host_session_id": HOST_SESSION_ID,
            "host_session_credential": HOST_CREDENTIAL,
        }
    )
    response, should_exit = server.dispatch_request(json.dumps(request))
    assert not should_exit
    return response


def test_storage_failure_is_a_typed_wire_error_with_zero_business_writes(
    tmp_path, scratch_dir
):
    """AC2-c: mid-transaction SQLite ABORT -> SOURCE_SYNC_STORAGE_FAILED.

    Wire assertions: ``result is None``; ``code/category/retryable`` equal the
    frozen C-17 §8 projection; the injected message is not echoed. Behaviour
    assertions: all 16 tables are byte-identical afterwards, the plan stays
    ``confirmed``, and a retry with a fresh operation id succeeds."""
    core = assemble_production_core(tmp_path / "core-data")
    server = CoreServiceServer(
        core, stdin=io.StringIO(), stdout=io.StringIO()
    )
    try:
        conn = core.conn
        stack = core.source_sync
        registry = core.source_read_refs
        _seed_book_and_chapter(conn)
        _zip_path, page1, _page2, _container = _seed_two_page_source(
            conn, scratch_dir, legacy_v7_evidence=False
        )
        changed = png_bytes(color=(0, 0, 255))
        new_zip = write_zip(
            scratch_dir / "new.zip",
            [("001.png", page1), ("002.png", changed)],
        )
        grant_id, scan = _scan(stack, registry, new_zip)
        body, plan = _freeze_plan(stack, scan)
        payload = _op_payload(
            scan,
            [grant_id],
            plan_id=body["plan_id"],
            plan_digest=plan["plan_digest"],
            operation_id="op-wire-storage-failure",
        )
        core_session_id = _open_host_session(server)
        # Real SQLite failure between BEGIN IMMEDIATE and COMMIT: p1's new
        # binding already published inside the transaction, p2's insert
        # aborts the whole batch.
        conn.execute(
            "CREATE TRIGGER fea11_inject_storage BEFORE INSERT ON"
            " page_bindings WHEN NEW.page_id = 'p2' BEGIN SELECT"
            " RAISE(ABORT, 'injected storage failure'); END"
        )
        conn.commit()
        baseline = _full_snapshot(conn)
        try:
            response = _host_control(
                server,
                core_session_id,
                "ResyncSource",
                payload,
                request_id="req-ac2c-apply",
            )
            assert response["result"] is None
            error = response["error"]
            assert error["code"] == "SOURCE_SYNC_STORAGE_FAILED"
            assert error["category"] == "internal"
            assert error["retryable"] is True
            assert "injected" not in error["message"]
            assert "injected" not in json.dumps(response)
            assert "RAISE" not in json.dumps(response)
            _assert_snapshot_equal(
                baseline, _full_snapshot(conn), label="AC2-c wire"
            )
            row = conn.execute(
                "SELECT state, applied_at FROM source_sync_plans"
                " WHERE plan_id = ?",
                (body["plan_id"],),
            ).fetchone()
            assert row["state"] == "confirmed"
            assert row["applied_at"] is None
            assert conn.execute(
                "SELECT COUNT(*) FROM source_operations"
            ).fetchone()[0] == 0
            assert conn.execute(
                "SELECT COUNT(*) FROM source_binding_publications"
            ).fetchone()[0] == 0
            # The injection point is INSIDE the transaction: the same service
            # seam raises the raw SQLite error (not a typed business
            # rejection) and still writes nothing.
            with pytest.raises(sqlite3.IntegrityError) as raised:
                stack["service"].apply(
                    "ResyncSource",
                    _op_payload(
                        scan,
                        [grant_id],
                        plan_id=body["plan_id"],
                        plan_digest=plan["plan_digest"],
                        operation_id="op-direct-storage-probe",
                    ),
                )
            assert "injected" in str(raised.value)
            _assert_snapshot_equal(
                baseline, _full_snapshot(conn), label="AC2-c direct probe"
            )
        finally:
            conn.execute("DROP TRIGGER fea11_inject_storage")
            conn.commit()
        # The plan is still usable: a fresh operation id succeeds on the wire.
        retry = _op_payload(
            scan,
            [grant_id],
            plan_id=body["plan_id"],
            plan_digest=plan["plan_digest"],
            operation_id="op-wire-storage-retry",
        )
        retried = _host_control(
            server,
            core_session_id,
            "ResyncSource",
            retry,
            request_id="req-ac2c-retry",
        )
        assert retried["error"] is None
        assert retried["result"]["accepted"] is True
        assert retried["result"]["state"] == "core-committed"
        assert retried["result"]["operation_id"] == "op-wire-storage-retry"
        assert conn.execute(
            "SELECT state FROM source_sync_plans WHERE plan_id = ?",
            (body["plan_id"],),
        ).fetchone()["state"] == "applied"
        assert conn.execute(
            "SELECT COUNT(*) FROM page_bindings WHERE page_id = 'p1'"
        ).fetchone()[0] == 2
        assert conn.execute(
            "SELECT COUNT(*) FROM page_bindings WHERE page_id = 'p2'"
        ).fetchone()[0] == 2
    finally:
        server.close()
        core.close()
