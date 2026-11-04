"""Production SQLite adapters for the TASK-013 pipeline seam."""

from __future__ import annotations

import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from enum import Enum
from dataclasses import replace
from contextlib import ExitStack
from typing import Any, Callable, Mapping

from application.tasks.store import (
    CatalogCommit,
    FrozenRunSnapshots,
    IdempotencyRecord,
    PipelineStore,
    SnapshotProvider,
    TargetCatalog,
    _merge,
)
from domain.regions.entities import SfxPolicy
from infrastructure.filesystem.integrity import integrity_of
from infrastructure.filesystem.managed_storage import ARTIFACT_TYPE_DIRS
from ports.repositories.storage import ManagedFileStoragePort
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
from application.tasks.store import snapshot_digest


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
        # RUN-STORE-CACHE-RACE-FIX-1 (AC2): per-Run write revision for the
        # ``run_json`` CAS. Only the cache-owner object may advance a Run; a
        # snapshot captured before a newer commit is rejected instead of
        # silently overwriting it (last-writer-wins).
        self._write_revision: dict[str, int] = {}
        with self._conn:
            self._conn.execute(
                "CREATE TABLE IF NOT EXISTS pipeline_run_idempotency ("
                "idempotency_key TEXT PRIMARY KEY, request_fingerprint TEXT NOT NULL, "
                "operation_type TEXT NOT NULL, run_id TEXT NOT NULL, created_at TEXT NOT NULL)"
            )

    def put(self, run_id: str, run: PipelineRun) -> None:
        if run_id != run.run_id:
            raise ValueError("run_id must match PipelineRun.run_id")
        self.put_many((run,))

    def write_in_current_transaction(self, run: PipelineRun) -> None:
        if not self._conn.in_transaction:
            raise RuntimeError("PipelineStore write requires the catalog transaction")
        self._write_run(run)
        self._cache[run.run_id] = run

    def put_many(self, runs) -> None:
        if not runs:
            return
        self._conn.execute("BEGIN IMMEDIATE")
        try:
            for run in runs:
                self._write_run(run)
            self._conn.commit()
        except BaseException:
            self._conn.rollback()
            raise
        self._cache.update((run.run_id, run) for run in runs)

    def _write_run(self, run: PipelineRun) -> None:
        revision = self._check_write_revision(run)
        value = _run_dict(run)
        now = _now()

        # step_result_candidates is the durable prepare/seam lifecycle truth.
        # Child graph rows are rebuilt below, so snapshot every candidate first;
        # deleting a step row cascades to its candidates.
        candidate_rows = [
            dict(row)
            for row in self._conn.execute(
                "SELECT candidate_id, pipeline_run_id, step_run_id, target_id, page_id,"
                " region_id, result_kind, base_revision_id, payload_json, reason, status,"
                " created_at, resolved_at FROM step_result_candidates"
                " WHERE pipeline_run_id = ? ORDER BY created_at, candidate_id",
                (run.run_id,),
            ).fetchall()
        ]

        self._conn.execute(
            "INSERT INTO pipeline_runs (run_id, command_type, scope_type,"
            " requested_targets_json, settings_snapshot_json,"
            " provider_binding_snapshot_json, constraint_snapshot_ref,"
            " context_policy_json, status, planned_step_units,"
            " terminal_step_units, pause_requested, cancel_requested,"
            " source_run_id, retry_reason, interruption_disposition,"
            " termination_reason, fatal_error, run_json, updated_at)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
            " ON CONFLICT(run_id) DO UPDATE SET"
            " command_type = excluded.command_type, scope_type = excluded.scope_type,"
            " requested_targets_json = excluded.requested_targets_json,"
            " settings_snapshot_json = excluded.settings_snapshot_json,"
            " provider_binding_snapshot_json = excluded.provider_binding_snapshot_json,"
            " constraint_snapshot_ref = excluded.constraint_snapshot_ref,"
            " context_policy_json = excluded.context_policy_json, status = excluded.status,"
            " planned_step_units = excluded.planned_step_units,"
            " terminal_step_units = excluded.terminal_step_units,"
            " pause_requested = excluded.pause_requested, cancel_requested = excluded.cancel_requested,"
            " source_run_id = excluded.source_run_id, retry_reason = excluded.retry_reason,"
            " interruption_disposition = excluded.interruption_disposition,"
            " termination_reason = excluded.termination_reason, fatal_error = excluded.fatal_error,"
            " run_json = excluded.run_json, updated_at = excluded.updated_at",
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

        # Rebuild only the graph beneath the UPSERTed parent. Candidate rows are
        # restored from the snapshot below, with run.candidates winning on IDs.
        self._conn.execute(
            "DELETE FROM pipeline_run_targets WHERE pipeline_run_id = ?", (run.run_id,)
        )
        self._conn.execute(
            "DELETE FROM pipeline_tasks WHERE pipeline_run_id = ?", (run.run_id,)
        )
        self._conn.execute(
            "DELETE FROM step_runs WHERE pipeline_run_id = ?", (run.run_id,)
        )
        self._conn.execute(
            "DELETE FROM step_result_candidates WHERE pipeline_run_id = ?", (run.run_id,)
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
                    task.target_type.value, task.page_id, task.region_id, task.status.value,
                    _dump([_unit_dict(item) for item in task.units]),
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
            for order, (key, output_value) in enumerate(step.output.items()):
                self._conn.execute(
                    "INSERT INTO step_run_output_refs (step_run_id, output_order, ref_key, value_json)"
                    " VALUES (?, ?, ?, ?)",
                    (step.step_run_id, order, key, _dump(output_value)),
                )

        candidates_by_id = {row["candidate_id"]: row for row in candidate_rows}
        for candidate in run.candidates:
            candidates_by_id[candidate.candidate_id] = {
                "candidate_id": candidate.candidate_id,
                "pipeline_run_id": run.run_id,
                "step_run_id": candidate.step_run_id,
                "target_id": candidate.target_id,
                "page_id": candidate.page_id,
                "region_id": candidate.region_id,
                "result_kind": candidate.result_kind,
                "base_revision_id": candidate.base_revision_id,
                "payload_json": _dump(candidate.payload),
                "reason": candidate.reason,
                "status": candidate.status,
                "created_at": now,
                "resolved_at": None,
            }
        for candidate in candidates_by_id.values():
            self._conn.execute(
                "INSERT INTO step_result_candidates (candidate_id, pipeline_run_id,"
                " step_run_id, target_id, page_id, region_id, result_kind,"
                " base_revision_id, payload_json, reason, status, created_at, resolved_at)"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    candidate["candidate_id"], candidate["pipeline_run_id"],
                    candidate["step_run_id"], candidate["target_id"],
                    candidate["page_id"], candidate["region_id"],
                    candidate["result_kind"], candidate["base_revision_id"],
                    candidate["payload_json"], candidate["reason"],
                    candidate["status"], candidate["created_at"],
                    candidate["resolved_at"],
                ),
            )
        self._write_revision[run.run_id] = revision + 1
        run._store_revision = revision + 1

    def get_idempotency(self, idempotency_key: str) -> IdempotencyRecord | None:
        row = self._conn.execute(
            "SELECT request_fingerprint, operation_type, run_id "
            "FROM pipeline_run_idempotency WHERE idempotency_key = ?",
            (idempotency_key,),
        ).fetchone()
        if row is None:
            return None
        return IdempotencyRecord(
            idempotency_key=idempotency_key,
            request_fingerprint=row["request_fingerprint"],
            operation_type=row["operation_type"],
            run_id=row["run_id"],
        )

    def accept(
        self, run: PipelineRun, *, idempotency_key: str,
        request_fingerprint: str, operation_type: str,
        validate: Callable[[], None] | None = None,
    ) -> tuple[PipelineRun, bool]:
        self._conn.execute("BEGIN IMMEDIATE")
        try:
            row = self._conn.execute(
                "SELECT request_fingerprint, run_id FROM pipeline_run_idempotency "
                "WHERE idempotency_key = ?", (idempotency_key,),
            ).fetchone()
            if row is not None:
                if row["request_fingerprint"] != request_fingerprint:
                    raise PipelineError(
                        "IDEMPOTENCY_KEY_REUSED", "idempotency key fingerprint differs"
                    )
                existing = self._read_run(row["run_id"])
                if existing is None:
                    raise PipelineError("TARGET_NOT_FOUND", "idempotent Run no longer exists")
                self._conn.commit()
                return existing, False
            if validate is not None:
                validate()
            self._write_run(run)
            self._conn.execute(
                "INSERT INTO pipeline_run_idempotency "
                "(idempotency_key, request_fingerprint, operation_type, run_id, created_at) "
                "VALUES (?, ?, ?, ?, ?)",
                (idempotency_key, request_fingerprint, operation_type, run.run_id, _now()),
            )
            self._conn.commit()
        except BaseException:
            self._conn.rollback()
            raise
        self._cache[run.run_id] = run
        return run, True

    def accept_restart(
        self, parent: PipelineRun, child: PipelineRun, *,
        idempotency_key: str | None, request_fingerprint: str | None,
    ) -> tuple[PipelineRun, bool]:
        self._conn.execute("BEGIN IMMEDIATE")
        try:
            if idempotency_key is not None:
                row = self._conn.execute(
                    "SELECT request_fingerprint, run_id FROM pipeline_run_idempotency "
                    "WHERE idempotency_key = ?", (idempotency_key,),
                ).fetchone()
                if row is not None:
                    if row["request_fingerprint"] != request_fingerprint:
                        raise PipelineError(
                            "IDEMPOTENCY_KEY_REUSED", "idempotency key fingerprint differs"
                        )
                    existing = self._read_run(row["run_id"])
                    if existing is None:
                        raise PipelineError("TARGET_NOT_FOUND", "idempotent Run no longer exists")
                    self._conn.commit()
                    return existing, False
            row = self._conn.execute(
                "SELECT status, interruption_disposition FROM pipeline_runs WHERE run_id = ?",
                (parent.run_id,),
            ).fetchone()
            if row is None:
                raise PipelineError("TARGET_NOT_FOUND", "restart source Run no longer exists")
            if row["status"] != PipelineRunStatus.INTERRUPTED.value or row["interruption_disposition"] is not None:
                raise PipelineError("INVALID_RUN_TRANSITION", "restart requires an undisposed interrupted run")
            self._write_run(parent)
            self._write_run(child)
            if idempotency_key is not None:
                self._conn.execute(
                    "INSERT INTO pipeline_run_idempotency "
                    "(idempotency_key, request_fingerprint, operation_type, run_id, created_at) "
                    "VALUES (?, ?, 'restart', ?, ?)",
                    (idempotency_key, request_fingerprint, child.run_id, _now()),
                )
            self._conn.commit()
        except BaseException:
            self._conn.rollback()
            raise
        self._cache[parent.run_id] = parent
        self._cache[child.run_id] = child
        return child, True

    def _adopt_revision(self, run: PipelineRun) -> PipelineRun:
        """Stamp a freshly loaded Run with the store's current write revision."""
        run._store_revision = self._write_revision.get(run.run_id, 0)
        return run

    def _check_write_revision(self, run: PipelineRun) -> int:
        """CAS precondition for ``run_json`` writes (RUN-STORE-CACHE-RACE-FIX-1 AC2).

        Returns the current store revision to bump on success. A Run object
        loaded through this store carries ``_store_revision`` from the moment it
        was read; if the store has committed a newer revision since then, the
        snapshot is stale and must not overwrite the newer committed state.
        """
        current = self._write_revision.get(run.run_id, 0)
        snapshot = getattr(run, "_store_revision", None)
        if snapshot is None:
            # In-process Run object built for its very first write (create_run).
            snapshot = current
        if snapshot != current:
            raise PipelineError(
                "STALE_RUN_SNAPSHOT",
                f"run {run.run_id} snapshot revision {snapshot} is older than "
                f"store revision {current}",
            )
        return current

    def _read_run(self, run_id: str) -> PipelineRun | None:
        row = self._conn.execute(
            "SELECT run_json FROM pipeline_runs WHERE run_id = ?", (run_id,)
        ).fetchone()
        if row is None:
            return None
        return self._adopt_revision(_run(_load(row["run_json"])))

    def get(self, run_id: str) -> PipelineRun | None:
        if run_id in self._cache:
            return self._cache[run_id]
        run = self._read_run(run_id)
        if run is not None:
            self._cache[run_id] = run
        return run

    def refresh(self, run_id: str) -> PipelineRun | None:
        """Read durable state as a detached *view*; never touch the execution cache.

        RUN-STORE-CACHE-RACE-FIX-1 (AC1). ``refresh`` backs
        ``get_run_snapshot(fresh=True)`` / ``GetTaskProjection``. Replacing
        ``self._cache[run_id]`` here used to split the mutable Run graph between
        the request thread and the scheduler thread: commits + detect-region
        backfill landed on the clone, the executor kept the regionless units
        (``INVALID_INPUT``) and the stale object's ``_persist`` reverted committed
        StepRuns to ``running``. The returned object is a detached clone; only
        ``get()``/``put()`` may own the execution cache entry.
        """
        return self._read_run(run_id)

    def list_ids(self) -> tuple[str, ...]:
        rows = self._conn.execute(
            "SELECT run_id FROM pipeline_runs ORDER BY updated_at, run_id"
        ).fetchall()
        return tuple(row["run_id"] for row in rows)


class SqliteTargetCatalog(TargetCatalog):
    """Real Book→Chapter→Page→Region target and optimistic commit adapter."""

    def __init__(
        self, conn: sqlite3.Connection, storage: ManagedFileStoragePort | None = None
    ) -> None:
        self._conn = conn
        self._storage = storage
        self.orphaned_paths: list[str] = []

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
        persist: Callable[[], None] | None = None,
        run_id: str | None = None,
        step_run_id: str | None = None,
        pause_requested: bool = False,
        cancel_requested: bool = False,
    ) -> CatalogCommit:
        candidates: dict[str, dict[str, Any]] = {}
        published_paths: list[str] = []
        leases = ExitStack()
        try:
            self._conn.execute("BEGIN IMMEDIATE")
            # Resolve candidate rows before target lookup so a deleted/missing
            # target still abandons and cleans every prepared token supplied
            # by this step.
            for token in dict.fromkeys(revision_updates.values()):
                if run_id is None or step_run_id is None:
                    row = self._conn.execute(
                        "SELECT candidate_id, pipeline_run_id, step_run_id, target_id, page_id,"
                        " region_id, result_kind, base_revision_id, payload_json, reason, status,"
                        " created_at, resolved_at FROM step_result_candidates WHERE candidate_id = ?",
                        (token,),
                    ).fetchone()
                else:
                    row = self._conn.execute(
                        "SELECT candidate_id, pipeline_run_id, step_run_id, target_id, page_id,"
                        " region_id, result_kind, base_revision_id, payload_json, reason, status,"
                        " created_at, resolved_at FROM step_result_candidates"
                        " WHERE candidate_id = ? AND pipeline_run_id = ? AND step_run_id = ?",
                        (token, run_id, step_run_id),
                    ).fetchone()
                if row is not None:
                    candidates[token] = dict(row)
            current = self.current(target_id)
            if callable(getattr(self, "source_commit_guard", None)):
                leases.enter_context(self.source_commit_guard(current.page_id))
            target_type = current.target_type.value
            if target_type not in {TargetType.REGION.value, TargetType.PAGE.value}:
                return self._reject_prepared(
                    "db_failed", f"unsupported target type: {target_type}", candidates.values()
                )

            if target_type == TargetType.REGION.value:
                allowed_keys = {"region", *ARTIFACT_TYPE_DIRS}
            else:
                allowed_keys = set(ARTIFACT_TYPE_DIRS)

            if any(key not in allowed_keys for key in revision_updates):
                return self._reject_prepared(
                    "db_failed", f"invalid revision key for {target_type} target", candidates.values()
                )

            for key, token in revision_updates.items():
                candidate = candidates.get(token)
                if candidate is None:
                    return self._reject_prepared(
                        "db_failed", f"prepared candidate {token!r} was not found", candidates.values()
                    )
                if candidate["status"] != "prepared":
                    return self._reject_prepared(
                        "db_failed", f"candidate {token!r} is not prepared", candidates.values()
                    )
                try:
                    candidate["payload"] = json.loads(candidate["payload_json"])
                except (TypeError, json.JSONDecodeError) as error:
                    return self._reject_prepared(
                        "db_failed", f"candidate {token!r} payload is invalid: {error}", candidates.values()
                    )
                if candidate["result_kind"] != key:
                    return self._reject_prepared(
                        "db_failed", f"candidate {token!r} kind does not match {key!r}", candidates.values()
                    )
                if key == "region":
                    if target_type != TargetType.REGION.value or candidate["target_id"] != target_id:
                        return self._reject_prepared(
                            "db_failed", "region candidate does not belong to the target", candidates.values()
                        )
                    if candidate["base_revision_id"] != current.current_revisions.get("region"):
                        return self._reject_prepared(
                            "input_revision_changed", "prepared region base Revision changed", candidates.values()
                        )
                else:
                    payload = candidate["payload"]
                    if (
                        payload.get("artifact_type") != key
                        or payload.get("page_id") != current.page_id
                        or candidate["page_id"] != current.page_id
                    ):
                        return self._reject_prepared(
                            "db_failed", "artifact candidate does not belong to the target", candidates.values()
                        )
                    artifact_row = self._conn.execute(
                        "SELECT artifact_id, current_revision_id FROM media_artifacts"
                        " WHERE page_id = ? AND artifact_type = ? ORDER BY created_at, artifact_id LIMIT 1",
                        (current.page_id, key),
                    ).fetchone()
                    actual_revision = artifact_row["current_revision_id"] if artifact_row else None
                    if candidate["base_revision_id"] != actual_revision or payload.get("base_revision_id") != actual_revision:
                        return self._reject_prepared(
                            "input_revision_changed", "prepared artifact base Revision changed", candidates.values()
                        )
                    if self._storage is None:
                        return self._reject_prepared(
                            "db_failed", "artifact candidate requires an injected storage adapter", candidates.values()
                        )
                    self._validate_artifact_temp(payload)

            if any(
                current.current_revisions.get(key) != value
                for key, value in expected_revisions.items() if key not in {"__fea10_guard__", "__fea10_protection__"}
            ):
                return self._reject_prepared(
                    "input_revision_changed", "current Revision changed", candidates.values()
                )
            if current.lock != expected_lock:
                return self._reject_prepared(
                    "lock_changed", "current Lock changed", candidates.values()
                )
            if ("__fea10_guard__" in expected_revisions and
                    expected_revisions["__fea10_guard__"] != snapshot_digest(current.metadata.get("commit_guard", {}))):
                return self._reject_prepared("lock_changed", "source binding or active draft changed", candidates.values())
            if ("__fea10_protection__" in expected_revisions and expected_revisions["__fea10_protection__"] !=
                    snapshot_digest([current.manual_edited, current.final_confirmed])):
                return self._reject_prepared("lock_changed", "manual/final protection changed", candidates.values())
            if current.manual_edited or current.final_confirmed:
                live_text = json.loads(self._conn.execute(
                    "SELECT text_json FROM regions WHERE region_id=?", (current.region_id,)).fetchone()[0])
                protected_keys = ("edited_translation", "edited_confirmed", "final_translation", "final_source", "manual_edited")
                if any(candidate["result_kind"] == "region" and any(
                    candidate["payload"]["text_json"].get(key) != live_text.get(key) for key in protected_keys
                ) for candidate in candidates.values()):
                    return self._reject_prepared("lock_changed", "candidate would replace protected translation", candidates.values())
            if candidates and current.metadata.get("commit_guard", {}).get("drafts"):
                return self._reject_prepared("lock_changed", "active draft requires candidate review", candidates.values())
            if run_id is not None:
                request_row = self._conn.execute(
                    "SELECT pause_requested, cancel_requested FROM pipeline_runs WHERE run_id = ?",
                    (run_id,),
                ).fetchone()
                if request_row is not None:
                    pause_requested = pause_requested or bool(request_row["pause_requested"])
                    cancel_requested = cancel_requested or bool(request_row["cancel_requested"])
            if cancel_requested:
                return self._reject_prepared(
                    "cancelled", "run cancellation requested before seam commit", candidates.values()
                )
            if pause_requested:
                return self._reject_prepared(
                    "paused", "run pause requested before seam commit", candidates.values()
                )

            artifact_ops: list[dict[str, Any]] = []
            for candidate in candidates.values():
                payload = candidate["payload"]
                artifact_type = candidate["result_kind"]
                if artifact_type == "region":
                    self._write_region_candidate(current, candidate, payload)
                else:
                    artifact_ops.append(
                        self._write_artifact_candidate(
                            current, candidate, payload, artifact_type
                        )
                    )

            for stage, state in stage_updates.items():
                self._conn.execute(
                    "INSERT INTO pipeline_stage_states (target_type, target_id, stage, status, updated_at)"
                    " VALUES (?, ?, ?, ?, ?) ON CONFLICT(target_type, target_id, stage) DO UPDATE SET"
                    " status = excluded.status, updated_at = excluded.updated_at",
                    (target_type, target_id, stage, StageState(state).value, _now()),
                )
            if persist is not None:
                persist()
            resolved_at = _now()
            for token in candidates:
                self._conn.execute(
                    "UPDATE step_result_candidates SET status = 'resolved', resolved_at = ?"
                    " WHERE candidate_id = ? AND status = 'prepared'",
                    (resolved_at, token),
                )
            for operation in artifact_ops:
                relative_path = operation["relative_path"]
                if self._publish_idempotent(
                    operation["temp_handle"], relative_path,
                    operation["sha256"], operation["size"],
                ):
                    published_paths.append(relative_path)
            self._conn.commit()
            return CatalogCommit("applied")
        except Exception as error:
            return self._reject_prepared(
                "db_failed", repr(error), candidates.values(), published_paths=published_paths
            )
        finally:
            leases.close()

    def _write_region_candidate(
        self, current: TargetSnapshot, candidate: Mapping[str, Any], payload: Mapping[str, Any]
    ) -> None:
        region_id = current.region_id
        if not region_id:
            raise RuntimeError("region candidate target has no region id")
        revision_no = self._conn.execute(
            "SELECT COALESCE(MAX(revision_no), 0) + 1 AS next_no"
            " FROM region_revisions WHERE region_id = ?",
            (region_id,),
        ).fetchone()["next_no"]
        self._conn.execute(
            "INSERT INTO region_revisions (region_revision_id, region_id, revision_no,"
            " snapshot_json, origin, review_state, is_pinned, source_run_id, source_step_run_id,"
            " restored_from_revision_id, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                candidate["candidate_id"], region_id, revision_no,
                _dump(payload["snapshot"]), payload["origin"], payload["review_state"],
                int(bool(payload["is_pinned"])), payload["source_run_id"],
                payload["source_step_run_id"], payload.get("restored_from_revision_id"),
                payload["created_at"],
            ),
        )
        cursor = self._conn.execute(
            "UPDATE regions SET text_json = ?, current_revision_id = ?, updated_at = ?"
            " WHERE region_id = ? AND current_revision_id IS ? AND deleted_at IS NULL",
            (
                _dump(payload["text_json"]), candidate["candidate_id"], _now(),
                region_id, candidate["base_revision_id"],
            ),
        )
        if cursor.rowcount != 1:
            raise RuntimeError("region pointer compare-and-set failed")

    def _write_artifact_candidate(
        self, current: TargetSnapshot, candidate: Mapping[str, Any],
        payload: Mapping[str, Any], artifact_type: str,
    ) -> dict[str, Any]:
        if self._storage is None:
            raise RuntimeError("artifact candidate requires storage")
        row = self._conn.execute(
            "SELECT artifact_id, current_revision_id FROM media_artifacts"
            " WHERE page_id = ? AND artifact_type = ? ORDER BY created_at, artifact_id LIMIT 1",
            (current.page_id, artifact_type),
        ).fetchone()
        now = _now()
        if row is None:
            artifact_id = payload.get("artifact_id") or uuid.uuid4().hex
            self._conn.execute(
                "INSERT INTO media_artifacts (artifact_id, book_id, chapter_id, page_id,"
                " artifact_type, current_revision_id, created_at, updated_at)"
                " VALUES (?, ?, ?, ?, ?, NULL, ?, ?)",
                (artifact_id, payload["book_id"], payload["chapter_id"],
                 current.page_id, artifact_type, now, now),
            )
            base_revision_id = None
        else:
            artifact_id = row["artifact_id"]
            if payload.get("artifact_id") not in (None, artifact_id):
                raise RuntimeError("prepared artifact id no longer matches the page artifact")
            base_revision_id = row["current_revision_id"]
        if base_revision_id != payload.get("base_revision_id"):
            raise RuntimeError("prepared artifact base Revision changed")
        revision_no = self._conn.execute(
            "SELECT COALESCE(MAX(revision_no), 0) + 1 AS next_no"
            " FROM artifact_revisions WHERE artifact_id = ?",
            (artifact_id,),
        ).fetchone()["next_no"]
        self._conn.execute(
            "INSERT INTO artifact_revisions (artifact_revision_id, artifact_id, revision_no,"
            " managed_path, file_hash, mime_type, width, height, size_bytes, integrity_status,"
            " last_verified_at, provider_profile_id, model_name, options_json, source_artifact_revision_id,"
            " pipeline_run_id, step_run_id, provenance_json, is_pinned, created_at)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'valid', ?, ?, ?, ?, ?, ?, ?, ?, 0, ?)",
            (
                candidate["candidate_id"], artifact_id, revision_no, payload["relative_path"],
                payload["sha256"], payload["mime_type"], payload.get("width"), payload.get("height"),
                payload["size"], now, payload.get("provider_profile_id"), payload.get("model_name"),
                payload.get("options_json"), payload.get("source_artifact_revision_id"),
                candidate["pipeline_run_id"], candidate["step_run_id"],
                payload.get("provenance_json"), now,
            ),
        )
        cursor = self._conn.execute(
            "UPDATE media_artifacts SET current_revision_id = ?, updated_at = ?"
            " WHERE artifact_id = ? AND current_revision_id IS ?",
            (candidate["candidate_id"], now, artifact_id, base_revision_id),
        )
        if cursor.rowcount != 1:
            raise RuntimeError("artifact pointer compare-and-set failed")
        return dict(payload)

    def _validate_artifact_temp(self, payload: Mapping[str, Any]) -> None:
        if self._storage is None:
            raise RuntimeError("artifact candidate requires storage")
        if not all(key in payload for key in ("temp_handle", "relative_path", "sha256", "size", "mime_type")):
            raise ValueError("artifact candidate payload is incomplete")
        temp_path = Path(str(payload["temp_handle"]))
        final_path = Path(self._storage.absolute_path(str(payload["relative_path"])))
        if temp_path.is_file():
            integrity = self._storage.verify_temp(str(temp_path))
        elif final_path.is_file():
            integrity = integrity_of(final_path)
        else:
            raise FileNotFoundError("staged artifact temp and final files are both missing")
        if integrity.sha256 != payload["sha256"] or integrity.size_bytes != int(payload["size"]):
            raise ValueError("staged artifact sha256/size validation failed")

    def _publish_idempotent(
        self, temp_handle: str, relative_path: str, sha256: str, size: int
    ) -> bool:
        if self._storage is None:
            raise RuntimeError("artifact candidate requires storage")
        final_path = Path(self._storage.absolute_path(relative_path))
        if final_path.exists():
            actual = integrity_of(final_path)
            if actual.sha256 != sha256 or actual.size_bytes != int(size):
                raise RuntimeError("managed artifact path exists with different content")
            self._storage.discard_temp(temp_handle)
            # A prepared candidate owns this immutable path until its DB
            # revision commits. Compensate it if a later step fails.
            return True
        try:
            self._storage.publish(temp_handle, relative_path)
        except Exception:
            # A storage adapter may report failure after the atomic rename. Let
            # the caller compensate if the expected file is now present.
            if final_path.is_file():
                actual = integrity_of(final_path)
                if actual.sha256 == sha256 and actual.size_bytes == int(size):
                    return True
            raise
        return True

    def _reject_prepared(
        self, status: str, detail: str, candidates, *, published_paths=()
    ) -> CatalogCommit:
        if self._conn.in_transaction:
            self._conn.rollback()
        extra: list[str] = []
        for relative_path in published_paths:
            try:
                if self._conn.execute(
                    "SELECT 1 FROM artifact_revisions WHERE managed_path = ? LIMIT 1",
                    (relative_path,),
                ).fetchone() is None and self._storage is not None:
                    self._storage.remove_managed(relative_path)
            except Exception as error:
                self.orphaned_paths.append(relative_path)
                extra.append(f"orphan managed file {relative_path!r}: {error!r}")
        rows = list(candidates)
        self._discard_candidate_temps(rows, extra)
        if rows:
            try:
                self._conn.execute("BEGIN IMMEDIATE")
                resolved_at = _now()
                for row in rows:
                    self._conn.execute(
                        "UPDATE step_result_candidates SET status = 'abandoned', resolved_at = ?"
                        " WHERE candidate_id = ? AND status = 'prepared'",
                        (resolved_at, row["candidate_id"]),
                    )
                self._conn.commit()
            except Exception as error:
                self._conn.rollback()
                extra.append(f"could not mark prepared candidate abandoned: {error!r}")
        if extra:
            detail = detail + "; " + "; ".join(extra)
        return CatalogCommit(status, detail)

    def _discard_candidate_temps(self, candidates, errors: list[str]) -> None:
        for row in candidates:
            payload = row.get("payload")
            if payload is None:
                try:
                    payload = json.loads(row.get("payload_json") or "{}")
                except (TypeError, json.JSONDecodeError):
                    continue
            temp_handle = payload.get("temp_handle") if isinstance(payload, Mapping) else None
            if not temp_handle:
                continue
            if self._storage is None:
                self.orphaned_paths.append(str(temp_handle))
                errors.append(f"temp cleanup unavailable for {temp_handle!r}")
                continue
            root = getattr(self._storage, "root", None)
            if root is not None:
                temp_root = (Path(root) / "temp").resolve()
                candidate_path = Path(str(temp_handle))
                try:
                    if candidate_path.resolve().parent != temp_root or candidate_path.suffix != ".tmp":
                        raise ValueError("temp handle escapes managed temp directory")
                except OSError as error:
                    errors.append(f"temp path validation failed for {temp_handle!r}: {error!r}")
                    continue
                if candidate_path.is_symlink():
                    errors.append(f"refusing temp symlink {temp_handle!r}")
                    continue
            try:
                self._storage.discard_temp(str(temp_handle))
            except Exception as error:
                self.orphaned_paths.append(str(temp_handle))
                errors.append(f"temp cleanup failed for {temp_handle!r}: {error!r}")

    def cleanup_staged_candidates(self) -> dict[str, Any]:
        rows = [
            dict(row)
            for row in self._conn.execute(
                "SELECT candidate_id, pipeline_run_id, step_run_id, target_id, page_id, region_id,"
                " result_kind, base_revision_id, payload_json, reason, status, created_at, resolved_at"
                " FROM step_result_candidates ORDER BY created_at, candidate_id"
            ).fetchall()
        ]
        counts = {"abandoned_prepared": 0, "discarded_temps": 0, "removed_orphans": 0}
        cleanup_errors: list[str] = []
        seen_temps: set[str] = set()
        for row in rows:
            try:
                payload = json.loads(row["payload_json"])
            except (TypeError, json.JSONDecodeError):
                continue
            if not isinstance(payload, Mapping):
                continue
            temp_handle = payload.get("temp_handle")
            relative_path = payload.get("relative_path")
            if temp_handle:
                seen_temps.add(str(temp_handle))
                if self._storage is None:
                    self.orphaned_paths.append(str(temp_handle))
                else:
                    temp_path = Path(str(temp_handle))
                    existed = temp_path.is_file()
                    self._discard_candidate_temps([{"payload": payload, "candidate_id": row["candidate_id"]}], cleanup_errors)
                    if existed and not temp_path.exists():
                        counts["discarded_temps"] += 1
            if relative_path:
                if self._storage is None:
                    self.orphaned_paths.append(str(relative_path))
                else:
                    try:
                        final_path = Path(self._storage.absolute_path(str(relative_path)))
                        referenced = self._conn.execute(
                            "SELECT 1 FROM artifact_revisions WHERE managed_path = ? LIMIT 1",
                            (relative_path,),
                        ).fetchone()
                        if referenced is None and final_path.is_file():
                            self._storage.remove_managed(str(relative_path))
                            counts["removed_orphans"] += 1
                    except Exception as error:
                        self.orphaned_paths.append(str(relative_path))
                        cleanup_errors.append(f"final cleanup failed for {relative_path!r}: {error!r}")
        if self._storage is not None:
            root = getattr(self._storage, "root", None)
            if root is not None:
                temp_dir = Path(root) / "temp"
                if temp_dir.is_dir():
                    for item in temp_dir.iterdir():
                        if item.suffix == ".tmp" and item.is_file() and str(item) not in seen_temps:
                            try:
                                self._storage.discard_temp(str(item))
                                counts["discarded_temps"] += 1
                            except Exception as error:
                                self.orphaned_paths.append(str(item))
                                cleanup_errors.append(f"untracked temp cleanup failed for {item!s}: {error!r}")
        # A crash after publish but before the DB commit can leave a final
        # managed file whose candidate is no longer discoverable by its run.
        # Sweep artifact directories too, while preserving Managed Copy originals.
        if self._storage is not None:
            root = getattr(self._storage, "root", None)
            if root is not None:
                managed_root = Path(root)
                artifact_dirs = set(ARTIFACT_TYPE_DIRS.values()) - {"original"}
                books_root = managed_root / "books"
                if books_root.is_dir():
                    for base, directories, files in os.walk(books_root, followlinks=False):
                        base_path = Path(base)
                        directories[:] = [
                            name for name in directories
                            if not (base_path / name).is_symlink()
                        ]
                        for name in files:
                            final_path = base_path / name
                            if final_path.is_symlink() or not final_path.is_file():
                                continue
                            relative_path = final_path.relative_to(managed_root).as_posix()
                            if not any(part in artifact_dirs for part in Path(relative_path).parts):
                                continue
                            referenced = self._conn.execute(
                                "SELECT 1 FROM artifact_revisions WHERE managed_path = ? LIMIT 1",
                                (relative_path,),
                            ).fetchone()
                            if referenced is not None:
                                continue
                            try:
                                self._storage.remove_managed(relative_path)
                                counts["removed_orphans"] += 1
                            except Exception as error:
                                self.orphaned_paths.append(relative_path)
                                cleanup_errors.append(
                                    f"orphan final cleanup failed for {relative_path!r}: {error!r}"
                                )

        prepared_ids = [row["candidate_id"] for row in rows if row["status"] == "prepared"]
        if prepared_ids:
            try:
                self._conn.execute("BEGIN IMMEDIATE")
                resolved_at = _now()
                abandoned_count = 0
                for candidate_id in prepared_ids:
                    cursor = self._conn.execute(
                        "UPDATE step_result_candidates SET status = 'abandoned', resolved_at = ?"
                        " WHERE candidate_id = ? AND status = 'prepared'",
                        (resolved_at, candidate_id),
                    )
                    abandoned_count += cursor.rowcount
                self._conn.commit()
                counts["abandoned_prepared"] = abandoned_count
            except Exception as error:
                self._conn.rollback()
                cleanup_errors.append(f"candidate status sweep failed: {error!r}")
        counts["orphaned_paths"] = list(dict.fromkeys(self.orphaned_paths))
        counts["errors"] = cleanup_errors
        return counts

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
                "source_hash": row["source_hash"],
                "commit_guard": self._commit_guard_value(page_id),
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
            metadata={**region.metadata, "commit_guard": self._commit_guard_value(row["page_id"])},
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
            metadata={"final_source": text.get("final_source"), "ocr_text": text.get("ocr_text", "")},
        )

    def _commit_guard_value(self, page_id: str) -> Mapping[str, Any]:
        reader = getattr(self, "guard_reader", None)
        return reader(page_id) if callable(reader) else {}

    def freeze_context(self, targets: tuple[TargetSnapshot, ...], window: int) -> tuple[TargetSnapshot, ...]:
        pinned = []
        for target in targets:
            rows = self._conn.execute(
                "SELECT page_id, sort_order FROM pages WHERE chapter_id=? AND page_id<>?"
                " AND deleted_at IS NULL ORDER BY ABS(sort_order-?), sort_order, page_id LIMIT ?",
                (target.chapter_id, target.page_id, target.page_order, window),
            ).fetchall()
            contexts = []
            for page in rows:
                regions = [dict(row) for row in self._conn.execute(
                    "SELECT region_id, current_revision_id, text_json FROM regions WHERE page_id=?"
                    " AND deleted_at IS NULL ORDER BY reading_order, region_id", (page["page_id"],))]
                text = "\n".join(json.loads(region["text_json"]).get("ocr_text", "") for region in regions)
                contexts.append({
                    "page_id": page["page_id"], "reading_order": page["sort_order"],
                    "position": "before" if page["sort_order"] < target.page_order else "after",
                    "text": text,
                    "revisions": {region["region_id"]: region["current_revision_id"] for region in regions},
                    "content_digest": snapshot_digest(text),
                })
            pinned.append(replace(target, metadata={**target.metadata, "context_pages": contexts}))
        return tuple(pinned)

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

