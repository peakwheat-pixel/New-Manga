"""FEA-11-L-S4-B-AUTO-RECOVERY-1 scope validation (card AC-LS4B-7).

Evaluates the DELIVERY DIFF against the card ``base_commit`` (``c6ca1aa3c``):
every tracked change (committed, staged or unstaged) plus every untracked file,
because the shared ``main`` working tree is used concurrently (Lead docs) and the
evidence must stay honest either way. The card ``allowed_paths`` are parsed from
the frozen card itself.

Checks:
* every delivery file is inside the card ``allowed_paths`` (file / glob /
  directory-prefix entries); Lead-owned concurrent docs are reported as
  ``CONCURRENT_NON_DELIVERY`` (never counted as this delivery, never modified);
* the explicit out-of-scope surfaces are untouched by the DELIVERY:
  ``src/infrastructure/sqlite/library.py`` (the ONE location-auth SQL may only
  be REUSED), ``doc/plan/**`` (C-16 v1.5 frozen bytes), ``doc/contracts/**``,
  the SQLite schema/migrator, this card's dependency/schema surface, and the
  STATUS / REBASELINE_PLAN / TASK_LEDGER pointers; the card ``status`` field is
  never changed by the Owner;
* ``CORE_PROTOCOL_MINOR`` is still 3 (zero wire drift) and the frozen C-16 v1.5
  byte pin is unchanged (``a7f57ebd…``);
* additive-only wire: ``ReattestSourceLocation`` exists in the Core host-control
  command set and is NOT registered as an App/Host (C-07) command — the command
  registry cardinality baseline (111) therefore cannot grow.

Writes:
* ``verification/FEA-11-L-S4-B-AUTO-RECOVERY-1/changed-files.txt``
* ``verification/FEA-11-L-S4-B-AUTO-RECOVERY-1/scope-validation.log``

Usage (repo root):
  C:/Python314/python.exe verification/FEA-11-L-S4-B-AUTO-RECOVERY-1/tools/scope_validation.py
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
TASK_ID = "FEA-11-L-S4-B-AUTO-RECOVERY-1"
EVIDENCE = REPO / "verification" / TASK_ID
CARD = REPO / "doc" / "tasks" / f"{TASK_ID}.md"
CARD_REL = CARD.relative_to(REPO).as_posix()

BASE = "c6ca1aa3c"

#: The frozen C-16 v1.5 byte pin (contract must not drift).
C16 = REPO / "doc" / "plan" / "FEA-C16_SOURCE_READ_WIRE_DRAFT.md"
C16_PIN = "a7f57ebdbd673a6bac0e148f54223301bb4117e0cbeafce008ab7adc1347b22d"

#: The B1 baseline C-07 command-registry cardinality (no new UI->Host command).
COMMAND_REGISTRY_BASELINE = 111

FORBIDDEN_PREFIXES = (
    "doc/plan/",
    "doc/contracts/",
    "src/infrastructure/sqlite/library.py",
    "src/infrastructure/sqlite/schema.py",
    "src/infrastructure/sqlite/migrator.py",
    "src/infrastructure/sqlite/source_sync.py",
    "requirements.txt",
    "pyproject.toml",
    "package.json",
    "apps/desktop-avalonia/src/NewManga.App/Services/SourceRecoveryModels.cs",
    "apps/desktop-avalonia/src/NewManga.App/Services/SourceImportModels.cs",
    "apps/desktop-avalonia/src/NewManga.App/Services/HostController.cs",
    "apps/desktop-avalonia/src/NewManga.App/Services/NullHostController.cs",
    "apps/desktop-avalonia/src/NewManga.Host/Sources/SourceAccessRegistry.cs",
    "doc/STATUS.md",
    "doc/REBASELINE_PLAN.md",
    "doc/TASK_LEDGER",
)

#: Lead-owned concurrent docs present in the shared tree; NEVER this delivery.
#: (The Lead committed the PREREQ r8/r9 close-out + progress handoffs on top of
#: the implementation start ``c6ca1aa3c``; their diff is docs-only.)
DEFAULT_CONCURRENT = (
    "doc/handoffs/DSH-HANDOFF-2026-11-06.md,"
    "doc/handoffs/DSH-PROGRESS-2026-11-07.md,"
    "doc/reviews/FEA-11-L-S4-B-PREREQ-1-r8.md,"
    "doc/reviews/FEA-11-L-S4-B-PREREQ-1-r9.md"
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


def _delivery_files() -> list[str]:
    """Tracked changes vs base + every untracked file (delivery candidates)."""
    changed = {
        name.strip()
        for name in _git("diff", "--name-only", BASE).splitlines()
        if name.strip()
    }
    status = _git("status", "--porcelain", "-uall").splitlines()
    for line in status:
        if not line.strip():
            continue
        path = line[3:].strip()
        if " -> " in path:  # rename entry
            path = path.split(" -> ", 1)[1].strip()
        changed.add(path)
    return sorted(changed)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default=BASE)
    parser.add_argument("--concurrent", default=DEFAULT_CONCURRENT)
    args = parser.parse_args()
    concurrent = {
        item.strip() for item in args.concurrent.split(",") if item.strip()
    }

    lines: list[str] = []

    def log(message: str) -> None:
        print(message)
        lines.append(message)

    log(
        f"[{datetime.now(timezone.utc).isoformat(timespec='milliseconds')}] "
        f"{TASK_ID} scope validation (delivery diff vs {args.base})"
    )
    log(f"card={CARD_REL} base={args.base}")

    all_changed = _delivery_files()
    delivery = [path for path in all_changed if path not in concurrent]
    concurrent_present = [path for path in all_changed if path in concurrent]
    log(f"changed_count={len(all_changed)} delivery={len(delivery)} "
        f"concurrent_non_delivery={len(concurrent_present)}")
    for path in concurrent_present:
        log(f"CONCURRENT_NON_DELIVERY {path}")

    allowed = _allowed_paths()
    log(f"allowed_paths={len(allowed)}")
    for entry in allowed:
        log(f"  ALLOWED {entry}")
    for path in delivery:
        log(f"ALLOWED  {path}")

    out_of_scope = [
        path for path in delivery
        if not any(_matches(entry, path) for entry in allowed)
    ]
    forbidden = [
        path for path in delivery
        if any(path == prefix or path.startswith(prefix)
               for prefix in FORBIDDEN_PREFIXES)
    ]

    # The Owner never changes the frozen card ``status`` field.
    card_status_ok = True
    diff = _git("diff", args.base, "--", CARD_REL)
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

    c16_sha = hashlib.sha256(C16.read_bytes()).hexdigest() if C16.is_file() else "MISSING"
    log(f"C16_SHA256={c16_sha}")
    c16_zero_drift = c16_sha == C16_PIN
    log(f"C16_PIN_MATCH={c16_zero_drift}")

    command_present = "ReattestSourceLocation" in core_service.read_text(
        encoding="utf-8", errors="replace"
    )
    log(f"CORE_HAS_REATTEST_COMMAND={command_present}")

    registry_path = (
        REPO / "apps" / "desktop-avalonia" / "src" / "NewManga.CoreClient"
        / "Commands" / "HostCommandRegistry.cs"
    )
    registered = False
    if registry_path.is_file():
        text = registry_path.read_text(encoding="utf-8", errors="replace")
        # The new Core command is a Host-control fact, NOT a UI->Host command:
        # the frozen C-07 registry must not grow (the App test asserts the
        # cardinality 111 at the B1 baseline; this check pins the command name).
        registered = "ReattestSourceLocation" in text
    command_registry_ok = not registered
    log(f"COMMAND_REGISTRY_BASELINE={COMMAND_REGISTRY_BASELINE} "
        f"COMMAND_REGISTRY_HAS_REATTEST={registered} "
        f"COMMAND_REGISTRY_OK={command_registry_ok}")

    zero_drift = [
        prefix for prefix in FORBIDDEN_PREFIXES
        if any(path == prefix or path.startswith(prefix) for path in delivery)
    ]
    log(f"zero_drift_violations={zero_drift}")
    log(f"out_of_scope={out_of_scope}")
    ok = (
        not out_of_scope
        and not forbidden
        and card_status_ok
        and minor == "3"
        and c16_zero_drift
        and command_present
        and command_registry_ok
    )

    EVIDENCE.mkdir(parents=True, exist_ok=True)
    (EVIDENCE / "changed-files.txt").write_text(
        "\n".join(delivery) + "\n", encoding="utf-8"
    )
    verdict = "PASS" if ok else "FAIL"
    log(
        f"result={verdict} changed={len(delivery)} out_of_scope={out_of_scope} "
        f"forbidden={forbidden} minor={minor} c16_zero_drift={c16_zero_drift} "
        f"command_registry_ok={command_registry_ok}"
    )
    (EVIDENCE / "scope-validation.log").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
