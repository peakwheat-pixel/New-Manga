#!/usr/bin/env python3
"""EXPORT-E2E-CLOSE-1 AC1: precheck the translated artifacts on the RELEASE-REPACK-2 sidecar.

Uses the data root produced by RELEASE-REPACK-2's same-build 8-page full-chain Run
(copied into this task env so the other task's evidence stays read-only), starts the
NEW sidecar ``c5531930…`` on it, and records:

  * the completed Run record (run id / status / sidecar build provenance),
  * ``GetReaderProjection(mode=translated)``: per page translated revision/sha/resource,
  * ``GetExportHistory``: no export exists yet (the export is the thing this task adds),
  * the durable page rows (translated_path/sha) + on-disk translated files and their sha256.

Nothing is fabricated: every value is read from the spawned exe, its wire responses, the
run DB, or the files on disk.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

TASK_ENV = Path(r"G:\CODEX\New Manga.workspace\task-envs\EXPORT-E2E-CLOSE-1")
REPACK2_RUN_ROOT = Path(
    r"G:\CODEX\New Manga.workspace\task-envs\RELEASE-REPACK-2\data-roots\data-root-full-chain"
)
REPACK2_RUN_JSON = Path(
    r"G:\CODEX\New Manga.workspace\task-envs\RELEASE-REPACK-2\full-chain-run.json"
)
SIDECAR = Path(
    r"G:\CODEX\New Manga.workspace\task-envs\RELEASE-REPACK-2\out"
    r"\NewManga-0.1.0-win-x64-models\app\core-sidecar"
)
DATA_ROOT = TASK_ENV / "data-root"
EVIDENCE = TASK_ENV / "evidence"
BOOK_ID = "14340ddad0ed472fbe687fe12340c5d8"
CHAPTER_ID = "240bdba549b74281bfc6d901b1a7abd7"
PROTOCOL = "new-manga.core"
PROTOCOL_VERSION = {"major": 2, "minor": 3}


class CoreSession:
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
        self._request_id = 0

    def send(self, command: str, payload: dict, timeout: float = 60.0) -> dict:
        self._request_id += 1
        request_id = f"ac1-{command}-{self._request_id}"
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
                frame = json.loads(line.decode("utf-8"))
            except json.JSONDecodeError:
                continue
            if frame.get("request_id") != request_id:
                continue
            frame["_elapsed_ms"] = round((time.monotonic() - started) * 1000, 1)
            return frame
        return {"request_id": request_id, "error": {"code": "PROBE_TIMEOUT"}}

    def close(self) -> None:
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
    entry = {"command": command, "elapsed_ms": response.pop("_elapsed_ms", None),
             "ok": response.get("error") is None and response.get("result") is not None}
    if not entry["ok"]:
        error = response.get("error") or {}
        entry["error"] = {"code": error.get("code"), "message": error.get("message")}
    return entry


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def prepare_data_root() -> Path:
    if DATA_ROOT.exists():
        shutil.rmtree(DATA_ROOT, ignore_errors=True)
    shutil.copytree(REPACK2_RUN_ROOT, DATA_ROOT)
    for stale in (
        "library.db.run-owner.lock",
        "derived/.preview-lifecycle.lock",
        # The preview-namespace catalog binding is tied to the original derived
        # root identity; a copy must drop the catalog DB (rebuildable preview
        # cache) and let the sidecar re-create the binding, exactly like the
        # REPACK-2 fresh-copy preparation did.
        "catalog/catalog.sqlite",
        "catalog/catalog.sqlite-wal",
        "catalog/catalog.sqlite-shm",
    ):
        try:
            (DATA_ROOT / stale).unlink()
        except OSError:
            pass
    return DATA_ROOT


def db_rows(root: Path) -> dict:
    """Read the run DB *after* the sidecar closed (durable rows only)."""
    uri = (root / "library.db").as_uri() + "?mode=ro"
    connection = sqlite3.connect(uri, uri=True)
    connection.row_factory = sqlite3.Row
    try:
        runs = []
        for row in connection.execute(
            "SELECT run_id, command_type, scope_type, status,"
            " provider_binding_snapshot_json, updated_at, run_json"
            " FROM pipeline_runs ORDER BY rowid DESC LIMIT 3"
        ):
            item = dict(row)
            try:
                run_json = json.loads(item.pop("run_json") or "{}")
                item["completed_at"] = run_json.get("completed_at")
                item["started_at"] = run_json.get("started_at")
            except json.JSONDecodeError:
                item["completed_at"] = None
            runs.append(item)
        pages = [dict(row) for row in connection.execute(
            "SELECT p.page_id, p.sort_order, p.source_order, p.width, p.height,"
            " ma.artifact_id AS translated_artifact_id,"
            " ma.current_revision_id AS translated_revision_id,"
            " ar.managed_path AS translated_managed_path,"
            " ar.file_hash AS translated_sha256,"
            " ar.size_bytes AS translated_size_bytes,"
            " ar.pipeline_run_id AS translated_source_run_id,"
            " ar.mime_type AS translated_mime_type"
            " FROM pages p"
            " JOIN media_artifacts ma ON ma.page_id = p.page_id AND ma.artifact_type = 'translated'"
            " JOIN artifact_revisions ar ON ar.artifact_revision_id = ma.current_revision_id"
            " AND ar.artifact_id = ma.artifact_id"
            " ORDER BY p.sort_order"
        )]
        return {"runs": runs, "pages": pages}
    finally:
        connection.close()


def main() -> int:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    exe = SIDECAR / "core_service.exe"
    if not exe.exists():
        raise SystemExit(f"missing sidecar exe: {exe}")
    data_root = prepare_data_root()
    evidence: dict = {
        "task": "EXPORT-E2E-CLOSE-1",
        "ac": "AC1",
        "sidecar": str(SIDECAR),
        "sidecar_core_service_sha256": sha256_of(exe),
        "sidecar_core_service_bytes": exe.stat().st_size,
        "source_run_root": str(REPACK2_RUN_ROOT),
        "copied_data_root": str(data_root),
        "book_id": BOOK_ID,
        "chapter_id": CHAPTER_ID,
        "commands": [],
    }
    session = CoreSession(SIDECAR, data_root, TASK_ENV / "ac1-core.stderr.log")
    try:
        for command, payload in (
            ("core.ping", {}),
            ("list_chapters", {"book_id": BOOK_ID}),
            ("list_chapter_pages", {"chapter_id": CHAPTER_ID}),
            ("GetExportHistory", {}),
            ("GetReaderProjection", {"chapter_id": CHAPTER_ID, "mode": "translated", "start_position": "beginning"}),
        ):
            response = session.send(command, payload, timeout=120)
            evidence["commands"].append(trace(command, response))
            result = unwrap(response) or {}
            if command == "list_chapter_pages":
                evidence["page_count"] = len(result.get("pages") or [])
                evidence["pages"] = [
                    {key: page.get(key) for key in ("page_id", "source_filename", "sort_order")}
                    for page in (result.get("pages") or [])
                ]
            elif command == "GetExportHistory":
                evidence["export_history"] = result
            elif command == "GetReaderProjection":
                translated_pages = []
                for page in result.get("pages") or []:
                    translated = page.get("translated") or {}
                    translated_pages.append({
                        "page_id": page.get("page_id"),
                        "order": page.get("order"),
                        "translated_artifact_revision_id": translated.get("artifact_revision_id"),
                        "translated_sha256": translated.get("sha256"),
                        "translated_resource_ref": translated.get("resource_ref"),
                        "original_sha256": (page.get("original") or {}).get("sha256"),
                    })
                evidence["reader_projection"] = translated_pages
                evidence["translated_pages"] = [
                    page for page in translated_pages if page["translated_artifact_revision_id"]
                ]
    finally:
        session.close()

    # durable rows + on-disk files (sidecar closed above)
    rows = db_rows(data_root)
    evidence["run_rows"] = rows["runs"]
    managed = data_root
    page_rows = []
    for row in rows["pages"]:
        translated_path = row.get("translated_managed_path")
        entry = {
            key: row.get(key) for key in (
                "page_id", "source_order", "sort_order", "width", "height",
                "translated_managed_path", "translated_sha256", "translated_revision_id",
                "translated_artifact_id", "translated_size_bytes", "translated_mime_type",
                "translated_source_run_id",
            )
        }
        if translated_path:
            candidate = Path(translated_path)
            absolute = candidate if candidate.is_absolute() else managed / "managed" / candidate
            entry["translated_file_exists"] = absolute.is_file()
            entry["translated_file_bytes"] = absolute.stat().st_size if absolute.is_file() else None
            entry["translated_file_sha256"] = sha256_of(absolute) if absolute.is_file() else None
            entry["translated_file_match"] = (
                entry["translated_file_sha256"] == row.get("translated_sha256")
                if absolute.is_file() else False
            )
        page_rows.append(entry)
    evidence["page_rows"] = page_rows
    evidence["translated_page_count"] = sum(
        1 for page in page_rows if page.get("translated_managed_path")
    )
    evidence["read_only_source_root_note"] = (
        "RELEASE-REPACK-2's completed-run data root was copied into this task env; the other "
        "task's evidence root was not modified."
    )
    if REPACK2_RUN_JSON.exists():
        upstream = json.loads(REPACK2_RUN_JSON.read_text(encoding="utf-8"))
        evidence["upstream_run"] = {
            "task": upstream.get("task"),
            "run_id": upstream.get("run_id"),
            "run_terminal_status": upstream.get("run_terminal_status"),
            "run_elapsed_ms": upstream.get("run_elapsed_ms"),
            "sidecar_core_service_sha256": upstream.get("sidecar_core_service_sha256"),
            "step_counts": upstream.get("step_counts"),
        }

    out = EVIDENCE / "ac1-precheck.json"
    out.write_text(json.dumps(evidence, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({
        "sidecar_sha256": evidence["sidecar_core_service_sha256"],
        "translated_page_count": evidence["translated_page_count"],
        "export_history": evidence.get("export_history"),
        "translated_pages": [
            {"page_id": page["page_id"], "sha": page["translated_sha256"]}
            for page in evidence.get("translated_pages", [])
        ],
        "run_rows": [(run.get("run_id"), run.get("status")) for run in evidence["run_rows"]],
        "out": str(out),
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
