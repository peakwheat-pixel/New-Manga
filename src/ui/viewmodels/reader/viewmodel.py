from __future__ import annotations

from PySide6.QtCore import Property, QObject, Signal, Slot

from application.reading.service import ReadingMode, ReadingService


class ReaderViewModel(QObject):
    changed = Signal()

    def __init__(self, service: ReadingService, parent: QObject | None = None):
        super().__init__(parent)
        self._service = service

    def _path(self) -> str:
        return self._service.current_source_path if self._service.pages else ""

    def _message(self) -> str:
        return self._service.status_message() if self._service.pages else ""

    sourcePath = Property(str, _path, notify=changed)
    statusMessage = Property(str, _message, notify=changed)
    mode = Property(str, lambda self: self._service.mode.value, notify=changed)
    direction = Property(str, lambda self: self._service.direction, notify=changed)
    pageIndex = Property(int, lambda self: self._service.progress.page_index, notify=changed)

    @Slot()
    def nextPage(self):
        self._service.next_page()
        self.changed.emit()

    @Slot(str)
    def setMode(self, value: str):
        self._service.mode = ReadingMode(value)
        self.changed.emit()

    @Slot(str)
    def setDirection(self, value: str):
        if value not in {"rtl", "ltr"}:
            return
        self._service.direction = value
        self.changed.emit()

