#!/usr/bin/env python3
"""Deterministic concurrency test sidecar for P04 AC2.

Provides deterministic request/response synchronization across multiple
concurrent callers on the same StdioLibraryChannel instance.

Records protocol fields (protocol, version, request_id) and Python runtime
provenance (sys.executable, sys.version) at the boundary into verification/P04/**
for diagnostic evidence without altering contract semantics.
"""

from __future__ import annotations

import json
import os
import sys
import time
from typing import Any


def log_event(log_path: str | None, event_type: str, data: dict[str, Any]) -> None:
    if not log_path:
        return
    try:
        os.makedirs(os.path.dirname(os.path.abspath(log_path)), exist_ok=True)
        entry = {
            "timestamp": time.time(),
            "event": event_type,
            **data,
        }
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, separators=(",", ":")) + "\n")
    except Exception as exc:
        sys.stderr.write(f"[sidecar-log-error] {exc}\n")
        sys.stderr.flush()


def make_response(req: dict[str, Any], result: Any = None, error: Any = None) -> dict[str, Any]:
    return {
        "protocol": req.get("protocol", "new-manga.core"),
        "version": req.get("version", {"major": 1, "minor": 4}),
        "request_id": req.get("request_id", "unknown"),
        "result": result,
        "error": error,
    }


def emit(resp: dict[str, Any], log_path: str | None) -> None:
    line = json.dumps(resp, separators=(",", ":"))
    sys.stdout.write(line + "\n")
    sys.stdout.flush()
    log_event(log_path, "response_emitted", {
        "protocol": resp.get("protocol"),
        "version": resp.get("version"),
        "request_id": resp.get("request_id"),
        "result": resp.get("result"),
        "error": resp.get("error"),
    })


def main() -> int:
    log_path = os.environ.get("P04_DIAGNOSTIC_LOG")
    if not log_path:
        here = os.path.dirname(os.path.abspath(__file__))
        log_path = os.path.join(here, f"diagnostic_sidecar_{os.getpid()}_{int(time.time()*1000)}.jsonl")

    # P2-2: Record Python runtime provenance for P02-approved environment verification
    log_event(log_path, "sidecar_provenance", {
        "sys_executable": sys.executable,
        "sys_version": sys.version,
        "pid": os.getpid(),
    })

    pending_requests: list[dict[str, Any]] = []

    for raw_line in sys.stdin:
        line = raw_line.strip()
        if not line:
            continue

        try:
            req = json.loads(line)
        except Exception as exc:
            err_resp = {
                "protocol": "new-manga.core",
                "version": {"major": 1, "minor": 4},
                "request_id": "malformed",
                "result": None,
                "error": {
                    "code": "PROTOCOL_MALFORMED",
                    "category": "validation",
                    "retryable": False,
                    "message": str(exc),
                },
            }
            emit(err_resp, log_path)
            continue

        log_event(log_path, "request_received", {
            "protocol": req.get("protocol"),
            "version": req.get("version"),
            "request_id": req.get("request_id"),
            "command": req.get("command"),
            "payload": req.get("payload"),
        })

        command = req.get("command", "")
        payload = req.get("payload") or {}

        if command == "core.shutdown":
            emit(make_response(req, result={"status": "stopped"}), log_path)
            return 0
        elif command == "core.ping":
            emit(make_response(req, result={
                "status": "ready",
                "protocol_version": {"major": 1, "minor": 4},
                "capabilities": ["library.list_books"],
            }), log_path)
        elif command.startswith("test.concurrent_"):
            pending_requests.append(req)
            # Deterministic sync barrier: wait until 2 concurrent requests arrive,
            # then emit responses in received order (FIFO)
            if len(pending_requests) >= 2:
                for r in pending_requests:
                    p = r.get("payload") or {}
                    res = {
                        "echo_caller": p.get("caller"),
                        "echo_token": p.get("token"),
                        "echo_command": r.get("command"),
                        "status": "ok",
                    }
                    emit(make_response(r, result=res), log_path)
                pending_requests.clear()
        else:
            res = {
                "echo_command": command,
                "echo_payload": payload,
            }
            emit(make_response(req, result=res), log_path)

    return 0


if __name__ == "__main__":
    sys.exit(main())
