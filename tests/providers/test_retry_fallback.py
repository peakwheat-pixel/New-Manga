"""Retry policy, D06 §57 payload stability and explicit fallback."""

from __future__ import annotations

import pytest

from infrastructure.providers.fallback import FallbackChain, chain_from_binding, run_chain
from infrastructure.providers.retry import RetryPolicy, run_with_retry
from ports.providers.errors import (
    ProviderAuthenticationError,
    ProviderError,
    ProviderInputError,
    ProviderInvalidOutput,
    ProviderRateLimited,
    ProviderUnavailable,
    is_retryable,
)


def test_retryability_classification_matches_d06_56() -> None:
    assert is_retryable(ProviderRateLimited.error_code) is True
    assert is_retryable(ProviderInvalidOutput.error_code) is True
    assert is_retryable(ProviderUnavailable.error_code) is True
    assert is_retryable(ProviderAuthenticationError.error_code) is False
    assert is_retryable("SOMETHING_UNDECLARED") is False


def test_retry_stops_after_policy_attempts_and_reports_attempts() -> None:
    calls: list[int] = []
    sleeps: list[float] = []

    def call():
        calls.append(1)
        raise ProviderRateLimited("slow down")

    policy = RetryPolicy(max_attempts=3, backoff_seconds=0.25)
    with pytest.raises(ProviderRateLimited):
        run_with_retry(call, policy, provider_id="p", sleep=sleeps.append)
    assert len(calls) == 3
    assert sleeps == [0.25, 0.5]


def test_non_retryable_failure_is_not_retried() -> None:
    calls: list[int] = []

    def call():
        calls.append(1)
        raise ProviderAuthenticationError("bad key")

    with pytest.raises(ProviderAuthenticationError):
        run_with_retry(call, RetryPolicy(max_attempts=5), provider_id="p", sleep=lambda _s: None)
    assert len(calls) == 1


def test_retry_uses_the_identical_payload_or_aborts() -> None:
    hashes = iter(["hash-a", "hash-a", "hash-b"])
    calls: list[int] = []

    def call():
        calls.append(1)
        raise ProviderUnavailable("down")

    with pytest.raises(ProviderInputError):
        run_with_retry(
            call,
            RetryPolicy(max_attempts=5),
            provider_id="p",
            payload_hash_provider=lambda: next(hashes),
            sleep=lambda _s: None,
        )
    assert len(calls) == 2


def test_retry_records_the_successful_attempt() -> None:
    state = {"fail": True}

    def call():
        if state["fail"]:
            state["fail"] = False
            raise ProviderUnavailable("flaky")
        return "ok"

    outcome = run_with_retry(
        call, RetryPolicy(max_attempts=2), provider_id="p", sleep=lambda _s: None
    )
    assert outcome.result == "ok"
    assert outcome.attempt_count == 2
    assert outcome.attempts[-1].succeeded is True


def test_chain_without_configured_fallback_never_tries_another_provider() -> None:
    tried: list[str] = []

    def invoke(provider_id: str):
        tried.append(provider_id)
        raise ProviderUnavailable("down", provider_id=provider_id)

    chain = FallbackChain("primary")
    assert chain.allows_fallback is False
    with pytest.raises(ProviderUnavailable):
        run_chain(chain, invoke, policy=RetryPolicy(max_attempts=1), sleep=lambda _s: None)
    assert tried == ["primary"]


def test_explicit_fallback_records_both_attempts() -> None:
    def invoke(provider_id: str):
        if provider_id == "primary":
            raise ProviderUnavailable("down", provider_id=provider_id)
        return f"result-{provider_id}"

    chain = FallbackChain("primary", ("secondary",))
    outcome = run_chain(chain, invoke, policy=RetryPolicy(max_attempts=1), sleep=lambda _s: None)
    assert outcome.result == "result-secondary"
    assert outcome.fallback_chain == ("primary", "secondary")
    assert outcome.used_fallback is True
    provenance = outcome.as_provenance()
    assert [attempt["provider_id"] for attempt in provenance["attempts"]] == [
        "primary",
        "secondary",
    ]
    assert provenance["attempts"][0]["ok"] is False


def test_fallback_is_not_burned_on_non_retryable_failures() -> None:
    tried: list[str] = []

    def invoke(provider_id: str):
        tried.append(provider_id)
        raise ProviderAuthenticationError("bad key", provider_id=provider_id)

    chain = FallbackChain("primary", ("secondary",))
    with pytest.raises(ProviderAuthenticationError):
        run_chain(chain, invoke, policy=RetryPolicy(max_attempts=1), sleep=lambda _s: None)
    assert tried == ["primary"]


def test_chain_from_binding_reads_only_explicit_configuration() -> None:
    assert chain_from_binding("p1") == FallbackChain("p1")
    chain = chain_from_binding(
        {"provider_id": "p1", "fallback": ["p2", "p2", "p1", ""]}
    )
    assert chain == FallbackChain("p1", ("p2",))
    assert chain_from_binding({"fallback": ["p2"]}) is None
    assert chain_from_binding(None) is None


def test_fallback_chain_rejects_self_reference_and_empty_primary() -> None:
    with pytest.raises(ValueError):
        FallbackChain("p", ("p",))
    with pytest.raises(ValueError):
        FallbackChain("")


def test_provider_error_keeps_typed_code_and_provenance() -> None:
    error = ProviderError("boom", provider_id="p", stage="ocr")
    assert error.error_code == "PROVIDER_FAILED"
    assert error.as_provenance() == {
        "error_code": "PROVIDER_FAILED",
        "detail": "boom",
        "provider_id": "p",
        "stage": "ocr",
    }
