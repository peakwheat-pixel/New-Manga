from __future__ import annotations

import json
from pathlib import Path
import sys

import pytest

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from bootstrap.core_service import CoreServiceServer, PROTOCOL_MAJOR, PROTOCOL_MINOR, _P15_PROTOCOL_MINOR, assemble_production_core
from domain.books.entities import ReadingDirection
from domain.pages.entities import Page
from infrastructure.transport.stdlib import StdlibTransport
from ports.network.profiles import MODE_HTTP, NetworkProfile
from ports.network.transport import TcpConnectionError, TransportRequest
from ports.providers.profiles import ProviderProfile


@pytest.fixture()
def env(tmp_path: Path):
    core = assemble_production_core(tmp_path / "data")
    server = CoreServiceServer(core)
    try:
        yield core, server
    finally:
        server.close()
        core.conn.close()


def request(server, command: str, payload: dict, *, minor: int = _P15_PROTOCOL_MINOR) -> dict:
    response, should_exit = server.dispatch_request(json.dumps({
        "protocol": "new-manga.core",
        "version": {"major": PROTOCOL_MAJOR, "minor": minor},
        "request_id": "p15-test",
        "command": command,
        "payload": payload,
    }))
    assert not should_exit
    return response


def create_profile(server, *, provider_id="shared-provider", capabilities=None, name="Primary") -> dict:
    response = request(server, "settings_provider_profiles_create", {
        "provider_id": provider_id,
        "display_name": name,
        "capabilities": capabilities or ["OCR"],
        "endpoint": "https://api.example.test/v1",
        "model": "model-a",
        "network_profile_id": None,
        "enabled": True,
    })
    assert response["error"] is None
    return response["result"]["profile"]


def assert_safe_error(response: dict, message_key: str) -> None:
    error = response["error"]
    assert error["details"] == {
        "phase": error["details"]["phase"],
        "action": error["details"]["action"],
        "message_key": message_key,
    }
    assert set(error["details"]) == {"phase", "action", "message_key"}
    assert message_key in error["message"]
    assert "CredentialRef" not in json.dumps(response)
    assert "secret-marker" not in json.dumps(response)
    assert "C:\\private" not in json.dumps(response)


def test_provider_profile_crud_is_typed_and_allows_same_provider(env):
    _core, server = env
    first = create_profile(server, capabilities=["OCR", "Rendering"])
    second = create_profile(server, name="Second")
    assert first["profile_id"] != second["profile_id"]
    assert first["provider_id"] == second["provider_id"] == "shared-provider"
    assert first["capabilities"] == ["OCR", "Rendering"]
    assert first["credential_state"] == "missing"

    updated = request(server, "settings_provider_profiles_update", {
        "profile_id": first["profile_id"],
        "display_name": "Updated",
        "capabilities": ["OCR"],
        "endpoint": "https://api.example.test/v2",
        "model": "model-b",
        "network_profile_id": None,
        "enabled": True,
    })
    assert updated["result"]["profile"]["display_name"] == "Updated"
    assert updated["result"]["profile"]["provider_id"] == "shared-provider"
    listed = request(server, "settings_provider_profiles_list", {})["result"]["profiles"]
    assert len(listed) == 2
    assert {profile["display_name"] for profile in listed} == {"Second", "Updated"}
    deleted = request(server, "settings_provider_profiles_delete", {"profile_id": second["profile_id"]})
    assert deleted["result"] == {"deleted": True}


@pytest.mark.parametrize("changes", [
    {"unknown": "value"},
    {"enabled": 1},
    {"capabilities": ["OCR", "OCR"]},
    {"capabilities": ["NotACapability"]},
    {"endpoint": "https://user:secret-marker@api.example.test"},
    {"endpoint": "https://api.example.test/?token=secret-marker"},
    {"endpoint": r"C:\private\secret.png"},
])
def test_provider_profile_rejects_invalid_fields_without_leaking_input(env, changes):
    _core, server = env
    payload = {
        "provider_id": "provider",
        "display_name": "Profile",
        "capabilities": ["OCR"],
        "endpoint": "https://api.example.test/v1",
        "model": "model-a",
        "network_profile_id": None,
        "enabled": True,
    }
    payload.update(changes)
    response = request(server, "settings_provider_profiles_create", payload)
    assert_safe_error(response, "SETTINGS_INVALID_INPUT")
    assert request(server, "settings_provider_profiles_list", {})["result"] == {"profiles": []}


