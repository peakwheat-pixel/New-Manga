import QtQuick
import QtQuick.Controls
import "../theme"

// D05 §7.1 BookGrid / BookList. Both views stay mounted and viewMode only
// picks the visible one. Deliberately Loader-free: Loader items are
// JavaScript-owned and the QML GC can collect them while Python-side
// wrappers still reference them (observed as use-after-free in tests).
//
// T2.1.1: the accepted bookshelf card width is Tokens.cardW (158px, contract
// DDR-10), not the pre-F 168px cell. The gutter stays local to the grid so
// the card itself is the token, not the cell around it.
FocusScope {
    id: shelfList
    objectName: "bookGrid"

    property var shelf: bookshelfViewModel
    signal bookSelected(string bookId)

    readonly property int cardGutter: 4

    GridView {
        objectName: "bookGridView"
        anchors.fill: parent
        visible: shelf.viewMode === "grid"
        clip: true
        cellWidth: Tokens.cardW + shelfList.cardGutter * 2
        cellHeight: Tokens.cardW * 1.25 + shelfList.cardGutter * 2
        model: shelf.bookListModel
        delegate: BookCard {
            width: Tokens.cardW
            height: Tokens.cardW * 1.25
            x: shelfList.cardGutter; y: shelfList.cardGutter
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
        spacing: shelfList.cardGutter
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
