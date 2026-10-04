"""P2 — re-detection idempotently reuses live regions and never rolls back
a human retype (M2-REGION-RETYPE-CORE, contract M2-C1 rev 1.4 §5.4 P2).

Trigger: the detect step re-runs over a page that already carries live
regions, one of which was retyped by the user. Expected: the handler reuses
the existing regions (handlers.py idempotency branch — no rebuild, no
delete) and the retyped region_type / sfx_policy / revision history survive
untouched. Only a page with NO live region goes through the single machine
write path (origin=machine).

The fixture shape mirrors tests/providers/test_detect_handler.py (real
SQLite seam, assembly-injected ``region_creator``)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from application.editing.service import RegionEditingService
from application.tasks.service import PipelineService
from domain.regions.entities import (
    BBox,
    RegionGeometry,
    RegionOrigin,
    RegionType,
    SfxPolicy,
)
from domain.tasks.models import (
    CommandType,
    PipelineScope,
    ScopeType,
    StepRunStatus,
)
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

    def __init__(self, result: DetectionResult) -> None:
        self.result = result
        self.requests: list[DetectionRequest] = []

    def detect(self, request: DetectionRequest) -> DetectionResult:
        self.requests.append(request)
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
    from infrastructure.filesystem.managed_storage import ManagedFileStorage

    storage = ManagedFileStorage(tmp_path / "managed")
    storage.ensure_layout()
    yield {"conn": conn, "regions": SqliteRegionRepository(conn), "storage": storage}
    conn.close()


def _pipeline(workspace, *, detector):
    handlers = ProductionHandlers(
        HandlerDependencies(
            registry=ProviderRegistry(),
            regions=workspace["regions"],
            region_writer=RegionStepWriter(workspace["conn"], workspace["regions"]),
            artifacts=ArtifactStepWriter(workspace["conn"], workspace["storage"]),
            images=FakeImages(),
            geometry=_FakeGeometrySource(),
            retry_policy=RetryPolicy(max_attempts=1, backoff_seconds=0),
            detector=detector,
            region_creator=None,
        )
    )
    return PipelineService(
        build_production_pipeline(
            workspace["conn"],
            handlers=handlers.as_mapping(),
            settings={"ocr": {"script": "japanese"}},
        )
    )


def test_p2_redetect_reuses_live_regions_and_keeps_human_retype(workspace) -> None:
    """P2: a re-detect over a page with live (and human-retyped) regions
    reuses them — the retype is never rolled back, nothing is rebuilt."""
    editing = RegionEditingService(workspace["regions"])
    region = editing.create_region(
        "page-1",
        RegionGeometry(bbox=BBox(0, 0, 10, 5)),
        reading_order=1,
        origin=RegionOrigin.MACHINE,
    )
    # the human retype lands on the machine-created region
    outcome = editing.set_region_type(
        region.region_id, "sfx", current_global_sfx_policy=SfxPolicy.TRANSLATE
    )
    assert outcome.revision_no == 2
    retyped_before = (
        region.region_type,
        region.sfx_policy,
        len(workspace["regions"].list_revisions(region.region_id)),
    )

    # re-detect over the same page (a fresh run's leading detect unit)
    detector = FakeDetector(_two_candidates())
    service = _pipeline(workspace, detector=detector)
    run = service.create_run(
        CommandType.TRANSLATE_ALL,
        PipelineScope(ScopeType.CHAPTER, chapter_id="chapter-1"),
    )
    service.plan_run(run.run_id)
    executed = service.execute_run(run.run_id)

    # idempotent reuse: the SAME region survives, no duplicate is created
    live = workspace["regions"].list_regions("page-1")
    assert [r.region_id for r in live] == [region.region_id]
    detect_step = next(
        step for step in executed.step_runs if step.step_type == STEP_DETECT
    )
    assert detect_step.status is StepRunStatus.COMPLETED
    assert detect_step.output["detection"]["reused_existing_regions"] == 1
    assert detector.requests == []  # the provider is never even consulted

    # the human retype is intact: type, policy snapshot and both revisions
    assert (
        region.region_type,
        region.sfx_policy,
        len(workspace["regions"].list_revisions(region.region_id)),
    ) == retyped_before
    assert region.region_type is RegionType.SFX
    assert region.sfx_policy is SfxPolicy.TRANSLATE
    revisions = workspace["regions"].list_revisions(region.region_id)
    assert [rev.origin.value for rev in revisions] == ["machine", "user"]