def test_capability_binding_resolution_priority_and_no_fallback(env):
    core, server = env
    global_profile = create_profile(server, name="Global")
    book_profile = create_profile(server, name="Book")
    chapter_profile = create_profile(server, name="Chapter")
    disabled_profile = create_profile(server, name="Disabled")
    book = core.library.create_book("Book", default_reading_direction=ReadingDirection.LTR)
    chapter = core.library.create_chapter(
        book.book_id, "Chapter", reading_direction=ReadingDirection.RTL
    )

    set_binding = lambda scope, profile: request(server, "settings_provider_bindings_set", {
        "scope": scope, "capability": "OCR", "profile_id": profile["profile_id"]
    })
    set_binding({"kind": "global"}, global_profile)
    set_binding({"kind": "book", "book_id": book.book_id}, book_profile)
    set_binding({"kind": "chapter", "chapter_id": chapter.chapter_id}, chapter_profile)

    resolved = request(server, "settings_provider_bindings_resolve", {
        "capability": "OCR", "chapter_id": chapter.chapter_id
    })["result"]
    assert resolved == {
        "profile_id": chapter_profile["profile_id"],
        "source": {"kind": "chapter", "chapter_id": chapter.chapter_id},
    }
    request(server, "settings_provider_bindings_clear", {
        "scope": {"kind": "chapter", "chapter_id": chapter.chapter_id}, "capability": "OCR"
    })
    resolved = request(server, "settings_provider_bindings_resolve", {
        "capability": "OCR", "chapter_id": chapter.chapter_id
    })["result"]
    assert resolved["profile_id"] == book_profile["profile_id"]
    assert resolved["source"] == {"kind": "book", "book_id": book.book_id}
    request(server, "settings_provider_bindings_clear", {
        "scope": {"kind": "book", "book_id": book.book_id}, "capability": "OCR"
    })
    resolved = request(server, "settings_provider_bindings_resolve", {
        "capability": "OCR", "chapter_id": chapter.chapter_id
    })["result"]
    assert resolved == {
        "profile_id": global_profile["profile_id"],
        "source": {"kind": "global"},
    }
    request(server, "settings_provider_bindings_clear", {
        "scope": {"kind": "global"}, "capability": "OCR"
    })
    assert request(server, "settings_provider_bindings_resolve", {
        "capability": "OCR", "chapter_id": chapter.chapter_id
    })["result"] == {"profile_id": None, "source": None}
    set_binding({"kind": "book", "book_id": book.book_id}, book_profile)

    set_binding({"kind": "chapter", "chapter_id": chapter.chapter_id}, disabled_profile)
    request(server, "settings_provider_profiles_update", {
        "profile_id": disabled_profile["profile_id"],
        "display_name": "Disabled",
        "capabilities": ["OCR"],
        "endpoint": "https://api.example.test/v1",
        "model": "model-a",
        "network_profile_id": None,
        "enabled": False,
    })
    blocked = request(server, "settings_provider_bindings_resolve", {
        "capability": "OCR", "chapter_id": chapter.chapter_id
    })
    assert_safe_error(blocked, "SETTINGS_CONFLICT")


def test_binding_rejects_unknown_profile_and_invalid_scope(env):
    _core, server = env
    missing = request(server, "settings_provider_bindings_set", {
        "scope": {"kind": "global"},
        "capability": "OCR",
        "profile_id": "missing-profile",
        "credential_ref": "secret-marker",
    })
    assert_safe_error(missing, "SETTINGS_INVALID_INPUT")
    missing = request(server, "settings_provider_bindings_set", {
        "scope": {"kind": "book", "book_id": "missing-book"},
        "capability": "OCR",
        "profile_id": "missing-profile",
    })
    assert_safe_error(missing, "SETTINGS_ITEM_NOT_FOUND")


