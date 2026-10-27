#!/usr/bin/env python3
"""RUN-EXPORT-E2E-1: drive Run/Export against the frozen core_service.

Spawns the frozen ``core_service.exe`` (base sidecar or models sidecar) on a
fresh copy of the BOOK-FIXTURE isolated data root, then really executes:

  core.ping -> list_chapters -> list_chapter_pages -> StartRun
  (translate_untranslated on the book) -> poll GetRunSnapshot / GetTaskProjection
  -> StartExport (valid shape) -> GetExportSnapshot / CancelExport / GetExportHistory

Nothing is faked: each step records the raw typed error or the observed status.
The run timeline is sampled so "which step failed and how long it took" is
evidence, not prose.

Usage:
  python run_export_probe.py --variant base
  python run_export_probe.py --variant models
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

TASK_ENV = Path(r"G:\CODEX\New Manga.workspace\task-envs\RUN-EXPORT-E2E-1")
FIXTURE_ROOT = Path(r"G:\CODEX\New Manga.workspace\task-envs\BOOK-FIXTURE-1\isolated-data")
BASE_SIDECAR = Path(r"G:\CODEX\New Manga.workspace\task-envs\FINAL-VALIDATION-1\sidecar-copy")
MODELS_SIDECAR = Path(
    r"G:\CODEX\New Manga.workspace\task-envs\FINAL-VALIDATION-1\out"
    r"\NewManga-0.1.0-win-x64-models\app\core-sidecar"
)
BOOK_ID = "14340ddad0ed472fbe687fe12340c5d8"
CHAPTER_ID = "240bdba549b74281bfc6d901b1a7abd7"
PROTOCOL = "new-manga.core"
PROTOCOL_VERSION = {"major": 2, "minor": 3}


class CoreSession:
    def __init__(self, sidecar: Path, data_root: Path, log_path: Path):
        self.sidecar = sidecar
        self.data_root = data_root
        self.log_path = log_path
        env = dict(os.environ)
        env["NEWMANGA_DATA_ROOT"] = str(data_root)
        env.pop("NEWMANGA_EVIDENCE_DIR", None)
        self.stderr = open(log_path, "wb")
        self.process = subprocess.Popen(
            [str(sidecar / "core_service.exe")],
            cwd=str(sidecar),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=self.stderr,
            env=env,
        )
        self._request_id = 0
        self.responses: dict[str, dict] = {}

    def send(self, command: str, payload: dict, timeout: float = 60.0) -> dict:
        self._request_id += 1
        request_id = f"re-{command}-{self._request_id}"
        request = {
            "protocol": PROTOCOL,
            "version": PROTOCOL_VERSION,
            "request_id": request_id,
            "command": command,
            "payload": payload,
        }
        assert self.process.stdin is not None
        self.process.stdin.write((json.dumps(request, ensure_ascii=False) + "\n").encode("utf-8"))
        self.process.stdin.flush()
        started = time.monotonic()
        stdout = self.process.stdout
        assert stdout is not None
        while time.monotonic() - started < timeout:
            line = stdout.readline()
            if not line:
                break
            try:
                response = json.loads(line.decode("utf-8"))
            except json.JSONDecodeError:
                continue
            if response.get("request_id") != request_id:
                self.responses[str(response.get("request_id"))] = response
                continue
            response["_elapsed_ms"] = round((time.monotonic() - started) * 1000, 1)
            return response
        return {"request_id": request_id, "error": {"code": "PROBE_TIMEOUT"}, "_elapsed_ms": round((time.monotonic() - started) * 1000, 1)}

    def close(self) -> None:
        try:
            self.process.terminate()
            self.process.wait(timeout=15)
        except Exception:  # noqa: BLE001 - teardown best effort
            try:
                self.process.kill()
            except Exception:  # noqa: BLE001
                pass
        try:
            self.stderr.close()
        except Exception:  # noqa: BLE001
            pass


def trace(command: str, response: dict) -> dict:
    entry = {
        "command": command,
        "elapsed_ms": response.pop("_elapsed_ms", None),
        # The frozen envelope is {"request_id": ..., "result": {...}, "error": null}
        # on success and {"request_id": ..., "result": null, "error": {...}} on failure.
        "ok": response.get("result") is not None and response.get("error") is None,
    }
    if not entry["ok"]:
        error = response.get("error") or {}
        entry["error"] = {
            "code": error.get("code"),
            "kind": error.get("kind"),
            "message": error.get("message"),
        }
    else:
        entry["result"] = response.get("result")
    return entry


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--variant", choices=["base", "models"], required=True)
    args = parser.parse_args(argv)

    TASK_ENV.mkdir(parents=True, exist_ok=True)
    data_root = TASK_ENV / f"data-root-{args.variant}"
    if data_root.exists():
        shutil.rmtree(data_root)
    shutil.copytree(FIXTURE_ROOT, data_root)
    # Namespace/owner locks are bound to the original derived root; a copied
    # data root must not inherit them (the frozen Core fails closed otherwise).
    for lock in (
        data_root / "derived" / ".preview-lifecycle.lock",
        data_root / "library.db.run-owner.lock",
        data_root / "catalog" / "catalog.sqlite",
        data_root / "catalog" / "catalog.sqlite-wal",
        data_root / "catalog" / "catalog.sqlite-shm",
    ):
        if lock.exists():
            lock.unlink()
    sidecar = BASE_SIDECAR if args.variant == "base" else MODELS_SIDECAR
    evidence = {
        "ac": "AC2/AC3",
        "variant": args.variant,
        "sidecar": str(sidecar),
        "sidecar_core_service_sha256": hashlib.sha256((sidecar / "core_service.exe").read_bytes()).hexdigest(),
        "data_root": str(data_root),
        "fixture_book": BOOK_ID,
        "fixture_chapter": CHAPTER_ID,
        "models_present": {
            "detector": (sidecar / "models" / "detector" / "rtdetr-v2-fixed.onnx").exists(),
            "ocr": (sidecar / "models" / "ocr" / "manga-ocr-onnx" / "encoder_model.onnx").exists(),
        },
        "commands": [],
    }
    log = TASK_ENV / f"core-{args.variant}.stderr.log"
    session = CoreSession(sidecar, data_root, log)
    timeline: list[dict] = []
    try:
        for command, payload in (
            ("core.ping", {}),
            ("list_chapters", {"book_id": BOOK_ID}),
        ):
            response = session.send(command, payload)
            evidence["commands"].append(trace(command, response))

        pages_resp = session.send("list_chapter_pages", {"chapter_id": CHAPTER_ID})
        evidence["commands"].append(trace("list_chapter_pages", pages_resp))
        pages = []
        if "result" in pages_resp:
            payload = pages_resp["result"].get("result", pages_resp["result"])
            pages = payload.get("pages") or []
        page_ids = [page.get("page_id") for page in pages if page.get("page_id")]
        evidence["page_count"] = len(page_ids)

        start_run = session.send(
            "StartRun",
            {
                "command": "translate_untranslated",
                "scope": {"kind": "book", "book_id": BOOK_ID},
                "overrides": {},
                "idempotency_key": f"re-e2e-{args.variant}-1",
                "_elapsed_check": None,
            },
        )
        evidence["commands"].append(trace("StartRun", start_run))
        run_id = None
        if "result" in start_run:
            payload = start_run["result"].get("result", start_run["result"])
            run_id = payload.get("run_id")
        evidence["run_id"] = run_id

        if run_id:
            started = time.monotonic()
            terminal = {"completed", "completed_with_failures", "failed", "cancelled", "interrupted"}
            last_status = None
            while time.monotonic() - started < 300:
                snapshot = session.send("GetRunSnapshot", {"run_id": run_id}, timeout=30)
                status = None
                if "result" in snapshot:
                    payload = snapshot["result"].get("result", snapshot["result"])
                    status = payload.get("status")
                entry = {
                    "t_ms": round((time.monotonic() - started) * 1000, 1),
                    "status": status,
                    "elapsed_ms": snapshot.get("_elapsed_ms"),
                    "ok": "result" in snapshot,
                }
                if "error" in snapshot:
                    entry["error"] = snapshot.get("error")
                if status != last_status:
                    timeline.append(entry)
                    last_status = status
                if status in terminal:
                    break
                time.sleep(0.5)
            evidence["run_timeline"] = timeline
            evidence["run_terminal_status"] = last_status

            projection = session.send("GetTaskProjection", {"run_id": run_id}, timeout=30)
            projection_entry = trace("GetTaskProjection", projection)
            projection_entry["raw"] = projection.get("result")
            evidence["commands"].append(projection_entry)
            if projection.get("result") is not None:
                evidence["task_projection"] = projection["result"]
            for command, payload in (
                ("ControlRun", {"run_id": run_id, "action": "pause"}),
                ("ResumeBlockedRun", {"run_id": run_id}),
            ):
                response = session.send(command, payload, timeout=30)
                evidence["commands"].append(trace(command, response))

        export_payload = {
            "book_id": BOOK_ID,
            "chapter_ids": [CHAPTER_ID],
            "ordered_page_ids": page_ids,
            "format": "pdf",
            "format_options": {"pdf_content": "image_only"},
            "stale_policy": "abort",
            "target_ref": "etref1.not-registered.probe-signature",
        }
        for command, payload in (
            ("StartExport", export_payload),
            ("GetExportSnapshot", {"export_id": "export-probe-missing"}),
            ("CancelExport", {"export_id": "export-probe-missing"}),
            ("GetExportHistory", {}),
        ):
            response = session.send(command, payload, timeout=120)
            evidence["commands"].append(trace(command, response))
    finally:
        session.close()

    out = TASK_ENV / f"probe-{args.variant}.json"
    out.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "variant": args.variant,
        "run_id": evidence.get("run_id"),
        "terminal": evidence.get("run_terminal_status"),
        "timeline": evidence.get("run_timeline"),
        "errors": [
            {c["command"]: c.get("error")} for c in evidence["commands"] if c.get("error")
        ],
        "out": str(out),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
