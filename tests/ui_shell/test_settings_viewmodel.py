"""T1.2.1: the settings page viewmodel (D05 §43.1, AC-SEC-001~005,
AC-PROVIDER-001/002, AC-NET-001~003).

Lightweight fakes stand in for the JSON profile stores, the credential
vault and the pipeline-defaults storage bridge; the safety gates under
test live in the application services the viewmodel calls. The core
posture checks: secrets reach *only* the vault, profile views carry only
``credential_set``, dangerous TLS changes need the explicit confirmation
round-trip, and error messages never quote a secret.
"""

from __future__ import annotations

import helpers  # noqa: F401  (sys.path injection)

import pytest

pytest.importorskip("PySide6")

from application.settings.network import NetworkProfileService  # noqa: E402
from application.settings.pipeline_defaults import (  # noqa: E402
    PipelineDefaults,
    PipelineDefaultsService,
)
from ui.viewmodels.settings.viewmodel import SettingsViewModel  # noqa: E402

_SECRET = "sk-live-do-not-leak-123"
# Production handler step names (build_production_handlers) — the names
# the pipeline_defaults row and the run snapshot actually carry.
_STEPS = frozenset({"detect", "ocr", "translate", "inpaint", "render"})


class FakeProviderStore:
    def __init__(self):
        self.profiles = {}

    def add_profile(self, profile):
        self.profiles[profile.provider_profile_id] = profile

    def get_profile(self, profile_id):
        return self.profiles.get(profile_id)

    def list_profiles(self):
        return list(self.profiles.values())

    def update_profile(self, profile):
        if profile.provider_profile_id not in self.profiles:
            raise KeyError(profile.provider_profile_id)
        self.profiles[profile.provider_profile_id] = profile

    def delete_profile(self, profile_id):
        self.profiles.pop(profile_id, None)


class FakeCredentialStore:
    def __init__(self):
        self.secrets = {}

    def store_credential(self, ref, secret):
        if ref in self.secrets:
            raise KeyError(f"credential already exists: {ref}")
        self.secrets[ref] = secret

    def resolve_credential(self, ref):
        return self.secrets[ref]

    def update_credential(self, ref, secret):
        if ref not in self.secrets:
            raise KeyError(ref)
        self.secrets[ref] = secret

    def delete_credential(self, ref):
        self.secrets.pop(ref, None)

    def has_credential(self, ref):
        return ref in self.secrets


class DefaultsBridge:
    """In-memory stand-in for the pipeline_defaults storage row."""

    def __init__(self):
        self.state = {
            "settings": {},
            "provider_bindings": {},
            "constraint_snapshot_ref": None,
            "context_policy": {},
        }

    def load(self):
        return PipelineDefaults(**self.state)

    def save(self, **kwargs):
        self.state.update(kwargs)


def _vm() -> tuple[SettingsViewModel, FakeCredentialStore, DefaultsBridge]:
    bridge = DefaultsBridge()
    credentials = FakeCredentialStore()
    vm = SettingsViewModel(
        provider_store=FakeProviderStore(),
        network_service=NetworkProfileService(_NetworkStoreFake()),
        credential_store=credentials,
        pipeline_defaults=PipelineDefaultsService(
            load=bridge.load, save=bridge.save, known_steps=_STEPS
        ),
    )
    return vm, credentials, bridge


class _NetworkStoreFake:
    def __init__(self):
        self.profiles = {}

    def add_profile(self, profile):
        self.profiles[profile.network_profile_id] = profile

    def get_profile(self, profile_id):
        return self.profiles.get(profile_id)

    def list_profiles(self):
        return list(self.profiles.values())

    def update_profile(self, profile):
        if profile.network_profile_id not in self.profiles:
            raise KeyError(profile.network_profile_id)
        self.profiles[profile.network_profile_id] = profile

    def delete_profile(self, profile_id):
        self.profiles.pop(profile_id, None)


def _provider_payload(**overrides) -> dict:
    payload = {
        "provider_profile_id": "openai-translation",
        "name": "OpenAI 翻译",
        "provider_type": "openai",
        "capabilities": ["translation"],
        "base_url": "https://api.example.com/v1",
        "model": "gpt-test",
        "api_key": _SECRET,
        "clear_credential": False,
        "network_profile_id": "",
        "proxy_policy": "inherit",
        "is_enabled": True,
    }
    payload.update(overrides)
    return payload


def _network_payload(**overrides) -> dict:
    payload = {
        "network_profile_id": "corp-proxy",
        "name": "公司代理",
        "mode": "http",
        "http_proxy": "http://proxy.internal:8080",
        "https_proxy": "",
        "socks5_proxy": "",
        "username": "alice",
        "proxy_password": _SECRET,
        "clear_credential": False,
        "bypass_hosts": ["localhost", ".internal"],
        "inherit_system": False,
        "verify_tls": True,
        "allow_proxy_failure_direct_fallback": False,
        "confirm_disable_tls": False,
    }
    payload.update(overrides)
    return payload


