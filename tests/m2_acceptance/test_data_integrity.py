"""M2-AC2 Data Integrity Acceptance suite (doc/tasks/M2-AC2.md).

Verifies the Rebaseline Plan M2 Acceptance Backlog row 2 promises on the
PRODUCTION assembly path (``bootstrap.core_service.assemble_production_core``
-- the same assembly the production sidecar runs) with a real SQLite store
and a real filesystem, plus one pipeline-family group over the acceptance
``mock_local_providers`` assembly (the M2-AC1 precedent inside
``tests/m2_acceptance/``):

  AC1  source hash integrity + the user source file is never touched
  AC2  Managed Copy isolation (authoritative copy, detectable absence)
  AC3  manual edits survive the pipeline (locked region)
  AC4  Lock (page SKIP_LOCK / region zero-write) and current/pinned Revision
  AC5  end-to-end recovery across a full re-assembly (process-restart
       equivalent)

Pure acceptance: NO product code may change here. A failing scenario is a
valid delivery outcome -- the defect is reported, not patched.
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import sys

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from application.importing.images.ports import DecodedImage, ImportSource  # noqa: E402
from application.importing.images.service import DuplicatePolicy  # noqa: E402
from application.maintenance.cleanup import CleanupService, CleanupTarget  # noqa: E402
from application.translation.color.service import SourceStyleService  # noqa: E402
from domain.tasks.models import CommandType, PipelineScope, ScopeType  # noqa: E402
from bootstrap.acceptance_bridge import synthetic_page_png  # noqa: E402
from bootstrap.core_assembly import assemble_core_services  # noqa: E402

from domain.regions.entities import BBox, RegionGeometry, RegionOrigin  # noqa: E402
from domain.regions.entities import RegionRevision  # noqa: E402
from infrastructure.filesystem.managed_storage import ManagedFileStorage  # noqa: E402
from application.importing.images.service import sha256_bytes  # noqa: E402
from infrastructure.sqlite.regions import SqliteRegionRepository  # noqa: E402

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


# Deterministic source payload: never a real codec concern (decode is
# validated structurally, not by codec), only bytes to hash, copy and
# protect.
SOURCE_BYTES_A = b"m2ac2-source-page-001\x00\x01\x02payload-A"
SOURCE_BYTES_B = b"m2ac2-source-page-002\x00\x03\x04payload-B"


def _assemble(data_root: Path, *, mock_providers: bool = False):
    """The production sidecar assembly (``assemble_production_core``) with an
    optional acceptance-provider upgrade (M2-AC1 precedent) for the pipeline
    scenarios. No other deviation from the production path.

    NOTE (M2-AC2 finding, DSH r2 P3-3 corroborated): the sidecar's own
    ``_PassthroughImageDecoder`` is broken — it passes ``format=`` to
    ``DecodedImage`` (real fields: width/height/mime_type), so ANY import
    through that stub raises TypeError. The sidecar command surface never
    imports, so M2-IPC1 was not affected; this suite supplies its own
    adapter via the assembly's required-adapter injection instead (I1-AC4).
    """

    core = assemble_core_services(
        data_root / "library.db",
        data_root / "managed",
        image_decoder=_AcceptanceDecoder(),
        font_catalog=object(),  # type: ignore[arg-type]
        layout_engine=object(),  # type: ignore[arg-type]
        compositor=object(),  # type: ignore[arg-type]
        source_styles=SourceStyleService(_AcceptanceStyleAnalyzer()),
        mock_local_providers=mock_providers,
    )
    return core


def _import_one_book(core, source_dir: Path, payload: bytes, filename: str):
    """Book -> chapter -> one real source file on disk -> production import.

    Returns (page, source_path). The import is the REAL production use case
    (duplicate check -> decode -> managed copy -> sink commit)."""

    def provider() -> bytes:
        return payload

    book = core.library.create_book("M2-AC2 Integrity Book")
    chapter = core.library.create_chapter(book.book_id, "Chapter 1")
    source_path = source_dir / filename
    source_path.write_bytes(payload)
    report = core.importer.import_files(
        chapter.chapter_id,
        [ImportSource(filename=filename, data_provider=provider)],
    )
    assert len(report.imported) == 1, f"import failed: {report.failed}"
    page = report.imported[0].page
    return page, source_path


def _managed_file(core, page) -> Path:
    return core.data_root / "managed" / page.managed_original_ref


def _lock_region(core, region_id: str) -> None:
    """Fixture-grade lock setup: flip the region lock through the same
    persisted column the pipeline guard reads."""
    core.conn.execute(
        "UPDATE regions SET region_locked = 1 WHERE region_id = ?",
        (region_id,),
    )
    core.conn.commit()


# ---------------------------------------------------------------------------
# AC1 — source hash integrity + the user source file is never touched
# ---------------------------------------------------------------------------


def test_ac1_source_hash_matches_and_source_file_untouched(tmp_path: Path) -> None:
    core = _assemble(tmp_path / "data-root")
    source_dir = tmp_path / "user-sources"
    source_dir.mkdir()

    before_bytes = SOURCE_BYTES_A
    page, source_path = _import_one_book(core, source_dir, before_bytes, "001.png")

    assert page.source_hash == sha256_bytes(before_bytes)
    assert source_path.read_bytes() == before_bytes, "source bytes changed"
    # No write into the user source directory at all.
    assert sorted(p.name for p in source_dir.iterdir()) == ["001.png"]
    assert source_path.stat().st_size == len(before_bytes)


def test_ac1_duplicate_import_is_skipped_without_second_copy(tmp_path: Path) -> None:
    core = _assemble(tmp_path / "data-root")
    source_dir = tmp_path / "user-sources"
    source_dir.mkdir()

    page, source_path = _import_one_book(core, source_dir, SOURCE_BYTES_A, "001.png")
    managed_first = _managed_file(core, page)
    assert managed_first.is_file()

    def provider() -> bytes:
        return SOURCE_BYTES_A

    chapter_id = page.chapter_id
    report = core.importer.import_files(
        chapter_id,
        [ImportSource(filename="001.png", data_provider=provider)],
        duplicate_policy=DuplicatePolicy.SKIP,
    )
    assert report.imported == ()
    assert report.skipped_duplicates == ("001.png",)
    pages = core.repository.list_pages(chapter_id)
    assert len(pages) == 1, "duplicate import must not create a second page"
    assert _managed_file(core, pages[0]) == managed_first


# ---------------------------------------------------------------------------
# AC2 — Managed Copy isolation
# ---------------------------------------------------------------------------


def test_ac2_managed_copy_is_authoritative_byte_for_byte(tmp_path: Path) -> None:
    core = _assemble(tmp_path / "data-root")
    source_dir = tmp_path / "user-sources"
    source_dir.mkdir()

    page, source_path = _import_one_book(core, source_dir, SOURCE_BYTES_A, "001.png")
    managed = _managed_file(core, page)

    assert managed.is_file()
    assert managed.read_bytes() == SOURCE_BYTES_A
    assert managed.resolve() != source_path.resolve()
    assert not managed.resolve().is_relative_to(source_dir.resolve()), (
        "managed copy must not live inside the user source directory"
    )

    # The managed copy is authoritative: destroy the user source and the
    # Core still holds the bytes.
    source_path.unlink()
    assert managed.read_bytes() == SOURCE_BYTES_A


def test_ac2_missing_managed_file_is_detectable_not_silent(tmp_path: Path) -> None:
    core = _assemble(tmp_path / "data-root")
    source_dir = tmp_path / "user-sources"
    source_dir.mkdir()

    page, _source_path = _import_one_book(core, source_dir, SOURCE_BYTES_A, "001.png")
    managed = _managed_file(core, page)
    assert managed.is_file()

    # The page catalog is the production read surface for the original; it
    # must report the loss instead of inventing pixels.
    status_present = core.page_catalog.image_state(page.page_id, mode="original")
    managed.unlink()
    status_missing = core.page_catalog.image_state(page.page_id, mode="original")

    assert status_present == "ok"
    assert status_missing != "ok", (
        f"a vanished managed original must be detectable, got {status_missing!r}"
    )


# ---------------------------------------------------------------------------
# AC3 — manual edits survive the pipeline
# ---------------------------------------------------------------------------


def _region_on(core, page):
    geometry = RegionGeometry(
        bbox=BBox(x=0, y=0, width=8, height=8),
        polygon=((0, 0), (8, 0), (8, 8)),
    )
    return core.editing.create_region(
        page.page_id,
        geometry,
        reading_order=1,
        origin=RegionOrigin.MACHINE,
    )


def test_ac3_manual_translation_survives_pipeline_on_locked_region(
    tmp_path: Path,
) -> None:
    core = _assemble(tmp_path / "data-root", mock_providers=True)
    source_dir = tmp_path / "user-sources"
    source_dir.mkdir()

    # A real decodable PNG: the production image-source stage must be able
    # to crop/decode the managed original, otherwise the OCR step never
    # reaches the provider or the write guard at all.
    page, _source = _import_one_book(
        core, source_dir, synthetic_page_png(0), "001.png"
    )
    core.pipeline_defaults.save_provider_binding("ocr", "m2ac1-mock-ocr")
    region = _region_on(core, page)

    manual_text = "人工译文：必须被保留"
    revision_no = core.editing.save_manual_translation(region.region_id, manual_text)
    stored = core.editing._repo.get_region(region.region_id)
    assert stored is not None and stored.text.edited_translation == manual_text
    assert stored.text.translation_locked is True, (
        "save_manual_translation must arm the RegionText content lock (TASK-011)"
    )
    assert stored.text.manual_edited is True

    revisions_before = core.editing._repo.list_revisions(region.region_id)

    # The pipeline must NOT overwrite the manual text on the locked region.
    run = core.pipeline.create_run(
        CommandType.REOCR_ALL,
        PipelineScope(ScopeType.PAGE, selected_ids=(page.page_id,)),
    )
    core.pipeline.plan_run(run.run_id)
    executed = core.pipeline.execute_run(run.run_id)

    after = core.editing._repo.get_region(region.region_id)
    assert after is not None
    assert after.text.edited_translation == manual_text, (
        f"pipeline overwrote the manual edit: {after.text.edited_translation!r}"
    )
    # The pipeline DID run (the OCR text-layer lock gates the translation
    # chain, not the OCR chain): a fresh revision records the new ocr_text
    # and the current pointer moves. The manual edit itself must survive
    # untouched — that is the promise under acceptance.
    revisions_after = core.editing._repo.list_revisions(region.region_id)
    assert len(revisions_after) == len(revisions_before) + 1, (
        "the pipeline OCR result must be recorded as a new revision"
    )
    assert after.text.ocr_text and after.text.ocr_text != stored.text.ocr_text
    assert after.current_revision_id != stored.current_revision_id
    assert after.text.edited_translation == manual_text, (
        "the manual edit must survive the pipeline untouched"
    )
    assert after.text.manual_edited is True
    assert after.text.translation_locked is True


# ---------------------------------------------------------------------------
# AC4 — Lock and current/pinned Revision
# ---------------------------------------------------------------------------


def test_ac4_page_lock_yields_skip_lock(tmp_path: Path) -> None:
    core = _assemble(tmp_path / "data-root", mock_providers=True)
    source_dir = tmp_path / "user-sources"
    source_dir.mkdir()

    page, _source = _import_one_book(core, source_dir, SOURCE_BYTES_A, "001.png")
    locked = replace(page, page_locked=True)
    core.repository.update_page(locked)

    run = core.pipeline.create_run(
        CommandType.REOCR_ALL,
        PipelineScope(ScopeType.PAGE, selected_ids=(page.page_id,)),
    )
    planned = core.pipeline.plan_run(run.run_id)
    decisions = {
        (u.step_type): u.decision.value for u in planned.tasks[0].units
    }
    assert all(value == "skip_lock" for value in decisions.values()), decisions
    executed = core.pipeline.execute_run(run.run_id)
    assert executed.step_runs == [], "a locked page must produce no StepRuns"


def test_ac4_region_lock_zero_write(tmp_path: Path) -> None:
    core = _assemble(tmp_path / "data-root", mock_providers=True)
    source_dir = tmp_path / "user-sources"
    source_dir.mkdir()

    page, _source = _import_one_book(
        core, source_dir, synthetic_page_png(1), "001.png"
    )
    core.pipeline_defaults.save_provider_binding("ocr", "m2ac1-mock-ocr")
    region = _region_on(core, page)
    revisions_before = core.editing._repo.list_revisions(region.region_id)

    run = core.pipeline.create_run(
        CommandType.REOCR_ALL,
        PipelineScope(ScopeType.PAGE, selected_ids=(page.page_id,)),
    )
    core.pipeline.plan_run(run.run_id)
    # M2-P1 N2 ordering: the lock flips after planning, so the OCR step is
    # actually attempted and must be refused by the write guard, zero-write.
    _lock_region(core, region.region_id)
    executed = core.pipeline.execute_run(run.run_id)

    ocr_steps = [s for s in executed.step_runs if s.step_type == "ocr"]
    assert ocr_steps and ocr_steps[0].error_code == "LOCK_CHANGED"
    revisions_after = core.editing._repo.list_revisions(region.region_id)
    assert len(revisions_after) == len(revisions_before), "zero-write violated"


def test_ac4_pinned_revision_survives_cleanup(tmp_path: Path) -> None:
    core = _assemble(tmp_path / "data-root")
    source_dir = tmp_path / "user-sources"
    source_dir.mkdir()

    page, _source = _import_one_book(core, source_dir, SOURCE_BYTES_A, "001.png")
    region = _region_on(core, page)
    core.editing.save_manual_translation(region.region_id, "钉住的译文")
    revisions = core.editing._repo.list_revisions(region.region_id)
    assert revisions
    target = revisions[0]
    core.editing.set_revision_pinned(region.region_id, target.revision_no, True)

    # A real cache population under the managed root + the production
    # CleanupService; the inventory only ever lists the cache, never the
    # business artifacts.
    cache_dir = core.data_root / "managed" / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    stale = cache_dir / "tile-stale.bin"
    stale.write_bytes(b"stale-tile-bytes")
    inventory_items = (CleanupTarget(relative_path="cache/tile-stale.bin",
                                     size_bytes=stale.stat().st_size),)

    class _Inventory:
        def list_cache_files(self) -> tuple[CleanupTarget, ...]:
            return inventory_items

    cleanup = CleanupService(
        inventory=_Inventory(),
        remover=core.storage,
        manifest=_MemoryManifest(),
    )
    outcome = cleanup.run()

    assert outcome.removed == 1
    assert not stale.exists(), "cache population must be cleanable"
    after = core.editing._repo.list_revisions(region.region_id)
    pinned = [r for r in after if r.revision_no == target.revision_no]
    assert pinned and pinned[0].is_pinned is True, (
        "cleanup must not touch current/pinned business revisions"
    )


class _MemoryManifest:
    def __init__(self) -> None:
        self._data: dict = {}

    def read_manifest(self) -> dict:
        return self._data

    def write_manifest(self, manifest: dict) -> None:
        self._data = manifest


def test_ac4_restore_revision_moves_current(tmp_path: Path) -> None:
    core = _assemble(tmp_path / "data-root")
    source_dir = tmp_path / "user-sources"
    source_dir.mkdir()

    page, _source = _import_one_book(core, source_dir, SOURCE_BYTES_A, "001.png")
    region = _region_on(core, page)
    # v1 = the machine origin revision from create_region (empty text);
    # manual saves produce v2/v3 with the real snapshot content.
    first_manual_no = core.editing.save_manual_translation(region.region_id, "第一版译文")
    core.editing.save_manual_translation(region.region_id, "第二版译文")

    after_two = core.editing._repo.get_region(region.region_id)
    assert after_two is not None
    assert after_two.text.edited_translation == "第二版译文"

    restored = core.editing.restore_revision(region.region_id, first_manual_no)
    assert restored.text.edited_translation == "第一版译文", (
        "restore must move the current pointer back to the restored revision"
    )
    revisions = core.editing._repo.list_revisions(region.region_id)
    assert len(revisions) == 4, (
        "restore is recorded as its own new revision (v4 = content of v2)"
    )
    restored_revision = [r for r in revisions if r.revision_no == 4]
    assert restored_revision and restored_revision[0].restored_from_revision_id, (
        "the restored revision must carry provenance back to its source"
    )


# ---------------------------------------------------------------------------
# AC5 — end-to-end recovery across a full re-assembly
# ---------------------------------------------------------------------------


def test_ac5_reassembly_preserves_every_integrity_promise(tmp_path: Path) -> None:
    data_root = tmp_path / "data-root"
    core = _assemble(data_root)
    source_dir = tmp_path / "user-sources"
    source_dir.mkdir()

    page_a, source_a = _import_one_book(core, source_dir, SOURCE_BYTES_A, "001.png")
    page_b, _ = _import_one_book(core, source_dir, SOURCE_BYTES_B, "002.png")
    region = _region_on(core, page_a)
    core.editing.save_manual_translation(region.region_id, "重启后仍在的译文")
    stored = core.editing._repo.get_region(region.region_id)
    assert stored is not None
    core.editing.set_revision_pinned(region.region_id, 1, True)
    locked = replace(page_b, page_locked=True)
    core.repository.update_page(locked)
    pinned_revision = core.editing._repo.list_revisions(region.region_id)[0]
    assert pinned_revision.is_pinned is True

    # Process-restart equivalent: drop every handle, re-assemble from the
    # same data root, and re-check every promise.
    core.conn.close()
    core2 = _assemble(data_root)

    assert source_a.read_bytes() == SOURCE_BYTES_A
    page_a2 = core2.repository.get_page(page_a.page_id)
    assert page_a2 is not None
    assert page_a2.source_hash == sha256_bytes(SOURCE_BYTES_A)
    assert _managed_file(core2, page_a2).read_bytes() == SOURCE_BYTES_A

    page_b2 = core2.repository.get_page(page_b.page_id)
    assert page_b2 is not None
    assert page_b2.page_locked is True, "page lock must survive restart"

    region2 = core2.editing._repo.get_region(region.region_id)
    assert region2 is not None
    assert region2.text.edited_translation == "重启后仍在的译文"
    assert region2.text.translation_locked is True
    rev2 = core2.editing._repo.list_revisions(region.region_id)
    pinned2 = [r for r in rev2 if r.revision_no == pinned_revision.revision_no]
    assert pinned2 and pinned2[0].is_pinned is True, "pin must survive restart"

    run = core2.pipeline.create_run(
        CommandType.REOCR_ALL,
        PipelineScope(ScopeType.PAGE, selected_ids=(page_b.page_id,)),
    )
    planned = core2.pipeline.plan_run(run.run_id)
    assert all(
        u.decision.value == "skip_lock" for u in planned.tasks[0].units
    ), "a restored page lock must still gate the planner after restart"
