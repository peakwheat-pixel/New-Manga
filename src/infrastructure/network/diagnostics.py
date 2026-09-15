"""Staged connection diagnostics (AC-NET-004, D07 §87~89).

The connection test must show DNS → TCP → TLS → HTTP → Provider Auth
as separate stages, and a failure must surface its typed error code —
"连接失败" alone is a contract violation. Stages run in order; the
first failure stops the ladder and later stages are reported as
skipped with the reason.

The first three stages probe the *first hop*: for proxied routes that
is the proxy itself (is the proxy reachable, does its TLS come up), for
direct routes the target. The HTTP stage then exercises the full route
through the transport, so proxy misbehavior shows up typed as well.
"""

from __future__ import annotations

import socket
import ssl
import time
from dataclasses import dataclass, field
from typing import Callable

from ports.network.profiles import NetworkProfile
from ports.network.transport import (
    Transport,
    TransportError,
    TransportRequest,
)

STAGE_DNS = "dns"
STAGE_TCP = "tcp"
STAGE_TLS = "tls"
STAGE_HTTP = "http"
STAGE_AUTH = "provider-auth"
STAGE_ORDER = (STAGE_DNS, STAGE_TCP, STAGE_TLS, STAGE_HTTP, STAGE_AUTH)

#: Optional hook returning extra headers (e.g. Authorization) for the
#: provider-auth stage; keeps the tester free of credential knowledge.
AuthHeadersProvider = Callable[[], dict[str, str]]


@dataclass(frozen=True)
class StageResult:
    stage: str
    ok: bool | None  # None = skipped
    error_code: str = ""
    detail: str = ""
    elapsed_ms: int = 0

    @property
    def label(self) -> str:
        return self.stage.upper()


@dataclass(frozen=True)
class ConnectionTestReport:
    url: str
    network_profile_id: str
    stages: tuple[StageResult, ...] = ()
    http_status: int | None = None
    fallback_events: tuple = field(default_factory=tuple)

    @property
    def ok(self) -> bool:
        completed = [s for s in self.stages if s.ok is not None]
        return bool(completed) and all(s.ok for s in completed)

    def failing_stage(self) -> StageResult | None:
        for stage in self.stages:
            if stage.ok is False:
                return stage
        return None


def _timed(fn):
    start = time.perf_counter()
    try:
        detail = fn()
        return True, "", str(detail), int((time.perf_counter() - start) * 1000)
    except TransportError as err:
        return (
            False,
            err.error_code,
            str(err),
            int((time.perf_counter() - start) * 1000),
        )
    except OSError as err:
        return (
            False,
            "OS_ERROR",
            str(err),
            int((time.perf_counter() - start) * 1000),
        )


class ConnectionTester:
    """Run the staged ladder against one URL under one network profile."""

    def __init__(self, transport: Transport) -> None:
        self._transport = transport

    def test(
        self,
        url: str,
        profile: NetworkProfile,
        *,
        auth_headers_provider: AuthHeadersProvider | None = None,
    ) -> ConnectionTestReport:
        route = self._transport.resolve_route(url, profile)
        first_host = route.proxy_host if route.via_proxy else route.target_host
        first_port = route.proxy_port if route.via_proxy else route.target_port

        stages: list[StageResult] = []
        skipped_after = False

        def add(stage: str, fn=None, skip_reason: str = "") -> None:
            nonlocal skipped_after
            if skipped_after:
                stages.append(StageResult(stage, None, "SKIPPED", "earlier stage failed"))
                return
            if fn is None:
                stages.append(StageResult(stage, None, "SKIPPED", skip_reason))
                return
            ok, code, detail, ms = _timed(fn)
            stages.append(StageResult(stage, ok, code, detail, ms))
            if not ok:
                skipped_after = True

        # Stage 1: DNS on the first hop.
        add(
            STAGE_DNS,
            lambda: self._resolve(first_host),
        )

        # Stage 2: TCP to the first hop under the profile timeout.
        add(
            STAGE_TCP,
            lambda: self._tcp(first_host, first_port, profile.timeout_seconds),
        )

        # Stage 3: TLS only where the first hop itself is TLS-protected.
        tls_first_hop = (
            not route.via_proxy and route.target_scheme == "https"
        ) or (route.via_proxy and route.proxy_kind == "https")
        if tls_first_hop:
            add(
                STAGE_TLS,
                lambda: self._tls(first_host, first_port, profile),
            )
        else:
            add(STAGE_TLS, None, "first hop is not TLS (tunnel/full path covered by HTTP stage)")

        # Stage 4: full-route HTTP exchange through the transport.
        outcome_holder: list = []

        def http_stage():
            outcome = self._transport.send(
                TransportRequest(method="GET", url=url), profile
            )
            outcome_holder.append(outcome)
            return f"status {outcome.response.status}"

        add(STAGE_HTTP, http_stage)

        # Stage 5: provider auth probe with caller-supplied headers.
        if auth_headers_provider is None:
            add(STAGE_AUTH, None, "no credentials configured for this provider")
        elif skipped_after or not outcome_holder:
            add(STAGE_AUTH, None, "earlier stage failed")
        else:
            def auth_stage():
                headers = auth_headers_provider()
                outcome = self._transport.send(
                    TransportRequest(method="GET", url=url, headers=headers), profile
                )
                status = outcome.response.status
                if status in (401, 403):
                    raise TransportError(
                        f"provider rejected credentials with status {status}"
                    )
                return f"status {status}"

            add(STAGE_AUTH, auth_stage)

        return ConnectionTestReport(
            url=url,
            network_profile_id=profile.network_profile_id,
            stages=tuple(stages),
            http_status=(
                outcome_holder[0].response.status if outcome_holder else None
            ),
            fallback_events=(
                outcome_holder[0].fallback_events if outcome_holder else ()
            ),
        )

    # ------------------------------------------------------------------
    # stage helpers
    # ------------------------------------------------------------------

    def _resolve(self, host: str) -> str:
        try:
            infos = socket.getaddrinfo(host, None)
        except socket.gaierror as err:
            from ports.network.transport import DnsResolutionError

            raise DnsResolutionError(f"cannot resolve {host!r}: {err}") from err
        return f"resolved to {len(infos)} address(es)"

    def _tcp(self, host: str, port: int, timeout: float) -> str:
        from ports.network.transport import TcpConnectionError, TransportTimeoutError

        try:
            sock = socket.create_connection((host, port), timeout=timeout)
        except socket.gaierror as err:
            from ports.network.transport import DnsResolutionError

            raise DnsResolutionError(str(err)) from err
        except TimeoutError as err:
            raise TransportTimeoutError(f"tcp connect timed out: {host}:{port}") from err
        except OSError as err:
            raise TcpConnectionError(f"tcp connect failed: {host}:{port}: {err}") from err
        finally:
            pass
        try:
            return f"tcp connect ok to {host}:{port}"
        finally:
            sock.close()

    def _tls(self, host: str, port: int, profile: NetworkProfile) -> str:
        from ports.network.transport import TlsError

        if profile.verify_tls:
            context = ssl.create_default_context()
        else:
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
        try:
            sock = socket.create_connection((host, port), timeout=profile.timeout_seconds)
        except OSError as err:
            from ports.network.transport import TcpConnectionError

            raise TcpConnectionError(str(err)) from err
        try:
            tls_sock = context.wrap_socket(sock, server_hostname=host)
            version = tls_sock.version()
            tls_sock.close()
            return f"tls ok ({version})"
        except (ssl.SSLCertVerificationError, ssl.SSLError) as err:
            raise TlsError(f"tls handshake failed for {host!r}: {err}") from err
