"""M2-AC4 acceptance suite (doc/tasks/M2-AC4.md): Reader export lineage +
Library page-count/unknown semantics.

Verifies the Rebaseline Plan M2 Acceptance Backlog row 4 promises through
the PRODUCTION assembly (``assemble_core_services`` -- the exact assembly
the production sidecar calls), the production RPC handler
(``CoreServiceServer.handle_list_books``), the production artifact write
path (``SqliteArtifactRepository.commit_revision``, the same repository the
render pipeline uses) and a real SQLite store on a real filesystem,
mirroring the M2-AC2/M2-AC3 precedent inside ``tests/m2_acceptance/``:

  AC1  export history rows reconcile one-to-one with the actual output
       files (format, page scope, terminal state, timestamps, file hash;
       zip entry names/bytes = page scope; text payload = page text;
       export_id unique, most-recent-first)
  AC2  stale renders fail closed by default (ABORT: typed error, zero
       output file, zero history rows) and pass only on explicit CONTINUE
       with the stale/missing pages honestly identified; missing and stale
       stay distinguishable
  AC3  mid-export failure and cancellation preserve the pre-existing
       target file byte-for-byte, never write source files, and record a
       failed/cancelled terminal state with a non-empty detail
  AC4  production list_books page_count equals the book's real chapter
       page total (same number as SQLite and the Reader side); books with
       no chapter/page data must NOT present a fabricated number; corrupt
       page data degrades without crash or fabricated fields
  AC5  user source files and Managed Copy files keep bytes/size/mtime_ns
       across every export path above

Pure acceptance: NO product code may change here. A failing scenario is a
valid delivery outcome -- the defect is reported, not patched. The two
known-defect scenarios are marked ``xfail(strict=True)``: they encode
ACCEPTANCE verdict FAIL evidence (verified on release commit 252705bf) so
the rest of the suite stays green; if a fix lands, XPASS fails loudly and
the marker must be removed by the confirming review.
"""

from __future__ import annotations

from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
import sys
import time
import zipfile

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from application.export.service import (  # noqa: E402
    ExportCancelledError,
    ExportFormat,
    ExportPage,
    ExportRequest,
    StaleExportError,
    StalePolicy,
)
from application.export.ports import file_bytes_provider  # noqa: E402
from application.importing.images.ports import DecodedImage, ImportSource  # noqa: E402
from application.reading.ports import ReaderPage  # noqa: E402
from application.translation.color.service import SourceStyleService  # noqa: E402
from bootstrap.core_assembly import CoreServices, assemble_core_services  # noqa: E402
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


# ----------------------------------------------------------------------
# production fixture channel (M2-AC2/M2-AC3 precedent: headless adapters
# through the assembly's required-adapter injection; no mock data layer)
# ----------------------------------------------------------------------

class _AcceptanceDecoder:
    """Headless decode validation adapter (assembly-required injection)."""

    def decode(self, payload: bytes) -> DecodedImage:
        del payload
        return DecodedImage(width=1, height=1, mime_type="image/png")


class _AcceptanceStyleAnalyzer:
    """Headless style adapter: no pixel styles for synthetic payloads."""

    def analyze_pixel_styles(self, image):
        del image
        return []


PAGE_A = b"m2ac4-source-page-001\x00\x01\x02payload-A"
PAGE_B = b"m2ac4-source-page-002\x00\x03\x04payload-B"
PAGE_C = b"m2ac4-source-page-003\x00\x05\x06payload-C"
TRANS_R1 = b"m2ac4-translated-R1-stale-version"
TRANS_R2 = b"m2ac4-translated-R2-current-version"
PAGE1_TEXT = "第一页的OCR文本:主角在雨中奔跑。"
FILENAME_A = "第01页.png"
FILENAME_B = "第02页.png"
FILENAME_C = "第03页.png"

# The production COUNT predicate (core_service._fetch_page_counts), used
# for the real-SQLite reconciliation assertion (M2-AC2 口径).
_PRODUCTION_COUNT_SQL = """
    SELECT COUNT(p.page_id) FROM chapters c
    JOIN pages p ON p.chapter_id = c.chapter_id
    WHERE c.book_id = ?
      AND c.deleted_at IS NULL
      AND p.deleted_at IS NULL
      AND p.source_hash IS NOT NULL
      AND p.managed_original_ref IS NOT NULL
      AND p.width IS NOT NULL
      AND p.height IS NOT NULL
"""


