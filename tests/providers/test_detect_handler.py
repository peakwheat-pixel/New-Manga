"""TASK-049 AC ①②③: the ``detect`` step over the real pipeline seam.

Page-level plans grow a leading ``detect`` unit; the handler fails closed
with ``PROVIDER_NOT_CONFIGURED`` when no detector is wired at assembly; and
detection candidates become real Regions through the *application-layer*
region writer (assembly-injected ``region_creator`` = production
``RegionEditingService.create_region`` — the handler never writes Regions
itself).  Every test here drives ``create_run → plan_run → execute_run`` over
the real SQLite pipeline seam.
"""

from __future__ import annotations

import json
import sqlite3
import time

import pytest
from application.tasks.service import PipelineService
from domain.tasks.models import (
    CommandType,
    PipelineRunStatus,
    PipelineScope,
    ScopeType,
    StepRunStatus,
)
from infrastructure.filesystem.managed_storage import ManagedFileStorage
from infrastructure.pipeline.assembly import build_production_pipeline
from infrastructure.providers.handlers import (
    HandlerDependencies,
    ProductionHandlers,
    STEP_DETECT,
)
from infrastructure.providers.registry import ProviderRegistry
from infrastructure.providers.retry import RetryPolicy
from infrastructure.providers.step_writes import (
    ArtifactStepWriter,
    RegionStepWriter,
)
from infrastructure.sqlite.connection import open_database
from infrastructure.sqlite.migrator import MigrationRunner
from infrastructure.sqlite.regions import SqliteRegionRepository
from infrastructure.sqlite.schema import default_migrations
from ports.detection.ports import (
    DetectionRequest,
    DetectionResult,
    RegionCandidate,
)
from ports.inpaint.ports import ImageFrame

NOW = "2026-01-01T00:00:00+00:00"


class FakeDetector:
    provider_id = "fake-detect"
    provider_type = "fake"

    def __init__(self, result: DetectionResult | Exception) -> None:
        self.result = result
        self.requests: list[DetectionRequest] = []

    def detect(self, request: DetectionRequest) -> DetectionResult:
        self.requests.append(request)
        if isinstance(self.result, Exception):
            raise self.result
        return self.result


class FakeImages:
    def page_frame(self, page_id: str) -> ImageFrame:
        return ImageFrame(
            width=32, height=16, mode="rgb24", data=b"\x00" * (32 * 16 * 3)
        )

    def region_crop(self, page_id: str, region_id: str) -> tuple[bytes, int, int]:
        raise AssertionError("detect must not need a region crop")

    def page_png(self, page_id: str) -> bytes:
        raise AssertionError("detect reads the frame, not the page png")


class _FakeGeometrySource:
    def polygon(self, region_id: str) -> tuple[tuple[int, int], ...]:
        return ((1, 1), (2, 2), (3, 3))

    def boxes(self, region_id: str) -> tuple:
        return ()


def _detection(*candidates: RegionCandidate) -> DetectionResult:
    return DetectionResult(
        page_id="page-1",
        candidates=tuple(candidates),
        provider_id="fake-detect",
        provider_type="fake",
    )


@pytest.fixture()
def workspace(tmp_path):
    conn, _ = open_database(
        tmp_path / "library.db",
        latest_known_schema_version=max(
            migration.schema_version for migration in default_migrations()
        ),
    )
    MigrationRunner(conn, default_migrations()).apply_pending()
    conn.execute(
        "INSERT INTO books (book_id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
        ("book-1", "Book", NOW, NOW),
    )
    conn.execute(
        "INSERT INTO chapters (chapter_id, book_id, title, created_at, updated_at)"
        " VALUES (?, ?, ?, ?, ?)",
        ("chapter-1", "book-1", "Chapter", NOW, NOW),
    )
    conn.execute(
        "INSERT INTO pages (page_id, chapter_id, source_filename, source_order,"
        " sort_order, source_hash, source_size_bytes, width, height,"
        " managed_original_ref, created_at, updated_at)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            "page-1", "chapter-1", "001.png", 0, 0, "hash", 3, 32, 16,
            "original/001.png", NOW, NOW,
        ),
    )
    conn.commit()
    storage = ManagedFileStorage(tmp_path / "managed")
    storage.ensure_layout()
    yield {"conn": conn, "regions": SqliteRegionRepository(conn), "storage": storage}
    conn.close()


