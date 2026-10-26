"""TASK-048: the production run path over real SQLite, on the worker thread.

§11 P-1: ``assemble_services`` opened the single SQLite connection on the
startup (GUI) thread while ``RunController`` executes ``PipelineService.
execute_run`` on a QThread worker — the first store write raised
``sqlite3.ProgrammingError`` and was swallowed into ``runCrashed``
(invisible: ``commandError`` has no QML consumer until TASK-052), leaving
the run stuck at ``running``.  These tests drive the *real* assembly, a
*real* SQLite file and the *real* ``RunController`` end to end, and make
the AC ① concurrency argument (module docstring of
``infrastructure/sqlite/connection.py``) observable:

- AC ④/discriminating: the run completes to a terminal status and the
  terminal status lands in the database; on the pre-fix tree the first
  worker ``_persist`` crashes the run (``runCrashed`` + row stuck at
  ``running``), so these assertions fail there;
- AC ①: a main thread that keeps reading *and writing* the library while
  the worker run executes does not crash and does not corrupt either
  write stream;
- AC ③: ``assemble_services`` reaps a run left ``running`` by a previous
  process to ``interrupted`` at startup.
"""

from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path

import workbench_helpers  # noqa: F401  (sys.path injection)

from PySide6.QtCore import QBuffer, QIODevice
from PySide6.QtGui import QImage

from domain.tasks.models import CommandType, PipelineScope, ScopeType


def _make_png(width: int, height: int) -> bytes:
    image = QImage(width, height, QImage.Format.Format_RGB32)
    image.fill(0xFF00FF00)
    buffer = QBuffer()
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    image.save(buffer, "PNG")
    return bytes(buffer.data())


_TERMINAL_STATUSES = {
    "completed",
    "completed_with_failures",
    "failed",
    "cancelled",
    "interrupted",
}


def _assembled_library(tmp_path: Path, page_count: int):
    from application.importing.images.ports import ImportSource
    from bootstrap.app import assemble_services

    services = assemble_services(tmp_path / "library.db", tmp_path / "managed")
    book = services.library.create_book("跨线程装配书")
    chapter = services.library.create_chapter(
        book.book_id,
        "条漫话",
        chapter_type="webtoon",
        reading_direction="vertical",
    )
    services.importer.import_files(
        chapter.chapter_id,
        [
            ImportSource(
                filename=f"p{index}.png",
                data_provider=lambda index=index: _make_png(40, 60),
            )
            for index in range(1, page_count + 1)
        ],
    )
    return services, chapter


def _planned_run(services, chapter):
    run = services.pipeline.create_run(
        CommandType.TRANSLATE_ALL.value,
        PipelineScope(ScopeType.CHAPTER, chapter_id=chapter.chapter_id),
    )
    services.pipeline.plan_run(run.run_id)
    return run


def _db_run_status(db_path: Path, run_id: str) -> str | None:
    """Read the run's persisted status through an independent connection."""
    conn = sqlite3.connect(str(db_path))
    try:
        row = conn.execute(
            "SELECT status FROM pipeline_runs WHERE run_id = ?", (run_id,)
        ).fetchone()
    finally:
        conn.close()
    return row[0] if row else None


def test_run_completes_on_worker_thread_over_real_sqlite(qapp, tmp_path):
    """AC ②/④: no ProgrammingError on the worker; the run reaches a
    terminal status and the database records it."""
    services, chapter = _assembled_library(tmp_path, page_count=2)
    run = _planned_run(services, chapter)

    crashed: list[str] = []
    finished: list[str] = []
    from ui.viewmodels.workbench.run_controller import RunController

    controller = RunController()
    controller.runCrashed.connect(lambda run_id, error: crashed.append(error))
    controller.runFinished.connect(
        lambda run_id, status: finished.append(status)
    )
    controller.start(services.pipeline, run)
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline and not finished and not crashed:
        qapp.processEvents()
        time.sleep(0.01)

    assert not crashed, f"worker crashed: {crashed}"
    assert finished, "run never finished"
    assert finished[0] in _TERMINAL_STATUSES, finished

    # AC ④: the terminal status is *in the database*, read back through a
    # fresh connection (the in-memory run object could hide a lost write).
    assert _db_run_status(tmp_path / "library.db", run.run_id) == finished[0]
    controller.shutdown()


def test_worker_run_and_main_thread_access_coexist(qapp, tmp_path):
    """AC ① negative case: while the worker executes the run, the main
    thread keeps issuing reads *and writes* on the same connection; both
    streams survive without exceptions and land their rows."""
    services, chapter = _assembled_library(tmp_path, page_count=8)
    run = _planned_run(services, chapter)

    crashed: list[str] = []
    finished: list[str] = []
    from ui.viewmodels.workbench.run_controller import RunController

    controller = RunController()
    controller.runCrashed.connect(lambda run_id, error: crashed.append(error))
    controller.runFinished.connect(
        lambda run_id, status: finished.append(status)
    )
    controller.start(services.pipeline, run)

    # main-thread write stream while the worker writes the pipeline tables
    created: list[str] = []
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline and not finished and not crashed:
        qapp.processEvents()
        book = services.library.create_book(f"并发书 {len(created)}")
        created.append(book.book_id)
        assert services.library.get_chapter(chapter.chapter_id) is not None
        assert services.library.list_books(), "main-thread read broke"
        time.sleep(0.002)

    assert not crashed, f"worker crashed under concurrency: {crashed}"
    assert finished, "run never finished under concurrency"
    assert finished[0] in _TERMINAL_STATUSES

    # both write streams landed: every concurrent book is durable, and the
    # run's terminal status is in the database
    conn = sqlite3.connect(str(tmp_path / "library.db"))
    try:
        book_rows = conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]
        run_row = conn.execute(
            "SELECT status FROM pipeline_runs WHERE run_id = ?", (run.run_id,)
        ).fetchone()
    finally:
        conn.close()
    assert book_rows >= 1 + len(created)
    assert run_row is not None and run_row[0] == finished[0]
    controller.shutdown()


def test_startup_recovers_runs_left_running(qapp, tmp_path):
    """AC ③: a run left ``running`` by a previous process becomes
    ``interrupted`` when the production assembly starts up again."""
    services, chapter = _assembled_library(tmp_path, page_count=1)
    run = _planned_run(services, chapter)

    # simulate the crash legacy: the persisted run *snapshot* says running
    # (on pre-fix trees a worker crash is exactly what left rows in this
    # state — the run_json replay is the store's source of truth)
    conn = sqlite3.connect(str(tmp_path / "library.db"))
    try:
        row = conn.execute(
            "SELECT run_json FROM pipeline_runs WHERE run_id = ?", (run.run_id,)
        ).fetchone()
        snapshot = json.loads(row[0])
        snapshot["status"] = "running"
        with conn:
            conn.execute(
                "UPDATE pipeline_runs SET status = 'running', run_json = ?"
                " WHERE run_id = ?",
                (json.dumps(snapshot), run.run_id),
            )
    finally:
        conn.close()

    # a fresh production start must reap it before anything observes it
    from bootstrap.app import assemble_services

    assemble_services(tmp_path / "library.db", tmp_path / "managed")
    assert _db_run_status(tmp_path / "library.db", run.run_id) == "interrupted"
