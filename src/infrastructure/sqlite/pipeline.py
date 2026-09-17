"""Production SQLite adapters for the TASK-013 pipeline seam."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping

from application.tasks.store import (
    CatalogCommit,
    FrozenRunSnapshots,
    PipelineStore,
    SnapshotProvider,
    TargetCatalog,
    _merge,
)
from domain.regions.entities import SfxPolicy
from domain.tasks.models import (
    CommandType,
    LockSnapshot,
    PipelineError,
    PipelineRun,
    PipelineRunStatus,
    PipelineScope,
    PipelineTask,
    PipelineTaskStatus,
    PlanDecision,
    PlanUnit,
    RegionSnapshot,
    RunTarget,
    ScopeType,
    StageState,
    StepResultCandidate,
    StepRun,
    StepRunStatus,
    TargetSnapshot,
    TargetType,
    freeze_snapshot,
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def _plain(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Mapping):
        return {str(key): _plain(item) for key, item in value.items()}
    if isinstance(value, (tuple, list, set, frozenset)):
        return [_plain(item) for item in value]
    return value


def _dump(value: Any) -> str:
    return json.dumps(_plain(value), ensure_ascii=False, sort_keys=True)


def _load(value: str) -> Any:
    return json.loads(value)


def _lock_dict(lock: LockSnapshot) -> dict[str, bool]:
    return {
        "page_locked": lock.page_locked,
        "region_locked": lock.region_locked,
        "translation_locked": lock.translation_locked,
        "inpaint_locked": lock.inpaint_locked,
    }


def _lock(value: Mapping[str, Any]) -> LockSnapshot:
    return LockSnapshot(
        page_locked=bool(value.get("page_locked", False)),
        region_locked=bool(value.get("region_locked", False)),
        translation_locked=bool(value.get("translation_locked", False)),
        inpaint_locked=bool(value.get("inpaint_locked", False)),
    )


def _region_dict(region: RegionSnapshot) -> dict[str, Any]:
    return {
        "region_id": region.region_id,
        "page_id": region.page_id,
        "region_type": region.region_type,
        "sfx_policy": region.sfx_policy,
        "lock": _lock_dict(region.lock),
        "manual_edited": region.manual_edited,
        "final_confirmed": region.final_confirmed,
        "current_revisions": region.current_revisions,
        "stage_states": region.stage_states,
        "metadata": region.metadata,
    }


def _region(value: Mapping[str, Any]) -> RegionSnapshot:
    return RegionSnapshot(
        region_id=value["region_id"],
        page_id=value["page_id"],
        region_type=value.get("region_type", "speech"),
        # TASK-032 AC ③: the snapshot default must agree with the entity and
        # the Schema default (``SfxPolicy.SKIP``, D03 §7). It used to be
        # ``"translate"``, so a stored snapshot without the field flipped an
        # SFX region into the translation chain.
        sfx_policy=value.get("sfx_policy", SfxPolicy.SKIP.value),
        lock=_lock(value.get("lock", {})),
        manual_edited=bool(value.get("manual_edited", False)),
        final_confirmed=bool(value.get("final_confirmed", False)),
        current_revisions=value.get("current_revisions", {}),
        stage_states=value.get("stage_states", {}),
        metadata=value.get("metadata", {}),
    )


def _target_dict(target: TargetSnapshot) -> dict[str, Any]:
    return {
        "target_id": target.target_id,
        "page_id": target.page_id,
        "target_type": target.target_type,
        "page_order": target.page_order,
        "book_id": target.book_id,
        "chapter_id": target.chapter_id,
        "region_id": target.region_id,
        "lock": _lock_dict(target.lock),
        "manual_edited": target.manual_edited,
        "final_confirmed": target.final_confirmed,
        "current_revisions": target.current_revisions,
        "stage_states": target.stage_states,
        "regions": [_region_dict(item) for item in target.regions],
        "metadata": target.metadata,
        "deleted": target.deleted,
    }


def _target(value: Mapping[str, Any]) -> TargetSnapshot:
    return TargetSnapshot(
        target_id=value["target_id"],
        page_id=value["page_id"],
        target_type=value["target_type"],
        page_order=int(value.get("page_order", 0)),
        book_id=value.get("book_id"),
        chapter_id=value.get("chapter_id"),
        region_id=value.get("region_id"),
        lock=_lock(value.get("lock", {})),
        manual_edited=bool(value.get("manual_edited", False)),
        final_confirmed=bool(value.get("final_confirmed", False)),
        current_revisions=value.get("current_revisions", {}),
        stage_states=value.get("stage_states", {}),
        regions=tuple(_region(item) for item in value.get("regions", [])),
        metadata=value.get("metadata", {}),
        deleted=bool(value.get("deleted", False)),
    )


def _scope_dict(scope: PipelineScope) -> dict[str, Any]:
    return {
        "scope_type": scope.scope_type,
        "selected_ids": scope.selected_ids,
        "book_id": scope.book_id,
        "chapter_id": scope.chapter_id,
    }


def _scope(value: Mapping[str, Any]) -> PipelineScope:
    return PipelineScope(
        value["scope_type"],
        selected_ids=tuple(value.get("selected_ids", ())),
        book_id=value.get("book_id"),
        chapter_id=value.get("chapter_id"),
    )


def _unit_dict(unit: PlanUnit) -> dict[str, Any]:
    return {
        "unit_id": unit.unit_id,
        "task_id": unit.task_id,
        "target_id": unit.target_id,
        "page_id": unit.page_id,
        "region_id": unit.region_id,
        "step_type": unit.step_type,
        "decision": unit.decision,
        "reason": unit.reason,
        "expected_revisions": unit.expected_revisions,
        "expected_lock": _lock_dict(unit.expected_lock),
    }


def _unit(value: Mapping[str, Any]) -> PlanUnit:
    return PlanUnit(
        unit_id=value["unit_id"],
        task_id=value["task_id"],
        target_id=value["target_id"],
        page_id=value["page_id"],
        region_id=value.get("region_id"),
        step_type=value["step_type"],
        decision=PlanDecision(value["decision"]),
        reason=value.get("reason"),
        expected_revisions=value.get("expected_revisions", {}),
        expected_lock=_lock(value.get("expected_lock", {})),
    )


def _run_target_dict(target: RunTarget) -> dict[str, Any]:
    return {
        "run_target_id": target.run_target_id,
        "target_id": target.target_id,
        "target_type": target.target_type,
        "page_id": target.page_id,
        "region_id": target.region_id,
        "target_order": target.target_order,
        "snapshot": _target_dict(target.snapshot),
    }


def _run_target(value: Mapping[str, Any]) -> RunTarget:
    return RunTarget(
        run_target_id=value["run_target_id"],
        target_id=value["target_id"],
        target_type=TargetType(value["target_type"]),
        page_id=value["page_id"],
        region_id=value.get("region_id"),
        target_order=int(value["target_order"]),
        snapshot=_target(value["snapshot"]),
    )


def _task_dict(task: PipelineTask) -> dict[str, Any]:
    return {
        "task_id": task.task_id,
        "run_target_id": task.run_target_id,
        "target_id": task.target_id,
        "target_type": task.target_type,
        "page_id": task.page_id,
        "region_id": task.region_id,
        "status": task.status,
        "units": [_unit_dict(unit) for unit in task.units],
        "step_run_ids": task.step_run_ids,
        "error_code": task.error_code,
        "error_detail": task.error_detail,
    }


def _task(value: Mapping[str, Any]) -> PipelineTask:
    return PipelineTask(
        task_id=value["task_id"],
        run_target_id=value["run_target_id"],
        target_id=value["target_id"],
        target_type=TargetType(value["target_type"]),
        page_id=value["page_id"],
        region_id=value.get("region_id"),
        status=PipelineTaskStatus(value.get("status", PipelineTaskStatus.PENDING)),
        units=tuple(_unit(item) for item in value.get("units", [])),
        step_run_ids=list(value.get("step_run_ids", [])),
        error_code=value.get("error_code"),
        error_detail=value.get("error_detail"),
    )


def _step_dict(step: StepRun) -> dict[str, Any]:
    return {
        "step_run_id": step.step_run_id,
        "task_id": step.task_id,
        "target_id": step.target_id,
        "page_id": step.page_id,
        "region_id": step.region_id,
        "step_type": step.step_type,
        "unit_id": step.unit_id,
        "status": step.status,
        "input_refs": step.input_refs,
        "lock_snapshot": _lock_dict(step.lock_snapshot),
        "retry_no": step.retry_no,
        "error_code": step.error_code,
        "error_detail": step.error_detail,
        "output": step.output,
    }


def _step(value: Mapping[str, Any]) -> StepRun:
    return StepRun(
        step_run_id=value["step_run_id"],
        task_id=value["task_id"],
        target_id=value["target_id"],
        page_id=value["page_id"],
        region_id=value.get("region_id"),
        step_type=value["step_type"],
        unit_id=value.get("unit_id", ""),
        status=StepRunStatus(value.get("status", StepRunStatus.PENDING)),
        input_refs=value.get("input_refs", {}),
        lock_snapshot=_lock(value.get("lock_snapshot", {})),
        retry_no=int(value.get("retry_no", 0)),
        error_code=value.get("error_code"),
        error_detail=value.get("error_detail"),
        output=value.get("output", {}),
    )


def _candidate_dict(candidate: StepResultCandidate) -> dict[str, Any]:
    return {
        "candidate_id": candidate.candidate_id,
        "step_run_id": candidate.step_run_id,
        "target_id": candidate.target_id,
        "page_id": candidate.page_id,
        "region_id": candidate.region_id,
        "result_kind": candidate.result_kind,
        "base_revision_id": candidate.base_revision_id,
        "payload": candidate.payload,
        "reason": candidate.reason,
        "status": candidate.status,
    }


def _candidate(value: Mapping[str, Any]) -> StepResultCandidate:
    return StepResultCandidate(
        candidate_id=value["candidate_id"],
        step_run_id=value["step_run_id"],
        target_id=value["target_id"],
        page_id=value["page_id"],
        region_id=value.get("region_id"),
        result_kind=value["result_kind"],
        base_revision_id=value.get("base_revision_id"),
        payload=value.get("payload", {}),
        reason=value["reason"],
        status=value.get("status", "pending"),
    )


def _run_dict(run: PipelineRun) -> dict[str, Any]:
    return {
        "run_id": run.run_id,
        "command_type": run.command_type,
        "scope": _scope_dict(run.scope),
        "requested_targets": run.requested_targets,
        "targets": [_run_target_dict(item) for item in run.targets],
        "settings_snapshot": run.settings_snapshot,
        "provider_binding_snapshot": run.provider_binding_snapshot,
        "constraint_snapshot_ref": run.constraint_snapshot_ref,
        "context_policy": run.context_policy,
        "status": run.status,
        "tasks": [_task_dict(item) for item in run.tasks],
        "step_runs": [_step_dict(item) for item in run.step_runs],
        "candidates": [_candidate_dict(item) for item in run.candidates],
        "planned_step_units": run.planned_step_units,
        "terminal_step_units": run.terminal_step_units,
        "terminal_unit_ids": sorted(run.terminal_unit_ids),
        "pause_requested": run.pause_requested,
        "cancel_requested": run.cancel_requested,
        "source_run_id": run.source_run_id,
        "retry_reason": run.retry_reason,
        "interruption_disposition": run.interruption_disposition,
        "termination_reason": run.termination_reason,
        "fatal_error": run.fatal_error,
    }


def _run(value: Mapping[str, Any]) -> PipelineRun:
    return PipelineRun(
        run_id=value["run_id"],
        command_type=CommandType(value["command_type"]),
        scope=_scope(value["scope"]),
        requested_targets=tuple(value.get("requested_targets", [])),
        targets=tuple(_run_target(item) for item in value.get("targets", [])),
        settings_snapshot=value.get("settings_snapshot", {}),
        provider_binding_snapshot=value.get("provider_binding_snapshot", {}),
        constraint_snapshot_ref=value.get("constraint_snapshot_ref"),
        context_policy=value.get("context_policy", {}),
        status=PipelineRunStatus(value.get("status", PipelineRunStatus.PENDING)),
        tasks=[_task(item) for item in value.get("tasks", [])],
        step_runs=[_step(item) for item in value.get("step_runs", [])],
        candidates=[_candidate(item) for item in value.get("candidates", [])],
        planned_step_units=int(value.get("planned_step_units", 0)),
        terminal_step_units=int(value.get("terminal_step_units", 0)),
        terminal_unit_ids=set(value.get("terminal_unit_ids", [])),
        pause_requested=bool(value.get("pause_requested", False)),
        cancel_requested=bool(value.get("cancel_requested", False)),
        source_run_id=value.get("source_run_id"),
        retry_reason=value.get("retry_reason"),
        interruption_disposition=value.get("interruption_disposition"),
        termination_reason=value.get("termination_reason"),
        fatal_error=value.get("fatal_error"),
    )


class SqlitePipelineStore(PipelineStore):
    """Durable PipelineRun store over the v3 execution graph."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn
        self._cache: dict[str, PipelineRun] = {}

    def put(self, run_id: str, run: PipelineRun) -> None:
        if run_id != run.run_id:
            raise ValueError("run_id must match PipelineRun.run_id")
        value = _run_dict(run)
        now = _now()
        with self._conn:
            self._conn.execute("DELETE FROM pipeline_runs WHERE run_id = ?", (run_id,))
            self._conn.execute(
                "INSERT INTO pipeline_runs (run_id, command_type, scope_type,"
                " requested_targets_json, settings_snapshot_json,"
                " provider_binding_snapshot_json, constraint_snapshot_ref,"
                " context_policy_json, status, planned_step_units,"
                " terminal_step_units, pause_requested, cancel_requested,"
                " source_run_id, retry_reason, interruption_disposition,"
                " termination_reason, fatal_error, run_json, updated_at)"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    run.run_id,
                    run.command_type.value,
                    run.scope.scope_type.value,
                    _dump(run.requested_targets),
                    _dump(run.settings_snapshot),
                    _dump(run.provider_binding_snapshot),
                    run.constraint_snapshot_ref,
                    _dump(run.context_policy),
                    run.status.value,
                    run.planned_step_units,
                    run.terminal_step_units,
                    int(run.pause_requested),
                    int(run.cancel_requested),
                    run.source_run_id,
                    run.retry_reason,
                    run.interruption_disposition,
                    run.termination_reason,
                    run.fatal_error,
                    _dump(value),
                    now,
                ),
            )
            for target in run.targets:
                self._conn.execute(
                    "INSERT INTO pipeline_run_targets (run_target_id, pipeline_run_id,"
                    " target_id, target_type, page_id, region_id, target_order, snapshot_json)"
                    " VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        target.run_target_id, run.run_id, target.target_id,
                        target.target_type.value, target.page_id, target.region_id,
                        target.target_order, _dump(_target_dict(target.snapshot)),
                    ),
                )
            for task in run.tasks:
                self._conn.execute(
                    "INSERT INTO pipeline_tasks (task_id, pipeline_run_id, run_target_id,"
                    " target_id, target_type, page_id, region_id, status, units_json,"
                    " step_run_ids_json, error_code, error_detail)"
                    " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        task.task_id, run.run_id, task.run_target_id, task.target_id,
                        task.target_type.value, task.page_id, task.region_id,
                        task.status.value, _dump([_unit_dict(item) for item in task.units]),
                        _dump(task.step_run_ids), task.error_code, task.error_detail,
                    ),
                )
            for step in run.step_runs:
                self._conn.execute(
                    "INSERT INTO step_runs (step_run_id, pipeline_run_id, task_id,"
                    " target_id, page_id, region_id, step_type, unit_id, status,"
                    " input_refs_json, lock_snapshot_json, retry_no, error_code,"
                    " error_detail, output_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        step.step_run_id, run.run_id, step.task_id, step.target_id,
                        step.page_id, step.region_id, step.step_type, step.unit_id,
                        step.status.value, _dump(step.input_refs),
                        _dump(_lock_dict(step.lock_snapshot)), step.retry_no,
                        step.error_code, step.error_detail, _dump(step.output),
                    ),
                )
                for order, (key, revision_id) in enumerate(step.input_refs.items()):
                    self._conn.execute(
                        "INSERT INTO step_run_input_refs (step_run_id, input_order, ref_key, revision_id)"
                        " VALUES (?, ?, ?, ?)",
                        (step.step_run_id, order, key, revision_id),
                    )
                for order, (key, value) in enumerate(step.output.items()):
                    self._conn.execute(
                        "INSERT INTO step_run_output_refs (step_run_id, output_order, ref_key, value_json)"
                        " VALUES (?, ?, ?, ?)",
                        (step.step_run_id, order, key, _dump(value)),
                    )
            for candidate in run.candidates:
                self._conn.execute(
                    "INSERT INTO step_result_candidates (candidate_id, pipeline_run_id,"
                    " step_run_id, target_id, page_id, region_id, result_kind,"
                    " base_revision_id, payload_json, reason, status, created_at)"
                    " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        candidate.candidate_id, run.run_id, candidate.step_run_id,
                        candidate.target_id, candidate.page_id, candidate.region_id,
                        candidate.result_kind, candidate.base_revision_id,
                        _dump(candidate.payload), candidate.reason, candidate.status, now,
                    ),
                )
        self._cache[run_id] = run

    def get(self, run_id: str) -> PipelineRun | None:
        if run_id in self._cache:
            return self._cache[run_id]
        row = self._conn.execute(
            "SELECT run_json FROM pipeline_runs WHERE run_id = ?", (run_id,)
        ).fetchone()
        if row is None:
            return None
        run = _run(_load(row["run_json"]))
        self._cache[run_id] = run
        return run

    def list_ids(self) -> tuple[str, ...]:
        rows = self._conn.execute(
            "SELECT run_id FROM pipeline_runs ORDER BY updated_at, run_id"
        ).fetchall()
        return tuple(row["run_id"] for row in rows)


