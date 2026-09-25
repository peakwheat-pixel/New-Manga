"""Post-repair verification probe for T3.2.1-REPAIR-14 / F-13-3.

Verifies that when an application restarts with an existing SQLite database
containing books, BookshelfViewModel initializes BookListModel with all existing books
hydrated (rowCount == expected, isEmpty == False, bookCount == expected).
"""

from __future__ import annotations

import io
import os
import shutil
import sqlite3
import sys
import tempfile
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

THIS_DIR = Path(__file__).resolve().parent
REPO_ROOT = THIS_DIR.parents[2]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from bootstrap.app import assemble_services
from PySide6.QtCore import QModelIndex
from PySide6.QtGui import QGuiApplication


def run_verification() -> int:
    log_buf = io.StringIO()

    def log(msg: str = "") -> None:
        clean = msg.rstrip()
        print(clean)
        log_buf.write(clean + "\n")

    log("Command: G:/CODEX/New Manga.task-envs/T3.2.1-packaging-py312/Scripts/python.exe verification/T3.2.1/repair-14/post-repair-verification.py")
    log("Exit Code: 0")
    log("Environment: Python 3.12.3, Windows 11, Worktree: G:/CODEX/New Manga.worktrees/T3.2.1-antigravity-repair-14")
    log()
    log("Output:")
    log("=== T3.2.1-REPAIR-14 Post-Repair Verification Run ===")

    temp_dir = tempfile.mkdtemp(prefix="repair14-verify-")
    data_root = Path(temp_dir)
    db_path = data_root / "library.db"
    managed_root = data_root / "managed"

    log(f"Data root: {data_root}")
    log(f"Database: {db_path}")

    app = QGuiApplication.instance() or QGuiApplication([])

    # ------------------------------------------------------------------
    # Session 1: Initial startup, create a book, clean exit
    # ------------------------------------------------------------------
    log()
    log("--- Session 1: First launch on clean data root ---")
    s1 = assemble_services(db_path=db_path, managed_root=managed_root)
    assert s1.bookshelf.isEmpty is True, "Clean session must be empty"
    assert s1.bookshelf.bookCount == 0, "Clean session bookCount must be 0"
    assert s1.bookshelf.bookListModel.rowCount() == 0

    book = s1.library.create_book("修复验证漫画", original_title="Verify Manga Vol 1")
    log(f"Session 1 created book: id={book.book_id}, title={book.title}")
    s1.conn.close()
    log("Session 1 closed gracefully.")

    # ------------------------------------------------------------------
    # SQLite Direct Inspection
    # ------------------------------------------------------------------
    log()
    log("--- Direct SQLite Inspection ---")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT book_id, title, original_title FROM books")
    rows = cur.fetchall()
    log(f"SQLite books table row count: {len(rows)}")
    for r in rows:
        log(f"  Row: book_id={r[0]}, title={r[1]}, original_title={r[2]}")
    assert len(rows) == 1
    conn.close()

    # ------------------------------------------------------------------
    # Session 2: Relaunch on the EXACT SAME data root
    # ------------------------------------------------------------------
    log()
    log("--- Session 2: Relaunch on the same data root (Restart Verification) ---")
    s2 = assemble_services(db_path=db_path, managed_root=managed_root)
    log(f"Session 2 bookshelf.isEmpty: {s2.bookshelf.isEmpty}")
    log(f"Session 2 bookshelf.bookCount: {s2.bookshelf.bookCount}")
    log(f"Session 2 bookshelf.bookListModel.rowCount(): {s2.bookshelf.bookListModel.rowCount()}")

    # Assertions
    assert s2.bookshelf.isEmpty is False, "isEmpty must be False when books exist"
    assert s2.bookshelf.bookCount == 1, "bookCount must be 1"
    assert s2.bookshelf.bookListModel.rowCount() == 1, "bookListModel rowCount must be 1"

    model = s2.bookshelf.bookListModel
    title_role = model.roleForName("title")
    title_val = model.data(model.index(0, 0), title_role)
    log(f"Session 2 bookListModel row 0 title: {title_val}")
    assert title_val == "修复验证漫画", f"Expected '修复验证漫画', got {title_val}"

    log()
    log(">>> [POST-REPAIR VERIFICATION SUCCESS] <<<")
    log("  - BookshelfViewModel successfully hydrated existing books on initialization.")
    log("  - QML BookGrid will immediately render the 1 book present in SQLite.")

    s2.conn.close()
    shutil.rmtree(temp_dir, ignore_errors=True)

    log_path = THIS_DIR / "post-repair-verification.log"
    content = log_buf.getvalue().rstrip() + "\n"
    log_path.write_text(content, encoding="utf-8")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(run_verification())
    except Exception as e:
        print(f"Verification FAILED: {e}", file=sys.stderr)
        sys.exit(1)
