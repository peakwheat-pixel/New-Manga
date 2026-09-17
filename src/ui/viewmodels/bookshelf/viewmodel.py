"""BookshelfViewModel: shelf state between QML and TASK-007 use cases.

Owns: book list (search/favorite/archive filters + sort), selection →
BookDetailPanel data + chapter list, CRUD entry points, the import entry
(delegating to the injected importer — production binds
``ImportImagesUseCase``), and shelf→workbench/reader navigation carrying
Book+Chapter context (D05 §67, D05 §8). No business logic lives in QML
(D05 §60); no infrastructure imports here (architecture guard).
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Property, QObject, Signal, Slot

from application.importing.images.ports import ImportSource
from application.library.service import LibraryService
from ui.models.library.models import BookListModel, ChapterListModel

_SORT_KEYS = ("recent", "title")


class BookshelfViewModel(QObject):
    bookCountChanged = Signal()
    selectedBookChanged = Signal()
    searchTextChanged = Signal()
    archivedFilterChanged = Signal()
    favoritesOnlyChanged = Signal()
    sortByChanged = Signal()
    viewModeChanged = Signal()
    importSummaryChanged = Signal()

    def __init__(
        self,
        *,
        library: LibraryService,
        importer,  # ImportImagesUseCase-shaped: import_files(chapter_id, sources, **kw)
        document_importer=None,  # TASK-023: ImportDocumentsUseCase-shaped; None keeps image-only
        navigation: QObject,  # NavigationViewModel
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._library = library
        self._importer = importer
        self._document_importer = document_importer
        self._navigation = navigation
        self._book_model = BookListModel(self)
        self._chapter_model = ChapterListModel(self)
        self._selected_book_id: str | None = None
        self._selected_book: dict = {}
        self._search_text = ""
        self._archived_filter = False
        self._favorites_only = False
        self._sort_by = "recent"
        self._view_mode = "grid"
        self._import_summary = ""

    # ------------------------------------------------------------------
    # models / properties
    # ------------------------------------------------------------------

    def get_book_list_model(self) -> QObject:
        return self._book_model

    bookListModel = Property(QObject, get_book_list_model, constant=True)

    def get_chapter_list_model(self) -> QObject:
        return self._chapter_model

    chapterListModel = Property(QObject, get_chapter_list_model, constant=True)

    def get_book_count(self) -> int:
        return self._book_model.rowCount()

    bookCount = Property(int, get_book_count, notify=bookCountChanged)

    def get_is_empty(self) -> bool:
        # D05 §62 书架无作品: shown only when the shelf has no book at all.
        return not self._library.list_books()

    isEmpty = Property(bool, get_is_empty, notify=bookCountChanged)

    def get_selected_book(self) -> dict:
        return self._selected_book

    selectedBook = Property("QVariantMap", get_selected_book, notify=selectedBookChanged)

    def get_search_text(self) -> str:
        return self._search_text

    def set_search_text(self, text: str) -> None:
        if self._search_text != text:
            self._search_text = text
            self.searchTextChanged.emit()
            self._apply_books()

    searchText = Property(str, get_search_text, set_search_text, notify=searchTextChanged)

    def get_archived_filter(self) -> bool:
        return self._archived_filter

    def set_archived_filter(self, enabled: bool) -> None:
        if self._archived_filter != bool(enabled):
            self._archived_filter = bool(enabled)
            self.archivedFilterChanged.emit()
            self._apply_books()

    archivedFilter = Property(
        bool, get_archived_filter, set_archived_filter, notify=archivedFilterChanged
    )

    def get_favorites_only(self) -> bool:
        return self._favorites_only

    def set_favorites_only(self, enabled: bool) -> None:
        if self._favorites_only != bool(enabled):
            self._favorites_only = bool(enabled)
            self.favoritesOnlyChanged.emit()
            self._apply_books()

    favoritesOnly = Property(
        bool, get_favorites_only, set_favorites_only, notify=favoritesOnlyChanged
    )

    @Slot(bool)
    def setFavoritesOnly(self, enabled: bool) -> None:
        self.set_favorites_only(enabled)

    def get_sort_by(self) -> str:
        return self._sort_by

    def set_sort_by(self, key: str) -> None:
        if key not in _SORT_KEYS:
            raise ValueError(f"unknown sort key: {key!r}")
        if self._sort_by != key:
            self._sort_by = key
            self.sortByChanged.emit()
            self._apply_books()

    sortBy = Property(str, get_sort_by, set_sort_by, notify=sortByChanged)

    def get_view_mode(self) -> str:
        return self._view_mode

    def set_view_mode(self, mode: str) -> None:
        if mode not in ("grid", "list"):
            raise ValueError(f"unknown view mode: {mode!r}")
        if self._view_mode != mode:
            self._view_mode = mode
            self.viewModeChanged.emit()

    viewMode = Property(str, get_view_mode, set_view_mode, notify=viewModeChanged)

    def get_import_summary(self) -> str:
        return self._import_summary

    importSummary = Property(
        str, get_import_summary, notify=importSummaryChanged
    )

    def get_navigation(self) -> QObject:
        return self._navigation

    navigation = Property(QObject, get_navigation, constant=True)

    # ------------------------------------------------------------------
    # QML slots wrapping the property setters
    # ------------------------------------------------------------------

    @Slot(str)
    def setSearchText(self, text: str) -> None:
        self.set_search_text(text)

    @Slot(bool)
    def setArchivedFilter(self, enabled: bool) -> None:
        self.set_archived_filter(enabled)

    @Slot(str)
    def setSortBy(self, key: str) -> None:
        self.set_sort_by(key)

    @Slot(str)
    def setViewMode(self, mode: str) -> None:
        self.set_view_mode(mode)

    # ------------------------------------------------------------------
    # shelf refresh / selection
    # ------------------------------------------------------------------

    @Slot()
    def refreshBooks(self) -> None:
        self._apply_books()
        self.bookCountChanged.emit()
        if self._selected_book_id is not None:
            self._refresh_selection(self._selected_book_id)

    def _apply_books(self) -> None:
        books = self._library.list_books()
        if self._archived_filter:
            books = [book for book in books if book.is_archived]
        else:
            books = [book for book in books if not book.is_archived]
        if self._favorites_only:
            books = [book for book in books if book.is_favorite]
        if self._search_text:
            needle = self._search_text.casefold()
            books = [
                book
                for book in books
                if needle in book.title.casefold()
                or needle in (book.original_title or "").casefold()
            ]
        books = sorted(books, key=self._sort_key)
        self._book_model.set_books([self._book_row(book) for book in books])

    def _sort_key(self, book):
        if self._sort_by == "title":
            return (0, book.title.casefold())
        # recent: last_opened_at desc, books never opened last
        return (1, "") if book.last_opened_at is None else (0, _invert(book.last_opened_at))

    @staticmethod
    def _book_row(book) -> dict:
        return {
            "book_id": book.book_id,
            "title": book.title,
            "original_title": book.original_title,
            "is_favorite": book.is_favorite,
            "is_archived": book.is_archived,
            # QML delegates bind strings: a raw datetime arrives as
            # undefined in QML, so expose ISO text ("" when never opened).
            "last_opened_at": (
                book.last_opened_at.isoformat() if book.last_opened_at else ""
            ),
            # no reading-progress field exists yet (TASK-007); render "—"
            "progress": None,
        }

    @Slot(str)
    def selectBook(self, book_id: str) -> None:
        self._refresh_selection(book_id)

    def _refresh_selection(self, book_id: str) -> None:
        book = self._library.get_book(book_id)  # raises if missing/deleted
        self._selected_book_id = book_id
        self._selected_book = {
            "book_id": book.book_id,
            "title": book.title,
            "original_title": book.original_title,
            "author": book.author,
            "description": book.description,
            "is_favorite": book.is_favorite,
            "is_archived": book.is_archived,
            "last_opened_at": (
                book.last_opened_at.isoformat() if book.last_opened_at else ""
            ),
            "progress": None,  # D05 §7.1 阅读进度 — 字段未落地，诚实显示
            "tags": [tag.name for tag in self._library.tags_of_book(book_id)],
        }
        self._chapter_model.set_chapters(
            self._chapter_rows(self._library.list_chapters(book_id))
        )
        self.selectedBookChanged.emit()

    @staticmethod
    def _chapter_rows(chapters) -> list[dict]:
        return [
            {
                "chapter_id": chapter.chapter_id,
                "chapter_number": chapter.chapter_number,
                "title": chapter.title,
                "chapter_type": chapter.chapter_type.value,
                "reading_direction": chapter.reading_direction.value,
                # page counts arrive with the page slice; 0 = unknown
                "page_count": 0,
            }
            for chapter in chapters
        ]

    # ------------------------------------------------------------------
    # CRUD entry points (D05 §8)
    # ------------------------------------------------------------------

    @Slot(str, str, result="QVariantMap")
    def createBook(self, title: str, original_title: str = "") -> dict:
        book = self._library.create_book(title, original_title=original_title)
        self.refreshBooks()
        return {"book_id": book.book_id, "title": book.title}

    @Slot(str)
    def deleteBook(self, book_id: str) -> None:
        self._library.delete_book(book_id)
        if self._selected_book_id == book_id:
            self._selected_book_id = None
            self._selected_book = {}
            self._chapter_model.set_chapters([])
            self.selectedBookChanged.emit()
        self.refreshBooks()

    @Slot(str, bool)
    def setFavorite(self, book_id: str, favorite: bool) -> None:
        self._library.set_favorite(book_id, favorite)
        self.refreshBooks()

    @Slot(str, bool)
    def setArchived(self, book_id: str, archived: bool) -> None:
        self._library.set_archived(book_id, archived)
        self.refreshBooks()

    @Slot(str, str, str, result="QVariantMap")
    def createChapter(self, book_id: str, title: str, chapter_number: str = "") -> dict:
        chapter = self._library.create_chapter(
            book_id, title, chapter_number=chapter_number
        )
        if self._selected_book_id == book_id:
            self._chapter_model.set_chapters(
                self._chapter_rows(self._library.list_chapters(book_id))
            )
        return {"chapter_id": chapter.chapter_id, "title": chapter.title}

    @Slot(str)
    def deleteChapter(self, chapter_id: str) -> None:
        chapter = self._library.get_chapter(chapter_id)
        book_id = chapter.book_id
        self._library.delete_chapter(chapter_id)
        if self._selected_book_id == book_id:
            self._chapter_model.set_chapters(
                self._chapter_rows(self._library.list_chapters(book_id))
            )

    # ------------------------------------------------------------------
    # import entry (D05 §7.1 导入)
    # ------------------------------------------------------------------

    def importPages(self, chapter_id: str, sources: list[ImportSource]):
        """Delegates to the injected import use case and surfaces a short
        human summary; the caller owns file selection dialogs."""
        self._library.get_chapter(chapter_id)  # unknown chapter → error
        report = self._importer.import_files(chapter_id, list(sources))
        self._import_summary = (
            f"导入 {len(report.imported)} 页，"
            f"跳过 {len(report.skipped_duplicates)} 个重复，"
            f"失败 {len(report.failed)} 个"
        )
        self.importSummaryChanged.emit()
        return report

    @Slot(str, "QVariantList", result="QVariantMap")
    def importFilesFromUrls(self, chapter_id: str, urls: list) -> dict:
        """QML import entry: local file URLs → ImportSource (bytes read via
        a data provider; the source file is only ever read, TASK-007 D07
        §37). Returns a QML-friendly summary map."""
        self._library.get_chapter(chapter_id)  # unknown chapter → error
        sources = [
            ImportSource(
                filename=Path(url.toLocalFile()).name,
                data_provider=lambda path=Path(url.toLocalFile()): path.read_bytes(),
            )
            for url in urls
        ]
        report = self._importer.import_files(chapter_id, sources)
        return {
            "imported": len(report.imported),
            "skipped": len(report.skipped_duplicates),
            "failed": len(report.failed),
            "summary": self._format_summary(report),
        }

    @Slot(str, list)
    def importDocumentsFromUrls(self, chapter_id: str, urls: list) -> dict:
        """QML entry for document imports (PDF; TASK-023). Same URL → bytes
        discipline as image import; MOBI/unknown formats fail typed as
        ``UNSUPPORTED_FORMAT`` inside the report. Requires the assembly to
        have injected a document importer."""
        if self._document_importer is None:
            return {"imported": 0, "skipped": 0, "failed": 0, "summary": "未启用文档导入"}
        self._library.get_chapter(chapter_id)  # unknown chapter → error
        sources = [
            ImportSource(
                filename=Path(url.toLocalFile()).name,
                data_provider=lambda path=Path(url.toLocalFile()): path.read_bytes(),
            )
            for url in urls
        ]
        report = self._document_importer.import_documents(chapter_id, sources)
        return {
            "imported": len(report.imported),
            "skipped": len(report.skipped_duplicates),
            "failed": len(report.failed),
            "summary": self._format_summary(report),
        }

    @staticmethod
    def _format_summary(report) -> str:
        return (
            f"导入 {len(report.imported)} 页，"
            f"跳过 {len(report.skipped_duplicates)} 个重复，"
            f"失败 {len(report.failed)} 个"
        )

    # ------------------------------------------------------------------
    # shelf → workbench / reader (D05 §8, §67)
    # ------------------------------------------------------------------

    @Slot(str)
    def enterTranslation(self, chapter_id: str) -> None:
        chapter = self._library.get_chapter(chapter_id)
        if chapter.book_id != self._selected_book_id:
            raise ValueError("select the chapter's book before entering the workbench")
        self._navigation.enterWorkbench(chapter.book_id, chapter_id)

    @Slot(str)
    def enterReading(self, chapter_id: str) -> None:
        chapter = self._library.get_chapter(chapter_id)
        if chapter.book_id != self._selected_book_id:
            raise ValueError("select the chapter's book before entering the reader")
        self._navigation.enterReader(chapter.book_id, chapter_id)


def _invert(text: str) -> str:
    """Sort lexicographically-descending without a reverse flag: ISO-ish
    timestamps inverted per character keep 'recent first' stable."""
    return "".join(chr(0x10FFFF - ord(ch)) for ch in text)
