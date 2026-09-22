"""Fresh T1.1.1 production bootstrap -> detect -> SQLite probe."""

from __future__ import annotations

import hashlib
import io
import os
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ["NEWMANGA_DETECTOR_WEIGHTS"] = str(
    Path.home() / ".cache" / "doctr" / "models" / "fast_base-688a8b34.pt"
)
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from PySide6.QtGui import QGuiApplication  # noqa: E402


def main() -> int:
    from PIL import Image, ImageDraw, ImageFont

    from application.importing.images.ports import ImportSource
    from bootstrap.app import assemble_services
    from domain.tasks.models import CommandType, PipelineScope, ScopeType, StepRunStatus

    qt_app = QGuiApplication.instance() or QGuiApplication([])
    image = Image.new("RGB", (640, 400), "white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 48)
    draw.text((80, 160), "DETECT ME", fill="black", font=font)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    source_png = buffer.getvalue()
    source_sha = hashlib.sha256(source_png).hexdigest()

    with tempfile.TemporaryDirectory(prefix="new-manga-t1111-bootstrap-") as temp:
        root = Path(temp)
        services = assemble_services(root / "library.db", root / "managed")
        try:
            book = services.library.create_book("T1.1.1 probe")
            chapter = services.library.create_chapter(book.book_id, "chapter")
            report = services.importer.import_files(
                chapter.chapter_id,
                [ImportSource(filename="page.png", data_provider=lambda: source_png)],
            )
            page = report.imported[0].page
            run = services.pipeline.create_run(
                CommandType.TRANSLATE_ALL,
                PipelineScope(ScopeType.CHAPTER, chapter_id=chapter.chapter_id),
            )
            services.pipeline.plan_run(run.run_id)
            executed = services.pipeline.execute_run(run.run_id)
            detect_step = executed.step_runs[0]
            regions = services.editing.list_regions(page.page_id)
            revisions = services.conn.execute(
                "SELECT region_id, revision_no, origin FROM region_revisions "
                "WHERE region_id IN (SELECT region_id FROM regions WHERE page_id = ?) "
                "ORDER BY region_id, revision_no",
                (page.page_id,),
            ).fetchall()
            stored_source_sha = services.conn.execute(
                "SELECT source_hash FROM pages WHERE page_id = ?", (page.page_id,)
            ).fetchone()["source_hash"]

            if detect_step.status is not StepRunStatus.COMPLETED:
                raise AssertionError(f"detect step status={detect_step.status}")
            if detect_step.error_code is not None:
                raise AssertionError(f"detect error={detect_step.error_code}")
            if not regions or not revisions:
                raise AssertionError("production detect did not persist Region/revision")
            if stored_source_sha != source_sha:
                raise AssertionError("source hash changed during production detect")
            print(
                "BOOTSTRAP_DETECT_SQLITE_OK "
                f"regions={len(regions)} revisions={len(revisions)} "
                f"detect_status={detect_step.status.value} "
                f"source_sha={stored_source_sha}"
            )
        finally:
            services.conn.close()
            qt_app.quit()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
