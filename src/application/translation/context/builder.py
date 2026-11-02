"""Context Builder (D06 §13~17, AC-TRANS-003/004).

Builds translation context bundles: ordered by page sort_order + region
reading_order, bounded by a token budget, and strictly separating the
read-only context scope from the write scope. A Webtoon's temporary tiles
never appear here — one long image stays one logical Page and context is
cut as a continuous Region window (D06 §17).
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass, field

from domain.regions.entities import Region

TokenEstimator = Callable[[str], int]

PRIMARY = "primary"
CONTEXT = "context"


class ContextBuildError(Exception):
    """Invalid context request (unknown page/region, empty targets)."""


@dataclass(frozen=True)
class PageContextInput:
    """One logical page in reading order with its regions pre-sorted."""

    page_id: str
    sort_order: int
    regions: tuple[Region, ...]


@dataclass(frozen=True)
class ContextEntry:
    page_id: str
    page_sort_order: int
    region_id: str
    reading_order: int
    text: str
    role: str  # primary | context
    region_type: str
    sfx_policy: str


@dataclass(frozen=True)
class ContextChunk:
    """A provider-sized slice of the bundle; every chunk carries its own
    primary regions so outputs can be mapped back (TASK-002 §4)."""

    entries: tuple[ContextEntry, ...] = ()

    @property
    def primary_region_ids(self) -> frozenset[str]:
        return frozenset(e.region_id for e in self.entries if e.role == PRIMARY)


@dataclass(frozen=True)
class ContextBundle:
    mode: str  # single_page | max_pages | webtoon
    entries: tuple[ContextEntry, ...]
    chunks: tuple[ContextChunk, ...]
    budget_used: int
    token_budget: int | None
    _write_scope: frozenset[tuple[str, str]] = field(repr=False)

    @property
    def write_scope(self) -> frozenset[tuple[str, str]]:
        """目标写回范围 (D06 §14): only these (page_id, region_id) pairs may
        be updated by a Step consuming this bundle."""

        return self._write_scope

    @property
    def context_scope(self) -> frozenset[tuple[str, str]]:
        return frozenset((e.page_id, e.region_id) for e in self.entries)

    def primary_entries(self) -> tuple[ContextEntry, ...]:
        return tuple(e for e in self.entries if e.role == PRIMARY)

    def provenance(self) -> dict:
        """实际上下文 provenance (D06 §13): what was read, in what order."""

        return {
            "mode": self.mode,
            "token_budget": self.token_budget,
            "budget_used": self.budget_used,
            "entries": [
                {
                    "page_id": e.page_id,
                    "page_sort_order": e.page_sort_order,
                    "region_id": e.region_id,
                    "reading_order": e.reading_order,
                    "role": e.role,
                }
                for e in self.entries
            ],
        }


def _entry(region: Region, page_id: str, page_sort_order: int, role: str) -> ContextEntry:
    return ContextEntry(
        page_id=page_id,
        page_sort_order=page_sort_order,
        region_id=region.region_id,
        reading_order=region.reading_order,
        text=region.text.ocr_text,
        role=role,
        region_type=region.region_type.value,
        sfx_policy=region.sfx_policy.value,
    )


def _sorted_entries(
    pages: Sequence[PageContextInput],
    *,
    target_page_id: str,
    target_region_ids: frozenset[str],
    included_page_ids: set[str],
) -> tuple[ContextEntry, ...]:
    ordered = sorted(pages, key=lambda p: p.sort_order)
    entries: list[ContextEntry] = []
    for page in ordered:
        if page.page_id not in included_page_ids:
            continue
        for region in sorted(page.regions, key=lambda r: r.reading_order):
            if page.page_id == target_page_id and region.region_id in target_region_ids:
                role = PRIMARY
            else:
                role = CONTEXT
            entries.append(_entry(region, page.page_id, page.sort_order, role))
    return tuple(entries)


def _target_ids(
    target_page: PageContextInput, target_region_ids: Sequence[str] | None
) -> frozenset[str]:
    available = {r.region_id for r in target_page.regions}
    if target_region_ids is None:
        return available
    requested = frozenset(target_region_ids)
    missing = requested - available
    if missing:
        raise ContextBuildError(
            f"target regions not on the target page: {sorted(missing)}"
        )
    if not requested:
        raise ContextBuildError("target_region_ids must not be empty")
    return requested


def _default_estimator(text: str) -> int:
    """First shipped budget unit: 1 token ≈ 1 character (CJK-friendly,
    deterministic, dependency-free). Callers may inject a real tokenizer."""

    return len(text)


class ContextBuilder:
    def __init__(self, estimator: TokenEstimator | None = None) -> None:
        self._estimate = estimator or _default_estimator

    # ------------------------------------------------------------------
    # D06 §15 — single-page modes
    # ------------------------------------------------------------------

    def build_single_page(
        self,
        pages: Sequence[PageContextInput],
        *,
        target_page_id: str,
        target_region_ids: Sequence[str] | None = None,
        window: str = "current",
        token_budget: int | None = None,
    ) -> ContextBundle:
        """window: current | previous | next | both. Neighbor pages contribute
        read-only context; only the target page's chosen regions are writable
        (D06 §14 invariant)."""

        if window not in {"current", "previous", "next", "both"}:
            raise ContextBuildError(f"unknown single-page window: {window}")
        ordered = sorted(pages, key=lambda p: p.sort_order)
        index = self._find_page(ordered, target_page_id)
        target = ordered[index]
        target_ids = _target_ids(target, target_region_ids)

        neighbors: list[PageContextInput] = []
        if window in {"previous", "both"} and index > 0:
            neighbors.append(ordered[index - 1])
        if window in {"next", "both"} and index + 1 < len(ordered):
            neighbors.append(ordered[index + 1])

        budget_used = sum(
            self._estimate(r.text.ocr_text) for r in target.regions if r.region_id in target_ids
        )
        included: list[PageContextInput] = []
        for neighbor in neighbors:
            cost = sum(self._estimate(r.text.ocr_text) for r in neighbor.regions)
            if token_budget is not None and budget_used + cost > token_budget:
                continue
            budget_used += cost
            included.append(neighbor)

        entries = _sorted_entries(
            [target, *included],
            target_page_id=target_page_id,
            target_region_ids=target_ids,
            included_page_ids={target.page_id, *(p.page_id for p in included)},
        )
        return self._bundle("single_page", entries, target_page_id, target_ids, budget_used, token_budget)

    # ------------------------------------------------------------------
    # D06 §16 — as many pages as the budget allows
    # ------------------------------------------------------------------

    def build_max_pages(
        self,
        pages: Sequence[PageContextInput],
        *,
        target_page_id: str,
        target_region_ids: Sequence[str] | None = None,
        token_budget: int,
    ) -> ContextBundle:
        """目标页全部 Region 优先 → 向前/向后扩展连续 Page → 预算前停止."""

        if token_budget is None or token_budget <= 0:
            raise ContextBuildError("max-pages mode requires a positive token_budget")
        ordered = sorted(pages, key=lambda p: p.sort_order)
        index = self._find_page(ordered, target_page_id)
        target = ordered[index]
        target_ids = _target_ids(target, target_region_ids)

        budget_used = sum(
            self._estimate(r.text.ocr_text) for r in target.regions if r.region_id in target_ids
        )
        included: list[PageContextInput] = []
        back, forward = index - 1, index + 1
        back_open = forward_open = True
        while back_open or forward_open:
            progressed = False
            if back_open and back >= 0:
                cost = sum(self._estimate(r.text.ocr_text) for r in ordered[back].regions)
                if budget_used + cost <= token_budget:
                    budget_used += cost
                    included.append(ordered[back])
                    back -= 1
                    progressed = True
                else:
                    back_open = False
            if forward_open and forward < len(ordered):
                cost = sum(self._estimate(r.text.ocr_text) for r in ordered[forward].regions)
                if budget_used + cost <= token_budget:
                    budget_used += cost
                    included.append(ordered[forward])
                    forward += 1
                    progressed = True
                else:
                    forward_open = False
            if not progressed:
                break

        entries = _sorted_entries(
            [target, *included],
            target_page_id=target_page_id,
            target_region_ids=target_ids,
            included_page_ids={target.page_id, *(p.page_id for p in included)},
        )
        return self._bundle("max_pages", entries, target_page_id, target_ids, budget_used, token_budget)

    # ------------------------------------------------------------------
    # D06 §17 — Webtoon: continuous Region window on one logical Page
    # ------------------------------------------------------------------

    def build_webtoon(
        self,
        page: PageContextInput,
        *,
        target_region_ids: Sequence[str],
        token_budget: int,
    ) -> ContextBundle:
        """One webtoon image is one logical Page; context is a continuous
        window over Region reading_order, cut into budget-sized chunks.
        Tiles are an image-processing concern and never appear here."""

        if token_budget is None or token_budget <= 0:
            raise ContextBuildError("webtoon mode requires a positive token_budget")
        target_ids = _target_ids(page, target_region_ids)
        ordered_regions = sorted(page.regions, key=lambda r: r.reading_order)
        positions = {r.region_id: i for i, r in enumerate(ordered_regions)}
        first = min(positions[rid] for rid in target_ids)
        last = max(positions[rid] for rid in target_ids)

        entries: list[ContextEntry] = []
        total_used = 0
        chunk_used = 0
        chunks: list[ContextChunk] = []
        current: list[ContextEntry] = []
        for region in ordered_regions[first : last + 1]:
            role = PRIMARY if region.region_id in target_ids else CONTEXT
            entry = _entry(region, page.page_id, page.sort_order, role)
            cost = self._estimate(entry.text)
            if current and chunk_used + cost > token_budget:
                chunks.append(ContextChunk(tuple(current)))
                current = []
                chunk_used = 0
            current.append(entry)
            chunk_used += cost
            total_used += cost
            entries.append(entry)
        if current:
            chunks.append(ContextChunk(tuple(current)))

        return ContextBundle(
            mode="webtoon",
            entries=tuple(entries),
            chunks=tuple(chunks),
            budget_used=total_used,
            token_budget=token_budget,
            _write_scope=frozenset(
                (page.page_id, rid) for rid in target_ids
            ),
        )

    # ------------------------------------------------------------------

    @staticmethod
    def _find_page(ordered: Sequence[PageContextInput], target_page_id: str) -> int:
        for index, page in enumerate(ordered):
            if page.page_id == target_page_id:
                return index
        raise ContextBuildError(f"unknown target page: {target_page_id}")

    def _bundle(
        self,
        mode: str,
        entries: tuple[ContextEntry, ...],
        target_page_id: str,
        target_ids: frozenset[str],
        budget_used: int,
        token_budget: int | None,
    ) -> ContextBundle:
        if mode == "single_page" and token_budget is not None and budget_used > token_budget:
            raise ContextBuildError("target page exceeds the token budget")
        return ContextBundle(
            mode=mode,
            entries=entries,
            chunks=(ContextChunk(entries),),
            budget_used=budget_used,
            token_budget=token_budget,
            _write_scope=frozenset((target_page_id, rid) for rid in target_ids),
        )
