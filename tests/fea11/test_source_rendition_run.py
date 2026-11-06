"""FEA-11-RENDITION-1 run-level evidence (AC-R1/R2/R4/R7).

The REAL production pipeline (``build_production_pipeline``) is wired exactly
like ``core_assembly`` wires it: the SAME ``_ManagedPageImageSource`` (real
rendition reader over a real zip + real grant), the SAME ``read_gate``
predicate feeding both the commit guard and the target catalog, the SAME
``run_guard_value``/``commit_guard`` reader pair, and a RECORDING detector —
recording, not stubbing: the pixels it receives are the production class's own
frame bytes, which is what makes the AC-R2 discriminator real.

The real ``run_source_guard`` logic (binding → gate → live grant → lease) is
reproduced here because it is an assembly-local closure; the behaviour under
test is the pipeline's, not a fake. The production wiring itself is asserted in
``test_source_rendition_gates.py`` against ``assemble_core_services``.
"""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
import io

import pytest

from application.editing.service import RegionEditingService
from application.sources.lineage import LineageIsolationGuard
from application.tasks.store import snapshot_digest
from bootstrap.core_assembly import _ManagedPageImageSource, _RegionGeometrySource
from domain.regions.entities import (
    BBox,
    Region,
    RegionGeometry,
    RegionOrigin,
    RegionType,
)
from domain.tasks.models import (
    CommandType,
    PipelineError,
    PipelineRunStatus,
    PipelineScope,
    ScopeType,
    StepRunStatus,
)
from infrastructure.pipeline.assembly import build_production_pipeline
from infrastructure.providers.handlers import (
    HandlerDependencies,
    ProductionHandlers,
    RegionMaskGeometry,
    STEP_DETECT,
)
from infrastructure.providers.registry import ProviderDescriptor, ProviderRegistry
from infrastructure.providers.retry import RetryPolicy
from infrastructure.providers.step_writes import ArtifactStepWriter, RegionStepWriter
from infrastructure.resource_channel.handle_resolver import ManagedRootTrust
from infrastructure.resource_channel.source_read_refs import SourceReadGrantRegistry
from infrastructure.sqlite.regions import SqliteRegionRepository
from infrastructure.sqlite.source_sync import SourceSyncLineageFacts
from ports.detection.ports import DetectionResult, RegionCandidate
from ports.ocr.ports import OcrResult
from ports.providers.profiles import CAPABILITY_OCR
from tests.fea11.test_source_rendition_source import (
    NEW_B,
    build_rendition_site,
    frame_image,
    png_image,
)


#: The region the recording detector reports: the blue marker block of B. It
#: only exists inside B's 12x7 rendition, so a crop of it proves the pixels.
_BLUE_BLOCK = (8.0, 2.0, 12.0, 6.0)


class RecordingDetector:
    """Records the REAL frame bytes; optionally mutates state mid-step (F3)."""

    provider_id = "recording-detect"
    provider_type = "fake"

    def __init__(self) -> None:
        self.requests = []
        self.on_detect = None

    def detect(self, request):
        self.requests.append(request)
        if self.on_detect is not None:
            self.on_detect(request)
        left, top, right, bottom = _BLUE_BLOCK
        return DetectionResult(
            page_id=request.page_id,
            candidates=(
                RegionCandidate(
                    polygon=((left, top), (right, top), (right, bottom), (left, bottom)),
                    reading_order=1,
                    provider_label="det-blue",
                ),
            ),
            provider_id=self.provider_id,
            provider_type=self.provider_type,
        )


@dataclass
class RecordingOcr:
    """Records the crops the OCR step really received."""

    provider_id: str = "recording-ocr"
    provider_type: str = "fake"
    model: str = "fake-model"
    languages: frozenset = frozenset({"japanese"})
    needs_detection: bool = False
    requires_gpu: bool = False
    requests: list = field(default_factory=list)

    def recognize(self, request) -> OcrResult:
        self.requests.append(request)
        return OcrResult(
            region_id=request.region_id,
            text="検出後OCR",
            provider_id=self.provider_id,
            provider_type=self.provider_type,
            model=self.model,
            confidence=0.9,
            script=request.script,
            direction=request.direction,
            options=request.options,
        )