@pytest.fixture
def core(tmp_path: Path):
    """Production assembly over one throwaway data root (sidecar equivalent)."""
    data_root = tmp_path / "data-root"
    data_root.mkdir()
    services = assemble_core_services(
        data_root / "library.db",
        data_root / "managed",
        image_decoder=_AcceptanceDecoder(),
        font_catalog=object(),  # type: ignore[arg-type]
        layout_engine=object(),  # type: ignore[arg-type]
        compositor=object(),  # type: ignore[arg-type]
        source_styles=SourceStyleService(_AcceptanceStyleAnalyzer()),
    )
    try:
        yield services
    finally:
        services.conn.close()


# ----------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------

def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _fingerprint(path: Path) -> tuple[str, int, int, str]:
    """AC5 source-safety fingerprint: sha256, size, mtime_ns."""
    return (str(path), path.stat().st_size, path.stat().st_mtime_ns, _sha256(path))


def _import_page(core: CoreServices, chapter_id: str, filename: str, payload: bytes):
    """Book-independent production import (real importer, real Managed Copy)."""

    def provider() -> bytes:
        return payload

    report = core.importer.import_files(
        chapter_id, [ImportSource(filename=filename, data_provider=provider)]
    )
    assert len(report.imported) == 1, f"production import failed: {report.failed}"
    return report.imported[0].page


def _snapshot_export_pages(
    core: CoreServices,
    snapshot: list[ReaderPage],
    *,
    text_by_page: dict[str, str] | None = None,
) -> tuple[ExportPage, ...]:
    """Build the export scope from a reader snapshot (production semantics:
    the reader/export caller holds the page view from when the chapter was
    opened; the artifact current pointer is resolved live through the same
    locator the reader catalog uses). A page whose snapshot revision now
    differs from the live current revision is exactly the reader's stale
    case (D06 §97, same judgement as ReaderPage.translated_stale)."""
    locator = SqlitePageArtifactLocator(core.conn)
    text_by_page = text_by_page or {}
    pages: list[ExportPage] = []
    for snap in snapshot:
        located = locator.locate_current(snap.page_id, ArtifactType.TRANSLATED)
        live_current = located[1].artifact_revision_id if located is not None else None
        pages.append(
            ExportPage(
                page_id=snap.page_id,
                filename=snap.filename,
                source_provider=file_bytes_provider(snap.original_path)
                if snap.original_path
                else (lambda: b""),
                translated_provider=file_bytes_provider(snap.translated_path)
                if snap.translated_path
                else None,
                translated_revision_id=snap.translated_revision_id,
                current_translated_revision_id=live_current,
                text=text_by_page.get(snap.page_id, ""),
            )
        )
    return tuple(pages)


def _seed_chapter_with_translated_page(
    core: CoreServices, *, translated_payloads: list[bytes]
):
    """One book/chapter/two real pages; page 1 gets TRANSLATED revisions
    through the production write path. Returns the pieces the scenarios
    need, with the reader snapshot taken while the FIRST revision was
    current -- exactly the state an open reader/workbench holds before a
    newer render lands, so page 1 is stale as soon as revision 2 exists."""
    book = core.library.create_book("M2-AC4 Lineage Book")
    chapter = core.library.create_chapter(book.book_id, "Chapter 1")
    page_a = _import_page(core, chapter.chapter_id, FILENAME_A, PAGE_A)
    page_b = _import_page(core, chapter.chapter_id, FILENAME_B, PAGE_B)

    artifacts = SqliteArtifactRepository(core.conn, core.storage)
    artifact = artifacts.create_artifact(
        NewArtifact(
            book_id=book.book_id,
            chapter_id=chapter.chapter_id,
            page_id=page_a.page_id,
            artifact_type=ArtifactType.TRANSLATED,
        )
    )
    revision_ids: list[str] = []
    expected_current: str | None = None

    def _commit(payload: bytes) -> str:
        nonlocal expected_current
        outcome = artifacts.commit_revision(
            PendingArtifactCommit(
                artifact_id=artifact.artifact_id,
                content_provider=ContentProvider(payload=payload),
                mime_type="image/png",
                expected_current_revision_id=expected_current,
                file_suffix=".png",
            )
        )
        assert outcome.status.name == "COMMITTED" and outcome.revision is not None, (
            f"production artifact commit failed: {outcome.status.name} {outcome.error_code}"
        )
        revision_ids.append(outcome.revision.artifact_revision_id)
        expected_current = outcome.revision.artifact_revision_id
        return expected_current

    _commit(translated_payloads[0])
    # reader snapshot while the FIRST revision is current
    snapshot = core.reader_catalog.list_pages(chapter.chapter_id)
    for payload in translated_payloads[1:]:
        _commit(payload)  # newer renders land after the snapshot
    return _Seed(book, chapter, page_a, page_b, revision_ids, snapshot)


class _Seed:
    def __init__(self, book, chapter, page_a, page_b, revision_ids, snapshot):
        self.book = book
        self.chapter = chapter
        self.page_a = page_a
        self.page_b = page_b
        self.revision_ids = revision_ids
        self.snapshot = snapshot


