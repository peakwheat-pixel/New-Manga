"""QML shell load tests: AppShell + navigation + bookshelf end to end.

Loads ``src/ui/qml/shell/AppShell.qml`` inside an ApplicationWindow host
(never shown) with the real ViewModels published as context properties —
exactly the assembly bootstrap will perform — and asserts the D05 / AC
behavior: exactly four top-level entries (AC-NAV-002), bookshelf selected
at startup (AC-NAV-001), visibility-only page switching that never
destroys the shelf context (AC-NAV-003 / D05 §3.1), the D05 §62 empty
states, and the 新建作品 dialog flowing into the use cases.

Notes on the harness (PySide6 6.11 specific):
- ``QQmlComponent.status`` is a *method* here, not a property; the boolean
  ``isReady()/isError()`` predicates are the reliable gate.
- Repeater/ItemView delegate items and Loader items are not on the
  QObject tree the way declared items are (and Loader items are
  JS-owned), so assertions reference declared ``objectName`` items and
  ``Repeater.itemAt`` only. Runs on the default Windows platform: the
  offscreen platform ships no font database (see conftest).
"""

from __future__ import annotations

import helpers  # noqa: F401  (sys.path injection; SRC_ROOT below)
from fakes import InMemoryLibraryRepository, StubImporter

import pytest

from PySide6.QtCore import QObject, QUrl
from PySide6.QtQml import QQmlComponent, QQmlEngine
from PySide6.QtQuick import QQuickWindow  # noqa: F401  (registers QQuickItem* converters for itemAt)

SHELL_QML = helpers.SRC_ROOT / "ui" / "qml" / "shell" / "AppShell.qml"
PAGES = ("bookshelf", "workbench", "reader", "settings")

# AppShell's root is an Item; tests host it in an ApplicationWindow (never
# shown) so delegate creation and Popup overlays have a window. The base
# URL points into shell/ so the sibling `AppShell` type resolves by name.
HOST_QML = """
import QtQuick
import QtQuick.Controls
ApplicationWindow {
    objectName: "testWindow"
    width: 1280
    height: 800
    AppShell { anchors.fill: parent }
}
"""


def find_one(root, object_name):
    """Declared QML items are on the QObject tree under the window."""
    listed = root.findChildren(QObject, object_name)
    assert listed, f"expected an item named {object_name!r} in the shell"
    return listed[0]


def nav_buttons(shell):
    """The four rail buttons, via the visual tree. Repeater delegate items
    are not on the QObject tree, and ``Repeater.itemAt`` returns None
    through the python wrapper (PySide6 6.11); childItems() on the
    declared rail item is the reliable path."""
    rail = find_one(shell.root, "navRail")
    columns = [
        child
        for child in rail.childItems()
        if child.metaObject().className() == "QQuickColumn"
    ]
    assert len(columns) == 1, "expected one Column in the rail"
    buttons = [
        child
        for child in columns[0].childItems()
        if child.objectName().startswith("nav-")
    ]
    assert len(buttons) == len(PAGES), f"expected {len(PAGES)} rail buttons"
    # Visual order == Column order == Repeater order == D05 §3.1 order.
    return buttons


def click_button(button):
    """Emit AbstractButton.clicked through QMetaMethod (the wrapper is
    statically typed QQuickItem, so no .clicked descriptor exists)."""
    meta = button.metaObject()
    index = meta.indexOfMethod("clicked()")
    assert index >= 0, "clicked() not found on nav button"
    meta.method(index).invoke(button)


class ShellHarness:
    def __init__(self, engine, window, root, nav, shelf, library):
        self.engine = engine
        self.window = window
        self.root = root  # the appShell item
        self.nav = nav
        self.shelf = shelf
        self.library = library

    def page_visible(self, page_id):
        item = find_one(self.root, f"page-{page_id}")
        return bool(item.property("visible"))


@pytest.fixture()
def shell(qapp):
    from application.library.service import LibraryService
    from ui.viewmodels.bookshelf.viewmodel import BookshelfViewModel
    from ui.viewmodels.navigation.viewmodel import NavigationViewModel

    library = LibraryService(InMemoryLibraryRepository())
    nav_vm = NavigationViewModel()
    shelf_vm = BookshelfViewModel(
        library=library, importer=StubImporter(), navigation=nav_vm
    )

    engine = QQmlEngine(None)
    engine.rootContext().setContextProperty("navigationViewModel", nav_vm)
    engine.rootContext().setContextProperty("bookshelfViewModel", shelf_vm)
    component = QQmlComponent(engine)
    component.setData(
        HOST_QML.encode(), QUrl.fromLocalFile(str(SHELL_QML.parent / "_TestHost.qml"))
    )
    if not component.isReady():
        raise AssertionError(
            f"shell host failed to load: {[e.toString() for e in component.errors()]}"
        )
    window = component.create()
    assert window is not None
    qapp.processEvents()
    shell_item = window.findChild(QObject, "appShell")
    assert shell_item is not None

    harness = ShellHarness(engine, window, shell_item, nav_vm, shelf_vm, library)
    yield harness

    window.deleteLater()
    engine.deleteLater()
    qapp.processEvents()


def test_appshell_declares_exactly_four_top_level_pages(shell):
    buttons = nav_buttons(shell)
    assert [b.objectName() for b in buttons] == [f"nav-{p}" for p in PAGES]
    for page_id in PAGES:
        find_one(shell.root, f"page-{page_id}")


def test_startup_lands_on_bookshelf(shell):
    # AC-NAV-001: bookshelf selected, current page is BookshelfView.
    assert shell.nav.currentPage == "bookshelf"
    assert shell.page_visible("bookshelf") is True
    for page_id in ("workbench", "reader", "settings"):
        assert shell.page_visible(page_id) is False, page_id
    checked = [bool(b.property("checked")) for b in nav_buttons(shell)]
    assert checked == [True, False, False, False]