@dataclass
class RunHarness:
    site: object
    service: object
    detector: RecordingDetector
    ocr: RecordingOcr
    regions: SqliteRegionRepository
    access: object

    @property
    def conn(self):
        return self.site.conn


def _replay_binding(provider_id: str) -> dict:
    """A complete replay-safe provider binding (the frozen prepared-Run schema)."""
    execution = {
        "provider_id": provider_id,
        "provider_type": "mock-local",
        "base_url": "",
        "model": "fake-model",
        "credential_ref": None,
        "timeout_seconds": 30.0,
        "extra_options": [],
        "network_profile": None,
        "target_language": "ja",
        "options": [],
        "adapter_version": "mock-local-v1",
    }
    return {
        "provider_id": provider_id,
        "execution": execution,
        "execution_digest": snapshot_digest(execution),
    }


def build_run_harness(
    site,
    *,
    detector: RecordingDetector | None = None,
    ocr: RecordingOcr | None = None,
    access=None,
) -> RunHarness:
    """The production pipeline wired like ``core_assembly`` wires it."""
    conn = site.conn
    guard = LineageIsolationGuard(SourceSyncLineageFacts(conn))
    regions = SqliteRegionRepository(conn, lineage_guard=guard)

    def page_binding_of(page_id: str) -> str | None:
        binding = site.repository.get_page_binding(page_id)
        return binding["binding_id"] if binding is not None else None

    editing = RegionEditingService(
        regions, lineage_binding=page_binding_of, lineage_guard=guard
    )

    def region_creator(page_id, polygon, reading_order, _provenance, provider_label=""):
        xs = [int(round(x)) for x, _ in polygon]
        ys = [int(round(y)) for _, y in polygon]
        region = editing.create_region(
            page_id,
            RegionGeometry(
                bbox=BBox(min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)),
                polygon=tuple((int(round(x)), int(round(y))) for x, y in polygon),
            ),
            region_type=(
                RegionType.SFX
                if str(provider_label).startswith("sfx")
                else RegionType.SPEECH
            ),
            reading_order=reading_order,
            origin=RegionOrigin.MACHINE,
        )
        return region.region_id

    detector = detector if detector is not None else RecordingDetector()
    ocr = ocr if ocr is not None else RecordingOcr()
    registry = ProviderRegistry()
    registry.register(
        ProviderDescriptor(
            provider_id=ocr.provider_id,
            provider_type="fake",
            capabilities=frozenset({CAPABILITY_OCR}),
        ),
        lambda: ocr,
    )
    source_access = site.registry if access is None else access
    images = _ManagedPageImageSource(
        site.repository,
        site.storage,
        site.regions,
        root_trust=ManagedRootTrust.capture(site.managed_root),
        source_access=source_access,
        read_gate=site.gate,
    )

    def run_guard_value(page_id: str):
        return {"binding": site.repository.get_page_binding(page_id), "drafts": []}

    @contextmanager
    def run_source_guard(page_id: str):
        """The production guard's behaviour: binding → gate → grant → lease."""
        binding = site.repository.get_page_binding(page_id)
        if binding is None:
            yield
            return
        state = site.gate(page_id)
        if state == "unavailable":
            raise PipelineError("TARGET_NOT_FOUND", "source binding is unavailable")
        if state == "pending":
            raise PipelineError(
                "TARGET_NOT_FOUND", "source binding is pending acknowledgement"
            )
        grant_id, _ = source_access.find_bound_for_source(
            binding["source_id"],
            binding["accepted_source_version"],
            binding["entry_id"],
        )
        with source_access.commit_guard(grant_id):
            yield

    handlers = ProductionHandlers(
        HandlerDependencies(
            registry=registry,
            regions=regions,
            region_writer=RegionStepWriter(conn, regions),
            artifacts=ArtifactStepWriter(conn, site.storage),
            images=images,
            geometry=_RegionGeometrySource(regions),
            retry_policy=RetryPolicy(max_attempts=1, backoff_seconds=0),
            detector=detector,
            region_creator=region_creator,
            lineage_guard=guard,
            commit_guard=run_guard_value,
        )
    )
    service = build_production_pipeline(
        conn,
        handlers=handlers.as_mapping(),
        storage=site.storage,
        settings={"ocr": {"script": "japanese"}},
        provider_bindings={"ocr": _replay_binding(ocr.provider_id)},
    )
    service._catalog.lineage_guard = guard
    service._catalog.lineage_binding = page_binding_of
    service._catalog.source_gate_reader = site.gate
    service._catalog.page_visibility = (
        lambda page_id: site.repository.get_page(page_id) is not None
    )
    service._catalog.guard_reader = run_guard_value
    service._catalog.source_commit_guard = run_source_guard
    return RunHarness(
        site=site,
        service=service,
        detector=detector,
        ocr=ocr,
        regions=regions,
        access=source_access,
    )


