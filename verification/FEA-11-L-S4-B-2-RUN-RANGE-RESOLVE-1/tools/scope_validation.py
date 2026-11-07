"""FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1 scope validation (card AC-RUN-7).

Evaluates the DELIVERY DIFF against the implementation start
``e78c144bb`` (the Lead's release commit; the card's ``base_commit`` is
``2ef3f1024`` = the frozen base the release commit points at). Every tracked
change (committed, staged or unstaged) plus every untracked file is considered,
because the shared ``main`` working tree is used concurrently (Lead docs). The
card ``allowed_paths`` are parsed from the frozen card itself.

Checks:
* the release range ``2ef3f1024..e78c144bb`` is docs-only (Lead's freeze/release
  commits are never this delivery);
* every delivery file is inside the card ``allowed_paths`` (file / glob /
  directory-prefix entries); Lead-owned concurrent docs are reported as
  ``CONCURRENT_NON_DELIVERY`` (never counted as this delivery, never modified);
* the explicit out-of-scope surfaces are untouched by the DELIVERY:
  ``src/**`` + ``tests/**`` (zero Python/Core change), ``doc/plan/**`` (frozen
  contract bytes), ``doc/contracts/**``, schema/dependencies,
  ``apps/desktop-avalonia/src/NewManga.Host/Sources/**`` (the scan/registry/
  coordinator/planner helpers are REUSED, never modified), the App surface, and
  the STATUS / REBASELINE_PLAN / TASK_LEDGER pointers; the card ``status`` field
  is never changed by the Owner;
* ``CORE_PROTOCOL_MINOR`` is still 3 (zero wire drift) and the frozen C-16 v1.5
  (``a7f57ebd…``) / C-17 v1.1 git blobs are unchanged.

Writes:
* ``verification/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1/changed-files.txt``
* ``verification/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1/scope-validation.log``

Usage (repo root):
  C:/Python314/python.exe verification/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1/tools/scope_validation.py
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
TASK_ID = "FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1"
EVIDENCE = REPO / "verification" / TASK_ID
CARD = REPO / "doc" / "tasks" / f"{TASK_ID}.md"
CARD_REL = CARD.relative_to(REPO).as_posix()

#: The card's frozen base_commit and the Lead's release commit (implementation start).
CARD_BASE = "2ef3f1024"
BASE = "e78c144bb"

C16 = REPO / "doc" / "plan" / "FEA-C16_SOURCE_READ_WIRE_DRAFT.md"
C16_PIN = "a7f57ebdbd673a6bac0e148f54223301bb4117e0cbeafce008ab7adc1347b22d"
C17 = REPO / "doc" / "plan" / "FEA-C17_SOURCE_SYNC_DRAFT.md"

FORBIDDEN_PREFIXES = (
    "src/",
    "tests/",
    "doc/plan/",
    "doc/contracts/",
    "requirements.txt",
    "pyproject.toml",
    "package.json",
    "apps/desktop-avalonia/src/NewManga.Host/Sources/",
    "apps/desktop-avalonia/src/NewManga.CoreClient/",
    "apps/desktop-avalonia/src/NewManga.App/",
    "apps/desktop-avalonia/tests/NewManga.App.Tests/",
    "apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceRegistryTests.cs",
    "apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceScanSchedulerTests.cs",
    "apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceScanExecutionRecoveryTests.cs",
    "apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceReattestTests.cs",
    "doc/STATUS.md",
    "doc/REBASELINE_PLAN.md",
    "doc/TASK_LEDGER",
)

#: Lead-owned docs in the shared tree; NEVER this delivery.
DEFAULT_CONCURRENT = ""


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


def _blob_hash(rev: str, path: str) -> str:
    """Git blob id at ``rev`` for ``path`` — newline-normalization independent."""
    return _git("rev-parse", f"{rev}:{path}").strip()


def _delivery_files(base: str) -> list[str]:
    changed = {
        name.strip()
        for name in _git("diff", "--name-only", base).splitlines()
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
    log(f"card={CARD_REL} card_base_commit={CARD_BASE} implementation_start={args.base}")

    # The frozen base .. implementation start range must be docs-only (Lead release).
    release_range = [
        name.strip()
        for name in _git("diff", "--name-only", CARD_BASE, args.base).splitlines()
        if name.strip()
    ]
    release_non_docs = [name for name in release_range if not name.startswith("doc/")]
    log(f"release_range_files={len(release_range)} non_docs={release_non_docs}")

    all_changed = _delivery_files(args.base)
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
    log(f"C16_WORKTREE_SHA256={c16_sha} PIN_MATCH={c16_sha == C16_PIN}")
    # Contract byte identity is asserted on the GIT BLOB (working-tree newline normalization is
    # irrelevant): the delivery HEAD must carry exactly the base commit's contract blobs.
    c16_blob_history = (
        _blob_hash(args.base, "doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md"),
        _blob_hash("HEAD", "doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md"),
    )
    c17_blob_history = (
        _blob_hash(args.base, "doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md"),
        _blob_hash("HEAD", "doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md"),
    )
    contracts_zero_drift = (
        c16_blob_history[0] == c16_blob_history[1]
        and c17_blob_history[0] == c17_blob_history[1]
    )
    log(f"C16_BLOB base={c16_blob_history[0]} head={c16_blob_history[1]} "
        f"ZERO_DRIFT={c16_blob_history[0] == c16_blob_history[1]}")
    log(f"C17_BLOB base={c17_blob_history[0]} head={c17_blob_history[1]} "
        f"ZERO_DRIFT={c17_blob_history[0] == c17_blob_history[1]}")

    zero_drift = [
        prefix for prefix in FORBIDDEN_PREFIXES
        if any(path == prefix or path.startswith(prefix) for path in delivery)
    ]
    log(f"zero_drift_violations={zero_drift}")
    log(f"out_of_scope={out_of_scope}")
    ok = (
        not out_of_scope
        and not forbidden
        and not release_non_docs
        and card_status_ok
        and minor == "3"
        and c16_sha == C16_PIN
        and contracts_zero_drift
    )

    EVIDENCE.mkdir(parents=True, exist_ok=True)
    (EVIDENCE / "changed-files.txt").write_text(
        "\n".join(delivery) + "\n", encoding="utf-8"
    )
    verdict = "PASS" if ok else "FAIL"
    log(
        f"result={verdict} changed={len(delivery)} out_of_scope={out_of_scope} "
        f"forbidden={forbidden} minor={minor} c16_pin_match={c16_sha == C16_PIN}"
    )
    (EVIDENCE / "scope-validation.log").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
