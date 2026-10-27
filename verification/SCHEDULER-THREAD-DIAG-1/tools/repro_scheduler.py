#!/usr/bin/env python
"""SCHEDULER-THREAD-DIAG-1: reproduce + instrument the scheduler-thread Run path.

Modes:
  scheduler : faithful core_service path — assemble_production_core + CoreServiceServer
              + _start_run_scheduler() (real lease + real "core-run-scheduler" thread)
              + accept_start_run() (what the StartRun handler does), then wait.
              Same thread topology as `python -m bootstrap.core_service`.
  direct    : control — same assembly, no scheduler thread; accept_start_run +
              plan_run + execute_run on the main thread (the CORE-PIPELINE-FIX-1
              AC3 in-process path that worked).

Instrumentation (diagnostic monkeypatch only, no product source changes) logs for
every store/catalog/pipeline mutation: thread name+id, connection identity,
sqlite `in_transaction` state, and the outcome status.
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import threading
import time
import traceback
from pathlib import Path

REPO = Path(r"G:\CODEX\New Manga")
TASK_ENV = Path(r"G:\CODEX\New Manga.workspace\task-envs\SCHEDULER-THREAD-DIAG-1")
FIXTURE = Path(r"G:\CODEX\New Manga.workspace\task-envs\BOOK-FIXTURE-1\isolated-data")
MODELS = Path(
    r"G:\CODEX\New Manga.workspace\task-envs\FINAL-VALIDATION-1\out"
    r"\NewManga-0.1.0-win-x64-models\app\core-sidecar\models"
)
BOOK_ID = "14340ddad0ed472fbe687fe12340c5d8"

T0 = time.time()
LOG: list[dict] = []
LOCK = threading.Lock()


def log(kind: str, **fields) -> None:
    entry = {
        "t_ms": round((time.time() - T0) * 1000, 1),
        "thread": threading.current_thread().name,
        "tid": threading.get_ident(),
        "event": kind,
    }
    entry.update(fields)
    with LOCK:
        LOG.append(entry)
        print("DIAG " + json.dumps(entry, ensure_ascii=False), flush=True)


def prepare(tag: str):
    root = TASK_ENV / ("data-root-" + tag)
    if root.exists():
        shutil.rmtree(root, ignore_errors=True)
    shutil.copytree(FIXTURE, root)
    for pat in ("derived/.preview-lifecycle.lock", "library.db.run-owner.lock",
                "catalog/catalog.sqlite", "catalog/catalog.sqlite-wal",
                "catalog/catalog.sqlite-shm", "library.db-wal", "library.db-shm"):
        p = root / pat
        try:
            if p.is_dir():
                shutil.rmtree(p)
            elif p.exists():
                p.unlink()
        except OSError:
            pass
    for sub in ("derived", "catalog", "managed"):
        (root / sub).mkdir(parents=True, exist_ok=True)
    return root


def set_env(root: Path) -> None:
    os.environ["NEWMANGA_DATA_ROOT"] = str(root)
    os.environ["M2RC1_DERIVED_ROOT"] = str(root / "derived")
    os.environ["M2RC2_CATALOG_DB"] = str(root / "catalog" / "catalog.sqlite")
    os.environ["M2RC1_MANAGED_ROOT"] = str(root / "managed")
    os.environ["NEWMANGA_DETECTOR_WEIGHTS"] = str(MODELS / "detector")
    os.environ["NEWMANGA_SFX_WEIGHTS"] = str(MODELS / "detector" / "yolo11s-seg.onnx")
    os.environ["NEWMANGA_MANGA_OCR_WEIGHTS"] = str(MODELS / "ocr" / "manga-ocr-onnx")
    os.environ["NEWMANGA_OCR_BACKEND"] = "onnx"
    sys.path.insert(0, str(REPO / "src"))


def patch() -> None:
    """Wrap the mutation points with diagnostics (behaviour preserved)."""
    from application.tasks.service import PipelineService
    from infrastructure.sqlite.pipeline import SqlitePipelineStore, SqliteTargetCatalog

    def tx_state(conn):
        try:
            return bool(conn.in_transaction)
        except Exception as error:  # noqa: BLE001
            return f"probe-error:{type(error).__name__}"

    def real_conn(conn):
        # ThreadRoutedConnection: one real sqlite3.Connection per thread
        try:
            return hex(id(conn._current()))
        except Exception as error:  # noqa: BLE001
            return f"probe-error:{type(error).__name__}"

    def status_vector(run):
        return [(s.step_type, s.status.value) for s in run.step_runs][-4:]

    orig_put = SqlitePipelineStore.put

    def put(self, run_id, run):
        log("store.put", facade=hex(id(self._conn)), real_conn=real_conn(self._conn),
            in_tx=tx_state(self._conn),
            run=run_id[:12], run_obj=hex(id(run)), status=run.status.value,
            steps=len(run.step_runs), tasks=len(run.tasks),
            vector=status_vector(run))
        return orig_put(self, run_id, run)

    orig_refresh = SqlitePipelineStore.refresh

    def refresh(self, run_id):
        before = self._cache.get(run_id)
        out = orig_refresh(self, run_id)
        after = self._cache.get(run_id)
        log("store.refresh.CACHE-REPLACED" if (before is not None and out is not None and before is not out) else "store.refresh",
            run=run_id[:12], facade=hex(id(self._conn)), real_conn=real_conn(self._conn),
            before_obj=hex(id(before)) if before is not None else None,
            after_obj=hex(id(out)) if out is not None else None,
            before_status=getattr(before, "status", None) and before.status.value,
            after_status=getattr(out, "status", None) and out.status.value,
            before_vector=status_vector(before) if before is not None else None,
            after_vector=status_vector(out) if out is not None else None)
        return out

    orig_wict = SqlitePipelineStore.write_in_current_transaction

    def write_in_current_transaction(self, run):
        before = tx_state(self._conn)
        try:
            out = orig_wict(self, run)
            after = tx_state(self._conn)
            log("store.write_in_current_transaction.ok", facade=hex(id(self._conn)),
                real_conn=real_conn(self._conn),
                in_tx_before=before, in_tx_after=after, run=run.run_id[:12],
                status=run.status.value, steps=len(run.step_runs))
            return out
        except BaseException as error:  # noqa: BLE001
            log("store.write_in_current_transaction.ERROR", conn=id(self._conn),
                in_tx_before=before, in_tx_after=tx_state(self._conn),
                error=f"{type(error).__name__}: {error}",
                traceback=traceback.format_exc()[-1200:])
            raise

    orig_get = SqlitePipelineStore.get

    def get(self, run_id):
        run = orig_get(self, run_id)
        if run is not None:
            log("store.get", conn=id(self._conn), run=run_id[:12],
                status=run.status.value, steps=len(run.step_runs),
                step_states=[(s.step_type, s.status.value) for s in run.step_runs][-3:],
                tasks=[(t.page_id[:8], t.status.value) for t in run.tasks][:2])
        return run

    orig_commit = SqliteTargetCatalog.commit_step

    def commit_step(self, **kwargs):
        target = kwargs.get("target_id")
        log("catalog.commit_step.enter", conn=id(self._conn),
            in_tx=tx_state(self._conn), target=target[:12],
            expected_revisions=dict(kwargs.get("expected_revisions") or {}),
            lock=str(kwargs.get("expected_lock")))
        outcome = orig_commit(self, **kwargs)
        log("catalog.commit_step.exit", conn=id(self._conn),
            in_tx=tx_state(self._conn), target=target[:12],
            status=getattr(outcome, "status", None),
            detail=str(getattr(outcome, "detail", ""))[:160])
        return outcome

    orig_persist = PipelineService._persist

    def _persist(self, run):
        log("pipeline._persist", run=run.run_id[:12], status=run.status.value,
            terminal_units=run.terminal_step_units,
            steps=[(s.step_type, s.status.value) for s in run.step_runs][-3:])
        return orig_persist(self, run)

    orig_record = PipelineService._record_step_attempt

    def _record_step_attempt(self, run, task, unit, *, retry_no):
        step = orig_record(self, run, task, unit, retry_no=retry_no)
        log("pipeline._record_step_attempt", run=run.run_id[:12], run_obj=hex(id(run)),
            unit=unit.unit_id[-40:],
            step=step.step_run_id[:10], step_type=step.step_type, status=step.status.value)
        return step

    orig_commit_result = PipelineService.commit_step_result

    def commit_step_result(self, step_run_id, result):
        try:
            found = self._find_step(step_run_id)
            log("pipeline._find_step", step=step_run_id[:10],
                run_obj=hex(id(found[0])), run_status=found[0].status.value,
                step_status=found[1].status.value,
                unit=found[3].unit_id[-40:])
        except BaseException as error:  # noqa: BLE001
            log("pipeline._find_step.ERROR", step=step_run_id[:10],
                error=f"{type(error).__name__}: {error}")
        outcome = orig_commit_result(self, step_run_id, result)
        log("pipeline.commit_step_result", step=step_run_id[:10],
            step_type=result.step_type, outcome=getattr(outcome, "status", None),
            region_ids=tuple(result.outputs.get("region_ids") or ())[:3])
        return outcome

    orig_backfill = PipelineService._backfill_detected_regions

    def _backfill_detected_regions(self, run, task, unit, result):
        log("pipeline._backfill_detected_regions.enter",
            page=unit.page_id[:8],
            region_ids=tuple(result.outputs.get("region_ids") or ()),
            detection=dict(result.outputs.get("detection") or {}).get("empty_detection"))
        out = orig_backfill(self, run, task, unit, result)
        log("pipeline._backfill_detected_regions.exit",
            page=unit.page_id[:8], task_units=len(task.units),
            task_status=task.status.value)
        return out

    SqlitePipelineStore.put = put
    SqlitePipelineStore.refresh = refresh
    SqlitePipelineStore.get = get
    SqlitePipelineStore.write_in_current_transaction = write_in_current_transaction
    SqliteTargetCatalog.commit_step = commit_step
    PipelineService._persist = _persist
    PipelineService._record_step_attempt = _record_step_attempt
    PipelineService.commit_step_result = commit_step_result
    PipelineService._backfill_detected_regions = _backfill_detected_regions


def dump_db(root: Path) -> dict:
    import sqlite3

    db = root / "library.db"
    out: dict = {}
    con = sqlite3.connect("file:%s?mode=ro" % str(db).replace("\\", "/"), uri=True)
    con.row_factory = sqlite3.Row
    try:
        out["run"] = [dict(r) for r in con.execute("SELECT * FROM pipeline_runs")]
        out["tasks"] = [dict(r) for r in con.execute("SELECT * FROM pipeline_tasks")]
        out["steps"] = [dict(r) for r in con.execute("SELECT * FROM step_runs")]
        out["regions"] = [
            {"region_id": r["region_id"], "page_id": r["page_id"]}
            for r in con.execute("SELECT region_id, page_id FROM regions")
        ]
        out["stage_states"] = [dict(r) for r in con.execute("SELECT * FROM pipeline_stage_states")]
    finally:
        con.close()
    for key in ("run", "tasks", "steps"):
        for row in out[key]:
            row.pop("run_json", None)
    return out


def wait_terminal(core, run_id: str, timeout: float, poll: str = "projection-fresh") -> str:
    from domain.tasks.models import PipelineRunStatus

    deadline = time.time() + timeout
    last = None
    while time.time() < deadline:
        if poll == "projection-fresh":
            # faithful to the GetTaskProjection RPC handler
            core.pipeline.get_task_projection(run_id, fresh=True)
        elif poll == "projection-cached":
            core.pipeline.get_task_projection(run_id, fresh=False)
        elif poll == "snapshot-fresh":
            core.pipeline.get_run_snapshot(run_id, fresh=True)
        snapshot = core.pipeline.get_run_snapshot(run_id)
        if snapshot.status is not last:
            last = snapshot.status
            log("run.status", run=run_id[:12], status=snapshot.status.value)
        if snapshot.status in (
            PipelineRunStatus.COMPLETED, PipelineRunStatus.COMPLETED_WITH_FAILURES,
            PipelineRunStatus.FAILED, PipelineRunStatus.CANCELLED,
            PipelineRunStatus.INTERRUPTED,
        ):
            return snapshot.status.value
        time.sleep(0.1)
    return f"timeout(last={last})"


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "scheduler"
    poll = sys.argv[2] if len(sys.argv) > 2 else "projection-fresh"
    tag = f"{mode}-{int(time.time())}"
    root = prepare(tag)
    set_env(root)
    patch()

    import bootstrap.core_service as cs
    from domain.tasks.models import CommandType, PipelineScope, ScopeType

    catalog_db = root / "catalog" / "catalog.sqlite"
    derived_root = root / "derived"
    cs._ensure_preview_namespace(catalog_db, derived_root)
    core = cs.assemble_production_core(root)
    evidence: dict = {"mode": mode, "poll": poll, "data_root": str(root),
                      "python": sys.version.split()[0], "started_at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    server = None
    run_id = None
    try:
        if mode == "scheduler":
            server = cs.CoreServiceServer(core)
            server._serving = True
            server._start_run_scheduler()
            log("scheduler.started", thread_owner=core.pipeline._scheduler_owner,
                lease=server._scheduler_lease is not None,
                worker=server._run_scheduler_thread.name if server._run_scheduler_thread else None)
        else:
            core.pipeline.set_scheduler_owner(True)
        overrides = {"provider_bindings": {"ocr": "manga-ocr"}}
        run, created = core.pipeline.accept_start_run(
            CommandType.TRANSLATE_UNTRANSLATED,
            PipelineScope(ScopeType.BOOK, book_id=BOOK_ID),
            overrides=overrides,
            idempotency_key=f"diag-{tag}",
        )
        run_id = run.run_id
        log("run.accepted", run=run_id[:12], created=created, status=run.status.value,
            tasks=len(run.tasks), thread_name=threading.current_thread().name)
        if mode == "direct":
            core.pipeline.plan_run(run_id)
            executed = core.pipeline.execute_run(run_id)
            terminal = executed.status.value
        else:
            terminal = wait_terminal(core, run_id, timeout=60, poll=poll)
        log("run.terminal", run=run_id[:12], status=terminal)
        evidence["terminal"] = terminal
        evidence["run_id"] = run_id
    except BaseException as error:  # noqa: BLE001
        evidence["exception"] = f"{type(error).__name__}: {error}"
        evidence["traceback"] = traceback.format_exc()[-4000:]
        log("run.ERROR", error=evidence["exception"])
    finally:
        if server is not None:
            try:
                server._stop_run_scheduler()
            except Exception as error:  # noqa: BLE001
                log("scheduler.stop_error", error=f"{type(error).__name__}: {error}")
        evidence["db"] = dump_db(root)
        evidence["log"] = LOG
        evidence["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        out = TASK_ENV / "evidence" / f"repro-{tag}.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(evidence, indent=2, ensure_ascii=False), encoding="utf-8")
        print("EVIDENCE " + str(out))
        try:
            core.conn.close()
        except Exception:
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
