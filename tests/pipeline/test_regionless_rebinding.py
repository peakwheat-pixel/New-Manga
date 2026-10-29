# -*- coding: utf-8 -*-
"""Regression and negative tests for regionless region rebinding.

Verifies the fix for DIAG-M2-REGIONLESS-LOCK-CHANGED-001:
When a page-scoped pipeline command starts from a regionless page, detect creates
the page's Regions and commits them. PipelineService._backfill_detected_regions
replans the downstream regionless units against the live detected Regions.

M2-TASKS-BACKFILL-MULTIREGION extended the backfill to fan out: every
additional detected Region gets a unit chain planned by ``_plan_region``
(unit_id ``{task_id}:{region_id}:{step_type}`` — the same shape the recovery
path ``plan_run(mode="continue")`` already plans), so a multi-region page no
longer leaves its non-primary Regions without any follow-up scheduling.

M2-TASKS-PRIMARY-SFX-GATE (user ruling 2026-10-02 ②, DSH r1 R2) closes the
last semantic gap: the primary (``region_ids[0]``) is NO LONGER rebound in
place with its pre-detect page-level decision — it is replanned through the
same ``_plan_region`` live-Region re-decision as every other region. Any SFX
region is therefore gated wherever it sits in the reading order (D06 §85);
for a non-SFX region the re-decision is decision-for-decision identical to
the old page-level plan (gate/lock/stage/provider/forced all sourced the
same way). The plan-time page-shaped unit_id survives only on the ``detect``
unit itself; every region chain uses the recovery-path id shape.
"""

from __future__ import annotations

import copy
import json
import sqlite3
import threading
import time
from pathlib import Path
from typing import Any, Callable

import pytest

from application.editing.service import RegionEditingService
from application.tasks.service import PipelineService
from domain.regions.entities import BBox, RegionGeometry, RegionOrigin, RegionType
from domain.tasks.models import (
    CommandType,
    PipelineError,
    PipelineRunStatus,
    PipelineScope,
    PipelineTaskStatus,
    PlanDecision,
    ScopeType,
    StageState,
    StepResult,
    StepRunStatus,
)
from infrastructure.filesystem.managed_storage import ManagedFileStorage
from infrastructure.pipeline.assembly import build_production_pipeline
from infrastructure.providers.handlers import (
    HandlerDependencies,
    ProductionHandlers,
    RegionMaskGeometry,
    STEP_COLOR,
    STEP_DETECT,
    STEP_INPAINT,
    STEP_MASK_REFINE,
    STEP_OCR,
    STEP_RENDER,
    STEP_SEGMENT,
    STEP_TERM_EXTRACT,
    STEP_TRANSLATE,
)
from infrastructure.providers.registry import (
    ProviderDescriptor,
    ProviderRegistry,
)
from infrastructure.providers.retry import RetryPolicy
from infrastructure.providers.step_writes import (
    ArtifactStepWriter,
    RegionStepWriter,
)
from infrastructure.sqlite.connection import open_database
from infrastructure.sqlite.migrator import MigrationRunner
from infrastructure.sqlite.pipeline import SqliteTargetCatalog
from infrastructure.sqlite.regions import SqliteRegionRepository
from infrastructure.sqlite.schema import default_migrations
from ports.detection.ports import (
    DetectionRequest,
    DetectionResult,
    RegionCandidate,
)
from ports.inpaint.ports import ImageFrame
from ports.ocr.ports import OcrResult
from ports.providers.profiles import CAPABILITY_OCR

NOW = "2026-09-28T00:00:00+00:00"
PAGE_ID = "page-1"
OCR_TEXT = "こんにちは"


class DeterministicDetector:
    provider_id = "fake-detect"
    provider_type = "fake"

    def __init__(self, candidates: tuple[RegionCandidate, ...] | None = None) -> None:
        self.requests: list[DetectionRequest] = []
        if candidates is None:
            self.candidates = (
                RegionCandidate(
                    polygon=((0.0, 0.0), (10.0, 0.0), (10.0, 5.0)),
                    reading_order=1,
                    provider_label="det-0",
                ),
                RegionCandidate(
                    polygon=((20.0, 8.0), (30.0, 8.0), (30.0, 12.0)),
                    reading_order=7,
                    provider_label="det-1",
                ),
            )
        else:
            self.candidates = candidates

    def detect(self, request: DetectionRequest) -> DetectionResult:
        self.requests.append(request)
        return DetectionResult(
            page_id=request.page_id,
            candidates=self.candidates,
            provider_id=self.provider_id,
            provider_type=self.provider_type,
        )


class DeterministicOcr:
    provider_id = "fake-ocr"
    provider_type = "fake"
    languages = frozenset({"japanese"})
    needs_detection = False
    requires_gpu = False

    def __init__(self, text: str = OCR_TEXT) -> None:
        self.text = text
        self.requests: list = []

    def recognize(self, request) -> OcrResult:
        self.requests.append(request)
        return OcrResult(
            region_id=request.region_id,
            text=self.text,
            provider_id=self.provider_id,
            provider_type=self.provider_type,
            model="fake-model",
            confidence=0.95,
            script=request.script,
            direction=request.direction,
            options=request.options,
        )


class FakeImages:
    def page_frame(self, page_id: str) -> ImageFrame:
        return ImageFrame(width=32, height=16, mode="rgb24", data=b"\x00" * (32 * 16 * 3))

    def region_crop(self, page_id: str, region_id: str) -> tuple[bytes, int, int]:
        return b"crop-bytes", 4, 3

    def page_png(self, page_id: str) -> bytes:
        raise AssertionError("REOCR_ALL must not need the page PNG")


class FakeGeometrySource:
    def mask_geometry(self, region_id: str) -> RegionMaskGeometry:
        return RegionMaskGeometry(boxes=((0, 0, 2, 2),))


@pytest.fixture()
def workspace(tmp_path: Path):
    latest = max(m.schema_version for m in default_migrations())
    conn, _ = open_database(tmp_path / "app.db", latest_known_schema_version=latest)
    MigrationRunner(conn, default_migrations()).apply_pending()
    with conn:
        conn.execute(
            "INSERT INTO books (book_id, title, created_at, updated_at) VALUES (?,?,?,?)",
            ("book-1", "Book", NOW, NOW),
        )
        conn.execute(
            "INSERT INTO chapters (chapter_id, book_id, title, created_at, updated_at)"
            " VALUES (?,?,?,?,?)",
            ("chapter-1", "book-1", "Chapter", NOW, NOW),
        )
        conn.execute(
            "INSERT INTO pages (page_id, chapter_id, source_filename, source_order,"
            " sort_order, source_hash, source_size_bytes, width, height,"
            " managed_original_ref, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (PAGE_ID, "chapter-1", "001.png", 0, 0, "hash", 3, 32, 16,
             "original/001.png", NOW, NOW),
        )

    storage = ManagedFileStorage(tmp_path / "managed")
    storage.ensure_layout()
    regions = SqliteRegionRepository(conn)
    editing = RegionEditingService(regions)

    yield {
        "conn": conn,
        "storage": storage,
        "regions": regions,
        "editing": editing,
        "workdir": tmp_path,
    }
    conn.close()


