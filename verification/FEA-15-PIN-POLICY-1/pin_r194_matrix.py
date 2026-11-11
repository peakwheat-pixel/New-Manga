#!/usr/bin/env python3
"""Build a modeled r194 match matrix and boundary-sample extract."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
INVENTORY = ROOT / "verification" / "FEA-15-PIN-POLICY-1" / "pin-inventory.json"
OUTPUT = ROOT / "verification" / "FEA-15-PIN-POLICY-1" / "pin-r194-baseline-matrix.json"

SAMPLES = {
    "BLOB_TEXT": "verification/AGPL-RELEASE-1/REPORT.md",
    "WORKTREE_TEXT": "verification/RELEASE-REPACK-6/verify.json",
    "MIXED_EOL_TEXT": "apps/desktop-avalonia/src/NewManga.Appearance/AppearanceJson.cs",
    "BINARY": "verification/CHAPTER-SELECTOR-1/screens/01-bookshelf-two-books.png",
}


def modeled_state(row: dict[str, Any]) -> str:
    pin = str(row.get("pin_sha256") or "")
    if len(pin) != 64:
        return "NO_PIN"
    worktree = row.get("pin_matches_worktree") is True
    blob = row.get("pin_matches_blob") is True
    if worktree and blob:
        return "MATCH_BOTH"
    if worktree:
        return "MATCH_WORKTREE_ONLY"
    if blob:
        return "MATCH_BLOB_ONLY"
    return "PIN_PRESENT_NO_MATCH_OR_UNAVAILABLE"


def main() -> None:
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    rows = inventory["records"]
    state_counts = Counter(modeled_state(row) for row in rows)
    basis_counts = Counter(str(row.get("basis") or "UNKNOWN") for row in rows)
    sample_rows: dict[str, dict[str, Any]] = {}
    for sample_id, path in SAMPLES.items():
        matches = [row for row in rows if str(row.get("path", "")).replace("\\", "/") == path]
        sample_rows[sample_id] = {
            "path": path,
            "row_count": len(matches),
            "records": [
                {
                    key: row.get(key)
                    for key in (
                        "source_file",
                        "evidence_id",
                        "commit",
                        "pin_sha256",
                        "basis",
                        "pin_matches_worktree",
                        "pin_matches_blob",
                        "worktree_eol_profile",
                        "blob_eol_profile",
                        "attributes",
                        "worktree_exists",
                    )
                }
                for row in matches
            ],
        }

    output = {
        "schema_version": 1,
        "measured_head": inventory.get("measured_head"),
        "input_inventory": str(INVENTORY.relative_to(ROOT)),
        "total_pin_rows": len(rows),
        "basis_counts": dict(sorted(basis_counts.items())),
        "modeled_r194_hash_match_state_counts": dict(sorted(state_counts.items())),
        "modeled_accept_predicate_rows": state_counts["MATCH_BOTH"]
        + state_counts["MATCH_WORKTREE_ONLY"]
        + state_counts["MATCH_BLOB_ONLY"],
        "modeled_nonpass_rows": state_counts["NO_PIN"]
        + state_counts["PIN_PRESENT_NO_MATCH_OR_UNAVAILABLE"],
        "samples": sample_rows,
        "limits": [
            "This matrix applies r194's documented worktree-or-commit-blob SHA predicate to inventory observations; it is not a per-row execution of check.ps1.",
            "check.ps1 validates the current Task scope, not every historical Task row in this inventory.",
            "A nonpass observation is not, by itself, an adjudication of corruption, invalid evidence, or permission to rewrite a pin.",
        ],
    }
    OUTPUT.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"HEAD={output['measured_head']}")
    print(f"TOTAL_PIN_ROWS={len(rows)} BASIS_COUNTS={dict(sorted(basis_counts.items()))}")
    print(
        "MODELED_R194="
        f"ACCEPT_PREDICATE={output['modeled_accept_predicate_rows']} "
        f"NONPASS={output['modeled_nonpass_rows']}"
    )
    for sample_id, record in sample_rows.items():
        print(f"SAMPLE={sample_id} PATH={record['path']} ROWS={record['row_count']}")
    print(f"OUTPUT={OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
