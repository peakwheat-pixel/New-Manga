"""In-memory fakes for the ui_shell suite.

A minimal LibraryRepository fake (protocol subset used by the shelf) and
a stub importer recording import_files calls, mirroring the contract in
application/library/ports.py and application/importing/images/ports.py.
"""

from __future__ import annotations

from domain.books.entities import Book, Chapter, Tag


class InMemoryLibraryRepository:
    def __init__(self) -> None:
        self.books: dict[str, Book] = {}
        self.chapters: dict[str, Chapter] = {}
        self.tags: dict[str, Tag] = {}
        self.book_tags: set[tuple[str, str]] = set()

    # books
    def add_book(self, book: Book) -> None:
        self.books[book.book_id] = book

    def get_book(self, book_id: str) -> Book | None:
        return self.books.get(book_id)

    def list_books(self) -> list[Book]:
        return list(self.books.values())

    def update_book(self, book: Book) -> None:
        self.books[book.book_id] = book

    # chapters
    def add_chapter(self, chapter: Chapter) -> None:
        self.chapters[chapter.chapter_id] = chapter

    def get_chapter(self, chapter_id: str) -> Chapter | None:
        return self.chapters.get(chapter_id)

    def list_chapters(self, book_id: str) -> list[Chapter]:
        return [
            chapter
            for chapter in self.chapters.values()
            if chapter.book_id == book_id
        ]

    def update_chapter(self, chapter: Chapter) -> None:
        self.chapters[chapter.chapter_id] = chapter

    # tags
    def add_tag(self, tag: Tag) -> None:
        self.tags[tag.tag_id] = tag

    def get_tag(self, tag_id: str) -> Tag | None:
        return self.tags.get(tag_id)

    def find_tag_by_name(self, name: str) -> Tag | None:
        for tag in self.tags.values():
            if tag.name == name:
                return tag
        return None

    def list_tags(self) -> list[Tag]:
        return list(self.tags.values())

    def update_tag(self, tag: Tag) -> None:
        self.tags[tag.tag_id] = tag

    def delete_tag(self, tag_id: str) -> None:
        self.tags.pop(tag_id, None)
        self.book_tags = {pair for pair in self.book_tags if pair[1] != tag_id}

    def add_book_tag(self, book_id: str, tag_id: str) -> None:
        self.book_tags.add((book_id, tag_id))

    def remove_book_tag(self, book_id: str, tag_id: str) -> None:
        self.book_tags.discard((book_id, tag_id))

    def list_tags_of_book(self, book_id: str) -> list[Tag]:
        return [
            self.tags[tag_id]
            for btag, tag_id in self.book_tags
            if btag == book_id and tag_id in self.tags
        ]


class StubImporter:
    """Records import_files calls; returns a canned ImportReport."""

    def __init__(self, report=None) -> None:
        from application.importing.images.ports import ImportReport

        self._default_report = report or ImportReport(chapter_id="")
        self.calls: list[dict] = []

    def import_files(self, chapter_id: str, sources: list, **kwargs):
        self.calls.append(
            {
                "chapter_id": chapter_id,
                "sources": list(sources),
                "kwargs": kwargs,
            }
        )
        from dataclasses import replace

        return replace(self._default_report, chapter_id=chapter_id)


class StubSource:
    """Minimal ImportSource stand-in (filename + read() bytes)."""

    def __init__(self, filename: str, data: bytes = b"") -> None:
        self.filename = filename
        self._data = data

    def read(self) -> bytes:
        return self._data


def make_source(filename: str, data: bytes = b""):
    """A real frozen ImportSource (application port dataclass)."""
    from application.importing.images.ports import ImportSource

    return ImportSource(filename=filename, data_provider=lambda: data)
