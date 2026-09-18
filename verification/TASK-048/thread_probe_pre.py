"""TASK-048 AC ② probe: the production run path over a real SQLite file.

Runs the real ``assemble_services`` + real ``RunController`` (QThread) and
executes one ``TRANSLATE_ALL`` command on the worker thread, then prints the
outcome.  Run it against both trees with the same interpreter:

    python verification/TASK-048/thread_probe_pre.py [tree_root]

- pre-fix tree (connection bound to the startup thread): ``OUTCOME=crashed``
  with ``sqlite3.ProgrammingError: SQLite objects created in a thread ...``
- post-fix tree: ``OUTCOME=finished`` with a terminal status.
"""

from __future__ import annotations

import sys
import tempfile
import time
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parents[2]
ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else DEFAULT_ROOT
sys.path.insert(0, str(ROOT / "src"))

from PySide6.QtCore import QBuffer, QIODevice  # noqa: E402
from PySide6.QtGui import QGuiApplication, QImage  # noqa: E402

from application.importing.images.ports import ImportSource  # noqa: E402
from bootstrap.app import assemble_services  # noqa: E402
from domain.tasks.models import CommandType, PipelineScope, ScopeType  # noqa: E402
from ui.viewmodels.workbench.run_controller import RunController  # noqa: E402


def make_png(width: int, height: int) -> bytes:
    image = QImage(width, height, QImage.Format.Format_RGB32)
    image.fill(0xFF00FF00)
    buffer = QBuffer()
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    image.save(buffer, "PNG")
    return bytes(buffer.data())


def main() -> int:
    app = QGuiApplication.instance() or QGuiApplication([])
    # mkdtemp, not TemporaryDirectory: the assembly keeps its WAL-mode
    # connection open for the process lifetime, so Windows cannot delete
    # the directory while we still hold it — the OS temp cleaner gets it.
    tmp = Path(tempfile.mkdtemp(prefix="task048-probe-"))
    services = assemble_services(tmp / "library.db", tmp / "managed")
    book = services.library.create_book("探针书")
    chapter = services.library.create_chapter(
        book.book_id, "条漫话", chapter_type="webtoon", reading_direction="vertical"
    )
    services.importer.import_files(
        chapter.chapter_id,
        [
                ImportSource(
                    filename=f"p{i}.png",
                    data_provider=lambda i=i: make_png(40, 60),
                )
            for i in (1, 2)
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
    controller.runCrashed.connect(lambda rid, err: crashed.append(err))
    controller.runFinished.connect(lambda rid, st: finished.append(st))
    controller.start(services.pipeline, run)
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline and not finished and not crashed:
        app.processEvents()
        time.sleep(0.01)
    controller.shutdown()

    if crashed:
        print(f"OUTCOME=crashed | error={crashed[0][:160]}")
        return 1
    if not finished:
        print("OUTCOME=timeout | neither finished nor crashed within 30s")
        return 2
    print(f"OUTCOME=finished | status={finished[0]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
