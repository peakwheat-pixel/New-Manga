"""REPAIR-13 regression guards for the bookshelf import entry.

Build 3's Sandbox run blocked AC3 twice over: every click on 导入 raised
``BookshelfView.qml:23: TypeError: Cannot read property 'currentChapterId'
of undefined`` (the handler reached into BookDetailPanel's *inner* QML id
`chapters`, which is invisible across components) and the button gave no
feedback while no chapter was selected. The fix exposes
``BookDetailPanel.currentChapterId`` as a readonly alias and binds the
toolbar button's enabled state plus a visible hint to the selection.

These tests load the real BookshelfView.qml with the real ViewModels the
way bootstrap publishes them (context properties) and guard:

- the alias follows a real chapter-row click,
- the import button is disabled with a visible hint until a chapter is
  selected and flips to enabled after,
- emitting ``importRequested`` with no chapter selected raises no QML
  TypeError and never opens the file dialog (message-handler probe,
  discriminating: the pre-repair handler fails it),
- the viewmodel entry receives the selected chapter id and the picked
  URLs (StubImporter records the call; real managed-copy byte behavior
  is covered by the live probe and the Sandbox rerun).
"""

from __future__ import annotations

import helpers  # noqa: F401  (sys.path injection; SRC_ROOT below)
from fakes import InMemoryLibraryRepository, StubImporter

import pytest

from PySide6.QtCore import QPoint, QUrl, Qt, QObject, qInstallMessageHandler
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlComponent, QQmlEngine
from PySide6.QtQuick import QQuickItem, QQuickWindow  # noqa: F401
from PySide6.QtTest import QTest

from application.importing.images.ports import ImportReport
from application.library.service import LibraryService
from ui.viewmodels.bookshelf.viewmodel import BookshelfViewModel
from ui.viewmodels.navigation.viewmodel import NavigationViewModel

pytestmark = pytest.mark.usefixtures("qapp")

SRC_QML = helpers.SRC_ROOT / "ui" / "qml" / "bookshelf" / "BookshelfView.qml"

HOST_QML = """
import QtQuick
import QtQuick.Controls
ApplicationWindow {
    objectName: "testWindow"
    visible: true
    width: 1280
    height: 800
    BookshelfView { anchors.fill: parent }
}
"""


def find_one(root, object_name):
    listed = root.findChildren(QObject, object_name)
    assert listed, f"expected an item named {object_name!r}"
    return listed[0]


def click_qml_button(button):
    meta = button.metaObject()
    index = meta.indexOfMethod("clicked()")
    assert index >= 0, "clicked() not found on button"
    meta.method(index).invoke(button)


class Harness:
    def __init__(self, engine, window, root, shelf, library, importer):
        self.engine = engine
        self.window = window
        self.root = root
        self.shelf = shelf
        self.library = library
        self.importer = importer


@pytest.fixture()
def harness(qapp):
    library = LibraryService(InMemoryLibraryRepository())
    nav_vm = NavigationViewModel()
    importer = StubImporter()
    shelf_vm = BookshelfViewModel(
        library=library, importer=importer, navigation=nav_vm
    )

    engine = QQmlEngine(None)
    engine.rootContext().setContextProperty("navigationViewModel", nav_vm)
    engine.rootContext().setContextProperty("bookshelfViewModel", shelf_vm)
    component = QQmlComponent(engine)
    component.setData(
        HOST_QML.encode(),
        QUrl.fromLocalFile(str(SRC_QML.parent / "_TestHost.qml")),
    )
    if not component.isReady():
        raise AssertionError(
            f"host failed to load: {[e.toString() for e in component.errors()]}"
        )
    window = component.create()
    assert window is not None
    qapp.processEvents()
    root = window.findChild(QObject, "bookshelfView")
    assert root is not None

    yield Harness(engine, window, root, shelf_vm, library, importer)

    window.deleteLater()
    engine.deleteLater()
    qapp.processEvents()


