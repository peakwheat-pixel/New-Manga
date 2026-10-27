#!/usr/bin/env python
"""RUN-STORE-CACHE-RACE-FIX-1: AC3 concurrent regression driver.

Faithful production topology (same as `python -m bootstrap.core_service`):
``assemble_production_core`` + ``CoreServiceServer`` + real ``_start_run_scheduler()``
thread + ``accept_start_run`` (what the StartRun handler does), while a *second*
thread polls ``pipeline.get_task_projection(run_id, fresh=True)`` every 100 ms --
exactly the ``GetTaskProjection`` RPC handler path that replaces
``SqlitePipelineStore._cache[run_id]`` before the fix.

Exit code / verdict:
  0  PASS  -- run reaches a terminal state, **0** StepRuns stuck in ``running``,
              **0** regionless ``INVALID_INPUT`` step failures.
  1  FAIL  -- the pre-fix race reproduces (stuck running / regionless input).

Usage (run from the repo worktree):
  python verification/RUN-STORE-CACHE-RACE-FIX-1/tools/repro_scheduler.py \
      [scheduler|direct] [projection-fresh|projection-cached|none] [--timeout N]

Evidence is written under ``$NEWMANGA_EVIDENCE_DIR`` (private task env); the
fixture data root is copied per run and never modified in place.
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

REPO = Path(__file__).resolve().parents[3]
DEFAULT_ENV = Path(r"G:\CODEX\New Manga.workspace\task-envs\RUN-STORE-CACHE-RACE-FIX-1")
EVIDENCE = Path(os.environ.get("NEWMANGA_EVIDENCE_DIR", str(DEFAULT_ENV / "evidence")))
FIXTURE = Path(os.environ.get(
    "NEWMANGA_FIXTURE_DATA_ROOT",
    r"G:\CODEX\New Manga.workspace\task-envs\BOOK-FIXTURE-1\isolated-data",
))
MODELS = Path(os.environ.get(
    "NEWMANGA_MODELS_DIR",
    r"G:\CODEX\New Manga.workspace\task-envs\FINAL-VALIDATION-1\out"
    r"\NewManga-0.1.0-win-x64-models\app\core-sidecar\models",
))
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


def prepare(tag: str) -> Path:
    root = DEFAULT_ENV / "data-roots" / ("data-root-" + tag)
    if root.exists():
        shutil.rmtree(root, ignore_errors=True)
    shutil.copytree(FIXTURE, root)
    for pat in (
        "derived/.preview-lifecycle.lock", "library.db.run-owner.lock",
        "catalog/catalog.sqlite", "catalog/catalog.sqlite-wal",
        "catalog/catalog.sqlite-shm", "library.db-wal", "library.db-shm",
    ):
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
    """Diagnostic monkeypatch only (behaviour preserved) -- one line per mutation."""
    from application.tasks.service import PipelineService
    from infrastructure.sqlite.pipeline import SqlitePipelineStore, SqliteTargetCatalog

    def status_vector(run):
        return [(s.step_type, s.status.value) for s in run.step_runs][-4:]

    orig_refresh = SqlitePipelineStore.refresh

    def refresh(self, run_id):
        before = self._cache.get(run_id)
        out = orig_refresh(self, run_id)
        after = self._cache.get(run_id)
        log(
            "store.refresh.CACHE-REPLACED"
            if (before is not None and out is not None and before is not out)
            else "store.refresh",
            run=run_id[:12],
            before_obj=hex(id(before)) if before is not None else None,
            after_obj=hex(id(out)) if out is not None else None,
        )
        return out

    orig_wict = SqlitePipelineStore.write_in_current_transaction

    def write_in_current_transaction(self, run):
        out = orig_wict(self, run)
        log("store.write_in_current_transaction.ok", run=run.run_id[:12],
            status=run.status.value, steps=len(run.step_runs))
        return out

    orig_persist = PipelineService._persist

    def _persist(self, run):
        log("pipeline._persist", run=run.run_id[:12], status=run.status.value,
            terminal_units=run.terminal_step_units,
            steps=[(s.step_type, s.status.value) for s in run.step_runs][-3:])
        return orig_persist(self, run)

    orig_find = PipelineService._find_step

    def _find_step(self, step_run_id):
        found = orig_find(self, step_run_id)
        log("pipeline._find_step", step=step_run_id[:10], run_obj=hex(id(found[0])),
            step_status=found[1].status.value, unit=found[3].unit_id[-40:])
        return found

    orig_commit = SqliteTargetCatalog.commit_step

    def commit_step(self, **kwargs):
        outcome = orig_commit(self, **kwargs)
        log("catalog.commit_step", target=str(kwargs.get("target_id"))[:12],
            status=getattr(outcome, "status", None))
        return outcome

    SqlitePipelineStore.refresh = refresh
    SqlitePipelineStore.write_in_current_transaction = write_in_current_transaction
    PipelineService._persist = _persist
    PipelineService._find_step = _find_step
    SqliteTargetCatalog.commit_step = commit_step


def dump_db(root: Path) -> dict:
    import sqlite3

    con = sqlite3.connect("file:%s?mode=ro" % str(root / "library.db").replace("\\", "/"), uri=True)
    con.row_factory = sqlite3.Row
    out: dict = {}
    try:
        out["run"] = [dict(r) for r in con.execute("SELECT * FROM pipeline_runs")]
        out["tasks"] = [dict(r) for r in con.execute("SELECT * FROM pipeline_tasks")]
        out["steps"] = [dict(r) for r in con.execute("SELECT * FROM step_runs")]
        out["regions"] = [
            {"region_id": r["region_id"], "page_id": r["page_id"]}
            for r in con.execute("SELECT region_id, page_id FROM regions")
        ]
    finally:
        con.close()
    for key in ("run", "tasks", "steps"):
        for row in out[key]:
            row.pop("run_json", None)
    return out


def wait_terminal(core, run_id: str, timeout: float, poll: str) -> str:
    from domain.tasks.models import PipelineRunStatus

    deadline = time.time() + timeout
    last = None
    while time.time() < deadline:
        if poll == "projection-fresh":
            # faithful to the GetTaskProjection RPC handler
            core.pipeline.get_task_projection(run_id, fresh=True)
        elif poll == "projection-cached":
            core.pipeline.get_task_projection(run_id, fresh=False)
        snapshot = core.pipeline.get_run_snapshot(run_id)
        if snapshot.status is not last:
            last = snapshot.status
            log("run.status", run=run_id[:12], status=snapshot.status.value)
        if snapshot.status in (
            PipelineRunStatus.COMPLETED,
            PipelineRunStatus.COMPLETED_WITH_FAILURES,
            PipelineRunStatus.FAILED,
            PipelineRunStatus.CANCELLED,
            PipelineRunStatus.INTERRUPTED,
        ):
            return snapshot.status.value
        time.sleep(0.1)
    return f"timeout(last={last})"


def analyse(db: dict) -> dict:
    steps = db.get("steps", [])
    stuck = [
        {
            "step_run_id": s.get("step_run_id"),
            "step_type": s.get("step_type"),
            "region_id": s.get("region_id"),
            "status": s.get("status"),
        }
        for s in steps
        if s.get("status") == "running"
    ]
    regionless_invalid = [
        {
            "step_run_id": s.get("step_run_id"),
            "step_type": s.get("step_type"),
            "region_id": s.get("region_id"),
            "error_code": s.get("error_code"),
        }
        for s in steps
        if s.get("error_code") == "INVALID_INPUT" and not s.get("region_id")
    ]
    by_status: dict[str, int] = {}
    for s in steps:
        key = str(s.get("status"))
        by_status[key] = by_status.get(key, 0) + 1
    return {
        "step_total": len(steps),
        "step_status_counts": by_status,
        "stuck_running": stuck,
        "regionless_invalid_input": regionless_invalid,
        "regions": len(db.get("regions", [])),
        "run_rows": [
            {"run_id": r.get("run_id"), "status": r.get("status")}
            for r in db.get("run", [])
        ],
        "task_status_counts": _count(db.get("tasks", []), "status"),
    }


def _count(rows, key):
    out: dict[str, int] = {}
    for row in rows:
        value = str(row.get(key))
        out[value] = out.get(value, 0) + 1
    return out


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    timeout = 90.0
    for a in sys.argv[1:]:
        if a.startswith("--timeout="):
            timeout = float(a.split("=", 1)[1])
    mode = args[0] if args else "scheduler"
    poll = args[1] if len(args) > 1 else "projection-fresh"
    tag = f"{mode}-{poll}-{int(time.time())}"
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    root = prepare(tag)
    set_env(root)
    patch()

    import bootstrap.core_service as cs
    from domain.tasks.models import CommandType, PipelineScope, ScopeType

    catalog_db = root / "catalog" / "catalog.sqlite"
    derived_root = root / "derived"
    cs._ensure_preview_namespace(catalog_db, derived_root)
    core = cs.assemble_production_core(root)
    evidence: dict = {
        "task": "RUN-STORE-CACHE-RACE-FIX-1",
        "mode": mode, "poll": poll, "data_root": str(root),
        "repo": str(REPO), "head": _git_head(),
        "python": sys.version.split()[0],
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    server = None
    run_id = None
    terminal = None
    try:
        if mode == "scheduler":
            server = cs.CoreServiceServer(core)
            server._serving = True
            server._start_run_scheduler()
            log("scheduler.started", owner=core.pipeline._scheduler_owner,
                worker=(server._run_scheduler_thread.name
                        if server._run_scheduler_thread else None))
        else:
            core.pipeline.set_scheduler_owner(True)
        overrides = {"provider_bindings": {"ocr": "manga-ocr"}}
        run, created = core.pipeline.accept_start_run(
            CommandType.TRANSLATE_UNTRANSLATED,
            PipelineScope(ScopeType.BOOK, book_id=BOOK_ID),
            overrides=overrides,
            idempotency_key=f"race-{tag}",
        )
        run_id = run.run_id
        log("run.accepted", run=run_id[:12], created=created, status=run.status.value,
            tasks=len(run.tasks))
        if mode == "direct":
            core.pipeline.plan_run(run_id)
            terminal = core.pipeline.execute_run(run_id).status.value
        else:
            terminal = wait_terminal(core, run_id, timeout=timeout, poll=poll)
        log("run.terminal", run=run_id[:12], status=terminal)
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
        db = dump_db(root)
        analysis = analyse(db)
        evidence["terminal"] = terminal
        evidence["run_id"] = run_id
        evidence["analysis"] = analysis
        evidence["db"] = db
        evidence["log"] = LOG
        evidence["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        passed = (
            terminal in ("completed", "completed_with_failures")
            and not analysis["stuck_running"]
            and not analysis["regionless_invalid_input"]
        )
        evidence["verdict"] = "PASS" if passed else "FAIL"
        out = EVIDENCE / f"repro-{tag}.json"
        out.write_text(json.dumps(evidence, indent=2, ensure_ascii=False), encoding="utf-8")
        print("RESULT " + json.dumps({
            "verdict": evidence["verdict"],
            "terminal": terminal,
            "stuck_running": len(analysis["stuck_running"]),
            "regionless_invalid_input": len(analysis["regionless_invalid_input"]),
            "step_status_counts": analysis["step_status_counts"],
            "task_status_counts": analysis["task_status_counts"],
            "evidence": str(out),
        }, ensure_ascii=False), flush=True)
        print("EVIDENCE " + str(out), flush=True)
        try:
            core.conn.close()
        except Exception:
            pass
    return 0 if passed else 1


def _git_head() -> str:
    try:
        import subprocess

        return subprocess.check_output(
            ["git", "-C", str(REPO), "rev-parse", "HEAD"], text=True
        ).strip()
    except Exception:  # noqa: BLE001
        return "unknown"


if __name__ == "__main__":
    raise SystemExit(main())
