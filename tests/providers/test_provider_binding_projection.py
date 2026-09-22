"""T1.2.1 R3 B-001/B-002: profile bindings reach the production registry.

The Settings UI saves user-named provider profiles (any profile id) and
binds pipeline steps to them, while ``ProviderRegistry`` only resolves its
fixed provider ids. These tests pin the production seam that closes that
gap: ``build_provider_runtime`` projects a bound profile onto the fixed
registry slot serving the step's capability, and the registry translates
the profile id through a binding alias — so ``registry.resolve`` /
``resolve_binding`` succeed on the production path, not just under unit
injection.

B-002 is pinned on the same seam: a provider profile naming a network
profile must reach its client config as a real ``NetworkProfile``, and the
client must hand exactly that profile to the transport (proxy/TLS/bypass
policy applied, not silently direct).
"""

from __future__ import annotations

import pytest

from infrastructure.providers.openai_client import (
    DEFAULT_NETWORK_PROFILE_ID,
    OpenAiCompatibleConfig,
)
from infrastructure.providers.runtime import (
    PROVIDER_SAKURA,
    PROVIDER_VISION_OCR,
    build_provider_runtime,
)
from infrastructure.transport.stdlib import StdlibTransport
from providers_helpers import FakeTransport

PROFILE_ID = "my-openai-profile"
SAKURA_PROFILE_ID = "sakura-home"
VISION_PROFILE_ID = "vision-fallback"
PROXY_ID = "corp-proxy"

_PROVIDER_SECRET_REF = "NewManga/provider/my-openai-profile"


def _base_settings() -> dict:
    return {
        "providers": {
            "profiles": {
                PROFILE_ID: {
                    "base_url": "https://api.example.com/v1",
                    "model": "gpt-test",
                    "credential_ref": _PROVIDER_SECRET_REF,
                    "enabled": True,
                    "options": {"temperature": "0.2"},
                    "provider_type": "openai-compatible",
                    "network_profile_id": "",
                    "proxy_policy": "inherit",
                },
                SAKURA_PROFILE_ID: {
                    "base_url": "http://192.168.1.20:8080/v1",
                    "model": "sakura-14b",
                    "credential_ref": None,
                    "enabled": True,
                    "options": {},
                    "provider_type": "local-sakura",
                    "network_profile_id": "",
                    "proxy_policy": "inherit",
                },
                VISION_PROFILE_ID: {
                    "base_url": "https://vision.example.com/v1",
                    "model": "vision-x",
                    "credential_ref": None,
                    "enabled": True,
                    "options": {},
                    "provider_type": "openai-compatible-vision",
                    "network_profile_id": "",
                    "proxy_policy": "inherit",
                },
            },
            "networks": {},
        }
    }


def _runtime_with_bindings(settings: dict, bindings: dict):
    return build_provider_runtime(
        settings=settings,
        provider_bindings=bindings,
        transport=StdlibTransport(),
        credential_resolver=_test_credential_resolver,
    )


def _test_credential_resolver(ref: str) -> str | None:
    return "test-secret"


# -- B-001: a bound profile resolves on the production registry path ------


