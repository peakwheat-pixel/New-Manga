"""Typed provider error taxonomy and readiness states (D06 §56/§92, TASK-019).

This module is **additive**: ``profiles.py`` keeps every existing field and
semantic; only the capability constant set there is extended. Nothing in the
existing profile/capability contract changes.

Every provider capability (detection / OCR / translation / inpaint) fails
through one closed taxonomy so the pipeline can classify a failure without
knowing which adapter produced it:

- ``error_code``  — the stable D06 §92 style code carried into ``StepRun``;
- ``retryable``   — D06 §56.1/§56.2: only transport/provider-transient faults
  retry inside the same provider; authentication, missing credentials and
  invalid local input fail immediately and wait for the user;
- ``provider_id`` — which provider produced the failure (provenance).

The retryability sets absorb the TASK-017 experiment classification
(``experiments/TASK-017/protocol.py``): provider-transport faults and malformed
provider output are retryable, authentication and invalid local input are not.
"""

from __future__ import annotations

from dataclasses import dataclass


class ProviderError(RuntimeError):
    """Base class for every typed provider failure."""

    error_code = "PROVIDER_FAILED"
    retryable = False

    def __init__(
        self,
        detail: str = "",
        *,
        provider_id: str = "",
        stage: str = "",
    ) -> None:
        self.detail = detail
        self.provider_id = provider_id
        self.stage = stage
        super().__init__(f"{self.error_code}: {detail}" if detail else self.error_code)

    def as_provenance(self) -> dict[str, str]:
        return {
            "error_code": self.error_code,
            "detail": self.detail,
            "provider_id": self.provider_id,
            "stage": self.stage,
        }


# ----------------------------------------------------------------------
# availability (fail-closed: the provider is not runnable at all)
# ----------------------------------------------------------------------


class ProviderNotConfigured(ProviderError):
    """No endpoint/model/credential was configured for this profile."""

    error_code = "PROVIDER_NOT_CONFIGURED"


class ProviderDependencyMissing(ProviderError):
    """The optional runtime dependency or model weight is not installed.

    AC-OPTIONAL-001/002: a missing heavy dependency must never crash the app;
    it is a reported Not-Ready state and a closed failure for the step.
    """

    error_code = "PROVIDER_DEPENDENCY_MISSING"


class ProviderDisabled(ProviderError):
    """The profile exists but is disabled by the user."""

    error_code = "PROVIDER_DISABLED"


class ProviderUnavailable(ProviderError):
    """The provider is configured and installed but currently not reachable."""

    error_code = "PROVIDER_UNAVAILABLE"
    retryable = True


class ProviderNotImplemented(ProviderError):
    """The route/provider has no registered implementation in this build.

    Fail-closed rule from TASK-018 R-007: a satisfied dependency list never
    turns an unimplemented route into a runnable one.
    """

    error_code = "PROVIDER_NOT_IMPLEMENTED"


# ----------------------------------------------------------------------
# provider / transport (D06 §56.1 retryable, §56.2 not)
# ----------------------------------------------------------------------


class ProviderAuthenticationError(ProviderError):
    """The provider rejected the credentials (HTTP 401/403)."""

    error_code = "PROVIDER_AUTH_FAILED"


class MissingCredential(ProviderError):
    """The profile references a credential that is not in the vault."""

    error_code = "MISSING_CREDENTIAL"


class ProviderRateLimited(ProviderError):
    """HTTP 429 / explicit rate-limit response (D06 §56.1)."""

    error_code = "PROVIDER_RATE_LIMITED"
    retryable = True


class ProviderTimeout(ProviderError):
    """Connect/read timeout (D06 §56.1 ``ReadTimeout``)."""

    error_code = "PROVIDER_TIMEOUT"
    retryable = True


class ProviderInvalidOutput(ProviderError):
    """The provider answered, but its payload violates the output contract.

    D06 §56.1 / TASK-017: malformed provider output is a provider fault and
    therefore retryable — it is never silently repaired or coerced.
    """

    error_code = "PROVIDER_INVALID_OUTPUT"
    retryable = True


class ProviderInputError(ProviderError):
    """Our own request was wrong (D06 §56.2 ``InvalidInput``)."""

    error_code = "INVALID_INPUT"