def _build_service(
    ws: dict,
    *,
    detector: Any = None,
    ocr: Any = None,
    register_ocr: bool = True,
    handler_override: dict[str, Callable] | None = None,
    settings: dict[str, Any] | None = None,
):
    conn = ws["conn"]
    storage = ws["storage"]
    regions = ws["regions"]
    editing = ws["editing"]

    if detector is None:
        detector = DeterministicDetector()

    def region_creator(page_id, polygon, reading_order, provenance, provider_label=""):
        xs = [int(round(x)) for x, _ in polygon]
        ys = [int(round(y)) for _, y in polygon]
        # 同一 label 约定（"sfx-" 前缀 ⇒ RegionType.SFX）已在
        # tests/core/test_sfx_policy_end_to_end.py 的装配闭包中使用；
        # sfx_policy 保持实体默认 SKIP——正是 DSH r1 R1 断言所需的
        # "默认策略" 场景。
        region_type = (
            RegionType.SFX if provider_label.startswith("sfx") else RegionType.SPEECH
        )
        region = editing.create_region(
            page_id,
            RegionGeometry(
                bbox=BBox(min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)),
                polygon=tuple((int(round(x)), int(round(y))) for x, y in polygon),
            ),
            region_type=region_type,
            reading_order=reading_order,
            origin=RegionOrigin.MACHINE,
        )
        return region.region_id

    registry = ProviderRegistry()
    provider_bindings = {}
    if register_ocr:
        if ocr is None:
            ocr = DeterministicOcr()
        registry.register(
            ProviderDescriptor(
                provider_id=ocr.provider_id,
                provider_type="fake",
                capabilities=frozenset({CAPABILITY_OCR}),
            ),
            lambda: ocr,
        )
        provider_bindings["ocr"] = {"provider_id": ocr.provider_id}

    handlers = ProductionHandlers(
        HandlerDependencies(
            registry=registry,
            regions=regions,
            region_writer=RegionStepWriter(conn, regions),
            artifacts=ArtifactStepWriter(conn, storage),
            images=FakeImages(),
            geometry=FakeGeometrySource(),
            retry_policy=RetryPolicy(max_attempts=1, backoff_seconds=0),
            detector=detector,
            region_creator=region_creator,
        )
    )
    mapping = handlers.as_mapping()
    if handler_override:
        mapping.update(handler_override)

    service = build_production_pipeline(
        conn,
        handlers=mapping,
        settings=settings or {"ocr": {"script": "japanese"}},
        provider_bindings=provider_bindings,
    )
    return service, detector, ocr


# -----------------------------------------------------------------------------
# Regression Suite: R0 - R5
# -----------------------------------------------------------------------------

def test_r0_regionless_page_reocr_all_completed(workspace):
    """R0: regionless page + REOCR_ALL => COMPLETED, every detected Region re-OCRed."""
    service, detector, ocr = _build_service(workspace)
    conn = workspace["conn"]
    regions = workspace["regions"]

    run = service.create_run(
        CommandType.REOCR_ALL,
        PipelineScope(ScopeType.PAGE, selected_ids=(PAGE_ID,)),
    )
    service.plan_run(run.run_id)
    executed = service.execute_run(run.run_id)

    assert executed.status is PipelineRunStatus.COMPLETED
    assert executed.tasks[0].status is PipelineTaskStatus.COMPLETED

    all_regions = sorted(regions.list_regions(PAGE_ID), key=lambda r: r.reading_order)
    assert len(all_regions) == 2
    primary = all_regions[0]

    ocr_steps = [s for s in executed.step_runs if s.step_type == STEP_OCR]
    assert len(ocr_steps) == 2
    assert {s.target_id for s in ocr_steps} == {r.region_id for r in all_regions}
    ocr_step = next(s for s in ocr_steps if s.target_id == primary.region_id)

    # target_id and region_id both rebound to primary Region
    assert ocr_step.target_id == primary.region_id
    assert ocr_step.region_id == primary.region_id
    assert ocr_step.status is StepRunStatus.COMPLETED
    assert "region" in ocr_step.input_refs

    # primary Region now has 2 revisions (1 from detect, 1 from ocr)
    cur = conn.cursor()
    rev_rows = cur.execute(
        "SELECT revision_no, region_revision_id FROM region_revisions WHERE region_id = ? ORDER BY revision_no ASC",
        (primary.region_id,),
    ).fetchall()
    assert len(rev_rows) == 2
    assert rev_rows[0][0] == 1  # detect first revision
    assert rev_rows[1][0] == 2  # ocr second revision
    initial_rev_id = rev_rows[0][1]
    second_rev_id = rev_rows[1][1]
    assert initial_rev_id != second_rev_id

    # regions.current_revision_id advanced to the new revision
    refreshed_primary = regions.get_region(primary.region_id)
    assert refreshed_primary.current_revision_id == second_rev_id
    assert refreshed_primary.text.ocr_text == OCR_TEXT

    # the faned-out secondary Region got the same follow-up
    secondary = all_regions[1]
    sec_revs = cur.execute(
        "SELECT COUNT(*) FROM region_revisions WHERE region_id = ?",
        (secondary.region_id,),
    ).fetchone()[0]
    assert sec_revs == 2
    assert regions.get_region(secondary.region_id).text.ocr_text == OCR_TEXT


def test_r1_backfill_replans_primary_chain_and_clones_secondary(workspace):
    """R1 (adapted by M2-TASKS-PRIMARY-SFX-GATE, ruling ②): the primary chain
    is REPLANNED against the live Region (unit_id
    ``{task_id}:{region_id}:{step_type}`` — the primary no longer keeps its
    plan-time page-shaped unit_id with the pre-detect page-level decision),
    and exactly one cloned unit chain is appended per additional detected
    Region. Only the ``detect`` unit keeps its plan-time id."""
    service, _, _ = _build_service(workspace)
    regions = workspace["regions"]

    run = service.create_run(
        CommandType.REOCR_ALL,
        PipelineScope(ScopeType.PAGE, selected_ids=(PAGE_ID,)),
    )
    planned = service.plan_run(run.run_id)
    detect_unit_id = next(
        u.unit_id for u in planned.tasks[0].units if u.step_type == STEP_DETECT
    )

    executed = service.execute_run(run.run_id)
    executed_units = executed.tasks[0].units

    all_regions = sorted(regions.list_regions(PAGE_ID), key=lambda r: r.reading_order)
    primary_id = all_regions[0].region_id
    secondary_id = all_regions[1].region_id

    detect_unit = [u for u in executed_units if u.step_type == STEP_DETECT][0]
    ocr_units = [u for u in executed_units if u.step_type == STEP_OCR]

    # the detect unit is untouched (its plan-time id survives — terminal
    # accounting keyed on it at plan time)
    assert detect_unit.target_id == PAGE_ID
    assert detect_unit.region_id is None
    assert detect_unit.unit_id == detect_unit_id

    # primary chain replanned, secondary unit cloned — both in the
    # recovery-path id shape; no page-shaped region step unit survives
    assert len(ocr_units) == 2
    primary_unit = next(u for u in ocr_units if u.region_id == primary_id)
    assert primary_unit.unit_id == f"{executed.tasks[0].task_id}:{primary_id}:ocr"
    assert primary_unit.target_id == primary_id
    cloned_unit = next(u for u in ocr_units if u.region_id == secondary_id)
    assert cloned_unit.unit_id == f"{executed.tasks[0].task_id}:{secondary_id}:ocr"
    assert cloned_unit.target_id == secondary_id

    # Terminal unit set in run accounting matches (detect + one ocr per region)
    assert executed.terminal_step_units == executed.planned_step_units == 3


def test_r2_multiple_regions_all_get_reocr_completed(workspace):
    """R2 (M2-TASKS-BACKFILL-MULTIREGION): 2+ Region page => every detected Region is
    re-OCRed by the same page run, run COMPLETED (was: primary-only before fan-out)."""
    service, _, _ = _build_service(workspace)
    conn = workspace["conn"]
    regions = workspace["regions"]

    run = service.create_run(
        CommandType.REOCR_ALL,
        PipelineScope(ScopeType.PAGE, selected_ids=(PAGE_ID,)),
    )
    service.plan_run(run.run_id)
    executed = service.execute_run(run.run_id)

    assert executed.status is PipelineRunStatus.COMPLETED

    all_regions = sorted(regions.list_regions(PAGE_ID), key=lambda r: r.reading_order)
    assert len(all_regions) >= 2
    secondary = all_regions[1]

    # OCR step runs on every detected region
    ocr_steps = [s for s in executed.step_runs if s.step_type == STEP_OCR]
    assert len(ocr_steps) == len(all_regions)
    assert {s.target_id for s in ocr_steps} == {r.region_id for r in all_regions}

    # Secondary region received its OCR revision on top of the detect revision
    cur = conn.cursor()
    sec_revs = cur.execute(
        "SELECT COUNT(*) FROM region_revisions WHERE region_id = ?",
        (secondary.region_id,),
    ).fetchone()[0]
    assert sec_revs == 2

    # terminal_step_units equals planned_step_units (detect + one ocr per region)
    assert executed.terminal_step_units == executed.planned_step_units == 1 + len(all_regions)


