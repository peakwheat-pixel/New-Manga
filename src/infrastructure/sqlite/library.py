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
from collections.abc import Sequence
from datetime import datetime, timezone

from domain.books.entities import Book, Chapter, ChapterType, ReadingDirection, Tag
from domain.pages.entities import Page
from infrastructure.filesystem.managed_storage import _is_reparse_point, _sanitize_component


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
        """Hashes of the chapter's **live** complete pages.

        Soft-deleted pages are excluded (F-10, TASK-044): a trashed page used
        to swallow a re-import silently — the file was reported as a duplicate
        while the chapter showed no page. ``max_source_order`` below
        deliberately still counts trashed pages, so a later restore can never
        collide with a page imported in the meantime.

        NOTE: ``application/importing/images/ports.py`` still documents the
        previous "soft-deleted rows stay visible here" contract; that docstring
        is outside TASK-044's allowed paths and is owed as a follow-up.
        """
        rows = self._conn.execute(
            "SELECT source_hash FROM pages"
            " WHERE chapter_id = ? AND deleted_at IS NULL AND "
            + self._COMPLETE_PAGE_WHERE,
            (chapter_id,),
        ).fetchall()
        return {row["source_hash"] for row in rows}

    def max_source_order(self, chapter_id: str) -> int:
        """Highest ``source_order`` in the chapter, trashed pages included.

        Keeping soft-deleted rows in the maximum is intentional: their order
        slots are reserved until the batch is restored or purged, so appending
        a new import after them cannot hand two pages the same order.
        """
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
        # Soft-deleted pages are hidden here too, consistent with
        # list_pages (AC-IMPORT semantics; recycle-bin/restore views are a
        # later slice with their own queries).
        row = self._conn.execute(
            "SELECT " + self._PAGE_COLUMNS + " FROM pages"
            " WHERE page_id = ? AND deleted_at IS NULL AND "
            + self._COMPLETE_PAGE_WHERE,
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
        with self._conn:
            self._conn.execute(
                "UPDATE artifact_revisions SET source_artifact_revision_id = NULL"
                f" WHERE source_artifact_revision_id IN ({purged_revisions})",
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
                }
            if isinstance(val, list):
                return {"managed_targets": list(val), "page_ids": []}
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

    def preflight_permanent_delete(
        self, book_ids: Sequence[str], storage: Any = None, export_runtime: Any = None
    ) -> tuple[bool, list[dict[str, Any]]]:
        all_ok = True
        items: list[dict[str, Any]] = []
        target_ids_set = set(book_ids)
        for book_id in book_ids:
            item_error: str | None = None
            book_row = self._conn.execute(
                "SELECT book_id FROM books WHERE book_id = ?", (book_id,)
            ).fetchone()
            manifest_row = self._conn.execute(
                "SELECT 1 FROM book_cleanup_manifests WHERE book_id = ?", (book_id,)
            ).fetchone()
            if book_row is None and manifest_row is None:
                item_error = "BOOK_NOT_FOUND"
            elif book_row is not None:
                # 1. R-001: Active pipeline runs
                busy_runs = self._conn.execute(
                    "SELECT 1 FROM pipeline_runs pr"
                    " WHERE pr.status NOT IN ('completed', 'completed_with_failures', 'failed', 'cancelled')"
                    " AND ("
                    "   json_extract(pr.run_json, '$.scope.book_id') = ?"
                    "   OR EXISTS ("
                    "     SELECT 1 FROM pipeline_run_targets prt"
                    "     JOIN pages p ON p.page_id = prt.page_id"
                    "     JOIN chapters c ON c.chapter_id = p.chapter_id"
                    "     WHERE prt.pipeline_run_id = pr.run_id AND c.book_id = ?"
                    "   )"
                    " )",
                    (book_id, book_id),
                ).fetchone()
                if busy_runs is not None:
                    item_error = "BOOK_BUSY"

                if item_error is None:
                    # 2. R-001: Active pipeline tasks
                    busy_tasks = self._conn.execute(
                        "SELECT 1 FROM pipeline_tasks pt"
                        " JOIN pages p ON p.page_id = pt.page_id"
                        " JOIN chapters c ON c.chapter_id = p.chapter_id"
                        " WHERE c.book_id = ? AND pt.status NOT IN ('completed', 'failed', 'cancelled')",
                        (book_id,),
                    ).fetchone()
                    if busy_tasks is not None:
                        item_error = "BOOK_BUSY"

                if item_error is None:
                    # 3. R-001: Active export history & export runtime
                    busy_exports = self._conn.execute(
                        "SELECT 1 FROM export_history"
                        " WHERE book_id = ? AND status NOT IN ('completed', 'skipped', 'cancelled', 'failed')",
                        (book_id,),
                    ).fetchone()
                    if busy_exports is not None:
                        item_error = "BOOK_BUSY"
                    elif export_runtime is not None:
                        try:
                            if export_runtime.has_active_exports_for_book(book_id):
                                item_error = "BOOK_BUSY"
                        except Exception:
                            item_error = "BOOK_BUSY"

                if item_error is None:
                    # 4. R-002: Shared Managed Copy (external to the requested batch)
                    placeholders = ",".join("?" * len(target_ids_set))
                    shared_page = self._conn.execute(
                        f"SELECT 1 FROM pages p2"
                        f" JOIN chapters c2 ON c2.chapter_id = p2.chapter_id"
                        f" WHERE c2.book_id NOT IN ({placeholders})"
                        f" AND p2.managed_original_ref IN ("
                        f"   SELECT p.managed_original_ref FROM pages p"
                        f"   JOIN chapters c ON c.chapter_id = p.chapter_id"
                        f"   WHERE c.book_id = ? AND p.managed_original_ref IS NOT NULL AND p.managed_original_ref != ''"
                        f" )",
                        (*target_ids_set, book_id),
                    ).fetchone()
                    if shared_page is not None:
                        item_error = "BOOK_DELETE_CONFLICT"

                    if item_error is None:
                        shared_artifact = self._conn.execute(
                            f"SELECT 1 FROM artifact_revisions ar2"
                            f" JOIN media_artifacts ma2 ON ma2.artifact_id = ar2.artifact_id"
                            f" WHERE ma2.book_id NOT IN ({placeholders})"
                            f" AND ar2.managed_path IN ("
                            f"   SELECT ar.managed_path FROM artifact_revisions ar"
                            f"   JOIN media_artifacts ma ON ma.artifact_id = ar.artifact_id"
                            f"   WHERE ma.book_id = ? AND ar.managed_path IS NOT NULL AND ar.managed_path != ''"
                            f" )",
                            (*target_ids_set, book_id),
                        ).fetchone()
                        if shared_artifact is not None:
                            item_error = "BOOK_DELETE_CONFLICT"

                if item_error is None:
                    # 5. R-002: Cross-project Revision references
                    cross_ref = self._conn.execute(
                        f"SELECT 1 FROM artifact_revisions ar2"
                        f" JOIN media_artifacts ma2 ON ma2.artifact_id = ar2.artifact_id"
                        f" WHERE ma2.book_id NOT IN ({placeholders})"
                        f" AND ar2.source_artifact_revision_id IN ("
                        f"   SELECT ar.artifact_revision_id FROM artifact_revisions ar"
                        f"   JOIN media_artifacts ma ON ma.artifact_id = ar.artifact_id"
                        f"   WHERE ma.book_id = ?"
                        f" )",
                        (*target_ids_set, book_id),
                    ).fetchone()
                    if cross_ref is not None:
                        item_error = "BOOK_DELETE_CONFLICT"

                if item_error is None:
                    # 6. Lexical and containment preflight of cleanup targets
                    targets = self.list_book_cleanup_targets(book_id)
                    for t in targets:
                        segments = t.replace("\\", "/").split("/")
                        if (
                            ".." in segments
                            or "." in segments
                            or Path(t).is_absolute()
                            or any(s == "" for s in segments[1:])
                        ):
                            item_error = "BOOK_DELETE_CONFLICT"
                            break
                        if storage is not None:
                            try:
                                abs_p = Path(storage.absolute_path(t)).resolve()
                                root = storage.root.resolve()
                                abs_p.relative_to(root)
                            except Exception:
                                item_error = "BOOK_DELETE_CONFLICT"
                                break
            if item_error is not None:
                all_ok = False
            items.append({
                "book_id": book_id,
                "status": "not_started",
                "error_code": item_error,
            })
        return all_ok, items

    def execute_permanent_delete_db(
        self,
        book_targets_map: dict[str, list[str]],
        book_page_ids_map: dict[str, list[str]] | None = None,
    ) -> None:
        now_iso = datetime.now(timezone.utc).isoformat(timespec="milliseconds")
        with self._conn:
            for book_id, targets in book_targets_map.items():
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

                manifest_payload = {
                    "managed_targets": list(targets),
                    "page_ids": list(pids),
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
                    if isinstance(rj.get("scope"), dict):
                        if book_title:
                            rj["scope"]["book_title"] = book_title
                        rj["scope"].pop("book_id", None)
                        rj["scope"].pop("chapter_id", None)
                        rj["scope"].pop("page_id", None)
                        rj["scope"].pop("page_ids", None)
                        rj["scope"].pop("ordered_page_ids", None)
                    self._conn.execute(
                        "UPDATE pipeline_runs SET run_json = ?, requested_targets_json = '[]' WHERE run_id = ?",
                        (json.dumps(rj, ensure_ascii=False), run_id),
                    )

                self._conn.execute(
                    "UPDATE pipeline_run_targets SET page_id = '', target_id = '', region_id = NULL, snapshot_json = '{}'"
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

                # R-003: Retain and detach pipeline_stage_states history (do NOT DELETE per contract §5.11.4)

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

                self._conn.execute(
                    "UPDATE artifact_revisions SET source_artifact_revision_id = NULL"
                    " WHERE source_artifact_revision_id IN ("
                    "   SELECT ar.artifact_revision_id FROM artifact_revisions ar"
                    "   JOIN media_artifacts ma ON ma.artifact_id = ar.artifact_id"
                    "   WHERE ma.book_id = ?"
                    " ) AND artifact_id IN ("
                    "   SELECT artifact_id FROM media_artifacts WHERE book_id = ?"
                    " )",
                    (book_id, book_id),
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

    def cleanup_book_files(
        self,
        book_id: str,
        targets: Sequence[str],
        storage: Any,
        render_previews: Any = None,
        page_ids: Sequence[str] | None = None,
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

        if render_previews is not None and page_ids:
            try:
                derived_root = getattr(render_previews, "_root", None)
                catalog = getattr(render_previews, "_catalog", None)
                if derived_root is not None and catalog is not None:
                    root_res = Path(derived_root).resolve()
                    for pid in page_ids:
                        res_id = f"page-original-{pid}"
                        try:
                            entry = catalog.lookup(res_id)
                            if entry is not None and entry.rel_path:
                                # AC5 / N-004: never resolve() before lstat().
                                # resolve() follows the link, so the reparse
                                # check would inspect the *destination* and the
                                # unlink would then delete the destination file
                                # instead of refusing the tampered entry.
                                # Walk the raw, unresolved path segment by
                                # segment and refuse the whole removal on the
                                # first link; only then touch the file.
                                raw_rel = str(entry.rel_path).replace("\\", "/")
                                raw_segs = [seg for seg in raw_rel.split("/") if seg]
                                if (
                                    raw_segs
                                    and not any(seg in ("..", ".") for seg in raw_segs)
                                    and not Path(raw_rel).is_absolute()
                                ):
                                    probe = root_res
                                    crossed_link = False
                                    for seg in raw_segs:
                                        probe = probe / seg
                                        try:
                                            probe_st = probe.lstat()
                                        except OSError:
                                            break  # nothing there to traverse
                                        if _is_reparse_point(probe_st):
                                            crossed_link = True
                                            break
                                    if not crossed_link:
                                        target_f = root_res / raw_rel
                                        if target_f.is_file():
                                            target_f.unlink(missing_ok=True)
                            catalog.remove(res_id)
                        except Exception:
                            all_deleted = False
            except Exception:
                all_deleted = False

        if storage is not None:
            try:
                _sanitize_component(book_id)
                root = storage.root.resolve()
                books_base = (root / "books").resolve()
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

        if all_deleted:
            with self._conn:
                self._conn.execute(
                    "DELETE FROM book_cleanup_manifests WHERE book_id = ?",
                    (book_id,),
                )
            return True
        return False



def _soft_delete_timestamp() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")
