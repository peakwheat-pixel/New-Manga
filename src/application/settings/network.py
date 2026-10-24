"""Network profile management and provider-to-network resolution
(D03 §25/§27, D07 §67~68, AC-SEC-004/005).

``NetworkProfileService`` owns the dangerous-setting gates:

- every new profile keeps ``verify_tls=True`` unless the caller already
  confirms the dangerous opt-out at creation (AC-SEC-004);
- flipping ``verify_tls`` off on an existing profile requires an
  explicit ``confirm_disable_tls=True`` — a silent default-off is a
  contract violation and raises (AC-SEC-005);
- enabling ``allow_proxy_failure_direct_fallback`` is allowed but the
  returned decision records it, so callers/UI can surface the change
  (D06 §55: fallback must stay visible and auditable).

``ProviderNetworkResolver`` maps a provider profile's ``proxy_policy``
(inherit / profile / direct) plus the effective settings to the network
profile that transport should use (D03 §25).
"""

from __future__ import annotations

from dataclasses import dataclass

from ports.network.profiles import NetworkProfile, NetworkProfileStore
from ports.providers.profiles import ProxyPolicy, ProviderProfile

from .errors import SettingsError
from .models import EffectiveSetting

#: Settings key holding the default network profile (global default).
NETWORK_PROFILE_SETTING_KEY = "network.profile_id"


class DangerousSettingError(SettingsError):
    """A dangerous option was changed without explicit confirmation."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.confirmation_required = True


@dataclass(frozen=True)
class ProfileUpdateDecision:
    """Outcome of a profile write, including visibility notes."""

    profile: NetworkProfile
    notes: tuple[str, ...] = ()


class NetworkProfileService:
    """CRUD facade with safety gates over a ``NetworkProfileStore``."""

    def __init__(self, store: NetworkProfileStore) -> None:
        self._store = store

    def create_profile(
        self, profile: NetworkProfile, *, confirm_disable_tls: bool = False
    ) -> ProfileUpdateDecision:
        if not profile.verify_tls and not confirm_disable_tls:
            raise DangerousSettingError(
                "creating a profile with verify_tls=False requires explicit "
                "confirmation (AC-SEC-005)"
            )
        notes = self._notes_for(profile)
        self._store.add_profile(profile)
        return ProfileUpdateDecision(profile, notes)

    def update_profile(
        self, profile: NetworkProfile, *, confirm_disable_tls: bool = False
    ) -> ProfileUpdateDecision:
        existing = self._store.get_profile(profile.network_profile_id)
        if existing is None:
            raise SettingsError(f"network profile {profile.network_profile_id!r} not found")
        if existing.verify_tls and not profile.verify_tls and not confirm_disable_tls:
            raise DangerousSettingError(
                f"disabling TLS verification on {profile.network_profile_id!r} "
                "requires explicit confirmation (AC-SEC-005)"
            )
        notes = self._notes_for(profile)
        if existing.allow_proxy_failure_direct_fallback != profile.allow_proxy_failure_direct_fallback:
            notes = notes + (
                "allow_proxy_failure_direct_fallback changed; direct fallback "
                "events remain visible in outcomes (D06 §55)",
            )
        self._store.update_profile(profile)
        return ProfileUpdateDecision(profile, notes)

    def delete_profile(self, network_profile_id: str) -> None:
        self._store.delete_profile(network_profile_id)

    def get_profile(self, network_profile_id: str) -> NetworkProfile | None:
        return self._store.get_profile(network_profile_id)

    def list_profiles(self) -> list[NetworkProfile]:
        return self._store.list_profiles()

    @staticmethod
    def _notes_for(profile: NetworkProfile) -> tuple[str, ...]:
        notes: list[str] = []
        if not profile.verify_tls:
            notes.append("TLS verification disabled (dangerous setting)")
        if profile.allow_proxy_failure_direct_fallback:
            notes.append("proxy failure may fall back to direct (visible)")
        return tuple(notes)


class ProviderNetworkResolver:
    """Resolve which network profile a provider profile uses (D03 §25).

    ``proxy_policy``:
      - ``direct``  → always the direct profile.
      - ``profile`` → the provider's own ``network_profile_id`` (must
        exist; missing raises instead of guessing).
      - ``inherit`` → the effective ``network.profile_id`` setting for
        the context, falling back to a direct profile when unset.
    """

    def __init__(
        self,
        network_store: NetworkProfileStore,
        *,
        direct_profile: NetworkProfile | None = None,
    ) -> None:
        self._networks = network_store
        self._direct = direct_profile or NetworkProfile(
            network_profile_id="direct-default", name="直连"
        )

    def resolve(
        self,
        provider: ProviderProfile,
        *,
        network_setting: EffectiveSetting | None = None,
    ) -> NetworkProfile:
        if provider.proxy_policy == ProxyPolicy.DIRECT:
            return self._direct
        if provider.proxy_policy == ProxyPolicy.PROFILE:
            profile_id = provider.network_profile_id
            if not profile_id:
                raise SettingsError(
                    f"provider {provider.provider_profile_id!r} uses "
                    "proxy_policy=profile without a network_profile_id"
                )
            profile = self._networks.get_profile(profile_id)
            if profile is None:
                raise SettingsError(
                    f"provider {provider.provider_profile_id!r} references "
                    f"missing network profile {profile_id!r}"
                )
            return profile
        # inherit
        if network_setting is not None:
            profile = self._networks.get_profile(network_setting.value)
            if profile is None:
                raise SettingsError(
                    f"effective {NETWORK_PROFILE_SETTING_KEY}="
                    f"{network_setting.value!r} does not match any network profile"
                )
            return profile
        return self._direct