def _region_text_for(core: CoreServices, page_id: str, text: str) -> None:
    """Persist OCR text through the production region repository (the same
    store the reader/workbench text surfaces read from)."""
    regions = SqliteRegionRepository(core.conn)
    regions.add_region(
        Region(
            region_id=f"m2ac4-region-{page_id[:8]}",
            page_id=page_id,
            reading_order=1,
            geometry=RegionGeometry(bbox=BBox(0, 0, 10, 10)),
            text=RegionText(
                ocr_text=text,
                machine_translation=text,
                final_translation=text,
                final_source="machine",
            ),
        )
    )
    stored = regions.list_regions(page_id)
    assert stored and stored[0].text.final_translation == text


def _list_books(core: CoreServices) -> dict[str, dict]:
    """The production ListBooks command handler (core_service RPC face)."""
    server = CoreServiceServer(core)
    summaries = server.handle_list_books({})
    assert isinstance(summaries, list) and summaries, "list_books must return rows"
    return {summary["book_id"]: summary for summary in summaries}


class _CancelAfter:
    """Cancel predicate firing on the Nth subsequent poll (production
    cancel channel of ExportRequest.cancel)."""

    def __init__(self, fire_after_polls: int) -> None:
        self._fire_after = fire_after_polls
        self.polls = 0

    def __call__(self) -> bool:
        self.polls += 1
        return self.polls > self._fire_after


# ----------------------------------------------------------------------
# AC1 — export lineage reconciles with the output files
# ----------------------------------------------------------------------

def test_ac1_zip_export_history_reconciles_with_output(core) -> None:
    """AC1(a)(b): one zip export -> exactly one history row whose fields
    (format, page scope, terminal state, timestamps, file hash, output
    path) match the request, and whose zip entries match the page scope by
    name (order-prefixed, Unicode preserved) and by exact bytes."""
    seed = _seed_chapter_with_translated_page(core, translated_payloads=[TRANS_R1])
    exports = core.data_root / "exports"
    target = exports / "lineage.zip"

    snapshot_pages = _snapshot_export_pages(core, seed.snapshot)
    result = core.export_service.export(
        ExportRequest(
            book_id=seed.book.book_id,
            chapter_id=seed.chapter.chapter_id,
            format=ExportFormat.ZIP,
            output_path=target,
            pages=snapshot_pages,
            mode="original",
        )
    )
    assert result.status.value == "completed"

    history = core.export_service.history()
    assert len(history) == 1, f"exactly one completed export expected, got {len(history)}"
    row = history[0]
    assert row.export_id == result.export_id and row.export_id.startswith("exp-")
    assert row.book_id == seed.book.book_id
    assert row.chapter_id == seed.chapter.chapter_id
    assert row.export_type == "zip"
    assert row.status == "completed"
    assert row.output_path == str(target)
    assert row.detail == ""

    scope = json.loads(row.scope_snapshot_json)
    expected_page_ids = [seed.page_a.page_id, seed.page_b.page_id]
    assert scope["page_ids"] == expected_page_ids
    assert scope["filenames"] == [FILENAME_A, FILENAME_B]
    assert scope["mode"] == "original"
    assert scope["overwrite_policy"] == "overwrite"
    assert scope["stale_policy"] == "abort"

    # timestamps are queryable instants, completed not earlier than created
    from datetime import datetime

    created = datetime.fromisoformat(row.created_at)
    completed = datetime.fromisoformat(row.completed_at)
    assert completed >= created

    # output file reconciliation: entry names = order prefix + page filename,
    # entry bytes = the Managed Copy page bytes (original mode)
    assert target.is_file()
    assert row.file_hash == _sha256(target)
    with zipfile.ZipFile(target) as archive:
        names = archive.namelist()
        assert names == [f"0001_{FILENAME_A}", f"0002_{FILENAME_B}"]
        assert archive.read(names[0]) == PAGE_A
        assert archive.read(names[1]) == PAGE_B


