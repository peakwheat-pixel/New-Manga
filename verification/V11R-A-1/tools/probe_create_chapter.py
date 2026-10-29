"""Probe the frozen sidecar copy for CreateChapter protocol minor 8 behaviour.

Read-only diagnostic: spawns core_service.exe in a throwaway data root, drives the
JSON-lines application channel, and prints the raw responses for:
  1. core.ping (minor 3)
  2. CreateBook (minor 8)
  3. CreateChapter (minor 8) valid payload
  4. CreateChapter (minor 8) blank title
  5. CreateChapter (minor 8) unknown book id
  6. CreateChapter (minor 8) empty payload
  7. CreateChapter (minor 3) wrong minor
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


def main() -> int:
    sidecar = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
        r"G:\CODEX\New Manga.workspace\task-envs\HOST-CORECLIENT-1\sidecar-copy\core_service.exe"
    )
    root = Path(tempfile.mkdtemp(prefix="v11r-probe-"))
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
        [str(sidecar)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        text=True,
        encoding="utf-8",
        bufsize=1,
        cwd=str(sidecar.parent),
    )
    assert process.stdin and process.stdout

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
            print(f"--- {label} ---")
            print(json.dumps(parsed, ensure_ascii=False, indent=2))
            return parsed

    try:
        send(request("core.ping", 3, {}), "core.ping minor=3")
        created = send(request("CreateBook", 8, {"title": "probe book"}), "CreateBook minor=8")
        book_id = (created.get("result") or {}).get("book_id", "missing-book")
        send(
            request("CreateChapter", 8, {"book_id": book_id, "title": "第 1 章"}),
            "CreateChapter valid",
        )
        send(
            request("CreateChapter", 8, {"book_id": book_id, "title": "   "}),
            "CreateChapter blank title",
        )
        send(
            request("CreateChapter", 8, {"book_id": "no-such-book", "title": "x"}),
            "CreateChapter unknown book",
        )
        send(request("CreateChapter", 8, {}), "CreateChapter empty payload")
        send(
            request("CreateChapter", 3, {"book_id": book_id, "title": "x"}),
            "CreateChapter wrong minor=3",
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
            print("--- stderr ---")
            print(stderr.strip()[-2000:])
    print(f"data root: {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
