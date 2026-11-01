from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from infrastructure.filesystem.draft_journal import DraftJournal

WORKER = ROOT / "tests/infrastructure/draft_journal_crash_worker.py"


def main() -> None:
    rows = []
    with tempfile.TemporaryDirectory(prefix="fea03-crash-") as temporary:
        for phase, exit_code, expected in (
            ("A", 70, "old"),
            ("B", 71, "old"),
            ("C", 72, "new"),
        ):
            root = Path(temporary) / phase
            process = subprocess.run(
                [sys.executable, str(WORKER), str(root), phase],
                cwd=ROOT, capture_output=True, text=True,
            )
            assert process.returncode == exit_code, (phase, process.returncode, process.stderr)
            journal = DraftJournal(root)
            recovered = journal.load_drafts()
            assert len(recovered) == 1
            actual = recovered[0][0].patch["text"]["value"]
            assert actual == expected, (phase, actual)
            assert not list(root.glob("*.tmp"))
            journal.close()
            rows.append(
                {"phase": phase, "exit": process.returncode,
                 "recovered": actual, "tmp_clean": True}
            )

        lock_root = Path(temporary) / "lock"
        first = DraftJournal(lock_root)
        blocked = subprocess.run(
            [sys.executable, str(WORKER), str(lock_root), "LOCK"],
            cwd=ROOT, capture_output=True, text=True,
        )
        first.close()
        released = subprocess.run(
            [sys.executable, str(WORKER), str(lock_root), "LOCK"],
            cwd=ROOT, capture_output=True, text=True,
        )
        assert blocked.returncode == 73
        assert released.returncode == 0
        rows.append(
            {"phase": "LOCK", "second_exit": blocked.returncode,
             "after_release_exit": released.returncode}
        )

    print(json.dumps(rows, sort_keys=True))


if __name__ == "__main__":
    main()