def test_run_snapshot_freezes_profile_and_setting_provenance_without_references(env):
    core, server = env
    book = core.library.create_book("Book", default_reading_direction=ReadingDirection.LTR)
    chapter = core.library.create_chapter(
        book.book_id, "Chapter", reading_direction=ReadingDirection.RTL
    )
    core.repository.add_page(Page(
        page_id="page-p15",
        chapter_id=chapter.chapter_id,
        source_filename="page.png",
        source_order=1,
        sort_order=1,
        source_hash="hash-p15",
        source_size_bytes=1,
        width=10,
        height=10,
        managed_original_ref=f"books/{book.book_id}/chapters/{chapter.chapter_id}/page.png",
    ))
    profile = create_profile(server)
    lower_priority_profile = create_profile(server, name="Chapter Default")
    request(server, "settings_provider_bindings_set", {
        "scope": {"kind": "global"},
        "capability": "OCR",
        "profile_id": lower_priority_profile["profile_id"],
    })
    request(server, "settings_provider_bindings_set", {
        "scope": {"kind": "chapter", "chapter_id": chapter.chapter_id},
        "capability": "OCR",
        "profile_id": lower_priority_profile["profile_id"],
    })
    stored = core.provider_profile_store.get_profile(profile["profile_id"])
    core.provider_profile_store.update_profile(ProviderProfile(
        provider_profile_id=stored.provider_profile_id,
        name=stored.name,
        provider_type=stored.provider_type,
        capabilities=stored.capabilities,
        base_url=stored.base_url,
        model=stored.model,
        credential_ref="ref-secret-marker",
        is_enabled=stored.is_enabled,
    ))
    core.pipeline_defaults.save_settings_section("reading", {"direction": "rtl"})
    core.pipeline_defaults.save_settings_section("sfx", {"policy": "manual"})

    # Isolate StartRun acceptance from the asynchronous scheduler worker.
    server._run_owner = True
    core.pipeline.set_scheduler_owner(True)
    started = request(server, "StartRun", {
        "command": "translate_all",
        "scope": {"kind": "chapter", "chapter_id": chapter.chapter_id},
        "idempotency_key": "p15-run-1",
        "overrides": {
            "provider_profiles": {"OCR": profile["profile_id"]},
            "settings": {"reading": {"direction": "ltr"}},
        },
    })
    assert started["error"] is None
    run_id = started["result"]["run_id"]

    updated = request(server, "settings_provider_profiles_update", {
        "profile_id": profile["profile_id"],
        "display_name": "Edited after Run",
        "capabilities": ["OCR"],
        "endpoint": "https://api.example.test/changed",
        "model": "model-new",
        "network_profile_id": None,
        "enabled": True,
    })
    assert updated["error"] is None

    frozen = request(server, "settings_provider_run_snapshot_get", {"run_id": run_id})
    assert frozen["error"] is None
    binding = frozen["result"]["bindings"][0]
    assert binding["display_name"] == "Primary"
    assert binding["endpoint"] == "https://api.example.test/v1"
    assert binding["provider_credential_state_at_snapshot"] == "configured"
    assert binding["source"] == {"kind": "run", "run_id": run_id}
    assert "credential_ref" not in json.dumps(frozen)
    assert "ref-secret-marker" not in json.dumps(frozen)

    overrides_response = request(server, "settings_resolve_overrides", {
        "keys": ["reading.direction", "sfx.policy"],
        "run_id": run_id,
    })
    assert overrides_response["error"] is None, overrides_response
    overrides = overrides_response["result"]["values"]
    assert overrides == [
        {"key": "reading.direction", "value": "ltr", "source": "run", "source_id": run_id, "is_default": False},
        {"key": "sfx.policy", "value": "manual", "source": "global", "is_default": False},
    ]
    resolved = request(server, "settings_provider_bindings_resolve", {
        "capability": "OCR", "run_id": run_id
    })["result"]
    assert resolved == {
        "profile_id": profile["profile_id"],
        "source": {"kind": "run", "run_id": run_id},
    }
    conflict = request(server, "settings_provider_profiles_delete", {"profile_id": profile["profile_id"]})
    assert_safe_error(conflict, "SETTINGS_CONFLICT")