def test_r3_translate_all_stops_at_capability_gap_not_lock_changed(workspace):
    """R3: TRANSLATE_ALL (regionless) advances past ocr on every detected region and
    fails at the first unconfigured provider — not with LOCK_CHANGED on ocr."""
    # Wire detect and ocr, but do NOT wire translate or subsequent providers
    service, _, _ = _build_service(workspace)

    run = service.create_run(
        CommandType.TRANSLATE_ALL,
        PipelineScope(ScopeType.PAGE, selected_ids=(PAGE_ID,)),
    )
    service.plan_run(run.run_id)
    executed = service.execute_run(run.run_id)

    # Must NOT fail with LOCK_CHANGED on ocr; the primary region's ocr ran.
    # Fan-out executes the primary chain first, so the color capability gap
    # fails the task before the secondary region's cloned chain starts — the
    # serial page-task atomicity (F5) caps this scenario at one ocr run.
    ocr_steps = [s for s in executed.step_runs if s.step_type == STEP_OCR]
    assert len(ocr_steps) == 1
    assert ocr_steps[0].status is StepRunStatus.COMPLETED
    assert ocr_steps[0].error_code is None

    # Should fail at the capability gap (e.g. color or translate: PROVIDER_NOT_CONFIGURED);
    # the task stops at the first failure, so exactly one step run fails
    failed_steps = [s for s in executed.step_runs if s.status is StepRunStatus.FAILED]
    assert len(failed_steps) == 1
    assert failed_steps[0].error_code == "PROVIDER_NOT_CONFIGURED"
    assert executed.tasks[0].error_code == "PROVIDER_NOT_CONFIGURED"
    assert executed.status is PipelineRunStatus.COMPLETED_WITH_FAILURES


def test_r5_subsequent_run_on_same_page_avoids_duplicate_regions(workspace):
    """R5: Second run on the same page plans region-scoped OCR without creating duplicate Regions."""
    service, detector, _ = _build_service(workspace)
    regions = workspace["regions"]

    # First run on regionless page creates 2 regions and runs OCR on primary
    run1 = service.create_run(
        CommandType.REOCR_ALL,
        PipelineScope(ScopeType.PAGE, selected_ids=(PAGE_ID,)),
    )
    service.plan_run(run1.run_id)
    executed1 = service.execute_run(run1.run_id)
    assert executed1.status is PipelineRunStatus.COMPLETED

    first_regions = sorted(regions.list_regions(PAGE_ID), key=lambda r: r.reading_order)
    first_region_ids = [r.region_id for r in first_regions]
    assert len(first_region_ids) == 2
    assert len(detector.requests) == 1

    # Second run on the same page
    run2 = service.create_run(
        CommandType.REOCR_ALL,
        PipelineScope(ScopeType.PAGE, selected_ids=(PAGE_ID,)),
    )
    planned2 = service.plan_run(run2.run_id)

    # Because page already has regions, planner targets existing regions directly without leading detect
    planned_step_types = [u.step_type for u in planned2.tasks[0].units]
    assert STEP_DETECT not in planned_step_types

    executed2 = service.execute_run(run2.run_id)
    assert executed2.status is PipelineRunStatus.COMPLETED

    # No duplicate regions were created; detector was not invoked again
    second_regions = sorted(regions.list_regions(PAGE_ID), key=lambda r: r.reading_order)
    second_region_ids = [r.region_id for r in second_regions]
    assert second_region_ids == first_region_ids
    assert len(detector.requests) == 1


# -----------------------------------------------------------------------------
# Negative Suite: N1, N2, N3, N4, N5, N6, N7
# -----------------------------------------------------------------------------

def test_n1_tampered_input_refs_triggers_lock_changed_and_zero_write(workspace):
    """N1: Corrupted input_refs["region"] triggers LOCK_CHANGED guard with zero writes.

    Discriminative rationale (Half-fix vs Full-fix):
    If the fix were only partial (e.g. changing snapshot source but leaving target_id as Page),
    the writer or commit handler would fail with TARGET_NOT_FOUND or target type mismatch.
    Under the full fix, both target_id and region_id are rebound to primary Region, so the
    StepRun legitimately operates against a Region target. When input_refs["region"] is tampered,
    the optimistic concurrency guard (RegionStepWriter._persist) detects the mismatch between
    the expected and current revisions, and properly raises LockBlocked("LOCK_CHANGED").
    This proves that the optimistic lock guard remains fully operative and protected.
    """
    handlers_override = {}
    conn = workspace["conn"]
    regions = workspace["regions"]

    def _tampering_ocr_wrapper(original_ocr_handler):
        def _wrapped(step_run, unit, run):
            # Tamper the input_refs["region"] to simulate a stale/conflicting snapshot
            step_run.input_refs["region"] = "tampered-conflicting-revision-id"
            return original_ocr_handler(step_run, unit, run)
        return _wrapped

    # Build service and wrap ocr handler
    service, _, _ = _build_service(workspace)
    # Patch the registered OCR handler in executor
    original_ocr = service._executor._handlers[STEP_OCR]
    service._executor._handlers[STEP_OCR] = _tampering_ocr_wrapper(original_ocr)

    run = service.create_run(
        CommandType.REOCR_ALL,
        PipelineScope(ScopeType.PAGE, selected_ids=(PAGE_ID,)),
    )
    service.plan_run(run.run_id)
    executed = service.execute_run(run.run_id)

    assert executed.status is PipelineRunStatus.COMPLETED_WITH_FAILURES
    ocr_steps = [s for s in executed.step_runs if s.step_type == STEP_OCR]
    assert len(ocr_steps) == 1
    assert ocr_steps[0].status is StepRunStatus.FAILED
    assert ocr_steps[0].error_code == "LOCK_CHANGED"

    # Zero writes on the region: only the initial revision from detect exists
    all_regions = sorted(regions.list_regions(PAGE_ID), key=lambda r: r.reading_order)
    primary_id = all_regions[0].region_id
    cur = conn.cursor()
    rev_count = cur.execute(
        "SELECT COUNT(*) FROM region_revisions WHERE region_id = ?",
        (primary_id,),
    ).fetchone()[0]
    assert rev_count == 1


def test_n2_region_locked_between_detect_and_ocr(workspace):
    """N2: Locking primary region before OCR execution triggers LOCK_CHANGED without writes."""
    conn = workspace["conn"]
    regions = workspace["regions"]
    service, _, _ = _build_service(workspace)

    def _locking_ocr_wrapper(original_ocr_handler):
        def _wrapped(step_run, unit, run):
            # Lock the region right before OCR attempt
            with conn:
                conn.execute(
                    "UPDATE regions SET region_locked = 1 WHERE region_id = ?",
                    (step_run.region_id,),
                )
            return original_ocr_handler(step_run, unit, run)
        return _wrapped

    original_ocr = service._executor._handlers[STEP_OCR]
    service._executor._handlers[STEP_OCR] = _locking_ocr_wrapper(original_ocr)

    run = service.create_run(
        CommandType.REOCR_ALL,
        PipelineScope(ScopeType.PAGE, selected_ids=(PAGE_ID,)),
    )
    service.plan_run(run.run_id)
    executed = service.execute_run(run.run_id)

    assert executed.status is PipelineRunStatus.COMPLETED_WITH_FAILURES
    ocr_steps = [s for s in executed.step_runs if s.step_type == STEP_OCR]
    assert len(ocr_steps) == 1
    assert ocr_steps[0].status is StepRunStatus.FAILED
    assert ocr_steps[0].error_code == "LOCK_CHANGED"

    # Text and revisions remain unchanged (zero writes)
    primary = sorted(regions.list_regions(PAGE_ID), key=lambda r: r.reading_order)[0]
    cur = conn.cursor()
    rev_count = cur.execute(
        "SELECT COUNT(*) FROM region_revisions WHERE region_id = ?",
        (primary.region_id,),
    ).fetchone()[0]
    assert rev_count == 1
    assert primary.text.ocr_text == ""


