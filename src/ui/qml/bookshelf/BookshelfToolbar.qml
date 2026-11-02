import QtQuick
import QtQuick.Controls
import "../common"
import "../theme"

// D05 §7.1 BookshelfToolbar: 新建作品 / 导入 / 搜索 / 筛选(收藏·归档) /
// 排序 / Grid-List 切换. All state lives in bookshelfViewModel.
Rectangle {
    id: toolbar
    objectName: "bookshelfToolbar"
    color: Tokens.bgPanel
    height: Tokens.tbH

    property var shelf: bookshelfViewModel
    // REPAIR-13 R13-AC1: the import entry must not fail silently. The view
    // binds these — the button stays disabled with a visible reason until a
    // book and a chapter are selected.
    property bool importReady: false
    property string importHint: ""

    signal createBookRequested()
    signal importRequested()

    Row {
        anchors.left: parent.left
        anchors.verticalCenter: parent.verticalCenter
        anchors.margins: 8
        spacing: 8

        Button {
            objectName: "btnCreateBook"
            text: "新建作品"
            onClicked: toolbar.createBookRequested()
        }
        Button {
            objectName: "btnImport"
            text: "导入"
            enabled: toolbar.importReady
            onClicked: toolbar.importRequested()
        }
        Label {
            objectName: "importHint"
            text: toolbar.importHint
            visible: toolbar.importHint !== ""
            anchors.verticalCenter: parent.verticalCenter
            color: Tokens.ink3
            font.pixelSize: Tokens.fsSm
        }
        TextField {
            objectName: "searchField"
            placeholderText: "搜索作品…"
            width: 180
            onTextChanged: toolbar.shelf.setSearchText(text)
        }
        Button {
            objectName: "btnFavoritesFilter"
            text: "收藏"
            checkable: true
            checked: toolbar.shelf.favoritesOnly
            onClicked: toolbar.shelf.setFavoritesOnly(checked)
        }
        Button {
            objectName: "btnArchivedFilter"
            text: "归档"
            checkable: true
            checked: toolbar.shelf.archivedFilter
            onClicked: toolbar.shelf.setArchivedFilter(checked)
        }
        Button {
            objectName: "btnSort"
            text: toolbar.shelf.sortBy === "recent" ? "排序：最近" : "排序：标题"
            onClicked: toolbar.shelf.setSortBy(
                toolbar.shelf.sortBy === "recent" ? "title" : "recent")
        }
        Button {
            objectName: "btnViewMode"
            text: toolbar.shelf.viewMode === "grid" ? "列表" : "网格"
            onClicked: toolbar.shelf.setViewMode(
                toolbar.shelf.viewMode === "grid" ? "list" : "grid")
        }
    }
}
