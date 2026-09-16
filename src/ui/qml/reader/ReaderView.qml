import QtQuick
import QtQuick.Controls
import "../common"

// D05 §37 ReaderView is a TASK-015 slice; this stage delivers the
// skeleton with the D05 §62 reader empty state only.
Rectangle {
    id: reader
    objectName: "readerView"
    color: "#f5f5f4"

    EmptyState {
        anchors.centerIn: parent
        title: "尚未选择阅读章节"
        description: "阅读器将提供 Original / Translated 与 RTL / LTR / Webtoon 阅读"
        Button {
            objectName: "readerPickChapter"
            text: "选择章节"
            enabled: false  // 章节选择悬浮窗属 TASK-015
        }
    }
}
