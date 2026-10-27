# -*- coding: utf-8 -*-
"""CHAPTER-SELECTOR-1 real-machine data: duplicate the BOOK-FIXTURE durable state into two books
and two chapters so the reader's multi-book entry and chapter picker can be exercised for real.

Only the *copy* under task-envs/CHAPTER-SELECTOR-1/isolated-data is modified; the source fixture is
left untouched. Page rows are duplicated with fresh ids and freshly copied managed image files so
every page keeps a resolvable managed_original_ref.
"""
import os
import shutil
import sqlite3
import uuid
from datetime import datetime, timezone

TASK = r"G:\CODEX\New Manga.workspace\task-envs\CHAPTER-SELECTOR-1"
SRC = r"G:\CODEX\New Manga.workspace\task-envs\BOOK-FIXTURE-1\isolated-data"
DST = os.path.join(TASK, "isolated-data")

now = datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "+00:00")


def hexid() -> str:
    return uuid.uuid4().hex


def copy_durable():
    if os.path.isdir(DST):
        shutil.rmtree(DST)
    os.makedirs(DST)
    for root, dirs, files in os.walk(SRC):
        rel = os.path.relpath(root, SRC)
        if rel.split(os.sep)[0] in {"logs", "backups", "derived", "catalog"}:
            continue
        for name in files:
            if name.endswith(".lock"):
                continue
            src_path = os.path.join(root, name)
            dst_dir = os.path.join(DST, rel) if rel != "." else DST
            os.makedirs(dst_dir, exist_ok=True)
            shutil.copy2(src_path, os.path.join(dst_dir, name))


def duplicate_pages(con, src_chapter, new_chapter, count, label):
    rows = con.execute(
        "select page_id, sort_order, source_filename, source_order, source_hash, source_size_bytes,"
        " width, height, managed_original_ref, page_locked, review_state, overall_status"
        " from pages where chapter_id=? and deleted_at is null order by sort_order limit ?",
        (src_chapter, count),
    ).fetchall()
    created = []
    for index, row in enumerate(rows):
        (_, sort_order, source_filename, source_order, source_hash, size, width, height,
         managed_ref, locked, review, status) = row
        new_page = hexid()
        new_ref = managed_ref
        if managed_ref:
            src_file = os.path.join(SRC, "managed", managed_ref.replace("/", os.sep))
            suffix = os.path.splitext(managed_ref)[1] or ".jpg"
            new_ref = f"books/{new_chapter}/pages/{new_page}{suffix}"
            dst_file = os.path.join(DST, "managed", new_ref.replace("/", os.sep))
            os.makedirs(os.path.dirname(dst_file), exist_ok=True)
            shutil.copy2(src_file, dst_file)
        con.execute(
            "insert into pages (page_id, chapter_id, sort_order, created_at, updated_at, deleted_at,"
            " source_filename, source_order, source_hash, source_size_bytes, width, height,"
            " managed_original_ref, page_locked, review_state, overall_status)"
            " values (?,?,?,?,?,NULL,?,?,?,?,?,?,?,?,?,?)",
            (new_page, new_chapter, sort_order + 1000 * 0 + index, now, now, source_filename,
             source_order, source_hash, size, width, height, new_ref, locked, review, status),
        )
        created.append(new_page)
    print(f"{label}: {len(created)} pages")
    return created


def main():
    copy_durable()
    con = sqlite3.connect(os.path.join(DST, "library.db"))
    con.execute("pragma foreign_keys=on")
    try:
        src_book = con.execute("select * from books limit 1").fetchone()
        book_cols = [d[0] for d in con.execute("select * from books limit 1").description]
        src_book_map = dict(zip(book_cols, src_book))
        src_chapter = con.execute(
            "select * from chapters where book_id=? order by sort_order limit 1",
            (src_book_map["book_id"],),
        ).fetchone()
        chapter_cols = [d[0] for d in con.execute("select * from chapters limit 1").description]
        src_chapter_map = dict(zip(chapter_cols, src_chapter))

        # --- chapter 2 of book 1 (4 pages): the picker switches to a different projection ---
        chapter_a2 = hexid()
        con.execute(
            "insert into chapters (chapter_id, book_id, title, sort_order, created_at, updated_at,"
            " deleted_at, chapter_number, subtitle, import_order, chapter_type, reading_direction, notes)"
            " values (?,?,?,?,?,?,NULL,?,?,?,?,?,?)",
            (chapter_a2, src_book_map["book_id"], "第二章 测试章", 2, now, now, "2", "",
             2, "webtoon", "vertical", ""),
        )
        duplicate_pages(con, src_chapter_map["chapter_id"], chapter_a2, 4, "book A / chapter 2")

        # --- book 2 + its first chapter (3 pages): the bookshelf opens a different book ---
        book_b = hexid()
        con.execute(
            "insert into books (book_id, title, created_at, updated_at, deleted_at, original_title,"
            " author, publisher, series_title, description, source_language, target_language,"
            " source_url, notes, default_chapter_type, default_reading_direction, is_favorite,"
            " is_archived, last_opened_at)"
            " values (?,?,?,?,NULL,?,?,?,?,?,?,?,?,?,?,?,?,?,NULL)",
            (book_b, "BOOK-FIXTURE-1 副本B 日漫_JA 测试书", now, now, "BOOK-FIXTURE-1 copy B", "",
             "", "", "", "", "", "", "", "webtoon", "vertical", 0, 0),
        )
        chapter_b1 = hexid()
        con.execute(
            "insert into chapters (chapter_id, book_id, title, sort_order, created_at, updated_at,"
            " deleted_at, chapter_number, subtitle, import_order, chapter_type, reading_direction, notes)"
            " values (?,?,?,?,?,?,NULL,?,?,?,?,?,?)",
            (chapter_b1, book_b, "第 1 章 · 副本", 1, now, now, "1", "", 1, "webtoon", "vertical", ""),
        )
        duplicate_pages(con, src_chapter_map["chapter_id"], chapter_b1, 3, "book B / chapter 1")

        con.commit()
        print("books:", [(r[0][:8], r[1]) for r in con.execute("select book_id, title from books")])
        print("chapters:", [(r[0][:8], r[1][:8], r[2], r[3]) for r in con.execute(
            "select chapter_id, book_id, title, sort_order from chapters order by book_id, sort_order")])
        print("pages:", con.execute("select count(*) from pages").fetchone()[0])
    finally:
        con.close()
    print("data root:", DST)


if __name__ == "__main__":
    main()
