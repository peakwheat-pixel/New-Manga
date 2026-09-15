"""Protected credential store contract (D07 §69, D08 AC-SEC-001~003).

Secrets (API keys, proxy passwords) live in the OS credential vault —
Windows Credential Manager on the target platform — never in SQLite,
settings files, logs or exports. The database and profile models keep
only ``credential_ref`` strings produced by :func:`make_credential_ref`.

``SecretValue`` is the only shape a secret takes in memory: its repr and
str are always redacted, and equality compares in constant time. Callers
must ``reveal()`` explicitly at the moment of use.
"""

from __future__ import annotations

import hmac
from typing import Protocol

_REDACTED = "<redacted secret>"

CREDENTIAL_KIND_PROVIDER = "provider"
CREDENTIAL_KIND_PROXY = "proxy"
CREDENTIAL_KINDS = frozenset({CREDENTIAL_KIND_PROVIDER, CREDENTIAL_KIND_PROXY})


def make_credential_ref(kind: str, name: str) -> str:
    """Build the canonical vault target for one secret (D07 §69).

    ``kind`` scopes the purpose (provider API key, proxy password) and
    ``name`` is the user-visible owner (profile name/id). The ref is the
    only string stored in SQLite; the secret itself is not recoverable
    from it.
    """
    if kind not in CREDENTIAL_KINDS:
        raise ValueError(f"unknown credential kind: {kind!r}")
    if not name:
        raise ValueError("credential name must not be empty")
    return f"NewManga/{kind}/{name}"


class SecretValue:
    """A secret whose repr/str can never leak the value (AC-SEC-002).

    Accidental inclusion in f-strings, log records, tracebacks of ``repr``
    calls and error messages prints the redaction marker instead of the
    secret. Use :meth:`reveal` only where the request is actually built.
    """

    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("secret must be a string")
        self._value = value

    def reveal(self) -> str:
        """Return the raw secret; call sites must not log the result."""
        return self._value

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return _REDACTED

    def __str__(self) -> str:
        return _REDACTED

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SecretValue):
            return NotImplemented
        return hmac.compare_digest(self._value, other._value)

    def __hash__(self) -> int:
        # Hashable so secrets can sit in sets/dicts without revealing
        # ordering-sensitive behavior; hash is of the redaction marker.
        return hash(_REDACTED)


class CredentialStore(Protocol):
    """CRUD contract for the protected credential vault."""

    def store_credential(self, ref: str, secret: SecretValue) -> None:
        """Create a new secret; raises if ``ref`` already exists."""
        ...

    def resolve_credential(self, ref: str) -> SecretValue:
        """Return the stored secret; raises ``CredentialNotFound`` if missing."""
        ...

    def update_credential(self, ref: str, secret: SecretValue) -> None:
        """Overwrite an existing secret; raises if ``ref`` is missing."""
        ...

    def delete_credential(self, ref: str) -> None: ...
    def has_credential(self, ref: str) -> bool: ...
