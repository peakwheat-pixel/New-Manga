"""FEA-11-RUN-GRANT-2C scope validation (card AC-2C-8).

Evaluates the DELIVERY DIFF against the implementation start ``c5f1b416f`` (the
Lead's PREREQ docs-only commit; the dispatch-time start head was ``0475adc72``
and ``0475adc72..c5f1b416f`` is the Lead-owned PREREQ freeze-record fix, reported
here as CONCURRENT_NON_DELIVERY). Every tracked change (committed, staged or
unstaged) plus every untracked file is considered, because the shared ``main``
working tree is used concurrently.

Checks:
* the release range ``fdd170039..0475adc72`` is docs-only (the Lead's 2C release);
* every delivery file is inside the card ``allowed_paths``;
* the explicit out-of-scope surfaces are untouched by the DELIVERY: ``src/**``
  (Core/Python zero diff), every ``tests/**`` file except the ONE allowed
  ``tests/fea11/test_source_run_grant.py``, ``doc/plan/**`` + ``doc/contracts/**``
  (frozen contract bytes), the PREREQ evidence tree, App/UI, the scan/registry
  helper files, schema/dependencies, and the STATUS / REBASELINE_PLAN /
  TASK_LEDGER pointers; the card ``status`` field is never changed by the Owner;
* C-06 v1.3 (``75f8e2b4…``) and C-16 v1.6 (``b8f46fb1…``) are the frozen pins and
  their working-tree bytes match; C-15/C-17 git blobs are unchanged vs the start;
* ``CORE_PROTOCOL_MINOR`` is still 3 (zero wire drift).

Writes:
* ``verification/FEA-11-RUN-GRANT-2C/changed-files.txt``
* ``verification/FEA-11-RUN-GRANT-2C/scope-validation.log``

Usage (repo root):
  C:/Python314/python.exe verification/FEA-11-RUN-GRANT-2C/tools/scope_validation.py
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
TASK_ID = "FEA-11-RUN-GRANT-2C"
EVIDENCE = REPO / "verification" / TASK_ID
CARD = REPO / "doc" / "tasks" / f"{TASK_ID}.md"
CARD_REL = CARD.relative_to(REPO).as_posix()

#: The card's frozen base_commit and the current implementation start head.
CARD_BASE = "fdd170039"
BASE = "c5f1b416f"
#: The Lead-owned PREREQ docs-only commit that landed between dispatch and delivery.
DEFAULT_CONCURRENT = (
    "doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md,"
    "doc/reviews/CONTRACT-UNFREEZE-2026-11-07-C06-C16-RUN-RENEWAL.md,"
    "verification/FEA-11-RUN-GRANT-2C-PREREQ-1/EV.md,"
    "verification/FEA-11-RUN-GRANT-2C-PREREQ-1/carrier.md,"
    "verification/FEA-11-RUN-GRANT-2C-PREREQ-1/logs/check-taskpath.log,"
    "verification/FEA-11-RUN-GRANT-2C-PREREQ-1/logs/check.log"
)

C06 = REPO / "doc" / "plan" / "FEA-C06_SOURCE_AUTH_DRAFT.md"
C06_PIN = "75f8e2b4eb808a7b33f503ae64e6455a390587a552a2689df9ce2ae133341c84"
C16 = REPO / "doc" / "plan" / "FEA-C16_SOURCE_READ_WIRE_DRAFT.md"
C16_PIN = "b8f46fb1feec7c85bc997516f1e7fa9d51ab46717cb4dcf982d8c6e7db1d18a0"

FORBIDDEN_PREFIXES = (
    "src/",
    "tests/",
    "doc/plan/",
    "doc/contracts/",
    "verification/FEA-11-RUN-GRANT-2C-PREREQ-1/",
    "requirements.txt",
    "pyproject.toml",
    "package.json",
    "apps/desktop-avalonia/src/NewManga.App/",
    "apps/desktop-avalonia/src/NewManga.CoreClient/CoreServiceClient.cs",
    "apps/desktop-avalonia/src/NewManga.CoreClient/Commands/RunContracts.cs",
    "apps/desktop-avalonia/src/NewManga.Host/Sources/SourceScanScheduler.cs",
    "apps/desktop-avalonia/src/NewManga.Host/Sources/SourceAccessRegistry.cs",
    "apps/desktop-avalonia/src/NewManga.Host/Sources/SourceRootReattestPlanner.cs",
    "apps/desktop-avalonia/src/NewManga.Host/Sources/SourceWatcher.cs",
    "apps/desktop-avalonia/tests/NewManga.App.Tests/",
    "doc/STATUS.md",
    "doc/REBASELINE_PLAN.md",
    "doc/TASK_LEDGER",
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


def _blob_hash(rev: str, path: str) -> str:
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

    release_range = [
        name.strip()
        for name in _git("diff", "--name-only", CARD_BASE, args.base).splitlines()
        if name.strip()
    ]
    release_non_docs = [
        name for name in release_range
        if not name.startswith(("doc/", "verification/"))
    ]
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
    # An allowed path always wins over a blanket forbidden prefix (the ONE Python test
    # file is an explicit card In; every other tests/** file stays forbidden).
    forbidden = [
        path for path in delivery
        if not any(_matches(entry, path) for entry in allowed)
        and any(path == prefix or path.startswith(prefix) for prefix in FORBIDDEN_PREFIXES)
    ]

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

    c06_sha = hashlib.sha256(C06.read_bytes()).hexdigest() if C06.is_file() else "MISSING"
    c16_sha = hashlib.sha256(C16.read_bytes()).hexdigest() if C16.is_file() else "MISSING"
    pins_ok = c06_sha == C06_PIN and c16_sha == C16_PIN
    log(f"C06_SHA256={c06_sha} PIN_MATCH={c06_sha == C06_PIN}")
    log(f"C16_SHA256={c16_sha} PIN_MATCH={c16_sha == C16_PIN}")

    unchanged_blobs = True
    for path in ("doc/plan/FEA-C15_SOURCE_STORAGE_DRAFT.md",
                 "doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md"):
        base_blob = _blob_hash(args.base, path)
        head_blob = _blob_hash("HEAD", path)
        same = base_blob == head_blob
        unchanged_blobs = unchanged_blobs and same
        log(f"BLOB {path} base={base_blob[:12]} head={head_blob[:12]} ZERO_DRIFT={same}")

    zero_drift = [
        prefix for prefix in FORBIDDEN_PREFIXES
        if any((path == prefix or path.startswith(prefix))
               and not any(_matches(entry, path) for entry in allowed)
               for path in delivery)
    ]
    log(f"zero_drift_violations={zero_drift}")
    log(f"out_of_scope={out_of_scope}")
    ok = (
        not out_of_scope
        and not forbidden
        and not release_non_docs
        and card_status_ok
        and minor == "3"
        and pins_ok
        and unchanged_blobs
    )

    EVIDENCE.mkdir(parents=True, exist_ok=True)
    (EVIDENCE / "changed-files.txt").write_text(
        "\n".join(delivery) + "\n", encoding="utf-8"
    )
    verdict = "PASS" if ok else "FAIL"
    log(
        f"result={verdict} changed={len(delivery)} out_of_scope={out_of_scope} "
        f"forbidden={forbidden} minor={minor} pins_ok={pins_ok} blobs_ok={unchanged_blobs}"
    )
    (EVIDENCE / "scope-validation.log").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
