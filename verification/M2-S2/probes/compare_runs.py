"""Compare two runs of the M2-S2 probes for repeatability.

Reads the first-run and repeat-run result JSONs and asserts that every
scenario kept its id, status and expected/actual rejection codes, and that
the summary counters match. Emits a small consistency report.

Run:
  python verification/M2-S2/probes/compare_runs.py \
    --first-dir <lab> --repeat-dir <lab> --out <json>
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def _comparable(result: dict) -> dict:
    scenarios = {
        record["id"]: {
            "status": record["status"],
            "expected_rejection_code": record.get("expected_rejection_code"),
            "actual_rejection_code": record.get("actual_rejection_code"),
        }
        for record in result["scenarios"]
    }
    return {"summary": result["summary"], "scenarios": scenarios}


def compare(first_path: Path, repeat_path: Path) -> dict:
    first = _comparable(json.loads(first_path.read_text(encoding="utf-8")))
    repeat = _comparable(json.loads(repeat_path.read_text(encoding="utf-8")))
    differences: list[dict] = []
    ids = sorted(set(first["scenarios"]) | set(repeat["scenarios"]))
    for scenario_id in ids:
        left = first["scenarios"].get(scenario_id)
        right = repeat["scenarios"].get(scenario_id)
        if left != right:
            differences.append({"scenario": scenario_id, "first": left, "repeat": right})
    summary_consistent = first["summary"] == repeat["summary"]
    return {
        "first": str(first_path),
        "repeat": str(repeat_path),
        "scenario_count": len(ids),
        "summary_consistent": summary_consistent,
        "summary_first": first["summary"],
        "summary_repeat": repeat["summary"],
        "differences": differences,
        "consistent": summary_consistent and not differences,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--first-dir", required=True, help="directory holding first-run result JSONs")
    parser.add_argument("--repeat-dir", required=True, help="directory holding repeat-run result JSONs")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    first_dir = Path(args.first_dir)
    repeat_dir = Path(args.repeat_dir)
    report = {
        "purpose": "M2-S2 probe repeatability check (first run vs repeat run)",
        "toctou": compare(first_dir / "toctou-result.json", repeat_dir / "toctou-result.json"),
        "mapping": compare(first_dir / "mapping-result.json", repeat_dir / "mapping-result.json"),
    }
    report["consistent"] = report["toctou"]["consistent"] and report["mapping"]["consistent"]
    text = json.dumps(report, indent=2)
    Path(args.out).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if report["consistent"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
