import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../theme"

// Shared chapter entry point for Reader and Workbench. It only consumes the
// already-published bookshelf ViewModel; no page or service is constructed.
Popup {
    id: root
    objectName: root.action === "workbench"
                ? "workbenchChapterPicker" : "readerChapterPicker"
    property var shelf: null
    property string action: "reader"

    readonly property bool hasBooks: shelf !== null && shelf.bookCount > 0
    readonly property bool hasChapters: chapterPickerChapterList.count > 0

    modal: true
    focus: true
    width: 480
    height: 320
    closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside
    anchors.centerIn: Overlay.overlay
    palette.window: Tokens.bgPanel
    palette.windowText: Tokens.ink
    palette.text: Tokens.ink
    // REPAIR-13 R-13-1: native-style surfaces are light and ignore QML
    // customization, so the light `ink` button labels were unreadable.
    // `ink-inv` is the F token for text on inverted (light) surfaces.
    palette.buttonText: Tokens.inkInv

    Accessible.name: "选择作品和章节"

    Keys.onEscapePressed: function(event) {
        close();
        event.accepted = true;
    }

    function syncBook() {
        if (shelf === null || chapterPickerBookList.currentValue === undefined
                || chapterPickerBookList.currentValue === "")
            return;
        shelf.selectBook(String(chapterPickerBookList.currentValue));
    }

    function acceptSelection() {
        if (shelf === null || !hasChapters
                || chapterPickerChapterList.currentValue === undefined)
            return;
        var chapterId = String(chapterPickerChapterList.currentValue);
        if (action === "workbench")
            shelf.enterTranslation(chapterId);
        else
            shelf.enterReading(chapterId);
        close();
    }

    onOpened: {
        if (hasBooks && chapterPickerBookList.currentIndex < 0)
            chapterPickerBookList.currentIndex = 0;
        syncBook();
        if (hasChapters && chapterPickerChapterList.currentIndex < 0)
            chapterPickerChapterList.currentIndex = 0;
    }

    background: Rectangle {
        color: Tokens.bgPanel
        border.color: Tokens.divider
        radius: Tokens.radMd
    }

    contentItem: ColumnLayout {
        anchors.fill: parent
        anchors.margins: Tokens.padPage
        spacing: Tokens.gap

        Label {
            text: root.action === "workbench" ? "选择工作台章节" : "选择阅读章节"
            font.pixelSize: Tokens.fsSub
            font.weight: Font.DemiBold
            color: Tokens.ink
            Accessible.name: text
        }

        Label {
            text: "作品"
            font.pixelSize: Tokens.fsSm
            color: Tokens.ink3
        }
        ComboBox {
            id: chapterPickerBookList
            objectName: "chapterPickerBookList"
            Layout.fillWidth: true
            model: root.shelf !== null ? root.shelf.bookListModel : null
            textRole: "title"
            valueRole: "bookId"
            // The native ComboBox paints its display text with the *text*
            // role on a light system surface, so this must be ink-inv too.
            palette.text: Tokens.inkInv
            palette.buttonText: Tokens.inkInv
            contentItem: Text {
                leftPadding: Tokens.gap / 2
                rightPadding: Tokens.gap * 2
                text: chapterPickerBookList.displayText
                color: Tokens.ink
                verticalAlignment: Text.AlignVCenter
                elide: Text.ElideRight
            }
            indicator: Label {
                x: parent.width - width - Tokens.gap / 2
                anchors.verticalCenter: parent.verticalCenter
                text: "⌄"
                color: Tokens.ink
            }
            Accessible.name: "作品列表"
            onCurrentIndexChanged: root.syncBook()
            onCurrentValueChanged: root.syncBook()
        }

        Label {
            text: "章节"
            font.pixelSize: Tokens.fsSm
            color: Tokens.ink3
        }
        ComboBox {
            id: chapterPickerChapterList
            objectName: "chapterPickerChapterList"
            Layout.fillWidth: true
            model: root.shelf !== null ? root.shelf.chapterListModel : null
            textRole: "title"
            valueRole: "chapterId"
            // The native ComboBox paints its display text with the *text*
            // role on a light system surface, so this must be ink-inv too.
            palette.text: Tokens.inkInv
            palette.buttonText: Tokens.inkInv
            contentItem: Text {
                leftPadding: Tokens.gap / 2
                rightPadding: Tokens.gap * 2
                text: chapterPickerChapterList.displayText
                color: Tokens.ink
                verticalAlignment: Text.AlignVCenter
                elide: Text.ElideRight
            }
            indicator: Label {
                x: parent.width - width - Tokens.gap / 2
                anchors.verticalCenter: parent.verticalCenter
                text: "⌄"
                color: Tokens.ink
            }
            Accessible.name: "章节列表"
        }

        Label {
            objectName: "chapterPickerEmpty"
            Layout.fillWidth: true
            visible: !root.hasChapters
            text: root.hasBooks ? "该作品暂无章节" : "暂无可选择的作品"
            color: Tokens.ink3
            font.pixelSize: Tokens.fsSm
        }

        RowLayout {
            Layout.fillWidth: true
            Layout.alignment: Qt.AlignRight
            spacing: Tokens.gap

            Button {
                objectName: "chapterPickerCancel"
                text: "取消"
                Accessible.name: "取消选择"
                onClicked: root.close()
            }
            Button {
                objectName: "chapterPickerAccept"
                text: root.action === "workbench" ? "进入工作台" : "进入阅读"
                enabled: root.hasChapters && chapterPickerChapterList.currentIndex >= 0
                Accessible.name: text
                onClicked: root.acceptSelection()
            }
        }
    }
}