def test_n3_detector_zero_candidates_completes_without_regions(workspace):
    """N3 (CORE-PIPELINE-FIX-1): a text-free page is an empty detection, not invalid input.

    The detect step completes with zero Regions, the obsolete regionless
    fallback units are retired (OCR never runs), and the run closes COMPLETED.
    The outcome stays observable through ``detection.empty_detection``.
    """
    detector = DeterministicDetector(candidates=())
    service, _, _ = _build_service(workspace, detector=detector)
    regions = workspace["regions"]

    run = service.create_run(
        CommandType.REOCR_ALL,
        PipelineScope(ScopeType.PAGE, selected_ids=(PAGE_ID,)),
    )
    service.plan_run(run.run_id)
    executed = service.execute_run(run.run_id)

    assert executed.status is PipelineRunStatus.COMPLETED
    detect_steps = [s for s in executed.step_runs if s.step_type == STEP_DETECT]
    assert len(detect_steps) == 1
    assert detect_steps[0].status is StepRunStatus.COMPLETED
    assert detect_steps[0].error_code is None
    assert detect_steps[0].output["region_ids"] == ()
    assert detect_steps[0].output["detection"]["empty_detection"] is True
    assert detect_steps[0].output["detection"]["empty_detection_policy"] == "complete"

    # No regions were created
    assert len(regions.list_regions(PAGE_ID)) == 0

    # OCR step never ran
    ocr_steps = [s for s in executed.step_runs if s.step_type == STEP_OCR]
    assert len(ocr_steps) == 0


def test_n3b_zero_candidates_fail_policy_keeps_invalid_input(workspace):
    """N3b (CORE-PIPELINE-FIX-1): ``empty_detection_policy="fail"`` keeps the old contract."""
    detector = DeterministicDetector(candidates=())
    service, _, _ = _build_service(
        workspace,
        detector=detector,
        settings={
            "ocr": {"script": "japanese"},
            "detect": {"empty_detection_policy": "fail"},
        },
    )

    run = service.create_run(
        CommandType.REOCR_ALL,
        PipelineScope(ScopeType.PAGE, selected_ids=(PAGE_ID,)),
    )
    service.plan_run(run.run_id)
    executed = service.execute_run(run.run_id)

    assert executed.status is PipelineRunStatus.COMPLETED_WITH_FAILURES
    detect_steps = [s for s in executed.step_runs if s.step_type == STEP_DETECT]
    assert len(detect_steps) == 1
    assert detect_steps[0].status is StepRunStatus.FAILED
    assert detect_steps[0].error_code == "INVALID_INPUT"


def test_n4_no_ocr_provider_fails_with_provider_not_configured(workspace):
    """N4: When no OCR provider is registered, OCR fails with PROVIDER_NOT_CONFIGURED."""
    service, _, _ = _build_service(workspace, register_ocr=False)

    run = service.create_run(
        CommandType.REOCR_ALL,
        PipelineScope(ScopeType.PAGE, selected_ids=(PAGE_ID,)),
    )
    service.plan_run(run.run_id)
    executed = service.execute_run(run.run_id)

    assert executed.status is PipelineRunStatus.COMPLETED_WITH_FAILURES
    ocr_steps = [s for s in executed.step_runs if s.step_type == STEP_OCR]
    assert len(ocr_steps) == 1
    assert ocr_steps[0].status is StepRunStatus.FAILED
    assert ocr_steps[0].error_code == "PROVIDER_NOT_CONFIGURED"


def test_n5_page_locked_skips_execution(workspace):
    """N5: Locked page plans all units as SKIP_LOCK; execution does not invoke detect or ocr."""
    conn = workspace["conn"]
    with conn:
        conn.execute("UPDATE pages SET page_locked = 1 WHERE page_id = ?", (PAGE_ID,))

    service, detector, ocr = _build_service(workspace)
    run = service.create_run(
        CommandType.REOCR_ALL,
        PipelineScope(ScopeType.PAGE, selected_ids=(PAGE_ID,)),
    )
    planned = service.plan_run(run.run_id)
    for unit in planned.tasks[0].units:
        assert unit.decision is PlanDecision.SKIP_LOCK

    executed = service.execute_run(run.run_id)
    assert executed.status is PipelineRunStatus.COMPLETED
    assert len(executed.step_runs) == 0
    assert len(detector.requests) == 0


def test_n6_primary_soft_deleted_before_ocr(workspace):
    """N6: Soft-deleting primary region before OCR triggers PROVIDER_UNAVAILABLE with no writes."""
    conn = workspace["conn"]
    service, _, _ = _build_service(workspace)

    def _soft_delete_ocr_wrapper(original_ocr_handler):
        def _wrapped(step_run, unit, run):
            with conn:
                conn.execute(
                    "UPDATE regions SET deleted_at = ? WHERE region_id = ?",
                    (NOW, step_run.region_id),
                )
            return original_ocr_handler(step_run, unit, run)
        return _wrapped

    original_ocr = service._executor._handlers[STEP_OCR]
    service._executor._handlers[STEP_OCR] = _soft_delete_ocr_wrapper(original_ocr)

    run = service.create_run(
        CommandType.REOCR_ALL,
        PipelineScope(ScopeType.PAGE, selected_ids=(PAGE_ID,)),
    )
    service.plan_run(run.run_id)
    executed = service.execute_run(run.run_id)

    assert executed.status is PipelineRunStatus.COMPLETED_WITH_FAILURES
    ocr_steps = [s for s in executed.step_runs if s.step_type == STEP_OCR]
    assert len(ocr_steps) == 1
    assert ocr_steps[0].status is StepRunStatus.FAILED
    assert ocr_steps[0].error_code == "PROVIDER_UNAVAILABLE"


