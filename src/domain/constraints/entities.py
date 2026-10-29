"""Translation constraint domain entities (D03 §12~14, TASK-002 §2.1).

Pure domain: no sqlite3/PySide6 imports (TASK-005 architecture guards).
A constraint fixes how one source term must be translated (``terminology``)
or that it must stay untranslated (``do_not_translate``). Candidate
lifecycle follows D03 §12.5: high-confidence auto terms activate,
low-confidence ones stay pending, and a rejected normalized key is kept so
auto extraction stops re-proposing it (AC-CONSTRAINT-003/004).
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from enum import Enum

from domain.books.entities import utc_now

_WHITESPACE = re.compile(r"\s+")


def normalize_term(text: str) -> str:
    """Standardized key (D03 §12.4 ``normalized_key``): NFKC, casefold,
    collapse whitespace. Kept stable for rejected keys (D03 §12.5) and
    reused as the Exact-Match key by TM (D03 §14.5)."""

    normalized = unicodedata.normalize("NFKC", text).strip().casefold()
    return _WHITESPACE.sub(" ", normalized)


class ConstraintScope(str, Enum):
    """D03 §12.1: chapter > book > global (more specific wins)."""

    GLOBAL = "global"
    BOOK = "book"
    CHAPTER = "chapter"


class ConstraintKind(str, Enum):
    """D03 §12.2."""

    TERMINOLOGY = "terminology"
    DO_NOT_TRANSLATE = "do_not_translate"


class ConstraintStatus(str, Enum):
    """D03 §12.4 candidate states; only ``active`` is a formal constraint
    (D06 §11); ``rejected`` keeps its normalized key (D03 §12.5)."""

    ACTIVE = "active"
    PENDING = "pending"
    REJECTED = "rejected"
    DISABLED = "disabled"


class ConstraintOrigin(str, Enum):
    """D03 §12.4 ``origin``."""

    MANUAL = "manual"
    AUTO = "auto"


def _validate_scope(scope_type: ConstraintScope, scope_id: str | None) -> None:
    if scope_type is ConstraintScope.GLOBAL:
        if scope_id:
            raise ValueError("global constraints must not carry a scope_id")
    elif not scope_id:
        raise ValueError(f"{scope_type.value} constraints require a scope_id")


@dataclass(frozen=True)
class ConstraintRevision:
    """Immutable constraint history entry (D03 §13, TASK-002 §2.1/2.2).

    ``UNIQUE(constraint_id, revision_no)`` is enforced by callers: the
    owning constraint hands out monotonic ``revision_no`` values from its
    internal counter, and persistence must re-check the pair in-transaction.
    """

    constraint_revision_id: str
    constraint_id: str
    revision_no: int
    snapshot: dict
    change_reason: str
    is_pinned: bool = False
    source_run_id: str | None = None
    created_at: str = field(default_factory=utc_now)


@dataclass
class TranslationConstraint:
    """One term constraint (D03 §12.4). ``current_revision_id`` must be
    attached inside the creation transaction (TASK-002 §2.1): freshly built
    instances start without one and :meth:`attach_revision` completes them.
    Every state/translation change records a new revision (D03 §13)."""

    constraint_id: str
    scope_type: ConstraintScope
    constraint_kind: ConstraintKind
    source_term: str
    target_term: str = ""
    scope_id: str | None = None
    category: str = "自定义"
    note: str = ""
    normalized_key: str = ""
    origin: ConstraintOrigin = ConstraintOrigin.MANUAL
    confidence: float | None = None
    status: ConstraintStatus = ConstraintStatus.ACTIVE
    locked: bool = False
    current_revision_id: str | None = None
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)
    _revision_count: int = field(default=0, repr=False, compare=False)

    def __post_init__(self) -> None:
        self.scope_type = ConstraintScope(self.scope_type)
        self.constraint_kind = ConstraintKind(self.constraint_kind)
        self.origin = ConstraintOrigin(self.origin)
        self.status = ConstraintStatus(self.status)
        _validate_scope(self.scope_type, self.scope_id)
        if not self.source_term.strip():
            raise ValueError("constraint requires a non-blank source_term")
        if self.confidence is not None and not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be within [0, 1]")
        if not self.normalized_key:
            self.normalized_key = normalize_term(self.source_term)

    # ------------------------------------------------------------------
    # revision bookkeeping (D03 §13, TASK-002 §2.1)
    # ------------------------------------------------------------------

    def record_revision(
        self,
        change_reason: str,
        *,
        source_run_id: str | None = None,
        is_pinned: bool = False,
    ) -> ConstraintRevision:
        """Record a fresh revision from the current state (D03 §13)."""

        self._revision_count += 1
        revision = ConstraintRevision(
            constraint_revision_id=f"{self.constraint_id}#rev{self._revision_count}",
            constraint_id=self.constraint_id,
            revision_no=self._revision_count,
            snapshot=self.snapshot_state(),
            change_reason=change_reason,
            is_pinned=is_pinned,
            source_run_id=source_run_id,
        )
        self.current_revision_id = revision.constraint_revision_id
        self.updated_at = utc_now()
        return revision
        self._revision_count += 1
        revision = ConstraintRevision(
            constraint_revision_id=f"{self.constraint_id}#rev{self._revision_count}",
            constraint_id=self.constraint_id,
            revision_no=self._revision_count,
            snapshot=self.snapshot_state(),
            change_reason=change_reason,
            is_pinned=is_pinned,
            source_run_id=source_run_id,
        )
        self.current_revision_id = revision.constraint_revision_id
        self.updated_at = utc_now()
        return revision

    def attach_revision(self, revision: ConstraintRevision) -> None:
        """Complete a creation transaction (TASK-002 §2.1): the current
        pointer must never stay empty on a committed constraint."""

        if revision.constraint_id != self.constraint_id:
            raise ValueError("revision belongs to a different constraint")
        self.current_revision_id = revision.constraint_revision_id
        self._revision_count = max(self._revision_count, revision.revision_no)

    def require_current_revision_id(self) -> str:
        if self.current_revision_id is None:
            raise ValueError("constraint has no attached revision (TASK-002 §2.1)")
        return self.current_revision_id

    # ------------------------------------------------------------------
    # state changes — each records a revision (D03 §13)
    # ------------------------------------------------------------------

    def change_target_term(
        self,
        target_term: str,
        *,
        change_reason: str,
        source_run_id: str | None = None,
    ) -> ConstraintRevision:
        if self.constraint_kind is ConstraintKind.DO_NOT_TRANSLATE:
            raise ValueError("do_not_translate constraints carry no target term")
        if not target_term.strip():
            raise ValueError("target_term must not be blank")
        self.target_term = target_term
        return self.record_revision(change_reason, source_run_id=source_run_id)

    def set_locked(self, locked: bool, *, source_run_id: str | None = None) -> ConstraintRevision:
        self.locked = bool(locked)
        return self.record_revision(
            "manual lock" if locked else "manual unlock",
            source_run_id=source_run_id,
        )

    def reject(self, *, source_run_id: str | None = None) -> ConstraintRevision:
        """User rejection (D03 §12.5): the normalized key is kept so the
        auto extractor can suppress re-proposals (AC-CONSTRAINT-004)."""

        self.status = ConstraintStatus.REJECTED
        return self.record_revision("user rejected candidate", source_run_id=source_run_id)

    def activate(self, *, source_run_id: str | None = None) -> ConstraintRevision:
        self.status = ConstraintStatus.ACTIVE
        return self.record_revision("constraint activated", source_run_id=source_run_id)

    def mark_pending(self, *, source_run_id: str | None = None) -> ConstraintRevision:
        self.status = ConstraintStatus.PENDING
        return self.record_revision("constraint moved to pending", source_run_id=source_run_id)

    def disable(self, *, source_run_id: str | None = None) -> ConstraintRevision:
        self.status = ConstraintStatus.DISABLED
        return self.record_revision("constraint disabled", source_run_id=source_run_id)

    def migrate_scope(
        self,
        scope_type: ConstraintScope,
        scope_id: str | None,
        *,
        source_run_id: str | None = None,
    ) -> ConstraintRevision:
        """Layer migration is a revision trigger (D03 §13 层级迁移)."""

        new_scope = ConstraintScope(scope_type)
        _validate_scope(new_scope, scope_id)
        self.scope_type = new_scope
        self.scope_id = scope_id
        return self.record_revision(
            f"scope migrated to {self.scope_type.value}",
            source_run_id=source_run_id,
        )

    # ------------------------------------------------------------------
    # snapshot
    # ------------------------------------------------------------------

    def snapshot_state(self) -> dict:
        return {
            "constraint_id": self.constraint_id,
            "scope_type": self.scope_type.value,
            "scope_id": self.scope_id,
            "constraint_kind": self.constraint_kind.value,
            "category": self.category,
            "source_term": self.source_term,
            "target_term": self.target_term,
            "normalized_key": self.normalized_key,
            "note": self.note,
            "origin": self.origin.value,
            "confidence": self.confidence,
            "status": self.status.value,
            "locked": self.locked,
        }
