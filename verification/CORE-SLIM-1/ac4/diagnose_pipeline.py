"""CORE-SLIM-1 / AC4 diagnostic: why does the acceptance pipeline now end
``completed_with_failures`` after the Qt->Pillow adapter switch?

Runs the exact ``tests/core/test_sfx_policy_end_to_end._scenario`` shape in a
plain process and dumps every step/task status plus its ``error_detail``.
Not product code and not a gate artefact: a one-off RCA helper kept with the
evidence so the recorded conclusion is reproducible.
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests" / "core"))

from _pytest.monkeypatch import MonkeyPatch  # noqa: E402

import test_sfx_policy_end_to_end as scenario_module  # noqa: E402


def main() -> int:
    scratch = Path(tempfile.mkdtemp(prefix="dp1-ac4-", dir=ROOT / "verification" / "CORE-SLIM-1" / "ac4"))
    monkey = MonkeyPatch()
    try:
        core, chapter_id, page_id, finished, _build = scenario_module._scenario(
            scratch, monkey, "translate"
        )
        print("run status:", finished.status)
        print("step runs:")
        for step in finished.step_runs:
            print(
                "  ",
                step.step_type,
                step.status,
                "| detail=",
                (getattr(step, "error_detail", None) or "")[:600],
            )
        print("tasks:")
        for task in finished.tasks:
            print(
                "  ",
                getattr(task, "task_type", getattr(task, "command", "?")),
                task.status,
                "| detail=",
                (getattr(task, "error_detail", None) or "")[:600],
            )
            for unit in getattr(task, "units", ()):
                print(
                    "     unit",
                    unit.step_type,
                    unit.decision,
                    unit.reason,
                    "| detail=",
                    (getattr(unit, "error_detail", None) or "")[:400],
                )
        print("regions:")
        rows = core.conn.execute(
            "SELECT region_id, region_type, sfx_policy, text_json FROM regions"
            " WHERE page_id = ? ORDER BY reading_order",
            (page_id,),
        ).fetchall()
        for row in rows:
            print("  ", row["region_type"], row["sfx_policy"], row["text_json"][:200])
        core.conn.close()
    finally:
        monkey.undo()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
