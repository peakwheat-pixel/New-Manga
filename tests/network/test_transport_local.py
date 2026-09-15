"""Transport end-to-end against local controllable endpoints only
(TASK-009 test requirements: no real/paid APIs).

Covers: direct GET, absolute-form HTTP proxy, CONNECT tunnel + TLS,
proxy auth (407 / socks5 user-pass), tunnel refusal without silent
direct, explicit fallback with a visible FallbackEvent, timeout, and
DNS failure typing (AC-NET-002/003, AC-SEC-004).
"""

from __future__ import annotations

import base64

import pytest

from infrastructure.transport.stdlib import StdlibTransport
from ports.network.transport import (
    DnsResolutionError,
    ProxyAuthenticationError,
    ProxyTunnelError,
    TransportTimeoutError,
)

import net_helpers
import servers
from net_helpers import MODE_HTTP, MODE_SOCKS5, make_network_profile


@pytest.fixture()
def transport():
    return StdlibTransport()


def _request(url, method="GET"):
    from ports.network.transport import TransportRequest

    return TransportRequest(method=method, url=url, headers={"X-Probe": "1"})


# ----------------------------------------------------------------------
# direct + plain proxy
# ----------------------------------------------------------------------


def test_direct_get_reaches_local_target(transport, target):
    outcome = transport.send(_request(target.url()), make_network_profile())
    assert outcome.response.status == 200
    assert b'"server": "target"' in outcome.response.body
    assert outcome.fallback_events == ()
    method, path, headers = target.requests[-1]
    assert (method, path) == ("GET", "/health")
    assert headers["x-probe"] == "1"


def test_absolute_form_through_http_proxy(transport, target):
    proxy = servers.ControlledProxyServer(mode="forward")
    try:
        profile = make_network_profile(
            mode=MODE_HTTP, http_proxy=f"http://127.0.0.1:{proxy.port}"
        )
        outcome = transport.send(_request(target.url()), profile)
        assert outcome.response.status == 200
        assert b'"server": "target"' in outcome.response.body
    finally:
        proxy.close()


# ----------------------------------------------------------------------
# proxy auth
# ----------------------------------------------------------------------


def test_proxy_407_maps_to_auth_error_without_fallback(transport, target):
    proxy = servers.ControlledProxyServer(
        mode="tunnel", username="tester", password="correct-password"
    )
    vault = net_helpers.InMemoryCredentialStore()
    try:
        from ports.providers.credentials import SecretValue, make_credential_ref

        ref = make_credential_ref("proxy", "corp")
        vault.store_credential(ref, SecretValue("wrong-password"))
        authed_transport = StdlibTransport(credential_store=vault)
        profile = make_network_profile(
            mode=MODE_HTTP,
            http_proxy=f"http://127.0.0.1:{proxy.port}",
            username="tester",
            credential_ref=ref,
        )
        with pytest.raises(ProxyAuthenticationError):
            authed_transport.send(
                _request("https://127.0.0.1:9/health"), profile
            )
        assert proxy.auth_failures == 1
        # 407 后 target 从未被触碰：没有静默直连（AC-NET-002）
        assert target.requests == []
    finally:
        proxy.close()


def test_missing_proxy_credential_is_config_error_not_network(transport, target):
    proxy = servers.ControlledProxyServer(mode="tunnel")
    try:
        profile = make_network_profile(
            mode=MODE_HTTP,
            http_proxy=f"http://127.0.0.1:{proxy.port}",
            username="tester",
            credential_ref="NewManga/proxy/never-stored",
        )
        from ports.network.transport import MissingCredentialError

        # https 目标强制 CONNECT，握手时才解析代理密码
        with pytest.raises(MissingCredentialError):
            transport.send(_request("https://127.0.0.1:9/health"), profile)
        assert proxy.connect_targets == []
    finally:
        proxy.close()


# ----------------------------------------------------------------------
# SOCKS5
# ----------------------------------------------------------------------


def test_socks5_circuit_plain_http(transport, target):
    socks = servers.MiniSocks5Server()
    try:
        profile = make_network_profile(
            mode=MODE_SOCKS5, socks5_proxy=f"127.0.0.1:{socks.port}"
        )
        outcome = transport.send(_request(target.url()), profile)
        assert outcome.response.status == 200
        assert socks.requests == [("127.0.0.1", target.port)]
    finally:
        socks.close()


