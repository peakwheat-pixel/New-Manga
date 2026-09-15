"""Standard-library transport: staged sockets, proxies, SOCKS5 and
strict proxy-failure semantics (D06 §55~56, D07 §67~68, AC-NET-001~004).

Pure stdlib on purpose — the transport is the trust boundary for proxy
and TLS behavior, so every stage (DNS, TCP, TLS, tunnel, HTTP, proxy
auth) maps to a typed error from ``ports.network.transport`` instead of
a generic "connection failed" (AC-NET-004).

Route resolution centralizes the unified policy (D03 §27):

- ``direct`` — connect straight to the target.
- ``system`` — use the OS/environment proxy for the scheme, honoring
  the system ``no_proxy`` list.
- ``http``/``https``/``socks5`` — use the profile's endpoint; when the
  endpoint is empty and ``inherit_system`` is set, fall back to the
  system proxy first (profile wins over system when configured).
- bypass always short-circuits to direct (default: localhost/127.0.0.1).

Proxy failure never silently retries direct. Only when the profile sets
``allow_proxy_failure_direct_fallback`` is one direct retry performed,
and the outcome then carries a visible :class:`FallbackEvent` so UI and
provenance can show it (AC-NET-002/003).
"""

from __future__ import annotations

import base64
import http.client
import socket
import ssl
import urllib.parse
import urllib.request
from dataclasses import dataclass, replace

from ports.network.profiles import (
    MODE_DIRECT,
    MODE_HTTP,
    MODE_HTTPS,
    MODE_SOCKS5,
    MODE_SYSTEM,
    NetworkProfile,
)
from ports.network.transport import (
    DnsResolutionError,
    FallbackEvent,
    MissingCredentialError,
    ProxyAuthenticationError,
    ProxyTunnelError,
    TcpConnectionError,
    TlsError,
    Transport,
    TransportError,
    TransportOutcome,
    TransportRequest,
    TransportResponse,
    TransportTimeoutError,
)

#: Failures on the proxy hop that a direct fallback may recover from.
#: MissingCredentialError is deliberately excluded: it is a config
#: error the user must fix, not a network failure (D06 §56.2).
_PROXY_FAILURE_TYPES = (
    TcpConnectionError,
    TlsError,
    TransportTimeoutError,
    ProxyTunnelError,
    ProxyAuthenticationError,
    DnsResolutionError,
)

_HTTP_PORT = 80
_HTTPS_PORT = 443


@dataclass(frozen=True)
class ResolvedRoute:
    """Concrete plan for one request after policy resolution."""

    target_scheme: str
    target_host: str
    target_port: int
    via_proxy: bool = False
    proxy_kind: str = ""  # "" | http | https | socks5
    proxy_host: str = ""
    proxy_port: int = 0
    proxy_source: str = ""  # profile | system
    reason: str = "direct"


def _parse_proxy_url(url: str) -> tuple[str, str, int]:
    parts = urllib.parse.urlsplit(url)
    scheme = parts.scheme.lower()
    if scheme not in (MODE_HTTP, MODE_HTTPS):
        raise TransportError(f"unsupported proxy URL scheme: {url!r}")
    host = parts.hostname
    if not host:
        raise TransportError(f"proxy URL has no host: {url!r}")
    port = parts.port or (_HTTPS_PORT if scheme == MODE_HTTPS else _HTTP_PORT)
    return scheme, host, port