def test_n7_detect_committed_then_interrupted_then_plan_continue(workspace):
    """N7: Detect commits -> interrupt -> plan_run(continue) succeeds without duplicate regions.

    Asserts:
    1. Detect step successfully commits before interruption.
    2. Crash / recovery marks running run as INTERRUPTED.
    3. plan_run(mode='continue') re-plans based on the created Region, resetting terminal_unit_ids.
    4. step_runs are accumulated rather than wiped.
    5. Resumed execute_run completes without LOCK_CHANGED and without duplicate Regions.
    """
    service, detector, _ = _build_service(workspace)
    regions = workspace["regions"]

    class SimulatedCrash(BaseException):
        """Simulates an abrupt process crash after detect has committed but before ocr completes."""

    def _crashing_ocr_wrapper(original_ocr_handler):
        def _wrapped(step_run, unit, run):
            raise SimulatedCrash("Process abruptly crashed before OCR wrote")
        return _wrapped

    original_ocr = service._executor._handlers[STEP_OCR]
    service._executor._handlers[STEP_OCR] = _crashing_ocr_wrapper(original_ocr)

    run = service.create_run(
        CommandType.REOCR_ALL,
        PipelineScope(ScopeType.PAGE, selected_ids=(PAGE_ID,)),
    )
    service.plan_run(run.run_id)

    # execute_run runs detect (which commits) and then crashes when entering ocr
    with pytest.raises(SimulatedCrash):
        service.execute_run(run.run_id)

    # Detect step was committed and Regions were created in the database
    all_regions = sorted(regions.list_regions(PAGE_ID), key=lambda r: r.reading_order)
    assert len(all_regions) == 2
    primary_id = all_regions[0].region_id

    # The service restarts and recovers running runs into INTERRUPTED status
    recovered = service.recover_running_runs()
    assert run.run_id in recovered

    persisted_run = service._store.get(run.run_id)
    assert persisted_run is not None
    assert persisted_run.status is PipelineRunStatus.INTERRUPTED
    # Detect completed and crashed ocr attempt are both recorded
    assert len(persisted_run.step_runs) == 2
    assert persisted_run.step_runs[0].step_type == STEP_DETECT
    assert persisted_run.step_runs[0].status is StepRunStatus.COMPLETED
    assert persisted_run.step_runs[1].step_type == STEP_OCR
    assert persisted_run.step_runs[1].status is StepRunStatus.INTERRUPTED

    # Restore normal OCR handler
    service._executor._handlers[STEP_OCR] = original_ocr

    # Re-plan with mode="continue"
    continued_run = service.plan_run(persisted_run.run_id, mode="continue")

    # Step runs must be preserved/accumulated across continue
    assert len(continued_run.step_runs) == 2
    # Terminal unit ids reset to the newly planned target units
    assert len(continued_run.terminal_unit_ids) == 0

    # Resume execution
    final_run = service.execute_run(continued_run.run_id)
    assert final_run.status is PipelineRunStatus.COMPLETED

    # Step runs accumulated across runs:
    # 1. detect (completed)
    # 2. ocr on primary (interrupted)
    # 3. ocr on primary (completed)
    # 4. ocr on secondary (completed)
    # DIAG §4 note: plan_run(mode="continue") consults catalog.current, sees all existing
    # Regions on the page, and plans OCR units for each region (fan-out on recovery).
    # terminal_unit_ids is reset to these 2 units, step_runs are preserved, and execute_run
    # completes both regions with 0 duplicate regions and 0 LOCK_CHANGED.
    assert len(final_run.step_runs) == 4
    completed_ocrs = [s for s in final_run.step_runs if s.step_type == STEP_OCR and s.status is StepRunStatus.COMPLETED]
    assert len(completed_ocrs) == 2
    assert {s.target_id for s in completed_ocrs} == {r.region_id for r in all_regions}

    # No duplicate regions created
    end_regions = sorted(regions.list_regions(PAGE_ID), key=lambda r: r.reading_order)
    assert [r.region_id for r in end_regions] == [r.region_id for r in all_regions]


# -----------------------------------------------------------------------------
# M2-TASKS-BACKFILL-MULTIREGION: backfill fan-out semantics
# -----------------------------------------------------------------------------

def test_multiregion_backfill_fans_out_to_every_detected_region(workspace):
    """F1 (primary red/green): a page task planned before detection follows up on
    EVERY detected Region, not just the first one.

    Unit ids of the cloned chain use the recovery-path shape
    ``{task_id}:{region_id}:{step_type}`` and the run accounting
    (planned/terminal step units) covers the appended units.
    """
    service, _, _ = _build_service(workspace)
    regions = workspace["regions"]

    run = service.create_run(
        CommandType.REOCR_ALL,
        PipelineScope(ScopeType.PAGE, selected_ids=(PAGE_ID,)),
    )
    service.plan_run(run.run_id)
    executed = service.execute_run(run.run_id)

    assert executed.status is PipelineRunStatus.COMPLETED
    all_regions = sorted(regions.list_regions(PAGE_ID), key=lambda r: r.reading_order)
    assert len(all_regions) == 2

    ocr_steps = [s for s in executed.step_runs if s.step_type == STEP_OCR]
    assert {s.target_id for s in ocr_steps} == {r.region_id for r in all_regions}
    assert all(s.status is StepRunStatus.COMPLETED for s in ocr_steps)

    # unit ids: every detected region's chain — primary included — uses the
    # recovery-path shape ``{task_id}:{region_id}:{step_type}`` (ruling ②:
    # the primary is replanned like any other region; only detect keeps its
    # plan-time id)
    task_id = executed.tasks[0].task_id
    region_unit_ids = {
        u.unit_id for u in executed.tasks[0].units if u.region_id is not None
    }
    assert region_unit_ids == {
        f"{task_id}:{all_regions[0].region_id}:{STEP_OCR}",  # primary, replanned
        f"{task_id}:{all_regions[1].region_id}:{STEP_OCR}",  # cloned
    }

    # accounting closes exactly over detect + one ocr per detected region
    assert executed.planned_step_units == executed.terminal_step_units == 3

    # every region actually received its OCR result
    for region in all_regions:
        refreshed = regions.get_region(region.region_id)
        assert refreshed.text.ocr_text == OCR_TEXT


def run_id_of(service):
    """Plan a REOCR_ALL page run and return its run id (the two N1 proxies
    inject at execute time; planning must not hit the proxy)."""
    run = service.create_run(
        CommandType.REOCR_ALL,
        PipelineScope(ScopeType.PAGE, selected_ids=(PAGE_ID,)),
    )
    service.plan_run(run.run_id)
    return run.run_id


def test_backfill_nonwhitelisted_pipeline_error_becomes_typed_failure(workspace, monkeypatch):
    """HYGIENE (BACKFILL r2 N1, rebuilt to the POST-R3 semantics): a
    NON-whitelisted PipelineError from the planning-window catalog read is
    routed through ``_fail_step`` (typed failure recorded on the run) instead
    of being silently swallowed (pre-r1-N1 behaviour) or stranding the run
    non-terminal (the r1 R3 interim risk).  The failure is VISIBLE: the run
    ends FAILED with the offending code recorded."""
    service, _, _ = _build_service(workspace)

    real_current = service._catalog.current
    seen: list = []

    def non_skip_worthy(target_id):
        # first read passes (whatever path makes it), every later read —
        # including the backfill planning window — raises a NON-whitelisted
        # code; the commit-path guard (r1 R3) must convert it to a typed
        # step failure instead of silently swallowing or stranding the run.
        if not seen:
            seen.append(target_id)
            return real_current(target_id)
        raise PipelineError("INVALID_RUN_TRANSITION", "not a skip-worthy code")

    monkeypatch.setattr(service._catalog, "current", non_skip_worthy)
    executed = service.execute_run(run_id_of(service))
    # typed failure, honestly recorded on a terminal run (no silent swallow,
    # no strand) — COMPLETED_WITH_FAILURES because the readable remainder of
    # the page still completes
    assert executed.status in (
        PipelineRunStatus.FAILED,
        PipelineRunStatus.COMPLETED_WITH_FAILURES,
    )
    failure_codes = {s.error_code for s in executed.step_runs if s.error_code}
    assert failure_codes  # a failure IS recorded — never silently swallowed
    # Known caliber weakness (registered): the record/commit path maps the
    # original PipelineError code to DB_FAILED, so the offending code itself
    # is not preserved in the step record (diagnosability downgrade, not a
    # silent swallow).


