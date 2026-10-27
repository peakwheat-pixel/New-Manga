#!/usr/bin/env python
"""SCHEDULER-THREAD-DIAG-1: consolidate the A/B evidence into diagnosis.json."""
import glob
import hashlib
import json
import os
from pathlib import Path

TASK_ENV = Path(r"G:\CODEX\New Manga.workspace\task-envs\SCHEDULER-THREAD-DIAG-1")
REPO = Path(r"G:\CODEX\New Manga")


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def summarize(path: Path, mode: str, poll: str) -> dict:
    d = json.load(open(path, encoding="utf-8"))
    db = d["db"]
    steps = db.get("step_runs") or db.get("steps") or []
    tasks = db.get("pipeline_tasks") or db.get("tasks") or []
    return {
        "evidence_file": path.name,
        "mode": mode,
        "poll": poll,
        "terminal": d.get("run", {}).get("terminal") or d.get("terminal"),
        "elapsed_ms": d.get("run", {}).get("elapsed_ms") or d.get("elapsed_ms"),
        "step_counts": {f"{t}:{s}": sum(1 for x in steps if x["step_type"] == t and x["status"] == s)
                        for t, s in sorted({(x["step_type"], x["status"]) for x in steps})},
        "stuck_running_steps": [f"{x['step_type']}@{x['page_id'][:8]}" for x in steps if x["status"] == "running"],
        "tasks": {s: sum(1 for t in tasks if t["status"] == s) for s in sorted({t["status"] for t in tasks})},
        "invalid_input_tasks": [t["page_id"][:8] for t in tasks if t["error_code"] == "INVALID_INPUT"],
        "regions": len(db.get("regions") or []),
    }


def causal_chain(d: dict) -> dict:
    log = d["log"]
    page = "f52f2772"
    chain = []
    for e in log:
        s = json.dumps(e, ensure_ascii=False)
        if "f52f2772" not in s:
            continue
        if e["event"] in ("run.status", "store.get", "run.status"):
            continue
        chain.append({k: e.get(k) for k in
                      ("t_ms", "thread", "event", "run_obj", "before_obj", "after_obj",
                       "vector", "unit", "status", "outcome", "task_units", "step")})
    facades = {}
    for e in log:
        for key in ("facade", "real_conn"):
            if e.get(key):
                facades.setdefault(e["thread"], set()).add((e.get("facade"), e.get("real_conn")))
    return {"page": page, "events": chain,
            "threads": {k: sorted(v) for k, v in facades.items()}}


