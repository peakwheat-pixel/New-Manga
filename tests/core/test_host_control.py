from __future__ import annotations

import base64
import hashlib
import hmac
import io
import json
import os
from pathlib import Path
import sys
import subprocess
import time
import uuid

import pytest

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from application.resource_channel.dto import TypedResourceChannelError
from bootstrap.core_service import PROTOCOL_MAJOR, PROTOCOL_MINOR, CoreServiceServer, assemble_production_core
from infrastructure.export.target_refs import ExportTargetRefError
from infrastructure.resource_channel.handle_resolver import HandleVerifiedFileReader

HOST_SESSION_ID = "host-session-test"
HOST_CREDENTIAL = base64.urlsafe_b64encode(bytes(range(32))).decode().rstrip("=")
SIGNING_KEY = bytes(range(32))


def _server(tmp_path: Path, *, stdin=None, stdout=None):
    core = assemble_production_core(tmp_path / "data")
    server = CoreServiceServer(
        core, stdin=stdin or io.StringIO(), stdout=stdout or io.StringIO(),
    )
    return core, server


def _wire(command: str, payload: dict, *, request_id: str | None = None) -> dict:
    return {
        "protocol": "new-manga.core",
        "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
        "request_id": request_id or uuid.uuid4().hex,
        "channel": "host-control",
        "command": command,
        "payload": payload,
    }


def _open(server: CoreServiceServer, *, host_id: str = HOST_SESSION_ID, credential: str = HOST_CREDENTIAL) -> str:
    response, _ = server.dispatch_request(json.dumps({
        "protocol": "new-manga.core",
        "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
        "request_id": "open-host-session",
        "channel": "host-control",
        "command": "OpenHostSession",
        "payload": {
            "host_session_id": host_id,
            "host_session_credential": credential,
        },
    }))
    assert response["error"] is None
    return response["result"]["core_session_id"]


def _request(
    server: CoreServiceServer,
    core_session_id: str,
    command: str,
    payload: dict,
    *,
    host_id: str = HOST_SESSION_ID,
    credential: str | None = HOST_CREDENTIAL,
) -> dict:
    request = _wire(command, payload)
    request.update({"core_session_id": core_session_id, "host_session_id": host_id})
    if credential is not None:
        request["host_session_credential"] = credential
    response, should_exit = server.dispatch_request(json.dumps(request))
    assert not should_exit
    return response


def _export_payload(tmp_path: Path, host_id: str, *, grant_id: str | None = None) -> tuple[dict, str]:
    grant_id = grant_id or uuid.uuid4().hex
    target = (tmp_path / "outputs" / "chapter.png").absolute()
    target.parent.mkdir(parents=True, exist_ok=True)
    expires_at = time.time() + 120
    signed = "\0".join((
        grant_id, host_id, str(target), "png", "1", f"{expires_at:.6f}",
    )).encode()
    signature = base64.urlsafe_b64encode(
        hmac.new(SIGNING_KEY, signed, hashlib.sha256).digest()
    ).decode().rstrip("=")
    return ({
        "grant_id": grant_id,
        "session_id": host_id,
        "target_path": str(target),
        "format": "png",
        "replace_existing": True,
        "expires_at": expires_at,
        "signing_key": base64.urlsafe_b64encode(SIGNING_KEY).decode().rstrip("="),
        "signature": signature,
    }, f"etref1.{grant_id}.{signature}")