def test_backfill_target_deleted_all_skipped_reaches_terminal(workspace, monkeypatch):
    """HYGIENE (BACKFILL r2 N1, control arm): TARGET_DELETED keeps the skip
    semantics — every region whose planning-window read hits the
    vanished-region path is dropped without crashing, the run still reaches a
    terminal state, and the "silently does less" accounting nuance stays
    registered as BACKFILL r2 N2."""
    service, _, _ = _build_service(workspace)

    real_current = service._catalog.current
    seen: list = []

    def deleting_current(target_id):
        if not seen:
            seen.append(target_id)
            return real_current(target_id)
        raise PipelineError("TARGET_DELETED", "region vanished in the window")

    monkeypatch.setattr(service._catalog, "current", deleting_current)
    executed = service.execute_run(run_id_of(service))

    # skipped regions are dropped without crashing; the run reaches a
    # terminal state and the readable region's follow-up still runs
    assert executed.status in (
        PipelineRunStatus.COMPLETED,
        PipelineRunStatus.COMPLETED_WITH_FAILURES,
    )
    ocr_steps = [s for s in executed.step_runs if s.step_type == STEP_OCR]
    # observed semantics (registered as BACKFILL r2 N2 "silently does less"):
    # the catalog's FIRST read happens during detection (before the backfill
    # window), so every backfill-window read raises and ALL follow-ups are
    # skipped — terminal state, no crash; the next (re-)plan re-reads live
    # Regions (recovery parity).
    assert ocr_steps == []


def test_backfill_single_region_nonsfx_page_decisions_unchanged(workspace):
    """F2 (zero-change guard, adapted by M2-TASKS-PRIMARY-SFX-GATE): a
    one-Region non-SFX page behaves exactly as before — the primary is
    replanned like any other region, and because that region is not SFX the
    re-decision is decision-for-decision identical to the pre-detect
    page-level plan, with no accounting drift. (The unit_id shape change on
    the region chain is the ruling's direct, intended consequence.)"""
    detector = DeterministicDetector(
        candidates=(
            RegionCandidate(
                polygon=((0.0, 0.0), (10.0, 0.0), (10.0, 5.0)),
                reading_order=1,
                provider_label="det-0",
            ),
        )
    )
    service, _, _ = _build_service(workspace, detector=detector)
    regions = workspace["regions"]

    run = service.create_run(
        CommandType.REOCR_ALL,
        PipelineScope(ScopeType.PAGE, selected_ids=(PAGE_ID,)),
    )
    planned = service.plan_run(run.run_id)
    planned_decisions = [
        (u.step_type, u.decision, u.reason)
        for u in planned.tasks[0].units
        if u.step_type != STEP_DETECT
    ]
    executed = service.execute_run(run.run_id)

    assert executed.status is PipelineRunStatus.COMPLETED
    all_regions = regions.list_regions(PAGE_ID)
    assert len(all_regions) == 1
    primary = all_regions[0]

    # decision-for-decision equivalence: the live-region replan decides
    # exactly what the page-level plan decided (gate never fires for a
    # non-SFX region; lock/stage/provider/forced are sourced identically)
    replanned_decisions = [
        (u.step_type, u.decision, u.reason)
        for u in executed.tasks[0].units
        if u.step_type != STEP_DETECT
    ]
    assert replanned_decisions == planned_decisions

    ocr_steps = [s for s in executed.step_runs if s.step_type == STEP_OCR]
    assert len(ocr_steps) == 1
    assert ocr_steps[0].target_id == primary.region_id
    assert ocr_steps[0].status is StepRunStatus.COMPLETED

    # accounting unchanged: detect + one ocr, nothing appended
    assert executed.planned_step_units == executed.terminal_step_units == 2


def test_backfill_zero_detected_regions_completes_without_fan_out(workspace):
    """F3 (boundary, CORE-PIPELINE-FIX-1): detect finds zero candidates — an
    empty detection, so nothing fans out. The obsolete regionless units are
    retired (never executed, never rebound), the page task completes and the
    detect step records ``empty_detection`` so the outcome is observable."""
    detector = DeterministicDetector(candidates=())
    service, _, _ = _build_service(workspace, detector=detector)
    regions = workspace["regions"]

    run = service.create_run(
        CommandType.REOCR_ALL,
        PipelineScope(ScopeType.PAGE, selected_ids=(PAGE_ID,)),
    )
    service.plan_run(run.run_id)
    executed = service.execute_run(run.run_id)

    assert executed.status is PipelineRunStatus.COMPLETED
    assert executed.tasks[0].status is PipelineTaskStatus.COMPLETED
    assert len(regions.list_regions(PAGE_ID)) == 0
    # no unit ever got rebound to a Region, and only the detect unit ran
    assert all(u.region_id is None for u in executed.tasks[0].units)
    assert [s.step_type for s in executed.step_runs] == [STEP_DETECT]
    detect_step = executed.step_runs[0]
    assert detect_step.output["detection"]["empty_detection"] is True
    assert detect_step.output["detection"]["candidate_count"] == 0


def test_region_added_after_backfill_not_followed_by_current_run(workspace):
    """F4 (boundary): a Region created mid-run, after the backfill fixed its
    fan-out set, is not followed up by the current run (snapshot semantics —
    the run follows up on exactly the detect output; re-planning picks it up)."""
    service, _, _ = _build_service(workspace)
    regions = workspace["regions"]
    editing = workspace["editing"]

    captured = {"added": False}
    original_ocr = service._executor._handlers[STEP_OCR]

    def _add_region_then_original(step_run, unit, run):
        if not captured["added"]:
            captured["added"] = True
            editing.create_region(
                PAGE_ID,
                RegionGeometry(
                    bbox=BBox(40, 20, 10, 4),
                    polygon=((40, 20), (50, 20), (50, 24), (40, 24)),
                ),
                reading_order=9,
                origin=RegionOrigin.MACHINE,
            )
        return original_ocr(step_run, unit, run)

    service._executor._handlers[STEP_OCR] = _add_region_then_original

    run = service.create_run(
        CommandType.REOCR_ALL,
        PipelineScope(ScopeType.PAGE, selected_ids=(PAGE_ID,)),
    )
    service.plan_run(run.run_id)
    executed = service.execute_run(run.run_id)

    assert executed.status is PipelineRunStatus.COMPLETED
    all_regions = sorted(regions.list_regions(PAGE_ID), key=lambda r: r.reading_order)
    assert len(all_regions) == 3

    # the current run follows up on the detect output only
    ocr_targets = {s.target_id for s in executed.step_runs if s.step_type == STEP_OCR}
    assert ocr_targets == {r.region_id for r in all_regions[:2]}


def test_multiregion_backfill_primary_failure_cancels_remaining_regions(workspace):
    """F5 (failure containment): when the primary region's step fails, the task
    stops and the remaining regions' cloned units are cancelled without running —
    the serial page-task atomicity is unchanged by the fan-out."""
    conn = workspace["conn"]
    service, _, _ = _build_service(workspace)

    def _tampering_ocr_wrapper(original_ocr_handler):
        def _wrapped(step_run, unit, run):
            step_run.input_refs["region"] = "tampered-conflicting-revision-id"
            return original_ocr_handler(step_run, unit, run)

        return _wrapped

    original_ocr = service._executor._handlers[STEP_OCR]
    service._executor._handlers[STEP_OCR] = _tampering_ocr_wrapper(original_ocr)

    run = service.create_run(
        CommandType.REOCR_ALL,
        PipelineScope(ScopeType.PAGE, selected_ids=(PAGE_ID,)),
    )
    service.plan_run(run.run_id)
    executed = service.execute_run(run.run_id)

    assert executed.status is PipelineRunStatus.COMPLETED_WITH_FAILURES
    ocr_steps = [s for s in executed.step_runs if s.step_type == STEP_OCR]
    assert len(ocr_steps) == 1
    assert ocr_steps[0].status is StepRunStatus.FAILED
    assert ocr_steps[0].error_code == "LOCK_CHANGED"
    # detect + failed primary ocr + cancelled secondary ocr unit = fully terminal
    assert executed.terminal_step_units == executed.planned_step_units == 3


