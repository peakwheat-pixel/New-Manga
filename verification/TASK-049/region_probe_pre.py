"""TASK-049 AC ③ probe: the page-level input face, before vs after.

Runs the real ``assemble_services`` assembly, imports a page and executes
one ``TRANSLATE_ALL`` run on the GUI thread (thread ownership is TASK-048's
concern), then prints every executed step with its terminal status and
error code:

- pre-fix tree: ``ocr`` fails with ``INVALID_INPUT`` —
  "step 'ocr' requires a Region target" (the §11 P-0 signature);
- post-fix tree: a leading ``detect`` step runs and fails with
  ``PROVIDER_NOT_CONFIGURED`` (no detector is wired in this window), and no
  step reports the missing-Region input error.

    python verification/TASK-049/region_probe_pre.py [tree_root]
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


def make_png(width: int, height: int) -> bytes:
    image = QImage(width, height, QImage.Format.Format_RGB32)
    image.fill(0xFF00FF00)
    buffer = QBuffer()
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    image.save(buffer, "PNG")
    return bytes(buffer.data())


def main() -> int:
    app = QGuiApplication.instance() or QGuiApplication([])
    tmp = Path(tempfile.mkdtemp(prefix="task049-probe-"))
    services = assemble_services(tmp / "library.db", tmp / "managed")
    book = services.library.create_book("探针书")
    chapter = services.library.create_chapter(
        book.book_id, "条漫话", chapter_type="webtoon", reading_direction="vertical"
    )
    services.importer.import_files(
        chapter.chapter_id,
        [ImportSource(filename="p1.png", data_provider=lambda: make_png(40, 60))],
    )
    run = services.pipeline.create_run(
        CommandType.TRANSLATE_ALL.value,
        PipelineScope(ScopeType.CHAPTER, chapter_id=chapter.chapter_id),
    )
    services.pipeline.plan_run(run.run_id)
    planned = [unit.step_type for unit in run.tasks[0].units]
    deadline = time.monotonic() + 30
    executed = services.pipeline.execute_run(run.run_id)
    del deadline, app  # execute_run is synchronous on this probe

    print(f"PLANNED_UNITS={planned}")
    for step in executed.step_runs:
        print(
            f"STEP {step.step_type} -> {step.status.value}"
            f" code={step.error_code!r}"
        )
    print(f"RUN_FINAL={executed.status.value}")
    invalid = [
        step
        for step in executed.step_runs
        if step.error_code == "INVALID_INPUT"
    ]
    print(f"MISSING_REGION_INPUT_FAILURES={len(invalid)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