def test_ac1_text_payload_and_two_exports_are_distinguishable(core) -> None:
    """AC1(a)(b)(c): text export payload equals the page texts; a second
    export of the same scope produces a distinct export_id and lands
    most-recent-first in history()."""
    seed = _seed_chapter_with_translated_page(core, translated_payloads=[TRANS_R1])
    _region_text_for(core, seed.page_a.page_id, PAGE1_TEXT)
    exports = core.data_root / "exports"

    snapshot_pages = _snapshot_export_pages(
        core, seed.snapshot, text_by_page={seed.page_a.page_id: PAGE1_TEXT}
    )
    text_result = core.export_service.export(
        ExportRequest(
            book_id=seed.book.book_id,
            chapter_id=seed.chapter.chapter_id,
            format=ExportFormat.TEXT,
            output_path=exports / "lineage.txt",
            pages=snapshot_pages,
            mode="original",
        )
    )
    assert text_result.status.value == "completed"

    expected_payload = ("【" + FILENAME_A + "】\n" + PAGE1_TEXT + "\n\n【" + FILENAME_B + "】\n")
    text_file = exports / "lineage.txt"
    assert text_file.read_text(encoding="utf-8") == expected_payload, (
        "the text export must be the per-page 【filename】+text payload"
    )

    time.sleep(0.02)  # utc_now has ms resolution; make the order assertion load-bearing
    zip_result = core.export_service.export(
        ExportRequest(
            book_id=seed.book.book_id,
            chapter_id=seed.chapter.chapter_id,
            format=ExportFormat.ZIP,
            output_path=exports / "lineage.zip",
            pages=snapshot_pages,
            mode="original",
        )
    )
    assert zip_result.status.value == "completed"

    assert text_result.export_id != zip_result.export_id, "export ids must be unique"

    history = core.export_service.history()
    assert len(history) == 2
    assert history[0].export_id == zip_result.export_id, (
        "history() must be most-recent-first"
    )
    assert history[1].export_id == text_result.export_id
    assert history[0].created_at >= history[1].created_at
    assert history[0].export_type == "zip"
    assert history[1].export_type == "text"
    for row in history:
        scope = json.loads(row.scope_snapshot_json)
        assert scope["page_ids"] == [seed.page_a.page_id, seed.page_b.page_id], (
            "both records must carry the same page scope"
        )


# ----------------------------------------------------------------------
# AC2 — stale fail-closed / explicit continue
# ----------------------------------------------------------------------

def test_ac2_stale_abort_fail_closed_zero_side_effects(core) -> None:
    """AC2(a): default ABORT refuses a stale translated render with the
    typed error carrying the stale page ids; zero output file and zero
    history rows (no completed record may exist for the refused export)."""
    seed = _seed_chapter_with_translated_page(
        core, translated_payloads=[TRANS_R1, TRANS_R2]
    )
    # reader snapshot holds R1; a newer render (R2) is now current
    stale_page_id = seed.page_a.page_id
    history_before = core.export_service.history()
    assert history_before == []

    target = core.data_root / "exports" / "stale-abort.zip"
    # scope narrowed to the stale page only: a pure stale case (the mixed
    # stale+missing case is AC2's next scenario)
    stale_only_pages = _snapshot_export_pages(core, seed.snapshot)[:1]
    request = ExportRequest(
        book_id=seed.book.book_id,
        chapter_id=seed.chapter.chapter_id,
        format=ExportFormat.ZIP,
        output_path=target,
        pages=stale_only_pages,
        mode="translated",
    )
    with pytest.raises(StaleExportError) as excinfo:
        core.export_service.export(request)

    error = excinfo.value
    assert error.stale_page_ids == (stale_page_id,), (
        "the stale page must be reported by id, as-is"
    )
    assert error.missing_page_ids == (), "no page in this scope is missing"

    assert not target.exists(), "ABORT must leave zero output files on disk"
    leftovers = sorted((core.data_root / "exports").glob(".*.tmp"))
    assert leftovers == [], "ABORT must not leak temp files"
    assert core.export_service.history() == [], (
        "a refused export must not gain any history row (zero completed records)"
    )


