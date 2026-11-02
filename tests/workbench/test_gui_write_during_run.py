"""TASK-060 AC ④: a run survives GUI writes issued *during* its execution.

Same production shape as the Qoder B-segment probe (post-hoc overturn
evidence): a real run executes on the worker thread while the GUI thread
keeps issuing real writes — here through BOTH transaction shapes the
workbench actually uses: explicit ``BEGIN IMMEDIATE`` blocks (region
commits) and implicit ``with conn:`` blocks (library writes).

Pre-fix (shared connection) this raced: GUI commits/rollbacks landed in
the worker's transaction and killed runs mid-flight, silently (3/10
twenty-second rounds in the probe; ``test_run_thread_e2e``'s sibling was
recorded "flaky" for exactly this).  Post-fix the two threads own
separate connections; the assertions below must hold every round:

- ``runCrashed`` never fires;
- the run reaches a terminal status and the database records it;
- every successful GUI write is readable back through an independent
  connection (AC ②'s read-back rule, sampled at the end).

Discriminating power: probabilistic pre-fix (documented; the
deterministic discriminators live in
``tests/core/test_connection_ownership.py``), so this case is the
end-to-end stability contract — run ≥10 rounds for AC ⑧ evidence.
"""

from __future__ import annotations

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


def test_run_survives_gui_explicit_and_implicit_writes(qapp, tmp_path):
    from application.importing.images.ports import ImportSource
    from bootstrap.app import assemble_services
    from ui.viewmodels.workbench.run_controller import RunController

    services = assemble_services(tmp_path / "library.db", tmp_path / "managed")
    book = services.library.create_book("交错存活书")
    chapter = services.library.create_chapter(
        book.book_id,
        "交错话",
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
            for index in range(1, 9)
        ],
    )
    run = services.pipeline.create_run(
        CommandType.TRANSLATE_ALL.value,
        PipelineScope(ScopeType.CHAPTER, chapter_id=chapter.chapter_id),
    )
    services.pipeline.plan_run(run.run_id)

    crashed: list[str] = []
    finished: list[str] = []
    controller = RunController()
    controller.runCrashed.connect(lambda run_id, error: crashed.append(error))
    controller.runFinished.connect(
        lambda run_id, status: finished.append(status)
    )
    controller.start(services.pipeline, run)

    written: list[str] = []
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline and not finished and not crashed:
        qapp.processEvents()
        # implicit transaction shape (library write)
        written.append(services.library.create_book(f"并发书 {len(written)}").book_id)
        # explicit BEGIN IMMEDIATE shape (region-commit shape, regions table)
        services.conn.execute("BEGIN IMMEDIATE")
        services.conn.execute(
            "UPDATE books SET updated_at = updated_at WHERE book_id = ?",
            (book.book_id,),
        )
        services.conn.commit()
        time.sleep(0.001)

    assert not crashed, f"run was killed by GUI writes: {crashed}"
    assert finished, "run never finished"
    assert finished[0] in _TERMINAL_STATUSES, finished

    judge = sqlite3.connect(str(tmp_path / "library.db"))
    try:
        db_status = judge.execute(
            "SELECT status FROM pipeline_runs WHERE run_id = ?", (run.run_id,)
        ).fetchone()
        assert db_status is not None and db_status[0] == finished[0]
        # AC ②: writer returned success ⇒ independent connection reads back
        for index, book_id in enumerate(written):
            if index % 50:  # sample
                continue
            row = judge.execute(
                "SELECT COUNT(*) FROM books WHERE book_id = ?", (book_id,)
            ).fetchone()
            assert row[0] == 1, f"GUI write {book_id} reported ok but is gone"
    finally:
        judge.close()

    controller.shutdown()