class TestProfileBindingResolution:
    def test_string_binding_resolves_profile_settings(self):
        runtime = _runtime_with_bindings(
            _base_settings(), {"translate": PROFILE_ID}
        )
        provider = runtime.registry.resolve("translation", PROFILE_ID)
        assert provider.config.base_url == "https://api.example.com/v1"
        assert provider.config.model == "gpt-test"
        assert provider.config.credential_ref == _PROVIDER_SECRET_REF
        assert dict(provider.config.extra_options) == {"temperature": "0.2"}

    def test_mapping_binding_resolves_profile_settings(self):
        runtime = _runtime_with_bindings(
            _base_settings(), {"translate": {"provider_profile_id": PROFILE_ID}}
        )
        provider = runtime.registry.resolve_binding("translation", {
            "provider_profile_id": PROFILE_ID
        })
        assert provider.config.model == "gpt-test"

    def test_resolve_binding_translates_profile_id(self):
        runtime = _runtime_with_bindings(
            _base_settings(), {"translate": PROFILE_ID}
        )
        provider = runtime.registry.resolve_binding("translation", PROFILE_ID)
        assert provider.config.base_url == "https://api.example.com/v1"

    def test_sakura_profile_takes_the_sakura_slot(self):
        runtime = _runtime_with_bindings(
            _base_settings(), {"translate": SAKURA_PROFILE_ID}
        )
        provider = runtime.registry.resolve("translation", SAKURA_PROFILE_ID)
        assert provider.config.base_url == "http://192.168.1.20:8080/v1"

    def test_ocr_profile_takes_the_vision_slot(self):
        runtime = _runtime_with_bindings(_base_settings(), {"ocr": VISION_PROFILE_ID})
        provider = runtime.registry.resolve("ocr", VISION_PROFILE_ID)
        assert provider.config.base_url == "https://vision.example.com/v1"

    def test_unregistered_profile_stays_fail_closed(self):
        runtime = _runtime_with_bindings(
            _base_settings(), {"translate": "no-such-profile"}
        )
        with pytest.raises(Exception) as excinfo:
            runtime.registry.resolve("translation", "no-such-profile")
        assert "no-such-profile" in str(excinfo.value)

    def test_disabled_profile_stays_unregistered(self):
        settings = _base_settings()
        settings["providers"]["profiles"][PROFILE_ID]["enabled"] = False
        runtime = _runtime_with_bindings(settings, {"translate": PROFILE_ID})
        with pytest.raises(Exception, match=PROFILE_ID):
            runtime.registry.resolve("translation", PROFILE_ID)

    def test_fixed_id_binding_keeps_working(self):
        """The pre-T1.2.1 settings shape (fixed slot + fixed-id binding)
        must keep resolving unchanged."""
        settings = _base_settings()
        settings["providers"]["profiles"][PROVIDER_SAKURA] = dict(
            settings["providers"]["profiles"][SAKURA_PROFILE_ID]
        )
        settings["providers"]["profiles"][PROVIDER_SAKURA]["base_url"] = (
            "http://127.0.0.1:8080/v1"
        )
        runtime = _runtime_with_bindings(
            settings, {"translate": PROVIDER_SAKURA}
        )
        provider = runtime.registry.resolve("translation", PROVIDER_SAKURA)
        assert provider.config.base_url == "http://127.0.0.1:8080/v1"

    def test_projection_does_not_add_registry_entries(self):
        baseline = _runtime_with_bindings(_base_settings(), {})
        projected = _runtime_with_bindings(
            _base_settings(), {"translate": PROFILE_ID}
        )
        assert len(projected.registry.readiness_report()) == len(
            baseline.registry.readiness_report()
        )


# -- B-002: the bound profile's network profile reaches the transport -----


def _proxy_settings() -> dict:
    settings = _base_settings()
    settings["providers"]["profiles"][PROFILE_ID]["network_profile_id"] = PROXY_ID
    settings["providers"]["profiles"][PROFILE_ID]["proxy_policy"] = "profile"
    settings["providers"]["networks"][PROXY_ID] = {
        "network_profile_id": PROXY_ID,
        "name": "公司代理",
        "mode": "socks5",
        "http_proxy": "",
        "https_proxy": "",
        "socks5_proxy": "socks5://gateway.internal:1080",
        "username": "proxy-user",
        "credential_ref": "NewManga/proxy/corp-proxy",
        "bypass_hosts": [".internal", "localhost", "127.0.0.1"],
        "inherit_system": False,
        "timeout_seconds": 12.5,
        "verify_tls": False,
        "allow_proxy_failure_direct_fallback": True,
    }
    return settings


