"""Single-route probes for the frozen P15 network-profile test command."""

from __future__ import annotations

import json
import socket
from dataclasses import replace
from urllib.parse import urlsplit, urlunsplit

from infrastructure.transport.stdlib import ResolvedRoute
from ports.network.profiles import MODE_SOCKS5, MODE_SYSTEM
from ports.network.transport import TransportError, TransportRequest

_AUTH_PROVIDER_TYPES = frozenset({"openai-compatible", "openai-compatible-vision"})
# shortcut: unsupported adapters fail at HTTP; add a mapping when one defines a safe probe.
_MODEL_PROVIDER_TYPES = _AUTH_PROVIDER_TYPES | {"local-sakura"}


class NetworkProfileTestProbe:
    """Run one real network operation per applicable diagnostic stage."""

    def __init__(self, transport) -> None:
        self._transport = transport

    def run(self, stage: str, endpoint: str, provider, network, context: dict) -> str | None:
        if stage == "Proxy":
            route, profile = self._route(endpoint, network, context)
            if network.mode == MODE_SYSTEM and not route.via_proxy:
                return "system_route_is_direct"
            if not route.via_proxy:
                raise TransportError("selected proxy route is unavailable")
            self._probe_proxy(route, profile)
        elif stage == "DNS":
            host = urlsplit(endpoint).hostname
            if not host:
                raise TransportError("provider endpoint has no host")
            socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
        elif stage == "TCP":
            route, profile = self._route(endpoint, network, context)
            sock = self._connect_provider(route, profile)
            sock.close()
        elif stage == "TLS":
            if urlsplit(endpoint).scheme.lower() == "http":
                return "provider_endpoint_uses_http"
            route, profile = self._route(endpoint, network, context)
            sock = self._connect_provider(route, profile)
            try:
                sock = self._transport._tls_wrap(
                    sock, route.target_host, profile, stage="provider-tls"
                )
            finally:
                sock.close()
        elif stage == "HTTP":
            self._probe_provider_http(endpoint, provider, network, context)
        elif stage == "ProviderAuth":
            if provider.provider_type not in _AUTH_PROVIDER_TYPES:
                return "provider_auth_not_required"
            if context.get("provider_auth_required") is False:
                return "provider_auth_not_required"
            if context.get("provider_auth_required") is not True:
                raise TransportError("provider authentication was not confirmed")
            self._probe_provider_auth(endpoint, provider, network, context)
        else:
            raise ValueError("unknown network-test stage")
        return None

    def _route(self, endpoint: str, network, context: dict):
        if "route" not in context:
            profile = replace(
                network,
                allow_proxy_failure_direct_fallback=False,
                bypass_hosts=frozenset(),
                inherit_system=network.mode == MODE_SYSTEM,
            )
            route = self._transport.resolve_route(endpoint, profile)
            if network.mode == MODE_SOCKS5:
                # Keep the legacy transport route behavior unchanged while honoring this command's SOCKS5 endpoint.
                proxy = urlsplit(profile.socks5_proxy)
                route = replace(
                    route,
                    proxy_host=proxy.hostname or "",
                    proxy_port=proxy.port or 1080,
                )
            context["route"] = route
            context["routing_profile"] = profile
        return context["route"], context["routing_profile"]

    def _probe_proxy(self, route, profile) -> None:
        if route.proxy_kind == "socks5":
            self._probe_socks5_proxy(route, profile)
            return
        sock = self._transport._tcp_connect(
            route.proxy_host, route.proxy_port, profile.timeout_seconds
        )
        try:
            if route.proxy_kind == "https":
                sock = self._transport._tls_wrap(
                    sock, route.proxy_host, profile, stage="proxy-tls"
                )
            self._transport._http_connect_tunnel(sock, route, profile)
        finally:
            sock.close()

    def _probe_socks5_proxy(self, route, profile) -> None:
        sock = self._transport._tcp_connect(
            route.proxy_host, route.proxy_port, profile.timeout_seconds
        )
        try:
            has_credentials = bool(profile.username or profile.credential_ref)
            password = self._transport._proxy_password(profile) if has_credentials else ""
            methods = b"\x05\x02\x00\x02" if has_credentials else b"\x05\x01\x00"
            sock.sendall(methods)
            version, method = self._recv_exact(sock, 2)
            if version != 5 or method == 0xFF:
                raise TransportError("SOCKS5 negotiation failed")
            if method == 0x02:
                if not has_credentials:
                    raise TransportError("SOCKS5 selected authentication that was not offered")
                username = profile.username.encode("utf-8")
                secret = password.encode("utf-8")
                if len(username) > 255 or len(secret) > 255:
                    raise TransportError("SOCKS5 credentials are invalid")
                sock.sendall(
                    b"\x01" + bytes((len(username),)) + username
                    + bytes((len(secret),)) + secret
                )
                version, status = self._recv_exact(sock, 2)
                if version != 1 or status != 0:
                    raise TransportError("SOCKS5 authentication failed")
            elif method != 0x00:
                raise TransportError("SOCKS5 selected an unsupported method")
        finally:
            sock.close()

    @staticmethod
    def _recv_exact(sock, count: int) -> bytes:
        received = bytearray()
        while len(received) < count:
            chunk = sock.recv(count - len(received))
            if not chunk:
                raise TransportError("SOCKS5 negotiation ended early")
            received.extend(chunk)
        return bytes(received)

    def _connect_provider(self, route, profile):
        if not route.via_proxy:
            return self._transport._tcp_connect(
                route.target_host, route.target_port, profile.timeout_seconds
            )
        if route.proxy_kind == "socks5":
            return self._transport._socks5_connect(route, profile)
        sock = self._transport._tcp_connect(
            route.proxy_host, route.proxy_port, profile.timeout_seconds
        )
        try:
            if route.proxy_kind == "https":
                sock = self._transport._tls_wrap(
                    sock, route.proxy_host, profile, stage="proxy-tls"
                )
            self._transport._http_connect_tunnel(sock, route, profile)
            return sock
        except BaseException:
            sock.close()
            raise

    def _probe_provider_http(self, endpoint: str, provider, network, context: dict) -> None:
        if provider.provider_type not in _MODEL_PROVIDER_TYPES:
            raise TransportError("provider adapter has no safe connection probe")
        route, profile = self._route(endpoint, network, context)
        probe_url = _models_url(endpoint)
        if _authority(probe_url) != _authority(endpoint):
            raise TransportError("provider probe changed authority")
        response = self._transport._send_once(
            TransportRequest(method="GET", url=probe_url), profile, route
        )
        auth_supported = provider.provider_type in _AUTH_PROVIDER_TYPES
        if auth_supported and response.status in (401, 403):
            context["provider_auth_required"] = True
            return
        if response.status != 200 or not _is_model_list(response.body):
            raise TransportError("provider probe response was not valid")
        context["provider_auth_required"] = False

    def _probe_provider_auth(self, endpoint: str, provider, network, context: dict) -> None:
        if context.get("provider_auth_required") is not True:
            return
        if not provider.credential_ref or self._transport._credentials is None:
            raise TransportError("provider authentication is unavailable")
        try:
            secret = self._transport._credentials.resolve_credential(
                provider.credential_ref
            ).reveal()
        except Exception:
            raise TransportError("provider authentication is unavailable") from None
        route, profile = self._route(endpoint, network, context)
        response = self._transport._send_once(
            TransportRequest(
                method="GET",
                url=_models_url(endpoint),
                headers={"Authorization": f"Bearer {secret}"},
            ),
            profile,
            route,
        )
        if response.status != 200 or not _is_model_list(response.body):
            raise TransportError("provider authentication was not confirmed")


def _authority(url: str) -> tuple[str, str, int | None]:
    parts = urlsplit(url)
    return parts.scheme.lower(), (parts.hostname or "").lower(), parts.port


def _models_url(endpoint: str) -> str:
    parts = urlsplit(endpoint)
    path = parts.path.rstrip("/")
    if path.endswith("/chat/completions"):
        path = path[: -len("/chat/completions")]
    if not path.endswith("/models"):
        path += "/models"
    return urlunsplit((parts.scheme, parts.netloc, path or "/models", "", ""))


def _is_model_list(body: bytes) -> bool:
    try:
        payload = json.loads(body)
    except (ValueError, TypeError):
        return False
    return (
        isinstance(payload, dict)
        and isinstance(payload.get("data"), list)
        and any(
            isinstance(item, dict) and isinstance(item.get("id"), str)
            for item in payload["data"]
        )
    )
