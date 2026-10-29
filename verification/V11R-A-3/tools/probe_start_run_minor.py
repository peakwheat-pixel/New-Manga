"""V11R-A-3 AC5: empirical check of the library_start_run minor compatibility boundary.

Drives the frozen core_service directly over the JSON-lines application channel and records the
raw response for four StartRun variants:

  (a) minor=3 + ordinary overrides (provider_bindings)      -> must reach the run store
  (b) minor=3 + overrides.provider_profiles                 -> expected INVALID_REQUEST
                                                               ("provider profile overrides require Core 2.6")
  (c) minor=7 + overrides.provider_profiles                 -> P15 wire path (Core >= 2.6)
  (d) minor=7 + ordinary overrides (control)                -> P15 wire path control sample

The command name/scope are constant; the probe only depends on the frozen sidecar copy
(NEWMANGA_CORECLIENT_SIDECAR_DIR) and a throwaway data root.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path

PROTOCOL = "new-manga.core"
SCOPE = {"kind": "book", "book_id": "probe-book-not-in-library"}
ORDINARY_OVERRIDES = {"provider_bindings": {"ocr": "manga-ocr"}}
PROVIDER_PROFILE_OVERRIDES = {
    "provider_profiles": {
        "translation": {
            "provider_id": "openai-compatible",
            "model": "probe-model",
            "endpoint": "http://127.0.0.1:6124",
        }
    }
}


def request(command: str, minor: int, payload: dict) -> str:
    return json.dumps(
        {
            "protocol": PROTOCOL,
            "version": {"major": 2, "minor": minor},
            "request_id": uuid.uuid4().hex,
            "command": command,
            "payload": payload,
        }
    )


def start_run_payload(label: str, overrides: dict, scope: dict | None = None) -> dict:
    return {
        "command": "translate_all",
        "scope": scope or SCOPE,
        "overrides": overrides,
        "idempotency_key": f"v11r-a3-{label}-{uuid.uuid4().hex[:8]}",
    }


def copy_book_fixture(destination: Path) -> bool:
    """Copy the durable BOOK-FIXTURE state into a throwaway data root (same rules as the tests)."""
    source = Path(
        os.environ.get("NEWMANGA_BOOK_FIXTURE_ROOT", "")
        or r"G:\CODEX\New Manga.workspace\task-envs\BOOK-FIXTURE-1\isolated-data"
    )
    if not (source / "library.db").exists():
        return False
    for name in ("derived", "catalog", "managed"):
        (destination / name).mkdir(parents=True, exist_ok=True)
    for path in source.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(source)
        first = relative.parts[0]
        if first in {"logs", "backups", "derived", "catalog"} or path.name.endswith(".lock"):
            continue
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(path.read_bytes())
    return True


def main() -> int:
    sidecar = Path(
        sys.argv[1]
        if len(sys.argv) > 1
        else os.environ.get("NEWMANGA_CORECLIENT_SIDECAR_DIR", "")
        or r"G:\CODEX\New Manga.workspace\task-envs\HOST-CORECLIENT-1\sidecar-copy"
    )
    if sidecar.is_file():
        sidecar = sidecar.parent
    executable = sidecar / "core_service.exe"
    if not executable.exists():
        raise SystemExit(f"core_service.exe not found under {sidecar}")

    root = Path(tempfile.mkdtemp(prefix="v11r-a3-minor-"))
    fixture_copied = copy_book_fixture(root)
    if not fixture_copied:
        for name in ("derived", "catalog", "managed"):
            (root / name).mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    env.update(
        {
            "NEWMANGA_DATA_ROOT": str(root),
            "M2RC1_DERIVED_ROOT": str(root / "derived"),
            "M2RC2_CATALOG_DB": str(root / "catalog" / "catalog.sqlite"),
            "M2RC1_MANAGED_ROOT": str(root / "managed"),
        }
    )
    process = subprocess.Popen(
        [str(executable)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        text=True,
        encoding="utf-8",
        bufsize=1,
        cwd=str(sidecar),
    )
    assert process.stdin and process.stdout

    results: list[dict] = []

    def send(line: str, label: str) -> dict:
        process.stdin.write(line + "\n")
        process.stdin.flush()
        while True:
            reply = process.stdout.readline()
            if reply == "":
                raise SystemExit(f"sidecar exited before answering {label}")
            if '"event_type"' in reply and '"request_id"' not in reply:
                continue
            parsed = json.loads(reply)
            results.append({"label": label, "request": json.loads(line), "response": parsed})
            return parsed

    try:
        send(request("core.ping", 3, {}), "core.ping")
        books = send(request("ListBooks", 3, {}), "ListBooks")
        book_id = None
        result = books.get("result")
        if isinstance(result, list) and result and isinstance(result[0], dict):
            book_id = result[0].get("book_id")
        scope = {"kind": "book", "book_id": book_id} if book_id else SCOPE
        print(f"probe scope book_id={book_id} (fixture_copied={fixture_copied})")
        send(
            request("StartRun", 3, start_run_payload("a", ORDINARY_OVERRIDES, scope)),
            "a: StartRun minor=3 ordinary overrides",
        )
        send(
            request("StartRun", 3, start_run_payload("b", PROVIDER_PROFILE_OVERRIDES, scope)),
            "b: StartRun minor=3 provider_profiles overrides",
        )
        send(
            request("StartRun", 7, start_run_payload("c", PROVIDER_PROFILE_OVERRIDES, scope)),
            "c: StartRun minor=7 provider_profiles overrides",
        )
        send(
            request("StartRun", 7, start_run_payload("d", ORDINARY_OVERRIDES, scope)),
            "d: StartRun minor=7 ordinary overrides",
        )
    finally:
        try:
            process.stdin.close()
        except Exception:
            pass
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
        stderr = process.stderr.read() if process.stderr else ""
        if stderr.strip():
            print("--- stderr tail ---")
            print(stderr.strip()[-1500:])

    for item in results:
        request_payload = item["request"]["payload"]
        response = item["response"]
        error = response.get("error")
        print(f"--- {item['label']} ---")
        print(
            json.dumps(
                {
                    "minor": item["request"]["version"]["minor"],
                    "overrides_keys": sorted((request_payload.get("overrides") or {}).keys()),
                    "result": response.get("result"),
                    "error": error,
                },
                ensure_ascii=False,
            )
        )

    output = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    if output:
        output.write_text(
            json.dumps(
                {
                    "task": "V11R-A-3",
                    "ac": "AC5 library_start_run minor compatibility",
                    "sidecar": str(sidecar),
                    "data_root": str(root),
                    "results": results,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