def _handlers(
    workspace, *, detector=None, region_creator=None
) -> ProductionHandlers:
    return ProductionHandlers(
        HandlerDependencies(
            registry=ProviderRegistry(),
            regions=workspace["regions"],
            region_writer=RegionStepWriter(workspace["conn"], workspace["regions"]),
            artifacts=ArtifactStepWriter(workspace["conn"], workspace["storage"]),
            images=FakeImages(),
            geometry=_FakeGeometrySource(),
            retry_policy=RetryPolicy(max_attempts=1, backoff_seconds=0),
            detector=detector,
            region_creator=region_creator,
        )
    )


def _pipeline(workspace, *, detector=None, region_creator=None) -> PipelineService:
    return build_production_pipeline(
        workspace["conn"],
        handlers=_handlers(
            workspace, detector=detector, region_creator=region_creator
        ).as_mapping(),
        settings={"ocr": {"script": "japanese"}},
    )


def _two_candidates() -> DetectionResult:
    return _detection(
        RegionCandidate(
            polygon=((0.0, 0.0), (10.0, 0.0), (10.0, 5.0)),
            provider_label="unmapped-0",
        ),
        RegionCandidate(
            polygon=((20.0, 8.0), (30.0, 8.0), (30.0, 12.0)),
            reading_order=7,
            provider_label="unmapped-1",
        ),
    )


def test_page_level_plan_grows_a_leading_detect_unit(workspace):
    """AC ① discriminating: pre-TASK-049 the first page-level unit is
    ``ocr``; the fix plans ``detect`` before it."""
    service = _pipeline(workspace)
    run = service.create_run(
        CommandType.TRANSLATE_ALL,
        PipelineScope(ScopeType.CHAPTER, chapter_id="chapter-1"),
    )
    service.plan_run(run.run_id)
    units = run.tasks[0].units
    assert units[0].step_type == STEP_DETECT
    assert units[0].region_id is None
    assert [unit.step_type for unit in units[1:3]] == ["ocr", "color"]


def test_detect_fails_typed_without_a_detector(workspace):
    """AC ①③: no detector wired → the run fails *at the detect step* with
    PROVIDER_NOT_CONFIGURED; no step ever reports the pre-fix
    INVALID_INPUT "requires a Region target"."""
    service = _pipeline(workspace)
    run = service.create_run(
        CommandType.TRANSLATE_ALL,
        PipelineScope(ScopeType.CHAPTER, chapter_id="chapter-1"),
    )
    service.plan_run(run.run_id)
    executed = service.execute_run(run.run_id)

    assert executed.status is PipelineRunStatus.COMPLETED_WITH_FAILURES
    detect_step = executed.step_runs[0]
    assert detect_step.step_type == STEP_DETECT
    assert detect_step.status is StepRunStatus.FAILED
    assert detect_step.error_code == "PROVIDER_NOT_CONFIGURED"
    for step in executed.step_runs[1:]:
        assert step.error_code != "INVALID_INPUT"


