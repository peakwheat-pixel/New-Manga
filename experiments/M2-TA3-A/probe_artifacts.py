"""M2-TA3-A evidence probe: extract ocr/translate/inpaint samples from the
per-case scratch databases left by run_smoke.py (fail-closed: a missing db
is reported, never faked). Read-only."""
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

SCRATCH = {
    "BJ02": Path(r"C:/Users/49745/AppData/Local/Temp/m2-ta3a-BJ02-1v1ot28i/library.sqlite"),
    "BJ06": Path(r"C:/Users/49745/AppData/Local/Temp/m2-ta3a-BJ06-uv6v_jij/library.sqlite"),
    "K01": Path(r"C:/Users/49745/AppData/Local/Temp/m2-ta3a-K01-385hq0yw/library.sqlite"),
    "K02": Path(r"C:/Users/49745/AppData/Local/Temp/m2-ta3a-K02-_2i0xj4s/library.sqlite"),
    "K11": Path(r"C:/Users/49745/AppData/Local/Temp/m2-ta3a-K11-erhinxx2/library.sqlite"),
}

SAMPLES_PER_STEP = 2


def samples_for(conn: sqlite3.Connection, step_type: str) -> list[dict]:
    rows = conn.execute(
        "SELECT r.ref_key, r.value_json FROM step_run_output_refs r "
        "JOIN step_runs o ON o.step_run_id = r.step_run_id "
        "WHERE o.step_type = ? ORDER BY o.step_run_id LIMIT ?",
        (step_type, SAMPLES_PER_STEP * 4),
    ).fetchall()
    return [{"ref_key": row[0], "value": (row[1] or "")[:160]} for row in rows[:SAMPLES_PER_STEP]]


def main() -> int:
    failures = 0
    report: dict = {}
    for case_id, db_path in SCRATCH.items():
        if not db_path.is_file():
            print(f"{case_id}\tPROBE_FAILED\tdb missing: {db_path}", file=sys.stderr)
            failures += 1
            continue
        conn = sqlite3.connect(db_path)
        try:
            entry = {
                "db": str(db_path),
                "step_counts": {
                    row[0]: {"total": row[1], "completed": row[2]}
                    for row in conn.execute(
                        "SELECT step_type, COUNT(*), SUM(status='completed') "
                        "FROM step_runs GROUP BY step_type ORDER BY step_type"
                    )
                },
                "ocr_samples": samples_for(conn, "ocr"),
                "translate_samples": samples_for(conn, "translate"),
                "inpaint_samples": samples_for(conn, "inpaint"),
                "render_samples": samples_for(conn, "render"),
            }
            report[case_id] = entry
            print(f"{case_id}\tPROBE_OK\tsteps={len(entry['step_counts'])}")
        finally:
            conn.close()
    out = Path("verification/M2-TA3-A/summaries/artifact-samples.json")
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"report -> {out}")
    print(f"SUMMARY cases={len(SCRATCH)} failures={failures}")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
