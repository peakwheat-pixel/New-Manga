"""Network profile safety gates and provider→network resolution
(AC-SEC-004/005, D03 §25 proxy_policy)."""

from __future__ import annotations

import pytest

from application.settings.errors import SettingsError
from application.settings.models import EffectiveSetting
from application.settings.network import (
    DangerousSettingError,
    NetworkProfileService,
    ProviderNetworkResolver,
)

from helpers import make_network_profile, make_provider_profile


@pytest.fixture()
def service(network_store):
    return NetworkProfileService(network_store)


def test_new_profile_defaults_to_verified_tls(service, network_store):
    decision = service.create_profile(make_network_profile("net-safe"))
    assert decision.profile.verify_tls is True  # AC-SEC-004
    assert network_store.get_profile("net-safe") is not None


def test_creating_unverified_tls_requires_confirmation(service):
    profile = make_network_profile("net-risk", verify_tls=False)
    with pytest.raises(DangerousSettingError) as exc:
        service.create_profile(profile)
    assert exc.value.confirmation_required is True

    decision = service.create_profile(profile, confirm_disable_tls=True)
    assert not decision.profile.verify_tls
    assert any("TLS" in note for note in decision.notes)


def test_disabling_tls_on_existing_profile_requires_confirmation(service):
    service.create_profile(make_network_profile("net-safe"))
    with pytest.raises(DangerousSettingError):
        service.update_profile(make_network_profile("net-safe", verify_tls=False))
    decision = service.update_profile(
        make_network_profile("net-safe", verify_tls=False), confirm_disable_tls=True
    )
    assert not decision.profile.verify_tls


def test_enabling_direct_fallback_is_recorded(service):
    service.create_profile(make_network_profile("net-1"))
    decision = service.update_profile(
        make_network_profile("net-1", mode="socks5", socks5_proxy="127.0.0.1:1080",
                             allow_proxy_failure_direct_fallback=True)
    )
    assert any("fallback" in note for note in decision.notes)


def test_update_unknown_profile_raises(service):
    with pytest.raises(SettingsError):
        service.update_profile(make_network_profile("ghost"))


# ----------------------------------------------------------------------
# provider -> network resolution (D03 §25 proxy_policy)
# ----------------------------------------------------------------------


@pytest.fixture()
def net_resolver(network_store):
    return ProviderNetworkResolver(network_store)


def test_direct_policy_ignores_everything(net_resolver, network_store):
    network_store.add_profile(make_network_profile("net-x", mode="http", http_proxy="http://10.0.0.1:3128"))
    provider = make_provider_profile("p1", proxy_policy="direct", network_profile_id="net-x")
    route = net_resolver.resolve(provider)
    assert route.mode == "direct"


def test_profile_policy_uses_provider_profile(net_resolver, network_store):
    network_store.add_profile(make_network_profile("net-x", mode="socks5", socks5_proxy="127.0.0.1:1080"))
    provider = make_provider_profile("p1", proxy_policy="profile", network_profile_id="net-x")
    assert net_resolver.resolve(provider).network_profile_id == "net-x"


def test_profile_policy_missing_network_raises(net_resolver):
    provider = make_provider_profile("p1", proxy_policy="profile", network_profile_id="ghost")
    with pytest.raises(SettingsError):
        net_resolver.resolve(provider)
    provider = make_provider_profile("p2", proxy_policy="profile", network_profile_id=None)
    with pytest.raises(SettingsError):
        net_resolver.resolve(provider)


def test_inherit_policy_uses_effective_setting(net_resolver, network_store):
    network_store.add_profile(make_network_profile("net-x", mode="http", http_proxy="http://10.0.0.1:3128"))
    provider = make_provider_profile("p1", proxy_policy="inherit")
    setting = EffectiveSetting(
        key="network.profile_id", value="net-x", source_scope_type="global"
    )
    assert net_resolver.resolve(provider, network_setting=setting).network_profile_id == "net-x"


def test_inherit_policy_without_setting_goes_direct(net_resolver):
    provider = make_provider_profile("p1", proxy_policy="inherit")
    route = net_resolver.resolve(provider)
    assert route.mode == "direct"