class StdlibTransport:
    """``Transport`` implementation over socket/ssl/http.client.

    ``credential_store`` resolves proxy passwords from the protected
    vault; secrets are used in the handshake and immediately dropped.
    """

    def __init__(self, credential_store=None, extra_cafile: str | None = None) -> None:
        self._credentials = credential_store
        # Optional extra trust anchors (e.g. corporate proxy CA), used
        # only while verify_tls is on; never disables verification.
        self._extra_cafile = extra_cafile

    # ------------------------------------------------------------------
    # route resolution (the unified policy, D03 §27)
    # ------------------------------------------------------------------

    def resolve_route(self, url: str, profile: NetworkProfile) -> ResolvedRoute:
        parts = urllib.parse.urlsplit(url)
        scheme = parts.scheme.lower()
        if scheme not in ("http", "https"):
            raise TransportError(f"unsupported URL scheme: {url!r}")
        host = parts.hostname
        if not host:
            raise TransportError(f"URL has no host: {url!r}")
        port = parts.port or (_HTTPS_PORT if scheme == "https" else _HTTP_PORT)

        direct = ResolvedRoute(
            target_scheme=scheme,
            target_host=host,
            target_port=port,
            reason="direct",
        )

        if profile.mode != MODE_DIRECT and profile.is_bypassed(host):
            return replace(direct, reason="bypass")

        if profile.mode == MODE_DIRECT:
            return direct

        if profile.mode == MODE_SYSTEM:
            return self._system_route(scheme, host, direct)

        if profile.mode == MODE_SOCKS5:
            if not profile.socks5_proxy:
                if profile.inherit_system:
                    return self._system_route(scheme, host, direct)
                return direct
            proxy_host, proxy_port = self._socks_endpoint(profile)
            return ResolvedRoute(
                target_scheme=scheme,
                target_host=host,
                target_port=port,
                via_proxy=True,
                proxy_kind=MODE_SOCKS5,
                proxy_host=proxy_host,
                proxy_port=proxy_port,
                proxy_source="profile",
                reason="profile:socks5",
            )

        proxy_url = self._profile_proxy_url(profile, scheme)
        if not proxy_url:
            if profile.inherit_system:
                return self._system_route(scheme, host, direct, source="system")
            return direct

        kind, proxy_host, proxy_port = _parse_proxy_url(proxy_url)
        return ResolvedRoute(
            target_scheme=scheme,
            target_host=host,
            target_port=port,
            via_proxy=True,
            proxy_kind=kind,
            proxy_host=proxy_host,
            proxy_port=proxy_port,
            proxy_source="profile",
            reason=f"profile:{profile.mode}",
        )

    def _profile_proxy_url(self, profile: NetworkProfile, scheme: str) -> str:
        if profile.mode == MODE_SOCKS5:
            return profile.socks5_proxy
        if profile.mode == MODE_HTTP:
            return profile.http_proxy or profile.https_proxy
        if profile.mode == MODE_HTTPS:
            return profile.https_proxy or profile.http_proxy
        return ""

    def _socks_endpoint(self, profile: NetworkProfile) -> tuple[str, int]:
        parts = urllib.parse.urlsplit("//" + profile.socks5_proxy.lstrip("/"))
        host = parts.hostname
        if not host:
            raise TransportError("socks5_proxy has no host")
        return host, parts.port or 1080

    def _system_route(
        self, scheme: str, host: str, direct: ResolvedRoute, *, source: str = "system"
    ) -> ResolvedRoute:
        if urllib.request.proxy_bypass(host):
            return replace(direct, reason="system-no_proxy")
        proxy_url = urllib.request.getproxies().get(scheme)
        if not proxy_url:
            return replace(direct, reason="system-none")
        kind, proxy_host, proxy_port = _parse_proxy_url(proxy_url)
        return ResolvedRoute(
            target_scheme=scheme,
            target_host=host,
            target_port=direct.target_port,
            via_proxy=True,
            proxy_kind=kind,
            proxy_host=proxy_host,
            proxy_port=proxy_port,
            proxy_source=source,
            reason=f"{source}:{kind}",
        )

    # ------------------------------------------------------------------
    # Transport protocol
    # ------------------------------------------------------------------

    def send(
        self, request: TransportRequest, profile: NetworkProfile
    ) -> TransportOutcome:
        route = self.resolve_route(request.url, profile)
        try:
            response = self._send_once(request, profile, route)
        except _PROXY_FAILURE_TYPES as err:
            if route.via_proxy and profile.allow_proxy_failure_direct_fallback:
                direct_route = ResolvedRoute(
                    target_scheme=route.target_scheme,
                    target_host=route.target_host,
                    target_port=route.target_port,
                    reason="proxy-failure-fallback",
                )
                response = self._send_once(request, profile, direct_route)
                event = FallbackEvent(
                    network_profile_id=profile.network_profile_id,
                    reason="proxy_failure",
                    fallback_to="direct",
                )
                return TransportOutcome(response, (event,))
            raise
        return TransportOutcome(response)

    # ------------------------------------------------------------------
    # one attempt
    # ------------------------------------------------------------------

    def _send_once(
        self,
        request: TransportRequest,
        profile: NetworkProfile,
        route: ResolvedRoute,
    ) -> TransportResponse:
        sock, selector, host_header = self._establish(request, profile, route)
        try:
            conn = http.client.HTTPConnection(
                route.target_host, route.target_port, timeout=profile.timeout_seconds
            )
            conn.sock = sock
            headers = {"Host": host_header, "Connection": "close"}
            headers.update(request.headers)
            try:
                conn.request(
                    request.method, selector, body=request.body, headers=headers
                )
                resp = conn.getresponse()
                body = resp.read()
            except http.client.HTTPException as err:
                raise TransportError(f"http exchange failed: {err}") from err
            finally:
                conn.close()
            return TransportResponse(
                status=resp.status,
                headers={k.lower(): v for k, v in resp.getheaders()},
                body=body,
            )
        finally:
            try:
                sock.close()
            except OSError:
                pass

    def _establish(
        self, request: TransportRequest, profile: NetworkProfile, route: ResolvedRoute
    ) -> tuple[socket.socket, str, str]:
        """Return (socket, request-selector, Host header value)."""
        parts = urllib.parse.urlsplit(request.url)
        path = parts.path or "/"
        if parts.query:
            path += f"?{parts.query}"
        host_header = f"{route.target_host}:{route.target_port}"
        tls_to_target = route.target_scheme == "https"

        if not route.via_proxy:
            sock = self._tcp_connect(
                route.target_host, route.target_port, profile.timeout_seconds
            )
            if tls_to_target:
                sock = self._tls_wrap(
                    sock, route.target_host, profile, stage="target-tls"
                )
            return sock, path, host_header

        if route.proxy_kind == MODE_SOCKS5:
            sock = self._socks5_connect(route, profile)
        else:
            sock = self._tcp_connect(
                route.proxy_host, route.proxy_port, profile.timeout_seconds
            )
            if route.proxy_kind == MODE_HTTPS:
                sock = self._tls_wrap(
                    sock, route.proxy_host, profile, stage="proxy-tls"
                )
            if tls_to_target:
                self._http_connect_tunnel(sock, route, profile)
            else:
                # Absolute-form through a plain HTTP proxy.
                return sock, request.url, host_header

        if tls_to_target:
            sock = self._tls_wrap(sock, route.target_host, profile, stage="target-tls")
        return sock, path, host_header

    # ------------------------------------------------------------------
    # stages
    # ------------------------------------------------------------------

    def _tcp_connect(self, host: str, port: int, timeout: float) -> socket.socket:
        try:
            return socket.create_connection((host, port), timeout=timeout)
        except socket.gaierror as err:
            raise DnsResolutionError(f"cannot resolve {host!r}: {err}") from err
        except (ConnectionRefusedError, ConnectionResetError):
            raise TcpConnectionError(f"connection refused: {host}:{port}") from None
        except OSError as err:
            # Timeouts surface as OSError subclasses (TimeoutError in
            # 3.10+); keep the distinction for retry classification.
            if isinstance(err, TimeoutError) or isinstance(err, socket.timeout):
                raise TransportTimeoutError(
                    f"connect timed out after {timeout}s: {host}:{port}"
                ) from err
            raise TcpConnectionError(f"cannot connect {host}:{port}: {err}") from err

    def _tls_wrap(
        self, sock: socket.socket, server_hostname: str, profile: NetworkProfile, *, stage: str
    ) -> ssl.SSLSocket:
        if profile.verify_tls:
            context = ssl.create_default_context()
            if self._extra_cafile:
                context.load_verify_locations(self._extra_cafile)
        else:
            # Explicit dangerous opt-out (AC-SEC-005 guards this at the
            # service layer); the transport still honors it faithfully.
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
        try:
            return context.wrap_socket(sock, server_hostname=server_hostname)
        except (ssl.SSLCertVerificationError, ssl.SSLError) as err:
            raise TlsError(f"{stage} failed for {server_hostname!r}: {err}") from err
        except (TimeoutError, socket.timeout) as err:
            raise TransportTimeoutError(f"{stage} handshake timed out") from err

    def _proxy_password(self, profile: NetworkProfile) -> str:
        if not profile.credential_ref:
            return ""
        if self._credentials is None:
            raise MissingCredentialError(
                "profile carries a proxy credential_ref but no credential store "
                "was provided"
            )
        try:
            return self._credentials.resolve_credential(
                profile.credential_ref
            ).reveal()
        except KeyError as err:
            raise MissingCredentialError(
                f"proxy credential {profile.credential_ref!r} not found in vault"
            ) from err
        except Exception as err:  # vault outages are config errors, not network
            raise MissingCredentialError(
                f"cannot resolve proxy credential {profile.credential_ref!r}: {err}"
            ) from err

    def _http_connect_tunnel(
        self, sock: socket.socket, route: ResolvedRoute, profile: NetworkProfile
    ) -> None:
        auth = ""
        if profile.username:
            token = base64.b64encode(
                f"{profile.username}:{self._proxy_password(profile)}".encode()
            ).decode()
            auth = f"Proxy-Authorization: Basic {token}\r\n"
        target = f"{route.target_host}:{route.target_port}"
        request = (
            f"CONNECT {target} HTTP/1.1\r\n"
            f"Host: {target}\r\n"
            f"{auth}"
            "Connection: keep-alive\r\n\r\n"
        )
        try:
            sock.sendall(request.encode())
            status, _headers = self._read_http_head(sock)
        except TransportError:
            raise
        except (TimeoutError, socket.timeout) as err:
            raise TransportTimeoutError("proxy CONNECT timed out") from err
        except OSError as err:
            raise ProxyTunnelError(f"proxy CONNECT failed: {err}") from err
        if status == 407:
            raise ProxyAuthenticationError(
                "proxy rejected credentials (HTTP 407 during CONNECT)"
            )
        if status != 200:
            raise ProxyTunnelError(
                f"proxy refused CONNECT tunnel with status {status}"
            )

    def _read_http_head(self, sock: socket.socket) -> tuple[int, str]:
        buf = bytearray()
        while b"\r\n\r\n" not in buf:
            chunk = sock.recv(4096)
            if not chunk:
                break
            buf.extend(chunk)
            if len(buf) > 65536:
                raise ProxyTunnelError("proxy response head too large")
        head = bytes(buf).split(b"\r\n\r\n", 1)[0].decode("latin-1", errors="replace")
        lines = head.split("\r\n")
        if not lines or not lines[0]:
            raise ProxyTunnelError("empty proxy response")
        try:
            status = int(lines[0].split()[1])
        except (IndexError, ValueError) as err:
            raise ProxyTunnelError(f"malformed proxy status line: {lines[0]!r}") from err
        return status, head

    # ------------------------------------------------------------------
    # SOCKS5 (RFC 1928/1929)
    # ------------------------------------------------------------------

    def _socks5_connect(
        self, route: ResolvedRoute, profile: NetworkProfile
    ) -> socket.socket:
        sock = self._tcp_connect(
            route.proxy_host, route.proxy_port, profile.timeout_seconds
        )
        try:
            password = ""
            if profile.username or profile.credential_ref:
                password = self._proxy_password(profile)
                methods = b"\x05\x02\x00\x02"  # no-auth + user/pass
            else:
                methods = b"\x05\x01\x00"

            self._socks_send(sock, methods)
            reply = self._socks_recv(sock, 2)
            if reply[0] != 0x05:
                raise ProxyTunnelError("not a SOCKS5 server")
            method = reply[1]
            if method == 0xFF:
                raise ProxyAuthenticationError(
                    "socks5 proxy accepts no offered auth methods"
                )
            if method == 0x02:
                user = profile.username.encode()
                pwd = password.encode()
                self._socks_send(
                    sock,
                    b"\x01"
                    + len(user).to_bytes(1, "big")
                    + user
                    + len(pwd).to_bytes(1, "big")
                    + pwd,
                )
                auth_reply = self._socks_recv(sock, 2)
                if auth_reply[1] != 0x00:
                    raise ProxyAuthenticationError(
                        "socks5 proxy rejected user/password credentials"
                    )
            elif method != 0x00:
                raise ProxyTunnelError(f"socks5 selected unsupported method {method}")

            host_bytes = route.target_host.encode()
            request = (
                b"\x05\x01\x00\x03"
                + len(host_bytes).to_bytes(1, "big")
                + host_bytes
                + route.target_port.to_bytes(2, "big")
            )
            self._socks_send(sock, request)
            head = self._socks_recv(sock, 4)
            if head[0] != 0x05:
                raise ProxyTunnelError("malformed socks5 reply header")
            if head[1] != 0x00:
                raise ProxyTunnelError(
                    f"socks5 CONNECT failed with code {head[1]}"
                )
            atyp = head[3]
            if atyp == 0x01:
                self._socks_recv(sock, 4)
            elif atyp == 0x03:
                length = self._socks_recv(sock, 1)[0]
                self._socks_recv(sock, length)
            elif atyp == 0x04:
                self._socks_recv(sock, 16)
            else:
                raise ProxyTunnelError(f"socks5 unknown address type {atyp}")
            self._socks_recv(sock, 2)
            return sock
        except TransportError:
            try:
                sock.close()
            except OSError:
                pass
            raise
        except (TimeoutError, socket.timeout) as err:
            try:
                sock.close()
            except OSError:
                pass
            raise TransportTimeoutError("socks5 handshake timed out") from err

    def _socks_send(self, sock: socket.socket, data: bytes) -> None:
        try:
            sock.sendall(data)
        except OSError as err:
            raise ProxyTunnelError(f"socks5 write failed: {err}") from err

    def _socks_recv(self, sock: socket.socket, count: int) -> bytes:
        buf = bytearray()
        while len(buf) < count:
            try:
                chunk = sock.recv(count - len(buf))
            except (TimeoutError, socket.timeout) as err:
                raise TransportTimeoutError("socks5 read timed out") from err
            except OSError as err:
                raise ProxyTunnelError(f"socks5 read failed: {err}") from err
            if not chunk:
                raise ProxyTunnelError("socks5 server closed connection early")
            buf.extend(chunk)
        return bytes(buf)
