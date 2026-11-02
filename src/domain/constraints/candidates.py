"""Automatic term-extraction candidate rules (D03 §12.5, D06 §9).

High-confidence proposals activate, low-confidence ones stay pending, and
existing manual work always wins (D06 §9.3): locked constraints are never
touched and manual active values defer new auto proposals. A normalized key
already rejected (or disabled) by the user suppresses re-creation of the
same candidate (AC-CONSTRAINT-004).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from domain.constraints.entities import (
    ConstraintKind,
    ConstraintOrigin,
    ConstraintStatus,
    TranslationConstraint,
    normalize_term,
)

#: Threshold separating 高置信度 → Active from 低置信度 → Pending (D03 §12.5).
#: The approved spec fixes the states but not a numeric value; 0.90 is the
#: shipped default and is overridable by callers.
AUTO_ACTIVE_CONFIDENCE = 0.90


class CandidateDecisionKind(str, Enum):
    CREATED_ACTIVE = "created_active"
    CREATED_PENDING = "created_pending"
    PROMOTED_ACTIVE = "promoted_active"
    UPDATED_EXISTING = "updated_existing"
    DEFERRED_TO_LOCKED = "deferred_to_locked"
    DEFERRED_TO_MANUAL = "deferred_to_manual"
    SUPPRESSED_REJECTED = "suppressed_rejected"
    SUPPRESSED_DISABLED = "suppressed_disabled"
    IGNORED = "ignored"


@dataclass(frozen=True)
class AutoTermProposal:
    """One auto-extracted term suggestion (D06 §9.1 inputs)."""

    source_term: str
    target_term: str
    category: str = "自定义"
    confidence: float = 0.0
    constraint_kind: ConstraintKind = ConstraintKind.TERMINOLOGY
    note: str = ""

    @property
    def normalized_key(self) -> str:
        return normalize_term(self.source_term)


@dataclass(frozen=True)
class CandidateDecision:
    kind: CandidateDecisionKind
    constraint: TranslationConstraint | None
    existing: TranslationConstraint | None


def propose_auto_constraint(
    existing: TranslationConstraint | None,
    proposal: AutoTermProposal,
    *,
    constraint_id: str,
    scope_type,
    scope_id: str | None = None,
) -> CandidateDecision:
    """Decide what (if anything) the extractor may create or update.

    ``existing`` is the constraint already stored for the same normalized
    key (any scope); ``None`` means the key is unseen.
    """

    if not 0.0 <= proposal.confidence <= 1.0:
        raise ValueError("proposal confidence must be within [0, 1]")

    if existing is not None:
        if normalize_term(existing.source_term) != proposal.normalized_key:
            raise ValueError("existing constraint does not match the proposed key")
        if existing.locked:
            return CandidateDecision(CandidateDecisionKind.DEFERRED_TO_LOCKED, None, existing)
        if existing.status is ConstraintStatus.REJECTED:
            return CandidateDecision(CandidateDecisionKind.SUPPRESSED_REJECTED, None, existing)
        if existing.status is ConstraintStatus.DISABLED:
            return CandidateDecision(CandidateDecisionKind.SUPPRESSED_DISABLED, None, existing)
        if existing.origin is ConstraintOrigin.MANUAL and existing.status is ConstraintStatus.ACTIVE:
            return CandidateDecision(CandidateDecisionKind.DEFERRED_TO_MANUAL, None, existing)

        confident = proposal.confidence >= AUTO_ACTIVE_CONFIDENCE
        if existing.status is ConstraintStatus.ACTIVE:
            # Auto re-extraction may refresh the effective auto value (D03 §13
            # 自动更新正式生效值) but only without losing confidence.
            if proposal.target_term != existing.target_term and proposal.confidence >= (existing.confidence or 0.0):
                existing.change_target_term(
                    proposal.target_term,
                    change_reason="auto re-extraction",
                )
                return CandidateDecision(CandidateDecisionKind.UPDATED_EXISTING, existing, existing)
            return CandidateDecision(CandidateDecisionKind.IGNORED, existing, existing)
        # pending auto candidate
        if confident:
            existing.confidence = proposal.confidence
            if proposal.target_term != existing.target_term:
                existing.change_target_term(
                    proposal.target_term,
                    change_reason="auto re-extraction",
                )
            existing.activate()
            return CandidateDecision(CandidateDecisionKind.PROMOTED_ACTIVE, existing, existing)
        return CandidateDecision(CandidateDecisionKind.IGNORED, existing, existing)

    candidate = TranslationConstraint(
        constraint_id=constraint_id,
        scope_type=scope_type,
        constraint_kind=proposal.constraint_kind,
        source_term=proposal.source_term,
        target_term=proposal.target_term,
        scope_id=scope_id,
        category=proposal.category,
        note=proposal.note,
        origin=ConstraintOrigin.AUTO,
        confidence=proposal.confidence,
        status=ConstraintStatus.ACTIVE
        if proposal.confidence >= AUTO_ACTIVE_CONFIDENCE
        else ConstraintStatus.PENDING,
    )
    candidate.attach_revision(candidate.record_revision("auto term extraction"))
    kind = (
        CandidateDecisionKind.CREATED_ACTIVE
        if candidate.status is ConstraintStatus.ACTIVE
        else CandidateDecisionKind.CREATED_PENDING
    )
    return CandidateDecision(kind, candidate, None)
