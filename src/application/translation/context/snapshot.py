"""Effective constraint snapshot freeze (D06 §10, TASK-002 §3.2).

准备阶段 merges the effective chapter/book/global constraints into a
read-only snapshot; every Translation Step of the Run then reads that
frozen snapshot. Terms edited while a Run is in flight only reach the
*next* Run — the frozen snapshot is immutable, so mid-run edits cannot
leak into already-frozen values.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping, Sequence

from domain.constraints.entities import ConstraintKind
from domain.constraints.merge import EffectiveConstraint, merge_constraints


@dataclass(frozen=True)
class EffectiveConstraintSnapshot:
    """Frozen, read-only view of the constraints governing one Run."""

    run_id: str
    frozen_at: str
    _terms: Mapping[str, EffectiveConstraint] = field(repr=False)
    _do_not_translate: frozenset[str] = field(repr=False)

    def lookup(self, normalized_key: str) -> EffectiveConstraint | None:
        return self._terms.get(normalized_key)

    def terminology(self) -> Mapping[str, EffectiveConstraint]:
        return self._terms

    def do_not_translate(self) -> frozenset[str]:
        return self._do_not_translate

    def provenance(self) -> tuple[dict, ...]:
        """Per-term provenance: which constraint revision supplied the value."""

        return tuple(
            {
                "normalized_key": key,
                "constraint_id": value.constraint_id,
                "revision_id": value.revision_id,
                "scope_type": value.scope_type.value,
                "locked": value.locked,
            }
            for key, value in self._terms.items()
        )


def freeze_constraints(
    constraints: Sequence,
    *,
    run_id: str,
    frozen_at: str,
    book_id: str | None = None,
    chapter_id: str | None = None,
) -> EffectiveConstraintSnapshot:
    merged = merge_constraints(constraints, book_id=book_id, chapter_id=chapter_id)
    terms = {k: v for k, v in merged.items() if v.constraint_kind is ConstraintKind.TERMINOLOGY}
    do_not_translate = frozenset(
        k for k, v in merged.items() if v.constraint_kind is ConstraintKind.DO_NOT_TRANSLATE
    )
    return EffectiveConstraintSnapshot(
        run_id=run_id,
        frozen_at=frozen_at,
        _terms=MappingProxyType(terms),
        _do_not_translate=do_not_translate,
    )
