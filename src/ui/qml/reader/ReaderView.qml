import QtQuick
import QtQuick.Controls
import "../common"

Rectangle {
    id: reader
    objectName: "readerView"
    color: "#f5f5f4"
    property var model: (typeof readerViewModel !== "undefined" ? readerViewModel : null)

    Column {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 8
        Row {
            spacing: 8
            Button { text: "Original"; enabled: reader.model !== null; onClicked: reader.model.setMode("original") }
            Button { text: "Translated"; enabled: reader.model !== null; onClicked: reader.model.setMode("translated") }
            Button { text: "RTL"; enabled: reader.model !== null; onClicked: reader.model.setDirection("rtl") }
            Button { text: "LTR"; enabled: reader.model !== null; onClicked: reader.model.setDirection("ltr") }
        }
        // stale / missing translated input is surfaced by the ViewModel.
        Label { text: reader.model ? reader.model.statusMessage : "尚未选择阅读章节"; color: "#9a3412"; visible: text !== "" }
        Image { objectName: "readerPage"; source: reader.model ? reader.model.sourcePath : ""; fillMode: Image.PreserveAspectFit; asynchronous: true; width: parent.width; height: parent.height - 72 }
        Button { text: "下一页"; enabled: reader.model !== null; onClicked: reader.model.nextPage() }
    }
}
