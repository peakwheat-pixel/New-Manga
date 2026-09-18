"""Reviewer-side probe for TASK-041 (Codex, non-author review of d114253).

Not part of the delivered slice. It answers two questions the author's own
suite does not:

A) What does MobiDocumentRaster's page list look like when the extractor's
   temp tree contains the names the real binding can emit besides
   ``image%05d.<ext>`` -- i.e. ``cover%05d`` (EXTH CoverOffset present;
   kindleunpack.py:418-419, CREATE_COVER_PAGE=True at line 153) and
   ``HDimage%05d`` (HDImages/, written when the container carries HD
   resources; use_hd defaults False so they are never merged).
   The tree is injected by monkeypatching mobi.extract, so this measures the
   ADAPTER's collection semantics, not a real container.

B) Do the fail-closed paths leave any managed copy behind? The author's tests
   assert only ``sink.pages == []``; this probe inspects the managed tree.

Run:  python verification/TASK-041/review-d114253/probe_collect.py
Env:  TASK041_WORKTREE (default G:/CODEX/New Manga.worktrees/TASK-041-zcode)
"""

import os
import sys
import tempfile
from pathlib import Path

WT = os.environ.get("TASK041_WORKTREE", r"G:\CODEX\New Manga.worktrees\TASK-041-zcode")
sys.path.insert(0, os.path.join(WT, "src"))
sys.path.insert(0, os.path.join(WT, "tests", "import_formats"))

from test_mobi_import import _make_jpeg, picture_mobi, text_only_mobi  # noqa: E402
from infrastructure.importing import MobiDocumentRaster  # noqa: E402
import mobi as mobibind  # noqa: E402
from PySide6.QtGui import QImage  # noqa: E402

print("=== PROBE A: adapter collection over a tree with cover/HD names ===")
fake = tempfile.mkdtemp(prefix="nm041fake")
imgdir = Path(fake) / "mobi7" / "Images"
imgdir.mkdir(parents=True)
hddir = Path(fake) / "HDImages"
hddir.mkdir(parents=True)
(imgdir / "image00002.jpeg").write_bytes(_make_jpeg(8, 6, (255, 0, 0)))
(imgdir / "image00003.jpeg").write_bytes(_make_jpeg(9, 7, (0, 255, 0)))
(imgdir / "cover00001.jpeg").write_bytes(_make_jpeg(4, 4, (255, 255, 255)))
(hddir / "HDimage00004.jpeg").write_bytes(_make_jpeg(5, 5, (0, 0, 255)))
(Path(fake) / "mobi7" / "book.html").write_text("<html></html>", encoding="utf-8")
print("injected tree (2 logical page images + cover + HD copy):")
for path in sorted(Path(fake).rglob("*")):
    if path.is_file():
        print("   ", path.relative_to(fake))

orig_extract = mobibind.extract
mobibind.extract = lambda infile: (fake, os.path.join(fake, "mobi7", "book.html"))
try:
    handle = MobiDocumentRaster().open(picture_mobi([_make_jpeg(8, 6, (255, 0, 0))]))
    print("adapter page_count =", handle.page_count)
    for index in range(handle.page_count):
        page = handle.render_page(index)
        image = QImage()
        assert image.loadFromData(page.png)
        colour = image.pixelColor(1, 1)
        print("    page", index + 1, (image.width(), image.height()),
              "rgb=", (colour.red(), colour.green(), colour.blue()))
    handle.close()
finally:
    mobibind.extract = orig_extract

print("=== PROBE B: fail-closed leaves no managed copy ===")
from application.importing.documents.service import ImportDocumentsUseCase  # noqa: E402
from application.importing.images.ports import ImportSource  # noqa: E402
from infrastructure.filesystem.managed_storage import ManagedFileStorage  # noqa: E402
from infrastructure.importing import (  # noqa: E402
    ManagedCopyStoreAdapter,
    PdfiumDocumentRaster,
)
from test_document_import import InMemoryPageSink  # noqa: E402

red = _make_jpeg(8, 6, (255, 0, 0))
cases = [
    ("drm", picture_mobi([red], crypto_type=1)),
    ("truncated", picture_mobi([red])[:100]),
    ("text_only", text_only_mobi()),
]
for label, payload in cases:
    root = Path(tempfile.mkdtemp(prefix="nm041b"))
    storage = ManagedFileStorage(root / "managed")
    copy_store = ManagedCopyStoreAdapter(storage, lambda chapter_id: "book-42")
    sink = InMemoryPageSink()
    use_case = ImportDocumentsUseCase(
        PdfiumDocumentRaster(), copy_store, sink, mobi_raster=MobiDocumentRaster()
    )
    report = use_case.import_documents(
        "chapter-7",
        [ImportSource(filename=label + ".mobi", data_provider=lambda d=payload: d)],
    )
    files = sorted(str(p.relative_to(root)) for p in root.rglob("*") if p.is_file())
    print(label,
          "| reason=", report.failed[0].reason if report.failed else "-",
          "| imported=", len(report.imported),
          "| sink.pages=", len(sink.pages),
          "| managed_root_exists=", (root / "managed").exists(),
          "| files=", files)