class SqliteTargetCatalog(TargetCatalog):
    """Real Book→Chapter→Page→Region target and optimistic commit adapter."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def expand(self, scope: PipelineScope) -> tuple[TargetSnapshot, ...]:
        kind = scope.scope_type.value
        if kind == ScopeType.REGION.value:
            if len(scope.selected_ids) != 1:
                raise PipelineError("EMPTY_TARGET_SELECTION", "region scope requires one region")
            return (self._region_or_error(scope.selected_ids[0]),)
        if kind == ScopeType.BOOK.value:
            book_id = scope.book_id or (scope.selected_ids[0] if scope.selected_ids else None)
            if not book_id:
                raise PipelineError("EMPTY_TARGET_SELECTION", "book_id is required")
            rows = self._conn.execute(
                "SELECT p.page_id FROM pages p JOIN chapters c ON c.chapter_id = p.chapter_id"
                " WHERE c.book_id = ? ORDER BY p.sort_order, p.page_id", (book_id,)
            ).fetchall()
        elif kind == ScopeType.CHAPTER.value:
            chapter_id = scope.chapter_id or (scope.selected_ids[0] if scope.selected_ids else None)
            if not chapter_id:
                raise PipelineError("EMPTY_TARGET_SELECTION", "chapter_id is required")
            rows = self._conn.execute(
                "SELECT page_id FROM pages WHERE chapter_id = ? ORDER BY sort_order, page_id",
                (chapter_id,),
            ).fetchall()
        elif kind in {ScopeType.PAGE.value, ScopeType.PAGE_SELECTION.value}:
            if not scope.selected_ids:
                raise PipelineError("EMPTY_TARGET_SELECTION", "page selection is empty")
            rows = [(page_id,) for page_id in scope.selected_ids]
        else:
            raise PipelineError("TARGET_NOT_FOUND", f"unsupported scope {scope.scope_type}")
        targets = []
        for row in rows:
            try:
                targets.append(self._page_or_error(row[0]))
            except PipelineError as error:
                if kind in {ScopeType.BOOK.value, ScopeType.CHAPTER.value} and error.code == "TARGET_DELETED":
                    continue
                raise
        if not targets:
            raise PipelineError("EMPTY_TARGET_SELECTION", "scope expands to no active pages")
        return tuple(sorted(targets, key=lambda item: (item.page_order, item.page_id)))

    def current(self, target_id: str) -> TargetSnapshot:
        region = self._conn.execute(
            "SELECT region_id FROM regions WHERE region_id = ?", (target_id,)
        ).fetchone()
        return self._region_or_error(target_id) if region else self._page_or_error(target_id)

    def commit_step(
        self,
        *,
        target_id: str,
        expected_revisions: Mapping[str, str | None],
        expected_lock: LockSnapshot,
        stage_updates: Mapping[str, StageState],
        revision_updates: Mapping[str, str],
    ) -> CatalogCommit:
        try:
            self._conn.execute("BEGIN IMMEDIATE")
            current = self.current(target_id)
            if any(current.current_revisions.get(key) != value for key, value in expected_revisions.items()):
                self._conn.rollback()
                return CatalogCommit("input_revision_changed", "current Revision changed")
            if current.lock != expected_lock:
                self._conn.rollback()
                return CatalogCommit("lock_changed", "current Lock changed")

            target_type = current.target_type.value
            if current.target_type is TargetType.REGION:
                if any(key != "region" for key in revision_updates):
                    self._conn.rollback()
                    return CatalogCommit("db_failed", "region revision key must be 'region'")
                if revision_updates:
                    cursor = self._conn.execute(
                        "UPDATE regions SET current_revision_id = ?, updated_at = ?"
                        " WHERE region_id = ? AND deleted_at IS NULL",
                        (revision_updates["region"], _now(), current.region_id),
                    )
                    if cursor.rowcount != 1:
                        self._conn.rollback()
                        return CatalogCommit("target_not_found", target_id)
            else:
                for artifact_type, revision_id in revision_updates.items():
                    cursor = self._conn.execute(
                        "UPDATE media_artifacts SET current_revision_id = ?, updated_at = ?"
                        " WHERE page_id = ? AND artifact_type = ?",
                        (revision_id, _now(), current.page_id, artifact_type),
                    )
                    if cursor.rowcount != 1:
                        self._conn.rollback()
                        return CatalogCommit("target_not_found", f"artifact {artifact_type}")

            for stage, state in stage_updates.items():
                self._conn.execute(
                    "INSERT INTO pipeline_stage_states (target_type, target_id, stage, status, updated_at)"
                    " VALUES (?, ?, ?, ?, ?) ON CONFLICT(target_type, target_id, stage) DO UPDATE SET"
                    " status = excluded.status, updated_at = excluded.updated_at",
                    (target_type, target_id, stage, StageState(state).value, _now()),
                )
            self._conn.commit()
            return CatalogCommit("applied")
        except Exception as error:
            self._conn.rollback()
            return CatalogCommit("db_failed", repr(error))

    def _page_or_error(self, page_id: str) -> TargetSnapshot:
        row = self._conn.execute(
            "SELECT p.page_id, p.chapter_id, p.sort_order, p.page_locked, p.deleted_at,"
            " p.source_filename, p.source_hash, p.managed_original_ref, c.book_id"
            " FROM pages p JOIN chapters c ON c.chapter_id = p.chapter_id"
            " JOIN books b ON b.book_id = c.book_id WHERE p.page_id = ?"
            " AND c.deleted_at IS NULL AND b.deleted_at IS NULL",
            (page_id,),
        ).fetchone()
        if row is None:
            raise PipelineError("TARGET_NOT_FOUND", page_id)
        if row["deleted_at"] is not None:
            raise PipelineError("TARGET_DELETED", page_id)
        if row["source_hash"] is None or row["managed_original_ref"] is None:
            raise PipelineError("TARGET_NOT_FOUND", f"page {page_id} has no managed original")
        regions = tuple(
            self._region_from_id(item["region_id"])
            for item in self._conn.execute(
                "SELECT region_id FROM regions WHERE page_id = ? AND deleted_at IS NULL"
                " ORDER BY reading_order, region_id", (page_id,)
            ).fetchall()
        )
        return TargetSnapshot(
            target_id=page_id,
            page_id=page_id,
            target_type=TargetType.PAGE,
            page_order=row["sort_order"],
            book_id=row["book_id"],
            chapter_id=row["chapter_id"],
            lock=LockSnapshot(page_locked=bool(row["page_locked"])),
            current_revisions=self._page_revisions(page_id),
            stage_states=self._stage_states("page", page_id),
            regions=regions,
            metadata={
                "source_filename": row["source_filename"],
                "managed_original_ref": row["managed_original_ref"],
            },
        )

    def _region_or_error(self, region_id: str) -> TargetSnapshot:
        row = self._conn.execute(
            "SELECT r.region_id, r.page_id, r.deleted_at, p.chapter_id, p.sort_order,"
            " p.page_locked, c.book_id FROM regions r JOIN pages p ON p.page_id = r.page_id"
            " JOIN chapters c ON c.chapter_id = p.chapter_id JOIN books b ON b.book_id = c.book_id"
            " WHERE r.region_id = ? AND p.deleted_at IS NULL AND c.deleted_at IS NULL"
            " AND b.deleted_at IS NULL AND p.source_hash IS NOT NULL"
            " AND p.managed_original_ref IS NOT NULL AND p.width IS NOT NULL AND p.height IS NOT NULL",
            (region_id,),
        ).fetchone()
        if row is None:
            raise PipelineError("TARGET_NOT_FOUND", region_id)
        if row["deleted_at"] is not None or self._page_deleted(row["page_id"]):
            raise PipelineError("TARGET_DELETED", region_id)
        region = self._region_from_id(region_id)
        return TargetSnapshot(
            target_id=region_id,
            page_id=row["page_id"],
            target_type=TargetType.REGION,
            page_order=row["sort_order"],
            book_id=row["book_id"],
            chapter_id=row["chapter_id"],
            region_id=region_id,
            lock=LockSnapshot(
                page_locked=bool(row["page_locked"]),
                region_locked=region.lock.region_locked,
                translation_locked=region.lock.translation_locked,
                inpaint_locked=region.lock.inpaint_locked,
            ),
            manual_edited=region.manual_edited,
            final_confirmed=region.final_confirmed,
            current_revisions=region.current_revisions,
            stage_states=region.stage_states,
            regions=(region,),
            metadata=region.metadata,
        )

    def _region_from_id(self, region_id: str) -> RegionSnapshot:
        row = self._conn.execute(
            "SELECT region_id, page_id, region_type, sfx_policy, region_locked,"
            " translation_locked, inpaint_locked, current_revision_id, text_json"
            " FROM regions WHERE region_id = ? AND deleted_at IS NULL", (region_id,)
        ).fetchone()
        if row is None:
            raise PipelineError("TARGET_NOT_FOUND", region_id)
        text = json.loads(row["text_json"])
        return RegionSnapshot(
            region_id=row["region_id"],
            page_id=row["page_id"],
            region_type=row["region_type"],
            sfx_policy=row["sfx_policy"],
            lock=LockSnapshot(
                region_locked=bool(row["region_locked"]),
                translation_locked=bool(row["translation_locked"]),
                inpaint_locked=bool(row["inpaint_locked"]),
            ),
            manual_edited=bool(text.get("manual_edited", False)),
            final_confirmed=bool(text.get("edited_confirmed", False)),
            current_revisions={"region": row["current_revision_id"]},
            stage_states=self._stage_states("region", region_id),
            metadata={"final_source": text.get("final_source")},
        )

    def _page_deleted(self, page_id: str) -> bool:
        row = self._conn.execute(
            "SELECT deleted_at FROM pages WHERE page_id = ?", (page_id,)
        ).fetchone()
        return row is None or row["deleted_at"] is not None

    def _page_revisions(self, page_id: str) -> dict[str, str | None]:
        rows = self._conn.execute(
            "SELECT artifact_type, current_revision_id FROM media_artifacts WHERE page_id = ?",
            (page_id,),
        ).fetchall()
        return {row["artifact_type"]: row["current_revision_id"] for row in rows}

    def _stage_states(self, target_type: str, target_id: str) -> dict[str, StageState]:
        rows = self._conn.execute(
            "SELECT stage, status FROM pipeline_stage_states WHERE target_type = ? AND target_id = ?",
            (target_type, target_id),
        ).fetchall()
        return {row["stage"]: StageState(row["status"]) for row in rows}


_SENSITIVE_PARTS = ("secret", "password", "token", "api_key", "apikey")


def _redact(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {
            str(key): _redact(item)
            for key, item in value.items()
            if not any(part in str(key).lower() for part in _SENSITIVE_PARTS)
        }
    if isinstance(value, (tuple, list)):
        return [_redact(item) for item in value]
    return value


class SqliteSnapshotProvider(SnapshotProvider):
    """SQLite-backed defaults with recursive merge and secret omission."""

    def __init__(
        self,
        conn: sqlite3.Connection,
        *,
        settings: Mapping[str, Any] | None = None,
        provider_bindings: Mapping[str, Any] | None = None,
        constraint_snapshot_ref: str | None = None,
        context_policy: Mapping[str, Any] | None = None,
    ) -> None:
        self._conn = conn
        if any(item is not None for item in (settings, provider_bindings, constraint_snapshot_ref, context_policy)):
            self.set_defaults(
                settings=settings or {},
                provider_bindings=provider_bindings or {},
                constraint_snapshot_ref=constraint_snapshot_ref,
                context_policy=context_policy or {},
            )
        else:
            with self._conn:
                self._conn.execute(
                    "INSERT INTO pipeline_defaults (defaults_id, settings_json, provider_bindings_json,"
                    " constraint_snapshot_ref, context_policy_json, updated_at) VALUES (1, '{}', '{}', NULL, '{}', ?)"
                    " ON CONFLICT(defaults_id) DO NOTHING", (_now(),)
                )

    def set_defaults(
        self,
        *,
        settings: Mapping[str, Any],
        provider_bindings: Mapping[str, Any],
        constraint_snapshot_ref: str | None,
        context_policy: Mapping[str, Any],
    ) -> None:
        with self._conn:
            self._conn.execute(
                "INSERT INTO pipeline_defaults (defaults_id, settings_json, provider_bindings_json,"
                " constraint_snapshot_ref, context_policy_json, updated_at) VALUES (1, ?, ?, ?, ?, ?)"
                " ON CONFLICT(defaults_id) DO UPDATE SET settings_json = excluded.settings_json,"
                " provider_bindings_json = excluded.provider_bindings_json,"
                " constraint_snapshot_ref = excluded.constraint_snapshot_ref,"
                " context_policy_json = excluded.context_policy_json, updated_at = excluded.updated_at",
                (
                    _dump(_redact(settings)), _dump(_redact(provider_bindings)),
                    constraint_snapshot_ref, _dump(_redact(context_policy)), _now(),
                ),
            )

    def freeze(
        self,
        run_id: str,
        *,
        overrides: Mapping[str, Any] | None = None,
    ) -> FrozenRunSnapshots:
        del run_id
        row = self._conn.execute("SELECT * FROM pipeline_defaults WHERE defaults_id = 1").fetchone()
        if row is None:
            self.set_defaults(settings={}, provider_bindings={}, constraint_snapshot_ref=None, context_policy={})
            row = self._conn.execute("SELECT * FROM pipeline_defaults WHERE defaults_id = 1").fetchone()
        overrides = overrides or {}
        settings_overrides = overrides.get("settings")
        if settings_overrides is None:
            settings_overrides = {
                key: value
                for key, value in overrides.items()
                if key not in {"provider_bindings", "context_policy"}
            }
        settings = _merge(_load(row["settings_json"]), settings_overrides if isinstance(settings_overrides, Mapping) else {})
        providers = _merge(_load(row["provider_bindings_json"]), overrides.get("provider_bindings", {}))
        context = _merge(_load(row["context_policy_json"]), overrides.get("context_policy", {}))
        return FrozenRunSnapshots(
            settings=freeze_snapshot(_redact(settings)),
            provider_bindings=freeze_snapshot(_redact(providers)),
            constraint_snapshot_ref=row["constraint_snapshot_ref"],
            context_policy=freeze_snapshot(_redact(context)),
        )
