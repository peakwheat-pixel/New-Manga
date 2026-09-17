"""ExportViewModel: export window state between QML and ExportService.

Published to QML as ``exportViewModel`` (window opened standalone) or
handed over as ``readerViewModel.exportController`` (reader-launched).

- scope/order/output/naming/overwrite policy map to D05 §51's window
  fields; scope is the open chapter's pages in reading order;
- stale handling implements D06 §97's prompt: before export the window
  shows 部分页面不是最新渲染结果 and the user either re-renders first or
  explicitly switches to 继续导出现有版本 (stalePolicy);
- exports run on a worker thread so the UI stays responsive and the
  cancel button can fire the cooperative cancel flag mid-archive;
- history powers 打开所在文件夹 / 查看状态 / 使用相同设置再次导出
  (D03 §31 / D04 §37).
"""

from __future__ import annotations

import threading
from collections.abc import Callable
from pathlib import Path

from PySide6.QtCore import Property, QObject, QStandardPaths, QUrl, Signal, Slot
from PySide6.QtGui import QDesktopServices

from application.export import (
    ExportCancelledError,
    ExportFormat,
    ExportPage,
    ExportRequest,
    ExportService,
    OverwritePolicy,
    StalePolicy,
)

_FORMATS = (
    ("single_image", "单图"),
    ("zip", "ZIP"),
    ("cbz", "CBZ"),
    ("pdf", "PDF"),
    ("text", "文本"),
)

_OVERWRITE_POLICIES = ("overwrite", "skip", "auto_rename")
_STALE_POLICIES = ("abort", "continue")

_FORMAT_SUFFIX = {
    "single_image": ".png",
    "zip": ".zip",
    "cbz": ".cbz",
    "pdf": ".pdf",
    "text": ".txt",
}


def default_output_dir() -> str:
    documents = QStandardPaths.writableLocation(
        QStandardPaths.StandardLocation.DocumentsLocation
    )
    return documents or str(Path.home())


