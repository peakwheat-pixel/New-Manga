"""FEA-11-L-S4-LOCATION-AUTH-REFRESH-1 (A) scope validation (card AC-LS4-7).

The delivery is evaluated from ITS OWN commits (explicit list passed on the
command line), not from a plain ``base..HEAD`` range, so the evidence stays
honest even though the shared ``main`` working tree is used concurrently by
another session (L-S1 Host work).  The card ``allowed_paths`` are parsed from
the frozen card itself.

Checks:
* every file changed by the delivery commits is inside the card
  ``allowed_paths`` (file / glob / directory-prefix entries);
* the frozen zero-drift surfaces are untouched by the delivery commits:
  ``apps/**``, ``doc/plan/**``, ``doc/contracts/**``, the SQLite schema /
  migrator, dependencies, STATUS / REBASELINE_PLAN / TASK_LEDGER, and the card
  ``status`` field (Owner never changes it);
* ``CORE_PROTOCOL_MINOR`` is still 3 (zero wire drift).

Writes:
* ``verification/FEA-11-L-S4-LOCATION-AUTH-REFRESH-1/changed-files.txt``
* ``verification/FEA-11-L-S4-LOCATION-AUTH-REFRESH-1/scope-validation.log``

Usage (repo root):
  C:/Python314/python.exe verification/FEA-11-L-S4-LOCATION-AUTH-REFRESH-1/tools/scope_validation.py \
      --commits <sha1>,<sha2>,<sha3>
"""

from __future__ import annotations

import argparse
import fnmatch
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
EVIDENCE = REPO / "verification" / "FEA-11-L-S4-LOCATION-AUTH-REFRESH-1"
CARD = REPO / "doc" / "tasks" / "FEA-11-L-S4-LOCATION-AUTH-REFRESH-1.md"

FORBIDDEN_PREFIXES = (
    "apps/",
    "doc/plan/",
    "doc/contracts/",
    "doc/STATUS.md",
    "doc/REBASELINE_PLAN.md",
    "doc/TASK_LEDGER",
    "src/infrastructure/sqlite/schema.py",
    "src/infrastructure/sqlite/migrator.py",
    "requirements.txt",
    "pyproject.toml",
    "package.json",
)


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


def _matches(entry: str, path: str) -> bool:
    if entry.endswith("/**"):
        return path.startswith(entry[: -len("/**")] + "/")
    if any(character in entry for character in "*?["):
        return fnmatch.fnmatch(path, entry)
    return path == entry


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--commits", required=True)
    parser.add_argument("--base", default="55306cb84")
    args = parser.parse_args()
    commits = [item.strip() for item in args.commits.split(",") if item.strip()]

    lines: list[str] = []

    def log(message: str) -> None:
        print(message)
        lines.append(message)

    log(
        f"[{datetime.now(timezone.utc).isoformat(timespec='milliseconds')}] "
        "FEA-11-L-S4 (A) scope validation"
    )
    log(f"card={CARD.relative_to(REPO).as_posix()} base={args.base}")
    log(f"delivery_commits={','.join(commits)}")

    changed: list[str] = []
    for commit in commits:
        names = _git(
            "show", "--pretty=format:", "--name-only", commit
        ).splitlines()
        for name in names:
            name = name.strip()
            if name and name not in changed:
                changed.append(name)
    changed.sort()
    log(f"changed={len(changed)}")
    for path in changed:
        log(f"  CHANGED {path}")

    allowed = _allowed_paths()
    log(f"allowed_paths={len(allowed)}")
    for entry in allowed:
        log(f"  ALLOWED {entry}")

    out_of_scope = [
        path for path in changed
        if not any(_matches(entry, path) for entry in allowed)
    ]
    forbidden = [
        path for path in changed
        if any(path == prefix or path.startswith(prefix)
               for prefix in FORBIDDEN_PREFIXES)
    ]

    # The Owner never changes the frozen card ``status`` field.
    card_status_ok = True
    if any(path == CARD.relative_to(REPO).as_posix() for path in changed):
        diff = _git(
            "diff", commits[0] + "^.." + commits[-1], "--",
            CARD.relative_to(REPO).as_posix(),
        )
        for line in diff.splitlines():
            if line.startswith(("+status:", "-status:")):
                card_status_ok = False
                log(f"  CARD_STATUS_DIFF {line}")
    log(f"card_status_unchanged={card_status_ok}")

    minor = "unknown"
    core_service = REPO / "src" / "bootstrap" / "core_service.py"
    if core_service.is_file():
        for line in core_service.read_text(
            encoding="utf-8", errors="replace"
        ).splitlines():
            if line.startswith("PROTOCOL_MINOR"):
                minor = line.split("=", 1)[1].strip()
                break
    log(f"PROTOCOL_MINOR={minor}")

    zero_drift = [
        prefix for prefix in FORBIDDEN_PREFIXES
        if any(path == prefix or path.startswith(prefix) for path in changed)
    ]
    log(f"zero_drift_violations={zero_drift}")
    log(f"out_of_scope={out_of_scope}")
    ok = not out_of_scope and not forbidden and card_status_ok and minor == "3"

    EVIDENCE.mkdir(parents=True, exist_ok=True)
    (EVIDENCE / "changed-files.txt").write_text(
        "\n".join(changed) + "\n", encoding="utf-8"
    )
    verdict = "PASS" if ok else "FAIL"
    log(
        f"result={verdict} changed={len(changed)} out_of_scope={out_of_scope} "
        f"forbidden={forbidden} minor={minor}"
    )
    (EVIDENCE / "scope-validation.log").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
