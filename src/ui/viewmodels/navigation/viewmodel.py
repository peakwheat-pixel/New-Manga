"""NavigationViewModel: QML bridge over NavigationService (TASK-012).

All decisions stay in the application service; this class only adapts
state to Qt properties/signals so QML stays free of business logic
(D05 §60). One instance is published to QML as ``navigationViewModel``.
"""

from __future__ import annotations

from PySide6.QtCore import Property, QObject, Signal, Slot

from application.navigation.service import NavigationService

_PAGE_LABELS = (
    ("bookshelf", "书架"),
    ("workbench", "工作台"),
    ("reader", "阅读器"),
    ("settings", "设置"),
)


class NavigationViewModel(QObject):
    currentPageChanged = Signal(str)
    workbenchContextChanged = Signal()
    readerContextChanged = Signal()
    workbenchBadgeChanged = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._service = NavigationService()

    # ------------------------------------------------------------------
    # properties
    # ------------------------------------------------------------------

    def get_current_page(self) -> str:
        return self._service.current_page.value

    currentPage = Property(str, get_current_page, notify=currentPageChanged)

    def get_pages(self) -> list[dict]:
        return [
            {"id": page_id, "label": label} for page_id, label in _PAGE_LABELS
        ]

    pages = Property("QVariantList", get_pages, constant=True)

    def get_workbench_context(self) -> dict:
        return self._service.workbench_context

    workbenchContext = Property(
        "QVariantMap", get_workbench_context, notify=workbenchContextChanged
    )

    def get_reader_context(self) -> dict:
        return self._service.reader_context

    readerContext = Property(
        "QVariantMap", get_reader_context, notify=readerContextChanged
    )

    def get_workbench_badge(self) -> str:
        return self._service.workbench_activity["badge"]

    workbenchBadge = Property(
        str, get_workbench_badge, notify=workbenchBadgeChanged
    )

    def get_workbench_running(self) -> bool:
        return self._service.workbench_activity["running"]

    workbenchRunning = Property(
        bool, get_workbench_running, notify=workbenchBadgeChanged
    )

    # ------------------------------------------------------------------
    # slots (QML call these)
    # ------------------------------------------------------------------

    @Slot(str)
    def navigate(self, page: str) -> None:
        target = self._service.navigate(page)
        self.currentPageChanged.emit(target.value)

    @Slot(str, str)
    def enterWorkbench(self, book_id: str, chapter_id: str) -> None:
        self._service.enter_workbench(book_id=book_id, chapter_id=chapter_id)
        self.currentPageChanged.emit(self._service.current_page.value)
        self.workbenchContextChanged.emit()

    @Slot(str, str, str, str)
    def enterReader(
        self, book_id: str, chapter_id: str, page_id: str = "", progress: str = ""
    ) -> None:
        self._service.enter_reader(
            book_id=book_id,
            chapter_id=chapter_id,
            page_id=page_id or None,
            progress=progress or None,
        )
        self.currentPageChanged.emit(self._service.current_page.value)
        self.readerContextChanged.emit()

    @Slot(bool, str)
    def setWorkbenchActivity(self, running: bool, badge: str = "") -> None:
        self._service.set_workbench_activity(running=running, badge=badge)
        self.workbenchBadgeChanged.emit()
