"""SQLite adapter for the library, page-import and page-round-trip
contracts (TASK-029, per the frozen TASK-028 design §2.1/§3).

Implements ``LibraryRepository`` + ``ImportPageSink`` + ``PageRepository``
structurally over the shared connection. Book/Chapter/Tag live in the v1
tables completed by v2; pages tolerate v1 structural placeholder rows
(import columns NULL) — such rows are never surfaced as Page objects and
import reads (dedup/next order) only consider fully imported rows.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import sqlite3
import stat
import uuid
from collections.abc import Sequence
from typing import Any
from datetime import datetime, timezone

from domain.books.entities import Book, Chapter, ChapterType, ReadingDirection, Tag
from domain.pages.entities import Page, PageView
from infrastructure.filesystem.managed_storage import _is_reparse_point, _sanitize_component
from infrastructure.filesystem.win_unlink import unlink_by_handle

#: FEA-09/C-15 v7 page column list (order matches ``_PAGE_COLUMNS`` and
#: ``add_page``/``update_page`` parameter packing).
_PAGE_COLUMN_LIST = (
    "page_id", "chapter_id", "source_filename", "source_order", "sort_order",
    "source_hash", "source_size_bytes", "width", "height", "managed_original_ref",
    "page_locked", "review_state", "overall_status", "created_at", "updated_at",
    "deleted_at", "source_mode", "integrity_status",
)


class SourceProjectMismatch(RuntimeError):
    """FEA-09/C-15 §2 book-ownership guard: page→chapter→book does not match
    the binding's ``project_id``; the commit transaction rolls back and the
    wire layer maps this to ``SOURCE_PROJECT_MISMATCH``."""


class PermanentDeleteBlockedError(RuntimeError):
    """FEA-12: typed refusal raised *inside* the permanent-delete transaction.

    The transaction has already been rolled back when this escapes, so the
    caller can project the code (``BOOK_BUSY``) with zero side effects.  It is
    raised for the state checks that must be re-read at the write boundary
    (D1 X1 non-terminal source operation; recovery of the transaction is the
    ``with`` block's job).  ``book_id`` lets the batch projection attribute the
    code to the exact item that changed between preflight and the transaction
    (r1 R-009).
    """

    def __init__(self, code: str, *, book_id: str | None = None) -> None:
        super().__init__(code)
        self.code = code
        self.book_id = book_id


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
        Page — the mapper refuses to fabricate hash/copy/dimensions.

        FEA-09/C-15 §3.1: referenced pages have no managed_original_ref;
        their completeness is the binding (P8), so the mapper only demands
        hash + dimensions in that mode."""
        source_mode = row["source_mode"] if "source_mode" in row.keys() else "managed"
        if row["source_hash"] is None:
            return None
        if row["width"] is None or row["height"] is None:
            return None
        if source_mode == "managed" and row["managed_original_ref"] is None:
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
            source_mode=source_mode,
            integrity_status=(
                row["integrity_status"] if "integrity_status" in row.keys() else "complete"
            ),
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
        " deleted_at, source_mode, integrity_status"
    )

    _COMPLETE_PAGE_WHERE = (
        "source_hash IS NOT NULL AND managed_original_ref IS NOT NULL"
        " AND width IS NOT NULL AND height IS NOT NULL"
    )

    #: FEA-09 / C-15 §4.1 ``is_complete_page`` — data completeness, ignoring
    #: deleted_at/time/resources. managed branch keeps the legacy column
    #: predicate (v7 backfill marks exactly that set complete); the
    #: referenced branch additionally requires a healthy binding whose
    #: verified_digest matches the bound entry (P7 ∧ P8).
    _IS_COMPLETE_PAGE_WHERE = (
        "((pages.source_mode = 'managed' AND pages.integrity_status = 'complete'"
        " AND pages.source_hash IS NOT NULL AND pages.managed_original_ref IS NOT NULL"
        " AND pages.width IS NOT NULL AND pages.height IS NOT NULL)"
        " OR (pages.source_mode = 'referenced' AND pages.integrity_status = 'complete'"
        " AND pages.source_hash IS NOT NULL AND pages.width IS NOT NULL"
        " AND pages.height IS NOT NULL"
        " AND EXISTS (SELECT 1 FROM page_bindings b JOIN source_entries e"
        "  ON (e.source_id, e.version_id, e.entry_id) ="
        "     (b.source_id, b.accepted_source_version, b.entry_id)"
        "  WHERE b.page_id = pages.page_id AND b.status = 'healthy'"
        "    AND b.verified_digest = e.content_digest)))"
    )

    #: FEA-09 / C-05 v1.2 ``V(p,t)`` visibility predicate (mode dispatch).
    #: managed = artifact witness OR copy-original witness; referenced = P7 ∧ P8
    #: (P1/P5 are added by the caller's JOIN/WHERE on parents and time).
    #: The moment is embedded as a validated SQL literal so callers keep their
    #: existing parameter tuples (and validators can pin one instant).
    _VISIBLE_TYPES_SQL = (
        "'original','thumbnail','clean','translated','render_preview','export'"
    )

    @staticmethod
    def _sql_timestamp(moment: str | None) -> str:
        from datetime import datetime, timezone

        if moment is None:
            moment = datetime.now(timezone.utc).isoformat(timespec="milliseconds")
        try:
            datetime.fromisoformat(moment.replace("Z", "+00:00"))
        except ValueError as error:  # pragma: no cover - internal input
            raise ValueError(f"invalid visibility moment: {moment!r}") from error
        return "'" + moment.replace("'", "''") + "'"

    @classmethod
    def _artifact_witness_sql(cls, timestamp: str) -> str:
        return (
            "EXISTS (SELECT 1 FROM media_artifacts a"
            " JOIN artifact_revisions r"
            " ON r.artifact_revision_id = a.current_revision_id"
            " WHERE a.page_id = pages.page_id"
            " AND a.artifact_type IN (" + cls._VISIBLE_TYPES_SQL + ")"
            " AND r.integrity_status = 'valid'"
            " AND r.created_at <= " + timestamp + ")"
        )

    @classmethod
    def _copy_witness_sql(cls, timestamp: str) -> str:
        return (
            "(pages.source_mode = 'managed'"
            " AND pages.integrity_status = 'complete'"
            " AND pages.source_hash IS NOT NULL"
            " AND pages.managed_original_ref IS NOT NULL"
            " AND pages.width > 0 AND pages.height > 0"
            " AND pages.created_at <= " + timestamp + ")"
        )

    @classmethod
    def _visible_page_where(cls, timestamp: str) -> str:
        return (
            "((pages.source_mode = 'managed' AND ("
            + cls._artifact_witness_sql(timestamp)
            + " OR " + cls._copy_witness_sql(timestamp)
            + ")) OR (pages.source_mode = 'referenced'"
            " AND pages.integrity_status = 'complete'"
            " AND pages.source_hash IS NOT NULL"
            " AND pages.width IS NOT NULL AND pages.width > 0"
            " AND pages.height IS NOT NULL AND pages.height > 0"
            " AND pages.created_at <= " + timestamp +
            " AND EXISTS (SELECT 1 FROM page_bindings b JOIN source_entries e"
            "  ON (e.source_id, e.version_id, e.entry_id) ="
            "     (b.source_id, b.accepted_source_version, b.entry_id)"
            "  WHERE b.page_id = pages.page_id AND b.status = 'healthy'"
            "    AND b.verified_digest = e.content_digest)))"
        )

    @classmethod
    def _artifact_original_select(cls, timestamp: str) -> str:
        base = (
            "SELECT r.{column} FROM media_artifacts a"
            " JOIN artifact_revisions r"
            " ON r.artifact_revision_id = a.current_revision_id"
            " WHERE a.page_id = pages.page_id"
            " AND a.artifact_type = 'original'"
            " AND r.integrity_status = 'valid'"
            " AND r.created_at <= " + timestamp +
            " ORDER BY r.created_at DESC LIMIT 1)"
        )
        return (
            ", (" + base.format(column="file_hash") + " AS artifact_file_hash"
            ", (" + base.format(column="managed_path") + " AS artifact_managed_path"
            ", (" + base.format(column="width") + " AS artifact_width"
            ", (" + base.format(column="height") + " AS artifact_height"
            ", (" + base.format(column="size_bytes") + " AS artifact_size_bytes"
            ", (" + cls._artifact_witness_sql(timestamp) + ") AS has_artifact_witness"
            ", (" + cls._copy_witness_sql(timestamp) + ") AS has_copy_witness"
        )

    def existing_source_hashes(self, chapter_id: str) -> set[str]:
        """Hashes of the chapter's **live** complete pages.

        Soft-deleted pages are excluded (F-10, TASK-044): a trashed page used
        to swallow a re-import silently — the file was reported as a duplicate
        while the chapter showed no page. ``max_source_order`` below
        deliberately still counts trashed pages, so a later restore can never
        collide with a page imported in the meantime.

        FEA-09/C-15 §4.2: the predicate is now the mode-dispatched
        ``is_complete_page`` (managed and referenced pages share it); dedup
        policy stays with the import layer, which must not collapse
        occurrences by digest.
        """
        rows = self._conn.execute(
            "SELECT source_hash FROM pages"
            " WHERE chapter_id = ? AND deleted_at IS NULL AND "
            + self._IS_COMPLETE_PAGE_WHERE,
            (chapter_id,),
        ).fetchall()
        return {row["source_hash"] for row in rows}

    def max_source_order(self, chapter_id: str) -> int:
        """Highest ``source_order`` in the chapter, trashed pages included.

        Keeping soft-deleted rows in the maximum is intentional: their order
        slots are reserved until the batch is restored or purged, so appending
        a new import after them cannot hand two pages the same order.

        FEA-09/C-15 §4.2: uses ``is_complete_page`` (soft-deleted pages
        included on purpose — this is not the live-only predicate).
        """
        row = self._conn.execute(
            "SELECT MAX(source_order) AS max_order FROM pages"
            " WHERE chapter_id = ? AND " + self._IS_COMPLETE_PAGE_WHERE,
            (chapter_id,),
        ).fetchone()
        return int(row["max_order"]) if row and row["max_order"] is not None else 0

    def add_page(self, page: Page) -> None:
        with self._conn:
            self._conn.execute(
                "INSERT INTO pages (" + self._PAGE_COLUMNS + ")"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    page.page_id, page.chapter_id, page.source_filename,
                    page.source_order, page.sort_order, page.source_hash,
                    page.source_size_bytes, page.width, page.height,
                    page.managed_original_ref, int(page.page_locked),
                    page.review_state, page.overall_status,
                    page.created_at, page.updated_at, page.deleted_at,
                    page.source_mode, page.integrity_status,
                ),
            )

    def get_page(self, page_id: str, *, at: str | None = None) -> Page | PageView | None:
        # Soft-deleted pages are hidden here too, consistent with
        # list_pages (AC-IMPORT semantics; recycle-bin/restore views are a
        # later slice with their own queries).
        # FEA-09/C-15 v1.1 §4.2: V(p,t) — parent deletion is checked through
        # the chapter/book JOIN (C-05 v1.2 P1 covers all three levels).
        timestamp = self._sql_timestamp(at)
        row = self._conn.execute(
            "SELECT " + self._page_columns_aliased(timestamp) + " FROM pages"
            " JOIN chapters c ON c.chapter_id = pages.chapter_id"
            " JOIN books b ON b.book_id = c.book_id"
            " WHERE pages.page_id = ? AND pages.deleted_at IS NULL"
            " AND c.deleted_at IS NULL AND b.deleted_at IS NULL AND "
            + self._visible_page_where(timestamp),
            (page_id,),
        ).fetchone()
        return self._page_or_view_from_row(row) if row else None

    def list_pages(self, chapter_id: str, *, at: str | None = None) -> list[Page | PageView]:
        # FEA-09/C-15 v1.1 §4.2: V(p,t) with parent-deletion visibility (P1);
        # every V row is observable (Page when constructible, else PageView).
        timestamp = self._sql_timestamp(at)
        rows = self._conn.execute(
            "SELECT " + self._page_columns_aliased(timestamp) + " FROM pages"
            " JOIN chapters c ON c.chapter_id = pages.chapter_id"
            " JOIN books b ON b.book_id = c.book_id"
            " WHERE pages.chapter_id = ? AND pages.deleted_at IS NULL"
            " AND c.deleted_at IS NULL AND b.deleted_at IS NULL AND "
            + self._visible_page_where(timestamp) +
            " ORDER BY pages.sort_order, pages.page_id",
            (chapter_id,),
        ).fetchall()
        pages: list[Page | PageView] = []
        for row in rows:
            page = self._page_or_view_from_row(row)
            if page is not None:
                pages.append(page)
        return pages

    def list_page_views(self, chapter_id: str, *, at: str | None = None) -> list[PageView]:
        """C-15 v1.1 §4.4 pure projection: every V row as a read-only view.

        Used by migration validation / reader pure projection; never publishes
        or resolves resources and does not open another connection.
        """
        timestamp = self._sql_timestamp(at)
        rows = self._conn.execute(
            "SELECT " + self._page_columns_aliased(timestamp) + " FROM pages"
            " JOIN chapters c ON c.chapter_id = pages.chapter_id"
            " JOIN books b ON b.book_id = c.book_id"
            " WHERE pages.chapter_id = ? AND pages.deleted_at IS NULL"
            " AND c.deleted_at IS NULL AND b.deleted_at IS NULL AND "
            + self._visible_page_where(timestamp) +
            " ORDER BY pages.sort_order, pages.page_id",
            (chapter_id,),
        ).fetchall()
        return [self._page_view_from_row(row) for row in rows]

    def get_visible_original_path(self, page_id: str, *, at: str | None = None) -> str | None:
        """Selected managed original for R: eligible original revision, else
        ``pages.managed_original_ref`` (C-15 v1.1 §4.2); None when the row is
        not V or has no resolvable path."""
        timestamp = self._sql_timestamp(at)
        row = self._conn.execute(
            "SELECT pages.managed_original_ref AS page_ref,"
            " (SELECT r.managed_path FROM media_artifacts a"
            "  JOIN artifact_revisions r ON r.artifact_revision_id = a.current_revision_id"
            "  WHERE a.page_id = pages.page_id AND a.artifact_type = 'original'"
            "  AND r.integrity_status = 'valid'"
            "  AND r.created_at <= " + timestamp +
            "  ORDER BY r.created_at DESC LIMIT 1) AS artifact_path"
            " FROM pages JOIN chapters c ON c.chapter_id = pages.chapter_id"
            " JOIN books b ON b.book_id = c.book_id"
            " WHERE pages.page_id = ? AND pages.deleted_at IS NULL"
            " AND c.deleted_at IS NULL AND b.deleted_at IS NULL AND "
            + self._visible_page_where(timestamp),
            (page_id,),
        ).fetchone()
        if row is None:
            return None
        return row["artifact_path"] or row["page_ref"]

    def update_page(self, page: Page) -> None:
        # FEA-09/C-15 §4.3: update_page never flips integrity_status —
        # only an explicit validated transition may do that.
        with self._conn:
            self._conn.execute(
                "UPDATE pages SET source_filename = ?, source_order = ?,"
                " sort_order = ?, source_hash = ?, source_size_bytes = ?,"
                " width = ?, height = ?, managed_original_ref = ?,"
                " page_locked = ?, review_state = ?, overall_status = ?,"
                " updated_at = ?, deleted_at = ?,"
                " source_mode = ?, integrity_status = ? WHERE page_id = ?",
                (
                    page.source_filename, page.source_order, page.sort_order,
                    page.source_hash, page.source_size_bytes, page.width,
                    page.height, page.managed_original_ref,
                    int(page.page_locked), page.review_state,
                    page.overall_status, page.updated_at, page.deleted_at,
                    page.source_mode, page.integrity_status,
                    page.page_id,
                ),
            )

    def _page_columns_aliased(self, timestamp: str) -> str:
        return (
            ", ".join("pages." + col.strip() for col in _PAGE_COLUMN_LIST)
            + self._artifact_original_select(timestamp)
        )

    def _page_view_from_row(self, row: sqlite3.Row) -> PageView:
        mode = row["source_mode"] if "source_mode" in row.keys() else "managed"
        artifact_hash = row["artifact_file_hash"]
        page_ref = row["managed_original_ref"]
        artifact_ref = row["artifact_managed_path"]
        width = row["width"] if row["width"] and row["width"] > 0 else row["artifact_width"]
        height = row["height"] if row["height"] and row["height"] > 0 else row["artifact_height"]
        has_artifact = bool(row["has_artifact_witness"])
        has_copy = bool(row["has_copy_witness"])
        witness = (
            "artifact+copy" if has_artifact and has_copy else
            "artifact" if has_artifact else
            "copy" if has_copy else "referenced"
        )
        ref = artifact_ref or page_ref
        return PageView(
            page_id=row["page_id"],
            chapter_id=row["chapter_id"],
            source_mode=mode,
            sort_order=int(row["sort_order"] or 0),
            visibility_witness=witness,
            original_available=bool(ref),
            integrity_status=row["integrity_status"] or "incomplete",
            source_filename=row["source_filename"],
            source_order=row["source_order"],
            created_at=row["created_at"],
            # Never use a non-original artifact hash as the source hash.
            source_hash=row["source_hash"] or artifact_hash,
            source_size_bytes=row["source_size_bytes"] or row["artifact_size_bytes"],
            managed_original_ref=ref,
            width=int(width) if width else None,
            height=int(height) if height else None,
            artifact_revision_id=None,
        )

    def _page_or_view_from_row(self, row: sqlite3.Row) -> Page | PageView | None:
        """C-15 v1.1 §4.4: full Page when constructible, else read-only view."""
        mode = row["source_mode"] if "source_mode" in row.keys() else "managed"
        if mode == "referenced":
            page = self._page_from_row(row)
            return page if page is not None else self._page_view_from_row(row)
        artifact_hash = row["artifact_file_hash"]
        page_ref = row["managed_original_ref"]
        artifact_ref = row["artifact_managed_path"]
        width = row["width"] if row["width"] and row["width"] > 0 else row["artifact_width"]
        height = row["height"] if row["height"] and row["height"] > 0 else row["artifact_height"]
        source_hash = row["source_hash"] or artifact_hash
        ref = page_ref or artifact_ref
        if source_hash and ref and width and height and width > 0 and height > 0:
            return Page(
                page_id=row["page_id"],
                chapter_id=row["chapter_id"],
                source_filename=row["source_filename"] or "",
                source_order=row["source_order"],
                sort_order=row["sort_order"],
                source_hash=source_hash,
                source_size_bytes=row["source_size_bytes"] or row["artifact_size_bytes"] or 0,
                width=int(width),
                height=int(height),
                managed_original_ref=ref,
                page_locked=bool(row["page_locked"]),
                review_state=row["review_state"] or "unreviewed",
                overall_status=row["overall_status"] or "not_started",
                created_at=row["created_at"],
                updated_at=row["updated_at"],
                deleted_at=row["deleted_at"],
                source_mode=mode,
                integrity_status=row["integrity_status"] or "incomplete",
            )
        return self._page_view_from_row(row)

    def soft_delete_page(self, page_id: str) -> None:
        with self._conn:
            self._conn.execute(
                "UPDATE pages SET deleted_at = ? WHERE page_id = ?",
                (_soft_delete_timestamp(), page_id),
            )

    # ------------------------------------------------------------------
    # TASK-021 trash subset: batch soft delete / restore / purge
    # ------------------------------------------------------------------

    def get_pages_by_ids(self, page_ids: Sequence[str]) -> list[Page]:
        """Fetch pages by id **including soft-deleted ones** (trash views and
        restore paths must see what the reader hides)."""
        ids = list(page_ids)
        if not ids:
            return []
        placeholders = ",".join("?" for _ in ids)
        rows = self._conn.execute(
            f"SELECT * FROM pages WHERE page_id IN ({placeholders})",
            tuple(ids),
        ).fetchall()
        pages = []
        for row in rows:
            page = self._page_from_row(row)
            if page is not None:
                pages.append(page)
        return pages

    def soft_delete_pages(self, page_ids: Sequence[str], deleted_at: str) -> int:
        """Soft-delete the given pages with **one shared timestamp** (same
        batch ⇒ same ``deleted_at`` value). Already-deleted pages are left
        untouched. Returns the number of rows actually soft-deleted."""
        ids = list(page_ids)
        if not ids:
            return 0
        placeholders = ",".join("?" for _ in ids)
        with self._conn:
            cursor = self._conn.execute(
                "UPDATE pages SET deleted_at = ?, updated_at = ?"
                f" WHERE page_id IN ({placeholders}) AND deleted_at IS NULL",
                (deleted_at, deleted_at, *ids),
            )
            return cursor.rowcount

    def restore_pages(self, page_ids: Sequence[str]) -> int:
        """Clear ``deleted_at`` on the given pages; already-live pages are
        untouched. Returns the number of rows actually restored."""
        ids = list(page_ids)
        if not ids:
            return 0
        placeholders = ",".join("?" for _ in ids)
        with self._conn:
            cursor = self._conn.execute(
                "UPDATE pages SET deleted_at = NULL, updated_at = ?"
                f" WHERE page_id IN ({placeholders}) AND deleted_at IS NOT NULL",
                (_soft_delete_timestamp(), *ids),
            )
            return cursor.rowcount

    def list_generated_asset_paths(self, page_ids: Sequence[str]) -> list[str]:
        """Managed paths of every generated artifact revision of these pages.

        Permanent deletion covers the generated assets as well as the managed
        original (F-6, TASK-044; D04 §permanent-delete). Paths are returned
        verbatim: the caller's remover is what refuses anything outside the
        managed root, so a corrupt row can never escalate into a file write.
        """
        ids = list(page_ids)
        if not ids:
            return []
        placeholders = ",".join("?" for _ in ids)
        rows = self._conn.execute(
            "SELECT ar.managed_path FROM artifact_revisions ar"
            " JOIN media_artifacts ma ON ma.artifact_id = ar.artifact_id"
            f" WHERE ma.page_id IN ({placeholders})"
            " ORDER BY ma.artifact_id, ar.revision_no",
            tuple(ids),
        ).fetchall()
        return [row["managed_path"] for row in rows]

    def list_live_managed_refs(self, refs) -> set[str]:
        """TASK-060 Q-007 ③: which refs a live (non-purged) page row still
        references as its managed original."""
        refs = [r for r in refs if r]
        if not refs:
            return set()
        placeholders = ",".join("?" for _ in refs)
        rows = self._conn.execute(
            # a soft-deleted row still EXISTS (restorable) — only a purged
            # row (gone) releases its file for sweeping (Q-007 ③)
            "SELECT managed_original_ref FROM pages"
            f" WHERE managed_original_ref IN ({placeholders})",
            tuple(refs),
        ).fetchall()
        return {row["managed_original_ref"] for row in rows}

    def list_trashed_page_groups(self) -> list[tuple[str, str, tuple[str, ...]]]:
        """``(chapter_id, deleted_at, page_ids)`` for each soft-deleted group.

        One soft-delete batch shares a single ``deleted_at`` value, so the
        batch list is derivable from the store; the JSON ledger is an index
        that can be rebuilt (F-7, TASK-044).
        """
        rows = self._conn.execute(
            "SELECT chapter_id, deleted_at, page_id FROM pages"
            " WHERE deleted_at IS NOT NULL"
            " ORDER BY deleted_at, chapter_id, sort_order, page_id"
        ).fetchall()
        groups: dict[tuple[str, str], list[str]] = {}
        for row in rows:
            groups.setdefault((row["chapter_id"], row["deleted_at"]), []).append(
                row["page_id"]
            )
        return [
            (chapter_id, deleted_at, tuple(page_ids))
            for (chapter_id, deleted_at), page_ids in groups.items()
        ]

    def purge_pages(self, page_ids: Sequence[str]) -> None:
        """Hard-delete page rows **and every row that references them**.

        Controlled data only: callers remove the managed files separately (see
        ``application.maintenance``); user source files live outside the
        managed root and are never addressed here.

        The statement order is the reverse of the real foreign-key graph,
        re-derived with ``PRAGMA foreign_key_list`` (six tables / seven
        foreign keys point at ``pages``, all ``NO ACTION``; F-2, TASK-044):

        1. provenance pointers that would dangle are cleared first —
           ``artifact_revisions.source_artifact_revision_id`` is an *immediate*
           self-reference, and a revision belonging to another page may derive
           from a revision being purged;
        2. pipeline rows, children before parents (``step_runs`` cascades its
           input/output refs), plus the non-FK ``pipeline_stage_states`` rows;
        3. artifact revisions *before* the artifacts that own them;
        4. region revisions, then regions, then the pages.

        ``media_artifacts.current_revision_id`` is deliberately left set: the
        schema's ``trg_media_artifacts_current_not_clearable`` aborts any
        attempt to clear an established pointer, and the composite foreign key
        is ``DEFERRABLE INITIALLY DEFERRED``, so deleting both sides inside
        this one transaction is what keeps it satisfied.

        Everything runs in a single transaction, so a failure leaves the
        database exactly as it was. Foreign-key enforcement is never disabled
        and ``IntegrityError`` is never swallowed.
        """
        ids = list(page_ids)
        if not ids:
            return
        placeholders = ",".join("?" for _ in ids)
        params = tuple(ids)
        page_artifacts = (
            "SELECT artifact_id FROM media_artifacts"
            f" WHERE page_id IN ({placeholders})"
        )
        purged_revisions = (
            "SELECT artifact_revision_id FROM artifact_revisions"
            f" WHERE artifact_id IN ({page_artifacts})"
        )
        page_regions = (
            f"SELECT region_id FROM regions WHERE page_id IN ({placeholders})"
        )
        # FEA-12 / D1 X1: the C-17 v8 subgraph that references the purged
        # pages/regions/revisions.  The page-level purge predates C-17, so
        # without this the first page that carries a v7 binding or v8 lineage
        # row would fail the FK check and roll the purge back.  Rows are
        # deleted child-first (publications → lineage → bindings), matching
        # the book-level path and the no-CASCADE declaration in C-17 §2.
        page_bindings = (
            "SELECT b.binding_id FROM page_bindings b"
            f" WHERE b.page_id IN ({placeholders})"
        )
        page_region_revisions = (
            "SELECT rr.region_revision_id FROM region_revisions rr"
            f" WHERE rr.region_id IN ({page_regions})"
        )
        with self._conn:
            self._conn.execute(
                "UPDATE artifact_revisions SET source_artifact_revision_id = NULL"
                f" WHERE source_artifact_revision_id IN ({purged_revisions})",
                params,
            )
            self._conn.execute(
                "DELETE FROM source_binding_publications"
                f" WHERE binding_id IN ({page_bindings})",
                params,
            )
            self._conn.execute(
                "DELETE FROM source_revision_lineage"
                f" WHERE revision_id IN ({page_region_revisions})"
                f" OR region_id IN ({page_regions})"
                f" OR binding_id IN ({page_bindings})",
                params * 3,
            )
            self._conn.execute(
                f"DELETE FROM page_bindings WHERE page_id IN ({placeholders})",
                params,
            )
            self._conn.execute(
                f"DELETE FROM step_result_candidates WHERE page_id IN ({placeholders})",
                params,
            )
            self._conn.execute(
                f"DELETE FROM step_runs WHERE page_id IN ({placeholders})", params
            )
            self._conn.execute(
                f"DELETE FROM pipeline_tasks WHERE page_id IN ({placeholders})", params
            )
            self._conn.execute(
                f"DELETE FROM pipeline_run_targets WHERE page_id IN ({placeholders})",
                params,
            )
            self._conn.execute(
                "DELETE FROM artifact_revisions"
                f" WHERE artifact_id IN ({page_artifacts})",
                params,
            )
            self._conn.execute(
                f"DELETE FROM media_artifacts WHERE page_id IN ({placeholders})",
                params,
            )
            self._conn.execute(
                "DELETE FROM region_revisions"
                f" WHERE region_id IN ({page_regions})",
                params,
            )
            self._conn.execute(
                "DELETE FROM pipeline_stage_states"
                f" WHERE target_type = 'page' AND target_id IN ({placeholders})",
                params,
            )
            self._conn.execute(
                "DELETE FROM pipeline_stage_states"
                " WHERE target_type = 'region'"
                f" AND target_id IN ({page_regions})",
                params,
            )
            self._conn.execute(
                f"DELETE FROM regions WHERE page_id IN ({placeholders})", params
            )
            self._conn.execute(
                f"DELETE FROM pages WHERE page_id IN ({placeholders})", params
            )

    # ------------------------------------------------------------------
    # FEA-12 A flow (C-09 SC-B04 / SC-B06): book-level trash
    # ------------------------------------------------------------------
    #
    # Soft delete / restore only ever flip ``books.deleted_at``; every other
    # row (content, protection, current/pinned pointers, progress, source
    # bindings) is untouched by construction (ADJ-001 §3 A).  Both faces are
    # per-item atomic: one statement per entry, so one item's failure or a
    # not-in-trash entry never rolls back the rest of the batch.

    def move_book_to_trash(self, book_id: str) -> bool:
        """Soft-delete one live book; ``False`` when it is missing or already
        trashed (the caller reports it as a per-item skip)."""
        now = datetime.now(timezone.utc).isoformat(timespec="milliseconds")
        cursor = self._conn.execute(
            "UPDATE books SET deleted_at = ?, updated_at = ?"
            " WHERE book_id = ? AND deleted_at IS NULL",
            (now, now, book_id),
        )
        return cursor.rowcount == 1

    def restore_book_from_trash(self, book_id: str) -> bool:
        """Clear ``deleted_at`` only; ``False`` when the entry is not in the
        trash (a per-item conflict, never a batch failure).

        R-007: ``Book.restore`` is the single domain authority for what restore
        means (clear the marker + bump ``updated_at``, touch nothing else);
        this adapter loads the row, applies it, and writes only those two
        columns back under the same ``deleted_at IS NOT NULL`` guard, so the
        per-item atomicity of the batch is preserved.
        """
        with self._conn:
            row = self._conn.execute(
                "SELECT " + self._BOOK_COLUMNS + " FROM books"
                " WHERE book_id = ? AND deleted_at IS NOT NULL",
                (book_id,),
            ).fetchone()
            if row is None:
                return False
            book = self._book_from_row(row)
            book.restore()
            cursor = self._conn.execute(
                "UPDATE books SET deleted_at = ?, updated_at = ?"
                " WHERE book_id = ? AND deleted_at IS NOT NULL",
                (book.deleted_at, book.updated_at, book_id),
            )
            return cursor.rowcount == 1

    def list_trash_entries(
        self, *, after: tuple[str, str] | None, limit: int
    ) -> list[dict[str, Any]]:
        """One page of the recycle bin, newest first (``deleted_at DESC``,
        then ``book_id ASC``).  ``after`` is the opaque ``(deleted_at,
        book_id)`` key of the last item already returned.  Returns at most
        ``limit + 1`` rows so the caller can tell whether a next page exists
        without a second COUNT."""
        sql = (
            "SELECT book_id, title, deleted_at FROM books"
            " WHERE deleted_at IS NOT NULL"
        )
        params: list[Any] = []
        if after is not None:
            after_deleted_at, after_book_id = after
            sql += " AND (deleted_at < ? OR (deleted_at = ? AND book_id > ?))"
            params.extend((after_deleted_at, after_deleted_at, after_book_id))
        sql += " ORDER BY deleted_at DESC, book_id ASC LIMIT ?"
        params.append(int(limit) + 1)
        rows = self._conn.execute(sql, tuple(params)).fetchall()
        return [dict(row) for row in rows]

    # ------------------------------------------------------------------
    # P09-AC3-DELETE-1: Project-level permanent deletion
    # ------------------------------------------------------------------

    def get_cleanup_manifest_data(self, book_id: str) -> dict[str, list[str]] | None:
        row = self._conn.execute(
            "SELECT targets_json FROM book_cleanup_manifests WHERE book_id = ?",
            (book_id,),
        ).fetchone()
        if row is None:
            return None
        try:
            val = json.loads(row["targets_json"])
            if isinstance(val, dict):
                return {
                    "managed_targets": list(val.get("managed_targets", [])),
                    "page_ids": list(val.get("page_ids", [])),
                    "preview_resource_ids": list(val.get("preview_resource_ids", [])),
                    # R2 Finding 3: distinguish "written with no previews" from "written
                    # before this field existed".  The first is a complete answer; the
                    # second is an unknown, and treating an unknown as zero let a legacy
                    # manifest report success, delete itself, and strand its previews.
                    "preview_ids_known": "preview_resource_ids" in val,
                }
            if isinstance(val, list):
                return {
                    "managed_targets": list(val),
                    "page_ids": [],
                    "preview_resource_ids": [],
                    "preview_ids_known": False,   # bare-list legacy format
                }
            return None
        except (json.JSONDecodeError, TypeError):
            return None

    def get_cleanup_manifest(self, book_id: str) -> list[str] | None:
        data = self.get_cleanup_manifest_data(book_id)
        return data.get("managed_targets") if data is not None else None

    def list_book_cleanup_targets(self, book_id: str) -> list[str]:
        targets: list[str] = []
        rows_pages = self._conn.execute(
            "SELECT p.managed_original_ref FROM pages p"
            " JOIN chapters c ON c.chapter_id = p.chapter_id"
            " WHERE c.book_id = ? AND p.managed_original_ref IS NOT NULL AND p.managed_original_ref != ''",
            (book_id,),
        ).fetchall()
        for r in rows_pages:
            ref = r["managed_original_ref"]
            if ref:
                targets.append(ref)
        rows_artifacts = self._conn.execute(
            "SELECT ar.managed_path FROM artifact_revisions ar"
            " JOIN media_artifacts ma ON ma.artifact_id = ar.artifact_id"
            " WHERE ma.book_id = ?",
            (book_id,),
        ).fetchall()
        for r in rows_artifacts:
            path = r["managed_path"]
            if path:
                targets.append(path)
        manifest_targets = self.get_cleanup_manifest(book_id)
        if manifest_targets:
            targets.extend(manifest_targets)
        seen: set[str] = set()
        ordered: list[str] = []
        for t in targets:
            if t not in seen:
                seen.add(t)
                ordered.append(t)
        return ordered

    def list_book_page_ids(self, book_id: str) -> list[str]:
        rows = self._conn.execute(
            "SELECT p.page_id FROM pages p"
            " JOIN chapters c ON c.chapter_id = p.chapter_id"
            " WHERE c.book_id = ?",
            (book_id,),
        ).fetchall()
        return [r["page_id"] for r in rows]

    def is_whole_library(self, book_ids: Sequence[str]) -> bool:
        rows = self._conn.execute("SELECT book_id FROM books").fetchall()
        all_book_ids = {r["book_id"] for r in rows}
        if not all_book_ids:
            return False
        return set(book_ids) == all_book_ids

    # ------------------------------------------------------------------
    # FEA-12 C flow: authoritative delete inventory + preflight
    # ------------------------------------------------------------------
    #
    # ADJ-001 PD-01/PD-03: the inventory is computed by Core from the same
    # rows the delete transaction will remove; it is strictly read-only (no
    # UPDATE/INSERT, no file mutation, no caching).  PD-08: shared references
    # that can be split safely are *not* a conflict — only out-of-target rows
    # that a delete would have to corrupt (schema CHECK forbids detaching
    # them) fail closed.  D1 X1: a non-terminal source operation is the
    # BOOK_BUSY blocker for the C-17 subgraph.

    _BOOK_BINDINGS_SUBQUERY = (
        "SELECT b.binding_id FROM page_bindings b WHERE b.project_id = ?"
    )
    _BOOK_REGION_REVISIONS_SUBQUERY = (
        "SELECT rr.region_revision_id FROM region_revisions rr"
        " JOIN regions r ON r.region_id = rr.region_id"
        " JOIN pages p ON p.page_id = r.page_id"
        " JOIN chapters c ON c.chapter_id = p.chapter_id WHERE c.book_id = ?"
    )
    _BOOK_REGION_IDS_SUBQUERY = (
        "SELECT r.region_id FROM regions r"
        " JOIN pages p ON p.page_id = r.page_id"
        " JOIN chapters c ON c.chapter_id = p.chapter_id WHERE c.book_id = ?"
    )

    def _count(self, sql: str, params: tuple) -> int:
        row = self._conn.execute(sql, params).fetchone()
        return int(row[0]) if row is not None and row[0] is not None else 0

    def list_book_region_current_pointers(self, book_id: str) -> list[dict[str, Any]]:
        """Every region of the book with its current revision, stable order.

        The caller picks the first *lineage-visible* pointer for the PD-01
        ``currentRevisionId`` disclosure (Lead ruling: the disclosure must
        follow the released FEA-11 read semantics, so the visible filter
        lives in the application/guard layer, not here).
        """
        rows = self._conn.execute(
            "SELECT p.page_id, r.region_id, r.current_revision_id"
            " FROM regions r"
            " JOIN pages p ON p.page_id = r.page_id"
            " JOIN chapters c ON c.chapter_id = p.chapter_id"
            " WHERE c.book_id = ?"
            " ORDER BY c.sort_order, c.import_order, c.chapter_id,"
            "          p.sort_order, p.page_id, r.reading_order, r.region_id",
            (book_id,),
        ).fetchall()
        return [dict(row) for row in rows]

    def list_book_artifact_current_pointers(self, book_id: str) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            "SELECT p.page_id, ma.artifact_id, ma.artifact_type,"
            "       ma.current_revision_id"
            " FROM media_artifacts ma"
            " JOIN pages p ON p.page_id = ma.page_id"
            " JOIN chapters c ON c.chapter_id = p.chapter_id"
            " WHERE c.book_id = ? AND ma.current_revision_id IS NOT NULL"
            " ORDER BY c.sort_order, c.import_order, c.chapter_id,"
            "          p.sort_order, p.page_id, ma.artifact_type, ma.artifact_id",
            (book_id,),
        ).fetchall()
        return [dict(row) for row in rows]

    def list_book_region_ids(self, book_id: str) -> list[str]:
        rows = self._conn.execute(self._BOOK_REGION_IDS_SUBQUERY, (book_id,)).fetchall()
        return [row[0] for row in rows]

    def list_book_region_revision_ids(self, book_id: str) -> list[str]:
        rows = self._conn.execute(
            self._BOOK_REGION_REVISIONS_SUBQUERY, (book_id,)
        ).fetchall()
        return [row[0] for row in rows]

    def list_book_binding_ids(self, book_id: str) -> list[str]:
        """The book's page bindings: ``project_id`` is the authority, plus the
        bindings of the book's own pages (a corrupt row naming another
        project is a preflight conflict, but the delete still needs the
        foreign-key closure to be complete)."""
        rows = self._conn.execute(
            "SELECT binding_id FROM page_bindings WHERE project_id = ?"
            " UNION"
            " SELECT b.binding_id FROM page_bindings b"
            " JOIN pages p ON p.page_id = b.page_id"
            " JOIN chapters c ON c.chapter_id = p.chapter_id"
            " WHERE c.book_id = ?",
            (book_id, book_id),
        ).fetchall()
        return [row[0] for row in rows]

    def list_book_artifact_revision_ids(self, book_id: str) -> list[str]:
        rows = self._conn.execute(
            "SELECT ar.artifact_revision_id FROM artifact_revisions ar"
            " JOIN media_artifacts ma ON ma.artifact_id = ar.artifact_id"
            " WHERE ma.book_id = ?",
            (book_id,),
        ).fetchall()
        return [row[0] for row in rows]

    def list_book_pinned_revision_ids(self, book_id: str) -> list[str]:
        """PD-01 pinned revisions: region revisions (C-01b current/pin) *and*
        artifact revisions carry ``is_pinned``; both are protected content the
        delete removes, so both are disclosed (Lead ruling, 2026-11-05)."""
        rows = self._conn.execute(
            "SELECT rr.region_revision_id AS revision_id FROM region_revisions rr"
            " JOIN regions r ON r.region_id = rr.region_id"
            " JOIN pages p ON p.page_id = r.page_id"
            " JOIN chapters c ON c.chapter_id = p.chapter_id"
            " WHERE c.book_id = ? AND rr.is_pinned = 1"
            " UNION"
            " SELECT ar.artifact_revision_id FROM artifact_revisions ar"
            " JOIN media_artifacts ma ON ma.artifact_id = ar.artifact_id"
            " WHERE ma.book_id = ? AND ar.is_pinned = 1",
            (book_id, book_id),
        ).fetchall()
        return sorted({row["revision_id"] for row in rows})

    def list_book_active_run_ids(self, book_id: str) -> list[str]:
        """Non-terminal Pipeline Run/Task ids touching the book (PD-01
        disclosure + the BOOK_BUSY blocker)."""
        rows = self._conn.execute(
            "SELECT DISTINCT pr.run_id FROM pipeline_runs pr"
            " WHERE pr.status NOT IN"
            "       ('completed', 'completed_with_failures', 'failed', 'cancelled')"
            " AND (json_extract(pr.run_json, '$.scope.book_id') = ?"
            "   OR EXISTS ("
            "     SELECT 1 FROM pipeline_run_targets prt"
            "     JOIN pages p ON p.page_id = prt.page_id"
            "     JOIN chapters c ON c.chapter_id = p.chapter_id"
            "     WHERE prt.pipeline_run_id = pr.run_id AND c.book_id = ?"
            "   ))"
            " UNION"
            " SELECT DISTINCT pt.pipeline_run_id FROM pipeline_tasks pt"
            " JOIN pages p ON p.page_id = pt.page_id"
            " JOIN chapters c ON c.chapter_id = p.chapter_id"
            " WHERE c.book_id = ?"
            "   AND pt.status NOT IN ('completed', 'failed', 'cancelled')",
            (book_id, book_id, book_id),
        ).fetchall()
        return sorted({row[0] for row in rows if row[0]})

    def list_book_active_export_ids(self, book_id: str) -> list[str]:
        rows = self._conn.execute(
            "SELECT export_id FROM export_history"
            " WHERE book_id = ?"
            "   AND status NOT IN ('completed', 'skipped', 'cancelled', 'failed')"
            " ORDER BY export_id",
            (book_id,),
        ).fetchall()
        return [row[0] for row in rows]

    def list_book_source_busy_operation_ids(self, book_id: str) -> list[str]:
        """D1 X1: non-terminal source operations bound to the book's bindings
        or lineage (started / host-authorized / core-committed-awaiting-ACK).
        These stay *kept* (plans/operations are audit history) but they block
        the delete with BOOK_BUSY while non-terminal."""
        rows = self._conn.execute(
            "SELECT DISTINCT op.operation_id FROM source_operations op"
            " WHERE op.state IN ('started', 'host-authorized', 'core-committed')"
            " AND (op.operation_id IN ("
            "        SELECT pub.operation_id FROM source_binding_publications pub"
            "        WHERE pub.binding_id IN (" + self._BOOK_BINDINGS_SUBQUERY + "))"
            "   OR op.operation_id IN ("
            "        SELECT lin.operation_id FROM source_revision_lineage lin"
            "        WHERE lin.operation_id IS NOT NULL"
            "          AND (lin.region_id IN (" + self._BOOK_REGION_IDS_SUBQUERY + ")"
            "            OR lin.binding_id IN (" + self._BOOK_BINDINGS_SUBQUERY + "))))"
            " ORDER BY op.operation_id",
            (book_id, book_id, book_id),
        ).fetchall()
        return [row[0] for row in rows]

    def has_unsafe_source_references(self, book_id: str) -> bool:
        """PD-08 fail-closed half: out-of-target source rows the delete cannot
        detach without violating a schema CHECK (or an inconsistent graph).

        Safely splittable sharing (shared managed files, shared artifact
        paths, out-of-target ``source_artifact_revision_id`` provenance) is
        NOT a conflict and is handled by the delete transaction itself.
        """
        bindings = self._BOOK_BINDINGS_SUBQUERY
        revisions = self._BOOK_REGION_REVISIONS_SUBQUERY
        regions = self._BOOK_REGION_IDS_SUBQUERY
        checks = (
            # A binding of the book's page that names another project.
            (
                "SELECT 1 FROM page_bindings b"
                " JOIN pages p ON p.page_id = b.page_id"
                " JOIN chapters c ON c.chapter_id = p.chapter_id"
                " WHERE c.book_id = ? AND b.project_id != ? LIMIT 1",
                (book_id, book_id),
            ),
            # A binding of the book whose page belongs to another book.
            (
                "SELECT 1 FROM page_bindings b WHERE b.project_id = ?"
                " AND b.page_id NOT IN ("
                "   SELECT p.page_id FROM pages p"
                "   JOIN chapters c ON c.chapter_id = p.chapter_id"
                "   WHERE c.book_id = ?) LIMIT 1",
                (book_id, book_id),
            ),
            # An out-of-target publication whose previous binding is the
            # book's: ``previous_binding_id`` cannot be detached for a
            # non-'added' relation (schema CHECK), so the row cannot survive.
            (
                "SELECT 1 FROM source_binding_publications pub"
                " WHERE pub.previous_binding_id IN (" + bindings + ")"
                "   AND pub.binding_id NOT IN (" + bindings + ") LIMIT 1",
                (book_id, book_id),
            ),
            # An out-of-target lineage row that names the book's rows.
            (
                "SELECT 1 FROM source_revision_lineage lin"
                " WHERE lin.revision_id NOT IN (" + revisions + ")"
                "   AND (lin.binding_id IN (" + bindings + ")"
                "     OR lin.from_revision_id IN (" + revisions + ")"
                "     OR lin.region_id IN (" + regions + ")) LIMIT 1",
                (book_id, book_id, book_id, book_id),
            ),
            # r1 R-010: an out-of-target binding whose ``previous_binding_id``
            # points at the book's binding.  The self-FK cannot be detached
            # without corrupting the other project's chain and the
            # ``UNIQUE(page_id) WHERE status <> 'superseded'`` rule forbids
            # inventing a replacement, so this inconsistent graph fails the
            # preflight as BOOK_DELETE_CONFLICT instead of an FK error later.
            (
                "SELECT 1 FROM page_bindings b"
                " WHERE b.binding_id NOT IN (" + bindings + ")"
                "   AND b.previous_binding_id IN (" + bindings + ") LIMIT 1",
                (book_id, book_id),
            ),
        )
        for sql, params in checks:
            if self._conn.execute(sql, params).fetchone() is not None:
                return True
        return False

    def shared_managed_targets(
        self, book_id: str, target_book_ids: Sequence[str]
    ) -> dict[str, int]:
        """Managed paths of this book that out-of-target books still
        reference, with the number of distinct other books.

        PD-08: those physical files are shared and must be *preserved*; the
        delete removes only the book's own rows, never the shared file.
        """
        targets = list(dict.fromkeys(target_book_ids))
        placeholders = ",".join("?" * len(targets))
        own_refs: set[str] = set()
        for sql in (
            "SELECT p.managed_original_ref AS ref FROM pages p"
            " JOIN chapters c ON c.chapter_id = p.chapter_id"
            " WHERE c.book_id = ? AND p.managed_original_ref IS NOT NULL"
            " AND p.managed_original_ref != ''",
            "SELECT ar.managed_path AS ref FROM artifact_revisions ar"
            " JOIN media_artifacts ma ON ma.artifact_id = ar.artifact_id"
            " WHERE ma.book_id = ? AND ar.managed_path IS NOT NULL"
            " AND ar.managed_path != ''",
        ):
            own_refs.update(row["ref"] for row in self._conn.execute(sql, (book_id,)))
        own_refs.discard("")
        if not own_refs:
            return {}
        ref_placeholders = ",".join("?" * len(own_refs))
        ordered_refs = sorted(own_refs)
        counts: dict[str, int] = {}
        page_rows = self._conn.execute(
            "SELECT p2.managed_original_ref AS ref,"
            "       COUNT(DISTINCT c2.book_id) AS n"
            " FROM pages p2"
            " JOIN chapters c2 ON c2.chapter_id = p2.chapter_id"
            f" WHERE c2.book_id NOT IN ({placeholders})"
            f"   AND p2.managed_original_ref IN ({ref_placeholders})"
            " GROUP BY p2.managed_original_ref",
            (*targets, *ordered_refs),
        ).fetchall()
        for row in page_rows:
            counts[row["ref"]] = max(counts.get(row["ref"], 0), int(row["n"]))
        artifact_rows = self._conn.execute(
            "SELECT ar2.managed_path AS ref, COUNT(DISTINCT ma2.book_id) AS n"
            " FROM artifact_revisions ar2"
            " JOIN media_artifacts ma2 ON ma2.artifact_id = ar2.artifact_id"
            f" WHERE ma2.book_id NOT IN ({placeholders})"
            f"   AND ar2.managed_path IN ({ref_placeholders})"
            " GROUP BY ar2.managed_path",
            (*targets, *ordered_refs),
        ).fetchall()
        for row in artifact_rows:
            counts[row["ref"]] = max(counts.get(row["ref"], 0), int(row["n"]))
        return counts

    def shared_source_entries(
        self, book_id: str, target_book_ids: Sequence[str]
    ) -> dict[str, int]:
        """Referenced-source entries this book shares with out-of-target books
        (PD-01 "other projects referencing the source" / PD-08 preserve)."""
        targets = list(dict.fromkeys(target_book_ids))
        own_entries = {
            row[0]
            for row in self._conn.execute(
                "SELECT DISTINCT entry_id FROM page_bindings WHERE project_id = ?",
                (book_id,),
            )
        }
        if not own_entries:
            return {}
        placeholders = ",".join("?" * len(targets))
        ref_placeholders = ",".join("?" * len(own_entries))
        rows = self._conn.execute(
            "SELECT entry_id, COUNT(DISTINCT project_id) AS n FROM page_bindings"
            f" WHERE entry_id IN ({ref_placeholders})"
            f"   AND project_id NOT IN ({placeholders})"
            " GROUP BY entry_id",
            (*sorted(own_entries), *targets),
        ).fetchall()
        return {row["entry_id"]: int(row["n"]) for row in rows}

    def cleanup_targets_for_delete(
        self, book_ids: Sequence[str]
    ) -> dict[str, list[str]]:
        """Own managed files per book, with safely-split shared files removed
        from the sweep list (the shared physical file is preserved; only the
        rows go away)."""
        target_ids = list(dict.fromkeys(book_ids))
        shared = {
            book_id: self.shared_managed_targets(book_id, target_ids)
            for book_id in target_ids
        }
        return {
            book_id: [
                path
                for path in self.list_book_cleanup_targets(book_id)
                if path not in shared[book_id]
            ]
            for book_id in target_ids
        }

    @staticmethod
    def _managed_target_size(storage: Any, relative_path: str) -> int:
        if storage is None:
            return 0
        try:
            return int(Path(storage.absolute_path(relative_path)).stat().st_size)
        except Exception:
            return 0

    def book_delete_inventory(
        self,
        book_id: str,
        target_book_ids: Sequence[str],
        storage: Any = None,
    ) -> dict[str, Any] | None:
        """The read-only PD-01 inventory of one book (``None`` = no Book row).

        Shared files are excluded from the sweep list *and* from
        ``deletedFiles``/``deletedBytes`` — they will not be deleted.
        """
        row = self._conn.execute(
            "SELECT book_id, title FROM books WHERE book_id = ?", (book_id,)
        ).fetchone()
        if row is None:
            return None
        targets = self.cleanup_targets_for_delete([book_id, *target_book_ids])[book_id]
        deleted_bytes = sum(
            self._managed_target_size(storage, path) for path in targets
        )
        return {
            "book_id": book_id,
            "title": row["title"],
            "lock_count": self._count(
                "SELECT COUNT(*) FROM regions r"
                " JOIN pages p ON p.page_id = r.page_id"
                " JOIN chapters c ON c.chapter_id = p.chapter_id"
                " WHERE c.book_id = ? AND ("
                "   r.region_locked = 1 OR r.translation_locked = 1"
                "   OR r.inpaint_locked = 1"
                "   OR COALESCE(json_extract(r.text_json,"
                "        '$.translation_locked'), 0) = 1)",
                (book_id,),
            ),
            "manual_region_count": self._count(
                "SELECT COUNT(*) FROM regions r"
                " JOIN pages p ON p.page_id = r.page_id"
                " JOIN chapters c ON c.chapter_id = p.chapter_id"
                " WHERE c.book_id = ?"
                "   AND COALESCE(json_extract(r.text_json, '$.manual_edited'), 0) = 1",
                (book_id,),
            ),
            "region_current_pointers": self.list_book_region_current_pointers(book_id),
            "artifact_current_pointers": self.list_book_artifact_current_pointers(
                book_id
            ),
            "pinned_revision_ids": self.list_book_pinned_revision_ids(book_id),
            "active_run_ids": self.list_book_active_run_ids(book_id),
            "active_export_ids": self.list_book_active_export_ids(book_id),
            "source_busy_operation_ids": self.list_book_source_busy_operation_ids(
                book_id
            ),
            "chapters": self._count(
                "SELECT COUNT(*) FROM chapters WHERE book_id = ?", (book_id,)
            ),
            "pages": self._count(
                "SELECT COUNT(*) FROM pages p"
                " JOIN chapters c ON c.chapter_id = p.chapter_id"
                " WHERE c.book_id = ?",
                (book_id,),
            ),
            "artifacts": self._count(
                "SELECT COUNT(*) FROM media_artifacts WHERE book_id = ?", (book_id,)
            ),
            "cleanup_targets": targets,
            "deleted_files": len(targets),
            "deleted_bytes": deleted_bytes,
            "shared_managed_targets": self.shared_managed_targets(
                book_id, [book_id, *target_book_ids]
            ),
            "shared_source_entries": self.shared_source_entries(
                book_id, [book_id, *target_book_ids]
            ),
            "source_graph_conflict": self.has_unsafe_source_references(book_id),
            "retry_manifest": self.get_cleanup_manifest_data(book_id) is not None,
        }

    def preflight_permanent_delete(
        self, book_ids: Sequence[str], storage: Any = None, export_runtime: Any = None
    ) -> tuple[bool, list[dict[str, Any]]]:
        """PD-08-aligned preflight: one authoritative inventory per book.

        A failure is *not* "sharing exists"; it is an inconsistent graph,
        unsplittable out-of-target state (BOOK_DELETE_CONFLICT), an active
        Run/Task/Export or a non-terminal source operation (BOOK_BUSY), or a
        target that has neither a Book row nor a pending cleanup manifest
        (BOOK_NOT_FOUND).
        """
        all_ok = True
        items: list[dict[str, Any]] = []
        target_book_ids = list(book_ids)
        for book_id in book_ids:
            inventory = self.book_delete_inventory(
                book_id, target_book_ids, storage=storage
            )
            if inventory is None:
                if self.get_cleanup_manifest_data(book_id) is None:
                    all_ok = False
                    items.append(
                        {
                            "book_id": book_id,
                            "status": "not_started",
                            "error_code": "BOOK_NOT_FOUND",
                        }
                    )
                else:
                    # PD-07: a committed delete whose file manifest survived
                    # is retryable and has no Book row to re-inspect.
                    items.append(
                        {"book_id": book_id, "status": "not_started", "error_code": None}
                    )
                continue
            item_error: str | None = None
            if inventory["active_run_ids"] or inventory["active_export_ids"]:
                item_error = "BOOK_BUSY"
            elif export_runtime is not None:
                try:
                    if export_runtime.has_active_exports_for_book(book_id):
                        item_error = "BOOK_BUSY"
                except Exception:
                    item_error = "BOOK_BUSY"
            if item_error is None and inventory["source_busy_operation_ids"]:
                item_error = "BOOK_BUSY"
            if item_error is None and inventory["source_graph_conflict"]:
                item_error = "BOOK_DELETE_CONFLICT"
            if item_error is None:
                # Managed path lexical/containment preflight of the actual
                # sweep list (shared files are preserved and skipped).
                for target in inventory["cleanup_targets"]:
                    segments = target.replace("\\", "/").split("/")
                    if (
                        ".." in segments
                        or "." in segments
                        or Path(target).is_absolute()
                        or any(segment == "" for segment in segments[1:])
                    ):
                        item_error = "BOOK_DELETE_CONFLICT"
                        break
                    if storage is not None:
                        try:
                            absolute_path = Path(
                                storage.absolute_path(target)
                            ).resolve()
                            # R5 P1: the baseline must not be resolved.
                            root = Path(os.path.abspath(str(storage.root)))
                            absolute_path.relative_to(root)
                        except Exception:
                            item_error = "BOOK_DELETE_CONFLICT"
                            break
            if item_error is not None:
                all_ok = False
            items.append(
                {
                    "book_id": book_id,
                    "status": "not_started",
                    "error_code": item_error,
                }
            )
        return all_ok, items

    def execute_permanent_delete_db(
        self,
        book_targets_map: dict[str, list[str]],
        book_page_ids_map: dict[str, list[str]] | None = None,
        book_preview_ids_map: dict[str, list[str]] | None = None,
    ) -> None:
        """Remove every content row of the target books in ONE transaction.

        ADJ-001 PD-05/PD-06: the transaction is opened explicitly with
        ``BEGIN IMMEDIATE`` so the read-checked preflight state cannot change
        under the delete, and any failure rolls the whole batch back — the
        caller only starts file cleanup after this returns.

        ADJ-001 PD-08: safely splittable shared references are removed from
        this book's side only; the shared physical file and the other
        projects' bindings are preserved.  Out-of-target
        ``source_artifact_revision_id`` provenance that would dangle is
        detached (the same rule the page-level purge already applies), while
        the target rows are deleted.

        D1 X1: the book's ``page_bindings`` / ``source_binding_publications``
        / ``source_revision_lineage`` rows are deleted in this same
        transaction; ``source_sync_plans`` / ``source_operations`` are audit
        history without a ``book_id`` column and stay queryable.  A
        non-terminal source operation is re-checked at the write boundary and
        raises ``BOOK_BUSY`` (zero side effects).
        """
        now_iso = datetime.now(timezone.utc).isoformat(timespec="milliseconds")
        target_book_ids = list(book_targets_map.keys())
        shared_targets = {
            book_id: self.shared_managed_targets(book_id, target_book_ids)
            for book_id in target_book_ids
        }
        conn = self._conn
        if not conn.in_transaction:
            conn.execute("BEGIN IMMEDIATE")
        with conn:
            for book_id, targets in book_targets_map.items():
                # PD-08: never sweep a physical file another (out-of-batch)
                # project still references; removing this book's rows is the
                # safe split, the shared file itself is preserved.
                targets = [t for t in targets if t not in shared_targets[book_id]]
                book_row = self._conn.execute(
                    "SELECT title FROM books WHERE book_id = ?", (book_id,)
                ).fetchone()
                book_title = book_row["title"] if book_row else ""

                existing_manifest = self.get_cleanup_manifest_data(book_id)
                if not book_row and existing_manifest:
                    continue

                pids = (book_page_ids_map or {}).get(book_id)
                if not pids:
                    pids = self.list_book_page_ids(book_id)
                if not pids and existing_manifest:
                    pids = existing_manifest.get("page_ids", [])

                # R1 Finding 1: preview_resource_ids are random (preview-<uuid4>) and
                # cannot be rebuilt once media_artifacts is gone, so a refused cleanup
                # would lose them forever and its retry would find an empty snapshot.
                # Persist them with the rest of the manifest.
                prior_preview = (existing_manifest or {}).get("preview_resource_ids", [])
                supplied_preview = (book_preview_ids_map or {}).get(book_id)
                manifest_payload = {
                    "managed_targets": list(targets),
                    "page_ids": list(pids),
                    "preview_resource_ids": list(
                        supplied_preview if supplied_preview else prior_preview
                    ),
                }

                self._conn.execute(
                    "INSERT OR REPLACE INTO book_cleanup_manifests (book_id, targets_json, created_at)"
                    " VALUES (?, ?, ?)",
                    (book_id, json.dumps(manifest_payload, ensure_ascii=False), now_iso),
                )

                if not book_row:
                    continue

                runs = self._conn.execute(
                    "SELECT DISTINCT pr.run_id, pr.run_json FROM pipeline_runs pr"
                    " WHERE json_extract(pr.run_json, '$.scope.book_id') = ?"
                    "   OR EXISTS ("
                    "       SELECT 1 FROM pipeline_run_targets prt"
                    "       JOIN pages p ON p.page_id = prt.page_id"
                    "       JOIN chapters c ON c.chapter_id = p.chapter_id"
                    "       WHERE prt.pipeline_run_id = pr.run_id AND c.book_id = ?"
                    "   )",
                    (book_id, book_id),
                ).fetchall()
                for r in runs:
                    run_id = r["run_id"]
                    try:
                        rj = json.loads(r["run_json"])
                    except Exception:
                        rj = {}
                    if book_title:
                        rj["book_title"] = book_title
                    if isinstance(rj.get("scope"), dict) and book_title:
                        rj["scope"]["book_title"] = book_title
                    # AC6 (R-003): strip locators from the WHOLE tree, not just
                    # the top-level scope.  A target/task/step entry nested
                    # below used to keep naming a page that no longer exists,
                    # so the retained history still identified deleted content.
                    # book_title is not a locator key and survives untouched.
                    rj = strip_run_json_locators(rj)
                    self._conn.execute(
                        "UPDATE pipeline_runs SET run_json = ?, requested_targets_json = '[]' WHERE run_id = ?",
                        (json.dumps(rj, ensure_ascii=False), run_id),
                    )

                # AC2 (N-001): a bare '' is not unique within a run.  The
                # table carries UNIQUE(pipeline_run_id, target_id), so
                # detaching every target of a multi-target run with '' makes
                # the second row collide and rolls the entire permanent delete
                # back.  The detached value has to stay unique while carrying
                # no locator meaning, so it is derived from the row's own
                # primary key and prefixed to mark it as detached rather than
                # as a reference to anything.
                self._conn.execute(
                    "UPDATE pipeline_run_targets"
                    " SET page_id = '',"
                    "     target_id = 'detached:' || run_target_id,"
                    "     region_id = NULL, snapshot_json = '{}'"
                    " WHERE page_id IN ("
                    "   SELECT p.page_id FROM pages p"
                    "   JOIN chapters c ON c.chapter_id = p.chapter_id"
                    "   WHERE c.book_id = ?"
                    " )",
                    (book_id,),
                )

                # R-003: Freeze target step_run_ids before clearing step_runs.page_id
                sr_rows = self._conn.execute(
                    "SELECT DISTINCT sr.step_run_id FROM step_runs sr"
                    " JOIN pages p ON p.page_id = sr.page_id"
                    " JOIN chapters c ON c.chapter_id = p.chapter_id"
                    " WHERE c.book_id = ?",
                    (book_id,),
                ).fetchall()
                target_step_run_ids = [r["step_run_id"] for r in sr_rows]

                # Clear output refs using the frozen step_run_ids
                if target_step_run_ids:
                    placeholders = ",".join("?" * len(target_step_run_ids))
                    self._conn.execute(
                        f"UPDATE step_run_output_refs SET value_json = '{{}}'"
                        f" WHERE step_run_id IN ({placeholders})",
                        target_step_run_ids,
                    )

                self._conn.execute(
                    "UPDATE pipeline_tasks SET page_id = '', target_id = '', region_id = NULL, units_json = '[]', step_run_ids_json = '[]'"
                    " WHERE page_id IN ("
                    "   SELECT p.page_id FROM pages p"
                    "   JOIN chapters c ON c.chapter_id = p.chapter_id"
                    "   WHERE c.book_id = ?"
                    " )",
                    (book_id,),
                )

                self._conn.execute(
                    "UPDATE step_runs SET page_id = '', target_id = '', region_id = NULL, input_refs_json = '[]', lock_snapshot_json = '{}', output_json = '{}'"
                    " WHERE page_id IN ("
                    "   SELECT p.page_id FROM pages p"
                    "   JOIN chapters c ON c.chapter_id = p.chapter_id"
                    "   WHERE c.book_id = ?"
                    " )",
                    (book_id,),
                )

                self._conn.execute(
                    "UPDATE step_run_input_refs SET revision_id = NULL"
                    " WHERE revision_id IN ("
                    "   SELECT ar.artifact_revision_id FROM artifact_revisions ar"
                    "   JOIN media_artifacts ma ON ma.artifact_id = ar.artifact_id"
                    "   WHERE ma.book_id = ?"
                    " )",
                    (book_id,),
                )

                self._conn.execute(
                    "UPDATE step_result_candidates SET page_id = '', target_id = '', region_id = NULL, base_revision_id = NULL, payload_json = '{}'"
                    " WHERE page_id IN ("
                    "   SELECT p.page_id FROM pages p"
                    "   JOIN chapters c ON c.chapter_id = p.chapter_id"
                    "   WHERE c.book_id = ?"
                    " ) OR base_revision_id IN ("
                    "   SELECT ar.artifact_revision_id FROM artifact_revisions ar"
                    "   JOIN media_artifacts ma ON ma.artifact_id = ar.artifact_id"
                    "   WHERE ma.book_id = ?"
                    " )",
                    (book_id, book_id),
                )

                # R-003 / AC6: Retain AND detach pipeline_stage_states history.
                # The rows must not be deleted (contract §5.11.4), but this
                # comment used to be the entire implementation: the locator
                # survived, so the retained history kept pointing at a page
                # that no longer exists - and at a region id that no longer
                # resolves.  The primary key is
                # (target_type, target_id, stage), so the detached value has to
                # stay unique across rows sharing a stage; a fresh random suffix
                # keeps it unique while carrying no reference to the deleted
                # page or region.
                self._conn.execute(
                    "UPDATE pipeline_stage_states"
                    " SET target_id = 'detached:' || lower(hex(randomblob(16)))"
                    " WHERE (target_type = 'page' AND target_id IN ("
                    "   SELECT p.page_id FROM pages p"
                    "   JOIN chapters c ON c.chapter_id = p.chapter_id"
                    "   WHERE c.book_id = ?"
                    " )) OR (target_type = 'region' AND target_id IN ("
                    "   SELECT r.region_id FROM regions r"
                    "   JOIN pages p ON p.page_id = r.page_id"
                    "   JOIN chapters c ON c.chapter_id = p.chapter_id"
                    "   WHERE c.book_id = ?"
                    " ))",
                    (book_id, book_id),
                )

                # D1 X1 (FEA-12-CORE): the C-17 §7.1 subgraph the book owns is
                # deleted in this same transaction — publications first (they
                # reference bindings), then lineage (it references revisions,
                # regions and bindings), then the page bindings themselves.
                # ``source_sync_plans`` / ``source_operations`` are NOT deleted:
                # they carry no book_id and remain the audit/operation history.
                # A non-terminal operation is re-read at this write boundary so
                # a race with source-sync cannot slip past the preflight.
                if self.list_book_source_busy_operation_ids(book_id):
                    raise PermanentDeleteBlockedError("BOOK_BUSY", book_id=book_id)
                self._delete_book_source_graph(book_id)

                exp_rows = self._conn.execute(
                    "SELECT export_id, scope_snapshot_json FROM export_history WHERE book_id = ?",
                    (book_id,),
                ).fetchall()
                for exp in exp_rows:
                    try:
                        sc = json.loads(exp["scope_snapshot_json"] or "{}")
                    except Exception:
                        sc = {}
                    sanitized_scope = {}
                    if book_title:
                        sanitized_scope["book_title"] = book_title
                    elif sc.get("book_title"):
                        sanitized_scope["book_title"] = sc["book_title"]
                    self._conn.execute(
                        "UPDATE export_history SET book_id = '', chapter_id = '', scope_snapshot_json = ? WHERE export_id = ?",
                        (json.dumps(sanitized_scope, ensure_ascii=False), exp["export_id"]),
                    )

                # PD-08 safely-splittable provenance: an out-of-target
                # revision may derive from a target revision.  Detach the
                # pointer on the surviving row instead of refusing the delete
                # (the same rule the page-level purge already applies); the
                # target's own rows are removed below anyway.
                self._conn.execute(
                    "UPDATE artifact_revisions SET source_artifact_revision_id = NULL"
                    " WHERE source_artifact_revision_id IN ("
                    "   SELECT ar.artifact_revision_id FROM artifact_revisions ar"
                    "   JOIN media_artifacts ma ON ma.artifact_id = ar.artifact_id"
                    "   WHERE ma.book_id = ?"
                    " )",
                    (book_id,),
                )
                self._conn.execute(
                    "DELETE FROM artifact_revisions WHERE artifact_id IN ("
                    "   SELECT artifact_id FROM media_artifacts WHERE book_id = ?"
                    " )",
                    (book_id,),
                )
                self._conn.execute("DELETE FROM media_artifacts WHERE book_id = ?", (book_id,))
                self._conn.execute(
                    "DELETE FROM region_revisions WHERE region_id IN ("
                    "   SELECT r.region_id FROM regions r"
                    "   JOIN pages p ON p.page_id = r.page_id"
                    "   JOIN chapters c ON c.chapter_id = p.chapter_id"
                    "   WHERE c.book_id = ?"
                    " )",
                    (book_id,),
                )
                self._conn.execute(
                    "DELETE FROM regions WHERE page_id IN ("
                    "   SELECT p.page_id FROM pages p"
                    "   JOIN chapters c ON c.chapter_id = p.chapter_id"
                    "   WHERE c.book_id = ?"
                    " )",
                    (book_id,),
                )
                self._conn.execute("DELETE FROM reading_progress WHERE book_id = ?", (book_id,))
                self._conn.execute(
                    "DELETE FROM pages WHERE chapter_id IN ("
                    "   SELECT chapter_id FROM chapters WHERE book_id = ?"
                    " )",
                    (book_id,),
                )
                self._conn.execute("DELETE FROM chapters WHERE book_id = ?", (book_id,))
                self._conn.execute("DELETE FROM book_tags WHERE book_id = ?", (book_id,))
                self._conn.execute("DELETE FROM books WHERE book_id = ?", (book_id,))

    # ------------------------------------------------------------------
    # FEA-12 C flow: D1 X1 source-graph cleanup (same transaction)
    # ------------------------------------------------------------------

    def _delete_book_source_graph(self, book_id: str) -> None:
        """Delete the book's C-17 subgraph: publications → lineage → bindings.

        D1 X1 (ADJ-2026-11-05-FEA-12-SCOPE): the C-17 draft §2 :30 explicitly
        defers this cleanup to a separate contract; this is that cleanup.  The
        child rows are deleted before their parents because C-17 declares no
        ``ON DELETE CASCADE``:

        * ``source_binding_publications`` reference ``page_bindings`` on both
          the new and the previous side;
        * ``source_revision_lineage`` references ``region_revisions``,
          ``regions`` and ``page_bindings``;
        * ``page_bindings`` reference ``pages`` and ``books``.

        Everything runs inside the caller's ``BEGIN IMMEDIATE`` transaction, so
        a failure leaves no orphan row behind.  Tables kept: ``sources``,
        ``source_locations``, ``source_versions``, ``source_entries``,
        ``source_sync_plans`` and ``source_operations`` (audit/operation
        history without a ``book_id`` column).
        """
        binding_ids = self.list_book_binding_ids(book_id)
        region_ids = self.list_book_region_ids(book_id)
        revision_ids = self.list_book_region_revision_ids(book_id)

        def _placeholders(values: Sequence[str]) -> tuple[str, tuple]:
            ordered = sorted(set(values))
            if not ordered:
                return "", ()
            return ",".join("?" for _ in ordered), tuple(ordered)

        binding_sql, binding_params = _placeholders(binding_ids)
        if binding_sql:
            self._conn.execute(
                "DELETE FROM source_binding_publications"
                f" WHERE binding_id IN ({binding_sql})",
                binding_params,
            )
        lineage_sql, lineage_params = _placeholders(
            [*revision_ids, *region_ids, *binding_ids]
        )
        if lineage_sql:
            revision_sql, revision_params = _placeholders(revision_ids)
            region_sql, region_params = _placeholders(region_ids)
            conditions = []
            params: list = []
            if revision_sql:
                conditions.append(f"revision_id IN ({revision_sql})")
                params.extend(revision_params)
            if region_sql:
                conditions.append(f"region_id IN ({region_sql})")
                params.extend(region_params)
            if binding_sql:
                conditions.append(f"binding_id IN ({binding_sql})")
                params.extend(binding_params)
            self._conn.execute(
                "DELETE FROM source_revision_lineage"
                f" WHERE {' OR '.join(conditions)}",
                tuple(params),
            )
        if binding_sql:
            self._conn.execute(
                f"DELETE FROM page_bindings WHERE binding_id IN ({binding_sql})",
                binding_params,
            )

    def list_page_artifact_ids(self, page_ids: Sequence[str]) -> list[str]:
        """AC4: artifact_ids of these pages, read from library.db.

        This is deliberately only half the answer.  ``preview_lifecycle`` lives in
        the *catalog* database, not this one - measured, not assumed: querying it
        here raises "no such table".  The caller joins the two: these artifact_ids
        are matched against catalog rows before the delete removes them.

        Why before: ``preview_lifecycle`` is reachable only through ``artifact_id``,
        and ``execute_permanent_delete_db`` deletes the ``media_artifacts`` rows.
        R7 measured that a lookup inside cleanup finds nothing by then.
        """
        if not page_ids:
            return []
        placeholders = ",".join("?" for _ in page_ids)
        rows = self._conn.execute(
            "SELECT artifact_id FROM media_artifacts WHERE page_id IN (%s)"
            % placeholders,
            tuple(page_ids),
        ).fetchall()
        return [row[0] for row in rows if row[0]]

    def cleanup_book_files(
        self,
        book_id: str,
        targets: Sequence[str],
        storage: Any,
        render_previews: Any = None,
        page_ids: Sequence[str] | None = None,
        preview_resource_ids: Sequence[str] | None = None,
    ) -> bool:
        manifest_data = None
        if not targets:
            manifest_data = self.get_cleanup_manifest_data(book_id)
            if manifest_data:
                targets = manifest_data.get("managed_targets", [])

        all_deleted = True
        for t in targets:
            try:
                storage.remove_managed(t)
            except Exception:
                all_deleted = False

        if not page_ids:
            if manifest_data is None:
                manifest_data = self.get_cleanup_manifest_data(book_id)
            if manifest_data:
                page_ids = manifest_data.get("page_ids")

        # AC4 (P09-PREVIEW-LIFECYCLE-RECLAIM-1): publish-style rows.  These cannot be
        # found by name -- the key is preview-<uuid4> and its rel_path is
        # previews/<key>.png, carrying no page or book component (measured R189).
        # The caller snapshots their resource_ids before the DB delete, because
        # preview_lifecycle is only reachable through artifact_id and that mapping
        # is gone by the time cleanup runs (R7).
        preview_ids_known = True
        if not preview_resource_ids:
            # R1 Finding 1: a retry after a refused cleanup cannot rebuild these (the
            # random key is gone once media_artifacts is deleted), so fall back to the
            # manifest written at delete time.
            if manifest_data is None:
                manifest_data = self.get_cleanup_manifest_data(book_id)
            if manifest_data:
                preview_resource_ids = manifest_data.get("preview_resource_ids") or []
                preview_ids_known = bool(manifest_data.get("preview_ids_known", True))
            elif not page_ids:
                # No manifest and no pages: nothing ever described previews for this book.
                preview_ids_known = True

        if preview_resource_ids and render_previews is not None:
            derived_root = getattr(render_previews, "_root", None)
            catalog = getattr(render_previews, "_catalog", None)
            if derived_root is not None and catalog is not None:
                root_res = Path(os.path.abspath(derived_root))
                for res_id in preview_resource_ids:
                    try:
                        entry = catalog.lookup(res_id)
                    except Exception:
                        all_deleted = False
                        continue
                    if entry is None or not entry.rel_path:
                        # Already gone: nothing to remove, nothing to count.
                        continue
                    try:
                        removed = unlink_preview_without_following(
                            str(entry.rel_path), root_res
                        )
                    except Exception:
                        # R1 Finding 3: the page-original branch converts a raising
                        # unlink into all_deleted=False rather than letting it escape
                        # past the boolean result.  Match that.
                        all_deleted = False
                        continue
                    if not removed:
                        # Same rule as the page-original branch: a refusal must not
                        # be counted as a removal, and its row must survive so the
                        # file stays traceable.
                        all_deleted = False
                        continue
                    try:
                        catalog.remove(res_id)
                    except Exception:
                        all_deleted = False

        if render_previews is not None and page_ids:
            try:
                derived_root = getattr(render_previews, "_root", None)
                catalog = getattr(render_previews, "_catalog", None)
                if derived_root is not None and catalog is not None:
                    # N-004 (Codex R4): do NOT resolve() here.  resolve()
                    # follows junctions, so when an ancestor of derived_root is a
                    # link it hands the chain an already-redirected root - and the
                    # chain then verifies that redirected root happily.  Measured:
                    # junction 'trusted' to an outside folder, resolve() yields
                    # outside\derived, and the delete succeeds on the outside file.
                    # abspath only normalises the path; the handle chain does its own
                    # per-segment reparse check starting at the drive root.
                    root_res = Path(os.path.abspath(derived_root))
                    for pid in page_ids:
                        res_id = f"page-original-{pid}"
                        try:
                            entry = catalog.lookup(res_id)
                            if entry is not None and entry.rel_path:
                                # AC5 / N-004: shared with its own unit test so
                                # this refusal cannot silently regress.
                                # F-004 (Codex R1): the helper returns False
                                # when it REFUSED to remove (reparse point,
                                # traversal, absolute path, or a plain unlink
                                # failure).  Dropping the catalog row anyway
                                # destroyed the only record of a file we did
                                # not delete, turning a recoverable failure
                                # into a permanent, untraceable leak.
                                removed = unlink_preview_without_following(
                                    str(entry.rel_path), root_res
                                )
                                if not removed:
                                    all_deleted = False
                                    continue
                            catalog.remove(res_id)
                        except Exception:
                            all_deleted = False
            except Exception:
                all_deleted = False

        if storage is not None:
            try:
                _sanitize_component(book_id)
                # R5 P1: baseline must not be resolved.  resolve() follows junctions, so a
                # link ABOVE the root drifts the baseline along with the candidate and
                # containment passes.  The candidate keeps resolve(), which is what makes an
                # escape visible.  Same defect class as N-004.
                root = Path(os.path.abspath(str(storage.root)))
                # R5 P1 (8th site, found by auditing every .resolve() rather than the
                # pattern I had assumed): books_base is a BASELINE, so it must not be
                # resolved either.  root is abspath now, but resolving books_base would
                # still follow a junction planted at root/books and move the bound.
                books_base = Path(os.path.abspath(str(root / "books")))
                book_dir = root / "books" / book_id
                resolved_dir = book_dir.resolve()
                if (
                    resolved_dir.is_relative_to(books_base)
                    and resolved_dir != books_base
                    and resolved_dir.exists()
                    and not _is_reparse_point(book_dir.lstat())
                ):
                    # AC8 (R-011): no recursive enumeration any more.  The
                    # previous os.walk visited every entry under the book
                    # directory just to rmdir empty ones, which enumerates
                    # user-visible export directories as a side effect.
                    # Now only the ancestor directories of the managed
                    # targets this run actually removed may be pruned,
                    # deepest first, and each prune is a plain rmdir that
                    # fails as soon as the directory is not empty.  Nothing
                    # under the book directory is listed, so a user export
                    # directory can be neither enumerated nor removed.
                    ancestors: set[Path] = set()
                    for rel_target in targets:
                        parts = [
                            seg
                            for seg in str(rel_target).replace("\\", "/").split("/")
                            if seg
                        ]
                        for cut in range(len(parts) - 1, 0, -1):
                            ancestors.add(Path(*parts[:cut]))
                    for rel_dir in sorted(
                        ancestors, key=lambda item: len(item.parts), reverse=True
                    ):
                        probe_dir = root / rel_dir
                        try:
                            probe_stat = probe_dir.lstat()
                        except OSError:
                            continue
                        if not stat.S_ISDIR(probe_stat.st_mode):
                            continue
                        if _is_reparse_point(probe_stat):
                            continue
                        try:
                            probe_dir.rmdir()
                        except OSError:
                            pass  # not empty (or vanished): leave it alone
                    try:
                        os.rmdir(str(book_dir))
                    except OSError:
                        pass
            except Exception:
                pass

        if all_deleted and not preview_ids_known:
            # R2 Finding 3: the manifest could not say whether previews exist (legacy
            # format).  Reporting success here would delete the manifest and strand any
            # rows it never described, with no record left to retry from.  Keep the
            # manifest and report pending instead.
            return False

        if all_deleted:
            with self._conn:
                self._conn.execute(
                    "DELETE FROM book_cleanup_manifests WHERE book_id = ?",
                    (book_id,),
                )
            return True
        return False
    # ------------------------------------------------------------------
    # FEA-09 / C-15 §2–§3: source storage + page bindings
    # ------------------------------------------------------------------

    def find_source_by_physical_identity(
        self, content_digest: str, volume_serial: int, file_id: int
    ) -> dict[str, Any] | None:
        """Locate an existing source by physical identity ``(content_digest,
        volume_serial, file_id)`` (C-15 §3.2 源复用规则). Returns the
        matched location row joined with its source_id, or None."""
        row = self._conn.execute(
            "SELECT l.source_id, l.location_id, l.is_current"
            " FROM source_locations l WHERE l.content_digest = ?"
            " AND l.volume_serial = ? AND l.file_id = ?",
            (content_digest, volume_serial, file_id),
        ).fetchone()
        return dict(row) if row else None

    def insert_source(
        self, source_id: str, source_kind: str, display_name: str,
        created_at: str, updated_at: str,
    ) -> None:
        with self._conn:
            self._conn.execute(
                "INSERT INTO sources (source_id, source_kind, display_name,"
                " created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                (source_id, source_kind, display_name, created_at, updated_at),
            )

    def insert_source_location(
        self, location_id: str, source_id: str, registry_id: str,
        authorization_generation: int, content_digest: str, volume_serial: int,
        file_id: int, size_bytes: int, observed_at: str, created_at: str,
        mtime_hint: str | None = None,
    ) -> None:
        with self._conn:
            self._conn.execute(
                "INSERT INTO source_locations (location_id, source_id,"
                " registry_id, authorization_generation, content_digest,"
                " volume_serial, file_id, size_bytes, mtime_hint, observed_at,"
                " created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (location_id, source_id, registry_id, authorization_generation,
                 content_digest, volume_serial, file_id, size_bytes, mtime_hint,
                 observed_at, created_at),
            )

    def refresh_source_location_auth(
        self, source_id: str, content_digest: str, volume_serial: int,
        file_id: int, registry_id: str, authorization_generation: int,
        last_verified_at: str,
    ) -> int:
        """Re-registration updates the matched physical location **in place**
        (registry/generation/last_verified_at) — no duplicate location row
        (C-15 §2 约束语义)."""
        with self._conn:
            cursor = self._conn.execute(
                "UPDATE source_locations SET registry_id = ?,"
                " authorization_generation = ?, last_verified_at = ?"
                " WHERE source_id = ? AND content_digest = ?"
                " AND volume_serial = ? AND file_id = ?",
                (registry_id, authorization_generation, last_verified_at,
                 source_id, content_digest, volume_serial, file_id),
            )
            return cursor.rowcount

    def supersede_source_location(self, location_id: str, superseded_marker: str) -> None:
        with self._conn:
            self._conn.execute(
                "UPDATE source_locations SET is_current = 0 WHERE location_id = ?",
                (location_id,),
            )

    def insert_source_version(
        self, version_id: str, source_id: str, location_id: str,
        content_digest: str, size_bytes: int, observed_at: str,
        created_at: str,
    ) -> None:
        with self._conn:
            self._conn.execute(
                "INSERT INTO source_versions (version_id, source_id,"
                " location_id, content_digest, size_bytes, observed_at,"
                " created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (version_id, source_id, location_id, content_digest,
                 size_bytes, observed_at, created_at),
            )

    def get_source_identity(self, source_id: str) -> dict[str, Any] | None:
        """Physical identity of a source's current location (C-15 §2.3).

        Used by the resolve path when the live grant was minted before the
        Core assigned the source id: the grant is matched by physical facts
        (content digest + volume/file id) instead.
        """
        row = self._conn.execute(
            "SELECT content_digest, volume_serial, file_id FROM source_locations"
            " WHERE source_id = ? AND is_current = 1",
            (source_id,),
        ).fetchone()
        return dict(row) if row else None

    def get_source_version(self, source_id: str, version_id: str) -> dict[str, Any] | None:
        row = self._conn.execute(
            "SELECT version_id, source_id, location_id, content_digest,"
            " size_bytes, observed_at FROM source_versions"
            " WHERE source_id = ? AND version_id = ?",
            (source_id, version_id),
        ).fetchone()
        return dict(row) if row else None

    def insert_source_entries(self, entries: Sequence[dict[str, Any]]) -> None:
        """Insert ``source_entries`` rows (one per occurrence — duplicate
        locators keep separate rows distinguished by ordinal; C-15 §3.2)."""
        with self._conn:
            self._conn.executemany(
                "INSERT INTO source_entries (source_id, version_id, entry_id,"
                " locator, ordinal, stable_sort_key, content_digest_kind,"
                " content_digest, encoded_digest, pixel_digest,"
                " pixel_digest_algorithm, size_bytes, mime_type, width, height,"
                " orientation, decoder_name, decoder_version,"
                " decoder_params_json, created_at)"
                " VALUES (:source_id, :version_id, :entry_id, :locator,"
                " :ordinal, :stable_sort_key, :content_digest_kind,"
                " :content_digest, :encoded_digest, :pixel_digest,"
                " :pixel_digest_algorithm, :size_bytes, :mime_type, :width,"
                " :height, :orientation, :decoder_name, :decoder_version,"
                " :decoder_params_json, :created_at)",
                [dict(entry) for entry in entries],
            )

    def find_current_binding_for_entry(
        self, project_id: str, source_id: str, entry_id: str
    ) -> dict[str, Any] | None:
        """Natural key for idempotent retries: same book + same entry with a
        non-superseded binding ⇒ already referenced (C-16 §4)."""
        row = self._conn.execute(
            "SELECT binding_id, page_id, status FROM page_bindings"
            " WHERE project_id = ? AND source_id = ? AND entry_id = ?"
            " AND status <> 'superseded'",
            (project_id, source_id, entry_id),
        ).fetchone()
        return dict(row) if row else None

    def insert_page_binding(self, binding: dict[str, Any]) -> None:
        """Insert a page_binding row with the frozen book-ownership guard
        (C-15 §2): page→chapter→book must equal ``project_id`` inside the
        same transaction, otherwise :class:`SourceProjectMismatch` rolls
        everything back."""
        row = self._conn.execute(
            "SELECT c.book_id FROM pages p JOIN chapters c"
            " ON c.chapter_id = p.chapter_id WHERE p.page_id = ?",
            (binding["page_id"],),
        ).fetchone()
        if row is None or row["book_id"] != binding["project_id"]:
            raise SourceProjectMismatch(
                "page->chapter->book does not match binding project_id"
                f" (page_id={binding['page_id']})"
            )
        self._conn.execute(
            "INSERT INTO page_bindings (binding_id, page_id, project_id,"
            " binding_version, source_id, entry_id, accepted_source_version,"
            " status, previous_binding_id, authorization_generation,"
            " authorized_at, verified_digest, created_at, updated_at)"
            " VALUES (:binding_id, :page_id, :project_id, :binding_version,"
            " :source_id, :entry_id, :accepted_source_version, :status,"
            " :previous_binding_id, :authorization_generation, :authorized_at,"
            " :verified_digest, :created_at, :updated_at)",
            dict(binding),
        )

    def get_page_binding(self, page_id: str) -> dict[str, Any] | None:
        row = self._conn.execute(
            "SELECT binding_id, page_id, project_id, binding_version,"
            " source_id, entry_id, accepted_source_version, status,"
            " authorization_generation, verified_digest"
            " FROM page_bindings WHERE page_id = ? AND status <> 'superseded'",
            (page_id,),
        ).fetchone()
        return dict(row) if row else None

    def mark_page_integrity_complete(self, page_id: str, updated_at: str) -> None:
        """Explicit, validated integrity transition for a referenced page
        commit (C-15 §4.3: update_page itself never flips the status)."""
        with self._conn:
            self._conn.execute(
                "UPDATE pages SET integrity_status = 'complete', updated_at = ?"
                " WHERE page_id = ? AND source_mode = 'referenced'",
                (updated_at, page_id),
            )

    def get_source_version_by_digest(
        self, source_id: str, content_digest: str
    ) -> dict[str, Any] | None:
        """Find a source's version by container digest (version reuse)."""
        row = self._conn.execute(
            "SELECT version_id, source_id, location_id, content_digest,"
            " size_bytes, observed_at FROM source_versions"
            " WHERE source_id = ? AND content_digest = ?",
            (source_id, content_digest),
        ).fetchone()
        return dict(row) if row else None

    def upsert_rendition_cache(self, entry: dict[str, Any]) -> None:
        """Record/refresh one reproducible rendition observation (C-15 §2.7).

        The cache row is derived-only metadata: it never carries user-source
        bytes or manual results. Existing keys refresh usage/size/digest.
        """
        now = entry["created_at"]
        with self._conn:
            self._conn.execute(
                "INSERT INTO rendition_cache (cache_key, source_id, version_id,"
                " entry_id, rendition_kind, decoder_name, decoder_version,"
                " params_digest, rel_path, size_bytes, content_digest,"
                " created_at, last_used_at, active_references)"
                " VALUES (:cache_key, :source_id, :version_id, :entry_id,"
                " :rendition_kind, :decoder_name, :decoder_version,"
                " :params_digest, :rel_path, :size_bytes, :content_digest,"
                " :created_at, :last_used_at, :active_references)"
                " ON CONFLICT(cache_key) DO UPDATE SET"
                " rel_path = excluded.rel_path,"
                " size_bytes = excluded.size_bytes,"
                " content_digest = excluded.content_digest,"
                " last_used_at = excluded.last_used_at",
                {
                    **entry,
                    "created_at": now,
                    "last_used_at": entry.get("last_used_at", now),
                    "active_references": int(
                        entry.get("active_references", 0) or 0
                    ),
                },
            )

    def list_source_entries(self, version_id: str) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            "SELECT entry_id, locator, ordinal, stable_sort_key,"
            " content_digest_kind, content_digest, size_bytes, width, height"
            " FROM source_entries"
            " WHERE version_id = ? ORDER BY ordinal",
            (version_id,),
        ).fetchall()
        return [dict(row) for row in rows]

    def entry_binding_exists_for_source(
        self, project_id: str, source_id: str
    ) -> bool:
        """Source-level already-referenced probe: any non-superseded binding
        of this source inside the project (C-16 §4 whole-source skip)."""
        row = self._conn.execute(
            "SELECT 1 FROM page_bindings WHERE project_id = ? AND source_id = ?"
            " AND status <> 'superseded' LIMIT 1",
            (project_id, source_id),
        ).fetchone()
        return row is not None

    def _current_location_id(self, source_id: str) -> str:
        row = self._conn.execute(
            "SELECT location_id FROM source_locations WHERE source_id = ?"
            " AND is_current = 1",
            (source_id,),
        ).fetchone()
        if row is None:
            raise SourceProjectMismatch(
                f"source {source_id} has no current location to version"
            )
        return str(row["location_id"])

    def commit_referenced_page_unit(
        self,
        *,
        page: Page,
        binding: dict[str, Any],
        source: dict[str, Any] | None,
        location: dict[str, Any] | None,
        version: dict[str, Any] | None,
        entries: Sequence[dict[str, Any]] | None,
    ) -> None:
        """FEA-09 one-page commit unit (C-15 §6.4/C-16 §4).

        A single SQLite transaction inserts (as needed) the source,
        location, version and all version entries, then the page and its
        healthy binding. ``SourceProjectMismatch`` and any constraint
        failure roll the whole unit back — uncommitted pages never become
        visible. Read/decode work happens outside this transaction.
        """
        with self._conn:
            location_id: str | None = None
            if source is not None and location is not None:
                self._conn.execute(
                    "INSERT INTO sources (source_id, source_kind, display_name,"
                    " created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                    (
                        source["source_id"], source["source_kind"],
                        source["display_name"], source["created_at"],
                        source["updated_at"],
                    ),
                )
                location_id = f"sl-{uuid.uuid4().hex}"
                self._conn.execute(
                    "INSERT INTO source_locations (location_id, source_id,"
                    " registry_id, authorization_generation, content_digest,"
                    " volume_serial, file_id, size_bytes, mtime_hint,"
                    " observed_at, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?,"
                    " ?, ?, ?)",
                    (
                        location_id, location["source_id"], location["registry_id"],
                        location["authorization_generation"],
                        location["content_digest"], location["volume_serial"],
                        location["file_id"], location["size_bytes"],
                        location.get("mtime_hint"), location["observed_at"],
                        location["created_at"],
                    ),
                )
            if version is not None:
                if location_id is None:
                    location_id = self._current_location_id(version["source_id"])
                self._conn.execute(
                    "INSERT INTO source_versions (version_id, source_id,"
                    " location_id, content_digest, size_bytes, observed_at,"
                    " created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (
                        version["version_id"], version["source_id"], location_id,
                        version["content_digest"], version["size_bytes"],
                        version["observed_at"], version["created_at"],
                    ),
                )
            if entries:
                self._conn.executemany(
                    "INSERT INTO source_entries (source_id, version_id, entry_id,"
                    " locator, ordinal, stable_sort_key, content_digest_kind,"
                    " content_digest, encoded_digest, pixel_digest,"
                    " pixel_digest_algorithm, size_bytes, mime_type, width,"
                    " height, orientation, decoder_name, decoder_version,"
                    " decoder_params_json, created_at)"
                    " VALUES (:source_id, :version_id, :entry_id, :locator,"
                    " :ordinal, :stable_sort_key, :content_digest_kind,"
                    " :content_digest, :encoded_digest, :pixel_digest,"
                    " :pixel_digest_algorithm, :size_bytes, :mime_type, :width,"
                    " :height, :orientation, :decoder_name, :decoder_version,"
                    " :decoder_params_json, :created_at)",
                    [dict(entry) for entry in entries],
                )
            self._conn.execute(
                "INSERT INTO pages (" + self._PAGE_COLUMNS + ")"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    page.page_id, page.chapter_id, page.source_filename,
                    page.source_order, page.sort_order, page.source_hash,
                    page.source_size_bytes, page.width, page.height,
                    page.managed_original_ref, int(page.page_locked),
                    page.review_state, page.overall_status,
                    page.created_at, page.updated_at, page.deleted_at,
                    page.source_mode, page.integrity_status,
                ),
            )
            self.insert_page_binding(dict(binding))




