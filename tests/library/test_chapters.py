"""Chapter hierarchy, type/direction rules, mixed book, reordering
(AC-CH-001~004, D03 §4.4)."""

import pytest

from application.library.errors import BookNotFound, ChapterNotFound
from domain.books.entities import Chapter, ReadingDirection


def test_hierarchy_book_chapter_page(library, book):
    # AC-CH-001: Book → Chapter → Page, no Volume layer anywhere.
    chapter = library.create_chapter(book.book_id, "第1话", chapter_number="1")
    assert chapter.book_id == book.book_id
    assert library.list_chapters(book.book_id) == [chapter]
    # The domain defines no Volume type; chapter_number carries 卷/话/番外.
    special = library.create_chapter(book.book_id, "第10.5话", chapter_number="10.5")
    assert special.chapter_number == "10.5"


def test_paged_chapter_directions(library, book):
    # AC-CH-002: paged with rtl or ltr.
    rtl = library.create_chapter(book.book_id, "右开", chapter_type="paged",
                                 reading_direction="rtl")
    ltr = library.create_chapter(book.book_id, "左开", chapter_type="paged",
                                 reading_direction="ltr")
    assert rtl.reading_direction is ReadingDirection.RTL
    assert ltr.reading_direction is ReadingDirection.LTR
    with pytest.raises(ValueError):
        Chapter(chapter_id="bad", book_id=book.book_id, title="竖排分页",
                chapter_type="paged", reading_direction="vertical")


def test_webtoon_chapter_is_vertical(library, book):
    # AC-CH-003: webtoon created with vertical.
    chapter = library.create_chapter(book.book_id, "条漫1", chapter_type="webtoon")
    assert chapter.chapter_type.value == "webtoon"
    assert chapter.reading_direction is ReadingDirection.VERTICAL
    with pytest.raises(ValueError):
        library.create_chapter(book.book_id, "条漫2", chapter_type="webtoon",
                               reading_direction="rtl")


def test_mixed_types_in_one_book(library, book):
    # AC-CH-004: same book holds paged and webtoon chapters together.
    paged = library.create_chapter(book.book_id, "第1话", chapter_type="paged")
    webtoon = library.create_chapter(book.book_id, "特别条漫", chapter_type="webtoon")
    listed = library.list_chapters(book.book_id)
    assert {c.chapter_type.value for c in listed} == {"paged", "webtoon"}


def test_type_defaults_inherit_from_book(library):
    from domain.books.entities import ChapterType

    webtoon_book = library.create_book(
        "纯条漫", source_language="ko", target_language="zh",
        default_chapter_type="webtoon", default_reading_direction="vertical",
    )
    chapter = library.create_chapter(webtoon_book.book_id, "EP1")
    assert chapter.chapter_type is ChapterType.WEBTOON
    assert chapter.reading_direction is ReadingDirection.VERTICAL

    # A paged chapter under a webtoon book falls back to rtl, not vertical.
    paged = library.create_chapter(webtoon_book.book_id, "番外分页", chapter_type="paged")
    assert paged.reading_direction is ReadingDirection.RTL

    ltr_book = library.create_book(
        "左开漫画", default_chapter_type="paged", default_reading_direction="ltr"
    )
    inherited_ltr = library.create_chapter(ltr_book.book_id, "第1话")
    assert inherited_ltr.reading_direction is ReadingDirection.LTR


def test_chapter_reorder_keeps_import_order(library, book):
    first = library.create_chapter(book.book_id, "第1话")
    second = library.create_chapter(book.book_id, "第2话")
    third = library.create_chapter(book.book_id, "第3话")
    assert [c.import_order for c in (first, second, third)] == [1, 2, 3]

    library.reorder_chapters(book.book_id, [third.chapter_id, first.chapter_id,
                                            second.chapter_id])
    listed = library.list_chapters(book.book_id)
    assert [c.title for c in listed] == ["第3话", "第1话", "第2话"]
    # import_order is frozen at creation (D03 §5.3 semantics for chapters).
    assert [c.import_order for c in listed] == [3, 1, 2]


def test_delete_chapter_and_unknown_book(library, book):
    chapter = library.create_chapter(book.book_id, "将被删除")
    library.delete_chapter(chapter.chapter_id)
    assert library.list_chapters(book.book_id) == []
    with pytest.raises(ChapterNotFound):
        library.get_chapter(chapter.chapter_id)
    with pytest.raises(BookNotFound):
        library.create_chapter("missing-book", "第1话")
