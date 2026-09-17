"""Provider profile model and store port (D03 §25, D08 AC-PROVIDER-001).

One provider adapter type may have several user profiles (e.g. OpenAI
translation, OpenAI vision OCR, OpenAI backup). Profiles are immutable
value objects: Run snapshots keep the object they were built with, so
later edits never mutate an already-frozen snapshot (D06 §50).

The model stores only ``credential_ref`` — a reference into a protected
credential store. API keys and proxy passwords never enter this model,
SQLite, logs or exports (D07 §69, AC-SEC-001/002/003).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


class ProxyPolicy:
    """How a provider profile selects its network profile (D03 §25)."""

    INHERIT = "inherit"  # use the resolved default network profile
    PROFILE = "profile"  # use this profile's own network_profile_id
    DIRECT = "direct"  # always direct, ignore any proxy
    ALL = frozenset({INHERIT, PROFILE, DIRECT})


#: Provider capabilities a binding can address (D06 §7.1, TASK-019).
CAPABILITY_DETECTION = "detection"
CAPABILITY_OCR = "ocr"
CAPABILITY_TRANSLATION = "translation"
CAPABILITY_INPAINT = "inpaint"
ALL_CAPABILITIES = frozenset(
    {CAPABILITY_DETECTION, CAPABILITY_OCR, CAPABILITY_TRANSLATION, CAPABILITY_INPAINT}
)


@dataclass(frozen=True)
class ProviderProfile:
    """User-visible configuration of one provider instance (D03 §25)."""

    provider_profile_id: str
    name: str
    provider_type: str
    capabilities: frozenset[str]
    base_url: str = ""
    model: str = ""
    credential_ref: str | None = None
    network_profile_id: str | None = None
    proxy_policy: str = ProxyPolicy.INHERIT
    options: tuple[tuple[str, str], ...] = ()  # stable-order provider params
    is_enabled: bool = True
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self) -> None:
        if not self.provider_profile_id:
            raise ValueError("provider_profile_id must not be empty")
        if self.proxy_policy not in ProxyPolicy.ALL:
            raise ValueError(f"unknown proxy policy: {self.proxy_policy!r}")
        unknown = set(self.capabilities) - ALL_CAPABILITIES
        if unknown:
            raise ValueError(f"unknown capabilities: {sorted(unknown)}")

    def option_dict(self) -> dict[str, str]:
        return dict(self.options)

    def is_local(self) -> bool:
        """Local providers run in-process and send nothing remote (D07 §87).

        Local adapter types are namespaced with the ``local-`` prefix; a
        profile without a base_url cannot reach a remote endpoint either.
        """
        return self.provider_type.startswith("local-") or not self.base_url


class ProviderProfileStore(Protocol):
    """Persistence contract for provider profiles.

    The in-memory implementation backs tests; the SQLite adapter lands in
    a later coordinated slice (TASK-029 owns the database layer). Only
    ``credential_ref`` strings ever cross this contract.
    """

    def add_profile(self, profile: ProviderProfile) -> None: ...
    def get_profile(self, provider_profile_id: str) -> ProviderProfile | None: ...
    def list_profiles(self) -> list[ProviderProfile]: ...
    def update_profile(self, profile: ProviderProfile) -> None: ...
    def delete_profile(self, provider_profile_id: str) -> None: ...
