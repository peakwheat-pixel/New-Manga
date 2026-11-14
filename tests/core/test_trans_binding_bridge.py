"""TRANS-BINDING-BRIDGE (L1-T-A): P15 profiles/bindings → run-side provider settings.

The Run runtime reads provider configuration from the single ``pipeline_defaults``
row (``settings["providers"]["profiles"][profile_id]`` + ``provider_bindings[step]``),
while P15 persists to JSON stores. These tests pin the bridge that joins them.

Every test drives the REAL Core command surface (``CoreServiceServer`` +
``assemble_production_core``); nothing is stubbed at the seam under test, so a
removal of the mirror turns them RED (no profile under ``settings``, no step
binding, or a half-written store).
"""

from __future__ import annotations

import json
from pathlib import Path
import sys

import pytest

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from application.settings.errors import BindingValidationError  # noqa: E402
from bootstrap.core_service import (  # noqa: E402
    PROTOCOL_MAJOR,
    PROTOCOL_MINOR,
    CoreServiceServer,
    _P15_PROTOCOL_MINOR,
    assemble_production_core,
)
from infrastructure.providers.fallback import chain_from_binding  # noqa: E402
from infrastructure.providers.runtime import (  # noqa: E402
    PROVIDER_OPENAI_TRANSLATION,
    _apply_profile_bindings,
)


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
        "request_id": "trans-binding",
        "command": command,
        "payload": payload,
    }))
    assert not should_exit
    return response


def create_profile(
    server,
    *,
    capabilities=("Translation",),
    endpoint: str = "https://api.example.test/v1",
    model: str = "model-a",
    name: str = "Primary",
) -> dict:
    response = request(server, "settings_provider_profiles_create", {
        "provider_id": "shared-provider",
        "display_name": name,
        "capabilities": list(capabilities),
        "endpoint": endpoint,
        "model": model,
        "network_profile_id": None,
        "enabled": True,
    })
    assert response["error"] is None, response["error"]
    return response["result"]["profile"]


def mirror_state(core) -> tuple[dict, dict]:
    defaults = core.pipeline_defaults.read()
    providers = defaults.settings.get("providers") or {}
    return dict(providers.get("profiles") or {}), dict(defaults.provider_bindings)


# ---------------------------------------------------------------- AC1 / AC6

def test_profile_and_binding_are_mirrored_into_run_settings(env) -> None:
    core, server = env
    profile = create_profile(server)
    profile_id = profile["profile_id"]

    bound = request(server, "settings_provider_bindings_set", {
        "scope": {"kind": "global"}, "capability": "Translation", "profile_id": profile_id,
    })
    assert bound["error"] is None, bound["error"]

    profiles, bindings = mirror_state(core)
    assert profile_id in profiles, f"profile was not mirrored: {profiles}"
    entry = profiles[profile_id]
    # AC1 key set: exactly what runtime.providers reads (plus the observability list).
    assert entry["provider_type"] == "shared-provider"
    assert entry["base_url"] == "https://api.example.test/v1"
    assert entry["model"] == "model-a"
    assert entry["enabled"] is True
    assert entry["credential_ref"] is None
    assert entry["capabilities"] == ["translation"]
    assert entry["proxy_policy"] == "inherit"
    assert entry["network_profile_id"] == ""
    assert entry["options"] == {}

    # The step binding is what handlers._chain reads; a missing one is the actual
    # PROVIDER_NOT_CONFIGURED source.
    assert bindings["translate"] == profile_id
    chain = chain_from_binding(bindings["translate"])
    assert chain is not None and chain.primary == profile_id

    # And the runtime projection accepts the mirrored pair: the user profile is
    # copied onto the fixed registry slot and aliased per capability.
    effective, aliases = _apply_profile_bindings(
        core.pipeline_defaults.read().settings, core.pipeline_defaults.read().provider_bindings
    )
    projected = effective["providers"]["profiles"][PROVIDER_OPENAI_TRANSLATION]
    assert projected["base_url"] == "https://api.example.test/v1"
    assert projected["provider_type"] == "shared-provider"
    assert aliases[(profile_id, "translation")] == PROVIDER_OPENAI_TRANSLATION


def test_profile_update_and_delete_keep_the_mirror_in_sync(env) -> None:
    core, server = env
    profile = create_profile(server)
    profile_id = profile["profile_id"]

    updated = request(server, "settings_provider_profiles_update", {
        "profile_id": profile_id,
        "display_name": "Renamed",
        "capabilities": ["Translation"],
        "endpoint": "https://second.example.test/v1",
        "model": "model-b",
        "network_profile_id": None,
        "enabled": False,
    })
    assert updated["error"] is None, updated["error"]
    profiles, _ = mirror_state(core)
    assert profiles[profile_id]["base_url"] == "https://second.example.test/v1"
    assert profiles[profile_id]["model"] == "model-b"
    assert profiles[profile_id]["enabled"] is False

    deleted = request(server, "settings_provider_profiles_delete", {"profile_id": profile_id})
    assert deleted["error"] is None, deleted["error"]
    profiles, _ = mirror_state(core)
    assert profile_id not in profiles


