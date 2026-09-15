"""Network profile model and store port (D03 §27, D07 §67~68).

Multiple named profiles (direct, system, HTTP/HTTPS/SOCKS5 proxies) can
coexist (AC-NET-001). Defaults encode the frozen safety posture:

- ``verify_tls=True`` on every new profile (AC-SEC-004); turning it off
  is a dangerous setting that requires explicit confirmation
  (AC-SEC-005) — enforced by ``NetworkProfileService``, not the model.
- ``allow_proxy_failure_direct_fallback=False``: proxy failures must
  fail loudly, never silently retry direct (AC-NET-002).
- ``localhost`` / ``127.0.0.1`` are bypassed by default.

Proxy passwords live in the credential vault; the model keeps only
``credential_ref`` (D07 §69).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

MODE_DIRECT = "direct"
MODE_SYSTEM = "system"
MODE_HTTP = "http"
MODE_HTTPS = "https"
MODE_SOCKS5 = "socks5"
ALL_MODES = frozenset({MODE_DIRECT, MODE_SYSTEM, MODE_HTTP, MODE_HTTPS, MODE_SOCKS5})

DEFAULT_BYPASS_HOSTS = frozenset({"localhost", "127.0.0.1", "::1"})
DEFAULT_TIMEOUT_SECONDS = 30.0


def _reject_userinfo(url: str, field_name: str) -> None:
    """Reject ``user:password@host`` proxy endpoints (R-008).

    Proxy passwords belong in the credential vault referenced by
    ``credential_ref``; userinfo would smuggle a secret into the model,
    its repr and whatever persists the profile.
    """
    netloc = url.split("://", 1)[-1].split("/", 1)[0]
    if "@" in netloc:
        raise ValueError(
            f"{field_name} must not carry user:password userinfo; store "
            "proxy credentials in the credential vault via credential_ref"
        )


@dataclass(frozen=True)
class NetworkProfile:
    """One named network configuration (D03 §27)."""

    network_profile_id: str
    name: str
    mode: str = MODE_DIRECT
    http_proxy: str = ""
    https_proxy: str = ""
    socks5_proxy: str = ""
    username: str = ""
    credential_ref: str | None = None
    bypass_hosts: frozenset[str] = DEFAULT_BYPASS_HOSTS
    inherit_system: bool = True
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS
    verify_tls: bool = True
    allow_proxy_failure_direct_fallback: bool = False
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self) -> None:
        if not self.network_profile_id:
            raise ValueError("network_profile_id must not be empty")
        if self.mode not in ALL_MODES:
            raise ValueError(f"unknown network mode: {self.mode!r}")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        for field_name in ("http_proxy", "https_proxy", "socks5_proxy"):
            value = getattr(self, field_name)
            if value:
                _reject_userinfo(value, field_name)  # R-008
        if self.mode in (MODE_HTTP, MODE_HTTPS):
            if not (self.http_proxy or self.https_proxy) and not self.inherit_system:
                raise ValueError(
                    f"mode {self.mode} requires an http(s)_proxy URL or "
                    "inherit_system=true"
                )
        if self.mode == MODE_SOCKS5 and not self.socks5_proxy and not self.inherit_system:
            raise ValueError("mode socks5 requires a socks5_proxy URL or inherit_system=true")

    def is_bypassed(self, host: str) -> bool:
        """True when ``host`` skips the proxy entirely (D03 §27).

        Exact match, or ``.suffix`` wildcard against the host's tail so
        ``.internal`` covers ``a.internal``. Only this profile's
        configured set counts; the localhost default comes from the
        constructor default, so callers can explicitly disable it.
        """
        host = host.lower().rstrip(".")
        for entry in self.bypass_hosts:
            entry = entry.lower()
            if entry.startswith("."):
                if host.endswith(entry) or host == entry[1:]:
                    return True
            elif host == entry:
                return True
        return False


class NetworkProfileStore(Protocol):
    """Persistence contract for network profiles.

    In-memory implementation for now; the SQLite adapter belongs to a
    later coordinated slice. Only ``credential_ref`` crosses this
    contract — never a proxy password.
    """

    def add_profile(self, profile: NetworkProfile) -> None: ...
    def get_profile(self, network_profile_id: str) -> NetworkProfile | None: ...
    def list_profiles(self) -> list[NetworkProfile]: ...
    def update_profile(self, profile: NetworkProfile) -> None: ...
    def delete_profile(self, network_profile_id: str) -> None: ...
