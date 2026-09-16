"""ViewModel tests for the reader/export slice (TASK-015).

Runs on PySide6; skips with an explicit reason when the toolkit is not
installed in the active interpreter.
"""

from __future__ import annotations

import time
from pathlib import Path

import pytest
from conftest import requires_pyside6
from reading_export_helpers import (
    make_pages,
    make_reading_service,
    make_service,
    to_export_pages,
)

pytest.importorskip("PySide6", reason="PySide6 not installed in this interpreter")

import time as _time  # noqa: E402

from PySide6.QtCore import QUrl  # noqa: E402

from application.export import ExportPage, ExportService  # noqa: E402
from ui.viewmodels.export.viewmodel import ExportViewModel  # noqa: E402
from ui.viewmodels.reader.viewmodel import ReaderViewModel  # noqa: E402

pytestmark = pytest.mark.usefixtures("qapp")  # timers/signals need an app instance


def pump_until(app, condition, timeout=5.0):
    """Run the event loop until ``condition()`` or timeout.

    ``QSignalSpy.wait`` is avoided on purpose: on PySide6 6.11/Windows its
    internal loop can starve freshly started Python threads, so the
    export worker would never run. Polling ``processEvents`` keeps both
    the thread scheduler and queued signals alive.
    """
    deadline = _time.monotonic() + timeout
    while _time.monotonic() < deadline:
        app.processEvents()
        if condition():
            return True
        _time.sleep(0.02)
    return condition()


class Catalog:
    """ReaderPageCatalog-shaped fake over a fixed page list."""

    def __init__(self, pages):
        self.pages = pages

    def list_pages(self, chapter_id):
        return list(self.pages)


@pytest.fixture()
def reading(tmp_path):
    return make_reading_service(tmp_path)


@pytest.fixture()
def pages(tmp_path):
    return make_pages(tmp_path, count=3, translated=True)


@pytest.fixture()
def reader(reading, pages):
    return ReaderViewModel(reading, Catalog(pages))


@pytest.fixture()
def export_service(tmp_path):
    return make_service(tmp_path)


# ----------------------------------------------------------------------
# ReaderViewModel
# ----------------------------------------------------------------------


@requires_pyside6
def test_reader_open_chapter_exposes_state(reader):
    reader.openChapter("b", "c", "第1话", "paged", "rtl")
    assert reader.hasChapter
    assert reader.chapterTitle == "第1话"
    assert reader.mode == "original"
    assert reader.direction == "rtl"
    assert reader.pageNumber == 1
    assert reader.pageCount == 3
    assert reader.sourcePath.endswith("page_00_第0页.png")
    assert reader.canGoNext and not reader.canGoPrevious


@requires_pyside6
def test_reader_missing_translation_message(reading, tmp_path):
    plain = make_pages(tmp_path / "plain", count=1)
    vm = ReaderViewModel(reading, Catalog(plain))
    vm.openChapter("b", "c", "第1话", "paged", "ltr")
    vm.setMode("translated")
    assert "译图缺失" in vm.statusMessage
    vm.setMode("original")
    assert vm.statusMessage == ""


@requires_pyside6
def test_reader_settles_elapsed_time_into_service(reader, reading):
    reader.openChapter("b", "c", "第1话", "paged", "rtl")
    reader._last_settle = time.monotonic() - 2.0  # simulate 2s of reading
    reader.settleReadingTime()
    assert reading.progress.total_read_seconds >= 2.0
    reader.closeReader()
    assert reading.progress.total_read_seconds >= 2.0


@requires_pyside6
def test_reader_summary_reflects_book_progress(reader):
    reader.openChapter("b", "c", "第1话", "paged", "rtl")
    reader.nextPage()
    summary = reader.bookSummary
    assert summary["has_progress"] is True
    assert summary["last_chapter_id"] == "c"
    assert summary["progress_percent"] > 0


@requires_pyside6
def test_open_exporter_lazy_singleton(tmp_path, reading, pages):
    without_export = ReaderViewModel(reading, Catalog(pages))
    assert without_export.openExporter() is None, "no export service injected yet"

    service = ExportService(make_service(tmp_path)._store)
    vm = ReaderViewModel(reading, Catalog(pages), export_service=service)
    controller = vm.openExporter()
    assert isinstance(controller, ExportViewModel)
    assert vm.exportController is controller
    assert vm.openExporter() is controller  # same instance reused


# ----------------------------------------------------------------------
# ExportViewModel
# ----------------------------------------------------------------------


def make_export_vm(tmp_path, pages, service, **kwargs):
    providers = to_export_pages(pages)
    return ExportViewModel(
        service,
        lambda: list(providers),
        book_id="b",
        chapter_id="c",
        output_dir=str(tmp_path / "out"),
        **kwargs,
    )


def make_stale_and_missing(vm):
    """Rewire the provider so page 0 is stale and page 1 lacks a render."""
    providers = list(vm._pages_provider())
    providers[0] = ExportPage(
        page_id="p0",
        filename=providers[0].filename,
        source_provider=providers[0].source_provider,
        translated_provider=providers[0].translated_provider,
        translated_revision_id="old",
        current_translated_revision_id="new",  # stale
    )
    providers[1] = ExportPage(
        page_id="p1",
        filename=providers[1].filename,
        source_provider=providers[1].source_provider,
        translated_provider=None,  # 缺译图
    )
    vm._pages_provider = lambda: providers


