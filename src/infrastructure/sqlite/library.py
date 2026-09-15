"""SQLite adapter for the library, page-import and page-round-trip
contracts (TASK-029, per the frozen TASK-028 design §2.1/§3).

Implements ``LibraryRepository`` + ``ImportPageSink`` + ``PageRepository``
structurally over the shared connection. Book/Chapter/Tag live in the v1
tables completed by v2; pages tolerate v1 structural placeholder rows
(import columns NULL) — such rows are never surfaced as Page objects and
import reads (dedup/next order) only consider fully imported rows.
"""

from __future__ import annotations

import sqlite3

from domain.books.entities import Book, Chapter, ChapterType, ReadingDirection, Tag
from domain.pages.entities import Page


class SqliteLibraryRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    # ------------------------------------------------------------------
    # row mappers
    # ------------------------------------------------------------------

    @staticmethod
    def _book_from_row(row: sqlite3.Row) -> Book:
        return Book(
            book_id=row["book_id"],
            title=row["title"],
            original_title=row["original_title"],
            author=row["author"],
            publisher=row["publisher"],
            series_title=row["series_title"],
            description=row["description"],
            source_language=row["source_language"],
            target_language=row["target_language"],
            source_url=row["source_url"],
            notes=row["notes"],
            default_chapter_type=ChapterType(row["default_chapter_type"]),
            default_reading_direction=ReadingDirection(row["default_reading_direction"]),
            is_favorite=bool(row["is_favorite"]),
            is_archived=bool(row["is_archived"]),
            last_opened_at=row["last_opened_at"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            deleted_at=row["deleted_at"],
        )

    @staticmethod
    def _chapter_from_row(row: sqlite3.Row) -> Chapter:
        return Chapter(
            chapter_id=row["chapter_id"],
            book_id=row["book_id"],
            title=row["title"],
            chapter_number=row["chapter_number"],
            subtitle=row["subtitle"],
            import_order=row["import_order"],
            sort_order=row["sort_order"],
            chapter_type=ChapterType(row["chapter_type"]),
            reading_direction=ReadingDirection(row["reading_direction"]),
            notes=row["notes"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            deleted_at=row["deleted_at"],
        )

    @staticmethod
    def _page_from_row(row: sqlite3.Row) -> Page | None:
        """A page without full import provenance is a v1 placeholder, not a
        Page — the mapper refuses to fabricate hash/copy/dimensions."""
        if row["source_hash"] is None or row["managed_original_ref"] is None:
            return None
        if row["width"] is None or row["height"] is None:
            return None
        return Page(
            page_id=row["page_id"],
            chapter_id=row["chapter_id"],
            source_filename=row["source_filename"] or "",
            source_order=row["source_order"],
            sort_order=row["sort_order"],
            source_hash=row["source_hash"],
            source_size_bytes=row["source_size_bytes"],
            width=row["width"],
            height=row["height"],
            managed_original_ref=row["managed_original_ref"],
            page_locked=bool(row["page_locked"]),
            review_state=row["review_state"] or "unreviewed",
            overall_status=row["overall_status"] or "not_started",
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            deleted_at=row["deleted_at"],
        )

    # ------------------------------------------------------------------
    # books
    # ------------------------------------------------------------------

    _BOOK_COLUMNS = (
        "book_id, title, original_title, author, publisher, series_title, description,"
        " source_language, target_language, source_url, notes, default_chapter_type,"
        " default_reading_direction, is_favorite, is_archived, last_opened_at,"
        " created_at, updated_at, deleted_at"
    )

    def add_book(self, book: Book) -> None:
        with self._conn:
            self._conn.execute(
                "INSERT INTO books (" + self._BOOK_COLUMNS + ")"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    book.book_id, book.title, book.original_title, book.author,
                    book.publisher, book.series_title, book.description,
                    book.source_language, book.target_language, book.source_url,
                    book.notes, book.default_chapter_type.value,
                    book.default_reading_direction.value, int(book.is_favorite),
                    int(book.is_archived), book.last_opened_at,
                    book.created_at, book.updated_at, book.deleted_at,
                ),
            )

    def get_book(self, book_id: str) -> Book | None:
        row = self._conn.execute(
            "SELECT " + self._BOOK_COLUMNS + " FROM books WHERE book_id = ?",
            (book_id,),
        ).fetchone()
        return self._book_from_row(row) if row else None

    def list_books(self) -> list[Book]:
        rows = self._conn.execute(
            "SELECT " + self._BOOK_COLUMNS + " FROM books"
        ).fetchall()
        return [self._book_from_row(row) for row in rows]

    def update_book(self, book: Book) -> None:
        with self._conn:
            self._conn.execute(
                "UPDATE books SET title = ?, original_title = ?, author = ?,"
                " publisher = ?, series_title = ?, description = ?,"
                " source_language = ?, target_language = ?, source_url = ?,"
                " notes = ?, default_chapter_type = ?, default_reading_direction = ?,"
                " is_favorite = ?, is_archived = ?, last_opened_at = ?,"
                " updated_at = ?, deleted_at = ? WHERE book_id = ?",
                (
                    book.title, book.original_title, book.author, book.publisher,
                    book.series_title, book.description, book.source_language,
                    book.target_language, book.source_url, book.notes,
                    book.default_chapter_type.value, book.default_reading_direction.value,
                    int(book.is_favorite), int(book.is_archived), book.last_opened_at,
                    book.updated_at, book.deleted_at, book.book_id,
                ),
            )

    # ------------------------------------------------------------------
    # chapters
    # ------------------------------------------------------------------

    _CHAPTER_COLUMNS = (
        "chapter_id, book_id, title, chapter_number, subtitle, import_order,"
        " sort_order, chapter_type, reading_direction, notes, created_at,"
        " updated_at, deleted_at"
    )

    def add_chapter(self, chapter: Chapter) -> None:
        with self._conn:
            self._conn.execute(
                "INSERT INTO chapters (" + self._CHAPTER_COLUMNS + ")"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    chapter.chapter_id, chapter.book_id, chapter.title,
                    chapter.chapter_number, chapter.subtitle, chapter.import_order,
                    chapter.sort_order, chapter.chapter_type.value,
                    chapter.reading_direction.value, chapter.notes,
                    chapter.created_at, chapter.updated_at, chapter.deleted_at,
                ),
            )

    def get_chapter(self, chapter_id: str) -> Chapter | None:
        row = self._conn.execute(
            "SELECT " + self._CHAPTER_COLUMNS + " FROM chapters WHERE chapter_id = ?",
            (chapter_id,),
        ).fetchone()
        return self._chapter_from_row(row) if row else None

    def list_chapters(self, book_id: str) -> list[Chapter]:
        rows = self._conn.execute(
            "SELECT " + self._CHAPTER_COLUMNS + " FROM chapters WHERE book_id = ?"
            " ORDER BY sort_order",
            (book_id,),
        ).fetchall()
        return [self._chapter_from_row(row) for row in rows]

    def update_chapter(self, chapter: Chapter) -> None:
        with self._conn:
            self._conn.execute(
                "UPDATE chapters SET title = ?, chapter_number = ?, subtitle = ?,"
                " import_order = ?, sort_order = ?, chapter_type = ?,"
                " reading_direction = ?, notes = ?, updated_at = ?, deleted_at = ?"
                " WHERE chapter_id = ?",
                (
                    chapter.title, chapter.chapter_number, chapter.subtitle,
                    chapter.import_order, chapter.sort_order,
                    chapter.chapter_type.value, chapter.reading_direction.value,
                    chapter.notes, chapter.updated_at, chapter.deleted_at,
                    chapter.chapter_id,
                ),
            )

    # ------------------------------------------------------------------
    # tags (delete = tag + links in ONE transaction; books untouched)
    # ------------------------------------------------------------------

    _TAG_COLUMNS = "tag_id, name, created_at, updated_at"

    def add_tag(self, tag: Tag) -> None:
        with self._conn:
            self._conn.execute(
                "INSERT INTO tags (" + self._TAG_COLUMNS + ") VALUES (?, ?, ?, ?)",
                (tag.tag_id, tag.name, tag.created_at, tag.updated_at),
            )

    def get_tag(self, tag_id: str) -> Tag | None:
        row = self._conn.execute(
            "SELECT " + self._TAG_COLUMNS + " FROM tags WHERE tag_id = ?", (tag_id,)
        ).fetchone()
        return Tag(**dict(row)) if row else None

    def find_tag_by_name(self, name: str) -> Tag | None:
        row = self._conn.execute(
            "SELECT " + self._TAG_COLUMNS + " FROM tags WHERE name = ?", (name,)
        ).fetchone()
        return Tag(**dict(row)) if row else None

    def list_tags(self) -> list[Tag]:
        rows = self._conn.execute(
            "SELECT " + self._TAG_COLUMNS + " FROM tags ORDER BY name"
        ).fetchall()
        return [Tag(**dict(row)) for row in rows]

    def update_tag(self, tag: Tag) -> None:
        with self._conn:
            self._conn.execute(
                "UPDATE tags SET name = ?, updated_at = ? WHERE tag_id = ?",
                (tag.name, tag.updated_at, tag.tag_id),
            )

    def delete_tag(self, tag_id: str) -> None:
        with self._conn:
            self._conn.execute(
                "DELETE FROM book_tags WHERE tag_id = ?", (tag_id,)
            )
            self._conn.execute("DELETE FROM tags WHERE tag_id = ?", (tag_id,))

    def add_book_tag(self, book_id: str, tag_id: str) -> None:
        with self._conn:
            self._conn.execute(
                "INSERT INTO book_tags (book_id, tag_id) VALUES (?, ?)"
                " ON CONFLICT (book_id, tag_id) DO NOTHING",
                (book_id, tag_id),
            )

    def remove_book_tag(self, book_id: str, tag_id: str) -> None:
        with self._conn:
            self._conn.execute(
                "DELETE FROM book_tags WHERE book_id = ? AND tag_id = ?",
                (book_id, tag_id),
            )

    def list_tags_of_book(self, book_id: str) -> list[Tag]:
        rows = self._conn.execute(
            "SELECT t.tag_id, t.name, t.created_at, t.updated_at"
            " FROM tags t JOIN book_tags bt ON bt.tag_id = t.tag_id"
            " WHERE bt.book_id = ? ORDER BY t.name",
            (book_id,),
        ).fetchall()
        return [Tag(**dict(row)) for row in rows]

    # ------------------------------------------------------------------
    # pages: ImportPageSink (dedup / order / insert) + PageRepository
    # ------------------------------------------------------------------

    _PAGE_COLUMNS = (
        "page_id, chapter_id, source_filename, source_order, sort_order,"
        " source_hash, source_size_bytes, width, height, managed_original_ref,"
        " page_locked, review_state, overall_status, created_at, updated_at,"
        " deleted_at"
    )

    _COMPLETE_PAGE_WHERE = (
        "source_hash IS NOT NULL AND managed_original_ref IS NOT NULL"
        " AND width IS NOT NULL AND height IS NOT NULL"
    )

    def existing_source_hashes(self, chapter_id: str) -> set[str]:
        rows = self._conn.execute(
            "SELECT source_hash FROM pages"
            " WHERE chapter_id = ? AND " + self._COMPLETE_PAGE_WHERE,
            (chapter_id,),
        ).fetchall()
        return {row["source_hash"] for row in rows}

    def max_source_order(self, chapter_id: str) -> int:
        row = self._conn.execute(
            "SELECT MAX(source_order) AS max_order FROM pages"
            " WHERE chapter_id = ? AND " + self._COMPLETE_PAGE_WHERE,
            (chapter_id,),
        ).fetchone()
        return int(row["max_order"]) if row and row["max_order"] is not None else 0

    def add_page(self, page: Page) -> None:
        with self._conn:
            self._conn.execute(
                "INSERT INTO pages (" + self._PAGE_COLUMNS + ")"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    page.page_id, page.chapter_id, page.source_filename,
                    page.source_order, page.sort_order, page.source_hash,
                    page.source_size_bytes, page.width, page.height,
                    page.managed_original_ref, int(page.page_locked),
                    page.review_state, page.overall_status,
                    page.created_at, page.updated_at, page.deleted_at,
                ),
            )

    def get_page(self, page_id: str) -> Page | None:
        row = self._conn.execute(
            "SELECT " + self._PAGE_COLUMNS + " FROM pages"
            " WHERE page_id = ? AND " + self._COMPLETE_PAGE_WHERE,
            (page_id,),
        ).fetchone()
        return self._page_from_row(row) if row else None

    def list_pages(self, chapter_id: str) -> list[Page]:
        rows = self._conn.execute(
            "SELECT " + self._PAGE_COLUMNS + " FROM pages"
            " WHERE chapter_id = ? AND deleted_at IS NULL AND "
            + self._COMPLETE_PAGE_WHERE +
            " ORDER BY sort_order",
            (chapter_id,),
        ).fetchall()
        pages = []
        for row in rows:
            page = self._page_from_row(row)
            if page is not None:
                pages.append(page)
        return pages

    def update_page(self, page: Page) -> None:
        with self._conn:
            self._conn.execute(
                "UPDATE pages SET source_filename = ?, source_order = ?,"
                " sort_order = ?, source_hash = ?, source_size_bytes = ?,"
                " width = ?, height = ?, managed_original_ref = ?,"
                " page_locked = ?, review_state = ?, overall_status = ?,"
                " updated_at = ?, deleted_at = ? WHERE page_id = ?",
                (
                    page.source_filename, page.source_order, page.sort_order,
                    page.source_hash, page.source_size_bytes, page.width,
                    page.height, page.managed_original_ref,
                    int(page.page_locked), page.review_state,
                    page.overall_status, page.updated_at, page.deleted_at,
                    page.page_id,
                ),
            )

    def soft_delete_page(self, page_id: str) -> None:
        with self._conn:
            self._conn.execute(
                "UPDATE pages SET deleted_at = ? WHERE page_id = ?",
                (_soft_delete_timestamp(), page_id),
            )


def _soft_delete_timestamp() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")