def test_socks5_user_pass_auth(transport, target):
    socks = servers.MiniSocks5Server(username="mega", password="secret-pw")
    vault = net_helpers.InMemoryCredentialStore()
    try:
        from ports.providers.credentials import SecretValue, make_credential_ref

        ref = make_credential_ref("proxy", "socks")
        vault.store_credential(ref, SecretValue("secret-pw"))
        profile = make_network_profile(
            mode=MODE_SOCKS5,
            socks5_proxy=f"127.0.0.1:{socks.port}",
            username="mega",
            credential_ref=ref,
        )
        authed_transport = StdlibTransport(credential_store=vault)
        outcome = authed_transport.send(
            _request(target.url(), method="POST"), profile
        )
        assert outcome.response.status == 200
        assert socks.auth_failures == 0
        assert target.requests[-1][0] == "POST"
    finally:
        socks.close()


def test_socks5_bad_password_rejected(transport, target):
    socks = servers.MiniSocks5Server(username="mega", password="right")
    vault = net_helpers.InMemoryCredentialStore()
    try:
        from ports.providers.credentials import SecretValue, make_credential_ref

        ref = make_credential_ref("proxy", "socks")
        vault.store_credential(ref, SecretValue("wrong"))
        profile = make_network_profile(
            mode=MODE_SOCKS5,
            socks5_proxy=f"127.0.0.1:{socks.port}",
            username="mega",
            credential_ref=ref,
        )
        authed_transport = StdlibTransport(credential_store=vault)
        with pytest.raises(ProxyAuthenticationError):
            authed_transport.send(_request(target.url()), profile)
        assert socks.auth_failures == 1
        assert target.requests == []
    finally:
        socks.close()


# ----------------------------------------------------------------------
# fallback semantics (AC-NET-002/003)
# ----------------------------------------------------------------------


def test_tunnel_refusal_fails_loudly_by_default(transport, target):
    """代理回 502 拒绝 CONNECT：默认直接报错（AC-NET-002）。"""
    proxy = servers.ControlledProxyServer(mode="refuse")
    try:
        profile = make_network_profile(
            mode=MODE_HTTP, http_proxy=f"http://127.0.0.1:{proxy.port}"
        )
        # https 目标强制走 CONNECT；CONNECT 在握手阶段被 502 拒绝，
        # 因此不需要真实 TLS 服务端。
        with pytest.raises(ProxyTunnelError):
            transport.send(_request("https://127.0.0.1:9/health"), profile)
    finally:
        proxy.close()


def _dead_proxy_port() -> int:
    """A port that nothing listens on: TCP connect is refused."""
    import socket as socket_mod

    probe = socket_mod.socket()
    probe.bind(("127.0.0.1", 0))
    port = probe.getsockname()[1]
    probe.close()
    return port


def test_proxy_tcp_failure_never_falls_back_silently(transport, target):
    profile = make_network_profile(
        mode=MODE_SOCKS5, socks5_proxy=f"127.0.0.1:{_dead_proxy_port()}"
    )
    from ports.network.transport import TcpConnectionError

    with pytest.raises(TcpConnectionError):
        transport.send(_request(target.url()), profile)
    assert target.requests == []  # 没有静默直连触碰目标


def test_explicit_direct_fallback_records_visible_event(transport, target):
    """allow_proxy_failure_direct_fallback=true：一次 Direct 重试 +
    FallbackEvent 可见可审计（AC-NET-003）。"""
    profile = make_network_profile(
        mode=MODE_SOCKS5,
        socks5_proxy=f"127.0.0.1:{_dead_proxy_port()}",
        allow_proxy_failure_direct_fallback=True,
    )
    outcome = transport.send(_request(target.url()), profile)
    assert outcome.response.status == 200
    assert b'"server": "target"' in outcome.response.body
    assert len(outcome.fallback_events) == 1
    event = outcome.fallback_events[0]
    assert event.network_profile_id == profile.network_profile_id
    assert event.reason == "proxy_failure"
    assert event.fallback_to == "direct"


# ----------------------------------------------------------------------
# timeout + DNS typing
# ----------------------------------------------------------------------


def test_silent_proxy_times_out_typed(transport, target):
    proxy = servers.ControlledProxyServer(mode="silent")
    try:
        profile = make_network_profile(
            mode=MODE_SOCKS5,
            socks5_proxy=f"127.0.0.1:{proxy.port}",
            timeout_seconds=0.5,
        )
        with pytest.raises(TransportTimeoutError):
            transport.send(_request(target.url()), profile)
    finally:
        proxy.close()


def test_unresolvable_host_is_dns_error(transport):
    profile = make_network_profile(timeout_seconds=2)
    with pytest.raises(DnsResolutionError):
        transport.send(_request("http://this-host-does-not-exist.invalid/x"), profile)