def _page_scope(page_id: str) -> PipelineScope:
    return PipelineScope(ScopeType.PAGE, selected_ids=(page_id,))


def _execute(harness: RunHarness, scope: PipelineScope, command=CommandType.REOCR_ALL):
    run = harness.service.create_run(command, scope)
    harness.service.plan_run(run.run_id)
    return harness.service.execute_run(run.run_id)


def _region_rows(conn) -> int:
    return conn.execute("SELECT count(*) AS n FROM regions").fetchone()["n"]


def _revision_rows(conn) -> int:
    return conn.execute("SELECT count(*) AS n FROM region_revisions").fetchone()["n"]


def _lineage_rows(conn) -> int:
    return conn.execute(
        "SELECT count(*) AS n FROM source_revision_lineage"
    ).fetchone()["n"]


# ---------------------------------------------------------------------------
# AC-R1: pure referenced targets enter the Run (page / chapter / region)
# ---------------------------------------------------------------------------


def test_pure_referenced_page_enters_page_scope_with_an_unchanged_metadata_shape(
    conn, book_chapter, tmp_path, registry
):
    site = build_rendition_site(
        conn, book_chapter, tmp_path, registry, managed_copy=False
    )
    harness = build_run_harness(site)

    run = harness.service.create_run(CommandType.REOCR_ALL, _page_scope("pr"))

    assert [target.target_id for target in run.targets] == ["pr"]
    snapshot = run.targets[0].snapshot
    # I-1: the metadata KEY SET is frozen (no binding/rendition observation
    # rides the Run snapshot — L-R9); only the value of the stale-copy key is
    # now None for a pure referenced page. ``context_pages`` is the existing
    # create_run projection, not a RENDITION-1 addition.
    assert set(snapshot.metadata) == {
        "source_filename",
        "managed_original_ref",
        "source_hash",
        "lineage_hidden_regions",
        "commit_guard",
        "context_pages",
    }
    assert snapshot.metadata["managed_original_ref"] is None
    assert snapshot.metadata["source_hash"]
    assert harness.service._catalog.current("pr").target_id == "pr"


def test_mixed_chapter_scope_expands_to_managed_and_referenced_pages(
    conn, book_chapter, tmp_path, registry
):
    site = build_rendition_site(
        conn, book_chapter, tmp_path, registry, managed_copy=False
    )
    site.add_page("pm", source_mode="managed")
    harness = build_run_harness(site)

    run = harness.service.create_run(
        CommandType.REOCR_ALL,
        PipelineScope(ScopeType.CHAPTER, chapter_id=site.chapter_id),
    )

    assert {target.target_id for target in run.targets} == {"pr", "pm"}
    # Both the referenced and the managed page keep their metadata keys.
    for target in run.targets:
        assert set(target.snapshot.metadata) == {
            "source_filename",
            "managed_original_ref",
            "source_hash",
            "lineage_hidden_regions",
            "commit_guard",
            "context_pages",
        }


