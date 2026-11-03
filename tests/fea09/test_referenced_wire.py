"""FEA-09 Phase C — Core-side source-read grants and the wire face.

Real ``SourceReadGrantRegistry`` (HMAC envelope per C-16 §2), the
host-control register/revoke pair and the application-channel
plan/start/receipt/cancel commands driven through ``CoreServiceServer``
dispatch with the frozen C-16 §6 error table.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import io
import json
import time

import pytest

from support import png_bytes, write_zip
from conftest import NOW
from infrastructure.resource_channel.source_read_refs import SourceReadGrantRegistry
from application.importing.referenced.errors import SourceImportError

SESSION = "host-session-1"
KEY = b"0123456789abcdef0123456789abcdef"


def _b64u(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def _facts_of(path) -> dict:
    import os

    info = os.stat(path)
    return {
        "volume_serial": int(info.st_dev),
        "file_id": int(info.st_ino),
        "size": int(info.st_size),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def mint_grant(
    *,
    grant_id: str,
    path,
    kind: str,
    expires_at: float,
    key: bytes = KEY,
    session_id: str = SESSION,
    registry_id: str = "reg-1",
    generation: int = 3,
    locator: str = "001.png",
    entries: list | None = None,
) -> dict:
    """Build a Host-shaped RegisterSourceReadGrant payload with signature."""
    if entries is None:
        entries = [{
            "entry_key": "k1", "entry_id": None, "locator": locator,
            "ordinal": 0, "path": str(path), "facts": _facts_of(path),
        }]
    payload = {
        "grant_id": grant_id,
        "session_id": session_id,
        "operation": "source-read",
        "scope_class": "user-source",
        "registry_id": registry_id,
        "generation": generation,
        "expires_at": expires_at,
        "budget": {"max_bytes": 1 << 24, "max_decode_bytes": 1 << 24, "max_entries": 1000},
        "scope": {
            "source_id": "pending",
            "version": "pending",
            "rendition": {"decoder": kind, "scale": 1.0, "params_digest": "0" * 64},
            "entries": entries,
        },
    }
    fields = {k: v for k, v in payload.items()}
    fields["expires_at"] = f"{expires_at:.6f}"
    canonical = json.dumps(fields, ensure_ascii=False, sort_keys=True,
                           separators=(",", ":")).encode()
    payload["signing_key"] = _b64u(key)
    payload["signature"] = _b64u(hmac.new(key, canonical, hashlib.sha256).digest())
    return payload


class _Clock:
    def __init__(self) -> None:
        self.now = 1_000_000.0

    def __call__(self) -> float:
        return self.now


@pytest.fixture()
def clock():
    return _Clock()


@pytest.fixture()
def registry(clock):
    return SourceReadGrantRegistry(clock=clock)


# ------------------------------------------------------------------ register
def test_register_and_resolve_roundtrip(tmp_path, registry, clock):
    path = tmp_path / "001.png"
    path.write_bytes(png_bytes(3, 3))
    payload = mint_grant(
        grant_id="g-src-0000000001", path=path, kind="image",
        expires_at=clock.now + 300,
    )
    registry.register(payload)

    resolved = registry.resolve("g-src-0000000001")
    assert resolved.source_kind == "image"
    assert resolved.container_path == str(path)
    assert resolved.budget.max_bytes == 1 << 24
    assert resolved.registry_id == "reg-1"
    assert resolved.generation == 3

    # End-to-end: the resolved grant feeds the real scanner (strict verify).
    from application.importing.referenced.pdf_probe import PdfiumSourceInspector
    from application.importing.referenced.scanner import scan_source

    scanned = scan_source(
        resolved, pdf_open=PdfiumSourceInspector().open
    )
    assert scanned.status == "ok"
    assert scanned.container_digest == payload["scope"]["entries"][0]["facts"]["sha256"]


def test_register_rejects_bad_signature(tmp_path, registry, clock):
    path = tmp_path / "001.png"
    path.write_bytes(png_bytes(3, 3))
    payload = mint_grant(
        grant_id="g-src-0000000002", path=path, kind="image",
        expires_at=clock.now + 300,
    )
    payload["signature"] = _b64u(b"x" * 32)
    with pytest.raises(SourceImportError) as caught:
        registry.register(payload)
    assert caught.value.code == "REF_SIGNATURE_INVALID"


def test_register_rejects_expired_window(tmp_path, registry, clock):
    path = tmp_path / "001.png"
    path.write_bytes(png_bytes(3, 3))
    payload = mint_grant(
        grant_id="g-src-0000000003", path=path, kind="image",
        expires_at=clock.now - 1,
    )
    with pytest.raises(SourceImportError) as caught:
        registry.register(payload)
    assert caught.value.code == "SOURCE_GRANT_EXPIRED"


def test_register_rejects_overlong_window(tmp_path, registry, clock):
    path = tmp_path / "001.png"
    path.write_bytes(png_bytes(3, 3))
    payload = mint_grant(
        grant_id="g-src-0000000004", path=path, kind="image",
        expires_at=clock.now + 301,
    )
    with pytest.raises(SourceImportError) as caught:
        registry.register(payload)
    assert caught.value.code == "SOURCE_GRANT_EXPIRED"


def test_session_binding_and_duplicate_grant(tmp_path, registry, clock):
    path = tmp_path / "001.png"
    path.write_bytes(png_bytes(3, 3))
    first = mint_grant(
        grant_id="g-src-0000000005", path=path, kind="image",
        expires_at=clock.now + 300,
    )
    registry.register(first)
    other_session = mint_grant(
        grant_id="g-src-0000000006", path=path, kind="image",
        expires_at=clock.now + 300, session_id="host-session-2",
    )
    with pytest.raises(SourceImportError) as caught:
        registry.register(other_session)
    assert caught.value.code == "SOURCE_ACCESS_DENIED"
    duplicate = dict(first)
    with pytest.raises(SourceImportError) as caught:
        registry.register(duplicate)
    assert caught.value.code == "SOURCE_ACCESS_DENIED"


def test_resolve_checks_expiry_and_revocation(tmp_path, registry, clock):
    path = tmp_path / "001.png"
    path.write_bytes(png_bytes(3, 3))
    registry.register(mint_grant(
        grant_id="g-src-0000000007", path=path, kind="image",
        expires_at=clock.now + 300,
    ))
    clock.now += 301
    with pytest.raises(SourceImportError) as caught:
        registry.resolve("g-src-0000000007")
    assert caught.value.code == "SOURCE_GRANT_EXPIRED"

    clock.now = 1_000_000.0
    registry.revoke_grants("reg-1", 4, ["g-src-0000000007"])
    with pytest.raises(SourceImportError) as caught:
        registry.resolve("g-src-0000000007")
    assert caught.value.code == "SOURCE_GRANT_REVOKED"


def test_generation_floor_kills_older_grants(tmp_path, registry, clock):
    """RevokeSourceReadGrant 的 generation 提升废止旧代 grant（C-06 v1.1）。"""
    path_a = tmp_path / "001.png"
    path_a.write_bytes(png_bytes(3, 3))
    path_b = tmp_path / "002.png"
    path_b.write_bytes(png_bytes(3, 3, (0, 255, 0)))
    registry.register(mint_grant(
        grant_id="g-src-0000000008", path=path_a, kind="image",
        expires_at=clock.now + 300, generation=3,
    ))
    registry.register(mint_grant(
        grant_id="g-src-0000000009", path=path_b, kind="image",
        expires_at=clock.now + 300, generation=5,
    ))
    revoked = registry.revoke_grants("reg-1", 5, ["g-src-0000000008"])
    assert revoked == 1
    # gen=3 grant dies via both the id list and the generation floor
    with pytest.raises(SourceImportError) as caught:
        registry.resolve("g-src-0000000008")
    assert caught.value.code == "SOURCE_GRANT_REVOKED"
    # gen=5 grant survives an equal floor
    assert registry.resolve("g-src-0000000009").grant_id == "g-src-0000000009"


def test_revoke_all_for_session(tmp_path, registry, clock):
    path = tmp_path / "001.png"
    path.write_bytes(png_bytes(3, 3))
    registry.register(mint_grant(
        grant_id="g-src-000000000a", path=path, kind="image",
        expires_at=clock.now + 300,
    ))
    assert registry.revoke_all_for_session() == 1
    with pytest.raises(SourceImportError) as caught:
        registry.verify_before_commit("g-src-000000000a")
    assert caught.value.code == "SOURCE_GRANT_REVOKED"


def test_folder_grant_scope_validation(tmp_path, registry, clock):
    root = tmp_path / "folder"
    root.mkdir()
    members = []
    for name in ("1.png", "2.png"):
        target = root / name
        target.write_bytes(png_bytes(2, 2))
        members.append(target)
    entries = [
        {"entry_key": f"k{i}", "entry_id": None, "locator": name,
         "ordinal": i, "path": str(target), "facts": _facts_of(target)}
        for i, (name, target) in enumerate((("1.png", members[0]), ("2.png", members[1])))
    ]
    registry.register(mint_grant(
        grant_id="g-src-000000000b", path=members[0], kind="folder",
        expires_at=clock.now + 300, entries=entries,
    ))
    resolved = registry.resolve("g-src-000000000b")
    assert resolved.folder_root == str(root)
    assert len(resolved.folder_entries) == 2

    # member outside the first entry's root is refused
    outside = tmp_path / "outside.png"
    outside.write_bytes(png_bytes(2, 2))
    bad_entries = [dict(entries[0]), dict(entries[1])]
    bad_entries[1]["path"] = str(outside)
    bad_entries[1]["facts"] = _facts_of(outside)
    with pytest.raises(SourceImportError) as caught:
        registry.register(mint_grant(
            grant_id="g-src-000000000c", path=members[0], kind="folder",
            expires_at=clock.now + 300, entries=bad_entries,
        ))
    assert caught.value.code == "SOURCE_ACCESS_DENIED"


# ------------------------------------------------------- stdio wire dispatch
def _make_server(registry, planner, runtime) -> "CoreServiceServer":
    from types import SimpleNamespace

    from bootstrap.core_service import CoreServiceServer

    core = SimpleNamespace(
        source_read_refs=registry,
        referenced_planner=planner,
        referenced_import=runtime,
        export_history_store=None,
        export_job_store=None,
        export_target_refs=None,
        pipeline=None,
    )
    return CoreServiceServer(core, stdin=io.StringIO(), stdout=io.StringIO())


def _dispatch(server, request: dict) -> dict:
    line = json.dumps(request)
    response, _ = server._dispatch_request(line)
    return response


def _request(command: str, payload, *, channel=None, minor=3) -> dict:
    request = {
        "protocol": "new-manga.core",
        "version": {"major": 2, "minor": minor},
        "request_id": "req-1",
        "command": command,
        "payload": payload,
    }
    if channel:
        request["channel"] = channel
    return request


def _wire_headers() -> dict:
    return {
        "core_session_id": None,  # patched after server construction
        "host_session_id": SESSION,
        "host_session_credential": _b64u(b"c" * 32),
    }


def test_wire_ping_advertises_source_read_capability():
    server = _make_server(SourceReadGrantRegistry(), None, None)
    response = _dispatch(server, _request("core.ping", {}))
    assert response["result"]["capabilities"] == [
        "library.list_books", "source.read/1",
    ]


def test_wire_register_revoke_host_control(tmp_path, clock):
    registry = SourceReadGrantRegistry(clock=clock)
    server = _make_server(registry, None, None)
    # open the host session first
    open_request = {
        "protocol": "new-manga.core",
        "version": {"major": 2, "minor": 3},
        "request_id": "r0",
        "channel": "host-control",
        "command": "OpenHostSession",
        "payload": {
            "host_session_id": SESSION,
            "host_session_credential": _b64u(b"c" * 32),
        },
    }
    opened = _dispatch(server, open_request)
    core_session_id = opened["result"]["core_session_id"]

    path = tmp_path / "001.png"
    path.write_bytes(png_bytes(3, 3))
    grant = mint_grant(
        grant_id="g-src-000000000d", path=path, kind="image",
        expires_at=clock.now + 300,
    )
    register = _request("RegisterSourceReadGrant", grant, channel="host-control")
    register.update({
        "core_session_id": core_session_id,
        "host_session_id": SESSION,
        "host_session_credential": _b64u(b"c" * 32),
    })
    response = _dispatch(server, register)
    assert response["result"] == {"registered": True}

    revoke = _request(
        "RevokeSourceReadGrant",
        {"registry_id": "reg-1", "generation": 9, "grant_ids": ["g-src-000000000d"]},
        channel="host-control",
    )
    revoke.update({
        "core_session_id": core_session_id,
        "host_session_id": SESSION,
        "host_session_credential": _b64u(b"c" * 32),
    })
    response = _dispatch(server, revoke)
    assert response["result"] == {"revoked": True, "grants_revoked": 1}
    with pytest.raises(SourceImportError):
        registry.resolve("g-src-000000000d")


def test_wire_referenced_import_commands(tmp_path, repo, book_chapter, clock):
    from application.importing.referenced.pdf_probe import PdfiumSourceInspector
    from application.importing.referenced.planner import ReferencedImportPlanner
    from application.importing.referenced.runtime import ReferencedImportRuntime
    from infrastructure.importing import PillowImageDecoder

    registry = SourceReadGrantRegistry(clock=clock)
    planner = ReferencedImportPlanner(
        access=registry, repository=repo,
        project_of_chapter=lambda chapter: "b1",
        pdf_open=PdfiumSourceInspector().open,
    )
    runtime = ReferencedImportRuntime(
        repository=repo, access=registry, planner=planner,
        project_of_chapter=lambda chapter: "b1",
        image_decoder=PillowImageDecoder(),
        pdf_open=PdfiumSourceInspector().open,
    )
    server = _make_server(registry, planner, runtime)

    path = write_zip(tmp_path / "w.zip", [("001.png", png_bytes(2, 2))])
    registry.register(mint_grant(
        grant_id="g-src-000000000e", path=path, kind="zip",
        expires_at=clock.now + 300,
    ))

    plan = _dispatch(server, _request("PlanImportReferences", {
        "chapter_id": "c1", "grants": ["g-src-000000000e"],
        "duplicate_policy": "skip",
    }))
    assert plan["error"] is None
    plan_result = plan["result"]
    assert plan_result["sources"][0]["status"] == "ok"

    started = _dispatch(server, _request("StartImportReferences", {
        "chapter_id": "c1", "plan_id": plan_result["plan_id"],
        "plan_digest": plan_result["plan_digest"],
        "grants": ["g-src-000000000e"], "duplicate_policy": "skip",
        "operation_id": "op-wire-0000000001",
    }))
    assert started["result"]["accepted"] is True

    import time as _time

    deadline = _time.time() + 10
    receipt = None
    while _time.time() < deadline:
        receipt = _dispatch(server, _request("GetImportReceipt", {
            "operation_id": "op-wire-0000000001",
        }))
        if receipt["result"]["state"] in {"completed", "cancelled", "failed"}:
            break
        _time.sleep(0.01)
    assert receipt["result"]["state"] == "completed"
    assert receipt["result"]["totals"]["imported_pages"] == 1

    cancelled = _dispatch(server, _request("CancelImport", {
        "operation_id": "op-wire-0000000001",
    }))
    assert cancelled["result"]["accepted"] is False  # already terminal

    missing = _dispatch(server, _request("GetImportReceipt", {
        "operation_id": "op-wire-9999999999",
    }))
    assert missing["error"]["code"] == "SOURCE_OPERATION_NOT_FOUND"
    assert missing["error"]["category"] == "not_found"
    assert missing["error"]["retryable"] is False

    conflict = _dispatch(server, _request("PlanImportReferences", {
        "chapter_id": "c1", "grants": ["g-src-000000000e"],
        "duplicate_policy": "nope",
    }))
    assert conflict["error"]["code"] == "SOURCE_OPERATION_CONFLICT"


def test_wire_source_commands_fail_closed_without_assembly():
    server = _make_server(None, None, None)
    response = _dispatch(server, _request("PlanImportReferences", {
        "chapter_id": "c1", "grants": ["g"], "duplicate_policy": "skip",
    }))
    assert response["error"]["code"] == "CORE_CAPABILITY_MISSING"