class TestNetworkProfileInjection:
    def test_bound_proxy_profile_reaches_provider_config(self):
        runtime = _runtime_with_bindings(
            _proxy_settings(), {"translate": PROFILE_ID}
        )
        provider = runtime.registry.resolve("translation", PROFILE_ID)
        network = provider.config.network_profile
        assert network is not None
        assert network.network_profile_id == PROXY_ID
        assert network.mode == "socks5"
        assert network.socks5_proxy == "socks5://gateway.internal:1080"
        assert network.username == "proxy-user"
        assert network.credential_ref == "NewManga/proxy/corp-proxy"
        assert network.verify_tls is False
        assert network.allow_proxy_failure_direct_fallback is True

    def test_transport_receives_the_bound_proxy_profile(self):
        """End-to-end proxy evidence: one real completion call hands the
        client's network profile — not the direct default — to the
        transport."""
        from ports.network.transport import TransportOutcome, TransportResponse

        class ProfileRecordingTransport:
            def __init__(self):
                self.profiles = []

            def send(self, request, profile):
                self.profiles.append(profile)
                return TransportOutcome(
                    TransportResponse(
                        status=200,
                        body=(
                            '{"choices":[{"message":{"content":"好的"}}]}'
                        ).encode("utf-8"),
                    )
                )

        transport = ProfileRecordingTransport()
        runtime = build_provider_runtime(
            settings=_proxy_settings(),
            provider_bindings={"translate": PROFILE_ID},
            transport=transport,
            credential_resolver=_test_credential_resolver,
        )
        provider = runtime.registry.resolve("translation", PROFILE_ID)
        provider.client.complete(user_text="翻译这段话")
        assert len(transport.profiles) == 1
        handed_over = transport.profiles[0]
        assert handed_over.mode == "socks5"
        assert handed_over.socks5_proxy == "socks5://gateway.internal:1080"
        assert handed_over.verify_tls is False

    def test_profile_policy_with_no_named_network_fails_closed(self):
        """R4 B-002: proxy_policy=profile without a network_profile_id must
        fail closed (readiness not-configured), never silently direct."""
        settings = _proxy_settings()
        settings["providers"]["profiles"][PROFILE_ID]["network_profile_id"] = ""
        runtime = _runtime_with_bindings(settings, {"translate": PROFILE_ID})
        with pytest.raises(Exception, match="network_profile_id"):
            runtime.registry.resolve("translation", PROFILE_ID)

    def test_unknown_network_profile_fails_closed(self):
        """R4 B-002: a named network profile that does not exist must fail
        closed, never silently fall back to direct."""
        settings = _proxy_settings()
        settings["providers"]["profiles"][PROFILE_ID]["network_profile_id"] = (
            "vanished-proxy"
        )
        runtime = _runtime_with_bindings(settings, {"translate": PROFILE_ID})
        with pytest.raises(Exception, match="vanished-proxy"):
            runtime.registry.resolve("translation", PROFILE_ID)

    def test_no_bindings_still_resolves_fixed_slot_network(self):
        """A fixed-slot profile with a network id works without bindings
        (pre-T1.2.1 callers pass provider_bindings=None)."""
        settings = _proxy_settings()
        settings["providers"]["profiles"][PROVIDER_VISION_OCR] = dict(
            settings["providers"]["profiles"][PROFILE_ID]
        )
        settings["providers"]["profiles"][PROVIDER_VISION_OCR][
            "base_url"
        ] = "https://vision.example.com/v1"
        runtime = build_provider_runtime(
            settings=settings, transport=StdlibTransport(),
            credential_resolver=_test_credential_resolver,
        )
        provider = runtime.registry.resolve("ocr", PROVIDER_VISION_OCR)
        assert provider.config.network_profile is not None
        assert provider.config.network_profile.mode == "socks5"


# -- credential/reference hygiene on the projected settings ---------------


class TestProjectionHygiene:
    def test_projection_copies_settings_without_aliasing(self):
        settings = _base_settings()
        _runtime_with_bindings(settings, {"translate": PROFILE_ID})
        assert PROFILE_ID in settings["providers"]["profiles"]
        assert PROVIDER_SAKURA not in settings["providers"]["profiles"]
        assert "networks" in settings["providers"]

    def test_network_secret_value_never_enters_settings(self):
        """The mirror stores ``credential_ref`` only; no plaintext proxy
        password may ride the projected settings into the runtime."""
        raw = repr(_proxy_settings()["providers"])
        assert "password123" not in raw


# -- R4 B-001: one profile id may alias several capability slots ----------


class TestMultiCapabilityAlias:
    def test_shared_profile_resolves_both_bound_capabilities(self):
        settings = _base_settings()
        settings["providers"]["profiles"][PROFILE_ID]["provider_type"] = (
            "openai-compatible-vision"
        )
        runtime = _runtime_with_bindings(
            settings, {"translate": PROFILE_ID, "ocr": PROFILE_ID}
        )
        translator = runtime.registry.resolve("translation", PROFILE_ID)
        assert translator.config.model == "gpt-test"
        ocr = runtime.registry.resolve("ocr", PROFILE_ID)
        assert ocr.config.base_url == "https://api.example.com/v1"

    def test_capability_specific_alias_does_not_leak(self):
        """After removing the OCR binding, the translation alias must keep
        pointing at the translation slot (no last-write-wins)."""
        settings = _base_settings()
        settings["providers"]["profiles"][PROFILE_ID]["provider_type"] = (
            "openai-compatible-vision"
        )
        runtime = _runtime_with_bindings(
            settings, {"translate": PROFILE_ID, "ocr": PROFILE_ID}
        )
        assert runtime.registry.binding_aliases[(PROFILE_ID, "translation")]
        assert runtime.registry.binding_aliases[(PROFILE_ID, "ocr")]


