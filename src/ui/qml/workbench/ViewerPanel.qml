import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

// D05 §20: center Viewer/Canvas — Original / Clean / Translated / Compare.
// Compare shows original and translated side by side (D05 §20.1). Image
// data comes from the viewmodel (managed-copy URLs); modes without a
// produced artifact in this slice render an honest placeholder instead of
// a fake image.
Rectangle {
    id: viewer
    objectName: "viewerPanel"
    color: "#e7e5e4"

    property string imageUrl: ""
    property string translatedUrl: ""
    property string pageName: ""
    property string mode: "original"

    Label {
        anchors.centerIn: parent
        visible: viewer.pageName === ""
        objectName: "viewerEmpty"
        text: "在左侧选择一个 Page"
        color: "#78716c"
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 12
        spacing: 8
        visible: viewer.pageName !== ""

        RowLayout {
            Layout.fillWidth: true
            Label {
                objectName: "viewerPageName"
                text: viewer.pageName
                font.bold: true
                color: "#44403c"
            }
            Item { Layout.fillWidth: true }
            Label {
                objectName: "viewerModeLabel"
                text: { var names = { original: "原图", clean: "修复图",
                    translated: "译图", compare: "对比" };
                    return names[viewer.mode] || viewer.mode; }
                color: "#78716c"
            }
        }

        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 8

            // Original pane (also the single-image pane for non-compare).
            Rectangle {
                objectName: "viewerImagePane"
                Layout.fillWidth: viewer.mode !== "compare"
                Layout.fillHeight: true
                color: "#ffffff"
                border.color: "#d6d3d1"
                Image {
                    id: mainImage
                    anchors.fill: parent
                    anchors.margins: 4
                    source: viewer.imageUrl
                    fillMode: Image.PreserveAspectFit
                    asynchronous: true
                }
                Label {
                    anchors.centerIn: parent
                    visible: mainImage.status === Image.Null || mainImage.source === ""
                    text: viewer.mode === "original" ? "原图不可用" : "该模式暂无产物"
                    color: "#a8a29e"
                }
                Label {
                    anchors.bottom: parent.bottom
                    anchors.left: parent.left
                    anchors.margins: 6
                    visible: viewer.mode === "compare"
                    text: "原图"
                    color: "#78716c"
                }
            }

            // Compare pane (D05 §20.1 左右双图).
            Rectangle {
                objectName: "viewerComparePane"
                Layout.fillWidth: true
                Layout.fillHeight: true
                visible: viewer.mode === "compare"
                color: "#ffffff"
                border.color: "#d6d3d1"
                Image {
                    anchors.fill: parent
                    anchors.margins: 4
                    source: viewer.translatedUrl
                    fillMode: Image.PreserveAspectFit
                    asynchronous: true
                }
                Label {
                    anchors.centerIn: parent
                    visible: viewer.translatedUrl === ""
                    text: "译图尚未产出"
                    color: "#a8a29e"
                }
                Label {
                    anchors.bottom: parent.bottom
                    anchors.left: parent.left
                    anchors.margins: 6
                    text: "译图"
                    color: "#78716c"
                }
            }
        }
    }
}
