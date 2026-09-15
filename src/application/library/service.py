"""Bookshelf use cases: Book/Chapter CRUD, tags, favorite/archive.

Favorite and archive are plain system flags on Book (D03 §3.3) — they never
create or consume Tag rows (AC-LIB-003). Tag deletion unlinks associations
only; books survive (AC-LIB-002, D04 §6).
"""

from __future__ import annotations

import uuid

from application.library.errors import (
    BookNotFound,
    ChapterNotFound,
    DuplicateTagName,
    TagNotFound,
)
from application.library.ports import LibraryRepository
from domain.books.entities import Book, Chapter, ChapterType, ReadingDirection, Tag


def _new_id() -> str:
    return uuid.uuid4().hex


class LibraryService:
    def __init__(self, repository: LibraryRepository) -> None:
        self._repo = repository

    # ------------------------------------------------------------------
    # books (AC-LIB-001)
    # ------------------------------------------------------------------

    def create_book(
        self,
        title: str,
        *,
        original_title: str = "",
        author: str = "",
        publisher: str = "",
        series_title: str = "",
        description: str = "",
        source_language: str = "",
        target_language: str = "",
        source_url: str = "",
        notes: str = "",
        default_chapter_type: ChapterType = ChapterType.PAGED,
        default_reading_direction: ReadingDirection = ReadingDirection.RTL,
    ) -> Book:
        book = Book(
            book_id=_new_id(),
            title=title,
            original_title=original_title,
            author=author,
            publisher=publisher,
            series_title=series_title,
            description=description,
            source_language=source_language,
            target_language=target_language,
            source_url=source_url,
            notes=notes,
            default_chapter_type=ChapterType(default_chapter_type),
            default_reading_direction=ReadingDirection(default_reading_direction),
        )
        self._repo.add_book(book)
        return book

    def get_book(self, book_id: str) -> Book:
        book = self._repo.get_book(book_id)
        if book is None or book.deleted:
            raise BookNotFound(book_id)
        return book

    def list_books(self) -> list[Book]:
        """Shelf contents: every book not soft-deleted (archived included,
        the UI filters views)."""
        return [book for book in self._repo.list_books() if not book.deleted]

    def update_book(self, book_id: str, **changes: str) -> Book:
        book = self.get_book(book_id)
        book.apply_edit(**changes)
        self._repo.update_book(book)
        return book

    def delete_book(self, book_id: str) -> None:
        book = self.get_book(book_id)
        book.soft_delete()
        self._repo.update_book(book)

    def set_favorite(self, book_id: str, favorite: bool) -> Book:
        book = self.get_book(book_id)
        book.set_favorite(favorite)
        self._repo.update_book(book)
        return book

    def set_archived(self, book_id: str, archived: bool) -> Book:
        book = self.get_book(book_id)
        book.set_archived(archived)
        self._repo.update_book(book)
        return book

    # ------------------------------------------------------------------
    # chapters (AC-CH-001..004)
    # ------------------------------------------------------------------

    def create_chapter(
        self,
        book_id: str,
        title: str,
        *,
        chapter_number: str = "",
        subtitle: str = "",
        chapter_type: ChapterType | None = None,
        reading_direction: ReadingDirection | None = None,
        notes: str = "",
    ) -> Chapter:
        book = self.get_book(book_id)
        resolved_type = ChapterType(chapter_type) if chapter_type else book.default_chapter_type
        if reading_direction is not None:
            direction = ReadingDirection(reading_direction)
        elif resolved_type is ChapterType.WEBTOON:
            direction = ReadingDirection.VERTICAL
        elif book.default_reading_direction is not ReadingDirection.VERTICAL:
            direction = book.default_reading_direction
        else:
            direction = ReadingDirection.RTL

        existing = [
            chapter for chapter in self._repo.list_chapters(book_id) if not chapter.deleted
        ]
        next_order = (
            max((chapter.import_order for chapter in existing), default=0) + 1
        )
        chapter = Chapter(
            chapter_id=_new_id(),
            book_id=book_id,
            title=title,
            chapter_number=chapter_number,
            subtitle=subtitle,
            import_order=next_order,
            sort_order=next_order,
            chapter_type=resolved_type,
            reading_direction=direction,
            notes=notes,
        )
        self._repo.add_chapter(chapter)
        return chapter

    def get_chapter(self, chapter_id: str) -> Chapter:
        chapter = self._repo.get_chapter(chapter_id)
        if chapter is None or chapter.deleted:
            raise ChapterNotFound(chapter_id)
        return chapter

    def list_chapters(self, book_id: str) -> list[Chapter]:
        self.get_book(book_id)  # existence + not deleted
        chapters = [
            chapter for chapter in self._repo.list_chapters(book_id) if not chapter.deleted
        ]
        return sorted(chapters, key=lambda chapter: chapter.sort_order)

    def update_chapter(self, chapter_id: str, **changes: str) -> Chapter:
        chapter = self.get_chapter(chapter_id)
        chapter.apply_edit(**changes)
        self._repo.update_chapter(chapter)
        return chapter

    def delete_chapter(self, chapter_id: str) -> None:
        chapter = self.get_chapter(chapter_id)
        chapter.soft_delete()
        self._repo.update_chapter(chapter)

    def reorder_chapters(self, book_id: str, ordered_chapter_ids: list[str]) -> list[Chapter]:
        """Apply a user ordering; import_order values stay frozen (D03 §5.3)."""
        chapters = {chapter.chapter_id: chapter for chapter in self.list_chapters(book_id)}
        missing = [cid for cid in ordered_chapter_ids if cid not in chapters]
        if missing:
            raise ChapterNotFound(missing[0])
        reordered = []
        for position, chapter_id in enumerate(ordered_chapter_ids, start=1):
            chapter = chapters[chapter_id]
            chapter.reorder(position)
            self._repo.update_chapter(chapter)
            reordered.append(chapter)
        return reordered

    # ------------------------------------------------------------------
    # tags (AC-LIB-002)
    # ------------------------------------------------------------------

    def create_tag(self, name: str) -> Tag:
        if self._repo.find_tag_by_name(name) is not None:
            raise DuplicateTagName(name)
        tag = Tag(tag_id=_new_id(), name=name)
        self._repo.add_tag(tag)
        return tag

    def rename_tag(self, tag_id: str, new_name: str) -> Tag:
        tag = self._require_tag(tag_id)
        clash = self._repo.find_tag_by_name(new_name)
        if clash is not None and clash.tag_id != tag_id:
            raise DuplicateTagName(new_name)
        tag.rename(new_name)
        self._repo.update_tag(tag)
        return tag

    def delete_tag(self, tag_id: str) -> None:
        self._require_tag(tag_id)
        # Associations are removed with the tag; books are untouched
        # (AC-LIB-002: deleting a tag never deletes a book).
        self._repo.delete_tag(tag_id)

    def list_tags(self) -> list[Tag]:
        return self._repo.list_tags()

    def add_tag_to_book(self, book_id: str, tag_id: str) -> None:
        self.get_book(book_id)
        self._require_tag(tag_id)
        self._repo.add_book_tag(book_id, tag_id)

    def remove_tag_from_book(self, book_id: str, tag_id: str) -> None:
        self.get_book(book_id)
        self._require_tag(tag_id)
        self._repo.remove_book_tag(book_id, tag_id)

    def tags_of_book(self, book_id: str) -> list[Tag]:
        self.get_book(book_id)
        return self._repo.list_tags_of_book(book_id)

    def _require_tag(self, tag_id: str) -> Tag:
        tag = self._repo.get_tag(tag_id)
        if tag is None:
            raise TagNotFound(tag_id)
        return tag
