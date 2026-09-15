"""Test helpers for library/import suites: in-memory contract fakes, a real
Qt decoder and PNG factories. Importable as plain ``helpers`` because pytest
puts this directory on sys.path (no package __init__ by design).
"""

from __future__ import annotations

import sys
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from application.importing.images.ports import DecodedImage, ImageDecodeError  # noqa: E402
from domain.books.entities import Book, Chapter, Tag  # noqa: E402  (annotations)
from domain.pages.entities import Page  # noqa: E402


# ----------------------------------------------------------------------
# in-memory contract fakes
# ----------------------------------------------------------------------


class InMemoryLibraryRepository:
    def __init__(self) -> None:
        self.books: dict[str, Book] = {}
        self.chapters: dict[str, Chapter] = {}
        self.tags: dict[str, Tag] = {}
        self.book_tags: set[tuple[str, str]] = set()

    def add_book(self, book):
        self.books[book.book_id] = book

    def get_book(self, book_id):
        return self.books.get(book_id)

    def list_books(self):
        return list(self.books.values())

    def update_book(self, book):
        self.books[book.book_id] = book

    def add_chapter(self, chapter):
        self.chapters[chapter.chapter_id] = chapter

    def get_chapter(self, chapter_id):
        return self.chapters.get(chapter_id)

    def list_chapters(self, book_id):
        return [c for c in self.chapters.values() if c.book_id == book_id]

    def update_chapter(self, chapter):
        self.chapters[chapter.chapter_id] = chapter

    def add_tag(self, tag):
        self.tags[tag.tag_id] = tag

    def get_tag(self, tag_id):
        return self.tags.get(tag_id)

    def find_tag_by_name(self, name):
        return next((t for t in self.tags.values() if t.name == name), None)

    def list_tags(self):
        return list(self.tags.values())

    def update_tag(self, tag):
        self.tags[tag.tag_id] = tag

    def delete_tag(self, tag_id):
        self.tags.pop(tag_id, None)
        self.book_tags = {pair for pair in self.book_tags if pair[1] != tag_id}

    def add_book_tag(self, book_id, tag_id):
        self.book_tags.add((book_id, tag_id))

    def remove_book_tag(self, book_id, tag_id):
        self.book_tags.discard((book_id, tag_id))

    def list_tags_of_book(self, book_id):
        return [self.tags[tag_id] for bid, tag_id in self.book_tags if bid == book_id]


class InMemoryPageSink:
    def __init__(self) -> None:
        self.pages: list[Page] = []

    def existing_source_hashes(self, chapter_id: str) -> set[str]:
        return {page.source_hash for page in self.pages if page.chapter_id == chapter_id}

    def max_source_order(self, chapter_id: str) -> int:
        return max(
            (page.source_order for page in self.pages if page.chapter_id == chapter_id),
            default=0,
        )

    def add_page(self, page: Page) -> None:
        self.pages.append(page)


class FakeManagedCopyStore:
    """Copies bytes verbatim; can be told to fail for given filenames."""

    def __init__(self, fail_on: set[str] | None = None) -> None:
        self.stored: dict[str, bytes] = {}
        self.fail_on = set(fail_on or ())

    def store_original(self, chapter_id, source_filename, data, source_hash):
        if source_filename in self.fail_on:
            raise OSError(f"injected copy failure for {source_filename}")
        ref = f"books/b/chapters/{chapter_id}/original/{source_hash[:12]}_{source_filename}"
        self.stored[ref] = data
        return ref


class QtImageDecoder:
    """Real decode validation through Qt (dimensions from the bitmap)."""

    def decode(self, data: bytes) -> DecodedImage:
        from PySide6.QtGui import QImage

        image = QImage.fromData(data)
        if image.isNull():
            raise ImageDecodeError("bytes are not a decodable image")
        return DecodedImage(width=image.width(), height=image.height(), mime_type="image/png")


# ----------------------------------------------------------------------
# PNG factories
# ----------------------------------------------------------------------


def make_png(width: int = 4, height: int = 3, *, with_alpha: bool = True) -> bytes:
    from PySide6.QtCore import QBuffer, QIODevice
    from PySide6.QtGui import QColor, QImage

    image = QImage(width, height, QImage.Format_RGBA8888 if with_alpha else QImage.Format_RGB32)
    image.fill(QColor(12, 34, 56, 200 if with_alpha else 255))
    buffer = QBuffer()
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    ok = image.save(buffer, "PNG")
    assert ok, "QImage PNG save failed in test factory"
    return bytes(buffer.data())


def make_corrupt_png() -> bytes:
    valid = make_png()
    return valid[: len(valid) // 2]


def make_source(filename: str, data: bytes):
    from application.importing.images.ports import ImportSource

    return ImportSource(filename=filename, data_provider=lambda: data)