def test_ac2_continue_passes_stale_and_missing_distinguishable(core) -> None:
    """AC2(b)(c): with one stale and one missing page, the refusal names
    both lists disjointly; explicit CONTINUE succeeds, ships the stale
    render's own bytes (never silently current ones) and the missing
    page's original, and the in-memory result carries both id lists."""
    seed = _seed_chapter_with_translated_page(
        core, translated_payloads=[TRANS_R1, TRANS_R2]
    )
    stale_page_id = seed.page_a.page_id
    missing_page_id = seed.page_b.page_id  # never had a TRANSLATED render
    target = core.data_root / "exports" / "stale-continue.zip"

    request = ExportRequest(
        book_id=seed.book.book_id,
        chapter_id=seed.chapter.chapter_id,
        format=ExportFormat.ZIP,
        output_path=target,
        pages=_snapshot_export_pages(core, seed.snapshot),
        mode="translated",
    )

    # (c) the refusal distinguishes stale from missing
    with pytest.raises(StaleExportError) as excinfo:
        core.export_service.export(request)
    assert excinfo.value.stale_page_ids == (stale_page_id,)
    assert excinfo.value.missing_page_ids == (missing_page_id,)
    assert set(excinfo.value.stale_page_ids).isdisjoint(excinfo.value.missing_page_ids)

    # (b) explicit CONTINUE
    continue_request = ExportRequest(
        book_id=request.book_id,
        chapter_id=request.chapter_id,
        format=request.format,
        output_path=target,
        pages=request.pages,
        mode="translated",
        stale_policy=StalePolicy.CONTINUE,
    )
    result = core.export_service.export(continue_request)
    assert result.status.value == "completed"
    assert result.included_stale_page_ids == (stale_page_id,), (
        "the stale page actually shipped must be named in the result"
    )
    assert result.included_missing_page_ids == (missing_page_id,)

    assert target.is_file()
    with zipfile.ZipFile(target) as archive:
        names = archive.namelist()
        assert names == [f"0001_{FILENAME_A}", f"0002_{FILENAME_B}"]
        assert archive.read(names[0]) == TRANS_R1, (
            "CONTINUE must export the existing (stale) render bytes, not refetch current"
        )
        assert archive.read(names[1]) == PAGE_B, (
            "a missing render falls back to the page's original bytes on CONTINUE"
        )

    history = core.export_service.history()
    assert len(history) == 1 and history[0].status == "completed"
    scope = json.loads(history[0].scope_snapshot_json)
    assert scope["stale_policy"] == "continue", (
        "the history scope must record that stale renders were continued"
    )


@pytest.mark.xfail(
    strict=True,
    reason=(
        "M2-AC4 AC1(a)/AC2(b) known product defect, verified on release commit "
        "252705bf (probe: verification/M2-AC4/raw/probe-output.log): the export "
        "history row carries neither included_stale_page_ids nor "
        "included_missing_page_ids, and scope_snapshot_json records only the "
        "stale_policy string -- the stale pages actually shipped are NOT "
        "traceable from the persisted lineage (ExportService._record / "
        "_scope_snapshot in src/application/export/service.py)."
    ),
)
def test_ac2_history_records_which_stale_pages_were_included(core) -> None:
    """AC1(a)/AC2(b) persisted-lineage half: the export history row must
    make the included stale pages queryable (the in-memory result does;
    the persisted record must too)."""
    seed = _seed_chapter_with_translated_page(
        core, translated_payloads=[TRANS_R1, TRANS_R2]
    )
    stale_page_id = seed.page_a.page_id
    target = core.data_root / "exports" / "stale-lineage.zip"
    result = core.export_service.export(
        ExportRequest(
            book_id=seed.book.book_id,
            chapter_id=seed.chapter.chapter_id,
            format=ExportFormat.ZIP,
            output_path=target,
            pages=_snapshot_export_pages(core, seed.snapshot),
            mode="translated",
            stale_policy=StalePolicy.CONTINUE,
        )
    )
    assert result.status.value == "completed"
    assert result.included_stale_page_ids == (stale_page_id,)

    row = core.export_service.find_export(result.export_id)
    assert row is not None, "the completed export must be in the persisted history"
    scope = json.loads(row.scope_snapshot_json)
    persisted_stale = set(scope.get("included_stale_page_ids") or ())
    assert persisted_stale == {stale_page_id}, (
        "the persisted export record must carry the included stale page ids"
    )


# ----------------------------------------------------------------------
# AC3 — failure / cancellation durability
# ----------------------------------------------------------------------

def test_ac3_mid_export_failure_preserves_target_and_sources(core, tmp_path: Path) -> None:
    """AC3(a)(b)(c): a provider failure after the first archive entry keeps
    the pre-existing target byte-identical, leaves no temp file, writes no
    source, and records a failed terminal state with a non-empty detail."""
    seed = _seed_chapter_with_translated_page(core, translated_payloads=[TRANS_R1])
    exports = core.data_root / "exports"
    exports.mkdir(parents=True, exist_ok=True)
    target = exports / "existing-target.zip"
    target.write_bytes(b"M2-AC4 pre-existing target bytes")
    target_before = _fingerprint(target)

    source_files = [core.data_root / "managed" / page.managed_original_ref for page in (seed.page_a, seed.page_b)]
    for path in source_files:
        assert path.is_file()
    sources_before = [_fingerprint(path) for path in source_files]

    pages = list(_snapshot_export_pages(core, seed.snapshot))

    def _boom() -> bytes:
        raise OSError("injected mid-export failure (M2-AC4 AC3)")

    pages[1] = ExportPage(
        page_id=pages[1].page_id,
        filename=pages[1].filename,
        source_provider=_boom,
        translated_provider=None,
        text="",
    )

    history_before = len(core.export_service.history())
    with pytest.raises(OSError):
        core.export_service.export(
            ExportRequest(
                book_id=seed.book.book_id,
                chapter_id=seed.chapter.chapter_id,
                format=ExportFormat.ZIP,
                output_path=target,
                pages=tuple(pages),
                mode="original",
            )
        )

    assert _fingerprint(target) == target_before, (
        "the pre-existing target file must survive a mid-export failure byte-for-byte"
    )
    assert [_fingerprint(path) for path in source_files] == sources_before, (
        "source/managed files must never be written by a failing export"
    )
    assert sorted(exports.glob(".*.tmp")) == [], "the temp output must be cleaned up"

    history = core.export_service.history()
    assert len(history) == history_before + 1
    row = history[0]
    assert row.status == "failed"
    assert row.detail.strip() != "", "the failed record must carry a diagnosable detail"
    assert "OSError" in row.detail, f"detail must name the failure type, got: {row.detail!r}"
    assert row.export_id != "" and row.book_id == seed.book.book_id
    assert row.file_hash == "", "a failed export publishes no file hash"


