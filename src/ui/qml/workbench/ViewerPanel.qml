import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../common"
import "../theme"

// D05 §20: center Viewer/Canvas — Original / Clean / Translated / Compare.
// Compare shows original and translated side by side (D05 §20.1). Image
// data comes from the viewmodel (managed-copy URLs); modes without a
// produced artifact in this slice render an honest placeholder instead of
// a fake image.
Rectangle {
    id: viewer
    objectName: "viewerPanel"
    color: Tokens.bgPanel

    property string imageUrl: ""
    property string translatedUrl: ""
    property string pageName: ""
    property string mode: "original"
    property var vm: null

    Label {
        anchors.centerIn: parent
        visible: viewer.pageName === ""
        objectName: "viewerEmpty"
        text: "在左侧选择一个 Page"
        color: Tokens.ink3
        font.pixelSize: Tokens.fsBase
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Tokens.gap
        spacing: Tokens.gap
        visible: viewer.pageName !== ""

        RowLayout {
            Layout.fillWidth: true
            Label {
                objectName: "viewerPageName"
                text: viewer.pageName
                font.bold: true
                color: Tokens.ink
                font.pixelSize: Tokens.fsSub
            }
            Item { Layout.fillWidth: true }
            Label {
                objectName: "viewerModeLabel"
                text: { var names = { original: "原图", clean: "修复图",
                    translated: "译图", compare: "对比" };
                    return names[viewer.mode] || viewer.mode; }
                color: Tokens.ink3
                font.pixelSize: Tokens.fsSm
            }
        }

        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: Tokens.gap

            // Original pane (also the single-image pane for non-compare).
            Rectangle {
                objectName: "viewerImagePane"
                Layout.fillWidth: viewer.mode !== "compare"
                Layout.fillHeight: true
                color: Tokens.bgCanvas
                border.color: Tokens.border
                Image {
                    id: mainImage
                    anchors.fill: parent
                    anchors.margins: 4
                    source: viewer.imageUrl
                    fillMode: Image.PreserveAspectFit
                    asynchronous: true
                }
                CanvasCaption {
                    anchors.centerIn: parent
                    visible: mainImage.status === Image.Null || mainImage.source === ""
                    text: viewer.mode === "original" ? "原图不可用" : "该模式暂无产物"
                }
                CanvasCaption {
                    anchors.bottom: parent.bottom
                    anchors.left: parent.left
                    anchors.margins: 6
                    visible: viewer.mode === "compare"
                    text: "原图"
                }

                // Region geometry belongs to the original page's pixel space,
                // so the canvas exists only over this pane in this mode: a
                // produced artifact has no guaranteed matching dimensions.
                // The margins match mainImage so the fit rect is the same rect
                // the image is letterboxed into.
                RegionOverlay {
                    objectName: "viewerRegionOverlay"
                    anchors.fill: parent
                    anchors.margins: 4
                    visible: viewer.mode === "original" && viewer.pageName !== ""
                    vm: viewer.vm
                }
            }

            // Compare pane (D05 §20.1 左右双图).
            Rectangle {
                objectName: "viewerComparePane"
                Layout.fillWidth: true
                Layout.fillHeight: true
                visible: viewer.mode === "compare"
                color: Tokens.bgCanvas
                border.color: Tokens.border
                Image {
                    anchors.fill: parent
                    anchors.margins: 4
                    source: viewer.translatedUrl
                    fillMode: Image.PreserveAspectFit
                    asynchronous: true
                }
                CanvasCaption {
                    anchors.centerIn: parent
                    visible: viewer.translatedUrl === ""
                    text: "译图尚未产出"
                }
                CanvasCaption {
                    anchors.bottom: parent.bottom
                    anchors.left: parent.left
                    anchors.margins: 6
                    text: "译图"
                }
            }
        }
    }
}
