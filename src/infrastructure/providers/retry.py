"""Bounded same-provider retry (D06 §56~§57, TASK-017 R-002 absorbed).

Two invariants are enforced here rather than documented:

- only explicitly retryable codes are retried (D06 §56.1); authentication,
  missing credentials, invalid input and lock conflicts fail immediately
  (D06 §56.2);
- a retry must carry the **identical** request payload (D06 §57): the caller
  supplies a payload-hash provider and a changed hash aborts the retry loop
  instead of silently retrying a different intent.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from ports.providers.errors import ProviderError, ProviderInputError, is_retryable


@dataclass(frozen=True)
class RetryPolicy:
    """Finite retry policy; ``max_attempts`` counts the first try."""

    max_attempts: int = 3
    backoff_seconds: float = 0.5
    retry_codes: frozenset[str] | None = None

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be >= 1")
        if self.backoff_seconds < 0:
            raise ValueError("backoff_seconds must be >= 0")

    def allows(self, error_code: str) -> bool:
        if self.retry_codes is not None:
            return error_code in self.retry_codes
        return is_retryable(error_code)

    def delay_for(self, attempt: int) -> float:
        """Linear backoff; no jitter so tests stay deterministic."""
        return self.backoff_seconds * attempt

    def as_dict(self) -> dict:
        return {
            "max_attempts": self.max_attempts,
            "backoff_seconds": self.backoff_seconds,
            "retry_codes": sorted(self.retry_codes) if self.retry_codes else None,
        }


@dataclass(frozen=True)
class AttemptRecord:
    """One provider attempt on one provider (audit trail)."""

    attempt: int
    provider_id: str
    payload_hash: str = ""
    error_code: str = ""
    detail: str = ""
    succeeded: bool = False
    elapsed_ms: int = 0

    def as_dict(self) -> dict:
        return {
            "attempt": self.attempt,
            "provider_id": self.provider_id,
            "payload_hash": self.payload_hash,
            "error_code": self.error_code,
            "detail": self.detail,
            "succeeded": self.succeeded,
            "elapsed_ms": self.elapsed_ms,
        }


@dataclass(frozen=True)
class RetryOutcome:
    result: Any
    attempts: tuple[AttemptRecord, ...]
    provider_id: str

    @property
    def attempt_count(self) -> int:
        return len(self.attempts)

    def as_provenance(self) -> dict:
        return {
            "provider_id": self.provider_id,
            "attempt_count": self.attempt_count,
            "attempts": [attempt.as_dict() for attempt in self.attempts],
        }


def run_with_retry(
    call: Callable[[], Any],
    policy: RetryPolicy,
    *,
    provider_id: str = "",
    payload_hash_provider: Callable[[], str] | None = None,
    sleep: Callable[[float], None] | None = None,
    clock: Callable[[], float] = time.perf_counter,
) -> RetryOutcome:
    """Run ``call`` with bounded retries; re-raises the last typed failure."""
    waiter = sleep if sleep is not None else time.sleep
    attempts: list[AttemptRecord] = []
    first_hash = payload_hash_provider() if payload_hash_provider else ""

    for attempt in range(1, policy.max_attempts + 1):
        if payload_hash_provider is not None and attempt > 1:
            current_hash = payload_hash_provider()
            if current_hash != first_hash:
                raise ProviderInputError(
                    "retry would change the request payload (D06 §57)",
                    provider_id=provider_id,
                    stage="retry",
                )
        started = clock()
        try:
            result = call()
        except ProviderError as error:
            attempts.append(
                AttemptRecord(
                    attempt=attempt,
                    provider_id=provider_id or error.provider_id,
                    payload_hash=first_hash,
                    error_code=error.error_code,
                    detail=error.detail,
                    elapsed_ms=int((clock() - started) * 1000),
                )
            )
            if attempt >= policy.max_attempts or not policy.allows(error.error_code):
                raise
            waiter(policy.delay_for(attempt))
        else:
            attempts.append(
                AttemptRecord(
                    attempt=attempt,
                    provider_id=provider_id,
                    payload_hash=first_hash,
                    succeeded=True,
                    elapsed_ms=int((clock() - started) * 1000),
                )
            )
            return RetryOutcome(result, tuple(attempts), provider_id)

    raise AssertionError("retry loop exited without a result")  # pragma: no cover


@dataclass
class StepAttemptState:
    """Mutable attempt bookkeeping shared by a chain (provenance source)."""

    records: list[AttemptRecord] = field(default_factory=list)

    def add(self, record: AttemptRecord) -> None:
        self.records.append(record)

    def extend(self, outcome: RetryOutcome) -> None:
        self.records.extend(outcome.attempts)

    def as_provenance(self) -> list[dict]:
        return [record.as_dict() for record in self.records]
