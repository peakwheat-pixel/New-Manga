"""TASK-013 production SQLite and provider-dispatch seam checks."""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

import pytest

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from application.tasks.service import PipelineService  # noqa: E402
from domain.tasks.models import (  # noqa: E402
    CommandType,
    PipelineRunStatus,
    PipelineScope,
    PlanDecision,
    ScopeType,
    StageState,
)
from infrastructure.pipeline.executor import ProductionStepExecutor  # noqa: E402
from infrastructure.sqlite.connection import open_database  # noqa: E402
from infrastructure.sqlite.migrator import MigrationRunner  # noqa: E402
from infrastructure.sqlite.pipeline import (  # noqa: E402
    SqlitePipelineStore,
    SqliteSnapshotProvider,
    SqliteTargetCatalog,
    _region,
)
from infrastructure.sqlite.schema import default_migrations  # noqa: E402

NOW = "2026-09-16T00:00:00+00:00"


@pytest.fixture()
def production_db(tmp_path: Path):
    conn, _ = open_database(tmp_path / "app.db", latest_known_schema_version=3)
    MigrationRunner(conn, default_migrations()).apply_pending()
    now = "2026-09-16T00:00:00+00:00"
    with conn:
        conn.execute(
            "INSERT INTO books (book_id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
            ("book-1", "Book", now, now),
        )
        conn.execute(
            "INSERT INTO chapters (chapter_id, book_id, title, created_at, updated_at)"
            " VALUES (?, ?, ?, ?, ?)",
            ("chapter-1", "book-1", "Chapter", now, now),
        )
        conn.execute(
            "INSERT INTO pages (page_id, chapter_id, source_filename, source_order, sort_order,"
            " source_hash, source_size_bytes, width, height, managed_original_ref, created_at, updated_at)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            ("page-1", "chapter-1", "001.png", 0, 0, "hash", 3, 100, 100, "original/001.png", now, now),
        )
        text = {
            "ocr_text": "こんにちは",
            "machine_translation": "Hello",
            "edited_translation": "",
            "final_translation": "Hello",
            "final_source": "machine",
            "edited_confirmed": False,
            "manual_edited": False,
            "translation_locked": False,
        }
        conn.execute(
            "INSERT INTO regions (region_id, page_id, region_type, geometry_json, text_json,"
            " style_json, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            ("region-1", "page-1", "speech", "{}", json.dumps(text), "{}", now, now),
        )
        conn.execute(
            "INSERT INTO region_revisions (region_revision_id, region_id, revision_no,"
            " snapshot_json, origin, review_state, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("region-rev-1", "region-1", 1, "{}", "imported", "unreviewed", now),
        )
        conn.execute(
            "UPDATE regions SET current_revision_id = ? WHERE region_id = ?",
            ("region-rev-1", "region-1"),
        )
    yield conn
    conn.close()


def test_sqlite_catalog_expands_real_hierarchy_and_commits_guarded_state(production_db):
    catalog = SqliteTargetCatalog(production_db)
    page = catalog.expand(PipelineScope(ScopeType.BOOK, book_id="book-1"))[0]
    assert page.book_id == "book-1"
    assert page.chapter_id == "chapter-1"
    assert page.regions[0].region_id == "region-1"

    region = catalog.current("region-1")
    with production_db:
        production_db.execute(
            "INSERT INTO region_revisions (region_revision_id, region_id, revision_no,"
            " snapshot_json, origin, review_state, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("region-rev-2", "region-1", 2, "{}", "machine", "needs_review", "now"),
        )
    result = catalog.commit_step(
        target_id="region-1",
        expected_revisions={"region": "region-rev-1"},
        expected_lock=region.lock,
        stage_updates={"ocr": StageState.COMPLETED},
        revision_updates={"region": "region-rev-2"},
    )
    assert result.status == "applied"
    assert catalog.current("region-1").stage("ocr") is StageState.COMPLETED
    assert catalog.current("region-1").current_revisions["region"] == "region-rev-2"


def test_sqlite_snapshot_redacts_secrets_and_merges_overrides(production_db):
    provider = SqliteSnapshotProvider(
        production_db,
        settings={"model": {"name": "m"}, "api_key": "do-not-store"},
        provider_bindings={"translate": {"provider_id": "local"}},
        constraint_snapshot_ref="constraint-rev-1",
        context_policy={"window": "both"},
    )
    frozen = provider.freeze("run-1", overrides={"model": {"temperature": 0}})
    assert frozen.settings["model"]["name"] == "m"
    assert frozen.settings["model"]["temperature"] == 0
    assert "api_key" not in frozen.settings
    raw = production_db.execute("SELECT settings_json FROM pipeline_defaults").fetchone()[0]
    assert "do-not-store" not in raw


