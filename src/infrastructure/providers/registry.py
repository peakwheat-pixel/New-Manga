"""Provider registry: declared readiness and fail-closed resolution.

Nothing is resolved implicitly. A capability request names one provider id
(the value the Run's frozen Provider snapshot carries, D06 §50); an unknown or
not-ready provider raises a typed :class:`~ports.providers.errors.ProviderError`
instead of falling through to "some other available provider"
(D06 §51, AC-FALLBACK-001).

Readiness states (AC-OPTIONAL-002):

``ready``               every declared requirement is satisfied,
``missing_dependency``  an optional runtime/weight is absent,
``not_configured``      endpoint/model/credential is not configured,
``disabled``            the user disabled the profile,
``not_ready``           configured but currently unrunnable (e.g. model
                        download incomplete — AC-MODEL-002),
``unknown``             no descriptor registered for that id.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field
from typing import Any

from infrastructure.providers.dependencies import (
    Requirement,
    RequirementProbe,
    evaluate_requirements,
    failure_for,
)
from ports.providers.errors import (
    ProviderDisabled,
    ProviderError,
    ProviderNotConfigured,
    ProviderNotImplemented,
    ProviderState,
    ProviderStatus,
    ProviderUnavailable,
)

#: A gate may add runtime readiness (e.g. "weights are verified and loaded").
ReadinessGate = Callable[[], tuple[bool, str, str]]


@dataclass(frozen=True)
class ProviderDescriptor:
    """Static declaration of one provider instance."""

    provider_id: str
    provider_type: str
    capabilities: frozenset[str]
    requirements: tuple[Requirement, ...] = ()
    requires_gpu: bool = False
    supports_cpu_fallback: bool = False
    heavy_gpu: bool = False
    allow_concurrent: bool = False
    implements: bool = True
    note: str = ""

    def __post_init__(self) -> None:
        if not self.provider_id or not self.provider_type:
            raise ValueError("a descriptor needs provider_id and provider_type")

    @property
    def heavy_gate_capacity(self) -> int:
        """GPU-heavy providers serialise to one slot unless they opt out."""
        return 2 if self.allow_concurrent else 1


@dataclass(frozen=True)
class ProviderRegistration:
    descriptor: ProviderDescriptor
    factory: Callable[[], Any] | None = None
    gate: ReadinessGate | None = None
    enabled: bool = True


@dataclass
class ProviderRegistry:
    """Registry of provider descriptors with probed readiness."""

    credential_resolver: Callable[[str], str | None] | None = None
    _registrations: dict[str, ProviderRegistration] = field(default_factory=dict, repr=False)
    _instances: dict[str, Any] = field(default_factory=dict, repr=False)

    # ------------------------------------------------------------------
    # registration
    # ------------------------------------------------------------------

    def register(
        self,
        descriptor: ProviderDescriptor,
        factory: Callable[[], Any] | None = None,
        *,
        gate: ReadinessGate | None = None,
        enabled: bool = True,
    ) -> ProviderRegistration:
        registration = ProviderRegistration(
            descriptor=descriptor, factory=factory, gate=gate, enabled=enabled
        )
        self._registrations[descriptor.provider_id] = registration
        return registration

    def set_enabled(self, provider_id: str, enabled: bool) -> None:
        registration = self._require_registration(provider_id)
        self._registrations[provider_id] = ProviderRegistration(
            descriptor=registration.descriptor,
            factory=registration.factory,
            gate=registration.gate,
            enabled=enabled,
        )

    def descriptors(self) -> tuple[ProviderDescriptor, ...]:
        return tuple(
            registration.descriptor
            for registration in self._registrations.values()
        )

    def descriptors_for(self, capability: str) -> tuple[ProviderDescriptor, ...]:
        return tuple(
            registration.descriptor
            for registration in self._registrations.values()
            if capability in registration.descriptor.capabilities
        )

    def provider_ids(self) -> tuple[str, ...]:
        return tuple(self._registrations)

    # ------------------------------------------------------------------
    # readiness (AC-OPTIONAL-002)
    # ------------------------------------------------------------------

    def probes(self, provider_id: str) -> tuple[RequirementProbe, ...]:
        registration = self._require_registration(provider_id)
        return evaluate_requirements(
            registration.descriptor.requirements,
            credential_resolver=self.credential_resolver,
        )

    def status(self, provider_id: str) -> ProviderStatus:
        registration = self._registrations.get(provider_id)
        if registration is None:
            return ProviderStatus(
                provider_id=provider_id,
                provider_type="",
                capabilities=frozenset(),
                state=ProviderState.UNKNOWN,
                error_code="PROVIDER_UNKNOWN",
                detail="no provider descriptor registered under this id",
            )
        descriptor = registration.descriptor
        probes = evaluate_requirements(
            descriptor.requirements, credential_resolver=self.credential_resolver
        )
        missing = tuple(
            probe.as_dict()["name"] for probe in probes if not probe.satisfied
        )

        def build(
            state: str,
            error_code: str = "",
            detail: str = "",
            *,
            missing_requirements: tuple[str, ...] = (),
        ) -> ProviderStatus:
            return ProviderStatus(
                provider_id=descriptor.provider_id,
                provider_type=descriptor.provider_type,
                capabilities=descriptor.capabilities,
                state=state,
                error_code=error_code,
                detail=detail,
                missing_requirements=missing_requirements,
            )

        if not registration.enabled:
            return build(
                ProviderState.DISABLED,
                ProviderDisabled.error_code,
                "provider is disabled by the user",
                missing_requirements=missing,
            )
        if not descriptor.implements:
            return build(
                ProviderState.NOT_READY,
                ProviderNotImplemented.error_code,
                descriptor.note or "no implementation registered in this build",
                missing_requirements=missing,
            )
        failure = failure_for(probes, provider_id=descriptor.provider_id)
        if failure is not None:
            state = (
                ProviderState.NOT_CONFIGURED
                if isinstance(failure, ProviderNotConfigured)
                else ProviderState.MISSING_DEPENDENCY
            )
            return build(
                state,
                failure.error_code,
                failure.detail,
                missing_requirements=missing,
            )
        if registration.gate is not None:
            ready, error_code, detail = registration.gate()
            if not ready:
                return build(
                    ProviderState.NOT_READY,
                    error_code or "PROVIDER_NOT_READY",
                    detail,
                    missing_requirements=missing,
                )
        return build(ProviderState.READY)

    def statuses(self) -> tuple[ProviderStatus, ...]:
        return tuple(self.status(provider_id) for provider_id in self._registrations)

    def readiness_report(self) -> tuple[dict, ...]:
        return tuple(status.as_dict() for status in self.statuses())

    # ------------------------------------------------------------------
    # resolution
    # ------------------------------------------------------------------

    def resolve(self, capability: str, provider_id: str) -> Any:
        """Return the provider instance for one capability or fail closed."""
        registration = self._registrations.get(provider_id)
        if registration is None:
            raise ProviderUnavailable(
                f"no provider registered as {provider_id!r}",
                provider_id=provider_id,
                stage="resolve",
            )
        descriptor = registration.descriptor
        if capability not in descriptor.capabilities:
            raise ProviderNotConfigured(
                f"provider {provider_id!r} does not declare capability"
                f" {capability!r}",
                provider_id=provider_id,
                stage="resolve",
            )
        status = self.status(provider_id)
        if not status.ready:
            raise _status_error(status)
        if registration.factory is None:
            raise ProviderNotImplemented(
                f"provider {provider_id!r} has no factory registered",
                provider_id=provider_id,
                stage="resolve",
            )
        if provider_id not in self._instances:
            self._instances[provider_id] = registration.factory()
        return self._instances[provider_id]

    def resolve_binding(self, capability: str, binding: Any) -> Any:
        """Resolve the provider named by a Run's frozen binding snapshot.

        Accepts the frozen mapping shape used by the pipeline
        (``{"provider_id": ...}`` / ``provider_profile_id`` / ``id``) or a
        plain string. The explicit ``enabled``/``available`` flags of the
        snapshot are honoured before any registry lookup.
        """
        if binding is None:
            raise ProviderNotConfigured(
                f"no binding configured for capability {capability!r}",
                stage="resolve",
            )
        if isinstance(binding, str):
            return self.resolve(capability, binding)
        if isinstance(binding, Mapping):
            if binding.get("enabled") is False or binding.get("available") is False:
                raise ProviderDisabled(
                    f"binding for {capability!r} is disabled in this Run",
                    stage="resolve",
                )
            for key in ("provider_id", "provider_profile_id", "id"):
                value = binding.get(key)
                if isinstance(value, str) and value:
                    return self.resolve(capability, value)
        raise ProviderNotConfigured(
            f"binding for capability {capability!r} names no provider",
            stage="resolve",
        )

    def invalidate(self, provider_id: str | None = None) -> None:
        """Drop cached instances (e.g. after an OOM unload or a settings edit)."""
        if provider_id is None:
            self._instances.clear()
        else:
            self._instances.pop(provider_id, None)

    def _require_registration(self, provider_id: str) -> ProviderRegistration:
        registration = self._registrations.get(provider_id)
        if registration is None:
            raise ProviderUnavailable(
                f"no provider registered as {provider_id!r}", provider_id=provider_id
            )
        return registration


def _status_error(status: ProviderStatus) -> ProviderError:
    """Map a Not-Ready status onto the closed error taxonomy."""
    mapping: dict[str, type[ProviderError]] = {
        ProviderNotImplemented.error_code: ProviderNotImplemented,
        ProviderDisabled.error_code: ProviderDisabled,
    }
    error_type = mapping.get(status.error_code)
    if error_type is not None:
        return error_type(status.detail, provider_id=status.provider_id, stage="resolve")
    if status.state == ProviderState.NOT_CONFIGURED:
        return ProviderNotConfigured(
            status.detail, provider_id=status.provider_id, stage="resolve"
        )
    if status.state == ProviderState.MISSING_DEPENDENCY:
        from ports.providers.errors import ProviderDependencyMissing

        return ProviderDependencyMissing(
            status.detail, provider_id=status.provider_id, stage="resolve"
        )
    return ProviderUnavailable(
        status.detail or status.state, provider_id=status.provider_id, stage="resolve"
    )


def build_registry(
    registrations: Iterable[tuple[ProviderDescriptor, Callable[[], Any] | None]],
    *,
    credential_resolver: Callable[[str], str | None] | None = None,
) -> ProviderRegistry:
    registry = ProviderRegistry(credential_resolver=credential_resolver)
    for descriptor, factory in registrations:
        registry.register(descriptor, factory)
    return registry
