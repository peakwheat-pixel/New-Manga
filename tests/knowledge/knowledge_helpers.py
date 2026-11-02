"""Shared fakes/factories for knowledge suites. Importable as plain
``knowledge_helpers`` (unique module name: tests/library/helpers.py owns
``helpers`` on sys.path)."""

from __future__ import annotations

import sys
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from domain.constraints.entities import (  # noqa: E402
    ConstraintKind,
    ConstraintOrigin,
    ConstraintScope,
    ConstraintStatus,
    TranslationConstraint,
)
from domain.pages.entities import Page  # noqa: E402
from domain.regions.entities import (  # noqa: E402
    BBox,
    Region,
    RegionGeometry,
    RegionText,
    RegionType,
    SfxPolicy,
)
from application.translation.knowledge.tm import (  # noqa: E402
    TranslationMemoryEntry,
    TranslationMemoryStore,
    TmScope,
    TmStatus,
)


class InMemoryTmStore(TranslationMemoryStore):
    """Structural fake over a dict; ``list_entries`` keeps insertion order."""

    def __init__(self) -> None:
        self.entries: dict[str, TranslationMemoryEntry] = {}

    def add(self, entry: TranslationMemoryEntry) -> None:
        self.entries[entry.tm_id] = entry

    def get(self, tm_id: str):
        return self.entries.get(tm_id)

    def find_by_source_hash(self, source_hash: str, *, scope_type: TmScope, book_id: str | None):
        return [
            e
            for e in self.entries.values()
            if e.source_hash == source_hash
            and e.scope_type is scope_type
            and e.book_id == book_id
        ]

    def list_entries(self, *, scope_type: TmScope, book_id: str | None):
        return [
            e
            for e in self.entries.values()
            if e.scope_type is scope_type and e.book_id == book_id
        ]

    def update(self, entry: TranslationMemoryEntry) -> None:
        self.entries[entry.tm_id] = entry


class FixedClock:
    """Deterministic ISO timestamps: t001, t002, ... in call order."""

    def __init__(self) -> None:
        self.calls = 0

    def __call__(self) -> str:
        self.calls += 1
        return f"2026-09-15T00:00:{self.calls:02d}"


def make_tm_service(start_ids: int = 0):
    from application.translation.knowledge.tm import TranslationMemoryService

    counter = start_ids

    def id_factory() -> str:
        nonlocal counter
        counter += 1
        return f"tm-{counter:03d}"

    return TranslationMemoryService(InMemoryTmStore(), clock=FixedClock(), id_factory=id_factory)


def make_constraint(
    constraint_id: str,
    *,
    source_term: str,
    target_term: str = "",
    scope_type: ConstraintScope = ConstraintScope.GLOBAL,
    scope_id: str | None = None,
    kind: ConstraintKind = ConstraintKind.TERMINOLOGY,
    origin: ConstraintOrigin = ConstraintOrigin.MANUAL,
    status: ConstraintStatus = ConstraintStatus.ACTIVE,
    locked: bool = False,
    confidence: float | None = None,
    updated_at: str | None = None,
) -> TranslationConstraint:
    constraint = TranslationConstraint(
        constraint_id=constraint_id,
        scope_type=scope_type,
        constraint_kind=kind,
        source_term=source_term,
        target_term=target_term,
        scope_id=scope_id,
        origin=origin,
        confidence=confidence,
        status=status,
        locked=locked,
    )
    constraint.attach_revision(constraint.record_revision("fixture creation"))
    if updated_at is not None:
        constraint.updated_at = updated_at
    return constraint


def make_page(page_id: str, sort_order: int) -> Page:
    """Real Page entity with the minimum bookkeeping fields filled."""

    return Page(
        page_id=page_id,
        chapter_id="ch-1",
        source_filename=f"{page_id}.png",
        source_order=sort_order,
        sort_order=sort_order,
        source_hash=f"hash-{page_id}",
        source_size_bytes=10,
        width=800,
        height=1200,
        managed_original_ref=f"managed/{page_id}",
    )


def make_region(
    region_id: str,
    reading_order: int,
    *,
    ocr_text: str = "",
    region_type: RegionType = RegionType.SPEECH,
    sfx_policy: SfxPolicy = SfxPolicy.SKIP,
    translation_locked: bool = False,
) -> Region:
    region = Region(
        region_id=region_id,
        page_id="unused",
        region_type=region_type,
        reading_order=reading_order,
        geometry=RegionGeometry(bbox=BBox(0, 0, 10, 10)),
        text=RegionText(ocr_text=ocr_text),
        sfx_policy=sfx_policy,
        translation_locked=translation_locked,
    )
    region.current_revision_id = f"{region_id}#rev1"
    return region
