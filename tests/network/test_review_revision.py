"""Regression tests for the TASK-009 review revision (R-001~R-010,
doc/reviews/TASK-009-f1dd602.md commit 2da1a39). One test per finding;
names carry the finding ID for direct disposition mapping."""

from __future__ import annotations

import pytest

from application.settings.bindings import ProviderBinding
from application.settings.errors import UnresolvedCapabilityError
from application.settings.snapshots import build_snapshot
from infrastructure.network.diagnostics import ConnectionTester, STAGE_AUTH, STAGE_HTTP
from infrastructure.transport.stdlib import ResolvedRoute, StdlibTransport, _parse_proxy_url
from ports.network.transport import (
    ProxyAuthenticationError,
    ProxyTunnelError,
    TransportError,
    TransportRequest,
    TransportTimeoutError,
)

import net_helpers
import servers
from net_helpers import MODE_HTTP, MODE_SOCKS5, make_network_profile, make_provider_profile


def _request(url):
    return TransportRequest(method="GET", url=url)


@pytest.fixture()
def transport():
    return StdlibTransport()


@pytest.fixture()
def tester():
    from infrastructure.network.diagnostics import ConnectionTester as _T

    return _T(StdlibTransport())


# ----------------------------------------------------------------------
# R-001: absolute-form proxy auth + 407 typed
# ----------------------------------------------------------------------


def test_r001_forward_proxy_sends_credentials(transport, target):
    proxy = servers.ControlledProxyServer(
        mode="forward", username="mega", password="right"
    )
    vault = net_helpers.InMemoryCredentialStore()
    try:
        from ports.providers.credentials import SecretValue, make_credential_ref

        ref = make_credential_ref("proxy", "fwd")
        vault.store_credential(ref, SecretValue("right"))
        authed = StdlibTransport(credential_store=vault)
        profile = make_network_profile(
            mode=MODE_HTTP,
            http_proxy=f"http://127.0.0.1:{proxy.port}",
            username="mega",
            credential_ref=ref,
        )
        outcome = authed.send(_request(target.url()), profile)
        assert outcome.response.status == 200
        import base64

        expected = base64.b64encode(b"mega:right").decode()
        assert proxy.forward_auth_headers == [f"Basic {expected}"]
    finally:
        proxy.close()


def test_r001_forward_407_is_typed_auth_error(transport, target):
    proxy = servers.ControlledProxyServer(
        mode="forward", username="mega", password="right"
    )
    vault = net_helpers.InMemoryCredentialStore()
    try:
        from ports.providers.credentials import SecretValue, make_credential_ref

        ref = make_credential_ref("proxy", "fwd-wrong")
        vault.store_credential(ref, SecretValue("wrong"))
        authed = StdlibTransport(credential_store=vault)
        profile = make_network_profile(
            mode=MODE_HTTP,
            http_proxy=f"http://127.0.0.1:{proxy.port}",
            username="mega",
            credential_ref=ref,
        )
        with pytest.raises(ProxyAuthenticationError):
            authed.send(_request(target.url()), profile)
        assert proxy.auth_failures == 1
        assert target.requests == []  # 无 fallback：目标未被触碰
    finally:
        proxy.close()


def test_r001_forward_407_falls_back_when_explicitly_allowed(target):
    proxy = servers.ControlledProxyServer(
        mode="forward", username="mega", password="right"
    )
    vault = net_helpers.InMemoryCredentialStore()
    try:
        from ports.providers.credentials import SecretValue, make_credential_ref

        ref = make_credential_ref("proxy", "fwd-fb")
        vault.store_credential(ref, SecretValue("wrong"))
        authed = StdlibTransport(credential_store=vault)
        profile = make_network_profile(
            mode=MODE_HTTP,
            http_proxy=f"http://127.0.0.1:{proxy.port}",
            username="mega",
            credential_ref=ref,
            allow_proxy_failure_direct_fallback=True,
        )
        outcome = authed.send(_request(target.url()), profile)
        assert outcome.response.status == 200
        assert len(outcome.fallback_events) == 1
        assert "407" in outcome.fallback_events[0].detail
    finally:
        proxy.close()


# ----------------------------------------------------------------------
# R-002: failure paths close the socket
# ----------------------------------------------------------------------


class _FakeSocket:
    """Minimal socket stand-in for establishment/exchange failure tests."""

    def __init__(self):
        self.close_count = 0
        import io

        self._file = io.BytesIO(b"")  # readline() -> b"": remote hung up

    def close(self):
        self.close_count += 1

    def sendall(self, data):
        pass

    def makefile(self, *args, **kwargs):
        return self._file


