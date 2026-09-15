"""Frozen settings snapshots for pipeline runs (D06 §49~50, D08
AC-PROVIDER-003/004).

A snapshot is built once when a run is created. Because profiles are
immutable value objects and the snapshot holds direct references — not
store lookups — later edits to global settings, bindings or profiles
cannot mutate an existing snapshot (AC-PROVIDER-003).

Restarting an interrupted run must not silently switch providers
(AC-PROVIDER-004): :func:`validate_snapshot` reports profiles that have
since been deleted or disabled so the UI can demand an explicit
rebinding decision.
"""

from __future__ import annotations

from types import MappingProxyType
from dataclasses import dataclass, field

from ports.network.profiles import NetworkProfile
from ports.providers.profiles import ProviderProfile

from .bindings import BindingResolution
from .models import EffectiveSetting


@dataclass(frozen=True)
class SettingsSnapshot:
    """Everything a run needs to reproduce its configuration (D06 §49).

    The mappings are wrapped in ``MappingProxyType`` on construction
    (R-006): the snapshot holder — e.g. an in-flight run — cannot have
    its providers or settings silently replaced by mutation.
    """

    settings: dict[str, EffectiveSetting] = field(default_factory=dict)
    bindings: dict[str, BindingResolution] = field(default_factory=dict)  # by capability
    provider_profiles: dict[str, ProviderProfile] = field(default_factory=dict)
    network_profiles: dict[str, NetworkProfile] = field(default_factory=dict)
    created_at: str = ""

    def __post_init__(self) -> None:
        for name in (
            "settings",
            "bindings",
            "provider_profiles",
            "network_profiles",
        ):
            object.__setattr__(
                self, name, MappingProxyType(dict(getattr(self, name)))
            )


@dataclass(frozen=True)
class SnapshotIssue:
    """One snapshot profile that no longer satisfies its contract."""

    capability: str | None
    provider_profile_id: str
    problem: str  # "missing" | "disabled"

    @property
    def requires_rebinding(self) -> bool:
        return True  # every issue demands an explicit user decision


def build_snapshot(
    *,
    settings: dict[str, EffectiveSetting],
    bindings: dict[str, BindingResolution],
    provider_profiles: dict[str, ProviderProfile],
    network_profiles: dict[str, NetworkProfile],
    created_at: str = "",
) -> SettingsSnapshot:
    """Freeze resolution results into an immutable run snapshot.

    Callers pass exactly the objects they resolved; the builder copies
    the mappings so later dict mutations in the caller's stores cannot
    leak into the snapshot.
    """
    return SettingsSnapshot(
        settings=dict(settings),
        bindings=dict(bindings),
        provider_profiles=dict(provider_profiles),
        network_profiles=dict(network_profiles),
        created_at=created_at,
    )


def snapshot_provider_view(snapshot: SettingsSnapshot) -> dict[str, ProviderProfile]:
    """Profiles referenced by this snapshot's bindings (frozen copies).

    The returned mapping only reflects the snapshot; it is what restart
    validation compares against current stores.
    """
    return dict(snapshot.provider_profiles)


def validate_snapshot(
    snapshot: SettingsSnapshot,
    *,
    current_profile_store,
) -> list[SnapshotIssue]:
    """Report snapshot bindings whose profile vanished or got disabled.

    Returns issues instead of substitutes on purpose: the caller (UI)
    must ask the user to rebind; the run stays interrupted/blocked
    meanwhile (D06 §50, AC-PROVIDER-004).
    """
    issues: list[SnapshotIssue] = []
    for capability, resolution in sorted(snapshot.bindings.items()):
        profile_id = resolution.provider_profile.provider_profile_id
        current = current_profile_store.get_profile(profile_id)
        if current is None:
            issues.append(
                SnapshotIssue(
                    capability=capability,
                    provider_profile_id=profile_id,
                    problem="missing",
                )
            )
        elif not current.is_enabled:
            issues.append(
                SnapshotIssue(
                    capability=capability,
                    provider_profile_id=profile_id,
                    problem="disabled",
                )
            )
    return issues
