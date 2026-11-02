"""T1.2.1: JSON-backed provider/network profile persistence.

The stores implement the D03 §25/§27 ports; these checks pin the
restart-survival contract (write with one store instance, read with a
fresh one) and the secret posture: only ``credential_ref`` strings are
persisted — never the secret itself (AC-SEC-001/003). Pure Python, no
Qt, no Windows vault.
"""

from __future__ import annotations

import json

import pytest

from infrastructure.settings.json_profile_stores import (
    JsonNetworkProfileStore,
    JsonProviderProfileStore,
    ProfileFileFormatError,
)
from ports.network.profiles import NetworkProfile
from ports.providers.profiles import ProviderProfile


def _provider(profile_id: str = "openai-translation") -> ProviderProfile:
    return ProviderProfile(
        provider_profile_id=profile_id,
        name="OpenAI 翻译",
        provider_type="openai",
        capabilities=frozenset({"translation", "ocr"}),
        base_url="https://api.example.com/v1",
        model="gpt-test",
        credential_ref="NewManga/provider/openai-translation",
        network_profile_id=None,
        proxy_policy="profile",
        options=(("temperature", "0.3"),),
        is_enabled=True,
        created_at="2026-01-01T00:00:00+00:00",
        updated_at="2026-01-02T00:00:00+00:00",
    )


def _network(profile_id: str = "corp-proxy") -> NetworkProfile:
    return NetworkProfile(
        network_profile_id=profile_id,
        name="公司代理",
        mode="http",
        http_proxy="http://proxy.internal:8080",
        https_proxy="http://proxy.internal:8080",
        username="alice",
        credential_ref="NewManga/proxy/corp-proxy",
        bypass_hosts=frozenset({"localhost", ".internal"}),
        inherit_system=False,
        timeout_seconds=15.0,
        verify_tls=True,
        allow_proxy_failure_direct_fallback=False,
    )


class TestProviderProfilePersistence:
    def test_profile_survives_restart(self, tmp_path):
        first = JsonProviderProfileStore(tmp_path)
        first.add_profile(_provider())
        # A fresh instance models the next process start.
        second = JsonProviderProfileStore(tmp_path)
        loaded = second.get_profile("openai-translation")
        assert loaded == _provider()
        assert [p.provider_profile_id for p in second.list_profiles()] == [
            "openai-translation"
        ]

    def test_multiple_profiles_per_provider_type(self, tmp_path):
        store = JsonProviderProfileStore(tmp_path)
        store.add_profile(_provider("openai-translation"))
        store.add_profile(_provider("openai-vision-ocr"))
        assert len(store.list_profiles()) == 2  # AC-PROVIDER-001

    def test_update_replaces_and_delete_removes(self, tmp_path):
        store = JsonProviderProfileStore(tmp_path)
        store.add_profile(_provider())
        store.update_profile(
            ProviderProfile(
                provider_profile_id="openai-translation",
                name="改名",
                provider_type="openai",
                capabilities=frozenset({"translation"}),
                updated_at="2026-01-03T00:00:00+00:00",
            )
        )
        assert store.get_profile("openai-translation").name == "改名"
        store.delete_profile("openai-translation")
        assert store.get_profile("openai-translation") is None

    def test_update_missing_raises(self, tmp_path):
        store = JsonProviderProfileStore(tmp_path)
        with pytest.raises(KeyError):
            store.update_profile(_provider())

    def test_stored_file_holds_credential_ref_only(self, tmp_path):
        store = JsonProviderProfileStore(tmp_path)
        store.add_profile(_provider())
        raw = (tmp_path / "provider_profiles.json").read_text(encoding="utf-8")
        payload = json.loads(raw)
        assert payload["profiles"][0]["credential_ref"] == (
            "NewManga/provider/openai-translation"
        )


class TestNetworkProfilePersistence:
    def test_profile_survives_restart(self, tmp_path):
        JsonNetworkProfileStore(tmp_path).add_profile(_network())
        second = JsonNetworkProfileStore(tmp_path)
        assert second.get_profile("corp-proxy") == _network()

    def test_stored_file_holds_credential_ref_only(self, tmp_path):
        JsonNetworkProfileStore(tmp_path).add_profile(_network())
        raw = (tmp_path / "network_profiles.json").read_text(encoding="utf-8")
        payload = json.loads(raw)
        assert payload["profiles"][0]["credential_ref"] == "NewManga/proxy/corp-proxy"
        # No password material anywhere in the file.
        assert "secret" not in raw.lower().replace("credential_ref", "")

    def test_corrupt_file_is_a_typed_error(self, tmp_path):
        target = tmp_path / "network_profiles.json"
        target.write_text("{not json", encoding="utf-8")
        with pytest.raises(ProfileFileFormatError):
            JsonNetworkProfileStore(tmp_path).list_profiles()

    def test_missing_file_reads_empty(self, tmp_path):
        assert JsonNetworkProfileStore(tmp_path).list_profiles() == []
