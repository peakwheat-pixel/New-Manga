from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

repo = Path(__file__).resolve().parents[2]
target_root = (repo / "apps/desktop/src-tauri/target").resolve()
isolation = Path(sys.argv[1]).resolve()
book_title, chapter_title = sys.argv[2:4]
if not isolation.is_relative_to(target_root):
    raise SystemExit("refusing to inspect a database outside worktree target")

database = isolation / "data/library.db"
connection = sqlite3.connect(f"file:{database.as_posix()}?mode=ro", uri=True)
try:
    books = connection.execute("SELECT book_id FROM books WHERE title = ?", (book_title,)).fetchall()
    if len(books) != 1:
        raise SystemExit(f"expected one created book, found {len(books)}")
    chapters = connection.execute(
        "SELECT chapter_id FROM chapters WHERE book_id = ? AND title = ?",
        (books[0][0], chapter_title),
    ).fetchall()
    if len(chapters) != 1:
        raise SystemExit(f"expected one created chapter for that book, found {len(chapters)}")
    totals = connection.execute(
        "SELECT (SELECT count(*) FROM books), (SELECT count(*) FROM chapters)"
    ).fetchone()
finally:
    connection.close()

print(f"isolated_records=PASS book_count={totals[0]} chapter_count={totals[1]} created_book=true created_chapter=true")