class TestProviderProfileFlow:
    def test_save_writes_vault_and_store(self, qapp):
        vm, credentials, _ = _vm()
        saved = []
        vm.saved.connect(saved.append)
        vm.saveProviderProfile(_provider_payload())
        assert saved, "save must report success"
        ref = "NewManga/provider/openai-translation"
        assert credentials.has_credential(ref)
        assert credentials.resolve_credential(ref).reveal() == _SECRET

    def test_profile_view_carries_only_the_ref(self, qapp):
        vm, _, _ = _vm()
        vm.saveProviderProfile(_provider_payload())
        views = vm.profiles
        assert len(views) == 1
        view = views[0]
        assert view["credential_set"] is True
        assert view["credential_ref"] == "NewManga/provider/openai-translation"
        assert _SECRET not in str(view)  # AC-SEC-001/002

    def test_empty_api_key_keeps_existing_credential(self, qapp):
        vm, credentials, _ = _vm()
        vm.saveProviderProfile(_provider_payload())
        vm.saveProviderProfile(_provider_payload(name="改名", api_key=""))
        ref = "NewManga/provider/openai-translation"
        assert credentials.resolve_credential(ref).reveal() == _SECRET
        assert vm.profiles[0]["name"] == "改名"

    def test_clear_credential_removes_vault_entry(self, qapp):
        vm, credentials, _ = _vm()
        vm.saveProviderProfile(_provider_payload())
        vm.saveProviderProfile(
            _provider_payload(api_key="", clear_credential=True)
        )
        assert not credentials.has_credential("NewManga/provider/openai-translation")
        assert vm.profiles[0]["credential_set"] is False

    def test_delete_provider_cleans_its_credential(self, qapp):
        vm, credentials, _ = _vm()
        vm.saveProviderProfile(_provider_payload())
        vm.deleteProviderProfile("openai-translation")
        assert vm.profiles == []
        assert credentials.secrets == {}


class TestBindingFlow:
    def test_binding_write_feeds_pipeline_defaults(self, qapp):
        vm, _, bridge = _vm()
        vm.saveProviderProfile(_provider_payload(api_key=""))
        vm.saveBinding("ocr", "openai-translation")
        assert bridge.state["provider_bindings"]["ocr"] == "openai-translation"
        assert vm.bindings["ocr"] == "openai-translation"

    def test_capability_binding_persists_production_step_name(self, qapp):
        """QML binds by capability name; the row stores the handler step
        name the run snapshot reader resolves (translate, not translation)."""
        vm, _, bridge = _vm()
        vm.saveProviderProfile(_provider_payload(api_key=""))
        vm.saveBinding("translation", "openai-translation")
        assert bridge.state["provider_bindings"]["translate"] == (
            "openai-translation"
        )
        assert "translation" not in bridge.state["provider_bindings"]
        assert vm.bindings["translation"] == "openai-translation"

    def test_binding_rejects_missing_profile(self, qapp):
        vm, _, bridge = _vm()
        failures = []
        vm.failed.connect(failures.append)
        vm.saveBinding("ocr", "no-such-profile")
        assert failures and "no-such-profile" in failures[0]
        assert bridge.state["provider_bindings"] == {}

    def test_unknown_step_fails_typed(self, qapp):
        vm, _, bridge = _vm()
        failures = []
        vm.failed.connect(failures.append)
        vm.saveBinding("teleport", "openai-translation")
        assert failures and "teleport" in failures[0]
        assert bridge.state["provider_bindings"] == {}

    def test_clear_binding_removes_the_step(self, qapp):
        vm, _, bridge = _vm()
        vm.saveProviderProfile(_provider_payload(api_key=""))
        vm.saveBinding("ocr", "openai-translation")
        vm.clearBinding("ocr")
        assert "ocr" not in bridge.state["provider_bindings"]


class TestNetworkFlow:
    def test_save_writes_proxy_password_to_vault(self, qapp):
        vm, credentials, _ = _vm()
        vm.saveNetworkProfile(_network_payload())
        ref = "NewManga/proxy/corp-proxy"
        assert credentials.resolve_credential(ref).reveal() == _SECRET
        assert vm.networks[0]["verify_tls"] is True

    def test_tls_off_requires_confirmation_roundtrip(self, qapp):
        vm, _, _ = _vm()
        confirmations = []
        vm.confirmationRequired.connect(confirmations.append)
        vm.saveNetworkProfile(_network_payload(verify_tls=False))
        assert confirmations, "AC-SEC-005: silent default-off is forbidden"
        assert vm.networks == []  # nothing persisted without confirmation
        vm.saveNetworkProfile(_network_payload(verify_tls=False,
                                               confirm_disable_tls=True))
        assert vm.networks[0]["verify_tls"] is False

    def test_default_network_profile_roundtrip(self, qapp):
        vm, _, bridge = _vm()
        vm.saveNetworkProfile(_network_payload())
        vm.setDefaultNetworkProfile("network", "corp-proxy")
        assert bridge.state["settings"]["network"]["profile_id"] == "corp-proxy"
        assert vm.defaultNetworkProfileId == "corp-proxy"


