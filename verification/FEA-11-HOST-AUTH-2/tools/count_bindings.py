"""FEA-11-HOST-AUTH-2 evidence helper: read-only publication counters.

The gated ACK/recovery IPC tests and the crash-point script need an independent
witness that a refused/duplicated completion creates ZERO new business rows
(C-17 §3.3: "不创建 binding"). This helper opens the isolated fixture
``library.db`` read-only (``mode=ro``) and prints one JSON line.

It never writes, never creates the database, never touches a real user library
and refuses any path outside the FEA-11 fixture envelope.

Usage:
  python count_bindings.py --db <fixture>/library.db
Output (one line):
  {"page_bindings": N, "source_binding_publications": N,
   "pending_publications": N, "source_operations": N}
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
FIXTURE_ROOT = (REPO.parent / f"{REPO.name}.workspace" / "FEA-11" / "fixtures").resolve()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=Path, required=True)
    args = parser.parse_args()

    db = args.db.resolve()
    if not db.is_relative_to(FIXTURE_ROOT):
        print("refused: only an isolated FEA-11 fixture library.db is allowed", file=sys.stderr)
        return 2
    if not db.is_file():
        print(f"missing: {db}", file=sys.stderr)
        return 2

    connection = sqlite3.connect(f"file:{db.as_posix()}?mode=ro", uri=True)
    try:
        def count(sql: str) -> int:
            return int(connection.execute(sql).fetchone()[0])

        counters = {
            "page_bindings": count("SELECT COUNT(*) FROM page_bindings"),
            "source_binding_publications": count(
                "SELECT COUNT(*) FROM source_binding_publications"
            ),
            "pending_publications": count(
                "SELECT COUNT(*) FROM source_binding_publications"
                " WHERE read_gate = 'pending'"
            ),
            "source_operations": count("SELECT COUNT(*) FROM source_operations"),
        }
    finally:
        connection.close()
    print(json.dumps(counters, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
