"""Constraint freeze semantics (D06 §10, TASK-002 §3.2): a Run keeps its
frozen snapshot while terms change mid-run; new values reach the next Run
only."""

from __future__ import annotations

import knowledge_helpers  # noqa: F401
from application.translation.context.snapshot import freeze_constraints
from domain.constraints.entities import (
    ConstraintKind,
    ConstraintScope,
    ConstraintStatus,
)

from knowledge_helpers import make_constraint


def build_run_snapshot():
    constraints = [
        make_constraint("g1", source_term="巨人", target_term="G值"),
        make_constraint("ch1", source_term="巨人", target_term="C值",
                        scope_type=ConstraintScope.CHAPTER, scope_id="ch"),
        make_constraint("g2", source_term="Sasha", kind=ConstraintKind.DO_NOT_TRANSLATE),
        make_constraint("g3", source_term="壁", target_term="待定",
                        status=ConstraintStatus.PENDING),
    ]
    return freeze_constraints(constraints, run_id="run-1", frozen_at="t0",
                              book_id="bk", chapter_id="ch")


def test_snapshot_resolves_merged_values() -> None:
    snapshot = build_run_snapshot()
    winner = snapshot.lookup("巨人")
    assert winner.target_term == "C值"  # chapter beats global
    assert snapshot.do_not_translate() == frozenset({"sasha"})
    assert snapshot.lookup("壁") is None  # pending never freezes


def test_snapshot_is_read_only() -> None:
    snapshot = build_run_snapshot()
    terms = snapshot.terminology()
    import pytest

    with pytest.raises(TypeError):
        terms["巨人"] = None  # type: ignore[index]


def test_midrun_term_edit_does_not_touch_frozen_values() -> None:
    """Run 中改术语不影响已冻结值 (TASK-010 AC / D06 §10.2)."""

    ch = make_constraint("ch1", source_term="巨人", target_term="C值",
                         scope_type=ConstraintScope.CHAPTER, scope_id="ch")
    snapshot = freeze_constraints([ch], run_id="run-1", frozen_at="t0",
                                  book_id="bk", chapter_id="ch")
    assert snapshot.lookup("巨人").target_term == "C值"

    # user edits the term while the Run is running
    ch.change_target_term("改后值", change_reason="mid-run edit")
    ch.disable()

    # the frozen snapshot still serves the original effective value
    assert snapshot.lookup("巨人").target_term == "C值"
    assert snapshot.lookup("巨人").revision_id == "ch1#rev1"
    assert snapshot.provenance()[0]["revision_id"] == "ch1#rev1"


def test_next_run_freezes_new_values() -> None:
    ch = make_constraint("ch1", source_term="巨人", target_term="C值",
                         scope_type=ConstraintScope.CHAPTER, scope_id="ch")
    frozen_first = freeze_constraints([ch], run_id="run-1", frozen_at="t0",
                                      book_id="bk", chapter_id="ch")
    ch.change_target_term("改后值", change_reason="user edit")
    frozen_second = freeze_constraints([ch], run_id="run-2", frozen_at="t1",
                                       book_id="bk", chapter_id="ch")
    assert frozen_first.lookup("巨人").target_term == "C值"
    assert frozen_second.lookup("巨人").target_term == "改后值"
    assert frozen_second.run_id == "run-2"
