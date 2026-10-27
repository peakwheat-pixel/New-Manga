#!/usr/bin/env python3
"""TRANSLATE-PROVIDER-1 AC3 (same-build check): drive a Run on the RELEASE-REPACK-1
new ``core_service.exe`` (models variant) and record exactly what it does.

The freshly repacked exe was built from ``main`` BEFORE this task's identity
provider existed, so this probe documents, on the real wire:

  detect 8/8 completed -> ocr 3/3 completed -> color 3/3 completed
  -> term_extract 3/3 completed -> translate 3 FAILED typed PROVIDER_NOT_CONFIGURED

i.e. the only remaining gap on that build is the (not yet injected) translation
provider. The identity-provider proof itself runs through the identical
production assembly path from source (``tools/verify_inproc.py``); the next
RELEASE-REPACK rebuild will carry this provider into the exe.

Nothing is faked: every frame is sent to the spawned exe and the typed errors /
statuses are recorded verbatim.
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

TASK_ENV = Path(r"G:\CODEX\New Manga.workspace\task-envs\TRANSLATE-PROVIDER-1")
FIXTURE_ROOT = Path(r"G:\CODEX\New Manga.workspace\task-envs\BOOK-FIXTURE-1\isolated-data")
NEW_MODELS_SIDECAR = Path(
    r"G:\CODEX\New Manga.workspace\task-envs\RELEASE-REPACK-1"
    r"\sidecar-models\core-sidecar"
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
        env["NEWMANGA_OCR_BACKEND"] = "onnx"
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

    def send(self, command: str, payload: dict, timeout: float = 60.0) -> dict:
        self._request_id += 1
        request_id = f"tp-{command}-{self._request_id}"
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
                continue
            response["_elapsed_ms"] = round((time.monotonic() - started) * 1000, 1)
            return response
        return {
            "request_id": request_id,
            "error": {"code": "PROBE_TIMEOUT"},
            "_elapsed_ms": round((time.monotonic() - started) * 1000, 1),
        }

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


def _unwrap(response: dict) -> dict | None:
    if response.get("error") is not None or response.get("result") is None:
        return None
    result = response["result"]
    return result.get("result", result) if isinstance(result, dict) else result


def _trace(command: str, response: dict) -> dict:
    entry = {
        "command": command,
        "elapsed_ms": response.pop("_elapsed_ms", None),
        "ok": response.get("error") is None and response.get("result") is not None,
    }
    if not entry["ok"]:
        error = response.get("error") or {}
        entry["error"] = {
            "code": error.get("code"),
            "kind": error.get("kind"),
            "message": error.get("message"),
        }
    return entry


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sidecar", default=str(NEW_MODELS_SIDECAR))
    parser.add_argument("--with-translate-binding", action="store_true",
                        help="also inject translate=identity-translation (only useful on a build that has it)")
    args = parser.parse_args(argv)
    sidecar = Path(args.sidecar)

    TASK_ENV.mkdir(parents=True, exist_ok=True)
    data_root = TASK_ENV / "exe-data-root"
    if data_root.exists():
        shutil.rmtree(data_root)
    shutil.copytree(FIXTURE_ROOT, data_root)
    for lock in (
        data_root / "derived" / ".preview-lifecycle.lock",
        data_root / "library.db.run-owner.lock",
        data_root / "catalog" / "catalog.sqlite",
        data_root / "catalog" / "catalog.sqlite-wal",
        data_root / "catalog" / "catalog.sqlite-shm",
    ):
        if lock.exists():
            lock.unlink()

    exe = sidecar / "core_service.exe"
    evidence = {
        "task": "TRANSLATE-PROVIDER-1",
        "ac": "AC3 same-build witness",
        "sidecar": str(sidecar),
        "sidecar_core_service_sha256": hashlib.sha256(exe.read_bytes()).hexdigest(),
        "sidecar_size_bytes": exe.stat().st_size,
        "data_root": str(data_root),
        "book_id": BOOK_ID,
        "chapter_id": CHAPTER_ID,
        "commands": [],
        "run_timeline": [],
    }
    log = TASK_ENV / "exe-core.stderr.log"
    session = CoreSession(sidecar, data_root, log)
    try:
        for command, payload in (
            ("core.ping", {}),
            ("list_chapters", {"book_id": BOOK_ID}),
            ("list_chapter_pages", {"chapter_id": CHAPTER_ID}),
        ):
            response = session.send(command, payload)
            entry = _trace(command, response)
            result = _unwrap(response)
            if command == "list_chapter_pages" and isinstance(result, dict):
                evidence["page_count"] = len(result.get("pages") or [])
            evidence["commands"].append(entry)

        overrides: dict = {"provider_bindings": {"ocr": "manga-ocr"}}
        if args.with_translate_binding:
            overrides["provider_bindings"]["translate"] = "identity-translation"
        evidence["overrides"] = overrides
        start = session.send(
            "StartRun",
            {
                "command": "translate_untranslated",
                "scope": {"kind": "book", "book_id": BOOK_ID},
                "overrides": overrides,
                "idempotency_key": "translate-provider-1-exe-1",
            },
        )
        evidence["commands"].append(_trace("StartRun", start))
        payload = _unwrap(start) or {}
        run_id = payload.get("run_id")
        evidence["run_id"] = run_id

        if run_id:
            started = time.monotonic()
            terminal = {"completed", "completed_with_failures", "failed", "cancelled", "interrupted"}
            last_status = None
            status = None
            while time.monotonic() - started < 600:
                snapshot = session.send("GetRunSnapshot", {"run_id": run_id}, timeout=30)
                status = (_unwrap(snapshot) or {}).get("status")
                if status != last_status:
                    evidence["run_timeline"].append(
                        {"t_ms": round((time.monotonic() - started) * 1000, 1), "status": status}
                    )
                    last_status = status
                if status in terminal:
                    break
                time.sleep(1.0)
            evidence["run_terminal_status"] = status
            evidence["run_elapsed_ms"] = round((time.monotonic() - started) * 1000, 1)

            projection = session.send("GetTaskProjection", {"run_id": run_id}, timeout=30)
            evidence["commands"].append(_trace("GetTaskProjection", projection))
            if projection.get("result") is not None:
                evidence["task_projection"] = projection["result"]
    finally:
        session.close()

    out = TASK_ENV / ("new-sidecar-run%s.json" % ("-identity-binding" if args.with_translate_binding else ""))
    out.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "sidecar_sha256": evidence["sidecar_core_service_sha256"],
        "run_id": evidence.get("run_id"),
        "terminal": evidence.get("run_terminal_status"),
        "elapsed_ms": evidence.get("run_elapsed_ms"),
        "timeline": evidence["run_timeline"],
        "page_count": evidence.get("page_count"),
        "errors": [c for c in evidence["commands"] if c.get("error")],
        "out": str(out),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
