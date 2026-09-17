"""Production handlers against the real TASK-013 pipeline seam.

These are the integration checks for TASK-019's write contract: real SQLite,
real optimistic guard, fake providers. They prove that

- a Region step writes exactly one Region (AC-OCR-001, AC-RFULL-002);
- manual/translation-locked results are never overwritten (AC-OCR-002);
- Mask/Clean revisions are persisted and re-inpaint creates a *new* Clean
  instead of overwriting the previous one (AC-INPAINT-001/002);
- a missing binding or an unimplemented route fails the step with a typed
  code and leaves the data untouched (AC-FALLBACK-001, fail-closed).
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

from application.tasks.service import PipelineService
from domain.tasks.models import (
    CommandType,
    PipelineRunStatus,
    PipelineScope,
    ScopeType,
    StageState,
    StepRunStatus,
)
from infrastructure.filesystem.managed_storage import ManagedFileStorage
from infrastructure.pipeline.assembly import build_production_pipeline
from infrastructure.providers.handlers import (
    HandlerDependencies,
    ProductionHandlers,
    RegionMaskGeometry,
)
from infrastructure.providers.registry import ProviderDescriptor, ProviderRegistry
from infrastructure.providers.retry import RetryPolicy
from infrastructure.providers.step_writes import (
    ArtifactStepWriter,
    RegionStepWriter,
    decode_mask_payload,
)
from application.translation.inpaint.router import RoutePolicy
from infrastructure.providers.inpaint_routes import EdgeBleedProvider, SimpleFillProvider
from infrastructure.sqlite.connection import open_database
from infrastructure.sqlite.migrator import MigrationRunner
from infrastructure.sqlite.regions import SqliteRegionRepository
from infrastructure.sqlite.schema import default_migrations
from ports.inpaint.ports import ROUTE_EDGE_BLEED, ROUTE_MANGA_LAMA, ROUTE_SIMPLE_FILL
from ports.providers.errors import LockBlocked
from ports.providers.profiles import (
    CAPABILITY_INPAINT,
    CAPABILITY_OCR,
    CAPABILITY_TRANSLATION,
)

from conftest import (
    FakeGeometry,
    FakeOcrProvider,
    FakePageImages,
    FakeTranslationProvider,
    frame,
)

NOW = "2026-09-17T00:00:00+00:00"


class _FakeGeometrySource:
    def __init__(self, boxes):
        self._boxes = boxes

    def mask_geometry(self, region_id: str) -> RegionMaskGeometry:
        return RegionMaskGeometry(boxes=self._boxes.get(region_id, ((0, 0, 2, 2),)))


@pytest.fixture()
def workspace(tmp_path: Path):
    latest = max(migration.schema_version for migration in default_migrations())
    conn, _opened = open_database(tmp_path / "app.db", latest_known_schema_version=latest)
    MigrationRunner(conn, default_migrations()).apply_pending()

    def region_text(**overrides):
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

    with conn:
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
            "INSERT INTO pages (page_id, chapter_id, source_filename, source_order, sort_order,"
            " source_hash, source_size_bytes, width, height, managed_original_ref, created_at, updated_at)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            ("page-1", "chapter-1", "001.png", 0, 0, "hash", 3, 20, 20, "original/001.png", NOW, NOW),
        )
        for region_id, text in (
            ("region-a", region_text(ocr_text="A-text")),
            ("region-b", region_text(ocr_text="B-source")),
            (
                "region-c",
                region_text(
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
                "INSERT INTO regions (region_id, page_id, region_type, geometry_json, text_json,"
                " style_json, sfx_policy, translation_locked, current_revision_id, created_at, updated_at)"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?, NULL, ?, ?)",
                (
                    region_id,
                    "page-1",
                    "speech",
                    json.dumps({"bbox": [2, 2, 3, 3], "polygon": []}),
                    json.dumps(text),
                    "{}",
                    "translate",
                    1 if text["translation_locked"] else 0,
                    NOW,
                    NOW,
                ),
            )
            conn.execute(
                "INSERT INTO region_revisions (region_revision_id, region_id, revision_no,"
                " snapshot_json, origin, review_state, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (f"{region_id}-rev-1", region_id, 1, "{}", "imported", "unreviewed", NOW),
            )
            conn.execute(
                "UPDATE regions SET current_revision_id = ? WHERE region_id = ?",
                (f"{region_id}-rev-1", region_id),
            )

        # region-b has already been OCR'ed in the product flow: the planner
        # requires a valid ``ocr`` stage before translate/segment (D06 §26).
        conn.execute(
            "INSERT INTO pipeline_stage_states (target_type, target_id, stage, status, updated_at)"
            " VALUES ('region', 'region-b', 'ocr', 'completed', ?)",
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

    handlers = ProductionHandlers(
        HandlerDependencies(
            registry=registry,
            regions=regions,
            region_writer=RegionStepWriter(conn, regions),
            artifacts=ArtifactStepWriter(conn, storage),
            images=FakePageImages(page=frame(20, 20, (240, 240, 240))),
            geometry=_FakeGeometrySource(
                {
                    "region-a": ((1, 1, 4, 4),),
                    "region-b": ((1, 1, 3, 3),),
                    "region-c": ((10, 10, 14, 14),),
                }
            ),
            retry_policy=RetryPolicy(max_attempts=1, backoff_seconds=0),
            route_policy=RoutePolicy(
                allowed_routes=(ROUTE_SIMPLE_FILL, ROUTE_EDGE_BLEED),
                color_route=ROUTE_MANGA_LAMA,
                requirements={ROUTE_MANGA_LAMA: False},
            ),
        )
    )

    yield {
        "conn": conn,
        "regions": regions,
        "storage": storage,
        "handlers": handlers,
        "ocr_provider": ocr_provider,
        "translate_provider": translate_provider,
    }
    conn.close()


def _pipeline(workspace, *, bindings=None, settings=None) -> PipelineService:
    return build_production_pipeline(
        workspace["conn"],
        handlers=workspace["handlers"].as_mapping(),
        settings=settings or {"ocr": {"script": "japanese"}},
        provider_bindings=bindings
        if bindings is not None
        else {
            "ocr": {"provider_id": "fake-ocr"},
            "translate": {"provider_id": "fake-translate"},
        },
    )


def _text(conn: sqlite3.Connection, region_id: str) -> dict:
    row = conn.execute(
        "SELECT text_json, current_revision_id, sfx_policy FROM regions WHERE region_id = ?",
        (region_id,),
    ).fetchone()
    return {
        "text": json.loads(row["text_json"]),
        "current_revision_id": row["current_revision_id"],
        "sfx_policy": row["sfx_policy"],
    }


def _revision_ids(conn: sqlite3.Connection, region_id: str) -> list[str]:
    rows = conn.execute(
        "SELECT region_revision_id FROM region_revisions WHERE region_id = ?"
        " ORDER BY revision_no",
        (region_id,),
    ).fetchall()
    return [row["region_revision_id"] for row in rows]


def _stage(conn: sqlite3.Connection, target_id: str, stage: str):
    row = conn.execute(
        "SELECT status FROM pipeline_stage_states WHERE target_type = 'region'"
        " AND target_id = ? AND stage = ?",
        (target_id, stage),
    ).fetchone()
    return StageState(row["status"]) if row else None


def test_ocr_region_writes_only_the_target_region(workspace) -> None:
    conn = workspace["conn"]
    before_a = _text(conn, "region-a")
    before_c = _text(conn, "region-c")

    service = _pipeline(workspace)
    run = service.create_run(
        CommandType.OCR_REGION, PipelineScope(ScopeType.REGION, selected_ids=("region-b",))
    )
    service.plan_run(run.run_id)
    executed = service.execute_run(run.run_id)

    assert executed.status is PipelineRunStatus.COMPLETED
    assert len(executed.step_runs) == 1
    step = executed.step_runs[0]
    assert step.status is StepRunStatus.COMPLETED
    assert step.output["ocr_text"] == "こんにちは"
    assert step.output["provenance"]["provider_id"] == "fake-ocr"
    assert step.output["provenance"]["model"] == "fake-model"
    assert step.output["provenance"]["attempt_count"] == 1

    target = _text(conn, "region-b")
    assert target["text"]["ocr_text"] == "こんにちは"
    assert target["current_revision_id"] == _revision_ids(conn, "region-b")[-1]
    assert len(_revision_ids(conn, "region-b")) == 2
    assert _stage(conn, "region-b", "ocr") is StageState.COMPLETED

    # A/C untouched: text, pointer and stage state.
    assert _text(conn, "region-a") == before_a
    assert _text(conn, "region-c") == before_c
    assert _stage(conn, "region-a", "ocr") is None
    assert _stage(conn, "region-c", "ocr") is None


def test_ocr_keeps_manual_translation_and_reports_the_hint(workspace) -> None:
    """AC-OCR-002 stays the domain's decision, not the adapter's."""
    conn = workspace["conn"]
    service = _pipeline(workspace)
    run = service.create_run(
        CommandType.OCR_REGION, PipelineScope(ScopeType.REGION, selected_ids=("region-c",))
    )
    service.plan_run(run.run_id)
    executed = service.execute_run(run.run_id)

    assert executed.status is PipelineRunStatus.COMPLETED
    assert executed.step_runs[0].output["retranslate_hint"] is True
    text = _text(conn, "region-c")["text"]
    assert text["ocr_text"] == "こんにちは"
    assert text["edited_translation"] == "人工译文"
    assert text["final_translation"] == "人工译文"
    assert text["translation_locked"] is True


def test_locked_region_is_skipped_and_never_translated(workspace) -> None:
    conn = workspace["conn"]
    before = _text(conn, "region-c")
    service = _pipeline(workspace)
    run = service.create_run(
        CommandType.RETRANSLATE_REGION,
        PipelineScope(ScopeType.REGION, selected_ids=("region-c",)),
    )
    service.plan_run(run.run_id)
    executed = service.execute_run(run.run_id)

    assert executed.step_runs == []
    assert executed.status is PipelineRunStatus.COMPLETED
    decisions = {unit.step_type: unit.decision for unit in executed.tasks[0].units}
    assert decisions["translate"].value == "skip_lock"
    assert _text(conn, "region-c") == before


def test_translate_step_commits_but_render_remains_unwired(workspace) -> None:
    """Evidence for AC-RFULL-001: only the capability steps this Task owns run."""
    conn = workspace["conn"]
    service = _pipeline(workspace)
    run = service.create_run(
        CommandType.RETRANSLATE_REGION,
        PipelineScope(ScopeType.REGION, selected_ids=("region-b",)),
    )
    service.plan_run(run.run_id)
    executed = service.execute_run(run.run_id)

    steps = {step.step_type: step for step in executed.step_runs}
    assert steps["translate"].status is StepRunStatus.COMPLETED
    assert steps["translate"].output["machine_translation"] == "[en]B-source"
    assert steps["translate"].output["provenance"]["provider_id"] == "fake-translate"
    assert tuple(steps["translate"].output["context_provenance"]["context_pages"]) == ()

    # AC-RFULL-001 evidence: the chain stops after the steps this Task owns.
    # `render` is planned BLOCKED (no Clean Artifact / no render handler), and
    # no StepRun is created for it — it is never faked.
    assert "render" not in steps
    decisions = {unit.step_type: unit.decision for unit in executed.tasks[0].units}
    assert decisions["render"].value == "blocked"
    render_unit = next(
        unit for unit in executed.tasks[0].units if unit.step_type == "render"
    )
    assert render_unit.reason == "missing_clean_artifact"
    assert executed.status is PipelineRunStatus.BLOCKED

    text = _text(conn, "region-b")["text"]
    assert text["machine_translation"] == "[en]B-source"
    assert text["final_translation"] == "[en]B-source"
    assert text["final_source"] == "machine"


def test_reinpaint_chain_persists_masks_and_clean_revisions(workspace) -> None:
    conn = workspace["conn"]
    service = _pipeline(
        workspace,
        settings={
            "inpaint": {
                "dilate_radius": 0,
                "erode_radius": 0,
                "is_solid_background": True,
                "route_policy": {
                    "allowed_routes": [ROUTE_SIMPLE_FILL, ROUTE_EDGE_BLEED],
                    "requirements": {ROUTE_SIMPLE_FILL: True, ROUTE_EDGE_BLEED: True},
                },
            }
        },
    )
    run = service.create_run(
        CommandType.REINPAINT_REGION,
        PipelineScope(ScopeType.REGION, selected_ids=("region-b",)),
    )
    service.plan_run(run.run_id)
    executed = service.execute_run(run.run_id)

    assert executed.status is PipelineRunStatus.COMPLETED, [
        (step.step_type, step.error_code, step.error_detail) for step in executed.step_runs
    ]
    steps = {step.step_type: step for step in executed.step_runs}
    assert set(steps) == {"segment", "mask_refine", "inpaint"}

    mask_artifact = conn.execute(
        "SELECT artifact_id, current_revision_id FROM media_artifacts"
        " WHERE page_id = 'page-1' AND artifact_type = 'mask'"
    ).fetchone()
    clean_artifact = conn.execute(
        "SELECT artifact_id, current_revision_id FROM media_artifacts"
        " WHERE page_id = 'page-1' AND artifact_type = 'clean'"
    ).fetchone()
    assert mask_artifact is not None and clean_artifact is not None

    mask_revisions = conn.execute(
        "SELECT artifact_revision_id, revision_no, managed_path, provenance_json"
        " FROM artifact_revisions WHERE artifact_id = ? ORDER BY revision_no",
        (mask_artifact["artifact_id"],),
    ).fetchall()
    assert [row["revision_no"] for row in mask_revisions] == [1, 2]
    assert mask_artifact["current_revision_id"] == mask_revisions[-1]["artifact_revision_id"]

    # AC-INPAINT-001: the current Mask Revision is readable after the run.
    workspace["storage"].absolute_path(mask_revisions[-1]["managed_path"])
    payload = Path(
        workspace["storage"].absolute_path(mask_revisions[1]["managed_path"])
    ).read_bytes()
    header, restored = decode_mask_payload(payload)
    assert (header["width"], header["height"]) == (20, 20)
    assert restored.area > 0
    record = json.loads(mask_revisions[1]["provenance_json"])["mask_record"]
    assert record["final_covers_raw"] is True
    assert record["mask_params"]["dilate_radius"] == "0"
    assert record["mask_params"]["min_region_pixels"] == "1"

    # AC-INPAINT-003: router provenance travels with the clean revision.
    clean_rows = conn.execute(
        "SELECT artifact_revision_id, provenance_json FROM artifact_revisions"
        " WHERE artifact_id = ? ORDER BY revision_no",
        (clean_artifact["artifact_id"],),
    ).fetchall()
    assert len(clean_rows) == 1
    provenance = json.loads(clean_rows[0]["provenance_json"])
    assert provenance["router_route"] == ROUTE_SIMPLE_FILL
    assert provenance["router_reason"]
    assert provenance["mask_params"]
    assert provenance["new_revision_required"] is True
    assert steps["inpaint"].output["route"] == ROUTE_SIMPLE_FILL

    # AC-INPAINT-002: a second repaint creates a new Clean revision.
    second = service.create_run(
        CommandType.REINPAINT_REGION,
        PipelineScope(ScopeType.REGION, selected_ids=("region-b",)),
    )
    service.plan_run(second.run_id)
    executed_again = service.execute_run(second.run_id)
    assert executed_again.status is PipelineRunStatus.COMPLETED, [
        (step.step_type, step.error_code, step.error_detail)
        for step in executed_again.step_runs
    ]
    clean_rows = conn.execute(
        "SELECT artifact_revision_id, revision_no FROM artifact_revisions"
        " WHERE artifact_id = ? ORDER BY revision_no",
        (clean_artifact["artifact_id"],),
    ).fetchall()
    assert [row["revision_no"] for row in clean_rows] == [1, 2]
    assert clean_rows[0]["artifact_revision_id"] != clean_rows[1]["artifact_revision_id"]
    current = conn.execute(
        "SELECT current_revision_id FROM media_artifacts WHERE artifact_id = ?",
        (clean_artifact["artifact_id"],),
    ).fetchone()["current_revision_id"]
    assert current == clean_rows[1]["artifact_revision_id"]


def test_unimplemented_route_blocks_without_writing_anything(workspace) -> None:
    conn = workspace["conn"]
    service = _pipeline(
        workspace,
        settings={
            "inpaint": {
                "is_color_webtoon": True,
                "route_policy": {"allowed_routes": [ROUTE_MANGA_LAMA]},
            }
        },
    )
    run = service.create_run(
        CommandType.REINPAINT_REGION,
        PipelineScope(ScopeType.REGION, selected_ids=("region-b",)),
    )
    service.plan_run(run.run_id)
    executed = service.execute_run(run.run_id)

    steps = {step.step_type: step for step in executed.step_runs}
    assert steps["inpaint"].status is StepRunStatus.FAILED
    assert steps["inpaint"].error_code == "PROVIDER_NOT_IMPLEMENTED"
    assert "not implemented" in (steps["inpaint"].error_detail or "")
    assert (
        conn.execute(
            "SELECT COUNT(*) FROM media_artifacts WHERE artifact_type = 'clean'"
        ).fetchone()[0]
        == 0
    )


def test_page_scope_reinpaint_expands_to_regions_and_accumulates_clean(workspace) -> None:
    """Page-scope commands expand into Region units (D06 §48) and stay cumulative."""
    conn = workspace["conn"]
    # Every Region of the page has already been OCR'ed (the planner requires a
    # valid OCR stage before segment; see the fixture note).
    for region_id in ("region-a", "region-c"):
        conn.execute(
            "INSERT INTO pipeline_stage_states (target_type, target_id, stage, status, updated_at)"
            " VALUES ('region', ?, 'ocr', 'completed', ?)",
            (region_id, NOW),
        )
    conn.commit()
    service = _pipeline(
        workspace,
        settings={
            "inpaint": {
                "dilate_radius": 0,
                "erode_radius": 0,
                "route_policy": {
                    "allowed_routes": [ROUTE_SIMPLE_FILL, ROUTE_EDGE_BLEED],
                    "requirements": {ROUTE_SIMPLE_FILL: True, ROUTE_EDGE_BLEED: True},
                },
            }
        },
    )
    run = service.create_run(
        CommandType.REINPAINT_ALL, PipelineScope(ScopeType.PAGE, selected_ids=("page-1",))
    )
    service.plan_run(run.run_id)
    executed = service.execute_run(run.run_id)

    assert executed.status is PipelineRunStatus.COMPLETED, [
        (step.step_type, step.error_code, step.error_detail) for step in executed.step_runs
    ]
    step_types = [step.step_type for step in executed.step_runs]
    assert step_types.count("segment") == 3
    assert step_types.count("mask_refine") == 3
    assert step_types.count("inpaint") == 3
    # Every unit is Region-scoped even though the command was page-scoped.
    assert {step.target_id for step in executed.step_runs} == {
        "region-a",
        "region-b",
        "region-c",
    }

    clean_artifact = conn.execute(
        "SELECT artifact_id FROM media_artifacts WHERE artifact_type = 'clean'"
    ).fetchone()
    clean_rows = conn.execute(
        "SELECT artifact_revision_id, revision_no, source_artifact_revision_id"
        " FROM artifact_revisions WHERE artifact_id = ? ORDER BY revision_no",
        (clean_artifact["artifact_id"],),
    ).fetchall()
    assert [row["revision_no"] for row in clean_rows] == [1, 2, 3]
    # Each region's repair is based on the previous Clean revision: the page's
    # repairs accumulate instead of overwriting each other.
    assert clean_rows[0]["source_artifact_revision_id"] is None
    assert clean_rows[1]["source_artifact_revision_id"] == clean_rows[0]["artifact_revision_id"]
    assert clean_rows[2]["source_artifact_revision_id"] == clean_rows[1]["artifact_revision_id"]
    current = conn.execute(
        "SELECT current_revision_id FROM media_artifacts WHERE artifact_id = ?",
        (clean_artifact["artifact_id"],),
    ).fetchone()["current_revision_id"]
    assert current == clean_rows[2]["artifact_revision_id"]

    mask_artifact = conn.execute(
        "SELECT artifact_id FROM media_artifacts WHERE artifact_type = 'mask'"
    ).fetchone()
    mask_count = conn.execute(
        "SELECT COUNT(*) FROM artifact_revisions WHERE artifact_id = ?",
        (mask_artifact["artifact_id"],),
    ).fetchone()[0]
    assert mask_count == 6  # raw + refined per Region, history preserved


def test_missing_provider_binding_fails_closed(workspace) -> None:
    conn = workspace["conn"]
    before = _text(conn, "region-b")
    service = _pipeline(workspace, bindings={})
    run = service.create_run(
        CommandType.OCR_REGION, PipelineScope(ScopeType.REGION, selected_ids=("region-b",))
    )
    service.plan_run(run.run_id)
    executed = service.execute_run(run.run_id)

    step = executed.step_runs[0]
    assert step.status is StepRunStatus.FAILED
    assert step.error_code == "PROVIDER_NOT_CONFIGURED"
    assert _text(conn, "region-b") == before
    assert len(_revision_ids(conn, "region-b")) == 1


def test_stale_region_revision_is_refused_before_any_write(workspace) -> None:
    """The writer applies the seam's optimistic guard before mutating text."""
    conn = workspace["conn"]
    writer = RegionStepWriter(conn, workspace["regions"])
    before = _text(conn, "region-b")

    with pytest.raises(LockBlocked) as error:
        writer.prepare_ocr_text(
            "region-b", "stale", expected_current_revision_id="region-b-rev-999"
        )
    assert error.value.error_code == "LOCK_CHANGED"
    assert _text(conn, "region-b") == before
    assert len(_revision_ids(conn, "region-b")) == 1

    # The matching expectation still writes.
    prepared = writer.prepare_ocr_text(
        "region-b", "fresh", expected_current_revision_id="region-b-rev-1"
    )
    assert prepared.revision_id in _revision_ids(conn, "region-b")


def test_locked_region_refuses_ocr_and_translation_writes(workspace) -> None:
    conn = workspace["conn"]
    conn.execute(
        "UPDATE regions SET region_locked = 1 WHERE region_id = 'region-a'"
    )
    conn.commit()
    writer = RegionStepWriter(conn, workspace["regions"])
    with pytest.raises(LockBlocked):
        writer.prepare_ocr_text("region-a", "x")

    # Translation lock on region-c (the planner skips it; the writer refuses too).
    with pytest.raises(LockBlocked):
        writer.prepare_machine_translation("region-c", "y")
    assert _text(conn, "region-c")["text"]["edited_translation"] == "人工译文"


def test_stale_artifact_pointer_is_refused_before_publishing(workspace) -> None:
    storage = workspace["storage"]
    writer = ArtifactStepWriter(workspace["conn"], storage)
    with pytest.raises(LockBlocked):
        writer.prepare_revision(
            page_id="page-1",
            artifact_type="mask",
            payload=b"payload",
            mime_type="application/x-newmanga-mask",
            expected_current_revision_id="not-the-current-one",
        )
    assert (
        workspace["conn"].execute(
            "SELECT COUNT(*) FROM artifact_revisions"
        ).fetchone()[0]
        == 0
    )