def test_override_layers_and_unsupported_value_fail_closed(env):
    core, server = env
    book = core.library.create_book("Book", default_reading_direction=ReadingDirection.LTR)
    chapter = core.library.create_chapter(
        book.book_id, "Chapter", reading_direction=ReadingDirection.RTL
    )
    core.pipeline_defaults.save_settings_section("reading", {"direction": "rtl"})
    global_value = request(server, "settings_resolve_overrides", {
        "keys": ["reading.direction"]
    })["result"]["values"][0]
    book_value = request(server, "settings_resolve_overrides", {
        "keys": ["reading.direction"], "book_id": book.book_id
    })["result"]["values"][0]
    chapter_value = request(server, "settings_resolve_overrides", {
        "keys": ["reading.direction"], "chapter_id": chapter.chapter_id
    })["result"]["values"][0]
    assert (global_value["value"], global_value["source"]) == ("rtl", "global")
    assert (book_value["value"], book_value["source"]) == ("ltr", "book")
    assert (chapter_value["value"], chapter_value["source"]) == ("rtl", "chapter")
    core.pipeline_defaults.save_settings_section("reading", {"direction": "unsupported-secret-marker"})
    overridden_unsafe = request(server, "settings_resolve_overrides", {
        "keys": ["reading.direction"], "book_id": book.book_id
    })["result"]["values"][0]
    assert (overridden_unsafe["value"], overridden_unsafe["source"]) == ("ltr", "book")
    assert_safe_error(request(server, "settings_resolve_overrides", {
        "keys": ["reading.direction"]
    }), "SETTINGS_UNAVAILABLE")

    default_sfx = request(server, "settings_resolve_overrides", {"keys": ["sfx.policy"]})["result"]["values"][0]
    assert default_sfx == {"key": "sfx.policy", "value": "skip", "source": "global", "is_default": True}
    core.pipeline_defaults.save_settings_section("translation", {"parameters": {"token": "secret-marker"}})
    unsafe = request(server, "settings_resolve_overrides", {"keys": ["translation.parameters"]})
    assert_safe_error(unsafe, "SETTINGS_UNAVAILABLE")


def test_new_settings_wire_requires_27_and_old_surface_keeps_23(env):
    _core, server = env
    old_ping = request(server, "core.ping", {}, minor=3)
    assert old_ping["version"] == {"major": 2, "minor": 3}
    assert old_ping["result"]["protocol_version"] == {"major": 2, "minor": 3}
    new_settings = request(server, "settings_provider_profiles_list", {}, minor=3)
    assert new_settings["version"] == {"major": 2, "minor": 7}
    assert_safe_error(new_settings, "SETTINGS_INVALID_INPUT")
    assert PROTOCOL_MINOR == 3
    assert _P15_PROTOCOL_MINOR == 7


class _MemoryCredentials:
    def __init__(self):
        self.refs = set()

    def has_credential(self, ref):
        return ref in self.refs

    def delete_credential(self, ref):
        self.refs.discard(ref)


def create_network_profile(server, *, mode="Direct", endpoint=None, **options):
    return request(server, "settings_network_profiles_create", {
        "display_name": "Network",
        "mode": mode,
        "proxy_endpoint": endpoint,
        **options,
    })