# -- R4 B-002: proxy_policy semantics (direct / profile / inherit) --------


class TestProxyPolicySemantics:
    def test_direct_policy_ignores_named_network_profile(self):
        settings = _proxy_settings()
        settings["providers"]["profiles"][PROFILE_ID]["proxy_policy"] = "direct"
        runtime = _runtime_with_bindings(settings, {"translate": PROFILE_ID})
        provider = runtime.registry.resolve("translation", PROFILE_ID)
        assert provider.config.network_profile is None

    def test_inherit_uses_global_network_profile_id(self):
        settings = _proxy_settings()
        settings["providers"]["profiles"][PROFILE_ID]["proxy_policy"] = "inherit"
        settings["network"] = {"profile_id": PROXY_ID}
        runtime = _runtime_with_bindings(settings, {"translate": PROFILE_ID})
        provider = runtime.registry.resolve("translation", PROFILE_ID)
        assert provider.config.network_profile is not None
        assert provider.config.network_profile.mode == "socks5"

    def test_inherit_without_global_setting_is_direct(self):
        settings = _proxy_settings()
        settings["providers"]["profiles"][PROFILE_ID]["proxy_policy"] = "inherit"
        runtime = _runtime_with_bindings(settings, {"translate": PROFILE_ID})
        provider = runtime.registry.resolve("translation", PROFILE_ID)
        assert provider.config.network_profile is None

    def test_inherit_with_missing_global_setting_fails_closed(self):
        settings = _proxy_settings()
        settings["providers"]["profiles"][PROFILE_ID]["proxy_policy"] = "inherit"
        settings["network"] = {"profile_id": "vanished-proxy"}
        runtime = _runtime_with_bindings(settings, {"translate": PROFILE_ID})
        with pytest.raises(Exception, match="vanished-proxy"):
            runtime.registry.resolve("translation", PROFILE_ID)

    def test_missing_policy_defaults_to_inherit(self):
        settings = _proxy_settings()
        del settings["providers"]["profiles"][PROFILE_ID]["proxy_policy"]
        runtime = _runtime_with_bindings(settings, {"translate": PROFILE_ID})
        provider = runtime.registry.resolve("translation", PROFILE_ID)
        assert provider.config.network_profile is None


# -- R4 B-004: a disabled fixed-slot profile is not resolvable ------------


class TestDisabledFixedSlot:
    def test_disabled_fixed_slot_is_not_resolvable(self):
        settings = _base_settings()
        settings["providers"]["profiles"][PROVIDER_SAKURA] = {
            "base_url": "http://127.0.0.1:8080/v1",
            "model": "sakura-14b",
            "credential_ref": None,
            "enabled": False,
            "options": {},
            "provider_type": "local-sakura",
            "network_profile_id": "",
            "proxy_policy": "inherit",
        }
        runtime = _runtime_with_bindings(settings, {})
        with pytest.raises(Exception, match="disabled"):
            runtime.registry.resolve("translation", PROVIDER_SAKURA)

    def test_disabled_fixed_slot_reports_disabled_readiness(self):
        settings = _base_settings()
        settings["providers"]["profiles"]["openai-vision-ocr"] = {
            "base_url": "https://vision.example.com/v1",
            "model": "vision-x",
            "credential_ref": None,
            "enabled": False,
            "options": {},
            "provider_type": "openai-compatible-vision",
            "network_profile_id": "",
            "proxy_policy": "inherit",
        }
        runtime = _runtime_with_bindings(settings, {})
        report = {
            entry["provider_id"]: entry
            for entry in runtime.registry.readiness_report()
        }
        assert report["openai-vision-ocr"]["state"] == "disabled"

    def test_enabled_fixed_slot_still_resolves(self):
        settings = _base_settings()
        settings["providers"]["profiles"][PROVIDER_SAKURA] = {
            "base_url": "http://127.0.0.1:8080/v1",
            "model": "sakura-14b",
            "credential_ref": None,
            "enabled": True,
            "options": {},
            "provider_type": "local-sakura",
            "network_profile_id": "",
            "proxy_policy": "inherit",
        }
        runtime = _runtime_with_bindings(settings, {})
        provider = runtime.registry.resolve("translation", PROVIDER_SAKURA)
        assert provider.config.base_url == "http://127.0.0.1:8080/v1"
