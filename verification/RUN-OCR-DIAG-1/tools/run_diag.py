#!/usr/bin/env python
"""RUN-OCR-DIAG-1 AC1: minimal reproduction of the Run-chain OCR failure.

Spawns the frozen models-package core_service.exe on a private copy of the
BOOK-FIXTURE data root, starts one run, and records every frame plus the DB rows
each stage wrote. Read-only w.r.t. product source; the data root is a private copy.

Env overrides (all optional, recorded in the evidence) exist so the diagnosis can
separate "weights not resolvable" from "weights resolvable but provider fails":
  --ocr-weights DIR   -> NEWMANGA_MANGA_OCR_WEIGHTS
  --ocr-device DEV    -> NEWMANGA_OCR_DEVICE
  --ocr-backend NAME  -> NEWMANGA_OCR_BACKEND
  --det-weights FILE  -> NEWMANGA_DETECTOR_WEIGHTS
"""
import argparse
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import threading
import time
from pathlib import Path

TASK_ENV = Path(r"G:\CODEX\New Manga.workspace\task-envs\RUN-OCR-DIAG-1")
MODELS_SIDECAR = Path(
    r"G:\CODEX\New Manga.workspace\task-envs\FINAL-VALIDATION-1\out"
    r"\NewManga-0.1.0-win-x64-models\app\core-sidecar"
)
BASE_SIDECAR = Path(
    r"G:\CODEX\New Manga.workspace\task-envs\FINAL-VALIDATION-1\out"
    r"\NewManga-0.1.0-win-x64\app\core-sidecar"
)
FIXTURE_ROOT = Path(r"G:\CODEX\New Manga.workspace\task-envs\BOOK-FIXTURE-1\isolated-data")
BOOK_ID = "14340ddad0ed472fbe687fe12340c5d8"
CHAPTER_ID = "240bdba549b74281bfc6d901b1a7abd7"


class CoreSession:
    def __init__(self, sidecar: Path, data_root: Path, env_extra: dict, log_path: Path):
        self.sidecar = sidecar
        self.data_root = data_root
        self.log_path = log_path
        self.frames = []
        self._id = 0
        self.proc = None
        self.stderr_text = ""
        self.env_extra = dict(env_extra)

    def __enter__(self):
        return self.start()

    def __exit__(self, *exc):
        self.close()

    def start(self):
        env = dict(os.environ)
        env.pop("NEWMANGA_EVIDENCE_DIR", None)
        env["NEWMANGA_DATA_ROOT"] = str(self.data_root)
        env["M2RC1_DERIVED_ROOT"] = str(self.data_root / "derived")
        env["M2RC2_CATALOG_DB"] = str(self.data_root / "catalog" / "catalog.sqlite")
        env["M2RC1_MANAGED_ROOT"] = str(self.data_root / "managed")
        for k, v in self.env_extra.items():
            if v is None:
                env.pop(k, None)
            else:
                env[k] = str(v)
        self.env_used = {k: env.get(k) for k in
                         ("NEWMANGA_DATA_ROOT", "NEWMANGA_MANGA_OCR_WEIGHTS",
                          "NEWMANGA_OCR_DEVICE", "NEWMANGA_OCR_BACKEND",
                          "NEWMANGA_DETECTOR_WEIGHTS", "NEWMANGA_SFX_WEIGHTS")}
        self.proc = subprocess.Popen(
            [str(self.sidecar / "core_service.exe")],
            cwd=str(self.sidecar),
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            env=env, bufsize=1, text=True, encoding="utf-8", errors="replace",
        )
        self._log = open(self.log_path, "w", encoding="utf-8")
        self._stderr_lines = []
        threading.Thread(target=self._pump_stderr, daemon=True).start()
        return self

    def _pump_stderr(self):
        for line in self.proc.stderr:
            self._stderr_lines.append(line)
            try:
                self._log.write("STDERR " + line)
                self._log.flush()
            except Exception:
                pass

    def send(self, command: str, payload: dict, timeout: float = 120.0) -> dict:
        self._id += 1
        rid = "diag-%s-%03d" % (command, self._id)
        frame = {"protocol": "new-manga.core", "version": {"major": 2, "minor": 3},
                 "request_id": rid, "command": command, "payload": payload}
        line = json.dumps(frame, ensure_ascii=False)
        self._log.write("REQ " + line + "\n")
        self._log.flush()
        self.proc.stdin.write(line + "\n")
        self.proc.stdin.flush()
        deadline = time.time() + timeout
        events = []
        while time.time() < deadline:
            raw = self.proc.stdout.readline()
            if not raw:
                break
            self._log.write("RAW " + raw)
            self._log.flush()
            try:
                obj = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if "event_type" in obj and "request_id" not in obj:
                events.append(obj)
                continue
            if obj.get("request_id") == rid:
                self.frames.append({"request": frame, "response": obj, "events": events})
                return {"response": obj, "events": events}
        self.frames.append({"request": frame, "response": None, "events": events,
                            "error": "timeout"})
        return {"response": None, "events": events, "error": "timeout"}

    def close(self):
        try:
            if self.proc and self.proc.poll() is None:
                self.proc.stdin.close()
                try:
                    self.proc.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    self.proc.kill()
        except Exception:
            pass
        time.sleep(0.2)
        self.stderr_text = "".join(self._stderr_lines)
        try:
            self._log.write("=== STDERR (all) ===\n" + self.stderr_text)
            self._log.close()
        except Exception:
            pass


