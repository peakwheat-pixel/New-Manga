"""Provider binding resolution by capability and scope (D03 §26,
D06 §51, D08 AC-PROVIDER-002, AC-OCR-003).

Resolution priority (most specific wins):

    task (current-run explicit choice)
        > chapter binding
        > book binding
        > global default binding

Within one scope, the highest-priority enabled binding wins. If nothing
matches, :class:`UnresolvedCapabilityError` is raised — the caller must
ask the user to bind a provider; picking any available provider would
violate the no-implicit-fallback rule (D06 §51).
"""

from __future__ import annotations

from dataclasses import dataclass

from ports.providers.profiles import ProviderProfile

from .errors import UnresolvedCapabilityError
from .models import SCOPE_BOOK, SCOPE_CHAPTER, SCOPE_GLOBAL, SCOPE_TASK


@dataclass(frozen=True)
class ProviderBinding:
    """Default provider choice for one capability at one scope (D03 §26)."""

    binding_id: str
    scope_type: str
    scope_id: str | None
    capability: str
    provider_profile_id: str
    priority: int = 0
    enabled: bool = True

    def __post_init__(self) -> None:
        if self.scope_type not in (SCOPE_GLOBAL, SCOPE_BOOK, SCOPE_CHAPTER):
            raise ValueError(f"binding scope must be global/book/chapter, got {self.scope_type!r}")
        if self.scope_type != SCOPE_GLOBAL and not self.scope_id:
            raise ValueError(f"binding scope {self.scope_type} requires scope_id")
        if self.scope_type == SCOPE_GLOBAL and self.scope_id:
            raise ValueError("global binding must not carry scope_id")


@dataclass(frozen=True)
class BindingResolution:
    """The chosen profile plus where the choice came from."""

    capability: str
    provider_profile: ProviderProfile
    source_scope_type: str
    source_scope_id: str | None
    binding: ProviderBinding | None  # None only for the task-scope choice

    @property
    def source_label(self) -> str:
        if self.source_scope_id:
            return f"{self.source_scope_type}:{self.source_scope_id}"
        return self.source_scope_type


class ProviderBindingResolver:
    """Resolve which provider profile serves a capability in context."""

    def __init__(self, profile_store) -> None:
        self._profiles = profile_store

    def resolve(
        self,
        capability: str,
        *,
        bindings: list[ProviderBinding] | tuple[ProviderBinding, ...] = (),
        book_id: str | None = None,
        chapter_id: str | None = None,
        task_profile_id: str | None = None,
    ) -> BindingResolution:
        if task_profile_id:
            profile = self._profiles.get_profile(task_profile_id)
            if profile is None or not profile.is_enabled:
                raise UnresolvedCapabilityError(
                    capability,
                    f"task-selected provider profile {task_profile_id!r} "
                    "does not exist or is disabled",
                )
            self._check_capability(profile, capability)  # R-007
            return BindingResolution(
                capability=capability,
                provider_profile=profile,
                source_scope_type=SCOPE_TASK,
                source_scope_id=None,
                binding=None,
            )

        # Most specific scope first; first scope with any enabled
        # binding wins outright (D03 §26).
        wanted: list[tuple[str, str | None]] = []
        if chapter_id:
            wanted.append((SCOPE_CHAPTER, chapter_id))
        if book_id:
            wanted.append((SCOPE_BOOK, book_id))
        wanted.append((SCOPE_GLOBAL, None))

        for scope_type, scope_id in wanted:
            matches = [
                b
                for b in bindings
                if b.enabled
                and b.capability == capability
                and b.scope_type == scope_type
                and b.scope_id == scope_id
            ]
            if not matches:
                continue
            binding = max(matches, key=lambda b: b.priority)
            profile = self._profiles.get_profile(binding.provider_profile_id)
            if profile is None or not profile.is_enabled:
                raise UnresolvedCapabilityError(
                    capability,
                    f"binding {binding.binding_id!r} points to missing/disabled "
                    f"profile {binding.provider_profile_id!r}",
                )
            self._check_capability(profile, capability)  # R-007
            return BindingResolution(
                capability=capability,
                provider_profile=profile,
                source_scope_type=scope_type,
                source_scope_id=scope_id,
                binding=binding,
            )

        raise UnresolvedCapabilityError(
            capability,
            f"no enabled binding for capability {capability!r} in this scope",
        )

    @staticmethod
    def _check_capability(profile: ProviderProfile, capability: str) -> None:
        """R-007: a resolved profile must actually declare the capability.

        Otherwise an OCR request could silently run on a
        translation-only profile. Raises instead of degrading: an
        invalid binding must surface to the user (D06 §51).
        """
        if capability not in profile.capabilities:
            raise UnresolvedCapabilityError(
                capability,
                f"profile {profile.provider_profile_id!r} does not declare "
                f"capability {capability!r} (has {sorted(profile.capabilities)})",
            )