def test_detect_lands_candidates_as_regions_and_ocr_advances(workspace):
    """AC ②③: with a detector + the application-layer creator wired, the
    candidates become real Regions (first revision, machine origin, stable
    reading order) and ``ocr`` now runs *against a Region* — failing at the
    next capability gap (no OCR provider) instead of the missing input."""
    conn = workspace["conn"]
    creator_pages: list[str] = []
    creator_orders: list[int] = []

    def creator(page_id, polygon, reading_order, provenance):
        creator_pages.append(page_id)
        creator_orders.append(reading_order)
        xs = [int(round(x)) for x, _ in polygon]
        ys = [int(round(y)) for _, y in polygon]
        from domain.regions.entities import BBox, RegionGeometry

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

    from application.editing.service import RegionEditingService
    from domain.regions.entities import RegionOrigin

    editing = RegionEditingService(workspace["regions"])
    detector = FakeDetector(_two_candidates())
    service = _pipeline(workspace, detector=detector, region_creator=creator)
    run = service.create_run(
        CommandType.TRANSLATE_ALL,
        PipelineScope(ScopeType.CHAPTER, chapter_id="chapter-1"),
    )
    service.plan_run(run.run_id)
    executed = service.execute_run(run.run_id)

    # AC ②: two Regions landed through create_region — first revisions in
    # one atomic commit, machine origin, candidate reading order honoured
    regions = sorted(
        workspace["regions"].list_regions("page-1"),
        key=lambda region: region.reading_order,
    )
    assert [region.region_id for region in regions] == list(
        executed.step_runs[0].output["region_ids"]
    )
    assert len(regions) == 2
    assert creator_pages == ["page-1", "page-1"]
    assert creator_orders == [1, 7]
    for region in regions:
        assert region.current_revision_id, "first revision pointer must be set"
    origins = [
        row[0]
        for row in conn.execute(
            "SELECT origin FROM region_revisions WHERE region_id IN"
            " (SELECT region_id FROM regions WHERE page_id = 'page-1')"
        ).fetchall()
    ]
    assert origins and set(origins) == {"machine"}

    # AC ③: the run got past the input face — detect committed, ocr ran and
    # failed at the *OCR provider* gap (never at a missing Region)
    detect_step = executed.step_runs[0]
    assert detect_step.status is StepRunStatus.COMPLETED
    assert len(detect_step.output["region_ids"]) == 2
    assert detect_step.output["detection"]["provider_id"] == "fake-detect"
    ocr_step = executed.step_runs[1]
    assert ocr_step.step_type == "ocr"
    assert ocr_step.status is StepRunStatus.FAILED
    assert ocr_step.error_code == "PROVIDER_NOT_CONFIGURED"
    assert executed.status is PipelineRunStatus.COMPLETED_WITH_FAILURES
    assert len(detector.requests) == 1


def test_detect_reuses_existing_live_regions(workspace):
    """AC ② idempotency: when Regions appear on the page between planning
    and execution (the only way a page-level ``detect`` unit coexists with
    live Regions — an earlier expansion would have made the task
    region-level), the handler reuses them and never piles up duplicates."""
    from application.editing.service import RegionEditingService
    from domain.regions.entities import BBox, RegionGeometry

    editing = RegionEditingService(workspace["regions"])
    detector = FakeDetector(_two_candidates())
    service = _pipeline(
        workspace, detector=detector, region_creator=lambda *args: "should-not-run"
    )
    run = service.create_run(
        CommandType.TRANSLATE_ALL,
        PipelineScope(ScopeType.CHAPTER, chapter_id="chapter-1"),
    )
    service.plan_run(run.run_id)
    assert run.tasks[0].units[0].step_type == STEP_DETECT

    # the race: a Region lands after planning (e.g. the user drew it while
    # the run was queued)
    editing.create_region(
        "page-1", RegionGeometry(bbox=BBox(0, 0, 4, 4)), reading_order=1
    )

    executed = service.execute_run(run.run_id)

    assert len(workspace["regions"].list_regions("page-1")) == 1
    assert detector.requests == []
    detect_step = executed.step_runs[0]
    assert detect_step.status is StepRunStatus.COMPLETED
    assert detect_step.output["region_ids"] == (
        workspace["regions"].list_regions("page-1")[0].region_id,
    )
    assert detect_step.output["detection"]["reused_existing_regions"] == 1


def test_detect_fails_typed_when_no_candidates(workspace):
    """AC ①: zero candidates → INVALID_INPUT at the detect step, so the
    task's remaining units are cancelled (ocr never runs without a Region)."""
    detector = FakeDetector(_detection())
    service = _pipeline(
        workspace, detector=detector, region_creator=lambda *args: "x"
    )
    run = service.create_run(
        CommandType.TRANSLATE_ALL,
        PipelineScope(ScopeType.CHAPTER, chapter_id="chapter-1"),
    )
    service.plan_run(run.run_id)
    executed = service.execute_run(run.run_id)

    detect_step = executed.step_runs[0]
    assert detect_step.status is StepRunStatus.FAILED
    assert detect_step.error_code == "INVALID_INPUT"
    assert executed.status is PipelineRunStatus.COMPLETED_WITH_FAILURES
