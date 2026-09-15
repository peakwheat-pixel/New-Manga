"""Context Builder ordering, windows and budgets (D06 §14~16,
AC-TRANS-003/004)."""

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


def page(page_id: str, sort_order: int, *regions) -> PageContextInput:
    return PageContextInput(page_id=page_id, sort_order=sort_order, regions=tuple(regions))


PAGES = [
    page("p1", 0, make_region("r11", 1, ocr_text="一页一号"),
         make_region("r12", 2, ocr_text="一页二号")),
    page("p2", 1, make_region("r21", 1, ocr_text="二页一号")),
    page("p3", 2, make_region("r31", 1, ocr_text="三页一号")),
    page("p4", 3, make_region("r41", 1, ocr_text="四页一号")),
    page("p5", 4, make_region("r51", 1, ocr_text="五页一号")),
]


# ----------------------------------------------------------------------
# ordering: Page sort_order + Region reading_order (AC-TRANS-004)
# ----------------------------------------------------------------------


def test_entries_are_sorted_by_page_and_reading_order() -> None:
    bundle = builder.build_single_page(
        [PAGES[2], PAGES[0], PAGES[1]],  # deliberately shuffled input
        target_page_id="p2",
        window="both",
    )
    assert [(e.page_id, e.region_id) for e in bundle.entries] == [
        ("p1", "r11"), ("p1", "r12"), ("p2", "r21"), ("p3", "r31"),
    ]


def test_write_scope_only_contains_target_regions() -> None:
    """D06 §14 invariant: Context Scope ≠ Write Scope."""

    bundle = builder.build_single_page(
        PAGES[:3],
        target_page_id="p2",
        target_region_ids=["r21"],
        window="both",
    )
    assert bundle.write_scope == frozenset({("p2", "r21")})
    context_pairs = {
        (e.page_id, e.region_id)
        for e in bundle.entries
        if e.role == CONTEXT
    }
    assert context_pairs and context_pairs.isdisjoint(bundle.write_scope)


def test_primary_role_marks_only_target_regions() -> None:
    bundle = builder.build_single_page(
        PAGES[:2],
        target_page_id="p1",
        target_region_ids=["r12"],
        window="current",
    )
    roles = {e.region_id: e.role for e in bundle.entries}
    assert roles == {"r11": CONTEXT, "r12": PRIMARY}


# ----------------------------------------------------------------------
# single-page windows (D06 §15)
# ----------------------------------------------------------------------


def test_window_current_only_reads_target_page() -> None:
    bundle = builder.build_single_page(PAGES, target_page_id="p3", window="current")
    assert {e.page_id for e in bundle.entries} == {"p3"}


def test_window_previous_reads_only_the_previous_page() -> None:
    bundle = builder.build_single_page(PAGES, target_page_id="p3", window="previous")
    assert {e.page_id for e in bundle.entries} == {"p2", "p3"}


def test_window_next_and_both() -> None:
    nxt = builder.build_single_page(PAGES, target_page_id="p3", window="next")
    assert {e.page_id for e in nxt.entries} == {"p3", "p4"}
    both = builder.build_single_page(PAGES, target_page_id="p3", window="both")
    assert {e.page_id for e in both.entries} == {"p2", "p3", "p4"}


def test_unknown_window_and_page_are_rejected() -> None:
    with pytest.raises(ContextBuildError):
        builder.build_single_page(PAGES, target_page_id="p3", window="diagonal")
    with pytest.raises(ContextBuildError):
        builder.build_single_page(PAGES, target_page_id="nope")


def test_target_regions_must_live_on_the_target_page() -> None:
    with pytest.raises(ContextBuildError):
        builder.build_single_page(
            PAGES, target_page_id="p3", target_region_ids=["r11"]
        )
    with pytest.raises(ContextBuildError):
        builder.build_single_page(PAGES, target_page_id="p3", target_region_ids=[])


# ----------------------------------------------------------------------
# budget behaviour
# ----------------------------------------------------------------------


def test_single_page_budget_drops_neighbor_but_keeps_target() -> None:
    # target r21=4 chars; p1 costs 8, p3 costs 4
    bundle = builder.build_single_page(
        PAGES, target_page_id="p2", window="both", token_budget=9
    )
    assert {e.page_id for e in bundle.entries} == {"p2", "p3"}  # p1 dropped
    assert bundle.budget_used == 8  # target + one neighbor


def test_single_page_target_page_may_exceed_budget_is_rejected() -> None:
    with pytest.raises(ContextBuildError):
        builder.build_single_page(
            PAGES, target_page_id="p1", window="current", token_budget=3
        )


def test_max_pages_extends_until_budget_stops() -> None:
    """D06 §16: 目标页全部 Region → 向前/向后扩展 → 预算前停止."""

    bundle = builder.build_max_pages(
        PAGES, target_page_id="p3", token_budget=15
    )
    page_ids = [e.page_id for e in bundle.entries]
    # every char costs 1: target(4)+p2(4)+p4(4)=12; next page (8 chars) does
    # not fit, so both directions stop before p1/p5
    assert set(page_ids) == {"p2", "p3", "p4"}
    assert bundle.write_scope == frozenset({("p3", "r31")})
    assert bundle.budget_used == 12


def test_max_pages_keeps_target_complete_even_if_budget_tight() -> None:
    bundle = builder.build_max_pages(
        [page("pa", 0, make_region("ra1", 1, ocr_text="很长很长很长很长")),
         page("pb", 1, make_region("rb1", 1, ocr_text="目标"))],
        target_page_id="pb",
        token_budget=4,
    )
    assert {e.region_id for e in bundle.primary_entries()} == {"rb1"}
    assert [e.region_id for e in bundle.entries if e.role == CONTEXT] == []


def test_max_pages_requires_positive_budget() -> None:
    with pytest.raises(ContextBuildError):
        builder.build_max_pages(PAGES, target_page_id="p3", token_budget=0)


def test_custom_estimator_is_used() -> None:
    wordish = ContextBuilder(estimator=lambda text: max(1, len(text) // 2))
    bundle = wordish.build_single_page(
        PAGES, target_page_id="p2", window="both", token_budget=6
    )
    assert bundle.budget_used == 6  # 2 + 2 + 2 half-char units


def test_provenance_records_actual_context() -> None:
    bundle = builder.build_single_page(
        PAGES, target_page_id="p2", window="both"
    )
    provenance = bundle.provenance()
    assert provenance["mode"] == "single_page"
    order = [(item["page_id"], item["region_id"], item["role"]) for item in provenance["entries"]]
    assert order == [
        ("p1", "r11", CONTEXT), ("p1", "r12", CONTEXT),
        ("p2", "r21", PRIMARY), ("p3", "r31", CONTEXT),
    ]
