"""JSON-file ``ProviderProfileStore`` / ``NetworkProfileStore`` (T1.2.1).

The store ports (D03 §25/§27) leave the durable adapter to a coordinated
slice; until that lands, provider/network profiles persist as JSON next
to the SQLite database — the same JSON-backed interim the reading
progress and export history use before T3.1.1 unifies storage. The files
implement exactly the port contracts, so the later SQLite adapter swaps
in without touching callers.

Only ``credential_ref`` strings are ever persisted (AC-SEC-001/003):
secrets live in the OS credential vault and never enter these files,
logs or exports. Writes are atomic (tmp + ``os.replace``) so a crash
cannot leave a half-written profile list behind.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from ports.network.profiles import NetworkProfile
from ports.providers.profiles import ProviderProfile

_FORMAT_VERSION = 1


class ProfileFileFormatError(ValueError):
    """The profile file exists but cannot be parsed — refuse to guess."""


def _atomic_write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    os.replace(tmp, path)


def _read_json(path: Path) -> list[dict]:
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ProfileFileFormatError(
            f"settings profile file {path.name} is not valid JSON: {error}"
        ) from error
    if not isinstance(payload, dict) or payload.get("version") != _FORMAT_VERSION:
        raise ProfileFileFormatError(
            f"settings profile file {path.name} has an unsupported format"
        )
    profiles = payload.get("profiles")
    if not isinstance(profiles, list):
        raise ProfileFileFormatError(
            f"settings profile file {path.name} is missing the profiles list"
        )
    return profiles


def _provider_to_json(profile: ProviderProfile) -> dict:
    return {
        "provider_profile_id": profile.provider_profile_id,
        "name": profile.name,
        "provider_type": profile.provider_type,
        "capabilities": sorted(profile.capabilities),
        "base_url": profile.base_url,
        "model": profile.model,
        "credential_ref": profile.credential_ref,
        "network_profile_id": profile.network_profile_id,
        "proxy_policy": profile.proxy_policy,
        "options": [[key, value] for key, value in profile.options],
        "is_enabled": profile.is_enabled,
        "created_at": profile.created_at,
        "updated_at": profile.updated_at,
    }


def _provider_from_json(data: dict) -> ProviderProfile:
    return ProviderProfile(
        provider_profile_id=data["provider_profile_id"],
        name=data["name"],
        provider_type=data["provider_type"],
        capabilities=frozenset(data["capabilities"]),
        base_url=data.get("base_url", ""),
        model=data.get("model", ""),
        credential_ref=data.get("credential_ref"),
        network_profile_id=data.get("network_profile_id"),
        proxy_policy=data.get("proxy_policy", "inherit"),
        options=tuple((key, value) for key, value in data.get("options", [])),
        is_enabled=data.get("is_enabled", True),
        created_at=data.get("created_at", ""),
        updated_at=data.get("updated_at", ""),
    )


def _network_to_json(profile: NetworkProfile) -> dict:
    return {
        "network_profile_id": profile.network_profile_id,
        "name": profile.name,
        "mode": profile.mode,
        "http_proxy": profile.http_proxy,
        "https_proxy": profile.https_proxy,
        "socks5_proxy": profile.socks5_proxy,
        "username": profile.username,
        "credential_ref": profile.credential_ref,
        "bypass_hosts": sorted(profile.bypass_hosts),
        "inherit_system": profile.inherit_system,
        "timeout_seconds": profile.timeout_seconds,
        "verify_tls": profile.verify_tls,
        "allow_proxy_failure_direct_fallback": (
            profile.allow_proxy_failure_direct_fallback
        ),
        "created_at": profile.created_at,
        "updated_at": profile.updated_at,
    }


def _network_from_json(data: dict) -> NetworkProfile:
    return NetworkProfile(
        network_profile_id=data["network_profile_id"],
        name=data["name"],
        mode=data["mode"],
        http_proxy=data.get("http_proxy", ""),
        https_proxy=data.get("https_proxy", ""),
        socks5_proxy=data.get("socks5_proxy", ""),
        username=data.get("username", ""),
        credential_ref=data.get("credential_ref"),
        bypass_hosts=frozenset(data.get("bypass_hosts", [])),
        inherit_system=data.get("inherit_system", True),
        timeout_seconds=data.get("timeout_seconds", 30.0),
        verify_tls=data.get("verify_tls", True),
        allow_proxy_failure_direct_fallback=data.get(
            "allow_proxy_failure_direct_fallback", False
        ),
        created_at=data.get("created_at", ""),
        updated_at=data.get("updated_at", ""),
    )


class JsonProviderProfileStore:
    """``ProviderProfileStore`` over ``<root>/provider_profiles.json``."""

    def __init__(self, directory: Path) -> None:
        self._path = Path(directory) / "provider_profiles.json"

    def add_profile(self, profile: ProviderProfile) -> None:
        profiles = {p["provider_profile_id"]: p for p in _read_json(self._path)}
        profiles[profile.provider_profile_id] = _provider_to_json(profile)
        self._write(profiles)

    def get_profile(self, provider_profile_id: str) -> ProviderProfile | None:
        for data in _read_json(self._path):
            if data["provider_profile_id"] == provider_profile_id:
                return _provider_from_json(data)
        return None

    def list_profiles(self) -> list[ProviderProfile]:
        return [_provider_from_json(data) for data in _read_json(self._path)]

    def update_profile(self, profile: ProviderProfile) -> None:
        profiles = {p["provider_profile_id"]: p for p in _read_json(self._path)}
        if profile.provider_profile_id not in profiles:
            raise KeyError(profile.provider_profile_id)
        profiles[profile.provider_profile_id] = _provider_to_json(profile)
        self._write(profiles)

    def delete_profile(self, provider_profile_id: str) -> None:
        profiles = {p["provider_profile_id"]: p for p in _read_json(self._path)}
        profiles.pop(provider_profile_id, None)
        self._write(profiles)

    def _write(self, profiles: dict[str, dict]) -> None:
        _atomic_write_json(
            self._path,
            {"version": _FORMAT_VERSION, "profiles": list(profiles.values())},
        )


class JsonNetworkProfileStore:
    """``NetworkProfileStore`` over ``<root>/network_profiles.json``."""

    def __init__(self, directory: Path) -> None:
        self._path = Path(directory) / "network_profiles.json"

    def add_profile(self, profile: NetworkProfile) -> None:
        profiles = {p["network_profile_id"]: p for p in _read_json(self._path)}
        profiles[profile.network_profile_id] = _network_to_json(profile)
        self._write(profiles)

    def get_profile(self, network_profile_id: str) -> NetworkProfile | None:
        for data in _read_json(self._path):
            if data["network_profile_id"] == network_profile_id:
                return _network_from_json(data)
        return None

    def list_profiles(self) -> list[NetworkProfile]:
        return [_network_from_json(data) for data in _read_json(self._path)]

    def update_profile(self, profile: NetworkProfile) -> None:
        profiles = {p["network_profile_id"]: p for p in _read_json(self._path)}
        if profile.network_profile_id not in profiles:
            raise KeyError(profile.network_profile_id)
        profiles[profile.network_profile_id] = _network_to_json(profile)
        self._write(profiles)

    def delete_profile(self, network_profile_id: str) -> None:
        profiles = {p["network_profile_id"]: p for p in _read_json(self._path)}
        profiles.pop(network_profile_id, None)
        self._write(profiles)

    def _write(self, profiles: dict[str, dict]) -> None:
        _atomic_write_json(
            self._path,
            {"version": _FORMAT_VERSION, "profiles": list(profiles.values())},
        )
