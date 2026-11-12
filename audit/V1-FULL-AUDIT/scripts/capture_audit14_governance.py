#!/usr/bin/env python3
"""Capture the four required governance gates for an AUDIT-14 stage head."""

from __future__ import annotations

import datetime as dt
import json
import subprocess
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / "audit" / "V1-FULL-AUDIT"
TASK = "doc/tasks/NEW-MANGA-V1-FULL-AUDIT.md"
STAMP = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
LOG_PATH = AUDIT / "logs" / f"audit14-governance-{STAMP}.log"
JSON_PATH = AUDIT / "evidence" / f"audit14-governance-{STAMP}.json"
COMMANDS = [
    ["pwsh", "-NoProfile", "-File", "tools/governance/check.ps1"],
    ["pwsh", "-NoProfile", "-File", "tools/governance/check.ps1", "-TaskPath", TASK],
    ["pwsh", "-NoProfile", "-File", "tools/governance/verify_pins.ps1"],
    ["python", "tools/generate_api_inventory.py", "--check"],
]


def run(argv: list[str]) -> dict[str, object]:
    start = time.monotonic()
    result = subprocess.run(
        argv,
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    return {
        "argv": argv,
        "cwd": str(ROOT),
        "shell": False,
        "interpreter": argv[0],
        "elapsed_seconds": round(time.monotonic() - start, 6),
        "exit": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def main() -> int:
    generated_at = dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")
    head = run(["git", "rev-parse", "HEAD"])
    branch = run(["git", "branch", "--show-current"])
    status = run(["git", "status", "--porcelain"])
    results = [run(command) for command in COMMANDS]
    record = {
        "schema": "audit14-governance/v1",
        "generated_at_utc": generated_at,
        "generated_head": str(head["stdout"]).strip(),
        "branch": str(branch["stdout"]).strip(),
        "git_status_porcelain": status["stdout"],
        "git_status_exit": status["exit"],
        "commands": [head, branch, status, *results],
    }
    JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    JSON_PATH.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    lines = [
        "AUDIT-14 governance gates",
        f"generated_at_utc={generated_at}",
        f"generated_head={record['generated_head']}",
        f"branch={record['branch']}",
        f"cwd={ROOT}",
        f"git_status_exit={status['exit']}",
        f"json={JSON_PATH.relative_to(ROOT).as_posix()}",
    ]
    for result in record["commands"]:
        lines.extend(
            [
                "",
                f"argv={json.dumps(result['argv'], ensure_ascii=False)}",
                f"shell={result.get('shell', False)} interpreter={result.get('interpreter', result['argv'][0])} cwd={result.get('cwd', ROOT)}",
                f"elapsed_seconds={result.get('elapsed_seconds', 0)} EXIT={result['exit']}",
                "stdout:",
                str(result["stdout"]).rstrip("\n"),
            ]
        )
        if result["stderr"]:
            lines.extend(["stderr:", str(result["stderr"]).rstrip("\n")])
    LOG_PATH.write_text("\n".join(lines).rstrip("\n") + "\n", encoding="utf-8", newline="\n")
    print(f"generated_head={record['generated_head']}")
    print(f"log={LOG_PATH.relative_to(ROOT).as_posix()}")
    print(f"json={JSON_PATH.relative_to(ROOT).as_posix()}")
    print("exits=" + ",".join(str(result["exit"]) for result in results))
    return 1 if any(result["exit"] != 0 for result in [head, branch, status, *results]) else 0


if __name__ == "__main__":
    raise SystemExit(main())
