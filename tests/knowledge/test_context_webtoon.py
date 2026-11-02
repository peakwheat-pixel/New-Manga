"""Webtoon context: continuous Region window + budget chunks (D06 §17);
tiles never become logical pages."""

from __future__ import annotations

import pytest

import knowledge_helpers  # noqa: F401
from application.translation.context.builder import (
    CONTEXT,
    PRIMARY,
    ContextBuildError,
    ContextBuilder,
    PageContextInput,
)

from knowledge_helpers import make_region

builder = ContextBuilder()

# One long webtoon image = one logical Page with 8 regions in reading order.
WEBTOON = PageContextInput(
    page_id="web-1",
    sort_order=0,
    regions=tuple(
        make_region(f"w{i}", i, ocr_text=f"段{i}" * 3, region_type="speech")
        for i in range(1, 9)
    ),
)


def test_continuous_window_covers_gaps_between_targets() -> None:
    """Targets w2 and w6: everything between stays as read-only context so
    the window is continuous over reading_order."""

    bundle = builder.build_webtoon(WEBTOON, target_region_ids=["w2", "w6"], token_budget=1000)
    assert bundle.mode == "webtoon"
    assert [(e.region_id, e.role) for e in bundle.entries] == [
        ("w2", PRIMARY), ("w3", CONTEXT), ("w4", CONTEXT),
        ("w5", CONTEXT), ("w6", PRIMARY),
    ]
    assert bundle.write_scope == frozenset({("web-1", "w2"), ("web-1", "w6")})


def test_budget_cuts_region_chunks_without_losing_targets() -> None:
    # each region text is 6 chars (段N * 3); budget 12 → 2 regions per chunk
    bundle = builder.build_webtoon(WEBTOON, target_region_ids=["w1", "w3", "w7"], token_budget=12)
    assert [len(chunk.entries) for chunk in bundle.chunks] == [2, 2, 2, 1]
    covered = [entry.region_id for chunk in bundle.chunks for entry in chunk.entries]
    assert covered == ["w1", "w2", "w3", "w4", "w5", "w6", "w7"]
    # every target is primary inside its own chunk so outputs map back
    all_primaries = set().union(*(chunk.primary_region_ids for chunk in bundle.chunks))
    assert all_primaries == {"w1", "w3", "w7"}
    empty_chunks = [chunk for chunk in bundle.chunks if not chunk.primary_region_ids]
    assert all(
        all(entry.role == CONTEXT for entry in chunk.entries) for chunk in empty_chunks
    )


def test_chunks_preserve_global_reading_order() -> None:
    bundle = builder.build_webtoon(WEBTOON, target_region_ids=["w1", "w8"], token_budget=12)
    flat = [entry.region_id for chunk in bundle.chunks for entry in chunk.entries]
    assert flat == sorted(flat, key=lambda rid: int(rid[1:]))


def test_tiles_are_not_context_units() -> None:
    """The builder API has no tile input at all: one page in, region window
    out (D06 §17 Webtoon 临时 Tile 只用于图像处理)."""

    bundle = builder.build_webtoon(WEBTOON, target_region_ids=["w4"], token_budget=100)
    assert all(entry.page_id == "web-1" for entry in bundle.entries)
    assert bundle.provenance()["mode"] == "webtoon"


def test_unknown_target_region_is_rejected() -> None:
    with pytest.raises(ContextBuildError):
        builder.build_webtoon(WEBTOON, target_region_ids=["w99"], token_budget=10)


def test_single_superlong_region_gets_its_own_chunk() -> None:
    huge = PageContextInput(
        page_id="web-2",
        sort_order=0,
        regions=(
            make_region("h1", 1, ocr_text="超" * 50),
            make_region("h2", 2, ocr_text="小"),
        ),
    )
    bundle = builder.build_webtoon(huge, target_region_ids=["h1", "h2"], token_budget=10)
    assert [len(chunk.entries) for chunk in bundle.chunks] == [1, 1]
