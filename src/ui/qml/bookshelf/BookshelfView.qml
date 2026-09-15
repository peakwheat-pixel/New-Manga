import QtQuick
import QtQuick.Controls
import QtQuick.Dialogs
import "../common"

// D05 §7 bookshelf layout: toolbar on top, book grid/list left, fixed
// BookDetailPanel right, D05 §62 empty state when the shelf is empty.
Rectangle {
    id: bookshelf
    objectName: "bookshelfView"
    color: "#f5f5f4"

    property var shelf: bookshelfViewModel

    BookshelfToolbar {
        id: toolbarArea
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        onCreateBookRequested: newBookDialog.open()
        onImportRequested: {
            if (detailArea.chapters.currentChapterId !== "") {
                importDialog.targetChapterId = detailArea.chapters.currentChapterId
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
        anchors.margins: 8

        Item {
            id: shelfArea
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.left: parent.left
            anchors.right: detailArea.left
            anchors.rightMargin: 8

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
            width: 320
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