def test_region_scope_admits_a_referenced_page_region(
    conn, book_chapter, tmp_path, registry
):
    site = build_rendition_site(
        conn, book_chapter, tmp_path, registry, managed_copy=False
    )
    site.regions.add_region(
        Region(
            region_id="rg-blue",
            page_id="pr",
            geometry=RegionGeometry(bbox=BBox(8, 2, 4, 4)),
            reading_order=1,
        )
    )
    harness = build_run_harness(site)

    run = harness.service.create_run(
        CommandType.OCR_REGION,
        PipelineScope(ScopeType.REGION, selected_ids=("rg-blue",)),
    )

    assert [target.target_id for target in run.targets] == ["rg-blue"]


def test_unverifiable_referenced_pages_stay_target_not_found(
    conn, book_chapter, tmp_path, registry
):
    site = build_rendition_site(
        conn, book_chapter, tmp_path, registry, managed_copy=False
    )
    harness = build_run_harness(site)
    # Sanity: the valid page enters (so the refusals below are not a blanket no).
    assert harness.service.create_run(
        CommandType.REOCR_ALL, _page_scope("pr")
    ).targets

    # (a) integrity_status != complete → V is false.
    site.conn.execute("UPDATE pages SET integrity_status = 'incomplete' WHERE page_id = 'pr'")
    site.conn.commit()
    with pytest.raises(PipelineError) as incomplete:
        harness.service.create_run(CommandType.REOCR_ALL, _page_scope("pr"))
    assert incomplete.value.code == "TARGET_NOT_FOUND"

    # (b) verified_digest != entry.content_digest → V is false.
    site.conn.execute(
        "UPDATE pages SET integrity_status = 'complete' WHERE page_id = 'pr'"
    )
    site.conn.execute(
        "UPDATE page_bindings SET verified_digest = ? WHERE page_id = 'pr'",
        ("f" * 64,),
    )
    site.conn.commit()
    with pytest.raises(PipelineError) as digest:
        harness.service.create_run(CommandType.REOCR_ALL, _page_scope("pr"))
    assert digest.value.code == "TARGET_NOT_FOUND"

    # (c) restoring both makes it readable again (the gate is the predicate).
    site.conn.execute(
        "UPDATE page_bindings SET verified_digest = ? WHERE page_id = 'pr'",
        (site.b_digest,),
    )
    site.conn.commit()
    assert harness.service.create_run(
        CommandType.REOCR_ALL, _page_scope("pr")
    ).targets


def test_region_scope_with_null_dimensions_stays_a_stable_target_not_found(
    conn, book_chapter, tmp_path, registry
):
    site = build_rendition_site(
        conn, book_chapter, tmp_path, registry, managed_copy=False
    )
    site.regions.add_region(
        Region(
            region_id="rg-blue",
            page_id="pr",
            geometry=RegionGeometry(bbox=BBox(8, 2, 4, 4)),
            reading_order=1,
        )
    )
    site.conn.execute("UPDATE pages SET width = NULL, height = NULL WHERE page_id = 'pr'")
    site.conn.commit()
    harness = build_run_harness(site)

    # Region scope: the frozen SQL predicate keeps refusing on the region id.
    with pytest.raises(PipelineError) as region_error:
        harness.service.create_run(
            CommandType.OCR_REGION,
            PipelineScope(ScopeType.REGION, selected_ids=("rg-blue",)),
        )
    assert region_error.value.code == "TARGET_NOT_FOUND"
    assert region_error.value.detail == "rg-blue"

    # Page scope: a typed refusal in the same family — never a budget/login
    # misleading code (the rendition is not even attempted).
    with pytest.raises(PipelineError) as page_error:
        harness.service.create_run(CommandType.REOCR_ALL, _page_scope("pr"))
    assert page_error.value.code == "TARGET_NOT_FOUND"
    assert "SOURCE_BUDGET_EXCEEDED" not in str(page_error.value.detail)


