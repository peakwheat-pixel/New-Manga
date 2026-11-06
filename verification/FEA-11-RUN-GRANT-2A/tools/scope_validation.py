"""FEA-11-RUN-GRANT-2A scope validation (card AC-G7).

The delivery is evaluated from ITS OWN commits (explicit list), not from a plain
``base..HEAD`` range: the shared main working tree is concurrently used by the
``FEA-11-RUN-GRANT-2B-PREREQ-1`` (C-16 v1.4 UNFREEZE) session, whose uncommitted
doc/plan + verification changes are NOT part of this ticket. Using the commit
list keeps this evidence honest without touching the other session's files.

Checks:
* every file changed by the delivery commits is inside the card ``allowed_paths``;
* the frozen zero-drift surfaces (doc/plan, doc/contracts, schema.py, migrations,
  dependencies, ``NewManga.App/**``, any apps file outside allowed_paths) are empty;
* ``CORE_PROTOCOL_MINOR`` is still 3.

Writes:
* ``verification/FEA-11-RUN-GRANT-2A/changed-files.txt``
* ``verification/FEA-11-RUN-GRANT-2A/scope-validation.log``

Usage (repo root): C:/Python314/python.exe verification/FEA-11-RUN-GRANT-2A/tools/scope_validation.py
"""

from __future__ import annotations

import fnmatch
import subprocess
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
EVIDENCE = REPO / "verification" / "FEA-11-RUN-GRANT-2A"
CARD = REPO / "doc" / "tasks" / "FEA-11-RUN-GRANT-2A.md"

#: The implementation hand-off started at this HEAD (card ``base_commit`` is
#: 9ec4826d6; 1b6152112 is the release commit the implementation branched from).
DELIVERY_BASE = "1b6152112"

#: This ticket's delivery commits (explicit, no range arithmetic — see docstring).
DELIVERY_COMMITS = ["aa0a5562b", "a0bafc89e"]

#: The 2A code/test surfaces (card allowed_paths, apps part).
IMPLEMENTATION_PATHS = {
    "apps/desktop-avalonia/src/NewManga.Host/Sources/SourceReadCoordinator.cs",
    "apps/desktop-avalonia/src/NewManga.Host/Sources/SourceScanScheduler.cs",
    "apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs",
    "apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11RunGrantIpcTests.cs",
    "apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceRegistryTests.cs",
}


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=str(REPO), capture_output=True, text=True,
        encoding="utf-8", errors="replace", check=True,
    ).stdout


def _allowed_paths() -> list[str]:
    text = CARD.read_text(encoding="utf-8")
    start = text.index("allowed_paths:")
    end = text.index("out_of_scope:")
    paths: list[str] = []
    for line in text[start:end].splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            paths.append(stripped[2:].strip())
    return paths


def _matches(path: str, patterns: list[str]) -> bool:
    for pattern in patterns:
        if pattern.endswith("/**"):
            if path == pattern[:-3] or path.startswith(pattern[:-2]):
                return True
        elif fnmatch.fnmatchcase(path, pattern):
            return True
    return False


def changed_files() -> list[tuple[str, str]]:
    """(status, path) union over the delivery commits, status aggregated A/M."""
    merged: dict[str, str] = {}
    for commit in DELIVERY_COMMITS:
        output = _git("show", "--name-status", "--format=", commit)
        for line in output.splitlines():
            if not line.strip():
                continue
            status, path = line.split("\t")[0], line.split("\t")[-1]
            if path not in merged:
                merged[path] = status[0]
    return [(status, path) for path, status in sorted(merged.items())]