#: Ordinary configuration keys that merely *look* sensitive to the substring
#: heuristic above. ``translate.context_token_budget`` is a plain integer
#: setting (SETTINGS-OPEN-A-1 §3.2) with a real consumer
#: (``handlers.py`` translate step) and must persist; the exemption is exact
#: key-name matching, so it cannot widen the scrubber for any other key.
_REDACTION_ALLOWED_KEYS = frozenset({"context_token_budget"})


def _redact(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {
            str(key): _redact(item)
            for key, item in value.items()
            if str(key) in _REDACTION_ALLOWED_KEYS
            or not any(part in str(key).lower() for part in _SENSITIVE_PARTS)
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
        transform: Callable | None = None,
    ) -> None:
        self._conn = conn
        self._transform = transform
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
            # PrepareRun is read-only even when defaults have not been seeded.
            return FrozenRunSnapshots(freeze_snapshot({}), freeze_snapshot({}), None, freeze_snapshot({}))
        overrides = overrides or {}
        settings_overrides = overrides.get("settings")
        if settings_overrides is None:
            settings_overrides = {
                key: value
                for key, value in overrides.items()
                if key not in {"provider_bindings", "context_policy", "provider_profiles"}
            }
        settings = _merge(_load(row["settings_json"]), settings_overrides if isinstance(settings_overrides, Mapping) else {})
        providers = _merge(_load(row["provider_bindings_json"]), overrides.get("provider_bindings", {}))
        context = _merge(_load(row["context_policy_json"]), overrides.get("context_policy", {}))
        frozen = FrozenRunSnapshots(
            settings=freeze_snapshot(_redact(settings)),
            provider_bindings=freeze_snapshot(_redact(providers)),
            constraint_snapshot_ref=row["constraint_snapshot_ref"],
            context_policy=freeze_snapshot(_redact(context)),
        )
        return self._transform(frozen) if self._transform is not None else frozen


class SqliteRunLedgerMaintenance:
    """Run-ledger maintenance for TASK-053 R-03: target-less runs are
    **kept** when pages are purged (a run spans pages and cascading it
    away would destroy shared audit history), and reclaimed only through
    this explicit entry point.

    Active runs (``running``/``paused``) are never removed here even when
    target-less: the startup recovery path may still hold them (TASK-048).
    All foreign keys along ``pipeline_runs`` are ``ON DELETE CASCADE``
    (pipeline_tasks / step_runs / step_result_candidates), so the reclaim
    is one statement with enforcement left on.
    """

    _ACTIVE_STATUSES = ("running", "paused")

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def count_targetless_runs(self) -> int:
        row = self._conn.execute(
            "SELECT COUNT(*) AS n FROM pipeline_runs r"
            " WHERE NOT EXISTS"
            " (SELECT 1 FROM pipeline_run_targets t WHERE t.pipeline_run_id = r.run_id)"
        ).fetchone()
        return int(row["n"])

    def purge_targetless_runs(self) -> int:
        placeholders = ",".join("?" for _ in self._ACTIVE_STATUSES)
        with self._conn:
            cursor = self._conn.execute(
                "DELETE FROM pipeline_runs WHERE NOT EXISTS"
                " (SELECT 1 FROM pipeline_run_targets t"
                "  WHERE t.pipeline_run_id = pipeline_runs.run_id)"
                f" AND status NOT IN ({placeholders})",
                self._ACTIVE_STATUSES,
            )
        return cursor.rowcount