def _tunnel_route():
    return ResolvedRoute(
        target_scheme="https",
        target_host="target.example",
        target_port=443,
        via_proxy=True,
        proxy_kind="http",
        proxy_host="127.0.0.1",
        proxy_port=1,
        proxy_source="profile",
        reason="profile:http",
    )


@pytest.mark.parametrize(
    "failing_stage",
    ["tunnel", "tls"],
)
def test_r002_establish_failure_closes_socket(monkeypatch, failing_stage):
    transport = StdlibTransport()
    fake = _FakeSocket()
    monkeypatch.setattr(transport, "_tcp_connect", lambda *a, **k: fake)
    # 两个分支都需要绕开真实隧道握手，让目标阶段抛错
    monkeypatch.setattr(transport, "_http_connect_tunnel", lambda *a, **k: None)
    if failing_stage == "tunnel":
        monkeypatch.setattr(
            transport,
            "_http_connect_tunnel",
            lambda *a, **k: (_ for _ in ()).throw(ProxyTunnelError("502")),
        )
    else:

        def _boom(*a, **k):
            raise ProxyTunnelError("tls stage exploded")

        # _tls_wrap 失败同样必须关闭底层 socket
        monkeypatch.setattr(transport, "_tls_wrap", _boom)
    profile = make_network_profile(mode=MODE_HTTP, http_proxy="http://127.0.0.1:1")
    with pytest.raises(ProxyTunnelError):
        transport._establish(
            _request("https://target.example/x"), profile, _tunnel_route()
        )
    assert fake.close_count == 1


def test_r002_exchange_failure_closes_socket(transport, monkeypatch):
    """HTTP exchange 阶段（含 typed 映射分支）失败也走同一 cleanup seam。"""
    fake = _FakeSocket()
    profile = make_network_profile(mode=MODE_HTTP, http_proxy="http://127.0.0.1:1")
    monkeypatch.setattr(
        transport,
        "_establish",
        lambda req, prof, route: (fake, "/x", "target.example:80", None),
    )
    route = transport.resolve_route("http://target.example/x", profile)
    # _FakeSocket.makefile 读到空 → RemoteDisconnected（OSError 子类）
    # → typed TcpConnectionError；finally 必须已关闭 socket
    #（conn.close() 与 cleanup seam 都会关，socket.close 幂等，≥1 即可）
    from ports.network.transport import TcpConnectionError

    with pytest.raises((TcpConnectionError, TransportError)):
        transport._send_once(_request("http://target.example/x"), profile, route)
    assert fake.close_count >= 1


# ----------------------------------------------------------------------
# R-003: post-connect timeout typed + enters fallback gate
# ----------------------------------------------------------------------


def test_r003_proxy_read_timeout_is_typed(transport, target):
    proxy = servers.ControlledProxyServer(mode="silent")
    try:
        profile = make_network_profile(
            mode=MODE_HTTP,
            http_proxy=f"http://127.0.0.1:{proxy.port}",
            timeout_seconds=0.3,
        )
        with pytest.raises(TransportTimeoutError):
            transport.send(_request("http://target.example/x"), profile)
        assert target.requests == []
    finally:
        proxy.close()


def test_r003_proxy_read_timeout_enters_fallback_gate(target):
    proxy = servers.ControlledProxyServer(mode="silent")
    try:
        transport = StdlibTransport()
        profile = make_network_profile(
            mode=MODE_HTTP,
            http_proxy=f"http://127.0.0.1:{proxy.port}",
            timeout_seconds=0.3,
            allow_proxy_failure_direct_fallback=True,
        )
        outcome = transport.send(_request(target.url()), profile)
        assert outcome.response.status == 200
        assert len(outcome.fallback_events) == 1
        assert "timed out" in outcome.fallback_events[0].detail
    finally:
        proxy.close()


# ----------------------------------------------------------------------
# R-004: fallback trace across diagnostic stages
# ----------------------------------------------------------------------


def test_r004_fallback_trace_covers_http_and_auth_stages(tester, target):
    proxy = servers.ControlledProxyServer(mode="refuse_get")
    try:
        transport = StdlibTransport()
        profile = make_network_profile(
            mode=MODE_HTTP,
            http_proxy=f"http://127.0.0.1:{proxy.port}",
            allow_proxy_failure_direct_fallback=True,
        )
        tester = ConnectionTester(transport)
        report = tester.test(
            target.url(),
            profile,
            auth_headers_provider=lambda: {"Authorization": "Bearer ok"},
        )
        assert report.ok
        assert [(s.stage, s.event.reason) for s in report.fallback_trace] == [
            (STAGE_HTTP, "proxy_failure"),
            (STAGE_AUTH, "proxy_failure"),
        ]
        assert all("502" in s.event.detail for s in report.fallback_trace)
    finally:
        proxy.close()


