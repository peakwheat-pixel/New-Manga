"""FEA-11 source-sync typed errors (C-17 §8 local closed set).

Reuses the existing SourceImportError envelope shape so the wire projection
(``code``/``category``/``retryable``) rides the M2-C1 error envelope without a
second taxonomy. Only the C-17 additions and the codes this face actually
raises are listed here; the frozen category/retryable projection follows
C-17 §8 verbatim.
"""

from __future__ import annotations

from application.importing.referenced.errors import SourceImportError

#: C-17 §8 projection: code -> (category, retryable). Codes marked "既有" in
#: the contract keep their existing projection; the four C-17 additions are
#: SOURCE_SYNC_STATE_CONFLICT / SOURCE_SYNC_UNSTABLE / SOURCE_SYNC_CANCELLED /
#: SOURCE_SYNC_STORAGE_FAILED.
SOURCE_SYNC_ERROR_RULES: dict[str, tuple[str, bool]] = {
    "INVALID_REQUEST": ("validation", False),
    "CORE_CAPABILITY_MISSING": ("protocol", False),
    "PROTOCOL_VERSION_UNSUPPORTED": ("protocol", False),
    "HOST_ONLY_REQUIRED": ("validation", False),
    "HOST_SESSION_INVALID": ("conflict", False),
    "CORE_SESSION_MISMATCH": ("conflict", False),
    "SOURCE_PLAN_STALE": ("conflict", True),
    "SOURCE_OPERATION_CONFLICT": ("conflict", False),
    "SOURCE_OPERATION_NOT_FOUND": ("not_found", False),
    "SOURCE_ACCESS_DENIED": ("authorization", False),
    "SOURCE_GRANT_EXPIRED": ("authorization", True),
    "SOURCE_GRANT_REVOKED": ("authorization", False),
    "SOURCE_REGISTRY_UNAVAILABLE": ("internal", True),
    "SOURCE_REGISTRY_BUSY": ("internal", True),
    "SOURCE_PASSWORD_REQUIRED": ("validation", False),
    "SOURCE_PASSWORD_INVALID": ("validation", False),
    "SOURCE_FORMAT_UNSUPPORTED": ("validation", False),
    "SOURCE_ENTRY_MISSING": ("not_found", False),
    "SOURCE_BUDGET_EXCEEDED": ("validation", False),
    "SOURCE_PROJECT_MISMATCH": ("validation", False),
    "FILE_IDENTITY_CHANGED": ("conflict", True),
    "REF_SIGNATURE_INVALID": ("validation", False),
    "STALE_BASE_REVISION": ("conflict", True),
    "SOURCE_SYNC_STATE_CONFLICT": ("conflict", False),
    "SOURCE_SYNC_UNSTABLE": ("conflict", True),
    "SOURCE_SYNC_CANCELLED": ("conflict", False),
    "SOURCE_SYNC_STORAGE_FAILED": ("internal", True),
    "SOURCE_MIGRATION_FAILED": ("internal", False),
}


class SourceSyncError(SourceImportError):
    """A C-17 source-sync failure carrying the frozen §8 projection."""

    def __init__(self, code: str, message: str, *, details: dict | None = None) -> None:
        super().__init__(code, message, details)
        category, retryable = SOURCE_SYNC_ERROR_RULES.get(code, ("validation", False))
        # The C-17 §8 projection replaces the C-16 default for this face.
        self.category = category
        self.retryable = retryable


def stale(cause: str, message: str = "source sync plan is stale") -> SourceSyncError:
    """SOURCE_PLAN_STALE with a frozen StaleReason cause detail."""
    return SourceSyncError(
        "SOURCE_PLAN_STALE", message, details={"cause": cause}
    )
