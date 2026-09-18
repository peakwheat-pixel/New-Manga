"""TASK-051 probe: the workbench viewer's three modes over one page and
one Managed Copy. Post-fix, ``translated`` resolves the current
TRANSLATED revision (same file the reader resolves) and ``compare``
shows the original for the side-by-side left pane; pre-fix both
returned "" (the P-6 finding)."""

import sqlite3
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from bootstrap.app import assemble_services  # noqa: E402
from infrastructure.providers.step_writes import ArtifactStepWriter  # noqa: E402


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
    root = Path(tempfile.mkdtemp(prefix="task051-probe-"))
    services = assemble_services(root / "library.db", root / "managed")
    try:
        book = services.library.create_book("探针书")
        chapter = services.library.create_chapter(book.book_id, "第1话")
        from application.importing.images.ports import ImportSource

        report = services.importer.import_files(
            chapter.chapter_id,
            [ImportSource(filename="p1.png", data_provider=lambda: make_png(40, 60))],
        )
        page_id = report.imported[0].page.page_id
        writer = ArtifactStepWriter(services.conn, services.storage)
        prepared = writer.prepare_revision(
            page_id=page_id,
            artifact_type="translated",
            payload=make_png(41, 61),
            mime_type="image/png",
            width=41,
            height=61,
        )
        writer.adopt_current(
            artifact_id=prepared.artifact_id,
            revision_id=prepared.revision_id,
            expected_current_revision_id=prepared.previous_revision_id,
        )

        vm = services.workbench
        vm._apply_viewer_page(page_id)
        for mode in ("original", "translated", "compare"):
            url = vm.viewerImageUrlFor(mode)
            try:
                state = vm.viewerImageStateFor(mode)
            except AttributeError:  # pre-TASK-051 trees have no state channel
                state = "unavailable"
            print(f"MODE {mode}: {'resolved' if url else 'EMPTY'} state={state}")
        return 0
    finally:
        try:
            services.conn.close()
        except sqlite3.Error:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
