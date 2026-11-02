"""Test helpers for the network/settings suites: in-memory contract
fakes, profile factories and (later batches) local controllable servers.
Importable as plain ``helpers`` because pytest puts this directory on
sys.path (no package __init__ by design, same as tests/library).
"""

from __future__ import annotations

import sys
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from ports.network.profiles import (  # noqa: E402
    MODE_DIRECT,
    MODE_HTTP,
    MODE_HTTPS,
    MODE_SOCKS5,
    MODE_SYSTEM,
    NetworkProfile,
)
from ports.providers.credentials import SecretValue  # noqa: E402
from ports.providers.profiles import (  # noqa: E402
    CAPABILITY_INPAINT,
    CAPABILITY_OCR,
    CAPABILITY_TRANSLATION,
    ProxyPolicy,
    ProviderProfile,
)


# ----------------------------------------------------------------------
# in-memory contract fakes
# ----------------------------------------------------------------------


class InMemoryProviderProfileStore:
    def __init__(self) -> None:
        self.profiles: dict[str, ProviderProfile] = {}

    def add_profile(self, profile: ProviderProfile) -> None:
        self.profiles[profile.provider_profile_id] = profile

    def get_profile(self, provider_profile_id: str) -> ProviderProfile | None:
        return self.profiles.get(provider_profile_id)

    def list_profiles(self) -> list[ProviderProfile]:
        return list(self.profiles.values())

    def update_profile(self, profile: ProviderProfile) -> None:
        if profile.provider_profile_id not in self.profiles:
            raise KeyError(profile.provider_profile_id)
        self.profiles[profile.provider_profile_id] = profile

    def delete_profile(self, provider_profile_id: str) -> None:
        self.profiles.pop(provider_profile_id, None)


class InMemoryNetworkProfileStore:
    def __init__(self) -> None:
        self.profiles: dict[str, NetworkProfile] = {}

    def add_profile(self, profile: NetworkProfile) -> None:
        self.profiles[profile.network_profile_id] = profile

    def get_profile(self, network_profile_id: str) -> NetworkProfile | None:
        return self.profiles.get(network_profile_id)

    def list_profiles(self) -> list[NetworkProfile]:
        return list(self.profiles.values())

    def update_profile(self, profile: NetworkProfile) -> None:
        if profile.network_profile_id not in self.profiles:
            raise KeyError(profile.network_profile_id)
        self.profiles[profile.network_profile_id] = profile

    def delete_profile(self, network_profile_id: str) -> None:
        self.profiles.pop(network_profile_id, None)


class InMemoryCredentialStore:
    """Vault fake; stores ``SecretValue`` objects, never plain strings."""

    def __init__(self) -> None:
        self._secrets: dict[str, SecretValue] = {}

    def store_credential(self, ref: str, secret: SecretValue) -> None:
        if ref in self._secrets:
            raise KeyError(f"credential already exists: {ref}")
        self._secrets[ref] = secret

    def resolve_credential(self, ref: str) -> SecretValue:
        if ref not in self._secrets:
            raise KeyError(ref)
        return self._secrets[ref]

    def update_credential(self, ref: str, secret: SecretValue) -> None:
        if ref not in self._secrets:
            raise KeyError(ref)
        self._secrets[ref] = secret

    def delete_credential(self, ref: str) -> None:
        self._secrets.pop(ref, None)

    def has_credential(self, ref: str) -> bool:
        return ref in self._secrets


# ----------------------------------------------------------------------
# factories
# ----------------------------------------------------------------------


def make_provider_profile(
    provider_profile_id: str = "prof-1",
    *,
    name: str = "OpenAI-翻译",
    provider_type: str = "openai",
    capabilities=frozenset({CAPABILITY_TRANSLATION}),
    base_url: str = "https://api.example.com/v1",
    model: str = "gpt-test",
    credential_ref: str | None = "NewManga/provider/prof-1",
    network_profile_id: str | None = None,
    proxy_policy: str = ProxyPolicy.INHERIT,
    is_enabled: bool = True,
    options: tuple[tuple[str, str], ...] = (),
) -> ProviderProfile:
    return ProviderProfile(
        provider_profile_id=provider_profile_id,
        name=name,
        provider_type=provider_type,
        capabilities=frozenset(capabilities),
        base_url=base_url,
        model=model,
        credential_ref=credential_ref,
        network_profile_id=network_profile_id,
        proxy_policy=proxy_policy,
        options=options,
        is_enabled=is_enabled,
    )


def make_network_profile(
    network_profile_id: str = "net-1",
    *,
    name: str = "直连",
    mode: str = MODE_DIRECT,
    bypass_hosts: frozenset[str] = frozenset(),  # tests hit 127.0.0.1 endpoints
    **kwargs,
) -> NetworkProfile:
    return NetworkProfile(
        network_profile_id=network_profile_id,
        name=name,
        mode=mode,
        bypass_hosts=bypass_hosts,
        **kwargs,
    )


ALL_MODE_VALUES = (MODE_DIRECT, MODE_SYSTEM, MODE_HTTP, MODE_HTTPS, MODE_SOCKS5)
