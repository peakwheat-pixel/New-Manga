"""Retry classification for transport/provider errors (D06 §56).

Same-provider automatic retry is allowed only for clearly transient
failures (timeouts, refused/unreachable sockets, provider rate limits).
Configuration and authentication failures fail fast so the user can fix
them; retrying them would only hide the problem (D06 §56.2).

HTTP statuses follow the same rule: 408/429 and 5xx are transient
candidates; 401/403 (auth), 400/413/422 (input) are not.
"""

from __future__ import annotations

from dataclasses import dataclass

from ports.network.transport import (
    DnsResolutionError,
    MissingCredentialError,
    ProviderAuthenticationError,
    ProxyAuthenticationError,
    TcpConnectionError,
    TransportError,
    TransportTimeoutError,
    TlsError,
)

#: Error classes eligible for same-provider automatic retry (D06 §56.1).
RETRYABLE_ERROR_TYPES = (
    TransportTimeoutError,
    TcpConnectionError,
)
#: Error classes that must fail fast (D06 §56.2 subset owned here).
NON_RETRYABLE_ERROR_TYPES = (
    MissingCredentialError,
    ProxyAuthenticationError,
    ProviderAuthenticationError,
    TlsError,
    DnsResolutionError,
)

_RETRYABLE_STATUSES = frozenset({408, 429})


@dataclass(frozen=True)
class RetryDecision:
    retryable: bool
    error_code: str
    reason: str


def classify_error(error: TransportError) -> RetryDecision:
    """Classify a transport error for the same-provider retry policy."""
    if isinstance(error, RETRYABLE_ERROR_TYPES):
        return RetryDecision(True, error.error_code, "transient transport failure")
    if isinstance(error, NON_RETRYABLE_ERROR_TYPES):
        return RetryDecision(False, error.error_code, "configuration or auth failure")
    if isinstance(error, TransportError):
        # Unknown transport subclasses: conservative fail-fast.
        return RetryDecision(False, error.error_code, "unclassified transport error")
    return RetryDecision(False, "UNKNOWN", f"not a transport error: {error!r}")


def classify_status(status: int) -> RetryDecision:
    """Classify an HTTP status reached through the transport."""
    if status in _RETRYABLE_STATUSES:
        return RetryDecision(True, "HTTP_RATE_LIMITED_OR_TIMEOUT", f"status {status}")
    if 500 <= status <= 599:
        return RetryDecision(True, "HTTP_SERVER_ERROR", f"status {status}")
    if status in (401, 403):
        return RetryDecision(False, "PROVIDER_AUTH_FAILED", f"status {status}")
    if 400 <= status <= 499:
        return RetryDecision(False, "INVALID_INPUT", f"status {status}")
    return RetryDecision(False, "HTTP_OK", f"status {status}")