# ---------------------------------------------------------------------------
# AC-R2: the Run input pixels are the CURRENT binding's rendition
# ---------------------------------------------------------------------------


def test_run_detector_receives_the_binding_rendition_pixels(
    conn, book_chapter, tmp_path, registry, monkeypatch
):
    site = build_rendition_site(conn, book_chapter, tmp_path, registry)
    # Sentinel: the stale managed copy must never be opened by this Run.
    def _forbidden(*args, **kwargs):  # noqa: ANN002, ANN003
        raise AssertionError("a referenced Run must not read the managed copy")

    monkeypatch.setattr(ManagedRootTrust, "read_bytes", _forbidden)
    harness = build_run_harness(site)

    executed = _execute(harness, _page_scope("pr"))

    detect_steps = [step for step in executed.step_runs if step.step_type == STEP_DETECT]
    assert len(detect_steps) == 1
    assert detect_steps[0].status is StepRunStatus.COMPLETED, (
        detect_steps[0].error_code,
        detect_steps[0].error_detail,
    )
    assert harness.detector.requests, "detection must run on the rendition"
    request = harness.detector.requests[0]
    # (a) the frame dimensions are B's, not the 30x20 managed copy's.
    assert (request.width, request.height) == (NEW_B["width"], NEW_B["height"])
    # (b) the pixels are B's (green background + blue marker at the crop box).
    from PIL import Image

    rgba = Image.frombytes(
        "RGBA", (request.width, request.height), request.image_bytes, "raw", "BGRA"
    )
    rgb = rgba.convert("RGB")
    assert rgb.getpixel((0, 0)) == NEW_B["background"]
    assert rgb.getpixel((9, 3)) == NEW_B["block_color"]
    # (c) the OCR crop of the detected (blue) region is B's marker block.
    assert harness.ocr.requests, "the OCR step must read the rendition crop"
    crop_request = harness.ocr.requests[0]
    assert (crop_request.width, crop_request.height) == (4, 4)
    assert png_image(crop_request.image_bytes).getpixel((0, 0)) == NEW_B["block_color"]


def test_detect_regions_register_native_lineage_for_the_current_binding(
    conn, book_chapter, tmp_path, registry
):
    site = build_rendition_site(conn, book_chapter, tmp_path, registry)
    harness = build_run_harness(site)

    executed = _execute(harness, _page_scope("pr"))

    assert executed.status is PipelineRunStatus.COMPLETED, [
        (step.step_type, step.error_code, step.error_detail)
        for step in executed.step_runs
    ]
    live = [region for region in harness.regions.list_regions("pr") if not region.deleted]
    assert len(live) == 1
    rows = harness.conn.execute(
        "SELECT binding_id, provenance FROM source_revision_lineage"
        " WHERE region_id = ?",
        (live[0].region_id,),
    ).fetchall()
    assert rows, "the detect-created Region must register lineage"
    assert {row["binding_id"] for row in rows} == {"pb-pr"}
    assert {row["provenance"] for row in rows} == {"native"}


# ---------------------------------------------------------------------------
# AC-R4: typed refusals, zero writes
# ---------------------------------------------------------------------------