class ExportViewModel(QObject):
    changed = Signal()
    exportFinished = Signal("QVariantMap")
    exportFailed = Signal(str)

    def __init__(
        self,
        service: ExportService,
        pages_provider: Callable[[], list[ExportPage]],
        *,
        book_id: str = "",
        chapter_id: str = "",
        output_dir: str | None = None,
        folder_opener: Callable[[str], bool] | None = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._service = service
        self._pages_provider = pages_provider
        self._book_id = book_id
        self._chapter_id = chapter_id
        self._format = "zip"
        self._output_dir = output_dir or default_output_dir()
        self._output_name = ""
        self._overwrite_policy = "overwrite"
        self._stale_policy = "abort"
        self._mode_value = "translated"
        self._stale_warning = ""
        self._status = ""
        self._running = False
        self._cancel_event = threading.Event()
        self._worker: threading.Thread | None = None
        self._folder_opener = folder_opener or _open_folder

    # ------------------------------------------------------------------
    # context
    # ------------------------------------------------------------------

    def set_context(self, book_id: str, chapter_id: str) -> None:
        self._book_id = book_id
        self._chapter_id = chapter_id
        self.changed.emit()

    # ------------------------------------------------------------------
    # properties (D05 §51 fields)
    # ------------------------------------------------------------------

    def _formats(self) -> list:
        return [{"value": value, "label": label} for value, label in _FORMATS]

    formats = Property("QVariantList", _formats, constant=True)

    def _format(self) -> str:
        return self._format

    format = Property(str, _format, notify=changed)

    def _scope_summary(self) -> str:
        pages = self._safe_pages()
        order = "阅读顺序"
        return f"范围：当前章节 {len(pages)} 页（{order}）"

    scopeSummary = Property(str, _scope_summary, notify=changed)

    def _page_count(self) -> int:
        return len(self._safe_pages())

    pageCount = Property(int, _page_count, notify=changed)

    def _output_path(self) -> str:
        return str(Path(self._output_dir) / self._default_name())

    outputPath = Property(str, _output_path, notify=changed)

    def _overwrite_policy(self) -> str:
        return self._overwrite_policy

    overwritePolicy = Property(str, _overwrite_policy, notify=changed)

    def _mode(self) -> str:
        return self._mode_value

    mode = Property(str, _mode, notify=changed)

    def _stale_policy(self) -> str:
        return self._stale_policy

    stalePolicy = Property(str, _stale_policy, notify=changed)

    def _stale_warning_visible(self) -> bool:
        return bool(self._stale_warning)

    staleWarningVisible = Property(bool, _stale_warning_visible, notify=changed)

    def _stale_warning(self) -> str:
        return self._stale_warning

    staleWarningText = Property(str, _stale_warning, notify=changed)

    def _status(self) -> str:
        return self._status

    statusMessage = Property(str, _status, notify=changed)

    def _running(self) -> bool:
        return self._running

    running = Property(bool, _running, notify=changed)

    def _history(self) -> list:
        rows = []
        for record in self._service.history():
            rows.append(
                {
                    "export_id": record.export_id,
                    "type": record.export_type,
                    "status": record.status,
                    "output_path": record.output_path,
                    "created_at": record.created_at,
                    "completed_at": record.completed_at,
                }
            )
        return rows

    history = Property("QVariantList", _history, notify=changed)

    # ------------------------------------------------------------------
    # QML slots
    # ------------------------------------------------------------------

    @Slot(str)
    def setFormat(self, value: str) -> None:
        if value not in dict(_FORMATS):
            return
        self._format = value
        self.changed.emit()

    @Slot(str)
    def setOutputPath(self, value: str) -> None:
        path = Path(QUrl(value).toLocalFile() if value.startswith("file:") else value)
        if path.name:
            self._output_dir = str(path.parent)
            self._output_name = path.name
        else:
            self._output_dir = str(path) or self._output_dir
            self._output_name = ""
        self.changed.emit()

    @Slot(str)
    def setOverwritePolicy(self, value: str) -> None:
        if value in _OVERWRITE_POLICIES:
            self._overwrite_policy = value
            self.changed.emit()

    @Slot(str)
    def setMode(self, value: str) -> None:
        """导出 Original（原图）或 Translated（译图）内容."""
        if value in ("original", "translated"):
            self._mode_value = value
            self.changed.emit()

    @Slot(str)
    def setStalePolicy(self, value: str) -> None:
        if value in _STALE_POLICIES:
            self._stale_policy = value
            self.refreshStaleWarning()
            self.changed.emit()

    @Slot()
    def refreshStaleWarning(self) -> None:
        """D06 §97 prompt state — must be visible before any translated
        export with stale/missing renders."""
        stale: list[str] = []
        missing: list[str] = []
        for page in self._safe_pages():
            if page.stale:
                stale.append(page.filename)
            if page.translated_provider is None:
                missing.append(page.filename)
        if not stale and not missing:
            self._stale_warning = ""
        elif self._stale_policy == StalePolicy.CONTINUE.value:
            self._stale_warning = (
                f"将继续导出现有版本：{len(stale)} 页不是最新渲染，{len(missing)} 页缺译图（将以原图代替）"
            )
        else:
            self._stale_warning = (
                f"部分页面不是最新渲染结果：{len(stale)} 页 stale，{len(missing)} 页缺译图。"
                "请先重新渲染，或选择“继续导出现有版本”。"
            )
        self.changed.emit()

    @Slot()
    def startExport(self) -> None:
        """Kick the export on a worker thread; results arrive via
        exportFinished / exportFailed so QML never blocks."""
        if self._running:
            return
        request = self._build_request()
        if request is None:
            self._fail("没有可导出的页面；请先打开一个章节")
            return
        self._cancel_event.clear()
        self._running = True
        self._status = "正在导出…"
        self.changed.emit()

        def _work() -> None:
            try:
                result = self._service.export(request)
            except ExportCancelledError:
                self._finish({"status": "cancelled"})
            # ExportError and OSError included: any escaping exception would
            # kill this worker silently and leave `running` stuck True (R-002).
            except Exception as error:
                self._fail(_worker_error_text(error))
            else:
                self._finish(
                    {
                        "status": result.status.value,
                        "output_path": str(result.output_path or ""),
                        "export_id": result.export_id,
                        "page_count": len(result.page_ids),
                        "included_stale": len(result.included_stale_page_ids),
                        "included_missing": len(result.included_missing_page_ids),
                    }
                )

        self._worker = threading.Thread(target=_work, daemon=True)
        self._worker.start()

    @Slot()
    def cancelExport(self) -> None:
        """Cooperative cancel: polled by the service between stages."""
        self._cancel_event.set()

    @Slot()
    def openOutputFolder(self) -> None:
        """打开所在文件夹 (D03 §31 / D04 §37) for the latest export."""
        rows = self._history()
        if not rows:
            return
        folder = str(Path(rows[0]["output_path"]).parent)
        if not self._folder_opener(folder):
            self._status = f"无法打开文件夹：{folder}"
            self.changed.emit()

    @Slot(str)
    def repeatExport(self, export_id: str) -> None:
        """使用相同设置再次导出 (D03 §31 / D04 §37)."""
        if self._running:
            return
        pages = {page.page_id: page for page in self._safe_pages()}
        self._cancel_event.clear()
        self._running = True
        self._status = "正在按相同设置导出…"
        self.changed.emit()

        def _work() -> None:
            try:
                result = self._service.repeat(
                    export_id,
                    pages,
                    cancel=self._cancel_event.is_set,
                )
            except ExportCancelledError:
                self._finish({"status": "cancelled"})
            # Same blanket guard as startExport (R-002): no exception may
            # escape the worker and leave `running` stuck True.
            except Exception as error:
                self._fail(_worker_error_text(error))
            else:
                self._finish(
                    {
                        "status": result.status.value,
                        "output_path": str(result.output_path or ""),
                        "export_id": result.export_id,
                        "page_count": len(result.page_ids),
                    }
                )

        self._worker = threading.Thread(target=_work, daemon=True)
        self._worker.start()

    # ------------------------------------------------------------------
    # internals
    # ------------------------------------------------------------------

    def _safe_pages(self) -> list[ExportPage]:
        try:
            return list(self._pages_provider())
        except Exception:
            return []

    def _default_name(self) -> str:
        if self._output_name:
            return self._output_name
        stem = self._chapter_id or "export"
        return f"{stem}{_FORMAT_SUFFIX[self._format]}"

    def _build_request(self) -> ExportRequest | None:
        pages = self._safe_pages()
        if not pages:
            return None
        return ExportRequest(
            book_id=self._book_id,
            chapter_id=self._chapter_id,
            format=ExportFormat(self._format),
            output_path=Path(self._output_dir) / self._default_name(),
            pages=tuple(pages),
            mode=self._mode_value,
            overwrite_policy=OverwritePolicy(self._overwrite_policy),
            stale_policy=StalePolicy(self._stale_policy),
            cancel=self._cancel_event.is_set,
        )

    def _finish(self, summary: dict) -> None:
        # TASK-036 AC ④ (R-05): publish the terminal state *before* clearing
        # `running`, so an observer that sees ``running == False`` has always
        # already seen the terminal status and signal. `changed` is re-emitted
        # after the flag clears because it is `running`'s notify signal.
        status = summary.get("status", "")
        if status == "completed":
            self._status = f"导出完成：{summary.get('output_path', '')}"
        elif status == "cancelled":
            self._status = "导出已取消；既有目标文件未被改动"
        else:
            self._status = f"导出状态：{status}"
        self.changed.emit()
        self.exportFinished.emit(summary)
        self._running = False
        self.changed.emit()

    def _fail(self, message: str) -> None:
        # TASK-036 AC ④ (R-05): same ordering as `_finish` — terminal status,
        # stale prompt, `changed`, terminal signal, then clear `running`.
        self._status = f"导出失败：{message}"
        # A failed translated export usually means stale/missing renders:
        # surface the D06 §97 prompt right away.
        self.refreshStaleWarning()
        self.changed.emit()
        self.exportFailed.emit(message)
        self._running = False
        self.changed.emit()


def _open_folder(folder: str) -> bool:
    return QDesktopServices.openUrl(QUrl.fromLocalFile(folder))


def _worker_error_text(error: Exception) -> str:
    """Human-readable text for a worker-thread failure (R-002)."""
    if isinstance(error, OSError):
        return f"导出写入失败：{error}"
    text = str(error)
    return text if text else type(error).__name__
