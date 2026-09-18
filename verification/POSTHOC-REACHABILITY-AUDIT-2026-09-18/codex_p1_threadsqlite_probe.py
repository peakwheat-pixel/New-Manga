"""Codex verification probe for Qoder's P-1 (P0) in
doc/research/PRODUCTION-REACHABILITY-AUDIT-2026-09-18.md:
"production task execution reuses a GUI-thread SQLite connection".

Part A: the REAL PipelineService built by assemble_services(), executed on a
        plain Python thread.
Part B: the REAL RunController (QThread + moveToThread + queued start) - the
        shipped path, because the workbench ViewModel hands the very same
        PipelineService instance to it.
Part C: control - the same calls on the main thread.

Read-only on production code; writes only inside a temp directory.
"""

import sys
import tempfile
import threading
from pathlib import Path

ROOT = Path(r"G:/CODEX/New Manga")
sys.path.insert(0, str(ROOT / "src"))

from PySide6.QtCore import QCoreApplication, QTimer  # noqa: E402
from PySide6.QtGui import QColor, QImage  # noqa: E402

from application.importing.images.ports import ImportSource  # noqa: E402
from bootstrap.app import assemble_services  # noqa: E402
from domain.tasks.models import CommandType, PipelineScope, ScopeType  # noqa: E402
from ui.viewmodels.workbench.run_controller import RunController  # noqa: E402


def make_png(directory: Path) -> Path:
    image = QImage(7, 5, QImage.Format.Format_RGB32)
    image.fill(QColor(10, 20, 30))
    path = directory / "source.png"
    assert image.save(str(path)), "could not write the probe page"
    return path


def assemble(directory: Path):
    services = assemble_services(directory / "library.db", directory / "managed")
    book = services.library.create_book("probe book")
    chapter = services.library.create_chapter(book.book_id, "第1话")
    source = make_png(directory)
    report = services.importer.import_files(
        chapter.chapter_id,
        [ImportSource(filename="source.png", data_provider=source.read_bytes)],
    )
    assert report.failed == (), report.failed
    return services, chapter


def plan_one(services, chapter):
    run = services.pipeline.create_run(
        CommandType.TRANSLATE_ALL,
        PipelineScope(ScopeType.CHAPTER, chapter_id=chapter.chapter_id),
    )
    planned = services.pipeline.plan_run(run.run_id)
    print("   planned status:", planned.status.value, "units:",
          sum(len(task.units) for task in planned.tasks))
    return planned


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="nmqoder-p1-"))
    app = QCoreApplication.instance() or QCoreApplication([])
    services, chapter = assemble(tmp)
    print("db:", tmp / "library.db")

    print("[A] REAL PipelineService -> plain Python thread")
    run_a = plan_one(services, chapter)
    captured = []

    def body_a():
        try:
            services.pipeline.execute_run(run_a.run_id)
            captured.append("NO-ERROR")
        except BaseException as error:  # noqa: BLE001 - probe
            captured.append(f"{type(error).__name__}: {error}")

    thread = threading.Thread(target=body_a, name="probe-thread")
    thread.start()
    thread.join()
    print("   execute_run on another thread ->", captured[0])

    print("[B] REAL RunController (QThread) -> same PipelineService instance")
    run_b = plan_one(services, chapter)
    controller = RunController()
    out = {}
    controller.runCrashed.connect(
        lambda rid, err: (out.update(crash=err), app.quit())
    )
    controller.runFinished.connect(
        lambda rid, status: (out.update(finished=status), app.quit())
    )
    controller.start(services.pipeline, run_b)
    QTimer.singleShot(20000, app.quit)
    app.exec()
    print("   signals:", out or "none within 20 s")
    try:
        stored = services.pipeline._require_run(run_b.run_id)
        print("   stored run status after the worker:", stored.status.value)
    except BaseException as error:  # noqa: BLE001 - probe
        print("   read back failed:", type(error).__name__, error)

    print("[C] control: same calls on the main thread")
    run_c = plan_one(services, chapter)
    try:
        final = services.pipeline.execute_run(run_c.run_id)
        print("   main-thread execute_run -> status:", final.status.value)
    except BaseException as error:  # noqa: BLE001 - probe
        print(f"   main-thread execute_run -> {type(error).__name__}: {error}")
    services.conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