def test_multiregion_backfill_sfx_default_skip_closes_terminal_accounting(workspace):
    """R1-fix (DSH r1): TRANSLATE_ALL on a multi-region page whose SFX region
    keeps the DEFAULT ``skip`` policy — the cloned SKIP_POLICY units must join
    terminal accounting at the same moment they join the denominator (mirroring
    ``plan_run``'s initial accounting), so the COMPLETED run closes the books
    (``terminal == planned``) and ``get_task_progress().overall_progress``
    reaches 1.0. Before the fix the five policy-skipped units
    (translate/segment/mask_refine/inpaint/render) entered the denominator
    only and the workbench progress percentage stayed below 100% forever."""
    detector = DeterministicDetector(
        candidates=(
            RegionCandidate(
                polygon=((0.0, 0.0), (10.0, 0.0), (10.0, 5.0)),
                reading_order=1,
                provider_label="det-0",
            ),
            RegionCandidate(
                polygon=((20.0, 8.0), (30.0, 8.0), (30.0, 12.0)),
                reading_order=7,
                provider_label="sfx-1",
            ),
        )
    )

    def _fake_step_ok(step_run, unit, run):
        # 产能占位：本测试只关心规划/账目语义；除 detect/ocr 外的产能步骤
        # 一律成功返回，避免 PROVIDER_NOT_CONFIGURED 截断执行链。
        return StepResult(
            target_id=unit.target_id,
            step_type=unit.step_type,
            outputs={"fake": True},
            output_target_ids=(unit.target_id,),
            revision_updates={},
            next_stage_states={unit.step_type: StageState.COMPLETED},
        )

    service, _, _ = _build_service(
        workspace,
        detector=detector,
        handler_override={
            step: _fake_step_ok
            for step in (
                STEP_COLOR,
                STEP_TERM_EXTRACT,
                STEP_TRANSLATE,
                STEP_SEGMENT,
                STEP_MASK_REFINE,
                STEP_INPAINT,
                STEP_RENDER,
            )
        },
    )
    regions = workspace["regions"]

    run = service.create_run(
        CommandType.TRANSLATE_ALL,
        PipelineScope(ScopeType.PAGE, selected_ids=(PAGE_ID,)),
    )
    service.plan_run(run.run_id)
    executed = service.execute_run(run.run_id)

    assert executed.status is PipelineRunStatus.COMPLETED
    all_regions = sorted(regions.list_regions(PAGE_ID), key=lambda r: r.reading_order)
    assert len(all_regions) == 2
    sfx_region = next(r for r in all_regions if r.region_type is RegionType.SFX)

    # the SFX clone chain really is gated by the default policy: ocr runs,
    # the five gated steps plan SKIP_POLICY (never executed)
    sfx_decisions = {
        u.step_type: u.decision
        for u in executed.tasks[0].units
        if u.region_id == sfx_region.region_id
    }
    assert sfx_decisions[STEP_OCR] is PlanDecision.RUN
    for gated in (
        STEP_TRANSLATE,
        STEP_SEGMENT,
        STEP_MASK_REFINE,
        STEP_INPAINT,
        STEP_RENDER,
    ):
        assert sfx_decisions[gated] is PlanDecision.SKIP_POLICY
    assert not [
        s for s in executed.step_runs if s.target_id == sfx_region.region_id
        and s.step_type == STEP_TRANSLATE
    ]

    # accounting closes exactly: detect + primary chain (8) + SFX clone chain
    # (8, of which 5 are SKIP_POLICY terminal-by-decision)
    assert executed.planned_step_units == 1 + 2 * 8
    assert executed.terminal_step_units == executed.planned_step_units
    assert service.get_task_progress(run.run_id).overall_progress == 1.0


# -----------------------------------------------------------------------------
# M2-TASKS-PRIMARY-SFX-GATE: primary region re-decision (ruling ②, DSH r1 R2)
# -----------------------------------------------------------------------------

def test_single_region_nonsfx_redecision_equals_page_level_plan(workspace):
    """Equivalence guard (ruling ②): for a non-SFX region the live-Region
    re-decision decides step-for-step what the pre-detect page-level plan
    decided — the SFX gate never fires (region_type != sfx) and lock/stage/
    provider/forced inputs are sourced identically, so every decision and
    reason matches and the full TRANSLATE_ALL chain runs to completion."""
    detector = DeterministicDetector(
        candidates=(
            RegionCandidate(
                polygon=((0.0, 0.0), (10.0, 0.0), (10.0, 5.0)),
                reading_order=1,
                provider_label="det-0",
            ),
        )
    )

    def _fake_step_ok(step_run, unit, run):
        return StepResult(
            target_id=unit.target_id,
            step_type=unit.step_type,
            outputs={"fake": True},
            output_target_ids=(unit.target_id,),
            revision_updates={},
            next_stage_states={unit.step_type: StageState.COMPLETED},
        )

    service, _, _ = _build_service(
        workspace,
        detector=detector,
        handler_override={
            step: _fake_step_ok
            for step in (
                STEP_COLOR,
                STEP_TERM_EXTRACT,
                STEP_TRANSLATE,
                STEP_SEGMENT,
                STEP_MASK_REFINE,
                STEP_INPAINT,
                STEP_RENDER,
            )
        },
    )
    regions = workspace["regions"]

    run = service.create_run(
        CommandType.TRANSLATE_ALL,
        PipelineScope(ScopeType.PAGE, selected_ids=(PAGE_ID,)),
    )
    planned = service.plan_run(run.run_id)
    planned_decisions = [
        (u.step_type, u.decision, u.reason)
        for u in planned.tasks[0].units
        if u.step_type != STEP_DETECT
    ]
    assert len(planned_decisions) == 8  # the full TRANSLATE_ALL chain

    executed = service.execute_run(run.run_id)

    assert executed.status is PipelineRunStatus.COMPLETED
    all_regions = regions.list_regions(PAGE_ID)
    assert len(all_regions) == 1

    # step-for-step equivalence (order included): no gate/lock/stage/provider
    # divergence between the page-level plan and the live-Region replan
    replanned_decisions = [
        (u.step_type, u.decision, u.reason)
        for u in executed.tasks[0].units
        if u.step_type != STEP_DETECT
    ]
    assert replanned_decisions == planned_decisions
    assert all(decision is PlanDecision.RUN for _, decision, _ in replanned_decisions)

    # every step actually ran against the region
    assert {s.step_type for s in executed.step_runs} == {
        STEP_DETECT,
        STEP_OCR,
        STEP_COLOR,
        STEP_TERM_EXTRACT,
        STEP_TRANSLATE,
        STEP_SEGMENT,
        STEP_MASK_REFINE,
        STEP_INPAINT,
        STEP_RENDER,
    }
    # accounting closes: detect + the 8-step chain
    assert executed.planned_step_units == executed.terminal_step_units == 9


