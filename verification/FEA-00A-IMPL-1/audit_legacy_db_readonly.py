#!/usr/bin/env python3
"""Read-only FEA-00A legacy library consistency audit.

Usage: python audit_legacy_db_readonly.py PATH_TO_EXISTING_LIBRARY_DB
This script does not create, restore, copy, or modify a database or backup.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sqlite3
from urllib.parse import quote


def audit(database: Path) -> dict[str, object]:
    resolved = database.resolve(strict=True)
    if not resolved.is_file():
        raise ValueError(f"not a regular database file: {resolved}")
    uri = "file:" + quote(resolved.as_posix(), safe="/:") + "?mode=ro"
    connection = sqlite3.connect(uri, uri=True)
    connection.row_factory = sqlite3.Row
    try:
        connection.execute("PRAGMA query_only = ON")
        query_only = int(connection.execute("PRAGMA query_only").fetchone()[0])
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
        required = {"regions", "region_revisions", "step_result_candidates"}
        missing = sorted(required - tables)
        if missing:
            return {
                "database": str(resolved),
                "open_mode": "read-only",
                "query_only": query_only,
                "missing_tables": missing,
                "consistent": False,
            }

        totals = connection.execute(
            "SELECT COUNT(*) AS n FROM region_revisions"
        ).fetchone()["n"]
        region_count = 0
        current_count = 0
        missing_current_revision = []
        wrong_region_revision = []
        text_mismatches = []
        for region in connection.execute(
            "SELECT region_id, text_json, current_revision_id FROM regions ORDER BY region_id"
        ):
            region_count += 1
            revision_id = region["current_revision_id"]
            if revision_id is None:
                missing_current_revision.append(region["region_id"])
                continue
            revision = connection.execute(
                "SELECT region_id, snapshot_json FROM region_revisions "
                "WHERE region_revision_id = ?",
                (revision_id,),
            ).fetchone()
            if revision is None:
                missing_current_revision.append(region["region_id"])
                continue
            current_count += 1
            if revision["region_id"] != region["region_id"]:
                wrong_region_revision.append(region["region_id"])
                continue
            try:
                live_text = json.loads(region["text_json"])
                snapshot_text = json.loads(revision["snapshot_json"]).get("text")
            except (TypeError, json.JSONDecodeError):
                text_mismatches.append(region["region_id"])
                continue
            if live_text != snapshot_text:
                text_mismatches.append(region["region_id"])

        candidate_rows = connection.execute(
            "SELECT candidate_id, pipeline_run_id, step_run_id, target_id, status "
            "FROM step_result_candidates ORDER BY candidate_id"
        ).fetchall()
        candidate_status_counts: dict[str, int] = {}
        for row in candidate_rows:
            status = str(row["status"])
            candidate_status_counts[status] = candidate_status_counts.get(status, 0) + 1

        consistent = not (
            missing_current_revision or wrong_region_revision or text_mismatches
        ) and query_only == 1
        return {
            "database": str(resolved),
            "open_mode": "read-only",
            "query_only": query_only,
            "region_count": region_count,
            "regions_with_resolvable_current_revision": current_count,
            "region_revision_count": totals,
            "missing_or_unresolvable_current_revision": missing_current_revision,
            "current_revision_wrong_region": wrong_region_revision,
            "text_json_snapshot_mismatch": text_mismatches,
            "candidate_rows_read": len(candidate_rows),
            "candidate_status_counts": candidate_status_counts,
            "consistent": consistent,
        }
    finally:
        connection.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("database", type=Path, help="existing library SQLite file")
    args = parser.parse_args()
    try:
        result = audit(args.database)
    except (OSError, sqlite3.Error, ValueError) as error:
        print(json.dumps({"consistent": False, "error": str(error)}, ensure_ascii=False, indent=2))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("consistent") else 1


if __name__ == "__main__":
    raise SystemExit(main())