def test_rail_button_click_switches_page(shell):
    # AC-NAV-002 nav flow: the QML button's onClicked drives navigate().
    buttons = nav_buttons(shell)
    click_button(buttons[3])  # nav-settings
    assert shell.nav.currentPage == "settings"
    assert shell.page_visible("settings") is True
    assert shell.page_visible("bookshelf") is False
    assert [bool(b.property("checked")) for b in buttons] == [
        False, False, False, True,
    ]


def test_switching_pages_only_toggles_visibility_and_keeps_context(shell):
    # AC-NAV-003: shelf context survives settings → bookshelf; the pages are
    # never destroyed (D05 §3.1), so the models still hold their rows.
    book = shell.shelf.createBook("迷宫饭")
    shell.shelf.selectBook(book["book_id"])
    shell.shelf.createChapter(book["book_id"], "第1话", "1")

    shell.nav.navigate("settings")
    assert shell.page_visible("settings") is True
    assert shell.page_visible("bookshelf") is False
    shell.nav.navigate("bookshelf")
    assert shell.page_visible("bookshelf") is True

    grid_view = find_one(shell.root, "bookGridView")
    assert int(grid_view.property("count")) == 1
    chapter_view = find_one(shell.root, "chapterListView")
    assert int(chapter_view.property("count")) == 1


def test_shelf_and_detail_empty_states(shell):
    # D05 §62: 还没有作品 / 未选择作品.
    empty = find_one(shell.root, "bookshelfEmptyState")
    assert bool(empty.property("visible")) is True
    assert empty.property("title") == "还没有作品"
    find_one(shell.root, "emptyCreateBook")
    assert bool(find_one(shell.root, "detailEmptyState").property("visible")) is True


def test_creating_book_clears_empty_state_and_populates_grid(shell):
    empty = find_one(shell.root, "bookshelfEmptyState")
    grid_view = find_one(shell.root, "bookGridView")
    assert int(grid_view.property("count")) == 0
    assert bool(empty.property("visible")) is True

    shell.shelf.createBook("迷宫饭")

    assert int(grid_view.property("count")) == 1
    assert bool(empty.property("visible")) is False


def test_new_book_dialog_flow_creates_book(shell):
    # D05 §8 新建作品 → Modal → createBook use case, end to end through QML.
    toolbar = find_one(shell.root, "bookshelfToolbar")
    toolbar.createBookRequested.emit()
    dialog = find_one(shell.root, "newBookDialog")
    assert bool(dialog.property("visible")) is True

    find_one(shell.root, "newBookTitleInput").setProperty("text", "文豪野犬")
    find_one(shell.root, "newBookOriginalInput").setProperty(
        "text", "Bungo Stray Dogs"
    )
    dialog.accept()

    books = shell.library.list_books()
    assert len(books) == 1
    assert books[0].title == "文豪野犬"
    assert books[0].original_title == "Bungo Stray Dogs"


def test_enter_buttons_follow_chapter_selection(shell):
    # D05 §7.1: 进入翻译/进入阅读 only once a chapter row is selected; the
    # delegate's onClicked writes ChapterList.currentChapterId, and these
    # buttons are enabled by that binding.
    book = shell.shelf.createBook("测试书")
    shell.shelf.selectBook(book["book_id"])
    enter_translation = find_one(shell.root, "btnEnterTranslation")
    enter_reading = find_one(shell.root, "btnEnterReading")
    assert bool(enter_translation.property("enabled")) is False
    assert bool(enter_reading.property("enabled")) is False

    shell.shelf.createChapter(book["book_id"], "第1话", "1")
    chapter_view = find_one(shell.root, "chapterListView")
    assert int(chapter_view.property("count")) == 1

    chapter_list = find_one(shell.root, "chapterList")
    assert chapter_list.property("currentChapterId") == ""
    chapter_list.setProperty("currentChapterId", book["book_id"] + ":nope")
    assert bool(enter_translation.property("enabled")) is True
    assert bool(enter_reading.property("enabled")) is True


def test_view_mode_switch_keeps_model(shell):
    # D05 §7.1 Grid / List 切换 swaps visibility, the model stays mounted.
    shell.shelf.createBook("第一本")
    shell.shelf.createBook("第二本")
    grid_view = find_one(shell.root, "bookGridView")
    list_view = find_one(shell.root, "bookListView")
    assert bool(grid_view.property("visible")) is True
    assert bool(list_view.property("visible")) is False

    shell.shelf.setViewMode("list")

    assert bool(grid_view.property("visible")) is False
    assert bool(list_view.property("visible")) is True
    assert int(list_view.property("count")) == 2
    shell.shelf.setViewMode("grid")
    assert int(grid_view.property("count")) == 2


def test_workbench_and_reader_are_honest_skeletons(shell):
    # D05 §62: skeleton pages exist but their pick actions stay disabled
    # until TASK-013/015 deliver the floating pickers.
    shell.nav.navigate("workbench")
    pick = find_one(shell.root, "workbenchPickContext")
    assert bool(pick.property("enabled")) is False
    shell.nav.navigate("reader")
    pick = find_one(shell.root, "readerPickChapter")
    assert bool(pick.property("enabled")) is False


def test_settings_page_lists_twelve_fixed_categories(shell):
    # D05 §43.1: settings is one top-level page with 12 fixed categories.
    shell.nav.navigate("settings")
    category_list = find_one(shell.root, "settingsCategoryList")
    assert int(category_list.property("count")) == 12
