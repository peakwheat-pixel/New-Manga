"""Top-level navigation use cases (AC-NAV-001..003, D05 §2/§3.1/§67).

Frozen rules:
- exactly four sibling top-level pages; anything else is rejected and can
  never become a fifth route (AC-NAV-002).
- the app starts on the bookshelf (AC-NAV-001).
- switching pages never clears Book/Chapter/Page context, and leaving the
  workbench never stops a running pipeline (AC-NAV-003, D05 §3.1).
- entering workbench/reader from the shelf carries Book+Chapter (and the
  reader additionally carries page/progress, D05 §67).
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum


class NavigationPage(str, Enum):
    """The four and only top-level pages (D05 §2.1)."""

    BOOKSHELF = "bookshelf"
    WORKBENCH = "workbench"
    READER = "reader"
    SETTINGS = "settings"


@dataclass(frozen=True)
class PageContext:
    """Context carried across page switches (AC-NAV-003)."""

    book_id: str | None = None
    chapter_id: str | None = None
    page_id: str | None = None
    progress: str | None = None

    def as_map(self) -> dict:
        return {
            "book_id": self.book_id,
            "chapter_id": self.chapter_id,
            "page_id": self.page_id,
            "progress": self.progress,
        }


@dataclass
class WorkbenchActivity:
    """Badge state for the workbench nav entry (D05 §3.1); never cleared by
    page switches. Pipeline binding itself arrives with TASK-011."""

    running: bool = False
    badge: str = ""


@dataclass
class NavigationState:
    current_page: NavigationPage = NavigationPage.BOOKSHELF
    workbench_context: PageContext = field(default_factory=PageContext)
    reader_context: PageContext = field(default_factory=PageContext)
    workbench_activity: WorkbenchActivity = field(default_factory=WorkbenchActivity)


class NavigationService:
    """Pure state holder; the ViewModel forwards QML calls here."""

    def __init__(self) -> None:
        self._state = NavigationState()

    # ------------------------------------------------------------------
    # queries
    # ------------------------------------------------------------------

    @property
    def current_page(self) -> NavigationPage:
        return self._state.current_page

    @property
    def workbench_context(self) -> dict:
        return self._state.workbench_context.as_map()

    @property
    def reader_context(self) -> dict:
        return self._state.reader_context.as_map()

    @property
    def workbench_activity(self) -> dict:
        activity = self._state.workbench_activity
        return {"running": activity.running, "badge": activity.badge}

    # ------------------------------------------------------------------
    # commands
    # ------------------------------------------------------------------

    def navigate(self, page: str) -> NavigationPage:
        try:
            target = NavigationPage(page)
        except ValueError:
            raise ValueError(
                f"{page!r} is not a top-level page; only "
                f"{[p.value for p in NavigationPage]} exist (AC-NAV-002)"
            ) from None
        # AC-NAV-003: switching never resets context or activity.
        self._state = replace(self._state, current_page=target)
        return target

    def enter_workbench(self, *, book_id: str, chapter_id: str) -> NavigationPage:
        context = PageContext(book_id=book_id, chapter_id=chapter_id)
        self._state = replace(
            self._state,
            current_page=NavigationPage.WORKBENCH,
            workbench_context=context,
        )
        return self._state.current_page

    def enter_reader(
        self,
        *,
        book_id: str,
        chapter_id: str,
        page_id: str | None = None,
        progress: str | None = None,
    ) -> NavigationPage:
        context = PageContext(
            book_id=book_id,
            chapter_id=chapter_id,
            page_id=page_id,
            progress=progress,
        )
        self._state = replace(
            self._state,
            current_page=NavigationPage.READER,
            reader_context=context,
        )
        return self._state.current_page

    def set_workbench_activity(self, *, running: bool, badge: str = "") -> None:
        self._state = replace(
            self._state,
            workbench_activity=WorkbenchActivity(running=running, badge=badge),
        )