def _import_payload(source: Path, host_id: str, *, grant_id: str | None = None) -> tuple[dict, dict]:
    grant_id = grant_id or uuid.uuid4().hex
    source = source.absolute()
    facts = HandleVerifiedFileReader(source.parent, limit=sys.maxsize).capture_facts(source.name)
    entries = [{
        "path": str(source),
        "facts": {
            "volume_serial": facts.volume_serial,
            "file_index": facts.file_index,
            "size": facts.size,
            "sha256": facts.sha256,
        },
    }]
    expires_at = time.time() + 120
    signed_fields = {
        "grant_id": grant_id,
        "session_id": host_id,
        "scope_class": "user-source",
        "operation": "ImportPages",
        "access": "read-only",
        "source_path": str(source),
        "source_kind": "file",
        "scope_identity": None,
        "entries": entries,
        "expires_at": f"{expires_at:.6f}",
    }
    signature = base64.urlsafe_b64encode(hmac.new(
        SIGNING_KEY,
        json.dumps(signed_fields, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode(),
        hashlib.sha256,
    ).digest()).decode().rstrip("=")
    return ({
        "grant_id": grant_id,
        "session_id": host_id,
        "scope_class": "user-source",
        "operation": "ImportPages",
        "access": "read-only",
        "source_path": str(source),
        "source_kind": "file",
        "scope_identity": None,
        "entries": entries,
        "expires_at": expires_at,
        "signing_key": base64.urlsafe_b64encode(SIGNING_KEY).decode().rstrip("="),
        "signature": signature,
    }, {"grant_id": grant_id, "host_signature": signature})


def _disk_snapshot(root: Path) -> dict[str, str]:
    return {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in root.rglob("*") if path.is_file()
    }


def _close(core, server):
    server.close()
    core.conn.close()


def test_host_control_stdio_handshake_and_eof_revoke(tmp_path: Path) -> None:
    core, server = _server(tmp_path)
    export_payload, export_ref = _export_payload(tmp_path, HOST_SESSION_ID)
    lines = [
        json.dumps({
            "protocol": "new-manga.core",
            "version": {"major": 2, "minor": 3},
            "request_id": "open",
            "channel": "host-control",
            "command": "OpenHostSession",
            "payload": {
                "host_session_id": HOST_SESSION_ID,
                "host_session_credential": HOST_CREDENTIAL,
            },
        }),
        json.dumps({
            **_wire("RegisterExportTarget", export_payload),
            "core_session_id": server._core_session_id,
            "host_session_id": HOST_SESSION_ID,
            "host_session_credential": HOST_CREDENTIAL,
        }),
    ]
    server._stdin = io.StringIO("\n".join(lines) + "\n")
    server._stdout = io.StringIO()
    try:
        assert server.serve_forever() == 0
        responses = [json.loads(line) for line in server._stdout.getvalue().splitlines()]
        assert len(responses) == 2
        assert responses[0]["result"]["core_session_id"] == server._core_session_id
        assert responses[1]["result"] == {"registered": True}
        assert all(response["version"] == {"major": 2, "minor": 3} for response in responses)
        assert all(response["error"] is None for response in responses)
        assert server._host_session_credential is None
        with pytest.raises(ExportTargetRefError, match="REF_REVOKED"):
            core.export_target_refs.resolve_and_consume(export_ref, "png")
    finally:
        _close(core, server)


def test_host_control_routes_existing_register_and_revoke_seams(tmp_path: Path) -> None:
    core, server = _server(tmp_path)
    source = tmp_path / "selected.png"
    source.write_bytes(b"selected source stays read-only")
    import_payload, import_ref = _import_payload(source, HOST_SESSION_ID)
    export_payload, export_ref = _export_payload(tmp_path, HOST_SESSION_ID)
    try:
        core_session_id = _open(server)
        imported = _request(server, core_session_id, "RegisterImportSource", import_payload)
        exported = _request(server, core_session_id, "RegisterExportTarget", export_payload)
        assert imported["result"] == {"registered": True}
        assert exported["result"] == {"registered": True}

        opened = core.import_source_refs.resolve_many([import_ref])
        assert len(opened) == 1
        opened[0].close()
        assert _request(server, core_session_id, "RevokeImportSource", {"grant_id": import_payload["grant_id"]})["result"] == {"revoked": True}
        assert _request(server, core_session_id, "RevokeExportTarget", {"grant_id": export_payload["grant_id"]})["result"] == {"revoked": True}
        assert _request(server, core_session_id, "RevokeImportSource", {"grant_id": import_payload["grant_id"]})["result"] == {"revoked": True}
        assert _request(server, core_session_id, "RevokeExportTarget", {"grant_id": export_payload["grant_id"]})["result"] == {"revoked": True}
        with pytest.raises(TypedResourceChannelError, match="REF_REVOKED"):
            core.import_source_refs.resolve_many([import_ref])
        with pytest.raises(ExportTargetRefError, match="REF_REVOKED"):
            core.export_target_refs.resolve_and_consume(export_ref, "png")
        unknown = _request(server, core_session_id, "RevokeExportTarget", {"grant_id": uuid.uuid4().hex})
        assert unknown["error"]["code"] == "REF_UNKNOWN_ID"
    finally:
        _close(core, server)


@pytest.mark.parametrize("case", [
    "ordinary_json_rpc", "credential_missing", "credential_wrong",
    "session_closed", "core_session_mismatch",
])
def test_three_host_only_rejections_do_not_call_seams_or_mutate_data(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, case: str,
) -> None:
    core, server = _server(tmp_path)
    calls: list[str] = []
    monkeypatch.setattr(server, "_register_import_source", lambda payload: calls.append("import"))
    monkeypatch.setattr(server, "_register_export_target", lambda payload: calls.append("export"))
    core_session_id = server._core_session_id
    if case != "ordinary_json_rpc":
        core_session_id = _open(server)
    if case == "session_closed":
        closed = _request(server, core_session_id, "CloseHostSession", {})
        assert closed["result"] == {"closed": True}

    target = tmp_path / "protected target.png"
    target.write_bytes(b"target sentinel")
    source = tmp_path / "source.png"
    source.write_bytes(b"source sentinel")
    disk_before = _disk_snapshot(tmp_path)
    db_changes_before = core.conn.total_changes
    import_grants_before = set(core.import_source_refs._grants)
    export_grants_before = set(core.export_target_refs._grants)

    if case == "ordinary_json_rpc":
        request = {
            "protocol": "new-manga.core",
            "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
            "request_id": "ordinary-host-only-attempt",
            "command": "RegisterExportTarget",
            "payload": {"grant_id": "unused"},
        }
        expected = "HOST_ONLY_REQUIRED"
    else:
        request = _wire("RegisterExportTarget", {"grant_id": "unused", "target_path": str(target)})
        request.update({
            "core_session_id": core_session_id,
            "host_session_id": HOST_SESSION_ID,
            "host_session_credential": HOST_CREDENTIAL,
        })
        expected = "HOST_SESSION_INVALID"
        if case == "credential_missing":
            request.pop("host_session_credential")
        elif case == "credential_wrong":
            request["host_session_credential"] = "wrong credential"
        elif case == "core_session_mismatch":
            request["core_session_id"] = "another-core-process"
            expected = "CORE_SESSION_MISMATCH"

    response, _ = server.dispatch_request(json.dumps(request))
    assert response["result"] is None
    assert response["error"]["code"] == expected
    assert response["error"]["category"] == {
        "HOST_ONLY_REQUIRED": "validation",
        "HOST_SESSION_INVALID": "conflict",
        "CORE_SESSION_MISMATCH": "conflict",
    }[expected]
    assert calls == []
    assert core.conn.total_changes == db_changes_before
    assert set(core.import_source_refs._grants) == import_grants_before
    assert set(core.export_target_refs._grants) == export_grants_before
    assert _disk_snapshot(tmp_path) == disk_before
    assert str(target) not in json.dumps(response["error"])
    assert HOST_CREDENTIAL not in json.dumps(response["error"])
    _close(core, server)


@pytest.mark.parametrize("command", sorted({
    "OpenHostSession", "RegisterImportSource", "RevokeImportSource",
    "RegisterExportTarget", "RevokeExportTarget", "CloseHostSession",
}))
def test_host_only_commands_are_not_in_the_json_rpc_dispatcher(tmp_path: Path, command: str) -> None:
    core, server = _server(tmp_path)
    request = {
        "protocol": "new-manga.core",
        "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
        "request_id": "ordinary-dispatcher-negative",
        "command": command,
        "payload": {},
    }
    try:
        response, _ = server.dispatch_request(json.dumps(request))
        assert response["error"]["code"] == "HOST_ONLY_REQUIRED"
        assert response["error"]["category"] == "validation"
        assert response["result"] is None
    finally:
        _close(core, server)


def test_session_close_revokes_grants_and_restart_gets_a_fresh_registry(tmp_path: Path) -> None:
    core, server = _server(tmp_path)
    source = tmp_path / "chosen.png"
    source_bytes = b"immutable user source"
    source.write_bytes(source_bytes)
    target_payload, export_ref = _export_payload(tmp_path, HOST_SESSION_ID)
    target = Path(target_payload["target_path"])
    target.write_bytes(b"existing target sentinel")
    import_payload, import_ref = _import_payload(source, HOST_SESSION_ID)
    try:
        core_session_id = _open(server)
        assert _request(server, core_session_id, "RegisterImportSource", import_payload)["result"] == {"registered": True}
        assert _request(server, core_session_id, "RegisterExportTarget", target_payload)["result"] == {"registered": True}
        opened = core.import_source_refs.resolve_many([import_ref])
        opened[0].close()
        disk_before_close = _disk_snapshot(tmp_path)

        closed = _request(server, core_session_id, "CloseHostSession", {})
        assert closed["result"] == {"closed": True}
        with pytest.raises(TypedResourceChannelError, match="REF_REVOKED"):
            core.import_source_refs.resolve_many([import_ref])
        with pytest.raises(ExportTargetRefError, match="REF_REVOKED"):
            core.export_target_refs.resolve_and_consume(export_ref, "png")
        assert source.read_bytes() == source_bytes
        assert target.read_bytes() == b"existing target sentinel"
        assert _disk_snapshot(tmp_path) == disk_before_close
        reopened, _ = server.dispatch_request(json.dumps({
            "protocol": "new-manga.core",
            "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
            "request_id": "second-open",
            "channel": "host-control",
            "command": "OpenHostSession",
            "payload": {
                "host_session_id": "rotated-host-session",
                "host_session_credential": base64.urlsafe_b64encode(b"x" * 32).decode().rstrip("="),
            },
        }))
        assert reopened["error"]["code"] == "HOST_SESSION_ALREADY_OPENED"

        restarted_core, restarted_server = _server(tmp_path / "restart")
        try:
            assert restarted_server._core_session_id != server._core_session_id
            with pytest.raises(TypedResourceChannelError, match="REF_UNKNOWN_ID"):
                restarted_core.import_source_refs.resolve_many([import_ref])
            with pytest.raises(ExportTargetRefError, match="REF_UNKNOWN_ID"):
                restarted_core.export_target_refs.resolve_and_consume(export_ref, "png")
        finally:
            _close(restarted_core, restarted_server)
    finally:
        _close(core, server)


def test_new_core_process_has_a_new_session_and_no_old_import_grants(tmp_path: Path) -> None:
    data_root = tmp_path / "core-data"
    seed = assemble_production_core(data_root)
    with seed.conn:
        seed.conn.execute(
            "INSERT INTO books (book_id,title,author,description,created_at,updated_at)"
            " VALUES ('book','Test','Author','',?,?)",
            ("2026-10-16T00:00:00+00:00", "2026-10-16T00:00:00+00:00"),
        )
        seed.conn.execute(
            "INSERT INTO chapters (chapter_id,book_id,title,chapter_number,sort_order,"
            "chapter_type,reading_direction,created_at,updated_at)"
            " VALUES ('chapter','book','Chapter','1',0,'paged','rtl',?,?)",
            ("2026-10-16T00:00:00+00:00", "2026-10-16T00:00:00+00:00"),
        )
    seed.conn.close()

    source = tmp_path / "user-source.png"
    source.write_bytes(b"read-only source for a restarted core")
    import_payload, import_ref = _import_payload(source, HOST_SESSION_ID)
    env = os.environ.copy()
    env["NEWMANGA_DATA_ROOT"] = str(data_root)
    cmd = [sys.executable, "-m", "bootstrap.core_service"]

    first = subprocess.Popen(
        cmd, cwd=SRC_ROOT, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, text=True,
    )
    try:
        assert first.stdin is not None and first.stdout is not None
        open_request = {
            "protocol": "new-manga.core",
            "version": {"major": 2, "minor": 3},
            "request_id": "first-process-open",
            "channel": "host-control",
            "command": "OpenHostSession",
            "payload": {
                "host_session_id": HOST_SESSION_ID,
                "host_session_credential": HOST_CREDENTIAL,
            },
        }
        first.stdin.write(json.dumps(open_request) + "\n")
        first.stdin.flush()
        first_open = json.loads(first.stdout.readline())
        first_core_id = first_open["result"]["core_session_id"]
        register = _wire("RegisterImportSource", import_payload)
        register.update({
            "core_session_id": first_core_id,
            "host_session_id": HOST_SESSION_ID,
            "host_session_credential": HOST_CREDENTIAL,
        })
        first.stdin.write(json.dumps(register) + "\n")
        first.stdin.flush()
        first_registered = json.loads(first.stdout.readline())
        assert first_registered["result"] == {"registered": True}
        first.stdin.close()
        assert first.wait(timeout=45) == 0
        first_stdout = first.stdout.read()
        first_stderr = first.stderr.read() if first.stderr is not None else ""
        assert HOST_CREDENTIAL not in first_stdout + first_stderr
        assert import_payload["source_path"] not in first_stdout + first_stderr
    finally:
        if first.poll() is None:
            first.kill()
            first.wait(timeout=10)

    restarted_credential = base64.urlsafe_b64encode(b"r" * 32).decode().rstrip("=")
    restarted_lines = [
        json.dumps({
            "protocol": "new-manga.core",
            "version": {"major": 2, "minor": 3},
            "request_id": "restarted-process-open",
            "channel": "host-control",
            "command": "OpenHostSession",
            "payload": {
                "host_session_id": "restarted-host-session",
                "host_session_credential": restarted_credential,
            },
        }),
        json.dumps({
            "protocol": "new-manga.core",
            "version": {"major": 2, "minor": 3},
            "request_id": "old-import-ref-after-restart",
            "command": "ImportPages",
            "payload": {"chapter_id": "chapter", "sources": [import_ref]},
        }),
    ]
    restarted = subprocess.run(
        cmd, cwd=SRC_ROOT, env=env, input="\n".join(restarted_lines) + "\n",
        capture_output=True, text=True, timeout=45,
    )
    responses = [json.loads(line) for line in restarted.stdout.splitlines() if line]
    assert restarted.returncode == 0, restarted.stderr
    assert len(responses) == 2
    assert responses[0]["result"]["core_session_id"] != first_core_id
    assert responses[1]["error"]["code"] == "REF_UNKNOWN_ID"
    assert import_payload["source_path"] not in restarted.stdout + restarted.stderr


def test_host_control_rejects_unknown_envelope_fields_without_routing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    core, server = _server(tmp_path)
    calls: list[dict] = []
    monkeypatch.setattr(server, "_register_export_target", lambda payload: calls.append(payload))
    core_session_id = _open(server)
    request = _wire("RegisterExportTarget", {"grant_id": "not-read"})
    request.update({
        "core_session_id": core_session_id,
        "host_session_id": HOST_SESSION_ID,
        "host_session_credential": HOST_CREDENTIAL,
        "unexpected": "reject",
    })
    try:
        response, _ = server.dispatch_request(json.dumps(request))
        assert response["error"]["code"] == "INVALID_REQUEST"
        assert response["result"] is None
        assert calls == []
    finally:
        _close(core, server)
