#!/usr/bin/env python3
"""EXPORT-E2E-CLOSE-1 AC2/AC3: independently check the real export artifact and its records.

Runs after the Host export E2E tests (`apps/desktop-avalonia/tests/NewManga.Host.Tests/ExportE2ETests.cs`)
and re-derives every claim from independent sources:

  * the exported ZIP on disk: size, sha256, entry list, manifest page order/sha256,
    per-entry bytes sha256 (must match the manifest and the durable translated revisions),
  * a NEW sidecar process on the same data root: GetExportHistory (completed + cancelled
    records), GetExportSnapshot for both ids, and CancelExport replay on the cancelled id,
  * typed negative: CancelExport/GetExportSnapshot on an unknown id => EXPORT_NOT_FOUND.

Nothing is fabricated: the ZIP bytes, the Core wire answers and the durable DB rows are read
from the artifacts the Host chain actually produced.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import sys
import zipfile
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
from ac1_precheck import (  # noqa: E402  (same-task helper reuse)
    DATA_ROOT,
    SIDECAR,
    TASK_ENV,
    CoreSession,
    sha256_of,
    trace,
    unwrap,
)

EVIDENCE = TASK_ENV / "evidence"
# test.ps1 overrides NEWMANGA_EVIDENCE_DIR to its own evidence root; the canonical
# run used -EvidenceDirectory .../dotnet-full-evidence. Override with --host-evidence.
DOTNET_EVIDENCE = EVIDENCE / "dotnet" / "export"


def load(name: str) -> dict:
    path = DOTNET_EVIDENCE / name
    if not path.exists():
        raise SystemExit(f"missing host-test evidence: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def verify_zip(target: str, expected_pages: list[dict], expected_sha: str) -> dict:
    path = Path(target)
    result = {
        "path": str(path),
        "exists": path.is_file(),
        "bytes": path.stat().st_size if path.is_file() else None,
        "sha256": sha256_of(path) if path.is_file() else None,
        "matches_expected_sha": None,
        "zip_opens": False,
        "entries": [],
        "page_entry_count": 0,
        "manifest_page_count": None,
        "manifest_sha_matches": None,
        "entry_sha_matches_manifest": None,
    }
    if not path.is_file():
        return result
    result["matches_expected_sha"] = result["sha256"] == expected_sha
    expected_by_page = {page["page_id"]: page["translated_sha256"] for page in expected_pages}
    with zipfile.ZipFile(path) as archive:
        result["zip_opens"] = archive.testzip() is None
        names = archive.namelist()
        manifest = json.loads(archive.read("manifest.json").decode("utf-8"))
        result["manifest_page_count"] = len(manifest.get("pages") or [])
        entry_checks = []
        for page in manifest.get("pages") or []:
            name = page["filename"]
            payload = archive.read(name)
            digest = hashlib.sha256(payload).hexdigest()
            entry_checks.append(
                {
                    "filename": name,
                    "entry_sha256": digest,
                    "manifest_sha256": page["sha256"],
                    "matches_manifest": digest == page["sha256"],
                    "matches_durable_translated": digest
                    == expected_by_page.get(page["page_id"]),
                    "bytes": len(payload),
                }
            )
            result["page_entry_count"] += 1
        result["manifest_sha_matches"] = all(
            entry["matches_manifest"] for entry in entry_checks
        )
        result["entry_sha_matches_manifest"] = result["manifest_sha_matches"]
        result["entry_matches_durable_translated"] = all(
            entry["matches_durable_translated"] for entry in entry_checks
        )
        result["entries"] = [
            {"name": name, "bytes": archive.getinfo(name).file_size} for name in names
        ]
        result["entry_checks"] = entry_checks
        result["lineage_entries"] = len(manifest.get("lineage") or [])
    return result


def read_export_history_rows() -> list[dict]:
    connection = sqlite3.connect(
        (DATA_ROOT / "library.db").as_uri() + "?mode=ro", uri=True
    )
    connection.row_factory = sqlite3.Row
    try:
        return [
            dict(row)
            for row in connection.execute(
                "SELECT export_id, book_id, chapter_id, export_type, status,"
                " output_path, file_hash, created_at, completed_at, detail"
                " FROM export_history ORDER BY created_at"
            )
        ]
    finally:
        connection.close()


def prepare_sidecar_start() -> None:
    for stale in ("library.db.run-owner.lock", "derived/.preview-lifecycle.lock"):
        try:
            (DATA_ROOT / stale).unlink()
        except OSError:
            pass


def main() -> int:
    global DOTNET_EVIDENCE
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--host-evidence", default=str(DOTNET_EVIDENCE))
    args = parser.parse_args()
    DOTNET_EVIDENCE = Path(args.host_evidence)

    success = load("export-success.json")
    cancel = load("export-cancel.json")
    cancelled_attempts = [attempt for attempt in cancel["attempts"] if attempt["terminal_status"] == "cancelled"]
    if not cancelled_attempts:
        raise SystemExit("host cancel evidence has no cancelled attempt")
    cancelled = cancelled_attempts[0]

    evidence: dict = {
        "task": "EXPORT-E2E-CLOSE-1",
        "ac": "AC2/AC3",
        "sidecar_core_service_sha256": sha256_of(SIDECAR / "core_service.exe"),
        "data_root": str(DATA_ROOT),
        "host_evidence": {
            "success": success,
            "cancel": cancel,
        },
        "commands": [],
    }

    evidence["artifact_success"] = verify_zip(
        success["target_path"], success["translated_pages"], success["artifact_sha256"]
    )
    # A cancelled export must not publish; the host evidence asserts it; re-check here.
    evidence["cancelled_target_absent"] = not Path(cancelled["target_path"]).exists()

    prepare_sidecar_start()
    session = CoreSession(SIDECAR, DATA_ROOT, TASK_ENV / "ac3-core.stderr.log")
    try:
        for command, payload in (
            ("core.ping", {}),
            ("GetExportHistory", {}),
            ("GetExportSnapshot", {"export_id": success["export_id"]}),
            ("GetExportSnapshot", {"export_id": cancelled["export_id"]}),
            ("CancelExport", {"export_id": cancelled["export_id"]}),
            ("GetExportSnapshot", {"export_id": "exp-does-not-exist"}),
            ("CancelExport", {"export_id": "exp-does-not-exist"}),
            ("GetExportSnapshot", {"export_id": "   "}),
        ):
            response = session.send(command, payload, timeout=60)
            entry = trace(command, response)
            entry["payload"] = payload
            result = unwrap(response) or {}
            if command == "GetExportHistory":
                entry["exports"] = result.get("exports")
            elif command in ("GetExportSnapshot", "CancelExport"):
                declaration = result if isinstance(result, dict) else {}
                entry["snapshot"] = {
                    key: declaration.get(key)
                    for key in ("export_id", "status", "output", "completed_pages", "total_pages")
                }
            evidence["commands"].append(entry)
    finally:
        session.close()

    evidence["export_history_rows"] = read_export_history_rows()
    evidence["history_row_by_id"] = {
        row["export_id"]: row for row in evidence["export_history_rows"]
    }
    out = EVIDENCE / "ac2-ac3-records.json"
    out.write_text(json.dumps(evidence, indent=2, ensure_ascii=False), encoding="utf-8")

    artifact = evidence["artifact_success"]
    print(json.dumps({
        "artifact_bytes": artifact["bytes"],
        "artifact_sha256": artifact["sha256"],
        "matches_expected_sha": artifact["matches_expected_sha"],
        "zip_opens": artifact["zip_opens"],
        "page_entries": artifact["page_entry_count"],
        "manifest_pages": artifact["manifest_page_count"],
        "manifest_sha_matches": artifact["manifest_sha_matches"],
        "entries_match_durable_translated": artifact.get("entry_matches_durable_translated"),
        "cancelled_target_absent": evidence["cancelled_target_absent"],
        "history_rows": [
            (row["export_id"], row["status"]) for row in evidence["export_history_rows"]
        ],
        "wire": [
            {"command": item["command"], "ok": item["ok"], "status": (item.get("snapshot") or {}).get("status"),
             "error": (item.get("error") or {}).get("code")}
            for item in evidence["commands"]
        ],
        "out": str(out),
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
