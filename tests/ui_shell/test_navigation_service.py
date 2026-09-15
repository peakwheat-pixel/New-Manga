"""NavigationService (AC-NAV-001..003, D05 §2/§3.1, D05 §67).

Pure application layer — no Qt.
"""

from __future__ import annotations

import helpers  # noqa: F401  (sys.path injection)

import pytest

from application.navigation.service import (
    NavigationPage,
    NavigationService,
)

FOUR_PAGES = {"bookshelf", "workbench", "reader", "settings"}


class TestDefaultAndRoutes:
    def test_startup_selects_bookshelf(self) -> None:
        service = NavigationService()
        assert service.current_page is NavigationPage.BOOKSHELF  # AC-NAV-001

    def test_exactly_four_top_level_pages(self) -> None:
        assert {page.value for page in NavigationPage} == FOUR_PAGES  # AC-NAV-002

    @pytest.mark.parametrize("page", sorted(FOUR_PAGES))
    def test_can_navigate_each_page(self, page: str) -> None:
        service = NavigationService()
        service.navigate(page)
        assert service.current_page.value == page

    def test_unknown_page_is_rejected(self) -> None:
        service = NavigationService()
        with pytest.raises(ValueError, match="not a top-level page"):
            service.navigate("book_detail")  # must never become a fifth route

    def test_navigate_to_same_page_is_a_noop(self) -> None:
        service = NavigationService()
        service.navigate("bookshelf")
        assert service.current_page is NavigationPage.BOOKSHELF


class TestContextPreservation:
    def test_switching_pages_keeps_workbench_context(self) -> None:
        service = NavigationService()
        service.enter_workbench(book_id="book-a", chapter_id="ch-12")
        service.navigate("settings")
        service.navigate("workbench")
        context = service.workbench_context
        assert context["book_id"] == "book-a"  # AC-NAV-003
        assert context["chapter_id"] == "ch-12"

    def test_enter_workbench_switches_page_and_carries_context(self) -> None:
        service = NavigationService()
        service.enter_workbench(book_id="book-a", chapter_id="ch-1")
        assert service.current_page is NavigationPage.WORKBENCH
        assert service.workbench_context["book_id"] == "book-a"

    def test_enter_reader_carries_progress(self) -> None:
        service = NavigationService()
        service.enter_reader(
            book_id="book-a", chapter_id="ch-2", page_id="page-23", progress="12/48"
        )
        assert service.current_page is NavigationPage.READER
        context = service.reader_context
        assert context["book_id"] == "book-a"
        assert context["chapter_id"] == "ch-2"
        assert context["page_id"] == "page-23"
        assert context["progress"] == "12/48"

    def test_contexts_are_independent(self) -> None:
        service = NavigationService()
        service.enter_workbench(book_id="book-a", chapter_id="ch-1")
        service.enter_reader(book_id="book-b", chapter_id="ch-2")
        assert service.workbench_context["book_id"] == "book-a"
        assert service.reader_context["book_id"] == "book-b"

    def test_leaving_workbench_does_not_clear_running_task_flag(self) -> None:
        service = NavigationService()
        service.set_workbench_activity(running=True, badge="运行中")
        service.navigate("bookshelf")
        assert service.workbench_activity["running"] is True
        assert service.workbench_activity["badge"] == "运行中"
