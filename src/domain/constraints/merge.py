"""Constraint merge order (D06 §11) — chapter > book > global, and within
one layer 人工锁定 > 人工值 > 自动 Active (D03 §12.6). ``pending``,
``rejected`` and ``disabled`` candidates are never formal constraints.

Pure domain: operates on :class:`TranslationConstraint` values, returns a
deterministic mapping keyed by ``normalized_key``.
"""

from __future__ import annotations

from dataclasses import dataclass

from domain.constraints.entities import (
    ConstraintKind,
    ConstraintOrigin,
    ConstraintScope,
    ConstraintStatus,
    TranslationConstraint,
)

_SCOPE_PRIORITY = {
    ConstraintScope.CHAPTER: 3,
    ConstraintScope.BOOK: 2,
    ConstraintScope.GLOBAL: 1,
}


@dataclass(frozen=True)
class EffectiveConstraint:
    """Read-only projection of a winning constraint for a given scope."""

    constraint_id: str
    revision_id: str
    scope_type: ConstraintScope
    constraint_kind: ConstraintKind
    category: str
    source_term: str
    target_term: str
    normalized_key: str
    note: str
    origin: ConstraintOrigin
    locked: bool


def _origin_rank(constraint: TranslationConstraint) -> int:
    if constraint.locked:
        return 3
    if constraint.origin is ConstraintOrigin.MANUAL:
        return 2
    return 1


def _applies_to(constraint: TranslationConstraint, *, book_id: str | None, chapter_id: str | None) -> bool:
    if constraint.scope_type is ConstraintScope.GLOBAL:
        return True
    if constraint.scope_type is ConstraintScope.BOOK:
        return book_id is not None and constraint.scope_id == book_id
    return chapter_id is not None and constraint.scope_id == chapter_id


def _winner_key(constraint: TranslationConstraint) -> tuple:
    """Total order for ties at the same priority: newest update wins, then
    the larger constraint_id, so merging is deterministic."""

    return (
        constraint.updated_at,
        constraint.constraint_id,
    )


def merge_constraints(
    constraints,
    *,
    book_id: str | None = None,
    chapter_id: str | None = None,
) -> dict[str, EffectiveConstraint]:
    """Resolve one effective value per normalized term for the given
    translation context (D06 §11). Constraints whose current revision was
    never attached are rejected first (TASK-002 §2.1)."""

    effective: dict[str, EffectiveConstraint] = {}
    best_rank: dict[str, tuple[int, int, tuple]] = {}
    for constraint in constraints:
        constraint.require_current_revision_id()
        if constraint.status is not ConstraintStatus.ACTIVE:
            continue
        if not _applies_to(constraint, book_id=book_id, chapter_id=chapter_id):
            continue
        rank = (
            _SCOPE_PRIORITY[constraint.scope_type],
            _origin_rank(constraint),
            _winner_key(constraint),
        )
        previous = best_rank.get(constraint.normalized_key)
        if previous is not None and rank <= previous:
            continue
        best_rank[constraint.normalized_key] = rank
        effective[constraint.normalized_key] = EffectiveConstraint(
            constraint_id=constraint.constraint_id,
            revision_id=constraint.current_revision_id,
            scope_type=constraint.scope_type,
            constraint_kind=constraint.constraint_kind,
            category=constraint.category,
            source_term=constraint.source_term,
            target_term=constraint.target_term,
            normalized_key=constraint.normalized_key,
            note=constraint.note,
            origin=constraint.origin,
            locked=constraint.locked,
        )
    return effective
