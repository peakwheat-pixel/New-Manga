"""Codex verification probe for Qoder's P-2 (P0) and P-6 (P1) in
doc/research/PRODUCTION-REACHABILITY-AUDIT-2026-09-18.md.

P-2: a page-level `ocr` unit carries no region_id, and handle_ocr calls
     _require_region() before _chain(), so the step fails with
     ProviderInputError("... requires a Region target") even with providers
     configured.  Measured here from the real run's persisted step_runs rows.
P-6: the workbench viewer's catalog refuses every non-"original" mode while the
     reader catalog resolves the page's current TRANSLATED artifact, for the
     same page and the same Managed Copy.

Main-thread execution on purpose: the worker path is covered by the P-1 probe.
"""

import sys
import tempfile
from pathlib import Path

ROOT = Path(r"G:/CODEX/New Manga")
sys.path.insert(0, str(ROOT / "src"))

from PySide6.QtCore import QCoreApplication  # noqa: E402
from PySide6.QtGui import QColor, QImage  # noqa: E402

from application.importing.images.ports import ImportSource  # noqa: E402
from bootstrap.app import (  # noqa: E402
    _ManagedPageCatalog,
    _ManagedReaderCatalog,
    assemble_services,
)
from domain.tasks.models import CommandType, PipelineScope, ScopeType  # noqa: E402
from infrastructure.providers.step_writes import ArtifactStepWriter  # noqa: E402
from infrastructure.rendering.locator import SqlitePageArtifactLocator  # noqa: E402


def make_png(directory: Path, name: str = "source.png", size=(7, 5)) -> Path:
    image = QImage(size[0], size[1], QImage.Format.Format_RGB32)
    image.fill(QColor(10, 20, 30))
    path = directory / name
    assert image.save(str(path))
    return path


def main() -> int:
    QCoreApplication.instance() or QCoreApplication([])
    tmp = Path(tempfile.mkdtemp(prefix="nmqoder-p2p6-"))
    services = assemble_services(tmp / "library.db", tmp / "managed")
    book = services.library.create_book("probe book")
    chapter = services.library.create_chapter(book.book_id, "第1话")
    source = make_png(tmp)
    report = services.importer.import_files(
        chapter.chapter_id,
        [ImportSource(filename="source.png", data_provider=source.read_bytes)],
    )
    page = report.imported[0].page
    print("page:", page.page_id)

    print("[P-2] real run, main thread (worker path is the P-1 probe)")
    run = services.pipeline.create_run(
        CommandType.TRANSLATE_ALL,
        PipelineScope(ScopeType.CHAPTER, chapter_id=chapter.chapter_id),
    )
    final = services.pipeline.execute_run(services.pipeline.plan_run(run.run_id).run_id)
    print("   run status:", final.status.value)
    rows = services.conn.execute(
        "SELECT step_type, region_id, status, error_code, substr(error_detail, 1, 70)"
        " FROM step_runs WHERE pipeline_run_id = ? ORDER BY step_type",
        (run.run_id,),
    ).fetchall()
    for step_type, region_id, status, code, detail in rows:
        print(f"   {step_type:<12} region={region_id} status={status}"
              f" code={code} detail={detail}")
    codes = sorted({row[3] for row in rows})
    print("   distinct error codes:", codes)

    print("[P-6] same page, two catalogs")
    writer = ArtifactStepWriter(services.conn, services.storage)
    prepared = writer.prepare_revision(
        page_id=page.page_id,
        artifact_type="translated",
        payload=make_png(tmp, "translated.png", (9, 6)).read_bytes(),
        mime_type="image/png",
        width=9,
        height=6,
    )
    writer.adopt_current(
        artifact_id=prepared.artifact_id,
        revision_id=prepared.revision_id,
        expected_current_revision_id=prepared.previous_revision_id,
    )
    workbench = _ManagedPageCatalog(services.repository, services.storage)
    reader = _ManagedReaderCatalog(
        services.repository, services.storage, SqlitePageArtifactLocator(services.conn)
    )
    reader_rows = {row.page_id: row for row in reader.list_pages(chapter.chapter_id)}
    print("   workbench image_url(original)  :", bool(workbench.image_url(page.page_id, "original")))
    print("   workbench image_url(translated):", repr(workbench.image_url(page.page_id, "translated")))
    print("   workbench image_url(compare)   :", repr(workbench.image_url(page.page_id, "compare")))
    print("   reader translated_path present :", bool(reader_rows[page.page_id].translated_path))
    services.conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
