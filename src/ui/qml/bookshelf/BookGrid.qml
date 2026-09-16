import QtQuick
import QtQuick.Controls

// D05 §7.1 BookGrid / BookList. Both views stay mounted and viewMode only
// picks the visible one. Deliberately Loader-free: Loader items are
// JavaScript-owned and the QML GC can collect them while Python-side
// wrappers still reference them (observed as use-after-free in tests).
FocusScope {
    id: shelfList
    objectName: "bookGrid"

    property var shelf: bookshelfViewModel
    signal bookSelected(string bookId)

    GridView {
        objectName: "bookGridView"
        anchors.fill: parent
        visible: shelf.viewMode === "grid"
        clip: true
        cellWidth: 168
        cellHeight: 210
        model: shelf.bookListModel
        delegate: BookCard {
            width: GridView.view.cellWidth - 8
            height: GridView.view.cellHeight - 8
            x: 4; y: 4
            bookId: model.bookId
            title: model.title
            originalTitle: model.originalTitle
            isFavorite: model.isFavorite
            isArchived: model.isArchived
            lastOpenedAt: model.lastOpenedAt
            progress: model.progress
            onCardActivated: function(bookId) { shelfList.bookSelected(bookId) }
            onFavoriteToggled: function(bookId, favorite) {
                shelf.setFavorite(bookId, favorite)
            }
        }
    }

    ListView {
        objectName: "bookListView"
        anchors.fill: parent
        visible: shelf.viewMode === "list"
        clip: true
        spacing: 4
        model: shelf.bookListModel
        delegate: BookCard {
            width: ListView.view.width
            height: 64
            bookId: model.bookId
            title: model.title
            originalTitle: model.originalTitle
            isFavorite: model.isFavorite
            isArchived: model.isArchived
            lastOpenedAt: model.lastOpenedAt
            progress: model.progress
            onCardActivated: function(bookId) { shelfList.bookSelected(bookId) }
            onFavoriteToggled: function(bookId, favorite) {
                shelf.setFavorite(bookId, favorite)
            }
        }
    }
}
