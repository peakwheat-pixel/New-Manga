"""FEA-09 source-read grant access port (C-16 §0/§2).

The orchestration consumes resolved grants through this port only. The
production implementation (Phase C) registers and verifies the Host-minted,
HMAC-signed source-read grants; tests inject an in-memory fake backed by the
same strict file verification rules. The orchestrator never receives paths
from UI/receipt payloads (C-16 §7.5).
"""

from __future__ import annotations

from typing import Protocol

from application.importing.referenced.model import ResolvedSourceRead


class SourceReadAccess(Protocol):
    """Resolve/verify/revoke surface the runtime and planner depend on."""

    def resolve(self, grant_id: str) -> ResolvedSourceRead:
        """Return the grant's resolved view or raise ``SourceImportError``.

        Verifies signature/session/operation/expiry/generation/scope and
        that every granted path still resolves inside the authorized roots
        (the Core side of ``VerifySourceRead``, C-16 §0).
        """
        ...

    def verify_before_commit(self, grant_id: str) -> None:
        """Strong re-verification right before each page transaction
        (C-06 v1.1 constraint 11: revocation/generation/expiry/identity)."""
        ...

    def revoke_all_for_session(self) -> int:
        """Invalidate every grant bound to the current host session
        (Core EOF/transport failure → all grants die, C-15 §6.6)."""
        ...
