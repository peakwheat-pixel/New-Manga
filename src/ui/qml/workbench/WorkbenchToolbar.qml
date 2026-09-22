import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../theme"

// D05 §17 Workbench Toolbar: Book/Chapter context, page navigation,
// viewer mode switch, and the batch command entries (D05 §56).
Rectangle {
    id: toolbar
    objectName: "workbenchToolbar"
    color: Tokens.bgPanel

    property string bookTitle: ""
    property string chapterTitle: ""
    property string viewerMode: "original"
    property bool hasSelection: false
    property bool runActive: false

    signal previousPageClicked()
    signal nextPageClicked()
    signal viewerModeClicked(string mode)
    signal translateAllClicked()
    signal translateUntranslatedClicked()
    signal translateSelectedClicked()

    implicitHeight: Tokens.tbH

    RowLayout {
        anchors.fill: parent
        anchors.margins: Tokens.gap
        spacing: Tokens.gap

        Label {
            objectName: "toolbarContext"
            text: toolbar.bookTitle + (toolbar.chapterTitle ? " · " + toolbar.chapterTitle : "")
            font.bold: true
            color: Tokens.ink
            font.pixelSize: Tokens.fsSub
        }

        Button { objectName: "toolbarPrevPage"; flat: true; text: "上一页"; onClicked: toolbar.previousPageClicked() }
        Button { objectName: "toolbarNextPage"; flat: true; text: "下一页"; onClicked: toolbar.nextPageClicked() }

        Rectangle { width: 1; height: 24; color: Tokens.divider }

        // D05 §20.1 viewer modes.
        RowLayout {
            spacing: 2
            Button {
                objectName: "modeOriginal"
                flat: true
                text: "原图"
                highlighted: toolbar.viewerMode === "original"
                onClicked: toolbar.viewerModeClicked("original")
            }
            Button {
                objectName: "modeClean"
                flat: true
                text: "修复图"
                highlighted: toolbar.viewerMode === "clean"
                onClicked: toolbar.viewerModeClicked("clean")
            }
            Button {
                objectName: "modeTranslated"
                flat: true
                text: "译图"
                highlighted: toolbar.viewerMode === "translated"
                onClicked: toolbar.viewerModeClicked("translated")
            }
            Button {
                objectName: "modeCompare"
                flat: true
                text: "对比"
                highlighted: toolbar.viewerMode === "compare"
                onClicked: toolbar.viewerModeClicked("compare")
            }
        }

        Item { Layout.fillWidth: true }

        // D05 §56 batch command entries; disabled while a run executes.
        Button {
            objectName: "cmdTranslateAll"
            text: "全部翻译"
            enabled: !toolbar.runActive
            onClicked: toolbar.translateAllClicked()
        }
        Button {
            objectName: "cmdTranslateUntranslated"
            text: "全部翻译（跳过已翻译）"
            enabled: !toolbar.runActive
            onClicked: toolbar.translateUntranslatedClicked()
        }
        Button {
            objectName: "cmdTranslateSelected"
            text: "翻译所选"
            enabled: !toolbar.runActive && toolbar.hasSelection
            onClicked: toolbar.translateSelectedClicked()
        }
    }
}
