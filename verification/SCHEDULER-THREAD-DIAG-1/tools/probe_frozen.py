#!/usr/bin/env python
"""SCHEDULER-THREAD-DIAG-1 AC3: does the *shipped* frozen sidecar hit the race?

Launches the packaged (FINAL-VALIDATION-1 models package) ``core_service.exe``
with the same private data root and the same request sequence that exposed the
anomaly in the source build:

  core.ping -> StartRun(translate_untranslated, book, overrides.provider_bindings.ocr)
  -> poll GetRunSnapshot + GetTaskProjection every 100 ms (what the Avalonia
     workbench does while a run is executing)

If the frozen build reproduces "detect StepRun stuck running + regionless ocr
INVALID_INPUT", the shipped product path is affected; if it stays clean, the
shipped build predates the racy cache-refresh code path (still relevant for the
next repack).
"""
from __future__ import annotations

import json
import os
import shutil
import sqlite3
import subprocess
import sys
import threading
import time
from pathlib import Path

TASK_ENV = Path(r"G:\CODEX\New Manga.workspace\task-envs\SCHEDULER-THREAD-DIAG-1")
FIXTURE = Path(r"G:\CODEX\New Manga.workspace\task-envs\BOOK-FIXTURE-1\isolated-data")
SIDECAR = Path(
    r"G:\CODEX\New Manga.workspace\task-envs\FINAL-VALIDATION-1\out"
    r"\NewManga-0.1.0-win-x64-models\app\core-sidecar"
)
EXE = SIDECAR / "core_service.exe"
BOOK_ID = "14340ddad0ed472fbe687fe12340c5d8"
CHAPTER_ID = "240bdba549b74281bfc6d901b1a7abd7"


def prepare(tag: str) -> Path:
    root = TASK_ENV / ("data-root-frozen-" + tag)
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


class Core:
    def __init__(self, root: Path, log_path: Path):
        env = dict(os.environ)
        env.pop("NEWMANGA_EVIDENCE_DIR", None)
        env["NEWMANGA_DATA_ROOT"] = str(root)
        env["M2RC1_DERIVED_ROOT"] = str(root / "derived")
        env["M2RC2_CATALOG_DB"] = str(root / "catalog" / "catalog.sqlite")
        env["M2RC1_MANAGED_ROOT"] = str(root / "managed")
        env["PYTHONIOENCODING"] = "utf-8"
        self.env_used = {k: env.get(k) for k in (
            "NEWMANGA_DATA_ROOT", "M2RC1_DERIVED_ROOT", "M2RC2_CATALOG_DB", "M2RC1_MANAGED_ROOT")}
        self.log = open(log_path, "w", encoding="utf-8")
        self.proc = subprocess.Popen(
            [str(EXE)], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, env=env, text=True, encoding="utf-8",
            errors="replace", bufsize=1,
        )
        self._stderr: list[str] = []
        threading.Thread(target=self._pump, daemon=True).start()
        self.i = 0
        self.frames: list[dict] = []

    def _pump(self) -> None:
        for line in self.proc.stderr:
            self._stderr.append(line)
            self.log.write("STDERR " + line)
            self.log.flush()

    def send(self, command: str, payload: dict, timeout: float = 180.0) -> dict:
        self.i += 1
        rid = "frozen-%03d-%s" % (self.i, command)
        frame = {"protocol": "new-manga.core", "version": {"major": 2, "minor": 10},
                 "request_id": rid, "command": command, "payload": payload}
        self.log.write("REQ " + json.dumps(frame, ensure_ascii=False) + "\n")
        self.proc.stdin.write(json.dumps(frame, ensure_ascii=False) + "\n")
        self.proc.stdin.flush()
        deadline = time.time() + timeout
        events = []
        while time.time() < deadline:
            raw = self.proc.stdout.readline()
            if not raw:
                break
            self.log.write("RAW " + raw)
            self.log.flush()
            try:
                obj = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if "event_type" in obj and "request_id" not in obj:
                events.append(obj)
                continue
            if obj.get("request_id") == rid:
                self.frames.append({"request": frame, "response": obj})
                return {"response": obj, "events": events}
        self.frames.append({"request": frame, "response": None, "error": "timeout"})
        return {"response": None, "events": events, "error": "timeout"}

    def close(self) -> None:
        try:
            if self.proc.poll() is None:
                self.proc.stdin.close()
                try:
                    self.proc.wait(timeout=20)
                except subprocess.TimeoutExpired:
                    self.proc.kill()
        except Exception:
            pass
        time.sleep(0.2)
        self.stderr_text = "".join(self._stderr)
        try:
            self.log.write("=== STDERR (all) ===\n" + self.stderr_text)
            self.log.close()
        except Exception:
            pass


