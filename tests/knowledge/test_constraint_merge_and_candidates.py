"""Merge order (D06 §11, AC-CONSTRAINT-001/002) and candidate rules
(D03 §12.5, AC-CONSTRAINT-002/003/004)."""

from __future__ import annotations

import pytest

import knowledge_helpers  # noqa: F401
from domain.constraints.candidates import (
    AUTO_ACTIVE_CONFIDENCE,
    AutoTermProposal,
    CandidateDecisionKind,
    propose_auto_constraint,
)
from domain.constraints.entities import (
    ConstraintOrigin,
    ConstraintScope,
    ConstraintStatus,
)
from domain.constraints.merge import merge_constraints

from knowledge_helpers import make_constraint


# ----------------------------------------------------------------------
# AC-CONSTRAINT-001: chapter > book > global
# ----------------------------------------------------------------------


def test_more_specific_scope_wins() -> None:
    constraints = [
        make_constraint("g1", source_term="巨人", target_term="GlobalA"),
        make_constraint("b1", source_term="巨人", target_term="BookB", scope_type=ConstraintScope.BOOK, scope_id="bk"),
        make_constraint("ch1", source_term="巨人", target_term="ChapterC", scope_type=ConstraintScope.CHAPTER, scope_id="ch"),
    ]
    effective = merge_constraints(constraints, book_id="bk", chapter_id="ch")
    assert effective["巨人"].target_term == "ChapterC"
    assert effective["巨人"].constraint_id == "ch1"


def test_other_scopes_do_not_leak_into_context() -> None:
    constraints = [
        make_constraint("b2", source_term="壁", target_term="别的作品", scope_type=ConstraintScope.BOOK, scope_id="other-book"),
        make_constraint("ch2", source_term="壁", target_term="别的章节", scope_type=ConstraintScope.CHAPTER, scope_id="other-ch"),
    ]
    effective = merge_constraints(constraints, book_id="bk", chapter_id="ch")
    assert effective == {}


def test_global_applies_when_only_book_context_given() -> None:
    constraints = [make_constraint("g2", source_term="壁", target_term="墙")]
    effective = merge_constraints(constraints, book_id="bk", chapter_id=None)
    assert effective["壁"].target_term == "墙"


# ----------------------------------------------------------------------
# same-layer priority: locked > manual > auto (D03 §12.6)
# ----------------------------------------------------------------------


def test_locked_beats_manual_and_auto_in_same_layer() -> None:
    constraints = [
        make_constraint(
            "auto1", source_term="エレン", target_term="自动值", origin=ConstraintOrigin.AUTO,
            confidence=0.95, scope_type=ConstraintScope.CHAPTER, scope_id="ch",
        ),
        make_constraint(
            "man1", source_term="エレン", target_term="人工值", origin=ConstraintOrigin.MANUAL,
            scope_type=ConstraintScope.CHAPTER, scope_id="ch",
        ),
        make_constraint(
            "lock1", source_term="エレン", target_term="锁定值", origin=ConstraintOrigin.MANUAL,
            locked=True, scope_type=ConstraintScope.CHAPTER, scope_id="ch",
        ),
    ]
    effective = merge_constraints(constraints, book_id="bk", chapter_id="ch")
    assert effective["エレン"].target_term == "锁定值"


def test_manual_beats_auto_in_same_layer() -> None:
    constraints = [
        make_constraint(
            "auto1", source_term="ミカサ", target_term="自动值", origin=ConstraintOrigin.AUTO,
            confidence=0.99, scope_type=ConstraintScope.CHAPTER, scope_id="ch",
        ),
        make_constraint(
            "man1", source_term="ミカサ", target_term="人工值", origin=ConstraintOrigin.MANUAL,
            scope_type=ConstraintScope.CHAPTER, scope_id="ch",
        ),
    ]
    effective = merge_constraints(constraints, book_id="bk", chapter_id="ch")
    assert effective["ミカサ"].target_term == "人工值"


def test_pending_rejected_disabled_are_never_formal_constraints() -> None:
    constraints = [
        make_constraint("p1", source_term="壁", target_term="待定", status=ConstraintStatus.PENDING),
        make_constraint("r1", source_term="壁", target_term="被拒", status=ConstraintStatus.REJECTED),
        make_constraint("d1", source_term="壁", target_term="停用", status=ConstraintStatus.DISABLED),
    ]
    assert merge_constraints(constraints, book_id="bk", chapter_id="ch") == {}


def test_merge_requires_attached_revision() -> None:
    from domain.constraints.entities import TranslationConstraint

    bare = TranslationConstraint(
        constraint_id="x", scope_type=ConstraintScope.GLOBAL,
        constraint_kind="terminology", source_term="无版本",
    )
    with pytest.raises(ValueError):
        merge_constraints([bare])


# ----------------------------------------------------------------------
# candidate lifecycle (AC-CONSTRAINT-002/003/004)
# ----------------------------------------------------------------------