def test_ac3_cancellation_preserves_target_and_records_state(core) -> None:
    """AC3(a)(b)(c): a cancel firing between archive entries keeps the
    pre-existing target byte-identical, never writes sources, and records
    a cancelled terminal state with a non-empty detail."""
    seed = _seed_chapter_with_translated_page(core, translated_payloads=[TRANS_R1])
    exports = core.data_root / "exports"
    exports.mkdir(parents=True, exist_ok=True)
    target = exports / "cancelled-target.zip"
    target.write_bytes(b"M2-AC4 target before cancellation")
    target_before = _fingerprint(target)

    source_files = [core.data_root / "managed" / page.managed_original_ref for page in (seed.page_a, seed.page_b)]
    sources_before = [_fingerprint(path) for path in source_files]

    history_before = len(core.export_service.history())
    cancel = _CancelAfter(fire_after_polls=2)  # poll 1: export start; poll 2: entry 1; poll 3: entry 2 -> fires
    with pytest.raises(ExportCancelledError):
        core.export_service.export(
            ExportRequest(
                book_id=seed.book.book_id,
                chapter_id=seed.chapter.chapter_id,
                format=ExportFormat.ZIP,
                output_path=target,
                pages=_snapshot_export_pages(core, seed.snapshot),
                mode="original",
                cancel=cancel,
            )
        )
    assert cancel.polls >= 2, "the cancel predicate must have been polled mid-export"

    assert _fingerprint(target) == target_before, (
        "cancellation must leave the pre-existing target byte-identical"
    )
    assert [_fingerprint(path) for path in source_files] == sources_before
    assert sorted(exports.glob(".*.tmp")) == []

    history = core.export_service.history()
    assert len(history) == history_before + 1
    row = history[0]
    assert row.status == "cancelled"
    assert row.detail.strip() != "", "the cancelled record must carry a non-empty detail"
    assert row.file_hash == "", "a cancelled export publishes no file hash"


# ----------------------------------------------------------------------
# AC4 — Library page-count / unknown semantics (production list_books)
# ----------------------------------------------------------------------

def test_ac4_page_count_matches_chapter_total_sqlite_and_reader(core) -> None:
    """AC4(a): production list_books page_count equals the book's chapter
    page total, the real SQLite page rows (same predicate as production),
    and the Reader-side count (reader catalog + ReadingService)."""
    book_a = core.library.create_book("M2-AC4 Multi-chapter Book")
    chapter_a1 = core.library.create_chapter(book_a.book_id, "A-1")
    _import_page(core, chapter_a1.chapter_id, FILENAME_A, PAGE_A)
    _import_page(core, chapter_a1.chapter_id, FILENAME_B, PAGE_B)
    chapter_a2 = core.library.create_chapter(book_a.book_id, "A-2")
    _import_page(core, chapter_a2.chapter_id, FILENAME_C, PAGE_C)

    book_b = core.library.create_book("M2-AC4 Single-chapter Book")
    chapter_b1 = core.library.create_chapter(book_b.book_id, "B-1")
    _import_page(core, chapter_b1.chapter_id, FILENAME_A, PAGE_A)

    summaries = _list_books(core)
    assert set(summaries) == {book_a.book_id, book_b.book_id}

    # chapter page totals straight from the repository
    total_a = len(core.repository.list_pages(chapter_a1.chapter_id)) + len(
        core.repository.list_pages(chapter_a2.chapter_id)
    )
    total_b = len(core.repository.list_pages(chapter_b1.chapter_id))
    assert total_a == 3 and total_b == 1, "fixture sanity: 3 and 1 real pages"

    # real SQLite reconciliation with the production COUNT predicate
    count_a = core.conn.execute(_PRODUCTION_COUNT_SQL, (book_a.book_id,)).fetchone()[0]
    count_b = core.conn.execute(_PRODUCTION_COUNT_SQL, (book_b.book_id,)).fetchone()[0]
    assert count_a == 3 and count_b == 1

    assert summaries[book_a.book_id]["page_count"] == count_a == total_a == 3
    assert summaries[book_b.book_id]["page_count"] == count_b == total_b == 1

    # Reader-side same-source check: reader catalog pages and the
    # ReadingService page_count over the production reader flow
    reader_total_b = len(core.reader_catalog.list_pages(chapter_b1.chapter_id))
    assert reader_total_b == 1
    core.reading.open(
        book_b.book_id, chapter_b1.chapter_id,
        core.reader_catalog.list_pages(chapter_b1.chapter_id),
    )
    assert core.reading.page_count == summaries[book_b.book_id]["page_count"] == 1

    # untouched fields stay honest
    summary_a = summaries[book_a.book_id]
    assert summary_a["title"] == "M2-AC4 Multi-chapter Book"
    assert summary_a["is_favorite"] is False and summary_a["is_archived"] is False