def dump_db(root: Path) -> dict:
    con = sqlite3.connect(
        "file:%s?mode=ro" % str(root / "library.db").replace("\\", "/"), uri=True)
    con.row_factory = sqlite3.Row
    out: dict = {}
    try:
        for table in ("pipeline_runs", "pipeline_tasks", "step_runs", "regions"):
            out[table] = [dict(r) for r in con.execute("select * from %s" % table)]
    finally:
        con.close()
    for row in out.get("pipeline_runs", []):
        row.pop("run_json", None)
    return out


def main() -> int:
    tag = sys.argv[1] if len(sys.argv) > 1 else "a"
    poll = sys.argv[2] if len(sys.argv) > 2 else "both"
    root = prepare(tag)
    log_path = TASK_ENV / "logs" / f"frozen-{tag}.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    overrides = {"provider_bindings": {"ocr": "manga-ocr"}}
    evidence = {"ac": "AC3", "tag": tag, "poll": poll, "exe": str(EXE),
                "exe_sha256": None, "data_root": str(root), "env": None,
                "sidecar_package": str(SIDECAR),
                "frozen_core_service_sha256":
                    "2b36bfebcf09ea118537a0bc77a6c7c9a47c8845d7a853bc60d56ed004ec519b"}
    import hashlib
    digest = hashlib.sha256()
    with EXE.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    evidence["exe_sha256"] = digest.hexdigest()

    core = Core(root, log_path)
    try:
        evidence["env"] = core.env_used
        core.send("core.ping", {})
        t0 = time.time()
        start = core.send("StartRun", {
            "command": "translate_untranslated",
            "scope": {"kind": "book", "book_id": BOOK_ID},
            "overrides": overrides,
            "idempotency_key": f"frozen-{tag}-{int(time.time())}",
        })
        run_id = ((start["response"] or {}).get("result") or {}).get("run_id")
        evidence["start_response"] = start["response"]
        terminal = None
        polls = 0
        if run_id:
            while time.time() - t0 < 60:
                snap = core.send("GetRunSnapshot", {"run_id": run_id})
                status = ((snap["response"] or {}).get("result") or {}).get("status")
                polls += 1
                if poll in ("both", "projection"):
                    core.send("GetTaskProjection", {"run_id": run_id})
                if status in ("completed", "completed_with_failures", "failed",
                              "cancelled", "interrupted"):
                    terminal = status
                    break
                time.sleep(0.1)
        evidence["run"] = {"run_id": run_id, "terminal": terminal,
                           "elapsed_ms": round((time.time() - t0) * 1000, 1),
                           "polls": polls}
        evidence["frames"] = core.frames
    finally:
        core.close()
    evidence["stderr"] = core.stderr_text
    evidence["db"] = dump_db(root)
    out = TASK_ENV / "evidence" / f"frozen-{tag}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(evidence, indent=2, ensure_ascii=False), encoding="utf-8")
    import collections
    db = evidence["db"]
    print(json.dumps({
        "tag": tag, "poll": poll, "terminal": evidence["run"]["terminal"],
        "elapsed_ms": evidence["run"]["elapsed_ms"], "polls": evidence["run"]["polls"],
        "steps": [f"{k[0]}:{k[1]}:{v}" for k, v in sorted(collections.Counter((s["step_type"], s["status"]) for s in db["step_runs"]).items())],
        "tasks": dict(collections.Counter(t["status"] for t in db["pipeline_tasks"])),
        "invalid_input": sum(1 for t in db["pipeline_tasks"] if t["error_code"] == "INVALID_INPUT"),
        "regions": len(db["regions"]),
        "stuck_running": [f"{s['step_type']}@{s['page_id'][:8]}" for s in db["step_runs"] if s["status"] == "running"],
        "evidence": str(out),
    }, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