def test_high_confidence_auto_candidate_activates_low_confidence_pends() -> None:
    high = propose_auto_constraint(
        None, AutoTermProposal("エレン", "艾伦", confidence=0.95),
        constraint_id="c-high", scope_type=ConstraintScope.BOOK, scope_id="bk",
    )
    low = propose_auto_constraint(
        None, AutoTermProposal("ミカサ", "三笠", confidence=0.5),
        constraint_id="c-low", scope_type=ConstraintScope.BOOK, scope_id="bk",
    )
    assert high.kind is CandidateDecisionKind.CREATED_ACTIVE
    assert high.constraint.status is ConstraintStatus.ACTIVE
    assert high.constraint.origin is ConstraintOrigin.AUTO
    assert low.kind is CandidateDecisionKind.CREATED_PENDING
    assert low.constraint.status is ConstraintStatus.PENDING


def test_auto_extraction_never_overrides_locked_constraint() -> None:
    """AC-CONSTRAINT-002."""

    locked = make_constraint(
        "locked", source_term="エレン", target_term="人工锁定",
        scope_type=ConstraintScope.BOOK, scope_id="bk", locked=True,
    )
    decision = propose_auto_constraint(
        locked, AutoTermProposal("エレン", "另一个译法", confidence=0.99),
        constraint_id="new", scope_type=ConstraintScope.BOOK, scope_id="bk",
    )
    assert decision.kind is CandidateDecisionKind.DEFERRED_TO_LOCKED
    assert decision.constraint is None
    assert locked.target_term == "人工锁定"
    assert locked.current_revision_id == "locked#rev1"  # untouched


def test_rejected_key_is_not_recommended_again() -> None:
    """AC-CONSTRAINT-004: same normalized key, different surface form."""

    rejected = make_constraint(
        "rej", source_term="壁", target_term="墙",
        scope_type=ConstraintScope.BOOK, scope_id="bk",
    )
    rejected.reject()
    decision = propose_auto_constraint(
        rejected, AutoTermProposal("壁 ", "墙", confidence=0.99),
        constraint_id="new", scope_type=ConstraintScope.BOOK, scope_id="bk",
    )
    assert decision.kind is CandidateDecisionKind.SUPPRESSED_REJECTED
    assert decision.constraint is None


def test_disabled_key_is_not_recreated() -> None:
    disabled = make_constraint(
        "dis", source_term="壁", target_term="墙",
        scope_type=ConstraintScope.BOOK, scope_id="bk",
    )
    disabled.disable()
    decision = propose_auto_constraint(
        disabled, AutoTermProposal("壁", "墙", confidence=0.99),
        constraint_id="new", scope_type=ConstraintScope.BOOK, scope_id="bk",
    )
    assert decision.kind is CandidateDecisionKind.SUPPRESSED_DISABLED


def test_auto_proposal_defers_to_manual_active_value() -> None:
    manual = make_constraint(
        "man", source_term="巨人", target_term="人工译法",
        scope_type=ConstraintScope.BOOK, scope_id="bk",
    )
    decision = propose_auto_constraint(
        manual, AutoTermProposal("巨人", "自动译法", confidence=0.99),
        constraint_id="new", scope_type=ConstraintScope.BOOK, scope_id="bk",
    )
    assert decision.kind is CandidateDecisionKind.DEFERRED_TO_MANUAL
    assert manual.target_term == "人工译法"


def test_auto_reextraction_refreshes_auto_value_without_losing_confidence() -> None:
    auto = make_constraint(
        "auto", source_term="巨人", target_term="旧自动值", origin=ConstraintOrigin.AUTO,
        confidence=0.8, scope_type=ConstraintScope.BOOK, scope_id="bk",
    )
    decision = propose_auto_constraint(
        auto, AutoTermProposal("巨人", "新自动值", confidence=0.9),
        constraint_id="new", scope_type=ConstraintScope.BOOK, scope_id="bk",
    )
    assert decision.kind is CandidateDecisionKind.UPDATED_EXISTING
    assert auto.target_term == "新自动值"
    assert auto.current_revision_id == "auto#rev2"


def test_pending_candidate_promotes_when_confidence_crosses_threshold() -> None:
    pending = make_constraint(
        "pend", source_term="壁", target_term="墙", origin=ConstraintOrigin.AUTO,
        confidence=0.4, status=ConstraintStatus.PENDING,
        scope_type=ConstraintScope.BOOK, scope_id="bk",
    )
    decision = propose_auto_constraint(
        pending, AutoTermProposal("壁", "墙", confidence=AUTO_ACTIVE_CONFIDENCE),
        constraint_id="new", scope_type=ConstraintScope.BOOK, scope_id="bk",
    )
    assert decision.kind is CandidateDecisionKind.PROMOTED_ACTIVE
    assert pending.status is ConstraintStatus.ACTIVE
    assert pending.current_revision_id == "pend#rev2"


def test_proposal_key_must_match_existing_constraint() -> None:
    existing = make_constraint(
        "man", source_term="巨人", target_term="人工译法",
        scope_type=ConstraintScope.BOOK, scope_id="bk",
    )
    with pytest.raises(ValueError):
        propose_auto_constraint(
            existing, AutoTermProposal("壁", "墙", confidence=0.9),
            constraint_id="new", scope_type=ConstraintScope.BOOK, scope_id="bk",
        )
