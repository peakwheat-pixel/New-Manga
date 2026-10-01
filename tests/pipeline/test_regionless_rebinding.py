# -*- coding: utf-8 -*-
"""M2-P1: Regression and negative tests for regionless region rebinding.

Verifies the fix for DIAG-M2-REGIONLESS-LOCK-CHANGED-001:
When a page-scoped pipeline command starts from a regionless page, detect creates
the page's Regions and commits them. PipelineService._backfill_detected_regions
must rebind both target_id and region_id of downstream regionless units to the
first detected Region (primary) while strictly preserving PlanUnit.unit_id.
"""

from __future__ import annotations

import copy
import json
import sqlite3
from pathlib import Path
from typing import Any, Callable

import pytest

from application.editing.service import RegionEditingService
from application.tasks.service import PipelineService
from domain.regions.entities import BBox, RegionGeometry, RegionOrigin
from domain.tasks.models import (
    CommandType,
    PipelineRunStatus,
    PipelineScope,
    PipelineTaskStatus,
    PlanDecision,
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
        region = editing.create_region(
            page_id,
            RegionGeometry(
                bbox=BBox(min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)),
                polygon=tuple((int(round(x)), int(round(y))) for x, y in polygon),
            ),
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
        settings={"ocr": {"script": "japanese"}},
        provider_bindings=provider_bindings,
    )
    return service, detector, ocr


# -----------------------------------------------------------------------------
# Regression Suite: R0 - R5
# -----------------------------------------------------------------------------

def test_r0_regionless_page_reocr_all_completed(workspace):
    """R0: regionless page + REOCR_ALL => COMPLETED, target_id==region_id==primary, 2 revisions."""
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
    assert len(ocr_steps) == 1
    ocr_step = ocr_steps[0]

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


def test_r1_backfill_rebinds_target_id_and_preserves_unit_ids(workspace):
    """R1: backfill sets unit.target_id==region_id==primary, preserving all plan unit_ids."""
    service, _, _ = _build_service(workspace)
    regions = workspace["regions"]

    run = service.create_run(
        CommandType.REOCR_ALL,
        PipelineScope(ScopeType.PAGE, selected_ids=(PAGE_ID,)),
    )
    planned = service.plan_run(run.run_id)
    planned_units = planned.tasks[0].units
    planned_unit_ids = [u.unit_id for u in planned_units]

    executed = service.execute_run(run.run_id)
    executed_units = executed.tasks[0].units
    executed_unit_ids = [u.unit_id for u in executed_units]

    # Invariant: unit_ids are never mutated across backfill
    assert executed_unit_ids == planned_unit_ids

    all_regions = sorted(regions.list_regions(PAGE_ID), key=lambda r: r.reading_order)
    primary_id = all_regions[0].region_id

    detect_unit = [u for u in executed_units if u.step_type == STEP_DETECT][0]
    ocr_unit = [u for u in executed_units if u.step_type == STEP_OCR][0]

    assert detect_unit.target_id == PAGE_ID
    assert detect_unit.region_id is None

    # target_id rebound to primary region along with region_id
    assert ocr_unit.target_id == primary_id
    assert ocr_unit.region_id == primary_id

    # Terminal unit set in run accounting matches
    assert executed.terminal_step_units == executed.planned_step_units == 2


def test_r2_multiple_regions_only_primary_reocr_completed(workspace):
    """R2: 2+ Region page => only primary has OCR, non-primary NOT_STARTED, run COMPLETED."""
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
    primary = all_regions[0]
    secondary = all_regions[1]

    # OCR step runs only on primary
    ocr_steps = [s for s in executed.step_runs if s.step_type == STEP_OCR]
    assert len(ocr_steps) == 1
    assert ocr_steps[0].target_id == primary.region_id

    # Secondary region remains untouched (1 revision from detect)
    cur = conn.cursor()
    sec_revs = cur.execute(
        "SELECT COUNT(*) FROM region_revisions WHERE region_id = ?",
        (secondary.region_id,),
    ).fetchone()[0]
    assert sec_revs == 1

    # terminal_step_units equals planned_step_units (2)
    assert executed.terminal_step_units == executed.planned_step_units == 2


def test_r3_translate_all_stops_at_capability_gap_not_lock_changed(workspace):
    """R3: TRANSLATE_ALL (regionless) advances past ocr and fails at next unconfigured provider."""
    # Wire detect and ocr, but do NOT wire translate or subsequent providers
    service, _, _ = _build_service(workspace)

    run = service.create_run(
        CommandType.TRANSLATE_ALL,
        PipelineScope(ScopeType.PAGE, selected_ids=(PAGE_ID,)),
    )
    service.plan_run(run.run_id)
    executed = service.execute_run(run.run_id)

    # Must NOT fail with LOCK_CHANGED on ocr
    ocr_steps = [s for s in executed.step_runs if s.step_type == STEP_OCR]
    assert len(ocr_steps) == 1
    assert ocr_steps[0].status is StepRunStatus.COMPLETED
    assert ocr_steps[0].error_code is None

    # Should fail at the capability gap (e.g. color or translate: PROVIDER_NOT_CONFIGURED)
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


def test_n3_detector_zero_candidates_fails_with_invalid_input(workspace):
    """N3: Detector returning 0 candidates results in INVALID_INPUT; no regions created and OCR skipped."""
    detector = DeterministicDetector(candidates=())
    service, _, _ = _build_service(workspace, detector=detector)
    regions = workspace["regions"]

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

    # No regions were created
    assert len(regions.list_regions(PAGE_ID)) == 0

    # OCR step never ran
    ocr_steps = [s for s in executed.step_runs if s.step_type == STEP_OCR]
    assert len(ocr_steps) == 0


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