@requires_pyside6
def test_export_vm_defaults_and_setters(tmp_path, pages, export_service):
    vm = make_export_vm(tmp_path, pages, export_service)
    assert vm.format == "zip"
    assert vm.mode == "translated"
    assert vm.overwritePolicy == "overwrite"
    assert vm.stalePolicy == "abort"
    assert vm.pageCount == 3
    assert "3 页" in vm.scopeSummary
    assert vm.outputPath.endswith(".zip")

    vm.setFormat("pdf")
    assert vm.outputPath.endswith(".pdf")
    vm.setOutputPath(QUrl.fromLocalFile(str(tmp_path / "out" / "书名.zip")).toString())
    assert vm.outputPath.endswith("书名.zip")  # Unicode naming stays intact
    vm.setOverwritePolicy("auto_rename")
    assert vm.overwritePolicy == "auto_rename"
    vm.setMode("original")
    assert vm.mode == "original"


@requires_pyside6
def test_stale_warning_flow(tmp_path, pages, export_service):
    vm = make_export_vm(tmp_path, pages, export_service)
    vm.refreshStaleWarning()
    assert not vm.staleWarningVisible  # all renders current

    vm.setMode("translated")
    make_stale_and_missing(vm)
    vm.refreshStaleWarning()
    assert vm.staleWarningVisible
    assert "不是最新渲染" in vm.staleWarningText
    assert "先重新渲染" in vm.staleWarningText

    # explicit continue flips the message into a confirmation
    vm.setStalePolicy("continue")
    assert vm.staleWarningVisible
    assert "继续导出现有版本" in vm.staleWarningText


@requires_pyside6
def test_start_export_completes_and_updates_history(qapp, tmp_path, pages, export_service):
    vm = make_export_vm(tmp_path, pages, export_service)
    vm.setOutputPath(str(tmp_path / "out" / "result.zip"))
    finished = []
    vm.exportFinished.connect(lambda summary: finished.append(summary))
    vm.startExport()
    assert pump_until(qapp, lambda: not vm.running)
    assert len(finished) == 1
    assert finished[0]["status"] == "completed"
    assert "导出完成" in vm.statusMessage
    assert len(vm.history) == 1
    assert (tmp_path / "out" / "result.zip").exists()


@requires_pyside6
def test_start_export_stale_abort_surfaces_failure(qapp, tmp_path, pages, export_service):
    vm = make_export_vm(tmp_path, pages, export_service)
    make_stale_and_missing(vm)
    failures = []
    vm.exportFailed.connect(lambda message: failures.append(message))
    vm.startExport()
    assert pump_until(qapp, lambda: not vm.running)
    assert len(failures) == 1
    assert "不是最新渲染" in failures[0]
    assert vm.staleWarningVisible


@requires_pyside6
def test_cancel_export_reports_and_keeps_ui_consistent(qapp, tmp_path, pages, export_service):
    vm = make_export_vm(tmp_path, pages, export_service)
    vm.setOutputPath(str(tmp_path / "out" / "x.zip"))
    vm.startExport()
    vm.cancelExport()  # cooperative flag; may land before or after completion
    assert pump_until(qapp, lambda: not vm.running)
    if (tmp_path / "out" / "x.zip").exists():
        assert vm.statusMessage.startswith("导出完成")
    else:
        # cancelled before any page was written: no file, clear message
        assert "取消" in vm.statusMessage or "导出失败" in vm.statusMessage


@requires_pyside6
def test_repeat_export_uses_history_settings(qapp, tmp_path, pages, export_service):
    opened = []
    vm = make_export_vm(
        tmp_path,
        pages,
        export_service,
        folder_opener=lambda folder: opened.append(folder) or True,
    )
    vm.setOutputPath(str(tmp_path / "out" / "r.zip"))
    vm.startExport()
    assert pump_until(qapp, lambda: not vm.running)
    assert vm.statusMessage.startswith("导出完成")
    export_id = vm.history[0]["export_id"]

    vm.repeatExport(export_id)
    assert pump_until(qapp, lambda: not vm.running)
    # repeat keeps the snapshot's overwrite policy (overwrite): the same
    # target is replaced and a second history row lands.
    assert vm.statusMessage.startswith("导出完成")
    assert len(vm.history) == 2

    vm.openOutputFolder()
    assert opened and opened[0] == str(tmp_path / "out")


@requires_pyside6
def test_repeat_export_os_error_surfaces_failure_not_stuck(qapp, tmp_path, pages, export_service):
    """R-002 regression: an OSError inside repeat() must surface via
    exportFailed and reset `running` instead of killing the worker thread
    silently (the state used to stick at 正在按相同设置导出… forever)."""
    vm = make_export_vm(tmp_path, pages, export_service)
    vm.setMode("original")  # snapshot mode=original keeps the stale check out of the way
    vm.setOutputPath(str(tmp_path / "out" / "r.zip"))
    vm.startExport()
    assert pump_until(qapp, lambda: not vm.running)
    export_id = vm.history[0]["export_id"]

    good = vm._pages_provider()

    def broken_pages():
        rows = list(good)
        rows[0] = ExportPage(
            page_id=rows[0].page_id,
            filename=rows[0].filename,
            source_provider=lambda: (_ for _ in ()).throw(OSError("disk full")),
        )
        return rows

    vm._pages_provider = broken_pages
    failures = []
    vm.exportFailed.connect(lambda message: failures.append(message))
    vm.repeatExport(export_id)
    assert pump_until(qapp, lambda: not vm.running), "running must reset"
    assert len(failures) == 1 and "disk full" in failures[0]


@requires_pyside6
def test_export_without_pages_surfaces_status(qapp, tmp_path, export_service):
    vm = ExportViewModel(
        export_service,
        lambda: [],
        book_id="b",
        chapter_id="c",
        output_dir=str(tmp_path / "out"),
    )
    failures = []
    vm.exportFailed.connect(lambda message: failures.append(message))
    vm.startExport()
    assert pump_until(qapp, lambda: not vm.running)
    assert vm.pageCount == 0
    assert len(failures) == 1