@pytest.mark.parametrize("mode,endpoint", [
    ("PAC", "http://proxy.example.test:8080"),
    ("HTTP", "https://proxy.example.test:8080"),
    ("HTTPS", "http://proxy.example.test:8080"),
    ("SOCKS5", "https://proxy.example.test:1080"),
    ("Direct", "http://proxy.example.test:8080"),
    ("System", "http://proxy.example.test:8080"),
    ("HTTP", "http://user:secret-marker@proxy.example.test:8080"),
    ("HTTP", "http://proxy.example.test:8080?"),
    ("HTTP", "http://proxy.example.test:8080#"),
])
def test_network_profile_rejects_invalid_mode_endpoint_and_embedded_credentials(env, mode, endpoint):
    _core, server = env
    response = create_network_profile(server, mode=mode, endpoint=endpoint)
    assert_safe_error(response, "SETTINGS_INVALID_INPUT")
    assert "secret-marker" not in json.dumps(response)
    assert request(server, "settings_network_profiles_list", {})["result"] == {"profiles": []}


def test_network_profile_crud_defaults_tls_confirmation_and_fallback(env):
    _core, server = env
    created = create_network_profile(server, mode="HTTP", endpoint="http://proxy.example.test:8080")
    assert created["version"] == {"major": 2, "minor": 7}
    profile = created["result"]["profile"]
    assert profile["verify_tls"] is True
    assert profile["tls_verification_state"] == "enabled"
    assert profile["allow_proxy_failure_direct_fallback"] is False
    assert profile["credential_state"] == "missing"

    unconfirmed = request(server, "settings_network_profiles_update", {
        "network_profile_id": profile["network_profile_id"],
        "display_name": "Changed",
        "mode": "Direct",
        "proxy_endpoint": None,
        "verify_tls": False,
        "allow_proxy_failure_direct_fallback": True,
    })
    assert_safe_error(unconfirmed, "TLS_CONFIRMATION_REQUIRED")

    updated = request(server, "settings_network_profiles_update", {
        "network_profile_id": profile["network_profile_id"],
        "display_name": "Changed",
        "mode": "HTTPS",
        "proxy_endpoint": "https://proxy.example.test:8443",
        "verify_tls": False,
        "confirm_disable_tls_verification": True,
        "allow_proxy_failure_direct_fallback": True,
    })["result"]["profile"]
    assert updated["mode"] == "HTTPS"
    assert updated["proxy_endpoint"] == "https://proxy.example.test:8443"
    assert updated["tls_verification_state"] == "disabled_confirmed"
    assert updated["allow_proxy_failure_direct_fallback"] is True

    listed = request(server, "settings_network_profiles_list", {})["result"]["profiles"]
    assert listed == [updated]
    assert request(server, "settings_network_profiles_delete", {
        "network_profile_id": profile["network_profile_id"]
    })["result"] == {"deleted": True}


def test_network_profile_tls_confirmation_at_creation_and_bad_types_fail_closed(env):
    _core, server = env
    response = create_network_profile(server, mode="Direct", endpoint=None, verify_tls=False)
    assert_safe_error(response, "TLS_CONFIRMATION_REQUIRED")

    created = create_network_profile(
        server,
        mode="System",
        endpoint=None,
        verify_tls=False,
        confirm_disable_tls_verification=True,
        allow_proxy_failure_direct_fallback=True,
    )["result"]["profile"]
    assert created["verify_tls"] is False
    assert created["allow_proxy_failure_direct_fallback"] is True

    bad_type = create_network_profile(server, mode="Direct", endpoint=None, verify_tls=1)
    assert_safe_error(bad_type, "SETTINGS_INVALID_INPUT")
    bad_fallback = create_network_profile(
        server, mode="Direct", endpoint=None, allow_proxy_failure_direct_fallback="true"
    )
    assert_safe_error(bad_fallback, "SETTINGS_INVALID_INPUT")