def test_binding_change_between_prepare_and_accept_is_run_stale_preview(
    conn, book_chapter, tmp_path, registry
):
    site = build_rendition_site(
        conn, book_chapter, tmp_path, registry, managed_copy=False
    )
    harness = build_run_harness(site)
    scope = _page_scope("pr")
    prepared = harness.service.prepare_run(CommandType.REOCR_ALL, scope)

    site.conn.execute(
        "UPDATE page_bindings SET entry_id = 'se1', verified_digest = ?"
        " WHERE page_id = 'pr'",
        (site.c_digest,),
    )
    site.conn.commit()
    site.registry.bind_imported_entry(site.grant_id, "s1", "sv1", "se1")

    with pytest.raises(PipelineError) as info:
        harness.service.accept_prepared_run(
            prepared, scope, idempotency_key="rendition-stale-1"
        )
    assert info.value.code == "RUN_STALE_PREVIEW"


def test_binding_change_between_decode_and_region_write_is_input_revision_changed(
    conn, book_chapter, tmp_path, registry
):
    """I-4 (F3): B1 pixels must never be stamped as B2 native lineage."""
    site = build_rendition_site(conn, book_chapter, tmp_path, registry)
    harness = build_run_harness(site)
    regions_before = _region_rows(conn)
    revisions_before = _revision_rows(conn)
    lineage_before = _lineage_rows(conn)

    def _switch_binding(request) -> None:
        # The frame was decoded above; the binding switches now, BEFORE the
        # handler writes any Region.
        harness.detector.on_detect = None
        site.conn.execute(
            "UPDATE page_bindings SET entry_id = 'se1', verified_digest = ?"
            " WHERE page_id = 'pr'",
            (site.c_digest,),
        )
        site.conn.commit()
        site.registry.bind_imported_entry(site.grant_id, "s1", "sv1", "se1")

    harness.detector.on_detect = _switch_binding
    executed = _execute(harness, _page_scope("pr"))

    detect_steps = [step for step in executed.step_runs if step.step_type == STEP_DETECT]
    assert len(detect_steps) == 1
    assert detect_steps[0].status is StepRunStatus.FAILED
    assert detect_steps[0].error_code == "INPUT_REVISION_CHANGED"
    # Zero business write: no Region, no revision, no lineage row.
    assert _region_rows(conn) == regions_before == 0
    assert _revision_rows(conn) == revisions_before == 0
    assert _lineage_rows(conn) == lineage_before == 0


def test_pending_gate_refuses_the_run_target_before_any_execution(
    conn, book_chapter, tmp_path, registry
):
    site = build_rendition_site(
        conn, book_chapter, tmp_path, registry, managed_copy=False
    )
    harness = build_run_harness(site)
    site.gate_state["value"] = "pending"

    with pytest.raises(PipelineError) as info:
        harness.service.create_run(CommandType.REOCR_ALL, _page_scope("pr"))

    assert info.value.code == "TARGET_NOT_FOUND"
    assert harness.detector.requests == []


# ---------------------------------------------------------------------------
# AC-R7 / L-R1: without a live Run-scoped grant the Run is typed-failed
# ---------------------------------------------------------------------------


def test_run_without_a_live_source_grant_is_typed_and_writes_nothing(
    conn, book_chapter, tmp_path, registry
):
    """L-R1 evidence: the Core side works, the grant channel does not exist."""
    site = build_rendition_site(
        conn, book_chapter, tmp_path, registry, managed_copy=False
    )
    empty = SourceReadGrantRegistry()
    harness = build_run_harness(site, access=empty)

    executed = _execute(harness, _page_scope("pr"))

    assert executed.status in {
        PipelineRunStatus.FAILED,
        PipelineRunStatus.COMPLETED_WITH_FAILURES,
    }, [(step.step_type, step.error_code) for step in executed.step_runs]
    codes = {
        step.error_code for step in executed.step_runs if step.error_code
    }
    assert codes & {"INVALID_INPUT", "PROVIDER_FAILED"}, codes
    # Typed, no crash, no partial business write.
    assert _region_rows(conn) == 0
    assert _revision_rows(conn) == 0
    assert _lineage_rows(conn) == 0
    assert harness.detector.requests == []
