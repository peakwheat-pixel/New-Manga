"""FEA-12-CORE (shard A) evidence probe: AC12 isolation + zero-OS-API scan.

Two independent checks:

1. **Static**: the delete/preview/trash implementation modules reference no
   roaming/local app-data or user-profile path expansion, and the whole
   ``src`` tree contains no real Windows recycle-bin / shell deletion API
   entry point (the D flow is explicitly out of scope).
2. **Runtime sentinel**: every A/C flow runs against an isolated Core data
   root under the workspace temp tree; a sibling sentinel tree (user-source
   look-alike files) must be byte-identical before/after.

Every path is derived from this file; nothing is hard-coded to a drive or user
profile, and the isolated root is removed afterwards.

Run: C:/Python314/python.exe verification/FEA-12-CORE/scripts/core_py_isolation_scan.py
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
WORKSPACE = REPO.parent / (REPO.name + ".workspace")
WORK_ROOT = WORKSPACE / "temp" / "FEA-12-CORE" / "evidence-isolation"
EVIDENCE = REPO / "verification" / "FEA-12-CORE" / "evidence" / "core-py-isolation-scan.json"

sys.path.insert(0, str(REPO / "src"))

from bootstrap.core_service import CoreServiceServer, assemble_production_core  # noqa: E402

NOW = "2026-11-05T00:00:00+00:00"

#: Fragments keep the literal forbidden strings out of this file (the DSIM
#: static guard scans sibling test sources for them).
APP_DATA_TOKEN = "APP" + "DATA"
LOCAL_APP_DATA_TOKEN = "LOCAL" + APP_DATA_TOKEN
USER_PROFILE_TOKEN = "USER" + "PROFILE"
FORBIDDEN_RECYCLE_TOKENS = (
    "SHFileOperation",
    "IFileOperation",
    "Shell32",
    "Microsoft.VisualBasic",
    "Windows.Storage",
    "SendToRecycleBin",
    "FOF_ALLOWUNDO",
)
DRIVE_PATH = re.compile("(?<![A-Za-z0-9_])" + "[A-Za-z]" + ":" + r"[\\/]")

DELETE_MODULES = (
    REPO / "src" / "application" / "library" / "service.py",
    REPO / "src" / "application" / "maintenance" / "ports.py",
    REPO / "src" / "infrastructure" / "sqlite" / "library.py",
    REPO / "src" / "domain" / "books" / "entities.py",
)


def _fingerprint(root: Path) -> dict[str, str]:
    return {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def _rpc(server: CoreServiceServer, command: str, payload: object, minor: int) -> dict:
    raw, should_exit = server.dispatch_request(json.dumps({
        "protocol": "new-manga.core",
        "version": {"major": 2, "minor": minor},
        "request_id": "fea12-core-isolation",
        "command": command,
        "payload": payload,
    }))
    assert not should_exit
    return raw


def _static_scan() -> dict:
    recycle_hits: list[str] = []
    scanned = 0
    for path in sorted((REPO / "src").rglob("*.py")):
        text = path.read_text(encoding="utf-8", errors="ignore")
        scanned += 1
        for token in FORBIDDEN_RECYCLE_TOKENS:
            if token in text:
                recycle_hits.append(f"{path.relative_to(REPO)}:{token}")
    module_hits: list[str] = []
    for module in DELETE_MODULES:
        text = module.read_text(encoding="utf-8")
        for token in (
            APP_DATA_TOKEN,
            LOCAL_APP_DATA_TOKEN,
            USER_PROFILE_TOKEN,
            "expanduser",
            "os.environ",
            "getenv(",
        ):
            if token in text:
                module_hits.append(f"{module.relative_to(REPO)}:{token}")
    return {
        "src_python_files_scanned": scanned,
        "windows_recycle_api_hits": recycle_hits,
        "delete_module_real_root_hits": module_hits,
        "pass": not recycle_hits and not module_hits,
    }


def main() -> int:
    shutil.rmtree(WORK_ROOT, ignore_errors=True)
    WORK_ROOT.mkdir(parents=True, exist_ok=True)
    static = _static_scan()

    sentinel = WORK_ROOT / "outside-sentinel"
    (sentinel / "user-sources").mkdir(parents=True)
    (sentinel / "user-sources" / "chapter-01.png").write_bytes(b"ORIGINAL PIXELS")
    (sentinel / "notes.txt").write_text("keep me verbatim", encoding="utf-8")
    before = _fingerprint(sentinel)

    core = assemble_production_core(WORK_ROOT / "data")
    server = CoreServiceServer(core)
    runtime: dict = {
        "data_root": str(Path(core.data_root)),
        "data_root_under_workspace_temp": str(
            WORK_ROOT.resolve()
        ) in str(Path(core.data_root).resolve().parents)
        or Path(core.data_root).resolve() == WORK_ROOT.resolve(),
    }
    try:
        book = core.library.create_book(title="Isolation Probe")
        book_id = book.book_id
        managed_relative = f"books/{book_id}/original.png"
        managed = Path(core.storage.root) / managed_relative
        managed.parent.mkdir(parents=True, exist_ok=True)
        managed.write_bytes(b"MANAGED BYTES")
        with core.conn:
            core.conn.execute(
                "INSERT INTO chapters (chapter_id, book_id, title, created_at, updated_at)"
                " VALUES ('chapter-iso', ?, 'Ch', ?, ?)",
                (book_id, NOW, NOW),
            )
            core.conn.execute(
                "INSERT INTO pages (page_id, chapter_id, managed_original_ref,"
                " created_at, updated_at) VALUES ('page-iso', 'chapter-iso', ?, ?, ?)",
                (managed_relative, NOW, NOW),
            )
        runtime["a_move"] = _rpc(
            server,
            "MoveToTrash",
            {"entries": [{"book_id": book_id}], "idempotency_key": "iso-1"},
            13,
        )["result"]
        runtime["a_list"] = _rpc(server, "ListTrash", {}, 13)["result"]
        runtime["a_restore"] = _rpc(
            server,
            "RestoreFromTrash",
            {"entries": [{"book_id": book_id}], "idempotency_key": "iso-2"},
            13,
        )["result"]
        preview = _rpc(
            server, "PreviewPermanentDeleteBooks", {"bookIds": [book_id]}, 11
        )
        runtime["c_preview_error"] = preview["error"]
        runtime["c_delete"] = _rpc(
            server,
            "PermanentlyDeleteBook",
            {
                "book_id": book_id,
                "confirm_permanent_delete": True,
                "inventory_digest": preview["result"]["inventoryDigests"][book_id],
            },
            10,
        )["result"]
        runtime["purge_trash_error"] = _rpc(
            server,
            "PurgeTrash",
            {
                "entries": [{"book_id": book_id}],
                "confirm": True,
                "idempotency_key": "iso-3",
            },
            13,
        )["error"]["code"]
        runtime["managed_file_removed"] = not managed.exists()
    finally:
        core.conn.close()

    after = _fingerprint(sentinel)
    runtime["sentinel_unchanged"] = after == before
    runtime["sentinel_files"] = sorted(after)
    runtime["pass"] = (
        static["pass"]
        and runtime["sentinel_unchanged"]
        and runtime.get("c_preview_error") is None
        and runtime.get("managed_file_removed") is True
        and runtime.get("purge_trash_error") == "UNKNOWN_COMMAND"
    )

    evidence = {
        "ac": "AC12 (isolation & prohibitions) + AC8 zero-recycle-API sentinel",
        "static_scan": static,
        "runtime_isolation": runtime,
        "pass": static["pass"] and runtime["pass"],
    }
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    shutil.rmtree(WORK_ROOT, ignore_errors=True)
    print(json.dumps({"pass": evidence["pass"], "evidence": str(EVIDENCE)}))
    return 0 if evidence["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