def test_network_profile_default_and_resolver_precedence(env, monkeypatch):
    core, server = env
    provider_network = create_network_profile(server, mode="HTTP", endpoint="http://provider-proxy.example.test:8080")["result"]["profile"]
    global_network = create_network_profile(server, mode="Direct", endpoint=None)["result"]["profile"]
    provider = request(server, "settings_provider_profiles_create", {
        "provider_id": "provider-a",
        "display_name": "Provider A",
        "capabilities": ["OCR"],
        "endpoint": "https://api.example.test/v1",
        "model": "model-a",
        "network_profile_id": provider_network["network_profile_id"],
        "enabled": True,
    })["result"]["profile"]

    monkeypatch.setattr("bootstrap.settings_commands.urllib.request.getproxies", lambda: {"https": "http://system-secret"})
    provider_result = request(server, "settings_network_profile_resolve", {
        "provider_profile_id": provider["profile_id"]
    })["result"]
    assert provider_result == {
        "network_profile_id": provider_network["network_profile_id"],
        "mode": "HTTP",
        "source": "provider",
    }
    assert request(server, "settings_network_profile_default_set", {
        "network_profile_id": global_network["network_profile_id"]
    })["result"] == {"network_profile_id": global_network["network_profile_id"]}
    assert core.network_profile_store.get_global_default_profile_id() == global_network["network_profile_id"]
    create_network_profile(server)
    assert core.network_profile_store.get_global_default_profile_id() == global_network["network_profile_id"]
    assert request(server, "settings_network_profile_resolve", {})["result"] == {
        "network_profile_id": global_network["network_profile_id"],
        "mode": "Direct",
        "source": "global",
    }

    assert request(server, "settings_network_profile_default_clear", {})["result"] == {
        "network_profile_id": None
    }
    system_result = request(server, "settings_network_profile_resolve", {})["result"]
    assert system_result == {"network_profile_id": None, "mode": "System", "source": "system"}
    assert "system-secret" not in json.dumps(system_result)
    monkeypatch.setattr("bootstrap.settings_commands.urllib.request.getproxies", lambda: {})
    assert request(server, "settings_network_profile_resolve", {})["result"] == {
        "network_profile_id": None,
        "mode": "Direct",
        "source": "direct",
    }

    missing = request(server, "settings_network_profile_default_set", {
        "network_profile_id": "missing-profile"
    })
    assert_safe_error(missing, "SETTINGS_ITEM_NOT_FOUND")
    assert core.network_profile_store.get_global_default_profile_id() is None


def test_network_profile_delete_rejects_global_and_provider_references(env):
    _core, server = env
    profile = create_network_profile(server)["result"]["profile"]
    profile_id = profile["network_profile_id"]
    request(server, "settings_network_profile_default_set", {"network_profile_id": profile_id})
    assert_safe_error(request(server, "settings_network_profiles_delete", {
        "network_profile_id": profile_id
    }), "SETTINGS_CONFLICT")
    request(server, "settings_network_profile_default_clear", {})

    provider = request(server, "settings_provider_profiles_create", {
        "provider_id": "provider-a",
        "display_name": "Provider A",
        "capabilities": ["OCR"],
        "endpoint": "https://api.example.test/v1",
        "model": "model-a",
        "network_profile_id": profile_id,
        "enabled": True,
    })["result"]["profile"]
    assert_safe_error(request(server, "settings_network_profiles_delete", {
        "network_profile_id": profile_id
    }), "SETTINGS_CONFLICT")
    request(server, "settings_provider_profiles_update", {
        "profile_id": provider["profile_id"],
        "display_name": "Provider A",
        "capabilities": ["OCR"],
        "endpoint": "https://api.example.test/v1",
        "model": "model-a",
        "network_profile_id": None,
        "enabled": True,
    })
    assert request(server, "settings_network_profiles_delete", {
        "network_profile_id": profile_id
    })["result"] == {"deleted": True}


