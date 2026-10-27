#!/usr/bin/env python3
"""RELEASE-REPACK-2 AC2/AC3 same-build probe.

Spawns the freshly repacked ``core_service.exe`` (models variant), starts a
``translate_untranslated`` Run on the BOOK-FIXTURE 8-page book with the identity
translation binding, polls ``GetTaskProjection`` from a second thread every
100 ms (the RUN-STORE-CACHE-RACE-FIX-1 projection-fresh topology, over the real
wire), and records:

  * per-page task/step statuses (via the final task projection),
  * per-step-type wall-clock durations (from the CurrentPageStepChanged event
    stream; the Core persists no step timestamps),
  * step_runs statistics from the isolated run DB: status counts per type,
    stuck ``running`` rows, regionless ``INVALID_INPUT`` rows,
  * all typed errors (must contain no PROVIDER_NOT_CONFIGURED).

Nothing is faked: every value comes from the spawned exe, its event frames, or
the run DB it wrote.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import queue
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
TASK_ENV = Path(r"G:\CODEX\New Manga.workspace\task-envs\RELEASE-REPACK-2")
FIXTURE_ROOT = Path(r"G:\CODEX\New Manga.workspace\task-envs\BOOK-FIXTURE-1\isolated-data")
PROTOCOL = "new-manga.core"
PROTOCOL_VERSION = {"major": 2, "minor": 3}
BOOK_ID = "14340ddad0ed472fbe687fe12340c5d8"

TERMINAL = {"completed", "completed_with_failures", "failed", "cancelled", "interrupted"}


class CoreSession:
    """Line-protocol client with a background reader thread (events + responses)."""

    def __init__(self, sidecar: Path, data_root: Path, log_path: Path):
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
        self.events: list[dict] = []
        self._responses: dict[str, dict] = {}
        self._cond = threading.Condition()
        self._lock = threading.Lock()
        self._request_id = 0
        self._closing = False
        self._reader = threading.Thread(target=self._read_loop, name="wire-reader", daemon=True)
        self._reader.start()

    def _read_loop(self) -> None:
        stdout = self.process.stdout
        assert stdout is not None
        while not self._closing:
            line = stdout.readline()
            if not line:
                return
            try:
                frame = json.loads(line.decode("utf-8"))
            except json.JSONDecodeError:
                continue
            now = time.monotonic()
            if "request_id" in frame:
                with self._cond:
                    self._responses[frame["request_id"]] = frame
                    self._cond.notify_all()
            elif "event_type" in frame:
                with self._lock:
                    self.events.append({"recv": now, "frame": frame})

    def send(self, command: str, payload: dict, timeout: float = 120.0) -> dict:
        with self._cond:
            self._request_id += 1
            request_id = f"rr2-{command}-{self._request_id}"
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
        with self._cond:
            while request_id not in self._responses:
                remaining = timeout - (time.monotonic() - started)
                if remaining <= 0:
                    return {"request_id": request_id, "error": {"code": "PROBE_TIMEOUT"}}
                self._cond.wait(remaining)
            response = self._responses.pop(request_id)
        response["_elapsed_ms"] = round((time.monotonic() - started) * 1000, 1)
        return response

    def close(self) -> None:
        self._closing = True
        try:
            self.process.terminate()
            self.process.wait(timeout=20)
        except Exception:  # noqa: BLE001
            try:
                self.process.kill()
            except Exception:  # noqa: BLE001
                pass
        try:
            self.stderr.close()
        except Exception:  # noqa: BLE001
            pass


def unwrap(response: dict) -> dict | None:
    if response.get("error") is not None or response.get("result") is None:
        return None
    result = response["result"]
    return result.get("result", result) if isinstance(result, dict) else result


def trace(command: str, response: dict) -> dict:
    entry = {
        "command": command,
        "elapsed_ms": response.get("_elapsed_ms"),
        "ok": response.get("error") is None and response.get("result") is not None,
    }
    if not entry["ok"]:
        error = response.get("error") or {}
        entry["error"] = {"code": error.get("code"), "message": error.get("message")}
    return entry


def prepare_data_root(tag: str) -> Path:
    root = TASK_ENV / "data-roots" / ("data-root-" + tag)
    if root.exists():
        shutil.rmtree(root, ignore_errors=True)
    shutil.copytree(FIXTURE_ROOT, root)
    for pat in (
        "derived/.preview-lifecycle.lock",
        "library.db.run-owner.lock",
        "catalog/catalog.sqlite",
        "catalog/catalog.sqlite-wal",
        "catalog/catalog.sqlite-shm",
        "library.db-wal",
        "library.db-shm",
    ):
        p = root / pat
        try:
            if p.exists():
                p.unlink()
        except OSError:
            pass
    for sub in ("derived", "catalog", "managed"):
        (root / sub).mkdir(parents=True, exist_ok=True)
    return root


def step_type_durations(events: list[dict], run_id: str) -> dict:
    """Per-step-type wall clock from CurrentPageStepChanged transitions."""
    marks: list[tuple[float, str]] = []
    for entry in events:
        frame = entry["frame"]
        if frame.get("event_type") != "CurrentPageStepChanged":
            continue
        payload = frame.get("payload") or {}
        if payload.get("run_id") != run_id:
            continue
        step = payload.get("current_step_type") or ""
        if not step:
            continue
        marks.append((entry["recv"], step))
    durations: dict[str, float] = {}
    for index, (when, step) in enumerate(marks):
        end = marks[index + 1][0] if index + 1 < len(marks) else (marks[-1][0] if marks else when)
        durations[step] = durations.get(step, 0.0) + max(0.0, end - when)
    return {key: round(value * 1000, 1) for key, value in durations.items()}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sidecar", required=True)
    parser.add_argument("--out", default=str(TASK_ENV / "full-chain-run.json"))
    parser.add_argument("--tag", default="full-chain")
    parser.add_argument("--poll-ms", type=int, default=100)
    args = parser.parse_args(argv)

    sidecar = Path(args.sidecar)
    exe = sidecar / "core_service.exe"
    if not exe.exists():
        raise SystemExit(f"missing core_service.exe under {sidecar}")
    data_root = prepare_data_root(args.tag)
    evidence: dict = {
        "task": "RELEASE-REPACK-2",
        "ac": "AC2/AC3",
        "sidecar": str(sidecar),
        "sidecar_core_service_sha256": hashlib.sha256(exe.read_bytes()).hexdigest(),
        "sidecar_core_service_bytes": exe.stat().st_size,
        "data_root": str(data_root),
        "book_id": BOOK_ID,
        "commands": [],
        "run_timeline": [],
        "projection_polls": 0,
    }

    session = CoreSession(sidecar, data_root, TASK_ENV / f"{args.tag}-core.stderr.log")
    projection_thread_stop = threading.Event()
    poll_errors: list[str] = []
    polls = {"count": 0}
    run_id_box: dict[str, str] = {}

    def projection_poller() -> None:
        while not projection_thread_stop.is_set():
            run_id = run_id_box.get("run_id")
            if run_id:
                response = session.send("GetTaskProjection", {"run_id": run_id}, timeout=60)
                polls["count"] += 1
                if response.get("error") is not None:
                    poll_errors.append(str(response["error"].get("code")))
            projection_thread_stop.wait(args.poll_ms / 1000)

    try:
        ping = session.send("core.ping", {})
        evidence["commands"].append(trace("core.ping", ping))
        chapters_response = session.send("list_chapters", {"book_id": BOOK_ID})
        evidence["commands"].append(trace("list_chapters", chapters_response))
        chapters = (unwrap(chapters_response) or {}).get("chapters") or []
        chapter_id = chapters[0].get("chapter_id") if chapters else None
        evidence["chapter_id"] = chapter_id
        if chapter_id:
            pages_response = session.send("list_chapter_pages", {"chapter_id": chapter_id})
            evidence["commands"].append(trace("list_chapter_pages", pages_response))
            pages_payload = unwrap(pages_response) or {}
            evidence["page_count"] = len(pages_payload.get("pages") or [])
        overrides = {"provider_bindings": {"ocr": "manga-ocr", "translate": "identity-translation"}}
        evidence["overrides"] = overrides
        start = session.send(
            "StartRun",
            {
                "command": "translate_untranslated",
                "scope": {"kind": "book", "book_id": BOOK_ID},
                "overrides": overrides,
                "idempotency_key": "release-repack-2-full-chain",
            },
            timeout=120,
        )
        evidence["commands"].append(trace("StartRun", start))
        run_id = (unwrap(start) or {}).get("run_id")
        evidence["run_id"] = run_id
        if run_id:
            run_id_box["run_id"] = run_id
            poller = threading.Thread(target=projection_poller, name="projection-poller", daemon=True)
            poller.start()
            started = time.monotonic()
            last_status = None
            status = None
            while time.monotonic() - started < 900:
                snapshot = session.send("GetRunSnapshot", {"run_id": run_id}, timeout=30)
                status = (unwrap(snapshot) or {}).get("status")
                if status != last_status:
                    evidence["run_timeline"].append(
                        {"t_ms": round((time.monotonic() - started) * 1000, 1), "status": status}
                    )
                    last_status = status
                if status in TERMINAL:
                    break
                time.sleep(0.5)
            evidence["run_terminal_status"] = status
            evidence["run_elapsed_ms"] = round((time.monotonic() - started) * 1000, 1)
            projection_thread_stop.set()
            poller.join(timeout=10)
            final_projection = session.send("GetTaskProjection", {"run_id": run_id}, timeout=60)
            evidence["commands"].append(trace("GetTaskProjection", final_projection))
            projection = unwrap(final_projection) or {}
            evidence["task_projection"] = projection
            evidence["projection_polls"] = polls["count"]
            evidence["projection_poll_errors"] = poll_errors[:20]
            evidence["step_type_durations_ms"] = step_type_durations(session.events, run_id)

            import sqlite3

            db = sqlite3.connect(data_root / "library.db")
            try:
                db.row_factory = sqlite3.Row
                by_type = [
                    dict(row)
                    for row in db.execute(
                        "SELECT step_type, status, COUNT(*) AS n FROM step_runs "
                        "WHERE pipeline_run_id = ? GROUP BY step_type, status ORDER BY step_type, status",
                        (run_id,),
                    )
                ]
                stuck = [
                    dict(row)
                    for row in db.execute(
                        "SELECT step_run_id, step_type, unit_id FROM step_runs "
                        "WHERE pipeline_run_id = ? AND status = 'running'",
                        (run_id,),
                    )
                ]
                regionless_invalid = [
                    dict(row)
                    for row in db.execute(
                        "SELECT step_run_id, step_type, unit_id, error_code FROM step_runs "
                        "WHERE pipeline_run_id = ? AND error_code = 'INVALID_INPUT' AND region_id IS NULL",
                        (run_id,),
                    )
                ]
                provider_not_configured = [
                    dict(row)
                    for row in db.execute(
                        "SELECT step_run_id, step_type, unit_id, error_code FROM step_runs "
                        "WHERE pipeline_run_id = ? AND error_code = 'PROVIDER_NOT_CONFIGURED'",
                        (run_id,),
                    )
                ]
                run_status = dict(
                    db.execute(
                        "SELECT status FROM pipeline_runs WHERE run_id = ?", (run_id,)
                    ).fetchone()
                    or {}
                )
            finally:
                db.close()
            evidence["step_runs_by_type"] = by_type
            evidence["stuck_running"] = stuck
            evidence["regionless_invalid_input"] = regionless_invalid
            evidence["provider_not_configured"] = provider_not_configured
            evidence["db_run_status"] = run_status.get("status")
        evidence["events"] = [
            {
                "event_type": entry["frame"].get("event_type"),
                "payload": entry["frame"].get("payload"),
            }
            for entry in session.events
        ][:5000]
    finally:
        projection_thread_stop.set()
        session.close()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary = {
        "ac": "AC2/AC3",
        "sidecar_sha256": evidence["sidecar_core_service_sha256"],
        "run_id": evidence.get("run_id"),
        "terminal": evidence.get("run_terminal_status"),
        "elapsed_ms": evidence.get("run_elapsed_ms"),
        "projection_polls": evidence.get("projection_polls"),
        "step_type_durations_ms": evidence.get("step_type_durations_ms"),
        "stuck_running": len(evidence.get("stuck_running") or []),
        "regionless_invalid_input": len(evidence.get("regionless_invalid_input") or []),
        "provider_not_configured": len(evidence.get("provider_not_configured") or []),
        "step_runs_by_type": evidence.get("step_runs_by_type"),
        "out": str(out),
    }
    print("RESULT " + json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
