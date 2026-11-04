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
from dataclasses import dataclass, field, replace
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
    """Registry of provider descriptors with probed readiness.

    ``binding_aliases`` maps a Settings-UI provider profile id **plus the
    capability being resolved** to the fixed registry id whose slot
    carries that profile's configuration (the projection built at
    assembly by ``build_provider_runtime``). The capability is part of the
    key because one multi-capability profile may legitimately be bound to
    several steps and therefore live in several fixed slots; a flat
    profile-id map would let the last binding win and route the other
    capabilities to the wrong provider. Resolution translates an aliased
    id up front, so a Run's frozen snapshot can name the user profile
    while readiness and instance caching stay keyed by the one registry
    id.
    """

    credential_resolver: Callable[[str], str | None] | None = None
    binding_aliases: Mapping[tuple[str, str], str] = field(default_factory=dict, repr=False)
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

    def descriptor(
        self, provider_id: str, *, capability: str | None = None
    ) -> ProviderDescriptor | None:
        """The static declaration behind one provider id, or ``None``.

        Read-only companion to :meth:`resolve`. Callers that need the declared
        capability flags (``requires_gpu`` / ``supports_cpu_fallback``, D06
        §82) must ask the descriptor: resolution returns the provider
        *instance*, and implementations do not repeat those declarations.

        When ``capability`` is given the same binding-alias translation
        :meth:`resolve` applies is honoured, so a Run's frozen user-profile id
        maps onto the fixed registry slot serving that capability. An unknown
        id returns ``None`` instead of raising: this is a lookup, not a
        resolution, and resolution keeps its fail-closed semantics.
        """
        if capability is not None:
            provider_id = self.binding_aliases.get(
                (provider_id, capability), provider_id
            )
        registration = self._registrations.get(provider_id)
        return registration.descriptor if registration is not None else None

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
        provider_id = self.binding_aliases.get(
            (provider_id, capability), provider_id
        )
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

    def freeze_run_snapshots(self, snapshots):
        """Capture only the typed provider execution fields; never instance __dict__."""
        from application.tasks.store import FrozenRunSnapshots, snapshot_value, snapshot_digest
        from domain.tasks.models import freeze_snapshot
        bindings = snapshot_value(snapshots.provider_bindings)
        for step, capability in (("translate", "translation"), ("ocr", "ocr")):
            binding = bindings.get(step)
            if not binding:
                continue
            provider_id = binding if isinstance(binding, str) else next((
                binding.get(key) for key in ("provider_id", "provider_profile_id", "id") if binding.get(key)), None)
            if not provider_id:
                continue
            try:
                provider = self.resolve(capability, provider_id)
            except ProviderError:
                # Preserve unavailable bindings: the existing planner owns blocking.
                continue
            config = getattr(provider, "config", None)
            if config is None:
                continue
            # A credential reference is an opaque vault lookup, never authentication bytes.
            execution = {key: getattr(config, key) for key in (
                "provider_id", "provider_type", "base_url", "model", "credential_ref",
                "timeout_seconds", "extra_options")}
            profile = config.network_profile
            execution["network_profile"] = None if profile is None else {
                key: snapshot_value(getattr(profile, key)) for key in (
                    "network_profile_id", "name", "mode", "http_proxy", "https_proxy", "socks5_proxy",
                    "username", "credential_ref", "inherit_system", "timeout_seconds", "verify_tls",
                    "allow_proxy_failure_direct_fallback", "created_at", "updated_at")}
            if profile is not None:
                execution["network_profile"]["bypass_hosts"] = sorted(profile.bypass_hosts)
            execution["target_language"] = getattr(provider, "target_language", "")
            execution["options"] = list(getattr(provider, "options", ()))
            allowed_options = {"temperature", "top_p", "max_tokens", "max_completion_tokens", "seed",
                               "frequency_penalty", "presence_penalty", "stop"}
            if any(key not in allowed_options for key, _ in execution["options"]):
                from domain.tasks.models import PipelineError
                raise PipelineError("RUN_SNAPSHOT_INCOMPLETE", "provider options contain unsupported replay fields")
            # Endpoint credentials are prohibited even when smuggled via query/userinfo.
            from urllib.parse import urlsplit
            url = urlsplit(config.base_url)
            if url.username or url.password or url.query or url.fragment:
                from domain.tasks.models import PipelineError
                raise PipelineError("RUN_SNAPSHOT_INCOMPLETE", "provider endpoint is not snapshot-safe")
            value = {"provider_id": provider_id} if isinstance(binding, str) else dict(binding)
            value["execution"] = execution
            value["execution_digest"] = snapshot_digest(execution)
            if isinstance(binding, Mapping):
                from infrastructure.providers.fallback import chain_from_binding
                chain = chain_from_binding(binding)
                if chain is not None and chain.explicit_fallbacks:
                    value["frozen_fallbacks"] = {
                        fallback_id: snapshot_value(self.freeze_run_snapshots(FrozenRunSnapshots(
                            snapshots.settings, {step: fallback_id}, snapshots.constraint_snapshot_ref,
                            snapshots.context_policy)).provider_bindings[step])
                        for fallback_id in chain.explicit_fallbacks
                    }
            bindings[step] = value
        return FrozenRunSnapshots(snapshots.settings, freeze_snapshot(bindings),
                                  snapshots.constraint_snapshot_ref, snapshots.context_policy)

    def resolve_for_run(self, capability: str, provider_id: str, binding: Any) -> Any:
        provider = self.resolve(capability, provider_id)
        if not isinstance(binding, Mapping) or "execution" not in binding:
            return provider
        named = next((binding.get(key) for key in ("provider_id", "provider_profile_id", "id") if binding.get(key)), None)
        if provider_id != named:
            fallback = binding.get("frozen_fallbacks", {}).get(provider_id)
            if fallback is None:
                raise ProviderUnavailable("fallback has no frozen execution configuration", stage="resolve")
            return self.resolve_for_run(capability, provider_id, fallback)
        from application.tasks.store import snapshot_digest
        execution = binding["execution"]
        if snapshot_digest(execution) != binding.get("execution_digest"):
            raise ProviderUnavailable("frozen provider configuration is incomplete", stage="resolve")
        from infrastructure.providers.openai_client import OpenAiCompatibleClient, OpenAiCompatibleConfig
        from ports.network.profiles import NetworkProfile
        config_values = {key: execution[key] for key in (
            "provider_id", "provider_type", "base_url", "model", "credential_ref", "timeout_seconds")}
        profile = execution["network_profile"]
        config_values["network_profile"] = None if profile is None else NetworkProfile(
            **{**profile, "bypass_hosts": frozenset(profile["bypass_hosts"])})
        config_values["extra_options"] = tuple(tuple(item) for item in execution["extra_options"])
        config = OpenAiCompatibleConfig(**config_values)
        client = provider.client
        frozen_client = OpenAiCompatibleClient(config, client._transport,
                                              credential_resolver=client._credential_resolver)
        values = {"config": config, "client": frozen_client, "options": tuple(tuple(item) for item in execution["options"])}
        if hasattr(provider, "target_language"):
            values["target_language"] = execution["target_language"]
        return replace(provider, **values)

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