def test_network_profile_delete_rejects_protected_run_snapshot_reference(env):
    core, server = env
    book = core.library.create_book("Book")
    chapter = core.library.create_chapter(book.book_id, "Chapter")
    core.repository.add_page(Page(
        page_id="page-network-snapshot",
        chapter_id=chapter.chapter_id,
        source_filename="page.png",
        source_order=1,
        sort_order=1,
        source_hash="hash-network-snapshot",
        source_size_bytes=1,
        width=10,
        height=10,
        managed_original_ref=f"books/{book.book_id}/chapters/{chapter.chapter_id}/page.png",
    ))
    network = create_network_profile(server, mode="HTTPS", endpoint="https://proxy.example.test:8443")["result"]["profile"]
    provider = request(server, "settings_provider_profiles_create", {
        "provider_id": "provider-a",
        "display_name": "Provider A",
        "capabilities": ["OCR"],
        "endpoint": "https://api.example.test/v1",
        "model": "model-a",
        "network_profile_id": network["network_profile_id"],
        "enabled": True,
    })["result"]["profile"]
    server._run_owner = True
    core.pipeline.set_scheduler_owner(True)
    started = request(server, "StartRun", {
        "command": "translate_all",
        "scope": {"kind": "chapter", "chapter_id": chapter.chapter_id},
        "idempotency_key": "network-snapshot-run",
        "overrides": {"provider_profiles": {"OCR": provider["profile_id"]}},
    })
    assert started["error"] is None
    assert_safe_error(request(server, "settings_network_profiles_delete", {
        "network_profile_id": network["network_profile_id"]
    }), "SETTINGS_CONFLICT")


def test_proxy_failure_does_not_retry_direct_by_default(monkeypatch):
    transport = StdlibTransport()
    profile = NetworkProfile(
        network_profile_id="proxy-profile",
        name="Proxy",
        mode=MODE_HTTP,
        http_proxy="http://proxy.example.test:8080",
    )
    attempted_routes = []

    def fail_proxy(_request, _profile, route):
        attempted_routes.append(route)
        raise TcpConnectionError("proxy unavailable")

    monkeypatch.setattr(transport, "_send_once", fail_proxy)
    with pytest.raises(TcpConnectionError):
        transport.send(
            TransportRequest(method="GET", url="https://api.example.test/v1"),
            profile,
        )
    assert len(attempted_routes) == 1
    assert attempted_routes[0].via_proxy is True
    assert attempted_routes[0].proxy_host == "proxy.example.test"


def test_credential_binding_validates_owner_and_never_returns_reference(env):
    core, server = env
    core.credential_store = _MemoryCredentials()
    first = create_profile(server, name="First")
    second = create_profile(server, name="Second")
    wrong_ref = f"NewManga/provider/{second['profile_id']}/host-ref"
    core.credential_store.refs.add(wrong_ref)
    unauthorized = request(server, "BindProfileCredential", {
        "target": {"kind": "provider_api", "profile_id": first["profile_id"]},
        "credential_ref": wrong_ref,
    })
    assert_safe_error(unauthorized, "SETTINGS_INVALID_INPUT")
    assert wrong_ref not in json.dumps(unauthorized)

    credential_ref = f"NewManga/provider/{first['profile_id']}/host-ref"
    core.credential_store.refs.add(credential_ref)
    bound = request(server, "BindProfileCredential", {
        "target": {"kind": "provider_api", "profile_id": first["profile_id"]},
        "credential_ref": credential_ref,
    })
    assert bound["result"] == {"state": "configured"}
    listed = request(server, "settings_provider_profiles_list", {})["result"]["profiles"]
    first_projection = next(item for item in listed if item["profile_id"] == first["profile_id"])
    assert first_projection["credential_state"] == "configured"
    assert credential_ref not in json.dumps(bound)
    assert credential_ref not in json.dumps(listed)
    assert "credential_ref" not in json.dumps(listed)

    cleared = request(server, "ClearProfileCredential", {
        "target": {"kind": "provider_api", "profile_id": first["profile_id"]}
    })
    assert cleared["result"] == {"state": "missing"}
    assert not core.credential_store.has_credential(credential_ref)
    assert core.provider_profile_store.get_profile(first["profile_id"]).credential_ref is None
    profiles = request(server, "settings_provider_profiles_list", {})["result"]["profiles"]
    first_projection = next(item for item in profiles if item["profile_id"] == first["profile_id"])
    assert first_projection["credential_state"] == "missing"