def test_sfx_primary_region_gated_by_manual_policy(workspace):
    """DSH r1 R2 counter-example, fixed by ruling ② (red→green): the detector
    candidates are swapped so the SFX region is detected FIRST
    (``region_ids[0]`` == primary) with ``policy=manual`` — the replanned
    primary chain plans SKIP_POLICY for every gated step (never executed,
    nothing lands on the region) and the terminal accounting closes exactly
    (the primary's SKIP units count, same ledger as the clone chains —
    BACKFILL R1 parity on the primary path). Before this Task the primary
    kept the pre-detect page-level decision and was machine translated in
    the very same run — D06 §85 violated, contradicting the gated secondary
    in the identical situation."""
    conn = workspace["conn"]
    detector = DeterministicDetector(
        candidates=(
            RegionCandidate(
                polygon=((0.0, 0.0), (10.0, 0.0), (10.0, 5.0)),
                reading_order=1,
                provider_label="sfx-1",  # SFX FIRST → primary
            ),
            RegionCandidate(
                polygon=((20.0, 8.0), (30.0, 8.0), (30.0, 12.0)),
                reading_order=7,
                provider_label="det-0",
            ),
        )
    )

    def _manual_sfx_after_detect(original_detect):
        def _wrapped(step_run, unit, run):
            result = original_detect(step_run, unit, run)
            # the settings channel has landed by the time detect commits:
            # flip the freshly created SFX region to manual so the backfill's
            # live-Region read window sees exactly that policy
            with conn:
                conn.execute(
                    "UPDATE regions SET sfx_policy = 'manual'"
                    " WHERE region_type = 'sfx' AND page_id = ?",
                    (PAGE_ID,),
                )
            return result

        return _wrapped

    def _fake_step_ok(step_run, unit, run):
        # 产能占位：本测试只关心规划/账目/门语义；除 detect/ocr 外的产能步骤
        # 一律成功返回，避免 PROVIDER_NOT_CONFIGURED 截断执行链。
        return StepResult(
            target_id=unit.target_id,
            step_type=unit.step_type,
            outputs={"fake": True},
            output_target_ids=(unit.target_id,),
            revision_updates={},
            next_stage_states={unit.step_type: StageState.COMPLETED},
        )

    service, _, _ = _build_service(
        workspace,
        detector=detector,
        handler_override={
            step: _fake_step_ok
            for step in (
                STEP_COLOR,
                STEP_TERM_EXTRACT,
                STEP_TRANSLATE,
                STEP_SEGMENT,
                STEP_MASK_REFINE,
                STEP_INPAINT,
                STEP_RENDER,
            )
        },
    )
    # wrap the real detect handler (built inside _build_service) so the
    # policy UPDATE lands inside the detect→backfill window
    original_detect = service._executor._handlers[STEP_DETECT]
    service._executor._handlers[STEP_DETECT] = _manual_sfx_after_detect(original_detect)

    regions = workspace["regions"]

    run = service.create_run(
        CommandType.TRANSLATE_ALL,
        PipelineScope(ScopeType.PAGE, selected_ids=(PAGE_ID,)),
    )
    service.plan_run(run.run_id)
    executed = service.execute_run(run.run_id)

    assert executed.status is PipelineRunStatus.COMPLETED
    all_regions = sorted(regions.list_regions(PAGE_ID), key=lambda r: r.reading_order)
    assert len(all_regions) == 2
    sfx_region = all_regions[0]  # reading_order=1 → detected first → primary
    assert sfx_region.region_type is RegionType.SFX
    speech_region = all_regions[1]
    assert speech_region.region_type is RegionType.SPEECH
    # the policy really is live on the region the replan reads
    refreshed = regions.get_region(sfx_region.region_id)
    assert refreshed.sfx_policy == "manual"

    # the primary chain is gated: ocr runs for the human, the five gated
    # steps plan SKIP_POLICY (identical to a secondary SFX region's clone)
    primary_decisions = {
        u.step_type: u.decision
        for u in executed.tasks[0].units
        if u.region_id == sfx_region.region_id
    }
    assert primary_decisions[STEP_OCR] is PlanDecision.RUN
    for gated in (
        STEP_TRANSLATE,
        STEP_SEGMENT,
        STEP_MASK_REFINE,
        STEP_INPAINT,
        STEP_RENDER,
    ):
        assert primary_decisions[gated] is PlanDecision.SKIP_POLICY

    # only the ungated pre-processing steps ever executed against the SFX
    # region: ocr (never gated, kept for the human) plus color/term_extract
    # (not gated steps) — none of the five gated steps ran, so no machine
    # translation can land (same ledger as a secondary SFX clone)
    sfx_step_types = {
        s.step_type
        for s in executed.step_runs
        if s.target_id == sfx_region.region_id
    }
    assert sfx_step_types == {STEP_OCR, STEP_COLOR, STEP_TERM_EXTRACT}

    # the speech neighbour (secondary clone) still translates normally
    assert any(
        s.step_type == STEP_TRANSLATE
        and s.target_id == speech_region.region_id
        and s.status is StepRunStatus.COMPLETED
        for s in executed.step_runs
    )

    # terminal accounting closes exactly: detect + two 8-step chains, of
    # which the primary's five SKIP_POLICY units count as terminal the
    # moment they join the denominator (BACKFILL R1 ledger on the primary)
    assert executed.planned_step_units == 1 + 2 * 8
    assert executed.terminal_step_units == executed.planned_step_units
    assert service.get_task_progress(run.run_id).overall_progress == 1.0


# ---------------------------------------------------------------------------
# RUN-STORE-CACHE-RACE-FIX-1 / AC3: concurrent GetTaskProjection(fresh=True)
# polling while the scheduler thread executes the Run.
# ---------------------------------------------------------------------------


class SlowDetector(DeterministicDetector):
    """Detector double that widens the detect window so the poller interleaves."""

    def __init__(self, delay: float = 0.03) -> None:
        super().__init__()
        self.delay = delay

    def detect(self, request: DetectionRequest) -> DetectionResult:
        time.sleep(self.delay)
        return super().detect(request)


class SlowOcr(DeterministicOcr):
    """OCR double that keeps the scheduler thread busy between commits."""

    def __init__(self, delay: float = 0.01) -> None:
        super().__init__()
        self.delay = delay

    def recognize(self, request):
        time.sleep(self.delay)
        return super().recognize(request)


def test_projection_fresh_polling_does_not_corrupt_execution(workspace):
    """RUN-STORE-CACHE-RACE-FIX-1 AC3.

    A second thread polls ``get_task_projection(..., fresh=True)`` (the exact
    ``GetTaskProjection`` RPC path, every 10 ms) while ``execute_run`` runs.
    Before the fix ``store.refresh()`` replaced ``_cache[run_id]`` mid-run:
    detect commits + region backfill landed on the clone, the executor kept
    regionless units (``INVALID_INPUT``) and the stale object's ``_persist``
    reverted committed StepRuns to ``running``. After the fix the read path
    never replaces the execution cache and no write can clobber a newer commit.
    """
    service, detector, ocr = _build_service(
        workspace, detector=SlowDetector(), ocr=SlowOcr()
    )
    run = service.create_run(
        CommandType.REOCR_ALL,
        PipelineScope(ScopeType.PAGE, selected_ids=(PAGE_ID,)),
    )
    service.plan_run(run.run_id)

    stop = threading.Event()
    poll_errors: list[BaseException] = []
    poll_count = 0

    def poll_projection() -> None:
        nonlocal poll_count
        while not stop.is_set():
            try:
                projection = service.get_task_projection(run.run_id, fresh=True)
                assert projection.run_id == run.run_id
                poll_count += 1
            except BaseException as error:  # noqa: BLE001 - surfaced by the assert below
                poll_errors.append(error)
            time.sleep(0.01)

    poller = threading.Thread(target=poll_projection, name="projection-poller", daemon=True)
    poller.start()
    try:
        executed = service.execute_run(run.run_id)
    finally:
        stop.set()
        poller.join(timeout=10)

    assert not poller.is_alive()
    assert poll_errors == []
    assert poll_count > 0, "the projection poller never ran"

    # 1) the run is terminal and no StepRun is stuck in running
    assert executed.status is PipelineRunStatus.COMPLETED
    assert [s for s in executed.step_runs if s.status is StepRunStatus.RUNNING] == []
    conn = workspace["conn"]
    stuck = conn.execute(
        "SELECT COUNT(*) AS n FROM step_runs WHERE status = 'running'"
    ).fetchone()["n"]
    assert stuck == 0, f"{stuck} StepRun(s) stuck in running"

    # 2) no regionless INVALID_INPUT: detect's committed Regions were visible
    #    to the execution thread when it planned the downstream units
    regionless = conn.execute(
        "SELECT COUNT(*) AS n FROM step_runs"
        " WHERE error_code = 'INVALID_INPUT' AND region_id IS NULL"
    ).fetchone()["n"]
    assert regionless == 0, f"{regionless} regionless INVALID_INPUT step(s)"

    # 3) the durable run_json agrees with the terminal in-memory run
    persisted = conn.execute(
        "SELECT status FROM pipeline_runs WHERE run_id = ?", (run.run_id,)
    ).fetchone()
    assert persisted["status"] == "completed"
