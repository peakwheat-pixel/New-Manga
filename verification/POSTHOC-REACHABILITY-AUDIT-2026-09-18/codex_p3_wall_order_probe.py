"""Codex probe: with a Region present (the API exists, only the UI entry is
missing), does a region-scoped OCR run get past P-2 and hit P-3
(no provider binding)?  This pins the wall ordering of Qoder's P-1..P-3.
"""

import sys
import tempfile
from pathlib import Path

ROOT = Path(r"G:/CODEX/New Manga")
sys.path.insert(0, str(ROOT / "src"))

from PySide6.QtCore import QCoreApplication  # noqa: E402
from PySide6.QtGui import QColor, QImage  # noqa: E402

from application.importing.images.ports import ImportSource  # noqa: E402
from bootstrap.app import assemble_services  # noqa: E402
from domain.regions.entities import BBox, RegionGeometry  # noqa: E402
from domain.tasks.models import CommandType, PipelineScope, ScopeType  # noqa: E402


def main() -> int:
    QCoreApplication.instance() or QCoreApplication([])
    tmp = Path(tempfile.mkdtemp(prefix="nmqoder-p3-"))
    services = assemble_services(tmp / "library.db", tmp / "managed")
    book = services.library.create_book("probe book")
    chapter = services.library.create_chapter(book.book_id, "第1话")
    image = QImage(7, 5, QImage.Format.Format_RGB32)
    image.fill(QColor(10, 20, 30))
    source = tmp / "source.png"
    assert image.save(str(source))
    page = services.importer.import_files(
        chapter.chapter_id,
        [ImportSource(filename="source.png", data_provider=source.read_bytes)],
    ).imported[0].page

    region = services.editing.create_region(
        page.page_id, RegionGeometry(bbox=BBox(0, 0, 4, 3))
    )
    print("region created through the application service:", region.region_id)
    run = services.pipeline.create_run(
        CommandType.OCR_REGION,
        PipelineScope(ScopeType.REGION, selected_ids=(region.region_id,)),
    )
    planned = services.pipeline.plan_run(run.run_id)
    print("planned status:", planned.status.value)
    for task in planned.tasks:
        for unit in task.units:
            print(f"   unit {unit.step_type} region={unit.region_id}"
                  f" decision={unit.decision.value} reason={unit.reason}")
    final = services.pipeline.execute_run(run.run_id)
    print("final status:", final.status.value)
    for row in services.conn.execute(
        "SELECT step_type, region_id, status, error_code, substr(error_detail, 1, 80)"
        " FROM step_runs WHERE pipeline_run_id = ? ORDER BY step_type",
        (run.run_id,),
    ).fetchall():
        print("   step_run:", tuple(row))
    services.conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
