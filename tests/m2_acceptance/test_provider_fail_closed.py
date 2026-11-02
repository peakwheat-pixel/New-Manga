"""M2-AC3 Provider Fail-closed Acceptance suite (doc/tasks/M2-AC3.md).

Verifies the Rebaseline Plan M2 Acceptance Backlog row 3 promises through
the PRODUCTION assembly function (``assemble_core_services`` -- the exact
assembly the production sidecar calls) with a real SQLite store and a real
filesystem, mirroring the M2-AC2 precedent inside ``tests/m2_acceptance/``:

  AC1  Provider unconfigured (zero config / missing binding / dangling
       binding) → typed ``PROVIDER_NOT_CONFIGURED`` / ``PROVIDER_UNAVAILABLE``,
       no fabricated results (no Region, no revision, no artifact)
  AC2  Network failure mid-run → typed retryable code, every existing
       result (manual edit, translation lock, pin, revisions) intact
  AC3  Partial failure → honest ``COMPLETED_WITH_FAILURES`` boundary,
       per-page diagnosability, success page fully usable
  AC4  User source files byte/mtime-identical across all failure runs;
       managed copy never partially written
  AC5  Recovery: re-assembly (process-restart equivalent) keeps the run
       truth queryable; retry after the fix leaves no duplicate or dangling
       results

Failure-injection follows the assembly adapter-injection precedent
(M2-AC1/M2-AC2): fixture providers are registered on the production
runtime registry under ``m2ac3-*`` ids and selected through the persisted
``pipeline_defaults`` binding -- the same channel a real provider binding
uses. No IPC surface, no test-mode bridge.

Pure acceptance: NO product code may change here. A failing scenario is a
valid delivery outcome -- the defect is reported, not patched.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from application.translation.color.service import SourceStyleService  # noqa: E402
from application.importing.images.ports import DecodedImage, ImportSource  # noqa: E402
from bootstrap.acceptance_bridge import synthetic_page_png  # noqa: E402
from bootstrap.core_assembly import assemble_core_services  # noqa: E402
from domain.regions.entities import BBox, RegionGeometry, RegionOrigin  # noqa: E402
from domain.tasks.models import CommandType, PipelineRunStatus  # noqa: E402
from domain.tasks.models import PipelineScope, PipelineTaskStatus, ScopeType  # noqa: E402
from infrastructure.providers.registry import ProviderDescriptor  # noqa: E402
from ports.ocr.ports import OcrRequest, OcrResult  # noqa: E402
from ports.providers.errors import (  # noqa: E402
    ProviderTimeout,
    ProviderUnavailable,
)
from ports.providers.profiles import CAPABILITY_OCR  # noqa: E402


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


def _assemble(data_root: Path, *, mock_providers: bool = False):
    """The production sidecar assembly (``assemble_production_core``) with an
    optional acceptance-provider upgrade (M2-AC1 precedent) for the pipeline
    scenarios. No other deviation from the production path."""

    return assemble_core_services(
        data_root / "library.db",
        data_root / "managed",
        image_decoder=_AcceptanceDecoder(),
        font_catalog=object(),  # type: ignore[arg-type]
        layout_engine=object(),  # type: ignore[arg-type]
        compositor=object(),  # type: ignore[arg-type]
        source_styles=SourceStyleService(_AcceptanceStyleAnalyzer()),
        mock_local_providers=mock_providers,
    )


def _import_page(core, source_dir: Path, payload: bytes, filename: str):
    """Book -> chapter -> one real source file on disk -> production import.

    Returns (page, source_path)."""

    def provider() -> bytes:
        return payload

    book = core.library.create_book("M2-AC3 Fail-closed Book")
    chapter = core.library.create_chapter(book.book_id, "Chapter 1")
    source_path = source_dir / filename
    source_path.write_bytes(payload)
    report = core.importer.import_files(
        chapter.chapter_id,
        [ImportSource(filename=filename, data_provider=provider)],
    )
    assert len(report.imported) == 1, f"import failed: {report.failed}"
    return report.imported[0].page, source_path


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


def _register_ocr_provider(core, provider) -> None:
    """Register a fixture OCR provider on the production runtime registry.

    The production registry never sees ``m2ac3-*`` ids from the assembly;
    registering through the same ``registry.register`` seam a real provider
    uses keeps the resolution path (and its fail-closed ladder) untouched.
    """

    core.providers.registry.register(
        ProviderDescriptor(
            provider_id=provider.provider_id,
            provider_type=provider.provider_type,
            capabilities=frozenset({CAPABILITY_OCR}),
            note="M2-AC3 acceptance fixture (never in production)",
        ),
        lambda provider=provider: provider,
    )


def _plan_and_execute(core, page_ids):
    run = core.pipeline.create_run(
        CommandType.REOCR_ALL,
        PipelineScope(ScopeType.PAGE, selected_ids=tuple(page_ids)),
    )
    core.pipeline.plan_run(run.run_id)
    return core.pipeline.execute_run(run.run_id)


def _revision_count(core, region_id: str) -> int:
    return len(core.editing._repo.list_revisions(region_id))


def _managed_inventory(core) -> set[str]:
    managed = core.data_root / "managed"
    return {
        p.relative_to(managed).as_posix()
        for p in managed.rglob("*")
        if p.is_file()
    }


def _fail_step(executed, task):
    """The FAILED StepRun of one task (guard: exactly one, typed)."""
    steps = [
        step
        for step in executed.step_runs
        if step.task_id == task.task_id and step.status.value == "failed"
    ]
    assert steps, (
        f"task {task.task_id} is {task.status.value} but carries no FAILED "
        "StepRun; the failure would be undiagnosable"
    )
    return steps[0]


# ---------------------------------------------------------------------------
# Failure-injection fixtures (registered on the production registry)
# ---------------------------------------------------------------------------


@dataclass
class _UnreachableOcrProvider:
    """Transport-level failure: every call raises the typed timeout code."""

    provider_id: str = "m2ac3-unreachable-ocr"
    provider_type: str = "m2ac3-acceptance-fixture"
    model: str = "unreachable-v1"
    requires_gpu: bool = False

    def recognize(self, request: OcrRequest) -> OcrResult:
        raise ProviderTimeout(
            "transport read timed out",
            provider_id=self.provider_id,
            stage="ocr",
        )


@dataclass
class _SelectiveOcrProvider:
    """Succeeds for every page except the ids in ``fail_pages`` (AC3)."""

    fail_pages: frozenset[str]
    provider_id: str = "m2ac3-selective-ocr"
    provider_type: str = "m2ac3-acceptance-fixture"
    model: str = "selective-v1"
    requires_gpu: bool = False

    def recognize(self, request: OcrRequest) -> OcrResult:
        if request.page_id in self.fail_pages:
            raise ProviderUnavailable(
                "upstream provider connection reset",
                provider_id=self.provider_id,
                stage="ocr",
            )
        from infrastructure.providers.mock_local import MOCK_OCR_TEXT

        return OcrResult(
            region_id=request.region_id,
            text=MOCK_OCR_TEXT,
            provider_id=self.provider_id,
            provider_type=self.provider_type,
            model=self.model,
            confidence=1.0,
            script=request.script,
            direction=request.direction,
        )


# ---------------------------------------------------------------------------
# AC1 — Provider unconfigured fails closed, no fabricated results
# ---------------------------------------------------------------------------


def test_ac1_zero_config_detect_fails_closed_without_fabricated_regions(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """AC1: a production assembly with zero provider configuration (no
    binding, no docTR weights) must fail the page-level run at the detect
    capability gap with a typed code, and land NO Region, NO revision and
    NO candidate -- the run never invents half-done results."""
    # The zero-config promise is about THIS data root; a host-provided
    # weights override would silently move the gap out of the scenario.
    monkeypatch.delenv("NEWMANGA_DETECTOR_WEIGHTS", raising=False)
    core = _assemble(tmp_path / "data-root")
    source_dir = tmp_path / "user-sources"
    source_dir.mkdir()

    # A REAL decodable PNG: the detect step reaches the frame read, so the
    # failure comes from the weights gap, not from an undecodable payload.
    page, _source = _import_page(
        core, source_dir, synthetic_page_png(0), "001.png"
    )
    inventory_before = _managed_inventory(core)

    executed = _plan_and_execute(core, (page.page_id,))

    assert executed.status is PipelineRunStatus.COMPLETED_WITH_FAILURES, (
        f"a zero-config run must not report success, got {executed.status!r}"
    )
    assert len(executed.tasks) == 1
    task = executed.tasks[0]
    assert task.status is PipelineTaskStatus.FAILED
    assert task.error_code == "PROVIDER_NOT_CONFIGURED", (
        f"expected the typed configuration gap, got {task.error_code!r}"
    )
    step = _fail_step(executed, task)
    assert step.step_type == "detect"
    assert step.error_code == "PROVIDER_NOT_CONFIGURED"
    detail = step.error_detail or ""
    assert "weights are not installed" in detail, (
        f"the detail must diagnose the missing-weights gap, got {detail!r}"
    )

    # No fabricated results: the detect failure must not leave a Region,
    # a revision, a committed candidate or any new managed artifact.
    assert core.editing._repo.list_regions(page.page_id) == [], (
        "a failed detect step must not fabricate Regions"
    )
    assert not executed.candidates, (
        "a failed step must not commit a result candidate"
    )
    assert _managed_inventory(core) == inventory_before, (
        "a failed run must not write new managed artifacts"
    )


def test_ac1_missing_binding_fails_closed_with_typed_slot(tmp_path: Path) -> None:
    """AC1: a region-level OCR run without any provider binding fails at
    the typed ``PROVIDER_NOT_CONFIGURED`` slot with a detail that names the
    unconfigured step -- distinguishable from every other failure -- and
    keeps the Region byte-for-byte untouched."""
    core = _assemble(tmp_path / "data-root", mock_providers=True)
    source_dir = tmp_path / "user-sources"
    source_dir.mkdir()

    page, _source = _import_page(
        core, source_dir, synthetic_page_png(1), "001.png"
    )
    region = _region_on(core, page)
    revisions_before = _revision_count(core, region.region_id)
    stored_before = core.editing._repo.get_region(region.region_id)
    assert stored_before is not None

    executed = _plan_and_execute(core, (page.page_id,))

    assert executed.status is PipelineRunStatus.COMPLETED_WITH_FAILURES
    task = executed.tasks[0]
    assert task.page_id == page.page_id
    assert task.status is PipelineTaskStatus.FAILED
    assert task.error_code == "PROVIDER_NOT_CONFIGURED"
    step = _fail_step(executed, task)
    assert step.step_type == "ocr"
    assert step.error_code == "PROVIDER_NOT_CONFIGURED"
    detail = step.error_detail or ""
    assert "no provider binding configured for step 'ocr'" in detail, (
        f"the detail must name the unconfigured step, got {detail!r}"
    )

    stored_after = core.editing._repo.get_region(region.region_id)
    assert stored_after is not None
    assert _revision_count(core, region.region_id) == revisions_before, (
        "an unconfigured run must not land a half-done revision"
    )
    assert stored_after.current_revision_id == stored_before.current_revision_id
    assert stored_after.text.ocr_text == stored_before.text.ocr_text


def test_ac1_dangling_binding_reports_unavailable_not_silent(
    tmp_path: Path,
) -> None:
    """AC1: a binding that names an unregistered provider id fails closed
    at registry resolution with ``PROVIDER_UNAVAILABLE`` and a detail that
    names the missing id -- the caller can tell "never registered" apart
    from a mid-run network fault (AC2) and from an unconfigured binding."""
    core = _assemble(tmp_path / "data-root", mock_providers=True)
    source_dir = tmp_path / "user-sources"
    source_dir.mkdir()

    page, _source = _import_page(
        core, source_dir, synthetic_page_png(2), "001.png"
    )
    region = _region_on(core, page)
    revisions_before = _revision_count(core, region.region_id)
    core.pipeline_defaults.save_provider_binding("ocr", "m2ac3-ghost-ocr")

    executed = _plan_and_execute(core, (page.page_id,))

    assert executed.status is PipelineRunStatus.COMPLETED_WITH_FAILURES
    task = executed.tasks[0]
    assert task.status is PipelineTaskStatus.FAILED
    assert task.error_code == "PROVIDER_UNAVAILABLE", (
        f"a dangling binding must fail closed at resolve, got {task.error_code!r}"
    )
    step = _fail_step(executed, task)
    assert step.error_code == "PROVIDER_UNAVAILABLE"
    detail = step.error_detail or ""
    assert "no provider registered as 'm2ac3-ghost-ocr'" in detail, (
        f"the detail must name the missing provider id, got {detail!r}"
    )
    assert _revision_count(core, region.region_id) == revisions_before, (
        "a failed resolve must not land a half-done revision"
    )


# ---------------------------------------------------------------------------
# AC2 — Network failure is typed and every existing result stays intact
# ---------------------------------------------------------------------------


def test_ac2_network_failure_typed_and_existing_results_intact(
    tmp_path: Path,
) -> None:
    """AC2: a provider transport failure mid-run surfaces as the typed
    retryable code (not swallowed, not reported as success), and every
    pre-existing result survives byte-for-byte: the manual translation,
    its content lock, the pinned revision and the revision sequence."""
    core = _assemble(tmp_path / "data-root", mock_providers=True)
    source_dir = tmp_path / "user-sources"
    source_dir.mkdir()

    page, _source = _import_page(
        core, source_dir, synthetic_page_png(3), "001.png"
    )
    region = _region_on(core, page)
    manual_text = "人工译文：网络失败后必须原样保留"
    manual_no = core.editing.save_manual_translation(region.region_id, manual_text)
    core.editing.set_revision_pinned(region.region_id, 1, True)
    stored_before = core.editing._repo.get_region(region.region_id)
    assert stored_before is not None
    assert stored_before.text.translation_locked is True
    revisions_before = _revision_count(core, region.region_id)

    provider = _UnreachableOcrProvider()
    _register_ocr_provider(core, provider)
    core.pipeline_defaults.save_provider_binding("ocr", provider.provider_id)

    executed = _plan_and_execute(core, (page.page_id,))

    assert executed.status is PipelineRunStatus.COMPLETED_WITH_FAILURES, (
        f"a network-failed run must not report success, got {executed.status!r}"
    )
    task = executed.tasks[0]
    assert task.status is PipelineTaskStatus.FAILED
    assert task.error_code == "PROVIDER_TIMEOUT", (
        f"a transport fault must keep its typed code, got {task.error_code!r}"
    )
    step = _fail_step(executed, task)
    assert step.error_code == "PROVIDER_TIMEOUT"
    assert step.error_code != "PROVIDER_NOT_CONFIGURED", (
        "a network failure must stay distinguishable from an unconfigured one"
    )
    detail = step.error_detail or ""
    assert "transport read timed out" in detail
    assert provider.provider_id in detail, (
        "the detail must carry the failing provider id for diagnosis"
    )

    after = core.editing._repo.get_region(region.region_id)
    assert after is not None
    assert after.text.edited_translation == manual_text, (
        "the manual translation must survive a failed run untouched"
    )
    assert after.text.translation_locked is True
    assert after.text.manual_edited is True
    assert after.current_revision_id == stored_before.current_revision_id, (
        "a failed run must not move the current pointer"
    )
    revisions_after = core.editing._repo.list_revisions(region.region_id)
    assert len(revisions_after) == revisions_before, (
        "a failed run must not land a half-done revision"
    )
    pinned = [r for r in revisions_after if r.revision_no == 1]
    assert pinned and pinned[0].is_pinned is True, (
        "the pinned revision must survive the failed run"
    )
    del manual_no


# ---------------------------------------------------------------------------
# AC3 — Partial failure boundary is honest and per-page diagnosable
# ---------------------------------------------------------------------------


def test_ac3_partial_failure_run_boundary_is_honest(tmp_path: Path) -> None:
    """AC3: a two-page run where the provider succeeds for page A and the
    transport fails for page B must end ``COMPLETED_WITH_FAILURES`` with an
    honest, queryable boundary: A's result is complete and usable, B lands
    nothing, and each page carries its own outcome."""
    from infrastructure.providers.mock_local import MOCK_OCR_TEXT

    core = _assemble(tmp_path / "data-root", mock_providers=True)
    source_dir = tmp_path / "user-sources"
    source_dir.mkdir()

    page_a, _ = _import_page(core, source_dir, synthetic_page_png(4), "001.png")
    page_b, _ = _import_page(core, source_dir, synthetic_page_png(5), "002.png")
    region_a = _region_on(core, page_a)
    region_b = _region_on(core, page_b)
    revisions_a_before = _revision_count(core, region_a.region_id)
    revisions_b_before = _revision_count(core, region_b.region_id)

    provider = _SelectiveOcrProvider(fail_pages=frozenset({page_b.page_id}))
    _register_ocr_provider(core, provider)
    core.pipeline_defaults.save_provider_binding("ocr", provider.provider_id)

    executed = _plan_and_execute(core, (page_a.page_id, page_b.page_id))

    assert executed.status is PipelineRunStatus.COMPLETED_WITH_FAILURES, (
        f"a mixed run must not collapse to success, got {executed.status!r}"
    )
    by_page = {task.page_id: task for task in executed.tasks}
    assert set(by_page) == {page_a.page_id, page_b.page_id}
    task_a = by_page[page_a.page_id]
    task_b = by_page[page_b.page_id]
    assert task_a.status is PipelineTaskStatus.COMPLETED
    assert task_b.status is PipelineTaskStatus.FAILED

    # Success page: a complete, usable result -- fresh revision with the
    # provider text and the current pointer moved onto it.
    assert _revision_count(core, region_a.region_id) == revisions_a_before + 1, (
        "the succeeded page must land exactly one new revision"
    )
    region_a_after = core.editing._repo.get_region(region_a.region_id)
    assert region_a_after is not None
    assert region_a_after.text.ocr_text == MOCK_OCR_TEXT
    revisions_a = core.editing._repo.list_revisions(region_a.region_id)
    latest_a = max(r.revision_no for r in revisions_a)
    current_a = next(
        r for r in revisions_a
        if r.region_revision_id == region_a_after.current_revision_id
    )
    assert current_a.revision_no == latest_a, (
        "the success page's current pointer must sit on its newest revision"
    )

    # Failure page: zero fabricated results, typed per-page diagnosis.
    assert _revision_count(core, region_b.region_id) == revisions_b_before, (
        "the failed page must not land any revision"
    )
    assert task_b.error_code == "PROVIDER_UNAVAILABLE"
    step_b = _fail_step(executed, task_b)
    assert step_b.error_code == "PROVIDER_UNAVAILABLE"
    detail_b = step_b.error_detail or ""
    assert "upstream provider connection reset" in detail_b
    assert provider.provider_id in detail_b
    region_b_after = core.editing._repo.get_region(region_b.region_id)
    assert region_b_after is not None
    assert region_b_after.text.ocr_text == "" , (
        "the failed page must not fabricate OCR text"
    )


# ---------------------------------------------------------------------------
# AC4 — User source files are untouched across every failure run
# ---------------------------------------------------------------------------


def test_ac4_source_files_untouched_across_failure_runs(tmp_path: Path) -> None:
    """AC4: across two consecutive failing runs (unconfigured binding, then
    dangling binding) the user source file keeps its bytes and mtime, its
    directory gains nothing, and the managed copy never diverges from the
    source bytes (no partial write)."""
    core = _assemble(tmp_path / "data-root")
    source_dir = tmp_path / "user-sources"
    source_dir.mkdir()

    payload = synthetic_page_png(0)
    page, source_path = _import_page(core, source_dir, payload, "001.png")
    region = _region_on(core, page)
    managed = core.data_root / "managed" / page.managed_original_ref
    assert managed.is_file()

    source_bytes = source_path.read_bytes()
    source_mtime = source_path.stat().st_mtime_ns
    dir_before = sorted(p.name for p in source_dir.iterdir())
    managed_before = managed.read_bytes()

    # Run 1: region-level OCR with no binding at all -> typed config gap.
    executed_1 = _plan_and_execute(core, (page.page_id,))
    assert executed_1.status is PipelineRunStatus.COMPLETED_WITH_FAILURES
    assert executed_1.tasks[0].error_code == "PROVIDER_NOT_CONFIGURED"

    # Run 2: a dangling binding -> typed resolve gap.
    core.pipeline_defaults.save_provider_binding("ocr", "m2ac3-ghost-ocr")
    executed_2 = _plan_and_execute(core, (page.page_id,))
    assert executed_2.status is PipelineRunStatus.COMPLETED_WITH_FAILURES
    assert executed_2.tasks[0].error_code == "PROVIDER_UNAVAILABLE"

    # The source file is untouched: bytes, size, mtime, directory.
    assert source_path.read_bytes() == source_bytes, "source bytes changed"
    assert source_path.stat().st_size == len(source_bytes)
    assert source_path.stat().st_mtime_ns == source_mtime, (
        "the user source file was rewritten (mtime changed)"
    )
    assert sorted(p.name for p in source_dir.iterdir()) == dir_before

    # The managed copy holds exactly the source bytes -- no partial write.
    assert managed.read_bytes() == payload
    assert managed.read_bytes() == source_bytes
    del region


# ---------------------------------------------------------------------------
# AC5 — Recovery: re-assembly keeps the truth; retry leaves no debris
# ---------------------------------------------------------------------------


def test_ac5_reassembly_after_failure_preserves_run_truth(tmp_path: Path) -> None:
    """AC5: after a failed run, a full re-assembly on the same data root
    (process-restart equivalent) still reports the same run status, the
    same typed per-task error and the same step-level detail -- the failure
    stays diagnosable across a restart, and the Region stays untouched."""
    core = _assemble(tmp_path / "data-root")
    source_dir = tmp_path / "user-sources"
    source_dir.mkdir()

    page, _source = _import_page(
        core, source_dir, synthetic_page_png(6), "001.png"
    )
    region = _region_on(core, page)
    revisions_before = _revision_count(core, region.region_id)

    executed = _plan_and_execute(core, (page.page_id,))
    assert executed.status is PipelineRunStatus.COMPLETED_WITH_FAILURES
    assert executed.tasks[0].error_code == "PROVIDER_NOT_CONFIGURED"
    run_id = executed.run_id

    core.conn.close()
    core2 = _assemble(tmp_path / "data-root")

    stored = core2.pipeline._store.get(run_id)
    assert stored is not None, "the failed run must survive a restart"
    assert stored.status is PipelineRunStatus.COMPLETED_WITH_FAILURES
    assert len(stored.tasks) == 1
    assert stored.tasks[0].status is PipelineTaskStatus.FAILED
    assert stored.tasks[0].error_code == "PROVIDER_NOT_CONFIGURED"
    failed_steps = [
        step for step in stored.step_runs if step.status.value == "failed"
    ]
    assert failed_steps, "the typed step failure must survive the restart"
    assert failed_steps[0].error_code == "PROVIDER_NOT_CONFIGURED"
    assert "no provider binding configured for step 'ocr'" in (
        failed_steps[0].error_detail or ""
    )

    region2 = core2.editing._repo.get_region(region.region_id)
    assert region2 is not None
    assert _revision_count(core2, region.region_id) == revisions_before, (
        "a restart must not retroactively alter the failed run's writes"
    )


def test_ac5_retry_after_fix_leaves_no_duplicates_or_dangling(
    tmp_path: Path,
) -> None:
    """AC5: after a network-failed run, fixing the binding and re-running
    on the same data root succeeds, and the Region's revision sequence has
    no duplicate or dangling entry: consecutive revision numbers, the
    current pointer on the newest revision, exactly one result per success."""
    core = _assemble(tmp_path / "data-root", mock_providers=True)
    source_dir = tmp_path / "user-sources"
    source_dir.mkdir()

    page, _source = _import_page(
        core, source_dir, synthetic_page_png(7), "001.png"
    )
    region = _region_on(core, page)
    region_id = region.region_id

    provider = _UnreachableOcrProvider()
    _register_ocr_provider(core, provider)
    core.pipeline_defaults.save_provider_binding("ocr", provider.provider_id)
    failed = _plan_and_execute(core, (page.page_id,))
    assert failed.status is PipelineRunStatus.COMPLETED_WITH_FAILURES
    assert failed.tasks[0].error_code == "PROVIDER_TIMEOUT"
    failed_run_id = failed.run_id
    revisions_after_failure = _revision_count(core, region_id)

    # Process-restart equivalent, then the fix: the binding moves to the
    # deterministic mock provider (M2-AC1 registry), and the same command
    # is re-run against the same data root.
    core.conn.close()
    core2 = _assemble(tmp_path / "data-root", mock_providers=True)
    core2.pipeline_defaults.save_provider_binding("ocr", "m2ac1-mock-ocr")

    retried = _plan_and_execute(core2, (page.page_id,))
    assert retried.status is PipelineRunStatus.COMPLETED, (
        f"the fixed retry must succeed, got {retried.status!r}"
    )
    # The failed run keeps its terminal truth; the retry does not revive it.
    stored_failed = core2.pipeline._store.get(failed_run_id)
    assert stored_failed is not None
    assert stored_failed.status is PipelineRunStatus.COMPLETED_WITH_FAILURES

    # No duplicate, no dangling: v1 is the creation origin (empty text),
    # the failed run added nothing, and the successful retry added exactly
    # one revision carrying the provider text with current on it.
    assert revisions_after_failure == 1, (
        "the failed run must have added no revision before the retry"
    )
    revisions = core2.editing._repo.list_revisions(region_id)
    numbers = sorted(r.revision_no for r in revisions)
    assert numbers == list(range(1, len(numbers) + 1)), (
        f"revision numbers must be consecutive with no duplicates, got {numbers}"
    )
    assert len(revisions) == 2, (
        "one failure + one success must leave exactly origin + result"
    )
    region_after = core2.editing._repo.get_region(region_id)
    assert region_after is not None
    current = next(
        r
        for r in revisions
        if r.region_revision_id == region_after.current_revision_id
    )
    assert current.revision_no == numbers[-1], (
        "current must sit on the newest revision, not dangle behind"
    )
    from infrastructure.providers.mock_local import MOCK_OCR_TEXT

    assert region_after.text.ocr_text == MOCK_OCR_TEXT, (
        "the retry's result must carry the provider text via the current revision"
    )