def prepare_data_root(name: str) -> Path:
    root = TASK_ENV / ("data-root-" + name)
    if root.exists():
        shutil.rmtree(root, ignore_errors=True)
    shutil.copytree(FIXTURE_ROOT, root)
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
    for sub in ("derived", "catalog", "managed", "_env"):
        (root / sub).mkdir(parents=True, exist_ok=True)
    return root


def dump_db(root: Path) -> dict:
    db = root / "library.db"
    out = {"db": str(db), "tables": {}}
    if not db.exists():
        return out
    con = sqlite3.connect("file:%s?mode=ro" % str(db).replace("\\", "/"), uri=True)
    con.row_factory = sqlite3.Row
    try:
        for table in ("pipeline_runs", "pipeline_tasks", "pipeline_stage_states",
                      "step_runs", "step_result_candidates", "regions", "artifact_revisions",
                      "pipeline_run_targets"):
            try:
                rows = [dict(r) for r in con.execute("select * from %s" % table)]
            except sqlite3.Error as e:
                out["tables"][table] = {"error": str(e)}
                continue
            out["tables"][table] = rows
    finally:
        con.close()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", choices=["models", "base"], default="models")
    ap.add_argument("--command", default="translate_untranslated")
    ap.add_argument("--scope", default="book", choices=["book", "chapter", "page"])
    ap.add_argument("--page-index", type=int, default=0)
    ap.add_argument("--ocr-weights", default=None)
    ap.add_argument("--ocr-device", default=None)
    ap.add_argument("--ocr-backend", default=None)
    ap.add_argument("--det-weights", default=None)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--poll-seconds", type=float, default=25.0)
    ap.add_argument("--bindings", default=None,
                    help="JSON object injected as StartRun overrides.provider_bindings")
    ap.add_argument("--detect-pages", action="store_true",
                    help="also call core.detect on every page before the run")
    args = ap.parse_args()

    sidecar = MODELS_SIDECAR if args.variant == "models" else BASE_SIDECAR
    root = prepare_data_root(args.tag)
    log = TASK_ENV / "logs" / ("core-" + args.tag + ".log")
    log.parent.mkdir(parents=True, exist_ok=True)

    env_extra = {
        "NEWMANGA_MANGA_OCR_WEIGHTS": args.ocr_weights,
        "NEWMANGA_OCR_DEVICE": args.ocr_device,
        "NEWMANGA_OCR_BACKEND": args.ocr_backend,
        "NEWMANGA_DETECTOR_WEIGHTS": args.det_weights,
    }
    evidence = {
        "ac": "AC1",
        "tag": args.tag,
        "variant": args.variant,
        "sidecar": str(sidecar),
        "sidecar_core_service_sha256": None,
        "data_root": str(root),
        "env": {k: v for k, v in env_extra.items()},
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "frames": [],
        "run": {},
        "db": {},
        "stderr": "",
    }
    import hashlib
    exe = sidecar / "core_service.exe"
    if exe.exists():
        h = hashlib.sha256()
        with open(exe, "rb") as f:
            for c in iter(lambda: f.read(1 << 20), b""):
                h.update(c)
        evidence["sidecar_core_service_sha256"] = h.hexdigest()

    with CoreSession(sidecar, root, env_extra, log) as s:
        evidence["env_used"] = s.env_used
        ping = s.send("core.ping", {})
        chaps = s.send("list_chapters", {"book_id": BOOK_ID})
        pages_resp = s.send("list_chapter_pages", {"chapter_id": CHAPTER_ID})
        pages = []
        try:
            prog = (pages_resp["response"] or {}).get("result")
            pages = [p.get("page_id") for p in (prog or {}).get("pages", [])] if isinstance(prog, dict) else []
        except Exception:
            pages = []
        if not pages:
            # fall back to the page ids recorded by earlier tasks
            pages = ["f52f2772e8044557a72e82f5ea6ab932", "4f8a24147b3044deabf4f5a2dd83b84f"]
        scope = {"kind": "book", "book_id": BOOK_ID}
        if args.scope == "chapter":
            scope = {"kind": "chapter", "chapter_id": CHAPTER_ID}
        elif args.scope == "page":
            scope = {"kind": "page", "page_id": pages[min(args.page_index, len(pages) - 1)]}
        overrides = {}
        if args.bindings:
            overrides["provider_bindings"] = json.loads(args.bindings)
        detect_probe = []
        if args.detect_pages:
            # core.detect is the verification surface over the SAME detector the
            # pipeline uses; it tells whether a page yields zero candidates.
            for idx, pid in enumerate(pages):
                dres = s.send("core.detect", {"page_id": pid})
                res = (dres["response"] or {}).get("result") or {}
                detect_probe.append({
                    "page_index": idx + 1, "page_id": pid,
                    "candidates": len(res.get("candidates") or []) if isinstance(res, dict) else None,
                    "error_code": ((dres["response"] or {}).get("error") or {}).get("code"),
                })
        start = s.send("StartRun", {
            "command": args.command,
            "scope": scope,
            "overrides": overrides,
            "idempotency_key": "diag-%s-%d" % (args.tag, int(time.time())),
        })
        run_id = ((start["response"] or {}).get("result") or {}).get("run_id")
        evidence["run"] = {"command": args.command, "scope": scope, "overrides": overrides,
                           "start_response": start["response"], "detect_probe": detect_probe}
        timeline = []
        if run_id:
            t0 = time.time()
            terminal = None
            last_proj = None
            while time.time() - t0 < args.poll_seconds:
                snap = s.send("GetRunSnapshot", {"run_id": run_id})
                status = ((snap["response"] or {}).get("result") or {}).get("status")
                timeline.append({"t_ms": round((time.time() - t0) * 1000, 1), "status": status})
                if status in ("completed", "completed_with_failures", "failed", "cancelled", "interrupted"):
                    terminal = status
                    break
                time.sleep(0.25)
            proj = s.send("GetTaskProjection", {"run_id": run_id})
            last_proj = (proj["response"] or {}).get("result")
            evidence["run"].update({
                "run_id": run_id, "terminal_status": terminal, "timeline": timeline,
                "task_projection": last_proj,
            })
        evidence["frames"] = s.frames
    evidence["stderr"] = s.stderr_text
    evidence["db"] = dump_db(root)
    evidence["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    Path(args.out).write_text(json.dumps(evidence, indent=2, ensure_ascii=False), encoding="utf-8")

    # compact console summary
    run = evidence["run"]
    print(json.dumps({"tag": args.tag, "run_id": run.get("run_id"),
                      "terminal": run.get("terminal_status"),
                      "rows": [{k: r.get(k) for k in ("page_order", "filename", "status", "error_code")}
                               for r in (run.get("task_projection") or {}).get("rows", [])],
                      "stderr_tail": evidence["stderr"][-800:]}, ensure_ascii=False, indent=1)[:4000])


if __name__ == "__main__":
    main()
