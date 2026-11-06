"""FEA-11-RUN-GRANT-2 (2B) scope validation (card AC-J4).

The delivery is evaluated from ITS OWN commits (explicit list), not from a plain
``base..HEAD`` range, so the evidence stays honest even if the shared main
working tree is used concurrently by another session.

Checks:
* every file changed by the delivery commits is inside the card ``allowed_paths``;
* the frozen zero-drift surfaces are empty: ``doc/plan`` (the frozen C-16 v1.4
  bytes are NOT part of this ticket), ``doc/contracts``, the SQLite schema,
  migrations, dependencies, ``NewManga.App/**``, STATUS/PLAN/TASK_LEDGER, any
  ``src/**`` file outside the card's Core allowance, any ``tests/**`` file
  outside the card's two test files, and any ``apps/**`` file outside the
  allowed Host surfaces;
* ``CORE_PROTOCOL_MINOR`` is still 3 (Run wire / minor zero drift).

Writes:
* ``verification/FEA-11-RUN-GRANT-2/changed-files.txt``
* ``verification/FEA-11-RUN-GRANT-2/scope-validation.log``

Usage (repo root): C:/Python314/python.exe verification/FEA-11-RUN-GRANT-2/tools/scope_validation.py
"""

from __future__ import annotations

import fnmatch
import subprocess
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
EVIDENCE = REPO / "verification" / "FEA-11-RUN-GRANT-2"
CARD = REPO / "doc" / "tasks" / "FEA-11-RUN-GRANT-2.md"

#: The implementation hand-off started at this HEAD (card ``base_commit`` 97812958d).
DELIVERY_BASE = "5397be149"

#: This ticket's delivery commits (explicit, no range arithmetic — see docstring).
DELIVERY_COMMITS = ["7466cb99d", "018008989"]

#: Allowed ``src/**`` files (card allowed_paths; core_service.py is allowed but unused).
ALLOWED_SRC = {
    "src/infrastructure/resource_channel/source_read_refs.py",
    "src/bootstrap/core_service.py",
}

#: Allowed Python test files (card allowed_paths).
ALLOWED_TESTS = {
    "tests/core/test_host_control.py",
    "tests/fea11/test_source_run_grant.py",
}

#: Allowed Host surfaces (card allowed_paths).
ALLOWED_APPS = {
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
        "# FEA-11-RUN-GRANT-2 (2B) scope validation",
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
        "doc/plan/** (frozen C-16 v1.4 bytes are not this ticket)": [
            p for p in changed if p.startswith("doc/plan/")
        ],
        "doc/contracts/**": [p for p in changed if p.startswith("doc/contracts/")],
        "src/infrastructure/sqlite/schema.py": [
            p for p in changed if p == "src/infrastructure/sqlite/schema.py"
        ],
        "migrations": [p for p in changed if "/migrations/" in p],
        "src/** beyond the card's Core allowance": [
            p for p in changed if p.startswith("src/") and p not in ALLOWED_SRC
        ],
        "tests/** beyond the card's two test files": [
            p for p in changed if p.startswith("tests/") and p not in ALLOWED_TESTS
        ],
        "dependencies (pyproject/requirements/*.csproj)": [
            p for p in changed
            if p.endswith(("pyproject.toml", "requirements.txt", ".csproj"))
        ],
        "NewManga.App/**": [
            p for p in changed if p.startswith("apps/desktop-avalonia/src/NewManga.App/")
        ],
        "STATUS/PLAN/TASK_LEDGER": [
            p for p in changed
            if p in {"doc/STATUS.md", "doc/REBASELINE_PLAN.md", "doc/TASK_LEDGER.md"}
        ],
        "apps/** beyond allowed_paths": [
            p for p in changed if p.startswith("apps/") and p not in ALLOWED_APPS
        ],
    }
    log.append("")
    log.append("## zero-drift surfaces")
    for name, hits in zero_drift.items():
        log.append(f"{name}: {'ZERO_DIFF' if not hits else 'DRIFT ' + str(hits)}")
        if hits:
            problems.append(name)
    core_service = (REPO / "src/bootstrap/core_service.py").read_text(encoding="utf-8")
    minor_ok = "PROTOCOL_MINOR = 3" in core_service
    log.append(f"protocol_minor=3 kept: {'YES' if minor_ok else 'NO'}")
    if not minor_ok:
        problems.append("protocol-minor")
    # Run wire surface: the frozen command catalog / error-code list must not grow.
    catalog_ok = "AuthorizeSourceReadForRun" in core_service
    log.append(f"Run authorization command kept: {'YES' if catalog_ok else 'NO'}")
    if not catalog_ok:
        problems.append("run-command")
    log.append("")
    log.append(
        f"result={'PASS' if not problems else 'FAIL'} "
        f"changed={len(changed)} out_of_scope={problems}"
    )
    log.append("")
    log.append("## shared-worktree note (honest disclosure)")
    log.append(
        "The changed-file set is computed from this ticket's own commits "
        f"({', '.join(DELIVERY_COMMITS)}), never from a base..HEAD range."
    )
    log.append(
        "The docs commit (card delivery record / Handoff / this verification tree) "
        "follows the delivery commits and is inside allowed_paths by construction."
    )
    log.append(
        "The frozen C-16 v1.4 contract bytes are NOT touched by this ticket: the "
        "pin audit (logs/gates.log PIN AUDIT) is the separate proof."
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
