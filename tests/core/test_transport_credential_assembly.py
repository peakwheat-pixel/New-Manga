"""T1.2.1 B-003 (R5): the production assembly injects the credential store.

The settings page can persist a network profile whose proxy carries a
credential ref, but a request only authenticates when the transport
built by ``assemble_services`` actually owns a credential store. These
tests observe ``AppServices.transport`` — the seam the app runs on —
plus the best-effort ``None`` fallback that keeps the app startable
when the Windows vault cannot be opened (AC-OPTIONAL-001).
"""

from __future__ import annotations

import sys

import pytest

import infrastructure.credentials.windows as credentials_windows
from bootstrap.app import _credential_resolver, _credential_store, assemble_services
from infrastructure.transport.stdlib import StdlibTransport
from ports.providers.credentials import SecretValue, make_credential_ref


class _BrokenVault:
    """A vault adapter whose constructor fails, e.g. advapi32 missing."""

    def __init__(self) -> None:
        raise RuntimeError("vault unavailable")


def test_assembled_transport_carries_the_production_credential_store(
    tmp_path,
) -> None:
    if sys.platform != "win32":  # pragma: no cover - platform guard
        pytest.skip("WindowsCredentialStore requires win32")
    services = assemble_services(tmp_path / "library.db", tmp_path / "managed")
    try:
        assert isinstance(services.transport, StdlibTransport)
        assert services.transport._credentials is not None
        assert isinstance(
            services.transport._credentials, credentials_windows.WindowsCredentialStore
        )
    finally:
        services.conn.close()


def test_transport_still_assembles_when_the_vault_cannot_be_constructed(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.setattr(credentials_windows, "WindowsCredentialStore", _BrokenVault)
    assert _credential_store() is None
    services = assemble_services(tmp_path / "library.db", tmp_path / "managed")
    try:
        assert isinstance(services.transport, StdlibTransport)
        assert services.transport._credentials is None
    finally:
        services.conn.close()


def test_credential_store_returns_none_when_the_module_cannot_import(
    monkeypatch,
) -> None:
    monkeypatch.setitem(sys.modules, "infrastructure.credentials.windows", None)
    assert _credential_store() is None


def test_credential_resolver_shares_the_assembly_store(monkeypatch) -> None:
    if sys.platform != "win32":  # pragma: no cover - platform guard
        pytest.skip("WindowsCredentialStore requires win32")
    store = _credential_store()
    assert store is not None
    ref = make_credential_ref("proxy", "assembly-test")
    store.store_credential(ref, SecretValue("s3cret"))
    try:
        resolver = _credential_resolver(store)
        assert resolver is not None
        assert resolver(ref) == "s3cret"
    finally:
        store.delete_credential(ref)

    # The same best-effort channel: a broken vault yields no resolver,
    # so providers report MISSING_CREDENTIAL instead of failing startup.
    monkeypatch.setattr(credentials_windows, "WindowsCredentialStore", _BrokenVault)
    assert _credential_resolver() is None
