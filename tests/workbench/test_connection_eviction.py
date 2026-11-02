"""TASK-061 R-002 end to end: the connection registry stays bounded as
runs come and go.

The production run path executes every TRANSLATE_ALL on a *fresh* QThread
(``RunController``), and each thread lazily opens its own real connection
(TASK-060).  Pre-fix (master ``6cb0afb``) nothing ever evicted a finished
thread's connection, so N runs left ``1 + N`` open connections until the
process exited (Qoder probe ``t060_review_probe.py`` S1: 8 runs ->
registry 9).  The post-fix facade evicts through a lease sentinel whose
weakref callback fires when the owning thread's locals are torn down.

The readouts tolerate the pre-fix tree (which lacks the observability
methods) by falling back to the registry dict itself, so the same test
running pre-fix fails by showing the actual ``1 -> N+1`` growth — that
failure is the discriminating artefact, not an import error.
"""

from __future__ import annotations

import time

import workbench_helpers  # noqa: F401  (sys.path injection)

from domain.tasks.models import CommandType, PipelineScope, ScopeType

_RUNS = 4
_REGRESSION_BOUND = 2  # GUI thread + at most one not-yet-collected worker


def _assembled_library(tmp_path, page_count: int):
    from application.importing.images.ports import ImportSource
    from bootstrap.app import assemble_services

    services = assemble_services(tmp_path / "library.db", tmp_path / "managed")
    book = services.library.create_book("驱逐边界书")
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


def _make_png(width: int, height: int) -> bytes:
    from PySide6.QtCore import QBuffer, QIODevice
    from PySide6.QtGui import QImage

    image = QImage(width, height, QImage.Format.Format_RGB32)
    image.fill(0xFF00FF00)
    buffer = QBuffer()
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    image.save(buffer, "PNG")
    return bytes(buffer.data())


def _registry_size(services) -> int:
    getter = getattr(services.conn, "registry_size", None)
    if getter is not None:
        return getter()
    return len(services.conn._connections)  # pre-fix fallback (real conns)


def _open_connections(services) -> int:
    getter = getattr(services.conn, "open_connection_count", None)
    if getter is not None:
        return getter()
    return len(services.conn._connections)  # pre-fix: every entry is open


def test_registry_does_not_grow_with_completed_runs(qapp, tmp_path):
    services, chapter = _assembled_library(tmp_path, page_count=2)
    from ui.viewmodels.workbench.run_controller import RunController

    growth: list[int] = []
    for _ in range(_RUNS):
        run = services.pipeline.create_run(
            CommandType.TRANSLATE_ALL.value,
            PipelineScope(ScopeType.CHAPTER, chapter_id=chapter.chapter_id),
        )
        services.pipeline.plan_run(run.run_id)
        finished: list[str] = []
        crashed: list[str] = []
        controller = RunController()
        controller.runCrashed.connect(lambda _rid, err: crashed.append(err))
        controller.runFinished.connect(
            lambda _rid, status: finished.append(status)
        )
        controller.start(services.pipeline, run)
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline and not finished and not crashed:
            qapp.processEvents()
            time.sleep(0.01)
        assert not crashed, f"worker crashed: {crashed}"
        assert finished, "run never finished"
        controller.shutdown()
        # the worker thread is gone (shutdown drained it); give the
        # interpreter the chance to tear the thread's locals down
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline and _registry_size(services) > (
            _REGRESSION_BOUND
        ):
            qapp.processEvents()
            time.sleep(0.05)
        growth.append(_registry_size(services))

    peak_open = _open_connections(services)
    assert growth == [1] * _RUNS, (
        f"registry grew with completed runs: {growth} "
        "(pre-fix shape is [2, 3, 4, 5] for 4 runs)"
    )
    assert peak_open <= _REGRESSION_BOUND, (
        f"{peak_open} connections stayed open after {_RUNS} runs "
        "(pre-fix: 1 per completed run, all open)"
    )