def test_binding_clear_removes_the_mirrored_step_binding(env) -> None:
    core, server = env
    profile = create_profile(server)
    profile_id = profile["profile_id"]
    assert request(server, "settings_provider_bindings_set", {
        "scope": {"kind": "global"}, "capability": "Translation", "profile_id": profile_id,
    })["error"] is None
    assert mirror_state(core)[1]["translate"] == profile_id

    cleared = request(server, "settings_provider_bindings_clear", {
        "scope": {"kind": "global"}, "capability": "Translation",
    })
    assert cleared["error"] is None, cleared["error"]
    assert "translate" not in mirror_state(core)[1]


def test_rendering_capability_never_invents_a_pipeline_step(env) -> None:
    core, server = env
    profile = create_profile(server, capabilities=("Rendering",))
    profile_id = profile["profile_id"]

    bound = request(server, "settings_provider_bindings_set", {
        "scope": {"kind": "global"}, "capability": "Rendering", "profile_id": profile_id,
    })
    assert bound["error"] is None, bound["error"]
    # The P15 row exists (unchanged behaviour) but no pipeline step is created for it:
    # render is local and consumes no remote provider profile.
    rows = core.provider_binding_store.list_bindings()
    assert any(row["capability"] == "Rendering" for row in rows)
    _, bindings = mirror_state(core)
    assert "render" not in bindings and "rendering" not in bindings


# ---------------------------------------------------------------- AC2

class _MemoryCredentials:
    """Same fake the P15 suite uses: refs only, never a secret value."""

    def __init__(self):
        self.refs = set()

    def has_credential(self, ref):
        return ref in self.refs

    def delete_credential(self, ref):
        self.refs.discard(ref)


def test_mirror_carries_credential_ref_but_never_the_secret(env) -> None:
    core, server = env
    core.credential_store = _MemoryCredentials()
    profile = create_profile(server)
    profile_id = profile["profile_id"]
    credential_ref = f"NewManga/provider/{profile_id}/api-key"
    core.credential_store.refs.add(credential_ref)

    bound = request(server, "BindProfileCredential", {
        "target": {"kind": "provider_api", "profile_id": profile_id},
        "credential_ref": credential_ref,
    })
    assert bound["error"] is None, bound["error"]

    profiles, _ = mirror_state(core)
    assert profiles[profile_id]["credential_ref"] == credential_ref
    dumped = json.dumps(core.pipeline_defaults.read().settings)
    assert credential_ref in dumped  # the reference rides the mirror
    lowered = dumped.lower()
    for forbidden in ("api_key", "apikey", "secret", "password", "bearer "):
        assert forbidden not in lowered, f"mirror leaked a secret-shaped key: {forbidden}"


# ---------------------------------------------------------------- AC3 / AC6

def test_profile_mirror_failure_is_typed_and_leaves_no_half_write(env, monkeypatch) -> None:
    core, server = env

    def boom(*args, **kwargs):
        raise BindingValidationError("mirror write refused")

    monkeypatch.setattr(core.pipeline_defaults, "save_settings_section", boom)
    response = request(server, "settings_provider_profiles_create", {
        "provider_id": "shared-provider",
        "display_name": "Primary",
        "capabilities": ["Translation"],
        "endpoint": "https://api.example.test/v1",
        "model": "model-a",
        "network_profile_id": None,
        "enabled": True,
    })
    assert response["error"] is not None
    assert response["error"]["code"] == "SETTINGS_UNAVAILABLE", response["error"]
    # Fail-closed in the strong direction: the JSON store was never written either.
    assert core.provider_profile_store.list_profiles() == []
    assert mirror_state(core)[0] == {}


def test_binding_mirror_failure_rolls_back_the_binding_rows(env, monkeypatch) -> None:
    core, server = env
    profile = create_profile(server)
    profile_id = profile["profile_id"]

    def boom(*args, **kwargs):
        raise BindingValidationError("binding mirror refused")

    monkeypatch.setattr(core.pipeline_defaults, "save_provider_binding", boom)
    response = request(server, "settings_provider_bindings_set", {
        "scope": {"kind": "global"}, "capability": "Translation", "profile_id": profile_id,
    })
    assert response["error"] is not None
    assert response["error"]["code"] == "SETTINGS_UNAVAILABLE", response["error"]
    assert core.provider_binding_store.list_bindings() == []
    assert "translate" not in mirror_state(core)[1]
