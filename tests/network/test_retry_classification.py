"""Retry classification: transient failures retry, config/auth fail fast
(D06 §56)."""

from __future__ import annotations

from infrastructure.network.retry import classify_error, classify_status
from ports.network.transport import (
    DnsResolutionError,
    MissingCredentialError,
    ProxyAuthenticationError,
    TcpConnectionError,
    TransportTimeoutError,
    TlsError,
)


def test_transient_failures_are_retryable():
    for error in (
        TransportTimeoutError("read timed out"),
        TcpConnectionError("connection refused"),
    ):
        decision = classify_error(error)
        assert decision.retryable, error


def test_config_and_auth_failures_fail_fast():
    for error in (
        ProxyAuthenticationError("407"),
        MissingCredentialError("no vault entry"),
        TlsError("bad cert"),
        DnsResolutionError("no such host"),
    ):
        decision = classify_error(error)
        assert not decision.retryable, error


def test_statuses_follow_same_rule():
    assert classify_status(429).retryable
    assert classify_status(408).retryable
    assert classify_status(503).retryable
    assert not classify_status(401).retryable
    assert not classify_status(403).retryable
    assert not classify_status(400).retryable
    assert classify_status(401).error_code == "PROVIDER_AUTH_FAILED"
    assert classify_status(429).error_code == "HTTP_RATE_LIMITED_OR_TIMEOUT"


def test_error_codes_are_typed_not_generic():
    decision = classify_error(ProxyAuthenticationError("proxy said no"))
    assert decision.error_code == "PROXY_AUTH_FAILED"
    decision = classify_error(TransportTimeoutError("t"))
    assert decision.error_code == "TIMEOUT"