@pytest.mark.xfail(
    strict=True,
    reason=(
        "M2-AC4 AC4(b) known product defect, verified on release commit 252705bf "
        "(probe: verification/M2-AC4/raw/probe-output.log): "
        "bootstrap/core_service.py handle_list_books presents "
        "page_counts.get(book.book_id, 0) -- a book with no chapters/pages "
        "renders as the plausible real number 0 (int) with no unknown marker, "
        "violating '缺失数据不得伪造成看似真实的数字'."
    ),
)
def test_ac4_books_without_pages_are_not_presented_as_zero(core) -> None:
    """AC4(b): a book with no chapters and a book with a chapter but no
    pages must NOT present a fabricated-looking count; the presentation
    must distinguish unknown/missing data from a genuine zero."""
    empty_book = core.library.create_book("M2-AC4 No-chapter Book")
    hollow_book = core.library.create_book("M2-AC4 Chapterless-pages Book")
    core.library.create_chapter(hollow_book.book_id, "no pages inside")

    summaries = _list_books(core)
    # the books themselves must be listed honestly
    assert empty_book.book_id in summaries
    assert hollow_book.book_id in summaries

    for book_id in (empty_book.book_id, hollow_book.book_id):
        summary = summaries[book_id]
        known_flag = summary.get("page_count_known")
        presented_unknown = (
            summary["page_count"] is None
            or (isinstance(summary["page_count"], int) and summary["page_count"] < 0)
            or known_flag is False
        )
        assert presented_unknown, (
            f"book {book_id} presents page_count={summary['page_count']!r} with "
            f"page_count_known={known_flag!r}: unknown data rendered as a "
            "plausible number instead of an unknown marker"
        )


def test_ac4_corrupt_page_rows_degrade_without_crash_or_fabrication(core) -> None:
    """AC4(c): rows missing the columns production counts on are excluded
    honestly; list_books neither crashes nor fabricates other fields; the
    presented number keeps matching the real (production-predicate) count."""
    book = core.library.create_book("M2-AC4 Corrupt-data Book")
    chapter = core.library.create_chapter(book.book_id, "C-1")
    page_a = _import_page(core, chapter.chapter_id, FILENAME_A, PAGE_A)
    page_b = _import_page(core, chapter.chapter_id, FILENAME_B, PAGE_B)

    # corrupt page B: blank the columns the production COUNT filters on
    core.conn.execute(
        "UPDATE pages SET width = NULL, height = NULL WHERE page_id = ?",
        (page_b.page_id,),
    )
    core.conn.commit()

    summaries = _list_books(core)
    assert book.book_id in summaries, "list_books must not crash on broken page data"
    summary = summaries[book.book_id]
    real_count = core.conn.execute(_PRODUCTION_COUNT_SQL, (book.book_id,)).fetchone()[0]
    assert real_count == 1, "the corrupt row must be excluded by the production predicate"
    assert summary["page_count"] == real_count == 1, (
        "the presented count must track the real (valid) rows"
    )
    assert summary["title"] == "M2-AC4 Corrupt-data Book"
    assert summary["is_favorite"] is False and summary["is_archived"] is False

    # corrupt the remaining page too: still no crash, still honest counting
    core.conn.execute(
        "UPDATE pages SET source_hash = NULL WHERE page_id = ?", (page_a.page_id,)
    )
    core.conn.commit()
    summaries = _list_books(core)
    assert book.book_id in summaries
    real_count = core.conn.execute(_PRODUCTION_COUNT_SQL, (book.book_id,)).fetchone()[0]
    assert real_count == 0
    assert summaries[book.book_id]["page_count"] == real_count == 0
    assert summaries[book.book_id]["title"] == "M2-AC4 Corrupt-data Book", (
        "other fields must never be fabricated when page data is broken"
    )