def test_production_service_round_trips_and_recovers_without_fake_executor(production_db):
    catalog = SqliteTargetCatalog(production_db)
    store = SqlitePipelineStore(production_db)
    service = PipelineService(
        catalog,
        store=store,
        snapshots=SqliteSnapshotProvider(production_db),
        executor=ProductionStepExecutor(),
    )
    run = service.create_run(
        CommandType.OCR_REGION,
        PipelineScope(ScopeType.REGION, selected_ids=("region-1",)),
    )
    service.plan_run(run.run_id)
    persisted = store.get(run.run_id)
    assert persisted is not None
    assert persisted.targets[0].page_id == "page-1"

    persisted.status = PipelineRunStatus.RUNNING
    store.put(run.run_id, persisted)
    assert service.recover_running_runs() == (run.run_id,)
    assert store.get(run.run_id).status is PipelineRunStatus.INTERRUPTED

    result = service.control_run(run.run_id, "continue")
    assert result.status is PipelineRunStatus.PENDING
    executed = service.execute_run(run.run_id)
    assert executed.status is PipelineRunStatus.COMPLETED_WITH_FAILURES
    assert executed.step_runs[0].error_code == "PROVIDER_UNAVAILABLE"
    assert production_db.execute("SELECT COUNT(*) FROM step_runs").fetchone()[0] == 1


# ---------------------------------------------------------------------------
# TASK-032 / F-1 against the real SQLite defaults
# ---------------------------------------------------------------------------


def _plan_region_units(conn, region_id: str):
    """Plan ``retranslate_region_full`` for one region through the real seam."""
    service = PipelineService(
        SqliteTargetCatalog(conn),
        store=SqlitePipelineStore(conn),
        snapshots=SqliteSnapshotProvider(conn),
        executor=ProductionStepExecutor(),
    )
    run = service.create_run(
        CommandType.RETRANSLATE_REGION_FULL,
        PipelineScope(ScopeType.REGION, selected_ids=(region_id,)),
    )
    service.plan_run(run.run_id)
    units = [unit for task in run.tasks for unit in task.units]
    return units, {unit.step_type: unit for unit in units}


def _seed_completed_stages(conn, region_id: str) -> None:
    for stage in ("ocr", "clean"):
        conn.execute(
            "INSERT INTO pipeline_stage_states (target_type, target_id, stage, status, updated_at)"
            " VALUES ('region', ?, ?, 'completed', ?)",
            (region_id, stage, NOW),
        )
    conn.commit()


def _insert_region(conn, region_id: str, *, region_type: str) -> None:
    """Insert a region without ``sfx_policy`` so the Schema default applies."""
    conn.execute(
        "INSERT INTO regions (region_id, page_id, region_type, geometry_json, text_json,"
        " style_json, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (
            region_id,
            "page-1",
            region_type,
            "{}",
            json.dumps(
                {
                    "ocr_text": "こんにちは",
                    "machine_translation": "Hello",
                    "edited_translation": "",
                    "final_translation": "Hello",
                    "final_source": "machine",
                    "edited_confirmed": False,
                    "manual_edited": False,
                    "translation_locked": False,
                }
            ),
            "{}",
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
    conn.commit()


def test_real_default_sfx_policy_does_not_gate_a_speech_region(production_db):
    """AC ④ / F-1: ``region_type='speech'`` + the Schema default policy plans RUN.

    The region is inserted **without** ``sfx_policy``, so the value comes from
    the real Schema default (``'skip'``, D03 §7) exactly as a newly created
    region would carry it — the situation the old helper's ``translate``
    default could not reach.
    """
    row = production_db.execute(
        "SELECT region_type, sfx_policy FROM regions WHERE region_id = 'region-1'"
    ).fetchone()
    assert (row["region_type"], row["sfx_policy"]) == ("speech", "skip")
    _seed_completed_stages(production_db, "region-1")

    units, by_step = _plan_region_units(production_db, "region-1")
    assert units
    assert {unit.decision for unit in units} == {PlanDecision.RUN}
    assert [unit for unit in units if unit.reason == "sfx_skip"] == []
    assert by_step["translate"].decision is PlanDecision.RUN


def test_real_default_sfx_policy_still_gates_an_sfx_region(production_db):
    """AC ①: with the same real default, an ``sfx`` region keeps SKIP_POLICY."""
    _insert_region(production_db, "region-2", region_type="sfx")
    row = production_db.execute(
        "SELECT region_type, sfx_policy FROM regions WHERE region_id = 'region-2'"
    ).fetchone()
    assert (row["region_type"], row["sfx_policy"]) == ("sfx", "skip")
    _seed_completed_stages(production_db, "region-2")

    _, by_step = _plan_region_units(production_db, "region-2")
    for step_type in ("translate", "segment", "mask_refine", "inpaint", "render"):
        assert by_step[step_type].decision is PlanDecision.SKIP_POLICY, step_type
        assert by_step[step_type].reason == "sfx_skip", step_type


def test_region_snapshot_deserialiser_uses_the_documented_sfx_default():
    """AC ③: the persisted-snapshot default agrees with entity and Schema.

    ``_region`` fills the field when a stored snapshot predates it; the value
    must be the documented ``skip`` (D03 §7), not ``translate``.
    """
    sfx = _region({"region_id": "r-sfx", "page_id": "p1", "region_type": "sfx"})
    assert sfx.sfx_policy == "skip"
    speech = _region({"region_id": "r-speech", "page_id": "p1"})
    assert speech.sfx_policy == "skip"
    # An explicitly stored value is still honoured unchanged.
    explicit = _region(
        {"region_id": "r-t", "page_id": "p1", "region_type": "sfx", "sfx_policy": "translate"}
    )
    assert explicit.sfx_policy == "translate"
