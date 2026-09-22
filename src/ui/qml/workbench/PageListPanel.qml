import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../theme"

// D05 §18: left PageListPanel — virtualized thumbnails (ListView),
// per-tile status glyph + lock overlay (AC-PAGE-003), current-viewer
// highlight vs pipeline-running indicator (D05 §18.3), single/ctrl/shift
// multi-select within the chapter (AC-PAGE-002).
Rectangle {
    id: pageList
    objectName: "pageListPanel"
    color: Tokens.bgPanel

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
            radius: Tokens.radSm
            // §6C R3-001 audits `ink` against an accent-soft selected row, so
            // the selected ground must stay accent-soft and its text Tokens.ink.
            color: model.isSelected ? Tokens.accentSoft
                 : model.pageId === pageList.viewerPageId ? Tokens.bgActive
                 : Tokens.bgRaised
            border.color: model.pageId === pageList.viewerPageId ? Tokens.borderStrong
                        : model.isSelected ? Tokens.accent : Tokens.divider
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
                    radius: Tokens.radSm
                    color: Tokens.bgInset
                    Label {
                        anchors.centerIn: parent
                        text: model.pageOrder
                        color: Tokens.ink2
                        font.pixelSize: Tokens.fsSm
                    }
                }

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 2
                    Label {
                        Layout.fillWidth: true
                        text: model.filename
                        elide: Text.ElideMiddle
                        color: Tokens.ink
                        font.pixelSize: Tokens.fsSm
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
                                var colors = { waiting: Tokens.ink3,
                                    processing: Tokens.stRun,
                                    completed: Tokens.stOk,
                                    failed: Tokens.stFail,
                                    skipped: Tokens.stSkip,
                                    blocked: Tokens.stBlock };
                                return colors[model.status] || Tokens.ink3;
                            }
                            font.pixelSize: Tokens.fsSm
                        }
                        Label {
                            objectName: "pageLock-" + model.pageId
                            text: "🔒"
                            visible: model.isLocked
                            color: Tokens.stLock
                            font.pixelSize: Tokens.fsSm
                        }
                        Label {
                            objectName: "pagePipelineCurrent-" + model.pageId
                            text: "▶ 运行中"
                            visible: model.isPipelineCurrent
                            color: Tokens.stRun
                            font.pixelSize: Tokens.fsSm
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
