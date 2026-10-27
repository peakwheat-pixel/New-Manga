#!/usr/bin/env python3
"""Read-only run/translation inspector for REAL-TRANSLATE-PROVIDER-1.

Reports, for the selected pages, the RegionID text triple the translate step
writes (``ocr_text`` → ``machine_translation`` → ``final_translation``), plus
the pipeline runs and their step error codes. Output is a sanitized JSON
(no API key, no credential material anywhere in the database).

Usage:
    python inspect_translate_run.py --db <data-root>/library.db \
        --page-id f52f... --page-id 4f8a... --page-id a607... \
        --out evidence/run-db-<phase>.json
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import time
from pathlib import Path


def _load(conn: sqlite3.Connection, sql: str, params: tuple = ()) -> list[dict]:
    cursor = conn.execute(sql, params)
    columns = [description[0] for description in cursor.description or ()]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    parser.add_argument("--page-id", action="append", default=[])
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    db = Path(args.db)
    if not db.is_file():
        raise SystemExit(f"database not found: {db}")
    conn = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row

    evidence: dict = {
        "ac": "AC3/AC4",
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "db": str(db),
        "pages": [],
        "runs": [],
        "failed_steps": [],
    }

    for page_id in args.page_id:
        regions = _load(
            conn,
            "SELECT region_id, region_type, reading_order, text_json "
            "FROM regions WHERE page_id = ? AND deleted_at IS NULL ORDER BY reading_order, region_id",
            (page_id,),
        )
        items = []
        for region in regions:
            try:
                text = json.loads(region["text_json"])
            except (TypeError, ValueError):
                text = {}
            source = str(text.get("ocr_text", "") or "")
            machine = str(text.get("machine_translation", "") or "")
            final = str(text.get("final_translation", "") or "")
            items.append(
                {
                    "region_id": region["region_id"],
                    "region_type": region["region_type"],
                    "reading_order": region["reading_order"],
                    "source_text": source,
                    "machine_translation": machine,
                    "final_translation": final,
                    "identity": bool(source) and source == machine == final,
                    "translated_differs_from_source": bool(source) and machine not in ("", source),
                    "translation_locked": bool(text.get("translation_locked", False)),
                }
            )
        evidence["pages"].append({"page_id": page_id, "regions": items})

    evidence["runs"] = _load(
        conn,
        "SELECT run_id, command_type, status, updated_at, termination_reason, fatal_error "
        "FROM pipeline_runs ORDER BY rowid DESC LIMIT 8",
    )
    evidence["failed_steps"] = _load(
        conn,
        "SELECT pipeline_run_id AS run_id, step_type, status, target_id, error_code, error_detail "
        "FROM step_runs WHERE status NOT IN ('completed', 'pending') "
        "ORDER BY rowid DESC LIMIT 40",
    )
    evidence["target_states"] = _load(
        conn,
        "SELECT target_type, target_id, stage, status FROM pipeline_stage_states "
        "WHERE status NOT IN ('completed', 'pending') ORDER BY rowid DESC LIMIT 40",
    )
    summary = {
        "pages_with_regions": sum(1 for page in evidence["pages"] if page["regions"]),
        "regions": sum(len(page["regions"]) for page in evidence["pages"]),
        "regions_translated_differs": sum(
            1 for page in evidence["pages"] for region in page["regions"] if region["translated_differs_from_source"]
        ),
        "regions_identity": sum(
            1 for page in evidence["pages"] for region in page["regions"] if region["identity"]
        ),
        "runs": len(evidence["runs"]),
        "failed_steps": len(evidence["failed_steps"]),
    }
    evidence["summary"] = summary
    conn.close()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(evidence, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
