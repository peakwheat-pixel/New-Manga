"""Transport request/response contract and error taxonomy (D06 §55~56,
D07 §67, D08 AC-NET-002~004).

The transport layer moves one HTTP request to an endpoint according to a
resolved :class:`~ports.network.profiles.NetworkProfile`. It never
decides business retry policy; it reports failures as typed errors and
returns HTTP statuses as data. Proxy failure defaults to a hard error —
a direct retry only happens when the profile explicitly allows it, and
then the outcome records a visible :class:`FallbackEvent` (AC-NET-003).
"""

from __future__ import annotations

from dataclasses import dataclass, field


class TransportError(Exception):
    """Base class for transport-level failures (no HTTP status reached)."""

    error_code = "TRANSPORT_FAILED"


class DnsResolutionError(TransportError):
    """First-hop host name could not be resolved (stage: DNS)."""

    error_code = "DNS_RESOLUTION_FAILED"


class TcpConnectionError(TransportError):
    """TCP connect to the first hop was refused or unreachable."""

    error_code = "TCP_CONNECTION_FAILED"


class TlsError(TransportError):
    """TLS handshake failed (wrong version, broken pipe, bad config)."""

    error_code = "TLS_HANDSHAKE_FAILED"


class TransportTimeoutError(TransportError):
    """Connect/read timed out within ``timeout_seconds`` (D06 §56.1)."""

    error_code = "TIMEOUT"


class ProxyTunnelError(TransportError):
    """Proxy refused the CONNECT/association (excludes auth failures)."""

    error_code = "PROXY_TUNNEL_FAILED"


class ProxyAuthenticationError(TransportError):
    """Proxy rejected credentials (HTTP 407 / SOCKS auth failure)."""

    error_code = "PROXY_AUTH_FAILED"


class MissingCredentialError(TransportError):
    """Profile references a credential that is not in the vault."""

    error_code = "MISSING_CREDENTIAL"


@dataclass(frozen=True)
class TransportRequest:
    method: str
    url: str
    headers: dict[str, str] = field(default_factory=dict)
    body: bytes | None = None


@dataclass(frozen=True)
class TransportResponse:
    status: int
    headers: dict[str, str] = field(default_factory=dict)
    body: bytes = b""


@dataclass(frozen=True)
class FallbackEvent:
    """A visible, auditable direct retry after proxy failure (AC-NET-003).

    ``reason`` is currently always ``proxy_failure``; the event exists so
    UI and provenance can show that this request bypassed the configured
    proxy (D06 §55, D07 §67).
    """

    network_profile_id: str
    reason: str = "proxy_failure"
    fallback_to: str = "direct"


@dataclass(frozen=True)
class TransportOutcome:
    """One logical request: final response plus any fallback trail."""

    response: TransportResponse
    fallback_events: tuple[FallbackEvent, ...] = ()


class Transport(Protocol):
    """Send one HTTP request under a network profile.

    Implementations must not silently retry direct after proxy failure
    unless ``profile.allow_proxy_failure_direct_fallback`` is set; when
    they do, the outcome must carry a :class:`FallbackEvent`.
    """

    def send(self, request: TransportRequest, profile) -> TransportOutcome: ...
