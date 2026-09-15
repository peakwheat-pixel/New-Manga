"""BookshelfViewModel + list models (AC-LIB-001, AC-CH-001, D05 §7/§8/§9,
§62 empty states, D05 §67 shelf→workbench/reader context)."""

from __future__ import annotations

import helpers  # noqa: F401  (sys.path injection)

import pytest

pytest.importorskip("PySide6")

from PySide6.QtCore import QModelIndex  # noqa: E402

from application.library.service import LibraryService  # noqa: E402
from fakes import InMemoryLibraryRepository, StubImporter, make_source  # noqa: E402
from ui.models.library.models import BookListModel, ChapterListModel  # noqa: E402
from ui.viewmodels.bookshelf.viewmodel import BookshelfViewModel  # noqa: E402


@pytest.fixture()
def repo():
    return InMemoryLibraryRepository()


@pytest.fixture()
def library(repo):
    return LibraryService(repo)


@pytest.fixture()
def importer():
    return StubImporter()


@pytest.fixture()
def vm(qapp, library, importer):
    from ui.viewmodels.navigation.viewmodel import NavigationViewModel

    return BookshelfViewModel(
        library=library, importer=importer, navigation=NavigationViewModel()
    )


def refresh(model: BookListModel) -> None:
    model.refresh()


class TestBookListModel:
    def test_roles_and_rows(self, vm, library) -> None:
        library.create_book("进击的巨人", original_title="進撃の巨人")
        library.create_book("海贼王")
        vm.refreshBooks()
        model = vm.bookListModel
        assert model.rowCount(QModelIndex()) == 2
        names = {bytes(v).decode() for v in model.roleNames().values()}
        assert {"bookId", "title", "originalTitle", "isFavorite", "isArchived"} <= names
        index = model.index(0, 0)
        assert model.data(index, model.roleForName("title")) in {"进击的巨人", "海贼王"}

    def test_role_for_name_unknown_returns_invalid(self, vm) -> None:
        model = vm.bookListModel
        assert model.roleForName("nope") == -1


class TestChapterListModel:
    def test_chapter_rows_sorted_by_sort_order(self, vm, library) -> None:
        book = library.create_book("书A")
        ch1 = library.create_chapter(book.book_id, "第01话", chapter_number="01")
        ch2 = library.create_chapter(book.book_id, "第02话", chapter_number="02")
        model = ChapterListModel()
        model.set_chapters(library.list_chapters(book.book_id))
        assert model.rowCount(QModelIndex()) == 2
        titles = [
            model.data(model.index(i, 0), model.roleForName("title"))
            for i in range(2)
        ]
        assert titles == ["第01话", "第02话"]
        assert ch1.sort_order < ch2.sort_order
        types = [
            model.data(model.index(i, 0), model.roleForName("chapterType"))
            for i in range(2)
        ]
        assert types == ["paged", "paged"]


class TestShelfCrud:
    def test_create_book_appears_in_model(self, vm) -> None:
        vm.createBook("新书", "Original")
        assert vm.bookListModel.rowCount(QModelIndex()) == 1  # AC-LIB-001
        assert vm.bookCount == 1

    def test_empty_state(self, vm) -> None:
        assert vm.bookCount == 0
        assert vm.isEmpty is True  # D05 §62: 还没有作品

    def test_select_book_exposes_detail_and_chapters(self, vm, library) -> None:
        book = library.create_book("书B")
        library.create_chapter(book.book_id, "第01话")
        vm.refreshBooks()
        vm.selectBook(book.book_id)
        detail = vm.selectedBook
        assert detail["title"] == "书B"
        assert vm.chapterListModel.rowCount(QModelIndex()) == 1

    def test_delete_book_removes_from_shelf(self, vm, library) -> None:
        book = library.create_book("将删")
        vm.refreshBooks()
        vm.deleteBook(book.book_id)
        assert vm.bookCount == 0

    def test_favorite_and_archive_flags(self, vm, library) -> None:
        book = library.create_book("书C")
        vm.refreshBooks()
        vm.setFavorite(book.book_id, True)
        vm.setArchived(book.book_id, True)
        stored = library.get_book(book.book_id)
        assert stored.is_favorite and stored.is_archived  # AC-LIB-003

    def test_archived_filter_hides_archived_by_default(self, vm, library) -> None:
        normal = library.create_book("正常")
        archived = library.create_book("已归档")
        library.set_archived(archived.book_id, True)
        vm.refreshBooks()
        assert vm.bookCount == 1
        vm.selectBook(normal.book_id)
        vm.setArchivedFilter(True)
        assert vm.bookCount == 1
        # after switching the filter the archived one is the only row
        assert vm.bookListModel.data(
            vm.bookListModel.index(0, 0), vm.bookListModel.roleForName("title")
        ) == "已归档"

    def test_search_filters_by_title(self, vm, library) -> None:
        library.create_book("进击的巨人")
        library.create_book("海贼王")
        vm.refreshBooks()
        vm.setSearchText("进击")
        assert vm.bookCount == 1


class TestImportEntry:
    def test_import_delegates_to_use_case(self, vm, library, importer) -> None:
        book = library.create_book("书D")
        chapter = library.create_chapter(book.book_id, "第01话")
        vm.refreshBooks()
        vm.selectBook(book.book_id)
        report = vm.importPages(chapter.chapter_id, [make_source("p001.png", b"x")])
        assert len(importer.calls) == 1
        call = importer.calls[0]
        assert call["chapter_id"] == chapter.chapter_id
        assert [s.filename for s in call["sources"]] == ["p001.png"]
        assert report.chapter_id == chapter.chapter_id

    def test_import_requires_known_chapter(self, vm, importer) -> None:
        from application.library.errors import ChapterNotFound

        with pytest.raises(ChapterNotFound):
            vm.importPages("missing-chapter", [make_source("p.png")])


class TestNavigationFromShelf:
    def test_enter_translation_carries_book_and_chapter(
        self, vm, library
    ) -> None:
        book = library.create_book("书E")
        chapter = library.create_chapter(book.book_id, "第01话")
        vm.refreshBooks()
        vm.selectBook(book.book_id)
        vm.enterTranslation(chapter.chapter_id)
        assert vm.navigation.currentPage == "workbench"
        assert vm.navigation.workbenchContext["book_id"] == book.book_id
        assert vm.navigation.workbenchContext["chapter_id"] == chapter.chapter_id

    def test_enter_reading_carries_reader_context(self, vm, library) -> None:
        book = library.create_book("书F")
        chapter = library.create_chapter(book.book_id, "第01话")
        vm.refreshBooks()
        vm.selectBook(book.book_id)
        vm.enterReading(chapter.chapter_id)
        assert vm.navigation.currentPage == "reader"
        context = vm.navigation.readerContext
        assert context["book_id"] == book.book_id
        assert context["chapter_id"] == chapter.chapter_id
