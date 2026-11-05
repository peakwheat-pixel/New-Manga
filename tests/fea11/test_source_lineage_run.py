"""FEA-11-LINEAGE-1 r3: page-scope Run execution chain and candidate projection.

r2 Review R2-01 (P1): the page-scope Run *execution* chain bypassed the
C-17 §7.1 lineage visibility set — ``handlers.handle_detect`` reused every
live Region through the page-id-only repository (hidden old-binding Regions
included), ``_backfill_detected_regions`` then hit the lineage guard and the
broad ``commit_step`` except turned the step into ``DB_FAILED``. These tests
drive the REAL production pipeline over REAL SQLite (stub providers only for
the external capabilities):

* cut page + hidden Region + stub detector → ``REOCR_ALL`` reuses nothing,
  detects on the NEW image, completes, and the hidden Region gains neither a
  revision nor a lineage row;
* the same page's ``RERENDER_ALL`` is a clean terminal no-op (the visible
  region set is empty) instead of a page-level unit that could fail;
* a prepared OCR candidate whose binding is cut between prepare and commit is
  projected as the EXISTING ``input_revision_changed`` conflict (result kept
  as candidate), never ``DB_FAILED`` (r2 Review R2-02).
"""

from __future__ import annotations

import json
from typing import Any

import pytest

from application.editing.service import RegionEditingService
from application.sources.lineage import LINEAGE_BINDING_CHANGED
from domain.regions.entities import BBox, RegionGeometry, RegionOrigin, RegionType
from domain.tasks.models import (
    CommandType,
    PipelineRunStatus,
    PipelineScope,
    PipelineTaskStatus,
    ScopeType,
    StepRunStatus,
)
from infrastructure.filesystem.managed_storage import ManagedFileStorage
from infrastructure.pipeline.assembly import build_production_pipeline
from infrastructure.providers.handlers import (
    HandlerDependencies,
    ProductionHandlers,
    RegionMaskGeometry,
    STEP_DETECT,
    STEP_OCR,
)
from infrastructure.providers.registry import ProviderDescriptor, ProviderRegistry
from infrastructure.providers.retry import RetryPolicy
from infrastructure.providers.step_writes import (
    ArtifactStepWriter,
    RegionStepWriter,
)
from infrastructure.sqlite.regions import SqliteRegionRepository
from ports.detection.ports import DetectionRequest, DetectionResult, RegionCandidate
from ports.inpaint.ports import ImageFrame
from ports.ocr.ports import OcrResult
from ports.providers.profiles import CAPABILITY_OCR
from tests.fea11.conftest import add_sync_switch
from tests.fea11.test_source_lineage_native import (
    lineage_rows,
    make_guard,
    revision_count,
    seed_referenced_page,
    seed_region,
)


class _StubDetector:
    provider_id = "fake-detect"
    provider_type = "fake"

    def __init__(self) -> None:
        self.requests: list[DetectionRequest] = []

    def detect(self, request: DetectionRequest) -> DetectionResult:
        self.requests.append(request)
        return DetectionResult(
            page_id=request.page_id,
            candidates=(
                RegionCandidate(
                    polygon=((0.0, 0.0), (10.0, 0.0), (10.0, 5.0)),
                    reading_order=1,
                    provider_label="det-0",
                ),
                RegionCandidate(
                    polygon=((20.0, 8.0), (30.0, 8.0), (30.0, 12.0)),
                    reading_order=2,
                    provider_label="det-1",
                ),
            ),
            provider_id=self.provider_id,
            provider_type=self.provider_type,
        )


class _StubOcr:
    provider_id = "fake-ocr"
    provider_type = "fake"
    languages = frozenset({"japanese"})
    needs_detection = False
    requires_gpu = False

    def __init__(self) -> None:
        self.requests: list[Any] = []

    def recognize(self, request) -> OcrResult:
        self.requests.append(request)
        return OcrResult(
            region_id=request.region_id,
            text="検出後OCR",
            provider_id=self.provider_id,
            provider_type=self.provider_type,
            model="fake-model",
            confidence=0.9,
            script=request.script,
            direction=request.direction,
            options=request.options,
        )


class _StubImages:
    def page_frame(self, page_id: str) -> ImageFrame:
        return ImageFrame(width=32, height=16, mode="rgb24", data=b"\x00" * (32 * 16 * 3))

    def region_crop(self, page_id: str, region_id: str) -> tuple[bytes, int, int]:
        return b"crop-bytes", 4, 3

    def page_png(self, page_id: str) -> bytes:  # pragma: no cover - not used here
        raise AssertionError("REOCR_ALL must not need the page PNG")


class _StubGeometry:
    def mask_geometry(self, region_id: str) -> RegionMaskGeometry:
        return RegionMaskGeometry(boxes=((0, 0, 2, 2),))


