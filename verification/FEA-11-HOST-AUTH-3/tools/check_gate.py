"""FEA-11-HOST-AUTH-3: read the page read-gate state (0 pending => open)."""

import argparse
import json
import sqlite3


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    parser.add_argument("--page-bindings", action="store_true")
    args = parser.parse_args()
    connection = sqlite3.connect(args.db)
    try:
        rows = connection.execute(
            "SELECT read_gate, COUNT(*) FROM source_binding_publications GROUP BY read_gate"
        ).fetchall()
    finally:
        connection.close()
    gates = {str(row[0]): int(row[1]) for row in rows}
    pending = sum(count for gate, count in gates.items() if gate != "open")
    result: dict = {"gates": gates, "pending": pending, "open": pending == 0}
    if args.page_bindings:
        connection = sqlite3.connect(args.db)
        connection.row_factory = sqlite3.Row
        try:
            result["page_bindings"] = [
                dict(row)
                for row in connection.execute(
                    "SELECT * FROM page_bindings ORDER BY page_id"
                )
            ]
        finally:
            connection.close()
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