# ----------------------------------------------------------------------
# AC5 — source files stay untouched across every export path
# ----------------------------------------------------------------------

def test_ac5_sources_and_managed_files_untouched_across_export_paths(core, tmp_path: Path) -> None:
    """AC5: success, ABORT refusal, CONTINUE, mid-export failure and
    cancellation over one data root leave every user source file and every
    Managed Copy/artifact file byte-, size- and mtime_ns-identical."""
    seed = _seed_chapter_with_translated_page(
        core, translated_payloads=[TRANS_R1, TRANS_R2]
    )
    exports = core.data_root / "exports"
    exports.mkdir(parents=True, exist_ok=True)
    existing_target = exports / "kept.zip"
    existing_target.write_bytes(b"M2-AC4 durable target")

    # user source files outside the managed root (import payload provenance)
    user_sources = [tmp_path / "user-src-1.png", tmp_path / "user-src-2.png"]
    user_sources[0].write_bytes(PAGE_A)
    user_sources[1].write_bytes(PAGE_B)

    r1_path = core.storage.absolute_path(
        SqlitePageArtifactLocator(core.conn)
        .locate_current(seed.page_a.page_id, ArtifactType.TRANSLATED)[1]
        .managed_path
    )
    # fingerprint everything AC3/AC5 protects BEFORE the operations
    protected = (
        user_sources
        + [core.data_root / "managed" / page.managed_original_ref for page in (seed.page_a, seed.page_b)]
        + [Path(r1_path)]
    )
    before = [_fingerprint(path) for path in protected]
    target_before = _fingerprint(existing_target)

    pages = _snapshot_export_pages(core, seed.snapshot)

    # 1. successful zip export (original mode)
    result = core.export_service.export(
        ExportRequest(
            book_id=seed.book.book_id,
            chapter_id=seed.chapter.chapter_id,
            format=ExportFormat.ZIP,
            output_path=exports / "ok.zip",
            pages=pages,
            mode="original",
        )
    )
    assert result.status.value == "completed"

    # 2. stale ABORT refusal (translated mode)
    with pytest.raises(StaleExportError):
        core.export_service.export(
            ExportRequest(
                book_id=seed.book.book_id,
                chapter_id=seed.chapter.chapter_id,
                format=ExportFormat.ZIP,
                output_path=exports / "aborted.zip",
                pages=pages,
                mode="translated",
            )
        )

    # 3. explicit CONTINUE over the same stale scope
    continued = core.export_service.export(
        ExportRequest(
            book_id=seed.book.book_id,
            chapter_id=seed.chapter.chapter_id,
            format=ExportFormat.ZIP,
            output_path=exports / "continued.zip",
            pages=pages,
            mode="translated",
            stale_policy=StalePolicy.CONTINUE,
        )
    )
    assert continued.status.value == "completed"

    # 4. mid-export failure against the pre-existing target
    broken = list(pages)

    def _boom() -> bytes:
        raise OSError("injected mid-export failure (M2-AC4 AC5 sweep)")

    broken[1] = ExportPage(
        page_id=broken[1].page_id,
        filename=broken[1].filename,
        source_provider=_boom,
        translated_provider=None,
        text="",
    )
    with pytest.raises(OSError):
        core.export_service.export(
            ExportRequest(
                book_id=seed.book.book_id,
                chapter_id=seed.chapter.chapter_id,
                format=ExportFormat.ZIP,
                output_path=existing_target,
                pages=tuple(broken),
                mode="original",
            )
        )

    # 5. cancellation against a fresh target
    cancel = _CancelAfter(fire_after_polls=2)
    with pytest.raises(ExportCancelledError):
        core.export_service.export(
            ExportRequest(
                book_id=seed.book.book_id,
                chapter_id=seed.chapter.chapter_id,
                format=ExportFormat.ZIP,
                output_path=exports / "cancelled.zip",
                pages=pages,
                mode="original",
                cancel=cancel,
            )
        )

    assert [_fingerprint(path) for path in protected] == before, (
        "user source files and Managed Copy/artifact files must keep "
        "bytes/size/mtime_ns across every export path"
    )
    assert _fingerprint(existing_target) == target_before, (
        "the pre-existing target must survive failure and cancellation"
    )
    assert not (exports / "aborted.zip").exists()
    assert not (exports / "cancelled.zip").exists()

    # terminal states all queryable: completed/failed/cancelled present
    statuses = sorted(row.status for row in core.export_service.history())
    assert statuses == ["cancelled", "completed", "completed", "failed"], (
        f"every terminal state must be recorded exactly once: {statuses}"
    )
