"""Credential vault contract tests, run against both the in-memory fake
and the real Windows Credential Manager (AC-SEC-003, D07 §69).

The Windows leg writes only throwaway entries under
``NewManga/test/...`` and deletes them in teardown; a failure between
store and delete leaks at most a labeled test credential, never a real
secret.
"""

from __future__ import annotations

import uuid

import pytest

from ports.providers.credentials import SecretValue, make_credential_ref

import helpers
from infrastructure.credentials.windows import (
    CredentialNotFoundError,
    WindowsCredentialStore,
)


def _ref(vault, purpose: str) -> str:
    """Windows vault entries use the throwaway ``test`` kind; the fake
    only accepts the two production kinds, so it reuses ``provider``."""
    if isinstance(vault, helpers.InMemoryCredentialStore):
        return make_credential_ref("provider", f"{purpose}-{uuid.uuid4().hex[:8]}")
    return f"NewManga/test/{purpose}-{uuid.uuid4().hex[:8]}"


@pytest.fixture(params=["memory", "windows"])
def vault(request):
    if request.param == "memory":
        yield helpers.InMemoryCredentialStore()
    else:
        base = WindowsCredentialStore()
        created: list[str] = []

        class _Tracked(WindowsCredentialStore):
            def store_credential(self, ref, secret):  # noqa: D102
                created.append(ref)
                return base.store_credential(ref, secret)

        tracked = _Tracked()
        yield tracked
        for ref in created:
            try:
                base.delete_credential(ref)
            except Exception:
                pass


def test_make_credential_ref_validates_kind_and_name():
    assert make_credential_ref("provider", "p1") == "NewManga/provider/p1"
    assert make_credential_ref("proxy", "px") == "NewManga/proxy/px"
    with pytest.raises(ValueError):
        make_credential_ref("database", "d")
    with pytest.raises(ValueError):
        make_credential_ref("provider", "")


def test_roundtrip_and_missing(vault):
    ref = _ref(vault, "rt")
    secret = SecretValue("sk-test-roundtrip")
    assert not vault.has_credential(ref)
    vault.store_credential(ref, secret)
    assert vault.has_credential(ref)
    assert vault.resolve_credential(ref).reveal() == "sk-test-roundtrip"
    vault.delete_credential(ref)
    assert not vault.has_credential(ref)
    with pytest.raises((KeyError, CredentialNotFoundError)):
        vault.resolve_credential(ref)


def test_update_requires_existing(vault):
    ref = _ref(vault, "up")
    with pytest.raises((KeyError, CredentialNotFoundError)):
        vault.update_credential(ref, SecretValue("x"))
    vault.store_credential(ref, SecretValue("old"))
    vault.update_credential(ref, SecretValue("new"))
    assert vault.resolve_credential(ref).reveal() == "new"
    vault.delete_credential(ref)


def test_store_rejects_duplicate(vault):
    ref = _ref(vault, "dup")
    vault.store_credential(ref, SecretValue("first"))
    with pytest.raises((KeyError, Exception)):
        vault.store_credential(ref, SecretValue("second"))
    vault.delete_credential(ref)


def test_unicode_secret_roundtrip(vault):
    ref = _ref(vault, "uni")
    vault.store_credential(ref, SecretValue("密码-パスワード-🔑"))
    assert vault.resolve_credential(ref).reveal() == "密码-パスワード-🔑"
    vault.delete_credential(ref)
