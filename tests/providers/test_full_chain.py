"""TASK-033 full-chain closure: color / term_extract / render handlers.

Real SQLite + real pipeline seam + real rendering assembly + fake providers
(the established ``tests/providers`` double style). Proves that

- the complete command chain runs every planned step and persists each stage
  (AC-RFULL-001's integration half; model quality stays BLOCKED);
- the target Region is written and same-page neighbours are untouched
  (AC-RFULL-002), manual translations and Locks survive (AC-RFULL-005);
- ``RenderService`` is the **single writer** of the ``translated`` pointer:
  the render handler yields ``revision_updates={}`` and every render moves the
  current pointer exactly one revision forward — no double write, no jitter
  (TASK-033 P0 constraint);
- missing assembly (color/term_extract/render without their service) and a
  missing upstream Clean both fail closed with typed codes.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

pytest.importorskip("PySide6", reason="the render/color assembly is Qt-backed")

from PySide6.QtGui import QGuiApplication  # noqa: E402

from application.rendering.service import RenderService  # noqa: E402
from application.tasks.service import PipelineService  # noqa: E402
from application.translation.color.service import SourceStyleService  # noqa: E402
from application.translation.knowledge.term_extraction import (  # noqa: E402
    TermExtractionService,
)
from application.translation.pipeline.executor import StepExecutionError  # noqa: E402
from application.translation.inpaint.router import RoutePolicy  # noqa: E402
from domain.tasks.models import (  # noqa: E402
    CommandType,
    LockSnapshot,
    PipelineRun,
    PipelineRunStatus,
    PipelineScope,
    PlanDecision,
    PlanUnit,
    ScopeType,
    StepRun,
    StepRunStatus,
    StageState,
)
from infrastructure.filesystem.managed_storage import ManagedFileStorage  # noqa: E402
from infrastructure.pipeline.assembly import build_production_pipeline  # noqa: E402
from infrastructure.providers.handlers import (  # noqa: E402
    HandlerDependencies,
    ProductionHandlers,
    RegionMaskGeometry,
)
from infrastructure.providers.inpaint_routes import (  # noqa: E402
    EdgeBleedProvider,
    SimpleFillProvider,
)
from infrastructure.providers.registry import (  # noqa: E402
    ProviderDescriptor,
    ProviderRegistry,
)
from infrastructure.providers.retry import RetryPolicy  # noqa: E402
from infrastructure.providers.step_writes import (  # noqa: E402
    ArtifactStepWriter,
    RegionStepWriter,
)
from infrastructure.rendering.font_catalog import QtFontCatalog  # noqa: E402
from infrastructure.rendering.locator import SqlitePageArtifactLocator  # noqa: E402
from infrastructure.rendering.pixel_source_style import (  # noqa: E402
    PixelSourceStyleAnalyzer,
)
from infrastructure.rendering.qt_compositor import QtImageCompositor  # noqa: E402
from infrastructure.rendering.qt_layout import QtTextLayoutEngine  # noqa: E402
from infrastructure.sqlite.artifacts import SqliteArtifactRepository  # noqa: E402
from infrastructure.sqlite.connection import open_database  # noqa: E402
from infrastructure.sqlite.migrator import MigrationRunner  # noqa: E402
from infrastructure.sqlite.regions import SqliteRegionRepository  # noqa: E402
from infrastructure.sqlite.schema import default_migrations  # noqa: E402
from ports.inpaint.ports import (  # noqa: E402
    ROUTE_EDGE_BLEED,
    ROUTE_MANGA_LAMA,
    ROUTE_SIMPLE_FILL,
)
from ports.providers.profiles import (  # noqa: E402
    CAPABILITY_INPAINT,
    CAPABILITY_OCR,
    CAPABILITY_TRANSLATION,
)

from providers_helpers import (  # noqa: E402
    FakeOcrProvider,
    FakePageImages,
    FakeTranslationProvider,
    frame,
)

NOW = "2026-09-18T00:00:00+00:00"

FULL_CHAIN = (
    "ocr",
    "color",
    "term_extract",
    "translate",
    "segment",
    "mask_refine",
    "inpaint",
    "render",
)


def _page_png(size: int = 32) -> bytes:
    from PySide6.QtCore import QBuffer, QIODevice
    from PySide6.QtGui import QColor, QImage

    image = QImage(size, size, QImage.Format.Format_RGB32)
    image.fill(QColor(235, 235, 235))
    buffer = QBuffer()
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    assert image.save(buffer, "PNG")
    return bytes(buffer.data())


@pytest.fixture(scope="module")
def qapp():
    """One QGuiApplication for the module (Qt font/compositor adapters)."""
    return QGuiApplication.instance() or QGuiApplication([])


def _region_text(**overrides):
    text = {
        "ocr_text": "",
        "machine_translation": "",
        "edited_translation": "",
        "final_translation": "",
        "final_source": "none",
        "edited_confirmed": False,
        "manual_edited": False,
        "translation_locked": False,
    }
    text.update(overrides)
    return text


class _Geometry:
    """RegionGeometrySource double: fixed boxes per region."""

    _BOXES = {
        "region-a": ((1, 1, 6, 6),),
        "region-b": ((4, 4, 24, 24),),
        "region-c": ((10, 10, 24, 24),),
    }

    def mask_geometry(self, region_id: str) -> RegionMaskGeometry:
        return RegionMaskGeometry(boxes=self._BOXES.get(region_id, ((1, 1, 3, 3),)))


@pytest.fixture()
def workspace(tmp_path: Path, qapp):
    latest = max(migration.schema_version for migration in default_migrations())
    conn, _opened = open_database(tmp_path / "app.db", latest_known_schema_version=latest)
    MigrationRunner(conn, default_migrations()).apply_pending()

    with conn:
        conn.execute(
            "INSERT INTO books (book_id, title, created_at, updated_at)"
            " VALUES (?, ?, ?, ?)",
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
                "page-1",
                "chapter-1",
                "001.png",
                0,
                0,
                "hash",
                3,
                32,
                32,
                "original/001.png",
                NOW,
                NOW,
            ),
        )
        for region_id, box, text in (
            ("region-a", [1, 1, 5, 5], _region_text(ocr_text="A-text")),
            ("region-b", [4, 4, 20, 20], _region_text(ocr_text="B-source")),
            (
                "region-c",
                [10, 10, 14, 14],
                _region_text(
                    ocr_text="C-text",
                    machine_translation="old-machine",
                    edited_translation="人工译文",
                    final_translation="人工译文",
                    final_source="edited",
                    edited_confirmed=True,
                    manual_edited=True,
                    translation_locked=True,
                ),
            ),
        ):
            conn.execute(
                "INSERT INTO regions (region_id, page_id, region_type, geometry_json,"
                " text_json, style_json, sfx_policy, translation_locked,"
                " current_revision_id, created_at, updated_at)"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?, NULL, ?, ?)",
                (
                    region_id,
                    "page-1",
                    "speech",
                    json.dumps({"bbox": box, "polygon": []}),
                    json.dumps(text),
                    "{}",
                    "translate",
                    1 if text["translation_locked"] else 0,
                    NOW,
                    NOW,
                ),
            )
            conn.execute(
                "INSERT INTO region_revisions (region_revision_id, region_id,"
                " revision_no, snapshot_json, origin, review_state, created_at)"
                " VALUES (?, ?, 1, '{}', 'imported', 'unreviewed', ?)",
                (f"{region_id}-rev-1", region_id, NOW),
            )
            conn.execute(
                "UPDATE regions SET current_revision_id = ? WHERE region_id = ?",
                (f"{region_id}-rev-1", region_id),
            )
        conn.execute(
            "INSERT INTO pipeline_stage_states (target_type, target_id, stage,"
            " status, updated_at) VALUES ('region', 'region-b', 'ocr', 'completed', ?)",
            (NOW,),
        )

    storage = ManagedFileStorage(tmp_path / "managed")
    storage.ensure_layout()
    regions = SqliteRegionRepository(conn)

    ocr_provider = FakeOcrProvider("こんにちは")
    translate_provider = FakeTranslationProvider()
    registry = ProviderRegistry()
    registry.register(
        ProviderDescriptor(
            provider_id="fake-ocr",
            provider_type="fake",
            capabilities=frozenset({CAPABILITY_OCR}),
        ),
        lambda: ocr_provider,
    )
    registry.register(
        ProviderDescriptor(
            provider_id="fake-translate",
            provider_type="fake",
            capabilities=frozenset({CAPABILITY_TRANSLATION}),
        ),
        lambda: translate_provider,
    )
    registry.register(
        ProviderDescriptor(
            provider_id="inpaint-simple-fill",
            provider_type="local-simple-fill",
            capabilities=frozenset({CAPABILITY_INPAINT}),
        ),
        SimpleFillProvider,
    )
    registry.register(
        ProviderDescriptor(
            provider_id="inpaint-edge-bleed",
            provider_type="local-edge-bleed",
            capabilities=frozenset({CAPABILITY_INPAINT}),
        ),
        EdgeBleedProvider,
    )

    font_catalog = QtFontCatalog()
    source_styles = SourceStyleService(PixelSourceStyleAnalyzer())
    from bootstrap.app import _render_content_decoder

    render_service = RenderService(
        region_repo=regions,
        locator=SqlitePageArtifactLocator(conn),
        artifacts=SqliteArtifactRepository(conn, storage),
        storage=storage,
        layout_engine=QtTextLayoutEngine(font_catalog),
        compositor=QtImageCompositor(),
        source_styles=source_styles,
        font_catalog=font_catalog,
        content_decoder=_render_content_decoder,
    )
    handlers = ProductionHandlers(
        HandlerDependencies(
            registry=registry,
            regions=regions,
            region_writer=RegionStepWriter(conn, regions),
            artifacts=ArtifactStepWriter(conn, storage),
            images=FakePageImages(
                page=frame(32, 32, (240, 240, 240)),
                png=_page_png(32),
            ),
            geometry=_Geometry(),
            retry_policy=RetryPolicy(max_attempts=1, backoff_seconds=0),
            route_policy=RoutePolicy(
                allowed_routes=(ROUTE_SIMPLE_FILL, ROUTE_EDGE_BLEED),
                color_route=ROUTE_MANGA_LAMA,
                requirements={ROUTE_MANGA_LAMA: False},
            ),
            source_styles=source_styles,
            terms=TermExtractionService(),
            render_service=render_service,
        )
    )

    yield {
        "conn": conn,
        "regions": regions,
        "storage": storage,
        "handlers": handlers,
        "render_service": render_service,
    }
    conn.close()


def _pipeline(workspace, settings=None) -> PipelineService:
    return build_production_pipeline(
        workspace["conn"],
        handlers=workspace["handlers"].as_mapping(),
        settings=settings
        or {"translate": {"glossary": {"こんにちは": "你好"}}},
        provider_bindings={
            "ocr": {"provider_id": "fake-ocr"},
            "translate": {"provider_id": "fake-translate"},
        },
    )


def _run_full_chain(workspace, settings=None):
    service = _pipeline(workspace, settings=settings)
    run = service.create_run(
        CommandType.RETRANSLATE_REGION_FULL,
        PipelineScope(ScopeType.REGION, selected_ids=("region-b",)),
    )
    service.plan_run(run.run_id)
    return service.execute_run(run.run_id)


def _text(conn: sqlite3.Connection, region_id: str) -> dict:
    row = conn.execute(
        "SELECT text_json, current_revision_id, translation_locked FROM regions"
        " WHERE region_id = ?",
        (region_id,),
    ).fetchone()
    return {
        "text": json.loads(row["text_json"]),
        "current_revision_id": row["current_revision_id"],
        "translation_locked": row["translation_locked"],
    }


def _translated_revisions(conn: sqlite3.Connection) -> list[tuple[str, int]]:
    rows = conn.execute(
        "SELECT ar.artifact_revision_id, ar.revision_no FROM artifact_revisions ar"
        " JOIN media_artifacts a ON ar.artifact_id = a.artifact_id"
        " WHERE a.page_id = 'page-1' AND a.artifact_type = 'translated'"
        " ORDER BY ar.revision_no"
    ).fetchall()
    return [(row["artifact_revision_id"], row["revision_no"]) for row in rows]


def _current_translated(conn: sqlite3.Connection) -> str | None:
    row = conn.execute(
        "SELECT current_revision_id FROM media_artifacts"
        " WHERE page_id = 'page-1' AND artifact_type = 'translated'"
    ).fetchone()
    return row["current_revision_id"] if row else None


def _stage(conn: sqlite3.Connection, target_id: str, stage: str):
    row = conn.execute(
        "SELECT status FROM pipeline_stage_states WHERE target_type = 'region'"
        " AND target_id = ? AND stage = ?",
        (target_id, stage),
    ).fetchone()
    return StageState(row["status"]) if row else None


def test_full_translation_chain_runs_every_step(workspace) -> None:
    """AC ⑤: the 9-step contract (8 step types + save) against the real seam."""
    conn = workspace["conn"]
    executed = _run_full_chain(workspace)

    steps = list(executed.step_runs)
    assert [step.step_type for step in steps] == list(FULL_CHAIN), [
        (step.step_type, step.status, step.error_code, step.error_detail)
        for step in steps
    ]
    assert all(
        step.status is StepRunStatus.COMPLETED for step in steps
    ), [(step.step_type, step.error_code, step.error_detail) for step in steps]
    assert executed.status is PipelineRunStatus.COMPLETED

    by_type = {step.step_type: step for step in steps}
    # color: judgement-only, no AI, fallback decision recorded (AC ①)
    assert by_type["color"].output["needs_fallback"] is True
    assert by_type["color"].output["provenance"]["ai_invoked"] is False
    assert list(by_type["color"].output["provenance"]["box"]) == [4, 4, 20, 20]
    # term_extract: glossary hit recorded, nothing written to the glossary/TM (AC ②)
    candidates = by_type["term_extract"].output["term_candidates"]
    assert any(
        candidate["source"] == "glossary"
        and candidate["term"] == "こんにちは"
        and candidate["suggested_target"] == "你好"
        for candidate in candidates
    )
    assert by_type["term_extract"].output["provenance"]["ai_invoked"] is False
    # render: the translated artifact exists and the report names the region (AC ③)
    assert by_type["render"].output["render_status"] == "committed"
    assert by_type["render"].output["translated_revision_no"] == 1
    reports = [dict(report) for report in by_type["render"].output["region_reports"]]
    assert reports == [
        {
            "region_id": "region-b",
            "status": "rendered",
            "skip_reason": None,
            "final_font_size": reports[0]["final_font_size"],
            "font_substituted": reports[0]["font_substituted"],
        }
    ]
    assert by_type["render"].output["provenance"]["ai_invoked"] is False

    # every stage reached the store ("save" is the commit of each step)
    for stage in FULL_CHAIN:
        assert _stage(conn, "region-b", stage) is StageState.COMPLETED, stage

    # target region written
    text = _text(conn, "region-b")["text"]
    assert text["ocr_text"] == "こんにちは"
    assert text["final_translation"] == "[en]こんにちは"

    # AC-RFULL-002: same-page neighbours untouched
    neighbour = _text(conn, "region-a")
    assert neighbour["text"]["ocr_text"] == "A-text"
    assert neighbour["current_revision_id"] == "region-a-rev-1"
    assert _stage(conn, "region-a", "ocr") is None

    # AC-RFULL-005: manual translation and lock preserved
    locked = _text(conn, "region-c")
    assert locked["text"]["final_translation"] == "人工译文"
    assert locked["text"]["manual_edited"] is True
    assert locked["text"]["final_source"] == "edited"
    assert locked["translation_locked"] == 1


def test_render_is_the_single_translated_pointer_writer(workspace) -> None:
    """P0 constraint: exactly one new translated revision per render, the
    handler yields no ``revision_updates``, and the pointer never jitters."""
    conn = workspace["conn"]

    executed = _run_full_chain(workspace)
    assert executed.status is PipelineRunStatus.COMPLETED
    assert not executed.candidates  # no pointer conflict recorded
    first = _translated_revisions(conn)
    assert len(first) == 1
    assert _current_translated(conn) == first[0][0]

    # Handler contract: the seam must not flip the pointer again — the
    # handler itself returns no revision update (RenderService committed it).
    unit = PlanUnit(
        unit_id="u-render",
        task_id="t-render",
        target_id="region-b",
        page_id="page-1",
        region_id="region-b",
        step_type="render",
        decision=PlanDecision.RUN,
    )
    step_run = StepRun(
        step_run_id="s-render",
        task_id="t-render",
        target_id="region-b",
        page_id="page-1",
        region_id="region-b",
        step_type="render",
        unit_id="u-render",
        status=StepRunStatus.RUNNING,
        input_refs={},
        lock_snapshot=LockSnapshot(),
    )
    run = PipelineRun(
        run_id="r-render",
        command_type=CommandType.RERENDER_REGION,
        scope=PipelineScope(ScopeType.REGION, selected_ids=("region-b",)),
        requested_targets=(),
        targets=(),
        settings_snapshot={},
        provider_binding_snapshot={},
        constraint_snapshot_ref=None,
        context_policy={},
    )
    result = workspace["handlers"].handle_render(step_run, unit, run)
    assert result.revision_updates == {}
    assert result.next_stage_states["render"] is StageState.COMPLETED
    second = _translated_revisions(conn)
    assert len(second) == 2
    assert _current_translated(conn) == second[1][0]

    # A second command through the full seam: still exactly one more revision.
    # (A render-only RERENDER_REGION run stays planning-BLOCKED across runs —
    # the pre-existing `_clean_available` stage gap is registered in the Task
    # as an inherited planner defect outside this slice's allowed paths.)
    done = _run_full_chain(workspace)
    assert done.status is PipelineRunStatus.COMPLETED
    rerun_steps = {step.step_type: step for step in done.step_runs}
    assert rerun_steps["render"].status is StepRunStatus.COMPLETED
    third = _translated_revisions(conn)
    assert len(third) == 3
    assert _current_translated(conn) == third[2][0]
    assert [no for _rid, no in third] == [1, 2, 3]  # no jitter, no rewrites


def test_color_and_term_extract_fail_closed_without_assembly(workspace) -> None:
    """AC ①/②: an unassembled service fails the step with a typed code."""
    bare = ProductionHandlers(
        HandlerDependencies(
            registry=workspace["handlers"].deps.registry,
            regions=workspace["handlers"].deps.regions,
            region_writer=workspace["handlers"].deps.region_writer,
            artifacts=workspace["handlers"].deps.artifacts,
            images=workspace["handlers"].deps.images,
            geometry=workspace["handlers"].deps.geometry,
            retry_policy=RetryPolicy(max_attempts=1, backoff_seconds=0),
            route_policy=workspace["handlers"].deps.route_policy,
        )
    )
    unit = PlanUnit(
        unit_id="u",
        task_id="t",
        target_id="region-b",
        page_id="page-1",
        region_id="region-b",
        step_type="color",
        decision=PlanDecision.RUN,
    )
    step_run = StepRun(
        step_run_id="s",
        task_id="t",
        target_id="region-b",
        page_id="page-1",
        region_id="region-b",
        step_type="color",
        unit_id="u",
        status=StepRunStatus.RUNNING,
        input_refs={},
        lock_snapshot=LockSnapshot(),
    )
    run = PipelineRun(
        run_id="r",
        command_type=CommandType.RETRANSLATE_REGION_FULL,
        scope=PipelineScope(ScopeType.REGION, selected_ids=("region-b",)),
        requested_targets=(),
        targets=(),
        settings_snapshot={},
        provider_binding_snapshot={},
        constraint_snapshot_ref=None,
        context_policy={},
    )
    with pytest.raises(StepExecutionError) as color_error:
        bare.as_mapping()["color"](step_run, unit, run)
    assert color_error.value.code == "PROVIDER_NOT_CONFIGURED"

    term_unit = PlanUnit(
        unit_id="u2",
        task_id="t",
        target_id="region-b",
        page_id="page-1",
        region_id="region-b",
        step_type="term_extract",
        decision=PlanDecision.RUN,
    )
    with pytest.raises(StepExecutionError) as term_error:
        bare.as_mapping()["term_extract"](step_run, term_unit, run)
    assert term_error.value.code == "PROVIDER_NOT_CONFIGURED"

    render_unit = PlanUnit(
        unit_id="u3",
        task_id="t",
        target_id="region-b",
        page_id="page-1",
        region_id="region-b",
        step_type="render",
        decision=PlanDecision.RUN,
    )
    with pytest.raises(StepExecutionError) as render_error:
        bare.as_mapping()["render"](step_run, render_unit, run)
    assert render_error.value.code == "PROVIDER_NOT_CONFIGURED"


def test_render_fails_closed_when_clean_is_missing(workspace) -> None:
    """AC ③: without an upstream Clean the handler fails closed with the
    RenderService's own code — the planning guard
    (``BLOCKED(missing_clean_artifact)``, see
    ``test_translate_step_commits_but_render_remains_unwired``) stays in place
    and this proves the handler layer does not silently succeed either."""
    conn = workspace["conn"]
    assert _current_translated(conn) is None

    unit = PlanUnit(
        unit_id="u",
        task_id="t",
        target_id="region-b",
        page_id="page-1",
        region_id="region-b",
        step_type="render",
        decision=PlanDecision.RUN,
    )
    step_run = StepRun(
        step_run_id="s",
        task_id="t",
        target_id="region-b",
        page_id="page-1",
        region_id="region-b",
        step_type="render",
        unit_id="u",
        status=StepRunStatus.RUNNING,
        input_refs={},
        lock_snapshot=LockSnapshot(),
    )
    run = PipelineRun(
        run_id="r",
        command_type=CommandType.RERENDER_REGION,
        scope=PipelineScope(ScopeType.REGION, selected_ids=("region-b",)),
        requested_targets=(),
        targets=(),
        settings_snapshot={},
        provider_binding_snapshot={},
        constraint_snapshot_ref=None,
        context_policy={},
    )
    with pytest.raises(StepExecutionError) as error:
        workspace["handlers"].handle_render(step_run, unit, run)
    assert error.value.code == "MISSING_REQUIRED_INPUT"
    assert "clean" in error.value.detail
    # nothing was written
    assert _translated_revisions(conn) == []
    assert _text(conn, "region-b")["text"]["final_translation"] == ""
