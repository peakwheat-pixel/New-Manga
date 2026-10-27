#!/usr/bin/env python3
"""REAL-TRANSLATE-PROVIDER-1 AC3/AC4 run probe over the frozen Core stdio protocol.

Spawns the packaged ``core_service.exe`` on a private data root (same process contract as the
RELEASE-REPACK-2 full-chain probe) and drives one real Run:

    StartRun command=translate_untranslated
             scope={"kind":"book","book_id":...}
             overrides.provider_bindings={"ocr":"manga-ocr","translate":<provider>}

Then polls ``GetRunSnapshot`` and records the final ``GetTaskProjection`` (per-step statuses,
typed error codes, durations). The provider id is a parameter, so the same tool produces:

* the real-provider attempt (``openai-compatible-translation`` configured in the task work root);
* the identity fallback attempt (``identity-translation``, the experimental placeholder), proving
  the switch is a frozen-binding change only.

No API key is read by this tool: the provider credential lives in the Windows vault and is resolved
by the Core through the profile's ``credential_ref``.
"""

from __future__ import annotations

import argparse
import json
import os
import queue
import subprocess
import sys
import threading
import time
from pathlib import Path

PROTOCOL = "new-manga.core"
PROTOCOL_VERSION = {"major": 2, "minor": 3}


