"""Runtime mirror of P15 provider profiles / capability bindings.

TRANS-BINDING-BRIDGE (L1-T-A, AC1–AC4). The Run runtime reads its provider
configuration from the single ``pipeline_defaults`` row:

* ``settings["providers"]["profiles"][profile_id]`` — the per-profile runtime
  shape read by ``infrastructure.providers.runtime`` (``_openai_config``
  ``base_url``/``model``/``credential_ref``/``options``, ``_slot_enabled``
  ``enabled``, ``_network_profile_for`` ``proxy_policy``/``network_profile_id``,
  ``_apply_profile_bindings`` ``provider_type``);
* ``provider_bindings[step]`` — the step → profile binding consumed by
  ``handlers._chain`` (a missing binding is the actual
  ``PROVIDER_NOT_CONFIGURED`` source) and projected onto the fixed registry
  slots by ``_apply_profile_bindings``.

P15 (``settings_provider_profiles_*`` / ``settings_provider_bindings_*``)
persists to JSON files under ``<data_root>/settings``. Historically only the
legacy QML settings view model mirrored those writes into the run settings
(``src/ui/viewmodels/settings/viewmodel.py``); the Core command surface had no
such writer, so any other client (Host/Avalonia) configured a provider that the
runtime could never see.

This module is that missing writer. It writes **only** through the
``PipelineDefaultsService`` seam (``save_settings_section`` /
``save_provider_binding`` / ``clear_provider_binding``) so no second
persistence implementation is invented and no wire command is added.

Secrets never cross this surface (AC2): a profile carries a ``credential_ref``
reference only, and the mirror copies that reference verbatim. ``credential_ref``
is the sole credential-shaped key; no secret value is ever accepted here.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ports.providers.profiles import (
    CAPABILITY_DETECTION,
    CAPABILITY_INPAINT,
    CAPABILITY_OCR,
    CAPABILITY_TRANSLATION,
    ProxyPolicy,
    ProviderProfile,
)

#: P15 capability → pipeline step. ``rendering`` is deliberately absent: render
#: is a local step that consumes no remote provider profile, so binding it must
#: not invent a step (fail-closed: ``bind_capability`` returns ``None`` and the
#: caller keeps the JSON-store-only semantics of that capability).
CAPABILITY_TO_STEP: dict[str, str] = {
    CAPABILITY_DETECTION: "detect",
    CAPABILITY_OCR: "ocr",
    CAPABILITY_TRANSLATION: "translate",
    CAPABILITY_INPAINT: "inpaint",
}

#: The settings section holding the runtime projection.
PROVIDERS_SECTION = "providers"

#: ``credential_ref`` is a reference into the platform credential store; it is
#: the only credential-shaped key this mirror may carry (AC2).
CREDENTIAL_REF_KEY = "credential_ref"


def profile_mirror_entry(profile: ProviderProfile) -> dict[str, Any]:
    """The exact runtime shape for one profile (AC1 key set).

    Keys match what ``infrastructure.providers.runtime`` reads; ``capabilities``
    is carried as a sorted list for observability/diagnostics (the runtime does
    not read it, and it contains no secret). ``credential_ref`` is copied as the
    reference only — the secret stays in the credential store.
    """
    return {
        "provider_type": profile.provider_type,
        "base_url": profile.base_url,
        "model": profile.model,
        CREDENTIAL_REF_KEY: profile.credential_ref,
        "enabled": profile.is_enabled,
        "options": profile.option_dict(),
        "network_profile_id": profile.network_profile_id or "",
        "proxy_policy": profile.proxy_policy or ProxyPolicy.INHERIT,
        "capabilities": sorted(profile.capabilities),
    }


def _providers_section(settings: Mapping[str, Any]) -> dict[str, Any]:
    raw = settings.get(PROVIDERS_SECTION)
    return dict(raw) if isinstance(raw, Mapping) else {}


def _profiles_section(providers: Mapping[str, Any]) -> dict[str, Any]:
    raw = providers.get("profiles")
    return dict(raw) if isinstance(raw, Mapping) else {}


class ProviderRuntimeMirror:
    """Write-through mirror over one ``PipelineDefaultsService`` (AC1/AC3/AC4).

    Every method is a single seam call, so a failure surfaces as a typed
    ``BindingValidationError`` (the service's own error) to the caller, which
    then rolls the JSON store back. The mirror never writes the JSON stores
    itself and never invents a second persistence path.
    """

    def __init__(self, defaults) -> None:
        self._defaults = defaults

    # -- read ----------------------------------------------------------

    def profiles(self) -> dict[str, Any]:
        return _profiles_section(_providers_section(self._defaults.read().settings))

    def provider_bindings(self) -> dict[str, Any]:
        return dict(self._defaults.read().provider_bindings)

    # -- write ---------------------------------------------------------

    def upsert_profile(self, profile: ProviderProfile) -> None:
        providers = _providers_section(self._defaults.read().settings)
        profiles = _profiles_section(providers)
        profiles[profile.provider_profile_id] = profile_mirror_entry(profile)
        providers["profiles"] = profiles
        self._defaults.save_settings_section(PROVIDERS_SECTION, providers)

    def remove_profile(self, profile_id: str) -> None:
        providers = _providers_section(self._defaults.read().settings)
        profiles = _profiles_section(providers)
        if profile_id not in profiles:
            return
        profiles.pop(profile_id, None)
        providers["profiles"] = profiles
        self._defaults.save_settings_section(PROVIDERS_SECTION, providers)

    def bind_capability(self, capability: str, profile_id: str) -> str | None:
        """Mirror one capability binding; ``None`` when the capability has no step."""
        step = CAPABILITY_TO_STEP.get(capability)
        if step is None:
            return None
        self._defaults.save_provider_binding(step, profile_id)
        return step

    def clear_capability(self, capability: str) -> str | None:
        step = CAPABILITY_TO_STEP.get(capability)
        if step is None:
            return None
        self._defaults.clear_provider_binding(step)
        return step

    # -- rollback ------------------------------------------------------

    def snapshot(self) -> tuple[dict[str, Any], dict[str, Any]]:
        """Capture (providers section, provider bindings) for a rollback."""
        defaults = self._defaults.read()
        return _providers_section(defaults.settings), dict(defaults.provider_bindings)

    def restore(self, snapshot: tuple[Mapping[str, Any], Mapping[str, Any]]) -> None:
        """Best-effort restore of a snapshot (used only on the failure path).

        Restoring the settings section re-writes only ``providers``; the other
        settings sections are untouched because ``save_settings_section`` is a
        per-section upsert.
        """
        providers, bindings = snapshot
        defaults = self._defaults.read()
        current = dict(defaults.provider_bindings)
        for step in current:
            if step not in bindings:
                self._defaults.clear_provider_binding(step)
        for step, binding in bindings.items():
            if current.get(step) != binding:
                self._defaults.save_provider_binding(step, binding)
        current_providers = _providers_section(defaults.settings)
        if current_providers != dict(providers):
            self._defaults.save_settings_section(PROVIDERS_SECTION, dict(providers))
