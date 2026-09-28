"""M2-AC4 pre-test probe: verify production export/library semantics facts
before writing the acceptance suite. Read-only against product code; writes
only to a throwaway temp data root. Evidence file, not a test.

Run with the TASK-012-py312 venv:
  PYTHONIOENCODING=utf-8 "$py" verification/M2-AC4/raw/probe_export_semantics.py
"""

from __future__ import annotations

from pathlib import Path
import json
import sys
import tempfile

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from application.export.service import (  # noqa: E402
    ExportFormat,
    ExportPage,
    ExportRequest,
    ExportService,
    OverwritePolicy,
    StaleExportError,
    StalePolicy,
)
from application.importing.images.ports import DecodedImage, ImportSource  # noqa: E402
from application.translation.color.service import SourceStyleService  # noqa: E402
from bootstrap.core_assembly import assemble_core_services  # noqa: E402
from bootstrap.core_service import CoreServiceServer  # noqa: E402
from domain.regions.entities import BBox, Region, RegionGeometry, RegionText  # noqa: E402
from infrastructure.rendering.locator import SqlitePageArtifactLocator  # noqa: E402
from infrastructure.sqlite.artifacts import SqliteArtifactRepository  # noqa: E402
from infrastructure.sqlite.regions import SqliteRegionRepository  # noqa: E402
from ports.repositories.artifacts import (  # noqa: E402
    ArtifactType,
    ContentProvider,
    NewArtifact,
    PendingArtifactCommit,
)

# export providers live under application/export/ports.py in this slice
from application.export.ports import file_bytes_provider  # noqa: E402


class _Decoder:
    def decode(self, payload: bytes) -> DecodedImage:
        del payload
        return DecodedImage(width=1, height=1, mime_type="image/png")


class _Analyzer:
    def analyze_pixel_styles(self, image):
        del image
        return []


PAGE_A = b"probe-page-A-bytes-0xA0"
PAGE_B = b"probe-page-B-bytes-0xB0"
TRANS_R1 = b"probe-translated-R1-stale-bytes"
TRANS_R2 = b"probe-translated-R2-current-bytes"
TEXT_A = "第一页的OCR文本"

