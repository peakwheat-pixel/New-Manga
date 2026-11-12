"""Capture the four read-only governance gates with HEAD and EXIT metadata."""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / "audit/V1-FULL-AUDIT"

COMMANDS = [
    ("default", ["pwsh", "-NoProfile", "-File", "tools/governance/check.ps1"]),
    ("taskpath", ["pwsh", "-NoProfile", "-File", "tools/governance/check.ps1", "-TaskPath", "doc/tasks/NEW-MANGA-V1-FULL-AUDIT.md"]),
    ("pins", ["pwsh", "-NoProfile", "-File", "tools/governance/verify_pins.ps1"]),
    ("api", [sys.executable, "tools/generate_api_inventory.py", "--check"]),
]


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()


def main() -> int:
    head = git("rev-parse", "HEAD")
    branch = git("branch", "--show-current")
    summary = []
    for label, argv in COMMANDS:
        started = datetime.now(timezone.utc)
        tick = time.perf_counter()
        result = subprocess.run(argv, cwd=ROOT, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, text=True,
                                encoding="utf-8", errors="replace")
        elapsed = round(time.perf_counter() - tick, 3)
        suffix = f"{head[:8]}-{label}"
        log_path = AUDIT / "logs" / f"audit-post-evidence-{suffix}.log"
        evidence_path = AUDIT / "evidence" / f"audit-post-evidence-{suffix}.json"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        evidence_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text(
            f"START_UTC={started.isoformat()}\nHEAD={head}\nBRANCH={branch}\n"
            f"SHELL=Python subprocess (no shell)\nINTERPRETER={sys.executable}\n"
            f"CWD={ROOT}\nARGV={json.dumps(argv)}\n\n{result.stdout}"
            f"\nEXIT={result.returncode}\nTIMED_OUT=False\nELAPSED_SECONDS={elapsed}\n",
            encoding="utf-8",
        )
        record = {
            "name": f"audit-post-evidence-{suffix}",
            "argv": argv,
            "cwd": str(ROOT),
            "started_utc": started.isoformat(),
            "head": head,
            "branch": branch,
            "exit_code": result.returncode,
            "timed_out": False,
            "elapsed_seconds": elapsed,
            "log": str(log_path.relative_to(ROOT)),
        }
        evidence_path.write_text(json.dumps(record, indent=2), encoding="utf-8")
        summary.append(record)
        print(json.dumps(record), flush=True)
    print(json.dumps({"generated_head": head, "results": summary}, indent=2), flush=True)
    return 0 if all(item["exit_code"] == 0 for item in summary) else 1


if __name__ == "__main__":
    raise SystemExit(main())