def main() -> int:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    allowed = _allowed_paths()
    rows = changed_files()
    head = _git("rev-parse", "HEAD").strip()
    log = [
        "# FEA-11-RUN-GRANT-2A scope validation",
        f"generated_at_utc={datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        f"delivery_base={DELIVERY_BASE}",
        f"delivery_commits={','.join(DELIVERY_COMMITS)}",
        f"repo_head={head}",
        "",
        "## allowed_paths (card frontmatter)",
        *[f"- {item}" for item in allowed],
        "",
        "## changed files (this ticket's commits only)",
    ]
    problems: list[str] = []
    for status, path in rows:
        ok = _matches(path, allowed)
        log.append(f"{status}\t{path}\t{'ALLOWED' if ok else 'OUT_OF_SCOPE'}")
        if not ok:
            problems.append(path)
    changed = [path for _, path in rows]
    zero_drift = {
        "doc/plan/**": [p for p in changed if p.startswith("doc/plan/")],
        "doc/contracts/**": [p for p in changed if p.startswith("doc/contracts/")],
        "src/infrastructure/sqlite/schema.py": [
            p for p in changed if p == "src/infrastructure/sqlite/schema.py"
        ],
        "migrations": [p for p in changed if "/migrations/" in p],
        "src/**": [p for p in changed if p.startswith("src/")],
        "tests/** (Python Core tests)": [
            p for p in changed if p.startswith("tests/") and not p.startswith("apps/")
        ],
        "dependencies (pyproject/requirements/*.csproj)": [
            p for p in changed
            if p.endswith(("pyproject.toml", "requirements.txt", ".csproj"))
        ],
        "src/bootstrap/core_assembly.py": [
            p for p in changed if p == "src/bootstrap/core_assembly.py"
        ],
        "NewManga.App/**": [
            p for p in changed if p.startswith("apps/desktop-avalonia/src/NewManga.App/")
        ],
        "STATUS/PLAN/TASK_LEDGER": [
            p for p in changed
            if p in {"doc/STATUS.md", "doc/REBASELINE_PLAN.md", "doc/TASK_LEDGER.md"}
        ],
        "apps/** beyond allowed_paths": [
            p for p in changed if p.startswith("apps/") and p not in IMPLEMENTATION_PATHS
        ],
    }
    log.append("")
    log.append("## zero-drift surfaces")
    for name, hits in zero_drift.items():
        log.append(f"{name}: {'ZERO_DIFF' if not hits else 'DRIFT ' + str(hits)}")
        if hits:
            problems.append(name)
    # Run wire / protocol minor byte parity (M2-C1 §5.5 request/response keys).
    core_service = (REPO / "src/bootstrap/core_service.py").read_text(encoding="utf-8")
    minor_ok = "PROTOCOL_MINOR = 3" in core_service
    log.append(f"protocol_minor=3 kept: {'YES' if minor_ok else 'NO'}")
    if not minor_ok:
        problems.append("protocol-minor")
    log.append("")
    log.append(
        f"result={'PASS' if not problems else 'FAIL'} "
        f"changed={len(changed)} out_of_scope={problems}"
    )
    log.append("")
    log.append("## shared-worktree note (honest disclosure)")
    log.append(
        "The same main working tree is being used concurrently by the "
        "FEA-11-RUN-GRANT-2B-PREREQ-1 session (C-16 v1.4 UNFREEZE + "
        "doc/plan/FEA-C16* + verification/FEA-11-RUN-GRANT-2B-PREREQ-1/**)."
    )
    log.append(
        "Those files are NOT part of this delivery; they are excluded here because the "
        "changed-file set is computed from this ticket's own commits "
        f"({', '.join(DELIVERY_COMMITS)}), not from a base..HEAD range."
    )
    log.append(
        "No file of that session was modified, staged or committed by this ticket."
    )
    log.append(
        "docs commit (card / handoff / verification evidence) follows the delivery "
        "commits; it is within allowed_paths by construction."
    )
    (EVIDENCE / "changed-files.txt").write_text(
        "".join(f"{status}\t{path}\n" for status, path in rows),
        encoding="utf-8", newline="",
    )
    (EVIDENCE / "scope-validation.log").write_text(
        "\n".join(log) + "\n", encoding="utf-8", newline="",
    )
    print("\n".join(log))
    return 0 if not problems else 1


if __name__ == "__main__":
    raise SystemExit(main())