class TestPipelineMirror:
    """R3 B-003: saved profiles must reach the pipeline settings shape the
    production bootstrap reads, so a restart resolves what the UI saved."""

    def test_provider_save_mirrors_runtime_shape(self, qapp):
        vm, _, bridge = _vm()
        vm.saveProviderProfile(
            _provider_payload(api_key="", network_profile_id="corp-proxy")
        )
        mirror = bridge.state["settings"]["providers"]["profiles"][
            "openai-translation"
        ]
        assert mirror == {
            "base_url": "https://api.example.com/v1",
            "model": "gpt-test",
            "credential_ref": None,
            "enabled": True,
            "options": {},
            "provider_type": "openai",
            "network_profile_id": "corp-proxy",
        }

    def test_provider_delete_cleans_mirror(self, qapp):
        vm, _, bridge = _vm()
        vm.saveProviderProfile(_provider_payload(api_key=""))
        vm.deleteProviderProfile("openai-translation")
        mirror = bridge.state["settings"]["providers"]["profiles"]
        assert "openai-translation" not in mirror

    def test_network_save_mirrors_runtime_shape(self, qapp):
        vm, _, bridge = _vm()
        vm.saveNetworkProfile(_network_payload())
        mirror = bridge.state["settings"]["providers"]["networks"]["corp-proxy"]
        assert mirror["mode"] == "http"
        assert mirror["http_proxy"] == "http://proxy.internal:8080"
        assert mirror["username"] == "alice"
        assert mirror["credential_ref"] == "NewManga/proxy/corp-proxy"
        assert mirror["bypass_hosts"] == [".internal", "localhost"]
        assert mirror["verify_tls"] is True

    def test_network_delete_cleans_mirror(self, qapp):
        vm, _, bridge = _vm()
        vm.saveNetworkProfile(_network_payload())
        vm.deleteNetworkProfile("corp-proxy")
        mirror = bridge.state["settings"]["providers"]["networks"]
        assert "corp-proxy" not in mirror

    def test_mirror_never_carries_secret_material(self, qapp):
        vm, _, bridge = _vm()
        vm.saveProviderProfile(_provider_payload())
        vm.saveNetworkProfile(_network_payload())
        import json as _json

        dumped = _json.dumps(bridge.state["settings"], ensure_ascii=False)
        assert _SECRET not in dumped  # refs only, never values

    def test_mirror_feeds_the_production_runtime(self, qapp):
        """Full seam: what the UI saved resolves on the production
        registry path and carries its network profile (B-001+B-002)."""
        from infrastructure.providers.runtime import build_provider_runtime
        from infrastructure.transport.stdlib import StdlibTransport

        vm, _, bridge = _vm()
        vm.saveNetworkProfile(
            _network_payload(
                mode="socks5",
                http_proxy="",
                https_proxy="",
                socks5_proxy="socks5://gateway.internal:1080",
                inherit_system=False,
            )
        )
        vm.saveProviderProfile(
            _provider_payload(
                api_key="", provider_type="openai-compatible",
                network_profile_id="corp-proxy",
            )
        )
        vm.saveBinding("translation", "openai-translation")
        runtime = build_provider_runtime(
            settings=bridge.state["settings"],
            provider_bindings=dict(bridge.state["provider_bindings"]),
            transport=StdlibTransport(),
        )
        provider = runtime.registry.resolve_binding(
            "translation", "openai-translation"
        )
        assert provider.config.base_url == "https://api.example.com/v1"
        network = provider.config.network_profile
        assert network is not None
        assert network.mode == "socks5"
        assert network.socks5_proxy == "socks5://gateway.internal:1080"


class TestSecurityPosture:
    def test_error_messages_never_quote_the_secret(self, qapp):
        vm, _, _ = _vm()
        failures = []
        vm.failed.connect(failures.append)
        # An unknown capability makes the frozen model raise; the payload
        # still carries the secret, which must not leak into the message.
        vm.saveProviderProfile(_provider_payload(capabilities=["teleport"]))
        assert failures
        assert _SECRET not in failures[0]

    def test_confirmation_message_never_quotes_the_secret(self, qapp):
        vm, _, _ = _vm()
        confirmations = []
        vm.confirmationRequired.connect(confirmations.append)
        vm.saveNetworkProfile(_network_payload(verify_tls=False))
        assert confirmations and _SECRET not in confirmations[0]

    def test_network_view_hides_password_material(self, qapp):
        vm, _, _ = _vm()
        vm.saveNetworkProfile(_network_payload())
        assert _SECRET not in str(vm.networks[0])