# ----------------------------------------------------------------------
# R-005: provider auth typed error distinct from proxy auth
# ----------------------------------------------------------------------


def test_r005_provider_auth_rejection_typed_and_distinct(tester, target):
    report = tester.test(
        target.url(),
        make_network_profile(),
        auth_headers_provider=lambda: {"X-Test-Status": "401"},
    )
    by_stage = {s.stage: s for s in report.stages}
    auth = by_stage[STAGE_AUTH]
    assert auth.ok is False
    assert auth.error_code == "PROVIDER_AUTH_FAILED"
    # 与代理鉴权错误码可区分
    from ports.network.transport import ProviderAuthenticationError

    assert ProviderAuthenticationError("x").error_code == "PROVIDER_AUTH_FAILED"
    assert ProxyAuthenticationError("x").error_code == "PROXY_AUTH_FAILED"
    from infrastructure.network.retry import classify_error

    assert not classify_error(ProviderAuthenticationError("401")).retryable


# ----------------------------------------------------------------------
# R-006: snapshot mappings are read-only
# ----------------------------------------------------------------------


def test_r006_snapshot_mappings_reject_mutation(provider_store, binding_resolver):
    provider_store.add_profile(make_provider_profile("prof-t"))
    resolution = binding_resolver.resolve(
        "translation",
        bindings=[ProviderBinding("bd", "global", None, "translation", "prof-t")],
    )
    snapshot = build_snapshot(
        settings={},
        bindings={"translation": resolution},
        provider_profiles={"prof-t": resolution.provider_profile},
        network_profiles={},
    )
    with pytest.raises(TypeError):
        snapshot.provider_profiles["injected"] = resolution.provider_profile
    with pytest.raises(TypeError):
        snapshot.settings["x"] = None
    with pytest.raises((TypeError, AttributeError)):
        snapshot.bindings.pop("translation")
    # 只读访问不受影响
    assert snapshot.bindings["translation"].provider_profile.provider_profile_id == "prof-t"


# ----------------------------------------------------------------------
# R-007: capability declared by resolved profile
# ----------------------------------------------------------------------


def test_r007_task_selected_profile_must_declare_capability(
    binding_resolver, provider_store
):
    provider_store.add_profile(
        make_provider_profile("prof-trans", capabilities=frozenset({"translation"}))
    )
    with pytest.raises(UnresolvedCapabilityError):
        binding_resolver.resolve(
            "ocr", task_profile_id="prof-trans"
        )


def test_r007_binding_profile_must_declare_capability(binding_resolver, provider_store):
    provider_store.add_profile(
        make_provider_profile("prof-trans", capabilities=frozenset({"translation"}))
    )
    with pytest.raises(UnresolvedCapabilityError):
        binding_resolver.resolve(
            "ocr",
            bindings=[
                ProviderBinding("bd", "global", None, "ocr", "prof-trans")
            ],
        )


# ----------------------------------------------------------------------
# R-008: no userinfo in proxy endpoints
# ----------------------------------------------------------------------


def test_r008_model_rejects_userinfo_in_proxy_urls():
    with pytest.raises(ValueError):
        make_network_profile(
            mode=MODE_HTTP, http_proxy="http://user:secret-pw@10.0.0.1:3128"
        )
    with pytest.raises(ValueError):
        make_network_profile(mode=MODE_SOCKS5, socks5_proxy="user:secret-pw@127.0.0.1:1080")
    with pytest.raises(ValueError):
        make_network_profile(
            mode=MODE_HTTP, https_proxy="https://alice:hunter2@proxy.corp:8443"
        )


def test_r008_parse_proxy_url_rejects_userinfo():
    with pytest.raises(Exception):
        _parse_proxy_url("http://user:secret-pw@10.0.0.1:3128")


# ----------------------------------------------------------------------
# R-009: unicode secret equality
# ----------------------------------------------------------------------


def test_r009_unicode_secret_equality():
    from ports.providers.credentials import SecretValue

    assert SecretValue("密码-パスワード") == SecretValue("密码-パスワード")
    assert SecretValue("密码") != SecretValue("不同的")
    assert SecretValue("ascii") == SecretValue("ascii")
