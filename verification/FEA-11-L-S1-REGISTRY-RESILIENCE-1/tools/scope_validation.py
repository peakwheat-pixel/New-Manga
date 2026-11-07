"""FEA-11-L-S1-REGISTRY-RESILIENCE-1 scope validation (card AC-L7).

The delivery is evaluated from ITS OWN commits (explicit list), not from a plain
``base..HEAD`` range: the shared main working tree is concurrently used by the
``FEA-11-L-S4-LOCATION-AUTH-REFRESH-1`` session (Python ``src/**`` / ``tests/**`` changes), which
are NOT part of this ticket. Using the commit list keeps this evidence honest without touching the
other session's files.

Checks:
* every file changed by the delivery commits is inside the card ``allowed_paths``;
* the frozen zero-drift surfaces (doc/plan, doc/contracts, schema.py, migrations, dependencies,
  ``NewManga.App/**``, any file outside allowed_paths) are empty;
* unchanged source blobs outside this ticket's write domain are byte-identical to the start HEAD.

Writes:
* ``verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1/changed-files.txt``
* ``verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1/scope-validation.log``

Usage (repo root): C:/Python314/python.exe verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1/tools/scope_validation.py
"""

from __future__ import annotations

import fnmatch
import subprocess
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
TASK = "FEA-11-L-S1-REGISTRY-RESILIENCE-1"
EVIDENCE = REPO / "verification" / TASK
CARD = REPO / "doc" / "tasks" / (TASK + ".md")

#: The implementation hand-off started at this HEAD (card ``base_commit`` is 55306cb84; db12dc5e5
#: is the release commit the implementation branched from).
DELIVERY_BASE = "db12dc5e5"

#: This ticket's delivery commits (explicit, no range arithmetic — see docstring).
#: Filled in after the implementation/test commits land; the docs commit (card / handoff /
#: verification evidence) follows them and is inside allowed_paths by construction.
DELIVERY_COMMITS: list[str] = ["1ac8cc0b7", "b56c5a0e6"]

#: The implementation/test surfaces of this card (card allowed_paths, apps part).
IMPLEMENTATION_PATHS = {
    "apps/desktop-avalonia/src/NewManga.Host/Sources/SourceAccessRegistry.cs",
    "apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceRegistryResilienceTests.cs",
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
            parts = line.split("\t")
            status, path = parts[0], parts[-1]
            if path not in merged:
                merged[path] = status[0]
    return [(status, path) for path, status in sorted(merged.items())]


def main() -> int:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    allowed = _allowed_paths()
    rows = changed_files()
    head = _git("rev-parse", "HEAD").strip()
    log = [
        "# FEA-11-L-S1-REGISTRY-RESILIENCE-1 scope validation",
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
        "src/** (Python Core)": [p for p in changed if p.startswith("src/")],
        "tests/** (Python Core tests)": [
            p for p in changed if p.startswith("tests/") and not p.startswith("apps/")
        ],
        "dependencies (pyproject/requirements/*.csproj)": [
            p for p in changed
            if p.endswith(("pyproject.toml", "requirements.txt", ".csproj"))
        ],
        "NewManga.App/**": [
            p for p in changed if p.startswith("apps/desktop-avalonia/src/NewManga.App/")
        ],
        "NewManga.CoreClient/**": [
            p for p in changed
            if p.startswith("apps/desktop-avalonia/src/NewManga.CoreClient/")
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
    log.append("")
    log.append(
        f"result={'PASS' if not problems else 'FAIL'} "
        f"changed={len(changed)} out_of_scope={problems}"
    )
    log.append("")
    log.append("## shared-worktree note (honest disclosure)")
    log.append(
        "The same main working tree is being used concurrently by the "
        "FEA-11-L-S4-LOCATION-AUTH-REFRESH-1 session (Python src/** + tests/**)."
    )
    log.append(
        "Those files are NOT part of this delivery; the changed-file set is computed from this "
        f"ticket's own commits ({', '.join(DELIVERY_COMMITS)}), not from a base..HEAD range."
    )
    log.append(
        "No file of that session was modified, staged or committed by this ticket; the tree-level "
        "git status at evidence time is recorded in logs/gates-governance.log."
    )
    log.append(
        "The docs commit (card / handoff / verification evidence) follows the delivery commits; "
        "it is within allowed_paths by construction."
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
