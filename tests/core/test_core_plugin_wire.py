"""PLUGIN-RUNTIME-1 AC1–AC4: the plugin runtime wire on the production Core.

Exercises the four additive application-channel commands at
``dispatch_request`` level on a real production assembly:

- ``plugins.list``               -> global switch + per-plugin snapshot;
- ``plugins.set_enabled``        -> the global kill switch (default OFF);
- ``plugins.set_plugin_enabled`` -> per-plugin enable (rejected plugins fail);
- ``plugins.audit_list``         -> the append-only ``plugin_events`` ledger.

They are ordinary application-channel commands (cleanup/backup precedent),
not HostControl: the frozen host-control envelope must keep refusing them,
and the protocol minor stays 3.
"""

from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
import sys

import pytest

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from bootstrap.core_service import (  # noqa: E402
    PROTOCOL_MAJOR,
    PROTOCOL_MINOR,
    CoreServiceServer,
    _HOST_CONTROL_COMMANDS,
    _PLUGIN_COMMANDS,
    assemble_production_core,
)


@pytest.fixture()
def core(tmp_path: Path):
    assembled = assemble_production_core(tmp_path / "data")
    try:
        yield assembled
    finally:
        assembled.conn.close()


def _request(server: CoreServiceServer, command: str, payload, request_id: str = "req-plugin-1") -> dict:
    request = {
        "protocol": "new-manga.core",
        "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
        "request_id": request_id,
        "command": command,
        "payload": payload,
    }
    response, should_exit = server.dispatch_request(json.dumps(request))
    assert not should_exit
    return response


def _write_plugin(core, plugin_id: str, *, permissions: tuple[str, ...] = ()) -> Path:
    directory = Path(core.data_root) / "plugins" / plugin_id
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "plugin.py").write_text(
        "def after_detect(payload):\n    return {'ok': True}\n", encoding="utf-8"
    )
    manifest = {
        "id": plugin_id,
        "name": f"Plugin {plugin_id}",
        "version": "1.0.0",
        "entry": "plugin.py",
        "hooks": ["after_detect"],
        "permissions": list(permissions),
    }
    (directory / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    return directory


def test_plugin_commands_are_application_channel_and_protocol_stays_3() -> None:
    assert _PLUGIN_COMMANDS == {
        "plugins.list",
        "plugins.set_enabled",
        "plugins.set_plugin_enabled",
        "plugins.audit_list",
    }
    assert not (_PLUGIN_COMMANDS & _HOST_CONTROL_COMMANDS)
    assert PROTOCOL_MINOR == 3


def test_list_plugins_reports_default_off_global_and_discovered_plugins(core) -> None:
    server = CoreServiceServer(core)
    _write_plugin(core, "acme-detect")
    _write_plugin(core, "acme-rejected", permissions=("files_read",))

    response = _request(server, "plugins.list", {})
    assert response["error"] is None
    result = response["result"]
    assert result["global_enabled"] is False
    assert result["plugin_root"].endswith("plugins")
    by_id = {item["plugin_id"]: item for item in result["plugins"]}
    assert by_id["acme-detect"]["status"] == "disabled"
    assert by_id["acme-detect"]["hooks"] == ["after_detect"]
    assert by_id["acme-rejected"]["status"] == "rejected"
    assert by_id["acme-rejected"]["reason"].startswith("PLUGIN_PERMISSIONS_UNSUPPORTED")


def test_global_and_per_plugin_switches_round_trip(core) -> None:
    server = CoreServiceServer(core)
    _write_plugin(core, "acme-detect")

    off = _request(server, "plugins.set_enabled", {"enabled": False})
    assert off["error"] is None
    assert off["result"] == {"global_enabled": False}

    on = _request(server, "plugins.set_enabled", {"enabled": True})
    assert on["result"] == {"global_enabled": True}

    enabled = _request(
        server, "plugins.set_plugin_enabled", {"plugin_id": "acme-detect", "enabled": True}
    )
    assert enabled["error"] is None
    assert enabled["result"] == {"plugin_id": "acme-detect", "enabled": True}

    listed = _request(server, "plugins.list", {})
    plugin = [item for item in listed["result"]["plugins"] if item["plugin_id"] == "acme-detect"][0]
    assert plugin["status"] == "enabled"
    assert plugin["enabled"] is True


def test_rejected_plugin_cannot_be_enabled_and_unknown_is_not_found(core) -> None:
    server = CoreServiceServer(core)
    _write_plugin(core, "acme-rejected", permissions=("files_read",))
    rejected = _request(
        server, "plugins.set_plugin_enabled", {"plugin_id": "acme-rejected", "enabled": True}
    )
    assert rejected["error"]["code"] == "PLUGIN_NOT_LOADED"
    assert rejected["error"]["category"] == "validation"
    assert rejected["error"]["retryable"] is False

    missing = _request(
        server, "plugins.set_plugin_enabled", {"plugin_id": "acme-absent", "enabled": True}
    )
    assert missing["error"]["code"] == "PLUGIN_NOT_FOUND"
    assert missing["error"]["category"] == "not_found"


def test_audit_list_returns_the_ledger(core) -> None:
    server = CoreServiceServer(core)
    _request(server, "plugins.set_enabled", {"enabled": True}, request_id="req-plugin-a")
    response = _request(server, "plugins.audit_list", {"limit": 10})
    assert response["error"] is None
    events = response["result"]
    assert events and events[0]["event_type"] == "enabled"
    assert events[0]["plugin_id"] == "__global__"
    assert "detail" in events[0]


def test_malformed_payloads_are_validation_errors(core) -> None:
    server = CoreServiceServer(core)
    not_object = _request(server, "plugins.list", [1, 2, 3])
    assert not_object["error"]["code"] == "PLUGIN_INVALID_REQUEST"
    assert not_object["error"]["category"] == "validation"
    assert not_object["error"]["retryable"] is False

    bad_flag = _request(server, "plugins.set_enabled", {"enabled": "yes"})
    assert bad_flag["error"]["code"] == "PLUGIN_INVALID_REQUEST"

    bad_limit = _request(server, "plugins.audit_list", {"limit": 0})
    assert bad_limit["error"]["code"] == "PLUGIN_INVALID_REQUEST"


def test_core_without_the_runtime_fails_closed(core) -> None:
    server = CoreServiceServer(replace(core, plugins=None))
    response = _request(server, "plugins.list", {})
    assert response["error"]["code"] == "CORE_UNAVAILABLE"
    assert response["error"]["category"] == "unavailable"