def _build_pipeline(conn, *, page_binding: dict[str, str], tmp_path):
    """Production pipeline + real handlers over the given connection."""
    guard = make_guard(conn)
    regions = SqliteRegionRepository(conn, lineage_guard=guard)
    editing = RegionEditingService(
        regions, lineage_binding=page_binding.get, lineage_guard=guard
    )

    def region_creator(page_id, polygon, reading_order, provenance, provider_label=""):
        xs = [int(round(x)) for x, _ in polygon]
        ys = [int(round(y)) for _, y in polygon]
        region = editing.create_region(
            page_id,
            RegionGeometry(
                bbox=BBox(min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)),
                polygon=tuple((int(round(x)), int(round(y))) for x, y in polygon),
            ),
            region_type=(
                RegionType.SFX if str(provider_label).startswith("sfx") else RegionType.SPEECH
            ),
            reading_order=reading_order,
            origin=RegionOrigin.MACHINE,
        )
        return region.region_id

    registry = ProviderRegistry()
    ocr = _StubOcr()
    registry.register(
        ProviderDescriptor(
            provider_id=ocr.provider_id,
            provider_type="fake",
            capabilities=frozenset({CAPABILITY_OCR}),
        ),
        lambda: ocr,
    )
    storage = ManagedFileStorage(tmp_path / "managed")
    storage.ensure_layout()
    detector = _StubDetector()
    handlers = ProductionHandlers(
        HandlerDependencies(
            registry=registry,
            regions=regions,
            region_writer=RegionStepWriter(conn, regions),
            artifacts=ArtifactStepWriter(conn, storage),
            images=_StubImages(),
            geometry=_StubGeometry(),
            retry_policy=RetryPolicy(max_attempts=1, backoff_seconds=0),
            detector=detector,
            region_creator=region_creator,
            lineage_guard=guard,
        )
    )
    service = build_production_pipeline(
        conn,
        handlers=handlers.as_mapping(),
        settings={"ocr": {"script": "japanese"}},
        storage=storage,
        provider_bindings={"ocr": {"provider_id": ocr.provider_id}},
    )
    service._catalog.lineage_guard = guard
    service._catalog.lineage_binding = page_binding.get
    return service, regions, detector, ocr


def _cut_page_with_hidden_region(conn, book_chapter, tmp_path):
    page_id, binding_id = seed_referenced_page(conn, book_chapter)
    seed_region(conn, page_id, lineage=(binding_id, "captured_v7"))
    add_sync_switch(
        conn,
        page_id=page_id,
        old_binding_id=binding_id,
        new_binding_id="pb-p1-b2",
        relation="changed",
        seq=1,
    )
    service, regions, detector, ocr = _build_pipeline(
        conn, page_binding={page_id: "pb-p1-b2"}, tmp_path=tmp_path
    )
    return page_id, service, regions, detector, ocr


# ---------------------------------------------------------------------------
# R2-01 — page-scope REOCR_ALL over a cut page
# ---------------------------------------------------------------------------


def test_page_scope_reocr_all_filters_hidden_region_and_detects_new_image(
    conn, book_chapter, tmp_path
):
    page_id, service, regions, detector, ocr = _cut_page_with_hidden_region(
        conn, book_chapter, tmp_path
    )
    hidden_revision_count = revision_count(conn, "rg1")
    hidden_lineage_count = len(
        [row for row in lineage_rows(conn) if row["region_id"] == "rg1"]
    )
    assert hidden_revision_count == 1
    assert hidden_lineage_count == 1

    run = service.create_run(
        CommandType.REOCR_ALL,
        PipelineScope(ScopeType.PAGE, selected_ids=(page_id,)),
    )
    # The Run target snapshot already excludes the old-coordinate Region.
    assert run.targets[0].snapshot.regions == ()
    service.plan_run(run.run_id)
    executed = service.execute_run(run.run_id)

    assert executed.status is PipelineRunStatus.COMPLETED, [
        (step.step_type, step.error_code, step.error_detail)
        for step in executed.step_runs
    ]
    detect_steps = [s for s in executed.step_runs if s.step_type == STEP_DETECT]
    assert len(detect_steps) == 1
    detect_step = detect_steps[0]
    assert detect_step.status is StepRunStatus.COMPLETED
    detect_output = detect_step.output or {}
    output_ids = tuple(detect_output.get("region_ids") or ())
    # Discriminating assertion: the hidden old-coordinate Region is NOT reused.
    assert "rg1" not in output_ids
    assert len(output_ids) == 2
    assert detector.requests, "detection must run on the new image"

    # Two fresh Regions exist on the new binding; OCR ran on both.
    live = [region for region in regions.list_regions(page_id) if not region.deleted]
    assert len(live) == 3  # rg1 (hidden legacy) + 2 detected on the new image
    new_ids = {region.region_id for region in live if region.region_id != "rg1"}
    assert new_ids == set(output_ids)
    assert {step.region_id for step in executed.step_runs if step.step_type == STEP_OCR} == new_ids
    for region_id in new_ids:
        assert revision_count(conn, region_id) == 2  # detect + ocr
    # Native lineage is registered against the CURRENT binding for every new
    # revision of the new image.
    new_rows = [
        row for row in lineage_rows(conn) if row["region_id"] in new_ids
    ]
    assert {row["binding_id"] for row in new_rows} == {"pb-p1-b2"}
    assert {row["provenance"] for row in new_rows} == {"native"}
    assert ocr.requests, "OCR must run on the newly detected Regions"

    # The hidden legacy Region was not touched by the Run (zero write).
    assert revision_count(conn, "rg1") == hidden_revision_count
    assert len(
        [row for row in lineage_rows(conn) if row["region_id"] == "rg1"]
    ) == hidden_lineage_count


