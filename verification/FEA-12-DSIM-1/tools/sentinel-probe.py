"""FEA-12-DSIM-1 — runtime sentinel probe (independent of pytest).

Builds a self-cleaning scratch tree in the OS temp directory (the same
location family as pytest ``tmp_path``, per ADJ-2026-11-05 §D7 item 3) and
proves at runtime that every path **outside** the simulated bin's isolated
root is byte-identical after:

1. a successful simulated recycle of a real file,
2. an injected-refusal simulated recycle (original must stay put),
3. the fail-closed production default over a real file (zero operations).

Usage:
    C:/Python314/python.exe verification/FEA-12-DSIM-1/tools/sentinel-probe.py

Exit code 0 = sentinel unchanged (PASS); 1 = violation / unexpected change.
"""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "src"))

from application.maintenance.recycle_gateway import (  # noqa: E402
    OriginalFileRecycleGateway,
    REASON_IN_USE,
    RecycleEntry,
    UnavailableOriginalFileRecycleGateway,
)
from infrastructure.filesystem.simulated_recycle_bin import (  # noqa: E402
    JsonLinesRecycleJournal,
    SimulatedRecycleBin,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _snapshot(root: Path, *, exclude: Path | None = None) -> dict[str, str]:
    snapshot: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if exclude is not None and (path == exclude or exclude in path.parents):
            continue
        relative = path.relative_to(root).as_posix()
        if path.is_dir():
            snapshot[relative] = "dir"
        else:
            snapshot[relative] = f"{path.stat().st_size}:{_sha256(path)}"
    return snapshot


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="fea12-dsim-sentinel-") as scratch:
        workspace = Path(scratch)
        isolated = workspace / "isolated-root"
        isolated.mkdir()
        outside = workspace / "outside-sentinel"
        (outside / "user-sources").mkdir(parents=True)
        sentinel_png = outside / "user-sources" / "chapter-01.png"
        sentinel_png.write_bytes(b"ORIGINAL PIXELS 01")
        sentinel_note = outside / "notes.txt"
        sentinel_note.write_text("keep me verbatim", encoding="utf-8")

        outside_before = _snapshot(workspace, exclude=isolated)
        sentinel_hashes_before = {
            "chapter-01.png": _sha256(sentinel_png),
            "notes.txt": _sha256(sentinel_note),
        }
        print(f"scratch root          : {workspace}")
        print(f"isolated root         : {isolated}")
        print(f"outside sentinel tree : {outside}")
        print("sentinel before       : " + json.dumps(sentinel_hashes_before))

        # 1) successful simulated recycle of a real file inside the isolated root
        success_target = isolated / "user-sources" / "page-01.png"
        success_target.parent.mkdir(parents=True)
        success_target.write_bytes(b"PAGE ONE")
        simulated = SimulatedRecycleBin(isolated)
        assert isinstance(simulated, OriginalFileRecycleGateway)
        success = simulated.move_to_recyclebin(
            [RecycleEntry("req-1", str(success_target))],
            journal=JsonLinesRecycleJournal(isolated),
        )
        print("run 1 (success)       : " + json.dumps(success.to_dict()))
        if not (success.complete and not success_target.exists()):
            print("FAIL: successful recycle did not move the isolated target")
            return 1

        # 2) injected refusal: the original must stay exactly where it was
        refused_target = isolated / "user-sources" / "locked.png"
        refused_target.write_bytes(b"LOCKED ORIGINAL")
        refused = SimulatedRecycleBin(
            isolated, failure_injector=lambda entry: REASON_IN_USE
        ).move_to_recyclebin(
            [RecycleEntry("req-2", str(refused_target))],
            journal=JsonLinesRecycleJournal(isolated),
        )
        print("run 2 (refused)       : " + json.dumps(refused.to_dict()))
        if refused.items[0].reason != REASON_IN_USE or not refused_target.exists():
            print("FAIL: refused item was not kept in place")
            return 1
        if refused_target.read_bytes() != b"LOCKED ORIGINAL":
            print("FAIL: refused item bytes changed")
            return 1

        # 3) fail-closed production default over a real file (zero operations)
        default_target = isolated / "user-sources" / "default.png"
        default_target.write_bytes(b"DEFAULT ORIGINAL")
        unavailable = UnavailableOriginalFileRecycleGateway()
        assert isinstance(unavailable, OriginalFileRecycleGateway)
        unavailable_outcome = unavailable.move_to_recyclebin(
            [RecycleEntry("req-3", str(default_target))],
            journal=JsonLinesRecycleJournal(isolated),
        )
        print("run 3 (unavailable)   : " + json.dumps(unavailable_outcome.to_dict()))
        if unavailable_outcome.not_started != 1 or not default_target.exists():
            print("FAIL: production default was not typed-unavailable/zero-op")
            return 1

        # sentinel proof: nothing outside the isolated root moved or changed
        outside_after = _snapshot(workspace, exclude=isolated)
        sentinel_hashes_after = {
            "chapter-01.png": _sha256(sentinel_png),
            "notes.txt": _sha256(sentinel_note),
        }
        print("sentinel after        : " + json.dumps(sentinel_hashes_after))
        changed_outside = sorted(
            set(outside_before) ^ set(outside_after)
            | {
                key
                for key in set(outside_before) & set(outside_after)
                if outside_before[key] != outside_after[key]
            }
        )
        print("outside changes       : " + json.dumps(changed_outside))
        isolated_changes = sorted(
            set(_snapshot(isolated)) - set(outside_before)
        )
        print("isolated-root entries : " + json.dumps(isolated_changes))
        if sentinel_hashes_after != sentinel_hashes_before:
            print("FAIL: outside sentinel bytes changed")
            return 1
        if changed_outside:
            print("FAIL: paths outside the isolated root changed")
            return 1
        if not isolated_changes:
            print("FAIL: isolated root did not change (nothing was exercised)")
            return 1
        print("PASS: runtime sentinel outside the isolated root unchanged")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
