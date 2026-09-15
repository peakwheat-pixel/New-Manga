"""Staged connection diagnostics against local endpoints: every failure
keeps its typed stage/error code — never a flat "连接失败"
(AC-NET-004)."""

from __future__ import annotations

import shutil

import pytest

from infrastructure.network.diagnostics import (
    STAGE_AUTH,
    STAGE_DNS,
    STAGE_HTTP,
    STAGE_TCP,
    STAGE_TLS,
    ConnectionTester,
)
from infrastructure.transport.stdlib import StdlibTransport

import servers
from helpers import MODE_SOCKS5, make_network_profile

openssl = shutil.which("openssl")
pytestmark_tls = pytest.mark.skipif(openssl is None, reason="openssl unavailable")


@pytest.fixture()
def tester():
    return ConnectionTester(StdlibTransport())


def test_all_stages_pass_with_auth(tester, target):
    report = tester.test(
        target.url(),
        make_network_profile(),
        auth_headers_provider=lambda: {"Authorization": "Bearer ok"},
    )
    assert report.ok
    assert [s.stage for s in report.stages] == [
        STAGE_DNS,
        STAGE_TCP,
        STAGE_TLS,
        STAGE_HTTP,
        STAGE_AUTH,
    ]
    # http 目标上 TLS 阶段合理跳过（ok=None）；不能有失败阶段
    assert not any(s.ok is False for s in report.stages)
    assert report.http_status == 200


def test_dns_failure_is_typed_and_stops_ladder(tester):
    report = tester.test(
        "http://no-such-host.invalid/x", make_network_profile(timeout_seconds=2)
    )
    failing = report.failing_stage()
    assert failing.stage == STAGE_DNS
    assert failing.error_code == "DNS_RESOLUTION_FAILED"
    later = {s.stage: s for s in report.stages}
    assert later[STAGE_TCP].ok is None  # skipped
    assert later[STAGE_HTTP].ok is None
    assert not report.ok


def test_tcp_failure_reports_first_hop_code(tester):
    report = tester.test(
        "http://127.0.0.1:9/x", make_network_profile(timeout_seconds=1)
    )
    failing = report.failing_stage()
    assert failing.stage == STAGE_TCP
    assert failing.error_code in ("TCP_CONNECTION_FAILED", "TIMEOUT")


def test_silent_proxy_surfaces_timeout_at_http_stage(tester, target):
    proxy = servers.ControlledProxyServer(mode="silent")
    try:
        profile = make_network_profile(
            mode=MODE_SOCKS5,
            socks5_proxy=f"127.0.0.1:{proxy.port}",
            timeout_seconds=0.5,
        )
        report = tester.test(target.url(), profile)
        by_stage = {s.stage: s for s in report.stages}
        assert by_stage[STAGE_DNS].ok and by_stage[STAGE_TCP].ok
        assert by_stage[STAGE_HTTP].ok is False
        assert by_stage[STAGE_HTTP].error_code == "TIMEOUT"  # 不是笼统"连接失败"
        assert by_stage[STAGE_AUTH].ok is None
    finally:
        proxy.close()


def test_provider_auth_rejection_is_typed(tester, target):
    report = tester.test(
        target.url(),
        make_network_profile(),
        auth_headers_provider=lambda: {"X-Test-Status": "401"},
    )
    by_stage = {s.stage: s for s in report.stages}
    assert by_stage[STAGE_HTTP].ok
    auth = by_stage[STAGE_AUTH]
    assert auth.ok is False
    assert "401" in auth.detail
    assert not report.ok


@pytestmark_tls
def test_tls_stage_fails_typed_for_untrusted_cert(tester, tmp_path):
    server, _cafile = servers.make_tls_target(tmp_path)
    try:
        report = tester.test(
            server.url("https"), make_network_profile(timeout_seconds=3)
        )
        by_stage = {s.stage: s for s in report.stages}
        tls = by_stage[STAGE_TLS]
        assert tls.ok is False
        assert tls.error_code == "TLS_HANDSHAKE_FAILED"
        assert by_stage[STAGE_HTTP].ok is None
    finally:
        server.close()