#: AC6 (R-003): locator keys that must not survive in a detached ``run_json``.
#: They identify pages, regions, targets, tasks or steps that no longer exist
#: once the book is permanently deleted.  ``run_id`` and the stage/status
#: fields are deliberately absent: the run itself is the history being kept.
_RUN_JSON_LOCATOR_KEYS = frozenset(
    {
        "book_id",
        "chapter_id",
        "page_id",
        "page_ids",
        "ordered_page_ids",
        "last_page_id",
        "region_id",
        "region_ids",
        "target_id",
        "target_ids",
        "run_target_id",
        "run_target_ids",
        "task_id",
        "task_ids",
        "step_run_id",
        "step_run_ids",
    }
)
def strip_run_json_locators(value: Any) -> Any:
    """AC6 (R-003): drop nested target/task/step locators from a run_json tree.

    The cleanup used to pop locators off ``rj["scope"]`` only, so any locator
    nested deeper - inside a target, task or step entry - survived the
    permanent delete and still named a page that no longer exists.  This walks
    the whole tree.  It is pure: the input structure is not modified.
    """
    if isinstance(value, dict):
        return {
            key: strip_run_json_locators(item)
            for key, item in value.items()
            if key not in _RUN_JSON_LOCATOR_KEYS
        }
    if isinstance(value, list):
        return [strip_run_json_locators(item) for item in value]
    return value


