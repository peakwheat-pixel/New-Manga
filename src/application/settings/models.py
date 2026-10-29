"""Setting override layers, effective values and run snapshots
(D03 §28, D06 §49, D08 AC-SET-001).

Resolution order (most specific wins):

    task (current-run temporary) > chapter > book > global

Every resolved value records where it came from so the UI can display
the effective source (AC-SET-001). Task-scope overrides exist only
inside a PipelineRun settings snapshot; they are not persisted as user
configuration (D03 §28).
"""

from __future__ import annotations

from dataclasses import dataclass

SCOPE_GLOBAL = "global"
SCOPE_BOOK = "book"
SCOPE_CHAPTER = "chapter"
SCOPE_TASK = "task"
#: Most-specific-first order used by the resolver.
SCOPE_PRECEDENCE: tuple[str, ...] = (SCOPE_TASK, SCOPE_CHAPTER, SCOPE_BOOK, SCOPE_GLOBAL)


@dataclass(frozen=True)
class SettingOverride:
    """One key/value at one scope (D03 §28 SettingOverride)."""

    scope_type: str
    scope_id: str | None
    key: str
    value: str

    def __post_init__(self) -> None:
        if self.scope_type not in SCOPE_PRECEDENCE:
            raise ValueError(f"unknown scope type: {self.scope_type!r}")
        if self.scope_type in (SCOPE_BOOK, SCOPE_CHAPTER) and not self.scope_id:
            raise ValueError(f"scope {self.scope_type} requires scope_id")
        if self.scope_type in (SCOPE_GLOBAL, SCOPE_TASK) and self.scope_id:
            raise ValueError(f"scope {self.scope_type} must not carry scope_id")
        if not self.key:
            raise ValueError("setting key must not be empty")


@dataclass(frozen=True)
class EffectiveSetting:
    """A resolved value plus the scope that produced it (AC-SET-001)."""

    key: str
    value: str
    source_scope_type: str
    source_scope_id: str | None = None

    @property
    def source_label(self) -> str:
        """Human-readable source for UI display, e.g. ``book:<id>``."""
        if self.source_scope_id:
            return f"{self.source_scope_type}:{self.source_scope_id}"
        return self.source_scope_type
