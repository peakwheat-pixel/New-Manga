from __future__ import annotations

import os
from pathlib import Path
import sys

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from domain.drafts.entities import Draft
from infrastructure.filesystem.draft_journal import DraftJournal


def main() -> int:
    root = Path(sys.argv[1])
    phase = sys.argv[2]
    if phase == "LOCK":
        journal = DraftJournal(root)
        # FEA-03: a second *process* is rejected at the writer lock, which
        # leaves the journal unavailable instead of raising at construction
        # (the Core still starts and only journal writes fail closed).
        if not journal.available:
            return 73
        journal.close()
        return 0

    draft_id = "crash-probe"
    journal = DraftJournal(root)
    old = Draft(draft_id, "s", "p", "r", "base", 1, patch={"text": {"value": "old"}})
    journal.write_draft(old)
    journal.close()

    journal = DraftJournal(root)
    new = Draft(draft_id, "s", "p", "r", "base", 1, patch={"text": {"value": "new"}})
    if phase == "A":
        os._exit(70)
    if phase == "B":
        import infrastructure.filesystem.draft_journal as module
        module.os.replace = lambda _source, _target: os._exit(71)
    if phase == "C":
        journal._fsync_directory = lambda _path: os._exit(72)
    journal.write_draft(new)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
