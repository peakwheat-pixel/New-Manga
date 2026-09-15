"""Fixtures for the network/settings suites (see helpers.py)."""

from __future__ import annotations

import pytest

import helpers  # noqa: F401  (injects src into sys.path first)
from application.settings.bindings import ProviderBindingResolver
from application.settings.resolution import SettingsResolutionService

from helpers import InMemoryNetworkProfileStore, InMemoryProviderProfileStore


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