root = Path(tempfile.mkdtemp(prefix="m2ac4-probe-"))
core = assemble_core_services(
    root / "library.db",
    root / "managed",
    image_decoder=_Decoder(),
    font_catalog=object(),
    layout_engine=object(),
    compositor=object(),
    source_styles=SourceStyleService(_Analyzer()),
)
try:
    book = core.library.create_book("Probe Book")
    chapter = core.library.create_chapter(book.book_id, "Ch 1")

    def prov(data: bytes):
        return lambda: data

    report = core.importer.import_files(
        chapter.chapter_id,
        [
            ImportSource(filename="第01页.png", data_provider=prov(PAGE_A)),
            ImportSource(filename="第02页.png", data_provider=prov(PAGE_B)),
        ],
    )
    pages = [entry.page for entry in report.imported]
    print("imported pages:", [p.page_id for p in pages])

    # --- production artifact write path: TRANSLATED R1 then R2 ---
    artifacts = SqliteArtifactRepository(core.conn, core.storage)
    artifact = artifacts.create_artifact(
        NewArtifact(
            book_id=book.book_id,
            chapter_id=chapter.chapter_id,
            page_id=pages[0].page_id,
            artifact_type=ArtifactType.TRANSLATED,
        )
    )
    out1 = artifacts.commit_revision(
        PendingArtifactCommit(
            artifact_id=artifact.artifact_id,
            content_provider=ContentProvider(payload=TRANS_R1),
            mime_type="image/png",
            expected_current_revision_id=None,
            file_suffix=".png",
        )
    )
    print("R1 commit:", out1.status.name, out1.revision.artifact_revision_id if out1.revision else None)
    out2 = artifacts.commit_revision(
        PendingArtifactCommit(
            artifact_id=artifact.artifact_id,
            content_provider=ContentProvider(payload=TRANS_R2),
            mime_type="image/png",
            expected_current_revision_id=out1.revision.artifact_revision_id,
            file_suffix=".png",
        )
    )
    print("R2 commit:", out2.status.name, out2.revision.artifact_revision_id if out2.revision else None)

    # --- reader snapshot taken between R1 and R2 (UI holds R1) ---
    snapshot = {p.page_id: p for p in core.reader_catalog.list_pages(chapter.chapter_id)}
    # snapshot was taken AFTER R2 in this linear script; rebuild R1-era facts:
    # translated_revision_id must come from the R1 revision record.
    locator = SqlitePageArtifactLocator(core.conn)
    located_current = locator.locate_current(pages[0].page_id, ArtifactType.TRANSLATED)
    current_rev_id = located_current[1].artifact_revision_id
    r1_rev_id = out1.revision.artifact_revision_id
    print("snapshot translated_revision_id:", snapshot[pages[0].page_id].translated_revision_id)
    print("live current revision:", current_rev_id, "| R1 was:", r1_rev_id)

    # --- region text through the production region repository ---
    regions = SqliteRegionRepository(core.conn)
    regions.add_region(
        Region(
            region_id="probe-region-1",
            page_id=pages[0].page_id,
            reading_order=1,
            geometry=RegionGeometry(bbox=BBox(0, 0, 10, 10)),
            text=RegionText(
                ocr_text=TEXT_A,
                machine_translation=TEXT_A,
                final_translation=TEXT_A,
                final_source="machine",
            ),
        )
    )
    region_text = regions.list_regions(pages[0].page_id)[0].text.final_translation
    print("region final_translation:", region_text)

    export_pages = []
    for index, page in enumerate(pages):
        snap = snapshot[page.page_id]
        is_stale_target = page.page_id == pages[0].page_id
        export_pages.append(
            ExportPage(
                page_id=page.page_id,
                filename=snap.filename,
                source_provider=file_bytes_provider(core.data_root / "managed" / page.managed_original_ref),
                translated_provider=(
                    file_bytes_provider(core.storage.absolute_path(out1.revision.managed_path))
                    if is_stale_target
                    else None
                ),
                translated_revision_id=(r1_rev_id if is_stale_target else None),
                current_translated_revision_id=(current_rev_id if is_stale_target else None),
                text=(region_text if index == 0 else ""),
            )
        )

    exports_dir = root / "exports"
    service = core.export_service

    # --- ABORT on stale (default policy) ---
    try:
        service.export(
            ExportRequest(
                book_id=book.book_id,
                chapter_id=chapter.chapter_id,
                format=ExportFormat.ZIP,
                output_path=exports_dir / "abort.zip",
                pages=tuple(export_pages),
                mode="translated",
            )
        )
        print("ABORT probe: NO raise (unexpected!)")
    except StaleExportError as error:
        print("ABORT probe: raised StaleExportError stale=", error.stale_page_ids, "missing=", error.missing_page_ids)
    print("history rows after ABORT:", len(service.history()))
    print("abort.zip exists:", (exports_dir / "abort.zip").exists())

    # --- CONTINUE ---
    result = service.export(
        ExportRequest(
            book_id=book.book_id,
            chapter_id=chapter.chapter_id,
            format=ExportFormat.ZIP,
            output_path=exports_dir / "continue.zip",
            pages=tuple(export_pages),
            mode="translated",
            overwrite_policy=OverwritePolicy.OVERWRITE,
            stale_policy=StalePolicy.CONTINUE,
        )
    )
    print("CONTINUE result status:", result.status.value)
    print("result.included_stale_page_ids:", result.included_stale_page_ids)
    print("result.included_missing_page_ids:", result.included_missing_page_ids)

    rows = service.history()
    print("history rows after CONTINUE:", len(rows))
    print("history row keys:", sorted(rows[-1].__dict__.keys()) if rows else None)
    if rows:
        row = rows[0]
        payload = json.loads(row.scope_snapshot_json)
        print("scope_snapshot keys:", sorted(payload.keys()))
        print("status:", row.status, "| export_type:", row.export_type, "| detail:", repr(row.detail))
        print("file_hash == sha256 of output:", row.file_hash != "")
    import zipfile

    with zipfile.ZipFile(exports_dir / "continue.zip") as zf:
        print("zip entries:", zf.namelist())
        print("zip stale entry bytes == R1:", zf.read(zf.namelist()[0]) == TRANS_R1)
        print("zip missing-page entry bytes == ORIGINAL:", zf.read(zf.namelist()[1]) == PAGE_B)

    # --- library page counts (production RPC handler) ---
    server = CoreServiceServer(core)
    summaries = server.handle_list_books({})
    print("list_books:", json.dumps(summaries, ensure_ascii=False))

    empty_book = core.library.create_book("Probe Empty Book")
    core.library.create_chapter(empty_book.book_id, "no pages chapter")
    summaries = server.handle_list_books({})
    for summary in summaries:
        print("  book:", summary["title"], "page_count:", summary["page_count"])

    print("PROBE DONE")
finally:
    core.conn.close()
