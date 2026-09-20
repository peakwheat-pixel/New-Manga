"""TASK-058: the app exit path drains the workbench run thread.

§11 P-10: ``main()`` used to close the shared SQLite connection right
after the event loop exits — nothing ever called
``WorkbenchViewModel.shutdown`` (zero callers in ``src/``), so a run
still executing on the worker thread was abandoned mid-write against a
closing connection.  ``bootstrap.app._shutdown_services`` is the single
exit drain: workbench first, connection second.

- the ordering contract (drain -> close) is pinned with a recording
  stub; on pre-fix trees the function does not exist (import-level
  failure);
- the real-assembly case drives a *real* VM run over *real* SQLite and
  asserts the thread is drained and the connection closed afterwards;
- pinning-only: ``WorkbenchViewModel.shutdown`` idempotence is existing
  semantics (not counted as discriminating).
"""

from __future__ import annotations

import sqlite3
import sys
import threading
import time
from pathlib import Path
from types import SimpleNamespace

# self-contained: this file must run standalone (pytest
# tests/core/test_shutdown_drain.py), not relying on another module in
# the directory being collected first to put src/ on sys.path
_SRC = Path(__file__).resolve().parents[2] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

import pytest


@pytest.fixture(scope="session")
def qapp():
    # same rationale as tests/workbench/conftest.py: the default Windows
    # platform ships the font database; offscreen does not
    from PySide6.QtGui import QGuiApplication

    app = QGuiApplication.instance() or QGuiApplication([])
    yield app


def test_shutdown_services_drains_workbench_before_closing_conn():
    """AC1: the drain runs before the shared connection closes.

    Discriminating: ``_shutdown_services`` does not exist on pre-fix
    trees (import fails); the recorded call order pins AC1 itself.
    """
    from bootstrap.app import _shutdown_services

    calls: list[str] = []
    services = SimpleNamespace(
        # TASK-060 Q-003: shutdown now reports drained; False/None would
        # make _shutdown_services skip close on purpose
        workbench=SimpleNamespace(
            shutdown=lambda: calls.append("shutdown") or True
        ),
        conn=SimpleNamespace(close=lambda: calls.append("close")),
    )
    _shutdown_services(services)
    assert calls == ["shutdown", "close"]


_TERMINAL_STATUSES = {
    "completed",
    "completed_with_failures",
    "failed",
    "cancelled",
    "interrupted",
}


def _make_library(tmp_path: Path, page_count: int):
    from PySide6.QtCore import QBuffer, QIODevice
    from PySide6.QtGui import QImage

    from application.importing.images.ports import ImportSource
    from bootstrap.app import assemble_services

    def _png() -> bytes:
        image = QImage(40, 60, QImage.Format.Format_RGB32)
        image.fill(0xFF00FF00)
        buffer = QBuffer()
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        image.save(buffer, "PNG")
        return bytes(buffer.data())

    services = assemble_services(tmp_path / "library.db", tmp_path / "managed")
    book = services.library.create_book("退出排空书")
    chapter = services.library.create_chapter(
        book.book_id,
        "退出话",
        chapter_type="webtoon",
        reading_direction="vertical",
    )
    services.importer.import_files(
        chapter.chapter_id,
        [
            ImportSource(
                filename=f"p{index}.png",
                data_provider=_png,
            )
            for index in range(1, page_count + 1)
        ],
    )
    return services, book, chapter


def test_shutdown_services_drains_an_active_real_run(qapp, tmp_path):
    """AC2: with a run executing on the worker thread, the production
    exit drain returns with the thread drained and the connection closed.

    Discriminating: the function is new (import fails pre-fix); it also
    exercises the real VM -> RunController -> worker path that the
    ordering stub cannot reach.
    """
    from bootstrap.app import _shutdown_services
    from application.translation.pipeline.executor import (
        DeterministicStepExecutor,
    )

    services, book, chapter = _make_library(tmp_path, page_count=6)
    worker_entered = threading.Event()

    def slow_step(*_args) -> None:
        worker_entered.set()
        time.sleep(1.0)

    services.pipeline._executor = DeterministicStepExecutor(on_execute=slow_step)
    vm = services.workbench
    vm.setContext(book.book_id, chapter.chapter_id, "退出排空书", "退出话")
    vm.startTranslateAll()

    # The injected first step remains active long enough to prove the
    # production drain is called on a live worker, not a completed run.
    from domain.tasks.models import PipelineRunStatus

    assert worker_entered.wait(5), "worker never entered a pipeline step"
    assert vm._run is not None, "run was never created"
    assert vm._run.status is not PipelineRunStatus.PENDING, (
        "worker never picked up the run"
    )
    assert vm._controller.is_running is True, (
        "worker finished before the shutdown drain could exercise it"
    )

    _shutdown_services(services)

    assert vm._controller.is_running is False, "worker thread was not drained"
    row = sqlite3.connect(str(tmp_path / "library.db")).execute(
        "SELECT status FROM pipeline_runs"
    ).fetchone()
    assert row is not None, "no run was started"
    assert row[0] in _TERMINAL_STATUSES, row[0]
    with pytest.raises(sqlite3.ProgrammingError):
        services.conn.execute("SELECT 1")  # connection was closed


def test_workbench_vm_shutdown_is_idempotent(qapp, tmp_path):
    """Pinning-only (existing VM semantics, not discriminating): a second
    shutdown after the drain must be a safe no-op."""
    from bootstrap.app import _shutdown_services

    services, book, chapter = _make_library(tmp_path, page_count=1)
    vm = services.workbench
    vm.setContext(book.book_id, chapter.chapter_id, "退出排空书", "退出话")
    _shutdown_services(services)
    vm.shutdown()
    assert vm._controller.is_running is False
