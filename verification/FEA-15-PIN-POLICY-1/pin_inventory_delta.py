#!/usr/bin/env python3
"""Compare two committed-head pin inventory snapshots without changing either."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
BASELINE = ROOT / "verification" / "FEA-15-PIN-EOL-GOV-1" / "pin-inventory.json"
CURRENT = ROOT / "verification" / "FEA-15-PIN-POLICY-1" / "pin-inventory.json"
OUTPUT = ROOT / "verification" / "FEA-15-PIN-POLICY-1" / "pin-inventory-delta.json"
EXPECTED_BASELINE_HEAD = "948d73e0629869e560df9a2b2d8a357cec67027f"


def identity(row: dict[str, Any]) -> tuple[str, str, str, str]:
    return (
        str(row.get("source_file", "")),
        str(row.get("evidence_id", "")),
        str(row.get("path", "")),
        str(row.get("commit", "")),
    )


def fingerprint(row: dict[str, Any]) -> tuple[str, str, str, str]:
    return (
        str(row.get("pin_sha256", "")),
        str(row.get("class", "")),
        str(row.get("ac_gate", "")),
        str(row.get("expected_source_filename", "")),
    )


def buckets(rows: list[dict[str, Any]]) -> dict[tuple[str, str, str, str], Counter]:
    result: dict[tuple[str, str, str, str], Counter] = defaultdict(Counter)
    for row in rows:
        result[identity(row)][fingerprint(row)] += 1
    return result


def row_details(key: tuple[str, str, str, str], fp: tuple[str, str, str, str], row: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_file": key[0],
        "evidence_id": key[1],
        "path": key[2],
        "commit": key[3],
        "pin_sha256": fp[0],
        "class": fp[1],
        "ac_gate": fp[2],
        "expected_source_filename": fp[3],
        "basis": row.get("basis"),
        "path_scope": row.get("path_scope"),
    }


def main() -> None:
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    current = json.loads(CURRENT.read_text(encoding="utf-8"))
    baseline_head = baseline.get("measured_head", "")
    if baseline_head != EXPECTED_BASELINE_HEAD:
        raise SystemExit(f"unexpected baseline HEAD: {baseline_head}")

    before = buckets(baseline["records"])
    after = buckets(current["records"])
    source_rows = {
        (identity(row), fingerprint(row)): row
        for row in [*baseline["records"], *current["records"]]
    }
    added: list[dict[str, Any]] = []
    removed: list[dict[str, Any]] = []
    changed: list[dict[str, Any]] = []

    for key in sorted(set(before) | set(after)):
        old = before.get(key, Counter()).copy()
        new = after.get(key, Counter()).copy()
        for fp in sorted(set(old) | set(new)):
            common = min(old[fp], new[fp])
            old[fp] -= common
            new[fp] -= common
        old_left = [(fp, count) for fp, count in sorted(old.items()) if count]
        new_left = [(fp, count) for fp, count in sorted(new.items()) if count]

        while old_left and new_left:
            old_fp, old_count = old_left[0]
            new_fp, new_count = new_left[0]
            count = min(old_count, new_count)
            changed.append(
                {
                    "row_count": count,
                    "before": row_details(key, old_fp, source_rows[(key, old_fp)]),
                    "after": row_details(key, new_fp, source_rows[(key, new_fp)]),
                }
            )
            old_left[0] = (old_fp, old_count - count)
            new_left[0] = (new_fp, new_count - count)
            if old_left[0][1] == 0:
                old_left.pop(0)
            if new_left[0][1] == 0:
                new_left.pop(0)

        for fp, count in new_left:
            added.append({"row_count": count, **row_details(key, fp, source_rows[(key, fp)])})
        for fp, count in old_left:
            removed.append({"row_count": count, **row_details(key, fp, source_rows[(key, fp)])})

    before_basis = Counter({k: int(v) for k, v in baseline["basis_counts"].items()})
    after_basis = Counter({k: int(v) for k, v in current["basis_counts"].items()})
    basis_delta = {
        key: after_basis[key] - before_basis[key]
        for key in sorted(set(before_basis) | set(after_basis))
    }
    added_by_source = Counter(row["source_file"] for row in added for _ in range(row["row_count"]))
    added_by_basis = Counter(row.get("basis", "UNKNOWN") for row in added for _ in range(row["row_count"]))

    output = {
        "schema_version": 1,
        "identity_fields": ["source_file", "evidence_id", "path", "commit"],
        "comparison_fields": ["pin_sha256", "class", "ac_gate", "expected_source_filename"],
        "baseline": {
            "path": str(BASELINE.relative_to(ROOT)),
            "measured_head": baseline_head,
            "total_pin_rows": baseline["total_pin_rows"],
            "basis_counts": baseline["basis_counts"],
        },
        "current": {
            "path": str(CURRENT.relative_to(ROOT)),
            "measured_head": current.get("measured_head"),
            "total_pin_rows": current["total_pin_rows"],
            "basis_counts": current["basis_counts"],
        },
        "delta": {
            "added_rows": sum(row["row_count"] for row in added),
            "removed_rows": sum(row["row_count"] for row in removed),
            "changed_rows": sum(row["row_count"] for row in changed),
            "added_by_source_file": dict(sorted(added_by_source.items())),
            "added_by_basis": dict(sorted(added_by_basis.items())),
            "basis_count_delta": basis_delta,
            "added": added,
            "removed": removed,
            "changed": changed,
        },
        "interpretation_limit": "Rows are pin entries, not unique files. Basis labels are generator observations, not adjudications of validity or damage.",
    }
    OUTPUT.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"BASELINE_HEAD={baseline_head}")
    print(f"CURRENT_HEAD={current.get('measured_head')}")
    print(
        "ROWS="
        f"{baseline['total_pin_rows']}->{current['total_pin_rows']} "
        f"ADDED={output['delta']['added_rows']} "
        f"REMOVED={output['delta']['removed_rows']} "
        f"CHANGED={output['delta']['changed_rows']}"
    )
    print(f"BASIS_DELTA={basis_delta}")
    print(f"ADDED_BY_SOURCE={dict(sorted(added_by_source.items()))}")
    print(f"OUTPUT={OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
