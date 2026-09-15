"""TLS behavior through real handshakes (AC-SEC-004, D07 §68).

Uses an openssl-generated self-signed local target: verified TLS works
(direct and through a CONNECT tunnel) when the CA is trusted; an
untrusted cert fails typed; ``verify_tls=False`` is the only way it
passes without trust — proving the dangerous flag is what it says.
Skipped when openssl is unavailable (recorded as NOT_RUN then).
"""

from __future__ import annotations

import shutil

import pytest

from infrastructure.transport.stdlib import StdlibTransport
from ports.network.transport import TlsError

import servers
from helpers import MODE_HTTP, make_network_profile

openssl = shutil.which("openssl")
pytestmark = pytest.mark.skipif(openssl is None, reason="openssl unavailable")


@pytest.fixture(scope="module")
def tls_setup(tmp_path_factory):
    server, cafile = servers.make_tls_target(tmp_path_factory.mktemp("tls-certs"))
    yield server, cafile
    server.close()


def _request(url):
    from ports.network.transport import TransportRequest

    return TransportRequest(method="GET", url=url)


def test_verified_tls_direct(tls_setup):
    server, cafile = tls_setup
    transport = StdlibTransport(extra_cafile=cafile)
    outcome = transport.send(_request(server.url("https")), make_network_profile())
    assert outcome.response.status == 200
    assert b'"server": "target"' in outcome.response.body


def test_verified_tls_through_connect_tunnel(tls_setup):
    server, cafile = tls_setup
    proxy = servers.ControlledProxyServer(mode="tunnel")
    try:
        transport = StdlibTransport(extra_cafile=cafile)
        profile = make_network_profile(
            mode=MODE_HTTP, http_proxy=f"http://127.0.0.1:{proxy.port}"
        )
        outcome = transport.send(_request(server.url("https")), profile)
        assert outcome.response.status == 200
        assert proxy.connect_targets == [f"127.0.0.1:{server.port}"]
    finally:
        proxy.close()


def test_untrusted_cert_fails_typed(tls_setup):
    server, _cafile = tls_setup
    transport = StdlibTransport()  # system trust only → self-signed rejected
    with pytest.raises(TlsError):
        transport.send(_request(server.url("https")), make_network_profile())


def test_untrusted_through_tunnel_fails_typed(tls_setup):
    server, _cafile = tls_setup
    proxy = servers.ControlledProxyServer(mode="tunnel")
    try:
        transport = StdlibTransport()
        profile = make_network_profile(
            mode=MODE_HTTP, http_proxy=f"http://127.0.0.1:{proxy.port}"
        )
        with pytest.raises(TlsError):
            transport.send(_request(server.url("https")), profile)
    finally:
        proxy.close()


def test_verify_tls_false_allows_untrusted(tls_setup):
    server, _cafile = tls_setup
    transport = StdlibTransport()
    profile = make_network_profile(verify_tls=False)
    outcome = transport.send(_request(server.url("https")), profile)
    assert outcome.response.status == 200
