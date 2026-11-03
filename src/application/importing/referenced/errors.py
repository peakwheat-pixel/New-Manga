"""FEA-09 referenced-import error envelope (C-16 §6 frozen closed set).

Every error carries the frozen ``code``/``category``/``retryable`` triple;
messages must never contain absolute paths, passwords or internal
structures — ``details`` only carries counts/enums/registry or operation
ids.
"""

from __future__ import annotations

#: Frozen closed set (C-16 §6): code -> (category, retryable).
SOURCE_ERROR_TABLE: dict[str, tuple[str, bool]] = {
    "SOURCE_ACCESS_DENIED": ("authorization", False),
    "SOURCE_GRANT_EXPIRED": ("authorization", True),
    "SOURCE_GRANT_REVOKED": ("authorization", False),
    "SOURCE_REGISTRY_UNAVAILABLE": ("internal", True),
    "SOURCE_REGISTRY_BUSY": ("internal", True),
    "SOURCE_PASSWORD_REQUIRED": ("validation", False),
    "SOURCE_PASSWORD_INVALID": ("validation", False),
    "SOURCE_FORMAT_UNSUPPORTED": ("validation", False),
    "SOURCE_PLAN_STALE": ("conflict", True),
    "SOURCE_ENTRY_MISSING": ("not_found", False),
    "SOURCE_BUDGET_EXCEEDED": ("validation", False),
    "SOURCE_OPERATION_NOT_FOUND": ("not_found", False),
    "SOURCE_OPERATION_CONFLICT": ("conflict", False),
    "SOURCE_IMPORT_BUSY": ("conflict", True),
    "SOURCE_PROJECT_MISMATCH": ("validation", False),
    "FILE_IDENTITY_CHANGED": ("conflict", True),
    "CORE_CAPABILITY_MISSING": ("protocol", False),
    "PROTOCOL_VERSION_UNSUPPORTED": ("protocol", False),
}


class SourceImportError(Exception):
    """Typed referenced-import failure; maps 1:1 onto the C-16 §6 table."""

    def __init__(self, code: str, message: str, details: dict | None = None) -> None:
        category, retryable = SOURCE_ERROR_TABLE.get(code, ("validation", False))
        super().__init__(message)
        self.code = code
        self.category = category
        self.retryable = retryable
        self.details = details or {}

    def envelope(self) -> dict:
        return {
            "code": self.code,
            "category": self.category,
            "message": str(self),
            "retryable": self.retryable,
            "details": self.details,
        }
