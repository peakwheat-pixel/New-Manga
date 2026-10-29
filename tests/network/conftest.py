"""Fixtures for the network/settings suites (see net_helpers.py)."""

from __future__ import annotations

import pytest

import net_helpers  # noqa: F401  (injects src into sys.path first)
import servers
from application.settings.bindings import ProviderBindingResolver
from application.settings.resolution import SettingsResolutionService

from net_helpers import InMemoryNetworkProfileStore, InMemoryProviderProfileStore


@pytest.fixture()
def provider_store():
    return InMemoryProviderProfileStore()


@pytest.fixture()
def network_store():
    return InMemoryNetworkProfileStore()


@pytest.fixture()
def resolver():
    return SettingsResolutionService()


@pytest.fixture()
def binding_resolver(provider_store):
    return ProviderBindingResolver(provider_store)


@pytest.fixture()
def target():
    server = servers.LocalTargetServer()
    yield server
    server.close()
