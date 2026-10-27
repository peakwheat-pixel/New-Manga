#!/usr/bin/env python
"""FLAKY-PYTEST-1 AC3: run the full pytest suite 5 consecutive times.

Each run writes ``<logdir>/run<N>-pytest.log`` with a RUN META header and an
EXIT marker.  A ``summary.json`` records the parsed tail + a consistency check.
The driver does not modify the worktree; runs are sequential (never parallel)
so the recorded result is exactly what a reviewer would reproduce.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(r"G:\CODEX\New Manga.workspace\worktrees\FLAKY-PYTEST-1")
ENV = Path(r"G:\CODEX\New Manga.workspace\task-envs\FLAKY-PYTEST-1")
LOGDIR = ENV / "log"
RUNS = 5


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=str(REPO), capture_output=True,
                          text=True).stdout.strip()


def main() -> int:
    LOGDIR.mkdir(parents=True, exist_ok=True)
    head = git("rev-parse", "HEAD")
    status = git("status", "--porcelain")
    rows = []
    for index in range(1, RUNS + 1):
        log = LOGDIR / f"run{index}-pytest.log"
        header = [
            "=== RUN META ===",
            f"command: python -m pytest tests -q   (AC3 consecutive run {index}/{RUNS})",
            "purpose: FLAKY-PYTEST-1 AC3 stability (sequential, no parallel jobs)",
            f"shell: pwsh / {sys.executable} / {sys.version.split()[0]}",
            f"cwd: {REPO}",
            f"git_head: {head}",
            "git_status: " + (status or "(clean)"),
            "=== OUTPUT ===",
        ]
        started = time.time()
        log.write_text("\n".join(header) + "\n", encoding="utf-8")
        with log.open("a", encoding="utf-8") as handle:
            proc = subprocess.run(
                [sys.executable, "-m", "pytest", "tests", "-q"],
                cwd=str(REPO), stdout=handle, stderr=subprocess.STDOUT,
            )
        elapsed = round(time.time() - started, 1)
        text = log.read_text(encoding="utf-8", errors="replace")
        with log.open("a", encoding="utf-8") as handle:
            handle.write(f"\n=== EXIT={proc.returncode} ===\n")
        match = re.search(r"^(\d+) failed, (\d+) passed, (\d+) skipped.*$", text, re.M)
        no_fail = re.search(r"^(\d+) passed, (\d+) skipped.*$", text, re.M)
        row = {"run": index, "exit": proc.returncode, "elapsed_s": elapsed,
               "log": str(log)}
        if match:
            row.update(failed=int(match.group(1)), passed=int(match.group(2)),
                       skipped=int(match.group(3)))
        elif no_fail:
            row.update(failed=0, passed=int(no_fail.group(1)),
                       skipped=int(no_fail.group(2)))
        rows.append(row)
        print(json.dumps(row, ensure_ascii=False), flush=True)

    shape = {(r["failed"], r["passed"], r["skipped"]) for r in rows}
    summary = {
        "task": "FLAKY-PYTEST-1",
        "purpose": "AC3: 5 consecutive full-suite runs after the fixes",
        "git_head": head,
        "runs": rows,
        "distinct_results": [list(item) for item in sorted(shape)],
        "consistent": len(shape) == 1 and all(r["failed"] == 0 for r in rows),
    }
    (ENV / "evidence").mkdir(parents=True, exist_ok=True)
    out = ENV / "evidence" / "ac3-five-runs.json"
    out.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("SUMMARY " + json.dumps({k: summary[k] for k in
                                   ("distinct_results", "consistent")}, ensure_ascii=False),
          flush=True)
    return 0 if summary["consistent"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
