"""Library application errors (user-facing failure reasons)."""

from __future__ import annotations


class LibraryError(Exception):
    """Base class for library use-case failures."""


class BookNotFound(LibraryError):
    def __init__(self, book_id: str) -> None:
        super().__init__(f"book not found: {book_id}")
        self.book_id = book_id


class ChapterNotFound(LibraryError):
    def __init__(self, chapter_id: str) -> None:
        super().__init__(f"chapter not found: {chapter_id}")
        self.chapter_id = chapter_id


class TagNotFound(LibraryError):
    def __init__(self, tag_id: str) -> None:
        super().__init__(f"tag not found: {tag_id}")
        self.tag_id = tag_id


class DuplicateTagName(LibraryError):
    def __init__(self, name: str) -> None:
        super().__init__(f"tag name already exists: {name}")
        self.name = name