def _make_book_and_chapter(harness):
    book = harness.shelf.createBook("导入探针", "probe")
    chapter = harness.shelf.createChapter(book["book_id"], "第一章", "1")
    harness.shelf.selectBook(book["book_id"])
    QTest.qWait(300)
    return book["book_id"], chapter["chapter_id"]


def _click_chapter_row(harness):
    list_view = find_one(harness.root, "chapterListView")
    content = list_view.property("contentItem")
    rows = [
        child
        for child in content.childItems()
        if child.metaObject().className().startswith("QQuickRectangle")
    ]
    assert rows, "expected one chapter row"
    row = rows[0]
    pos = row.mapToScene(QPoint(30, int(row.height() // 2))).toPoint()
    QTest.mouseClick(harness.window, Qt.LeftButton, Qt.NoModifier, pos)
    QTest.qWait(100)


def test_import_entry_disabled_with_hint_before_selection(harness):
    btn = find_one(harness.root, "btnImport")
    hint = find_one(harness.root, "importHint")
    assert not btn.isEnabled(), "import must be disabled without a chapter"
    assert hint.isVisible(), "the disabled import must explain how to proceed"
    text = hint.property("text")
    assert "章节" in text, f"hint should mention the chapter prerequisite: {text!r}"


def test_current_chapter_alias_follows_row_click(harness):
    _, chapter_id = _make_book_and_chapter(harness)
    detail = find_one(harness.root, "bookDetailPanel")
    assert detail.property("currentChapterId") == "", "no row clicked yet"
    _click_chapter_row(harness)
    assert detail.property("currentChapterId") == chapter_id


def test_import_entry_enabled_after_row_click(harness):
    _make_book_and_chapter(harness)
    btn = find_one(harness.root, "btnImport")
    hint = find_one(harness.root, "importHint")
    assert not btn.isEnabled()
    _click_chapter_row(harness)
    assert btn.isEnabled(), "import unlocks once a chapter is selected"
    assert not hint.isVisible(), "the hint disappears once import is usable"


def test_import_requested_without_chapter_raises_no_qml_typeerror(harness):
    """Discriminating guard: the pre-repair handler threw
    ``Cannot read property 'currentChapterId' of undefined`` every time the
    toolbar emitted importRequested without a selection (31 occurrences in
    the Build 3 stderr). The message handler below must see no QML error."""
    toolbar = find_one(harness.root, "bookshelfToolbar")
    dialog = find_one(harness.root, "importDialog")
    messages: list[str] = []

    def capture(mode, context, message):
        messages.append(message)

    qInstallMessageHandler(capture)
    try:
        meta = toolbar.metaObject()
        index = meta.indexOfMethod("importRequested()")
        assert index >= 0, "importRequested() signal missing"
        for _ in range(3):
            meta.method(index).invoke(toolbar)
        QTest.qWait(100)
    finally:
        qInstallMessageHandler(None)

    errors = [m for m in messages if "TypeError" in m]
    assert not errors, f"QML TypeError on the import path: {errors}"
    assert not dialog.property("visible"), (
        "the file dialog must not open without a selected chapter"
    )


def test_import_flow_passes_selection_and_files_to_viewmodel(harness):
    _, chapter_id = _make_book_and_chapter(harness)
    _click_chapter_row(harness)

    report = ImportReport(
        chapter_id=chapter_id,
        imported=[object(), object()],
    )
    harness.importer._default_report = report

    summary = harness.shelf.importFilesFromUrls(
        chapter_id,
        [QUrl("file:///fixture-a.png"), QUrl("file:///fixture-b.png")],
    )
    assert summary["imported"] == 2
    assert len(harness.importer.calls) == 1
    call = harness.importer.calls[0]
    assert call["chapter_id"] == chapter_id
    assert [source.filename for source in call["sources"]] == [
        "fixture-a.png",
        "fixture-b.png",
    ]
