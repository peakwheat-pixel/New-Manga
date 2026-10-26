import QtQuick
import QtQuick.Controls
import QtQuick.Dialogs
import "../common"
import "../theme"

// D05 §7 bookshelf layout: toolbar on top, book grid/list left, fixed
// BookDetailPanel right, D05 §62 empty state when the shelf is empty.
Rectangle {
    id: bookshelf
    objectName: "bookshelfView"
    color: Tokens.bgPage

    property var shelf: bookshelfViewModel

    BookshelfToolbar {
        id: toolbarArea
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        // REPAIR-13 R13-AC1: read the selection through the panel's public
        // alias; the old `detailArea.chapters.currentChapterId` reached into
        // an inner QML id and threw a TypeError on every import click.
        readonly property bool chapterSelected:
            detailArea.currentChapterId !== ""
        importReady: chapterSelected
        importHint: {
            if (chapterSelected)
                return ""
            var book = shelf !== null ? shelf.selectedBook : null
            var bookSelected = book !== null && book !== undefined
                               && book.book_id !== undefined
                               && book.book_id !== ""
            return bookSelected
                ? "已选作品还未选择章节：请在右侧新建或点击章节后再导入页面"
                : "先新建作品并选择章节，再导入页面"
        }
        onCreateBookRequested: newBookDialog.open()
        onImportRequested: {
            if (chapterSelected) {
                importDialog.targetChapterId = detailArea.currentChapterId
                importDialog.open()
            }
        }
    }

    Item {
        id: contentArea
        anchors.top: toolbarArea.bottom
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.margins: Tokens.padPage

        Item {
            id: shelfArea
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.left: parent.left
            anchors.right: detailArea.left
            anchors.rightMargin: Tokens.gap

            EmptyState {
                objectName: "bookshelfEmptyState"
                anchors.centerIn: parent
                visible: shelf.isEmpty
                title: "还没有作品"
                Button {
                    objectName: "emptyCreateBook"
                    text: "新建作品"
                    onClicked: newBookDialog.open()
                }
                Button {
                    objectName: "emptyImport"
                    text: "导入作品"
                    enabled: false
                }
            }

            BookGrid {
                anchors.fill: parent
                visible: !shelf.isEmpty
                onBookSelected: function(bookId) { shelf.selectBook(bookId) }
            }
        }

        BookDetailPanel {
            id: detailArea
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.right: parent.right
            width: Tokens.detW
        }
    }

    // D05 §8 新建作品 → Modal.
    Dialog {
        id: newBookDialog
        objectName: "newBookDialog"
        modal: true
        title: "新建作品"
        anchors.centerIn: parent
        width: 320
        standardButtons: Dialog.Cancel | Dialog.Ok

        Column {
            spacing: 6
            TextField {
                id: newBookTitle
                objectName: "newBookTitleInput"
                placeholderText: "作品标题"
                width: 260
            }
            TextField {
                id: newBookOriginal
                objectName: "newBookOriginalInput"
                placeholderText: "原始标题（可选）"
                width: 260
            }
        }
        onAccepted: shelf.createBook(newBookTitle.text, newBookOriginal.text)
    }

    // D05 §8 导入 entry: multi-file picker feeding the TASK-007 import use
    // case through bookshelfViewModel.importFilesFromUrls.
    FileDialog {
        id: importDialog
        objectName: "importDialog"
        property string targetChapterId: ""
        fileMode: FileDialog.OpenFiles
        nameFilters: ["图片文件 (*.png *.jpg *.jpeg *.webp *.bmp)"]
        onAccepted: {
            shelf.importFilesFromUrls(targetChapterId, selectedFiles)
            importDialog.close()
        }
    }
}
