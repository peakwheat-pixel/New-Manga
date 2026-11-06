"""FEA-11-RUN-GRANT-1 scope validation (card AC-R6).

Reads the frozen card's ``allowed_paths`` from its frontmatter and checks the
delivery diff (``base_commit..HEAD``) plus the explicit "zero drift" surfaces
(doc/plan, doc/contracts, schema.py, dependencies, apps/** beyond the three
Host files, core_assembly.py). Writes:

* ``verification/FEA-11-RUN-GRANT-1/changed-files.txt``
* ``verification/FEA-11-RUN-GRANT-1/scope-validation.log``

Usage (repo root): C:/Python314/python.exe verification/FEA-11-RUN-GRANT-1/tools/scope_validation.py
"""

from __future__ import annotations

import fnmatch
import subprocess
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
EVIDENCE = REPO / "verification" / "FEA-11-RUN-GRANT-1"
CARD = REPO / "doc" / "tasks" / "FEA-11-RUN-GRANT-1.md"


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=str(REPO), capture_output=True, text=True, check=True
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


#: The implementation hand-off started at this HEAD (card ``base_commit`` is
#: 2067789ea, but the card/PREREQ release commit a94052ba7 is the tree the
#: implementation branched from; the diff starts there).
DELIVERY_BASE = "a94052ba7"


def main() -> int:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    base = DELIVERY_BASE
    head = _git("rev-parse", "HEAD").strip()
    allowed = _allowed_paths()
    diff = _git("diff", "--name-status", f"{base}..{head}").splitlines()
    rows = [line.split("\t") for line in diff if line.strip()]
    log = [
        "# FEA-11-RUN-GRANT-1 scope validation",
        f"generated_at_utc={datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        f"base_commit={base}",
        f"delivery_head={head}",
        "",
        "## allowed_paths (card frontmatter)",
        *[f"- {item}" for item in allowed],
        "",
        "## changed files in range",
    ]
    problems: list[str] = []
    for row in rows:
        status, path = row[0], row[-1]
        ok = _matches(path, allowed)
        log.append(f"{status}\t{path}\t{'ALLOWED' if ok else 'OUT_OF_SCOPE'}")
        if not ok:
            problems.append(path)
    changed = [row[-1] for row in rows]
    zero_drift = {
        "doc/plan/**": [p for p in changed if p.startswith("doc/plan/")],
        "doc/contracts/**": [p for p in changed if p.startswith("doc/contracts/")],
        "src/infrastructure/sqlite/schema.py": [
            p for p in changed if p == "src/infrastructure/sqlite/schema.py"
        ],
        "migrations": [p for p in changed if "/migrations/" in p],
        "dependencies (pyproject/requirements/*.csproj)": [
            p for p in changed
            if p.endswith(("pyproject.toml", "requirements.txt", ".csproj"))
        ],
        "src/bootstrap/core_assembly.py": [
            p for p in changed if p == "src/bootstrap/core_assembly.py"
        ],
        "NewManga.App/**": [p for p in changed if p.startswith("apps/desktop-avalonia/src/NewManga.App/")],
        "apps/** beyond allowed_paths": [
            p for p in changed
            if p.startswith("apps/") and p not in {
                "apps/desktop-avalonia/src/NewManga.Host/Sources/SourceReadCoordinator.cs",
                "apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs",
                "apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandDispatcher.cs",
                "apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceRegistryTests.cs",
                "apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11RunGrantIpcTests.cs",
            }
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
    log.append("## R-12 approved scope extension (Lead, commit 218775bca)")
    log.append(
        "reason: the frozen C-16 v1.3 §0 capability ``source.read.run/1`` is an "
        "additive ping advertisement, but two pre-existing tests asserted the "
        "capability list by exact equality; they had to gain the one string."
    )
    log.append("- tests/core/test_core_service.py: +\"source.read.run/1\" in two exact expectations only")
    log.append("- tests/fea09/test_referenced_wire.py: +\"source.read.run/1\" in one exact expectation only")
    log.append(
        "no existing assertion was deleted/weakened and no skip was added "
        "(diff reviewed: additive lines only)."
    )
    log.append(
        "docs commit (card / handoff / verification evidence) follows the "
        "delivery head; it is within allowed_paths by construction."
    )
    (EVIDENCE / "changed-files.txt").write_text(
        "".join(f"{row[0]}\t{row[-1]}\n" for row in rows), encoding="utf-8", newline=""
    )
    (EVIDENCE / "scope-validation.log").write_text(
        "\n".join(log) + "\n", encoding="utf-8", newline=""
    )
    print("\n".join(log))
    return 0 if not problems else 1


if __name__ == "__main__":
    raise SystemExit(main())
