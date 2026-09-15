"""Route resolution unit tests: unified Direct/System/HTTP/HTTPS/SOCKS5
plus bypass/inherit policy (AC-NET-001, D03 §27)."""

from __future__ import annotations

import os

import pytest

from infrastructure.transport.stdlib import StdlibTransport

from net_helpers import (
    MODE_DIRECT,
    MODE_HTTP,
    MODE_HTTPS,
    MODE_SOCKS5,
    MODE_SYSTEM,
    make_network_profile,
)


@pytest.fixture()
def transport():
    return StdlibTransport()


def test_direct_mode_routes_straight(transport):
    route = transport.resolve_route(
        "http://api.example.com/v1", make_network_profile(mode=MODE_DIRECT)
    )
    assert not route.via_proxy
    assert (route.target_host, route.target_port) == ("api.example.com", 80)


def test_http_mode_uses_matching_endpoint(transport):
    profile = make_network_profile(
        mode=MODE_HTTP, http_proxy="http://127.0.0.1:8888"
    )
    route = transport.resolve_route("http://api.example.com/v1", profile)
    assert route.via_proxy
    assert route.proxy_kind == "http"
    assert (route.proxy_host, route.proxy_port) == ("127.0.0.1", 8888)
    assert route.proxy_source == "profile"


def test_https_mode_prefers_https_endpoint(transport):
    profile = make_network_profile(
        mode=MODE_HTTPS,
        http_proxy="http://127.0.0.1:8888",
        https_proxy="https://127.0.0.1:8443",
    )
    route = transport.resolve_route("https://api.example.com/v1", profile)
    assert route.proxy_kind == "https"
    assert route.proxy_port == 8443


def test_socks5_mode_sets_socks_kind(transport):
    profile = make_network_profile(
        mode=MODE_SOCKS5, socks5_proxy="127.0.0.1:1080"
    )
    route = transport.resolve_route("http://api.example.com/v1", profile)
    assert route.via_proxy and route.proxy_kind == "socks5"
    assert (route.proxy_host, route.proxy_port) == ("127.0.0.1", 1080)


def test_bypass_hosts_force_direct_even_in_proxy_mode(transport):
    from ports.network.profiles import DEFAULT_BYPASS_HOSTS

    profile = make_network_profile(
        mode=MODE_HTTP,
        http_proxy="http://127.0.0.1:8888",
        bypass_hosts=frozenset({"api.example.com", ".internal"})
        | DEFAULT_BYPASS_HOSTS,
    )
    assert transport.resolve_route(
        "http://api.example.com/v1", profile
    ).reason == "bypass"
    assert transport.resolve_route("http://nas.internal/x", profile).reason == "bypass"
    # 构造器默认集含 localhost/127.0.0.1（D03 §27），可显式关闭：
    assert transport.resolve_route("http://127.0.0.1:9/x", profile).reason == "bypass"
    assert (
        transport.resolve_route(
            "http://api.example.com/v1",
            make_network_profile(mode=MODE_HTTP, http_proxy="http://127.0.0.1:8888"),
        ).via_proxy
        is True
    )


def test_system_mode_respects_environment(monkeypatch, transport):
    monkeypatch.setenv("http_proxy", "http://127.0.0.1:8888")
    monkeypatch.delenv("https_proxy", raising=False)
    monkeypatch.delenv("no_proxy", raising=False)
    monkeypatch.setattr(
        "urllib.request.proxy_bypass", lambda host: host == "bypassed.example"
    )
    profile = make_network_profile(mode=MODE_SYSTEM)
    route = transport.resolve_route("http://api.example.com/v1", profile)
    assert route.via_proxy and route.proxy_source == "system"
    assert (route.proxy_host, route.proxy_port) == ("127.0.0.1", 8888)

    assert not transport.resolve_route(
        "http://bypassed.example/v1", profile
    ).via_proxy
    assert transport.resolve_route(
        "https://api.example.com/v1", profile
    ).reason == "system-none"


def test_inherit_system_fills_empty_endpoint(monkeypatch, transport):
    monkeypatch.setenv("https_proxy", "http://127.0.0.1:8888")
    monkeypatch.setattr("urllib.request.proxy_bypass", lambda host: False)
    profile = make_network_profile(mode=MODE_HTTP, inherit_system=True)
    route = transport.resolve_route("https://api.example.com/v1", profile)
    assert route.via_proxy and route.proxy_source == "system"
    # explicit endpoint wins over system
    configured = make_network_profile(
        mode=MODE_HTTP, http_proxy="http://10.0.0.1:3128", inherit_system=True
    )
    route = transport.resolve_route("http://api.example.com/v1", configured)
    assert (route.proxy_host, route.proxy_port) == ("10.0.0.1", 3128)


def test_explicit_port_and_defaults(transport):
    route = transport.resolve_route(
        "https://api.example.com:8443/v1", make_network_profile()
    )
    assert route.target_port == 8443
    route = transport.resolve_route(
        "https://api.example.com/v1", make_network_profile()
    )
    assert route.target_port == 443


def test_bad_urls_rejected(transport):
    with pytest.raises(Exception):
        transport.resolve_route("ftp://api.example.com/x", make_network_profile())
    with pytest.raises(Exception):
        transport.resolve_route("not-a-url", make_network_profile())
