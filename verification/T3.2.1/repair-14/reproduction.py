"""Reproduction probe for T3.2.1-REPAIR-14 / F-13-3.

Demonstrates that when an application restarts with an existing SQLite database
containing books, BookshelfViewModel initializes an empty BookListModel (rowCount=0)
even though the database contains books (isEmpty=False).
"""

from __future__ import annotations

import os
import shutil
import sqlite3
import sys
import tempfile
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

# Add src to Python path
SRC_DIR = Path(__file__).resolve().parents[3] / "src"
sys.path.insert(0, str(SRC_DIR))

from bootstrap.app import assemble_services
from PySide6.QtGui import QGuiApplication


def run_reproduction() -> int:
    temp_dir = tempfile.mkdtemp(prefix="repair14-repro-")
    data_root = Path(temp_dir)
    db_path = data_root / "library.db"
    managed_root = data_root / "managed"

    print("=== T3.2.1-REPAIR-14 / F-13-3 Reproduction Run ===")
    print(f"Data root: {data_root}")
    print(f"Database: {db_path}")

    app = QGuiApplication.instance() or QGuiApplication([])

    # ------------------------------------------------------------------
    # Session 1: Initial startup, create a book, refresh, and clean exit
    # ------------------------------------------------------------------
    print("\n--- Session 1: First launch on clean data root ---")
    s1 = assemble_services(db_path=db_path, managed_root=managed_root)
    print(f"Session 1 initial isEmpty: {s1.bookshelf.isEmpty}")
    print(f"Session 1 initial bookCount: {s1.bookshelf.bookCount}")

    book = s1.library.create_book("复现测试漫画", original_title="Repro Manga Vol 1")
    print(f"Session 1 created book: id={book.book_id}, title={book.title}")

    # Explicit refresh in session 1 (simulating GUI import/creation reaction)
    s1.bookshelf.refreshBooks()
    print(f"Session 1 after refreshBooks() bookCount: {s1.bookshelf.bookCount}")
    print(f"Session 1 after refreshBooks() rowCount: {s1.bookshelf.bookListModel.rowCount()}")
    s1.conn.close()
    print("Session 1 closed gracefully.")

    # ------------------------------------------------------------------
    # SQLite Direct Verification: Check database on disk
    # ------------------------------------------------------------------
    print("\n--- Direct SQLite Inspection ---")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT book_id, title, original_title FROM books")
    rows = cur.fetchall()
    print(f"SQLite books table row count: {len(rows)}")
    for r in rows:
        print(f"  Row: book_id={r[0]}, title={r[1]}, original_title={r[2]}")
    conn.close()

    # ------------------------------------------------------------------
    # Session 2: Second launch (restart) on the EXACT SAME data root
    # ------------------------------------------------------------------
    print("\n--- Session 2: Relaunch on the same data root (Restart Simulation) ---")
    s2 = assemble_services(db_path=db_path, managed_root=managed_root)
    print(f"Session 2 bookshelf.isEmpty: {s2.bookshelf.isEmpty}")
    print(f"Session 2 bookshelf.bookCount: {s2.bookshelf.bookCount}")
    print(f"Session 2 bookshelf.bookListModel.rowCount(): {s2.bookshelf.bookListModel.rowCount()}")
    print(f"Session 2 bookshelf.selectedBook: {s2.bookshelf.selectedBook}")

    bug_confirmed = False
    if s2.bookshelf.isEmpty is False and s2.bookshelf.bookListModel.rowCount() == 0:
        bug_confirmed = True
        print("\n>>> [DEFECT F-13-3 CONFIRMED] <<<")
        print("  - SQLite has 1 book, so bookshelf.isEmpty is False (QML hides EmptyState).")
        print("  - However, bookshelf.bookListModel has rowCount == 0 (QML BookGrid renders 0 items).")
        print("  - Result: The user sees an empty shelf without even an empty state banner.")

    s2.conn.close()
    shutil.rmtree(temp_dir, ignore_errors=True)
    return 0 if bug_confirmed else 1


if __name__ == "__main__":
    sys.exit(run_reproduction())