def test_page_scope_rerender_all_on_empty_visible_set_is_a_clean_noop(
    conn, book_chapter, tmp_path
):
    page_id, service, _regions, _detector, _ocr = _cut_page_with_hidden_region(
        conn, book_chapter, tmp_path
    )
    run = service.create_run(
        CommandType.RERENDER_ALL,
        PipelineScope(ScopeType.PAGE, selected_ids=(page_id,)),
    )
    assert run.targets[0].snapshot.regions == ()
    service.plan_run(run.run_id)
    executed = service.execute_run(run.run_id)

    # Clean terminal: no page-level unit, no DB_FAILED, no step at all.
    assert executed.status is PipelineRunStatus.COMPLETED
    assert list(executed.step_runs) == []
    assert executed.tasks[0].status is PipelineTaskStatus.SKIPPED
    assert all(
        (step.error_code or "") != "DB_FAILED" for step in executed.step_runs
    )
    # Nothing was written for the hidden Region.
    assert revision_count(conn, "rg1") == 1


# ---------------------------------------------------------------------------
# R2-02 — prepared candidate commit after a cut binding
# ---------------------------------------------------------------------------


def test_run_candidate_cut_between_prepare_and_commit_keeps_candidate_conflict(
    conn, book_chapter, tmp_path
):
    page_id, binding_id = seed_referenced_page(conn, book_chapter)
    seed_region(conn, page_id, lineage=(binding_id, "native"))
    page_binding = {page_id: binding_id}
    service, _regions, _detector, _ocr = _build_pipeline(
        conn, page_binding=page_binding, tmp_path=tmp_path
    )

    run = service.create_run(
        CommandType.OCR_REGION,
        PipelineScope(ScopeType.REGION, selected_ids=("rg1",)),
    )
    service.plan_run(run.run_id)
    step = service.record_step_attempt(run.tasks[0].task_id, "ocr")
    repo = SqliteRegionRepository(conn, lineage_guard=make_guard(conn))
    prepared = RegionStepWriter(conn, repo).prepare_ocr_text(
        "rg1",
        "新しい原文",
        source_run_id=run.run_id,
        source_step_run_id=step.step_run_id,
        expected_current_revision_id="rv1",
    )
    revisions_before = revision_count(conn, "rg1")
    lineage_before = len(lineage_rows(conn))

    # The page switches to a CUT binding AFTER the candidate was prepared.
    add_sync_switch(
        conn,
        page_id=page_id,
        old_binding_id=binding_id,
        new_binding_id="pb-p1-b2",
        relation="changed",
        seq=1,
    )

    outcome = service.commit_step_result(
        step.step_run_id,
        _ocr_step_result(prepared.revision_id),
    )

    # Existing conflict projection (not DB_FAILED) and the result is kept as a
    # candidate row; the old command face keeps its conflict semantics.
    assert outcome.status == "candidate"
    assert outcome.error_code == "INPUT_REVISION_CHANGED"
    assert LINEAGE_BINDING_CHANGED in (outcome.detail or "")
    assert step.error_code == "INPUT_REVISION_CHANGED"

    # Zero business write: no revision, no lineage row, current pointer intact.
    assert revision_count(conn, "rg1") == revisions_before
    assert len(lineage_rows(conn)) == lineage_before
    assert conn.execute(
        "SELECT current_revision_id FROM regions WHERE region_id = 'rg1'"
    ).fetchone()["current_revision_id"] == "rv1"

    # The prepared result is preserved as a candidate (C-17 §7.1 interleaving:
    # "结果留 candidate，不改已接受快照") with the conflict reason.
    candidates = conn.execute(
        "SELECT candidate_id, result_kind, reason, status, payload_json"
        " FROM step_result_candidates WHERE pipeline_run_id = ?"
        " ORDER BY created_at, candidate_id",
        (run.run_id,),
    ).fetchall()
    conflict_rows = [row for row in candidates if row["reason"] == "INPUT_REVISION_CHANGED"]
    assert conflict_rows, [dict(row) for row in candidates]
    preserved = json.loads(conflict_rows[-1]["payload_json"])
    assert "ocr_text" in preserved or "region_ids" in preserved
    assert conflict_rows[-1]["status"] != "abandoned"


def _ocr_step_result(revision_id: str):
    from domain.tasks.models import StepResult

    return StepResult(
        target_id="rg1",
        step_type="ocr",
        outputs={"ocr_text": "新しい原文"},
        revision_updates={"region": revision_id},
    )