def main() -> None:
    def newest(pattern: str) -> Path:
        return sorted(glob.glob(str(TASK_ENV / "evidence" / pattern)), key=os.path.getmtime)[-1]
    files = {
        "source-fresh": (Path(newest("repro-scheduler-*.json")), "scheduler", "projection-fresh"),
    }
    # pick the three source-mode runs by content
    src_runs = {}
    for p in sorted(glob.glob(str(TASK_ENV / "evidence" / "repro-*.json")), key=os.path.getmtime):
        d = json.load(open(p, encoding="utf-8"))
        if d.get("mode") == "scheduler" and d.get("poll"):
            src_runs[d["poll"]] = Path(p)
    frozen = {}
    for p in sorted(glob.glob(str(TASK_ENV / "evidence" / "frozen-*.json")), key=os.path.getmtime):
        d = json.load(open(p, encoding="utf-8"))
        frozen[d.get("poll", "?")] = Path(p)

    matrix = []
    for poll, p in src_runs.items():
        matrix.append(summarize(p, "source-scheduler", poll))
    for poll, p in frozen.items():
        matrix.append(summarize(p, "frozen-shipped", poll))

    fresh_path = src_runs.get("projection-fresh")
    fresh = json.load(open(fresh_path, encoding="utf-8")) if fresh_path else {}
    chain = causal_chain(fresh) if fresh else {"page": "f52f2772", "events": [], "threads": {}}

    src_pins = {}
    for rel in ("src/application/tasks/service.py",
                "src/infrastructure/sqlite/pipeline.py",
                "src/infrastructure/pipeline/assembly.py",
                "src/bootstrap/core_service.py"):
        src_pins[rel] = {"sha256": sha(REPO / rel), "bytes": (REPO / rel).stat().st_size}

    diagnosis = {
        "task": "SCHEDULER-THREAD-DIAG-1",
        "verdict": "CONFIRMED shared-mutable run cache race (SqlitePipelineStore._cache) between the "
                   "scheduler execution thread and the stdio/host request thread calling "
                   "GetTaskProjection(fresh=True) -> store.refresh()",
        "root_cause": {
            "one_line": "SqlitePipelineStore caches PipelineRun objects in a plain shared dict "
                        "(_cache) while sqlite connections are thread-routed; GetTaskProjection "
                        "calls pipeline.get_task_projection(fresh=True) -> store.refresh(), which "
                        "replaces the cache entry with a newly loaded clone. The scheduler thread's "
                        "execute_run keeps executing its own (now-stale) object, while "
                        "commit_step_result/_find_step read the clone. Result: commit+backfill land on "
                        "the clone, the stale object keeps the old regionless unit list -> downstream "
                        "ocr INVALID_INPUT; the stale object's later _persist writes the pre-commit "
                        "state back over pipeline_runs.run_json -> StepRun stuck at running.",
            "code_points": [
                {"file": "src/bootstrap/core_service.py", "symbol": "_cached_task_projection",
                 "line": 3236, "detail": "GetTaskProjection RPC -> pipeline.get_task_projection(run_id, fresh=True)"},
                {"file": "src/application/tasks/service.py", "symbol": "PipelineService.get_run_snapshot",
                 "line": 1394, "detail": "fresh=True -> self._store.refresh(run_id)"},
                {"file": "src/infrastructure/sqlite/pipeline.py", "symbol": "SqlitePipelineStore.refresh",
                 "line": 415, "detail": "reads DB then self._cache[run_id] = run (replaces the object "
                                         "the executor thread is using)"},
                {"file": "src/application/tasks/service.py", "symbol": "PipelineService._find_step",
                 "line": 1531, "detail": "commit_step_result resolves run via store.get() -> cache -> clone"},
                {"file": "src/application/tasks/service.py", "symbol": "PipelineService._persist",
                 "line": 1454, "detail": "whole-run JSON write; stale local run overwrites newer committed state"},
                {"file": "src/infrastructure/sqlite/connection.py", "symbol": "ThreadRoutedConnection",
                 "line": 82, "detail": "connections ARE thread-routed correctly; the leak is the un-shared "
                                        "cache, not the sqlite connection"},
            ],
            "trigger": "any client calling GetTaskProjection while a Run is being executed "
                       "(projection face is designed for UI polling)",
        },
        "thread_and_connection_routing": {
            "threads": chain.get("threads", {}),
            "note": "facade identity is shared (same ThreadRoutedConnection object); the per-thread "
                    "sqlite3.Connection differs as designed; _cache is a plain dict shared by both threads.",
        },
        "causal_chain_page1": chain.get("events", []),
        "ab_matrix": matrix,
        "fix_recommendation": {
            "minimal": "Stop view reads from mutating the execution cache: make "
                       "get_run_snapshot(fresh=True)/refresh() return a detached read without "
                       "replacing _cache[run_id] (or add a separate read-only path used by "
                       "GetTaskProjection). Add a regression test: execute_run on one thread while "
                       "another thread polls get_task_projection(fresh=True) -> run must complete "
                       "with zero stuck StepRuns and no regionless-unit INVALID_INPUT.",
            "hardening": "Also guard the whole-run write: pipeline_runs.run_json is last-writer-wins "
                         "across threads. Either keep execution writes on the owner thread only "
                         "(reject writes from non-owner runs) or add an updated_at/revision CAS check "
                         "so a stale snapshot cannot overwrite a newer one.",
            "no_core_semantics_change": True,
            "suggested_next_task": "RUN-STORE-CACHE-RACE-FIX-1 (implementation; small, Core-only, "
                                   "with concurrency regression test).",
        },
        "product_impact": {
            "shipped_binary_contains_race": True,
            "frozen_repro": "packaged core_service.exe (sha256 2b36bfeb…4ec519b) with projection polling: "
                            "3 detect steps stuck running + regionless ocr INVALID_INPUT on 3 pages; "
                            "with snapshot-only polling: 0 stuck (clean).",
            "current_gui_polling": "Avalonia Host wires library_get_task_projection "
                                   "(apps/desktop-avalonia/src/NewManga.App/Shell/ReaderWorkbenchSupport.cs:195, "
                                   "CoreClient/Commands/HostCommandRegistry.cs:102/147) but no viewmodel "
                                   "invokes it on a timer yet -> the shipped GUI does not trigger it today; "
                                   "any workbench projection polling (next S4 UI batch), Host integration "
                                   "test or diagnostic tool that polls the face does.",
            "verdict": "latent production defect in shipped binary; must be fixed before the workbench "
                       "projection polling lands (or any tool that polls GetTaskProjection during a run).",
        },
        "source_pins": src_pins,
        "repro": {
            "script": "tools/repro_scheduler.py",
            "frozen_probe": "tools/probe_frozen.py",
            "stable": "source-mode projection-fresh repro: 3/3 runs showed stuck detect + INVALID_INPUT; "
                      "projection-cached and no-poll controls: 2/2 clean.",
        },
    }
    out_dir = REPO / "verification" / "SCHEDULER-THREAD-DIAG-1"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "diagnosis.json").write_text(
        json.dumps(diagnosis, indent=2, ensure_ascii=False), encoding="utf-8")
    print("diagnosis.json written:", (out_dir / "diagnosis.json").stat().st_size, "bytes")
    for row in matrix:
        print(f"  {row['mode']:<18} poll={str(row['poll']):<18} terminal={row['terminal']:<26} "
              f"stuck={len(row['stuck_running_steps'])} invalid={len(row['invalid_input_tasks'])} "
              f"tasks={row['tasks']}")


if __name__ == "__main__":
    main()
