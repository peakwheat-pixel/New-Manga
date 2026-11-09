"""FEA-11-HOST-AUTH-3: read the page read-gate state (0 pending => open)."""

import argparse
import json
import sqlite3


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
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
    print(json.dumps({"gates": gates, "pending": pending, "open": pending == 0}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
