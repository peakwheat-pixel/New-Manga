import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

// D05 §18: left PageListPanel — virtualized thumbnails (ListView),
// per-tile status glyph + lock overlay (AC-PAGE-003), current-viewer
// highlight vs pipeline-running indicator (D05 §18.3), single/ctrl/shift
// multi-select within the chapter (AC-PAGE-002).
Rectangle {
    id: pageList
    objectName: "pageListPanel"
    color: "#ffffff"

    property var pageModel: null
    property string viewerPageId: ""
    property bool collapsed: false

    signal pageClicked(string pageId)
    signal pageCtrlClicked(string pageId)
    signal pageShiftClicked(string pageId)

    implicitWidth: collapsed ? 36 : 176

    Button {
        objectName: "pageListCollapse"
        flat: true
        anchors.top: parent.top
        anchors.right: parent.right
        anchors.margins: 2
        z: 2
        text: pageList.collapsed ? "»" : "«"
        onClicked: pageList.collapsed = !pageList.collapsed
    }

    ListView {
        id: listView
        objectName: "pageListView"
        anchors.fill: parent
        anchors.topMargin: 30
        model: pageModel
        clip: true
        spacing: 4

        ScrollBar.vertical: ScrollBar {}

        delegate: Rectangle {
            id: tile
            width: listView.width - 8
            x: 4
            height: 64
            objectName: "pageTile-" + model.pageId
            radius: 4
            color: model.isSelected ? "#dbeafe"
                 : model.pageId === pageList.viewerPageId ? "#fef3c7"
                 : "#f9fafb"
            border.color: model.pageId === pageList.viewerPageId ? "#d97706"
                        : model.isSelected ? "#2563eb" : "#e5e7eb"
            border.width: model.pageId === pageList.viewerPageId || model.isSelected ? 2 : 1

            // AC-PAGE-002: single / ctrl / shift selection + viewer open.
            TapHandler {
                acceptedModifiers: Qt.ControlModifier
                onTapped: pageList.pageCtrlClicked(model.pageId)
            }
            TapHandler {
                acceptedModifiers: Qt.ShiftModifier
                onTapped: pageList.pageShiftClicked(model.pageId)
            }
            TapHandler {
                acceptedModifiers: Qt.NoModifier
                onTapped: pageList.pageClicked(model.pageId)
            }

            RowLayout {
                anchors.fill: parent
                anchors.margins: 6
                spacing: 6

                Rectangle {
                    // thumbnail placeholder: real thumbnails load async from
                    // managed storage in a later rendering slice (D05 §65).
                    width: 48
                    height: 48
                    radius: 3
                    color: "#e5e7eb"
                    Label { anchors.centerIn: parent; text: model.pageOrder; color: "#6b7280" }
                }

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 2
                    Label {
                        Layout.fillWidth: true
                        text: model.filename
                        elide: Text.ElideMiddle
                        font.pixelSize: 11
                    }
                    RowLayout {
                        spacing: 4
                        Label {
                            objectName: "pageStatus-" + model.pageId
                            text: {
                                var glyphs = { waiting: "○ 等待", processing: "● 处理中",
                                    completed: "✓ 已完成", failed: "! 失败",
                                    skipped: "↷ 跳过", blocked: "⏸ 阻塞" };
                                return glyphs[model.status] || model.status;
                            }
                            color: {
                                var colors = { waiting: "#9ca3af", processing: "#2563eb",
                                    completed: "#16a34a", failed: "#dc2626",
                                    skipped: "#a855f7", blocked: "#d97706" };
                                return colors[model.status] || "#9ca3af";
                            }
                            font.pixelSize: 11
                        }
                        Label {
                            objectName: "pageLock-" + model.pageId
                            text: "🔒"
                            visible: model.isLocked
                            font.pixelSize: 11
                        }
                        Label {
                            objectName: "pagePipelineCurrent-" + model.pageId
                            text: "▶ 运行中"
                            visible: model.isPipelineCurrent
                            color: "#2563eb"
                            font.pixelSize: 10
                        }
                    }
                }
            }
        }

        // AC-PROGRESS-003: TaskProgress “点击当前页” scrolls here.
        function locatePage(pageId) {
            var index = pageModel.rowIndexOf ? pageModel.rowIndexOf(pageId) : -1
            if (index >= 0) {
                listView.positionViewAtIndex(index, ListView.Contain)
            }
        }
    }
}
