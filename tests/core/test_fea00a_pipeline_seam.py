"""FEA-00a V1–V9 checks through the production Core assembly and pipeline."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import hashlib
import io
import json
from pathlib import Path
import sqlite3
import sys
from urllib.parse import quote

from PIL import Image
import pytest

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from application.importing.images.ports import ImportSource
from application.translation.color.service import SourceStyleService
from bootstrap.core_assembly import assemble_core_services
from bootstrap.core_service import _PassthroughImageDecoder
from domain.regions.entities import BBox, RegionGeometry, SfxPolicy
from domain.tasks.models import CommandType, PipelineRunStatus, PipelineScope, ScopeType, StageState
from infrastructure.rendering.pillow_source_style import PillowSourceStyleAnalyzer
from infrastructure.sqlite.pipeline import SqlitePipelineStore


def _assemble(root: Path):
    return assemble_core_services(
        root / "library.db",
        root / "managed",
        image_decoder=_PassthroughImageDecoder(),
        font_catalog=object(),  # type: ignore[arg-type]
        layout_engine=object(),  # type: ignore[arg-type]
        compositor=object(),  # type: ignore[arg-type]
        source_styles=SourceStyleService(PillowSourceStyleAnalyzer()),
        mock_local_providers=True,
        recover_runs_on_assembly=True,
    )


def _png() -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (32, 24), "white").save(buffer, format="PNG")
    return buffer.getvalue()


def _new_workspace(root: Path):
    core = _assemble(root)
    book = core.library.create_book("FEA-00a test")
    chapter = core.library.create_chapter(book.book_id, "Chapter")
    payload = _png()
    imported = core.importer.import_files(
        chapter.chapter_id,
        [ImportSource(filename="page.png", data_provider=lambda: payload)],
    )
    page = imported.imported[0].page
    region = core.editing.create_region(
        page.page_id,
        RegionGeometry(bbox=BBox(4, 4, 16, 12)),
        reading_order=1,
    )
    core.pipeline_defaults.save_provider_binding("ocr", "m2ac1-mock-ocr")
    core.pipeline_defaults.save_settings_section("ocr", {"script": "japanese"})
    return core, page.page_id, region.region_id


def _prepare_ocr(core, region_id: str, *, running: bool = False):
    pipeline = core.pipeline
    run = pipeline.create_run(
        CommandType.OCR_REGION,
        PipelineScope(ScopeType.REGION, selected_ids=(region_id,)),
    )
    pipeline.plan_run(run.run_id)
    if running:
        run.status = PipelineRunStatus.RUNNING
        pipeline._persist(run)
    task = run.tasks[0]
    unit = next(item for item in task.units if item.step_type == "ocr")
    step = pipeline.record_step_attempt(task.task_id, "ocr")
    result = pipeline._executor.execute(step, unit, run)
    return run, step, unit, result


def _prepare_segment(core, region_id: str, *, running: bool = False):
    current = core.pipeline._catalog.current(region_id)
    if current.stage("ocr") is not StageState.COMPLETED:
        _ocr_run, ocr_step, _ocr_unit, ocr_result = _prepare_ocr(core, region_id)
        assert core.pipeline.commit_step_result(
            ocr_step.step_run_id, ocr_result
        ).status == "committed"
    pipeline = core.pipeline
    run = pipeline.create_run(
        CommandType.REINPAINT_REGION,
        PipelineScope(ScopeType.REGION, selected_ids=(region_id,)),
    )
    pipeline.plan_run(run.run_id)
    if running:
        run.status = PipelineRunStatus.RUNNING
        pipeline._persist(run)
    task = run.tasks[0]
    unit = next(item for item in task.units if item.step_type == "segment")
    assert unit.decision.value == "run", (unit.decision, unit.reason)
    step = pipeline.record_step_attempt(task.task_id, "segment")
    result = pipeline._executor.execute(step, unit, run)
    return run, step, unit, result


def _region_snapshot(core, region_id: str):
    row = core.conn.execute(
        "SELECT text_json, current_revision_id FROM regions WHERE region_id = ?",
        (region_id,),
    ).fetchone()
    count = core.conn.execute(
        "SELECT COUNT(*) FROM region_revisions WHERE region_id = ?", (region_id,)
    ).fetchone()[0]
    return row["text_json"], row["current_revision_id"], count


def _candidate(core, candidate_id: str):
    row = core.conn.execute(
        "SELECT candidate_id, pipeline_run_id, step_run_id, result_kind,"
        " base_revision_id, payload_json, status, resolved_at"
        " FROM step_result_candidates WHERE candidate_id = ?",
        (candidate_id,),
    ).fetchone()
    return dict(row) if row else None


def _commit_ocr(core, step, result):
    return core.pipeline.commit_step_result(step.step_run_id, result)


def test_v1_revision_conflict_abandons_prepare_and_preserves_both_rows(tmp_path):
    core, _page_id, region_id = _new_workspace(tmp_path)
    try:
        before_prepare = _region_snapshot(core, region_id)
        run, step, _unit, result = _prepare_ocr(core, region_id)
        candidate_id = result.revision_updates["region"]
        assert _region_snapshot(core, region_id) == before_prepare

        core.editing.set_region_type(
            region_id, "sfx", current_global_sfx_policy=SfxPolicy.SKIP
        )
        before_seam = _region_snapshot(core, region_id)
        outcome = _commit_ocr(core, step, result)

        assert outcome.status == "candidate"
        assert outcome.error_code == "INPUT_REVISION_CHANGED"
        assert _region_snapshot(core, region_id) == before_seam
        rows = core.conn.execute(
            "SELECT candidate_id, status, resolved_at FROM step_result_candidates"
            " WHERE step_run_id = ? ORDER BY status",
            (step.step_run_id,),
        ).fetchall()
        assert {row["status"] for row in rows} == {"abandoned", "pending"}
        assert len({row["candidate_id"] for row in rows}) == 2
        prepared = next(row for row in rows if row["candidate_id"] == candidate_id)
        assert prepared["resolved_at"] is not None
    finally:
        core.conn.close()


def test_v2_lock_conflict_abandons_prepare_without_live_mutation(tmp_path):
    core, _page_id, region_id = _new_workspace(tmp_path)
    try:
        run, step, _unit, result = _prepare_ocr(core, region_id)
        candidate_id = result.revision_updates["region"]
        with core.conn:
            core.conn.execute(
                "UPDATE regions SET region_locked = 1 WHERE region_id = ?", (region_id,)
            )
        before_seam = _region_snapshot(core, region_id)
        outcome = _commit_ocr(core, step, result)

        assert outcome.status == "candidate"
        assert outcome.error_code == "LOCK_CHANGED"
        assert _region_snapshot(core, region_id) == before_seam
        row = _candidate(core, candidate_id)
        assert row["status"] == "abandoned"
        assert row["resolved_at"] is not None
    finally:
        core.conn.close()


def test_v3_stale_run_snapshot_rolls_back_live_region_writes(tmp_path):
    core, _page_id, region_id = _new_workspace(tmp_path)
    second = None
    try:
        run, step, _unit, result = _prepare_ocr(core, region_id)
        candidate_id = result.revision_updates["region"]
        before_seam = _region_snapshot(core, region_id)
        second = sqlite3.connect(str(core.database_path), timeout=10)
        second.row_factory = sqlite3.Row
        second.execute("PRAGMA foreign_keys = ON")
        mirror_store = SqlitePipelineStore(second)
        store = core.pipeline._store

        def stale_snapshot(_run):
            from domain.tasks.models import PipelineError
            raise PipelineError("STALE_RUN_SNAPSHOT", "injected concurrent Run revision")

        store._check_write_revision = stale_snapshot
        outcome = _commit_ocr(core, step, result)

        assert outcome.status == "stale"
        assert "STALE_RUN_SNAPSHOT" in outcome.detail
        assert _region_snapshot(core, region_id) == before_seam
        row = _candidate(core, candidate_id)
        assert row["status"] == "abandoned"
        assert row["resolved_at"] is not None
    finally:
        if second is not None:
            second.close()
        core.conn.close()


def test_v4_artifact_commit_failure_compensates_published_file(tmp_path):
    core, page_id, region_id = _new_workspace(tmp_path)
    try:
        run, step, _unit, result = _prepare_segment(core, region_id)
        before_region = _region_snapshot(core, region_id)
        candidate_id = result.revision_updates["mask"]
        candidate = _candidate(core, candidate_id)
        payload = json.loads(candidate["payload_json"])
        final_path = Path(core.storage.absolute_path(payload["relative_path"]))
        temp_path = Path(payload["temp_handle"])
        original_publish = core.storage.publish

        def publish_then_violate_deferred_fk(temp_handle, relative_path):
            original_publish(temp_handle, relative_path)
            core.conn.execute("PRAGMA defer_foreign_keys = ON")
            core.conn.execute(
                "INSERT INTO media_artifacts (artifact_id, book_id, chapter_id, page_id,"
                " artifact_type, current_revision_id, created_at, updated_at)"
                " VALUES ('orphan-injected', 'missing-book', 'missing-chapter', ?,"
                " 'mask', NULL, 'now', 'now')",
                (page_id,),
            )

        core.storage.publish = publish_then_violate_deferred_fk
        try:
            outcome = core.pipeline.commit_step_result(step.step_run_id, result)
        finally:
            core.storage.publish = original_publish

        assert outcome.status == "failed"
        assert outcome.error_code == "DB_FAILED"
        assert _region_snapshot(core, region_id) == before_region
        assert core.conn.execute(
            "SELECT COUNT(*) FROM media_artifacts WHERE page_id = ?", (page_id,)
        ).fetchone()[0] == 0
        assert core.conn.execute("SELECT COUNT(*) FROM artifact_revisions").fetchone()[0] == 0
        assert not final_path.exists()
        assert not temp_path.exists()
        assert core.pipeline._catalog.orphaned_paths == []
        assert _candidate(core, candidate_id)["status"] == "abandoned"
    finally:
        core.conn.close()


@pytest.mark.parametrize(
    ("action", "expected", "step_status"),
    [("pause", "paused", "interrupted"), ("stop", "cancelled", "cancelled")],
)
def test_v5_pause_and_cancel_abandon_after_seam_rollback(
    tmp_path, action: str, expected: str, step_status: str
):
    core, _page_id, region_id = _new_workspace(tmp_path)
    try:
        before = _region_snapshot(core, region_id)
        run, step, _unit, result = _prepare_ocr(core, region_id, running=True)
        candidate_id = result.revision_updates["region"]
        core.pipeline.control_run(run.run_id, action)
        outcome = _commit_ocr(core, step, result)

        assert outcome.status == expected
        assert _region_snapshot(core, region_id) == before
        assert _candidate(core, candidate_id)["status"] == "abandoned"
        fresh = core.pipeline.get_run_snapshot(run.run_id, fresh=True)
        assert fresh.step_runs[-1].status.value == step_status
        assert fresh.status.value == expected
        assert not core.conn.in_transaction
    finally:
        core.conn.close()


def test_v6_restart_sweep_abandons_prepared_candidate_and_counts_it(tmp_path):
    core, _page_id, region_id = _new_workspace(tmp_path)
    before = _region_snapshot(core, region_id)
    run, step, _unit, result = _prepare_ocr(core, region_id, running=True)
    candidate_id = result.revision_updates["region"]
    assert _candidate(core, candidate_id)["status"] == "prepared"
    core.conn.close()

    restarted = _assemble(tmp_path)
    try:
        assert _region_snapshot(restarted, region_id) == before
        row = _candidate(restarted, candidate_id)
        assert row["status"] == "abandoned"
        assert row["resolved_at"] is not None
        assert restarted.pipeline.startup_cleanup_result["abandoned_prepared"] == 1
    finally:
        restarted.conn.close()


def test_v6_artifact_restart_removes_unreferenced_final_file(tmp_path):
    core, page_id, region_id = _new_workspace(tmp_path)
    run, step, _unit, result = _prepare_segment(core, region_id, running=True)
    candidate_id = result.revision_updates["mask"]
    payload = json.loads(_candidate(core, candidate_id)["payload_json"])
    final_path = Path(core.storage.absolute_path(payload["relative_path"]))
    core.storage.publish(payload["temp_handle"], payload["relative_path"])
    assert final_path.exists()
    core.conn.close()

    restarted = _assemble(tmp_path)
    try:
        row = _candidate(restarted, candidate_id)
        assert row["status"] == "abandoned"
        assert row["resolved_at"] is not None
        assert not final_path.exists()
        assert restarted.conn.execute(
            "SELECT COUNT(*) FROM media_artifacts WHERE page_id = ?", (page_id,)
        ).fetchone()[0] == 0
        assert restarted.pipeline.startup_cleanup_result["abandoned_prepared"] == 1
        assert restarted.pipeline.startup_cleanup_result["removed_orphans"] == 1
    finally:
        restarted.conn.close()


def test_v7_region_commit_has_one_observable_transaction(tmp_path):
    core, _page_id, region_id = _new_workspace(tmp_path)
    reader = None
    try:
        before = _region_snapshot(core, region_id)
        run, step, _unit, result = _prepare_ocr(core, region_id)
        revision_id = result.revision_updates["region"]
        db_path = quote(str(core.database_path).replace("\\", "/"), safe="/:")
        reader = sqlite3.connect(f"file:///{db_path}?mode=ro", uri=True)
        reader.row_factory = sqlite3.Row
        reader.execute("PRAGMA query_only = ON")
        observed_at_commit = []
        trace = []

        def observe(statement: str):
            normalized = statement.strip().lower()
            trace.append(normalized)
            if normalized == "commit":
                row = reader.execute(
                    "SELECT text_json, current_revision_id FROM regions WHERE region_id = ?",
                    (region_id,),
                ).fetchone()
                observed_at_commit.append((row["text_json"], row["current_revision_id"]))

        core.conn.set_trace_callback(observe)
        outcome = _commit_ocr(core, step, result)
        core.conn.set_trace_callback(None)

        assert outcome.status == "committed"
        assert trace.count("commit") == 1
        insert_revision = next(i for i, sql in enumerate(trace) if "insert into region_revisions" in sql)
        update_live = next(i for i, sql in enumerate(trace) if "update regions set text_json" in sql)
        resolve_candidate = next(
            i for i, sql in enumerate(trace)
            if "update step_result_candidates set status = 'resolved'" in sql
        )
        commit_index = trace.index("commit")
        assert insert_revision < update_live < resolve_candidate < commit_index
        assert observed_at_commit == [before[:2]]
        after = reader.execute(
            "SELECT text_json, current_revision_id FROM regions WHERE region_id = ?",
            (region_id,),
        ).fetchone()
        assert after["current_revision_id"] == revision_id
        assert after["text_json"] != before[0]
    finally:
        if reader is not None:
            reader.close()
        core.conn.set_trace_callback(None)
        core.conn.close()


def test_v8_concurrent_same_region_has_one_winner_and_one_abandoned_candidate(tmp_path):
    core, _page_id, region_id = _new_workspace(tmp_path)
    try:
        run_a, step_a, _unit_a, result_a = _prepare_ocr(core, region_id)
        run_b, step_b, _unit_b, result_b = _prepare_ocr(core, region_id)
        token_a = result_a.revision_updates["region"]
        token_b = result_b.revision_updates["region"]
        assert _region_snapshot(core, region_id)[1] == step_a.input_refs["region"]

        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [
                pool.submit(core.pipeline.commit_step_result, step_a.step_run_id, result_a),
                pool.submit(core.pipeline.commit_step_result, step_b.step_run_id, result_b),
            ]
            outcomes = [future.result(timeout=20) for future in futures]

        assert sorted(outcome.status for outcome in outcomes) == ["candidate", "committed"]
        rows = [_candidate(core, token_a), _candidate(core, token_b)]
        assert sorted(row["status"] for row in rows) == ["abandoned", "resolved"]
        assert sum(row["resolved_at"] is not None for row in rows) == 2
        assert _region_snapshot(core, region_id)[2] == 2
    finally:
        core.conn.close()


def test_artifact_candidate_fails_closed_without_storage_adapter(tmp_path):
    core, page_id, region_id = _new_workspace(tmp_path)
    try:
        _run, step, _unit, result = _prepare_segment(core, region_id)
        candidate_id = result.revision_updates["mask"]
        payload = json.loads(_candidate(core, candidate_id)["payload_json"])
        temp_path = Path(payload["temp_handle"])
        before_region = _region_snapshot(core, region_id)
        core.pipeline._catalog._storage = None

        outcome = core.pipeline.commit_step_result(step.step_run_id, result)

        assert outcome.status == "failed"
        assert outcome.error_code == "DB_FAILED"
        assert _region_snapshot(core, region_id) == before_region
        assert _candidate(core, candidate_id)["status"] == "abandoned"
        assert core.conn.execute(
            "SELECT COUNT(*) FROM media_artifacts WHERE page_id = ?", (page_id,)
        ).fetchone()[0] == 0
        assert temp_path.exists()
        assert str(temp_path) in core.pipeline._catalog.orphaned_paths

        # A later production startup sweep receives the storage adapter and
        # safely removes the retained temp handle.
        core.pipeline._catalog._storage = core.storage
        cleanup = core.pipeline._catalog.cleanup_staged_candidates()
        assert not temp_path.exists()
        assert cleanup["discarded_temps"] == 1
    finally:
        core.conn.close()


def test_v9_artifact_failure_is_invisible_and_success_publishes_consistently(tmp_path):
    core, page_id, region_id = _new_workspace(tmp_path)
    try:
        failed_run, failed_step, _failed_unit, failed_result = _prepare_segment(core, region_id)
        before_region = _region_snapshot(core, region_id)
        failed_id = failed_result.revision_updates["mask"]
        failed_payload = json.loads(_candidate(core, failed_id)["payload_json"])
        assert {
            "temp_handle", "relative_path", "artifact_type", "page_id",
            "book_id", "chapter_id", "base_revision_id", "sha256",
            "size", "mime_type", "content_format",
        } <= set(failed_payload)
        assert "revision_no" not in failed_payload
        assert core.conn.execute(
            "SELECT COUNT(*) FROM media_artifacts WHERE page_id = ?", (page_id,)
        ).fetchone()[0] == 0
        failed_temp = Path(failed_payload["temp_handle"])
        assert failed_temp.exists()
        failed_final = Path(core.storage.absolute_path(failed_payload["relative_path"]))
        real_publish = core.storage.publish

        def fail_before_publish(_temp_handle, _relative_path):
            raise OSError("injected publish failure")

        core.storage.publish = fail_before_publish
        try:
            failed = core.pipeline.commit_step_result(failed_step.step_run_id, failed_result)
        finally:
            core.storage.publish = real_publish

        assert failed.status == "failed"
        assert failed.error_code == "DB_FAILED"
        assert _region_snapshot(core, region_id) == before_region
        assert core.conn.execute(
            "SELECT COUNT(*) FROM media_artifacts WHERE page_id = ? AND artifact_type = 'mask'",
            (page_id,),
        ).fetchone()[0] == 0
        assert core.conn.execute("SELECT COUNT(*) FROM artifact_revisions").fetchone()[0] == 0
        assert not failed_temp.exists()
        assert not failed_final.exists()
        assert core.pipeline._catalog.orphaned_paths == []

        run, step, _unit, result = _prepare_segment(core, region_id)
        candidate_id = result.revision_updates["mask"]
        candidate_payload = json.loads(_candidate(core, candidate_id)["payload_json"])
        assert Path(candidate_payload["temp_handle"]).exists()
        assert not Path(core.storage.absolute_path(candidate_payload["relative_path"])).exists()
        trace = []
        core.conn.set_trace_callback(lambda statement: trace.append(statement.strip().lower()))
        real_publish = core.storage.publish

        def trace_publish(temp_handle, relative_path):
            assert core.conn.in_transaction
            assert _candidate(core, candidate_id)["status"] == "resolved"
            trace.append("storage.publish")
            return real_publish(temp_handle, relative_path)

        core.storage.publish = trace_publish
        try:
            success = core.pipeline.commit_step_result(step.step_run_id, result)
        finally:
            core.storage.publish = real_publish
            core.conn.set_trace_callback(None)
        assert success.status == "committed"
        positions = {
            "begin": trace.index("begin immediate"),
            "artifact": next(i for i, sql in enumerate(trace) if "insert into media_artifacts" in sql),
            "revision": next(i for i, sql in enumerate(trace) if "insert into artifact_revisions" in sql),
            "pointer": next(i for i, sql in enumerate(trace) if "update media_artifacts set current_revision_id" in sql),
            "stage": next(i for i, sql in enumerate(trace) if "insert into pipeline_stage_states" in sql),
            "resolved": next(i for i, sql in enumerate(trace) if "update step_result_candidates set status = 'resolved'" in sql),
            "publish": trace.index("storage.publish"),
            "commit": trace.index("commit"),
        }
        assert list(positions.values()) == sorted(positions.values())

        artifact = core.conn.execute(
            "SELECT artifact_id, current_revision_id FROM media_artifacts"
            " WHERE page_id = ? AND artifact_type = 'mask'",
            (page_id,),
        ).fetchone()
        revision = core.conn.execute(
            "SELECT managed_path, file_hash, size_bytes, mime_type, revision_no"
            " FROM artifact_revisions WHERE artifact_revision_id = ?",
            (candidate_id,),
        ).fetchone()
        final_path = Path(core.storage.absolute_path(revision["managed_path"]))
        file_bytes = final_path.read_bytes()
        assert artifact["current_revision_id"] == candidate_id
        assert revision["managed_path"] == candidate_payload["relative_path"]
        assert revision["file_hash"] == hashlib.sha256(file_bytes).hexdigest()
        assert revision["size_bytes"] == len(file_bytes)
        assert revision["mime_type"] == "application/x-newmanga-mask"
        assert revision["revision_no"] == 1
        assert _candidate(core, candidate_id)["status"] == "resolved"
        assert not Path(candidate_payload["temp_handle"]).exists()
    finally:
        core.conn.close()
