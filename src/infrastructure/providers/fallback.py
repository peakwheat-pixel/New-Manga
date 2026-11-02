"""Explicit, auditable provider fallback (D06 §51~§54, AC-FALLBACK-001/002).

The rule the pipeline depends on: a provider failure **never** selects
"another available provider" on its own (D06 §51). A fallback runs only when

1. the Run's frozen binding names the secondary provider(s) explicitly, and
2. the failure is one that a different provider could plausibly repair.

Every attempt on every provider is recorded, so AC-FALLBACK-002's "provenance
records both attempts" is produced by construction rather than by discipline.
Non-retryable failures (authentication, missing credential, invalid input)
stop the chain immediately: another provider would not fix them.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from infrastructure.providers.retry import RetryPolicy, run_with_retry
from ports.providers.errors import ProviderError, is_retryable


@dataclass(frozen=True)
class ProviderAttempt:
    """One provider tried by a chain (success or failure)."""

    provider_id: str
    ok: bool
    error_code: str = ""
    detail: str = ""
    attempt_count: int = 1

    def as_dict(self) -> dict:
        return {
            "provider_id": self.provider_id,
            "ok": self.ok,
            "error_code": self.error_code,
            "detail": self.detail,
            "attempt_count": self.attempt_count,
        }


@dataclass(frozen=True)
class ChainOutcome:
    result: Any
    attempts: tuple[ProviderAttempt, ...]
    final_provider_id: str

    @property
    def fallback_chain(self) -> tuple[str, ...]:
        return tuple(attempt.provider_id for attempt in self.attempts)

    @property
    def used_fallback(self) -> bool:
        return len(self.attempts) > 1

    def as_provenance(self) -> dict:
        return {
            "attempts": [attempt.as_dict() for attempt in self.attempts],
            "attempt_count": sum(attempt.attempt_count for attempt in self.attempts),
            "fallback_chain": list(self.fallback_chain),
            "final_provider_id": self.final_provider_id,
            "used_fallback": self.used_fallback,
        }


@dataclass(frozen=True)
class FallbackChain:
    """The providers one capability binding may use, in order.

    ``primary`` is always tried; ``explicit_fallbacks`` stays empty unless the
    user configured them (AC-FALLBACK-001).
    """

    primary: str
    explicit_fallbacks: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.primary:
            raise ValueError("a fallback chain needs a primary provider")
        if self.primary in self.explicit_fallbacks:
            raise ValueError("the primary provider cannot also be a fallback")

    @property
    def allows_fallback(self) -> bool:
        return bool(self.explicit_fallbacks)

    def providers(self) -> tuple[str, ...]:
        return (self.primary, *self.explicit_fallbacks)

    def as_dict(self) -> dict:
        return {
            "primary": self.primary,
            "explicit_fallbacks": list(self.explicit_fallbacks),
            "allows_fallback": self.allows_fallback,
        }


def run_chain(
    chain: FallbackChain,
    invoke: Callable[[str], Any],
    *,
    policy: RetryPolicy | None = None,
    payload_hash_provider: Callable[[], str] | None = None,
    sleep: Callable[[float], None] | None = None,
) -> ChainOutcome:
    """Try the primary, then only the explicitly configured fallbacks.

    The last failure is re-raised unchanged, so the StepRun carries the real
    provider error code rather than a generic "fallback failed".
    """
    retry_policy = policy or RetryPolicy()
    attempts: list[ProviderAttempt] = []
    last_error: ProviderError | None = None
    requested: Sequence[str] = (
        chain.providers() if chain.allows_fallback else (chain.primary,)
    )

    for index, provider_id in enumerate(requested):
        last = index == len(requested) - 1
        try:
            outcome = run_with_retry(
                lambda provider_id=provider_id: invoke(provider_id),
                retry_policy,
                provider_id=provider_id,
                payload_hash_provider=payload_hash_provider,
                sleep=sleep,
            )
        except ProviderError as error:
            attempts.append(
                ProviderAttempt(
                    provider_id=provider_id,
                    ok=False,
                    error_code=error.error_code,
                    detail=error.detail,
                )
            )
            last_error = error
            if last:
                break
            if not is_retryable(error.error_code):
                # A different provider cannot repair auth/input/credential
                # failures; stop instead of burning the fallback.
                break
            continue
        attempts.append(
            ProviderAttempt(
                provider_id=provider_id, ok=True, attempt_count=outcome.attempt_count
            )
        )
        return ChainOutcome(
            result=outcome.result,
            attempts=tuple(attempts),
            final_provider_id=provider_id,
        )

    if last_error is None:  # pragma: no cover - providers() is never empty
        raise AssertionError("fallback chain tried no provider")
    raise last_error


def chain_from_binding(
    binding: Any,
    *,
    fallback_key: str = "fallback",
) -> FallbackChain | None:
    """Read an explicit fallback chain out of a frozen binding snapshot.

    Returns ``None`` when the binding is missing or names no provider, so the
    caller fails with a typed configuration error instead of inventing one.
    """
    if isinstance(binding, str) and binding:
        return FallbackChain(binding)
    if not isinstance(binding, Mapping):
        return None
    primary = ""
    for key in ("provider_id", "provider_profile_id", "id"):
        value = binding.get(key)
        if isinstance(value, str) and value:
            primary = value
            break
    if not primary:
        return None
    raw_fallbacks = binding.get(fallback_key) or ()
    if isinstance(raw_fallbacks, str):
        raw_fallbacks = (raw_fallbacks,)
    seen = {primary}
    fallbacks: list[str] = []
    for item in raw_fallbacks:
        if not isinstance(item, str) or not item or item in seen:
            continue
        seen.add(item)
        fallbacks.append(item)
    return FallbackChain(primary, tuple(fallbacks))
