"""TASK-050 AC ③ probe: bind a local deterministic provider through the
*application write face* and watch an OCR_REGION command advance past
``PROVIDER_NOT_CONFIGURED`` over the real production assembly.

Runs against whatever tree it lives in:
- post-fix tree: WRITE_FACE=ok, ocr step COMPLETED, echo text landed.
- pre-fix tree:  ``pipeline_defaults`` does not exist on AppServices ->
  WRITE_FACE=unavailable, nothing can bind, ocr dies PROVIDER_NOT_CONFIGURED
  (the pre-TASK-050 wall, reproduced).
"""

import sqlite3
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from bootstrap.app import assemble_services  # noqa: E402
from domain.regions.entities import BBox, RegionGeometry, RegionOrigin  # noqa: E402
from domain.tasks.models import CommandType, PipelineScope, ScopeType  # noqa: E402
from infrastructure.providers.registry import ProviderDescriptor  # noqa: E402
from ports.ocr.ports import OcrResult  # noqa: E402


class EchoOcr:
    provider_id = "probe-local-ocr"
    provider_type = "deterministic-probe"

    def recognize(self, request) -> OcrResult:
        return OcrResult(
            region_id=request.region_id,
            text="probe-echo",
            provider_id=self.provider_id,
            provider_type=self.provider_type,
        )


def make_png(width: int, height: int) -> bytes:
    from PySide6.QtCore import QBuffer, QIODevice
    from PySide6.QtGui import QImage

    image = QImage(width, height, QImage.Format.Format_RGB32)
    image.fill(0xFF00FF00)
    buffer = QBuffer()
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    image.save(buffer, "PNG")
    return bytes(buffer.data())


def main() -> int:
    root = Path(tempfile.mkdtemp(prefix="task050-probe-"))
    services = assemble_services(root / "library.db", root / "managed")
    try:
        services.providers.registry.register(
            ProviderDescriptor(
                provider_id="probe-local-ocr",
                provider_type="deterministic-probe",
                capabilities=frozenset({"ocr"}),
                note="TASK-050 probe-local provider",
            ),
            EchoOcr,
        )
        try:
            services.pipeline_defaults.save_provider_binding("ocr", "probe-local-ocr")
            print("WRITE_FACE=ok")
        except AttributeError:
            print("WRITE_FACE=unavailable")

        book = services.library.create_book("探针书")
        chapter = services.library.create_chapter(book.book_id, "第1话")
        report = services.importer.import_files(
            chapter.chapter_id,
            [
                __import__(
                    "application.importing.images.ports", fromlist=["ImportSource"]
                ).ImportSource(
                    filename="p1.png",
                    data_provider=lambda: make_png(40, 60),
                )
            ],
        )
        page_id = report.imported[0].page.page_id
        geometry = RegionGeometry(
            bbox=BBox(4, 4, 30, 40),
            polygon=((4, 4), (34, 4), (34, 44), (4, 44)),
        )
        region = services.editing.create_region(
            page_id, geometry, reading_order=1, origin=RegionOrigin.USER
        )

        run = services.pipeline.create_run(
            CommandType.OCR_REGION,
            PipelineScope(ScopeType.REGION, selected_ids=(region.region_id,)),
        )
        services.pipeline.plan_run(run.run_id)
        print(f"PROVIDER_BINDING_SNAPSHOT={run.provider_binding_snapshot}")
        run = services.pipeline.execute_run(run.run_id)
        ocr = next(s for s in run.step_runs if s.step_type == "ocr")
        print(
            f"STEP ocr -> {ocr.status.value} code={ocr.error_code!r}"
        )
        print(f"RUN_FINAL={run.status.value}")

        revisions = services.conn.execute(
            "SELECT snapshot_json FROM region_revisions WHERE region_id = ?",
            (region.region_id,),
        ).fetchall()
        landed = any("probe-echo" in (row[0] or "") for row in revisions)
        print(f"ECHO_LANDED={int(landed)}")
        return 0
    finally:
        try:
            services.conn.close()
        except sqlite3.Error:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