class OutputMappingViolation(ProviderError):
    """Provider output does not map back onto the requested write scope."""

    error_code = "OUTPUT_MAPPING_MISMATCH"


class LockBlocked(ProviderError):
    """A Page/Region/Translation/Inpaint Lock forbids the write."""

    error_code = "LOCK_CHANGED"


class NonTargetWriteViolation(ProviderError):
    """A provider changed pixels outside its mask (non-target protection).

    TASK-018: an inpaint may rewrite masked pixels only. A violation is a hard
    failure and the result must never be committed.
    """

    error_code = "NON_TARGET_WRITE"


# ----------------------------------------------------------------------
# device / model (D06 §92 Device/Model)
# ----------------------------------------------------------------------


class DeviceUnavailable(ProviderError):
    """No device satisfies the provider's requirement (no silent downgrade)."""

    error_code = "DEVICE_UNAVAILABLE"


class ProviderOutOfMemory(ProviderError):
    """GPU/host OOM inside the provider (AC-GPU-001: never crash the app)."""

    error_code = "OUT_OF_MEMORY"


class ModelLoadFailed(ProviderError):
    """The model could not be loaded (corrupt/incompatible weights)."""

    error_code = "MODEL_LOAD_FAILED"


class ModelIncomplete(ProviderError):
    """Weights failed the size/hash gate — never reported as Ready."""

    error_code = "MODEL_INCOMPLETE"


# ----------------------------------------------------------------------
# classification helpers
# ----------------------------------------------------------------------

#: D06 §56.1 — retry inside the same provider (bounded by policy).
RETRYABLE_CODES = frozenset(
    error.error_code
    for error in (
        ProviderUnavailable,
        ProviderRateLimited,
        ProviderTimeout,
        ProviderInvalidOutput,
    )
)

#: D06 §56.2 — fail immediately and let the user fix the input/credential.
NOT_RETRYABLE_CODES = frozenset(
    error.error_code
    for error in (
        ProviderNotConfigured,
        ProviderDependencyMissing,
        ProviderDisabled,
        ProviderNotImplemented,
        ProviderAuthenticationError,
        MissingCredential,
        ProviderInputError,
        OutputMappingViolation,
        LockBlocked,
        NonTargetWriteViolation,
        DeviceUnavailable,
        ProviderOutOfMemory,
        ModelLoadFailed,
        ModelIncomplete,
    )
)


def is_retryable(error_code: str) -> bool:
    """Classify one error code; unknown codes are **not** retried.

    Fail-closed by design: a code outside both tables must not be retried
    automatically (it is not declared retryable anywhere).
    """
    if error_code in RETRYABLE_CODES:
        return True
    if error_code in NOT_RETRYABLE_CODES:
        return False
    return False


# ----------------------------------------------------------------------
# readiness (AC-OPTIONAL-002)
# ----------------------------------------------------------------------


class ProviderState:
    """User-visible provider readiness states (AC-OPTIONAL-002)."""

    READY = "ready"
    NOT_READY = "not_ready"
    MISSING_DEPENDENCY = "missing_dependency"
    NOT_CONFIGURED = "not_configured"
    DISABLED = "disabled"
    UNKNOWN = "unknown"

    ALL = frozenset({READY, NOT_READY, MISSING_DEPENDENCY, NOT_CONFIGURED, DISABLED, UNKNOWN})


@dataclass(frozen=True)
class ProviderStatus:
    """One provider's readiness plus the reason a UI can render."""

    provider_id: str
    provider_type: str
    capabilities: frozenset[str]
    state: str = ProviderState.UNKNOWN
    error_code: str = ""
    detail: str = ""
    missing_requirements: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.state not in ProviderState.ALL:
            raise ValueError(f"unknown provider state: {self.state!r}")

    @property
    def ready(self) -> bool:
        return self.state == ProviderState.READY

    def as_dict(self) -> dict:
        return {
            "provider_id": self.provider_id,
            "provider_type": self.provider_type,
            "capabilities": sorted(self.capabilities),
            "state": self.state,
            "error_code": self.error_code,
            "detail": self.detail,
            "missing_requirements": list(self.missing_requirements),
        }
