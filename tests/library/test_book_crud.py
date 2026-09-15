"""Book CRUD, tags, favorite/archive separation (AC-LIB-001/002/003)."""

import pytest

from application.library.errors import BookNotFound, DuplicateTagName, TagNotFound
from application.library.service import LibraryService


def test_create_book_shows_on_shelf(library):
    # AC-LIB-001: create with the approved fields, immediately visible.
    book = library.create_book(
        "我推的孩子",
        original_title="【推しの子】",
        author="赤坂アカ",
        source_language="ja",
        target_language="zh",
        default_chapter_type="paged",
        default_reading_direction="rtl",
    )
    shelf = library.list_books()
    assert [b.title for b in shelf] == ["我推的孩子"]
    assert book.original_title == "【推しの子】"
    assert book.default_chapter_type.value == "paged"


def test_book_requires_title(library):
    with pytest.raises(ValueError):
        library.create_book("   ")


def test_update_and_soft_delete_book(library, book):
    library.update_book(book.book_id, title="改名作品", notes="用户备注")
    updated = library.get_book(book.book_id)
    assert updated.title == "改名作品" and updated.notes == "用户备注"

    library.delete_book(book.book_id)
    assert updated.deleted is True
    assert all(b.book_id != book.book_id for b in library.list_books())
    with pytest.raises(BookNotFound):
        library.get_book(book.book_id)


def test_tag_lifecycle_and_book_link(library, book):
    # AC-LIB-002: create / rename / delete / attach / detach.
    tag = library.create_tag("连载中")
    library.rename_tag(tag.tag_id, "已完结")
    library.add_tag_to_book(book.book_id, tag.tag_id)
    assert [t.name for t in library.tags_of_book(book.book_id)] == ["已完结"]

    other = library.create_book("另一部")
    library.add_tag_to_book(other.book_id, tag.tag_id)
    library.remove_tag_from_book(other.book_id, tag.tag_id)
    assert library.tags_of_book(other.book_id) == []

    library.delete_tag(tag.tag_id)
    assert library.list_tags() == []
    # Deleting a tag never deletes books (AC-LIB-002).
    assert library.get_book(book.book_id).title == "進撃テスト"
    assert library.get_book(other.book_id).title == "另一部"


def test_duplicate_tag_name_rejected(library):
    library.create_tag("同人")
    with pytest.raises(DuplicateTagName):
        library.create_tag("同人")


def test_unknown_tag_operations(library, book):
    with pytest.raises(TagNotFound):
        library.add_tag_to_book(book.book_id, "missing")


def test_favorite_and_archive_are_system_states(library, book):
    # AC-LIB-003: favorite/archive are flags on the book, not tags.
    library.set_favorite(book.book_id, True)
    library.set_archived(book.book_id, True)

    stored = library.get_book(book.book_id)
    assert stored.is_favorite and stored.is_archived
    assert library.list_tags() == []  # no tag rows were created for them
    assert library.tags_of_book(book.book_id) == []

    # A same-named tag remains an independent user label.
    tag = library.create_tag("收藏夹")
    library.add_tag_to_book(book.book_id, tag.tag_id)
    library.set_favorite(book.book_id, False)
    stored = library.get_book(book.book_id)
    assert stored.is_favorite is False
    assert [t.name for t in library.tags_of_book(book.book_id)] == ["收藏夹"]


def test_simulated_restart_keeps_persisted_state(library, book):
    # Persistence contract: a fresh service over the same repository sees
    # the same data (real SQLite wiring arrives with the infra slice).
    repo = type(library._repo)()  # same contract implementation, fresh store
    first = LibraryService(repo)
    created = first.create_book("重启持久化", source_language="ko", target_language="zh")
    tag = first.create_tag("重启标签")
    first.add_tag_to_book(created.book_id, tag.tag_id)

    second = LibraryService(repo)  # "restart"
    loaded = second.get_book(created.book_id)
    assert loaded.title == "重启持久化"
    assert [t.name for t in second.tags_of_book(created.book_id)] == ["重启标签"]