class CoreSession:
    def __init__(self, executable: Path, data_root: Path, stderr_path: Path) -> None:
        env = dict(os.environ)
        env["NEWMANGA_DATA_ROOT"] = str(data_root)
        env["M2RC1_DERIVED_ROOT"] = str(data_root / "derived")
        env["M2RC2_CATALOG_DB"] = str(data_root / "catalog" / "catalog.sqlite")
        env["M2RC1_MANAGED_ROOT"] = str(data_root / "managed")
        (data_root / "derived").mkdir(parents=True, exist_ok=True)
        (data_root / "catalog").mkdir(parents=True, exist_ok=True)
        (data_root / "managed").mkdir(parents=True, exist_ok=True)
        self._stderr = stderr_path.open("wb")
        self._process = subprocess.Popen(
            [str(executable)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=self._stderr,
            env=env,
        )
        self._responses: "queue.Queue[dict]" = queue.Queue()
        self._reader = threading.Thread(target=self._read_loop, daemon=True)
        self._reader.start()
        self._request_id = 0

    def _read_loop(self) -> None:
        assert self._process.stdout is not None
        for raw in self._process.stdout:
            line = raw.decode("utf-8", "replace").strip()
            if not line:
                continue
            try:
                frame = json.loads(line)
            except ValueError:
                continue
            if "request_id" in frame:
                self._responses.put(frame)
            # Run events are not needed for the probe's evidence.

    def send(self, command: str, payload: dict, timeout: float = 300.0) -> dict:
        with threading.Lock():
            self._request_id += 1
        request = {
            "protocol": PROTOCOL,
            "version": PROTOCOL_VERSION,
            "request_id": f"rtp-{command}-{self._request_id}",
            "command": command,
            "payload": payload,
        }
        assert self._process.stdin is not None
        self._process.stdin.write((json.dumps(request, ensure_ascii=False) + "\n").encode("utf-8"))
        self._process.stdin.flush()
        deadline = time.monotonic() + timeout
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return {"error": {"code": "PROBE_TIMEOUT", "message": command}}
            try:
                frame = self._responses.get(timeout=remaining)
            except queue.Empty:
                return {"error": {"code": "PROBE_TIMEOUT", "message": command}}
            if frame.get("request_id") == request["request_id"]:
                return frame

    def close(self) -> None:
        try:
            self._process.terminate()
            self._process.wait(timeout=15)
        except Exception:  # noqa: BLE001
            self._process.kill()
        self._stderr.close()


def unwrap(response: dict) -> dict:
    result = response.get("result")
    if response.get("error") is not None or result is None:
        return {}
    return result.get("result", result) if isinstance(result, dict) else {}


def summarize_projection(projection: dict) -> dict:
    tasks = projection.get("tasks") or []
    step_status: dict[str, dict[str, int]] = {}
    error_codes: list[dict] = []
    for task in tasks:
        if not isinstance(task, dict):
            continue
        for step in task.get("steps") or []:
            if not isinstance(step, dict):
                continue
            step_type = str(step.get("step_type", ""))
            status = str(step.get("status", ""))
            step_status.setdefault(step_type, {})
            step_status[step_type][status] = step_status[step_type].get(status, 0) + 1
            code = step.get("error_code") or step.get("error")
            if code:
                error_codes.append({"step_type": step_type, "status": status, "error_code": str(code)})
    return {
        "run_status": projection.get("run_status"),
        "overall_progress": projection.get("overall_progress"),
        "counts": projection.get("counts"),
        "blocked_reasons": projection.get("blocked_reasons"),
        "step_status": step_status,
        "error_codes": error_codes[:40],
        "tasks": [
            {
                "target_id": task.get("target_id") or task.get("page_id"),
                "status": task.get("status"),
                "steps": [
                    {
                        "step_type": step.get("step_type"),
                        "status": step.get("status"),
                        "error_code": step.get("error_code") or step.get("error"),
                    }
                    for step in (task.get("steps") or [])
                    if isinstance(step, dict)
                ],
            }
            for task in tasks[:12]
            if isinstance(task, dict)
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sidecar", required=True, help="packaged app/core-sidecar directory")
    parser.add_argument("--data-root", required=True)
    parser.add_argument("--book-id", default="14340ddad0ed472fbe687fe12340c5d8")
    parser.add_argument("--provider", default="openai-compatible-translation")
    parser.add_argument("--command", default="translate_untranslated")
    parser.add_argument("--out", required=True)
    parser.add_argument("--timeout", type=float, default=420.0)
    parser.add_argument("--poll-ms", type=int, default=400)
    parser.add_argument("--label", default="")
    args = parser.parse_args()

    sidecar = Path(args.sidecar)
    data_root = Path(args.data_root)
    executable = sidecar / "core_service.exe"
    if not executable.is_file():
        raise SystemExit(f"core_service.exe not found under {sidecar}")
    evidence: dict = {
        "ac": "AC3/AC4",
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "sidecar": str(sidecar),
        "data_root": str(data_root),
        "book_id": args.book_id,
        "command": args.command,
        "translate_provider": args.provider,
        "label": args.label or args.provider,
        "api_key_read_by_tool": False,
        "commands": [],
    }

    stderr_path = Path(args.out).with_suffix(".stderr.log")
    session = CoreSession(executable, data_root, stderr_path)
    try:
        ping = session.send("core.ping", {}, timeout=60)
        evidence["commands"].append({"command": "core.ping", "result": unwrap(ping)})

        overrides = {"provider_bindings": {"ocr": "manga-ocr", "translate": args.provider}}
        evidence["overrides"] = overrides
        started = session.send(
            "StartRun",
            {
                "command": args.command,
                "scope": {"kind": "book", "book_id": args.book_id},
                "overrides": overrides,
                "idempotency_key": f"real-translate-{args.label or args.provider}-{int(time.time())}",
            },
            timeout=120,
        )
        evidence["start"] = started.get("error") or unwrap(started)
        run_id = unwrap(started).get("run_id")
        if not run_id:
            evidence["terminal"] = "start_failed"
            Path(args.out).write_text(json.dumps(evidence, indent=2, ensure_ascii=False), encoding="utf-8")
            return 1

        started_at = time.monotonic()
        statuses: list[str] = []
        deadline = started_at + args.timeout
        snapshot = {}
        while time.monotonic() < deadline:
            snapshot = session.send("GetRunSnapshot", {"run_id": run_id}, timeout=60)
            status = unwrap(snapshot).get("status", "")
            if status and (not statuses or statuses[-1] != status):
                statuses.append(status)
            if status in {"completed", "completed_with_failures", "failed", "blocked", "cancelled"}:
                break
            time.sleep(max(args.poll_ms, 50) / 1000.0)
        elapsed_ms = round((time.monotonic() - started_at) * 1000, 1)
        evidence["command"] = args.command
        evidence["run_id"] = run_id
        evidence["terminal"] = unwrap(snapshot).get("status")
        evidence["status_transitions"] = statuses
        evidence["elapsed_ms"] = elapsed_ms

        projection = session.send("GetTaskProjection", {"run_id": run_id}, timeout=120)
        evidence["command_traces"] = {
            "GetRunSnapshot_request": snapshot.get("request") if isinstance(snapshot, dict) else None,
        }
        evidence["task_projection"] = summarize_projection(unwrap(projection))
    finally:
        session.close()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(evidence, indent=2, ensure_ascii=False), encoding="utf-8")
    print(
        f"{args.label or args.provider}: status={evidence.get('terminal')} "
        f"elapsed_ms={evidence.get('elapsed_ms')} -> {out}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
