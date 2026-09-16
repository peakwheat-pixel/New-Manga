from __future__ import annotations

from PySide6.QtCore import Property, QObject, Signal, Slot

from application.export.service import ExportFormat, ExportRequest, ExportService


class ExportViewModel(QObject):
    changed = Signal()

    def __init__(self, service: ExportService, parent: QObject | None = None):
        super().__init__(parent)
        self._service = service
        self._message = ""

    def _history(self):
        return self._service.history()

    def _status(self):
        return self._message

    history = Property("QVariantList", _history, notify=changed)
    statusMessage = Property(str, _status, notify=changed)

    @Slot(str, str)
    def export(self, format_name: str, output_path: str):
        self._message = "Export requires page data from the reader"
        self.changed.emit()

