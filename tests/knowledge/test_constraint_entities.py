"""Constraint entity contract: fields, scope validation, revision trail
(D03 §12~14, TASK-002 §2.1)."""

from __future__ import annotations

import pytest

import knowledge_helpers  # noqa: F401
from domain.constraints.entities import (
    ConstraintKind,
    ConstraintScope,
    ConstraintStatus,
    TranslationConstraint,
    normalize_term,
)

from knowledge_helpers import make_constraint


def test_normalized_key_folds_case_width_and_whitespace() -> None:
    assert normalize_term("  Ｍａｇｉｃ   Sword\n") == "magic sword"
    assert normalize_term("進撃の巨人") == "進撃の巨人"


def test_scope_validation_rejects_mismatched_scope_ids() -> None:
    with pytest.raises(ValueError):
        TranslationConstraint(
            constraint_id="c1",
            scope_type=ConstraintScope.GLOBAL,
            constraint_kind=ConstraintKind.TERMINOLOGY,
            source_term="巨人",
            scope_id="book-1",
        )
    with pytest.raises(ValueError):
        TranslationConstraint(
            constraint_id="c2",
            scope_type=ConstraintScope.BOOK,
            constraint_kind=ConstraintKind.TERMINOLOGY,
            source_term="巨人",
        )


def test_new_constraint_requires_attached_revision() -> None:
    """TASK-002 §2.1: current_revision_id must be non-empty when the
    creation transaction commits; require_current_revision_id enforces it."""

    bare = TranslationConstraint(
        constraint_id="c3",
        scope_type=ConstraintScope.GLOBAL,
        constraint_kind=ConstraintKind.TERMINOLOGY,
        source_term="立体機動",
        target_term="立体机动",
    )
    assert bare.current_revision_id is None
    with pytest.raises(ValueError):
        bare.require_current_revision_id()
    bare.attach_revision(bare.record_revision("create"))
    assert bare.require_current_revision_id() == "c3#rev1"


def test_every_state_change_records_a_revision() -> None:
    """D03 §13 triggers: 译法修改、锁定、启用/禁用、层级迁移."""

    constraint = make_constraint("c4", source_term="エレン", target_term="艾伦")
    first = constraint.current_revision_id

    constraint.change_target_term("艾伦·耶格尔", change_reason="manual fix")
    assert constraint.current_revision_id == "c4#rev2"

    constraint.set_locked(True)
    constraint.set_locked(False)
    constraint.disable()
    constraint.activate()
    constraint.mark_pending()
    constraint.reject()
    constraint.migrate_scope(ConstraintScope.BOOK, "book-1")

    assert constraint.current_revision_id == "c4#rev9"
    assert first != constraint.current_revision_id
    assert constraint.status is ConstraintStatus.REJECTED
    assert constraint.normalized_key == "エレン"  # rejected key kept (D03 §12.5)


def test_revisions_carry_snapshot_reason_and_monotonic_numbers() -> None:
    constraint = make_constraint("c5", source_term="ミカサ", target_term="三笠")
    revision = constraint.change_target_term("米卡莎", change_reason="proofread")
    assert revision.constraint_id == "c5"
    assert revision.revision_no == 2
    assert revision.change_reason == "proofread"
    assert revision.snapshot["target_term"] == "米卡莎"
    assert revision.snapshot["normalized_key"] == "ミカサ"


def test_rejected_constraint_keeps_normalized_key_for_suppression() -> None:
    constraint = make_constraint(
        "c6",
        source_term="壁",
        target_term="墙",
        status=ConstraintStatus.ACTIVE,
    )
    constraint.reject()
    assert constraint.status is ConstraintStatus.REJECTED
    assert constraint.normalized_key == "壁"


def test_do_not_translate_carries_no_target_term() -> None:
    constraint = make_constraint(
        "c7",
        source_term="Sasha",
        kind=ConstraintKind.DO_NOT_TRANSLATE,
    )
    assert constraint.target_term == ""
    with pytest.raises(ValueError):
        constraint.change_target_term("萨莎", change_reason="invalid")