def test_credential_replace_failure_preserves_old_binding_and_removes_new_ref(env, monkeypatch):
    core, server = env
    core.credential_store = _MemoryCredentials()
    profile = create_profile(server)
    old_ref = f"NewManga/provider/{profile['profile_id']}/old"
    new_ref = f"NewManga/provider/{profile['profile_id']}/new"
    core.credential_store.refs.update({old_ref, new_ref})
    target = {"kind": "provider_api", "profile_id": profile["profile_id"]}
    assert request(server, "BindProfileCredential", {"target": target, "credential_ref": old_ref})["error"] is None

    store = core.provider_profile_store
    update = store.update_profile
    def fail_new_binding(item):
        if item.credential_ref == new_ref:
            raise OSError("C:/private/secret-marker")
        update(item)
    monkeypatch.setattr(store, "update_profile", fail_new_binding)

    failed = request(server, "BindProfileCredential", {"target": target, "credential_ref": new_ref})
    assert_safe_error(failed, "SETTINGS_UNAVAILABLE")
    assert new_ref not in json.dumps(failed)
    assert new_ref not in core.credential_store.refs
    assert old_ref in core.credential_store.refs
    assert store.get_profile(profile["profile_id"]).credential_ref == old_ref


def test_cleared_provider_does_not_resolve_to_another_provider(env):
    core, server = env
    core.credential_store = _MemoryCredentials()
    first = create_profile(server, provider_id="same-provider", name="First")
    second = create_profile(server, provider_id="same-provider", name="Second")
    first_ref = f"NewManga/provider/{first['profile_id']}/first"
    second_ref = f"NewManga/provider/{second['profile_id']}/second"
    core.credential_store.refs.update({first_ref, second_ref})
    for profile, ref in ((first, first_ref), (second, second_ref)):
        assert request(server, "BindProfileCredential", {
            "target": {"kind": "provider_api", "profile_id": profile["profile_id"]},
            "credential_ref": ref,
        })["error"] is None
    request(server, "settings_provider_bindings_set", {
        "scope": {"kind": "global"},
        "capability": "OCR",
        "profile_id": first["profile_id"],
    })

    request(server, "ClearProfileCredential", {
        "target": {"kind": "provider_api", "profile_id": first["profile_id"]}
    })
    resolved = request(server, "settings_provider_bindings_resolve", {
        "capability": "OCR"
    })["result"]
    assert resolved["profile_id"] == first["profile_id"]
    assert resolved["profile_id"] != second["profile_id"]
    assert core.provider_profile_store.get_profile(first["profile_id"]).credential_ref is None
    assert core.provider_profile_store.get_profile(second["profile_id"]).credential_ref == second_ref
    assert second_ref in core.credential_store.refs


def test_proxy_credential_binding_is_profile_scoped_and_secret_free(env):
    core, server = env
    core.credential_store = _MemoryCredentials()
    network = create_network_profile(server, mode="SOCKS5", endpoint="socks5://proxy.example.test:1080")["result"]["profile"]
    credential_ref = f"NewManga/proxy/{network['network_profile_id']}/proxy-auth"
    core.credential_store.refs.add(credential_ref)
    target = {"kind": "proxy_auth", "network_profile_id": network["network_profile_id"]}
    bound = request(server, "BindProfileCredential", {"target": target, "credential_ref": credential_ref})
    assert bound["result"] == {"state": "configured"}
    profile = request(server, "settings_network_profiles_list", {})["result"]["profiles"][0]
    assert profile["credential_state"] == "configured"
    assert credential_ref not in json.dumps(profile)
    assert request(server, "ClearProfileCredential", {"target": target})["result"] == {"state": "missing"}
    assert not core.credential_store.has_credential(credential_ref)


def test_private_credential_commands_require_p15_minor_seven_and_test_command_stays_absent(env):
    _core, server = env
    invalid_version = request(server, "BindProfileCredential", {}, minor=3)
    assert invalid_version["version"] == {"major": 2, "minor": 7}
    assert_safe_error(invalid_version, "SETTINGS_INVALID_INPUT")
    assert request(server, "settings_network_profiles_test", {}, minor=7)["error"]["code"] == "UNKNOWN_COMMAND"
