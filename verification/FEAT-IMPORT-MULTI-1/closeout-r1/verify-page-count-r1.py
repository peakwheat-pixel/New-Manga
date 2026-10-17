from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

root = Path(sys.argv[1]).resolve()
approved = (Path(sys.argv[3]) / "feat-import-multi-r1").resolve()
if root != approved:
    raise SystemExit("refusing to inspect a database outside the approved TEMP isolation root")
title = sys.argv[2]
database = root / "fresh-data/library.db"
if not database.is_file():
    raise SystemExit("isolated library database is missing")
connection = sqlite3.connect(f"file:{database.as_posix()}?mode=ro", uri=True, timeout=20)
try:
    rows = connection.execute(
        "SELECT c.chapter_id, COUNT(p.page_id) FROM chapters c "
        "LEFT JOIN pages p ON p.chapter_id = c.chapter_id "
        "WHERE c.title = ? AND c.deleted_at IS NULL GROUP BY c.chapter_id",
        (title,),
    ).fetchall()
finally:
    connection.close()
if len(rows) != 1:
    raise SystemExit(f"expected one isolated chapter match, found {len(rows)}")
print(f"chapter_pages={int(rows[0][1])} database=fresh-data/library.db")