def unlink_preview_without_following(raw_rel: str, root_res: Path) -> bool:
    """AC5 (N-004): delete one derived preview file without following a link.

    Returns True when a plain file was actually removed.

    The raw, *unresolved* path is walked one segment at a time and the removal
    is refused as soon as any component is a reparse point.  Resolving first
    would follow a junction/symlink, let the reparse check inspect the
    *destination* - an ordinary file that passes every check - and then unlink
    that destination, deleting a file the tampered catalog entry never
    legitimately referred to.  Lexical component checks and an absolute-path
    guard run before the walk.
    """
    normalised = raw_rel.replace("\\", "/")
    segments = [segment for segment in normalised.split("/") if segment]
    if not segments:
        return False
    if any(segment in ("..", ".") for segment in segments):
        return False
    # F-003 (Codex R1): reject any embedded colon.  Two distinct Windows
    # hazards hide behind it.  "C:evil.png" is drive-RELATIVE, so
    # Path.is_absolute() is False and the absolute guard below passes it
    # straight through.  And a colon inside a path opens an alternate data
    # stream, so "file.png:hidden" names a different file than the catalog row
    # claims.  A preview filename this code ever writes contains neither.
    if any(":" in segment for segment in segments):
        return False
    if Path(normalised).is_absolute():
        return False
    probe = root_res
    for segment in segments:
        probe = probe / segment
        try:
            probe_stat = probe.lstat()
        except OSError:
            break  # nothing there to traverse through
        if _is_reparse_point(probe_stat):
            return False
    # N-002 (Codex R2): hand the last step to a handle chain.  Everything above
    # checks *names*; unlink() would resolve the name once more, and a junction
    # swapped in after the loop sends that resolution outside the root.  The probe
    # in verification/P09-AC3-DELETE-HARDEN-1 reproduces exactly that: the helper
    # returned True while deleting the outside file, a silent wrong-delete, since
    # the caller then proceeds to catalog.remove().
    #
    # unlink_by_handle opens each component relative to its parent's handle, so the
    # checks and the delete act on the same object.  None means the platform has no
    # such implementation and the path-based tail below runs instead.
    handled = unlink_by_handle(root_res, segments)
    if handled is not None:
        return handled
    if probe.is_file():
        probe.unlink(missing_ok=True)
        return True
    return False


def _soft_delete_timestamp() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")
