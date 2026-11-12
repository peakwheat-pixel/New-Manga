#!/usr/bin/env python3
"""Capture AUDIT-03 repository boundaries and exact product baseline comparison."""
from __future__ import annotations

import datetime as dt
import json
import subprocess
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / "audit/V1-FULL-AUDIT"
BASE = "10e4ee013835605800d3830fb960ae8d3aa04167"
STAMP = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
LOG_PATH = AUDIT / "logs" / f"audit03-static-{STAMP}.log"
JSON_PATH = AUDIT / "evidence" / f"audit03-static-{STAMP}.json"
ALLOWED_PREFIXES = (
    "audit/V1-FULL-AUDIT/",
    "doc/tasks/NEW-MANGA-V1-FULL-AUDIT.md",
    "doc/STATUS.md",
    "doc/REBASELINE_PLAN.md",
    "doc/TASK_LEDGER.md",
)


def run(argv: list[str]) -> dict[str, object]:
    started = dt.datetime.now(dt.timezone.utc).isoformat()
    tick = time.monotonic()
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
        "started_utc": started,
        "elapsed_seconds": round(time.monotonic() - tick, 6),
        "exit": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def main() -> int:
    head = run(["git", "rev-parse", "HEAD"])
    branch = run(["git", "branch", "--show-current"])
    status = run(["git", "status", "--porcelain", "--untracked-files=all"])
    product_diff = run(["git", "diff", "--quiet", BASE, str(head["stdout"]).strip(), "--", "src", "apps", "tests"])
    changed_paths = run(["git", "diff", "--name-only", BASE, str(head["stdout"]).strip()])
    whitespace = run(["git", "diff", "--check"])
    paths = [line for line in str(changed_paths["stdout"]).splitlines() if line]
    inherited_paths_outside_task_allowlist = [path for path in paths if not path.startswith(ALLOWED_PREFIXES)]
    worktree_paths = [
        line[3:].split(" -> ")[-1]
        for line in str(status["stdout"]).splitlines()
        if len(line) >= 4
    ]
    out_of_scope_worktree = [path for path in worktree_paths if not path.startswith(ALLOWED_PREFIXES)]
    generated_at = dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")
    record = {
        "schema": "audit03-static/v1",
        "generated_at_utc": generated_at,
        "generated_head": str(head["stdout"]).strip(),
        "branch": str(branch["stdout"]).strip(),
        "base_commit": BASE,
        "worktree_status_porcelain": str(status["stdout"]),
        "product_paths_diff_exit": product_diff["exit"],
        "changed_paths": paths,
        "inherited_paths_outside_task_allowlist": inherited_paths_outside_task_allowlist,
        "worktree_paths": worktree_paths,
        "out_of_scope_worktree_paths": out_of_scope_worktree,
        "whitespace_diff_exit": whitespace["exit"],
        "commands": [head, branch, status, product_diff, changed_paths, whitespace],
    }
    JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    JSON_PATH.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    lines = [
        "AUDIT-03 static repository boundary capture",
        f"generated_at_utc={generated_at}",
        f"generated_head={record['generated_head']}",
        f"branch={record['branch']}",
        f"base_commit={BASE}",
        f"product_paths_diff_exit={product_diff['exit']}",
        f"changed_paths_count={len(paths)}",
        f"inherited_paths_outside_task_allowlist={json.dumps(inherited_paths_outside_task_allowlist, ensure_ascii=False)}",
        f"worktree_paths_count={len(worktree_paths)}",
        f"out_of_scope_worktree_paths={json.dumps(out_of_scope_worktree, ensure_ascii=False)}",
        f"whitespace_diff_exit={whitespace['exit']}",
        f"json={JSON_PATH}",
    ]
    for result in record["commands"]:
        lines.extend(
            [
                "",
                f"argv={json.dumps(result['argv'], ensure_ascii=False)}",
                f"cwd={ROOT} shell=False interpreter={result.get('interpreter', result['argv'][0])}",
                f"started_utc={result.get('started_utc', generated_at)} elapsed_seconds={result.get('elapsed_seconds', 0)} EXIT={result['exit']}",
                "stdout:",
                str(result["stdout"]).rstrip("\n"),
            ]
        )
        if result["stderr"]:
            lines.extend(["stderr:", str(result["stderr"]).rstrip("\n")])
    LOG_PATH.write_text("\n".join(lines).rstrip("\n") + "\n", encoding="utf-8", newline="\n")
    print(f"generated_head={record['generated_head']}")
    print(f"log={LOG_PATH}")
    print(f"json={JSON_PATH}")
    print(f"product_diff_exit={product_diff['exit']} historical_changed_paths={len(paths)} inherited_outside_task_allowlist={len(inherited_paths_outside_task_allowlist)} worktree_paths={len(worktree_paths)} out_of_scope_worktree={len(out_of_scope_worktree)} whitespace_exit={whitespace['exit']}")
    return 1 if product_diff["exit"] != 0 or whitespace["exit"] != 0 or out_of_scope_worktree else 0


if __name__ == "__main__":
    raise SystemExit(main())
